from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "script_sanity.sh"

VERDICT_WORDS = ("BLOCKER", "MAJOR", "MINOR", "PASS", "FAIL")


def run_script_sanity(skill_dir: Path, *extra: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    completed = subprocess.run(
        ["sh", str(SCRIPT), str(skill_dir), "--format", "json", *extra],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed, json.loads(completed.stdout)


def write_script(path: Path, *, executable: bool = True, line_ending: str = "\n", content: str | None = None) -> None:
    if content is None:
        content = f"#!/usr/bin/env sh{line_ending}exit 0{line_ending}"
    path.write_bytes(content.encode("utf-8"))
    if executable:
        path.chmod(0o755)
    else:
        path.chmod(0o644)


class ErrorTests(unittest.TestCase):
    """not_executable, missing_shebang, crlf_in_executable, secret_pattern_file:
    each has no legitimate reading for any target, so each must fail the run."""

    def test_non_executable_launcher_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            scripts_dir = skill_dir / "scripts"
            skill_dir.mkdir()
            scripts_dir.mkdir()
            write_script(scripts_dir / "start.sh")
            write_script(scripts_dir / "repair.sh", executable=False)

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("not_executable", {e["code"] for e in data["errors"]})

    def test_executable_python_script_without_shebang_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            scripts_dir = skill_dir / "scripts"
            skill_dir.mkdir()
            scripts_dir.mkdir()
            script_path = scripts_dir / "helper.py"
            script_path.write_text("print('hi')\n", encoding="utf-8")
            script_path.chmod(0o755)

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("missing_shebang", {e["code"] for e in data["errors"]})

    def test_executable_shell_launcher_without_shebang_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            scripts_dir = skill_dir / "scripts"
            skill_dir.mkdir()
            scripts_dir.mkdir()
            script_path = scripts_dir / "start.sh"
            script_path.write_text("echo hi\n", encoding="utf-8")
            script_path.chmod(0o755)

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("missing_shebang", {e["code"] for e in data["errors"]})

    def test_crlf_in_executable_script_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            scripts_dir = skill_dir / "scripts"
            skill_dir.mkdir()
            scripts_dir.mkdir()
            write_script(scripts_dir / "start.sh", line_ending="\r\n")

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("crlf_in_executable", {e["code"] for e in data["errors"]})

    def test_env_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / ".env").write_text("SECRET_KEY=abc123\n", encoding="utf-8")

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("secret_pattern_file", {e["code"] for e in data["errors"]})

    def test_credentials_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "credentials.json").write_text('{"key": "value"}', encoding="utf-8")

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("secret_pattern_file", {e["code"] for e in data["errors"]})

    def test_a_target_with_an_error_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            scripts_dir = skill_dir / "scripts"
            skill_dir.mkdir()
            scripts_dir.mkdir()
            write_script(scripts_dir / "repair.sh", executable=False)

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertGreater(data["error_count"], 0)


class ObservationTests(unittest.TestCase):
    """crlf, script_no_trap: each fact's significance depends on the target, so
    each must be reported without failing the run."""

    def test_crlf_in_a_non_executable_file_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            refs_dir = skill_dir / "references"
            skill_dir.mkdir()
            refs_dir.mkdir()
            (refs_dir / "notes.md").write_bytes(b"line one\r\nline two\r\n")

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertEqual(codes, {"crlf"})

    def test_missing_trap_is_observed_when_the_script_makes_temp_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            scripts_dir = skill_dir / "scripts"
            skill_dir.mkdir()
            scripts_dir.mkdir()
            write_script(
                scripts_dir / "helper.sh",
                content='#!/usr/bin/env sh\nset -eu\nout=$(mktemp)\necho ok >"$out"\n',
            )

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertEqual(codes, {"script_no_trap"})

    def test_no_trap_observation_when_there_is_nothing_to_clean_up(self) -> None:
        # A script that creates no temporary file has nothing to remove, so
        # demanding a trap of it reports noise and trains the reader to skip
        # the observation that matters.
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            scripts_dir = skill_dir / "scripts"
            skill_dir.mkdir()
            scripts_dir.mkdir()
            write_script(scripts_dir / "helper.sh", content="#!/usr/bin/env sh\nset -eu\necho ok\n")

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertNotIn("script_no_trap", {o["code"] for o in data["observations"]})

    def test_script_with_trap_has_no_observation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            scripts_dir = skill_dir / "scripts"
            skill_dir.mkdir()
            scripts_dir.mkdir()
            write_script(
                scripts_dir / "helper.sh",
                content="#!/usr/bin/env sh\nset -eu\ntrap 'rm -f /tmp/x' EXIT\nout=$(mktemp)\necho ok >\"$out\"\n",
            )

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertNotIn("script_no_trap", {o["code"] for o in data["observations"]})


class CleanTargetTests(unittest.TestCase):
    def test_missing_scripts_directory_has_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertEqual(data["observation_count"], 0)
        self.assertEqual(data["script_count"], 0)

    def test_valid_script_surface_has_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            scripts_dir = skill_dir / "scripts"
            skill_dir.mkdir()
            scripts_dir.mkdir()
            for name in ("start.sh", "verify.sh", "helper.py"):
                write_script(scripts_dir / name)

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertEqual(data["observation_count"], 0)
        self.assertEqual(data["errors"], [])
        self.assertEqual(data["observations"], [])

    def test_executable_binary_without_extension_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            scripts_dir = skill_dir / "scripts"
            skill_dir.mkdir()
            scripts_dir.mkdir()
            binary_path = scripts_dir / "tool"
            binary_path.write_bytes(b"\x7fELF\x02\x01\x01\x00binary payload")
            binary_path.chmod(0o755)

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertEqual(data["observation_count"], 0)

    def test_active_skill_passes(self) -> None:
        completed, data = run_script_sanity(ROOT)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)


class ObservationsOnlyExitTests(unittest.TestCase):
    def test_a_target_whose_only_findings_are_observations_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            scripts_dir = skill_dir / "scripts"
            skill_dir.mkdir()
            scripts_dir.mkdir()
            write_script(
                scripts_dir / "helper.sh",
                content='#!/usr/bin/env sh\nset -eu\nout=$(mktemp)\necho ok >"$out"\n',
            )

            completed, data = run_script_sanity(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertGreater(data["observation_count"], 0)


class SourceTagTests(unittest.TestCase):
    def test_every_observation_source_is_open_standard_or_repo_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            refs_dir = skill_dir / "references"
            scripts_dir = skill_dir / "scripts"
            skill_dir.mkdir()
            refs_dir.mkdir()
            scripts_dir.mkdir()
            (refs_dir / "notes.md").write_bytes(b"line one\r\nline two\r\n")
            write_script(
                scripts_dir / "helper.sh",
                content='#!/usr/bin/env sh\nset -eu\nout=$(mktemp)\necho ok >"$out"\n',
            )

            completed, data = run_script_sanity(skill_dir)

        self.assertGreater(data["observation_count"], 0)
        for obs in data["observations"]:
            if "source" in obs:
                self.assertIn(obs["source"], {"open-standard", "repo-overlay"})


class VerdictVocabularyTests(unittest.TestCase):
    def test_no_severity_or_verdict_words_appear(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            observation_dir = Path(tmp) / "demo-skill"
            refs_dir = observation_dir / "references"
            observation_dir.mkdir()
            refs_dir.mkdir()
            (refs_dir / "notes.md").write_bytes(b"line one\r\nline two\r\n")

            error_dir = Path(tmp) / "broken-skill"
            error_scripts_dir = error_dir / "scripts"
            error_dir.mkdir()
            error_scripts_dir.mkdir()
            write_script(error_scripts_dir / "repair.sh", executable=False)

            runs = [
                subprocess.run(
                    ["sh", str(SCRIPT), str(d), "--format", fmt],
                    capture_output=True, text=True, check=False,
                )
                for d in (observation_dir, error_dir)
                for fmt in ("json", "text")
            ]

        for completed in runs:
            for word in VERDICT_WORDS:
                self.assertNotIn(word, completed.stdout)
                self.assertNotIn(word, completed.stderr)


class UsageExitTests(unittest.TestCase):
    def test_unusable_input_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()

            bad_flag = subprocess.run(
                ["sh", str(SCRIPT), str(skill_dir), "--nope"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(bad_flag.returncode, 2)

            bad_format = subprocess.run(
                ["sh", str(SCRIPT), str(skill_dir), "--format", "xml"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(bad_format.returncode, 2)
            self.assertIn("hint:", bad_format.stderr)

        missing_dir = subprocess.run(
            ["sh", str(SCRIPT), "/tmp/definitely-not-a-real-skill-dir-xyz"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(missing_dir.returncode, 2)


class TaxonomySortTests(unittest.TestCase):
    """The governing rule: an error has no legitimate reading for any target; an
    observation's significance depends on the target. This pins the script's
    error/observation sort exactly, so a code silently moved between buckets --
    or a new one added to neither list -- fails here."""

    @staticmethod
    def _codes(function_name: str) -> set[str]:
        text = SCRIPT.read_text(encoding="utf-8")
        return set(re.findall(rf'\b{function_name}\s+"([a-z0-9_]+)"', text))

    def test_error_codes_match_the_governing_sort(self) -> None:
        self.assertEqual(
            self._codes("error"),
            {"not_executable", "missing_shebang", "crlf_in_executable", "secret_pattern_file"},
        )

    def test_observation_codes_match_the_governing_sort(self) -> None:
        self.assertEqual(self._codes("observe"), {"crlf", "script_no_trap"})


if __name__ == "__main__":
    unittest.main()
