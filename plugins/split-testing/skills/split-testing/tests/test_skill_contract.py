from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT.parents[1]
SKILL_MD = ROOT / "SKILL.md"
EXPECTED_DESCRIPTION = (
    "Obtain the strongest defensible comparative evidence for a live decision "
    "across artifacts, people, systems, processes, or agent runs. Use for A/B, "
    "split, benchmark, blind or unblinded, repeated, audience, or N-way "
    "comparisons; when existing evidence is not fit and the needed observations "
    "must be arranged; or whenever one alternative is claimed better."
)
EXPECTED_SHORT_DESCRIPTION = "Defensible evidence for live comparisons"
EXPECTED_DEFAULT_PROMPT = (
    "Use $split-testing to obtain the strongest defensible evidence for this decision."
)
EXPECTED_REFERENCES = {
    "references/arranging-evidence.md",
    "references/information-and-execution.md",
    "references/presenting-evidence.md",
    "references/validity-and-attribution.md",
}


def frontmatter_value(key: str) -> str:
    block = SKILL_MD.read_text(encoding="utf-8").split("---", 2)[1]
    lines = block.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith(f"{key}:"):
            continue
        value = line.split(":", 1)[1].strip()
        if value not in {">", ">-", ">+", "|", "|-", "|+"}:
            return value.strip("\"'")
        folded: list[str] = []
        for continuation in lines[index + 1 :]:
            if continuation and not continuation.startswith(" "):
                break
            if continuation.strip():
                folded.append(continuation.strip())
        return " ".join(folded)
    raise AssertionError(f"missing frontmatter field: {key}")


class SkillContractTests(unittest.TestCase):
    def test_identity_and_dual_host_metadata_are_synchronized(self) -> None:
        self.assertEqual(frontmatter_value("name"), ROOT.name)
        self.assertEqual(frontmatter_value("description"), EXPECTED_DESCRIPTION)

        codex = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        claude = json.loads(
            (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        for manifest in (codex, claude):
            self.assertEqual(manifest["name"], "split-testing")
            self.assertEqual(manifest["version"], "2.0.0")
            self.assertEqual(manifest["description"], EXPECTED_DESCRIPTION)
            self.assertEqual(manifest["license"], "MIT")
            self.assertNotIn("dependencies", manifest)
        self.assertEqual(codex["interface"]["longDescription"], EXPECTED_DESCRIPTION)
        self.assertEqual(
            codex["interface"]["shortDescription"], EXPECTED_SHORT_DESCRIPTION
        )
        self.assertEqual(codex["interface"]["defaultPrompt"], EXPECTED_DEFAULT_PROMPT)
        self.assertEqual(codex["interface"]["category"], "Testing")
        self.assertEqual(codex["interface"]["capabilities"], ["Read", "Write"])

        yaml_text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Split Testing"', yaml_text)
        self.assertIn(f'short_description: "{EXPECTED_SHORT_DESCRIPTION}"', yaml_text)
        self.assertIn(f'default_prompt: "{EXPECTED_DEFAULT_PROMPT}"', yaml_text)

    def test_skill_is_a_compact_direct_router(self) -> None:
        content = SKILL_MD.read_text(encoding="utf-8")
        direct = set(
            re.findall(r"\]\((references/[A-Za-z0-9._/-]+\.md)(?:#[^)]+)?\)", content)
        )
        on_disk = {
            f"references/{path.name}" for path in (ROOT / "references").glob("*.md")
        }
        self.assertEqual(direct, EXPECTED_REFERENCES)
        self.assertEqual(on_disk, EXPECTED_REFERENCES)
        for relative in direct:
            reference = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIsNone(
                re.search(r"\]\((?:\.\./)?references/", reference),
                f"nested reference route in {relative}",
            )

    def test_runtime_preserves_decision_quality_without_fixed_method(self) -> None:
        content = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("least-cost sufficient comparative evidence", content)
        self.assertIn("Infer ordinary observations, conditions, instruments", content)
        self.assertIn("Keep representative evidence separate from diagnostic challenges", content)
        self.assertIn("Treat every instruction surface as part of exposure", content)
        self.assertIn("verify each decisive factual premise", content)
        self.assertIn("report non-identifiability", content)
        self.assertIn("Apply no arbitrary cap", content)
        self.assertIn("A conversational answer is sufficient for a simple live choice", content)

    def test_execution_and_review_are_semantic_functions_not_stages(self) -> None:
        execution = (ROOT / "references" / "information-and-execution.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("according to exposure risk, not as mandatory roles or stages", execution)
        self.assertIn("A process coordinator or separate directory does not by itself establish", execution)
        self.assertIn("Preserve native outputs and raw responses", execution)
        self.assertIn("Do not impose semantic response templates", execution)
        self.assertIn("Simulated audiences and expert personas are diagnostic proxies", execution)

    def test_failure_attribution_and_causal_claims_require_discriminating_evidence(self) -> None:
        validity = (ROOT / "references" / "validity-and-attribution.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Keep mechanical termination, infrastructure behavior, task validity", validity)
        self.assertIn("An unsatisfiable or authority-incoherent task", validity)
        self.assertIn("Assign an underlying cause only when evidence distinguishes it", validity)
        self.assertIn("When evidence cannot identify a winner, cause, authority, or valid comparison", validity)
        self.assertIn("earliest actionable cause", validity)

    def test_presentation_is_conditional_and_non_authoritative(self) -> None:
        presentation = (ROOT / "references" / "presenting-evidence.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("only after the evidence and supported claim are established", presentation)
        self.assertIn("Do not create a report, file, table, chart, dashboard", presentation)
        self.assertIn("Presentation is a derived, non-authoritative projection", presentation)
        self.assertIn("Retain the native evidence", presentation)

    def test_no_rejected_runtime_mechanism_or_closed_ontology_is_shipped(self) -> None:
        self.assertFalse((ROOT / "scripts").exists())
        self.assertFalse((ROOT / "schemas").exists())
        self.assertFalse((ROOT / "dist").exists())
        self.assertFalse((ROOT / "evals").exists())
        self.assertFalse((ROOT / "assets").exists())

        runtime = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in [SKILL_MD, *(ROOT / "references").glob("*.md")]
        )
        self.assertNotRegex(
            runtime,
            r"(?:shall|must|required to) (?:use|produce) a (?:score|vector|frontier)",
        )


if __name__ == "__main__":
    unittest.main()
