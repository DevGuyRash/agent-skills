#!/bin/sh
set -eu

# Store artifacts are private by construction: every file or directory this
# process creates is user-only regardless of the caller's umask. Existing
# artifacts are never re-chmodded.
umask 077

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname "$0")" && pwd)
# shellcheck disable=SC1091
. "$SCRIPT_DIR/_common.sh"

MAX_BYTES=8192
MAX_TRAPS=15

print_help() {
  cat <<'EOF'
Usage:
  printf '%s' '{"traps":[{"anchor":"evt-0142","avoid":"one-line avoidance guidance"}]}' \
    | sh scripts/update-traps.sh [--events-file PATH]
  sh scripts/update-traps.sh --clear [--events-file PATH]

Grounded publisher for known-traps.md, the feed-forward distillate surfaced
at session start. The model supplies only judgment - which anchors matter and
the avoidance guidance; this script derives every clerical fact (key,
sighting count, last-seen date) from the event store and refuses anchors that
do not exist there. It does NOT gate on open/resolved state or sighting
counts: which traps deserve publishing is mend judgment, not script policy.

Input is one JSON object on stdin:
  {"traps": [{"anchor": "evt-NNNN", "avoid": "one line"}, ...]}
Anchors may be recurrence ids (followed to their friction anchor). Published
line shape, derived by this script:
  - [trap-key] avoidance guidance (evt-NNNN xCOUNT, last YYYY-MM-DD)

Caps: at most 15 traps and 8192 bytes. Publication replaces the whole file
atomically under the store lock; identical trap content is a no-op.

Options:
  --events-file PATH   Locate the traps file next to this events file
                       (default: repo-derived)
  --clear              Remove known-traps.md (all traps mended or decayed)
  --help
EOF
}

events_file=${FRICTION_EVENTS_FILE-}
clear_traps=0

trap release_friction_lock EXIT HUP INT TERM

while [ $# -gt 0 ]; do
  case "$1" in
    --events-file) events_file=${2-}; shift 2 ;;
    --clear) clear_traps=1; shift ;;
    --help|-h) print_help; exit 0 ;;
    *) die "Unknown argument: $1" ;;
  esac
done

if [ -z "$events_file" ]; then
  events_file=$(default_events_file_ro)
fi
events_dir=$(dirname "$events_file")
traps_file=$events_dir/known-traps.md

if [ "$clear_traps" -eq 1 ]; then
  if [ -f "$traps_file" ]; then
    acquire_friction_lock "$events_dir"
    rm -f "$traps_file"
    printf 'Removed %s\n' "$traps_file"
  else
    printf 'No traps file to remove at %s\n' "$traps_file"
  fi
  exit 0
fi

content=$(cat)
if [ -z "$(trim "$content")" ]; then
  die "stdin was empty - nothing written. Pipe the traps JSON in, or use --clear to remove the file."
fi

case "$content" in
  \{*|\[*) ;;
  *)
    die "update-traps.sh takes grounded JSON on stdin, not markdown. Provide:
  {\"traps\":[{\"anchor\":\"evt-NNNN\",\"avoid\":\"one-line avoidance guidance\"}]}
The script derives key, sighting count, and last-seen date from the store." ;;
esac

[ -f "$events_file" ] || die "Events file not found: $events_file (traps must be grounded in an existing store)"
if ! command -v python3 >/dev/null 2>&1; then
  die "python3 is required for update-traps.sh"
fi

lifecycle_state=$(mktemp)
if ! python3 -I "$SCRIPT_DIR/lifecycle.py" --events-file "$events_file" >"$lifecycle_state"; then
  rm -f "$lifecycle_state"
  die "Unable to derive lifecycle state from $events_file"
fi

py_out=$(python3 -I - "$lifecycle_state" "$content" <<'PY'
import json
import sys
from pathlib import Path

state = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
raw = sys.argv[2]
try:
    payload = json.loads(raw)
except json.JSONDecodeError as exc:
    print("Invalid JSON on stdin - nothing written. The publisher takes:", file=sys.stderr)
    print('  {"traps":[{"anchor":"evt-NNNN","avoid":"one-line avoidance guidance"}]}', file=sys.stderr)
    print(f"JSON error: line {exc.lineno}, column {exc.colno}: {exc.msg}", file=sys.stderr)
    sys.exit(2)

if isinstance(payload, list):
    traps = payload
elif isinstance(payload, dict):
    traps = payload.get("traps")
else:
    traps = None
if not isinstance(traps, list) or not traps:
    print('No traps found - nothing written. Provide {"traps":[{"anchor":"evt-NNNN","avoid":"..."}]}.', file=sys.stderr)
    sys.exit(2)

kinds = state.get("kinds") or {}
anchors = state.get("anchors") or {}
anchor_of = state.get("anchor_of") or {}

errors = []
lines = []
seen = set()
for i, entry in enumerate(traps):
    if not isinstance(entry, dict):
        errors.append(f"traps[{i}] must be an object")
        continue
    target = str(entry.get("anchor") or "").strip()
    avoid = " ".join(str(entry.get("avoid") or "").split())
    if not target:
        errors.append(f"traps[{i}].anchor is required")
        continue
    if not avoid:
        errors.append(f"traps[{i}].avoid is required")
        continue
    kind = kinds.get(target)
    if kind is None:
        errors.append(f"traps[{i}].anchor {target} does not exist in the store")
        continue
    if kind == "resolution":
        errors.append(f"traps[{i}].anchor {target} is a resolution record, not a friction anchor")
        continue
    anchor = target if kind == "friction" else anchor_of.get(target, "")
    info = anchors.get(anchor)
    if not anchor or info is None:
        errors.append(f"traps[{i}].anchor {target} does not resolve to a friction anchor")
        continue
    if anchor in seen:
        continue
    seen.add(anchor)
    key = info.get("key") or anchor
    lines.append("- [%s] %s (%s x%d, last %s)" % (
        key, avoid, anchor, info.get("sightings") or 1, info.get("last_seen") or "unknown"))

if errors:
    print("Ungrounded traps - nothing written:", file=sys.stderr)
    for item in errors:
        print(f"- {item}", file=sys.stderr)
    sys.exit(2)

counts = state.get("counts") or {}
print("OPEN\t%d" % (counts.get("open_anchors") or 0))
print("\n".join(lines))
PY
) || { rm -f "$lifecycle_state"; exit 2; }
rm -f "$lifecycle_state"

open_count=$(printf '%s\n' "$py_out" | awk -F'\t' 'NR==1 && $1=="OPEN" { print $2 }')
rendered=$(printf '%s\n' "$py_out" | awk 'NR>1')
rendered=$(sanitize_text "$rendered")

trap_count=$(printf '%s\n' "$rendered" | grep -c '^- \[' || true)
if [ "$trap_count" -eq 0 ]; then
  die "No trap lines rendered. Nothing written."
fi
if [ "$trap_count" -gt "$MAX_TRAPS" ]; then
  die "Too many traps: $trap_count (max $MAX_TRAPS). Keep the highest recurrence x impact; the rest stay reachable in events.jsonl."
fi

acquire_friction_lock "$events_dir"

if [ -f "$traps_file" ]; then
  existing_lines=$(grep '^- \[' "$traps_file" || true)
  if [ "$existing_lines" = "$rendered" ]; then
    printf 'FRICTION_TRAPS_FILE=%s\n' "$traps_file"
    printf 'Unchanged (%s traps) - not rewritten.\n' "$trap_count"
    exit 0
  fi
fi

generated=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
header="# Known traps (grounded pointers into events.jsonl - published by friction-mend)
Generated: $generated from $events_file (${open_count:-0} open friction events)
"

full="$header
$rendered"
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
