use crate::util::{
    absolute_existing_root, atomic_write, atomic_write_json, canonical_bytes, capture_tree,
    digest_bytes, manifest_digest, object, read_raw_json, reject_symlink_components, relative_path,
    string_from, verify_tree,
};
use anyhow::{anyhow, bail, Context, Result};
use rand::random;
use serde_json::{json, Value};
use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::fs;
use std::io::{Read, Write};
use std::net::{IpAddr, SocketAddr, TcpListener, TcpStream};
use std::path::Path;
use std::time::Duration;

const CONTROL: &str = ".derived-evidence-view";
const VIEW_SCHEMA: &str = "derived-evidence-view.v1";
const RECEIPT_SCHEMA: &str = "derived-evidence-view-receipt.v1";
const RECORD_SCHEMA: &str = "derived-evidence-view-seal.v1";
const DELIVERY_SCHEMA: &str = "derived-evidence-view-delivery.v1";
const DELIVERY_NONCE_PLACEHOLDER: &str = "__SPLIT_TEST_HELPER_DELIVERY_NONCE_6B9F1D0E__";

pub(crate) fn seal(root_arg: &Path, spec_path: &Path) -> Result<Value> {
    let root = absolute_existing_root(root_arg)?;
    let raw = read_raw_json(spec_path, VIEW_SCHEMA, "derived-view specification")?;
    validate_spec(&root, &raw.value)?;
    let control = root.join(CONTROL);
    if control.exists() {
        let record = load_record(&root)?;
        if record.get("spec_digest").and_then(Value::as_str) != Some(&raw.digest) {
            bail!("derived view is already sealed with different content");
        }
        return verify_value(&root);
    }
    let manifest = capture_tree(&root, &[CONTROL])?;
    let manifest_hash = manifest_digest(&manifest)?;
    let reader = reader_html(&raw.value, &raw.digest, &manifest_hash)?;
    let reader_digest = digest_bytes(reader.as_bytes());
    let record = generated_record(&raw.digest, &manifest_hash, &reader_digest);
    let stage = root.join(format!(".{CONTROL}.stage-{:016x}", random::<u64>()));
    fs::create_dir(&stage)?;
    let write_result = (|| -> Result<()> {
        atomic_write(&stage.join("spec.json"), &raw.bytes, false)?;
        atomic_write_json(&stage.join("manifest.json"), &manifest)?;
        atomic_write_json(&stage.join("record.json"), &record)?;
        atomic_write(&stage.join("reader/index.html"), reader.as_bytes(), false)?;
        atomic_write(&stage.join("reader/spec.json"), &raw.bytes, false)?;
        atomic_write_json(&stage.join("reader/manifest.json"), &manifest)?;
        atomic_write_json(&stage.join("reader/record.json"), &record)?;
        fs::rename(&stage, &control).context("commit derived-view seal")?;
        Ok(())
    })();
    if write_result.is_err() {
        let _ = fs::remove_dir_all(&stage);
    }
    write_result?;
    output(&root, &record, true)
}

pub(crate) fn verify(root_arg: &Path) -> Result<Value> {
    let root = absolute_existing_root(root_arg)?;
    verify_value(&root)
}

pub(crate) fn receipt(root_arg: &Path) -> Result<Value> {
    let root = absolute_existing_root(root_arg)?;
    let verified = verify_value(&root)?;
    Ok(json!({
        "schema": RECEIPT_SCHEMA,
        "root": root,
        "spec_digest": verified.get("spec_digest").cloned().ok_or_else(|| anyhow!("verified view missing spec digest"))?,
        "manifest_digest": verified.get("manifest_digest").cloned().ok_or_else(|| anyhow!("verified view missing manifest digest"))?,
        "reader_digest": verified.get("reader_digest").cloned().ok_or_else(|| anyhow!("verified view missing reader digest"))?
    }))
}

pub(crate) fn serve(root_arg: &Path, bind: &str, port: u16) -> Result<()> {
    let root = absolute_existing_root(root_arg)?;
    let bind_ip: IpAddr = bind.parse().context("parse --bind address")?;
    if !bind_ip.is_loopback() {
        bail!("view serve accepts only a loopback --bind address");
    }
    verify_value(&root)?;
    let listener = TcpListener::bind((bind_ip, port)).context("bind evidence-view server")?;
    let address = listener.local_addr()?;
    let capability = serve_capability();
    let delivery_nonce = serve_capability();
    let url = format!("http://{address}/{capability}/{CONTROL}/reader/index.html");
    let mut stdout = std::io::stdout().lock();
    serde_json::to_writer(&mut stdout, &json!({"schema": VIEW_SCHEMA, "url": url}))?;
    stdout.write_all(b"\n")?;
    stdout.flush()?;
    for stream in listener.incoming() {
        match stream {
            Ok(mut stream) => {
                if let Err(error) = handle_request(&root, &capability, &delivery_nonce, &mut stream)
                {
                    let body = format!("request rejected: {error}\n");
                    let _ = write_response(
                        &mut stream,
                        "400 Bad Request",
                        "text/plain; charset=utf-8",
                        body.as_bytes(),
                        false,
                        shell_csp(),
                        false,
                    );
                }
            }
            Err(error) => return Err(error).context("accept evidence-view request"),
        }
    }
    Ok(())
}

fn verify_value(root: &Path) -> Result<Value> {
    let control = root.join(CONTROL);
    verify_control_layout(&control)?;
    let record = load_record(root)?;
    let spec = fs::read(control.join("spec.json")).context("read retained view specification")?;
    let spec_hash = digest_bytes(&spec);
    if record.get("spec_digest").and_then(Value::as_str) != Some(&spec_hash) {
        bail!("derived-view specification mutation detected");
    }
    let spec_value: Value =
        serde_json::from_slice(&spec).context("parse retained view specification")?;
    validate_spec(root, &spec_value)?;
    let manifest: Value = serde_json::from_slice(
        &fs::read(control.join("manifest.json")).context("read derived-view manifest")?,
    )
    .context("parse derived-view manifest")?;
    let manifest_hash = manifest_digest(&manifest)?;
    if record.get("manifest_digest").and_then(Value::as_str) != Some(&manifest_hash) {
        bail!("derived-view manifest mutation detected");
    }
    verify_tree(root, &[CONTROL], &manifest)?;
    let reader = fs::read(control.join("reader/index.html")).context("read evidence reader")?;
    let expected_reader = reader_html(&spec_value, &spec_hash, &manifest_hash)?;
    if reader != expected_reader.as_bytes() {
        bail!("evidence-reader package consistency failure");
    }
    let reader_hash = digest_bytes(&reader);
    let expected_record = generated_record(&spec_hash, &manifest_hash, &reader_hash);
    let expected_record_bytes = canonical_bytes(&expected_record)?;
    if fs::read(control.join("reader/spec.json")).context("read reader spec")? != spec {
        bail!("reader spec copy mutation detected");
    }
    let manifest_bytes =
        fs::read(control.join("manifest.json")).context("read derived-view manifest")?;
    if fs::read(control.join("reader/manifest.json")).context("read reader manifest")?
        != manifest_bytes
    {
        bail!("reader manifest copy mutation detected");
    }
    let record_bytes = fs::read(control.join("record.json")).context("read derived-view record")?;
    if record_bytes != expected_record_bytes {
        bail!("generated seal record mismatch");
    }
    if fs::read(control.join("reader/record.json")).context("read reader record")?
        != expected_record_bytes
    {
        bail!("reader generated seal record mismatch");
    }
    output(root, &expected_record, false)
}

fn generated_record(spec_digest: &str, manifest_digest: &str, reader_digest: &str) -> Value {
    json!({
        "schema": RECORD_SCHEMA,
        "view_schema": VIEW_SCHEMA,
        "spec_digest": spec_digest,
        "manifest_digest": manifest_digest,
        "reader_digest": reader_digest,
        "spec_file": "spec.json",
        "manifest_file": "manifest.json",
        "record_file": "record.json",
        "reader_file": "reader/index.html"
    })
}

fn verify_control_layout(control: &Path) -> Result<()> {
    verify_exact_directory(
        control,
        &["manifest.json", "reader", "record.json", "spec.json"],
        "derived-view control",
    )?;
    require_control_directory(&control.join("reader"), "reader control directory")?;
    verify_exact_directory(
        &control.join("reader"),
        &["index.html", "manifest.json", "record.json", "spec.json"],
        "reader control",
    )?;
    for relative in [
        "manifest.json",
        "record.json",
        "spec.json",
        "reader/index.html",
        "reader/manifest.json",
        "reader/record.json",
        "reader/spec.json",
    ] {
        require_control_file(&control.join(relative), relative)?;
    }
    Ok(())
}

fn verify_exact_directory(path: &Path, expected: &[&str], label: &str) -> Result<()> {
    require_control_directory(path, label)?;
    let mut actual = BTreeSet::new();
    for entry in fs::read_dir(path).with_context(|| format!("read {label}"))? {
        let entry = entry.with_context(|| format!("read {label} entry"))?;
        let name = entry
            .file_name()
            .into_string()
            .map_err(|_| anyhow!("unexpected control entry with a non-UTF-8 name in {label}"))?;
        actual.insert(name);
    }
    let expected = expected
        .iter()
        .map(|name| (*name).to_owned())
        .collect::<BTreeSet<_>>();
    if let Some(name) = actual.difference(&expected).next() {
        bail!("unexpected control entry in {label}: {name}");
    }
    if let Some(name) = expected.difference(&actual).next() {
        bail!("missing control entry in {label}: {name}");
    }
    Ok(())
}

fn require_control_directory(path: &Path, label: &str) -> Result<()> {
    let metadata = fs::symlink_metadata(path).with_context(|| format!("read {label}"))?;
    if metadata.file_type().is_symlink() || !metadata.file_type().is_dir() {
        bail!("{label} must be a real directory, not a symlink");
    }
    Ok(())
}

fn require_control_file(path: &Path, label: &str) -> Result<()> {
    let metadata = fs::symlink_metadata(path).with_context(|| format!("read {label}"))?;
    if metadata.file_type().is_symlink() || !metadata.file_type().is_file() {
        bail!("{label} must be a regular control file, not a symlink");
    }
    Ok(())
}

fn load_record(root: &Path) -> Result<Value> {
    let path = root.join(CONTROL).join("record.json");
    let bytes = fs::read(&path).map_err(|_| anyhow!("derived view is not sealed"))?;
    let value: Value = serde_json::from_slice(&bytes).context("parse derived-view record")?;
    if value.get("schema").and_then(Value::as_str) != Some(RECORD_SCHEMA) {
        bail!("unsupported derived-view record schema");
    }
    Ok(value)
}

fn output(root: &Path, record: &Value, created: bool) -> Result<Value> {
    Ok(json!({
        "schema": VIEW_SCHEMA,
        "root": root,
        "spec_digest": record.get("spec_digest").ok_or_else(|| anyhow!("view record missing spec digest"))?,
        "manifest_digest": record.get("manifest_digest").ok_or_else(|| anyhow!("view record missing manifest digest"))?,
        "reader_digest": record.get("reader_digest").ok_or_else(|| anyhow!("view record missing reader digest"))?,
        "reader": root.join(CONTROL).join("reader/index.html"),
        "created": created
    }))
}

fn validate_spec(root: &Path, value: &Value) -> Result<()> {
    let fields = object(value, "derived-view specification")?;
    if string_from(fields, "schema", "derived-view specification")? != VIEW_SCHEMA {
        bail!("unsupported derived-view schema");
    }
    let source_refs = fields
        .get("source_refs")
        .and_then(Value::as_array)
        .ok_or_else(|| anyhow!("derived-view specification.source_refs must be an array"))?;
    if source_refs.is_empty() {
        bail!("derived-view specification.source_refs must not be empty");
    }
    let entrypoints = fields
        .get("entrypoints")
        .and_then(Value::as_array)
        .ok_or_else(|| anyhow!("derived-view specification.entrypoints must be an array"))?;
    if entrypoints.is_empty() {
        bail!("derived-view specification.entrypoints must not be empty");
    }
    for value in entrypoints {
        let text = value
            .as_str()
            .ok_or_else(|| anyhow!("derived-view entrypoints must be strings"))?;
        let relative = relative_path(text, "derived-view entrypoint")?;
        let path = root.join(relative);
        let is_regular_file =
            fs::symlink_metadata(&path).is_ok_and(|metadata| metadata.file_type().is_file());
        if !is_regular_file {
            bail!("derived-view entrypoint is missing or not a regular file: {text}");
        }
    }
    validate_local_refs(root, fields)?;
    Ok(())
}

fn validate_local_refs(root: &Path, fields: &serde_json::Map<String, Value>) -> Result<()> {
    for key in [
        "source_refs",
        "derivation_refs",
        "runtime_refs",
        "external_dependencies",
    ] {
        let Some(value) = fields.get(key) else {
            continue;
        };
        let values = value
            .as_array()
            .ok_or_else(|| anyhow!("derived-view specification.{key} must be an array"))?;
        for reference in values {
            if let Some(path_value) = reference.as_object().and_then(|item| item.get("path")) {
                let text = path_value
                    .as_str()
                    .ok_or_else(|| anyhow!("declared local reference path must be a string"))?;
                let relative = relative_path(text, "declared local reference")?;
                let path = root.join(relative);
                let metadata = fs::symlink_metadata(&path)
                    .with_context(|| format!("declared local asset is missing: {text}"))?;
                if metadata.file_type().is_symlink()
                    || (!metadata.file_type().is_file() && !metadata.file_type().is_dir())
                {
                    bail!("declared local asset has an unsupported file type: {text}");
                }
            }
        }
    }
    Ok(())
}

fn reader_html(spec: &Value, spec_digest: &str, manifest_digest: &str) -> Result<String> {
    let fields = object(spec, "derived-view specification")?;
    let entrypoints = fields
        .get("entrypoints")
        .and_then(Value::as_array)
        .ok_or_else(|| anyhow!("entrypoints missing"))?;
    let first = entrypoints
        .first()
        .and_then(Value::as_str)
        .ok_or_else(|| anyhow!("entrypoint missing"))?;
    let mut links = String::new();
    for entry in entrypoints.iter().filter_map(Value::as_str) {
        let label = html_escape(entry);
        let href = html_escape(&url_path(entry));
        write!(
            links,
            "<li><button type=\"button\" class=\"asset-link\" disabled data-served-src=\"../../{href}\">{label}</button></li>"
        )?;
    }
    let raw_links = local_reference_links(fields)?;
    let sources_value = fields
        .get("source_refs")
        .cloned()
        .map_or(Value::Null, |value| value);
    let derivations_value = fields
        .get("derivation_refs")
        .cloned()
        .map_or(Value::Array(Vec::new()), |value| value);
    let runtime_value = fields
        .get("runtime_refs")
        .cloned()
        .map_or(Value::Array(Vec::new()), |value| value);
    let dependencies_value = fields
        .get("external_dependencies")
        .cloned()
        .map_or(Value::Array(Vec::new()), |value| value);
    let disclosures_value = fields
        .get("interpretive_disclosures")
        .cloned()
        .map_or(Value::Array(Vec::new()), |value| value);
    let sources = html_escape(&serde_json::to_string_pretty(&sources_value)?);
    let derivations = html_escape(&serde_json::to_string_pretty(&derivations_value)?);
    let runtime = html_escape(&serde_json::to_string_pretty(&runtime_value)?);
    let dependencies = html_escape(&serde_json::to_string_pretty(&dependencies_value)?);
    let disclosures = html_escape(&serde_json::to_string_pretty(&disclosures_value)?);
    let (allowed_refs, reference_index) = reference_transport(fields, spec_digest)?;
    let first = html_escape(&url_path(first));
    let spec_digest = html_escape(spec_digest);
    let manifest_digest = html_escape(manifest_digest);
    Ok(format!(
        r#"<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; frame-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:; media-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; connect-src 'self'">
<title>Evidence view</title>
<style>
:root {{ font: 15px/1.45 system-ui,sans-serif; color-scheme:light dark; --line:color-mix(in srgb,currentColor 20%,transparent); }}
html[data-theme="light"] {{ color-scheme:light }} html[data-theme="dark"] {{ color-scheme:dark }}
* {{ box-sizing:border-box }} body {{ margin:0; min-height:100vh; display:grid; grid-template-columns:minmax(17rem,24rem) 1fr; background:Canvas; color:CanvasText }}
aside {{ padding:1rem; border-right:1px solid var(--line); overflow:auto }} main {{ min-width:0; padding:1rem }} h1 {{ font-size:1.25rem }} h2 {{ font-size:1rem; margin-top:1.4rem }} ul {{ padding-left:1.2rem }} a {{ color:LinkText }} pre {{ white-space:pre-wrap; overflow-wrap:anywhere; font-size:.78rem }} code {{ white-space:pre-wrap; overflow-wrap:anywhere }} iframe {{ width:100%; min-height:calc(100vh - 2rem); border:1px solid var(--line); background:white }} select {{ font:inherit; color:inherit; background:Canvas; border:1px solid var(--line); border-radius:.35rem; padding:.25rem .45rem }} .asset-link {{ padding:0; border:0; color:LinkText; background:transparent; font:inherit; text-align:left; text-decoration:underline; cursor:pointer }} .asset-link:disabled {{ color:GrayText; cursor:not-allowed; text-decoration:none }} .theme-control {{ display:flex; align-items:center; justify-content:space-between; gap:.75rem; margin:1rem 0 }} .inspection > summary {{ font-weight:700; margin-block:1rem }} .meta-list, .raw-list {{ display:grid; gap:.35rem; padding-left:0; list-style:none }} .muted {{ color:color-mix(in srgb, currentColor 70%, transparent) }}
@media (max-width:760px) {{ body {{ grid-template-columns:1fr }} aside {{ border-right:0; border-bottom:1px solid var(--line) }} iframe {{ min-height:70vh }} }}
@media (prefers-reduced-motion:reduce) {{ * {{ scroll-behavior:auto!important; animation:none!important; transition:none!important }} }}
@media print {{ body {{ display:block }} aside {{ border:0 }} iframe {{ min-height:70vh }} }}
</style>
</head>
<body>
<aside><header><h1>Evidence view</h1><p>Derived projection. Inspect sources and disclosures before acting.</p><div class="theme-control"><label for="reader-theme">Theme</label><select id="reader-theme"><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></div></header>
<nav aria-label="View entrypoints"><h2>Entrypoints</h2><ul>{links}</ul></nav>
<details class="inspection"><summary>Inspect package and evidence</summary><section aria-labelledby="package-identity"><h2 id="package-identity">Package identity</h2><ul class="meta-list"><li><strong>Specification digest</strong><br><code>{spec_digest}</code></li><li><strong>Manifest digest</strong><br><code>{manifest_digest}</code></li><li><strong>Reader metadata</strong><br><a href="spec.json" target="_blank" rel="noopener">spec.json</a> · <a href="manifest.json" target="_blank" rel="noopener">manifest.json</a> · <a href="record.json" target="_blank" rel="noopener">record.json</a></li></ul></section>
<details><summary>Raw local evidence</summary>{raw_links}</details>
<details><summary>Source references</summary><pre>{sources}</pre></details>
<details><summary>Derivation references</summary><pre>{derivations}</pre></details>
<details><summary>Runtime references</summary><pre>{runtime}</pre></details>
<details><summary>Dependencies</summary><pre>{dependencies}</pre></details>
<details><summary>Interpretive disclosures</summary><pre>{disclosures}</pre></details></details></aside>
<main><p id="reader-status" class="muted" aria-live="polite">Reader status: verifying the delivery boundary.</p><section id="static-inspection" hidden><h2>Static inspection mode</h2><p>This mode exposes retained package metadata for static inspection but does not navigate or execute authored entrypoints. Active authored content requires the constrained loopback server.</p></section><iframe id="evidence-frame" name="evidence-frame" title="Authored evidence entrypoint" sandbox="allow-scripts allow-forms allow-downloads" hidden data-src="../../{first}"></iframe></main>
<script>
(() => {{
  const frame = document.getElementById('evidence-frame');
  const status = document.getElementById('reader-status');
  const staticInspection = document.getElementById('static-inspection');
  const theme = document.getElementById('reader-theme');
  const authoredLinks = document.querySelectorAll('[data-served-src]');
  const allowedRefs = new Map({allowed_refs});
  const referenceIndex = {{schema:'evidence-view-message.v1', type:'reference-index', references:{reference_index}}};
  const expectedDeliveryNonce = '{DELIVERY_NONCE_PLACEHOLDER}';
  let helperDelivery = false;
  let authoredReady = false;
  function sendReferenceIndex() {{
    if (!helperDelivery) return;
    frame.contentWindow.postMessage(referenceIndex, '*');
  }}
  theme.addEventListener('change', () => {{
    if (theme.value === 'system') document.documentElement.removeAttribute('data-theme');
    else document.documentElement.setAttribute('data-theme', theme.value);
  }});
  function openRef(ref) {{
    if (!helperDelivery || !allowedRefs.has(ref)) return;
    navigateAuthored(allowedRefs.get(ref));
  }}
  function navigateAuthored(href) {{
    if (!helperDelivery) return;
    authoredReady = false;
    status.textContent = 'Reader status: loading authored entrypoint.';
    frame.src = href;
  }}
  authoredLinks.forEach((link) => {{
    link.addEventListener('click', () => navigateAuthored(link.dataset.servedSrc));
  }});
  frame.addEventListener('load', () => {{
    if (!helperDelivery) return;
    if (!authoredReady) status.textContent = 'Reader status: authored entrypoint loaded.';
    sendReferenceIndex();
  }});
  window.addEventListener('message', (event) => {{
    if (event.source !== frame.contentWindow) return;
    if (!helperDelivery) return;
    const data = event.data;
    if (!data || typeof data !== 'object' || data.schema !== 'evidence-view-message.v1' || typeof data.type !== 'string') {{
      return;
    }}
    if (data.type === 'ready') {{
      authoredReady = true;
      status.textContent = 'Reader status: authored entrypoint reported ready.';
      sendReferenceIndex();
      return;
    }}
    if (data.type === 'resize' && Number.isFinite(data.height)) {{
      const height = Math.max(320, Math.min(20000, Math.trunc(data.height)));
      frame.style.minHeight = `${{height}}px`;
      return;
    }}
    if (data.type === 'open-ref' && typeof data.ref === 'string') {{
      openRef(data.ref);
    }}
  }});
  function keepStatic() {{
    helperDelivery = false;
    authoredReady = false;
    frame.hidden = true;
    frame.removeAttribute('src');
    staticInspection.hidden = false;
    authoredLinks.forEach((link) => {{
      link.disabled = true;
      link.title = 'Use the constrained loopback server to open authored content.';
    }});
    status.textContent = 'Reader status: static inspection; authored content is inactive.';
  }}
  function activateHelperDelivery() {{
    helperDelivery = true;
    staticInspection.hidden = true;
    frame.hidden = false;
    authoredLinks.forEach((link) => {{
      link.disabled = false;
      link.removeAttribute('title');
    }});
    authoredReady = false;
    status.textContent = 'Reader status: loading authored entrypoint.';
    frame.src = frame.dataset.src;
  }}
  async function establishHelperDelivery() {{
    if (window.location.protocol !== 'http:') return false;
    if (!['127.0.0.1', 'localhost', '[::1]', '::1'].includes(window.location.hostname)) return false;
    const match = window.location.pathname.match(/^\/([0-9a-f]{{64}})\/\.derived-evidence-view\/reader\/index\.html$/);
    if (!match) return false;
    if (!/^[0-9a-f]{{64}}$/.test(expectedDeliveryNonce)) return false;
    try {{
      const response = await fetch('delivery.json', {{cache:'no-store', credentials:'omit'}});
      if (!response.ok) return false;
      const delivery = await response.json();
      if (delivery.schema !== 'derived-evidence-view-delivery.v1' || delivery.capability !== match[1] || delivery.nonce !== expectedDeliveryNonce) return false;
      return true;
    }} catch (_error) {{
      return false;
    }}
  }}
  establishHelperDelivery().then((active) => {{
    if (active) activateHelperDelivery();
    else keepStatic();
  }});
}})();
</script>
</body></html>
"#
    ))
}

fn local_reference_links(fields: &serde_json::Map<String, Value>) -> Result<String> {
    let mut links = String::new();
    let mut any = false;
    for key in [
        "source_refs",
        "derivation_refs",
        "runtime_refs",
        "external_dependencies",
    ] {
        let Some(values) = fields.get(key).and_then(Value::as_array) else {
            continue;
        };
        for reference in values {
            let Some(text) = reference
                .as_object()
                .and_then(|item| item.get("path"))
                .and_then(Value::as_str)
            else {
                continue;
            };
            let label = html_escape(text);
            let href = html_escape(&url_path(text));
            write!(
                links,
                "<li><button type=\"button\" class=\"asset-link\" disabled data-served-src=\"../../{href}\">{label}</button> <span class=\"muted\">({key})</span></li>"
            )?;
            any = true;
        }
    }
    if !any {
        return Ok("<p class=\"muted\">No local evidence files were declared.</p>".to_owned());
    }
    Ok(format!("<ul class=\"raw-list\">{links}</ul>"))
}

fn reference_transport(
    fields: &serde_json::Map<String, Value>,
    spec_digest: &str,
) -> Result<(String, String)> {
    let mut pairs = Vec::new();
    let mut index = Vec::new();
    let mut sequence = 0_usize;
    let mut add = |label: &str, href: String| {
        let reference = opaque_ref_id(spec_digest, sequence, &href);
        sequence += 1;
        pairs.push(json!([reference, href]));
        index.push(json!({"ref": reference, "label": label}));
    };
    for relative in ["spec.json", "manifest.json", "record.json"] {
        add(relative, relative.to_owned());
    }
    for entry in fields
        .get("entrypoints")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
    {
        add(entry, format!("../../{}", url_path(entry)));
    }
    for key in [
        "source_refs",
        "derivation_refs",
        "runtime_refs",
        "external_dependencies",
    ] {
        let Some(values) = fields.get(key).and_then(Value::as_array) else {
            continue;
        };
        for reference in values {
            let Some(path) = reference
                .as_object()
                .and_then(|item| item.get("path"))
                .and_then(Value::as_str)
            else {
                continue;
            };
            add(path, format!("../../{}", url_path(path)));
        }
    }
    Ok((
        json_for_script(&Value::Array(pairs))?,
        json_for_script(&Value::Array(index))?,
    ))
}

fn opaque_ref_id(spec_digest: &str, sequence: usize, href: &str) -> String {
    let material = format!("{spec_digest}\0{sequence}\0{href}");
    let suffix = digest_bytes(material.as_bytes())
        .chars()
        .take(24)
        .collect::<String>();
    format!("ref-{suffix}")
}

fn html_escape(value: &str) -> String {
    value
        .replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#39;")
}

fn json_for_script(value: &Value) -> Result<String> {
    Ok(serde_json::to_string(value)?
        .replace('<', "\\u003c")
        .replace('>', "\\u003e")
        .replace('\u{2028}', "\\u2028")
        .replace('\u{2029}', "\\u2029"))
}

fn url_path(value: &str) -> String {
    let mut encoded = String::with_capacity(value.len());
    for byte in value.bytes() {
        if byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'.' | b'_' | b'~' | b'/') {
            encoded.push(char::from(byte));
        } else {
            encoded.push('%');
            encoded.push(upper_hex_digit(byte >> 4));
            encoded.push(upper_hex_digit(byte & 0x0f));
        }
    }
    encoded
}

fn upper_hex_digit(nibble: u8) -> char {
    if nibble < 10 {
        char::from(b'0' + nibble)
    } else {
        char::from(b'A' + nibble - 10)
    }
}

fn handle_request(
    root: &Path,
    capability: &str,
    delivery_nonce: &str,
    stream: &mut TcpStream,
) -> Result<()> {
    let local_addr = stream.local_addr()?;
    let authored_origin = format!("http://{local_addr}");
    stream
        .set_read_timeout(Some(Duration::from_secs(5)))
        .context("set HTTP request timeout")?;
    let request_bytes = read_request_head(stream)?;
    if request_bytes.is_empty() {
        bail!("empty request");
    }
    let request = std::str::from_utf8(&request_bytes).context("request must be UTF-8")?;
    validate_host_header(request, local_addr)?;
    let line = request
        .lines()
        .next()
        .ok_or_else(|| anyhow!("missing request line"))?;
    let mut parts = line.split_whitespace();
    let method = parts.next().ok_or_else(|| anyhow!("missing method"))?;
    let target = parts.next().ok_or_else(|| anyhow!("missing target"))?;
    if !matches!(method, "GET" | "HEAD") {
        return write_response(
            stream,
            "405 Method Not Allowed",
            "text/plain; charset=utf-8",
            b"method not allowed\n",
            method == "HEAD",
            shell_csp(),
            false,
        );
    }
    let raw_path = target.split_once('?').map_or(target, |(path, _)| path);
    let decoded = percent_decode(raw_path)?;
    if decoded.contains('\0') || decoded.contains('\\') {
        bail!("request path is not portable");
    }
    let verified = verify_value(root)?;
    let capability_prefix = format!("/{capability}");
    let scoped = if decoded == capability_prefix {
        "/"
    } else if let Some(scoped) = decoded.strip_prefix(&format!("{capability_prefix}/")) {
        scoped.strip_prefix('/').map_or(scoped, |value| value)
    } else {
        return write_response(
            stream,
            "404 Not Found",
            "text/plain; charset=utf-8",
            b"not found\n",
            method == "HEAD",
            shell_csp(),
            false,
        );
    };
    let scoped = if scoped == "/" {
        "/".to_owned()
    } else {
        format!("/{scoped}")
    };
    if scoped == "/" || scoped == format!("/{CONTROL}/reader/index.html") {
        let retained = read_verified_reader_control(root, "index.html", &verified)?;
        let bytes = inject_delivery_nonce(&retained, delivery_nonce)?;
        return write_response(
            stream,
            "200 OK",
            "text/html; charset=utf-8",
            &bytes,
            method == "HEAD",
            shell_csp(),
            false,
        );
    }
    if scoped == format!("/{CONTROL}/reader/delivery.json") {
        let bytes = canonical_bytes(&json!({
            "schema": DELIVERY_SCHEMA,
            "capability": capability,
            "nonce": delivery_nonce
        }))?;
        return write_response(
            stream,
            "200 OK",
            "application/json",
            &bytes,
            method == "HEAD",
            shell_csp(),
            false,
        );
    }
    if let Some(name) = scoped.strip_prefix(&format!("/{CONTROL}/reader/")) {
        if matches!(name, "spec.json" | "manifest.json" | "record.json") {
            let bytes = read_verified_reader_control(root, name, &verified)?;
            return write_response(
                stream,
                "200 OK",
                "application/json",
                &bytes,
                method == "HEAD",
                shell_csp(),
                false,
            );
        }
    }
    let relative = relative_path(scoped.trim_start_matches('/'), "request path")?;
    let manifest: Value = serde_json::from_slice(
        &fs::read(root.join(CONTROL).join("manifest.json")).context("read served view manifest")?,
    )
    .context("parse served view manifest")?;
    if verified.get("manifest_digest").and_then(Value::as_str)
        != Some(manifest_digest(&manifest)?.as_str())
    {
        bail!("served view manifest mutation detected");
    }
    let Some(bytes) = read_manifest_bound_file(root, &relative, &manifest)? else {
        return write_response(
            stream,
            "404 Not Found",
            "text/plain; charset=utf-8",
            b"not found\n",
            method == "HEAD",
            shell_csp(),
            false,
        );
    };
    let csp = authored_csp(&authored_origin);
    write_response(
        stream,
        "200 OK",
        mime_for(&relative),
        &bytes,
        method == "HEAD",
        &csp,
        true,
    )
}

fn validate_host_header(request: &str, local_addr: SocketAddr) -> Result<()> {
    let mut hosts = request
        .lines()
        .skip(1)
        .take_while(|line| !line.trim().is_empty())
        .filter_map(|line| {
            line.split_once(':')
                .filter(|(name, _)| name.eq_ignore_ascii_case("host"))
                .map(|(_, value)| value.trim())
        });
    let host = hosts.next().ok_or_else(|| anyhow!("missing Host header"))?;
    if hosts.next().is_some() {
        bail!("multiple Host headers are not allowed");
    }
    let ip_authority = match local_addr.ip() {
        IpAddr::V4(ip) => ip.to_string(),
        IpAddr::V6(ip) => format!("[{ip}]"),
    };
    let expected = [
        ip_authority.clone(),
        format!("{ip_authority}:{}", local_addr.port()),
        "localhost".to_owned(),
        format!("localhost:{}", local_addr.port()),
    ];
    if !expected
        .iter()
        .any(|candidate| candidate.eq_ignore_ascii_case(host))
    {
        bail!("unexpected Host header");
    }
    Ok(())
}

fn serve_capability() -> String {
    format!(
        "{:016x}{:016x}{:016x}{:016x}",
        random::<u64>(),
        random::<u64>(),
        random::<u64>(),
        random::<u64>()
    )
}

fn inject_delivery_nonce(retained_reader: &[u8], delivery_nonce: &str) -> Result<Vec<u8>> {
    if delivery_nonce.len() != 64
        || !delivery_nonce
            .bytes()
            .all(|byte| byte.is_ascii_hexdigit() && !byte.is_ascii_uppercase())
    {
        bail!("delivery nonce must be exactly 64 lowercase hexadecimal characters");
    }
    let retained = std::str::from_utf8(retained_reader).context("retained reader must be UTF-8")?;
    let mut matches = retained.match_indices(DELIVERY_NONCE_PLACEHOLDER);
    let (start, placeholder) = matches
        .next()
        .ok_or_else(|| anyhow!("retained reader is missing the delivery nonce placeholder"))?;
    if matches.next().is_some() {
        bail!("retained reader contains duplicate delivery nonce placeholders");
    }
    let end = start.saturating_add(placeholder.len());
    let before = retained
        .get(..start)
        .ok_or_else(|| anyhow!("delivery nonce placeholder start is invalid"))?;
    let after = retained
        .get(end..)
        .ok_or_else(|| anyhow!("delivery nonce placeholder end is invalid"))?;
    let mut served = String::with_capacity(
        retained
            .len()
            .saturating_sub(placeholder.len())
            .saturating_add(delivery_nonce.len()),
    );
    served.push_str(before);
    served.push_str(delivery_nonce);
    served.push_str(after);
    Ok(served.into_bytes())
}

fn read_request_head(stream: &mut TcpStream) -> Result<Vec<u8>> {
    const MAX_REQUEST_HEAD: usize = 16_384;
    let mut request = Vec::new();
    let mut chunk = [0_u8; 1_024];
    loop {
        let count = stream.read(&mut chunk).context("read HTTP request")?;
        if count == 0 {
            break;
        }
        if request.len().saturating_add(count) > MAX_REQUEST_HEAD {
            bail!("HTTP request head exceeds 16384 bytes");
        }
        let bytes = chunk
            .get(..count)
            .ok_or_else(|| anyhow!("HTTP read exceeded its buffer"))?;
        request.extend_from_slice(bytes);
        if request.windows(4).any(|window| window == b"\r\n\r\n")
            || request.windows(2).any(|window| window == b"\n\n")
        {
            break;
        }
    }
    Ok(request)
}

fn read_manifest_bound_file(
    root: &Path,
    relative: &Path,
    manifest: &Value,
) -> Result<Option<Vec<u8>>> {
    let fields = object(manifest, "view manifest")?;
    let entries = fields
        .get("entries")
        .and_then(Value::as_array)
        .ok_or_else(|| anyhow!("view manifest entries are invalid"))?;
    let normalized = relative
        .components()
        .map(|part| part.as_os_str().to_string_lossy())
        .collect::<Vec<_>>()
        .join("/");
    let Some(entry) = entries.iter().find(|entry| {
        entry.get("kind").and_then(Value::as_str) == Some("file")
            && entry.get("path").and_then(Value::as_str) == Some(normalized.as_str())
    }) else {
        return Ok(None);
    };
    let path = root.join(relative);
    reject_symlink_components(&path, "served view asset")?;
    let bytes = fs::read(&path).context("read served view asset")?;
    let expected_size = entry
        .get("size")
        .and_then(Value::as_u64)
        .ok_or_else(|| anyhow!("view manifest file size is invalid"))?;
    let actual_size = u64::try_from(bytes.len()).context("served view asset size overflow")?;
    if actual_size != expected_size
        || entry.get("sha256").and_then(Value::as_str) != Some(digest_bytes(&bytes).as_str())
    {
        bail!("served view asset mutation detected");
    }
    Ok(Some(bytes))
}

fn read_verified_reader_control(root: &Path, name: &str, verified: &Value) -> Result<Vec<u8>> {
    let path = root.join(CONTROL).join("reader").join(name);
    reject_symlink_components(&path, "served reader control")?;
    let bytes = fs::read(&path).context("read served reader control")?;
    match name {
        "index.html" => {
            if verified.get("reader_digest").and_then(Value::as_str)
                != Some(digest_bytes(&bytes).as_str())
            {
                bail!("served evidence reader mutation detected");
            }
        }
        "spec.json" => {
            if verified.get("spec_digest").and_then(Value::as_str)
                != Some(digest_bytes(&bytes).as_str())
            {
                bail!("served reader specification mutation detected");
            }
        }
        "manifest.json" => {
            let manifest: Value =
                serde_json::from_slice(&bytes).context("parse served reader manifest")?;
            if verified.get("manifest_digest").and_then(Value::as_str)
                != Some(manifest_digest(&manifest)?.as_str())
            {
                bail!("served reader manifest mutation detected");
            }
        }
        "record.json" => {
            let spec_digest = verified
                .get("spec_digest")
                .and_then(Value::as_str)
                .ok_or_else(|| anyhow!("verified view missing spec digest"))?;
            let manifest_digest = verified
                .get("manifest_digest")
                .and_then(Value::as_str)
                .ok_or_else(|| anyhow!("verified view missing manifest digest"))?;
            let reader_digest = verified
                .get("reader_digest")
                .and_then(Value::as_str)
                .ok_or_else(|| anyhow!("verified view missing reader digest"))?;
            let expected = canonical_bytes(&generated_record(
                spec_digest,
                manifest_digest,
                reader_digest,
            ))?;
            if bytes != expected {
                bail!("served reader generated seal record mismatch");
            }
        }
        _ => bail!("unsupported reader control file"),
    }
    Ok(bytes)
}

fn write_response(
    stream: &mut TcpStream,
    status: &str,
    content_type: &str,
    body: &[u8],
    head: bool,
    csp: &str,
    allow_null_origin: bool,
) -> Result<()> {
    let cross_origin_headers = if allow_null_origin {
        "Access-Control-Allow-Origin: null\r\nVary: Origin\r\nCross-Origin-Resource-Policy: cross-origin\r\n"
    } else {
        ""
    };
    // This deliberately serves complete in-memory representations. It does not implement
    // byte ranges and therefore is not a general seekable or large-media server.
    write!(
        stream,
        "HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\nContent-Length: {}\r\nContent-Security-Policy: {csp}\r\n{cross_origin_headers}X-Content-Type-Options: nosniff\r\nReferrer-Policy: no-referrer\r\nAccept-Ranges: none\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n",
        body.len()
    )?;
    if !head {
        stream.write_all(body)?;
    }
    stream.flush()?;
    Ok(())
}

fn percent_decode(value: &str) -> Result<String> {
    let mut bytes = value.as_bytes().iter().copied();
    let mut output = Vec::with_capacity(value.len());
    while let Some(byte) = bytes.next() {
        if byte == b'%' {
            let high = hex_value(
                bytes
                    .next()
                    .ok_or_else(|| anyhow!("invalid percent-encoded path"))?,
            )?;
            let low = hex_value(
                bytes
                    .next()
                    .ok_or_else(|| anyhow!("invalid percent-encoded path"))?,
            )?;
            output.push(high * 16 + low);
        } else {
            output.push(byte);
        }
    }
    String::from_utf8(output).context("decoded request path must be UTF-8")
}

fn hex_value(value: u8) -> Result<u8> {
    match value {
        b'0'..=b'9' => Ok(value - b'0'),
        b'a'..=b'f' => Ok(value - b'a' + 10),
        b'A'..=b'F' => Ok(value - b'A' + 10),
        _ => bail!("invalid percent-encoded path"),
    }
}

fn mime_for(path: &Path) -> &'static str {
    match path.extension().and_then(|extension| extension.to_str()) {
        Some("html" | "htm") => "text/html; charset=utf-8",
        Some("css") => "text/css; charset=utf-8",
        Some("js" | "mjs") => "text/javascript; charset=utf-8",
        Some("json") => "application/json",
        Some("jsonl") => "application/x-ndjson",
        Some("svg") => "image/svg+xml",
        Some("png") => "image/png",
        Some("jpg" | "jpeg") => "image/jpeg",
        Some("gif") => "image/gif",
        Some("webp") => "image/webp",
        Some("pdf") => "application/pdf",
        Some("mp4") => "video/mp4",
        Some("webm") => "video/webm",
        Some("mp3") => "audio/mpeg",
        Some("wav") => "audio/wav",
        Some("txt" | "md" | "csv" | "tsv") => "text/plain; charset=utf-8",
        _ => "application/octet-stream",
    }
}

const fn shell_csp() -> &'static str {
    "default-src 'none'; script-src 'unsafe-inline'; frame-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:; media-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; connect-src 'self'; frame-ancestors 'none'"
}

fn authored_csp(origin: &str) -> String {
    format!(
        "default-src 'none'; connect-src {origin}; img-src {origin} data: blob:; media-src {origin} data: blob:; font-src {origin} data:; style-src {origin} 'unsafe-inline'; script-src {origin} 'unsafe-inline' blob:; worker-src blob:; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors {origin}"
    )
}

#[cfg(test)]
mod tests {
    use super::{inject_delivery_nonce, json_for_script, DELIVERY_NONCE_PLACEHOLDER};
    use serde_json::json;

    #[test]
    fn script_json_cannot_end_the_script_or_emit_javascript_line_separators() {
        let result = json_for_script(&json!([["\t</script>\u{2028}\u{2029}", "ok"]]));
        assert!(result.is_ok());
        let encoded = result.unwrap_or_default();
        assert!(!encoded.contains("</script>"));
        assert!(encoded.contains("\\t\\u003c/script\\u003e\\u2028\\u2029"));
    }

    #[test]
    fn delivery_nonce_injection_requires_exactly_one_placeholder() {
        let nonce = "a".repeat(64);
        let retained = format!("before{DELIVERY_NONCE_PLACEHOLDER}after");
        let injected = inject_delivery_nonce(retained.as_bytes(), &nonce);
        assert!(injected.is_ok());
        assert_eq!(
            String::from_utf8(injected.unwrap_or_default()).unwrap_or_default(),
            format!("before{nonce}after")
        );
        assert!(inject_delivery_nonce(b"no placeholder", &nonce).is_err());
        let duplicate = format!("{DELIVERY_NONCE_PLACEHOLDER}middle{DELIVERY_NONCE_PLACEHOLDER}");
        assert!(inject_delivery_nonce(duplicate.as_bytes(), &nonce).is_err());
    }
}
