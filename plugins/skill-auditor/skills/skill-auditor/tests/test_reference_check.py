from __future__ import annotations

import json
import re
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "reference_check.sh"

VERDICT_WORDS = ("BLOCKER", "MAJOR", "MINOR", "PASS", "FAIL")


def run_reference_check(skill_dir: Path, *extra: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    completed = subprocess.run(
        ["sh", str(SCRIPT), str(skill_dir), "--format", "json", *extra],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed, json.loads(completed.stdout)


def make_skill(
    tmp: str,
    *,
    slug: str = "demo-skill",
    name: str = "Demo Skill",
    description: str = "Check demo skills and explain findings. Use when the task involves: (1) Auditing demo skills, (2) Reviewing demo packaging.",
    body: str = "\n# Demo Skill\n",
    scripts: dict[str, str] | None = None,
    extra_files: dict[str, str] | None = None,
    references: dict[str, str] | None = None,
) -> Path:
    skill_dir = Path(tmp) / slug
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_md = f"---\nname: {name}\ndescription: >-\n  {description}\n---\n{body}"
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    if scripts:
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        for fname, content in scripts.items():
            script_file = scripts_dir / fname
            script_file.write_text(content, encoding="utf-8")
            if fname.endswith(".sh"):
                script_file.chmod(script_file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    if references:
        ref_dir = skill_dir / "references"
        ref_dir.mkdir(exist_ok=True)
        for fname, content in references.items():
            (ref_dir / fname).write_text(content, encoding="utf-8")

    if extra_files:
        for fpath, content in extra_files.items():
            full = skill_dir / fpath
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")

    return skill_dir


class ErrorTests(unittest.TestCase):
    """missing_reference_file: a link with no file behind it is broken for every
    target, so it must fail the run."""

    def test_missing_reference_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp, body="\n- Packaging fit -> `<skills-file-root>/references/nope.md`\n"
            )

            completed, data = run_reference_check(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(data["error_count"], 1)
        self.assertIn("missing_reference_file", {e["code"] for e in data["errors"]})

    def test_a_target_with_an_error_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp, body="\n- Packaging fit -> `<skills-file-root>/references/nope.md`\n"
            )

            completed, data = run_reference_check(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertGreater(data["error_count"], 0)


class ObservationTests(unittest.TestCase):
    """Each fact's significance depends on the target, so each must be reported
    without failing the run."""

    def test_bare_reference_path_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                references={"packaging-fit.md": "# Packaging\n"},
                body="\n- Packaging fit -> `references/packaging-fit.md`\n",
            )

            completed, data = run_reference_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertEqual(codes, {"bare_reference_path"})

    def test_prefixed_reference_path_has_no_bare_path_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                references={"packaging-fit.md": "# Packaging\n"},
                body="\n- Packaging fit -> `<skills-file-root>/references/packaging-fit.md`\n",
            )

            completed, data = run_reference_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertNotIn("bare_reference_path", {o["code"] for o in data["observations"]})

    def test_flags_unlinked_active_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                references={
                    "packaging-fit.md": "# Packaging\n",
                    "trigger-evals.md": "# Trigger\n",
                },
                body="\n- Packaging fit -> `<skills-file-root>/references/packaging-fit.md`\n",
            )

            completed, data = run_reference_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertEqual(codes, {"unlinked_reference"})
        subjects = {o["subject"] for o in data["observations"]}
        self.assertIn("references/trigger-evals.md", subjects)

    def test_recurses_into_nested_reference_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                references={"packaging-fit.md": "# Packaging\n"},
                body="\n- Packaging fit -> `<skills-file-root>/references/packaging-fit.md`\n",
            )
            nested_dir = skill_dir / "references" / "aws"
            nested_dir.mkdir(parents=True)
            (nested_dir / "setup.md").write_text("# Setup\n", encoding="utf-8")

            completed, data = run_reference_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertIn("unlinked_reference", codes)
        subjects = {o["subject"] for o in data["observations"]}
        self.assertIn("references/aws/setup.md", subjects)

    def test_flags_nested_reference_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                references={
                    "packaging-fit.md": "See references/trigger-evals.md for more.\n",
                    "trigger-evals.md": "# Trigger\n",
                },
                body=(
                    "\n- Packaging fit -> `<skills-file-root>/references/packaging-fit.md`\n"
                    "- Trigger fit -> `<skills-file-root>/references/trigger-evals.md`\n"
                ),
            )

            completed, data = run_reference_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertEqual(codes, {"nested_reference_link"})

    def test_reference_over_300_lines_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            long_ref = "\n".join(f"Line {i}" for i in range(310))
            skill_dir = make_skill(
                tmp,
                references={"big-ref.md": long_ref},
                body="\n- Big ref -> `<skills-file-root>/references/big-ref.md`\n",
            )

            completed, data = run_reference_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertIn("reference_too_long", codes)


class HardWrapTests(unittest.TestCase):
    def test_results_are_identical_whether_or_not_clauses_are_hard_wrapped(self) -> None:
        long_line_body = (
            "\n- Packaging fit, covering manifest shape, capability declarations, and marketplace "
            "metadata for reviewers auditing plugin boundaries in depth -> "
            "`<skills-file-root>/references/packaging-fit.md`\n"
        )
        wrapped_body = (
            "\n- Packaging fit, covering manifest shape, capability declarations, and\n"
            "  marketplace metadata for reviewers auditing plugin boundaries in depth ->\n"
            "  `<skills-file-root>/references/packaging-fit.md`\n"
        )

        results = []
        for body in (long_line_body, wrapped_body):
            with tempfile.TemporaryDirectory() as tmp:
                skill_dir = make_skill(
                    tmp, references={"packaging-fit.md": "# Packaging\n"}, body=body
                )
                completed, data = run_reference_check(skill_dir)
                self.assertEqual(completed.returncode, 0)
                results.append(
                    (
                        data["linked_references"],
                        data["active_references"],
                        data["error_count"],
                        data["observation_count"],
                        sorted(e["code"] for e in data["errors"]),
                        sorted(o["code"] for o in data["observations"]),
                    )
                )

        self.assertEqual(results[0], results[1])


class CleanTargetTests(unittest.TestCase):
    def test_fully_clean_skill_has_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                references={"packaging-fit.md": "# Packaging\n"},
                body="\n- Packaging fit -> `<skills-file-root>/references/packaging-fit.md`\n",
            )

            completed, data = run_reference_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertEqual(data["observation_count"], 0)
        self.assertEqual(data["errors"], [])
        self.assertEqual(data["observations"], [])

    def test_active_skill_passes(self) -> None:
        completed, data = run_reference_check(ROOT)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)


class ObservationsOnlyExitTests(unittest.TestCase):
    def test_a_target_whose_only_findings_are_observations_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                references={
                    "packaging-fit.md": "# Packaging\n",
                    "trigger-evals.md": "# Trigger\n",
                },
                body="\n- Packaging fit -> `references/packaging-fit.md`\n",
            )

            completed, data = run_reference_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertGreater(data["observation_count"], 0)


class SourceTagTests(unittest.TestCase):
    def test_every_observation_source_is_open_standard_or_repo_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                references={
                    "packaging-fit.md": "# Packaging\n",
                    "trigger-evals.md": "# Trigger\n",
                },
                body="\n- Packaging fit -> `references/packaging-fit.md`\n",
            )

            completed, data = run_reference_check(skill_dir)

        self.assertGreater(data["observation_count"], 0)
        for obs in data["observations"]:
            if "source" in obs:
                self.assertIn(obs["source"], {"open-standard", "repo-overlay"})


class VerdictVocabularyTests(unittest.TestCase):
    def test_no_severity_or_verdict_words_appear(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            observation_dir = make_skill(
                tmp,
                references={"packaging-fit.md": "# Packaging\n"},
                body="\n- Packaging fit -> `references/packaging-fit.md`\n",
            )
            error_dir = make_skill(
                tmp,
                slug="broken-skill",
                body="\n- Packaging fit -> `<skills-file-root>/references/nope.md`\n",
            )

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
            skill_dir = make_skill(tmp)

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

            empty_dir = Path(tmp) / "empty-dir"
            empty_dir.mkdir()
            missing_skill_md = subprocess.run(
                ["sh", str(SCRIPT), str(empty_dir)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(missing_skill_md.returncode, 2)

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
        self.assertEqual(self._codes("error"), {"missing_reference_file"})

    def test_observation_codes_match_the_governing_sort(self) -> None:
        self.assertEqual(
            self._codes("observe"),
            {"bare_reference_path", "unlinked_reference", "nested_reference_link", "reference_too_long"},
        )


if __name__ == "__main__":
    unittest.main()
