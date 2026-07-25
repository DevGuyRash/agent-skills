#!/bin/sh
set -eu

# Store artifacts are private by construction: every file or directory this
# process creates is user-only regardless of the caller's umask. Existing
# artifacts are never re-chmodded.
umask 077

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname "$0")" && pwd)
# shellcheck disable=SC1091
. "$SCRIPT_DIR/_common.sh"

QUESTIONS_FILE=$SCRIPT_DIR/../assets/interview-questions.txt

print_help() {
  cat <<'EOF'
Usage:
  sh scripts/report-friction.sh [--events-file PATH] --from-json PATH|-
  sh scripts/report-friction.sh [--events-file PATH] [fields]
  sh scripts/report-friction.sh --recur EVENT_ID --actual-outcome "..." [--note "..."] [--impact VALUE]
  sh scripts/report-friction.sh --interview

Canonical target resolution:
  --events-file PATH     Explicit canonical event log path.
  If omitted, the tool writes to the repo-scoped rolling log derived from the
  current git root, or to a deterministic temp-root path outside a git repo.

Structured input (primary path):
  --from-json PATH|-     Load record fields from JSON on disk or stdin.
                         Prefer stdin for shell-sensitive or multiline text.

Composed fields, in composition order:
  --actual-outcome TEXT      What actually happened - exact text when text
                             exists; else a labeled observation, measurement,
                             or explicit non-occurrence.
  --expected-outcome TEXT    What you predicted, and what grounded the prediction.
  --reading TEXT             The account from inside the decision.
  --decision TEXT            What you did about it: options seen, set aside, the
                             action taken, and the license for any deviation.
                             History, not proposal.
  --pivot-information TEXT   The single piece of information that would have
                             changed the outcome, and where it lives.
  --impact VALUE             blocked | degraded | noisy | continued
  --recurrence-key TEXT      Optional stable trap slug (2-5 hyphenated words).
  --tags TEXT                Optional comma-separated labels.
  --note TEXT                Optional free slot: whatever mattered that no field
                             asked for.
  --title TEXT               Optional; auto-derived from actual outcome when omitted.

Source fields (single source via CLI; use --from-json for multiple):
  --source-kind KIND     One of: artifact, instruction, tool, assumption,
                         memory, observation, other
  --source-ref TEXT      Path, URL, tool name, or a label naming the belief
  --source-claim TEXT    What you believed it said or would do (verbatim quote
                         for artifact/instruction)
  --source-line INT      Start line (artifacts)
  --source-end-line INT  End line (artifacts)

Recurrence (cheap path for a known trap that bit again):
  --recur EVENT_ID       File a recurrence record against a prior event.
                         Requires --actual-outcome; --note and --impact optional
                         (impact defaults to the anchor's).
  --distinct             File a full event even when an identical recurrence
                         key already exists in the stream.

Aids:
  --interview            Print rotated eliciting questions and exit.

Identity:
  --repo-root PATH

Tag management (run after initial record creation):
  --add-tags EVENT_ID "tag1,tag2,tag3"
  --add-aliases EVENT_ID "alias1,alias2"   (legacy v4 events only)

Deprecated inputs (accepted and coerced with a note, never rejected):
  --hindsight TEXT       Stored as pivot_information
  --aliases TEXT         Folded into tags
  --source-type TYPE     Mapped to --source-kind
  --source-excerpt TEXT  Stored as the source claim
  --fingerprint-key TEXT Stored as the recurrence key

Exit codes:
  0  record written
  1  invalid arguments or unrecoverable validation failure
  2  input error on --from-json (empty stdin, malformed JSON, bad payload)
  3  duplicate soft-stop: an identical recurrence key exists; re-run with
     --recur EVENT_ID (repeat) or --distinct (new). Nothing was written.

Other:
  --help
EOF
}

events_file=${FRICTION_EVENTS_FILE-}
from_json=
title=
expected_outcome=
actual_outcome=
reading=
decision=
pivot_information=
note=
repo_root=
impact=
tags_csv=
aliases_csv=
recurrence_key=
recur_id=
distinct=0
interview=0
add_tags_event_id=
add_tags_csv=
add_aliases_event_id=
add_aliases_csv=
source_kind=
source_ref=
source_line=
source_end_line=
source_claim=
sources_json=
cli_notes=

trap release_friction_lock EXIT HUP INT TERM

add_cli_note() {
  if [ -n "$cli_notes" ]; then
    cli_notes="$cli_notes
note: $1"
  else
    cli_notes="note: $1"
  fi
}

# Print up to N rotated eliciting questions, optionally filtered to one field.
# Rotation is the mechanical anti-convergence source: the pool varies what the
# composer sees, so no single phrasing becomes the template.
rotated_questions() {
  field_filter=$1
  count=$2
  [ -f "$QUESTIONS_FILE" ] || return 0
  seed=$(od -An -N4 -tu4 /dev/urandom 2>/dev/null | tr -d ' ')
  case "$seed" in ''|*[!0-9]*) seed=$$ ;; esac
  awk -F'\t' -v want="$field_filter" -v seed="$seed" '
    BEGIN { srand(seed) }
    /^[[:space:]]*#/ { next }
    NF >= 2 {
      if (want == "" || $1 == want) { k++; line[k] = "[" $1 "] " $2 }
    }
    END {
      for (i = k; i > 1; i--) {
        j = int(rand() * i) + 1
        tmp = line[j]; line[j] = line[i]; line[i] = tmp
      }
      for (i = 1; i <= k; i++) print line[i]
    }' "$QUESTIONS_FILE" | sed -n "1,${count}p"
}

# Cap a narrative field, marking the truncation in the stored text and on stderr.
cap_narrative() {
  cap_label=$1
  cap_value=$2
  cap_limit=${3:-20000}
  cap_length=$(printf '%s' "$cap_value" | wc -c | tr -d ' ')
  if [ "$cap_length" -gt "$cap_limit" ]; then
    printf 'note: %s truncated from %s to %s chars at filing\n' "$cap_label" "$cap_length" "$cap_limit" >&2
    printf '%s...[truncated %s chars at filing]' \
      "$(printf '%s' "$cap_value" | cut -c1-"$cap_limit")" "$((cap_length - cap_limit))"
  else
    printf '%s' "$cap_value"
  fi
}

# Scan the store and describe it relative to a candidate record. Pure function
# of (args, store): all recurrence and dedup knowledge lives here, never in
# agent memory. Output is TSV; failures degrade to an empty scan (never block
# filing because the scanner broke).
store_scan() {
  scan_key=$1
  scan_outcome=$2
  scan_tags=$3
  scan_self=$4
  scan_state=$(mktemp)
  python3 -I "$SCRIPT_DIR/lifecycle.py" --events-file "$events_file" >"$scan_state" 2>/dev/null || printf '{}\n' >"$scan_state"
  python3 -I - "$events_file" "$events_dir/known-traps.md" "$scan_key" "$scan_outcome" "$scan_tags" "$scan_self" "$scan_state" <<'PY' 2>/dev/null || true
import json, re, sys
from pathlib import Path

events_path = Path(sys.argv[1])
traps_path = Path(sys.argv[2])
key = sys.argv[3]
outcome = sys.argv[4]
tags_csv = sys.argv[5]
self_id = sys.argv[6]

# Lifecycle state comes from lifecycle.py - the one order-aware reducer.
try:
    state = json.loads(Path(sys.argv[7]).read_text(encoding="utf-8"))
except Exception:
    state = {}
open_map = state.get("open") or {}
anchors_state = state.get("anchors") or {}
state_counts = state.get("counts") or {}


def toks(text):
    t = (text or "")[:400].lower()
    t = re.sub(r"'[^']*'", " ", t)
    t = re.sub(r'"[^"]*"', " ", t)
    t = re.sub(r"/\S*", " ", t)
    t = re.sub(r"[0-9a-f]{6,}", " ", t)
    t = re.sub(r"[0-9]+", " ", t)
    t = re.sub(r"[^a-z]+", " ", t)
    return {w for w in t.split() if len(w) >= 3}


def clean_title(rec):
    text = rec.get("title") or rec.get("actual_outcome") or ""
    return re.sub(r"\s+", " ", text).strip()[:60]


records = []
if events_path.is_file():
    for raw in events_path.open(encoding="utf-8", errors="replace"):
        raw = raw.strip()
        if not raw:
            continue
        try:
            records.append(json.loads(raw))
        except json.JSONDecodeError:
            continue

frictions = {}
for rec in records:
    if (rec.get("kind") or "friction") == "friction":
        frictions[rec.get("event_id") or ""] = rec


def key_of(rec):
    return rec.get("recurrence_key") or rec.get("fingerprint") or ""


def anchor_info(rid):
    return anchors_state.get(rid) or {}


def count_of(rid):
    return anchor_info(rid).get("sightings") or 1


def last_seen_of(rid):
    return anchor_info(rid).get("last_seen") or ""


def is_open(rid):
    return bool(open_map.get(rid, True))


match = None
if key:
    candidates = [
        (rec.get("recorded_at") or "", rid)
        for rid, rec in frictions.items()
        if rid != self_id and key_of(rec) == key
    ]
    if candidates:
        _, mid = max(candidates)
        match_state = "open" if is_open(mid) else "resolved"
        resolver = anchor_info(mid).get("closed_by") or ""
        print("MATCH\t%s\t%s\t%s\t%d\t%s\t%s" % (
            mid, match_state, resolver, count_of(mid),
            last_seen_of(mid), clean_title(frictions[mid])))
        match = mid

target = toks(outcome)
if target:
    scored = []
    for rid, rec in frictions.items():
        if rid == self_id or rid == match:
            continue
        other = toks(rec.get("actual_outcome") or "")
        if not other:
            continue
        union = target | other
        score = len(target & other) / len(union) if union else 0.0
        if score >= 0.25:
            scored.append((is_open(rid), score, rid))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    for is_open_flag, score, rid in scored[:3]:
        print("SIM\t%s\t%.2f\t%d\t%s\t%s" % (
            rid, score, count_of(rid), last_seen_of(rid),
            clean_title(frictions[rid])))

for tag in [t.strip().lower() for t in tags_csv.split(",") if t.strip()]:
    hits = 0
    for rid, rec in frictions.items():
        if rid == self_id:
            continue
        stored = rec.get("tags") or []
        if isinstance(stored, list) and tag in [str(t).lower() for t in stored]:
            hits += 1
    print("TAG\t%s\t%d" % (tag, hits))

open_anchors = state_counts.get("open_anchors")
if open_anchors is None:
    open_anchors = sum(1 for rid in frictions if is_open(rid))
open_clusters = state_counts.get("open_recurring_clusters") or 0

traps = 0
if traps_path.is_file():
    for line in traps_path.open(encoding="utf-8", errors="replace"):
        if line.lstrip().startswith("- ["):
            traps += 1
print("META\t%d\t%d\t%d" % (open_anchors, open_clusters, traps))
PY
  rm -f "$scan_state"
}

scan_field() {
  printf '%s\n' "$1" | awk -F'\t' -v tag="$2" -v col="$3" '$1==tag { print $col; exit }'
}

# Render the talkback block: the store briefing the agent so no session memory
# is ever required for correct behavior.
print_talkback() {
  tb_scan=$1
  tb_sim=$(printf '%s\n' "$tb_scan" | awk -F'\t' '$1=="SIM" {
    printf "  %s (sim %s, x%s, last %s) %s\n", $2, $3, $4, $5, $6 }')
  if [ -n "$tb_sim" ]; then
    printf 'Similar prior events:\n%s\n' "$tb_sim"
  fi
  tb_tags=$(printf '%s\n' "$tb_scan" | awk -F'\t' '$1=="TAG" {
    if ($3 > 0) { seen = seen sep $2 " x" $3; sep = ", " }
    else { fresh = fresh fsep $2; fsep = ", " } }
    END {
      if (seen != "") printf "tags seen before: %s", seen
      if (fresh != "") { if (seen != "") printf "; "; printf "new tags: %s", fresh }
      if (seen != "" || fresh != "") printf "\n" }')
  if [ -n "$tb_tags" ]; then
    printf '%s\n' "$tb_tags"
  fi
  tb_open=$(scan_field "$tb_scan" META 2)
  tb_clusters=$(scan_field "$tb_scan" META 3)
  tb_traps=$(scan_field "$tb_scan" META 4)
  if [ -n "$tb_open" ]; then
    printf 'open anchors: %s | open recurring clusters (2+ sightings): %s | known traps: %s (%s)\n' \
      "$tb_open" "${tb_clusters:-0}" "${tb_traps:-0}" "$events_dir/known-traps.md"
  fi
}

load_json_overrides() {
  path=$1
  if ! command -v python3 >/dev/null 2>&1; then
    die "python3 is required for --from-json"
  fi
  scratch_dir=$2

  # from_json.py owns parsing, coercion, validation, and redaction. The
  # shared redaction rules travel as trailing argv pairs so the shell and
  # python sanitizers stay one list.
  set --
  while IFS="$(printf '\t')" read -r redact_pattern redact_replacement; do
    [ -n "$redact_pattern" ] || continue
    set -- "$@" "$redact_pattern" "$redact_replacement"
  done <<EOF
$(friction_redaction_rules)
EOF

  json_output=$(python3 -I "$SCRIPT_DIR/from_json.py" "$path" "$scratch_dir" "$(temp_root_dir)" "$@") || return $?

  # Decode "name<TAB>base64" lines. No eval: payload-derived text is never
  # shell-parsed. The heredoc keeps the loop in this shell so assignments
  # survive into the caller.
  json_tab=$(printf '\t')
  while IFS="$json_tab" read -r json_field json_encoded; do
    [ -n "$json_field" ] || continue
    json_value=$(base64_decode "$json_encoded")
    case "$json_field" in
      title) json_title=$json_value ;;
      actual_outcome) json_actual_outcome=$json_value ;;
      expected_outcome) json_expected_outcome=$json_value ;;
      reading) json_reading=$json_value ;;
      decision) json_decision=$json_value ;;
      pivot_information) json_pivot_information=$json_value ;;
      note) json_note=$json_value ;;
      repo_root) json_repo_root=$json_value ;;
      impact) json_impact=$json_value ;;
      recurrence_key) json_recurrence_key=$json_value ;;
      tags_csv) json_tags_csv=$json_value ;;
      sources_json) json_sources_json=$json_value ;;
      notes) json_notes=$json_value ;;
    esac
  done <<EOF
$json_output
EOF
}

load_json_field() {
  current=$1
  default=$2
  var_name=$3
  if [ "$current" != "$default" ]; then
    printf '%s\n' "$current"
    return 0
  fi
  eval "var_is_set=\${$var_name+x}"
  if [ "$var_is_set" != "x" ]; then
    printf '%s\n' "$current"
    return 0
  fi
  eval "printf '%s\n' \"\${$var_name}\""
}

while [ $# -gt 0 ]; do
  case "$1" in
    --events-file) events_file=${2-}; shift 2 ;;
    --from-json) from_json=${2-}; shift 2 ;;
    --title) title=${2-}; shift 2 ;;
    --actual-outcome) actual_outcome=${2-}; shift 2 ;;
    --expected-outcome) expected_outcome=${2-}; shift 2 ;;
    --reading) reading=${2-}; shift 2 ;;
    --decision) decision=${2-}; shift 2 ;;
    --pivot-information) pivot_information=${2-}; shift 2 ;;
    --hindsight)
      if [ -z "$pivot_information" ]; then
        pivot_information=${2-}
        add_cli_note "coerced deprecated --hindsight to pivot_information"
      else
        add_cli_note "ignored --hindsight because --pivot-information was provided"
      fi
      shift 2 ;;
    --note) note=${2-}; shift 2 ;;
    --repo-root) repo_root=${2-}; shift 2 ;;
    --impact) impact=${2-}; shift 2 ;;
    --tags) tags_csv=${2-}; shift 2 ;;
    --aliases)
      aliases_csv=${2-}
      add_cli_note "folded deprecated --aliases into tags"
      shift 2 ;;
    --recurrence-key) recurrence_key=${2-}; shift 2 ;;
    --fingerprint-key)
      if [ -z "$recurrence_key" ]; then
        recurrence_key=${2-}
        add_cli_note "coerced deprecated --fingerprint-key to recurrence_key"
      fi
      shift 2 ;;
    --recur) recur_id=${2-}; shift 2 ;;
    --distinct) distinct=1; shift ;;
    --interview) interview=1; shift ;;
    --add-tags) add_tags_event_id=${2-}; add_tags_csv=${3-}; shift 3 ;;
    --add-aliases) add_aliases_event_id=${2-}; add_aliases_csv=${3-}; shift 3 ;;
    --source-kind) source_kind=${2-}; shift 2 ;;
    --source-type)
      if [ -z "$source_kind" ]; then
        source_kind=$(coerce_source_type_to_kind "${2-}")
        add_cli_note "coerced deprecated --source-type '${2-}' to source kind '$source_kind'"
      fi
      shift 2 ;;
    --source-ref) source_ref=${2-}; shift 2 ;;
    --source-line) source_line=${2-}; shift 2 ;;
    --source-end-line) source_end_line=${2-}; shift 2 ;;
    --source-claim) source_claim=${2-}; shift 2 ;;
    --source-excerpt)
      if [ -z "$source_claim" ]; then
        source_claim=${2-}
        add_cli_note "coerced deprecated --source-excerpt to source claim"
      fi
      shift 2 ;;
    --help|-h) print_help; exit 0 ;;
    *) die "Unknown argument: $1" ;;
  esac
done

# --- --interview mode: print rotated eliciting questions and exit ---
if [ "$interview" -eq 1 ]; then
  printf 'Answer what applies, in any order. These questions rotate.\n\n'
  for interview_field in actual_outcome expected_outcome reading decision pivot_information sources recurrence_key; do
    rotated_questions "$interview_field" 2
  done
  exit 0
fi

if [ -n "$from_json" ]; then
  invalid_json_scratch_dir=
  resolved_repo_root=$repo_root
  if [ -z "$resolved_repo_root" ]; then
    resolved_repo_root=$(git_repo_root)
  fi
  if [ -n "$resolved_repo_root" ]; then
    invalid_json_scratch_dir=$(friction_scratch_dir_for_repo "$resolved_repo_root")
  fi
  load_json_overrides "$from_json" "$invalid_json_scratch_dir"
  title=$(load_json_field "$title" "" json_title)
  actual_outcome=$(load_json_field "$actual_outcome" "" json_actual_outcome)
  expected_outcome=$(load_json_field "$expected_outcome" "" json_expected_outcome)
  reading=$(load_json_field "$reading" "" json_reading)
  decision=$(load_json_field "$decision" "" json_decision)
  pivot_information=$(load_json_field "$pivot_information" "" json_pivot_information)
  note=$(load_json_field "$note" "" json_note)
  repo_root=$(load_json_field "$repo_root" "" json_repo_root)
  impact=$(load_json_field "$impact" "" json_impact)
  recurrence_key=$(load_json_field "$recurrence_key" "" json_recurrence_key)
  tags_csv=$(load_json_field "$tags_csv" "" json_tags_csv)
  # sources_json is set directly by the Python helper
  sources_json=$(load_json_field "$sources_json" "" json_sources_json)
  json_notes_text=$(load_json_field "" "" json_notes)
  if [ -n "$json_notes_text" ]; then
    printf '%s\n' "$json_notes_text" >&2
  fi
fi

if [ -n "$cli_notes" ]; then
  printf '%s\n' "$cli_notes" >&2
fi

if [ -z "$events_file" ]; then
  events_file=$(default_events_file)
fi
events_dir=$(dirname "$events_file")
mkdir -p "$events_dir"

# --- --add-tags mode: patch tags on an existing event ---
if [ -n "$add_tags_event_id" ]; then
  if [ -z "$add_tags_csv" ]; then
    die "--add-tags requires EVENT_ID and TAGS arguments"
  fi
  if [ ! -f "$events_file" ]; then
    die "Events file not found: $events_file"
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    die "python3 is required for --add-tags"
  fi
  acquire_friction_lock "$events_dir"
  tmp_tags_file=$(mktemp "$events_dir/.events-tags.XXXXXX.tmp")
  if python3 -I - "$events_file" "$tmp_tags_file" "$add_tags_event_id" "$add_tags_csv" <<'PY'
import json, os, sys
events_path, output_path, target_id, tags_csv = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
new_tags = [t.strip().lower() for t in tags_csv.split(",") if t.strip()]
if not new_tags:
    print("No tags provided", file=sys.stderr)
    sys.exit(1)
found = False
with open(events_path, "r", encoding="utf-8") as src, open(output_path, "w", encoding="utf-8") as dst:
    for raw in src:
        stripped = raw.strip()
        if not stripped:
            dst.write(raw)
            continue
        event = json.loads(stripped)
        if event.get("event_id") == target_id:
            found = True
            existing = event.get("tags", [])
            if isinstance(existing, str):
                existing = [t.strip().lower() for t in existing.split(",") if t.strip()]
            merged = list(dict.fromkeys(existing + new_tags))
            event["tags"] = merged
            dst.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
        else:
            dst.write(raw)
if not found:
    try:
        os.remove(output_path)
    except FileNotFoundError:
        pass
    print(f"Event not found: {target_id}", file=sys.stderr)
    sys.exit(1)
os.replace(output_path, events_path)
PY
  then
    :
  else
    status=$?
    rm -f "$tmp_tags_file"
    exit "$status"
  fi
  printf 'FRICTION_TAGS_UPDATED=%s\n' "$add_tags_event_id"
  sh "$SCRIPT_DIR/build-index.sh" --events-file "$events_file" >/dev/null ||
    printf 'warning: index rebuild failed; the tag update was committed and INDEX.md is stale\n' >&2
  exit 0
fi

# --- --add-aliases mode: patch aliases on an existing (legacy v4) event ---
if [ -n "$add_aliases_event_id" ]; then
  if [ -z "$add_aliases_csv" ]; then
    die "--add-aliases requires EVENT_ID and ALIASES arguments"
  fi
  if [ ! -f "$events_file" ]; then
    die "Events file not found: $events_file"
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    die "python3 is required for --add-aliases"
  fi
  acquire_friction_lock "$events_dir"
  tmp_aliases_file=$(mktemp "$events_dir/.events-aliases.XXXXXX.tmp")
  if python3 -I - "$events_file" "$tmp_aliases_file" "$add_aliases_event_id" "$add_aliases_csv" <<'PY'
import json, os, sys
events_path, output_path, target_id, aliases_csv = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
new_aliases = [a.strip().lower() for a in aliases_csv.split(",") if a.strip()]
if not new_aliases:
    print("No aliases provided", file=sys.stderr)
    sys.exit(1)
found = False
with open(events_path, "r", encoding="utf-8") as src, open(output_path, "w", encoding="utf-8") as dst:
    for raw in src:
        stripped = raw.strip()
        if not stripped:
            dst.write(raw)
            continue
        event = json.loads(stripped)
        if event.get("event_id") == target_id:
            found = True
            existing = event.get("aliases", [])
            if isinstance(existing, str):
                existing = [a.strip().lower() for a in existing.split(",") if a.strip()]
            merged = list(dict.fromkeys(existing + new_aliases))
            event["aliases"] = merged
            dst.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
        else:
            dst.write(raw)
if not found:
    try:
        os.remove(output_path)
    except FileNotFoundError:
        pass
    print(f"Event not found: {target_id}", file=sys.stderr)
    sys.exit(1)
os.replace(output_path, events_path)
PY
  then
    :
  else
    status=$?
    rm -f "$tmp_aliases_file"
    exit "$status"
  fi
  printf 'FRICTION_ALIASES_UPDATED=%s\n' "$add_aliases_event_id"
  sh "$SCRIPT_DIR/build-index.sh" --events-file "$events_file" >/dev/null ||
    printf 'warning: index rebuild failed; the alias update was committed and INDEX.md is stale\n' >&2
  exit 0
fi

if [ -z "$repo_root" ]; then
  repo_root=$(git_repo_root)
fi
session_ref=$(resolve_session_ref "$events_dir")
record_version=$(schema_version)

# --- --recur mode: file a cheap recurrence record against a prior event ---
if [ -n "$recur_id" ]; then
  if [ ! -f "$events_file" ]; then
    die "Events file not found: $events_file (nothing to recur against)"
  fi
  validate_required_field "actual_outcome" "$actual_outcome"
  actual_outcome=$(sanitize_text "$actual_outcome")
  actual_outcome=$(cap_narrative "actual_outcome" "$actual_outcome")
  note=$(sanitize_text "$note")

  recur_state=$(mktemp)
  if ! python3 -I "$SCRIPT_DIR/lifecycle.py" --events-file "$events_file" >"$recur_state"; then
    rm -f "$recur_state"
    die "Unable to inspect events file for --recur"
  fi
  anchor_info=$(python3 -I - "$recur_state" "$recur_id" <<'PY'
import json, sys
from pathlib import Path

state = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
target = sys.argv[2]
kinds = state.get("kinds") or {}
anchors = state.get("anchors") or {}
anchor_of = state.get("anchor_of") or {}

kind = kinds.get(target)
if kind is None:
    print("NOTFOUND")
    sys.exit(0)
if kind == "resolution":
    print("NOTANCHOR\t%s\t%s" % (target, kind))
    sys.exit(0)
anchor_id = target if kind == "friction" else anchor_of.get(target, "")
info = anchors.get(anchor_id)
if not anchor_id or info is None:
    print("NOTFOUND")
    sys.exit(0)
print("ANCHOR\t%s\t%s\t%s\t%d\t%s\t%s" % (
    anchor_id,
    info.get("impact") or "",
    info.get("key") or "",
    info.get("sightings") or 1,
    "open" if info.get("open") else "resolved",
    info.get("title") or "",
))
PY
) || { rm -f "$recur_state"; die "Unable to inspect events file for --recur"; }
  rm -f "$recur_state"

  anchor_status=$(printf '%s\n' "$anchor_info" | awk -F'\t' '{ print $1; exit }')
  case "$anchor_status" in
    ANCHOR) ;;
    NOTANCHOR)
      die "--recur target resolves to a $(printf '%s\n' "$anchor_info" | awk -F'\t' '{print $3}') record; point at a friction event id" ;;
    *)
      die "Event not found for --recur: $recur_id" ;;
  esac
  anchor_id=$(printf '%s\n' "$anchor_info" | awk -F'\t' '{ print $2; exit }')
  anchor_impact=$(printf '%s\n' "$anchor_info" | awk -F'\t' '{ print $3; exit }')
  anchor_count=$(printf '%s\n' "$anchor_info" | awk -F'\t' '{ print $5; exit }')
  anchor_state=$(printf '%s\n' "$anchor_info" | awk -F'\t' '{ print $6; exit }')
  anchor_title=$(printf '%s\n' "$anchor_info" | awk -F'\t' '{ print $7; exit }')
  if [ "$anchor_id" != "$recur_id" ]; then
    printf 'note: %s is a recurrence of %s; filing against %s\n' "$recur_id" "$anchor_id" "$anchor_id" >&2
  fi
  if [ -z "$impact" ]; then
    impact=$anchor_impact
  fi
  impact=$(normalize_impact "$impact")

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
    printf '%s,' "$(json_string "kind" "recurrence")"
    json_string_if "session_ref" "$session_ref"
    printf '%s,' "$(json_string "events_file" "$events_file")"
    printf '%s,' "$(json_string "repo_root" "$repo_root")"
    printf '%s,' "$(json_string "recurs" "$anchor_id")"
    printf '%s,' "$(json_string "actual_outcome" "$actual_outcome")"
    json_string_if "note" "$note"
    printf '%s' "$(json_string "impact" "$impact")"
    printf '}\n'
  } >"$tmp_event"
  cat "$tmp_event" >>"$events_file"
  rm -f "$tmp_event"

  # Append is the commit point: receipt before derived work.
  printf 'FRICTION_EVENTS_FILE=%s\n' "$events_file"
  printf 'FRICTION_EVENT_ID=%s\n' "$event_id"
  printf 'FRICTION_RECURS=%s\n' "$anchor_id"

  sh "$SCRIPT_DIR/build-index.sh" --events-file "$events_file" >/dev/null ||
    printf 'warning: index rebuild failed; the record was committed and INDEX.md is stale\n' >&2
  printf '\nAnchor %s "%s" now x%s\n' "$anchor_id" "$anchor_title" "$((anchor_count + 1))"
  if [ "$anchor_state" = "resolved" ]; then
    printf 'Anchor %s was resolved; this recurrence reopens it.\n' "$anchor_id"
  fi
  scan_output=$(store_scan "" "" "" "$event_id")
  tb_open=$(scan_field "$scan_output" META 2)
  tb_clusters=$(scan_field "$scan_output" META 3)
  tb_traps=$(scan_field "$scan_output" META 4)
  if [ -n "$tb_open" ]; then
    printf 'open anchors: %s | open recurring clusters (2+ sightings): %s | known traps: %s (%s)\n' \
      "$tb_open" "${tb_clusters:-0}" "${tb_traps:-0}" "$events_dir/known-traps.md"
  fi
  exit 0
fi

# --- Full friction event ---

# Build sources JSON from CLI flags if not already set from --from-json
if [ -z "$sources_json" ]; then
  if [ -n "$source_ref" ]; then
    if [ -z "$source_kind" ]; then
      source_kind=artifact
      printf 'note: defaulted source kind to artifact; pass --source-kind if wrong\n' >&2
    fi
    validate_source_kind "$source_kind"
    source_claim=$(cap_narrative "source claim" "$source_claim" 2000)
    src_fields="$(json_string "kind" "$source_kind"),$(json_string "ref" "$(sanitize_text "$source_ref")")"
    if [ -n "$source_claim" ]; then src_fields="$src_fields,$(json_string "claim" "$(sanitize_text "$source_claim")")"; fi
    src_line_val=$(safe_int "$source_line")
    src_end_line_val=$(safe_int "$source_end_line")
    if [ "$src_line_val" -gt 0 ]; then src_fields="$src_fields,$(json_number "line" "$src_line_val")"; fi
    if [ "$src_end_line_val" -gt 0 ]; then src_fields="$src_fields,$(json_number "end_line" "$src_end_line_val")"; fi
    sources_json="[{${src_fields}}]"
  else
    die "Missing required source: provide --source-ref (and --source-kind) or use --from-json with a sources array. Ask: what inputs supported your prediction?"
  fi
fi

# Extract primary source ref for the recurrence-key fallback
primary_source_ref=$(extract_primary_source_ref "$sources_json")

# Validate required narrative fields (composition order)
validate_required_field "actual_outcome" "$actual_outcome"
validate_required_field "expected_outcome" "$expected_outcome"
validate_required_field "reading" "$reading"
if [ -z "$(trim "$decision")" ]; then
  printf 'Missing required field: --decision\n' >&2
  printf 'What did you do about it? Name the options you saw, the ones you set aside, and\n' >&2
  printf "the action you took - including 'continued unchanged' when true. If your path cut\n" >&2
  printf 'against anything documented as required, state what made that feel permitted at\n' >&2
  printf 'the moment you chose. This is history - the response you made, not a proposal.\n' >&2
  exit 1
fi
if [ -z "$(trim "$pivot_information")" ]; then
  printf 'Missing required field: pivot_information\n' >&2
  printf 'Name the single piece of information that, visible before acting, would have\n' >&2
  printf 'changed the outcome - or, when you caught this before harm, the fact a future\n' >&2
  printf "agent should check first. Or: 'none - unknowable in advance, because ...'\n" >&2
  exit 1
fi

# Validate impact
if [ -z "$impact" ]; then
  die "Missing required field: --impact (blocked, degraded, noisy, or continued)"
fi
impact=$(normalize_impact "$impact")

# Sanitize narrative fields
title=$(sanitize_text "$title")
actual_outcome=$(sanitize_text "$actual_outcome")
expected_outcome=$(sanitize_text "$expected_outcome")
reading=$(sanitize_text "$reading")
decision=$(sanitize_text "$decision")
pivot_information=$(sanitize_text "$pivot_information")
note=$(sanitize_text "$note")

# Apply caps. Required-field presence was validated above; there are no
# length floors - exact evidence can legitimately be short ("EPIPE"), and
# narrative quality is the skill contract's business, not this script's.
actual_outcome=$(cap_narrative "actual_outcome" "$actual_outcome")
expected_outcome=$(cap_narrative "expected_outcome" "$expected_outcome")
reading=$(cap_narrative "reading" "$reading")
decision=$(cap_narrative "decision" "$decision")
pivot_information=$(cap_narrative "pivot_information" "$pivot_information")
if [ -n "$note" ]; then
  note=$(cap_narrative "note" "$note")
fi

# Fold deprecated aliases input into tags
if [ -n "$aliases_csv" ]; then
  if [ -n "$tags_csv" ]; then
    tags_csv="$tags_csv,$aliases_csv"
  else
    tags_csv=$aliases_csv
  fi
  aliases_csv=
fi
tags_json=$(csv_to_json_array "$tags_csv")

# Auto-title from actual_outcome if not provided (title composes last, or never).
# Prefer the first line that carries the outcome itself over a leading "$ cmd"
# transcript line, so derived titles name the error, not the invocation.
if [ -z "$(trim "$title")" ]; then
  title_line=$(printf '%s\n' "$actual_outcome" | awk 'NF && $0 !~ /^\$[[:space:]]/ { print; exit }')
  if [ -z "$title_line" ]; then
    title_line=$actual_outcome
  fi
  title=$(truncate_line "$title_line" 80)
fi

recurrence_key=$(build_recurrence_key "$recurrence_key" "$actual_outcome" "$primary_source_ref")

acquire_friction_lock "$events_dir"

# Pre-write similar-check: shape disambiguation, never logging policy. An exact
# key match asks one question - repeat-pointer or new event? - with both
# answers one flag away. Nothing is written on exit 3; nothing is ever lost.
scan_output=$(store_scan "$recurrence_key" "$actual_outcome" "$tags_csv" "")
match_id=$(scan_field "$scan_output" MATCH 2)
if [ -n "$match_id" ] && [ "$distinct" -ne 1 ]; then
  match_state=$(scan_field "$scan_output" MATCH 3)
  match_resolver=$(scan_field "$scan_output" MATCH 4)
  match_count=$(scan_field "$scan_output" MATCH 5)
  match_last=$(scan_field "$scan_output" MATCH 6)
  match_title=$(scan_field "$scan_output" MATCH 7)
  if [ "$match_state" = "resolved" ]; then
    printf 'This trap was previously resolved by %s: %s "%s" (x%s, last seen %s).\n' \
      "$match_resolver" "$match_id" "$match_title" "$match_count" "$match_last"
    printf 'File as recurrence (reopens the cluster): --recur %s\n' "$match_id"
  else
    printf 'Similar open event: %s "%s" (x%s, last seen %s).\n' \
      "$match_id" "$match_title" "$match_count" "$match_last"
    printf 'File as recurrence:      --recur %s\n' "$match_id"
  fi
  printf 'File as distinct anyway: --distinct\n'
  print_talkback "$scan_output"
  printf 'NO event was filed (exit 3).\n'
  exit 3
fi

event_date=$(date -u '+%Y-%m-%d')
entry_number=0
if [ -f "$events_file" ]; then
  entry_number=$(wc -l <"$events_file" | tr -d ' ')
fi
entry_number=$((entry_number + 1))
event_id=$(printf 'evt-%04d' "$entry_number")
recorded=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
index_file=$events_dir/INDEX.md

# Emit record JSON in v5 stored key order (system block, then composition
# order: evidence before interpretation, classification late, title last)
tmp_event=$(mktemp "$events_dir/.event.XXXXXX.tmp")
{
  printf '{'
  printf '%s,' "$(json_string "event_id" "$event_id")"
  printf '%s,' "$(json_string "recorded_at" "$recorded")"
  printf '%s,' "$(json_string "schema_version" "$record_version")"
  printf '%s,' "$(json_string "kind" "friction")"
  json_string_if "session_ref" "$session_ref"
  printf '%s,' "$(json_string "events_file" "$events_file")"
  printf '%s,' "$(json_string "repo_root" "$repo_root")"
  printf '%s,' "$(json_string "actual_outcome" "$actual_outcome")"
  printf '%s,' "$(json_string "expected_outcome" "$expected_outcome")"
  printf '%s,' "$(json_string "reading" "$reading")"
  printf '%s,' "$(json_string "decision" "$decision")"
  printf '%s,' "$(json_string "pivot_information" "$pivot_information")"
  printf '"sources":%s,' "$sources_json"
  printf '%s,' "$(json_string "impact" "$impact")"
  printf '%s,' "$(json_string "recurrence_key" "$recurrence_key")"
  printf '"tags":%s,' "$tags_json"
  json_string_if "note" "$note"
  printf '%s' "$(json_string "title" "$title")"
  printf '}\n'
} >"$tmp_event"

record_bytes=$(wc -c <"$tmp_event" | tr -d ' ')
if [ "$record_bytes" -gt 65536 ]; then
  rm -f "$tmp_event"
  die "Record is ${record_bytes} bytes after caps (limit 65536). Trim the sources array or narrative fields and re-file."
fi

cat "$tmp_event" >>"$events_file"
rm -f "$tmp_event"

# The append above is the commit point: print the receipt before any derived
# work so an index failure can never masquerade as a failed filing (a blind
# retry after such a failure would duplicate the record).
printf 'FRICTION_EVENTS_FILE=%s\n' "$events_file"
printf 'FRICTION_INDEX_FILE=%s\n' "$index_file"
printf 'FRICTION_EVENT_ID=%s\n' "$event_id"
printf 'FRICTION_RECURRENCE_KEY=%s\n' "$recurrence_key"
if [ -n "$repo_root" ]; then
  printf 'FRICTION_REPO_ROOT=%s\n' "$repo_root"
fi

sh "$SCRIPT_DIR/build-index.sh" --events-file "$events_file" >/dev/null ||
  printf 'warning: index rebuild failed; the record was committed and INDEX.md is stale\n' >&2

# Talkback: the store briefs the agent at the point of action
printf '\n'
scan_output=$(store_scan "" "$actual_outcome" "$tags_csv" "$event_id")
print_talkback "$scan_output"
printf 'If this trap bites again: sh %s/report-friction.sh --recur %s --actual-outcome "..."\n' "$SCRIPT_DIR" "$event_id"
printf 'To add tags: sh %s/report-friction.sh --add-tags %s "tag1,tag2"\n' "$SCRIPT_DIR" "$event_id"
