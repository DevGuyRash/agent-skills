# Mend playbook

Reference material for mend sessions. Nothing here is a required sequence — use what helps, ignore what does not.

## Clustering rubric

Recurrence-key equality is a hint, not truth: v4 fingerprints collide unrelated same-day events and split same-trap different-day events; even v5 keys are only as good as the naming instinct at filing time. Judge clusters by:

- **Same pivot_information ≈ same trap.** Two events missing the same piece of information are the same gap, whatever their surface errors look like.
- **Same betrayed source + same claim class.** Events trusting the same artifact/instruction for the same kind of claim usually mend together.
- **Same error class across different refs** may be one environmental trap (e.g. a shell behavior) wearing different costumes.
- Token-overlap candidates from `cluster-hints.sh` surface surface-text similarity; verify against the two rules above before merging.

Invent the taxonomy from the data in front of you. The reporters' tags are not ground truth — capture-time labels were written without seeing the corpus.

## Root-cause questions per cluster

- What did every member trust? (`sources[].kind` + `ref` + `claim`)
- Is the gap in the world (the artifact/instruction says the wrong thing or nothing) or in the reading (it says it, agents miss it)? The first mends by editing the ref; the second mends by moving or sharpening the information.
- Where does the pivot information live today, and where would an agent actually look? The mend is often relocation, not correction.
- Is this mendable at all? Environmental behavior nobody controls is a trap to distill, not a bug to fix — close as wontfix and let the traps file carry it.

## Resolution recording

- One resolution per mended cluster; list every anchor id it closes.
- `--action` states what changed, concretely: the edit, the file, the sentence added.
- `--ref` points at the mend: a commit, a path, a URL.
- `--wontfix "reason"` is honest closure — noise clusters, expected behaviors, one-off environment flukes. Closing noise is a valid mend outcome; leaving it open forever is not.

## Trap format

You supply only judgment — which anchors matter and the avoidance guidance; the publisher derives every clerical fact (key, sighting count, last-seen date) from the store and refuses anchors that do not exist there:

```sh
printf '%s' '{"traps":[{"anchor":"evt-0142","avoid":"One-line statement of the trap and how to avoid it."}]}' \
  | sh <skills-file-root>/scripts/update-traps.sh
```

Published line shape (rendered by the script, never hand-written):

```
- [trap-key] One-line statement of the trap and how to avoid it. (evt-0142 x14, last 2026-07-01)
```

- ≤15 traps, ≤8KB (the script enforces both). Budget rule when over: keep highest recurrence x impact. The script does not gate on open state or sighting counts — which traps deserve a slot is your judgment.
- The traps file lists **active dangers, not open records**: a mended trap is deleted because the danger is gone, but a cluster closed as `wontfix` for an environmental cause (shell behavior, harness quirks, untrusted content) may keep its trap — the record is honestly closed while the danger remains real for future sessions.
- Each trap is a pointer, not a replacement: the key and anchor id lead back to full events, and via `session_ref` to transcripts. Precision is paged out, never lost.
- Prefer traps that bite across task types; a trap only one workflow can hit earns its slot by recurrence count.
- Write the avoidance, not the incident: the reader is a future session deciding what to do, not a historian.

## Transcript drill-down

Records may carry `session_ref` — on Claude Code it is the session UUID exported by the plugin's SessionStart hook; on Codex it is the runtime's native `CODEX_THREAD_ID` (a time-ordered UUIDv7 whose `019...` prefix embeds the start timestamp).

- Claude transcript: `~/.claude/projects/<cwd-with-slashes-replaced-by-dashes>/<session-id>.jsonl`; when the munged cwd is uncertain, `find ~/.claude/projects -name '<session_ref>.jsonl'` is the robust locator.
- Codex rollout: `~/.codex/sessions/<YYYY>/<MM>/<DD>/rollout-*-<session_ref>.jsonl`; robust locator `find ~/.codex/sessions -name "*<session_ref>*"`.

For records without `session_ref`, correlate by `recorded_at` overlap with transcript timestamps in the repo's project directory. The transcript is where the reporter's self-account can be verified — what was actually read, in what order, before the divergence. Presence of the link is enrichment, never a requirement.

## Measuring the session

`generate-report.sh --report-type stats` before and after: open count down, resolutions up, key collisions unchanged at 0, and — over weeks — recurrence share rising (repeats getting filed as cheap pointers) while events/day falls.
