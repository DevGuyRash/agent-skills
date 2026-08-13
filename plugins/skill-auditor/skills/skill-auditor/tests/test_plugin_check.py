from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT.parents[1]
SCRIPT = ROOT / "scripts" / "plugin_check.sh"

VERDICT_WORDS = ("BLOCKER", "MAJOR", "MINOR", "PASS", "FAIL")

DESCRIPTION = (
    "Check demo things and explain findings. Use when the task involves: "
    "(1) Auditing demo things, (2) Reviewing demo packaging."
)


def run_plugin_check(plugin_dir: Path, *extra: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    completed = subprocess.run(
        ["sh", str(SCRIPT), str(plugin_dir), "--format", "json", *extra],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed, json.loads(completed.stdout)


def make_plugin(
    tmp: str,
    *,
    name: str = "demo-plugin",
    version: str = "1.0.0",
    codex_version: str | None = None,
    description: str = DESCRIPTION,
    codex_description: str | None = None,
    skills: dict[str, str] | None = None,
    license_field: str | None = None,
) -> Path:
    plugin_dir = Path(tmp) / name
    (plugin_dir / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (plugin_dir / ".codex-plugin").mkdir(parents=True, exist_ok=True)

    claude: dict = {"name": name, "version": version, "description": description}
    codex: dict = {
        "name": name,
        "version": codex_version or version,
        "description": codex_description or description,
    }
    if license_field:
        claude["license"] = license_field
        codex["license"] = license_field

    (plugin_dir / ".claude-plugin/plugin.json").write_text(json.dumps(claude, indent=2), encoding="utf-8")
    (plugin_dir / ".codex-plugin/plugin.json").write_text(json.dumps(codex, indent=2), encoding="utf-8")

    for slug, desc in (skills or {"demo-skill": description}).items():
        d = plugin_dir / "skills" / slug
        d.mkdir(parents=True, exist_ok=True)
        title = " ".join(w.capitalize() for w in slug.split("-"))
        (d / "SKILL.md").write_text(
            f"---\nname: {title}\ndescription: >-\n  {desc}\n---\n\n# {title}\n",
            encoding="utf-8",
        )

    return plugin_dir


class ErrorTests(unittest.TestCase):
    """manifest_version_mismatch, manifest_description_mismatch,
    missing_claude_manifest, missing_codex_manifest, no_skills,
    skill_description_mismatch, catalog_version_mismatch, published_but_untracked:
    each has no legitimate reading for any target, so each must fail the run."""

    def test_version_disagreement_between_hosts_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp, version="1.0.0", codex_version="2.0.0")
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("manifest_version_mismatch", {e["code"] for e in data["errors"]})

    def test_description_disagreement_between_hosts_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp, codex_description="Something else entirely.")
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("manifest_description_mismatch", {e["code"] for e in data["errors"]})

    def test_manifest_and_single_skill_must_agree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp, skills={"demo-skill": "A different description entirely."})
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("skill_description_mismatch", {e["code"] for e in data["errors"]})

    def test_a_missing_codex_manifest_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp)
            (plugin / ".codex-plugin/plugin.json").unlink()
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("missing_codex_manifest", {e["code"] for e in data["errors"]})

    def test_a_missing_claude_manifest_fails(self) -> None:
        # The sibling of the Codex case. Both host manifests are required, so
        # testing only one leaves the other free to regress unnoticed.
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp)
            (plugin / ".claude-plugin/plugin.json").unlink()
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("missing_claude_manifest", {e["code"] for e in data["errors"]})

    def test_no_bundled_skills_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_dir = Path(tmp) / "empty-plugin"
            (plugin_dir / ".claude-plugin").mkdir(parents=True)
            (plugin_dir / ".codex-plugin").mkdir(parents=True)
            manifest = {"name": "empty-plugin", "version": "1.0.0", "description": DESCRIPTION}
            (plugin_dir / ".claude-plugin/plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
            (plugin_dir / ".codex-plugin/plugin.json").write_text(json.dumps(manifest), encoding="utf-8")

            completed, data = run_plugin_check(plugin_dir)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("no_skills", {e["code"] for e in data["errors"]})

    def test_a_target_with_an_error_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp, version="1.0.0", codex_version="2.0.0")
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 1)
        self.assertGreater(data["error_count"], 0)


class EncodingTests(unittest.TestCase):
    def test_a_json_escaped_dash_does_not_read_as_drift(self) -> None:
        # JSON stores non-ASCII as \uXXXX while YAML carries the literal bytes.
        # Without folding both, every description holding an em-dash would be
        # reported as drifted from itself.
        desc = "Check demo things — and explain. Use when the task involves: (1) Auditing, (2) Reviewing."
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp, description=desc, skills={"demo-skill": desc})
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0, data["errors"])


class RoutingTests(unittest.TestCase):
    def test_a_one_way_routing_edge_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(
                tmp,
                skills={
                    "demo-log": "Log things. Do not use for mending (that is demo-mend).",
                    "demo-mend": "Mend things. Use when the task involves: (1) Mending, (2) Closing.",
                },
            )
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertIn("one_way_routing_edge", {o["code"] for o in data["observations"]})

    def test_reciprocal_edges_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(
                tmp,
                skills={
                    "demo-log": "Log things. Do not use for mending (that is demo-mend).",
                    "demo-mend": "Mend things. Do not use for logging (that is demo-log).",
                },
            )
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 0)
        self.assertNotIn("one_way_routing_edge", {o["code"] for o in data["observations"]})

    def test_multi_skill_plugins_skip_the_single_skill_comparison(self) -> None:
        # A manifest description cannot equal two different skill descriptions.
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(
                tmp,
                skills={"demo-a": "Do A things always.", "demo-b": "Do B things always."},
            )
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 0)
        self.assertNotIn("skill_description_mismatch", {e["code"] for e in data["errors"]})
        self.assertEqual(data["skills"], 2)


class CatalogTests(unittest.TestCase):
    def _catalog(self, tmp: str, name: str, version: str | None) -> Path:
        # A description containing a comma is the case that breaks naive parsing.
        entry: dict = {
            "name": name,
            "source": f"./plugins/{name}",
            "description": "Compile bounded, verifiable things.",
        }
        if version is not None:
            entry["version"] = version
        cat = Path(tmp) / "marketplace.json"
        cat.write_text(
            json.dumps({"name": "demo", "plugins": [entry]}, indent=2),
            encoding="utf-8",
        )
        return cat

    def test_catalog_version_drift_is_found_past_a_comma(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp, version="2.0.0")
            cat = self._catalog(tmp, "demo-plugin", "1.8.1")
            completed, data = run_plugin_check(plugin, "--marketplace", str(cat))

        self.assertEqual(completed.returncode, 1)
        self.assertIn("catalog_version_mismatch", {e["code"] for e in data["errors"]})

    def test_matching_catalog_version_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp, version="2.0.0")
            cat = self._catalog(tmp, "demo-plugin", "2.0.0")
            completed, data = run_plugin_check(plugin, "--marketplace", str(cat))

        self.assertEqual(completed.returncode, 0)
        self.assertNotIn("catalog_version_mismatch", {e["code"] for e in data["errors"]})

    def test_an_unpublished_plugin_is_observed_not_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp)
            cat = self._catalog(tmp, "some-other-plugin", "1.0.0")
            completed, data = run_plugin_check(plugin, "--marketplace", str(cat))

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertIn("not_published", {o["code"] for o in data["observations"]})

    def test_catalog_entry_without_a_version_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp)
            cat = self._catalog(tmp, "demo-plugin", None)
            completed, data = run_plugin_check(plugin, "--marketplace", str(cat))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("catalog_no_version", {o["code"] for o in data["observations"]})


class LicenseTests(unittest.TestCase):
    def test_declared_license_without_a_file_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp, license_field="MIT")
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertIn("license_without_file", {o["code"] for o in data["observations"]})


class UncheckedSurfaceTests(unittest.TestCase):
    def test_surfaces_that_cannot_be_located_are_named_not_passed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp)
            completed, data = run_plugin_check(plugin, "--installed", str(Path(tmp) / "nowhere"))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("install", data["unchecked"])


class CleanTargetTests(unittest.TestCase):
    def test_a_coherent_plugin_has_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp)
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertEqual(data["observation_count"], 0)
        self.assertEqual(data["skills"], 1)

    def test_active_plugin_passes(self) -> None:
        completed, data = run_plugin_check(PLUGIN_ROOT)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)


class ObservationsOnlyExitTests(unittest.TestCase):
    def test_a_target_whose_only_findings_are_observations_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(
                tmp,
                license_field="MIT",
                skills={
                    "demo-log": "Log things. Do not use for mending (that is demo-mend).",
                    "demo-mend": "Mend things. Use when the task involves: (1) Mending, (2) Closing.",
                },
            )
            completed, data = run_plugin_check(plugin)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(data["error_count"], 0)
        self.assertGreater(data["observation_count"], 0)


class SourceTagTests(unittest.TestCase):
    def test_every_observation_source_is_open_standard_or_repo_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(
                tmp,
                license_field="MIT",
                skills={
                    "demo-log": "Log things. Do not use for mending (that is demo-mend).",
                    "demo-mend": "Mend things. Use when the task involves: (1) Mending, (2) Closing.",
                },
            )

            completed, data = run_plugin_check(plugin)

        self.assertGreater(data["observation_count"], 0)
        for obs in data["observations"]:
            if "source" in obs:
                self.assertIn(obs["source"], {"open-standard", "repo-overlay"})


class VerdictVocabularyTests(unittest.TestCase):
    def test_no_severity_or_verdict_words_appear(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            observation_plugin = make_plugin(tmp, name="observation-plugin", license_field="MIT")
            error_plugin = make_plugin(tmp, name="error-plugin", version="1.0.0", codex_version="2.0.0")

            runs = [
                subprocess.run(
                    ["sh", str(SCRIPT), str(d), "--format", fmt],
                    capture_output=True, text=True, check=False,
                )
                for d in (observation_plugin, error_plugin)
                for fmt in ("json", "text")
            ]

        for completed in runs:
            for word in VERDICT_WORDS:
                self.assertNotIn(word, completed.stdout)
                self.assertNotIn(word, completed.stderr)


class UsageExitTests(unittest.TestCase):
    def test_unusable_input_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = make_plugin(tmp)

            bad_flag = subprocess.run(
                ["sh", str(SCRIPT), str(plugin), "--nope"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(bad_flag.returncode, 2)

            bad_format = subprocess.run(
                ["sh", str(SCRIPT), str(plugin), "--format", "xml"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(bad_format.returncode, 2)
            self.assertIn("hint:", bad_format.stderr)

        missing_dir = subprocess.run(
            ["sh", str(SCRIPT), "/tmp/definitely-not-a-real-plugin-dir-xyz"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(missing_dir.returncode, 2)


class TaxonomySortTests(unittest.TestCase):
    """The governing rule: an error has no legitimate reading for any target; an
    observation's significance depends on the target. This pins the script's
    error/observation sort exactly, so a code silently moved between buckets --
    or a new one added to neither list -- fails here."""

    @staticmethod
    def _codes(function_name: str) -> set[str]:
        text = SCRIPT.read_text(encoding="utf-8")
        return set(re.findall(rf'\b{function_name}\s+"([a-z0-9_]+)"', text))

    def test_error_codes_match_the_governing_sort(self) -> None:
        self.assertEqual(
            self._codes("error"),
            {
                "missing_claude_manifest",
                "missing_codex_manifest",
                "no_skills",
                "manifest_version_mismatch",
                "manifest_description_mismatch",
                "skill_description_mismatch",
                "catalog_version_mismatch",
                "published_but_untracked",
            },
        )

    def test_observation_codes_match_the_governing_sort(self) -> None:
        self.assertEqual(
            self._codes("observe"),
            {
                "install_drift",
                "license_without_file",
                "one_way_routing_edge",
                "not_published",
                "catalog_no_version",
            },
        )


if __name__ == "__main__":
    unittest.main()
