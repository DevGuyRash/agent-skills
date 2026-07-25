from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = ROOT / "SKILL.md"
FIXTURES = ROOT / "tests" / "fixtures"
SKILLS_FILE_ROOT = "<skills-file-root>/"


def load_json(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    cleaned = text.lower().replace("`", "")
    return re.sub(r"\s+", " ", cleaned).strip()


class PlanningBehaviorTests(unittest.TestCase):
    def test_description_uses_realistic_trigger_language(self) -> None:
        skill_text = SKILL_MD.read_text(encoding="utf-8")
        description_match = re.search(r"^description:\s*>-\n((?:\s{2}.+\n)+)", skill_text, flags=re.MULTILINE)
        assert description_match is not None, "SKILL.md has no folded description block"
        description = normalize(description_match.group(1))
        prompt_terms = load_json("trigger_prompts.json")

        for term in prompt_terms["positive_terms"]:
            with self.subTest(term=term):
                self.assertIn(normalize(term), description)

        for term in prompt_terms["negative_terms"]:
            with self.subTest(term=term):
                self.assertNotIn(normalize(term), description)

    def test_question_router_maps_fixture_cases(self) -> None:
        content = SKILL_MD.read_text(encoding="utf-8")
        mappings = {
            question.strip(): path.strip()
            for question, path in re.findall(
                r"^\| ([A-Za-z ]+?) \| [^|]+ \| `([^`]+)` \|$",
                content,
                flags=re.MULTILINE,
            )
        }

        for case in load_json("planning_cases.json"):
            with self.subTest(case=case["question"]):
                linked = mappings[case["question"]]
                self.assertTrue(
                    linked.startswith(SKILLS_FILE_ROOT),
                    f"router link bypasses {SKILLS_FILE_ROOT}: {linked}",
                )
                self.assertEqual(linked[len(SKILLS_FILE_ROOT):], case["reference"])

                reference_text = (ROOT / case["reference"]).read_text(encoding="utf-8").lower()
                for term in case["terms"]:
                    self.assertIn(term.lower(), reference_text)

    def test_open_standard_covers_fixture_profiles(self) -> None:
        open_standard = normalize((ROOT / "references" / "open-standard.md").read_text(encoding="utf-8"))

        for case in load_json("profile_cases.json"):
            with self.subTest(profile=case["profile"]):
                self.assertIn(case["profile"], open_standard)
                self.assertIn(normalize(case["cue"]), open_standard)

    def test_skill_states_its_contract_in_order(self) -> None:
        normalized = normalize(SKILL_MD.read_text(encoding="utf-8"))
        positions = []

        for claim in load_json("work_order_steps.json"):
            index = normalized.find(normalize(claim))
            self.assertNotEqual(index, -1, claim)
            positions.append(index)

        self.assertEqual(sorted(positions), positions)
        self.assertLessEqual(len(SKILL_MD.read_text(encoding="utf-8").splitlines()), 220)

    def test_leverage_order_covers_every_question(self) -> None:
        normalized = normalize(SKILL_MD.read_text(encoding="utf-8"))

        self.assertIn(
            "frame, packaging, trigger, task, context, verification, instruction design",
            normalized,
        )

        for question in (case["question"] for case in load_json("planning_cases.json")):
            with self.subTest(question=question):
                self.assertIn(normalize(question), normalized)

    def test_active_skill_drops_router_cli_and_domain_taxonomy(self) -> None:
        content = SKILL_MD.read_text(encoding="utf-8")

        self.assertNotIn("audit-skill", content)
        self.assertNotIn("25 domains", content.lower())
        self.assertIsNone(re.search(r"\bD\d+\b", content))

    def test_loop_bounds_reading_and_names_a_stop(self) -> None:
        normalized = normalize(SKILL_MD.read_text(encoding="utf-8"))

        self.assertIn(
            normalize(
                "You SHALL read at most one question reference before drafting the first brief."
            ),
            normalized,
        )
        self.assertIn(
            normalize(
                "WHEN the packaging verdict is neither `KEEP_AS_SKILL` nor `REWORK_AS_SKILL` "
                "THEN you SHALL stop optimizing the target as a standalone skill"
            ),
            normalized,
        )
        self.assertIn(
            normalize("WHEN the leading bottleneck and its next check are clear THEN you SHALL stop."),
            normalized,
        )

    def test_scope_routing_covers_plugin_and_bare_skill(self) -> None:
        normalized = normalize(SKILL_MD.read_text(encoding="utf-8"))

        self.assertIn("if the target contains a plugin manifest", normalized)
        self.assertIn("else you shall audit the single skill", normalized)

    def test_scripts_are_mechanism_not_policy(self) -> None:
        normalized = normalize(SKILL_MD.read_text(encoding="utf-8"))

        self.assertIn("the scripts supply mechanism", normalized)
        self.assertIn(
            "you shall not treat a script's output as a verdict you owe deference to",
            normalized,
        )

    def test_every_reference_is_reachable_from_skill_md(self) -> None:
        content = SKILL_MD.read_text(encoding="utf-8")
        linked = {
            path[len(SKILLS_FILE_ROOT):] if path.startswith(SKILLS_FILE_ROOT) else path
            for path in re.findall(r"`((?:<skills-file-root>/)?references/[^`]+\.md)`", content)
        }
        on_disk = {f"references/{p.name}" for p in (ROOT / "references").glob("*.md")}

        self.assertEqual(on_disk - linked, set(), "unlinked reference files")


if __name__ == "__main__":
    unittest.main()
