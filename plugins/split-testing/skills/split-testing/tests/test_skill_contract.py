from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT.parents[1]
SKILL_MD = ROOT / "SKILL.md"
EXPECTED_DESCRIPTION = (
    "Determine the least-cost defensible basis for a live, consequential "
    "comparative decision or material claim across artifacts, people, systems, "
    "processes, or agent runs. Use for consequential A/B, split, benchmark, "
    "blind or unblinded, repeated, audience, or N-way comparisons when existing "
    "evidence, rightful preference, or new observations must be assessed, "
    "checked, or arranged."
)
EXPECTED_SHORT_DESCRIPTION = "Least-cost defensible evidence for consequential comparisons"
EXPECTED_DEFAULT_PROMPT = (
    "Use $split-testing to determine the least-cost defensible basis for this decision."
)
EXPECTED_CATEGORY = "Testing"
EXPECTED_REFERENCES = {
    "references/decision-warrant.md",
    "references/caller-interface.md",
    "references/digital-execution.md",
    "references/evidence-view.md",
    "references/exposure-and-control.md",
    "references/helper-contract.md",
    "references/inference-and-reporting.md",
    "references/observation-and-review.md",
    "references/obtaining-evidence.md",
}
EXPECTED_COMMANDS = {
    "add-commitment",
    "add-work-set",
    "close-work-set",
    "events",
    "init",
    "prepare-work",
    "publish",
    "receipt",
    "reveal",
    "seal-work",
    "status",
    "view",
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


def help_text(script: str) -> str:
    completed = subprocess.run(
        [str(ROOT / "scripts" / script), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return completed.stdout


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
        self.assertEqual(
            codex["interface"]["defaultPrompt"], EXPECTED_DEFAULT_PROMPT
        )
        self.assertEqual(codex["interface"]["category"], EXPECTED_CATEGORY)
        self.assertEqual(codex["interface"]["capabilities"], ["Read", "Write"])
        self.assertTrue((PLUGIN_ROOT / "LICENSE").is_file())

        yaml_text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Split Testing"', yaml_text)
        self.assertIn(f'short_description: "{EXPECTED_SHORT_DESCRIPTION}"', yaml_text)
        self.assertIn(f'default_prompt: "{EXPECTED_DEFAULT_PROMPT}"', yaml_text)

    def test_every_reference_is_directly_routed_from_skill_md(self) -> None:
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
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_runtime_kernel_is_declarative_and_routes_optional_views_late(self) -> None:
        content = SKILL_MD.read_text(encoding="utf-8").lower()
        view = (ROOT / "references" / "evidence-view.md").read_text(
            encoding="utf-8"
        ).lower()

        self.assertIn("live decision", content)
        self.assertIn("rightful authority", content)
        self.assertIn("do not ask the user", content)
        self.assertIn("after evidence", content)
        self.assertIn("non-authoritative", view)
        self.assertIn("reopen", view)
        self.assertIn("no view", view)

    def test_analyst_conventions_cannot_become_decision_requirements(self) -> None:
        # A blinded release trial exposed agents turning supported action classes into
        # unauthorized gates and rollout details. Remove this compensation only after
        # three consecutive fresh rounds preserve authority without the explicit clause.
        warrant = (ROOT / "references" / "decision-warrant.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "does not authorize you to invent decision-changing implementation details",
            warrant,
        )
        self.assertIn("analyst-chosen convention non-gating and conditional", warrant)
        self.assertIn("rightful authority supplied or delegated it", warrant)

    def test_bounded_evidence_cannot_become_an_invented_qualification_gate(self) -> None:
        # A fresh hidden-decision trial exposed the candidate importing a broader
        # proof horizon after a decisive maker-defined veto. Reconsider this
        # compensation after three consecutive prospective rounds act correctly
        # without it across materially different evidence topologies.
        content = SKILL_MD.read_text(encoding="utf-8")
        warrant = (ROOT / "references" / "decision-warrant.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("a decisive veto can resolve the live action", content)
        self.assertIn("Do not turn a bounded conclusion into an extra acceptance gate", warrant)
        self.assertIn("remaining alternatives already satisfy maker-set requirements", warrant)

    def test_imaginable_values_cannot_manufacture_an_authority_gap(self) -> None:
        # A separate hidden-decision trial exposed the candidate withholding an
        # ordinary operational default because merely possible unequal utilities
        # were imagined. Reconsider after three consecutive prospective rounds
        # preserve real non-dominance without inventing an authority gap.
        content = SKILL_MD.read_text(encoding="utf-8")
        warrant = (ROOT / "references" / "decision-warrant.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Do not manufacture non-dominance", content)
        self.assertIn("merely imaginable consequence asymmetries", warrant)
        self.assertIn("a concrete unresolved value in the supplied context", warrant)

    def test_autonomy_review_and_sampling_keep_evidence_backed_boundaries(self) -> None:
        # Separate hidden-decision and instrument-failure trials exposed these
        # liabilities. Reconsider only after prospective necessity/liability
        # ablations show that the clauses are redundant or harmful.
        content = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn(
            "Infer only consequence relations entailed by supplied goals and governing constraints",
            content,
        )
        self.assertIn("Do not infer taste, risk tolerance, rights, fairness weights", content)
        self.assertIn("verify every decisive factual premise against trusted evidence", content)
        self.assertIn("Use no universal sample-size minimum or maximum", content)
        self.assertIn("Do not cap alternatives or useful work merely to fit host concurrency", content)
        self.assertIn("prospectively set an initial budget, replacement rule, and stopping rule", content)

    def test_failure_attribution_requires_discriminating_evidence(self) -> None:
        inference = (ROOT / "references" / "inference-and-reporting.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("belongs first to the tested condition", inference)
        self.assertIn("not automatically to either the task or the executor", inference)
        self.assertIn("evidence distinguishes that generator", inference)
        self.assertIn("report the behavioral failure and the attribution limit", inference)

    def test_runtime_has_no_prescribed_benchmark_or_visual_form(self) -> None:
        text_paths = [SKILL_MD, *(ROOT / "references").glob("*.md")]
        runtime = "\n".join(
            path.read_text(encoding="utf-8").lower() for path in text_paths
        )
        forbidden = (
            "evaluation-world",
            "benchmark family",
            "benchmark lineage",
            "six relationships",
            "three runs",
            "three reviewers",
            "required dimensions",
            "radar chart",
            "heatmap",
            "matplotlib",
            "plotly",
            "vega-lite",
            "markdown report is required",
        )
        for phrase in forbidden:
            self.assertNotIn(phrase, runtime)
        self.assertNotRegex(runtime, r"(?:shall|must|required to) (?:use|produce) a (?:score|vector|frontier)")

    def test_runtime_surface_contains_only_structural_helpers(self) -> None:
        scripts = {path.name for path in (ROOT / "scripts").iterdir() if path.is_file()}
        self.assertEqual(scripts, {"split-test", "split-test.ps1"})
        self.assertTrue((ROOT / "scripts" / "split-test").stat().st_mode & 0o111)
        powershell = (ROOT / "scripts" / "split-test.ps1").read_text(encoding="utf-8")
        self.assertIn("$env:OS -eq 'Windows_NT'", powershell)
        self.assertNotIn("$IsWindows", powershell)

    def test_helpers_do_not_launch_or_implement_semantic_judgment(self) -> None:
        custody = help_text("split-test")
        commands = set(
            re.findall(r"^\s+([a-z][a-z-]+)\s", custody, flags=re.MULTILINE)
        )
        self.assertEqual(commands, EXPECTED_COMMANDS)

        view = subprocess.run(
            [str(ROOT / "scripts" / "split-test"), "view", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(view.returncode, 0, view.stderr)
        view_commands = set(
            re.findall(r"^\s+([a-z][a-z-]+)\s", view.stdout, flags=re.MULTILINE)
        )
        self.assertEqual(view_commands, {"receipt", "seal", "serve", "verify"})

    def test_caller_schemas_are_open_and_owned_by_split_testing(self) -> None:
        schema_root = ROOT / "schemas"
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
        self.assertTrue(request["additionalProperties"])
        self.assertTrue(result["additionalProperties"])
        self.assertEqual(
            request["properties"]["schema"]["const"],
            "comparative-evidence-request.v1",
        )
        self.assertEqual(
            result["properties"]["schema"]["const"],
            "comparative-evidence-result.v1",
        )

    def test_caller_design_prohibition_does_not_override_rightful_authority(self) -> None:
        interface = (ROOT / "references" / "caller-interface.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("as caller-chosen comparison design", interface)
        self.assertIn("rightful authority requirement", interface)
        self.assertIn("real deployment or consumer boundary", interface)
        self.assertIn("honor it to the extent of its authority", interface)

    def test_no_fixed_eval_corpus_or_report_template_is_shipped(self) -> None:
        self.assertFalse((ROOT / "evals").exists())
        self.assertFalse((ROOT / "assets").exists())


if __name__ == "__main__":
    unittest.main()
