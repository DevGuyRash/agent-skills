use anyhow::{anyhow, bail, Context, Result};
use rand::random;
use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
#[cfg(unix)]
use std::fs::File;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::{Component, Path, PathBuf};

pub(crate) const CAPTURE_SCHEMA: &str = "portable-content-manifest.v1";
pub(crate) const CAPTURE_PROFILE: &str =
    "relative-topology-regular-bytes-empty-directories-symlink-targets-executable-bits.v1";

#[derive(Debug)]
pub(crate) struct RawJson {
    pub bytes: Vec<u8>,
    pub value: Value,
    pub digest: String,
}

pub(crate) fn canonical_bytes(value: &Value) -> Result<Vec<u8>> {
    let mut bytes = serde_json::to_vec(value).context("serialize canonical JSON")?;
    bytes.push(b'\n');
    Ok(bytes)
}

pub(crate) fn digest_bytes(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

pub(crate) fn digest_file(path: &Path) -> Result<String> {
    let bytes = fs::read(path).with_context(|| format!("read {}", path.display()))?;
    Ok(digest_bytes(&bytes))
}

pub(crate) fn read_raw_json(path: &Path, expected_schema: &str, label: &str) -> Result<RawJson> {
    let metadata = fs::symlink_metadata(path)
        .with_context(|| format!("read {label} at {}", path.display()))?;
    if !metadata.file_type().is_file() {
        bail!("{label} must be a regular file");
    }
    let bytes = fs::read(path).with_context(|| format!("read {label}"))?;
    let value: Value = serde_json::from_slice(&bytes).with_context(|| format!("parse {label}"))?;
    let object = value
        .as_object()
        .ok_or_else(|| anyhow!("{label} must be a JSON object"))?;
    let schema = string_from(object, "schema", label)?;
    if schema != expected_schema {
        bail!("unsupported {label} schema {schema:?}; expected {expected_schema}");
    }
    let digest = digest_bytes(&bytes);
    Ok(RawJson {
        bytes,
        value,
        digest,
    })
}

pub(crate) fn object<'a>(value: &'a Value, label: &str) -> Result<&'a Map<String, Value>> {
    value
        .as_object()
        .ok_or_else(|| anyhow!("{label} must be a JSON object"))
}

pub(crate) fn string_from<'a>(
    object: &'a Map<String, Value>,
    key: &str,
    label: &str,
) -> Result<&'a str> {
    object
        .get(key)
        .and_then(Value::as_str)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| anyhow!("{label}.{key} must be a non-empty string"))
}

pub(crate) fn array_from<'a>(
    object: &'a Map<String, Value>,
    key: &str,
    label: &str,
) -> Result<&'a [Value]> {
    object
        .get(key)
        .and_then(Value::as_array)
        .map(Vec::as_slice)
        .ok_or_else(|| anyhow!("{label}.{key} must be an array"))
}

pub(crate) fn bool_from(object: &Map<String, Value>, key: &str, label: &str) -> Result<bool> {
    object
        .get(key)
        .and_then(Value::as_bool)
        .ok_or_else(|| anyhow!("{label}.{key} must be a boolean"))
}

pub(crate) fn safe_id(value: &str, label: &str) -> Result<String> {
    if value.is_empty()
        || value.len() > 128
        || value == "."
        || value == ".."
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b'-'))
    {
        bail!("{label} must use 1-128 ASCII letters, digits, dot, underscore, or hyphen");
    }
    Ok(value.to_owned())
}

pub(crate) fn absolute_existing_root(value: &Path) -> Result<PathBuf> {
    if !value.is_absolute() {
        bail!("ROOT must be an absolute path");
    }
    reject_symlink_components(value, "ROOT")?;
    let metadata = fs::metadata(value).context("ROOT does not exist")?;
    if !metadata.is_dir() {
        bail!("ROOT must be a directory");
    }
    value.canonicalize().context("resolve ROOT")
}

pub(crate) fn absolute_empty_root(value: &Path) -> Result<PathBuf> {
    let root = absolute_existing_root(value)?;
    if fs::read_dir(&root)
        .context("inspect ROOT")?
        .next()
        .is_some()
    {
        bail!("ROOT must be empty");
    }
    Ok(root)
}

pub(crate) fn reject_symlink_components(path: &Path, label: &str) -> Result<()> {
    let mut current = PathBuf::new();
    for component in path.components() {
        current.push(component.as_os_str());
        match fs::symlink_metadata(&current) {
            Ok(metadata) if metadata.file_type().is_symlink() => {
                bail!(
                    "{label} contains a symlink component: {}",
                    current.display()
                );
            }
            Ok(_) => {}
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
            Err(error) => return Err(error).with_context(|| format!("inspect {label}")),
        }
    }
    Ok(())
}

pub(crate) fn relative_path(value: &str, label: &str) -> Result<PathBuf> {
    let path = Path::new(value);
    if path.is_absolute() || value.is_empty() {
        bail!("{label} must be a non-empty relative path");
    }
    let mut clean = PathBuf::new();
    for component in path.components() {
        match component {
            Component::Normal(part) => clean.push(part),
            Component::CurDir => {}
            Component::ParentDir | Component::RootDir | Component::Prefix(_) => {
                bail!("{label} must stay inside its package");
            }
        }
    }
    if clean.as_os_str().is_empty() {
        bail!("{label} must identify a package path");
    }
    Ok(clean)
}

pub(crate) fn atomic_write(path: &Path, bytes: &[u8], executable: bool) -> Result<()> {
    let parent = path
        .parent()
        .ok_or_else(|| anyhow!("output path has no parent"))?;
    fs::create_dir_all(parent).with_context(|| format!("create {}", parent.display()))?;
    let name = path
        .file_name()
        .and_then(|name| name.to_str())
        .ok_or_else(|| anyhow!("output filename must be UTF-8"))?;
    let temporary = parent.join(format!(".{name}.tmp-{:016x}", random::<u64>()));
    let result = (|| -> Result<()> {
        let mut file = OpenOptions::new()
            .create_new(true)
            .write(true)
            .open(&temporary)
            .with_context(|| format!("create {}", temporary.display()))?;
        file.write_all(bytes).context("write temporary file")?;
        file.sync_all().context("sync temporary file")?;
        set_executable(&temporary, executable)?;
        fs::rename(&temporary, path).with_context(|| format!("commit {}", path.display()))?;
        sync_dir(parent)?;
        Ok(())
    })();
    if result.is_err() {
        let _ = fs::remove_file(&temporary);
    }
    result
}

pub(crate) fn atomic_write_json(path: &Path, value: &Value) -> Result<()> {
    atomic_write(path, &canonical_bytes(value)?, false)
}

fn sync_dir(path: &Path) -> Result<()> {
    #[cfg(not(unix))]
    let _ = path;
    #[cfg(unix)]
    {
        File::open(path)
            .with_context(|| format!("open directory {}", path.display()))?
            .sync_all()
            .with_context(|| format!("sync directory {}", path.display()))?;
    }
    Ok(())
}

pub(crate) fn set_executable(path: &Path, executable: bool) -> Result<()> {
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mode = if executable { 0o755 } else { 0o644 };
        fs::set_permissions(path, fs::Permissions::from_mode(mode))
            .with_context(|| format!("set portable mode on {}", path.display()))?;
    }
    #[cfg(not(unix))]
    let _ = (path, executable);
    Ok(())
}

fn executable(metadata: &fs::Metadata) -> bool {
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        metadata.permissions().mode() & 0o111 != 0
    }
    #[cfg(not(unix))]
    {
        let _ = metadata;
        false
    }
}

pub(crate) fn capture_tree(root: &Path, excluded_top_level: &[&str]) -> Result<Value> {
    let root = absolute_existing_root(root)?;
    let excluded = excluded_top_level
        .iter()
        .map(std::string::ToString::to_string)
        .collect::<BTreeSet<_>>();
    let mut entries = Vec::new();
    capture_directory(&root, Path::new(""), &excluded, &mut entries)?;
    Ok(json!({
        "schema": CAPTURE_SCHEMA,
        "profile": CAPTURE_PROFILE,
        "entries": entries
    }))
}

fn capture_directory(
    root: &Path,
    relative: &Path,
    excluded: &BTreeSet<String>,
    entries: &mut Vec<Value>,
) -> Result<()> {
    let directory = root.join(relative);
    let mut children = fs::read_dir(&directory)
        .with_context(|| format!("read {}", directory.display()))?
        .collect::<std::result::Result<Vec<_>, _>>()?;
    children.sort_by_key(fs::DirEntry::file_name);
    for child in children {
        let name = child
            .file_name()
            .into_string()
            .map_err(|_| anyhow!("portable paths must be valid UTF-8"))?;
        if relative.as_os_str().is_empty() && excluded.contains(&name) {
            continue;
        }
        let child_relative = relative.join(&name);
        let path_text = path_text(&child_relative)?;
        let metadata = fs::symlink_metadata(child.path())
            .with_context(|| format!("inspect {}", child.path().display()))?;
        let file_type = metadata.file_type();
        if file_type.is_dir() {
            entries.push(json!({"path": path_text, "kind": "directory"}));
            capture_directory(root, &child_relative, excluded, entries)?;
        } else if file_type.is_file() {
            entries.push(json!({
                "path": path_text,
                "kind": "file",
                "sha256": digest_file(&child.path())?,
                "size": metadata.len(),
                "executable": executable(&metadata)
            }));
        } else if file_type.is_symlink() {
            let target = fs::read_link(child.path())
                .with_context(|| format!("read symlink {}", child.path().display()))?;
            validate_symlink_target(&child_relative, &target)?;
            let target_text = target
                .to_str()
                .ok_or_else(|| anyhow!("portable symlink targets must be valid UTF-8"))?;
            entries.push(json!({"path": path_text, "kind": "symlink", "target": target_text}));
        } else {
            bail!("unsupported special file: {}", child.path().display());
        }
    }
    Ok(())
}

fn path_text(path: &Path) -> Result<String> {
    let parts = path
        .components()
        .map(|component| match component {
            Component::Normal(value) => value
                .to_str()
                .map(str::to_owned)
                .ok_or_else(|| anyhow!("portable paths must be valid UTF-8")),
            _ => Err(anyhow!("portable paths must be relative and normalized")),
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(parts.join("/"))
}

fn validate_symlink_target(link_relative: &Path, target: &Path) -> Result<()> {
    if target.is_absolute() {
        bail!("absolute symlink target is not portable");
    }
    let parent = link_relative.parent().unwrap_or_else(|| Path::new(""));
    let mut depth = parent.components().count();
    for component in target.components() {
        match component {
            Component::Normal(_) => depth += 1,
            Component::CurDir => {}
            Component::ParentDir if depth > 0 => depth -= 1,
            Component::ParentDir => bail!("symlink target escapes the captured root"),
            Component::RootDir | Component::Prefix(_) => {
                bail!("symlink target escapes the captured root");
            }
        }
    }
    Ok(())
}

pub(crate) fn manifest_digest(manifest: &Value) -> Result<String> {
    Ok(digest_bytes(&canonical_bytes(manifest)?))
}

pub(crate) fn verify_tree(root: &Path, excluded: &[&str], expected: &Value) -> Result<()> {
    let actual = capture_tree(root, excluded)?;
    if &actual != expected {
        bail!("portable content mutation detected");
    }
    Ok(())
}

pub(crate) fn materialize_tree(source: &Path, destination: &Path, manifest: &Value) -> Result<()> {
    if destination.exists() {
        bail!("destination already exists: {}", destination.display());
    }
    fs::create_dir_all(destination).with_context(|| format!("create {}", destination.display()))?;
    let entries = object(manifest, "capture manifest")?
        .get("entries")
        .and_then(Value::as_array)
        .ok_or_else(|| anyhow!("capture manifest entries are invalid"))?;
    for entry in entries {
        let fields = object(entry, "capture entry")?;
        let relative = relative_path(
            string_from(fields, "path", "capture entry")?,
            "capture path",
        )?;
        let source_path = source.join(&relative);
        let destination_path = destination.join(&relative);
        match string_from(fields, "kind", "capture entry")? {
            "directory" => fs::create_dir_all(&destination_path)
                .with_context(|| format!("create {}", destination_path.display()))?,
            "file" => {
                let parent = destination_path
                    .parent()
                    .ok_or_else(|| anyhow!("file destination has no parent"))?;
                fs::create_dir_all(parent)?;
                fs::copy(&source_path, &destination_path).with_context(|| {
                    format!(
                        "copy {} to {}",
                        source_path.display(),
                        destination_path.display()
                    )
                })?;
                let expected_executable = fields
                    .get("executable")
                    .and_then(Value::as_bool)
                    .ok_or_else(|| anyhow!("capture file executable flag is invalid"))?;
                set_executable(&destination_path, expected_executable)?;
            }
            "symlink" => {
                let parent = destination_path
                    .parent()
                    .ok_or_else(|| anyhow!("symlink destination has no parent"))?;
                fs::create_dir_all(parent)?;
                let target = Path::new(string_from(fields, "target", "capture symlink")?);
                create_symlink(target, &destination_path, &source_path)?;
            }
            other => bail!("unsupported capture entry kind {other:?}"),
        }
    }
    Ok(())
}

#[cfg(unix)]
fn create_symlink(target: &Path, destination: &Path, _source: &Path) -> Result<()> {
    std::os::unix::fs::symlink(target, destination)
        .with_context(|| format!("create symlink {}", destination.display()))
}

#[cfg(windows)]
fn create_symlink(target: &Path, destination: &Path, source: &Path) -> Result<()> {
    if fs::metadata(source)
        .map(|metadata| metadata.is_dir())
        .unwrap_or(false)
    {
        std::os::windows::fs::symlink_dir(target, destination)
            .with_context(|| format!("create directory symlink {}", destination.display()))
    } else {
        std::os::windows::fs::symlink_file(target, destination)
            .with_context(|| format!("create file symlink {}", destination.display()))
    }
}

pub(crate) fn copy_external_reference(source: &Path, destination: &Path) -> Result<Value> {
    let metadata = fs::symlink_metadata(source)
        .with_context(|| format!("inspect effective input {}", source.display()))?;
    if metadata.file_type().is_symlink() || (!metadata.is_file() && !metadata.is_dir()) {
        bail!("effective input must be a regular file or directory");
    }
    fs::create_dir_all(destination)?;
    let payload = destination.join("payload");
    if metadata.is_file() {
        fs::create_dir(&payload)?;
        let name = source
            .file_name()
            .ok_or_else(|| anyhow!("effective input has no filename"))?;
        fs::copy(source, payload.join(name))?;
    } else {
        let manifest = capture_tree(source, &[])?;
        materialize_tree(source, &payload, &manifest)?;
    }
    let manifest = capture_tree(&payload, &[])?;
    atomic_write_json(&destination.join("manifest.json"), &manifest)?;
    Ok(manifest)
}
