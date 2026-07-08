#!/bin/sh
# SessionStart hook: export session identity for friction records.
# OPTIONAL enrichment - fail-open by contract: exits 0 on every path, never
# blocks a session, never prints to stdout (SessionStart stdout enters
# context). Appends to $CLAUDE_ENV_FILE (never truncates - other hooks may
# share it); the env file is per-session, so concurrent sessions in one repo
# attribute correctly. Where the mechanism is absent (Codex today), no-ops
# and records simply omit session_ref.
{
  [ -n "${CLAUDE_ENV_FILE-}" ] || exit 0
  payload=$(cat 2>/dev/null || true)
  [ -n "$payload" ] || exit 0
  if command -v jq >/dev/null 2>&1; then
    sid=$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null || true)
    tpath=$(printf '%s' "$payload" | jq -r '.transcript_path // empty' 2>/dev/null || true)
  else
    sid=$(printf '%s' "$payload" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | sed -n '1p')
    tpath=$(printf '%s' "$payload" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | sed -n '1p')
  fi
  case "$sid" in
    *[!A-Za-z0-9._-]*) sid= ;;
  esac
  if [ -n "$sid" ]; then
    printf "export FRICTION_SESSION_REF='%s'\n" "$sid" >>"$CLAUDE_ENV_FILE"
  fi
  if [ -n "$tpath" ]; then
    tpath_escaped=$(printf '%s' "$tpath" | sed "s/'/'\\\\''/g")
    printf "export FRICTION_TRANSCRIPT_PATH='%s'\n" "$tpath_escaped" >>"$CLAUDE_ENV_FILE"
  fi
} 2>/dev/null
exit 0
