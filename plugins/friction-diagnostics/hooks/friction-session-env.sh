#!/bin/sh
# SessionStart hook: session identity + boundary presence for friction records.
#
# OPTIONAL enrichment - fail-open by contract: exits 0 on every path and
# never blocks a session. Three jobs, all skipped silently when their
# preconditions are absent:
#
#   1. Sidecar: write <store>/session-ref.json (atomic, 0600) so records
#      filed in continued/resumed conversations attribute to the CURRENT
#      session instead of a stale env-file export. Written only when the
#      friction store directory already exists - the hook never creates
#      repository state. Caveat: two live sessions in one repo last-writer-
#      win the sidecar; session_ref is contractually optional enrichment.
#   2. Env file (Claude): export FRICTION_SESSION_REF / FRICTION_TRANSCRIPT_PATH
#      via $CLAUDE_ENV_FILE, deduping prior FRICTION_ lines first so continued
#      conversations do not accumulate stale duplicate exports.
#   3. Boundary presence: when the repo store has open events, print at most
#      two lines to stdout (SessionStart stdout enters session context) -
#      derived facts only, no imperatives. Silent when the store is absent,
#      empty, fully closed, or implausibly large. This also fires on resume
#      and post-compaction starts (no matcher), re-surfacing open traps at
#      exactly the moments prior context died.
#
# Works on both hosts: Codex ports this hooks.json unchanged; the env-file
# branch is Claude-guarded and Codex session identity comes natively from
# CODEX_THREAD_ID either way.
umask 077
{
  payload=$(cat 2>/dev/null || true)

  sid=
  tpath=
  pcwd=
  if [ -n "$payload" ]; then
    if command -v jq >/dev/null 2>&1; then
      sid=$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null || true)
      tpath=$(printf '%s' "$payload" | jq -r '.transcript_path // empty' 2>/dev/null || true)
      pcwd=$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null || true)
    else
      sid=$(printf '%s' "$payload" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | sed -n '1p')
      tpath=$(printf '%s' "$payload" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | sed -n '1p')
      pcwd=$(printf '%s' "$payload" | sed -n 's/.*"cwd"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | sed -n '1p')
    fi
  fi
  case "$sid" in
    *[!A-Za-z0-9._-]*) sid= ;;
  esac

  # --- Locate the repo's existing friction store; never create state.
  # Mirrors existing_local_dir_for_repo in the skill's _common.sh.
  base_dir=$pcwd
  [ -n "$base_dir" ] && [ -d "$base_dir" ] || base_dir=$(pwd)
  repo_root=$(git -C "$base_dir" rev-parse --show-toplevel 2>/dev/null || true)
  friction_dir=
  if [ -n "$repo_root" ]; then
    local_dir=$repo_root/.local
    if [ ! -d "$local_dir" ]; then
      local_dir=$(find "$repo_root" -maxdepth 1 -mindepth 1 -type d -name '.local*' 2>/dev/null | LC_ALL=C sort | sed -n '1p')
    fi
    if [ -n "$local_dir" ] && [ -d "$local_dir/reports/friction" ]; then
      friction_dir=$local_dir/reports/friction
    fi
  fi

  # --- 1. Sidecar (atomic, only into an existing store directory) ---
  if [ -n "$friction_dir" ] && [ -n "$sid" ]; then
    now_epoch=$(date +%s 2>/dev/null || printf '0')
    now_iso=$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || printf '')
    sidecar_tmp=$(mktemp "$friction_dir/.session-ref.XXXXXX.tmp" 2>/dev/null || true)
    if [ -n "$sidecar_tmp" ]; then
      if command -v jq >/dev/null 2>&1; then
        jq -n --arg sid "$sid" --arg tpath "$tpath" \
          --argjson epoch "${now_epoch:-0}" --arg iso "$now_iso" \
          '{session_id: $sid, transcript_path: $tpath, written_at: $epoch, written_at_iso: $iso, source: "SessionStart"}' \
          >"$sidecar_tmp" 2>/dev/null
      else
        tpath_json=$(printf '%s' "$tpath" | sed 's/\\/\\\\/g; s/"/\\"/g')
        printf '{"session_id":"%s","transcript_path":"%s","written_at":%s,"written_at_iso":"%s","source":"SessionStart"}\n' \
          "$sid" "$tpath_json" "${now_epoch:-0}" "$now_iso" >"$sidecar_tmp"
      fi
      if [ -s "$sidecar_tmp" ]; then
        mv -f "$sidecar_tmp" "$friction_dir/session-ref.json"
      else
        rm -f "$sidecar_tmp"
      fi
    fi
  fi

  # --- 2. Env-file exports (Claude only), deduped before appending ---
  if [ -n "${CLAUDE_ENV_FILE-}" ]; then
    if [ -f "$CLAUDE_ENV_FILE" ] && grep -q '^export FRICTION_' "$CLAUDE_ENV_FILE" 2>/dev/null; then
      env_tmp=$(mktemp 2>/dev/null || true)
      if [ -n "$env_tmp" ]; then
        grep -v '^export FRICTION_SESSION_REF=' "$CLAUDE_ENV_FILE" 2>/dev/null |
          grep -v '^export FRICTION_TRANSCRIPT_PATH=' >"$env_tmp" || true
        cat "$env_tmp" >"$CLAUDE_ENV_FILE"
        rm -f "$env_tmp"
      fi
    fi
    if [ -n "$sid" ]; then
      printf "export FRICTION_SESSION_REF='%s'\n" "$sid" >>"$CLAUDE_ENV_FILE"
    fi
    if [ -n "$tpath" ]; then
      tpath_escaped=$(printf '%s' "$tpath" | sed "s/'/'\\\\''/g")
      printf "export FRICTION_TRANSCRIPT_PATH='%s'\n" "$tpath_escaped" >>"$CLAUDE_ENV_FILE"
    fi
  fi

  # --- 3. Boundary presence: derived facts only, at most two lines ---
  if [ -n "$friction_dir" ] && [ -f "$friction_dir/events.jsonl" ] && command -v python3 >/dev/null 2>&1; then
    events_size=$(wc -c <"$friction_dir/events.jsonl" 2>/dev/null | tr -d ' ') || events_size=0
    if [ "${events_size:-0}" -gt 0 ] && [ "$events_size" -le 20971520 ]; then
      hook_dir=$(CDPATH='' cd -- "$(dirname "$0")" && pwd)
      lifecycle_py=$hook_dir/../skills/friction-diagnostics/scripts/lifecycle.py
      if [ -f "$lifecycle_py" ]; then
        summary=$(python3 -I "$lifecycle_py" --events-file "$friction_dir/events.jsonl" 2>/dev/null |
          python3 -I -c '
import json, sys
state = json.load(sys.stdin)
counts = state.get("counts") or {}
open_anchors = counts.get("open_anchors") or 0
if open_anchors:
    keyed = {}
    for info in (state.get("anchors") or {}).values():
        if info.get("open") and info.get("key"):
            key = info["key"]
            keyed[key] = keyed.get(key, 0) + (info.get("sightings") or 1)
    top = sorted(keyed.items(), key=lambda kv: (-kv[1], kv[0]))[:2]
    line = "friction: %d open anchor%s" % (open_anchors, "" if open_anchors == 1 else "s")
    if top:
        line += "; top recurring: " + ", ".join("%s x%d" % (k, n) for k, n in top)
    print(line)
' 2>/dev/null) || summary=
        if [ -n "$summary" ]; then
          printf '%s\n' "$summary"
          if [ -f "$friction_dir/known-traps.md" ]; then
            traps_count=$(grep -c '^- \[' "$friction_dir/known-traps.md" 2>/dev/null) || traps_count=0
            printf 'known-traps: %s (%s traps)\n' "$friction_dir/known-traps.md" "$traps_count"
          fi
        fi
      fi
    fi
  fi
} 2>/dev/null
exit 0
