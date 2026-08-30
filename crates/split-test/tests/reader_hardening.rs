//! Focused security and trust-boundary regressions for the derived-evidence reader.
#![allow(
    clippy::expect_used,
    clippy::indexing_slicing,
    clippy::multiple_crate_versions
)]

use serde_json::{json, Value};
use std::fs;
use std::io::{BufRead, BufReader, Read, Write};
use std::net::TcpStream;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Output, Stdio};
use std::sync::OnceLock;
use std::time::{SystemTime, UNIX_EPOCH};
use tempfile::TempDir;

fn binary() -> &'static Path {
    static BINARY: OnceLock<PathBuf> = OnceLock::new();
    BINARY.get_or_init(|| {
        let source = PathBuf::from(env!("CARGO_BIN_EXE_split-test"));
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("clock before unix epoch")
            .as_nanos();
        let target = std::env::temp_dir().join(format!(
            "split-test-reader-hardening-{}-{nonce}",
            std::process::id()
        ));
        fs::copy(&source, &target).expect("copy split-test binary");
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let mode = fs::metadata(&source)
                .expect("read split-test metadata")
                .permissions()
                .mode();
            fs::set_permissions(&target, fs::Permissions::from_mode(mode))
                .expect("preserve split-test permissions");
        }
        target
    })
}

fn seal_view() -> (TempDir, PathBuf, String) {
    let temp = tempfile::tempdir().expect("tempdir");
    let root = temp.path().join("view");
    fs::create_dir(&root).expect("create view root");
    fs::write(
        root.join("active.html"),
        b"<!doctype html><script>globalThis.authoredRan=true</script>\n",
    )
    .expect("write authored entrypoint");
    fs::write(root.join("source.json"), b"{\"result\":true}\n").expect("write source");
    fs::write(
        root.join("active-dependency.html"),
        b"<!doctype html><script>globalThis.dependencyRan=true</script>\n",
    )
    .expect("write active dependency");
    let spec = temp.path().join("view.json");
    fs::write(
        &spec,
        serde_json::to_vec(&json!({
            "schema": "derived-evidence-view.v1",
            "source_refs": [{"path": "source.json"}],
            "external_dependencies": [{"path": "active-dependency.html"}],
            "entrypoints": ["active.html"]
        }))
        .expect("serialize view spec"),
    )
    .expect("write view spec");

    let output = Command::new(binary())
        .args([
            "view",
            "seal",
            &root.to_string_lossy(),
            &spec.to_string_lossy(),
        ])
        .output()
        .expect("seal view");
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    let reader = fs::read_to_string(root.join(".derived-evidence-view/reader/index.html"))
        .expect("read generated reader");
    (temp, root, reader)
}

fn run(args: &[&str]) -> Output {
    Command::new(binary())
        .args(args)
        .output()
        .expect("run split-test")
}

fn canonical_json(value: &Value) -> Vec<u8> {
    let mut bytes = serde_json::to_vec(value).expect("serialize canonical JSON");
    bytes.push(b'\n');
    bytes
}

fn mutate_record_copies(root: &Path, field: &str, value: Value) {
    let control = root.join(".derived-evidence-view");
    let mut record: Value = serde_json::from_slice(
        &fs::read(control.join("record.json")).expect("read generated record"),
    )
    .expect("parse generated record");
    record[field] = value;
    let bytes = canonical_json(&record);
    fs::write(control.join("record.json"), &bytes).expect("mutate generated record");
    fs::write(control.join("reader/record.json"), &bytes).expect("mutate reader record copy");
}

fn spawn_server(root: &Path) -> (Child, String, String) {
    let mut child = Command::new(binary())
        .args([
            "view",
            "serve",
            &root.to_string_lossy(),
            "--bind",
            "127.0.0.1",
            "--port",
            "0",
        ])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn reader server");
    let mut line = String::new();
    BufReader::new(child.stdout.take().expect("server stdout"))
        .read_line(&mut line)
        .expect("read server URL");
    let value: Value = serde_json::from_str(&line).expect("parse server URL");
    let url = value["url"].as_str().expect("server URL").to_owned();
    let address = url
        .strip_prefix("http://")
        .and_then(|rest| rest.split('/').next())
        .expect("server address")
        .to_owned();
    (child, address, url)
}

fn request(address: &str, target: &str, host: &str, extra_headers: &str) -> Vec<u8> {
    let mut stream = TcpStream::connect(address).expect("connect reader server");
    write!(
        stream,
        "GET {target} HTTP/1.1\r\nHost: {host}\r\n{extra_headers}Connection: close\r\n\r\n"
    )
    .expect("write request");
    let mut response = Vec::new();
    stream.read_to_end(&mut response).expect("read response");
    response
}

fn terminate(child: &mut Child) {
    child.kill().expect("kill server");
    let _ = child.wait();
}

#[test]
fn authored_content_requires_helper_attestation_and_refs_stay_sandboxed() {
    let (_temp, root, reader) = seal_view();
    fs::write(
        root.join("active.html"),
        b"<!doctype html><script>globalThis.mutatedAuthoredRan=true</script>\n",
    )
    .expect("mutate authored entrypoint after seal");

    assert!(reader.contains("window.location.protocol !== 'http:'"));
    assert!(reader.contains("derived-evidence-view-delivery.v1"));
    assert!(reader.contains("fetch('delivery.json'"));
    assert!(reader.contains("delivery.capability !== match[1]"));
    assert!(reader.contains("delivery.nonce !== expectedDeliveryNonce"));
    assert_eq!(
        reader
            .matches("__SPLIT_TEST_HELPER_DELIVERY_NONCE_")
            .count(),
        1
    );
    assert!(reader.contains("!/^[0-9a-f]{64}$/.test(expectedDeliveryNonce)"));
    assert!(reader.contains("Static inspection mode"));
    assert!(reader.contains("requires the constrained loopback server"));
    assert!(!reader.contains("href=\"../../active.html\""));
    assert!(!reader.contains("href=\"../../source.json\""));
    assert!(!reader.contains("href=\"../../active-dependency.html\""));
    assert!(reader.contains("disabled data-served-src=\"../../active.html\""));
    assert!(reader.contains("data-served-src=\"../../active-dependency.html\""));
    assert!(reader.contains("authoredReady = false;"));
    assert!(reader.contains("Reader status: authored entrypoint reported ready."));
    assert!(!reader.contains("data.label"));
    assert!(!reader.contains("window.open("));
    assert!(reader.contains("navigateAuthored(allowedRefs.get(ref));"));
    assert!(reader.contains("frame.hidden = false;"));
    assert!(!root
        .join(".derived-evidence-view/reader/delivery.json")
        .exists());
}

#[test]
fn retained_delivery_marker_is_rejected_as_an_undeclared_control_file() {
    let (_temp, root, _reader) = seal_view();
    fs::write(
        root.join(".derived-evidence-view/reader/delivery.json"),
        b"{\"schema\":\"derived-evidence-view-delivery.v1\",\"capability\":\"forged\"}\n",
    )
    .expect("write forged retained delivery marker");

    let output = run(&["view", "verify", &root.to_string_lossy()]);
    assert!(!output.status.success());
    assert!(
        String::from_utf8_lossy(&output.stderr).contains("unexpected control entry"),
        "unexpected verification error: {}",
        String::from_utf8_lossy(&output.stderr)
    );
}

#[test]
fn generated_record_is_exact_for_verify_and_receipt() {
    for (field, value) in [
        ("reader_file", json!("reader/forged.html")),
        ("view_schema", json!("derived-evidence-view.forged")),
    ] {
        let (_temp, root, _reader) = seal_view();
        mutate_record_copies(&root, field, value);

        for command in ["verify", "receipt"] {
            let output = run(&["view", command, &root.to_string_lossy()]);
            assert!(
                !output.status.success(),
                "view {command} accepted mutated generated field {field}"
            );
            assert!(
                String::from_utf8_lossy(&output.stderr).contains("generated seal record"),
                "unexpected view {command} error: {}",
                String::from_utf8_lossy(&output.stderr)
            );
        }
    }
}

#[test]
fn served_record_route_rechecks_the_exact_generated_record() {
    let (_temp, root, _reader) = seal_view();
    let (mut child, address, url) = spawn_server(&root);
    let reader_target = url
        .strip_prefix(&format!("http://{address}"))
        .expect("reader target");
    let record_target = reader_target
        .strip_suffix("index.html")
        .map(|prefix| format!("{prefix}record.json"))
        .expect("reader record target");

    mutate_record_copies(&root, "reader_file", json!("reader/forged.html"));
    let response =
        String::from_utf8_lossy(&request(&address, &record_target, &address, "")).into_owned();
    assert!(response.starts_with("HTTP/1.1 400 Bad Request"));
    assert!(response.contains("generated seal record"));

    terminate(&mut child);
}

#[test]
fn loopback_server_rejects_foreign_hosts_and_discloses_non_seekable_delivery() {
    let (_temp, root, retained_reader) = seal_view();
    let (mut child, address, url) = spawn_server(&root);
    let target = url
        .strip_prefix(&format!("http://{address}"))
        .expect("reader target");
    let capability = target
        .strip_prefix('/')
        .and_then(|value| value.split('/').next())
        .expect("delivery capability");
    let delivery_target = target
        .strip_suffix("index.html")
        .map(|prefix| format!("{prefix}delivery.json"))
        .expect("delivery target");

    let rejected =
        String::from_utf8_lossy(&request(&address, target, "attacker.invalid", "")).into_owned();
    assert!(rejected.starts_with("HTTP/1.1 400 Bad Request"));

    let accepted = String::from_utf8_lossy(&request(&address, target, &address, "")).into_owned();
    assert!(accepted.starts_with("HTTP/1.1 200 OK"));
    assert!(accepted.contains("Content-Security-Policy:"));
    assert!(accepted.contains("frame-ancestors 'none'"));
    assert!(accepted.contains("Accept-Ranges: none"));
    let nonce_prefix = "const expectedDeliveryNonce = '";
    let nonce_start = accepted
        .find(nonce_prefix)
        .map(|index| index + nonce_prefix.len())
        .expect("served delivery nonce");
    let nonce = accepted
        .get(nonce_start..nonce_start + 64)
        .expect("64-character served delivery nonce");
    assert!(nonce.bytes().all(|byte| byte.is_ascii_hexdigit()));
    assert!(!retained_reader.contains(nonce));
    assert!(retained_reader.contains("__SPLIT_TEST_HELPER_DELIVERY_NONCE_"));

    let delivery =
        String::from_utf8_lossy(&request(&address, &delivery_target, &address, "")).into_owned();
    assert!(delivery.starts_with("HTTP/1.1 200 OK"));
    assert!(delivery.contains("\"schema\":\"derived-evidence-view-delivery.v1\""));
    assert!(delivery.contains(&format!("\"capability\":\"{capability}\"")));
    assert!(delivery.contains(&format!("\"nonce\":\"{nonce}\"")));

    let range =
        String::from_utf8_lossy(&request(&address, target, &address, "Range: bytes=0-9\r\n"))
            .into_owned();
    assert!(range.starts_with("HTTP/1.1 200 OK"));
    assert!(!range.starts_with("HTTP/1.1 206 Partial Content"));
    assert!(range.contains("Accept-Ranges: none"));

    terminate(&mut child);
}
