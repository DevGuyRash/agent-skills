# Workspace Helper Contract

Use this reference only while operating `scripts/split_test_workspace.py`. The helper stores and publishes experiment structure; it never authors tasks or criteria, launches agents, chooses models, grades results, aggregates preferences, or declares a winner.

## Commands and topology

```text
python3 scripts/split_test_workspace.py init ROOT
python3 scripts/split_test_workspace.py add-round ROOT DESIGN.json
python3 scripts/split_test_workspace.py assignments ROOT ROUND_ID
python3 scripts/split_test_workspace.py anonymize ROOT ROUND_ID
python3 scripts/split_test_workspace.py reveal ROOT ROUND_ID
python3 scripts/split_test_workspace.py status ROOT
```

Use an explicit absolute root. `init` refuses a nonempty root and `add-round` is append-only. `assignments` exposes private controller identities; never place its output in executor or reviewer material. Populate each returned opaque execution workspace's `input/`, collect its committed result in `artifact/`, and store prompt, model, trace, timing, and usage evidence in its `record_dir`.

Populate each reviewer `material_dir` with the common task material, frozen core rubric, and any declared reviewer-specific lens before anonymization. The helper publishes that content as `brief/`; reviewer prompts must use published paths rather than controller-private locations.

The evaluator-authored design describes storage topology, not experimental policy:

```json
{
  "schema_version": "1.0",
  "round_id": "private-round-id",
  "runs": [
    {
      "id": "private-run-id",
      "condition": "private-condition-id",
      "case": "optional-private-case-id",
      "metadata": {}
    }
  ],
  "review_sets": [
    {
      "id": "private-review-set-id",
      "candidates": [
        {"id": "private-candidate-id", "runs": ["private-run-id"]}
      ],
      "reviewers": [
        {
          "id": "private-reviewer-id",
          "candidate_order": ["private-candidate-id"],
          "metadata": {}
        }
      ]
    }
  ],
  "metadata": {}
}
```

A candidate can bundle any number of runs; a review set can contain any number of candidates and reviewers. Separate review sets may expose different candidate groupings. Reviewer metadata can record a requested model, effort, or specialty, but the helper does not interpret it. An optional `candidate_order` is a complete private-ID permutation for counterbalancing; otherwise candidate and sample order are independently randomized with labels extending beyond `Z`.

When a review set uses non-null `case` values, reviewer-local `Bxxx-Syyy` paths preserve opaque matched blocks across any number of candidates. Repetitions within a candidate/block receive distinct sample suffixes. Unmatched declared cases remain visible as unmatched blocks; null-case occurrences are distinct singletons. Wholly uncased review sets retain `Sxxx`. The reveal mapping resolves both forms and the earlier flat layout.

## Custody guarantees and limits

`anonymize` preflights the complete round before publishing. It preserves regular-file bytes, directory topology, empty directories, complete POSIX modes, and contained relative symlinks; it rejects escaping or absolute symlinks and special files. Workspace locks serialize controller mutations and a recoverable transaction prevents half-published views.

Publication is process-atomic and integrity-checked; the helper does not promise that temporary evidence survives host power or storage failure. Move completed evidence to storage with the needed durability when that hazard belongs to the decision.

`reveal` rechecks source and blinded trees and refuses identity mapping until every configured `judgment.md` is nonempty. It snapshots the exact blind judgment bytes and hashes, then returns the private mapping path and digest rather than injecting the potentially large per-file map into command output. Read that file only after reveal and preserve it with the judgment snapshot. This proves commitment and integrity, not semantic adequacy.

Opaque paths hide controller labels, not self-identifying content. Do not silently rewrite a consequential artifact to make it appear blind. Name what the harness conceals and preserve remaining inference risk.

The helper is not a read-isolation or hostile-process security boundary. A same-user process may traverse the wider filesystem, and a racing process can mutate controller-owned paths. Use OS-level permissions, sandboxes, containers, isolated users, or a trusted experiment platform when those threats matter. The helper assumes one controller owns mutations below its root.
