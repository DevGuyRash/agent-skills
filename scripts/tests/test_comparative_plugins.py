from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SPLIT_ROOT = REPO_ROOT / "plugins" / "split-testing"
AUDITOR_ROOT = REPO_ROOT / "plugins" / "skill-auditor"
SPLIT_SHORT = "Least-cost defensible evidence for consequential comparisons"
AUDITOR_SHORT = "Audit skills; delegate new comparisons when available"


def catalog_entry(path: Path, name: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return next(item for item in data["plugins"] if item["name"] == name)


def manifest(plugin_root: Path, host: str) -> dict:
    return json.loads(
        (plugin_root / f".{host}-plugin" / "plugin.json").read_text(encoding="utf-8")
    )


def section(text: str, start_heading: str, end_heading: str) -> str:
    start = text.index(start_heading)
    end = text.index(end_heading, start)
    return text[start:end].rstrip() + "\n"


class ComparativePluginRepositoryTests(unittest.TestCase):
    def test_catalogs_match_versions_and_optional_relationship_metadata(self) -> None:
        codex_path = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
        claude_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
        expectations = {
            "split-testing": (SPLIT_ROOT, "2.0.0", SPLIT_SHORT),
            "skill-auditor": (AUDITOR_ROOT, "4.0.0", AUDITOR_SHORT),
        }
        for name, (plugin_root, version, short_description) in expectations.items():
            codex = catalog_entry(codex_path, name)
            claude = catalog_entry(claude_path, name)
            codex_manifest = manifest(plugin_root, "codex")
            claude_manifest = manifest(plugin_root, "claude")
            self.assertEqual(codex["description"], short_description)
            self.assertEqual(claude["description"], short_description)
            self.assertEqual(claude["version"], version)
            self.assertEqual(codex_manifest["version"], version)
            self.assertEqual(claude_manifest["version"], version)
            self.assertEqual(codex_manifest["interface"]["shortDescription"], short_description)
            self.assertNotIn("dependencies", codex_manifest)
            self.assertNotIn("dependencies", claude_manifest)

    def test_root_inventory_states_separate_ownership_and_optional_handoff(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "`plugins/split-testing/` owns generic comparative-evidence method",
            readme,
        )
        self.assertIn("optional derived evidence views", readme)
        self.assertIn(
            "`plugins/skill-auditor/` owns audit disposition and optionally delegates",
            readme,
        )
        self.assertIn("without a hard plugin dependency", readme)

    def test_adopted_governing_architecture_is_source_equal(self) -> None:
        governing = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        adopted = (
            AUDITOR_ROOT
            / "skills"
            / "skill-auditor"
            / "references"
            / "instruction-design.md"
        ).read_text(encoding="utf-8")
        source = section(
            governing,
            "## Governing Architecture\n",
            "---\n\n## ⚠️ Command Isolation",
        )
        copy = section(adopted, "## Governing Architecture\n", "---\n\n## Audit use\n")
        self.assertEqual(copy, source)

    def test_friction_diagnostics_is_not_coupled_to_either_plugin(self) -> None:
        for plugin_root in (SPLIT_ROOT, AUDITOR_ROOT):
            texts = [
                path.read_text(encoding="utf-8")
                for path in plugin_root.rglob("*.json")
                if "tests" not in path.parts
            ]
            self.assertNotIn("friction-diagnostics", "\n".join(texts))

    def test_split_testing_is_caller_neutral_and_relationship_is_one_way(self) -> None:
        text_suffixes = {
            ".json",
            ".md",
            ".ps1",
            ".py",
            ".rs",
            ".sh",
            ".toml",
            ".yaml",
            ".yml",
        }
        split_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in SPLIT_ROOT.rglob("*")
            if path.is_file()
            and path.suffix in text_suffixes
        ).lower()
        auditor_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in AUDITOR_ROOT.rglob("*")
            if path.is_file()
            and "tests" not in path.parts
            and path.suffix in {".json", ".md", ".ps1", ".sh", ".toml", ".yaml", ".yml"}
        ).lower()
        self.assertNotIn("skill-auditor", split_text)
        self.assertIsNone(re.search(r"\baudit(?:ed|ing|or|ors|s)?\b", split_text))
        self.assertIn("split-testing", auditor_text)

    def test_caller_schemas_are_vendored_byte_for_byte(self) -> None:
        names = (
            "comparative-evidence-request.v1.schema.json",
            "comparative-evidence-result.v1.schema.json",
        )
        for name in names:
            split = SPLIT_ROOT / "skills" / "split-testing" / "schemas" / name
            auditor = AUDITOR_ROOT / "skills" / "skill-auditor" / "schemas" / name
            self.assertEqual(auditor.read_bytes(), split.read_bytes(), name)

    def test_caller_schemas_are_honest_about_cross_document_verification(self) -> None:
        schema_root = SPLIT_ROOT / "skills" / "split-testing" / "schemas"
        request = json.loads(
            (schema_root / "comparative-evidence-request.v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        result = json.loads(
            (schema_root / "comparative-evidence-result.v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        request_conditions = request["properties"]["closure_conditions"]
        result_assessments = result["properties"]["closure_assessment"]
        for contract in (request_conditions, result_assessments):
            self.assertEqual(contract["minItems"], 1)
            self.assertIs(contract["uniqueItems"], True)
            self.assertIn("caller-side verification", contract["description"])
        caller = (
            SPLIT_ROOT
            / "skills"
            / "split-testing"
            / "references"
            / "caller-interface.md"
        ).read_text(encoding="utf-8")
        self.assertIn("split-test exchange verify REQUEST.json RESULT.json", caller)
        self.assertIn("JSON Schema cannot express", caller)

    def test_repo_delegation_guidance_is_generic_and_not_template_locked(self) -> None:
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertNotIn("split-testing", agents.lower())
        self.assertNotIn("skill-auditor", agents.lower())
        for plugin_root in (SPLIT_ROOT, AUDITOR_ROOT):
            self.assertEqual(list(plugin_root.rglob("AGENTS.md")), [])
        delegated = section(
            agents,
            "## Skill authoring: subagent dispatch prompt design\n",
            "---\n\n## Skill authoring: output size discipline",
        ).lower()
        self.assertIn("role-complete", delegated)
        self.assertIn("narrowest real output interface", delegated)
        self.assertIn("inspect", delegated)
        self.assertIn("inherit", delegated)
        self.assertNotIn("fill-in-the-blank", delegated)
        for leaked in ("split testing", "split-testing", "estimand", "comparative evidence"):
            self.assertNotIn(leaked, delegated)


if __name__ == "__main__":
    unittest.main()
