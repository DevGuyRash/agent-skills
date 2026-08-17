from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT.parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[1]
SKILL_MD = ROOT / "SKILL.md"
EXPECTED_DESCRIPTION = (
    "Design and run blinded comparative tests of any alternatives with variable "
    "conditions, runs, rounds, models, agents, and reviewers, including when a "
    "decision has no ready-made test tasks. Use for split testing, A/B or multi-way "
    "comparisons, repeated trials, blind evaluation, or evidence that one option "
    "performs better than another."
)
EXPECTED_SHORT_DESCRIPTION = "Run flexible blind comparisons across alternatives"
EXPECTED_DEFAULT_PROMPT = (
    "Use $split-testing to compare these alternatives with blinded evidence."
)
EXPECTED_CATEGORY = "Testing"
EXPECTED_REFERENCES = {
    "references/design.md",
    "references/execution.md",
    "references/helper-contract.md",
    "references/review.md",
    "references/interpretation-and-reporting.md",
}


def command_help(command: list[str]) -> str:
    """Capture help through a file because some Node CLIs truncate piped output."""
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as stream:
        subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=False)
        stream.seek(0)
        return stream.read()


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


def catalog_entry(path: Path, name: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return next(item for item in data["plugins"] if item["name"] == name)


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
            self.assertEqual(manifest["version"], "1.0.0")
            self.assertEqual(manifest["description"], EXPECTED_DESCRIPTION)
            self.assertEqual(manifest["license"], "MIT")
        self.assertEqual(codex["interface"]["longDescription"], EXPECTED_DESCRIPTION)
        self.assertEqual(
            codex["interface"]["shortDescription"], EXPECTED_SHORT_DESCRIPTION
        )
        self.assertEqual(
            codex["interface"]["defaultPrompt"], EXPECTED_DEFAULT_PROMPT
        )
        self.assertEqual(codex["interface"]["category"], EXPECTED_CATEGORY)
        self.assertEqual(codex["interface"]["capabilities"], ["Read", "Write"])
        self.assertTrue((PLUGIN_ROOT / "LICENSE").is_file())

    def test_catalogs_and_openai_metadata_match(self) -> None:
        codex_catalog = catalog_entry(
            REPO_ROOT / ".agents" / "plugins" / "marketplace.json", "split-testing"
        )
        claude_catalog = catalog_entry(
            REPO_ROOT / ".claude-plugin" / "marketplace.json", "split-testing"
        )
        self.assertEqual(codex_catalog["description"], EXPECTED_SHORT_DESCRIPTION)
        self.assertEqual(codex_catalog["category"], EXPECTED_CATEGORY)
        self.assertNotIn("version", codex_catalog)
        self.assertEqual(claude_catalog["description"], EXPECTED_SHORT_DESCRIPTION)
        self.assertEqual(claude_catalog["version"], "1.0.0")

        yaml_text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Split Testing"', yaml_text)
        self.assertIn(f'short_description: "{EXPECTED_SHORT_DESCRIPTION}"', yaml_text)
        self.assertIn(f'default_prompt: "{EXPECTED_DEFAULT_PROMPT}"', yaml_text)

    def test_every_shipped_reference_is_reachable_without_flattening_routes(self) -> None:
        on_disk = {
            f"references/{path.name}" for path in (ROOT / "references").glob("*.md")
        }

        self.assertEqual(on_disk, EXPECTED_REFERENCES)

        pending = [SKILL_MD]
        seen = {SKILL_MD.resolve()}
        reachable: set[str] = set()
        while pending:
            source = pending.pop()
            content = source.read_text(encoding="utf-8")
            for raw in re.findall(r"\]\(([^)#]+\.md)(?:#[^)]+)?\)", content):
                target = (source.parent / raw).resolve()
                if target.parent != (ROOT / "references").resolve():
                    continue
                relative = target.relative_to(ROOT).as_posix()
                reachable.add(relative)
                self.assertTrue(target.is_file(), relative)
                if target not in seen:
                    seen.add(target)
                    pending.append(target)

        self.assertEqual(reachable, EXPECTED_REFERENCES)
        direct = set(
            re.findall(
                r"\]\((references/[A-Za-z0-9._/-]+\.md)(?:#[^)]+)?\)",
                SKILL_MD.read_text(encoding="utf-8"),
            )
        )
        self.assertNotIn("references/helper-contract.md", direct)

    def test_runtime_surface_contains_only_the_structural_workspace_helper(self) -> None:
        scripts = {path.name for path in (ROOT / "scripts").iterdir() if path.is_file()}
        self.assertEqual(scripts, {"split_test_workspace.py"})
        helper = ROOT / "scripts" / "split_test_workspace.py"
        self.assertTrue(helper.stat().st_mode & 0o111)

    def test_helper_syntax_matches_the_documented_python_floor(self) -> None:
        helper = ROOT / "scripts" / "split_test_workspace.py"
        ast.parse(
            helper.read_text(encoding="utf-8"),
            filename=str(helper),
            feature_version=(3, 9),
        )
        execution = (ROOT / "references" / "execution.md").read_text(encoding="utf-8")
        self.assertIn("requires Python 3.9 or later", execution)

    def test_no_fixed_eval_corpus_or_report_template_is_shipped(self) -> None:
        self.assertFalse((ROOT / "evals").exists())
        self.assertFalse((ROOT / "assets").exists())

    def test_cli_examples_only_use_flags_exposed_by_installed_hosts(self) -> None:
        execution = (ROOT / "references" / "execution.md").read_text(encoding="utf-8")
        if shutil.which("codex"):
            help_text = command_help(["codex", "exec", "--help"])
            for flag in ("--ephemeral", "--model", "--config", "--cd", "--json"):
                self.assertIn(flag, help_text)
                self.assertIn(flag, execution)
        if shutil.which("claude"):
            help_text = command_help(["claude", "--help"])
            for flag in (
                "--print",
                "--no-session-persistence",
                "--model",
                "--effort",
                "--output-format",
            ):
                self.assertIn(flag, help_text)
                self.assertIn(flag, execution)


if __name__ == "__main__":
    unittest.main()
