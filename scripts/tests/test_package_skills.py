from __future__ import annotations

import importlib.util
import json
import os
import platform
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "package_skills.py"
SPEC = importlib.util.spec_from_file_location("package_skills", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
package_skills = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package_skills)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class PackageSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(prefix="package-skills-test-")
        self.repo = Path(self.tmpdir.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.original_repo_root = package_skills.REPO_ROOT
        self.original_config_path = package_skills.CONFIG_PATH
        package_skills.REPO_ROOT = self.repo
        package_skills.CONFIG_PATH = self.repo / "packaging" / "skills.toml"
        self.addCleanup(self.restore_module_paths)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def restore_module_paths(self) -> None:
        package_skills.REPO_ROOT = self.original_repo_root
        package_skills.CONFIG_PATH = self.original_config_path

    def write_config(self) -> None:
        write(
            package_skills.CONFIG_PATH,
            textwrap.dedent(
                """
                [skills.tool]
                package = "tool"
                binary = "tool"
                skill_dir = "plugins/tool/skills/tool"
                launcher = "scripts/tool"
                required_platforms = ["linux-x86_64"]
                ci_platforms = ["linux-x86_64"]
                """
            ).strip()
            + "\n",
        )

    def write_workspace(self) -> None:
        write(
            self.repo / "Cargo.toml",
            textwrap.dedent(
                """
                [workspace]
                members = ["crates/tool", "crates/helper"]
                resolver = "2"
                """
            ).strip()
            + "\n",
        )
        write(
            self.repo / "Cargo.lock",
            "# test lockfile\n",
        )
        write(
            self.repo / "rust-toolchain.toml",
            textwrap.dedent(
                """
                [toolchain]
                channel = "stable"
                """
            ).strip()
            + "\n",
        )
        write(
            self.repo / "crates" / "tool" / "Cargo.toml",
            textwrap.dedent(
                """
                [package]
                name = "tool"
                version = "0.1.0"
                edition = "2021"

                [dependencies]
                helper = { path = "../helper" }
                """
            ).strip()
            + "\n",
        )
        write(self.repo / "crates" / "tool" / "src" / "main.rs", "fn main() {}\n")
        write(
            self.repo / "crates" / "helper" / "Cargo.toml",
            textwrap.dedent(
                """
                [package]
                name = "helper"
                version = "0.1.0"
                edition = "2021"
                """
            ).strip()
            + "\n",
        )
        write(self.repo / "crates" / "helper" / "src" / "lib.rs", "pub fn helper() {}\n")
        write(self.repo / "plugins" / "tool" / "skills" / "tool" / "scripts" / "tool", "#!/bin/sh\n")
        write(self.repo / "plugins" / "tool" / "skills" / "tool" / "tests" / "smoke.sh", "#!/bin/sh\n")

    def write_multi_config(self) -> None:
        write(
            package_skills.CONFIG_PATH,
            textwrap.dedent(
                """
                [skills.tool]
                package = "tool"
                binary = "tool"
                skill_dir = "plugins/tool/skills/tool"
                launcher = "scripts/tool"
                required_platforms = ["linux-x86_64"]
                ci_platforms = ["linux-x86_64"]

                [skills.helper]
                package = "helper"
                binary = "helper"
                skill_dir = "plugins/helper/skills/helper"
                launcher = "scripts/helper"
                required_platforms = ["linux-x86_64"]
                ci_platforms = ["linux-x86_64"]
                """
            ).strip()
            + "\n",
        )

    def test_selected_platforms_prefers_manifest_order(self) -> None:
        self.write_config()
        config = package_skills.load_config()
        self.assertEqual(package_skills.selected_platforms(config, "required"), ["linux-x86_64"])
        self.assertEqual(package_skills.selected_platforms(config, "ci"), ["linux-x86_64"])
        self.assertEqual(package_skills.selected_platforms(config, "all"), ["linux-x86_64"])

    def test_host_platform_id_rejects_non_linux_hosts(self) -> None:
        original_sys_platform = sys.platform
        original_machine = platform.machine
        original_module_sys_platform = package_skills.sys.platform
        original_module_platform_machine = package_skills.platform.machine

        sys.platform = "darwin"
        package_skills.sys.platform = "darwin"
        platform.machine = lambda: "x86_64"
        package_skills.platform.machine = lambda: "x86_64"
        self.addCleanup(setattr, sys, "platform", original_sys_platform)
        self.addCleanup(setattr, package_skills.sys, "platform", original_module_sys_platform)
        self.addCleanup(setattr, platform, "machine", original_machine)
        self.addCleanup(setattr, package_skills.platform, "machine", original_module_platform_machine)

        with self.assertRaises(SystemExit) as ctx:
            package_skills.host_platform_id()
        self.assertIn("only Linux packaging is supported", str(ctx.exception))

    def test_verify_complete_accepts_tracked_required_payloads(self) -> None:
        self.write_config()
        payload = self.repo / "plugins" / "tool" / "skills" / "tool" / "dist" / "linux-x86_64" / "tool"
        write(payload, "linux binary\n")
        payload.chmod(0o755)
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)

        package_skills.verify_complete("required")

    def test_compare_and_sync_artifacts_use_downloaded_artifact_tree(self) -> None:
        self.write_config()
        repo_payload = self.repo / "plugins" / "tool" / "skills" / "tool" / "dist" / "linux-x86_64" / "tool"
        write(repo_payload, "old payload\n")
        repo_payload.chmod(0o755)
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)

        artifact_root = self.repo / "artifact-downloads"
        artifact_payload = artifact_root / "skill-dist-linux-x86_64" / "plugins" / "tool" / "skills" / "tool" / "dist" / "linux-x86_64" / "tool"
        write(artifact_payload, "new payload\n")

        with self.assertRaises(SystemExit):
            package_skills.compare_artifacts(artifact_root, "required")

        package_skills.sync_artifacts(artifact_root, "required")
        self.assertEqual(repo_payload.read_text(encoding="utf-8"), "new payload\n")
        package_skills.compare_artifacts(artifact_root, "required")

    def test_stage_host_can_target_specific_skills(self) -> None:
        self.write_multi_config()
        target_release = self.repo / "target" / "release"
        write(target_release / "tool", "tool payload\n")
        write(target_release / "helper", "helper payload\n")

        original_stage_host_native = package_skills.stage_host_native
        original_use_container_build = package_skills.use_container_build
        original_host_platform_id = package_skills.host_platform_id
        calls: list[tuple[list[tuple[str, dict[str, object]]], str]] = []

        def fake_stage_host_native(selected: list[tuple[str, dict[str, object]]], platform_id: str) -> None:
            calls.append((selected, platform_id))
            for _, skill in selected:
                target_name = str(skill["binary"])
                dst = self.repo / str(skill["skill_dir"]) / "dist" / platform_id / target_name
                write(dst, f"{target_name} payload\n")
                dst.chmod(0o755)

        package_skills.stage_host_native = fake_stage_host_native
        package_skills.use_container_build = lambda platform_id: False
        package_skills.host_platform_id = lambda: "linux-x86_64"
        self.addCleanup(setattr, package_skills, "stage_host_native", original_stage_host_native)
        self.addCleanup(setattr, package_skills, "use_container_build", original_use_container_build)
        self.addCleanup(setattr, package_skills, "host_platform_id", original_host_platform_id)

        package_skills.stage_host(["tool"])

        self.assertEqual(
            calls,
            [([("tool", package_skills.load_config()["tool"])], "linux-x86_64")],
        )
        self.assertTrue((self.repo / "plugins" / "tool" / "skills" / "tool" / "dist" / "linux-x86_64" / "tool").exists())
        self.assertFalse((self.repo / "plugins" / "helper" / "skills" / "helper" / "dist" / "linux-x86_64" / "helper").exists())

    def test_selected_skill_entries_rejects_unknown_skill(self) -> None:
        self.write_config()
        config = package_skills.load_config()
        with self.assertRaises(SystemExit) as ctx:
            package_skills.selected_skill_entries(config, ["missing"])
        self.assertIn("unknown packaged skill(s): missing", str(ctx.exception))

    def test_compare_artifacts_flags_stale_repo_payloads_and_sync_removes_them(self) -> None:
        self.write_config()
        repo_payload = self.repo / "plugins" / "tool" / "skills" / "tool" / "dist" / "linux-x86_64" / "tool"
        stale_payload = self.repo / "plugins" / "helper" / "skills" / "helper" / "dist" / "linux-x86_64" / "helper"
        write(repo_payload, "current payload\n")
        write(stale_payload, "stale payload\n")
        repo_payload.chmod(0o755)
        stale_payload.chmod(0o755)

        artifact_root = self.repo / "artifact-downloads"
        artifact_payload = artifact_root / "skill-dist-linux-x86_64" / "plugins" / "tool" / "skills" / "tool" / "dist" / "linux-x86_64" / "tool"
        write(artifact_payload, "current payload\n")

        with self.assertRaises(SystemExit) as ctx:
            package_skills.compare_artifacts(artifact_root, "required")
        self.assertIn("artifact payloads do not match", str(ctx.exception))

        package_skills.sync_artifacts(artifact_root, "required")
        self.assertTrue(repo_payload.exists())
        self.assertFalse(stale_payload.exists())
        package_skills.compare_artifacts(artifact_root, "required")

    def test_build_env_adds_reproducible_remap_flags(self) -> None:
        original_env = os.environ.copy()
        original_repo_root = package_skills.REPO_ROOT
        package_skills.REPO_ROOT = Path("/workspace/repo")
        os.environ["CARGO_HOME"] = "/custom/cargo"
        os.environ["RUSTUP_HOME"] = "/custom/rustup"
        os.environ["PATH"] = "/tmp/bin:/dev-cache/intercepts:/usr/bin"
        os.environ["RUSTFLAGS"] = "-C target-cpu=native"
        self.addCleanup(setattr, package_skills, "REPO_ROOT", original_repo_root)
        self.addCleanup(os.environ.clear)
        self.addCleanup(os.environ.update, original_env)

        env = package_skills.build_env()

        self.assertIn("--remap-path-prefix=/workspace/repo=/workspace", env["RUSTFLAGS"])
        self.assertIn("--remap-path-prefix=/custom/cargo=/cargo-home", env["RUSTFLAGS"])
        self.assertIn("--remap-path-prefix=/custom/rustup=/rustup-home", env["RUSTFLAGS"])
        self.assertNotIn("target-cpu=native", env["RUSTFLAGS"])
        self.assertIn("-Cstrip=symbols", env["RUSTFLAGS"])
        self.assertNotIn("/Brepro", env["RUSTFLAGS"])
        self.assertEqual(env["PATH"], "/tmp/bin:/usr/bin")
        self.assertEqual(env["CARGO_INCREMENTAL"], "0")
        self.assertEqual(env["SOURCE_DATE_EPOCH"], "1")

    def test_windows_release_env_adds_reproducible_linker_flag(self) -> None:
        original_env = os.environ.copy()
        os.environ["CARGO_HOME"] = "/custom/cargo"
        os.environ["RUSTUP_HOME"] = "/custom/rustup"
        self.addCleanup(os.environ.clear)
        self.addCleanup(os.environ.update, original_env)

        env = package_skills.build_env_for_root(
            Path("/workspace/repo"), "x86_64-pc-windows-msvc"
        )

        self.assertIn("--remap-path-prefix=/workspace/repo=/workspace", env["RUSTFLAGS"])
        self.assertIn("--remap-path-prefix=/custom/cargo=/cargo-home", env["RUSTFLAGS"])
        self.assertIn("--remap-path-prefix=/custom/rustup=/rustup-home", env["RUSTFLAGS"])
        self.assertIn("-Clink-arg=/Brepro", env["RUSTFLAGS"])
        self.assertIn("-Clink-arg=/DEBUG:NONE", env["RUSTFLAGS"])
        self.assertIn("-Clink-arg=/timestamp:1", env["RUSTFLAGS"])

    def test_container_rustflags_use_fixed_container_prefixes(self) -> None:
        original_env = os.environ.copy()
        os.environ["RUSTFLAGS"] = "-C target-cpu=native"
        self.addCleanup(os.environ.clear)
        self.addCleanup(os.environ.update, original_env)

        flags = package_skills.container_rustflags()

        self.assertIn("--remap-path-prefix=/work=/workspace", flags)
        self.assertIn("--remap-path-prefix=/usr/local/cargo=/cargo-home", flags)
        self.assertIn("--remap-path-prefix=/usr/local/rustup=/rustup-home", flags)
        self.assertTrue(flags.endswith("-C target-cpu=native"))

    def test_use_container_build_prefers_docker_for_linux_x86_64_in_auto_mode(self) -> None:
        original_env = os.environ.copy()
        original_docker_available = package_skills.docker_available
        os.environ.pop("AGENT_TOOLING_DIST_BUILD_MODE", None)
        os.environ.pop("AGENT_SKILLS_DIST_BUILD_MODE", None)
        package_skills.docker_available = lambda: True
        self.addCleanup(os.environ.clear)
        self.addCleanup(os.environ.update, original_env)
        self.addCleanup(setattr, package_skills, "docker_available", original_docker_available)

        self.assertTrue(package_skills.use_container_build("linux-x86_64"))
        self.assertFalse(package_skills.use_container_build("linux-aarch64"))

    def test_dist_build_mode_accepts_deprecated_agent_skills_alias(self) -> None:
        original_env = os.environ.copy()
        os.environ.pop("AGENT_TOOLING_DIST_BUILD_MODE", None)
        os.environ["AGENT_SKILLS_DIST_BUILD_MODE"] = "host"
        self.addCleanup(os.environ.clear)
        self.addCleanup(os.environ.update, original_env)

        self.assertEqual(package_skills.dist_build_mode(), "host")

    def test_use_container_build_requires_docker_in_container_mode(self) -> None:
        original_env = os.environ.copy()
        original_docker_available = package_skills.docker_available
        os.environ["AGENT_TOOLING_DIST_BUILD_MODE"] = "container"
        os.environ.pop("AGENT_SKILLS_DIST_BUILD_MODE", None)
        package_skills.docker_available = lambda: False
        self.addCleanup(os.environ.clear)
        self.addCleanup(os.environ.update, original_env)
        self.addCleanup(setattr, package_skills, "docker_available", original_docker_available)

        with self.assertRaises(SystemExit) as ctx:
            package_skills.use_container_build("linux-x86_64")
        self.assertIn("cannot run a container", str(ctx.exception))

    def _stub_docker(self, *, on_path: bool, info_returncode: int = 0, raises: bool = False):
        """Replace the two calls docker_available makes on the outside world."""
        original_which = package_skills.shutil.which
        original_run = package_skills.subprocess.run
        self.addCleanup(setattr, package_skills.shutil, "which", original_which)
        self.addCleanup(setattr, package_skills.subprocess, "run", original_run)

        package_skills.shutil.which = lambda name: "/usr/bin/docker" if on_path else None

        def fake_run(cmd, *args, **kwargs):
            if raises:
                raise OSError("docker went away")
            return subprocess.CompletedProcess(cmd, info_returncode, b"", b"")

        package_skills.subprocess.run = fake_run

    def test_docker_available_is_false_when_docker_is_not_installed(self) -> None:
        self._stub_docker(on_path=False)
        self.assertFalse(package_skills.docker_available())

    def test_docker_available_is_false_when_the_daemon_cannot_run_a_container(self) -> None:
        # The case that motivated the probe: docker is installed and answers, but
        # a kernel updated without a reboot leaves it unable to build a container
        # network. Checking PATH alone reported this as available and turned a
        # recoverable condition into a hard failure mid-build.
        self._stub_docker(on_path=True, info_returncode=1)
        self.assertFalse(package_skills.docker_available())

    def test_docker_available_is_false_when_probing_raises(self) -> None:
        self._stub_docker(on_path=True, raises=True)
        self.assertFalse(package_skills.docker_available())

    def test_docker_available_is_true_when_the_daemon_answers(self) -> None:
        self._stub_docker(on_path=True, info_returncode=0)
        self.assertTrue(package_skills.docker_available())

    def test_auto_mode_falls_back_to_host_when_the_daemon_is_broken(self) -> None:
        original_env = os.environ.copy()
        os.environ.pop("AGENT_TOOLING_DIST_BUILD_MODE", None)
        os.environ.pop("AGENT_SKILLS_DIST_BUILD_MODE", None)
        self.addCleanup(os.environ.clear)
        self.addCleanup(os.environ.update, original_env)
        self._stub_docker(on_path=True, info_returncode=1)

        self.assertFalse(package_skills.use_container_build("linux-x86_64"))

    def test_watched_repo_paths_include_crates_launchers_and_dist(self) -> None:
        self.write_config()
        self.write_workspace()

        watched = package_skills.watched_repo_paths(package_skills.load_config(), ["tool"])

        self.assertIn("packaging/skills.toml", watched)
        self.assertIn("scripts/package_skills.py", watched)
        self.assertIn("Cargo.toml", watched)
        self.assertIn("Cargo.lock", watched)
        self.assertIn("rust-toolchain.toml", watched)
        self.assertIn("crates/tool", watched)
        self.assertIn("crates/helper", watched)
        self.assertIn("plugins/tool/skills/tool/scripts/tool", watched)
        self.assertIn("plugins/tool/skills/tool/dist", watched)

    def test_matches_changed_files_respects_watch_prefixes_and_optional_tests(self) -> None:
        self.write_config()
        self.write_workspace()
        config = package_skills.load_config()

        self.assertTrue(
            package_skills.matches_changed_files(
                ["crates/helper/src/lib.rs"],
                config,
                ["tool"],
            )
        )
        self.assertTrue(
            package_skills.matches_changed_files(
                ["plugins/tool/skills/tool/dist/linux-x86_64/tool"],
                config,
                ["tool"],
            )
        )
        self.assertFalse(
            package_skills.matches_changed_files(
                ["plugins/tool/skills/tool/tests/smoke.sh"],
                config,
                ["tool"],
            )
        )
        self.assertTrue(
            package_skills.matches_changed_files(
                ["./plugins/tool/skills/tool/tests/smoke.sh"],
                config,
                ["tool"],
                include_tests=True,
            )
        )

    def test_tracked_dist_paths_follow_each_skill_target_matrix_and_binary_name(self) -> None:
        write(
            package_skills.CONFIG_PATH,
            textwrap.dedent(
                """
                [skills.tool]
                package = "tool"
                binary = "tool"
                skill_dir = "plugins/tool/skills/tool"
                launcher = "scripts/tool"
                required_platforms = ["linux-x86_64"]
                ci_platforms = ["linux-x86_64"]

                [skills."matrix"]
                package = "matrix-tool"
                binary = "matrix-tool"
                skill_dir = "plugins/matrix/skills/matrix"
                launcher = "scripts/matrix-tool"
                required_platforms = ["linux-x86_64", "linux-aarch64", "windows-x86_64", "windows-aarch64"]
                ci_platforms = ["linux-x86_64", "linux-aarch64", "windows-x86_64", "windows-aarch64"]

                [skills."matrix".targets."linux-x86_64"]
                artifact = "matrix-tool"
                cargo_target = "x86_64-unknown-linux-gnu"

                [skills."matrix".targets."linux-aarch64"]
                artifact = "matrix-tool"
                cargo_target = "aarch64-unknown-linux-gnu"

                [skills."matrix".targets."windows-x86_64"]
                artifact = "matrix-tool.exe"
                cargo_target = "x86_64-pc-windows-msvc"

                [skills."matrix".targets."windows-aarch64"]
                artifact = "matrix-tool.exe"
                cargo_target = "aarch64-pc-windows-msvc"
                """
            ).strip()
            + "\n",
        )
        config = package_skills.load_config()

        tracked = {
            path.relative_to(self.repo).as_posix()
            for path in package_skills.tracked_dist_paths(config, "required")
        }

        self.assertEqual(
            tracked,
            {
                "plugins/tool/skills/tool/dist/linux-x86_64/tool",
                "plugins/matrix/skills/matrix/dist/linux-x86_64/matrix-tool",
                "plugins/matrix/skills/matrix/dist/linux-aarch64/matrix-tool",
                "plugins/matrix/skills/matrix/dist/windows-x86_64/matrix-tool.exe",
                "plugins/matrix/skills/matrix/dist/windows-aarch64/matrix-tool.exe",
            },
        )

    def test_sync_artifacts_is_transactional_when_any_expected_payload_is_missing(self) -> None:
        write(
            package_skills.CONFIG_PATH,
            textwrap.dedent(
                """
                [skills.first]
                package = "first"
                binary = "first"
                skill_dir = "plugins/first/skills/first"
                launcher = "scripts/first"
                required_platforms = ["linux-x86_64"]
                ci_platforms = ["linux-x86_64"]

                [skills.second]
                package = "second"
                binary = "second"
                skill_dir = "plugins/second/skills/second"
                launcher = "scripts/second"
                required_platforms = ["linux-x86_64"]
                ci_platforms = ["linux-x86_64"]
                """
            ).strip()
            + "\n",
        )
        first_repo = self.repo / "plugins" / "first" / "skills" / "first" / "dist" / "linux-x86_64" / "first"
        second_repo = self.repo / "plugins" / "second" / "skills" / "second" / "dist" / "linux-x86_64" / "second"
        write(first_repo, "old first\n")
        write(second_repo, "old second\n")
        first_repo.chmod(0o755)
        second_repo.chmod(0o755)

        artifact_root = self.repo / "artifact-downloads"
        artifact_first = artifact_root / "skill-dist-linux-x86_64" / "plugins" / "first" / "skills" / "first" / "dist" / "linux-x86_64" / "first"
        write(artifact_first, "new first\n")

        with self.assertRaises(SystemExit) as ctx:
            package_skills.sync_artifacts(artifact_root, "required")
        self.assertIn("missing artifact payload", str(ctx.exception))
        self.assertEqual(first_repo.read_text(encoding="utf-8"), "old first\n")
        self.assertEqual(second_repo.read_text(encoding="utf-8"), "old second\n")

    def test_dist_refresh_uses_frozen_git_index_and_records_dev_cache_receipt(self) -> None:
        write(
            package_skills.CONFIG_PATH,
            textwrap.dedent(
                """
                [skills."release-tool"]
                package = "release-tool"
                binary = "release-tool"
                skill_dir = "plugins/release-tool/skills/release-tool"
                launcher = "scripts/release-tool"
                required_platforms = ["windows-x86_64"]
                ci_platforms = ["windows-x86_64"]
                dist_sources = ["Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "crates/release-tool", "packaging/skills.toml"]

                [skills."release-tool".targets."windows-x86_64"]
                artifact = "release-tool.exe"
                cargo_target = "x86_64-pc-windows-msvc"
                recipe = "cargo-xwin"
                recipe_version = "0.23.1"
                """
            ).strip()
            + "\n",
        )
        write(self.repo / "Cargo.lock", "# locked\n")
        write(self.repo / "Cargo.toml", "[workspace]\nresolver = \"2\"\n")
        write(self.repo / "crates" / "release-tool" / "src" / "main.rs", "fn main() {}\n")
        write(self.repo / "crates" / "release-tool" / "Cargo.toml", "[package]\nname = \"release-tool\"\nversion = \"2.0.0\"\n")
        write(
            self.repo / "rust-toolchain.toml",
            "[toolchain]\nchannel = \"stable\"\n",
        )
        write(self.repo / "plugins" / "release-tool" / "skills" / "release-tool" / "scripts" / "release-tool", "#!/bin/sh\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)

        original_run = package_skills.subprocess.run
        original_stage_from_frozen_index = package_skills.stage_from_frozen_index
        original_dev_cache_temp_root = package_skills.dev_cache_temp_root
        calls: list[tuple[list[str], str | None]] = []
        dev_cache_temp = self.repo / "dev-cache-temp"
        dev_cache_temp.mkdir()
        package_skills.dev_cache_temp_root = lambda: dev_cache_temp

        def fake_run(cmd, *args, **kwargs):
            calls.append((list(cmd), kwargs.get("cwd")))
            if cmd[:3] == ["git", "write-tree", "--missing-ok"]:
                return subprocess.CompletedProcess(cmd, 0, "tree123\n", "")
            if cmd[:2] == ["git", "checkout-index"]:
                return original_run(cmd, *args, **kwargs)
            if cmd[:3] == ["git", "status", "--short"]:
                return subprocess.CompletedProcess(cmd, 0, "M " + cmd[-1] + "\n", "")
            if cmd[:3] == ["git", "add", "--"]:
                return subprocess.CompletedProcess(cmd, 0, "", "")
            if cmd[:4] == ["dev-cache", "artifacts", "put", "--json"]:
                payload = {"digest": "cache123"}
                return subprocess.CompletedProcess(cmd, 0, json.dumps(payload), "")
            raise AssertionError(f"unexpected command: {cmd}")

        build_payloads: list[Path] = []

        def fake_stage_from_frozen_index(selected_targets, frozen_root, artifacts_root):
            self.assertTrue(frozen_root.is_dir())
            self.assertTrue(artifacts_root.is_dir())
            self.assertEqual(len(selected_targets), 1)
            skill_name, _, platform_id = selected_targets[0]
            self.assertEqual(skill_name, "release-tool")
            self.assertEqual(platform_id, "windows-x86_64")
            payload = (
                artifacts_root
                / "plugins"
                / "release-tool"
                / "skills"
                / "release-tool"
                / "dist"
                / "windows-x86_64"
                / "release-tool.exe"
            )
            write(payload, "windows payload\n")
            payload.chmod(0o755)
            build_payloads.append(payload)

        package_skills.subprocess.run = fake_run
        package_skills.stage_from_frozen_index = fake_stage_from_frozen_index
        self.addCleanup(setattr, package_skills, "subprocess", package_skills.subprocess)
        self.addCleanup(setattr, package_skills, "stage_from_frozen_index", original_stage_from_frozen_index)
        self.addCleanup(setattr, package_skills, "dev_cache_temp_root", original_dev_cache_temp_root)
        self.addCleanup(setattr, package_skills.subprocess, "run", original_run)

        changed = package_skills.dist_refresh("index", "required", skill_names=["release-tool"], git_stage=True)

        self.assertEqual(len(build_payloads), 2, "release refresh must compare two independent builds")
        self.assertTrue(
            all(str(payload).startswith(str(dev_cache_temp)) for payload in build_payloads),
            "release build roots must be owned by dev-cache",
        )
        self.assertEqual(
            set(changed),
            {
                "plugins/release-tool/skills/release-tool/dist/windows-x86_64/release-tool.exe",
                "plugins/release-tool/skills/release-tool/dist/receipt.json",
            },
        )
        receipt = self.repo / "plugins/release-tool/skills/release-tool/dist/receipt.json"
        self.assertTrue(receipt.is_file())
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "agent-tooling-skill-dist-receipt.v2")
        self.assertRegex(payload["source"]["digest"], r"^sha256:[0-9a-f]{64}$")
        self.assertRegex(payload["source"]["cargo_lock_digest"], r"^sha256:[0-9a-f]{64}$")
        self.assertRegex(payload["build_recipe_digest"], r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(payload["artifacts"][0]["platform"], "windows-x86_64")
        self.assertEqual(payload["artifacts"][0]["artifact"], "release-tool.exe")
        self.assertEqual(payload["artifacts"][0]["recipe"], "cargo-xwin")
        self.assertEqual(payload["artifacts"][0]["recipe_version"], "0.23.1")
        self.assertEqual(payload["artifacts"][0]["dev_cache_cas_digest"], "cache123")
        self.assertEqual(
            sum(1 for cmd, _ in calls if cmd[:2] == ["git", "checkout-index"]),
            2,
        )
        self.assertTrue(
            any(
                cmd[:4] == ["dev-cache", "artifacts", "put", "--json"]
                and cmd[-1]
                == str(
                    self.repo
                    / "plugins"
                    / "release-tool"
                    / "skills"
                    / "release-tool"
                    / "dist"
                    / "windows-x86_64"
                    / "release-tool.exe"
                )
                for cmd, _ in calls
            )
        )

    def test_release_tool_versions_use_the_plugin_executables_directly(self) -> None:
        calls: list[tuple[list[str], str]] = []
        original_command_version = package_skills.command_version
        original_which = package_skills.shutil.which

        def fake_command_version(command: list[str], label: str) -> str:
            calls.append((command, label))
            if command == ["cargo-zigbuild", "--version"]:
                return "cargo-zigbuild 0.23.3"
            if command == ["zig", "version"]:
                return "0.16.0"
            if command == ["cargo-xwin", "--version"]:
                return "cargo-xwin 0.23.1"
            if command == ["clang", "--version"]:
                return "clang version 22.1.8"
            raise AssertionError(f"unexpected version command: {command}")

        package_skills.command_version = fake_command_version
        package_skills.shutil.which = lambda command: "/usr/bin/lld-link" if command == "lld-link" else original_which(command)
        self.addCleanup(setattr, package_skills, "command_version", original_command_version)
        self.addCleanup(setattr, package_skills.shutil, "which", original_which)

        package_skills.verify_release_tool(
            {
                "targets": {
                    "linux-x86_64": {
                        "recipe": "cargo-zigbuild",
                        "recipe_version": "0.23.3",
                        "zig_version": "0.16.0",
                    }
                }
            },
            "linux-x86_64",
        )
        package_skills.verify_release_tool(
            {
                "targets": {
                    "windows-x86_64": {
                        "recipe": "cargo-xwin",
                        "recipe_version": "0.23.1",
                        "llvm_version": "22.1.8",
                    }
                }
            },
            "windows-x86_64",
        )

        self.assertIn((["cargo-zigbuild", "--version"], "cargo-zigbuild"), calls)
        self.assertIn((["cargo-xwin", "--version"], "cargo-xwin"), calls)

    def test_dev_cache_temp_root_uses_explicit_repo_routing(self) -> None:
        routed = self.repo / "owned-temp"
        original_run = package_skills.subprocess.run
        calls: list[list[str]] = []

        def fake_run(command, *args, **kwargs):
            calls.append(list(command))
            return subprocess.CompletedProcess(
                command,
                0,
                json.dumps({"adapter": "temp", "path": str(routed)}),
                "",
            )

        package_skills.subprocess.run = fake_run
        self.addCleanup(setattr, package_skills.subprocess, "run", original_run)

        self.assertEqual(package_skills.dev_cache_temp_root(), routed)
        self.assertTrue(routed.is_dir())
        self.assertEqual(
            calls,
            [["dev-cache", "path", "temp", "--repo", str(self.repo), "--json"]],
        )

    def test_verify_dist_receipt_is_pure_and_detects_source_or_binary_drift(self) -> None:
        write(
            package_skills.CONFIG_PATH,
            textwrap.dedent(
                """
                [skills."release-tool"]
                package = "release-tool"
                binary = "release-tool"
                skill_dir = "plugins/release-tool/skills/release-tool"
                launcher = "scripts/release-tool"
                required_platforms = ["linux-x86_64"]
                ci_platforms = ["linux-x86_64"]
                dist_sources = ["Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "crates/release-tool", "packaging/skills.toml"]

                [skills."release-tool".targets."linux-x86_64"]
                artifact = "release-tool"
                cargo_target = "x86_64-unknown-linux-musl"
                recipe = "cargo-zigbuild"
                recipe_version = "0.23.3"
                """
            ).strip()
            + "\n",
        )
        write(self.repo / "Cargo.toml", "[workspace]\nresolver = \"2\"\n")
        write(self.repo / "Cargo.lock", "# locked\n")
        write(self.repo / "rust-toolchain.toml", "[toolchain]\nchannel = \"1.94.1\"\n")
        original_source = "fn main() {}\n"
        write(self.repo / "crates/release-tool/src/main.rs", original_source)
        write(self.repo / "crates/release-tool/Cargo.toml", "[package]\nname = \"release-tool\"\nversion = \"2.0.0\"\n")
        artifact = self.repo / "plugins/release-tool/skills/release-tool/dist/linux-x86_64/release-tool"
        write(artifact, "binary\n")
        artifact.chmod(0o755)

        config = package_skills.load_config()
        skill = config["release-tool"]
        source = package_skills.source_receipt(skill, self.repo)
        receipt = {
            "schema": "agent-tooling-skill-dist-receipt.v2",
            "skill": "release-tool",
            "source": source,
            "toolchain": {"channel": "1.94.1"},
            "build_recipe_digest": package_skills.build_recipe_digest(skill, ["linux-x86_64"]),
            "artifacts": [{
                "platform": "linux-x86_64",
                "artifact": "release-tool",
                "cargo_target": "x86_64-unknown-linux-musl",
                "recipe": "cargo-zigbuild",
                "recipe_version": "0.23.3",
                "output_digest": package_skills.sha256_file(artifact),
                "dev_cache_cas_digest": "cache123",
            }],
        }
        receipt_path = self.repo / "plugins/release-tool/skills/release-tool/dist/receipt.json"
        write(receipt_path, json.dumps(receipt, sort_keys=True) + "\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)

        original_stage = package_skills.stage_from_frozen_index
        package_skills.stage_from_frozen_index = lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("verification must never build")
        )
        self.addCleanup(setattr, package_skills, "stage_from_frozen_index", original_stage)

        package_skills.verify_dist_receipt("required", source="index", skill_names=["release-tool"])

        missing_toolchain = json.loads(json.dumps(receipt))
        del missing_toolchain["toolchain"]
        write(receipt_path, json.dumps(missing_toolchain, sort_keys=True) + "\n")
        subprocess.run(["git", "-C", str(self.repo), "add", str(receipt_path.relative_to(self.repo))], check=True)
        with self.assertRaises(SystemExit) as toolchain_error:
            package_skills.verify_dist_receipt("required", source="index", skill_names=["release-tool"])
        self.assertIn("toolchain", str(toolchain_error.exception))
        write(receipt_path, json.dumps(receipt, sort_keys=True) + "\n")
        subprocess.run(["git", "-C", str(self.repo), "add", str(receipt_path.relative_to(self.repo))], check=True)

        missing_cache_binding = json.loads(json.dumps(receipt))
        del missing_cache_binding["artifacts"][0]["dev_cache_cas_digest"]
        write(receipt_path, json.dumps(missing_cache_binding, sort_keys=True) + "\n")
        subprocess.run(["git", "-C", str(self.repo), "add", str(receipt_path.relative_to(self.repo))], check=True)
        with self.assertRaises(SystemExit) as cache_error:
            package_skills.verify_dist_receipt("required", source="index", skill_names=["release-tool"])
        self.assertIn("dev-cache CAS digest", str(cache_error.exception))
        write(receipt_path, json.dumps(receipt, sort_keys=True) + "\n")
        subprocess.run(["git", "-C", str(self.repo), "add", str(receipt_path.relative_to(self.repo))], check=True)

        write(self.repo / "crates/release-tool/src/main.rs", "fn main() { println!(\"changed\"); }\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "crates/release-tool/src/main.rs"], check=True)
        with self.assertRaises(SystemExit) as source_error:
            package_skills.verify_dist_receipt("required", source="index", skill_names=["release-tool"])
        self.assertIn("source digest", str(source_error.exception))

        write(self.repo / "crates/release-tool/src/main.rs", original_source)
        subprocess.run(["git", "-C", str(self.repo), "add", "crates/release-tool/src/main.rs"], check=True)
        write(artifact, "mutated\n")
        subprocess.run(["git", "-C", str(self.repo), "add", str(artifact.relative_to(self.repo))], check=True)
        with self.assertRaises(SystemExit) as artifact_error:
            package_skills.verify_dist_receipt("required", source="index", skill_names=["release-tool"])
        self.assertIn("artifact digest", str(artifact_error.exception))


class HookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(prefix="package-skills-hook-test-")
        self.root = Path(self.tmpdir.name)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _run_hook(
        self,
        hook_name: str,
        *,
        stdin: str = "",
    ) -> tuple[subprocess.CompletedProcess[str], str]:
        bin_dir = self.root / "bin"
        log_path = self.root / "log.txt"
        bin_dir.mkdir(parents=True, exist_ok=True)
        just = bin_dir / "just"
        just.write_text(
            "#!/bin/sh\nprintf 'just %s\\n' \"$*\" >> \"$HOOK_LOG\"\n",
            encoding="utf-8",
        )
        just.chmod(0o755)

        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
        env["HOOK_LOG"] = str(log_path)

        result = subprocess.run(
            [str(MODULE_PATH.parents[1] / "githooks" / hook_name)],
            check=False,
            cwd=MODULE_PATH.parents[1],
            env=env,
            input=stdin,
            text=True,
            capture_output=True,
        )
        return result, log_path.read_text(encoding="utf-8")

    def test_pre_push_runs_the_non_mutating_repository_gate(self) -> None:
        result, log = self._run_hook("pre-push")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(log, "just ci\n")


class VendorCopyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory(prefix="package-skills-vendor-test-")
        self.repo = Path(self.tmpdir.name)
        self.original_repo_root = package_skills.REPO_ROOT
        self.original_config_path = package_skills.CONFIG_PATH
        package_skills.REPO_ROOT = self.repo
        package_skills.CONFIG_PATH = self.repo / "packaging" / "skills.toml"
        self.addCleanup(self.restore_module_paths)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def restore_module_paths(self) -> None:
        package_skills.REPO_ROOT = self.original_repo_root
        package_skills.CONFIG_PATH = self.original_config_path

    def write_vendor_config(self) -> None:
        write(
            package_skills.CONFIG_PATH,
            textwrap.dedent(
                """
                [[vendor.copies]]
                source = "plugins/a/skills/a/scripts/shared.sh"
                targets = ["plugins/a/skills/b/scripts/shared.sh"]
                """
            ).strip()
            + "\n",
        )

    def test_vendor_sync_then_check(self) -> None:
        self.write_vendor_config()
        source = self.repo / "plugins/a/skills/a/scripts/shared.sh"
        target = self.repo / "plugins/a/skills/b/scripts/shared.sh"
        write(source, "#!/bin/sh\necho shared\n")

        with self.assertRaises(SystemExit):
            package_skills.vendor_copies(check_only=True)

        package_skills.vendor_copies(check_only=False)
        self.assertEqual(source.read_bytes(), target.read_bytes())
        package_skills.vendor_copies(check_only=True)

    def test_vendor_check_detects_drift(self) -> None:
        self.write_vendor_config()
        source = self.repo / "plugins/a/skills/a/scripts/shared.sh"
        target = self.repo / "plugins/a/skills/b/scripts/shared.sh"
        write(source, "#!/bin/sh\necho shared\n")
        write(target, "#!/bin/sh\necho drifted\n")

        with self.assertRaises(SystemExit) as ctx:
            package_skills.vendor_copies(check_only=True)
        self.assertIn("out of sync", str(ctx.exception))

    def test_vendor_missing_source_fails(self) -> None:
        self.write_vendor_config()
        with self.assertRaises(SystemExit) as ctx:
            package_skills.vendor_copies(check_only=True)
        self.assertIn("vendor source missing", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
