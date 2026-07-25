from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = SKILL_ROOT.parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[1]
SKILL_MD = SKILL_ROOT / "SKILL.md"
PLUGIN_JSON = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
OPENAI_YAML = SKILL_ROOT / "agents" / "openai.yaml"
REPOSITORY_README = REPO_ROOT / "README.md"
CODEX_MARKETPLACE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
CLAUDE_MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
TRIGGER_EVALS = SKILL_ROOT / "evals" / "trigger-prompts.json"
BEHAVIOR_EVALS = SKILL_ROOT / "evals" / "evals.json"
ENVIRONMENT_FIXTURES = SKILL_ROOT / "evals" / "environment-fixtures.json"
REFERENCE_NAMES = {"routing.md", "verification.md", "recovery.md", "portability.md"}
SUCCESS_INVARIANT = (
    "A tool acknowledgement is not product success. Success requires observing "
    "the requested user-visible state after the action."
)


def read_frontmatter(path: Path) -> dict[str, str]:
    parts = path.read_text(encoding="utf-8").split("---", 2)
    if len(parts) != 3:
        raise AssertionError(f"missing YAML frontmatter: {path}")
    lines = parts[1].strip().splitlines()
    result: dict[str, str] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("name:"):
            result["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("description:"):
            value = line.split(":", 1)[1].strip()
            if value in {">", ">-", "|", "|-"}:
                block: list[str] = []
                index += 1
                while index < len(lines) and lines[index].startswith("  "):
                    block.append(lines[index].strip())
                    index += 1
                result["description"] = " ".join(block)
                continue
            result["description"] = value.strip('"')
        index += 1
    return result


def yaml_interface_value(key: str) -> str:
    content = OPENAI_YAML.read_text(encoding="utf-8")
    match = re.search(rf'^  {re.escape(key)}: "([^"]+)"$', content, flags=re.MULTILINE)
    if match is None:
        raise AssertionError(f"missing openai.yaml interface value: {key}")
    return match.group(1)


class LinuxDesktopControlContractTests(unittest.TestCase):
    def test_manifest_is_ga_codex_instruction_plugin(self) -> None:
        manifest = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))

        self.assertEqual("linux-desktop-control", manifest["name"])
        self.assertEqual("1.0.0", manifest["version"])
        self.assertEqual("Agent Tooling Contributors", manifest["author"]["name"])
        self.assertEqual("./skills/", manifest["skills"])
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("hooks", manifest)
        self.assertNotIn("apps", manifest)
        interface = manifest["interface"]
        self.assertEqual("Linux Desktop Control", interface["displayName"])
        self.assertEqual(
            "Control and verify Linux desktop UI outcomes safely.",
            interface["shortDescription"],
        )
        self.assertEqual("Agent Tooling Contributors", interface["developerName"])
        self.assertEqual("Productivity", interface["category"])
        self.assertEqual(["Read", "Write", "Interactive"], interface["capabilities"])
        self.assertEqual(1, len(interface["defaultPrompt"]))
        self.assertLessEqual(len(interface["defaultPrompt"][0]), 128)

    def test_marketplace_publication_is_codex_only(self) -> None:
        codex = json.loads(CODEX_MARKETPLACE.read_text(encoding="utf-8"))
        claude = json.loads(CLAUDE_MARKETPLACE.read_text(encoding="utf-8"))
        codex_entries = [entry for entry in codex["plugins"] if entry["name"] == "linux-desktop-control"]
        claude_entries = [entry for entry in claude["plugins"] if entry["name"] == "linux-desktop-control"]

        self.assertEqual(1, len(codex_entries))
        self.assertEqual([], claude_entries)
        self.assertEqual("AVAILABLE", codex_entries[0]["policy"]["installation"])
        self.assertEqual("ON_INSTALL", codex_entries[0]["policy"]["authentication"])
        self.assertEqual("Productivity", codex_entries[0]["category"])

    def test_skill_metadata_is_mandatory_and_bounded(self) -> None:
        metadata = read_frontmatter(SKILL_MD)
        description = metadata["description"]
        content = SKILL_MD.read_text(encoding="utf-8")

        self.assertEqual("Linux Desktop Control", metadata["name"])
        self.assertTrue(description.startswith("REQUIRED"))
        self.assertIn("do not", description.lower())
        self.assertIn("Covers: (1)", description)
        self.assertIn("If the task involves Linux desktop control, use this skill.", description)
        self.assertLessEqual(len(description), 1024)
        self.assertIn("# Linux Desktop Control", content)
        self.assertLess(len(content.splitlines()), 500)

    def test_openai_yaml_matches_public_interface(self) -> None:
        self.assertEqual("Linux Desktop Control", yaml_interface_value("display_name"))
        self.assertEqual(
            "Control and verify Linux desktop UI outcomes safely",
            yaml_interface_value("short_description"),
        )
        self.assertEqual(
            "Use $linux-desktop-control to inspect the Linux desktop, select operational control channels, perform the requested interaction, and verify the visible outcome.",
            yaml_interface_value("default_prompt"),
        )

    def test_reference_topology_is_shallow_and_complete(self) -> None:
        references = SKILL_ROOT / "references"
        names = {path.name for path in references.glob("*.md")}
        skill = SKILL_MD.read_text(encoding="utf-8")

        self.assertEqual(REFERENCE_NAMES, names)
        for name in REFERENCE_NAMES:
            self.assertIn(f"<skills-file-root>/references/{name}", skill)
            content = (references / name).read_text(encoding="utf-8")
            self.assertLess(len(content.splitlines()), 300)
            self.assertNotIn("references/", content)

    def test_instruction_surface_has_one_success_invariant_and_ears_controls(self) -> None:
        instruction_files = [SKILL_MD, *(SKILL_ROOT / "references").glob("*.md")]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in instruction_files)
        verification = (SKILL_ROOT / "references" / "verification.md").read_text(encoding="utf-8")
        control_lines = [
            line
            for line in SKILL_MD.read_text(encoding="utf-8").splitlines()
            if re.match(r"^\d+\. (WHEN|BEFORE|AFTER|IF|You SHALL)", line)
        ]

        self.assertEqual(1, combined.count(SUCCESS_INVARIANT))
        self.assertGreaterEqual(len(control_lines), 22)
        self.assertTrue(all("SHALL" in line for line in control_lines))
        self.assertIn("distinguishes success from plausible alternatives", verification)
        self.assertIn("use it instead of global desktop enumeration", combined)
        self.assertIn("SHALL NOT retain, restate, or report unrelated entries", combined)
        self.assertIn("returned scope matches that target", combined)
        self.assertIn("capture is cropped to the intended target", combined)
        self.assertIn("A requested selector is not evidence about the response", combined)

    def test_package_has_no_native_or_bespoke_payload(self) -> None:
        forbidden_files = {".mcp.json", "hooks.json", ".app.json"}
        payload_files = [
            PLUGIN_JSON,
            SKILL_MD,
            OPENAI_YAML,
            TRIGGER_EVALS,
            BEHAVIOR_EVALS,
            ENVIRONMENT_FIXTURES,
            *(SKILL_ROOT / "references").glob("*.md"),
        ]
        forbidden_terms = [
            "".join(["chat", "mux"]),
            "".join(["chat", "gpt"]),
            "".join(["ge", "mini"]),
            "".join(["gr", "ok"]),
            "".join(["br", "ave"]),
            "".join(["kdo", "tool"]),
            "".join(["spect", "acle"]),
            "".join(["ydo", "tool"]),
            "/home/",
            "mcp__",
        ]

        self.assertTrue(all(path.name not in forbidden_files for path in PLUGIN_ROOT.rglob("*")))
        self.assertEqual([], list(PLUGIN_ROOT.rglob("*.rs")))
        for path in payload_files:
            content = path.read_text(encoding="utf-8").lower()
            for term in forbidden_terms:
                self.assertNotIn(term.lower(), content, f"{term!r} found in {path}")
        executable_files = [
            path
            for path in PLUGIN_ROOT.rglob("*")
            if path.is_file() and path.stat().st_mode & 0o111
        ]
        self.assertEqual([], executable_files)

    def test_trigger_evaluations_cover_both_sides_of_boundary(self) -> None:
        data = json.loads(TRIGGER_EVALS.read_text(encoding="utf-8"))
        queries = data["queries"]
        ids = [query["id"] for query in queries]

        self.assertEqual("linux-desktop-control", data["skill_name"])
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(sum(query["should_trigger"] for query in queries), 7)
        self.assertGreaterEqual(sum(not query["should_trigger"] for query in queries), 7)

    def test_behavioral_evaluations_cover_ga_matrix(self) -> None:
        data = json.loads(BEHAVIOR_EVALS.read_text(encoding="utf-8"))
        evals = data["evals"]
        ids = [case["id"] for case in evals]
        status_words = {"verified", "unverified", "blocked", "not attempted"}

        self.assertEqual("linux-desktop-control", data["skill_name"])
        self.assertEqual(20, len(evals))
        self.assertEqual(len(ids), len(set(ids)))
        for case in evals:
            self.assertTrue(case["prompt"].strip())
            expected = case["expected_output"].lower()
            self.assertTrue(any(status in expected for status in status_words))
            self.assertTrue(case["expected_decision"].strip())
            self.assertTrue(case["expected_result"].strip())
            self.assertTrue(any(status in case["expected_result"].lower() for status in status_words))
            self.assertEqual([], case["files"])

    def test_simulated_environment_fixtures_cover_portability_matrix(self) -> None:
        data = json.loads(ENVIRONMENT_FIXTURES.read_text(encoding="utf-8"))
        fixtures = data["fixtures"]
        ids = [fixture["id"] for fixture in fixtures]
        families = {fixture["family"] for fixture in fixtures}
        expected_families = {
            "wayland",
            "x11",
            "gnome-family",
            "kde-family",
            "wlroots-family",
            "tiling-window-manager",
            "multi-monitor",
            "headless",
            "partially-configured",
        }
        status_words = {"verified", "unverified", "blocked", "not attempted"}

        self.assertEqual("linux-desktop-control", data["skill_name"])
        self.assertIn("simulated", data["claim_scope"].lower())
        self.assertEqual(expected_families, families)
        self.assertEqual(len(ids), len(set(ids)))
        for fixture in fixtures:
            self.assertIs(fixture["simulated"], True)
            self.assertTrue(fixture["capabilities"])
            self.assertGreaterEqual(len(fixture["transcript"]), 2)
            self.assertTrue(fixture["expected_decision"].strip())
            result = fixture["expected_result"].lower()
            self.assertTrue(any(status in result for status in status_words))

    def test_repository_inventory_documents_specific_backend_without_plugin_readme(self) -> None:
        readme = REPOSITORY_README.read_text(encoding="utf-8")
        normalized_readme = " ".join(readme.split())

        self.assertIn(
            "[`codex-desktop-linux`](https://github.com/ilysenko/codex-desktop-linux)",
            readme,
        )
        self.assertIn("This plugin is specific to that integration", normalized_readme)
        self.assertIn("the linked project supplies", normalized_readme)
        self.assertFalse((PLUGIN_ROOT / "README.md").exists())
        self.assertEqual([], list(SKILL_ROOT.rglob("README.md")))

    def test_shipped_text_uses_lf_line_endings(self) -> None:
        text_suffixes = {".md", ".json", ".yaml", ".py"}
        for path in PLUGIN_ROOT.rglob("*"):
            if path.is_file() and path.suffix in text_suffixes:
                self.assertNotIn(b"\r\n", path.read_bytes(), str(path))


if __name__ == "__main__":
    unittest.main()
