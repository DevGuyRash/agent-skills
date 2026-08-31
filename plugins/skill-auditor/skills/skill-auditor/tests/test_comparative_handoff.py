from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "references" / "comparative-handoff.md"


class ComparativeHandoffTests(unittest.TestCase):
    def test_delegation_uses_ordinary_context_without_an_exchange_schema(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("$split-testing", text)
        self.assertIn("ordinary context", text)
        for needed in (
            "claim",
            "authority",
            "existing evidence",
            "constraints",
            "consequence",
        ):
            self.assertIn(needed, text.lower())
        for rejected in (
            "comparative-evidence-request.v1",
            "comparative-evidence-result.v1",
            "request_digest",
            "closure_assessment",
            "JSON",
            "envelope",
            "schema",
        ):
            self.assertNotIn(rejected, text)

    def test_auditor_keeps_audit_authority_after_delegation(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8").lower()
        for authority in (
            "claim selection",
            "authority interpretation",
            "materiality",
            "severity",
            "repair",
            "release",
            "reopening",
            "disposition",
        ):
            self.assertIn(authority, text)
        self.assertIn("does not decide audit disposition", text)

    def test_unavailable_split_testing_does_not_create_a_local_fallback(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8").lower()
        self.assertIn("assess existing evidence", text)
        self.assertIn("does not recreate comparative method", text)
        self.assertIn("leave the exact claim unresolved", text)
        self.assertIn("audit consequence", text)
        self.assertIn("plain language", text)


if __name__ == "__main__":
    unittest.main()
