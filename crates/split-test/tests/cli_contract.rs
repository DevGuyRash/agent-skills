//! End-to-end contract for the role-neutral Split Testing helper.
#![allow(
    clippy::expect_used,
    clippy::indexing_slicing,
    clippy::missing_const_for_fn,
    clippy::multiple_crate_versions,
    // These are deliberately end-to-end state-machine narratives. Splitting
    // them would hide the prospective ordering and custody invariants they test.
    clippy::too_many_lines
)]

use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs;
use std::io::{BufRead, BufReader, Read, Write};
use std::net::{Shutdown, TcpStream};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Output, Stdio};
use std::sync::OnceLock;
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
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
            "split-test-cli-contract-{}-{nonce}",
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

fn run(args: &[&str]) -> Output {
    Command::new(binary())
        .args(args)
        .output()
        .expect("run split-test")
}

fn run_from(cwd: &Path, args: &[&str]) -> Output {
    Command::new(binary())
        .current_dir(cwd)
        .args(args)
        .output()
        .expect("run split-test")
}

fn run_owned(args: &[String]) -> Output {
    Command::new(binary())
        .args(args)
        .output()
        .expect("run split-test")
}

fn run_with_env(args: &[&str], key: &str, value: &str) -> Output {
    Command::new(binary())
        .args(args)
        .env(key, value)
        .output()
        .expect("run split-test with isolated environment override")
}

fn success(args: &[&str]) -> Value {
    let output = run(args);
    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    serde_json::from_slice(&output.stdout).expect("compact JSON output")
}

fn success_from(cwd: &Path, args: &[&str]) -> Value {
    let output = run_from(cwd, args);
    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    serde_json::from_slice(&output.stdout).expect("compact JSON output")
}

fn success_owned(args: &[String]) -> Value {
    let output = run_owned(args);
    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    serde_json::from_slice(&output.stdout).expect("compact JSON output")
}

fn write_json(path: &Path, value: &Value) {
    fs::write(path, serde_json::to_vec(value).expect("serialize JSON")).expect("write JSON");
}

fn write_raw(path: &Path, text: &str) {
    fs::write(path, text).expect("write raw JSON");
}

fn stdout_text(output: &Output) -> String {
    String::from_utf8(output.stdout.clone()).expect("UTF-8 stdout")
}

fn stderr_text(output: &Output) -> String {
    String::from_utf8(output.stderr.clone()).expect("UTF-8 stderr")
}

fn setup() -> (TempDir, PathBuf) {
    let temp = tempfile::tempdir().expect("tempdir");
    let root = temp.path().join("workspace");
    fs::create_dir(&root).expect("create root");
    let root_arg = root.to_string_lossy().into_owned();
    let result = success(&["init", &root_arg]);
    assert_eq!(result["schema"], "split-testing-workspace.v2");
    (temp, root)
}

fn add_commitment(temp: &TempDir, root: &Path) {
    let spec = temp.path().join("commitment.json");
    write_json(
        &spec,
        &json!({
            "schema": "split-testing-commitment.v2",
            "commitment_id": "frozen-policy",
            "policy": {"future": [1, 2, 3]},
            "unknown": {"kept": true}
        }),
    );
    success(&[
        "add-commitment",
        &root.to_string_lossy(),
        &spec.to_string_lossy(),
    ]);
}

fn add_work_set(temp: &TempDir, root: &Path) {
    add_work_set_with_units(temp, root, &["u-1", "u-2"]);
}

fn add_work_set_with_units(temp: &TempDir, root: &Path, units: &[&str]) {
    let spec = temp.path().join("work-set.json");
    let units = Value::Array(
        units
            .iter()
            .map(|unit| json!({"unit_id": unit, "private_condition": format!("condition-{unit}")}))
            .collect(),
    );
    write_json(
        &spec,
        &json!({
            "schema": "split-testing-work-set.v2",
            "set_id": "set-a",
            "commitment_refs": ["frozen-policy"],
            "units": units,
            "future": {"retained": true}
        }),
    );
    success(&[
        "add-work-set",
        &root.to_string_lossy(),
        &spec.to_string_lossy(),
    ]);
}

fn prepare(temp: &TempDir, root: &Path, unit: &str) -> PathBuf {
    let input = temp.path().join(format!("input-{unit}.txt"));
    fs::write(&input, format!("input for {unit}\n")).expect("write input");
    let spec = temp.path().join(format!("work-{unit}.json"));
    write_json(
        &spec,
        &json!({
            "schema": "split-testing-work.v2",
            "set_id": "set-a",
            "unit_id": unit,
            "commitment_refs": ["frozen-policy"],
            "effective_input_refs": [{"path": input.to_string_lossy()}],
            "transport_unknown": ["preserve", 7]
        }),
    );
    let result = success(&[
        "prepare-work",
        &root.to_string_lossy(),
        "set-a",
        unit,
        &spec.to_string_lossy(),
    ]);
    PathBuf::from(result["workspace"].as_str().expect("workspace path"))
}

fn seal(temp: &TempDir, root: &Path, unit: &str) {
    seal_with_event(temp, root, unit, "returned");
}

fn seal_with_event(temp: &TempDir, root: &Path, unit: &str, event: &str) {
    let terminal = temp.path().join(format!("terminal-{unit}.json"));
    write_json(
        &terminal,
        &json!({
            "schema": "split-testing-terminal.v2",
            "event": event,
            "observed": {"exit_code": 0}
        }),
    );
    success(&[
        "seal-work",
        &root.to_string_lossy(),
        "set-a",
        unit,
        &terminal.to_string_lossy(),
    ]);
}

fn read_json(path: &Path) -> Value {
    serde_json::from_slice(&fs::read(path).expect("read JSON")).expect("parse JSON")
}

fn only_pending_bytes(root: &Path) -> Vec<u8> {
    let mut entries = fs::read_dir(root.join(".split-testing/pending"))
        .expect("pending directory")
        .collect::<Result<Vec<_>, _>>()
        .expect("pending entries");
    assert_eq!(
        entries.len(),
        1,
        "expected one authoritative pending marker"
    );
    fs::read(entries.pop().expect("pending marker").path()).expect("pending marker bytes")
}

fn spawn_view_server(root: &Path) -> (Child, String) {
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
        .expect("spawn view serve");
    let stdout = child.stdout.take().expect("stdout");
    let mut reader = BufReader::new(stdout);
    let mut line = String::new();
    reader.read_line(&mut line).expect("read serve line");
    let value: Value = serde_json::from_str(&line).expect("parse serve output");
    let url = value["url"].as_str().expect("serve url").to_owned();
    (child, url)
}

fn http_request(address: &str, request: &str) -> Vec<u8> {
    let mut stream = None;
    for _ in 0..50 {
        match TcpStream::connect(address) {
            Ok(conn) => {
                stream = Some(conn);
                break;
            }
            Err(_) => thread::sleep(Duration::from_millis(20)),
        }
    }
    let mut stream = stream.expect("connect to view server");
    stream
        .write_all(request.as_bytes())
        .expect("write HTTP request");
    let mut bytes = Vec::new();
    std::io::Read::read_to_end(&mut stream, &mut bytes).expect("read HTTP response");
    bytes
}

fn http_request_chunks(address: &str, chunks: &[&[u8]]) -> Vec<u8> {
    let mut stream = TcpStream::connect(address).expect("connect view server");
    for chunk in chunks {
        stream.write_all(chunk).expect("write request chunk");
        stream.flush().expect("flush request chunk");
        std::thread::sleep(std::time::Duration::from_millis(15));
    }
    let _ = stream.shutdown(Shutdown::Write);
    let mut bytes = Vec::new();
    stream.read_to_end(&mut bytes).expect("read response");
    bytes
}

fn terminate(child: &mut Child) {
    child.kill().expect("kill server");
    let _ = child.wait();
}

#[test]
fn help_exposes_only_role_neutral_commands() {
    let output = run(&["--help"]);
    assert!(output.status.success());
    let help = String::from_utf8(output.stdout).expect("UTF-8 help");
    for command in [
        "add-commitment",
        "add-work-set",
        "prepare-work",
        "seal-work",
        "close-work-set",
        "publish",
        "reveal",
        "events",
        "receipt",
        "status",
        "view",
    ] {
        assert!(help.contains(command), "missing {command}");
    }
    for legacy in ["add-round", "prepare-run", "add-review-set", "anonymize"] {
        assert!(!help.contains(legacy), "legacy command {legacy}");
    }
}

#[test]
fn init_requires_an_absolute_empty_root_and_rejects_old_workspaces() {
    let relative = run(&["init", "relative"]);
    assert!(!relative.status.success());
    assert!(String::from_utf8_lossy(&relative.stderr).contains("absolute"));

    let temp = tempfile::tempdir().expect("tempdir");
    let nonempty = temp.path().join("nonempty");
    fs::create_dir(&nonempty).expect("mkdir");
    fs::write(nonempty.join("keep"), b"protected").expect("write");
    let rejected = run(&["init", &nonempty.to_string_lossy()]);
    assert!(!rejected.status.success());
    assert_eq!(fs::read(nonempty.join("keep")).expect("read"), b"protected");

    let old = temp.path().join("old");
    fs::create_dir_all(old.join(".split-testing/rounds")).expect("old tree");
    fs::write(
        old.join(".split-testing/workspace.json"),
        br#"{"schema":"split-testing-workspace.v2"}"#,
    )
    .expect("old workspace");
    let status = run(&["status", &old.to_string_lossy()]);
    assert!(!status.status.success());
    assert!(String::from_utf8_lossy(&status.stderr).contains("unsupported"));
}

#[test]
fn exact_specs_unknown_fields_and_events_are_preserved() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set(&temp, &root);
    let workspace = prepare(&temp, &root, "u-1");
    assert!(workspace.is_absolute());
    assert!(workspace.starts_with(&root));
    assert!(fs::read_dir(&workspace)
        .expect("workspace exists")
        .next()
        .is_none());

    let input_objects = root.join(".split-testing/records/work/set-a/u-1/effective-inputs");
    assert!(input_objects.is_dir());

    let events = run(&["events", &root.to_string_lossy(), "--format", "jsonl"]);
    assert!(events.status.success());
    let lines = String::from_utf8(events.stdout).expect("UTF-8 events");
    assert_eq!(lines.lines().count(), 4);
    for line in lines.lines() {
        let value: Value = serde_json::from_str(line).expect("event JSON");
        assert_eq!(value["schema"], "split-testing-event.v2");
    }
}

#[test]
fn prepared_work_record_binds_each_captured_effective_input_manifest() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set(&temp, &root);
    prepare(&temp, &root, "u-1");

    let captured =
        root.join(".split-testing/records/work/set-a/u-1/effective-inputs/0/payload/input-u-1.txt");
    let manifest_path =
        root.join(".split-testing/records/work/set-a/u-1/effective-inputs/0/manifest.json");
    fs::write(&captured, b"substituted input\n").expect("replace captured input");
    let mut manifest = read_json(&manifest_path);
    let file = manifest["entries"]
        .as_array_mut()
        .and_then(|entries| entries.iter_mut().find(|entry| entry["kind"] == "file"))
        .expect("captured file manifest entry");
    file["sha256"] = Value::String(format!("{:x}", Sha256::digest(b"substituted input\n")));
    file["size"] = Value::from(b"substituted input\n".len());
    write_json(&manifest_path, &manifest);

    let status = run(&["status", &root.to_string_lossy()]);
    assert!(!status.status.success());
    assert!(stderr_text(&status).contains("effective-input manifest digest mismatch"));
}

#[test]
fn seal_captures_portable_content_and_status_detects_mutation_from_other_cwd() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set(&temp, &root);
    let workspace = prepare(&temp, &root, "u-1");
    fs::create_dir(workspace.join("empty")).expect("empty dir");
    fs::write(workspace.join("answer.txt"), b"answer\n").expect("answer");
    #[cfg(unix)]
    {
        use std::os::unix::fs::{symlink, PermissionsExt};
        symlink("answer.txt", workspace.join("answer-link")).expect("symlink");
        let mut permissions = fs::metadata(workspace.join("answer.txt"))
            .expect("metadata")
            .permissions();
        permissions.set_mode(0o754);
        fs::set_permissions(workspace.join("answer.txt"), permissions).expect("chmod");
    }
    seal(&temp, &root, "u-1");

    let seal_record =
        read_json(&root.join(".split-testing/records/work/set-a/u-1/seal/record.json"));
    let captured = root.join(
        seal_record["payload_root"]
            .as_str()
            .expect("retained payload reference"),
    );
    assert_eq!(
        fs::read(captured.join("answer.txt")).expect("read retained sealed payload"),
        b"answer\n"
    );
    assert!(captured.join("empty").is_dir());

    let other = tempfile::tempdir().expect("other cwd");
    let okay = run_from(other.path(), &["status", &root.to_string_lossy()]);
    assert!(
        okay.status.success(),
        "{}",
        String::from_utf8_lossy(&okay.stderr)
    );

    fs::write(workspace.join("answer.txt"), b"mutated\n").expect("mutate");
    let changed = success_from(other.path(), &["status", &root.to_string_lossy()]);
    assert!(changed["diagnostics"].as_array().is_some_and(|items| items
        .iter()
        .any(|item| item["kind"] == "sealed-workspace-drift")));
    assert_eq!(
        fs::read(captured.join("answer.txt")).expect("sealed payload survives source mutation"),
        b"answer\n"
    );
}

#[test]
fn event_chain_binds_exact_generated_record_bytes() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    let record = root.join(".split-testing/records/commitments/frozen-policy/record.json");
    let mut bytes = fs::read(&record).expect("read generated record");
    bytes.push(b'\n');
    fs::write(&record, bytes).expect("rewrite semantically equivalent record bytes");

    let status = run(&["status", &root.to_string_lossy()]);
    assert!(!status.status.success());
    assert!(stderr_text(&status).contains("record digest mismatch"));
}

#[test]
fn sealing_rejects_escaping_symlinks_and_nonmechanical_terminal_claims() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set(&temp, &root);
    let workspace = prepare(&temp, &root, "u-1");
    #[cfg(unix)]
    {
        std::os::unix::fs::symlink("../../../../outside", workspace.join("escape"))
            .expect("symlink");
        let terminal = temp.path().join("terminal.json");
        write_json(
            &terminal,
            &json!({"schema": "split-testing-terminal.v2", "event": "returned"}),
        );
        let rejected = run(&[
            "seal-work",
            &root.to_string_lossy(),
            "set-a",
            "u-1",
            &terminal.to_string_lossy(),
        ]);
        assert!(!rejected.status.success());
        assert!(String::from_utf8_lossy(&rejected.stderr).contains("symlink"));
        fs::remove_file(workspace.join("escape")).expect("remove escape");
    }

    let invalid = temp.path().join("semantic-terminal.json");
    write_json(
        &invalid,
        &json!({"schema": "split-testing-terminal.v2", "event": "task-succeeded"}),
    );
    let rejected = run(&[
        "seal-work",
        &root.to_string_lossy(),
        "set-a",
        "u-1",
        &invalid.to_string_lossy(),
    ]);
    assert!(!rejected.status.success());
    assert!(String::from_utf8_lossy(&rejected.stderr).contains("mechanical"));
}

#[test]
fn closure_publication_and_reveal_require_complete_prospective_accounting() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set(&temp, &root);
    for unit in ["u-1", "u-2"] {
        let workspace = prepare(&temp, &root, unit);
        fs::write(workspace.join("result.txt"), format!("{unit} result\n")).expect("result");
        seal(&temp, &root, unit);
    }

    let incomplete = temp.path().join("incomplete-closure.json");
    write_json(
        &incomplete,
        &json!({
            "schema": "split-testing-work-closure.v2",
            "set_id": "set-a",
            "units": [{"unit_id": "u-1", "status": "completed"}]
        }),
    );
    let rejected = run(&[
        "close-work-set",
        &root.to_string_lossy(),
        "set-a",
        &incomplete.to_string_lossy(),
    ]);
    assert!(!rejected.status.success());
    assert!(String::from_utf8_lossy(&rejected.stderr).contains("every frozen unit"));

    let closure = temp.path().join("closure.json");
    write_json(
        &closure,
        &json!({
            "schema": "split-testing-work-closure.v2",
            "set_id": "set-a",
            "units": [
                {"unit_id": "u-1", "status": "completed"},
                {"unit_id": "u-2", "status": "completed"}
            ]
        }),
    );
    success(&[
        "close-work-set",
        &root.to_string_lossy(),
        "set-a",
        &closure.to_string_lossy(),
    ]);

    let publication = temp.path().join("publication.json");
    write_json(
        &publication,
        &json!({
            "schema": "split-testing-publication.v2",
            "publication_id": "blind-one",
            "set_id": "set-a",
            "commitment_refs": ["frozen-policy"],
            "units": [
                {"unit_id": "u-1", "admitted": true, "reason": "prospective policy"},
                {"unit_id": "u-2", "admitted": false, "reason": "prospective exclusion"}
            ]
        }),
    );
    let published = success(&[
        "publish",
        &root.to_string_lossy(),
        &publication.to_string_lossy(),
    ]);
    let blind_root = PathBuf::from(published["blind_root"].as_str().expect("blind root"));
    assert!(
        !blind_root.to_string_lossy().contains("blind-one"),
        "blind delivery paths must not disclose the controller publication identity"
    );
    let blind_names = fs::read_dir(&blind_root)
        .expect("blind root")
        .map(|entry| {
            entry
                .expect("entry")
                .file_name()
                .to_string_lossy()
                .into_owned()
        })
        .collect::<Vec<_>>();
    assert_eq!(blind_names.len(), 1);
    assert!(!blind_names[0].contains("u-1"));
    let blind_bytes = fs::read_dir(&blind_root)
        .expect("blind root")
        .next()
        .expect("blind entry")
        .expect("entry")
        .path();
    assert!(!blind_bytes.join("identity-map.json").exists());

    let mapping_path =
        root.join(".split-testing/records/publications/blind-one/private-mapping.json");
    let retained_mapping = fs::read(&mapping_path).expect("retained mapping");
    fs::write(
        &mapping_path,
        b"[{\"opaque_id\":\"item-forged\",\"set_id\":\"set-a\",\"unit_id\":\"u-2\"}]\n",
    )
    .expect("forge mapping");
    let mapping_mutation = run(&["status", &root.to_string_lossy()]);
    assert!(!mapping_mutation.status.success());
    assert!(stderr_text(&mapping_mutation).contains("private mapping mutation"));
    fs::write(&mapping_path, retained_mapping).expect("restore mapping");

    let second_set = temp.path().join("work-set-b.json");
    write_json(
        &second_set,
        &json!({
            "schema": "split-testing-work-set.v2",
            "set_id": "set-b",
            "commitment_refs": ["frozen-policy"],
            "units": [{"unit_id": "b-1"}]
        }),
    );
    success(&[
        "add-work-set",
        &root.to_string_lossy(),
        &second_set.to_string_lossy(),
    ]);
    let second_closure = temp.path().join("closure-b.json");
    write_json(
        &second_closure,
        &json!({
            "schema": "split-testing-work-closure.v2",
            "set_id": "set-b",
            "units": [{"unit_id": "b-1", "status": "withheld"}]
        }),
    );
    success(&[
        "close-work-set",
        &root.to_string_lossy(),
        "set-b",
        &second_closure.to_string_lossy(),
    ]);
    let unrelated_reveal = temp.path().join("unrelated-reveal.json");
    write_json(
        &unrelated_reveal,
        &json!({
            "schema": "split-testing-reveal.v2",
            "reveal_id": "reveal-unrelated",
            "publication_id": "blind-one",
            "closure_refs": ["set-b"]
        }),
    );
    let unrelated = run(&[
        "reveal",
        &root.to_string_lossy(),
        &unrelated_reveal.to_string_lossy(),
    ]);
    assert!(!unrelated.status.success());
    assert!(stderr_text(&unrelated).contains("publication work-set closure"));

    let reveal = temp.path().join("reveal.json");
    write_json(
        &reveal,
        &json!({
            "schema": "split-testing-reveal.v2",
            "reveal_id": "reveal-one",
            "publication_id": "blind-one",
            "closure_refs": ["set-a"]
        }),
    );
    let revealed = success(&["reveal", &root.to_string_lossy(), &reveal.to_string_lossy()]);
    let reveal_root = PathBuf::from(revealed["reveal_root"].as_str().expect("reveal root"));
    assert_ne!(reveal_root, blind_root);
    assert!(reveal_root.join("identity-map.json").is_file());
    assert!(!blind_root.join("identity-map.json").exists());
}

#[test]
fn a_closed_work_set_rejects_first_time_prepare_and_seal_operations() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set_with_units(&temp, &root, &["u-1"]);
    let lost_closure = temp.path().join("closed-before-prepare.json");
    write_json(
        &lost_closure,
        &json!({
            "schema": "split-testing-work-closure.v2",
            "set_id": "set-a",
            "units": [{"unit_id": "u-1", "status": "lost"}]
        }),
    );
    success(&[
        "close-work-set",
        &root.to_string_lossy(),
        "set-a",
        &lost_closure.to_string_lossy(),
    ]);
    let late_work = temp.path().join("late-work.json");
    write_json(
        &late_work,
        &json!({
            "schema": "split-testing-work.v2",
            "set_id": "set-a",
            "unit_id": "u-1",
            "commitment_refs": ["frozen-policy"]
        }),
    );
    let late_prepare = run(&[
        "prepare-work",
        &root.to_string_lossy(),
        "set-a",
        "u-1",
        &late_work.to_string_lossy(),
    ]);
    assert!(!late_prepare.status.success());
    assert!(stderr_text(&late_prepare).contains("work set is already closed"));

    let seal_root = temp.path().join("closed-before-seal");
    fs::create_dir(&seal_root).expect("seal root");
    success(&["init", &seal_root.to_string_lossy()]);
    add_commitment(&temp, &seal_root);
    add_work_set_with_units(&temp, &seal_root, &["u-1"]);
    prepare(&temp, &seal_root, "u-1");
    let withheld_closure = temp.path().join("closed-before-seal.json");
    write_json(
        &withheld_closure,
        &json!({
            "schema": "split-testing-work-closure.v2",
            "set_id": "set-a",
            "units": [{"unit_id": "u-1", "status": "withheld"}]
        }),
    );
    success(&[
        "close-work-set",
        &seal_root.to_string_lossy(),
        "set-a",
        &withheld_closure.to_string_lossy(),
    ]);
    let terminal = temp.path().join("late-terminal.json");
    write_json(
        &terminal,
        &json!({
            "schema": "split-testing-terminal.v2",
            "event": "returned"
        }),
    );
    let late_seal = run(&[
        "seal-work",
        &seal_root.to_string_lossy(),
        "set-a",
        "u-1",
        &terminal.to_string_lossy(),
    ]);
    assert!(!late_seal.status.success());
    assert!(stderr_text(&late_seal).contains("work set is already closed"));
}

#[test]
fn publication_and_reveal_construction_remain_private_until_marker_arming() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set_with_units(&temp, &root, &["u-1"]);
    let workspace = prepare(&temp, &root, "u-1");
    fs::write(workspace.join("answer.txt"), b"answer\n").expect("answer");
    seal(&temp, &root, "u-1");
    let closure = temp.path().join("fault-closure.json");
    write_json(
        &closure,
        &json!({
            "schema": "split-testing-work-closure.v2",
            "set_id": "set-a",
            "units": [{"unit_id": "u-1", "status": "completed"}]
        }),
    );
    success(&[
        "close-work-set",
        &root.to_string_lossy(),
        "set-a",
        &closure.to_string_lossy(),
    ]);
    let publication = temp.path().join("fault-publication.json");
    write_json(
        &publication,
        &json!({
            "schema": "split-testing-publication.v2",
            "publication_id": "fault-publication",
            "set_id": "set-a",
            "commitment_refs": ["frozen-policy"],
            "units": [{"unit_id": "u-1", "admitted": true, "reason": "prospective"}]
        }),
    );
    let injected_publication = run_with_env(
        &[
            "publish",
            &root.to_string_lossy(),
            &publication.to_string_lossy(),
        ],
        "SPLIT_TEST_TEST_FAIL_AFTER_OUTPUT_CONSTRUCTION",
        "publication",
    );
    assert!(!injected_publication.status.success());
    assert!(stderr_text(&injected_publication).contains("injected output-construction failure"));
    assert_eq!(
        fs::read_dir(root.join(".split-testing/pending"))
            .expect("pending markers after publication injection")
            .count(),
        0,
        "fault occurs before pending-event arming"
    );
    assert_eq!(
        fs::read_dir(root.join("publications"))
            .expect("publication namespace")
            .count(),
        0,
        "constructed output must remain controller-private before marker arming"
    );
    let published = success(&[
        "publish",
        &root.to_string_lossy(),
        &publication.to_string_lossy(),
    ]);
    assert!(Path::new(published["blind_root"].as_str().expect("blind root")).is_dir());
    assert_eq!(
        fs::read_dir(root.join("publications"))
            .expect("publication namespace")
            .count(),
        1
    );

    let reveal = temp.path().join("fault-reveal.json");
    write_json(
        &reveal,
        &json!({
            "schema": "split-testing-reveal.v2",
            "reveal_id": "fault-reveal",
            "publication_id": "fault-publication",
            "closure_refs": ["set-a"]
        }),
    );
    let injected_reveal = run_with_env(
        &["reveal", &root.to_string_lossy(), &reveal.to_string_lossy()],
        "SPLIT_TEST_TEST_FAIL_AFTER_OUTPUT_CONSTRUCTION",
        "reveal",
    );
    assert!(!injected_reveal.status.success());
    assert!(stderr_text(&injected_reveal).contains("injected output-construction failure"));
    assert_eq!(
        fs::read_dir(root.join(".split-testing/pending"))
            .expect("pending markers after reveal injection")
            .count(),
        0,
        "fault occurs before pending-event arming"
    );
    assert_eq!(
        fs::read_dir(root.join("reveals"))
            .expect("reveal namespace")
            .count(),
        0,
        "constructed reveal must remain controller-private before marker arming"
    );
    let revealed = success(&["reveal", &root.to_string_lossy(), &reveal.to_string_lossy()]);
    assert!(Path::new(revealed["reveal_root"].as_str().expect("reveal root")).is_dir());
    assert_eq!(
        fs::read_dir(root.join("reveals"))
            .expect("reveal namespace")
            .count(),
        1
    );
    assert_eq!(
        fs::read_dir(root.join(".split-testing/pending"))
            .expect("pending markers")
            .count(),
        0
    );
    success(&["status", &root.to_string_lossy()]);
}

#[test]
fn post_publication_effect_crash_cannot_rebind_output_to_different_spec_bytes() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set_with_units(&temp, &root, &["u-1"]);
    let workspace = prepare(&temp, &root, "u-1");
    fs::write(workspace.join("answer.txt"), b"answer\n").expect("answer");
    seal(&temp, &root, "u-1");
    let closure = temp.path().join("publication-tail-closure.json");
    write_json(
        &closure,
        &json!({
            "schema": "split-testing-work-closure.v2",
            "set_id": "set-a",
            "units": [{"unit_id": "u-1", "status": "completed"}]
        }),
    );
    success(&[
        "close-work-set",
        &root.to_string_lossy(),
        "set-a",
        &closure.to_string_lossy(),
    ]);
    let original = temp.path().join("publication-tail-original.json");
    write_json(
        &original,
        &json!({
            "schema": "split-testing-publication.v2",
            "publication_id": "tail-publication",
            "set_id": "set-a",
            "commitment_refs": ["frozen-policy"],
            "units": [{"unit_id": "u-1", "admitted": true, "reason": "original policy application"}]
        }),
    );
    let interrupted = run_with_env(
        &[
            "publish",
            &root.to_string_lossy(),
            &original.to_string_lossy(),
        ],
        "SPLIT_TEST_TEST_FAIL_AFTER_EFFECT_COMMIT",
        "publication",
    );
    assert!(!interrupted.status.success());
    assert!(stderr_text(&interrupted).contains("injected post-effect failure"));
    assert_eq!(
        fs::read_dir(root.join("publications"))
            .expect("publication namespace")
            .count(),
        1
    );
    assert!(!root
        .join(".split-testing/records/publications/tail-publication/record.json")
        .exists());
    let pending_before = only_pending_bytes(&root);

    let changed = temp.path().join("publication-tail-changed.json");
    write_json(
        &changed,
        &json!({
            "schema": "split-testing-publication.v2",
            "publication_id": "tail-publication",
            "set_id": "set-a",
            "commitment_refs": ["frozen-policy"],
            "units": [{"unit_id": "u-1", "admitted": true, "reason": "different bytes, same published payload"}]
        }),
    );
    let rebound = run(&[
        "publish",
        &root.to_string_lossy(),
        &changed.to_string_lossy(),
    ]);
    assert!(!rebound.status.success());
    assert!(stderr_text(&rebound).contains("committed effect has no exact custody record"));
    assert_eq!(only_pending_bytes(&root), pending_before);
    assert!(!root
        .join(".split-testing/records/publications/tail-publication/record.json")
        .exists());
}

#[test]
fn post_reveal_effect_crash_cannot_rebind_output_to_different_spec_bytes() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set_with_units(&temp, &root, &["u-1"]);
    let workspace = prepare(&temp, &root, "u-1");
    fs::write(workspace.join("answer.txt"), b"answer\n").expect("answer");
    seal(&temp, &root, "u-1");
    let closure = temp.path().join("reveal-tail-closure.json");
    write_json(
        &closure,
        &json!({
            "schema": "split-testing-work-closure.v2",
            "set_id": "set-a",
            "units": [{"unit_id": "u-1", "status": "completed"}]
        }),
    );
    success(&[
        "close-work-set",
        &root.to_string_lossy(),
        "set-a",
        &closure.to_string_lossy(),
    ]);
    let publication = temp.path().join("reveal-tail-publication.json");
    write_json(
        &publication,
        &json!({
            "schema": "split-testing-publication.v2",
            "publication_id": "reveal-source",
            "set_id": "set-a",
            "commitment_refs": ["frozen-policy"],
            "units": [{"unit_id": "u-1", "admitted": true, "reason": "prospective"}]
        }),
    );
    success(&[
        "publish",
        &root.to_string_lossy(),
        &publication.to_string_lossy(),
    ]);
    let original = temp.path().join("reveal-tail-original.json");
    write_json(
        &original,
        &json!({
            "schema": "split-testing-reveal.v2",
            "reveal_id": "tail-reveal",
            "publication_id": "reveal-source",
            "closure_refs": ["set-a"],
            "extension_note": "original"
        }),
    );
    let interrupted = run_with_env(
        &[
            "reveal",
            &root.to_string_lossy(),
            &original.to_string_lossy(),
        ],
        "SPLIT_TEST_TEST_FAIL_AFTER_EFFECT_COMMIT",
        "reveal",
    );
    assert!(!interrupted.status.success());
    assert!(stderr_text(&interrupted).contains("injected post-effect failure"));
    assert!(root.join("reveals/tail-reveal").is_dir());
    assert!(!root
        .join(".split-testing/records/reveals/tail-reveal/record.json")
        .exists());
    let pending_before = only_pending_bytes(&root);

    let changed = temp.path().join("reveal-tail-changed.json");
    write_json(
        &changed,
        &json!({
            "schema": "split-testing-reveal.v2",
            "reveal_id": "tail-reveal",
            "publication_id": "reveal-source",
            "closure_refs": ["set-a"],
            "extension_note": "changed bytes, same revealed payload"
        }),
    );
    let rebound = run(&[
        "reveal",
        &root.to_string_lossy(),
        &changed.to_string_lossy(),
    ]);
    assert!(!rebound.status.success());
    assert!(stderr_text(&rebound).contains("committed effect has no exact custody record"));
    assert_eq!(only_pending_bytes(&root), pending_before);
    assert!(!root
        .join(".split-testing/records/reveals/tail-reveal/record.json")
        .exists());
}

#[test]
fn post_seal_effect_crash_cannot_rebind_payload_to_different_terminal_bytes() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set_with_units(&temp, &root, &["u-1"]);
    let workspace = prepare(&temp, &root, "u-1");
    fs::write(workspace.join("answer.txt"), b"answer\n").expect("answer");
    let original = temp.path().join("seal-tail-original.json");
    write_json(
        &original,
        &json!({
            "schema": "split-testing-terminal.v2",
            "event": "returned",
            "transport_note": "original"
        }),
    );
    let interrupted = run_with_env(
        &[
            "seal-work",
            &root.to_string_lossy(),
            "set-a",
            "u-1",
            &original.to_string_lossy(),
        ],
        "SPLIT_TEST_TEST_FAIL_AFTER_EFFECT_COMMIT",
        "seal",
    );
    assert!(!interrupted.status.success());
    assert!(stderr_text(&interrupted).contains("injected post-effect failure"));
    assert!(root
        .join(".split-testing/objects/sealed/set-a/u-1/payload")
        .is_dir());
    assert!(!root
        .join(".split-testing/records/work/set-a/u-1/seal/record.json")
        .exists());
    let pending_before = only_pending_bytes(&root);

    let changed = temp.path().join("seal-tail-changed.json");
    write_json(
        &changed,
        &json!({
            "schema": "split-testing-terminal.v2",
            "event": "returned",
            "transport_note": "changed bytes, same workspace manifest"
        }),
    );
    let rebound = run(&[
        "seal-work",
        &root.to_string_lossy(),
        "set-a",
        "u-1",
        &changed.to_string_lossy(),
    ]);
    assert!(!rebound.status.success());
    assert!(stderr_text(&rebound).contains("committed effect has no exact custody record"));
    assert_eq!(only_pending_bytes(&root), pending_before);
    assert!(!root
        .join(".split-testing/records/work/set-a/u-1/seal/record.json")
        .exists());
}

#[test]
fn repeated_commands_are_idempotent_and_conflicting_identity_reuse_fails() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    let before = success(&["receipt", &root.to_string_lossy()]);
    add_commitment(&temp, &root);
    let after = success(&["receipt", &root.to_string_lossy()]);
    assert_eq!(before, after);

    let conflict = temp.path().join("commitment-conflict.json");
    write_json(
        &conflict,
        &json!({
            "schema": "split-testing-commitment.v2",
            "commitment_id": "frozen-policy",
            "changed": true
        }),
    );
    let rejected = run(&[
        "add-commitment",
        &root.to_string_lossy(),
        &conflict.to_string_lossy(),
    ]);
    assert!(!rejected.status.success());
    assert!(String::from_utf8_lossy(&rejected.stderr).contains("different content"));
}

#[test]
fn exact_raw_specs_terminal_bytes_and_unknown_fields_are_retained_verbatim() {
    let (temp, root) = setup();

    let commitment = temp.path().join("commitment-raw.json");
    let commitment_bytes = concat!(
        "{\n",
        "  \"schema\": \"split-testing-commitment.v2\",\n",
        "  \"commitment_id\": \"frozen-policy\",\n",
        "  \"policy\": {\"future\": [1, 2, 3]},\n",
        "  \"unknown\": {\"kept\": true}\n",
        "}\n"
    );
    write_raw(&commitment, commitment_bytes);
    success(&[
        "add-commitment",
        &root.to_string_lossy(),
        &commitment.to_string_lossy(),
    ]);
    let retained_commitment =
        root.join(".split-testing/records/commitments/frozen-policy/spec.json");
    assert_eq!(
        fs::read(&retained_commitment).expect("retained commitment"),
        commitment_bytes.as_bytes()
    );
    assert_eq!(read_json(&retained_commitment)["unknown"]["kept"], true);

    let work_set = temp.path().join("work-set-raw.json");
    let work_set_bytes = concat!(
        "{\n",
        "  \"schema\": \"split-testing-work-set.v2\",\n",
        "  \"set_id\": \"set-a\",\n",
        "  \"commitment_refs\": [\"frozen-policy\"],\n",
        "  \"units\": [{\"unit_id\": \"u-1\", \"transport\": {\"unknown\": true}}],\n",
        "  \"future\": {\"retained\": true}\n",
        "}\n"
    );
    write_raw(&work_set, work_set_bytes);
    success(&[
        "add-work-set",
        &root.to_string_lossy(),
        &work_set.to_string_lossy(),
    ]);

    let input = temp.path().join("payload.bin");
    fs::write(&input, [0_u8, 1, 2, 3, 255]).expect("write payload");
    let work = temp.path().join("work-raw.json");
    let work_bytes = format!(
        concat!(
            "{{\n",
            "  \"schema\": \"split-testing-work.v2\",\n",
            "  \"set_id\": \"set-a\",\n",
            "  \"unit_id\": \"u-1\",\n",
            "  \"commitment_refs\": [\"frozen-policy\"],\n",
            "  \"effective_input_refs\": [{{\"path\": \"{}\"}}, {{\"opaque\": true}}],\n",
            "  \"native_payload\": {{\"bytes\": [0, 1, 2, 3, 255]}},\n",
            "  \"unknown_transport\": [\"preserve\", 7]\n",
            "}}\n"
        ),
        input.display()
    );
    write_raw(&work, &work_bytes);
    success(&[
        "prepare-work",
        &root.to_string_lossy(),
        "set-a",
        "u-1",
        &work.to_string_lossy(),
    ]);
    let retained_work = root.join(".split-testing/records/work/set-a/u-1/spec.json");
    assert_eq!(
        fs::read(&retained_work).expect("retained work"),
        work_bytes.as_bytes()
    );
    assert_eq!(
        read_json(&retained_work)["unknown_transport"][0],
        Value::String("preserve".to_owned())
    );
    assert_eq!(
        read_json(&root.join(".split-testing/records/work/set-a/u-1/record.json"))
            ["effective_inputs"][1]["availability"],
        "unavailable-or-opaque"
    );

    let terminal = temp.path().join("terminal-raw.json");
    let terminal_bytes = concat!(
        "{\n",
        "  \"schema\": \"split-testing-terminal.v2\",\n",
        "  \"event\": \"returned\",\n",
        "  \"observed\": {\"stdout_bytes\": [0, 10, 255]},\n",
        "  \"unknown\": {\"retained\": true}\n",
        "}\n"
    );
    write_raw(&terminal, terminal_bytes);
    success(&[
        "seal-work",
        &root.to_string_lossy(),
        "set-a",
        "u-1",
        &terminal.to_string_lossy(),
    ]);
    let retained_terminal = root.join(".split-testing/records/work/set-a/u-1/seal/terminal.json");
    assert_eq!(
        fs::read(&retained_terminal).expect("retained terminal"),
        terminal_bytes.as_bytes()
    );
    assert_eq!(read_json(&retained_terminal)["unknown"]["retained"], true);
}

#[test]
fn prepare_work_serializes_same_input_reuses_identity_and_keeps_workspaces_isolated() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set_with_units(&temp, &root, &["u-1", "u-2"]);

    let input = temp.path().join("shared.txt");
    fs::write(&input, "shared\n").expect("write shared input");

    let spec = temp.path().join("work-u-1.json");
    write_json(
        &spec,
        &json!({
            "schema": "split-testing-work.v2",
            "set_id": "set-a",
            "unit_id": "u-1",
            "commitment_refs": ["frozen-policy"],
            "effective_input_refs": [{"path": input.to_string_lossy()}],
            "native_format": {"kind": "application/octet-stream"}
        }),
    );
    let first = success(&[
        "prepare-work",
        &root.to_string_lossy(),
        "set-a",
        "u-1",
        &spec.to_string_lossy(),
    ]);
    let second = success(&[
        "prepare-work",
        &root.to_string_lossy(),
        "set-a",
        "u-1",
        &spec.to_string_lossy(),
    ]);
    assert_eq!(first["created"], true);
    assert_eq!(second["created"], false);
    assert_eq!(first["workspace"], second["workspace"]);

    let conflict = temp.path().join("work-u-1-conflict.json");
    write_json(
        &conflict,
        &json!({
            "schema": "split-testing-work.v2",
            "set_id": "set-a",
            "unit_id": "u-1",
            "commitment_refs": ["frozen-policy"],
            "effective_input_refs": [{"path": input.to_string_lossy()}],
            "native_format": {"kind": "application/octet-stream"},
            "changed": true
        }),
    );
    let rejected = run(&[
        "prepare-work",
        &root.to_string_lossy(),
        "set-a",
        "u-1",
        &conflict.to_string_lossy(),
    ]);
    assert!(!rejected.status.success());
    assert!(stderr_text(&rejected).contains("different content"));

    let concurrent = temp.path().join("work-u-2.json");
    write_json(
        &concurrent,
        &json!({
            "schema": "split-testing-work.v2",
            "set_id": "set-a",
            "unit_id": "u-2",
            "commitment_refs": ["frozen-policy"],
            "effective_input_refs": [{"path": input.to_string_lossy()}]
        }),
    );
    let root_arg = root.to_string_lossy().into_owned();
    let spec_arg = concurrent.to_string_lossy().into_owned();
    let first_join = thread::spawn({
        let root_arg = root_arg.clone();
        let spec_arg = spec_arg.clone();
        move || {
            success_owned(&[
                "prepare-work".to_owned(),
                root_arg,
                "set-a".to_owned(),
                "u-2".to_owned(),
                spec_arg,
            ])
        }
    });
    let second_join = thread::spawn(move || {
        success_owned(&[
            "prepare-work".to_owned(),
            root_arg,
            "set-a".to_owned(),
            "u-2".to_owned(),
            spec_arg,
        ])
    });
    let concurrent_a = first_join.join().expect("first prepare");
    let concurrent_b = second_join.join().expect("second prepare");
    assert_eq!(concurrent_a["workspace"], concurrent_b["workspace"]);
    let created = [
        concurrent_a["created"].as_bool().expect("created bool"),
        concurrent_b["created"].as_bool().expect("created bool"),
    ];
    assert_eq!(created.into_iter().filter(|value| *value).count(), 1);

    let first_workspace = PathBuf::from(first["workspace"].as_str().expect("u-1 workspace"));
    let second_workspace =
        PathBuf::from(concurrent_a["workspace"].as_str().expect("u-2 workspace"));
    assert_ne!(first_workspace, second_workspace);
    assert!(first_workspace.is_absolute());
    assert!(second_workspace.is_absolute());
    assert!(first_workspace.starts_with(&root));
    assert!(second_workspace.starts_with(&root));
    assert!(fs::read_dir(&first_workspace)
        .expect("u-1 workspace")
        .next()
        .is_none());
    assert!(fs::read_dir(&second_workspace)
        .expect("u-2 workspace")
        .next()
        .is_none());
}

#[test]
fn invalid_references_and_all_mechanical_terminal_states_follow_the_contract() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set_with_units(&temp, &root, &["u-1", "u-2", "u-3", "u-4", "u-5", "u-6"]);

    let mismatch = temp.path().join("mismatch.json");
    write_json(
        &mismatch,
        &json!({
            "schema": "split-testing-work.v2",
            "set_id": "set-b",
            "unit_id": "u-1",
            "commitment_refs": ["frozen-policy"]
        }),
    );
    let mismatch_output = run(&[
        "prepare-work",
        &root.to_string_lossy(),
        "set-a",
        "u-1",
        &mismatch.to_string_lossy(),
    ]);
    assert!(!mismatch_output.status.success());
    assert!(stderr_text(&mismatch_output).contains("does not match the command identity"));

    let unknown_unit = temp.path().join("unknown-unit.json");
    write_json(
        &unknown_unit,
        &json!({
            "schema": "split-testing-work.v2",
            "set_id": "set-a",
            "unit_id": "unknown",
            "commitment_refs": ["frozen-policy"]
        }),
    );
    let unknown_output = run(&[
        "prepare-work",
        &root.to_string_lossy(),
        "set-a",
        "unknown",
        &unknown_unit.to_string_lossy(),
    ]);
    assert!(!unknown_output.status.success());
    assert!(stderr_text(&unknown_output).contains("not frozen"));

    let unprepared_seal = temp.path().join("unprepared-terminal.json");
    write_json(
        &unprepared_seal,
        &json!({"schema": "split-testing-terminal.v2", "event": "returned"}),
    );
    let unprepared_output = run(&[
        "seal-work",
        &root.to_string_lossy(),
        "set-a",
        "u-1",
        &unprepared_seal.to_string_lossy(),
    ]);
    assert!(!unprepared_output.status.success());
    assert!(stderr_text(&unprepared_output).contains("missing prepared work"));

    let terminal_events = [
        ("u-1", "returned"),
        ("u-2", "spawn-failed"),
        ("u-3", "timed-out"),
        ("u-4", "signaled"),
        ("u-5", "controller-aborted"),
        ("u-6", "lost"),
    ];
    for (unit, event) in terminal_events {
        prepare(&temp, &root, unit);
        let sealed = {
            let terminal = temp.path().join(format!("{unit}-{event}.json"));
            write_json(
                &terminal,
                &json!({
                    "schema": "split-testing-terminal.v2",
                    "event": event,
                    "native_terminal": {"kind": "opaque", "event": event}
                }),
            );
            success(&[
                "seal-work",
                &root.to_string_lossy(),
                "set-a",
                unit,
                &terminal.to_string_lossy(),
            ])
        };
        assert_eq!(sealed["created"], true, "{event} should be accepted");
    }
}

#[test]
fn closure_publication_and_reveal_enforce_accounting_prerequisites_and_idempotence() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set(&temp, &root);

    let not_closed_publication = temp.path().join("not-closed-publication.json");
    write_json(
        &not_closed_publication,
        &json!({
            "schema": "split-testing-publication.v2",
            "publication_id": "blind-zero",
            "set_id": "set-a",
            "commitment_refs": ["frozen-policy"],
            "units": [
                {"unit_id": "u-1", "admitted": true, "reason": "ready"},
                {"unit_id": "u-2", "admitted": false, "reason": "held"}
            ]
        }),
    );
    let unpublished = run(&[
        "publish",
        &root.to_string_lossy(),
        &not_closed_publication.to_string_lossy(),
    ]);
    assert!(!unpublished.status.success());
    assert!(stderr_text(&unpublished).contains("work-set closure"));

    let workspace = prepare(&temp, &root, "u-1");
    fs::write(workspace.join("result.txt"), b"u-1\n").expect("u-1 result");
    seal(&temp, &root, "u-1");
    prepare(&temp, &root, "u-2");

    let completed_unsealed = temp.path().join("completed-unsealed.json");
    write_json(
        &completed_unsealed,
        &json!({
            "schema": "split-testing-work-closure.v2",
            "set_id": "set-a",
            "units": [
                {"unit_id": "u-1", "status": "completed"},
                {"unit_id": "u-2", "status": "completed"}
            ]
        }),
    );
    let unsealed = run(&[
        "close-work-set",
        &root.to_string_lossy(),
        "set-a",
        &completed_unsealed.to_string_lossy(),
    ]);
    assert!(!unsealed.status.success());
    assert!(stderr_text(&unsealed).contains("has no sealed evidence"));

    let closure = temp.path().join("closure-neutral.json");
    write_json(
        &closure,
        &json!({
            "schema": "split-testing-work-closure.v2",
            "set_id": "set-a",
            "units": [
                {"unit_id": "u-1", "status": "completed"},
                {"unit_id": "u-2", "status": "withheld"}
            ]
        }),
    );
    let first_closure = success(&[
        "close-work-set",
        &root.to_string_lossy(),
        "set-a",
        &closure.to_string_lossy(),
    ]);
    let second_closure = success(&[
        "close-work-set",
        &root.to_string_lossy(),
        "set-a",
        &closure.to_string_lossy(),
    ]);
    assert_eq!(first_closure["created"], true);
    assert_eq!(second_closure["created"], false);

    let duplicate_publication = temp.path().join("duplicate-publication.json");
    write_json(
        &duplicate_publication,
        &json!({
            "schema": "split-testing-publication.v2",
            "publication_id": "blind-dup",
            "set_id": "set-a",
            "commitment_refs": ["frozen-policy"],
            "units": [
                {"unit_id": "u-1", "admitted": true, "reason": "ready"},
                {"unit_id": "u-1", "admitted": false, "reason": "duplicate"}
            ]
        }),
    );
    let duplicate = run(&[
        "publish",
        &root.to_string_lossy(),
        &duplicate_publication.to_string_lossy(),
    ]);
    assert!(!duplicate.status.success());
    assert!(stderr_text(&duplicate).contains("repeats unit"));

    let incomplete_publication = temp.path().join("incomplete-publication.json");
    write_json(
        &incomplete_publication,
        &json!({
            "schema": "split-testing-publication.v2",
            "publication_id": "blind-incomplete",
            "set_id": "set-a",
            "commitment_refs": ["frozen-policy"],
            "units": [{"unit_id": "u-1", "admitted": true, "reason": "ready"}]
        }),
    );
    let incomplete = run(&[
        "publish",
        &root.to_string_lossy(),
        &incomplete_publication.to_string_lossy(),
    ]);
    assert!(!incomplete.status.success());
    assert!(stderr_text(&incomplete).contains("exactly once"));

    let publication = temp.path().join("publication.json");
    write_json(
        &publication,
        &json!({
            "schema": "split-testing-publication.v2",
            "publication_id": "blind-one",
            "set_id": "set-a",
            "commitment_refs": ["frozen-policy"],
            "units": [
                {"unit_id": "u-1", "admitted": true, "reason": "ready"},
                {"unit_id": "u-2", "admitted": false, "reason": "withheld"}
            ]
        }),
    );
    let first_publication = success(&[
        "publish",
        &root.to_string_lossy(),
        &publication.to_string_lossy(),
    ]);
    let second_publication = success(&[
        "publish",
        &root.to_string_lossy(),
        &publication.to_string_lossy(),
    ]);
    assert_eq!(first_publication["created"], true);
    assert_eq!(second_publication["created"], false);
    let blind_root = PathBuf::from(
        first_publication["blind_root"]
            .as_str()
            .expect("blind root"),
    );
    assert_eq!(fs::read_dir(&blind_root).expect("blind root").count(), 1);

    let missing_publication_reveal = temp.path().join("missing-publication-reveal.json");
    write_json(
        &missing_publication_reveal,
        &json!({
            "schema": "split-testing-reveal.v2",
            "reveal_id": "reveal-missing",
            "publication_id": "missing",
            "closure_refs": ["set-a"]
        }),
    );
    let missing_publication = run(&[
        "reveal",
        &root.to_string_lossy(),
        &missing_publication_reveal.to_string_lossy(),
    ]);
    assert!(!missing_publication.status.success());
    assert!(stderr_text(&missing_publication).contains("missing publication"));

    let empty_closures = temp.path().join("empty-closure-refs.json");
    write_json(
        &empty_closures,
        &json!({
            "schema": "split-testing-reveal.v2",
            "reveal_id": "reveal-empty",
            "publication_id": "blind-one",
            "closure_refs": []
        }),
    );
    let missing_closure = run(&[
        "reveal",
        &root.to_string_lossy(),
        &empty_closures.to_string_lossy(),
    ]);
    assert!(!missing_closure.status.success());
    assert!(stderr_text(&missing_closure).contains("must not be empty"));

    let reveal = temp.path().join("reveal.json");
    write_json(
        &reveal,
        &json!({
            "schema": "split-testing-reveal.v2",
            "reveal_id": "reveal-one",
            "publication_id": "blind-one",
            "closure_refs": ["set-a"]
        }),
    );
    let first_reveal = success(&["reveal", &root.to_string_lossy(), &reveal.to_string_lossy()]);
    let second_reveal = success(&["reveal", &root.to_string_lossy(), &reveal.to_string_lossy()]);
    let reveal_root = PathBuf::from(first_reveal["reveal_root"].as_str().expect("reveal root"));
    assert_eq!(first_reveal["created"], true);
    assert_eq!(second_reveal["created"], false);
    assert_ne!(reveal_root, blind_root);
    assert!(reveal_root.join("identity-map.json").is_file());
    assert!(!blind_root.join("identity-map.json").exists());
}

#[test]
fn events_and_status_detect_deletion_reorder_and_record_mutation_with_deterministic_filters() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set(&temp, &root);
    let workspace = prepare(&temp, &root, "u-1");
    fs::write(workspace.join("result.txt"), b"result\n").expect("result");
    seal(&temp, &root, "u-1");

    let first = run(&[
        "events",
        &root.to_string_lossy(),
        "set-a",
        "--format",
        "jsonl",
    ]);
    let second = run(&[
        "events",
        &root.to_string_lossy(),
        "set-a",
        "--format",
        "jsonl",
    ]);
    assert!(first.status.success());
    assert_eq!(first.stdout, second.stdout);
    let lines = stdout_text(&first);
    assert_eq!(lines.lines().count(), 3);
    for line in lines.lines() {
        let value: Value = serde_json::from_str(line).expect("event");
        assert!(value["scope_refs"]
            .as_array()
            .is_some_and(|ids| ids.iter().any(|item| item == "work-set:set-a")));
    }
    let page = run(&[
        "events",
        &root.to_string_lossy(),
        "set-a",
        "--format",
        "jsonl",
        "--after-sequence",
        "3",
        "--max-items",
        "1",
    ]);
    assert!(page.status.success(), "{}", stderr_text(&page));
    let page_lines = stdout_text(&page);
    assert_eq!(page_lines.lines().count(), 1);
    let page_event: Value = serde_json::from_str(page_lines.trim()).expect("paged event");
    assert_eq!(page_event["sequence"], 4);
    let receipt = success(&["receipt", &root.to_string_lossy(), "set-a"]);
    assert_eq!(receipt["scoped_event_count"], 3);

    let invalid_format = run(&["events", &root.to_string_lossy(), "--format", "json"]);
    assert!(!invalid_format.status.success());
    assert!(stderr_text(&invalid_format).contains("supports only jsonl"));
    let invalid_limit = run(&["events", &root.to_string_lossy(), "--max-items", "0"]);
    assert!(!invalid_limit.status.success());
    assert!(stderr_text(&invalid_limit).contains("--max-items must be greater than zero"));

    let deleted_root = temp.path().join("deleted");
    fs::create_dir(&deleted_root).expect("deleted root");
    success(&["init", &deleted_root.to_string_lossy()]);
    add_commitment(&temp, &deleted_root);
    add_work_set(&temp, &deleted_root);
    let deleted_workspace = prepare(&temp, &deleted_root, "u-1");
    fs::write(deleted_workspace.join("result.txt"), b"deleted\n").expect("deleted result");
    seal(&temp, &deleted_root, "u-1");
    fs::remove_file(deleted_root.join(".split-testing/events/00000000000000000002.json"))
        .expect("remove event");
    let deleted = run(&["status", &deleted_root.to_string_lossy()]);
    assert!(!deleted.status.success());
    assert!(stderr_text(&deleted).contains("event filename"));

    let reordered_root = temp.path().join("reordered");
    fs::create_dir(&reordered_root).expect("reordered root");
    success(&["init", &reordered_root.to_string_lossy()]);
    add_commitment(&temp, &reordered_root);
    add_work_set(&temp, &reordered_root);
    let reordered_workspace = prepare(&temp, &reordered_root, "u-1");
    fs::write(reordered_workspace.join("result.txt"), b"reordered\n").expect("reordered result");
    seal(&temp, &reordered_root, "u-1");
    fs::rename(
        reordered_root.join(".split-testing/events/00000000000000000002.json"),
        reordered_root.join(".split-testing/events/00000000000000000009.json"),
    )
    .expect("rename event");
    let reordered = run(&["status", &reordered_root.to_string_lossy()]);
    assert!(!reordered.status.success());
    assert!(stderr_text(&reordered).contains("event filename"));

    let mutated_root = temp.path().join("mutated");
    fs::create_dir(&mutated_root).expect("mutated root");
    success(&["init", &mutated_root.to_string_lossy()]);
    add_commitment(&temp, &mutated_root);
    add_work_set(&temp, &mutated_root);
    let mutated_workspace = prepare(&temp, &mutated_root, "u-1");
    fs::write(mutated_workspace.join("result.txt"), b"mutated\n").expect("mutated result");
    seal(&temp, &mutated_root, "u-1");
    fs::write(
        mutated_root.join(".split-testing/records/commitments/frozen-policy/spec.json"),
        b"{\"schema\":\"split-testing-commitment.v2\",\"commitment_id\":\"frozen-policy\",\"changed\":true}\n",
    )
    .expect("mutate record");
    let mutated = run(&["status", &mutated_root.to_string_lossy()]);
    assert!(!mutated.status.success());
    assert!(stderr_text(&mutated).contains("different content"));

    let tail_root = temp.path().join("tail-deleted");
    fs::create_dir(&tail_root).expect("tail root");
    success(&["init", &tail_root.to_string_lossy()]);
    add_commitment(&temp, &tail_root);
    fs::remove_file(tail_root.join(".split-testing/events/00000000000000000002.json"))
        .expect("remove tail event");
    let tail_deleted = run(&["status", &tail_root.to_string_lossy()]);
    assert!(!tail_deleted.status.success());
    assert!(stderr_text(&tail_deleted).contains("unreferenced custody record"));

    let record_root = temp.path().join("record-deleted");
    fs::create_dir(&record_root).expect("record root");
    success(&["init", &record_root.to_string_lossy()]);
    add_commitment(&temp, &record_root);
    fs::remove_dir_all(record_root.join(".split-testing/records/commitments/frozen-policy"))
        .expect("remove referenced record");
    let record_deleted = run(&["status", &record_root.to_string_lossy()]);
    assert!(!record_deleted.status.success());
    assert!(stderr_text(&record_deleted).contains("event record is missing"));

    let schema_root = temp.path().join("schema-drift");
    fs::create_dir(&schema_root).expect("schema root");
    success(&["init", &schema_root.to_string_lossy()]);
    add_commitment(&temp, &schema_root);
    let commitment_record =
        schema_root.join(".split-testing/records/commitments/frozen-policy/record.json");
    let mut drifted = read_json(&commitment_record);
    drifted["schema"] = Value::String("split-testing-commitment.v1".to_owned());
    write_json(&commitment_record, &drifted);
    let schema_drift = run(&["status", &schema_root.to_string_lossy()]);
    assert!(!schema_drift.status.success());
    assert!(stderr_text(&schema_drift).contains("record digest mismatch"));
}

#[test]
fn events_refuses_unverified_records_and_retained_payloads() {
    let temp = tempfile::tempdir().expect("tempdir");

    let deleted_root = temp.path().join("events-deleted-record");
    fs::create_dir(&deleted_root).expect("deleted root");
    success(&["init", &deleted_root.to_string_lossy()]);
    add_commitment(&temp, &deleted_root);
    fs::remove_file(
        deleted_root.join(".split-testing/records/commitments/frozen-policy/record.json"),
    )
    .expect("delete event-bound record");
    let deleted = run(&[
        "events",
        &deleted_root.to_string_lossy(),
        "--format",
        "jsonl",
    ]);
    assert!(!deleted.status.success());
    assert!(stderr_text(&deleted).contains("event record is missing"));

    let rewritten_root = temp.path().join("events-rewritten-record");
    fs::create_dir(&rewritten_root).expect("rewritten root");
    success(&["init", &rewritten_root.to_string_lossy()]);
    add_commitment(&temp, &rewritten_root);
    let record =
        rewritten_root.join(".split-testing/records/commitments/frozen-policy/record.json");
    let value = read_json(&record);
    fs::write(
        &record,
        format!(
            "{}\n",
            serde_json::to_string_pretty(&value).expect("pretty record")
        ),
    )
    .expect("rewrite exact record bytes");
    let rewritten = run(&[
        "events",
        &rewritten_root.to_string_lossy(),
        "--format",
        "jsonl",
    ]);
    assert!(!rewritten.status.success());
    assert!(stderr_text(&rewritten).contains("event record digest mismatch"));

    let payload_root = temp.path().join("events-retained-payload");
    fs::create_dir(&payload_root).expect("payload root");
    success(&["init", &payload_root.to_string_lossy()]);
    add_commitment(&temp, &payload_root);
    add_work_set_with_units(&temp, &payload_root, &["u-1"]);
    let workspace = prepare(&temp, &payload_root, "u-1");
    fs::write(workspace.join("answer.txt"), b"answer\n").expect("answer");
    seal(&temp, &payload_root, "u-1");
    let seal_record =
        read_json(&payload_root.join(".split-testing/records/work/set-a/u-1/seal/record.json"));
    let retained = payload_root.join(
        seal_record["payload_root"]
            .as_str()
            .expect("retained payload root"),
    );
    fs::write(retained.join("answer.txt"), b"corrupt\n").expect("corrupt retained payload");
    let corrupted = run(&[
        "events",
        &payload_root.to_string_lossy(),
        "--format",
        "jsonl",
    ]);
    assert!(!corrupted.status.success());
    assert!(stderr_text(&corrupted).contains("mutation"));
}

#[test]
fn a_prospective_pending_marker_recovers_only_the_crash_tail_it_committed() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);

    let event_path = root.join(".split-testing/events/00000000000000000002.json");
    let event = read_json(&event_path);
    fs::remove_file(&event_path).expect("remove simulated crash-tail event");
    let record_ref = event["record_ref"].as_str().expect("record ref");
    let marker_name = format!("{:x}.json", Sha256::digest(record_ref.as_bytes()));
    let marker = root.join(".split-testing/pending").join(marker_name);
    write_json(
        &marker,
        &json!({
            "schema": "split-testing-pending-event.v2",
            "kind": event["kind"],
            "scope_refs": event["scope_refs"],
            "record_ref": record_ref,
            "record_digest": event["record_digest"],
            "content_digest": event["content_digest"]
        }),
    );

    let recovered = run(&["status", &root.to_string_lossy()]);
    assert!(recovered.status.success(), "{}", stderr_text(&recovered));
    assert!(event_path.is_file());
    assert_eq!(
        fs::read_dir(root.join(".split-testing/pending"))
            .expect("pending directory")
            .count(),
        0
    );

    fs::remove_file(&event_path).expect("remove unmarked event");
    let unmarked = run(&["status", &root.to_string_lossy()]);
    assert!(!unmarked.status.success());
    assert!(stderr_text(&unmarked).contains("unreferenced custody record"));
}

#[test]
fn pending_recovery_rejects_semantically_equivalent_record_byte_rewrites() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);

    let event_path = root.join(".split-testing/events/00000000000000000002.json");
    let event = read_json(&event_path);
    fs::remove_file(&event_path).expect("remove simulated crash-tail event");
    let record_ref = event["record_ref"].as_str().expect("record ref");
    let marker_name = format!("{:x}.json", Sha256::digest(record_ref.as_bytes()));
    write_json(
        &root.join(".split-testing/pending").join(marker_name),
        &json!({
            "schema": "split-testing-pending-event.v2",
            "kind": event["kind"],
            "scope_refs": event["scope_refs"],
            "record_ref": record_ref,
            "record_digest": event["record_digest"],
            "content_digest": event["content_digest"]
        }),
    );

    let record_path = root.join(record_ref);
    let value = read_json(&record_path);
    let rewritten = serde_json::to_string_pretty(&value).expect("pretty record");
    fs::write(&record_path, format!("{rewritten}\n")).expect("rewrite exact record bytes");

    let rejected = run(&["status", &root.to_string_lossy()]);
    assert!(!rejected.status.success());
    assert!(stderr_text(&rejected).contains("pending event record digest mismatch"));
    assert!(
        !event_path.exists(),
        "recovery must not append a forged tail"
    );
}

#[test]
fn typed_compound_scopes_isolate_duplicate_units_and_namespace_collisions() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);

    for set_id in ["frozen-policy", "set-b"] {
        let set_spec = temp.path().join(format!("scope-set-{set_id}.json"));
        write_json(
            &set_spec,
            &json!({
                "schema": "split-testing-work-set.v2",
                "set_id": set_id,
                "commitment_refs": ["frozen-policy"],
                "units": [{"unit_id": "shared"}]
            }),
        );
        success(&[
            "add-work-set",
            &root.to_string_lossy(),
            &set_spec.to_string_lossy(),
        ]);

        let work_spec = temp.path().join(format!("scope-work-{set_id}.json"));
        write_json(
            &work_spec,
            &json!({
                "schema": "split-testing-work.v2",
                "set_id": set_id,
                "unit_id": "shared",
                "commitment_refs": ["frozen-policy"]
            }),
        );
        success(&[
            "prepare-work",
            &root.to_string_lossy(),
            set_id,
            "shared",
            &work_spec.to_string_lossy(),
        ]);
    }

    let bare_set = run(&[
        "events",
        &root.to_string_lossy(),
        "frozen-policy",
        "--format",
        "jsonl",
    ]);
    assert!(bare_set.status.success(), "{}", stderr_text(&bare_set));
    let bare_events = stdout_text(&bare_set)
        .lines()
        .map(|line| serde_json::from_str::<Value>(line).expect("event"))
        .collect::<Vec<_>>();
    assert_eq!(bare_events.len(), 2, "bare scope defaults to a work set");
    assert!(bare_events.iter().all(|event| event["scope_refs"]
        .as_array()
        .is_some_and(|refs| refs.iter().any(|value| value == "work-set:frozen-policy"))));

    let commitment = success(&[
        "receipt",
        &root.to_string_lossy(),
        "commitment:frozen-policy",
    ]);
    assert_eq!(commitment["scope_ref"], "commitment:frozen-policy");
    assert_eq!(commitment["scoped_event_count"], 1);

    for set_id in ["frozen-policy", "set-b"] {
        let selector = format!("work:{set_id}/shared");
        let receipt = success(&["receipt", &root.to_string_lossy(), &selector]);
        assert_eq!(receipt["scope_ref"], selector);
        assert_eq!(receipt["scoped_event_count"], 1);
    }
}

#[test]
fn retained_sealed_payload_is_authoritative_and_missing_unsealed_work_can_close_lost() {
    let (temp, root) = setup();
    add_commitment(&temp, &root);
    add_work_set_with_units(&temp, &root, &["u-1"]);
    let workspace = prepare(&temp, &root, "u-1");
    fs::remove_dir_all(&workspace).expect("simulate lost unsealed workspace");

    let lost_closure = temp.path().join("lost-closure.json");
    write_json(
        &lost_closure,
        &json!({
            "schema": "split-testing-work-closure.v2",
            "set_id": "set-a",
            "units": [{"unit_id": "u-1", "status": "lost"}]
        }),
    );
    success(&[
        "close-work-set",
        &root.to_string_lossy(),
        "set-a",
        &lost_closure.to_string_lossy(),
    ]);
    let lost_status = success(&["status", &root.to_string_lossy()]);
    assert!(lost_status["diagnostics"]
        .as_array()
        .is_some_and(|items| items
            .iter()
            .any(|item| item["kind"] == "unsealed-workspace-missing")));

    let retained_root = temp.path().join("retained-workspace");
    fs::create_dir(&retained_root).expect("retained root");
    success(&["init", &retained_root.to_string_lossy()]);
    add_commitment(&temp, &retained_root);
    add_work_set_with_units(&temp, &retained_root, &["u-1"]);
    let live = prepare(&temp, &retained_root, "u-1");
    fs::write(live.join("answer.txt"), b"sealed answer\n").expect("sealed answer");
    seal(&temp, &retained_root, "u-1");
    fs::write(live.join("answer.txt"), b"later drift\n").expect("drift live workspace");

    let status = success(&["status", &retained_root.to_string_lossy()]);
    assert!(status["diagnostics"].as_array().is_some_and(|items| items
        .iter()
        .any(|item| item["kind"] == "sealed-workspace-drift")));
    fs::remove_dir_all(&live).expect("remove live sealed workspace");
    let missing = success(&["status", &retained_root.to_string_lossy()]);
    assert!(missing["diagnostics"].as_array().is_some_and(|items| items
        .iter()
        .any(|item| item["kind"] == "sealed-workspace-missing")));
    seal(&temp, &retained_root, "u-1");

    let closure = temp.path().join("retained-closure.json");
    write_json(
        &closure,
        &json!({
            "schema": "split-testing-work-closure.v2",
            "set_id": "set-a",
            "units": [{"unit_id": "u-1", "status": "completed"}]
        }),
    );
    success(&[
        "close-work-set",
        &retained_root.to_string_lossy(),
        "set-a",
        &closure.to_string_lossy(),
    ]);
    let publication = temp.path().join("retained-publication.json");
    write_json(
        &publication,
        &json!({
            "schema": "split-testing-publication.v2",
            "publication_id": "retained",
            "set_id": "set-a",
            "commitment_refs": ["frozen-policy"],
            "units": [{"unit_id": "u-1", "admitted": true, "reason": "prospective"}]
        }),
    );
    let published = success(&[
        "publish",
        &retained_root.to_string_lossy(),
        &publication.to_string_lossy(),
    ]);
    let blind_root = PathBuf::from(published["blind_root"].as_str().expect("blind root"));
    let opaque = fs::read_dir(&blind_root)
        .expect("blind root")
        .next()
        .expect("blind item")
        .expect("blind entry")
        .path();
    assert_eq!(
        fs::read(opaque.join("answer.txt")).expect("published answer"),
        b"sealed answer\n"
    );
}

#[test]
fn view_supports_arbitrary_assets_reader_properties_and_loopback_only_serving() {
    let temp = tempfile::tempdir().expect("tempdir");
    let root = temp.path().join("view-serve");
    fs::create_dir(&root).expect("view root");
    fs::write(
        root.join("index.html"),
        b"<!doctype html><title>Evidence</title><p id=fetch-status>loading</p><script>fetch('source.jsonl').then(r=>r.text()).then(v=>document.querySelector('#fetch-status').textContent=v.trim()).catch(()=>document.querySelector('#fetch-status').textContent='fetch failed')</script>\n",
    )
    .expect("index");
    fs::write(root.join("source.jsonl"), b"{\"value\":1}\n").expect("jsonl");
    fs::write(root.join("derivation.md"), b"# derivation\n").expect("derivation");
    fs::write(root.join("runtime.log"), b"runtime ready\n").expect("runtime");
    fs::write(root.join("vendor.js"), b"globalThis.vendorReady = true;\n")
        .expect("local runtime dependency");
    fs::write(
        root.join("entry #2.html"),
        b"<!doctype html><title>Second view</title>\n",
    )
    .expect("encoded entrypoint");
    fs::write(root.join("clip.mp4"), [0, 0, 0, 24, b'f', b't', b'y', b'p']).expect("mp4");
    fs::write(root.join("sound.wav"), b"RIFF....WAVEfmt ").expect("wav");
    fs::write(root.join("asset.bin"), [9_u8, 8, 7, 6]).expect("bin");
    let separator_name = "line\u{2028}break.json";
    fs::write(root.join(separator_name), b"{}\n").expect("separator asset");
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(root.join("asset.bin"), fs::Permissions::from_mode(0o755))
            .expect("chmod asset");
    }
    let spec = temp.path().join("view-serve.json");
    write_json(
        &spec,
        &json!({
            "schema": "derived-evidence-view.v1",
            "source_refs": [
                {"path": "source.jsonl"},
                {"path": "clip.mp4"},
                {"path": "sound.wav"},
                {"path": "asset.bin"},
                {"path": separator_name}
            ],
            "derivation_refs": [{"path": "derivation.md"}],
            "runtime_refs": [{"path": "runtime.log"}],
            "external_dependencies": [
                {"name": "offline-browser", "required": true},
                {"path": "vendor.js", "required": true}
            ],
            "entrypoints": ["index.html", "entry #2.html"],
            "interpretive_disclosures": ["projection only"],
            "extensions": {
                "future": {
                    "retained": true,
                    "path": "https://example.invalid/not-a-local-reference"
                }
            }
        }),
    );
    success(&[
        "view",
        "seal",
        &root.to_string_lossy(),
        &spec.to_string_lossy(),
    ]);

    let manifest = read_json(&root.join(".derived-evidence-view/manifest.json"));
    let manifest_paths = manifest["entries"]
        .as_array()
        .expect("manifest entries")
        .iter()
        .filter_map(|entry| entry["path"].as_str())
        .collect::<Vec<_>>();
    assert!(!manifest_paths
        .iter()
        .any(|path| path.starts_with(".derived-evidence-view")));
    #[cfg(unix)]
    assert!(manifest["entries"]
        .as_array()
        .expect("manifest entries")
        .iter()
        .any(|entry| entry["path"] == "asset.bin" && entry["executable"] == true));

    let rejected_bind = run(&[
        "view",
        "serve",
        &root.to_string_lossy(),
        "--bind",
        "0.0.0.0",
        "--port",
        "0",
    ]);
    assert!(!rejected_bind.status.success());
    assert!(stderr_text(&rejected_bind).contains("loopback"));

    let (mut child, url) = spawn_view_server(&root);
    let address = url
        .strip_prefix("http://")
        .and_then(|value| value.split('/').next())
        .expect("serve address")
        .to_owned();
    let reader_path = url
        .strip_prefix(&format!("http://{address}"))
        .expect("reader route")
        .to_owned();
    let capability_root = reader_path
        .strip_suffix("/.derived-evidence-view/reader/index.html")
        .expect("capability-scoped reader route")
        .to_owned();
    assert_eq!(
        capability_root
            .strip_prefix('/')
            .expect("absolute capability route")
            .len(),
        64
    );

    let unscoped = String::from_utf8(http_request(
        &address,
        "GET /.derived-evidence-view/reader/index.html HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n",
    ))
    .expect("unscoped response");
    assert!(unscoped.starts_with("HTTP/1.1 404 Not Found"));

    let reader = String::from_utf8(http_request(
        &address,
        &format!("GET {reader_path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"),
    ))
    .expect("reader response");
    assert!(reader.starts_with("HTTP/1.1 200 OK"));
    assert!(reader.contains("Derived projection. Inspect sources and disclosures before acting."));
    assert!(reader.contains("sandbox=\"allow-scripts allow-forms allow-downloads\""));
    assert!(!reader.contains("allow-same-origin"));
    assert!(!reader.contains("object-src 'self'"));
    for forbidden in [
        "navigator.serviceWorker",
        "localStorage",
        "sessionStorage",
        "indexedDB",
        "sendBeacon",
    ] {
        assert!(!reader.contains(forbidden), "reader retained {forbidden}");
    }
    assert!(reader.contains("Inspect package and evidence"));
    assert!(reader.contains("Package identity"));
    assert!(reader.contains("Raw local evidence"));
    assert!(reader.contains("for=\"reader-theme\""));
    for theme in ["system", "light", "dark"] {
        assert!(reader.contains(&format!("value=\"{theme}\"")));
    }
    assert!(reader.contains("Derivation references"));
    assert!(reader.contains("Runtime references"));
    assert!(reader.contains("evidence-view-message.v1"));
    assert!(reader.contains("reference-index"));
    assert!(reader.contains("let authoredReady = false;"));
    assert!(reader.contains("if (!authoredReady) status.textContent"));
    assert!(reader.contains("data-src=\"../../index.html\""));
    let transport_listener = reader
        .find("window.addEventListener('message'")
        .expect("listener");
    let frame_navigation = reader
        .find("frame.src = frame.dataset.src;")
        .expect("deferred frame navigation");
    assert!(transport_listener < frame_navigation);
    assert!(reader.contains("\"ref-"));
    assert!(!reader.contains("[\"source.jsonl\",\"../../source.jsonl\"]"));
    assert!(reader.contains("line\\u2028break.json"));
    assert!(reader.contains("spec.json"));
    assert!(reader.contains("../../source.jsonl"));
    assert!(reader.contains("../../entry%20%232.html"));
    assert!(reader.contains("data-served-src=\"../../vendor.js\""));

    let root_get = String::from_utf8(http_request(
        &address,
        &format!("GET {capability_root}/ HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"),
    ))
    .expect("root response");
    assert!(root_get.starts_with("HTTP/1.1 200 OK"));
    assert!(root_get.contains("Content-Type: text/html; charset=utf-8"));

    let segmented_start = format!("GET {reader_path} HTTP/1.1\r\n");
    let segmented_reader = String::from_utf8(http_request_chunks(
        &address,
        &[
            segmented_start.as_bytes(),
            b"Host: localhost\r\nConnection: close\r\n\r\n",
        ],
    ))
    .expect("segmented reader response");
    assert!(segmented_reader.starts_with("HTTP/1.1 200 OK"));
    assert!(segmented_reader.contains("Evidence view"));

    let authored = String::from_utf8(http_request(
        &address,
        &format!(
            "GET {capability_root}/index.html HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        ),
    ))
    .expect("authored response");
    assert!(authored.starts_with("HTTP/1.1 200 OK"));
    assert!(authored.contains(&format!("connect-src http://{address}")));
    assert!(authored.contains("Access-Control-Allow-Origin: null"));

    let encoded_entrypoint = String::from_utf8(http_request(
        &address,
        &format!(
            "GET {capability_root}/entry%20%232.html HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        ),
    ))
    .expect("encoded entrypoint response");
    assert!(encoded_entrypoint.starts_with("HTTP/1.1 200 OK"));
    assert!(encoded_entrypoint.contains("Second view"));

    let jsonl_head = String::from_utf8(http_request(
        &address,
        &format!(
            "HEAD {capability_root}/source.jsonl HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        ),
    ))
    .expect("head response");
    assert!(jsonl_head.starts_with("HTTP/1.1 200 OK"));
    assert!(jsonl_head.contains("Content-Type: application/x-ndjson"));
    assert!(!jsonl_head.ends_with("{\"value\":1}\n"));

    let media = String::from_utf8_lossy(&http_request(
        &address,
        &format!(
            "GET {capability_root}/clip.mp4 HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        ),
    ))
    .into_owned();
    assert!(media.starts_with("HTTP/1.1 200 OK"));
    assert!(media.contains("Content-Type: video/mp4"));

    let reader_spec = String::from_utf8(http_request(
        &address,
        &format!(
            "GET {capability_root}/.derived-evidence-view/reader/spec.json HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        ),
    ))
    .expect("reader spec");
    assert!(reader_spec.starts_with("HTTP/1.1 200 OK"));
    assert!(reader_spec.contains("\"schema\":\"derived-evidence-view.v1\""));

    let missing = String::from_utf8(http_request(
        &address,
        &format!(
            "GET {capability_root}/missing.txt HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        ),
    ))
    .expect("missing response");
    assert!(missing.starts_with("HTTP/1.1 404 Not Found"));

    let traversal = String::from_utf8(http_request(
        &address,
        &format!(
            "GET {capability_root}/..%2Fsecret.txt HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        ),
    ))
    .expect("traversal response");
    assert!(traversal.starts_with("HTTP/1.1 400 Bad Request"));

    let mut race = TcpStream::connect(&address).expect("connect mutable-file probe");
    race.write_all(
        format!(
            "GET {capability_root}/source.jsonl HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n"
        )
        .as_bytes(),
    )
    .expect("write incomplete request");
    race.flush().expect("flush incomplete request");
    thread::sleep(Duration::from_millis(100));
    fs::write(root.join("source.jsonl"), b"{\"value\":999}\n").expect("mutate served payload");
    race.write_all(b"\r\n").expect("finish request");
    race.shutdown(Shutdown::Write).expect("finish request body");
    let mut raced_response = Vec::new();
    race.read_to_end(&mut raced_response)
        .expect("read guarded response");
    fs::write(root.join("source.jsonl"), b"{\"value\":1}\n").expect("restore served payload");
    assert!(String::from_utf8_lossy(&raced_response).starts_with("HTTP/1.1 400 Bad Request"));

    terminate(&mut child);
}

#[test]
fn view_seal_verify_receipt_and_mutation_detection_are_content_addressed() {
    let temp = tempfile::tempdir().expect("tempdir");
    let root = temp.path().join("view");
    fs::create_dir(&root).expect("view root");
    fs::write(
        root.join("index.html"),
        b"<!doctype html><title>Evidence</title>\n",
    )
    .expect("entrypoint");
    fs::write(root.join("source.jsonl"), b"{\"value\":1}\n").expect("source");
    let spec = temp.path().join("view.json");
    write_json(
        &spec,
        &json!({
            "schema": "derived-evidence-view.v1",
            "source_refs": [{"path": "source.jsonl"}],
            "entrypoints": ["index.html"],
            "interpretive_disclosures": ["projection only"],
            "unknown_future": {"preserved": true}
        }),
    );
    let sealed = success(&[
        "view",
        "seal",
        &root.to_string_lossy(),
        &spec.to_string_lossy(),
    ]);
    assert_eq!(sealed["schema"], "derived-evidence-view.v1");
    let first_receipt = success(&["view", "receipt", &root.to_string_lossy()]);
    success(&[
        "view",
        "seal",
        &root.to_string_lossy(),
        &spec.to_string_lossy(),
    ]);
    let second_receipt = success(&["view", "receipt", &root.to_string_lossy()]);
    assert_eq!(first_receipt, second_receipt);
    success(&["view", "verify", &root.to_string_lossy()]);

    let control = root.join(".derived-evidence-view");
    let reader_path = control.join("reader/index.html");
    let original_reader = fs::read(&reader_path).expect("retained reader");
    let original_record = fs::read(control.join("record.json")).expect("retained record");
    let mut forged_reader = original_reader.clone();
    forged_reader.extend_from_slice(b"<!-- controller mutation -->\n");
    fs::write(&reader_path, &forged_reader).expect("forge reader");
    let mut forged_record: Value =
        serde_json::from_slice(&original_record).expect("parse retained record");
    forged_record["reader_digest"] = Value::String(format!("{:x}", Sha256::digest(&forged_reader)));
    let forged_record_bytes = serde_json::to_vec(&forged_record).expect("serialize forged record");
    fs::write(control.join("record.json"), &forged_record_bytes).expect("forge record");
    fs::write(control.join("reader/record.json"), &forged_record_bytes)
        .expect("forge reader record copy");
    let forged = run(&["view", "verify", &root.to_string_lossy()]);
    assert!(!forged.status.success());
    assert!(stderr_text(&forged).contains("consistency"));

    fs::write(&reader_path, original_reader).expect("restore reader");
    fs::write(control.join("record.json"), &original_record).expect("restore record");
    fs::write(control.join("reader/record.json"), original_record)
        .expect("restore reader record copy");

    fs::write(root.join("source.jsonl"), b"{\"value\":2}\n").expect("mutate");
    let changed = run(&["view", "verify", &root.to_string_lossy()]);
    assert!(!changed.status.success());
    assert!(String::from_utf8_lossy(&changed.stderr).contains("mutation"));
}

#[test]
fn view_rejects_missing_or_escaping_entrypoints_without_executing_payload() {
    let temp = tempfile::tempdir().expect("tempdir");
    let root = temp.path().join("view");
    fs::create_dir(&root).expect("view root");
    fs::write(root.join("danger.sh"), b"#!/bin/sh\ntouch executed\n").expect("payload");
    let spec = temp.path().join("view.json");
    write_json(
        &spec,
        &json!({
            "schema": "derived-evidence-view.v1",
            "source_refs": ["opaque:evidence"],
            "entrypoints": ["../outside.html"]
        }),
    );
    let rejected = run(&[
        "view",
        "seal",
        &root.to_string_lossy(),
        &spec.to_string_lossy(),
    ]);
    assert!(!rejected.status.success());
    assert!(!root.join("executed").exists());

    let local_ref = temp.path().join("missing-local-ref.json");
    write_json(
        &local_ref,
        &json!({
            "schema": "derived-evidence-view.v1",
            "source_refs": [{"path": "missing.json"}],
            "entrypoints": ["danger.sh"]
        }),
    );
    let missing_ref = run(&[
        "view",
        "seal",
        &root.to_string_lossy(),
        &local_ref.to_string_lossy(),
    ]);
    assert!(!missing_ref.status.success());
    assert!(stderr_text(&missing_ref).contains("declared local asset is missing"));

    let digest = Sha256::digest(fs::read(root.join("danger.sh")).expect("read payload"));
    assert_ne!(format!("{digest:x}"), "");
}
