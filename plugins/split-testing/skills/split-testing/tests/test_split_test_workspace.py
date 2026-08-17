from __future__ import annotations

import fcntl
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "split_test_workspace.py"


def run_helper(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def parse_json(completed: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(completed.stdout)


class WorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="split-testing-")
        self.base = Path(self.temporary.name)
        self.root = self.base / "workspace with spaces"
        self.plan = self.base / "round.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_plan(
        self,
        *,
        round_id: str = "round-one",
        runs: list[dict] | None = None,
        review_sets: list[dict] | None = None,
    ) -> None:
        if runs is None:
            runs = [
                {
                    "id": "alpha-run-1",
                    "condition": "secret alpha condition",
                    "case": "shared-case",
                    "metadata": {"model": "model-a", "effort": "high"},
                },
                {
                    "id": "beta-run-1",
                    "condition": "secret beta condition",
                    "case": "shared-case",
                    "metadata": {"model": "model-a", "effort": "high"},
                },
                {
                    "id": "alpha-run-2",
                    "condition": "secret alpha condition",
                    "case": "second-case",
                },
            ]
        if review_sets is None:
            review_sets = [
                {
                    "id": "overall-quality",
                    "candidates": [
                        {
                            "id": "alpha bundle",
                            "runs": ["alpha-run-1", "alpha-run-2"],
                        },
                        {"id": "beta bundle", "runs": ["beta-run-1"]},
                    ],
                    "reviewers": [
                        {
                            "id": "judge-one",
                            "metadata": {"model": "review-model-a", "effort": "max"},
                        },
                        {
                            "id": "judge-two",
                            "metadata": {"model": "review-model-b", "effort": "high"},
                        },
                    ],
                },
                {
                    "id": "specialist-check",
                    "candidates": [
                        {"id": "alpha one", "runs": ["alpha-run-1"]},
                        {"id": "beta one", "runs": ["beta-run-1"]},
                    ],
                    "reviewers": [{"id": "specialist"}],
                },
            ]
        self.plan.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "round_id": round_id,
                    "runs": runs,
                    "review_sets": review_sets,
                    "metadata": {"purpose": "private controller note"},
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def init(self) -> None:
        completed = run_helper("init", str(self.root))
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def add_round(self) -> dict:
        self.write_plan()
        completed = run_helper("add-round", str(self.root), str(self.plan))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return parse_json(completed)

    def assignments(self, round_id: str = "round-one") -> dict:
        completed = run_helper("assignments", str(self.root), round_id)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return parse_json(completed)

    def populate(self) -> dict:
        assignments = self.assignments()
        for run in assignments["runs"]:
            workspace = Path(run["workspace"])
            (workspace / "input" / "task.md").write_text(
                "Complete the assigned work.\n", encoding="utf-8"
            )
            (workspace / "artifact" / "result.txt").write_text(
                f"artifact from {run['id']}\n", encoding="utf-8"
            )
            Path(run["record_dir"]).joinpath("run.json").write_text(
                json.dumps({"elapsed_ms": 10}) + "\n", encoding="utf-8"
            )
        for review in assignments["reviews"]:
            Path(review["material_dir"]).joinpath("brief.md").write_text(
                "Choose the result that best serves the supplied objective.\n",
                encoding="utf-8",
            )
        return assignments

    def test_init_requires_an_explicit_empty_absolute_root(self) -> None:
        relative = run_helper("init", "relative/path")
        self.assertEqual(relative.returncode, 2)
        self.assertIn("absolute", relative.stderr)

        self.root.mkdir()
        (self.root / "occupied").write_text("x\n", encoding="utf-8")
        occupied = run_helper("init", str(self.root))
        self.assertEqual(occupied.returncode, 2)
        self.assertIn("empty", occupied.stderr)

    def test_init_creates_private_controller_state(self) -> None:
        self.init()

        self.assertEqual(self.root.stat().st_mode & 0o777, 0o700)
        self.assertTrue((self.root / ".split-testing" / "experiment.json").is_file())
        status = run_helper("status", str(self.root))
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertEqual(parse_json(status)["rounds"], [])

    def test_add_round_supports_arbitrary_runs_bundles_and_reviewers(self) -> None:
        self.init()
        summary = self.add_round()
        assignments = self.assignments()

        self.assertEqual(summary["run_count"], 3)
        self.assertEqual(summary["review_set_count"], 2)
        self.assertEqual(summary["reviewer_count"], 3)
        self.assertEqual(len(assignments["runs"]), 3)
        self.assertEqual(len(assignments["reviews"]), 3)
        self.assertEqual(
            assignments["runs"][0]["metadata"],
            {"model": "model-a", "effort": "high"},
        )

    def test_executor_visible_paths_are_opaque(self) -> None:
        self.init()
        completed = self.add_round()
        assignments = self.assignments()
        secrets = {
            "alpha-run-1",
            "beta-run-1",
            "alpha-run-2",
            "secret alpha condition",
            "secret beta condition",
            "shared-case",
            "second-case",
            "judge-one",
            "judge-two",
            "specialist",
        }

        self.assertTrue(secrets.isdisjoint(completed.keys()))
        public_output = json.dumps(completed)
        status_output = run_helper("status", str(self.root)).stdout
        for secret in secrets:
            self.assertNotIn(secret, public_output)
            self.assertNotIn(secret, status_output)

        for run in assignments["runs"]:
            workspace = Path(run["workspace"])
            self.assertEqual(workspace.parent.name, "workspaces")
            self.assertRegex(workspace.name, r"^[0-9a-f]{32}$")
            for secret in secrets:
                self.assertNotIn(secret, str(workspace))

        for review in assignments["reviews"]:
            self.assertRegex(Path(review["material_dir"]).name, r"^[0-9a-f]{32}$")
            self.assertRegex(Path(review["view_dir"]).name, r"^[0-9a-f]{32}$")

    def test_assignments_is_the_explicit_private_mapping_surface(self) -> None:
        self.init()
        self.add_round()
        assignments = self.assignments()

        by_id = {run["id"]: run for run in assignments["runs"]}
        self.assertEqual(by_id["alpha-run-1"]["condition"], "secret alpha condition")
        self.assertEqual(by_id["alpha-run-1"]["case"], "shared-case")
        self.assertTrue(Path(by_id["alpha-run-1"]["record_dir"]).is_dir())

    def test_anonymize_preflights_the_entire_round_before_writing_views(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        Path(assignments["runs"][1]["workspace"]).joinpath(
            "artifact", "result.txt"
        ).unlink()

        completed = run_helper("anonymize", str(self.root), "round-one")

        self.assertEqual(completed.returncode, 1)
        self.assertIn("artifact", completed.stderr)
        for review in assignments["reviews"]:
            self.assertFalse(Path(review["view_dir"]).exists())
        self.assertEqual(self.assignments()["state"], "open")

    def test_anonymize_preserves_contained_relative_symlinks(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        artifact = Path(assignments["runs"][0]["workspace"]) / "artifact"
        (artifact / "nested").mkdir()
        os.symlink("../result.txt", artifact / "nested" / "alias")
        os.symlink("nested", artifact / "linked-directory")

        anonymized = run_helper("anonymize", str(self.root), "round-one")

        self.assertEqual(anonymized.returncode, 0, anonymized.stderr)
        copied_links = [
            path
            for review in assignments["reviews"]
            for path in Path(review["view_dir"]).joinpath("candidates").glob(
                "*/*/nested/alias"
            )
            if path.is_symlink()
        ]
        self.assertTrue(copied_links)
        for copied in copied_links:
            self.assertEqual(os.readlink(copied), "../result.txt")
            self.assertEqual(
                copied.read_text(encoding="utf-8"),
                "artifact from alpha-run-1\n",
            )

        for review in assignments["reviews"]:
            Path(review["view_dir"]).joinpath("judgment.md").write_text(
                "Committed judgment.\n", encoding="utf-8"
            )
        (artifact / "nested" / "alias").unlink()
        os.symlink("../different.txt", artifact / "nested" / "alias")
        changed = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(changed.returncode, 1)
        self.assertIn("changed after anonymization", changed.stderr)

    def test_anonymize_rejects_escaping_symlinks_and_special_files(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        artifact = Path(assignments["runs"][0]["workspace"]) / "artifact"
        os.symlink("../outside.txt", artifact / "escape")

        escaped = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(escaped.returncode, 1)
        self.assertIn("escapes copied tree", escaped.stderr)

        (artifact / "escape").unlink()
        os.symlink(self.base / "outside.txt", artifact / "escape")
        absolute = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(absolute.returncode, 1)
        self.assertIn("escapes copied tree", absolute.stderr)

        (artifact / "escape").unlink()
        os.mkfifo(artifact / "stream")
        special = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(special.returncode, 1)
        self.assertIn("special file", special.stderr)

    def test_anonymize_rejects_a_symlinked_workspace_ancestor(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        workspace = Path(assignments["runs"][0]["workspace"])
        outside = self.base / "outside execution"
        (outside / "artifact").mkdir(parents=True)
        (outside / "artifact" / "result.txt").write_text(
            "outside artifact\n", encoding="utf-8"
        )
        shutil.rmtree(workspace)
        os.symlink(outside, workspace)

        completed = run_helper("anonymize", str(self.root), "round-one")

        self.assertEqual(completed.returncode, 1)
        self.assertIn("symbolic link", completed.stderr)
        for review in assignments["reviews"]:
            self.assertFalse(Path(review["view_dir"]).exists())
        self.assertEqual(
            (outside / "artifact" / "result.txt").read_text(encoding="utf-8"),
            "outside artifact\n",
        )

    def test_anonymize_creates_independent_blind_views_and_preserves_content(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()

        completed = run_helper("anonymize", str(self.root), "round-one")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(self.assignments()["state"], "anonymized")
        for review in assignments["reviews"]:
            view = Path(review["view_dir"])
            self.assertEqual(
                (view / "brief" / "brief.md").read_text(encoding="utf-8"),
                "Choose the result that best serves the supplied objective.\n",
            )
            labels = sorted(path.name for path in (view / "candidates").iterdir())
            self.assertEqual(labels, ["A", "B"])
            observed = {
                path.read_text(encoding="utf-8")
                for path in (view / "candidates").glob("*/*/result.txt")
            }
            self.assertTrue(observed)
            self.assertTrue(
                observed.issubset(
                    {
                        "artifact from alpha-run-1\n",
                        "artifact from alpha-run-2\n",
                        "artifact from beta-run-1\n",
                    }
                )
            )

    def test_candidate_labels_extend_beyond_z(self) -> None:
        runs = [
            {"id": f"run-{index}", "condition": f"condition-{index}"}
            for index in range(28)
        ]
        candidates = [
            {"id": f"candidate-{index}", "runs": [f"run-{index}"]}
            for index in range(28)
        ]
        reviews = [
            {
                "id": "large-list",
                "candidates": candidates,
                "reviewers": [{"id": "one-reviewer"}],
            }
        ]
        self.write_plan(runs=runs, review_sets=reviews)
        self.init()
        added = run_helper("add-round", str(self.root), str(self.plan))
        self.assertEqual(added.returncode, 0, added.stderr)
        assignments = self.assignments()
        for run in assignments["runs"]:
            Path(run["workspace"]).joinpath("artifact", "result.txt").write_text(
                "result\n", encoding="utf-8"
            )
        Path(assignments["reviews"][0]["material_dir"]).joinpath("brief.md").write_text(
            "Compare all candidates.\n", encoding="utf-8"
        )

        completed = run_helper("anonymize", str(self.root), "round-one")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        labels = {
            path.name
            for path in Path(assignments["reviews"][0]["view_dir"])
            .joinpath("candidates")
            .iterdir()
        }
        self.assertEqual(len(labels), 28)
        self.assertIn("Z", labels)
        self.assertIn("AA", labels)
        self.assertIn("AB", labels)

    def test_cased_samples_preserve_opaque_n_way_blocks_and_repetitions(self) -> None:
        runs = [
            {"id": "a-x-1", "condition": "a", "case": "case-x"},
            {"id": "a-x-2", "condition": "a", "case": "case-x"},
            {"id": "a-y", "condition": "a", "case": "case-y"},
            {"id": "a-null", "condition": "a", "case": None},
            {"id": "b-x", "condition": "b", "case": "case-x"},
            {"id": "b-y-1", "condition": "b", "case": "case-y"},
            {"id": "b-y-2", "condition": "b", "case": "case-y"},
            {"id": "b-null", "condition": "b", "case": None},
            {"id": "c-x", "condition": "c", "case": "case-x"},
            {"id": "c-z", "condition": "c", "case": "unmatched-case-z"},
            {"id": "shared-null", "condition": "shared", "case": None},
        ]
        review_sets = [
            {
                "id": "n-way",
                "candidates": [
                    {
                        "id": "candidate-a",
                        "runs": [
                            "a-x-1",
                            "a-x-2",
                            "a-y",
                            "a-null",
                            "shared-null",
                        ],
                    },
                    {
                        "id": "candidate-b",
                        "runs": ["b-x", "b-y-1", "b-y-2", "b-null"],
                    },
                    {
                        "id": "candidate-c",
                        "runs": ["c-x", "c-z", "shared-null"],
                    },
                ],
                "reviewers": [
                    {"id": "reviewer-one"},
                    {"id": "reviewer-two"},
                    {"id": "reviewer-three"},
                ],
            }
        ]
        self.write_plan(runs=runs, review_sets=review_sets)
        self.init()
        added = run_helper("add-round", str(self.root), str(self.plan))
        self.assertEqual(added.returncode, 0, added.stderr)
        assignments = self.populate()
        anonymized = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(anonymized.returncode, 0, anonymized.stderr)
        for review in assignments["reviews"]:
            Path(review["view_dir"]).joinpath("judgment.md").write_text(
                "Committed judgment.\n", encoding="utf-8"
            )

        revealed = run_helper("reveal", str(self.root), "round-one")

        self.assertEqual(revealed.returncode, 0, revealed.stderr)
        result = parse_json(revealed)
        mapping = json.loads(Path(result["mapping_path"]).read_text(encoding="utf-8"))
        run_case = {run["id"]: run.get("case") for run in runs}
        reviewer_case_maps: list[tuple[tuple[str, str], ...]] = []
        for review in mapping["reviews"]:
            labels_by_occurrence = {
                (candidate["candidate_id"], sample["run_id"]): sample["label"]
                for candidate in review["candidates"]
                for sample in candidate["samples"]
            }
            self.assertEqual(
                {run_id for _, run_id in labels_by_occurrence}, set(run_case)
            )
            for label in labels_by_occurrence.values():
                self.assertRegex(label, r"^B[0-9]{3,}-S[0-9]{3,}$")

            blocks_by_case: dict[str, set[str]] = {}
            for (_, run_id), label in labels_by_occurrence.items():
                case = run_case[run_id]
                if case is not None:
                    blocks_by_case.setdefault(case, set()).add(
                        label.split("-", 1)[0]
                    )
            self.assertTrue(all(len(blocks) == 1 for blocks in blocks_by_case.values()))
            case_blocks = {case: next(iter(blocks)) for case, blocks in blocks_by_case.items()}
            self.assertEqual(len(set(case_blocks.values())), len(case_blocks))
            self.assertEqual(
                {
                    labels_by_occurrence[("candidate-a", "a-x-1")],
                    labels_by_occurrence[("candidate-a", "a-x-2")],
                },
                {
                    f'{case_blocks["case-x"]}-S001',
                    f'{case_blocks["case-x"]}-S002',
                },
            )
            self.assertEqual(
                {
                    labels_by_occurrence[("candidate-b", "b-y-1")],
                    labels_by_occurrence[("candidate-b", "b-y-2")],
                },
                {
                    f'{case_blocks["case-y"]}-S001',
                    f'{case_blocks["case-y"]}-S002',
                },
            )
            null_blocks = {
                labels_by_occurrence[("candidate-a", "a-null")].split("-", 1)[0],
                labels_by_occurrence[("candidate-b", "b-null")].split("-", 1)[0],
                labels_by_occurrence[("candidate-a", "shared-null")].split(
                    "-", 1
                )[0],
                labels_by_occurrence[("candidate-c", "shared-null")].split(
                    "-", 1
                )[0],
            }
            self.assertEqual(len(null_blocks), 4)
            self.assertTrue(null_blocks.isdisjoint(case_blocks.values()))
            reviewer_case_maps.append(tuple(sorted(case_blocks.items())))

            view = next(
                Path(item["view_dir"])
                for item in assignments["reviews"]
                if item["reviewer_id"] == review["reviewer_id"]
            )
            self.assertEqual(
                {path.name for path in view.iterdir() if path.is_file()},
                {"judgment.md"},
            )

        self.assertEqual(len(reviewer_case_maps), 3)

    def test_reviewer_block_namespace_is_reshuffled_for_each_presentation(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "split_test_workspace_block_shuffle", SCRIPT
        )
        assert spec is not None and spec.loader is not None
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)

        review_set = {
            "candidates": [
                {"id": "a", "runs": ["a-x", "a-y", "a-z"]},
                {"id": "b", "runs": ["b-x", "b-y", "b-z"]},
            ]
        }
        run_by_id = {
            "a-x": {"case": "x"},
            "a-y": {"case": "y"},
            "a-z": {"case": "z"},
            "b-x": {"case": "x"},
            "b-y": {"case": "y"},
            "b-z": {"case": "z"},
        }

        class AlternatingBlockShuffle:
            def __init__(self) -> None:
                self.block_calls = 0

            def shuffle(self, values: list[Any]) -> None:
                if values and isinstance(values[0], tuple):
                    if self.block_calls % 2:
                        values.reverse()
                    self.block_calls += 1

        random = AlternatingBlockShuffle()
        first = helper.reviewer_samples(review_set, run_by_id, random)
        second = helper.reviewer_samples(review_set, run_by_id, random)

        def case_blocks(presentation: dict[str, list[dict[str, str]]]) -> dict[str, str]:
            return {
                run_by_id[sample["run_id"]]["case"]: sample["label"].split("-", 1)[0]
                for samples in presentation.values()
                for sample in samples
            }

        self.assertNotEqual(case_blocks(first), case_blocks(second))
        self.assertEqual(random.block_calls, 2)

    def test_uncased_review_sets_keep_sample_labels(self) -> None:
        runs = [
            {"id": "a-1", "condition": "a"},
            {"id": "a-2", "condition": "a", "case": None},
            {"id": "b-1", "condition": "b"},
        ]
        review_sets = [
            {
                "id": "uncased",
                "candidates": [
                    {"id": "candidate-a", "runs": ["a-1", "a-2"]},
                    {"id": "candidate-b", "runs": ["b-1"]},
                ],
                "reviewers": [{"id": "reviewer"}],
            }
        ]
        self.write_plan(runs=runs, review_sets=review_sets)
        self.init()
        added = run_helper("add-round", str(self.root), str(self.plan))
        self.assertEqual(added.returncode, 0, added.stderr)
        assignments = self.populate()

        anonymized = run_helper("anonymize", str(self.root), "round-one")

        self.assertEqual(anonymized.returncode, 0, anonymized.stderr)
        candidates = Path(assignments["reviews"][0]["view_dir"]) / "candidates"
        labels = {
            path.name
            for candidate in candidates.iterdir()
            for path in candidate.iterdir()
        }
        self.assertEqual(labels, {"S001", "S002"})

    def test_cased_mapping_rejects_a_valid_shaped_alignment_mutation(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        anonymized = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(anonymized.returncode, 0, anonymized.stderr)
        mapping_path = Path(assignments["mapping_path"])
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        review = next(
            item for item in mapping["reviews"] if item["review_set_id"] == "overall-quality"
        )
        alpha = next(
            item for item in review["candidates"] if item["candidate_id"] == "alpha bundle"
        )
        shared = next(
            item for item in alpha["samples"] if item["run_id"] == "alpha-run-1"
        )
        second = next(
            item for item in alpha["samples"] if item["run_id"] == "alpha-run-2"
        )
        shared["label"], second["label"] = second["label"], shared["label"]
        alpha["samples"].sort(key=lambda item: item["label"])
        mapping_path.write_text(
            json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        state_path = self.root / ".split-testing" / "experiment.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["rounds"][0]["mapping_sha256"] = __import__("hashlib").sha256(
            mapping_path.read_bytes()
        ).hexdigest()
        state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        rejected = run_helper("reveal", str(self.root), "round-one")

        self.assertEqual(rejected.returncode, 1)
        self.assertIn("private mapping is malformed", rejected.stderr)

    def test_reveal_reads_legacy_flat_labels_for_an_already_anonymized_cased_set(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        anonymized = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(anonymized.returncode, 0, anonymized.stderr)

        spec = importlib.util.spec_from_file_location(
            "split_test_workspace_legacy_fixture", SCRIPT
        )
        assert spec is not None and spec.loader is not None
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        mapping_path = Path(assignments["mapping_path"])
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        state_path = self.root / ".split-testing" / "experiment.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        round_record = state["rounds"][0]
        reviewer_tokens = {
            (review_set["id"], reviewer["id"]): reviewer["view_token"]
            for review_set in round_record["review_sets"]
            for reviewer in review_set["reviewers"]
        }
        for review in mapping["reviews"]:
            view = Path(review["view_dir"])
            for candidate in review["candidates"]:
                candidate_root = view / "candidates" / candidate["label"]
                for index, sample in enumerate(candidate["samples"], start=1):
                    old_label = f"S{index:03d}"
                    (candidate_root / sample["label"]).rename(candidate_root / old_label)
                    sample["label"] = old_label
            view_token = reviewer_tokens[
                (review["review_set_id"], review["reviewer_id"])
            ]
            mapping["copy_hashes"][view_token]["candidates"] = helper.scan_regular_tree(
                view / "candidates", "legacy blinded candidates", self.root
            )
        mapping_path.write_text(
            json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        round_record["mapping_sha256"] = __import__("hashlib").sha256(
            mapping_path.read_bytes()
        ).hexdigest()
        state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        for review in assignments["reviews"]:
            Path(review["view_dir"]).joinpath("judgment.md").write_text(
                "Committed judgment.\n", encoding="utf-8"
            )

        revealed = run_helper("reveal", str(self.root), "round-one")

        self.assertEqual(revealed.returncode, 0, revealed.stderr)

    def test_controller_can_counterbalance_candidate_order(self) -> None:
        runs = [
            {"id": "run-a", "condition": "condition-a"},
            {"id": "run-b", "condition": "condition-b"},
        ]
        review_sets = [
            {
                "id": "position-check",
                "candidates": [
                    {"id": "candidate-a", "runs": ["run-a"]},
                    {"id": "candidate-b", "runs": ["run-b"]},
                ],
                "reviewers": [
                    {
                        "id": "reviewer-one",
                        "candidate_order": ["candidate-a", "candidate-b"],
                    },
                    {
                        "id": "reviewer-two",
                        "candidate_order": ["candidate-b", "candidate-a"],
                    },
                ],
            }
        ]
        self.write_plan(runs=runs, review_sets=review_sets)
        self.init()
        added = run_helper("add-round", str(self.root), str(self.plan))
        self.assertEqual(added.returncode, 0, added.stderr)
        assignments = self.populate()
        anonymized = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(anonymized.returncode, 0, anonymized.stderr)
        for review in assignments["reviews"]:
            Path(review["view_dir"]).joinpath("judgment.md").write_text(
                "Committed judgment.\n", encoding="utf-8"
            )

        revealed = run_helper("reveal", str(self.root), "round-one")

        self.assertEqual(revealed.returncode, 0, revealed.stderr)
        result = parse_json(revealed)
        mapping = json.loads(Path(result["mapping_path"]).read_text(encoding="utf-8"))
        by_reviewer = {item["reviewer_id"]: item for item in mapping["reviews"]}
        self.assertEqual(
            [item["candidate_id"] for item in by_reviewer["reviewer-one"]["candidates"]],
            ["candidate-a", "candidate-b"],
        )
        self.assertEqual(
            [item["candidate_id"] for item in by_reviewer["reviewer-two"]["candidates"]],
            ["candidate-b", "candidate-a"],
        )

    def test_reveal_requires_every_judgment_and_detects_tampering(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        anonymized = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(anonymized.returncode, 0, anonymized.stderr)

        blocked = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(blocked.returncode, 1)
        self.assertIn("judgment", blocked.stderr)

        for review in assignments["reviews"]:
            Path(review["view_dir"]).joinpath("judgment.md").write_text(
                "Committed judgment.\n", encoding="utf-8"
            )
        tampered_file = next(
            Path(assignments["reviews"][0]["view_dir"])
            .joinpath("candidates")
            .glob("*/*/result.txt")
        )
        original = tampered_file.read_text(encoding="utf-8")
        tampered_file.write_text("tampered\n", encoding="utf-8")
        tampered = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(tampered.returncode, 1)
        self.assertIn("changed after anonymization", tampered.stderr)

        tampered_file.write_text(original, encoding="utf-8")
        revealed = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(revealed.returncode, 0, revealed.stderr)
        result = parse_json(revealed)
        mapping = json.loads(Path(result["mapping_path"]).read_text(encoding="utf-8"))
        self.assertEqual(result["round_id"], "round-one")
        self.assertEqual(result["state"], "revealed")
        self.assertEqual(result["review_count"], 3)
        self.assertEqual(len(mapping["reviews"]), 3)
        self.assertEqual(self.assignments()["state"], "revealed")

    def test_reveal_rejects_noncommitted_judgment_files(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        anonymized = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(anonymized.returncode, 0, anonymized.stderr)

        for review in assignments["reviews"]:
            Path(review["view_dir"]).joinpath("judgment.md").write_text(
                "   \n", encoding="utf-8"
            )
        whitespace = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(whitespace.returncode, 1)
        self.assertIn("judgment is empty", whitespace.stderr)

        for review in assignments["reviews"]:
            Path(review["view_dir"]).joinpath("judgment.md").write_text(
                "Committed judgment.\n", encoding="utf-8"
            )
        first = Path(assignments["reviews"][0]["view_dir"]) / "judgment.md"
        first.unlink()
        os.symlink(Path(assignments["reviews"][0]["view_dir"]) / "brief" / "brief.md", first)
        symlinked = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(symlinked.returncode, 1)
        self.assertIn("regular file", symlinked.stderr)

    def test_reveal_preserves_the_exact_blind_judgments(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        anonymized = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(anonymized.returncode, 0, anonymized.stderr)
        expected = {}
        for index, review in enumerate(assignments["reviews"], start=1):
            text = f"Judgment {index} with material reasons.\n"
            expected[review["reviewer_id"]] = text
            Path(review["view_dir"]).joinpath("judgment.md").write_text(
                text, encoding="utf-8"
            )

        revealed = run_helper("reveal", str(self.root), "round-one")

        self.assertEqual(revealed.returncode, 0, revealed.stderr)
        result = parse_json(revealed)
        snapshot_path = Path(result["judgments_path"])
        self.assertEqual(snapshot_path, Path(assignments["judgments_path"]))
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        self.assertEqual(
            {item["reviewer_id"]: item["text"] for item in snapshot["reviews"]},
            expected,
        )
        self.assertEqual(
            result["judgments_sha256"],
            __import__("hashlib").sha256(snapshot_path.read_bytes()).hexdigest(),
        )

        changed = Path(assignments["reviews"][0]["view_dir"]) / "judgment.md"
        changed.chmod(0o600)
        changed.write_text("Identity-informed replacement.\n", encoding="utf-8")
        rereveal = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(rereveal.returncode, 1)
        self.assertIn("changed after commitment", rereveal.stderr)

    def test_tree_integrity_preserves_empty_directories_and_full_modes(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        source = Path(assignments["runs"][0]["workspace"]) / "artifact"
        (source / "empty" / "nested").mkdir(parents=True)
        result = source / "result.txt"
        result.chmod(0o744)
        for review in assignments["reviews"]:
            Path(review["material_dir"]).joinpath("brief.md").chmod(0o640)

        anonymized = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(anonymized.returncode, 0, anonymized.stderr)
        copied_results = [
            path
            for review in assignments["reviews"]
            for path in Path(review["view_dir"]).joinpath("candidates").glob(
                "*/*/result.txt"
            )
            if path.read_text(encoding="utf-8") == "artifact from alpha-run-1\n"
        ]
        self.assertTrue(copied_results)
        for copied in copied_results:
            self.assertTrue((copied.parent / "empty" / "nested").is_dir())
            self.assertEqual(copied.stat().st_mode & 0o7777, 0o744)
        for review in assignments["reviews"]:
            copied_brief = Path(review["view_dir"]) / "brief" / "brief.md"
            self.assertEqual(copied_brief.stat().st_mode & 0o7777, 0o640)
        for review in assignments["reviews"]:
            Path(review["view_dir"]).joinpath("judgment.md").write_text(
                "Committed judgment.\n", encoding="utf-8"
            )

        result.chmod(0o644)
        changed_mode = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(changed_mode.returncode, 1)
        self.assertIn("changed after anonymization", changed_mode.stderr)
        result.chmod(0o744)

        copied_results[0].chmod(0o700)
        changed_copy_mode = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(changed_copy_mode.returncode, 1)
        self.assertIn("changed after anonymization", changed_copy_mode.stderr)
        copied_results[0].chmod(0o744)

        (source / "empty" / "nested").rmdir()
        removed_directory = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(removed_directory.returncode, 1)
        self.assertIn("changed after anonymization", removed_directory.stderr)
        (source / "empty" / "nested").mkdir()

        extra = copied_results[0].parent / "unexpected-empty"
        extra.mkdir()
        changed_copy = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(changed_copy.returncode, 1)
        self.assertIn("changed after anonymization", changed_copy.stderr)
        extra.rmdir()
        revealed = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(revealed.returncode, 0, revealed.stderr)

    def test_anonymize_preserves_opaque_binary_artifacts(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        source = Path(assignments["runs"][0]["workspace"]) / "artifact"
        payload = bytes(range(256)) + b"\x00\xff\x00split-testing\x80"
        (source / "opaque.bin").write_bytes(payload)

        anonymized = run_helper("anonymize", str(self.root), "round-one")

        self.assertEqual(anonymized.returncode, 0, anonymized.stderr)
        copied = [
            path
            for review in assignments["reviews"]
            for path in Path(review["view_dir"]).joinpath("candidates").glob(
                "*/*/opaque.bin"
            )
        ]
        self.assertTrue(copied)
        self.assertTrue(all(path.read_bytes() == payload for path in copied))

    def test_prepared_anonymization_recovers_after_state_save_failure(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        spec = importlib.util.spec_from_file_location(
            "split_test_workspace_under_test", SCRIPT
        )
        assert spec is not None
        loader = spec.loader
        assert loader is not None
        helper = importlib.util.module_from_spec(spec)
        loader.exec_module(helper)

        workspace_lock = getattr(helper, "workspace_lock")
        load_experiment = getattr(helper, "load_experiment")
        find_round = getattr(helper, "find_round")
        anonymize = getattr(helper, "anonymize")
        original_save = getattr(helper, "save_experiment")

        with workspace_lock(self.root, exclusive=True):
            experiment = load_experiment(self.root)
            round_record = find_round(experiment, "round-one")

            def fail_save(root: Path, value: dict[str, Any]) -> None:
                raise OSError("injected state-save failure")

            setattr(helper, "save_experiment", fail_save)
            try:
                with self.assertRaisesRegex(OSError, "injected state-save failure"):
                    anonymize(self.root, round_record, experiment)
            finally:
                setattr(helper, "save_experiment", original_save)

        self.assertEqual(self.assignments()["state"], "open")
        with workspace_lock(self.root, exclusive=True):
            experiment = load_experiment(self.root)
            round_record = find_round(experiment, "round-one")
            recovered = anonymize(self.root, round_record, experiment)
        self.assertEqual(recovered["state"], "anonymized")
        for review in assignments["reviews"]:
            Path(review["view_dir"]).joinpath("judgment.md").write_text(
                "Committed judgment.\n", encoding="utf-8"
            )
        revealed = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(revealed.returncode, 0, revealed.stderr)

    def test_mapping_is_permanent_and_rounds_are_append_only(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        first = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(first.returncode, 0, first.stderr)
        mapping_path = Path(assignments["mapping_path"])
        mapping = mapping_path.read_bytes()

        second = run_helper("anonymize", str(self.root), "round-one")
        self.assertEqual(second.returncode, 1)
        self.assertEqual(mapping_path.read_bytes(), mapping)

        self.write_plan(round_id="round-two", review_sets=[])
        added = run_helper("add-round", str(self.root), str(self.plan))
        self.assertEqual(added.returncode, 0, added.stderr)
        status = parse_json(run_helper("status", str(self.root)))
        self.assertEqual(
            [(item["round_id"], item["state"]) for item in status["rounds"]],
            [("round-one", "anonymized"), ("round-two", "open")],
        )
        self.assertEqual(mapping_path.read_bytes(), mapping)

        duplicate = run_helper("add-round", str(self.root), str(self.plan))
        self.assertEqual(duplicate.returncode, 1)
        self.assertIn("already exists", duplicate.stderr)

    def test_invalid_design_is_rejected_before_any_round_state_exists(self) -> None:
        self.init()
        self.write_plan(
            runs=[{"id": "one", "condition": "a"}],
            review_sets=[
                {
                    "id": "bad",
                    "candidates": [{"id": "x", "runs": ["missing"]}],
                    "reviewers": [{"id": "judge"}],
                }
            ],
        )

        completed = run_helper("add-round", str(self.root), str(self.plan))

        self.assertEqual(completed.returncode, 2)
        self.assertIn("unknown run", completed.stderr)
        self.assertEqual(parse_json(run_helper("status", str(self.root)))["rounds"], [])

    def test_loaded_state_rejects_path_escape_and_wrong_nested_types(self) -> None:
        self.init()
        self.add_round()
        self.populate()
        state_path = self.root / ".split-testing" / "experiment.json"
        original = json.loads(state_path.read_text(encoding="utf-8"))
        escaped = json.loads(json.dumps(original))
        outside = self.base / "outside-mapping.json"
        escaped["rounds"][0]["mapping_rel"] = str(outside)
        state_path.write_text(json.dumps(escaped) + "\n", encoding="utf-8")

        rejected_escape = run_helper("anonymize", str(self.root), "round-one")

        self.assertEqual(rejected_escape.returncode, 2)
        self.assertIn("managed path", rejected_escape.stderr)
        self.assertFalse(outside.exists())
        malformed = json.loads(json.dumps(original))
        malformed["rounds"][0]["runs"][0]["workspace_rel"] = ["workspaces"]
        state_path.write_text(json.dumps(malformed) + "\n", encoding="utf-8")
        rejected_type = run_helper("status", str(self.root))
        self.assertEqual(rejected_type.returncode, 2)
        self.assertIn("workspace_rel", rejected_type.stderr)
        self.assertLessEqual(len(rejected_type.stderr.splitlines()), 2)

    def test_workspace_lock_serializes_competing_anonymizers(self) -> None:
        self.init()
        self.add_round()
        assignments = self.populate()
        lock_path = self.root / ".split-testing" / "workspace.lock"
        with lock_path.open("r+b") as lock_stream:
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
            command = [
                sys.executable,
                str(SCRIPT),
                "anonymize",
                str(self.root),
                "round-one",
            ]
            first = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            second = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_UN)
            first_output, first_error = first.communicate(timeout=20)
            second_output, second_error = second.communicate(timeout=20)

        results = [
            (first.returncode, first_output, first_error),
            (second.returncode, second_output, second_error),
        ]
        self.assertEqual(sorted(item[0] for item in results), [0, 1])
        failed = next(item for item in results if item[0] == 1)
        self.assertIn("not open", failed[2])
        self.assertEqual(self.assignments()["state"], "anonymized")
        for review in assignments["reviews"]:
            Path(review["view_dir"]).joinpath("judgment.md").write_text(
                "Committed judgment.\n", encoding="utf-8"
            )
        revealed = run_helper("reveal", str(self.root), "round-one")
        self.assertEqual(revealed.returncode, 0, revealed.stderr)

    def test_help_and_errors_are_short_and_actionable(self) -> None:
        help_result = run_helper("--help")
        self.assertEqual(help_result.returncode, 0)
        for command in ("init", "add-round", "assignments", "anonymize", "reveal", "status"):
            self.assertIn(command, help_result.stdout)

        unknown = run_helper("unknown")
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("error:", unknown.stderr)
        self.assertIn("hint:", unknown.stderr)
        self.assertLessEqual(len(unknown.stderr.splitlines()), 3)


if __name__ == "__main__":
    unittest.main()
