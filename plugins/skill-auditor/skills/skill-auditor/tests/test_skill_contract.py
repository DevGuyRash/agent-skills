from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT.parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[1]
SKILL_MD = ROOT / "SKILL.md"
EXPECTED_DESCRIPTION = (
    "Audit an existing skill or plugin for material evidence about target "
    "authority, executable behavior, host contracts, instruction design, and "
    "task value. Use for evidence-driven quality reviews, self-audits, "
    "release-risk investigation, or suspected packaging, routing, source, "
    "context, verification, or task-value drift. Do not use to author a new "
    "skill or review ordinary source-code changes."
)
EXPECTED_SHORT_DESCRIPTION = "Audit existing skills and plugins with concrete evidence"
EXPECTED_DEFAULT_PROMPT = "Use $skill-auditor to audit this skill or plugin."
EXPECTED_CATEGORY = "Developer Tools"
EXPECTED_REFERENCES = {
    "references/context-and-source-evidence.md",
    "references/host-contracts.md",
    "references/instruction-design.md",
    "references/open-standard.md",
    "references/packaging-fit.md",
    "references/plugin-fit.md",
    "references/repo-overlay.md",
    "references/task-value-evidence.md",
    "references/trigger-evals.md",
}
GOVERNING_BLOCK_SHA256 = "c79e2dbd6c1d5d90eebc30242fde51216ea894f70b4dd7e1b98dcb81ee4bc038"


def frontmatter_value(key: str) -> str:
    text = SKILL_MD.read_text(encoding="utf-8")
    block = text.split("---", 2)[1]
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


def catalog_entry(path: Path, name: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return next(item for item in data["plugins"] if item["name"] == name)


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
            self.assertEqual(manifest["version"], "3.2.0")
            self.assertEqual(manifest["license"], "MIT")
        self.assertEqual(codex["interface"]["longDescription"], EXPECTED_DESCRIPTION)
        self.assertEqual(
            codex["interface"]["shortDescription"], EXPECTED_SHORT_DESCRIPTION
        )
        self.assertEqual(codex["interface"]["defaultPrompt"], EXPECTED_DEFAULT_PROMPT)
        self.assertEqual(codex["interface"]["category"], EXPECTED_CATEGORY)
        self.assertEqual(codex["interface"]["capabilities"], ["Read", "Write"])
        self.assertTrue((PLUGIN_ROOT / "LICENSE").is_file())

    def test_catalog_metadata_matches_the_plugin_interface(self) -> None:
        codex_catalog = catalog_entry(
            REPO_ROOT / ".agents" / "plugins" / "marketplace.json", "skill-auditor"
        )
        claude_catalog = catalog_entry(
            REPO_ROOT / ".claude-plugin" / "marketplace.json", "skill-auditor"
        )
        self.assertEqual(codex_catalog["description"], EXPECTED_SHORT_DESCRIPTION)
        self.assertEqual(codex_catalog["category"], EXPECTED_CATEGORY)
        self.assertEqual(claude_catalog["description"], EXPECTED_SHORT_DESCRIPTION)
        self.assertEqual(claude_catalog["version"], "3.2.0")

    def test_every_reference_is_directly_routed_from_skill_md(self) -> None:
        content = SKILL_MD.read_text(encoding="utf-8")
        linked = set(re.findall(r"\]\((references/[A-Za-z0-9._/-]+\.md)\)", content))
        on_disk = {f"references/{path.name}" for path in (ROOT / "references").glob("*.md")}

        self.assertEqual(linked, EXPECTED_REFERENCES)
        self.assertEqual(on_disk, EXPECTED_REFERENCES)
        self.assertNotIn("<skills-file-root>/", content)
        for relative in linked:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_runtime_scripts_are_structural_helpers(self) -> None:
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

    def test_governing_architecture_block_is_byte_preserved(self) -> None:
        text = (ROOT / "references" / "instruction-design.md").read_text(encoding="utf-8")
        start = text.index("## Governing Architecture\n")
        end = text.index("\n\n---", start)
        block = text[start:end] + "\n"
        self.assertEqual(hashlib.sha256(block.encode("utf-8")).hexdigest(), GOVERNING_BLOCK_SHA256)


if __name__ == "__main__":
    unittest.main()
