---
name: Friction Mend
description: >-
  Batch-mend accumulated friction: cluster open friction events, root-cause
  them, propose edits to the artifacts and instructions that misled, record
  resolutions, and distill recurring traps into known-traps.md. Use when the
  user asks to review, triage, mend, resolve, or distill logged friction.
compatibility: Designed for filesystem-capable coding agents on Linux. Deterministic helpers require POSIX sh. No network required.
metadata:
  author: generated-template
  version: "5.1.3"
  category: diagnostics
  tags: friction,mending,distillation,resolution
---

# Friction Mend

The convergent half of friction diagnostics. Capture (the `friction-diagnostics` skill) diverges: rich, unframed records at the moment of surprise. Mending converges: you read the accumulated corpus, invent the taxonomy the data actually supports, fix what misled, and distill what remains into a small feed-forward file.

WHEN the user has not asked for mending THEN you SHALL NOT mend — logging-only is the default posture. You MAY suggest a mend session when the dashboard shows accumulation.

## Outcome contract

A mend session is done when, for the clusters you took on:

1. Each cluster is either **mended** — the `sources[].ref` artifacts, instructions, or configurations that misled were edited (with the owner's approval for anything beyond the repo's own files) — or **honestly closed** as `wontfix` with a reason.
2. Every resolution you made is **recorded** for provenance via `record-resolution.sh` (the resolving is yours; the script only writes down that it happened).
3. Recurring traps that remain open are **distilled** into `known-traps.md` via `update-traps.sh` — at most 15 one-liners, each a pointer (`[key]` + anchor id) into the lossless store. Mended traps are deleted, not marked; traps that stopped recurring decay out.
4. The user gets the delta: what closed, what stayed open, what changed in the traps file.

How you get there — what to read first, how to cluster, what order to fix in — is entirely your judgment. There is no prescribed sequence. Mechanical hints never bind.

## Tools (all supplemental)

```sh
sh <skills-file-root>/scripts/query-friction.sh --open --kind friction --format json   # the open corpus
sh <skills-file-root>/scripts/cluster-hints.sh                                          # mechanical starting points: key groups + token-overlap candidates
sh <skills-file-root>/scripts/record-resolution.sh --resolves "evt-A,evt-B" --action "..." --ref "commit:..."
sh <skills-file-root>/scripts/record-resolution.sh --resolves "evt-C" --wontfix "expected zsh behavior, not mendable"
... | sh <skills-file-root>/scripts/update-traps.sh                                     # capped atomic publisher
sh <skills-file-root>/scripts/generate-report.sh --report-type stats --format md        # health metrics before/after
sh <skills-file-root>/scripts/generate-report.sh --scan-dirs ~/repos --report-type cross-repo   # cross-repo view
```

`references/mend-playbook.md` offers a clustering rubric, root-cause questions, and the trap format. It is reference material, not procedure.

## Hard rules (store integrity only)

- You SHALL NOT edit or delete lines in `events.jsonl`; resolutions are append-only records.
- You SHALL NOT hand-edit `known-traps.md` or `INDEX.md`; publish traps only through `update-traps.sh`.
- WHEN a fix touches anything outside the repository's own files THEN you SHALL present the diff and get approval before applying.
