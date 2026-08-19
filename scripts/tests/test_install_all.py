from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_ALL = REPO_ROOT / "scripts" / "install-all"
CODEX_MARKETPLACE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
CLAUDE_MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"


def write_fake_cli(path: Path, command_name: str) -> None:
    path.write_text(
        textwrap.dedent(
            f"""\
            #!{sys.executable}
            import json
            import os
            import sys

            with open(os.environ["AGENT_TOOLING_FAKE_CLI_LOG"], "a", encoding="utf-8") as handle:
                handle.write(json.dumps({{"command": {command_name!r}, "args": sys.argv[1:]}}) + "\\n")
            if sys.argv[1:] == ["plugin", "marketplace", "list", "--json"]:
                configured = json.loads(os.environ.get("AGENT_TOOLING_FAKE_MARKETPLACES", "{{}}"))
                names = configured.get({command_name!r}, [])
                payload = [{{"name": name}} for name in names]
                if {command_name!r} == "codex":
                    payload = {{"marketplaces": payload}}
                print(json.dumps(payload))
            """
        ),
        encoding="utf-8",
    )
    path.chmod(0o755)


def load_calls(log_path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]


def marketplace_plugin_selectors(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [f'{entry["name"]}@{data["name"]}' for entry in data["plugins"]]


class InstallAllTests(unittest.TestCase):
    def _run_install_all_process(
        self,
        repo_root: Path,
        temp_root: Path,
        *args: str,
        fake_marketplaces: dict[str, list[str]] | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], list[dict[str, object]]]:
        install_all = repo_root / "scripts" / "install-all"
        bin_dir = temp_root / "bin"
        bin_dir.mkdir()
        log_path = temp_root / "cli.jsonl"
        log_path.touch()
        write_fake_cli(bin_dir / "codex", "codex")
        write_fake_cli(bin_dir / "claude", "claude")
        path_value = os.environ.get("PATH", os.defpath)
        env = {
            **os.environ,
            "PATH": f"{bin_dir}{os.pathsep}{path_value}",
            "AGENT_TOOLING_FAKE_CLI_LOG": str(log_path),
            "AGENT_TOOLING_FAKE_MARKETPLACES": json.dumps(fake_marketplaces or {}),
        }
        proc = subprocess.run(
            [str(install_all), *args],
            cwd=repo_root,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=120,
        )
        return proc, load_calls(log_path)

    def run_install_all_process(
        self,
        *args: str,
        fake_marketplaces: dict[str, list[str]] | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], list[dict[str, object]]]:
        with tempfile.TemporaryDirectory(prefix="install-all-test-") as tmp:
            tmp_path = Path(tmp)
            return self._run_install_all_process(
                REPO_ROOT,
                tmp_path,
                *args,
                fake_marketplaces=fake_marketplaces,
            )

    def run_install_all_with_catalogs(
        self,
        codex_plugins: list[str],
        claude_plugins: list[str],
        *args: str,
    ) -> tuple[subprocess.CompletedProcess[str], list[dict[str, object]]]:
        with tempfile.TemporaryDirectory(prefix="install-all-catalog-test-") as tmp:
            tmp_path = Path(tmp)
            repo_root = tmp_path / "repo"
            (repo_root / "scripts").mkdir(parents=True)
            (repo_root / ".agents" / "plugins").mkdir(parents=True)
            (repo_root / ".claude-plugin").mkdir(parents=True)
            shutil.copy2(INSTALL_ALL, repo_root / "scripts" / "install-all")
            (repo_root / ".agents" / "plugins" / "marketplace.json").write_text(
                json.dumps(
                    {
                        "name": "agent-tooling",
                        "plugins": [{"name": name} for name in codex_plugins],
                    }
                ),
                encoding="utf-8",
            )
            (repo_root / ".claude-plugin" / "marketplace.json").write_text(
                json.dumps(
                    {
                        "name": "agent-tooling",
                        "plugins": [{"name": name} for name in claude_plugins],
                    }
                ),
                encoding="utf-8",
            )
            return self._run_install_all_process(repo_root, tmp_path, *args)

    def run_install_all(self, *args: str) -> list[dict[str, object]]:
        proc, calls = self.run_install_all_process(*args)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        return calls

    def test_installs_all_plugins_to_codex_and_claude_with_sparse_marketplaces(self) -> None:
        calls = self.run_install_all("--source", "DevGuyRash/agent-tooling", "--ref", "main", "--claude-scope", "local")

        codex_calls = [call["args"] for call in calls if call["command"] == "codex"]
        claude_calls = [call["args"] for call in calls if call["command"] == "claude"]

        self.assertEqual(
            ["plugin", "marketplace", "add", "--ref", "main", "--sparse", ".agents/plugins", "--sparse", "plugins", "DevGuyRash/agent-tooling"],
            codex_calls[0],
        )
        self.assertEqual(["plugin", "marketplace", "upgrade", "agent-tooling"], codex_calls[1])
        self.assertEqual(
            ["plugin", "marketplace", "add", "--scope", "local", "DevGuyRash/agent-tooling", "--sparse", ".claude-plugin", "plugins"],
            claude_calls[0],
        )
        self.assertEqual(["plugin", "marketplace", "update", "agent-tooling"], claude_calls[1])

        codex_installs = codex_calls[2:]
        claude_installs = [args for args in claude_calls[2:] if args[:2] == ["plugin", "install"]]
        # 'install' no-ops on an already-installed plugin, so each install is
        # followed by 'update' to advance the installed_plugins.json record.
        claude_updates = [args for args in claude_calls[2:] if args[:2] == ["plugin", "update"]]
        codex_plugins = [args[-1] for args in codex_installs]
        claude_plugins = [args[-1] for args in claude_installs]
        self.assertEqual(marketplace_plugin_selectors(CODEX_MARKETPLACE), codex_plugins)
        self.assertEqual(marketplace_plugin_selectors(CLAUDE_MARKETPLACE), claude_plugins)
        self.assertEqual(claude_plugins, [args[-1] for args in claude_updates])

    def test_local_source_omits_sparse_and_ref_flags(self) -> None:
        calls = self.run_install_all("--source", str(REPO_ROOT), "--codex-only")

        self.assertEqual(
            {"command": "codex", "args": ["plugin", "marketplace", "add", str(REPO_ROOT)]},
            calls[0],
        )
        self.assertFalse(any(call["command"] == "claude" for call in calls))
        self.assertEqual(1 + len(marketplace_plugin_selectors(CODEX_MARKETPLACE)), len(calls))

    def test_replace_marketplace_removes_existing_source_before_local_add(self) -> None:
        proc, calls = self.run_install_all_process(
            "--source",
            str(REPO_ROOT),
            "--include",
            "goalspec",
            "--replace-marketplace",
            fake_marketplaces={"codex": ["agent-tooling"], "claude": ["agent-tooling"]},
        )
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)

        self.assertEqual(
            [
                {"command": "codex", "args": ["plugin", "marketplace", "list", "--json"]},
                {"command": "codex", "args": ["plugin", "marketplace", "remove", "agent-tooling"]},
                {"command": "codex", "args": ["plugin", "marketplace", "add", str(REPO_ROOT)]},
                {"command": "codex", "args": ["plugin", "add", "goalspec@agent-tooling"]},
                {"command": "claude", "args": ["plugin", "marketplace", "list", "--json"]},
                {"command": "claude", "args": ["plugin", "marketplace", "remove", "--scope", "user", "agent-tooling"]},
                {"command": "claude", "args": ["plugin", "marketplace", "add", "--scope", "user", str(REPO_ROOT)]},
                {"command": "claude", "args": ["plugin", "install", "--scope", "user", "goalspec@agent-tooling"]},
                {"command": "claude", "args": ["plugin", "update", "--scope", "user", "goalspec@agent-tooling"]},
            ],
            calls,
        )

    def test_replace_marketplace_skips_removal_when_already_absent(self) -> None:
        proc, calls = self.run_install_all_process(
            "--source",
            str(REPO_ROOT),
            "--include",
            "goalspec",
            "--replace-marketplace",
        )

        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertFalse(
            any(call["args"][:3] == ["plugin", "marketplace", "remove"] for call in calls)
        )
        self.assertIn("already absent; skipping removal", proc.stderr)

    def test_rejects_invalid_claude_scope_before_cli_mutation(self) -> None:
        proc, calls = self.run_install_all_process("--claude-scope", "workspace")

        self.assertNotEqual(0, proc.returncode)
        self.assertIn("--claude-scope must be user, project, or local", proc.stderr)
        self.assertEqual([], calls)

    def test_claude_only_skips_codex(self) -> None:
        calls = self.run_install_all("--claude-only", "--include", "goalspec")

        self.assertFalse(any(call["command"] == "codex" for call in calls))
        self.assertEqual(
            [
                {
                    "command": "claude",
                    "args": ["plugin", "marketplace", "add", "--scope", "user", "DevGuyRash/agent-tooling", "--sparse", ".claude-plugin", "plugins"],
                },
                {
                    "command": "claude",
                    "args": ["plugin", "marketplace", "update", "agent-tooling"],
                },
                {
                    "command": "claude",
                    "args": ["plugin", "install", "--scope", "user", "goalspec@agent-tooling"],
                },
                {
                    "command": "claude",
                    "args": ["plugin", "update", "--scope", "user", "goalspec@agent-tooling"],
                },
            ],
            calls,
        )

    def test_exclude_accepts_csv_globs_and_removes_matching_plugins(self) -> None:
        calls = self.run_install_all("--exclude", "software-development")

        codex_installs = [call["args"][-1] for call in calls if call["command"] == "codex" and call["args"][:2] == ["plugin", "add"]]
        claude_installs = [call["args"][-1] for call in calls if call["command"] == "claude" and call["args"][:2] == ["plugin", "install"]]

        expected_codex = [
            selector
            for selector in marketplace_plugin_selectors(CODEX_MARKETPLACE)
            if selector != "software-development@agent-tooling"
        ]
        expected_claude = [
            selector
            for selector in marketplace_plugin_selectors(CLAUDE_MARKETPLACE)
            if selector != "software-development@agent-tooling"
        ]
        self.assertEqual(expected_codex, codex_installs)
        self.assertEqual(expected_claude, claude_installs)
        self.assertNotIn("software-development@agent-tooling", codex_installs)
        self.assertNotIn("software-development@agent-tooling", claude_installs)

    def test_include_and_exclude_are_repeatable_and_globbed(self) -> None:
        calls = self.run_install_all(
            "--include",
            "software-development",
            "--include",
            "goalspec",
            "--exclude",
            "software-development",
        )

        codex_installs = [call["args"][-1] for call in calls if call["command"] == "codex" and call["args"][:2] == ["plugin", "add"]]
        self.assertEqual(["goalspec@agent-tooling"], codex_installs)

    def test_unmatched_filter_fails_fast(self) -> None:
        proc, calls = self.run_install_all_process("--include", "missing-plugin")

        self.assertNotEqual(0, proc.returncode)
        self.assertIn("--include pattern(s) matched no Codex or Claude Code plugins: missing-plugin", proc.stderr)
        self.assertEqual([], calls)

    def test_synthetic_claude_only_plugin_skips_codex(self) -> None:
        proc, calls = self.run_install_all_with_catalogs(
            ["shared"],
            ["shared", "claude-only"],
            "--include",
            "claude-only",
        )

        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertFalse(any(call["command"] == "codex" for call in calls))
        self.assertEqual(
            [
                [
                    "plugin",
                    "marketplace",
                    "add",
                    "--scope",
                    "user",
                    "DevGuyRash/agent-tooling",
                    "--sparse",
                    ".claude-plugin",
                    "plugins",
                ],
                ["plugin", "marketplace", "update", "agent-tooling"],
                ["plugin", "install", "--scope", "user", "claude-only@agent-tooling"],
                ["plugin", "update", "--scope", "user", "claude-only@agent-tooling"],
            ],
            [call["args"] for call in calls],
        )

if __name__ == "__main__":
    unittest.main()
