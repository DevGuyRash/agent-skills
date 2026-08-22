---
name: friction-mend
description: >-
  Batch-mend accumulated friction: cluster open events, root-cause them,
  fix the artifacts and instructions that misled, record resolutions, and
  distill recurring traps into known-traps.md. Use when the user asks to:
  (1) Review or triage an existing friction corpus, backlog, or dashboard,
  (2) Mend, resolve, or close logged friction events, (3) Distill or
  refresh known-traps.md, or (4) Work through friction accumulated across
  sessions. Do not use for logging new incidents (that is
  friction-diagnostics) or for reviewing the plugin's own implementation.
compatibility: Designed for filesystem-capable coding agents on Linux. Deterministic helpers require POSIX sh. No network required.
metadata:
  author: generated-template
  version: "5.2.2"
  category: diagnostics
  tags: friction,mending,distillation,resolution
---

# Friction Mend

## Mission

You are the convergent half of friction diagnostics. Capture diverges: rich, unframed records at the moment of surprise. You converge — you read the accumulated corpus, invent the taxonomy the data actually supports, fix what misled, and distill what remains into a small feed-forward file.

How you get there — what to read first, how to cluster, what order to fix in — is your judgment.

You SHALL end a mend session in which, for every cluster you took on:

1. the cluster is either mended — the `sources[].ref` artifacts, instructions, or configurations that misled were edited — or closed as `wontfix` with a stated reason;
2. a resolution record names every anchor you closed;
3. the traps that remain open and still bite are in `known-traps.md`, and traps whose danger you removed are deleted from it.

The resolving is yours; `record-resolution.sh` only writes down that it happened.

## Environment

`events.jsonl` is append-only, and lifecycle is reduced from the stream rather than stored. A resolution closes every anchor its `resolves` list reaches, following recurrence ids to their friction anchor. A later recurrence landing on a closed anchor reopens it, and a later resolution closes it again. Resolving an anchor that is already closed warns and records anyway; resolving a reopened anchor is the normal close-again path and warns about nothing.

`update-traps.sh` derives every clerical fact — key, sighting count, last-seen date — from the store, and refuses anchors that are not in it. It enforces at most 15 traps and 8KB. Which traps deserve a slot is yours: the publisher does not gate on open state or sighting count.

`cluster-hints.sh` groups by recurrence-key equality and by token overlap. Both are surface signals: v4 fingerprints collide unrelated same-day events and split same-trap different-day ones, and even a v5 key is only as good as the naming instinct at filing time.

```sh
sh <skills-file-root>/scripts/query-friction.sh --open --kind friction --format json   # the open corpus
sh <skills-file-root>/scripts/cluster-hints.sh                                          # mechanical starting points: key groups + token-overlap candidates
sh <skills-file-root>/scripts/record-resolution.sh --resolves "evt-A,evt-B" --action "..." --ref "commit:..."
sh <skills-file-root>/scripts/record-resolution.sh --resolves "evt-C" --wontfix "expected zsh behavior, not mendable"
printf '%s' '{"traps":[{"anchor":"evt-A","avoid":"..."}]}' | sh <skills-file-root>/scripts/update-traps.sh   # grounded publisher (derives key/count/date from the store)
sh <skills-file-root>/scripts/generate-report.sh --report-type stats --format md        # health metrics before/after
sh <skills-file-root>/scripts/generate-report.sh --scan-dirs ~/repos --report-type cross-repo   # cross-repo view
```

`<skills-file-root>/references/mend-playbook.md` offers a clustering rubric, root-cause questions, and the trap format. It is reference material, not procedure.

## Boundaries

WHEN the user has not asked for mending THEN you SHALL NOT mend. Logging-only is the default posture; suggesting a mend session when the dashboard shows accumulation is fine.

You SHALL NOT edit or delete lines in `events.jsonl` [these tools have no edit path; resolutions are appended].

You SHALL NOT hand-edit `known-traps.md` or `INDEX.md` [`update-traps.sh` is the only publisher and `build-index.sh` regenerates the dashboard].

WHEN a fix touches anything outside the repository's own files THEN you SHALL present the diff and get approval before applying it. The order carries the hazard: an edit to a shared or upstream artifact leaves a surface nobody in this session owns, and it cannot be taken back from here.

## Loop

WHEN every cluster you took on is closed and recorded and the traps file reflects the result THEN you SHALL stop.

WHEN you cannot finish the clusters you took on THEN you SHALL stop and report which closed, which remain open, and what each remaining one still needs.

IF an out-of-repo fix needs an owner's approval AND no one can approve it THEN you SHALL leave the cluster open and name the blocker and the pending edit in your report ELSE you SHALL apply the approved edit.

## Precedence

WHEN a mechanical hint — recurrence-key equality or a token-overlap candidate — conflicts with your read of the corpus THEN your read prevails and the hint yields.

WHEN a direct instruction from the user conflicts with this skill THEN the user's instruction prevails and this skill yields.

WHEN clauses collide with no tiebreak written THEN the prohibition beats the mandate; failing that you SHALL take the more reversible course and escalate.

## Output contract

WHEN a mend session ends THEN you SHALL report what closed, what stayed open, and what changed in `known-traps.md`.
