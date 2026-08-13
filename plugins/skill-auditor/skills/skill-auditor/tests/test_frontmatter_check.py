from __future__ import annotations

import json
import re
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "frontmatter_check.sh"

VERDICT_WORDS = ("BLOCKER", "MAJOR", "MINOR", "PASS", "FAIL")


def run_frontmatter_check(skill_dir: Path, *extra: str) -> tuple[subprocess.CompletedProcess[str], dict]:
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
    description: str = "Check demo skills and explain findings for maintainers updating metadata and packaging boundaries.",
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
    """frontmatter_missing, name_missing, description_missing, description_empty:
    each has no legitimate reading for any target, so each must fail the run."""

    def test_missing_frontmatter_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Demo Skill\nno frontmatter here.\n", encoding="utf-8")

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(data["error_count"], 1)
        self.assertIn("frontmatter_missing", {e["code"] for e in data["errors"]})

    def test_missing_name_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\ndescription: Review demo skills and explain findings for maintainers.\n---\n",
                encoding="utf-8",
            )

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("name_missing", {e["code"] for e in data["errors"]})

    def test_missing_description_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("---\nname: Demo Skill\n---\n", encoding="utf-8")

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("description_missing", {e["code"] for e in data["errors"]})

    def test_empty_description_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: Demo Skill\ndescription:\n---\n", encoding="utf-8"
            )

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("description_empty", {e["code"] for e in data["errors"]})

    def test_a_target_with_an_error_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("---\nname: Demo Skill\n---\n", encoding="utf-8")

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertGreater(data["error_count"], 0)


class ParsingTests(unittest.TestCase):
    """extract_description must fold every YAML block-scalar style the repo
    uses, or a well-formed description would misreport as missing."""

    def test_inline_description_is_read_correctly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    name: Demo Skill
                    description: Review demo skills for maintainers updating metadata and instructions.
                    ---
                    """
                ),
                encoding="utf-8",
            )

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)

    def test_keep_chomp_block_scalar_is_read_correctly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    name: Demo Skill
                    description: >+
                      Check a demo skill and explain what it does. Use when
                      reviewing demo skills.
                    ---
                    """
                ),
                encoding="utf-8",
            )

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)

    def test_one_space_indented_block_is_read_correctly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    name: Demo Skill
                    description: >-
                     Check a demo skill and explain what it does. Use when
                     reviewing demo skills.
                    ---
                    """
                ),
                encoding="utf-8",
            )

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)


class ObservationTests(unittest.TestCase):
    """Each fact's significance depends on the target, so each must be reported
    without failing the run."""

    def test_bad_directory_slug_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(tmp, slug="Bad--Slug", name="Bad Slug", body="\n# Bad Slug\n")

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertEqual(codes, {"slug_format", "slug_double_hyphen"})

    def test_long_slug_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            long_slug = "demo-skill-" + "x" * 60
            skill_dir = make_skill(tmp, slug=long_slug)

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertIn("slug_length", {o["code"] for o in data["observations"]})

    def test_lowercase_name_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(tmp, name="demo skill", body="\n# demo skill\n")

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertIn("name_not_title_case", codes)
        self.assertIn("name_slug_mismatch", codes)

    def test_name_slug_mismatch_is_observed_alone(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(tmp, name="Wrong Name", body="\n# Wrong Name\n")

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertEqual(codes, {"name_slug_mismatch"})

    def test_h1_mismatch_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(tmp, body="\n# Wrong Heading\n")

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertEqual(codes, {"h1_name_mismatch"})

    def test_matching_h1_has_no_mismatch_observation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(tmp, body="\n# Demo Skill\n")

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertNotIn("h1_name_mismatch", {o["code"] for o in data["observations"]})

    def test_long_description_is_observed(self) -> None:
        filler = "This sentence pads the description with extra harmless words. " * 20
        description = filler + "Use when the task involves: (1) Auditing demo skills, (2) Reviewing demo packaging."
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(tmp, description=description)

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertGreater(data["description_chars"], 1024)
        codes = {o["code"] for o in data["observations"]}
        self.assertEqual(codes, {"description_length"})

    def test_simple_description_has_no_trigger_list_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp, description="A simple skill that does things for people every day."
            )

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertNotIn("description_no_trigger_list", {o["code"] for o in data["observations"]})

    def test_slug_frontmatter_with_title_cased_h1_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                name="demo-skill",
                body="\n# Demo Skill\n",
            )

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertEqual(data["observations"], [])


class DeletedHeuristicRegressionTests(unittest.TestCase):
    """description_too_vague, description_brief, and description_trigger_weak
    were word-count and prefix guesses wearing an exit code, deleted on purpose.
    A fixture built to trip them must never resurrect them."""

    DELETED_CODES = {"description_too_vague", "description_brief", "description_trigger_weak"}

    def test_short_description_triggers_none_of_the_deleted_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(tmp, description="Does one thing.")

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertEqual(codes & self.DELETED_CODES, set())

    def test_helps_with_prefix_triggers_none_of_the_deleted_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp, description="Helps with demo skills and related maintenance tasks for users."
            )

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        codes = {o["code"] for o in data["observations"]}
        self.assertEqual(codes & self.DELETED_CODES, set())


class CleanTargetTests(unittest.TestCase):
    def test_fully_clean_skill_has_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(tmp)

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertEqual(data["observation_count"], 0)
        self.assertEqual(data["errors"], [])
        self.assertEqual(data["observations"], [])

    def test_active_skill_passes(self) -> None:
        completed, data = run_frontmatter_check(ROOT)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)


class ObservationsOnlyExitTests(unittest.TestCase):
    def test_a_target_whose_only_findings_are_observations_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(tmp, slug="Bad--Slug", name="Bad Slug", body="\n# Bad Slug\n")

            completed, data = run_frontmatter_check(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertGreater(data["observation_count"], 0)


class SourceTagTests(unittest.TestCase):
    def test_every_observation_source_is_open_standard_or_repo_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(tmp, slug="Bad--Slug", name="Bad Slug", body="\n# Bad Slug\n")

            completed, data = run_frontmatter_check(skill_dir)

        self.assertGreater(data["observation_count"], 0)
        for obs in data["observations"]:
            if "source" in obs:
                self.assertIn(obs["source"], {"open-standard", "repo-overlay"})


class VerdictVocabularyTests(unittest.TestCase):
    def test_no_severity_or_verdict_words_appear(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            observation_dir = make_skill(tmp, name="demo skill", body="\n# Wrong Heading\n")
            error_dir = Path(tmp) / "broken-skill"
            error_dir.mkdir()
            (error_dir / "SKILL.md").write_text("---\nname: Demo Skill\n---\n", encoding="utf-8")

            runs = [
                subprocess.run(
                    ["sh", str(SCRIPT), str(observation_dir), "--format", fmt],
                    capture_output=True, text=True, check=False,
                )
                for fmt in ("json", "text")
            ] + [
                subprocess.run(
                    ["sh", str(SCRIPT), str(error_dir), "--format", fmt],
                    capture_output=True, text=True, check=False,
                )
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
        self.assertEqual(
            self._codes("error"),
            {"frontmatter_missing", "name_missing", "description_missing", "description_empty"},
        )

    def test_observation_codes_match_the_governing_sort(self) -> None:
        self.assertEqual(
            self._codes("observe"),
            {
                "slug_format",
                "slug_double_hyphen",
                "slug_length",
                "name_not_title_case",
                "name_slug_mismatch",
                "h1_name_mismatch",
                "description_length",
            },
        )


if __name__ == "__main__":
    unittest.main()
