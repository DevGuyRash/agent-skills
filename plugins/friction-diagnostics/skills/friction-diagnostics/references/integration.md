# Integration patterns

## Self-encapsulated by default

The plugin needs no repository edits to work. The SessionStart hook carries the ambient integration: it surfaces the open-anchor count, top recurring keys, and the known-traps path as context lines at every session start (including resume and post-compaction) whenever the repo store has open events, and it maintains the session-attribution sidecar. Repos do not need the snippet below for any of that.

## Optional `AGENTS.md` snippet

For repos that additionally want the full filing policy in ambient instructions (e.g. for subagents on hosts without hook support), a paste-ready contract exists at `assets/agents-md-snippet.md`. It is an optional pattern, not the mechanism.

```markdown
## Friction diagnostics

WHEN `.local/reports/friction/known-traps.md` exists THEN you SHALL read it before acting (it is at most 15 one-line traps).
WHEN reality diverges from what you predicted AND recording it would change a future session's behavior THEN you SHALL file it at that moment using the `friction-diagnostics` skill.
WHEN the divergence matches a known trap or an open event THEN you SHALL file `--recur <event-id>` instead of a new event.
You SHALL NOT file outcomes you predicted or engineered (intended test failures, expected error paths, probes), nor task status.
WHEN you filed nothing AND the user did not raise friction diagnostics THEN you SHALL NOT mention friction diagnostics, or the decision not to file, anywhere in your response.
```

## Filing

JSON via stdin is the primary path. The skeleton's placeholders are the eliciting questions; `--title` is derived from `actual_outcome` rather than passed:

```sh
printf '%s' '{
  "actual_outcome":    "<what actually happened - verbatim>",
  "expected_outcome":  "<what you predicted, and what grounded it>",
  "reading":           "<from inside the decision: consulted, believed, did, diverged>",
  "decision":          "<the response as history: options seen, set aside, action taken, and the license for any deviation>",
  "pivot_information": "<the information that would have changed the outcome, and where it lives>",
  "sources":           [{"kind": "<artifact|instruction|tool|assumption|memory|observation>", "ref": "<...>", "claim": "<what you believed about it - the prior belief only>"}],
  "impact":            "<blocked|degraded|noisy|continued>",
  "recurrence_key":    "<2-5 hyphenated words; omit if unsure>",
  "note":              "<optional free slot: whatever mattered that no field asked for>"
}' | sh scripts/report-friction.sh --from-json -
```

Repeats are one line:

```sh
sh scripts/report-friction.sh --recur evt-NNNN --actual-outcome "<short verbatim>" [--note "<what differed>"]
```

Post-hoc tag additions: `sh scripts/report-friction.sh --add-tags evt-NNNN "tag1,tag2"`.

## Canonical target resolution

1. Inside a git repo: `<repo>/.local/reports/friction/events.jsonl`
2. If `.local` absent but `.local*` exists: use that existing local area
3. No `.local*` in the repo: create `.local/reports/friction/events.jsonl`
4. Outside git: `<system-temp>/agent-friction/<cwd-hash>/events.jsonl`
5. Explicit override: `--events-file <path>`

The same resolution runs identically in every agent and subagent — a shared store with no coordination needed. Concurrent writers are serialized by a lock directory next to the events file.

## The loop

Capture is the default posture; nothing mends autonomously. On user request, the sibling `friction-mend` skill clusters open events, proposes edits to the `sources[].ref` targets that misled, records append-only resolutions, and publishes `known-traps.md` (≤15 one-liners, ≤8KB) — the feed-forward artifact the snippet above makes every future session read before acting.

## Querying and reports

```sh
sh scripts/query-friction.sh --open --kind friction --format json
sh scripts/query-friction.sh --key <recurrence-key> --format md
sh scripts/query-friction.sh --recurs evt-NNNN
sh scripts/query-friction.sh --tag auth --date-from 2026-03-01
sh scripts/generate-report.sh --report-type stats --format md
sh scripts/generate-report.sh --scan-dirs ~/repos --report-type cross-repo
```

Tag queries use substring matching (`--tag auth` matches `ssh-auth-sock`); `--tag-exact` for exact. `--alias`/`--alias-exact` still query the v4 corpus. `INDEX.md` is a bounded synthesis dashboard; the full stream is reachable only through queries.

## Session linkage (optional)

The plugin ships a SessionStart hook (`hooks/friction-session-env.sh` at the plugin root) that does three fail-open jobs: writes a session-attribution sidecar (`<store>/session-ref.json`, atomic, 0600, only when the store directory already exists), exports `FRICTION_SESSION_REF` and `FRICTION_TRANSCRIPT_PATH` via the documented `$CLAUDE_ENV_FILE` mechanism (deduping its own prior lines so continued conversations do not accumulate stale exports), and prints the boundary-presence lines described above. Records then carry `session_ref`, linking each record to the transcript where the actual reasoning lives.

Resolution precedence at filing time: native runtime identity (`CODEX_SESSION_ID`, `CODEX_THREAD_ID`) first, then a fresh sidecar (`FRICTION_SIDECAR_TTL`, default 86400s), then the env chain (`FRICTION_SESSION_REF`, `CLAUDE_SESSION_ID`). The sidecar exists because env-file exports go stale across continued/resumed Claude conversations — the sidecar is rewritten at every session start, so post-resume filings attribute to the current session. Caveat: two live sessions in one repo last-writer-win the sidecar; `session_ref` is contractually optional enrichment, never load-bearing. The hook exits 0 on every path, and everything works with hooks absent.

Observed host behavior (2026-07, Claude Code 2.1.x / Codex CLI 0.142):

- **Claude Code**: the hook fires at session start and records carry the session UUID; transcripts live at `~/.claude/projects/<munged-cwd>/<session-id>.jsonl`. Propagation of env-file vars to subagents and resumed sessions is undocumented upstream — treat as best-effort.
- **Codex**: no hook needed — the runtime natively exports `CODEX_THREAD_ID` (per-thread UUID), which the probe catches; records filed under `codex exec` carried correct per-thread refs, including under `--sandbox workspace-write` (filing mechanics fully functional in the sandbox).
- **Codex nested under Claude** (companion wrappers): the wrapper injects `CLAUDE_CODE_SESSION_ID` (the _parent_ Claude session) into the child environment. The probe deliberately does not read that variable — `CODEX_THREAD_ID` wins, so nested runs attribute to their own thread, not the parent session.
- Host packaging difference worth knowing: Claude installs a version-keyed cache copy (content changes need a version bump to propagate), while Codex references the marketplace working tree live.

## Session summary

A courtesy rendering for the user at task end (nothing correctness-bearing depends on it):

```sh
sh scripts/render-summary.sh --events-file <events-file> --after "<lower-bound-timestamp>"
```
