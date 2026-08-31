from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT.parents[1]
SKILL_MD = ROOT / "SKILL.md"
EXPECTED_DESCRIPTION = (
    "Audit an existing skill or plugin for material evidence about target "
    "authority, executable behavior, host contracts, instruction design, and "
    "task value. Use for evidence-driven quality reviews, self-audits, "
    "release-risk investigation, or suspected packaging, routing, source, "
    "context, verification, or task-value drift. Delegates newly needed "
    "comparative evidence to Split Testing when available. Do not use to author "
    "a new skill or review ordinary source-code changes."
)
EXPECTED_SHORT_DESCRIPTION = "Audit skills; delegate new comparisons when available"
EXPECTED_DEFAULT_PROMPT = "Use $skill-auditor to audit this skill or plugin."
EXPECTED_CATEGORY = "Developer Tools"
EXPECTED_REFERENCES = {
    "references/comparative-handoff.md",
    "references/context-and-source-evidence.md",
    "references/executable-evidence.md",
    "references/host-contracts.md",
    "references/instruction-design.md",
    "references/open-standard.md",
    "references/packaging-fit.md",
    "references/plugin-fit.md",
    "references/repo-overlay.md",
    "references/trigger-evals.md",
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
    def test_portable_identity_and_manifest_description_are_in_sync(self) -> None:
        self.assertEqual(frontmatter_value("name"), ROOT.name)
        self.assertEqual(frontmatter_value("description"), EXPECTED_DESCRIPTION)

        claude = json.loads(
            (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        codex = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        for manifest in (claude, codex):
            self.assertEqual(manifest["description"], EXPECTED_DESCRIPTION)
            self.assertEqual(manifest["version"], "4.0.0")
            self.assertEqual(manifest["license"], "MIT")
            self.assertNotIn("dependencies", manifest)
            self.assertIn("comparative-evidence", manifest["keywords"])
        self.assertEqual(codex["interface"]["longDescription"], EXPECTED_DESCRIPTION)
        self.assertEqual(
            codex["interface"]["shortDescription"], EXPECTED_SHORT_DESCRIPTION
        )
        self.assertEqual(codex["interface"]["defaultPrompt"], EXPECTED_DEFAULT_PROMPT)
        self.assertEqual(codex["interface"]["category"], EXPECTED_CATEGORY)
        self.assertEqual(codex["interface"]["capabilities"], ["Read", "Write"])
        self.assertTrue((PLUGIN_ROOT / "LICENSE").is_file())

        yaml_text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Skill Auditor"', yaml_text)
        self.assertIn(f'short_description: "{EXPECTED_SHORT_DESCRIPTION}"', yaml_text)
        self.assertIn(f'default_prompt: "{EXPECTED_DEFAULT_PROMPT}"', yaml_text)

    def test_every_reference_is_directly_routed_from_skill_md(self) -> None:
        content = SKILL_MD.read_text(encoding="utf-8")
        linked = set(
            re.findall(r"\]\((references/[A-Za-z0-9._/-]+\.md)(?:#[^)]+)?\)", content)
        )
        on_disk = {
            f"references/{path.name}" for path in (ROOT / "references").glob("*.md")
        }

        self.assertEqual(linked, EXPECTED_REFERENCES)
        self.assertEqual(on_disk, EXPECTED_REFERENCES)
        self.assertNotIn("<skills-file-root>/", content)
        for relative in linked:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_comparative_method_is_delegated_without_a_local_fallback(self) -> None:
        content = SKILL_MD.read_text(encoding="utf-8").lower()
        handoff = (ROOT / "references" / "comparative-handoff.md").read_text(
            encoding="utf-8"
        ).lower()

        self.assertIn("$split-testing", content)
        self.assertIn("existing evidence", content)
        self.assertIn("ordinary context", content)
        self.assertIn("does not recreate comparative method", content)
        self.assertIn("plain-language", content)
        self.assertIn("does not recreate comparative method", handoff)
        self.assertIn("unresolved consequence", handoff)
        self.assertIn("audit disposition", handoff)
        self.assertFalse((ROOT / "references" / "task-value-evidence.md").exists())
        self.assertFalse((ROOT / "schemas").exists())

    def test_handoff_is_natural_context_and_audit_owned(self) -> None:
        handoff = (ROOT / "references" / "comparative-handoff.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("ordinary context", handoff)
        for needed in ("claim", "authority", "existing evidence", "constraints", "consequence"):
            self.assertIn(needed, handoff.lower())
        self.assertIn("Skill Auditor", handoff)
        for rejected in ("schema", "envelope", "request_digest", "closure_assessment"):
            self.assertNotIn(rejected, handoff)

    def test_removed_comparison_manual_is_not_duplicated_elsewhere(self) -> None:
        runtime = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in [SKILL_MD, *(ROOT / "references").glob("*.md")]
            if path.name != "comparative-handoff.md"
        )
        old_method_clauses = (
            "treatment executors receive the target",
            "prompt purity is a causal property",
            "replication must re-expose",
            "nested panel",
            "fresh executors can measure executor variation",
            "before candidate exposure, independent validation",
        )
        for clause in old_method_clauses:
            self.assertNotIn(clause, runtime)

    def test_runtime_scripts_remain_auditor_owned_structural_observers(self) -> None:
        scripts = {path.name for path in (ROOT / "scripts").glob("*.sh")}
        self.assertEqual(
            scripts,
            {
                "frontmatter_check.sh",
                "plugin_check.sh",
                "reference_check.sh",
                "script_sanity.sh",
            },
        )

    def test_no_semantic_prompt_corpus_is_shipped(self) -> None:
        self.assertFalse((ROOT / "evals").exists())


if __name__ == "__main__":
    unittest.main()
