from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path
from unittest import mock


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "skills" / "rust-panic-audit" / "scripts" / "panic_audit.py"
ORIGINAL_DONT_WRITE_BYTECODE = sys.dont_write_bytecode
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("panic_audit", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
panic_audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = panic_audit
try:
    SPEC.loader.exec_module(panic_audit)
finally:
    sys.dont_write_bytecode = ORIGINAL_DONT_WRITE_BYTECODE
    shutil.rmtree(SCRIPT.parent / "__pycache__", ignore_errors=True)
    shutil.rmtree(Path(__file__).resolve().parent / "__pycache__", ignore_errors=True)


def cargo_clippy_available() -> bool:
    cargo = shutil.which("cargo")
    if cargo is None:
        return False
    try:
        result = subprocess.run(
            [cargo, "clippy", "--version"],
            cwd=PLUGIN_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


CARGO_CLIPPY_AVAILABLE = cargo_clippy_available()
INTEGRATION_AUDIT_TIMEOUT_SECONDS = 240

LEXICAL_TEST_EXCLUSION_RISK = (
    "conventional test-only paths and definitely test-only items remain outside "
    "lexical candidates even with --all-targets; these lexical exclusions are "
    "distinct from compiler target coverage"
)


class ScannerTests(unittest.TestCase):
    def scan(self, source: str, profile: str = "strict-boundary"):
        with tempfile.TemporaryDirectory(prefix="panic-audit-scan-") as temp:
            path = Path(temp) / "lib.rs"
            path.write_text(textwrap.dedent(source).lstrip(), encoding="utf-8")
            return panic_audit.scan_source(path, profile)

    def test_ignores_comments_strings_raw_strings_and_nested_comments(self) -> None:
        findings, _ = self.scan(
            r'''
            const A: &str = "panic!() .unwrap()";
            const B: &str = r###"expect(\"no\") and todo!()"###;
            const C: &[u8] = br#"unreachable!()"#;
            // panic!("line comment");
            /* outer .unwrap() /* nested panic!() */ expect("comment") */
            pub fn ok<'a>(value: &'a str) -> &'a str { value }
            '''
        )
        self.assertEqual([], findings)

    def test_finds_multiline_direct_constructs_and_strict_assertions(self) -> None:
        findings, _ = self.scan(
            """
            pub fn live(value: Option<u8>) -> u8 {
                value
                    .unwrap()
            }
            pub fn invariant() { assert_eq!(1, 1); debug_assert!(true); }
            """
        )
        messages = [item.message for item in findings]
        self.assertTrue(any("unwrap candidate" in item for item in messages))
        self.assertTrue(any("assert_eq candidate" in item for item in messages))
        self.assertTrue(any("debug_assert candidate" in item for item in messages))

    def test_finds_direct_panic_functions_but_not_unsafe_unwrap_unchecked(self) -> None:
        findings, _ = self.scan(
            """
            use std::panic::{panic_any, resume_unwind};

            pub fn payload() { panic_any(17_u8); }
            pub fn propagate(payload: Box<dyn std::any::Any + Send>) {
                resume_unwind(payload);
            }
            pub unsafe fn unchecked(value: Option<u8>) -> u8 {
                unsafe { value.unwrap_unchecked() }
            }
            """,
            profile="core",
        )

        messages = [item.message for item in findings]
        self.assertTrue(any("panic_any candidate" in item for item in messages))
        self.assertTrue(any("resume_unwind candidate" in item for item in messages))
        self.assertFalse(any("unwrap_unchecked" in item for item in messages))

    def test_masks_test_only_items_but_keeps_mixed_cfg_candidates(self) -> None:
        findings, _ = self.scan(
            """
            #[test]
            fn direct_test() { panic!("test"); }

            #[cfg(test)]
            mod tests { fn helper() { panic!("test module"); } }

            #[cfg(all(test, unix))]
            fn test_only() { unreachable!(); }

            #[cfg(any(test, feature = "audit-me"))]
            fn mixed_scope() { panic!("can be production"); }
            """,
            profile="core",
        )
        self.assertEqual(1, len(findings))
        self.assertIn("panic candidate", findings[0].message)

    def test_scans_unattributed_production_module_named_tests(self) -> None:
        findings, _ = self.scan(
            """
            mod tests {
                pub fn production_reachable() { panic!("audit me"); }
            }
            """,
            profile="core",
        )

        self.assertEqual(1, len(findings))
        self.assertIn("audit me", findings[0].message)

    def test_cfg_test_implication_handles_order_nesting_and_mixed_any(self) -> None:
        findings, _ = self.scan(
            """
            #[cfg(all(unix, test))]
            fn reordered_terms() { panic!("test only"); }

            #[cfg(all(unix, all(feature = "extra", test)))]
            fn nested_all() { unreachable!(); }

            #[cfg(any(all(unix, test), all(test, windows)))]
            fn nested_any_branches_are_test_only() { panic!("test only"); }

            #[cfg(any(test, feature = "audit-me"))]
            fn mixed_any_is_production_reachable() { panic!("audit me"); }
            """,
            profile="core",
        )
        self.assertEqual(1, len(findings))
        self.assertIn("audit me", findings[0].message)

    def test_cfg_test_implication_preserves_correlated_atoms(self) -> None:
        findings, _ = self.scan(
            """
            #[cfg(all(any(test, unix), not(unix)))]
            fn correlated_test_only() { panic!("test only"); }

            #[cfg(all(any(test, feature = "audit-me"), not(feature="audit-me")))]
            fn correlated_feature_test_only() { panic!("test only"); }

            #[cfg(any(test, unix))]
            fn production_reachable() { panic!("audit me"); }
            """,
            profile="core",
        )
        self.assertEqual(1, len(findings))
        self.assertIn("audit me", findings[0].message)

    def test_adjacent_cfg_attributes_are_parsed_independently(self) -> None:
        findings, _ = self.scan(
            """
            #[cfg(test)] #[cfg(unix)] fn test_only_on_unix() { panic!("test only"); }

            #[cfg(unix)] #[cfg(feature = "audit-me")] fn production_reachable() {
                panic!("audit me");
            }
            """,
            profile="core",
        )
        self.assertEqual(1, len(findings))
        self.assertIn("audit me", findings[0].message)

    def test_reports_expected_lints_and_reasons(self) -> None:
        findings, expectations = self.scan(
            """
            #[expect(clippy::unwrap_used, reason = "validated non-empty invariant")]
            pub fn first(value: Option<u8>) -> u8 { value.unwrap() }
            """,
            profile="core",
        )
        self.assertEqual(1, len(findings))
        self.assertEqual(1, len(expectations))
        self.assertIn("clippy::unwrap_used", expectations[0].lints)
        self.assertEqual("validated non-empty invariant", expectations[0].reason)

    def test_target_mode_controls_example_and_bench_lexical_scope(self) -> None:
        with tempfile.TemporaryDirectory(prefix="panic-audit-files-") as temp:
            root = Path(temp) / "crate"
            manifest = root / "Cargo.toml"
            generated = root / "src" / "generated" / "bindings.rs"
            production_tests_file = root / "src" / "tests.rs"
            production_tests_module = root / "src" / "tests" / "mod.rs"
            production_test_suffix_file = root / "src" / "worker_test.rs"
            test_file = root / "tests" / "integration.rs"
            example_file = root / "examples" / "demo.rs"
            bench_file = root / "benches" / "throughput.rs"
            fixture_file = root / "fixtures" / "sample.rs"
            vcs_file = root / ".git" / "objects" / "generated.rs"
            target_file = root / "target" / "debug" / "build" / "out.rs"
            for path in (
                manifest,
                generated,
                production_tests_file,
                production_tests_module,
                production_test_suffix_file,
                test_file,
                example_file,
                bench_file,
                fixture_file,
                vcs_file,
                target_file,
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "panic!();\n" if path.suffix == ".rs" else "", encoding="utf-8"
                )
            packages = [{"manifest_path": str(manifest)}]
            default_files = panic_audit.rust_files(packages, root / "target")
            all_target_files = panic_audit.rust_files(
                packages, root / "target", all_targets=True
            )

            self.assertEqual(
                sorted(
                    [
                        generated.resolve(),
                        production_tests_file.resolve(),
                        production_tests_module.resolve(),
                        production_test_suffix_file.resolve(),
                    ]
                ),
                default_files,
            )
            self.assertEqual(
                sorted(
                    [
                        bench_file.resolve(),
                        example_file.resolve(),
                        generated.resolve(),
                        production_tests_file.resolve(),
                        production_tests_module.resolve(),
                        production_test_suffix_file.resolve(),
                    ]
                ),
                all_target_files,
            )

    def test_compiler_json_keeps_policy_findings_separate_from_build_errors(self) -> None:
        output = "\n".join(
            [
                json.dumps(
                    {
                        "reason": "compiler-message",
                        "message": {
                            "level": "warning",
                            "message": "used unwrap",
                            "code": {"code": "clippy::unwrap_used"},
                            "spans": [
                                {
                                    "is_primary": True,
                                    "file_name": "src/lib.rs",
                                    "line_start": 4,
                                    "column_start": 8,
                                }
                            ],
                        },
                    }
                ),
                json.dumps(
                    {
                        "reason": "compiler-message",
                        "message": {
                            "level": "error",
                            "message": "cannot find type Missing",
                            "code": {"code": "E0412"},
                            "spans": [],
                        },
                    }
                ),
            ]
        )
        findings, errors = panic_audit.parse_compiler_messages(
            output, {"clippy::unwrap_used"}
        )
        self.assertEqual("clippy::unwrap_used", findings[0].kind)
        self.assertEqual(["cannot find type Missing"], errors)


class AuditStateTests(unittest.TestCase):
    def test_member_manifest_selects_its_package_not_workspace_defaults(self) -> None:
        workspace = Path("/repo")
        root_manifest = workspace / "Cargo.toml"
        service_manifest = workspace / "crates" / "service" / "Cargo.toml"
        default_package = {
            "id": "default 0.1.0",
            "name": "default",
            "manifest_path": str(workspace / "crates" / "default" / "Cargo.toml"),
            "targets": [],
        }
        service_package = {
            "id": "service 0.1.0",
            "name": "service",
            "manifest_path": str(service_manifest),
            "targets": [],
        }
        metadata = {
            "packages": [default_package, service_package],
            "workspace_members": ["default 0.1.0", "service 0.1.0"],
            "workspace_default_members": ["default 0.1.0"],
            "workspace_root": str(workspace),
        }
        args = panic_audit.parse_args(
            ["--manifest-path", str(service_manifest), "--profile", "core"]
        )

        selected = panic_audit.select_packages(metadata, args, service_manifest)

        self.assertEqual([service_package], selected)
        self.assertNotEqual(root_manifest, service_manifest)

    def test_unreadable_selected_source_makes_lexical_scope_incomplete(self) -> None:
        with tempfile.TemporaryDirectory(prefix="panic-audit-unreadable-") as temp:
            root = Path(temp)
            manifest = root / "Cargo.toml"
            missing = root / "src" / "missing.rs"
            manifest.write_text(
                "[package]\nname='demo'\nversion='0.1.0'\n", encoding="utf-8"
            )
            package = {
                "id": "demo 0.1.0",
                "name": "demo",
                "manifest_path": str(manifest),
                "targets": [],
            }
            metadata = {
                "packages": [package],
                "workspace_members": ["demo 0.1.0"],
                "workspace_default_members": ["demo 0.1.0"],
                "target_directory": str(root / "target"),
            }
            args = panic_audit.parse_args(
                ["--manifest-path", str(manifest), "--profile", "core"]
            )
            with (
                mock.patch.object(panic_audit, "locate_workspace", return_value=root),
                mock.patch.object(panic_audit, "load_metadata", return_value=metadata),
                mock.patch.object(panic_audit, "tracked_status", return_value="stable"),
                mock.patch.object(panic_audit, "rust_files", return_value=[missing]),
            ):
                report, code = panic_audit.audit(args)

            self.assertEqual(panic_audit.EXIT_INCOMPLETE, code)
            self.assertEqual("incomplete", report["status"])
            self.assertIn(
                f"cannot read Rust source {missing}", report["tooling_errors"][0]
            )

    def test_unavailable_requested_lint_makes_audit_incomplete(self) -> None:
        with tempfile.TemporaryDirectory(prefix="panic-audit-state-") as temp:
            root = Path(temp)
            manifest = root / "Cargo.toml"
            source = root / "src" / "lib.rs"
            source.parent.mkdir()
            manifest.write_text(
                "[package]\nname='demo'\nversion='0.1.0'\n", encoding="utf-8"
            )
            source.write_text("pub fn ok() {}\n", encoding="utf-8")
            metadata = {
                "packages": [
                    {
                        "id": "demo 0.1.0",
                        "name": "demo",
                        "manifest_path": str(manifest),
                        "targets": [],
                    }
                ],
                "workspace_members": ["demo 0.1.0"],
                "workspace_default_members": ["demo 0.1.0"],
                "target_directory": str(root / "target"),
            }
            args = panic_audit.parse_args(
                ["--manifest-path", str(manifest), "--profile", "core"]
            )
            available = {
                panic_audit.normalize_lint(item)
                for item in panic_audit.CORE_LINTS[:-1]
            }
            command = panic_audit.CommandResult(["cargo", "clippy"], 0, "", "")
            with (
                mock.patch.object(panic_audit, "locate_workspace", return_value=root),
                mock.patch.object(panic_audit, "load_metadata", return_value=metadata),
                mock.patch.object(panic_audit, "tracked_status", return_value=""),
                mock.patch.object(panic_audit, "discover_lints", return_value=(available, None)),
                mock.patch.object(panic_audit, "run_clippy", return_value=(command, [], [])),
            ):
                report, code = panic_audit.audit(args)
            self.assertEqual(panic_audit.EXIT_INCOMPLETE, code)
            self.assertEqual("incomplete", report["status"])
            self.assertEqual([panic_audit.CORE_LINTS[-1]], report["unavailable_lints"])

    def test_policy_finding_plus_unrelated_clippy_failure_is_incomplete(self) -> None:
        with tempfile.TemporaryDirectory(prefix="panic-audit-state-") as temp:
            root = Path(temp)
            manifest = root / "Cargo.toml"
            source = root / "src" / "lib.rs"
            source.parent.mkdir()
            manifest.write_text("[package]\nname='demo'\nversion='0.1.0'\n", encoding="utf-8")
            source.write_text("pub fn ok() {}\n", encoding="utf-8")
            package = {
                "id": "demo 0.1.0",
                "name": "demo",
                "manifest_path": str(manifest),
                "targets": [],
            }
            metadata = {
                "packages": [package],
                "workspace_members": ["demo 0.1.0"],
                "workspace_default_members": ["demo 0.1.0"],
                "target_directory": str(root / "target"),
            }
            args = panic_audit.parse_args(
                ["--manifest-path", str(manifest), "--profile", "core"]
            )
            finding = panic_audit.Finding(
                source="compiler",
                kind="clippy::unwrap_used",
                path="src/lib.rs",
                line=1,
                column=1,
                message="used unwrap",
                level="error",
            )
            stdout = json.dumps({"reason": "build-finished", "success": False})
            command = panic_audit.CommandResult(["cargo", "clippy"], 101, stdout, "")
            available = {panic_audit.normalize_lint(item) for item in panic_audit.CORE_LINTS}
            with (
                mock.patch.object(panic_audit, "locate_workspace", return_value=root),
                mock.patch.object(panic_audit, "load_metadata", return_value=metadata),
                mock.patch.object(panic_audit, "tracked_status", return_value="stable"),
                mock.patch.object(panic_audit, "discover_lints", return_value=(available, None)),
                mock.patch.object(
                    panic_audit,
                    "run_clippy",
                    return_value=(command, [finding], ["cannot find type Missing"]),
                ),
            ):
                report, code = panic_audit.audit(args)

            self.assertEqual(panic_audit.EXIT_INCOMPLETE, code)
            self.assertEqual("incomplete", report["status"])
            self.assertEqual("clippy::unwrap_used", report["compiler_findings"][0]["kind"])
            self.assertIn("cannot find type Missing", report["tooling_errors"])
            self.assertIn(
                "Cargo Clippy did not complete the requested audit scope",
                report["tooling_errors"],
            )

    def test_successful_clippy_without_requested_target_is_incomplete(self) -> None:
        with tempfile.TemporaryDirectory(prefix="panic-audit-state-") as temp:
            root = Path(temp)
            manifest = root / "Cargo.toml"
            source = root / "src" / "lib.rs"
            source.parent.mkdir()
            manifest.write_text("[package]\nname='demo'\nversion='0.1.0'\n", encoding="utf-8")
            source.write_text("pub fn ok() {}\n", encoding="utf-8")
            target = {
                "name": "demo",
                "kind": ["lib"],
                "src_path": str(source),
            }
            package = {
                "id": "demo 0.1.0",
                "name": "demo",
                "manifest_path": str(manifest),
                "targets": [target],
            }
            metadata = {
                "packages": [package],
                "workspace_members": ["demo 0.1.0"],
                "workspace_default_members": ["demo 0.1.0"],
                "target_directory": str(root / "target"),
            }
            args = panic_audit.parse_args(
                ["--manifest-path", str(manifest), "--profile", "core"]
            )
            available = {
                panic_audit.normalize_lint(item) for item in panic_audit.CORE_LINTS
            }
            command = panic_audit.CommandResult(
                ["cargo", "clippy"],
                0,
                json.dumps({"reason": "build-finished", "success": True}),
                "",
            )
            with (
                mock.patch.object(panic_audit, "locate_workspace", return_value=root),
                mock.patch.object(panic_audit, "load_metadata", return_value=metadata),
                mock.patch.object(panic_audit, "tracked_status", return_value="stable"),
                mock.patch.object(
                    panic_audit, "discover_lints", return_value=(available, None)
                ),
                mock.patch.object(
                    panic_audit, "run_clippy", return_value=(command, [], [])
                ),
            ):
                report, code = panic_audit.audit(args)

            self.assertEqual(panic_audit.EXIT_INCOMPLETE, code)
            self.assertEqual("incomplete", report["status"])
            self.assertTrue(
                any(
                    "full requested target scope: demo::demo [lib]" in item
                    for item in report["tooling_errors"]
                ),
                report["tooling_errors"],
            )

    def test_scope_flags_are_forwarded_without_inventing_features(self) -> None:
        manifest = Path("/repo/Cargo.toml")
        args = panic_audit.parse_args(
            [
                "--manifest-path",
                str(manifest),
                "--profile",
                "strict-boundary",
                "--workspace",
                "--package",
                "one",
                "--package",
                "two",
                "--all-targets",
                "--no-default-features",
                "--target",
                "wasm32-unknown-unknown",
                "--features",
                "alpha,beta",
            ]
        )
        scope = panic_audit.cargo_scope_args(args, manifest)
        self.assertNotIn("--workspace", scope)
        self.assertEqual(2, scope.count("--package"))
        self.assertIn("--all-targets", scope)
        self.assertIn("--no-default-features", scope)
        self.assertEqual("wasm32-unknown-unknown", scope[scope.index("--target") + 1])
        self.assertEqual("alpha,beta", scope[-1])
        self.assertNotIn("--all-features", scope)

    def test_nonzero_clippy_requires_policy_only_diagnostics_and_failed_build_marker(self) -> None:
        policy_finding = panic_audit.Finding(
            source="compiler",
            kind="clippy::unwrap_used",
            path="src/lib.rs",
            line=1,
            column=1,
            message="used unwrap",
            level="error",
        )
        failed_build = json.dumps({"reason": "build-finished", "success": False})
        result = panic_audit.CommandResult(
            ["cargo", "clippy"],
            101,
            failed_build,
            "\x1b[1m\x1b[32m    Checking\x1b[0m demo v0.1.0\n"
            "\x1b[1m\x1b[31merror\x1b[0m: could not compile `demo` (lib) "
            "due to 1 previous error\n",
        )

        self.assertTrue(
            panic_audit.nonzero_clippy_is_policy_only(result, [policy_finding], [])
        )
        self.assertFalse(
            panic_audit.nonzero_clippy_is_policy_only(
                result, [policy_finding], ["cannot find type Missing"]
            )
        )
        warning_only = panic_audit.Finding(
            source="compiler",
            kind="clippy::unwrap_used",
            path="src/lib.rs",
            line=1,
            column=1,
            message="used unwrap",
            level="warning",
        )
        self.assertFalse(
            panic_audit.nonzero_clippy_is_policy_only(result, [warning_only], [])
        )

        no_build_marker = panic_audit.CommandResult(
            ["cargo", "clippy"], 101, "", "error: could not compile `demo`"
        )
        self.assertFalse(
            panic_audit.nonzero_clippy_is_policy_only(
                no_build_marker, [policy_finding], []
            )
        )

        unparsed_stdout = panic_audit.CommandResult(
            ["cargo", "clippy"],
            101,
            failed_build + "\nunrelated output\n",
            "",
        )
        self.assertFalse(
            panic_audit.nonzero_clippy_is_policy_only(
                unparsed_stdout, [policy_finding], []
            )
        )

        unrelated_stderr = panic_audit.CommandResult(
            ["cargo", "clippy"],
            101,
            failed_build,
            "rustc-LLVM ERROR: out of memory\n",
        )
        self.assertFalse(
            panic_audit.nonzero_clippy_is_policy_only(
                unrelated_stderr, [policy_finding], []
            )
        )

    def test_cargo_operations_share_manifest_directory_and_executable(self) -> None:
        manifest = Path("/repo/member/Cargo.toml")
        manifest_dir = manifest.parent
        cargo = "/toolchain/bin/cargo"
        args = panic_audit.parse_args(
            ["--manifest-path", str(manifest), "--profile", "core"]
        )
        metadata = {
            "packages": [],
            "workspace_members": [],
            "workspace_default_members": [],
        }
        calls: list[tuple[list[str], Path]] = []

        def fake_run(command, cwd, **kwargs):
            calls.append((list(command), cwd))
            if command[1] == "locate-project":
                return panic_audit.CommandResult(list(command), 0, "/repo/Cargo.toml\n", "")
            if command[1] == "metadata":
                return panic_audit.CommandResult(list(command), 0, json.dumps(metadata), "")
            if command[-2:] == ["-W", "help"]:
                return panic_audit.CommandResult(
                    list(command), 0, "clippy::unwrap-used allow fixture\n", ""
                )
            return panic_audit.CommandResult(
                list(command),
                0,
                json.dumps({"reason": "build-finished", "success": True}),
                "",
            )

        with mock.patch.object(panic_audit, "run_command", side_effect=fake_run):
            self.assertEqual(Path("/repo"), panic_audit.locate_workspace(manifest, cargo))
            self.assertEqual(
                metadata,
                panic_audit.load_metadata(args, manifest, manifest_dir, False, cargo),
            )
            available, error = panic_audit.discover_lints(
                args, manifest, manifest_dir, False, cargo
            )
            self.assertIsNone(error)
            self.assertIn("clippy::unwrap_used", available)
            panic_audit.run_clippy(
                args,
                manifest,
                manifest_dir,
                False,
                ["clippy::unwrap_used"],
                cargo,
            )

        self.assertTrue(calls)
        self.assertTrue(all(cwd == manifest_dir for _, cwd in calls))
        self.assertTrue(all(command[0] == cargo for command, _ in calls))
        self.assertFalse(any(command[0].endswith("rustup") for command, _ in calls))
        self.assertEqual(
            ["--message-format=json", "--", "-D", "clippy::unwrap_used"],
            calls[-1][0][-4:],
        )

    def test_tracked_snapshot_detects_changes_to_an_already_dirty_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="panic-audit-tracked-") as temp:
            root = Path(temp)
            tracked = root / "tracked.rs"
            tracked.write_text("pub fn original() {}\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "tests@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Tests"], cwd=root, check=True)
            subprocess.run(["git", "add", "tracked.rs"], cwd=root, check=True)
            subprocess.run(
                ["git", "commit", "--no-gpg-sign", "-qm", "fixture"],
                cwd=root,
                check=True,
            )

            tracked.write_text("pub fn dirty_before() {}\n", encoding="utf-8")
            before = panic_audit.tracked_status(root)
            tracked.write_text("pub fn dirty_after() {}\n", encoding="utf-8")
            after = panic_audit.tracked_status(root)

            self.assertIsNotNone(before)
            self.assertIsNotNone(after)
            self.assertNotEqual(before, after)

    def test_tracked_snapshot_from_nested_workspace_detects_dirty_sibling(self) -> None:
        with tempfile.TemporaryDirectory(prefix="panic-audit-tracked-") as temp:
            root = Path(temp)
            workspace = root / "nested" / "workspace"
            sibling = root / "sibling.rs"
            workspace.mkdir(parents=True)
            (workspace / "lib.rs").write_text("pub fn local() {}\n", encoding="utf-8")
            sibling.write_text("pub fn before() {}\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "tests@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Tests"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(
                ["git", "commit", "--no-gpg-sign", "-qm", "fixture"],
                cwd=root,
                check=True,
            )

            before = panic_audit.tracked_status(workspace)
            sibling.write_text("pub fn after() {}\n", encoding="utf-8")
            after = panic_audit.tracked_status(workspace)

            self.assertIsNotNone(before)
            self.assertIsNotNone(after)
            self.assertNotEqual(before, after)

    def test_untracked_snapshot_detects_new_paths_outside_cargo_target(self) -> None:
        with tempfile.TemporaryDirectory(prefix="panic-audit-untracked-") as temp:
            root = Path(temp)
            target = root / "target"
            target.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)

            before = panic_audit.unignored_untracked_paths(root, (target,))
            (root / "side-effect.txt").write_text("created\n", encoding="utf-8")
            (target / "cache.bin").write_bytes(b"generated")
            after = panic_audit.unignored_untracked_paths(root, (target,))

            self.assertEqual(set(), before)
            self.assertEqual({"side-effect.txt"}, after)

    def test_missing_requested_targets_respects_cargo_target_mode(self) -> None:
        declared = [
            {"package": "app", "name": "app", "kind": ["lib"], "src_path": "/src/lib.rs"},
            {"package": "app", "name": "smoke", "kind": ["test"], "src_path": "/tests/smoke.rs"},
            {
                "package": "app",
                "name": "demo",
                "kind": ["example"],
                "src_path": "/examples/demo.rs",
            },
            {
                "package": "app",
                "name": "speed",
                "kind": ["bench"],
                "src_path": "/benches/speed.rs",
            },
            {"package": "app", "name": "build-script-build", "kind": ["custom-build"], "src_path": "/build.rs"},
        ]
        analyzed = [declared[0]]

        self.assertEqual(
            [],
            panic_audit.missing_requested_targets(declared, analyzed, False),
        )
        self.assertEqual(
            declared[1:4],
            panic_audit.missing_requested_targets(declared, analyzed, True),
        )


class CommandExecutionTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "posix", "process-group assertion requires POSIX")
    def test_timeout_terminates_the_command_and_its_descendants(self) -> None:
        with tempfile.TemporaryDirectory(prefix="panic-audit-timeout-") as temp:
            root = Path(temp)
            marker = root / "descendant-survived"
            descendant = (
                "import time; from pathlib import Path; "
                f"time.sleep(0.8); Path({str(marker)!r}).write_text('survived')"
            )
            parent = (
                "import subprocess, sys, time; "
                f"subprocess.Popen([sys.executable, '-c', {descendant!r}]); "
                "time.sleep(10)"
            )

            with self.assertRaisesRegex(panic_audit.AuditError, "timed out"):
                panic_audit.run_command(
                    [sys.executable, "-c", parent],
                    root,
                    timeout_seconds=0.2,
                    max_output_bytes=1024 * 1024,
                )

            time.sleep(1.0)
            self.assertFalse(marker.exists())

    def test_output_limit_stops_unbounded_command_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="panic-audit-output-") as temp:
            with self.assertRaisesRegex(
                panic_audit.AuditError, "output exceeded"
            ):
                panic_audit.run_command(
                    [sys.executable, "-c", "print('x' * 65536)"],
                    Path(temp),
                    timeout_seconds=5,
                    max_output_bytes=1024,
                )


@unittest.skipUnless(
    CARGO_CLIPPY_AVAILABLE,
    "Cargo and Clippy are required for integration coverage",
)
class RunnerIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="panic-audit-integration-")
        self.root = Path(self.temp.name)
        self.manifest = self.root / "Cargo.toml"
        self.crate_manifest = self.root / "app" / "Cargo.toml"
        self.source = self.root / "app" / "src" / "lib.rs"
        self.source.parent.mkdir(parents=True)
        self.manifest.write_text(
            '[workspace]\nmembers = ["app"]\nresolver = "2"\n', encoding="utf-8"
        )
        self.crate_manifest.write_text(
            textwrap.dedent(
                """
                [package]
                name = "app"
                version = "0.1.0"
                edition = "2021"

                [features]
                risky = []
                """
            ).lstrip(),
            encoding="utf-8",
        )
        self.source.write_text(
            "pub fn checked(value: Option<u32>) -> Option<u32> { value }\n",
            encoding="utf-8",
        )
        integration_test = self.root / "app" / "tests" / "smoke.rs"
        integration_test.parent.mkdir()
        integration_test.write_text("#[test]\nfn smoke() {}\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "tests@example.invalid"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Tests"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "commit", "--no-gpg-sign", "-qm", "fixture"],
            cwd=self.root,
            check=True,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def tracked_status(self) -> str:
        return subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=no"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout

    def run_audit_for_manifest(
        self, manifest: Path, *extra: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--manifest-path",
                str(manifest),
                "--profile",
                "core",
                *extra,
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=INTEGRATION_AUDIT_TIMEOUT_SECONDS,
        )

    def run_audit(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return self.run_audit_for_manifest(self.manifest, *extra)

    def test_clean_text_exit_zero_and_no_tracked_write(self) -> None:
        before = self.tracked_status()
        proc = self.run_audit("--workspace")
        after = self.tracked_status()
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("status: clean", proc.stdout)
        self.assertIn("target mode: cargo-defaults", proc.stdout)
        self.assertIn("declared targets:", proc.stdout)
        self.assertIn("analyzed targets:", proc.stdout)
        self.assertIn("no forbidden direct constructs found in the audited scope", proc.stdout)
        self.assertNotIn("panic-free", proc.stdout.lower())
        self.assertIn(f"- {LEXICAL_TEST_EXCLUSION_RISK}", proc.stdout)
        self.assertEqual(before, after)
        self.assertFalse((self.root / "Cargo.lock").exists())

    def test_json_findings_exit_one_and_preserve_scope(self) -> None:
        self.source.write_text(
            "pub fn required(value: Option<u32>) -> u32 { value.unwrap() }\n",
            encoding="utf-8",
        )
        before = self.tracked_status()
        proc = self.run_audit("--package", "app", "--features", "risky", "--json")
        after = self.tracked_status()
        self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual("findings", payload["status"])
        self.assertEqual(["app"], payload["scope"]["packages"])
        self.assertEqual("risky", payload["scope"]["features"])
        self.assertTrue(payload["compiler_findings"])
        self.assertTrue(payload["lexical_candidates"])
        self.assertIn(LEXICAL_TEST_EXCLUSION_RISK, payload["residual_risk"])
        self.assertEqual(before, after)

    def test_scans_production_test_named_modules_and_source_files(self) -> None:
        tests_file = self.root / "app" / "src" / "tests" / "mod.rs"
        test_suffix_file = self.root / "app" / "src" / "worker_test.rs"
        self.source.write_text(
            '#[path = "tests/mod.rs"]\npub mod production_tests;\npub mod worker_test;\n',
            encoding="utf-8",
        )
        tests_file.parent.mkdir()
        tests_file.write_text(
            '#[allow(clippy::panic)]\npub fn production() { panic!("tests module"); }\n',
            encoding="utf-8",
        )
        test_suffix_file.write_text(
            '#[allow(clippy::panic)]\npub fn production() { panic!("test suffix"); }\n',
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "commit",
                "--no-gpg-sign",
                "-qm",
                "production modules",
            ],
            cwd=self.root,
            check=True,
        )

        before = self.tracked_status()
        proc = self.run_audit("--json")
        after = self.tracked_status()

        self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual("findings", payload["status"])
        self.assertEqual([], payload["compiler_findings"])
        lexical_paths = {item["path"] for item in payload["lexical_candidates"]}
        self.assertEqual(
            {str(tests_file.resolve()), str(test_suffix_file.resolve())},
            lexical_paths,
        )
        self.assertEqual(before, after)

    def test_build_script_worktree_side_effect_makes_audit_incomplete(self) -> None:
        build_script = self.root / "app" / "build.rs"
        build_script.write_text(
            textwrap.dedent(
                """
                fn main() -> Result<(), Box<dyn std::error::Error>> {
                    let root = std::env::var("CARGO_MANIFEST_DIR")?;
                    std::fs::write(
                        std::path::Path::new(&root).join("side-effect.txt"),
                        "created",
                    )?;
                    Ok(())
                }
                """
            ).lstrip(),
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "app/build.rs"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "commit", "--no-gpg-sign", "-qm", "build script"],
            cwd=self.root,
            check=True,
        )

        proc = self.run_audit("--json")

        self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual("incomplete", payload["status"])
        self.assertTrue(
            any("untracked paths changed" in item for item in payload["tooling_errors"]),
            payload["tooling_errors"],
        )

    def test_default_and_all_target_reports_distinguish_declared_and_analyzed(self) -> None:
        default_proc = self.run_audit("--json")
        self.assertEqual(0, default_proc.returncode, default_proc.stdout + default_proc.stderr)
        default_scope = json.loads(default_proc.stdout)["scope"]
        self.assertEqual("cargo-defaults", default_scope["target_mode"])
        self.assertIn(
            "test",
            {kind for target in default_scope["declared_targets"] for kind in target["kind"]},
        )
        self.assertNotIn(
            "test",
            {kind for target in default_scope["analyzed_targets"] for kind in target["kind"]},
        )

        all_proc = self.run_audit("--all-targets", "--json")
        self.assertEqual(0, all_proc.returncode, all_proc.stdout + all_proc.stderr)
        all_scope = json.loads(all_proc.stdout)["scope"]
        self.assertEqual("all-targets", all_scope["target_mode"])
        self.assertIn(
            "test",
            {kind for target in all_scope["analyzed_targets"] for kind in target["kind"]},
        )

    def test_all_targets_lexically_scans_examples_and_benches_but_not_tests(self) -> None:
        example = self.root / "app" / "examples" / "latent.rs"
        bench = self.root / "app" / "benches" / "latent.rs"
        test_only = self.root / "app" / "tests" / "lexical_only.rs"
        example.parent.mkdir()
        bench.parent.mkdir()
        example.write_text(
            '#[allow(clippy::panic)]\nfn latent() { panic!("example"); }\nfn main() {}\n',
            encoding="utf-8",
        )
        bench.write_text(
            '#[allow(clippy::panic)]\nfn latent() { panic!("bench"); }\n',
            encoding="utf-8",
        )
        test_only.write_text(
            '#[allow(clippy::panic)]\nfn latent() { panic!("test"); }\n',
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "commit", "--no-gpg-sign", "-qm", "target fixtures"],
            cwd=self.root,
            check=True,
        )

        before = self.tracked_status()
        default_proc = self.run_audit("--json")
        default_payload = json.loads(default_proc.stdout)
        self.assertEqual(
            0, default_proc.returncode, default_proc.stdout + default_proc.stderr
        )
        self.assertEqual([], default_payload["lexical_candidates"])

        all_proc = self.run_audit("--all-targets", "--json")
        after = self.tracked_status()
        self.assertEqual(1, all_proc.returncode, all_proc.stdout + all_proc.stderr)
        payload = json.loads(all_proc.stdout)
        self.assertEqual("1.0", payload["schema_version"])
        self.assertEqual(1, payload["exit_code"])
        self.assertEqual("findings", payload["status"])
        lexical_paths = {item["path"] for item in payload["lexical_candidates"]}
        self.assertEqual({str(example.resolve()), str(bench.resolve())}, lexical_paths)
        self.assertNotIn(str(test_only.resolve()), lexical_paths)
        analyzed_kinds = {
            kind
            for target in payload["scope"]["analyzed_targets"]
            for kind in target["kind"]
        }
        self.assertTrue({"example", "bench"}.issubset(analyzed_kinds))
        self.assertEqual(before, after)

    def test_member_manifest_uses_member_local_cargo_config_and_toolchain(self) -> None:
        member_config = self.root / "app" / ".cargo" / "config.toml"
        member_config.parent.mkdir()
        member_config.write_text(
            '[env]\nPANIC_AUDIT_MEMBER_CONFIG = "loaded"\n', encoding="utf-8"
        )
        self.source.write_text(
            'const _: &str = env!("PANIC_AUDIT_MEMBER_CONFIG");\n', encoding="utf-8"
        )
        if shutil.which("rustup"):
            active = subprocess.run(
                ["rustup", "show", "active-toolchain"],
                cwd=self.root,
                capture_output=True,
                text=True,
                check=False,
            )
            if active.returncode == 0 and active.stdout.split():
                (self.root / "app" / "rust-toolchain.toml").write_text(
                    f'[toolchain]\nchannel = "{active.stdout.split()[0]}"\n',
                    encoding="utf-8",
                )

        proc = self.run_audit_for_manifest(self.crate_manifest, "--json")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertEqual("clean", json.loads(proc.stdout)["status"])

    def test_expectation_is_reported_as_intentional_review_candidate(self) -> None:
        self.source.write_text(
            textwrap.dedent(
                """
                #[expect(clippy::unwrap_used, reason = "fixture invariant")]
                pub fn required(value: Option<u32>) -> u32 { value.unwrap() }
                """
            ).lstrip(),
            encoding="utf-8",
        )
        proc = self.run_audit("--json")
        self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual("fixture invariant", payload["intentional_expectations"][0]["reason"])
        self.assertEqual([], payload["compiler_findings"])
        self.assertTrue(payload["lexical_candidates"])

    def test_repo_denied_policy_lint_is_a_completed_finding(self) -> None:
        self.crate_manifest.write_text(
            self.crate_manifest.read_text(encoding="utf-8")
            + '\n[lints.clippy]\nunwrap_used = "deny"\n',
            encoding="utf-8",
        )
        self.source.write_text(
            "pub fn required(value: Option<u32>) -> u32 { value.unwrap() }\n",
            encoding="utf-8",
        )

        proc = self.run_audit("--json")
        self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual("findings", payload["status"])
        self.assertEqual("clippy::unwrap_used", payload["compiler_findings"][0]["kind"])
        self.assertEqual("error", payload["compiler_findings"][0]["level"])
        self.assertEqual([], payload["tooling_errors"])
        self.assertTrue(payload["scope"]["analyzed_targets"])

    def test_all_targets_policy_failure_is_incomplete_when_later_target_is_unanalyzed(self) -> None:
        self.crate_manifest.write_text(
            self.crate_manifest.read_text(encoding="utf-8")
            + '\n[lints.clippy]\nunwrap_used = "deny"\n',
            encoding="utf-8",
        )
        self.source.write_text(
            "pub fn required(value: Option<u32>) -> u32 { value.unwrap() }\n",
            encoding="utf-8",
        )

        proc = self.run_audit("--all-targets", "--json")
        self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual("incomplete", payload["status"])
        self.assertTrue(
            any("full requested target scope" in item for item in payload["tooling_errors"]),
            payload["tooling_errors"],
        )
        analyzed_kinds = {
            kind
            for target in payload["scope"]["analyzed_targets"]
            for kind in target["kind"]
        }
        self.assertNotIn("test", analyzed_kinds)

    def test_run_clippy_preserves_manifest_deny_with_colored_cargo_stderr(self) -> None:
        self.crate_manifest.write_text(
            self.crate_manifest.read_text(encoding="utf-8")
            + '\n[lints.clippy]\nunwrap_used = "deny"\n',
            encoding="utf-8",
        )
        self.source.write_text(
            "pub fn required(value: Option<u32>) -> u32 { value.unwrap() }\n",
            encoding="utf-8",
        )
        cargo_config = self.root / ".cargo" / "config.toml"
        cargo_config.parent.mkdir()
        cargo_config.write_text('[term]\ncolor = "always"\n', encoding="utf-8")
        args = panic_audit.parse_args(
            ["--manifest-path", str(self.manifest), "--profile", "core"]
        )

        result, findings, non_policy_errors = panic_audit.run_clippy(
            args,
            self.manifest,
            self.root,
            False,
            ["clippy::unwrap_used"],
            panic_audit.cargo_executable(),
        )

        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("\x1b[", result.stderr)
        self.assertEqual([], non_policy_errors)
        self.assertEqual(["clippy::unwrap_used"], [item.kind for item in findings])
        self.assertEqual(["error"], [item.level for item in findings])
        self.assertIs(False, panic_audit.cargo_build_success(result.stdout))
        self.assertTrue(
            panic_audit.nonzero_clippy_is_policy_only(
                result, findings, non_policy_errors
            )
        )

    def test_missing_manifest_is_json_exit_two(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--manifest-path",
                str(self.root / "missing.toml"),
                "--profile",
                "strict-boundary",
                "--json",
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(2, proc.returncode)
        payload = json.loads(proc.stdout)
        self.assertEqual("incomplete", payload["status"])
        self.assertIn("manifest does not exist", payload["tooling_errors"][0])


if __name__ == "__main__":
    unittest.main()
