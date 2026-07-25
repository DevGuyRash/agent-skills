from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
OUTPUT_CONTRACT = ROOT / "references" / "output-contract.md"


def extract_template(text: str) -> str:
    marker = "```markdown\n"
    start = text.index(marker) + len(marker)
    end = text.index("\n```", start)
    return text[start:end]


class OutputContractTests(unittest.TestCase):
    def test_template_contains_required_sections_in_order(self) -> None:
        template = extract_template(OUTPUT_CONTRACT.read_text(encoding="utf-8"))
        positions = []

        for section in json.loads((FIXTURES / "output_sections.json").read_text(encoding="utf-8")):
            index = template.find(section)
            self.assertNotEqual(index, -1, section)
            positions.append(index)

        self.assertEqual(sorted(positions), positions)

    def test_contract_lists_all_packaging_verdicts(self) -> None:
        content = OUTPUT_CONTRACT.read_text(encoding="utf-8")

        for verdict in (
            "KEEP_AS_SKILL",
            "REWORK_AS_SKILL",
            "MIGRATE_TO_AGENTS",
            "MIGRATE_TO_HOOK",
            "MIGRATE_TO_SUBAGENT",
            "MIGRATE_TO_COMMAND",
            "MIGRATE_TO_EXPLICIT_PROMPT",
            "MIGRATE_TO_TOOL",
            "MIGRATE_TO_MCP",
            "HYBRID_RECOMMENDED",
        ):
            with self.subTest(verdict=verdict):
                self.assertIn(verdict, content)

    def test_contract_disallows_old_default_shape(self) -> None:
        content = OUTPUT_CONTRACT.read_text(encoding="utf-8").lower()

        self.assertIn("large taxonomy table", content)
        self.assertIn("long audit dissertation", content)
        self.assertIn("script dump", content)

    def test_contract_requires_concrete_evidence_anchors(self) -> None:
        content = OUTPUT_CONTRACT.read_text(encoding="utf-8")

        self.assertIn("at least one observed prompt, output, or file anchor", content)
        self.assertIn("## Key evidence", content)

    def test_contract_separates_plugin_scope_from_skill_scope(self) -> None:
        content = OUTPUT_CONTRACT.read_text(encoding="utf-8")

        self.assertIn("## Plugin-level findings", content)
        self.assertIn("## Scope", content)

    def test_contract_allows_a_clean_result(self) -> None:
        content = OUTPUT_CONTRACT.read_text(encoding="utf-8").lower()

        self.assertIn("clean brief", content)
        self.assertIn("manufacturing a finding", content)


if __name__ == "__main__":
    unittest.main()
