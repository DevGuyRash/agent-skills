from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "references" / "comparative-handoff.md"
REQUEST_FIELDS = {
    "schema",
    "claim_id",
    "target_ref",
    "authority_ref",
    "claim",
    "decision_context",
    "existing_evidence_refs",
    "closure_conditions",
    "unresolved_consequence",
    "prohibited_effects",
    "extensions",
}
RESULT_FIELDS = {
    "schema",
    "claim_id",
    "request_digest",
    "tested_conditions",
    "conclusion",
    "closure_assessment",
    "evidence_refs",
    "scope_and_limits",
    "uncertainty",
    "reopening_conditions",
    "extensions",
}


def section(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading) + len(heading)
    end = text.index(next_heading, start)
    return text[start:end]


def bullet_fields(text: str) -> set[str]:
    return set(re.findall(r"^- `([a-z_]+)`:", text, flags=re.MULTILINE))


class ComparativeHandoffTests(unittest.TestCase):
    def test_request_and_result_interfaces_have_only_the_adopted_required_fields(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        request = section(text, "## Request interface\n", "## Result interface\n")
        result = text[text.index("## Result interface\n") :]
        self.assertEqual(bullet_fields(request), REQUEST_FIELDS)
        self.assertEqual(bullet_fields(result), RESULT_FIELDS)
        self.assertIn("comparative-evidence-request.v1", request)
        self.assertIn("comparative-evidence-result.v1", result)

    def test_digest_contract_binds_exact_bytes_not_parsed_json(self) -> None:
        compact = b'{"schema":"comparative-evidence-request.v1","claim_id":"claim-7","future":1}\n'
        reformatted = b'{\n  "schema": "comparative-evidence-request.v1",\n  "claim_id": "claim-7",\n  "future": 1\n}\n'
        self.assertNotEqual(hashlib.sha256(compact).digest(), hashlib.sha256(reformatted).digest())
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("exact frozen UTF-8 request bytes", text)
        self.assertIn("not parsed or reformatted JSON", text)

    def test_interface_is_open_without_prescribing_comparison_design(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("preserve unknown fields", text)
        self.assertIn("arbitrary additional fields", text)
        self.assertIn("not a closed result enum", text)
        self.assertIn("SHALL NOT prescribe observations, cases, graders, scores, topology", text)
        self.assertIn("is not a design prescription", text)
        self.assertIn("real consumer or deployment boundary", text)
        for status in ("closes", "narrows", "does_not_resolve"):
            self.assertRegex(text, rf"`{status}`")

    def test_closure_identifiers_are_unique_and_covered_exactly_once(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("stable ID that is unique within the request", text)
        self.assertIn("exactly one entry for every request closure-condition ID", text)
        self.assertIn("no unrequested IDs", text)
        self.assertIn("split-test exchange verify REQUEST.json RESULT.json", text)
        self.assertIn("JSON Schema alone cannot establish", text)

    def test_unavailable_paths_do_not_recreate_a_local_comparison(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("MAY assess already-existing evidence", text)
        self.assertIn("SHALL NOT design or run a replacement comparison", text)
        self.assertIn("emit the request envelope", text)
        self.assertIn("state the unresolved consequence", text)
        self.assertIn("Skill Auditor retains rightful authority interpretation", text)


if __name__ == "__main__":
    unittest.main()
