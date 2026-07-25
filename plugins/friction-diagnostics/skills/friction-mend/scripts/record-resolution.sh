#!/bin/sh
set -eu

# Store artifacts are private by construction: every file or directory this
# process creates is user-only regardless of the caller's umask. Existing
# artifacts are never re-chmodded.
umask 077

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname "$0")" && pwd)
# shellcheck disable=SC1091
. "$SCRIPT_DIR/_common.sh"

print_help() {
  cat <<'EOF'
Usage:
  sh scripts/record-resolution.sh --resolves "evt-A,evt-B" --action "..." [options]
  sh scripts/record-resolution.sh --resolves "evt-C" --wontfix "reason"

Provenance appender: the model resolves; this script only records that it
happened. It never edits or deletes existing records.

Required:
  --resolves IDS         Comma-separated friction event ids this resolution
                         closes. Recurrence ids are followed to their anchor.
  --action TEXT          What was done to mend (edit made, doc changed, ...).
  --wontfix TEXT         Shorthand for --action "wontfix: TEXT" — honest
                         closure of a noise cluster.

Optional:
  --ref TEXT             Provenance pointer: commit, path, or URL of the mend.
  --note TEXT            Short context note.
  --events-file PATH     Explicit events file (default: repo-derived).
  --repo-root PATH

Exit codes:
  0  resolution recorded
  1  invalid arguments or unknown event ids

Other:
  --help
EOF
}

events_file=${FRICTION_EVENTS_FILE-}
resolves_csv=
action=
wontfix=
ref=
note=
repo_root=

trap release_friction_lock EXIT HUP INT TERM

while [ $# -gt 0 ]; do
  case "$1" in
    --events-file) events_file=${2-}; shift 2 ;;
    --resolves) resolves_csv=${2-}; shift 2 ;;
    --action) action=${2-}; shift 2 ;;
    --wontfix) wontfix=${2-}; shift 2 ;;
    --ref) ref=${2-}; shift 2 ;;
    --note) note=${2-}; shift 2 ;;
    --repo-root) repo_root=${2-}; shift 2 ;;
    --help|-h) print_help; exit 0 ;;
    *) die "Unknown argument: $1" ;;
  esac
done

validate_required_field "resolves" "$resolves_csv"
if [ -n "$wontfix" ]; then
  if [ -n "$action" ]; then
    die "Provide --action or --wontfix, not both"
  fi
  action="wontfix: $wontfix"
fi
validate_required_field "action" "$action"

if [ -z "$events_file" ]; then
  events_file=$(default_events_file_ro)
fi
[ -f "$events_file" ] || die "Events file not found: $events_file (nothing to resolve)"
events_dir=$(dirname "$events_file")

if [ -z "$repo_root" ]; then
  repo_root=$(git_repo_root)
fi
session_ref=$(resolve_session_ref "$events_dir")
record_version=$(schema_version)

if ! command -v python3 >/dev/null 2>&1; then
  die "python3 is required for record-resolution.sh"
fi

# Normalize the target list against lifecycle.py state: verify existence,
# follow recurrence pointers to their anchors, and warn (never fail) when a
# target is already closed. A reopened anchor re-resolves without a warning -
# that is the intended close-again path.
lifecycle_state=$(mktemp)
if ! python3 -I "$SCRIPT_DIR/lifecycle.py" --events-file "$events_file" >"$lifecycle_state"; then
  rm -f "$lifecycle_state"
  die "Unable to inspect events file"
fi
target_info=$(python3 -I - "$lifecycle_state" "$resolves_csv" <<'PY'
import json, sys
from pathlib import Path

state = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
targets = [t.strip() for t in sys.argv[2].split(",") if t.strip()]
kinds = state.get("kinds") or {}
anchors_state = state.get("anchors") or {}
anchor_of = state.get("anchor_of") or {}

anchors = []
for target in targets:
    kind = kinds.get(target)
    if kind is None:
        print("MISSING\t%s" % target)
        continue
    if kind == "resolution":
        print("NOTFRICTION\t%s\t%s" % (target, kind))
        continue
    anchor = target if kind == "friction" else anchor_of.get(target, "")
    info = anchors_state.get(anchor)
    if not anchor or info is None:
        print("MISSING\t%s" % target)
        continue
    if anchor != target:
        print("FOLLOWED\t%s\t%s" % (target, anchor))
    if not info.get("open"):
        print("ALREADY\t%s\t%s" % (anchor, info.get("closed_by") or ""))
    if anchor not in anchors:
        anchors.append(anchor)

print("ANCHORS\t%s" % ",".join(anchors))
PY
) || { rm -f "$lifecycle_state"; die "Unable to inspect events file"; }
rm -f "$lifecycle_state"

missing=$(printf '%s\n' "$target_info" | awk -F'\t' '$1=="MISSING" { ids = ids sep $2; sep = ", " } END { print ids }')
if [ -n "$missing" ]; then
  die "Event ids not found: $missing"
fi
notfriction=$(printf '%s\n' "$target_info" | awk -F'\t' '$1=="NOTFRICTION" { ids = ids sep $2; sep = ", " } END { print ids }')
if [ -n "$notfriction" ]; then
  die "Not friction events (resolutions cannot resolve resolutions): $notfriction"
fi
printf '%s\n' "$target_info" | awk -F'\t' '$1=="FOLLOWED" { printf "note: %s is a recurrence of %s; resolving %s\n", $2, $3, $3 }' >&2
printf '%s\n' "$target_info" | awk -F'\t' '$1=="ALREADY" { printf "warning: %s was already resolved by %s; recording again\n", $2, $3 }' >&2
anchors_csv=$(printf '%s\n' "$target_info" | awk -F'\t' '$1=="ANCHORS" { print $2; exit }')
[ -n "$anchors_csv" ] || die "No resolvable event ids remained after normalization"

resolves_json=$(csv_to_json_array "$anchors_csv")
action=$(sanitize_text "$action")
note=$(sanitize_text "$note")

acquire_friction_lock "$events_dir"
entry_number=$(wc -l <"$events_file" | tr -d ' ')
entry_number=$((entry_number + 1))
event_id=$(printf 'evt-%04d' "$entry_number")
recorded=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

tmp_event=$(mktemp "$events_dir/.event.XXXXXX.tmp")
{
  printf '{'
  printf '%s,' "$(json_string "event_id" "$event_id")"
  printf '%s,' "$(json_string "recorded_at" "$recorded")"
  printf '%s,' "$(json_string "schema_version" "$record_version")"
  printf '%s,' "$(json_string "kind" "resolution")"
  json_string_if "session_ref" "$session_ref"
  printf '%s,' "$(json_string "events_file" "$events_file")"
  printf '%s,' "$(json_string "repo_root" "$repo_root")"
  printf '"resolves":%s,' "$resolves_json"
  printf '%s' "$(json_string "action" "$action")"
  if [ -n "$ref" ]; then printf ',%s' "$(json_string "ref" "$ref")"; fi
  if [ -n "$note" ]; then printf ',%s' "$(json_string "note" "$note")"; fi
  printf '}\n'
} >"$tmp_event"
cat "$tmp_event" >>"$events_file"
rm -f "$tmp_event"

# Append is the commit point: receipt before derived work, so an index or
# query failure can never make a committed resolution look unfiled.
printf 'FRICTION_EVENTS_FILE=%s\n' "$events_file"
printf 'FRICTION_EVENT_ID=%s\n' "$event_id"
printf 'FRICTION_RESOLVED=%s\n' "$anchors_csv"

if [ -f "$SCRIPT_DIR/build-index.sh" ]; then
  sh "$SCRIPT_DIR/build-index.sh" --events-file "$events_file" >/dev/null ||
    printf 'warning: index rebuild failed; the resolution was committed and INDEX.md is stale\n' >&2
fi

open_count=$(sh "$SCRIPT_DIR/query-friction.sh" --events-file "$events_file" --open --kind friction --format json | jq 'length') || open_count=unknown
printf '\nOpen friction events remaining: %s\n' "$open_count"
