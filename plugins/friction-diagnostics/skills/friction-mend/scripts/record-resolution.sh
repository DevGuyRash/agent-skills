#!/bin/sh
set -eu

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
lock_dir=
resolution_lock_acquired=0

cleanup_resolution_lock() {
  if [ "${resolution_lock_acquired:-0}" -eq 1 ] && [ -n "${lock_dir-}" ]; then
    rm -f "$lock_dir/pid" 2>/dev/null || true
    rmdir "$lock_dir" 2>/dev/null || true
  fi
}

acquire_resolution_lock() {
  target_dir=$1
  lock_dir=$target_dir/.report-friction.lock
  while ! mkdir "$lock_dir" 2>/dev/null; do
    if [ -f "$lock_dir/pid" ]; then
      lock_pid=$(sed -n '1p' "$lock_dir/pid" 2>/dev/null || true)
      case "$lock_pid" in
        ''|*[!0-9]*) ;;
        *)
          if ! kill -0 "$lock_pid" 2>/dev/null; then
            rm -f "$lock_dir/pid" 2>/dev/null || true
            rmdir "$lock_dir" 2>/dev/null || true
            continue
          fi
          ;;
      esac
    fi
    sleep 1
  done
  resolution_lock_acquired=1
  printf '%s\n' "$$" >"$lock_dir/pid"
}

trap cleanup_resolution_lock EXIT HUP INT TERM

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
  events_file=$(default_events_file)
fi
[ -f "$events_file" ] || die "Events file not found: $events_file (nothing to resolve)"
events_dir=$(dirname "$events_file")

if [ -z "$repo_root" ]; then
  repo_root=$(git_repo_root)
fi
session_ref=$(resolve_session_ref)
record_version=$(schema_version)

if ! command -v python3 >/dev/null 2>&1; then
  die "python3 is required for record-resolution.sh"
fi

# Normalize the target list: verify existence, follow recurrence pointers to
# their anchors, and report already-resolved ids (warn, never fail).
target_info=$(python3 -I - "$events_file" "$resolves_csv" <<'PY'
import json, sys
from pathlib import Path

events_path, csv = Path(sys.argv[1]), sys.argv[2]
targets = [t.strip() for t in csv.split(",") if t.strip()]

records = {}
resolved_by = {}
for raw in events_path.open(encoding="utf-8", errors="replace"):
    raw = raw.strip()
    if not raw:
        continue
    try:
        rec = json.loads(raw)
    except json.JSONDecodeError:
        continue
    rid = rec.get("event_id") or ""
    records[rid] = rec
    if (rec.get("kind") or "friction") == "resolution":
        for target in rec.get("resolves") or []:
            resolved_by[target] = rid

anchors = []
for target in targets:
    rec = records.get(target)
    if rec is None:
        print("MISSING\t%s" % target)
        continue
    hops = 0
    while (rec.get("kind") or "friction") == "recurrence" and hops < 5:
        follow = rec.get("recurs") or ""
        rec = records.get(follow)
        if rec is None:
            print("MISSING\t%s" % target)
            break
        hops += 1
    if rec is None:
        continue
    kind = rec.get("kind") or "friction"
    if kind != "friction":
        print("NOTFRICTION\t%s\t%s" % (target, kind))
        continue
    anchor = rec.get("event_id") or ""
    if anchor != target:
        print("FOLLOWED\t%s\t%s" % (target, anchor))
    if anchor in resolved_by:
        print("ALREADY\t%s\t%s" % (anchor, resolved_by[anchor]))
    if anchor not in anchors:
        anchors.append(anchor)

print("ANCHORS\t%s" % ",".join(anchors))
PY
) || die "Unable to inspect events file"

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

acquire_resolution_lock "$events_dir"
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

if [ -f "$SCRIPT_DIR/build-index.sh" ]; then
  sh "$SCRIPT_DIR/build-index.sh" --events-file "$events_file" >/dev/null
fi

open_count=$(sh "$SCRIPT_DIR/query-friction.sh" --events-file "$events_file" --open --kind friction --format json | jq 'length')

printf 'FRICTION_EVENTS_FILE=%s\n' "$events_file"
printf 'FRICTION_EVENT_ID=%s\n' "$event_id"
printf 'FRICTION_RESOLVED=%s\n' "$anchors_csv"
printf '\nOpen friction events remaining: %s\n' "$open_count"
