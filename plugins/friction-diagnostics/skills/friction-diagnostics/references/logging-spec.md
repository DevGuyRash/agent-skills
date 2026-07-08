# Logging specification

## Canonical data

`events.jsonl` is the only canonical persisted data store. Each non-empty line is one JSON object — one record. The stream is append-only: records are never edited or deleted (the sole exception is `--add-tags`/`--add-aliases`, which patch one record's tag arrays in place under the write lock).

Derived, tool-managed views next to it (never hand-edited, regenerable at any time):

- `INDEX.md` — synthesis dashboard (bounded size)
- `known-traps.md` — feed-forward distillate published by friction-mend

## Record kinds

One stream, three kinds, discriminated by `kind` (absent = v4 friction event):

| Kind | Purpose | Required fields beyond system block |
|---|---|---|
| `friction` | Full capture of a genuine surprise | `actual_outcome`, `expected_outcome`, `reading`, `decision`, `pivot_information`, `sources` (≥1), `impact` |
| `recurrence` | Cheap pointer: a known trap bit again | `recurs` (anchor event id), `actual_outcome`; `impact` defaults to the anchor's |
| `resolution` | Provenance that the model mended/closed events | `resolves` (event ids), `action` |

`note` is an optional free slot on every kind — on friction records it is the deliberately question-less field for whatever mattered that no field asked for.

System block, stamped by the tool on every record: `event_id`, `recorded_at`, `schema_version`, `kind`, `session_ref` (only when a harness session id is discoverable via `FRICTION_SESSION_REF`/`CLAUDE_SESSION_ID`/`CODEX_*`; on Claude Code the plugin's optional SessionStart hook exports `FRICTION_SESSION_REF` per session), `events_file`, `repo_root`.

## Lifecycle — derived, never stored

There is no status field. An event is **open** iff its id (or, for a recurrence record, its `recurs` anchor) appears in no resolution's `resolves` array. `query-friction.sh --open` computes this in one pass. Resolutions are append-only; re-resolving warns and records again.

## Composition order

Stored key order equals composition order: evidence before interpretation, classification late, `title` last (auto-derived from `actual_outcome` when omitted, which is preferred). The canonical order and each field's eliciting question live in `friction-event-schema.json` (`x-composition-order`, `x-eliciting-question`) — the single source of truth all scripts derive from at runtime.

## Sources

`sources` names what the agent **trusted**, not where friction surfaced.

| Field | Description |
|---|---|
| `kind` | `artifact`, `instruction`, `tool`, `assumption`, `memory`, `observation`, `other` |
| `ref` | Path, URL, tool name, or a short label naming the belief |
| `claim` | What the agent believed it said or would do (verbatim quote for artifact/instruction) |
| `line`, `end_line` | Line range (artifacts only) |

Deprecated v4 inputs are coerced on write, never rejected: `type` → `kind` (file/url/documentation → artifact, conversation → instruction, audio/visual → observation), `excerpt` → `claim`.

## Recurrence keys

`recurrence_key` is the trap's stable cross-day identity: a model-supplied 2–5 word slug, or a content-token fallback (`auto-` prefix) derived from `actual_outcome` plus the primary source ref. Deliberately no date component. v4 `fingerprint` values remain readable; all read-side grouping uses `(.recurrence_key // .fingerprint)`.

## Duplicate handling (filing-time, mechanical)

Before writing, the tool scans the store under the write lock:

- Exact key match on an existing friction event → **soft-stop, exit 3, nothing written**. Output names the match and both one-flag escapes: `--recur <id>` (repeat) or `--distinct` (new). A resolved match names its resolver and notes that `--recur` reopens.
- Fuzzy token-overlap candidates → INFO lines only; the write proceeds.
- After every successful write a talkback block briefs the agent: similar events with similarity scores and counts, tag history, open clusters, traps count. No agent memory is ever required for correct filing.

## Caps and floors

- Narrative fields: minimum floors 15/15/30/15 chars for actual/expected/reading/decision (blank-guards); cap 20,000 chars with an explicit truncation marker and stderr note.
- `sources[].claim`: cap 2,000 chars.
- Whole record: 65,536 bytes (hard error after caps).
- `reading` under 200 chars triggers an informational nudge with rotated eliciting questions; it never blocks.

## Sanitization

Write-time sanitization is always applied: bearer tokens, GitHub/API/AWS/Slack tokens, and generic password/token/secret/api-key assignments are redacted before persisting.

## Exit codes (report-friction.sh)

| Code | Meaning |
|---|---|
| 0 | record written |
| 1 | invalid arguments or unrecoverable validation failure |
| 2 | input error on `--from-json`: empty stdin (loud error, **no quarantine file**), malformed JSON (quarantined with a replay command), or invalid payload |
| 3 | duplicate soft-stop; nothing written |

## Deprecated input coercions

Accepted and coerced with a printed note, never rejected: `--hindsight`/`hindsight` → `pivot_information`; `--aliases`/`aliases` → folded into `tags`; `--fingerprint-key`/`fingerprint_key` → `recurrence_key`; scalar `tags` string → array; single `sources` object → array; string `line` numbers → integers.

## Isolation

All embedded python helpers run `python3 -I` (isolated mode) so stray modules on `sys.path` (e.g. a `/tmp/bisect.py`) cannot shadow the standard library and crash filing.

## Structural blind spots

The stream is a self-report instrument gated on surprise, and readers should know what that excludes. (1) **Surprise gating**: friction exists only where a prediction was violated; deliberate or unnoticed shortcuts produce no record, so the stream under-represents motivated deviation — absence of records is not evidence of correct behavior. (2) **Cold start**: first occurrences of transient-looking friction legitimately fail the worth test; the minimal-anchor MAY clause narrows, not closes, this gap. (3) **Self-report ceiling**: every field is the reporter's own account — `decision` elicits the license an agent operated under but cannot audit it; `session_ref`, when present, points at the transcript where verification lives. (4) **Question framing**: eliciting questions pre-structure answers, and the unasked is systematically at risk; the `note` free slot and question rotation mitigate, neither eliminates — the corpus's answers are shaped by its questions.
