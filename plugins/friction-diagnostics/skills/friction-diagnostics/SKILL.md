---
name: Friction Diagnostics
description: >-
  Log genuine surprise — reality diverged from what you predicted: a tool,
  command, instruction, document, or assumption behaved differently than
  expected, in any domain (code, writing, research, ops). Worth-logging
  test: would this record change what a future session does? Predicted or
  engineered outcomes (intended test failures, expected error paths,
  probes) are not friction. A known trap repeating → file --recur against
  the earlier event. Also for user requests to log, review, mend, or
  distill friction.
compatibility: Designed for filesystem-capable coding agents on Linux. Deterministic helpers require POSIX sh. No network required.
metadata:
  author: generated-template
  version: "5.1.3"
  category: diagnostics
  tags: friction,logging,surprise,diagnostics
---

# Friction Diagnostics

A cognitive debugging instrument. It captures genuine surprises — moments when reality diverged from your prediction — as structured JSONL records that trace what you trusted and what information was missing, so that instructions and environments can be mended and future sessions avoid known traps.

## Policy

WHEN reality diverges from your prediction AND recording it would change a future session's behavior THEN you SHALL file an event at that moment, not batched at task end.
WHEN the divergence matches a known trap or an open event THEN you SHALL file `--recur <event-id>` instead of a new event.
WHEN friction looks transient AND it would matter if it recurred THEN you MAY file a minimal anchor event (short fields suffice) so a later `--recur` has a target.
You SHALL NOT file outcomes you predicted or engineered, nor task status.
WHEN you filed nothing AND the user did not raise friction diagnostics THEN you SHALL NOT mention friction diagnostics, or the decision not to file, anywhere in your response.

Routing: surprised? — no: nothing, and say nothing about it. yes: seen before? — yes: `--recur`. no: worth test — full event, or a minimal anchor for a transient that would matter if it recurs.

Everything beyond logging — what to fix, how to work, what to try next — stays entirely with you. Logging is supplemental; it never limits how you operate.

WHEN `known-traps.md` exists next to the events file THEN you SHOULD read it before acting (it is at most 15 one-line traps). Accumulated friction is mended by the `friction-mend` skill, on user request only.

## How to file

JSON via stdin is the primary path (safe for backticks, quotes, multiline text). Compose fields in the order shown — verbatim evidence first, interpretation after, classification last. The placeholders are the questions to answer:

```sh
printf '%s' '{
  "actual_outcome":    "<what actually happened - paste verbatim, never paraphrase>",
  "expected_outcome":  "<what you predicted, and what specifically grounded that prediction>",
  "reading":           "<from inside the decision: what you consulted, what you believed it said, what you did, the moment reality diverged>",
  "decision":          "<what you did about it: options seen, options set aside, the action taken - and, for any deviation from something documented as required, what made it feel permitted at the time>",
  "pivot_information": "<the single piece of information that would have changed the outcome, and where it lives - or the fact a future agent should check first, when you caught this before harm - or: none - unknowable in advance, because ...>",
  "sources":           [{"kind": "<artifact|instruction|tool|assumption|memory|observation>",
                         "ref": "<path, url, tool name, or belief label>",
                         "claim": "<what you believed it said or would do - the prior belief only>"}],
  "impact":            "<blocked|degraded|noisy|continued>",
  "recurrence_key":    "<2-5 hyphenated words naming the trap; omit if unsure>",
  "tags":              ["<optional labels>"],
  "note":              "<optional free slot: whatever mattered that no field asked for>"
}' | sh <skills-file-root>/scripts/report-friction.sh --from-json -
```

The placeholders and questions are prompts, not perimeters — if something mattered that no question asked about, include it; whatever fits no field goes in `note`. The question shape never excuses omission.

Direct flags exist for short single-source payloads with no shell-sensitive text (`--actual-outcome`, `--expected-outcome`, `--reading`, `--decision`, `--pivot-information`, `--source-kind`, `--source-ref`, `--source-claim`, `--impact`, `--recurrence-key`, `--tags`, `--note`). Do not pass `--title`; it is derived from the actual outcome.

The tool talks back after every filing: similar prior events with counts, tag history, open clusters, known traps. You never need to remember or search the stream before filing — the store briefs you at the point of action.

WHEN you are unsure what a field wants THEN you MAY run `--interview` for rotated eliciting questions. It is an aid, never a required step.

### Repeats

```sh
sh <skills-file-root>/scripts/report-friction.sh --recur evt-0142 --actual-outcome "<short verbatim of this occurrence>" [--note "<what differed this time>"]
```

A recurrence record is one line: it bumps the trap's count and timeline without recomposing the narrative. Impact defaults to the anchor's.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | record written |
| 1 | invalid arguments or unrecoverable validation failure |
| 2 | input error on `--from-json` (empty stdin, malformed JSON, bad payload) — nothing was filed |
| 3 | duplicate soft-stop: an identical recurrence key exists. Re-run with `--recur <event-id>` (it is a repeat) or `--distinct` (it is new). Nothing was written. |

## Fields

- **`actual_outcome`** — verbatim evidence: the error text, output, or sentence as written. Never paraphrase. A stranger should be able to judge from it alone.
- **`expected_outcome`** — the prediction and its grounding: what made you expect that?
- **`reading`** — the account from inside the decision. What you consulted, what exactly you believed it said (quote the wording you acted on), what you did, and the moment reality diverged from your model. Write it your way; `references/examples.md` lists the properties it must satisfy, not sentences to imitate.
- **`decision`** — the response as history: options you saw, options you set aside, the action you took (even "continued unchanged"), and — for any deviation from something documented as required — what made it feel permitted at the moment you chose. Past tense, never a proposal. "Filed before acting; no response yet" is a truthful value when that is the state.
- **`pivot_information`** — an information gap, not a self-verdict: name the fact that, visible before acting, would have changed the outcome — or, when you caught this before harm, the fact a future agent should check first. State where that fact lives (a file, a doc, an output, nowhere). Escape hatch when honest: `none — the outcome was unknowable in advance, because ...`
- **`sources`** — what you trusted that betrayed you. Kinds: `artifact` (file/url/doc with a mendable body), `instruction` (user/system/skill directive), `tool` (tool or command behavior), `assumption` (belief with no external backing), `memory` (recalled, not consulted), `observation` (read from output/screen). For each: `ref` names it, `claim` states what you believed about it.
- **`impact`** — `blocked` (work stopped) | `degraded` (workaround used) | `noisy` (extra retries/effort) | `continued` (no disruption).
- **`recurrence_key`** — the trap's stable name across days and sessions (e.g. `zsh-status-readonly`). Omit if unsure; a content-derived fallback is computed.

Do not propose fixes inside records — mending is a separate activity with its own skill. Your own completed response is history and belongs in `decision`; what the misleading sources should say instead does not belong anywhere in a record.

## Storage

- Inside a git repo: `<repo>/.local/reports/friction/events.jsonl` (an existing `.local*` area is reused; `--events-file` overrides)
- Outside git: `<system-temp>/agent-friction/<cwd-hash>/events.jsonl`
- `INDEX.md` (synthesis dashboard) and `known-traps.md` (distilled traps) live next to it. Both are maintained by tooling; do not hand-edit.

One append-only stream holds three record kinds: `friction` (full capture), `recurrence` (cheap repeat pointer), `resolution` (mend provenance, written by friction-mend). Records are never edited or deleted.

## How to query

```sh
sh <skills-file-root>/scripts/query-friction.sh --impact blocked --format md
sh <skills-file-root>/scripts/query-friction.sh --open --tag auth
sh <skills-file-root>/scripts/query-friction.sh --key zsh-status-readonly
sh <skills-file-root>/scripts/generate-report.sh --scan-dirs ~/repos --report-type cross-repo
```

## Session summary

WHEN your task is complete AND you filed at least one new record since your last assistant turn THEN you SHALL include a friction summary at the end of your final response, produced by:

```sh
sh <skills-file-root>/scripts/render-summary.sh --events-file <events-file> --after "<lower-bound-timestamp>"
```

Paste its output verbatim. WHEN no lower bound is known THEN you MAY use `--date-from` with today's date. This summary is a courtesy to the user; nothing correctness-bearing depends on it.

## Scripts

| Script | Purpose |
|---|---|
| `report-friction.sh` | File friction and recurrence records; duplicate soft-stop; talkback; `--interview`; `--add-tags` |
| `query-friction.sh` | Filter and render the stream by kind, lifecycle, key, impact, tags, text, dates, sources |
| `generate-report.sh` | `index` (dashboard), `stats`, `cross-repo`, `per-repo`, `timeseries` reports |
| `build-index.sh` | Internal index maintenance |
