# Host session identity for plugins and skills

How a plugin's shell scripts can learn _which session/thread they are running in_ on Claude Code and Codex, and how to walk from that identifier to the on-disk transcript. Discovered and validated live 2026-07 (Claude Code 2.1.x, Codex CLI 0.142); reference implementation lives in `plugins/friction-diagnostics` (`hooks/`, `skills/friction-diagnostics/scripts/_common.sh` `resolve_session_ref`).

## The problem

Claude Code does **not** put a session identifier in the environment of Bash tool executions. `CLAUDE_SESSION_ID` does not exist there; hooks receive `session_id` in their stdin JSON, but scripts the model runs never see it. Codex, by contrast, needs nothing: its runtime natively exports the thread id.

## Per-host mechanism

| Host | Mechanism | Identifier |
| --- | --- | --- |
| Claude Code | Plugin-shipped **SessionStart hook** writes `export` lines to `$CLAUDE_ENV_FILE` (documented); the variables appear in every later Bash call of that session | `session_id` from hook stdin JSON — a **UUIDv4**, identical to the transcript filename |
| Codex | Nothing to ship — the runtime exports it natively | `CODEX_THREAD_ID` — a **UUIDv7** (first 48 bits = Unix-ms start timestamp), identical to the id in the rollout filename |

`$CLAUDE_ENV_FILE` is per-session, so concurrent sessions in one repo attribute correctly. Propagation of env-file variables to subagents and resumed sessions is undocumented upstream — treat as best-effort enrichment, never a correctness dependency.

## Consumer probe pattern

Scripts should probe env vars in an explicit order and omit the field when nothing is set:

```sh
for candidate in "${MYPLUGIN_SESSION_REF-}" "${CLAUDE_SESSION_ID-}" "${CODEX_SESSION_ID-}" "${CODEX_THREAD_ID-}"; do
  [ -n "$candidate" ] && { printf '%s\n' "$candidate"; return 0; }
done
```

- Put your own hook-exported variable first so the hook can override anything.
- You SHALL NOT probe `CLAUDE_CODE_SESSION_ID`: companion wrappers (e.g. the codex-companion plugin) inject it into _nested_ child processes carrying the **parent Claude session's** id — reading it would mis-attribute a Codex thread's work to the Claude session that launched it. `CODEX_THREAD_ID` is the correct identity for nested Codex runs and wins by being reachable only when actually inside Codex.

## From identifier to transcript

- **Claude**: `~/.claude/projects/<cwd-with-slashes-replaced-by-dashes>/<session-id>.jsonl`. Robust locator when the munged cwd is uncertain: `find ~/.claude/projects -name '<id>.jsonl'`.
- **Codex**: `~/.codex/sessions/<YYYY>/<MM>/<DD>/rollout-<timestamp>-<thread-id>.jsonl`. Robust locator: `find ~/.codex/sessions -name "*<id>*"`. The UUIDv7 prefix doubles as the date (decode the first 12 hex chars as ms-since-epoch).
- Records lacking an id can still be correlated: match the record's timestamp against transcript timestamps in the repo's project directory.

## The reusable SessionStart hook recipe

`hooks/hooks.json` at the **plugin root** (not inside a skill — skills must stay self-contained), with the host-neutral guarded command:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ {
        "type": "command",
        "command": "sh -c 'p=\"${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}\"; [ -n \"$p\" ] && [ -x \"$p/hooks/my-session-env.sh\" ] && exec \"$p/hooks/my-session-env.sh\"; exit 0'",
        "timeout": 10
      } ] }
    ]
  }
}
```

The dual-var fallback makes one committed file correct on both hosts, so `scripts/plugin_port.py` converts it with zero rewrites (verified byte-identical through claude→codex→claude).

The hook script contract — every clause is load-bearing:

- You SHALL exit 0 on every path; a hook failure must never block a session.
- You SHALL NOT print to stdout (SessionStart stdout enters the model's context).
- You SHALL append to `$CLAUDE_ENV_FILE`, never truncate — other hooks may share it.
- You SHALL no-op when `$CLAUDE_ENV_FILE` is unset (Codex today) — the consumer probe covers that host natively.
- You SHALL sanitize the id before writing an `export NAME='<id>'` line (e.g. reject anything outside `[A-Za-z0-9._-]`) and single-quote-escape any path you export — the env file is sourced shell.

Parse stdin JSON with `jq` when present, a `sed` fallback otherwise; useful stdin fields are `session_id` and `transcript_path` (exporting the latter saves consumers the path derivation).

Reference implementation: `plugins/friction-diagnostics/hooks/friction-session-env.sh`; behavioral fixtures (export, no-env-file, garbage stdin, hostile-id rejection) in `plugins/friction-diagnostics/skills/friction-diagnostics/tests/smoke-posix.sh` (Test 18).

## Deployment note

Claude Code installs a **version-keyed cache copy** of the plugin — content edits do not reach sessions until the plugin version is bumped and reinstalled. Codex references the marketplace **working tree live**. Long-running sessions (and their subagents) keep the plugin root they resolved at session start; restart to pick up a new version.
