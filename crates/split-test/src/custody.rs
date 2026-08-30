use crate::util::{
    absolute_empty_root, absolute_existing_root, array_from, atomic_write, atomic_write_json,
    bool_from, canonical_bytes, capture_tree, copy_external_reference, digest_bytes, digest_file,
    manifest_digest, materialize_tree, object, read_raw_json, reject_symlink_components,
    relative_path, safe_id, string_from, verify_tree, RawJson,
};
use anyhow::{anyhow, bail, Context, Result};
use fs2::FileExt;
use rand::random;
use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
use std::fs::{self, File, OpenOptions};
use std::path::{Path, PathBuf};

const CONTROL: &str = ".split-testing";
const WORKSPACE_SCHEMA: &str = "split-testing-workspace.v2";
const WORKSPACE_CONTRACT: &str = "role-neutral-v2";
const COMMITMENT_SCHEMA: &str = "split-testing-commitment.v2";
const WORK_SET_SCHEMA: &str = "split-testing-work-set.v2";
const WORK_SCHEMA: &str = "split-testing-work.v2";
const TERMINAL_SCHEMA: &str = "split-testing-terminal.v2";
const CLOSURE_SCHEMA: &str = "split-testing-work-closure.v2";
const PUBLICATION_SCHEMA: &str = "split-testing-publication.v2";
const REVEAL_SCHEMA: &str = "split-testing-reveal.v2";
const EVENT_SCHEMA: &str = "split-testing-event.v2";
const PENDING_EVENT_SCHEMA: &str = "split-testing-pending-event.v2";
const RECEIPT_SCHEMA: &str = "split-testing-receipt.v2";
const ZERO_DIGEST: &str = "0000000000000000000000000000000000000000000000000000000000000000";
const TERMINAL_EVENTS: &[&str] = &[
    "returned",
    "spawn-failed",
    "timed-out",
    "signaled",
    "controller-aborted",
    "lost",
];

#[derive(Debug)]
pub(crate) struct Workspace {
    pub root: PathBuf,
    pub control: PathBuf,
    pub metadata: Value,
}

struct LockGuard {
    file: File,
}

struct PendingEvent {
    path: PathBuf,
    kind: String,
    scope_refs: Vec<String>,
    record_ref: String,
    record_digest: String,
    content_digest: String,
}

impl PendingEvent {
    fn begin(
        workspace: &Workspace,
        kind: &str,
        scope_refs: &[String],
        record_ref: &str,
        record_digest: &str,
        content_digest: &str,
    ) -> Result<Self> {
        let identity = digest_bytes(record_ref.as_bytes());
        let path = workspace
            .control
            .join("pending")
            .join(format!("{identity}.json"));
        let value = json!({
            "schema": PENDING_EVENT_SCHEMA,
            "kind": kind,
            "scope_refs": scope_refs,
            "record_ref": record_ref,
            "record_digest": record_digest,
            "content_digest": content_digest
        });
        if path.exists() {
            let existing = read_json(&path, "pending event")?;
            if existing != value {
                bail!("pending event identity already exists with different content");
            }
        } else {
            atomic_write_json(&path, &value)?;
        }
        Ok(Self {
            path,
            kind: kind.to_owned(),
            scope_refs: scope_refs.to_vec(),
            record_ref: record_ref.to_owned(),
            record_digest: record_digest.to_owned(),
            content_digest: content_digest.to_owned(),
        })
    }

    fn finish(self, workspace: &Workspace) -> Result<()> {
        append_event(
            workspace,
            &self.kind,
            &self.scope_refs,
            &self.record_ref,
            &self.record_digest,
            &self.content_digest,
        )?;
        fs::remove_file(&self.path).context("clear completed pending event")
    }
}

impl Drop for LockGuard {
    fn drop(&mut self) {
        let _ = FileExt::unlock(&self.file);
    }
}

fn lock(workspace: &Workspace) -> Result<LockGuard> {
    let path = workspace.control.join("lock");
    let file = OpenOptions::new()
        .create(true)
        .truncate(false)
        .read(true)
        .write(true)
        .open(&path)
        .with_context(|| format!("open controller lock {}", path.display()))?;
    file.lock_exclusive().context("acquire controller lock")?;
    Ok(LockGuard { file })
}

pub(crate) fn init(root_arg: &Path) -> Result<Value> {
    if root_arg.is_absolute() && root_arg.join(CONTROL).join("workspace.json").is_file() {
        let workspace = load(root_arg)?;
        let _guard = lock(&workspace)?;
        recover_trailing_event(&workspace)?;
        return status_value(&workspace);
    }
    let root = absolute_empty_root(root_arg)?;
    let control = root.join(CONTROL);
    fs::create_dir(&control).context("create custody directory")?;
    for relative in ["events", "records", "objects", "pending"] {
        fs::create_dir(control.join(relative))?;
    }
    fs::create_dir(root.join("workspaces"))?;
    fs::create_dir(root.join("publications"))?;
    fs::create_dir(root.join("reveals"))?;
    set_private_directory(&control)?;

    let mut secret = Vec::with_capacity(32);
    for _ in 0..4 {
        secret.extend_from_slice(&random::<u64>().to_le_bytes());
    }
    atomic_write(&control.join("secret"), &secret, false)?;
    set_private_file(&control.join("secret"))?;
    let metadata = json!({
        "schema": WORKSPACE_SCHEMA,
        "contract": WORKSPACE_CONTRACT,
        "workspace_id": digest_bytes(&secret),
        "secret_digest": digest_bytes(&secret)
    });
    let workspace = Workspace {
        root,
        control,
        metadata,
    };
    let _guard = lock(&workspace)?;
    let metadata_digest = digest_bytes(&canonical_bytes(&workspace.metadata)?);
    let pending = PendingEvent::begin(
        &workspace,
        "workspace-initialized",
        &[],
        ".split-testing/workspace.json",
        &metadata_digest,
        workspace
            .metadata
            .get("workspace_id")
            .and_then(Value::as_str)
            .ok_or_else(|| anyhow!("workspace identity missing"))?,
    )?;
    atomic_write_json(
        &workspace.control.join("workspace.json"),
        &workspace.metadata,
    )?;
    pending.finish(&workspace)?;
    status_value(&workspace)
}

pub(crate) fn load(root_arg: &Path) -> Result<Workspace> {
    let root = absolute_existing_root(root_arg)?;
    let control = root.join(CONTROL);
    let metadata_path = control.join("workspace.json");
    let bytes = fs::read(&metadata_path).map_err(|_| {
        anyhow!(
            "unsupported or uninitialized split-testing workspace at {}",
            root.display()
        )
    })?;
    let metadata: Value = serde_json::from_slice(&bytes)
        .map_err(|_| anyhow!("unsupported split-testing workspace metadata"))?;
    let fields = object(&metadata, "workspace metadata")?;
    if fields.get("schema").and_then(Value::as_str) != Some(WORKSPACE_SCHEMA)
        || fields.get("contract").and_then(Value::as_str) != Some(WORKSPACE_CONTRACT)
        || control.join("rounds").exists()
    {
        bail!("unsupported split-testing workspace contract; no legacy reader is provided");
    }
    let secret = fs::read(control.join("secret")).context("read workspace secret")?;
    if fields.get("secret_digest").and_then(Value::as_str) != Some(&digest_bytes(&secret)) {
        bail!("workspace secret digest mismatch");
    }
    Ok(Workspace {
        root,
        control,
        metadata,
    })
}

pub(crate) fn add_commitment(root: &Path, spec_path: &Path) -> Result<Value> {
    let workspace = load(root)?;
    let _guard = lock(&workspace)?;
    recover_trailing_event(&workspace)?;
    verify_workspace(&workspace)?;
    let raw = read_raw_json(spec_path, COMMITMENT_SCHEMA, "commitment specification")?;
    let fields = object(&raw.value, "commitment specification")?;
    let commitment_id = safe_id(
        string_from(fields, "commitment_id", "commitment specification")?,
        "commitment_id",
    )?;
    let record_dir = workspace
        .control
        .join("records/commitments")
        .join(&commitment_id);
    let record_ref = relative_to_root(&workspace, &record_dir.join("record.json"))?;
    let record = json!({
        "schema": COMMITMENT_SCHEMA,
        "commitment_id": commitment_id,
        "spec_digest": raw.digest,
        "raw_file": "spec.json"
    });
    let record_digest = digest_bytes(&canonical_bytes(&record)?);
    let pending = if record_dir.exists() {
        None
    } else {
        Some(PendingEvent::begin(
            &workspace,
            "commitment-added",
            &[commitment_scope(&commitment_id)],
            &record_ref,
            &record_digest,
            &raw.digest,
        )?)
    };
    let created = commit_raw_record(&record_dir, &raw, &record)?;
    if let Some(pending) = pending {
        pending.finish(&workspace)?;
    }
    Ok(json!({
        "schema": COMMITMENT_SCHEMA,
        "commitment_id": commitment_id,
        "spec_digest": raw.digest,
        "created": created
    }))
}

pub(crate) fn add_work_set(root: &Path, spec_path: &Path) -> Result<Value> {
    let workspace = load(root)?;
    let _guard = lock(&workspace)?;
    recover_trailing_event(&workspace)?;
    verify_workspace(&workspace)?;
    let raw = read_raw_json(spec_path, WORK_SET_SCHEMA, "work-set specification")?;
    let fields = object(&raw.value, "work-set specification")?;
    let set_id = safe_id(
        string_from(fields, "set_id", "work-set specification")?,
        "set_id",
    )?;
    let commitments = parse_id_list(
        array_from(fields, "commitment_refs", "work-set specification")?,
        "commitment_refs",
    )?;
    if commitments.is_empty() {
        bail!("work-set specification.commitment_refs must not be empty");
    }
    require_commitments(&workspace, &commitments)?;
    let units = parse_units(array_from(fields, "units", "work-set specification")?)?;
    if units.is_empty() {
        bail!("work-set specification.units must not be empty");
    }
    let record_dir = workspace.control.join("records/work-sets").join(&set_id);
    let record_ref = relative_to_root(&workspace, &record_dir.join("record.json"))?;
    let record = json!({
        "schema": WORK_SET_SCHEMA,
        "set_id": set_id,
        "spec_digest": raw.digest,
        "raw_file": "spec.json",
        "commitment_refs": commitments,
        "units": units
    });
    let record_digest = digest_bytes(&canonical_bytes(&record)?);
    let pending = if record_dir.exists() {
        None
    } else {
        Some(PendingEvent::begin(
            &workspace,
            "work-set-added",
            &[work_set_scope(&set_id)],
            &record_ref,
            &record_digest,
            &raw.digest,
        )?)
    };
    let created = commit_raw_record(&record_dir, &raw, &record)?;
    if let Some(pending) = pending {
        pending.finish(&workspace)?;
    }
    Ok(json!({
        "schema": WORK_SET_SCHEMA,
        "set_id": set_id,
        "spec_digest": raw.digest,
        "created": created
    }))
}

pub(crate) fn prepare_work(
    root: &Path,
    set_arg: &str,
    unit_arg: &str,
    spec_path: &Path,
) -> Result<Value> {
    let workspace = load(root)?;
    let _guard = lock(&workspace)?;
    recover_trailing_event(&workspace)?;
    verify_workspace(&workspace)?;
    let set_id = safe_id(set_arg, "SET_ID")?;
    let unit_id = safe_id(unit_arg, "UNIT_ID")?;
    let set_record = load_record(
        &workspace.control.join("records/work-sets").join(&set_id),
        "work set",
    )?;
    let set_units = string_array_field(&set_record, "units", "work-set record")?;
    if !set_units.contains(&unit_id) {
        bail!("UNIT_ID is not frozen in work set {set_id}");
    }
    let raw = read_raw_json(spec_path, WORK_SCHEMA, "work specification")?;
    let fields = object(&raw.value, "work specification")?;
    require_matching_id(fields, "set_id", &set_id, "work specification")?;
    require_matching_id(fields, "unit_id", &unit_id, "work specification")?;
    let commitments = parse_id_list(
        array_from(fields, "commitment_refs", "work specification")?,
        "commitment_refs",
    )?;
    require_commitments(&workspace, &commitments)?;
    let set_commitments = string_array_field(&set_record, "commitment_refs", "work-set record")?;
    if !set_commitments
        .iter()
        .all(|item| commitments.contains(item))
    {
        bail!("work specification must bind every work-set commitment");
    }

    let record_dir = workspace
        .control
        .join("records/work")
        .join(&set_id)
        .join(&unit_id);
    let work_dir = workspace
        .root
        .join("workspaces")
        .join(&set_id)
        .join(&unit_id);
    if record_dir.exists() {
        let existing = load_record(&record_dir, "prepared work")?;
        ensure_same_digest(&existing, &raw.digest, "prepared work")?;
        if !work_dir.is_dir() {
            bail!("prepared workspace is missing");
        }
        return Ok(json!({
            "schema": WORK_SCHEMA,
            "set_id": set_id,
            "unit_id": unit_id,
            "spec_digest": raw.digest,
            "workspace": work_dir,
            "created": false
        }));
    }
    if workspace
        .control
        .join("records/closures")
        .join(&set_id)
        .join("record.json")
        .is_file()
    {
        bail!("work set is already closed; first-time work preparation is forbidden");
    }
    if work_dir.exists() {
        if fs::read_dir(&work_dir)?.next().is_some() {
            bail!("non-empty isolated workspace exists without a custody record");
        }
        fs::remove_dir(&work_dir).context("remove interrupted empty workspace")?;
    }

    let record_ref = relative_to_root(&workspace, &record_dir.join("record.json"))?;
    let parent = record_dir
        .parent()
        .ok_or_else(|| anyhow!("work record has no parent"))?;
    fs::create_dir_all(parent)?;
    let stage = parent.join(format!(".prepare-{unit_id}-{:016x}", random::<u64>()));
    fs::create_dir(&stage)?;
    let prepare_result = (|| -> Result<(Value, PendingEvent)> {
        atomic_write(&stage.join("spec.json"), &raw.bytes, false)?;
        let effective_inputs = capture_effective_inputs(fields, spec_path, &stage)?;
        let record = json!({
            "schema": WORK_SCHEMA,
            "set_id": set_id,
            "unit_id": unit_id,
            "spec_digest": raw.digest,
            "raw_file": "spec.json",
            "commitment_refs": commitments,
            "effective_inputs": effective_inputs,
            "workspace": relative_to_root(&workspace, &work_dir)?
        });
        atomic_write_json(&stage.join("record.json"), &record)?;
        let record_digest = digest_bytes(&canonical_bytes(&record)?);
        let pending = PendingEvent::begin(
            &workspace,
            "work-prepared",
            &[work_set_scope(&set_id), work_scope(&set_id, &unit_id)],
            &record_ref,
            &record_digest,
            &raw.digest,
        )?;
        fs::create_dir_all(
            work_dir
                .parent()
                .ok_or_else(|| anyhow!("work directory has no parent"))?,
        )?;
        fs::create_dir(&work_dir).context("create isolated workspace")?;
        if let Err(error) = fs::rename(&stage, &record_dir).context("commit prepared-work record") {
            let _ = fs::remove_dir(&work_dir);
            return Err(error);
        }
        Ok((record, pending))
    })();
    if prepare_result.is_err() {
        let _ = fs::remove_dir_all(&stage);
    }
    let (_record, pending) = prepare_result?;
    pending.finish(&workspace)?;
    Ok(json!({
        "schema": WORK_SCHEMA,
        "set_id": set_id,
        "unit_id": unit_id,
        "spec_digest": raw.digest,
        "workspace": work_dir,
        "created": true
    }))
}

pub(crate) fn seal_work(
    root: &Path,
    set_arg: &str,
    unit_arg: &str,
    terminal_path: &Path,
) -> Result<Value> {
    let workspace = load(root)?;
    let _guard = lock(&workspace)?;
    recover_trailing_event(&workspace)?;
    verify_workspace(&workspace)?;
    let set_id = safe_id(set_arg, "SET_ID")?;
    let unit_id = safe_id(unit_arg, "UNIT_ID")?;
    let record_dir = workspace
        .control
        .join("records/work")
        .join(&set_id)
        .join(&unit_id);
    let _prepared = load_record(&record_dir, "prepared work")?;
    let raw = read_raw_json(terminal_path, TERMINAL_SCHEMA, "terminal record")?;
    let fields = object(&raw.value, "terminal record")?;
    let event = string_from(fields, "event", "terminal record")?;
    if !TERMINAL_EVENTS.contains(&event) {
        bail!(
            "terminal record.event must be a mechanical event: {}",
            TERMINAL_EVENTS.join(", ")
        );
    }
    let seal_dir = record_dir.join("seal");
    let retained_payload = workspace
        .control
        .join("objects/sealed")
        .join(&set_id)
        .join(&unit_id)
        .join("payload");
    if seal_dir.exists() {
        let record = load_record(&seal_dir, "sealed work")?;
        ensure_same_field(&record, "terminal_digest", &raw.digest, "sealed work")?;
        let manifest = read_json(&seal_dir.join("manifest.json"), "work manifest")?;
        let manifest_hash = manifest_digest(&manifest)?;
        ensure_same_field(&record, "manifest_digest", &manifest_hash, "sealed work")?;
        verify_tree(&retained_payload, &[], &manifest)?;
        return Ok(json!({
            "schema": TERMINAL_SCHEMA,
            "set_id": set_id,
            "unit_id": unit_id,
            "terminal_digest": raw.digest,
            "manifest_digest": manifest_hash,
            "created": false
        }));
    }
    if workspace
        .control
        .join("records/closures")
        .join(&set_id)
        .join("record.json")
        .is_file()
    {
        bail!("work set is already closed; first-time work sealing is forbidden");
    }
    let work_dir = workspace
        .root
        .join("workspaces")
        .join(&set_id)
        .join(&unit_id);
    let manifest = capture_tree(&work_dir, &[])?;
    let manifest_hash = manifest_digest(&manifest)?;
    let record = json!({
        "schema": TERMINAL_SCHEMA,
        "set_id": set_id,
        "unit_id": unit_id,
        "terminal_digest": raw.digest,
        "manifest_digest": manifest_hash,
        "raw_file": "terminal.json",
        "manifest_file": "manifest.json",
        "workspace": relative_to_root(&workspace, &work_dir)?,
        "payload_root": relative_to_root(&workspace, &retained_payload)?
    });
    let record_digest = digest_bytes(&canonical_bytes(&record)?);
    let record_ref = relative_to_root(&workspace, &seal_dir.join("record.json"))?;
    let pending = PendingEvent::begin(
        &workspace,
        "work-sealed",
        &[work_set_scope(&set_id), work_scope(&set_id, &unit_id)],
        &record_ref,
        &record_digest,
        &manifest_hash,
    )?;
    let retained_parent = retained_payload
        .parent()
        .ok_or_else(|| anyhow!("retained payload has no parent"))?;
    if retained_parent.exists() {
        verify_tree(&retained_payload, &[], &manifest)?;
    } else {
        commit_directory(retained_parent, |stage| {
            materialize_tree(&work_dir, &stage.join("payload"), &manifest)
        })?;
    }
    maybe_inject_post_effect_failure("seal")?;
    commit_directory(&seal_dir, |stage| {
        atomic_write(&stage.join("terminal.json"), &raw.bytes, false)?;
        atomic_write_json(&stage.join("manifest.json"), &manifest)?;
        atomic_write_json(&stage.join("record.json"), &record)
    })?;
    pending.finish(&workspace)?;
    Ok(json!({
        "schema": TERMINAL_SCHEMA,
        "set_id": set_id,
        "unit_id": unit_id,
        "terminal_digest": raw.digest,
        "manifest_digest": manifest_hash,
        "created": true
    }))
}

pub(crate) fn close_work_set(root: &Path, set_arg: &str, closure_path: &Path) -> Result<Value> {
    let workspace = load(root)?;
    let _guard = lock(&workspace)?;
    recover_trailing_event(&workspace)?;
    verify_workspace(&workspace)?;
    let set_id = safe_id(set_arg, "SET_ID")?;
    let set_record = load_record(
        &workspace.control.join("records/work-sets").join(&set_id),
        "work set",
    )?;
    let raw = read_raw_json(closure_path, CLOSURE_SCHEMA, "work-set closure")?;
    let fields = object(&raw.value, "work-set closure")?;
    require_matching_id(fields, "set_id", &set_id, "work-set closure")?;
    let frozen = string_array_field(&set_record, "units", "work-set record")?;
    let entries = array_from(fields, "units", "work-set closure")?;
    let mut seen = BTreeSet::new();
    for entry in entries {
        let item = object(entry, "work-set closure unit")?;
        let unit_id = safe_id(
            string_from(item, "unit_id", "work-set closure unit")?,
            "closure unit_id",
        )?;
        if !seen.insert(unit_id.clone()) {
            bail!("work-set closure repeats unit {unit_id}");
        }
        let status = string_from(item, "status", "work-set closure unit")?;
        if status == "completed"
            && !workspace
                .control
                .join("records/work")
                .join(&set_id)
                .join(&unit_id)
                .join("seal/record.json")
                .is_file()
        {
            bail!("completed unit {unit_id} has no sealed evidence");
        }
    }
    let expected = frozen.iter().cloned().collect::<BTreeSet<_>>();
    if seen != expected {
        bail!("work-set closure must account for every frozen unit exactly once");
    }
    let record_dir = workspace.control.join("records/closures").join(&set_id);
    let record_ref = relative_to_root(&workspace, &record_dir.join("record.json"))?;
    let record = json!({
        "schema": CLOSURE_SCHEMA,
        "set_id": set_id,
        "spec_digest": raw.digest,
        "raw_file": "spec.json",
        "units": frozen
    });
    let record_digest = digest_bytes(&canonical_bytes(&record)?);
    let pending = if record_dir.exists() {
        None
    } else {
        Some(PendingEvent::begin(
            &workspace,
            "work-set-closed",
            &[work_set_scope(&set_id)],
            &record_ref,
            &record_digest,
            &raw.digest,
        )?)
    };
    let created = commit_raw_record(&record_dir, &raw, &record)?;
    if let Some(pending) = pending {
        pending.finish(&workspace)?;
    }
    Ok(json!({
        "schema": CLOSURE_SCHEMA,
        "set_id": set_id,
        "closure_digest": raw.digest,
        "created": created
    }))
}

pub(crate) fn publish(root: &Path, publication_path: &Path) -> Result<Value> {
    let workspace = load(root)?;
    let _guard = lock(&workspace)?;
    recover_trailing_event(&workspace)?;
    verify_workspace(&workspace)?;
    let raw = read_raw_json(
        publication_path,
        PUBLICATION_SCHEMA,
        "publication specification",
    )?;
    let fields = object(&raw.value, "publication specification")?;
    let publication_id = safe_id(
        string_from(fields, "publication_id", "publication specification")?,
        "publication_id",
    )?;
    let set_id = safe_id(
        string_from(fields, "set_id", "publication specification")?,
        "set_id",
    )?;
    let set_record = load_record(
        &workspace.control.join("records/work-sets").join(&set_id),
        "work set",
    )?;
    load_record(
        &workspace.control.join("records/closures").join(&set_id),
        "work-set closure",
    )?;
    let commitments = parse_id_list(
        array_from(fields, "commitment_refs", "publication specification")?,
        "commitment_refs",
    )?;
    require_commitments(&workspace, &commitments)?;
    let set_commitments = string_array_field(&set_record, "commitment_refs", "work-set record")?;
    if commitments != set_commitments {
        bail!("publication must bind the frozen work-set commitments exactly");
    }
    let frozen = string_array_field(&set_record, "units", "work-set record")?;
    let publication_units = parse_publication_units(
        array_from(fields, "units", "publication specification")?,
        &frozen,
    )?;

    let record_dir = workspace
        .control
        .join("records/publications")
        .join(&publication_id);
    let secret = fs::read(workspace.control.join("secret"))?;
    let publication_scope = opaque_publication_id(&secret, &publication_id);
    let blind_root = workspace
        .root
        .join("publications")
        .join(publication_scope)
        .join("blind");
    if record_dir.exists() {
        let record = load_record(&record_dir, "publication")?;
        ensure_same_digest(&record, &raw.digest, "publication")?;
        let manifest = read_json(&record_dir.join("blind-manifest.json"), "blind manifest")?;
        verify_tree(&blind_root, &[], &manifest)?;
        return Ok(publication_output(
            &publication_id,
            &set_id,
            &raw.digest,
            &blind_root,
            false,
        ));
    }
    let interrupted_publication = blind_root.parent().is_some_and(Path::exists);
    if interrupted_publication && !blind_root.is_dir() {
        bail!("publication output exists without a complete blind directory");
    }

    let output_stage = prepare_private_output_stage(&workspace, "publication", &publication_id)?;
    let stage_blind = output_stage.join("blind");
    fs::create_dir(&stage_blind)?;
    let mut mappings = Vec::new();
    let build_result = (|| -> Result<Value> {
        for (unit_id, admitted, _reason) in &publication_units {
            if !admitted {
                continue;
            }
            let seal_dir = workspace
                .control
                .join("records/work")
                .join(&set_id)
                .join(unit_id)
                .join("seal");
            let seal_record = load_record(&seal_dir, "sealed work")?;
            let manifest = read_json(&seal_dir.join("manifest.json"), "work manifest")?;
            let payload_relative = relative_path(
                string_from(
                    object(&seal_record, "sealed-work record")?,
                    "payload_root",
                    "sealed-work record",
                )?,
                "sealed payload reference",
            )?;
            let retained_payload = workspace.root.join(payload_relative);
            reject_symlink_components(&retained_payload, "sealed payload reference")?;
            verify_tree(&retained_payload, &[], &manifest)?;
            ensure_same_field(
                &seal_record,
                "manifest_digest",
                &manifest_digest(&manifest)?,
                "sealed work",
            )?;
            let opaque = opaque_id(&secret, &publication_id, unit_id);
            materialize_tree(&retained_payload, &stage_blind.join(&opaque), &manifest)?;
            mappings.push(json!({"opaque_id": opaque, "set_id": set_id, "unit_id": unit_id}));
        }
        capture_tree(&stage_blind, &[])
    })();
    let blind_manifest = match build_result {
        Ok(value) => value,
        Err(error) => {
            let _ = fs::remove_dir_all(&output_stage);
            return Err(error);
        }
    };
    let mapping = Value::Array(mappings);
    let mapping_digest = digest_bytes(&canonical_bytes(&mapping)?);
    let record = json!({
        "schema": PUBLICATION_SCHEMA,
        "publication_id": publication_id,
        "set_id": set_id,
        "spec_digest": raw.digest,
        "raw_file": "spec.json",
        "commitment_refs": commitments,
        "blind_root": relative_to_root(&workspace, &blind_root)?,
        "blind_manifest_digest": manifest_digest(&blind_manifest)?,
        "mapping_file": "private-mapping.json",
        "mapping_digest": mapping_digest
    });
    let record_ref = relative_to_root(&workspace, &record_dir.join("record.json"))?;
    let record_digest = digest_bytes(&canonical_bytes(&record)?);
    maybe_inject_output_construction_failure("publication")?;
    let pending = PendingEvent::begin(
        &workspace,
        "publication-created",
        &[
            work_set_scope(&set_id),
            publication_scope_ref(&publication_id),
        ],
        &record_ref,
        &record_digest,
        &raw.digest,
    )?;
    let final_publication_root = blind_root
        .parent()
        .ok_or_else(|| anyhow!("publication root has no parent"))?;
    if interrupted_publication {
        let existing_manifest = capture_tree(&blind_root, &[])?;
        if existing_manifest != blind_manifest {
            let _ = fs::remove_dir_all(&output_stage);
            bail!("interrupted publication output differs from the prospective publication");
        }
        fs::remove_dir_all(&output_stage).context("discard duplicate publication staging")?;
    } else {
        fs::rename(&output_stage, final_publication_root).context("commit blind publication")?;
    }
    maybe_inject_post_effect_failure("publication")?;

    commit_directory(&record_dir, |stage| {
        atomic_write(&stage.join("spec.json"), &raw.bytes, false)?;
        atomic_write_json(&stage.join("private-mapping.json"), &mapping)?;
        atomic_write_json(&stage.join("blind-manifest.json"), &blind_manifest)?;
        atomic_write_json(&stage.join("record.json"), &record)
    })?;
    pending.finish(&workspace)?;
    Ok(publication_output(
        &publication_id,
        &set_id,
        &raw.digest,
        &blind_root,
        true,
    ))
}

pub(crate) fn reveal(root: &Path, reveal_path: &Path) -> Result<Value> {
    let workspace = load(root)?;
    let _guard = lock(&workspace)?;
    recover_trailing_event(&workspace)?;
    verify_workspace(&workspace)?;
    let raw = read_raw_json(reveal_path, REVEAL_SCHEMA, "reveal specification")?;
    let fields = object(&raw.value, "reveal specification")?;
    let reveal_id = safe_id(
        string_from(fields, "reveal_id", "reveal specification")?,
        "reveal_id",
    )?;
    let publication_id = safe_id(
        string_from(fields, "publication_id", "reveal specification")?,
        "publication_id",
    )?;
    let publication_dir = workspace
        .control
        .join("records/publications")
        .join(&publication_id);
    let publication_record = load_record(&publication_dir, "publication")?;
    let publication_set_id = string_field(&publication_record, "set_id", "publication record")?;
    let closure_refs = parse_id_list(
        array_from(fields, "closure_refs", "reveal specification")?,
        "closure_refs",
    )?;
    if closure_refs.is_empty() {
        bail!("reveal specification.closure_refs must not be empty");
    }
    if !closure_refs.contains(&publication_set_id) {
        bail!("reveal must include the publication work-set closure");
    }
    for closure in &closure_refs {
        load_record(
            &workspace.control.join("records/closures").join(closure),
            "reveal closure prerequisite",
        )?;
    }
    let record_dir = workspace.control.join("records/reveals").join(&reveal_id);
    let reveal_root = workspace.root.join("reveals").join(&reveal_id);
    if record_dir.exists() {
        let record = load_record(&record_dir, "reveal")?;
        ensure_same_digest(&record, &raw.digest, "reveal")?;
        let manifest = read_json(&record_dir.join("reveal-manifest.json"), "reveal manifest")?;
        verify_tree(&reveal_root, &[], &manifest)?;
        return Ok(json!({
            "schema": REVEAL_SCHEMA,
            "reveal_id": reveal_id,
            "publication_id": publication_id,
            "reveal_digest": raw.digest,
            "reveal_root": reveal_root,
            "created": false
        }));
    }
    let set_id = publication_set_id;
    let record_ref = relative_to_root(&workspace, &record_dir.join("record.json"))?;
    let interrupted_reveal = reveal_root.exists();
    if interrupted_reveal && !reveal_root.is_dir() {
        bail!("reveal output exists without a complete directory");
    }
    let blind_root = workspace.root.join(string_field(
        &publication_record,
        "blind_root",
        "publication record",
    )?);
    let blind_manifest = read_json(
        &publication_dir.join("blind-manifest.json"),
        "blind manifest",
    )?;
    verify_tree(&blind_root, &[], &blind_manifest)?;
    let mapping = read_json(
        &publication_dir.join("private-mapping.json"),
        "private publication mapping",
    )?;
    let stage = prepare_private_output_stage(&workspace, "reveal", &reveal_id)?;
    let build_result = (|| -> Result<Value> {
        materialize_tree(&blind_root, &stage.join("evidence"), &blind_manifest)?;
        atomic_write_json(&stage.join("identity-map.json"), &mapping)?;
        capture_tree(&stage, &[])
    })();
    let reveal_manifest = match build_result {
        Ok(value) => value,
        Err(error) => {
            let _ = fs::remove_dir_all(&stage);
            return Err(error);
        }
    };
    let record = json!({
        "schema": REVEAL_SCHEMA,
        "reveal_id": reveal_id,
        "publication_id": publication_id,
        "set_id": set_id,
        "spec_digest": raw.digest,
        "raw_file": "spec.json",
        "closure_refs": closure_refs,
        "reveal_root": relative_to_root(&workspace, &reveal_root)?,
        "reveal_manifest_digest": manifest_digest(&reveal_manifest)?
    });
    let record_digest = digest_bytes(&canonical_bytes(&record)?);
    maybe_inject_output_construction_failure("reveal")?;
    let pending = PendingEvent::begin(
        &workspace,
        "identity-revealed",
        &[
            work_set_scope(&set_id),
            publication_scope_ref(&publication_id),
            reveal_scope_ref(&reveal_id),
        ],
        &record_ref,
        &record_digest,
        &raw.digest,
    )?;
    if interrupted_reveal {
        let existing_manifest = capture_tree(&reveal_root, &[])?;
        if existing_manifest != reveal_manifest {
            let _ = fs::remove_dir_all(&stage);
            bail!("interrupted reveal output differs from the prospective reveal");
        }
        fs::remove_dir_all(&stage).context("discard duplicate reveal staging")?;
    } else {
        fs::rename(&stage, &reveal_root).context("commit revealed package")?;
    }
    maybe_inject_post_effect_failure("reveal")?;
    commit_directory(&record_dir, |record_stage| {
        atomic_write(&record_stage.join("spec.json"), &raw.bytes, false)?;
        atomic_write_json(&record_stage.join("reveal-manifest.json"), &reveal_manifest)?;
        atomic_write_json(&record_stage.join("record.json"), &record)
    })?;
    pending.finish(&workspace)?;
    Ok(json!({
        "schema": REVEAL_SCHEMA,
        "reveal_id": reveal_id,
        "publication_id": publication_id,
        "reveal_digest": raw.digest,
        "reveal_root": reveal_root,
        "created": true
    }))
}

pub(crate) fn events(
    root: &Path,
    scope: Option<&str>,
    format: &str,
    after_sequence: Option<u64>,
    max_items: Option<usize>,
) -> Result<Vec<Value>> {
    if format != "jsonl" {
        bail!("events --format supports only jsonl");
    }
    if max_items == Some(0) {
        bail!("events --max-items must be greater than zero");
    }
    let workspace = load(root)?;
    let _guard = lock(&workspace)?;
    recover_trailing_event(&workspace)?;
    verify_workspace(&workspace)?;
    let mut all = verify_event_chain(&workspace)?;
    if let Some(sequence) = after_sequence {
        all.retain(|event| {
            event
                .get("sequence")
                .and_then(Value::as_u64)
                .is_some_and(|candidate| candidate > sequence)
        });
    }
    if let Some(scope_id) = scope {
        let safe_scope = normalize_scope_ref(scope_id)?;
        all.retain(|event| {
            event
                .get("scope_refs")
                .and_then(Value::as_array)
                .is_some_and(|ids| ids.iter().any(|id| id.as_str() == Some(&safe_scope)))
        });
    }
    if let Some(limit) = max_items {
        all.truncate(limit);
    }
    Ok(all)
}

pub(crate) fn receipt(root: &Path, scope: Option<&str>) -> Result<Value> {
    let workspace = load(root)?;
    let _guard = lock(&workspace)?;
    recover_trailing_event(&workspace)?;
    verify_workspace(&workspace)?;
    let all = verify_event_chain(&workspace)?;
    let scope_value = scope.map(normalize_scope_ref).transpose()?;
    let scoped = all.iter().filter(|event| {
        scope_value.as_ref().is_none_or(|scope_id| {
            event
                .get("scope_refs")
                .and_then(Value::as_array)
                .is_some_and(|ids| ids.iter().any(|id| id.as_str() == Some(scope_id)))
        })
    });
    let mut scoped_count = 0_u64;
    let mut scoped_head = ZERO_DIGEST.to_owned();
    for event in scoped {
        scoped_count += 1;
        scoped_head = string_field(event, "event_digest", "event")?;
    }
    let chain_head = if all.is_empty() {
        ZERO_DIGEST.to_owned()
    } else {
        string_field(
            all.last()
                .ok_or_else(|| anyhow!("event chain missing final event after non-empty check"))?,
            "event_digest",
            "event",
        )?
    };
    Ok(json!({
        "schema": RECEIPT_SCHEMA,
        "workspace_id": workspace.metadata.get("workspace_id").cloned().ok_or_else(|| anyhow!("workspace identity missing"))?,
        "scope_ref": scope_value,
        "event_count": all.len(),
        "chain_head": chain_head,
        "scoped_event_count": scoped_count,
        "scoped_head": scoped_head
    }))
}

pub(crate) fn status(root: &Path) -> Result<Value> {
    let workspace = load(root)?;
    let _guard = lock(&workspace)?;
    recover_trailing_event(&workspace)?;
    status_value(&workspace)
}

fn status_value(workspace: &Workspace) -> Result<Value> {
    verify_workspace(workspace)?;
    let events = verify_event_chain(workspace)?;
    let diagnostics = gather_diagnostics(workspace)?;
    let chain_head = if events.is_empty() {
        Value::String(ZERO_DIGEST.to_owned())
    } else {
        events
            .last()
            .and_then(|event| event.get("event_digest"))
            .cloned()
            .ok_or_else(|| anyhow!("event digest missing from non-empty event chain"))?
    };
    Ok(json!({
        "schema": WORKSPACE_SCHEMA,
        "workspace_id": workspace.metadata.get("workspace_id").cloned().ok_or_else(|| anyhow!("workspace identity missing"))?,
        "root": workspace.root,
        "event_count": events.len(),
        "chain_head": chain_head,
        "diagnostics": diagnostics,
        "valid": true
    }))
}

fn verify_workspace(workspace: &Workspace) -> Result<()> {
    let events = verify_event_chain(workspace)?;
    verify_event_records(workspace, &events)?;
    verify_records(workspace, &events)
}

fn verify_records(workspace: &Workspace, events: &[Value]) -> Result<()> {
    let referenced = events
        .iter()
        .filter_map(|event| event.get("record_ref").and_then(Value::as_str))
        .map(str::to_owned)
        .collect::<BTreeSet<_>>();
    for directory in record_directories(workspace)? {
        let record_path = directory.join("record.json");
        let record = read_json(&record_path, "custody record")?;
        validate_record(workspace, &directory, &record)?;
        let record_ref = relative_to_root(workspace, &record_path)?;
        if !referenced.contains(&record_ref) {
            bail!("unreferenced custody record: {record_ref}");
        }
    }
    Ok(())
}

fn record_directories(workspace: &Workspace) -> Result<Vec<PathBuf>> {
    let records = workspace.control.join("records");
    if !records.is_dir() {
        bail!("custody records directory is missing");
    }
    let mut directories = Vec::new();
    let mut stack = vec![records];
    while let Some(directory) = stack.pop() {
        let entries = fs::read_dir(&directory)
            .with_context(|| format!("read record directory {}", directory.display()))?;
        for entry in entries {
            let entry = entry?;
            let metadata = fs::symlink_metadata(entry.path())?;
            if metadata.file_type().is_symlink() {
                bail!("custody records must not contain symlinks");
            }
            if metadata.is_dir() {
                stack.push(entry.path());
            }
        }
        if directory.join("record.json").is_file() {
            directories.push(directory);
        }
    }
    directories.sort();
    Ok(directories)
}

fn validate_record(workspace: &Workspace, directory: &Path, record: &Value) -> Result<()> {
    let required_schema = schema_for_record_dir(&workspace.control.join("records"), directory)?;
    if record.get("schema").and_then(Value::as_str) != Some(required_schema) {
        bail!("unsupported custody record schema");
    }
    if let Some(raw_file) = record.get("raw_file").and_then(Value::as_str) {
        let raw_path = directory.join(raw_file);
        ensure_same_field(
            record,
            "spec_digest",
            &digest_file(&raw_path)?,
            "custody record",
        )
        .or_else(|_| {
            ensure_same_field(
                record,
                "terminal_digest",
                &digest_file(&raw_path)?,
                "custody record",
            )
        })?;
    }
    if record.get("workspace").and_then(Value::as_str).is_some() {
        if let Some(manifest_name) = record.get("manifest_file").and_then(Value::as_str) {
            let manifest = read_json(&directory.join(manifest_name), "work manifest")?;
            let retained_relative = relative_path(
                string_from(
                    object(record, "sealed-work record")?,
                    "payload_root",
                    "sealed-work record",
                )?,
                "sealed payload reference",
            )?;
            let retained_payload = workspace.root.join(retained_relative);
            reject_symlink_components(&retained_payload, "sealed payload reference")?;
            verify_tree(&retained_payload, &[], &manifest)?;
            ensure_same_field(
                record,
                "manifest_digest",
                &manifest_digest(&manifest)?,
                "sealed-work record",
            )?;
        }
    }
    if let Some(blind_relative) = record.get("blind_root").and_then(Value::as_str) {
        let manifest = read_json(&directory.join("blind-manifest.json"), "blind manifest")?;
        verify_tree(&workspace.root.join(blind_relative), &[], &manifest)?;
        ensure_same_field(
            record,
            "blind_manifest_digest",
            &manifest_digest(&manifest)?,
            "publication record",
        )?;
        let mapping_file = string_from(
            object(record, "publication record")?,
            "mapping_file",
            "publication record",
        )?;
        let mapping_path = directory.join(mapping_file);
        let mapping_digest =
            digest_file(&mapping_path).context("read retained private publication mapping")?;
        if record.get("mapping_digest").and_then(Value::as_str) != Some(mapping_digest.as_str()) {
            bail!("private mapping mutation detected");
        }
    }
    if let Some(reveal_relative) = record.get("reveal_root").and_then(Value::as_str) {
        let manifest = read_json(&directory.join("reveal-manifest.json"), "reveal manifest")?;
        verify_tree(&workspace.root.join(reveal_relative), &[], &manifest)?;
        ensure_same_field(
            record,
            "reveal_manifest_digest",
            &manifest_digest(&manifest)?,
            "reveal record",
        )?;
    }
    verify_effective_inputs(directory, record)?;
    Ok(())
}

fn verify_effective_inputs(directory: &Path, record: &Value) -> Result<()> {
    let capture_root = directory.join("effective-inputs");
    let Some(expected) = record.get("effective_inputs") else {
        if capture_root.exists() {
            bail!("custody record has unbound effective-input captures");
        }
        return Ok(());
    };
    let expected = expected
        .as_array()
        .ok_or_else(|| anyhow!("custody record effective_inputs must be an array"))?;
    let mut retained = BTreeSet::new();
    if capture_root.exists() {
        let metadata = fs::symlink_metadata(&capture_root)?;
        if !metadata.is_dir() || metadata.file_type().is_symlink() {
            bail!("effective-input capture root must be a directory");
        }
        for entry in fs::read_dir(&capture_root)? {
            let entry = entry?;
            let metadata = fs::symlink_metadata(entry.path())?;
            if !metadata.is_dir() || metadata.file_type().is_symlink() {
                bail!("effective-input captures must be indexed directories");
            }
            let name = entry
                .file_name()
                .into_string()
                .map_err(|_| anyhow!("effective-input capture indexes must be UTF-8"))?;
            let index = name
                .parse::<usize>()
                .map_err(|_| anyhow!("effective-input capture index is invalid"))?;
            if name != index.to_string() || !retained.insert(index) {
                bail!("effective-input capture index is invalid");
            }
        }
    }

    let mut bound = BTreeSet::new();
    for (position, value) in expected.iter().enumerate() {
        let fields = object(value, "effective-input record")?;
        if fields.get("index").and_then(Value::as_u64)
            != Some(u64::try_from(position).context("effective-input index overflow")?)
        {
            bail!("effective-input record index is not contiguous");
        }
        let item = capture_root.join(position.to_string());
        if fields.get("availability").and_then(Value::as_str) == Some("unavailable-or-opaque") {
            if item.exists() {
                bail!("unavailable effective input unexpectedly has captured content");
            }
            continue;
        }
        if !bound.insert(position) || !retained.contains(&position) {
            bail!("effective-input capture is missing");
        }
        reject_symlink_components(&item, "effective-input capture")?;
        let manifest = read_json(&item.join("manifest.json"), "effective-input manifest")?;
        verify_tree(&item.join("payload"), &[], &manifest)?;
        let actual = manifest_digest(&manifest)?;
        if fields.get("manifest_digest").and_then(Value::as_str) != Some(actual.as_str()) {
            bail!("effective-input manifest digest mismatch");
        }
    }
    if retained != bound {
        bail!("effective-input capture set does not match its custody record");
    }
    Ok(())
}

fn recover_trailing_event(workspace: &Workspace) -> Result<()> {
    let pending_dir = workspace.control.join("pending");
    if !pending_dir.is_dir() {
        bail!("pending-event directory is missing");
    }
    let mut pending = fs::read_dir(&pending_dir)?.collect::<std::result::Result<Vec<_>, _>>()?;
    pending.sort_by_key(fs::DirEntry::file_name);
    if pending.len() > 1 {
        bail!("multiple pending events prevent deterministic crash recovery");
    }
    let Some(entry) = pending.pop() else {
        return Ok(());
    };
    if !entry.file_type()?.is_file() {
        bail!("pending-event directory contains an unsupported entry");
    }
    let value = read_json(&entry.path(), "pending event")?;
    let fields = object(&value, "pending event")?;
    if string_from(fields, "schema", "pending event")? != PENDING_EVENT_SCHEMA {
        bail!("unsupported pending-event schema");
    }
    let kind = string_from(fields, "kind", "pending event")?;
    let scopes = parse_scope_refs(
        array_from(fields, "scope_refs", "pending event")?,
        "scope_refs",
    )?;
    let record_ref = string_from(fields, "record_ref", "pending event")?;
    let content_digest = string_from(fields, "content_digest", "pending event")?;
    if kind == "workspace-initialized" {
        if record_ref != ".split-testing/workspace.json"
            || workspace
                .metadata
                .get("workspace_id")
                .and_then(Value::as_str)
                != Some(content_digest)
        {
            bail!("pending workspace initialization does not match workspace identity");
        }
        let expected_record_digest = digest_file(&workspace.control.join("workspace.json"))?;
        let record_digest = string_from(fields, "record_digest", "pending event")?;
        if record_digest != expected_record_digest {
            bail!("pending event record digest mismatch");
        }
        append_event(
            workspace,
            kind,
            &scopes,
            record_ref,
            record_digest,
            content_digest,
        )?;
        return fs::remove_file(entry.path()).context("clear recovered pending event");
    }
    let record_relative = relative_path(record_ref, "pending record reference")?;
    let record_path = workspace.root.join(record_relative);
    if record_path.is_file() {
        let record_digest = string_from(fields, "record_digest", "pending event")?;
        if record_digest != digest_file(&record_path)? {
            bail!("pending event record digest mismatch");
        }
        let directory = record_path
            .parent()
            .ok_or_else(|| anyhow!("pending record has no parent"))?;
        let record = read_json(&record_path, "pending custody record")?;
        validate_record(workspace, directory, &record)?;
        append_event(
            workspace,
            kind,
            &scopes,
            record_ref,
            record_digest,
            content_digest,
        )?;
    } else if pending_effect_committed(workspace, kind, &scopes)? {
        bail!(
            "pending committed effect has no exact custody record; recovery fails closed without rebinding"
        );
    }
    fs::remove_file(entry.path()).context("clear recovered pending event")
}

fn pending_effect_committed(
    workspace: &Workspace,
    kind: &str,
    scope_refs: &[String],
) -> Result<bool> {
    let effect = match kind {
        "work-sealed" => {
            let work = required_scope_ref(scope_refs, "work:", "work-sealed")?;
            let (set_id, unit_id) = work
                .split_once('/')
                .ok_or_else(|| anyhow!("pending work scope is not compound"))?;
            workspace
                .control
                .join("objects/sealed")
                .join(set_id)
                .join(unit_id)
                .join("payload")
        }
        "publication-created" => {
            let publication_id =
                required_scope_ref(scope_refs, "publication:", "publication-created")?;
            let secret = fs::read(workspace.control.join("secret"))?;
            workspace
                .root
                .join("publications")
                .join(opaque_publication_id(&secret, publication_id))
                .join("blind")
        }
        "identity-revealed" => {
            let reveal_id = required_scope_ref(scope_refs, "reveal:", "identity-revealed")?;
            workspace.root.join("reveals").join(reveal_id)
        }
        _ => return Ok(false),
    };
    match fs::symlink_metadata(&effect) {
        Ok(_) => Ok(true),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(false),
        Err(error) => {
            Err(error).with_context(|| format!("inspect committed effect {}", effect.display()))
        }
    }
}

fn required_scope_ref<'a>(scope_refs: &'a [String], prefix: &str, kind: &str) -> Result<&'a str> {
    scope_refs
        .iter()
        .find_map(|scope| scope.strip_prefix(prefix))
        .ok_or_else(|| anyhow!("pending {kind} event is missing its {prefix} scope"))
}

fn schema_for_record_dir(records_root: &Path, directory: &Path) -> Result<&'static str> {
    let relative = directory
        .strip_prefix(records_root)
        .map_err(|_| anyhow!("custody record escaped the records root"))?;
    let parts = relative
        .components()
        .map(|component| {
            component
                .as_os_str()
                .to_str()
                .ok_or_else(|| anyhow!("custody record paths must be valid UTF-8"))
        })
        .collect::<Result<Vec<_>>>()?;
    match parts.as_slice() {
        ["commitments", _] => Ok(COMMITMENT_SCHEMA),
        ["work-sets", _] => Ok(WORK_SET_SCHEMA),
        ["work", _, _] => Ok(WORK_SCHEMA),
        ["work", _, _, "seal"] => Ok(TERMINAL_SCHEMA),
        ["closures", _] => Ok(CLOSURE_SCHEMA),
        ["publications", _] => Ok(PUBLICATION_SCHEMA),
        ["reveals", _] => Ok(REVEAL_SCHEMA),
        _ => bail!("unsupported custody record location"),
    }
}

fn verify_event_records(workspace: &Workspace, events: &[Value]) -> Result<()> {
    for event in events {
        let fields = object(event, "event")?;
        let record_ref = string_from(fields, "record_ref", "event")?;
        let relative = relative_path(record_ref, "event record reference")?;
        let record_path = workspace.root.join(relative);
        reject_symlink_components(&record_path, "event record reference")?;
        let metadata = fs::symlink_metadata(&record_path)
            .map_err(|_| anyhow!("event record is missing: {record_ref}"))?;
        if !metadata.file_type().is_file() {
            bail!("event record is not a regular file: {record_ref}");
        }
        if fields.get("record_digest").and_then(Value::as_str)
            != Some(digest_file(&record_path)?.as_str())
        {
            bail!("event record digest mismatch");
        }
        let record = read_json(&record_path, "event record")?;
        let kind = string_from(fields, "kind", "event")?;
        let digest_field = match kind {
            "workspace-initialized" => "workspace_id",
            "commitment-added"
            | "work-set-added"
            | "work-prepared"
            | "work-set-closed"
            | "publication-created"
            | "identity-revealed" => "spec_digest",
            "work-sealed" => "manifest_digest",
            _ => bail!("unsupported event kind"),
        };
        if record.get(digest_field).and_then(Value::as_str)
            != fields.get("content_digest").and_then(Value::as_str)
        {
            bail!("event record content digest mismatch");
        }
    }
    Ok(())
}

fn append_event(
    workspace: &Workspace,
    kind: &str,
    scope_refs: &[String],
    record_ref: &str,
    record_digest: &str,
    content_digest: &str,
) -> Result<()> {
    let events = verify_event_chain(workspace)?;
    verify_event_records(workspace, &events)?;
    let record_relative = relative_path(record_ref, "event record reference")?;
    let record_path = workspace.root.join(record_relative);
    reject_symlink_components(&record_path, "event record reference")?;
    let actual_record_digest = digest_file(&record_path)?;
    if actual_record_digest != record_digest {
        bail!("pending event record digest mismatch");
    }
    if events.iter().any(|event| {
        event.get("kind").and_then(Value::as_str) == Some(kind)
            && event.get("record_ref").and_then(Value::as_str) == Some(record_ref)
            && event.get("content_digest").and_then(Value::as_str) == Some(content_digest)
            && event.get("record_digest").and_then(Value::as_str) == Some(record_digest)
    }) {
        return Ok(());
    }
    let previous = events
        .last()
        .and_then(|event| event.get("event_digest"))
        .and_then(Value::as_str)
        .map_or(ZERO_DIGEST, std::convert::identity);
    let sequence = u64::try_from(events.len()).context("event sequence overflow")? + 1;
    let mut event = json!({
        "schema": EVENT_SCHEMA,
        "sequence": sequence,
        "kind": kind,
        "scope_refs": scope_refs,
        "record_ref": record_ref,
        "record_digest": record_digest,
        "content_digest": content_digest,
        "previous_digest": previous
    });
    let digest = digest_bytes(&canonical_bytes(&event)?);
    event
        .as_object_mut()
        .ok_or_else(|| anyhow!("event must be an object"))?
        .insert("event_digest".to_owned(), Value::String(digest));
    let event_path = workspace
        .control
        .join("events")
        .join(format!("{sequence:020}.json"));
    atomic_write_json(&event_path, &event)
}

fn verify_event_chain(workspace: &Workspace) -> Result<Vec<Value>> {
    let event_dir = workspace.control.join("events");
    let mut paths = fs::read_dir(&event_dir)
        .context("read event directory")?
        .collect::<std::result::Result<Vec<_>, _>>()?;
    paths.sort_by_key(fs::DirEntry::file_name);
    let mut previous = ZERO_DIGEST.to_owned();
    let mut events = Vec::new();
    for (index, entry) in paths.into_iter().enumerate() {
        if !entry.file_type()?.is_file() {
            bail!("event directory contains unsupported entry");
        }
        let event = read_json(&entry.path(), "event")?;
        let fields = object(&event, "event")?;
        if fields.get("schema").and_then(Value::as_str) != Some(EVENT_SCHEMA) {
            bail!("unsupported event schema");
        }
        parse_scope_refs(array_from(fields, "scope_refs", "event")?, "scope_refs")?;
        let expected_sequence = u64::try_from(index).context("event index overflow")? + 1;
        if entry.file_name() != std::ffi::OsString::from(format!("{expected_sequence:020}.json")) {
            bail!("event filename does not match its sequence");
        }
        if fields.get("sequence").and_then(Value::as_u64) != Some(expected_sequence) {
            bail!("event sequence is not contiguous");
        }
        if fields.get("previous_digest").and_then(Value::as_str) != Some(&previous) {
            bail!("event chain previous digest mismatch");
        }
        let claimed = string_from(fields, "event_digest", "event")?.to_owned();
        let mut material = event.clone();
        material
            .as_object_mut()
            .ok_or_else(|| anyhow!("event must be an object"))?
            .remove("event_digest");
        let actual = digest_bytes(&canonical_bytes(&material)?);
        if actual != claimed {
            bail!("event digest mismatch");
        }
        previous = claimed;
        events.push(event);
    }
    Ok(events)
}

fn commit_raw_record(record_dir: &Path, raw: &RawJson, record: &Value) -> Result<bool> {
    if record_dir.exists() {
        let existing = load_record(record_dir, "record")?;
        ensure_same_digest(&existing, &raw.digest, "record")?;
        return Ok(false);
    }
    commit_directory(record_dir, |stage| {
        atomic_write(&stage.join("spec.json"), &raw.bytes, false)?;
        atomic_write_json(&stage.join("record.json"), record)
    })?;
    Ok(true)
}

fn commit_directory<F>(destination: &Path, write: F) -> Result<()>
where
    F: FnOnce(&Path) -> Result<()>,
{
    let parent = destination
        .parent()
        .ok_or_else(|| anyhow!("record path has no parent"))?;
    fs::create_dir_all(parent)?;
    let name = destination
        .file_name()
        .and_then(|value| value.to_str())
        .ok_or_else(|| anyhow!("record identity must be UTF-8"))?;
    let stage = parent.join(format!(".{name}.stage-{:016x}", random::<u64>()));
    fs::create_dir(&stage)?;
    let result = (|| -> Result<()> {
        write(&stage)?;
        fs::rename(&stage, destination)
            .with_context(|| format!("commit record {}", destination.display()))?;
        Ok(())
    })();
    if result.is_err() {
        let _ = fs::remove_dir_all(&stage);
    }
    result
}

fn prepare_private_output_stage(
    workspace: &Workspace,
    kind: &str,
    identity: &str,
) -> Result<PathBuf> {
    let staging_root = workspace.control.join("staging").join(kind);
    fs::create_dir_all(&staging_root).context("create private output staging root")?;
    let stage = staging_root.join(identity);
    if stage.exists() {
        let metadata = fs::symlink_metadata(&stage).context("inspect private output stage")?;
        if metadata.file_type().is_symlink() || !metadata.is_dir() {
            bail!("private output stage is not a controller-owned directory");
        }
        fs::remove_dir_all(&stage).context("discard stranded private output stage")?;
    }
    fs::create_dir(&stage).context("create private output stage")?;
    Ok(stage)
}

fn maybe_inject_output_construction_failure(kind: &str) -> Result<()> {
    if std::env::var_os("SPLIT_TEST_TEST_FAIL_AFTER_OUTPUT_CONSTRUCTION").as_deref()
        == Some(std::ffi::OsStr::new(kind))
    {
        bail!("injected output-construction failure before pending-event arming");
    }
    Ok(())
}

fn maybe_inject_post_effect_failure(kind: &str) -> Result<()> {
    if std::env::var_os("SPLIT_TEST_TEST_FAIL_AFTER_EFFECT_COMMIT").as_deref()
        == Some(std::ffi::OsStr::new(kind))
    {
        bail!("injected post-effect failure before custody-record commit");
    }
    Ok(())
}

fn load_record(directory: &Path, label: &str) -> Result<Value> {
    read_json(&directory.join("record.json"), label)
}

fn read_json(path: &Path, label: &str) -> Result<Value> {
    let bytes = fs::read(path).with_context(|| format!("missing {label} at {}", path.display()))?;
    serde_json::from_slice(&bytes).with_context(|| format!("parse {label}"))
}

fn ensure_same_digest(record: &Value, digest: &str, label: &str) -> Result<()> {
    ensure_same_field(record, "spec_digest", digest, label)
}

fn ensure_same_field(record: &Value, key: &str, expected: &str, label: &str) -> Result<()> {
    let actual = record.get(key).and_then(Value::as_str);
    if actual != Some(expected) {
        bail!("{label} identity already exists with different content");
    }
    Ok(())
}

fn commitment_scope(commitment_id: &str) -> String {
    format!("commitment:{commitment_id}")
}

fn work_set_scope(set_id: &str) -> String {
    format!("work-set:{set_id}")
}

fn work_scope(set_id: &str, unit_id: &str) -> String {
    format!("work:{set_id}/{unit_id}")
}

fn publication_scope_ref(publication_id: &str) -> String {
    format!("publication:{publication_id}")
}

fn reveal_scope_ref(reveal_id: &str) -> String {
    format!("reveal:{reveal_id}")
}

fn normalize_scope_ref(scope: &str) -> Result<String> {
    if let Some((kind, rest)) = scope.split_once(':') {
        return match kind {
            "commitment" => Ok(commitment_scope(&safe_id(rest, "SCOPE_ID")?)),
            "work-set" => Ok(work_set_scope(&safe_id(rest, "SCOPE_ID")?)),
            "publication" => Ok(publication_scope_ref(&safe_id(rest, "SCOPE_ID")?)),
            "reveal" => Ok(reveal_scope_ref(&safe_id(rest, "SCOPE_ID")?)),
            "work" => {
                let (set_id, unit_id) = rest
                    .split_once('/')
                    .ok_or_else(|| anyhow!("SCOPE_ID work selector must be work:<set>/<unit>"))?;
                Ok(work_scope(
                    &safe_id(set_id, "SCOPE_ID set")?,
                    &safe_id(unit_id, "SCOPE_ID unit")?,
                ))
            }
            _ => bail!(
                "SCOPE_ID must be a bare work-set id or one of commitment:<id>, work-set:<id>, work:<set>/<unit>, publication:<id>, reveal:<id>"
            ),
        };
    }
    Ok(work_set_scope(&safe_id(scope, "SCOPE_ID")?))
}

fn parse_scope_refs(values: &[Value], label: &str) -> Result<Vec<String>> {
    let mut output = Vec::new();
    let mut seen = BTreeSet::new();
    for value in values {
        let text = value
            .as_str()
            .ok_or_else(|| anyhow!("{label} entries must be strings"))?;
        let normalized = normalize_scope_ref(text)?;
        if normalized != text {
            bail!("{label} entries must use canonical typed scope references");
        }
        if !seen.insert(normalized.clone()) {
            bail!("{label} repeats {normalized}");
        }
        output.push(normalized);
    }
    Ok(output)
}

fn parse_id_list(values: &[Value], label: &str) -> Result<Vec<String>> {
    let mut output = Vec::new();
    let mut seen = BTreeSet::new();
    for value in values {
        let text = value
            .as_str()
            .ok_or_else(|| anyhow!("{label} entries must be strings"))?;
        let identifier = safe_id(text, label)?;
        if !seen.insert(identifier.clone()) {
            bail!("{label} repeats {identifier}");
        }
        output.push(identifier);
    }
    Ok(output)
}

fn parse_units(values: &[Value]) -> Result<Vec<String>> {
    let mut output = Vec::new();
    let mut seen = BTreeSet::new();
    for value in values {
        let text = if let Some(text) = value.as_str() {
            text
        } else {
            let fields = object(value, "work-set unit")?;
            string_from(fields, "unit_id", "work-set unit")?
        };
        let identifier = safe_id(text, "unit_id")?;
        if !seen.insert(identifier.clone()) {
            bail!("work-set units repeat {identifier}");
        }
        output.push(identifier);
    }
    Ok(output)
}

fn require_commitments(workspace: &Workspace, commitments: &[String]) -> Result<()> {
    for commitment in commitments {
        load_record(
            &workspace
                .control
                .join("records/commitments")
                .join(commitment),
            "commitment",
        )?;
    }
    Ok(())
}

fn string_array_field(record: &Value, key: &str, label: &str) -> Result<Vec<String>> {
    let fields = object(record, label)?;
    parse_id_list(array_from(fields, key, label)?, key)
}

fn require_matching_id(
    fields: &Map<String, Value>,
    key: &str,
    expected: &str,
    label: &str,
) -> Result<()> {
    if string_from(fields, key, label)? != expected {
        bail!("{label}.{key} does not match the command identity");
    }
    Ok(())
}

fn capture_effective_inputs(
    fields: &Map<String, Value>,
    spec_path: &Path,
    stage: &Path,
) -> Result<Vec<Value>> {
    let Some(values) = fields.get("effective_input_refs") else {
        return Ok(Vec::new());
    };
    let refs = values
        .as_array()
        .ok_or_else(|| anyhow!("work specification.effective_input_refs must be an array"))?;
    let mut captured = Vec::new();
    for (index, reference) in refs.iter().enumerate() {
        let Some(path_value) = reference.get("path").and_then(Value::as_str) else {
            captured.push(json!({"index": index, "availability": "unavailable-or-opaque"}));
            continue;
        };
        let path = PathBuf::from(path_value);
        let resolved = if path.is_absolute() {
            path
        } else {
            spec_path
                .parent()
                .ok_or_else(|| anyhow!("work specification has no parent"))?
                .join(path)
        };
        let destination = stage.join("effective-inputs").join(index.to_string());
        let manifest = copy_external_reference(&resolved, &destination)?;
        captured.push(json!({
            "index": index,
            "source": path_value,
            "manifest_digest": manifest_digest(&manifest)?
        }));
    }
    Ok(captured)
}

fn parse_publication_units(
    values: &[Value],
    frozen: &[String],
) -> Result<Vec<(String, bool, String)>> {
    let mut output = Vec::new();
    let mut seen = BTreeSet::new();
    for value in values {
        let fields = object(value, "publication unit")?;
        let unit_id = safe_id(
            string_from(fields, "unit_id", "publication unit")?,
            "publication unit_id",
        )?;
        if !seen.insert(unit_id.clone()) {
            bail!("publication repeats unit {unit_id}");
        }
        let admitted = bool_from(fields, "admitted", "publication unit")?;
        let reason = string_from(fields, "reason", "publication unit")?.to_owned();
        output.push((unit_id, admitted, reason));
    }
    let expected = frozen.iter().cloned().collect::<BTreeSet<_>>();
    if seen != expected {
        bail!("publication must account for every frozen unit exactly once");
    }
    Ok(output)
}

fn gather_diagnostics(workspace: &Workspace) -> Result<Vec<Value>> {
    let work_root = workspace.control.join("records/work");
    if !work_root.is_dir() {
        return Ok(Vec::new());
    }
    let mut diagnostics = Vec::new();
    for set_entry in fs::read_dir(&work_root)? {
        let set_entry = set_entry?;
        if !set_entry.file_type()?.is_dir() {
            continue;
        }
        let set_id = set_entry
            .file_name()
            .into_string()
            .map_err(|_| anyhow!("work set path must be valid UTF-8"))?;
        for unit_entry in fs::read_dir(set_entry.path())? {
            let unit_entry = unit_entry?;
            if !unit_entry.file_type()?.is_dir() {
                continue;
            }
            let unit_id = unit_entry
                .file_name()
                .into_string()
                .map_err(|_| anyhow!("work unit path must be valid UTF-8"))?;
            let record = load_record(&unit_entry.path(), "work record")?;
            let live_workspace =
                workspace
                    .root
                    .join(string_field(&record, "workspace", "work record")?);
            let seal_dir = unit_entry.path().join("seal");
            let live_metadata = fs::symlink_metadata(&live_workspace);
            let live_directory = matches!(
                &live_metadata,
                Ok(metadata) if metadata.is_dir() && !metadata.file_type().is_symlink()
            );
            if seal_dir.is_dir() {
                let manifest = read_json(&seal_dir.join("manifest.json"), "work manifest")?;
                let kind = if !live_directory {
                    Some("sealed-workspace-missing")
                } else if verify_tree(&live_workspace, &[], &manifest).is_err() {
                    Some("sealed-workspace-drift")
                } else {
                    None
                };
                if let Some(kind) = kind {
                    diagnostics.push(json!({
                        "kind": kind,
                        "set_id": set_id,
                        "unit_id": unit_id,
                        "workspace": live_workspace
                    }));
                }
            } else if !live_directory {
                diagnostics.push(json!({
                    "kind": "unsealed-workspace-missing",
                    "set_id": set_id,
                    "unit_id": unit_id,
                    "workspace": live_workspace
                }));
            }
        }
    }
    diagnostics.sort_by(|left, right| {
        let left_key = (
            left.get("kind").and_then(Value::as_str),
            left.get("set_id").and_then(Value::as_str),
            left.get("unit_id").and_then(Value::as_str),
        );
        let right_key = (
            right.get("kind").and_then(Value::as_str),
            right.get("set_id").and_then(Value::as_str),
            right.get("unit_id").and_then(Value::as_str),
        );
        left_key.cmp(&right_key)
    });
    Ok(diagnostics)
}

fn opaque_id(secret: &[u8], publication_id: &str, unit_id: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(b"split-testing-publication-v2\0");
    hasher.update(secret);
    hasher.update([0]);
    hasher.update(publication_id.as_bytes());
    hasher.update([0]);
    hasher.update(unit_id.as_bytes());
    let digest = format!("{:x}", hasher.finalize());
    format!("item-{}", &digest[..32])
}

fn opaque_publication_id(secret: &[u8], publication_id: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(b"split-testing-publication-scope-v2\0");
    hasher.update(secret);
    hasher.update([0]);
    hasher.update(publication_id.as_bytes());
    let digest = format!("{:x}", hasher.finalize());
    format!("package-{}", &digest[..32])
}

fn publication_output(
    publication_id: &str,
    set_id: &str,
    digest: &str,
    blind_root: &Path,
    created: bool,
) -> Value {
    json!({
        "schema": PUBLICATION_SCHEMA,
        "publication_id": publication_id,
        "set_id": set_id,
        "publication_digest": digest,
        "blind_root": blind_root,
        "created": created
    })
}

fn relative_to_root(workspace: &Workspace, path: &Path) -> Result<String> {
    let relative = path
        .strip_prefix(&workspace.root)
        .map_err(|_| anyhow!("custody path escaped ROOT"))?;
    Ok(relative
        .components()
        .map(|component| {
            component
                .as_os_str()
                .to_str()
                .ok_or_else(|| anyhow!("custody paths must be valid UTF-8"))
        })
        .collect::<Result<Vec<_>>>()?
        .join("/"))
}

fn string_field(record: &Value, key: &str, label: &str) -> Result<String> {
    Ok(string_from(object(record, label)?, key, label)?.to_owned())
}

fn set_private_directory(path: &Path) -> Result<()> {
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(path, fs::Permissions::from_mode(0o700))?;
    }
    #[cfg(not(unix))]
    let _ = path;
    Ok(())
}

fn set_private_file(path: &Path) -> Result<()> {
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(path, fs::Permissions::from_mode(0o600))?;
    }
    #[cfg(not(unix))]
    let _ = path;
    Ok(())
}
