#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname "$0")" && pwd)
# shellcheck disable=SC1091
. "$SCRIPT_DIR/_common.sh"

MAX_BYTES=8192
MAX_TRAPS=15

print_help() {
  cat <<'EOF'
Usage:
  ... | sh scripts/update-traps.sh [--events-file PATH]
  sh scripts/update-traps.sh --clear [--events-file PATH]

Capped publisher for known-traps.md, the feed-forward distillate read at
session start. The model composes the content; this script only enforces
shape: at most 15 trap lines and 8192 bytes, atomic write, generated header.

Trap line format (one line per trap, anchor id keeps it a pointer into the
lossless store):
  - [trap-key] One-line statement of the trap and how to avoid it. (evt-0142 x14, last 2026-07-01)

Rules the caller owns: mended traps are deleted, not marked; traps that stop
recurring decay out at the next mend; prefer traps that bite across task
types; the whole file is regenerable from events.jsonl at any time.

Options:
  --events-file PATH   Locate the traps file next to this events file
                       (default: repo-derived)
  --clear              Remove known-traps.md (all traps mended or decayed)
  --help
EOF
}

events_file=${FRICTION_EVENTS_FILE-}
clear_traps=0

while [ $# -gt 0 ]; do
  case "$1" in
    --events-file) events_file=${2-}; shift 2 ;;
    --clear) clear_traps=1; shift ;;
    --help|-h) print_help; exit 0 ;;
    *) die "Unknown argument: $1" ;;
  esac
done

if [ -z "$events_file" ]; then
  events_file=$(default_events_file)
fi
events_dir=$(dirname "$events_file")
traps_file=$events_dir/known-traps.md

if [ "$clear_traps" -eq 1 ]; then
  if [ -f "$traps_file" ]; then
    rm -f "$traps_file"
    printf 'Removed %s\n' "$traps_file"
  else
    printf 'No traps file to remove at %s\n' "$traps_file"
  fi
  exit 0
fi

content=$(cat)
if [ -z "$(trim "$content")" ]; then
  die "stdin was empty - nothing written. Pipe the traps markdown in, or use --clear to remove the file."
fi

trap_count=$(printf '%s\n' "$content" | grep -c '^- \[' || true)
if [ "$trap_count" -eq 0 ]; then
  die "No trap lines found (expected lines starting with '- ['). Nothing written."
fi
if [ "$trap_count" -gt "$MAX_TRAPS" ]; then
  die "Too many traps: $trap_count (max $MAX_TRAPS). Keep the highest recurrence x impact; the rest stay reachable in events.jsonl."
fi

open_count=0
if [ -f "$events_file" ] && command -v jq >/dev/null 2>&1; then
  open_count=$(sh "$SCRIPT_DIR/query-friction.sh" --events-file "$events_file" --open --kind friction --format json 2>/dev/null | jq 'length' 2>/dev/null) || open_count=0
fi

generated=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
header="# Known traps (auto-distilled - read before acting)
Generated: $generated from $events_file ($open_count open friction events)
"

full="$header
$content"
byte_count=$(printf '%s\n' "$full" | wc -c | tr -d ' ')
if [ "$byte_count" -gt "$MAX_BYTES" ]; then
  die "Traps file would be ${byte_count} bytes (max $MAX_BYTES). Trim to the highest recurrence x impact traps."
fi

mkdir -p "$events_dir"
tmp_traps=$(mktemp "$events_dir/.known-traps.XXXXXX.tmp")
printf '%s\n' "$full" >"$tmp_traps"
mv -f "$tmp_traps" "$traps_file"

printf 'FRICTION_TRAPS_FILE=%s\n' "$traps_file"
printf 'Traps: %s | Bytes: %s\n' "$trap_count" "$byte_count"
