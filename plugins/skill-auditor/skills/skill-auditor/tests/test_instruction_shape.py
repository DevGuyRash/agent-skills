from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "instruction_shape.sh"


def run_shape(skill_dir: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    completed = subprocess.run(
        ["sh", str(SCRIPT), str(skill_dir), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed, json.loads(completed.stdout)


def make_skill(tmp: str, body: str, *, slug: str = "demo-skill") -> Path:
    skill_dir = Path(tmp) / slug
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: Demo Skill\ndescription: >-\n  A demo.\n---\n" + body,
        encoding="utf-8",
    )
    return skill_dir


class ReportsRatherThanJudgesTests(unittest.TestCase):
    """The script supplies mechanism. Policy belongs to the auditor, so an
    observation must never become an exit status the caller has to obey."""

    def test_a_document_violating_every_convention_still_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                "# Demo Skill\n\nThe executor shall do the thing.\n"
                "The executor SHALL also do the other thing.\n",
            )
            completed, data = run_shape(skill_dir)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["second_person_refs"], 0)
        self.assertEqual(data["third_person_binds"], 2)
        self.assertEqual(data["modal_case"], "mixed")
        self.assertNotIn("if_without_else", data)
        self.assertNotIn("sections_out_of_order", data)
        self.assertNotIn("separate_examples_section", data)
        self.assertNotIn("ok", data)
        self.assertNotIn("issues", data)

    def test_unusable_input_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = subprocess.run(
                ["sh", str(SCRIPT), str(Path(tmp) / "nope")],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(missing.returncode, 2)

        bad_flag = subprocess.run(
            ["sh", str(SCRIPT), str(ROOT), "--nope"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(bad_flag.returncode, 2)

        bad_format = subprocess.run(
            ["sh", str(SCRIPT), str(ROOT), "--format", "xml"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(bad_format.returncode, 2)
        self.assertIn("hint:", bad_format.stderr)


class ObservationTests(unittest.TestCase):
    def test_wrapped_clauses_are_not_reported_as_duplicates(self) -> None:
        # Documents here wrap near 100 columns. A line-oriented match would
        # truncate both clauses at "stop" and call them identical.
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                "# Demo Skill\n\nyou own this.\n\n"
                "WHEN the verdict is final THEN you SHALL stop\n"
                "optimizing the target and return guidance.\n\n"
                "WHEN the bottleneck is clear THEN you SHALL stop.\n",
            )
            _, data = run_shape(skill_dir)

        self.assertEqual(data["duplicate_branch_outcomes"], 0)

    def test_identical_branch_outcomes_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                "# Demo Skill\n\nyou own this.\n\n"
                "WHEN a happens THEN you SHALL stop the run.\n\n"
                "WHEN b happens THEN you SHALL stop the run.\n",
            )
            _, data = run_shape(skill_dir)

        self.assertEqual(data["duplicate_branch_outcomes"], 1)

    def test_function_headings_are_reported_without_order_judgment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                "# Demo Skill\n\nyou own this. You are done when it holds.\n"
                "## Binding Language\nx\n"
                "## Output Contract\ny\n"
                "## State and Environment\nz\n"
                "## Mission\nw\n",
            )
            _, data = run_shape(skill_dir)

        self.assertEqual(
            data["function_headings_present"],
            "Mission,Environment,State,Output Contract,Binding Language",
        )
        self.assertNotIn("sections_present", data)
        self.assertNotIn("sections_out_of_order", data)
        self.assertEqual(data["done_condition"], "yes")

    def test_function_headings_may_be_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                "# Demo Skill\n\nyou own this.\n## Operating Notes\nx\n",
            )
            _, data = run_shape(skill_dir)

        self.assertEqual(data["function_headings_present"], "none")

    def test_frontmatter_is_excluded_from_the_body(self) -> None:
        # "description" in frontmatter must not be mistaken for prose.
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(tmp, "# Demo Skill\n\nnothing here.\n")
            _, data = run_shape(skill_dir)

        self.assertEqual(data["second_person_refs"], 0)
        self.assertEqual(data["heading_count"], 0)


class SelfReferenceTests(unittest.TestCase):
    def test_naming_the_notation_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                tmp,
                "# Demo Skill\n\nyou own this.\n\n"
                "These instructions follow the Governing Architecture.\n",
            )
            _, data = run_shape(skill_dir)

        self.assertEqual(data["notation_self_reference"], "yes")

    def test_a_clean_document_reports_no_self_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(tmp, "# Demo Skill\n\nyou own this.\n")
            _, data = run_shape(skill_dir)

        self.assertEqual(data["notation_self_reference"], "no")


class SelfAuditTests(unittest.TestCase):
    def test_this_skill_satisfies_the_doctrine_it_enforces(self) -> None:
        _, data = run_shape(ROOT)

        self.assertGreater(data["second_person_refs"], 0)
        self.assertEqual(data["third_person_binds"], 0)
        self.assertEqual(data["modal_case"], "consistent")
        self.assertEqual(data["duplicate_branch_outcomes"], 0)
        self.assertEqual(data["done_condition"], "yes")
        self.assertEqual(data["notation_self_reference"], "no")
        self.assertNotIn("if_without_else", data)
        self.assertNotIn("sections_present", data)
        self.assertNotIn("sections_out_of_order", data)
        self.assertNotIn("separate_examples_section", data)


if __name__ == "__main__":
    unittest.main()
