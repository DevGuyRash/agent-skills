#!/bin/sh
set -eu

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
  --actual-outcome TEXT      What actually happened, verbatim. Never paraphrase.
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
lock_dir=
report_lock_acquired=0

cleanup_report_lock() {
  if [ "${report_lock_acquired:-0}" -eq 1 ] && [ -n "${lock_dir-}" ]; then
    rm -f "$lock_dir/pid" 2>/dev/null || true
    rmdir "$lock_dir" 2>/dev/null || true
  fi
}

acquire_report_lock() {
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
  report_lock_acquired=1
  printf '%s\n' "$$" >"$lock_dir/pid"
}

trap cleanup_report_lock EXIT HUP INT TERM

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
  python3 -I - "$events_file" "$events_dir/known-traps.md" "$scan_key" "$scan_outcome" "$scan_tags" "$scan_self" <<'PY' 2>/dev/null || true
import json, re, sys
from pathlib import Path

events_path = Path(sys.argv[1])
traps_path = Path(sys.argv[2])
key = sys.argv[3]
outcome = sys.argv[4]
tags_csv = sys.argv[5]
self_id = sys.argv[6]


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
recur_counts = {}
last_seen = {}
resolved_by = {}
for rec in records:
    rid = rec.get("event_id") or ""
    kind = rec.get("kind") or "friction"
    when = (rec.get("recorded_at") or "")[:10]
    if kind == "resolution":
        for target in rec.get("resolves") or []:
            resolved_by[target] = rid
    elif kind == "recurrence":
        anchor = rec.get("recurs") or ""
        if anchor:
            recur_counts[anchor] = recur_counts.get(anchor, 0) + 1
            if when > last_seen.get(anchor, ""):
                last_seen[anchor] = when
    else:
        frictions[rid] = rec
        if when > last_seen.get(rid, ""):
            last_seen[rid] = when


def key_of(rec):
    return rec.get("recurrence_key") or rec.get("fingerprint") or ""


def count_of(rid):
    return 1 + recur_counts.get(rid, 0)


def is_open(rid):
    return rid not in resolved_by


match = None
if key:
    candidates = [
        (rec.get("recorded_at") or "", rid)
        for rid, rec in frictions.items()
        if rid != self_id and key_of(rec) == key
    ]
    if candidates:
        _, mid = max(candidates)
        state = "open" if is_open(mid) else "resolved"
        resolver = resolved_by.get(mid, "")
        print("MATCH\t%s\t%s\t%s\t%d\t%s\t%s" % (
            mid, state, resolver, count_of(mid),
            last_seen.get(mid, ""), clean_title(frictions[mid])))
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
            rid, score, count_of(rid), last_seen.get(rid, ""),
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

sightings = {}
open_keys = set()
for rid, rec in frictions.items():
    k = key_of(rec)
    if not k:
        continue
    sightings[k] = sightings.get(k, 0) + count_of(rid)
    if is_open(rid):
        open_keys.add(k)
open_clusters = sum(1 for k, n in sightings.items() if n >= 2 and k in open_keys)

traps = 0
if traps_path.is_file():
    for line in traps_path.open(encoding="utf-8", errors="replace"):
        if line.lstrip().startswith("- ["):
            traps += 1
print("META\t%d\t%d" % (open_clusters, traps))
PY
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
  tb_clusters=$(scan_field "$tb_scan" META 2)
  tb_traps=$(scan_field "$tb_scan" META 3)
  if [ -n "$tb_clusters" ]; then
    printf 'open clusters: %s | known traps: %s (%s)\n' \
      "$tb_clusters" "${tb_traps:-0}" "$events_dir/known-traps.md"
  fi
}

load_json_overrides() {
  path=$1
  if ! command -v python3 >/dev/null 2>&1; then
    die "python3 is required for --from-json"
  fi
  scratch_dir=$2
  json_helper=$(mktemp "$(temp_root_dir)/friction-json-helper.XXXXXX.py")
  cat >"$json_helper" <<'PY'
import json
import shlex
import sys
import tempfile

path = sys.argv[1]
scratch_dir = sys.argv[2]
temp_root = sys.argv[3]
if path == "-":
    raw = sys.stdin.read()
else:
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()

if raw.strip() == "":
    print("error: stdin was empty - NO event was filed.", file=sys.stderr)
    print("Common causes: a heredoc terminator mismatch, or a previous command", file=sys.stderr)
    print("consumed stdin. Re-run with:", file=sys.stderr)
    print("  printf '%s' '<json>' | sh .../report-friction.sh --from-json -", file=sys.stderr)
    print("or pass a file path: --from-json <path>", file=sys.stderr)
    sys.exit(2)


def hint_for(err_msg: str) -> str:
    msg = err_msg.lower()
    if "expecting property name enclosed in double quotes" in msg:
        return "Hint: check for trailing commas or single-quoted keys."
    if "unterminated string" in msg:
        return "Hint: a quoted string is not closed."
    if "expecting value" in msg:
        return "Hint: a value is missing or a trailing comma is present."
    return "Hint: provide one JSON object with double-quoted keys and values."


try:
    data = json.loads(raw)
except json.JSONDecodeError as exc:
    lines = raw.splitlines() or [raw]
    offending = lines[exc.lineno - 1] if 0 < exc.lineno <= len(lines) else ""
    pointer = " " * max(exc.colno - 1, 0) + "^"
    print("Invalid JSON input for --from-json - NO event was filed.", file=sys.stderr)
    print(f"Line {exc.lineno}, column {exc.colno}", file=sys.stderr)
    if offending:
        print(offending, file=sys.stderr)
        print(pointer, file=sys.stderr)
    if path == "-":
        try:
            target_dir = scratch_dir if scratch_dir else temp_root
            import os
            os.makedirs(target_dir, exist_ok=True)
            fd, bad_path = tempfile.mkstemp(prefix="invalid-stdin.", suffix=".json", dir=target_dir)
            with open(fd, "w", encoding="utf-8", closefd=True) as bad_fh:
                bad_fh.write(raw)
            print(f"Saved payload to: {bad_path}", file=sys.stderr)
            print(f"Edit and re-file: sh .../report-friction.sh --from-json {bad_path}", file=sys.stderr)
        except Exception as save_exc:
            print(f"Unable to save invalid stdin payload: {save_exc}", file=sys.stderr)
    print(hint_for(exc.msg), file=sys.stderr)
    sys.exit(2)

if not isinstance(data, dict):
    print("Invalid JSON input for --from-json - NO event was filed.", file=sys.stderr)
    print("Hint: the payload must be one JSON object.", file=sys.stderr)
    sys.exit(2)

VALID_SOURCE_KINDS = {
    "artifact", "instruction", "tool",
    "assumption", "memory", "observation", "other",
}
TYPE_TO_KIND = {
    "file": "artifact", "url": "artifact", "documentation": "artifact",
    "conversation": "instruction", "audio": "observation", "visual": "observation",
    "tool": "tool", "assumption": "assumption", "memory": "memory",
    "observation": "observation", "other": "other",
}

errors = []
notes = []

# --- Coerce deprecated top-level fields (accept + note, never reject) ---
if data.get("pivot_information") is None and isinstance(data.get("hindsight"), str):
    data["pivot_information"] = data["hindsight"]
    notes.append("coerced deprecated 'hindsight' to pivot_information")
if data.get("recurrence_key") is None and isinstance(data.get("fingerprint_key"), str):
    data["recurrence_key"] = data["fingerprint_key"]
    notes.append("coerced deprecated 'fingerprint_key' to recurrence_key")

# --- Tags: accept array or scalar; fold aliases in ---
tags = data.get("tags")
if isinstance(tags, str):
    tags = [t.strip() for t in tags.split(",") if t.strip()]
    notes.append("coerced tags string to array")
elif tags is None:
    tags = []
elif isinstance(tags, list):
    coerced = []
    for item in tags:
        if isinstance(item, str):
            coerced.append(item)
        else:
            coerced.append(str(item))
            notes.append("coerced non-string tag to string")
    tags = coerced
else:
    errors.append("tags must be an array or comma-separated string")
    tags = []

aliases = data.get("aliases")
if aliases is not None:
    if isinstance(aliases, str):
        alias_items = [a.strip() for a in aliases.split(",") if a.strip()]
    elif isinstance(aliases, list):
        alias_items = [str(a) for a in aliases if a]
    else:
        alias_items = []
    if alias_items:
        tags = tags + [a for a in alias_items if a not in tags]
        notes.append("folded deprecated 'aliases' into tags")

# --- Build sources array ---
sources = data.get("sources")
if isinstance(sources, dict):
    sources = [sources]
    notes.append("wrapped single sources object in an array")
if sources is not None:
    if not isinstance(sources, list):
        errors.append("field must be an array when present: sources")
        sources = []
    for i, src in enumerate(sources):
        if not isinstance(src, dict):
            errors.append(f"sources[{i}] must be an object")
            continue
        if not src.get("kind") and src.get("type"):
            mapped = TYPE_TO_KIND.get(str(src["type"]).lower(), "other")
            src["kind"] = mapped
            src.pop("type", None)
            notes.append(f"coerced sources[{i}].type to kind '{mapped}'")
        if not src.get("kind"):
            errors.append(f"sources[{i}].kind is required (one of: {', '.join(sorted(VALID_SOURCE_KINDS))})")
        elif src["kind"] not in VALID_SOURCE_KINDS:
            errors.append(
                f"sources[{i}].kind must be one of: {', '.join(sorted(VALID_SOURCE_KINDS))} (got '{src['kind']}')"
            )
        if not src.get("ref"):
            errors.append(f"sources[{i}].ref is required")
        if src.get("claim") is None and isinstance(src.get("excerpt"), str):
            src["claim"] = src.pop("excerpt")
            notes.append(f"coerced sources[{i}].excerpt to claim")
        claim = src.get("claim")
        if isinstance(claim, str) and len(claim) > 2000:
            src["claim"] = claim[:2000] + f"...[truncated {len(claim) - 2000} chars at filing]"
            notes.append(f"sources[{i}].claim truncated to 2000 chars")
        for int_key in ("line", "end_line"):
            val = src.get(int_key)
            if val is not None and not isinstance(val, int):
                try:
                    src[int_key] = int(val)
                    notes.append(f"coerced sources[{i}].{int_key} to integer")
                except (TypeError, ValueError):
                    errors.append(f"sources[{i}].{int_key} must be an integer")
else:
    errors.append("missing required field: sources")

# --- Validate required narrative fields ---
required_narrative = [
    "actual_outcome",
    "expected_outcome",
    "reading",
    "decision",
    "pivot_information",
]
for req_key in required_narrative:
    value = data.get(req_key)
    if value is None:
        if req_key == "pivot_information":
            errors.append(
                "missing required field: pivot_information - name the single piece of "
                "information that, visible before acting, would have changed the outcome "
                "(or, when caught before harm, the fact a future agent should check first; "
                "or: 'none - the outcome was unknowable in advance, because ...')"
            )
        elif req_key == "decision":
            errors.append(
                "missing required field: decision - what did you do about it: the options "
                "you saw, the ones you set aside, and the action you took (even 'continued "
                "unchanged'), plus what made any deviation feel permitted at the time. "
                "Past tense - history, not proposal."
            )
        else:
            errors.append(f"missing required field: {req_key}")
    elif not isinstance(value, str):
        errors.append(f"field must be a string: {req_key}")
    elif value.strip() == "":
        errors.append(f"field must not be blank: {req_key}")

impact_val = data.get("impact")
if impact_val is not None:
    if impact_val not in ("blocked", "degraded", "noisy", "continued"):
        errors.append(f"impact must be one of: blocked, degraded, noisy, continued (got '{impact_val}')")

if errors:
    print("Invalid friction payload for --from-json - NO event was filed.", file=sys.stderr)
    for item in errors:
        print(f"- {item}", file=sys.stderr)
    sys.exit(2)


def normalize(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


keys = [
    ("title", "json_title"),
    ("actual_outcome", "json_actual_outcome"),
    ("expected_outcome", "json_expected_outcome"),
    ("reading", "json_reading"),
    ("decision", "json_decision"),
    ("pivot_information", "json_pivot_information"),
    ("note", "json_note"),
    ("repo_root", "json_repo_root"),
    ("impact", "json_impact"),
    ("recurrence_key", "json_recurrence_key"),
]

for data_key, var_name in keys:
    value = normalize(data.get(data_key))
    if value is not None:
        print(f"{var_name}={shlex.quote(value)}")

if tags:
    print(f"json_tags_csv={shlex.quote(','.join(tags))}")

print(f"json_sources_json={shlex.quote(json.dumps(sources, ensure_ascii=False, separators=(',', ':')))}")
if notes:
    print(f"json_notes={shlex.quote(chr(10).join('note: ' + n for n in notes))}")
PY
  json_output=$(python3 -I "$json_helper" "$path" "$scratch_dir" "$(temp_root_dir)") || {
    status=$?
    rm -f "$json_helper"
    return "$status"
  }
  rm -f "$json_helper"
  eval "$json_output"
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
  acquire_report_lock "$events_dir"
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
  sh "$SCRIPT_DIR/build-index.sh" --events-file "$events_file" >/dev/null
  printf 'FRICTION_TAGS_UPDATED=%s\n' "$add_tags_event_id"
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
  acquire_report_lock "$events_dir"
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
  sh "$SCRIPT_DIR/build-index.sh" --events-file "$events_file" >/dev/null
  printf 'FRICTION_ALIASES_UPDATED=%s\n' "$add_aliases_event_id"
  exit 0
fi

if [ -z "$repo_root" ]; then
  repo_root=$(git_repo_root)
fi
session_ref=$(resolve_session_ref)
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

  anchor_info=$(python3 -I - "$events_file" "$recur_id" <<'PY'
import json, re, sys
from pathlib import Path

events_path, target = Path(sys.argv[1]), sys.argv[2]
records = {}
recur_counts = {}
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
    if (rec.get("kind") or "friction") == "recurrence" and rec.get("recurs"):
        anchor = rec["recurs"]
        recur_counts[anchor] = recur_counts.get(anchor, 0) + 1

rec = records.get(target)
if rec is None:
    print("NOTFOUND")
    sys.exit(0)
hops = 0
while (rec.get("kind") or "friction") == "recurrence" and hops < 5:
    follow = rec.get("recurs") or ""
    rec = records.get(follow)
    if rec is None:
        print("NOTFOUND")
        sys.exit(0)
    hops += 1
kind = rec.get("kind") or "friction"
if kind != "friction":
    print("NOTANCHOR\t%s\t%s" % (rec.get("event_id") or "", kind))
    sys.exit(0)
anchor_id = rec.get("event_id") or ""
title = re.sub(r"\s+", " ", rec.get("title") or rec.get("actual_outcome") or "").strip()[:60]
print("ANCHOR\t%s\t%s\t%s\t%d\t%s" % (
    anchor_id,
    rec.get("impact") or "",
    rec.get("recurrence_key") or rec.get("fingerprint") or "",
    1 + recur_counts.get(anchor_id, 0),
    title,
))
PY
) || die "Unable to inspect events file for --recur"

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
  anchor_title=$(printf '%s\n' "$anchor_info" | awk -F'\t' '{ print $6; exit }')
  if [ "$anchor_id" != "$recur_id" ]; then
    printf 'note: %s is a recurrence of %s; filing against %s\n' "$recur_id" "$anchor_id" "$anchor_id" >&2
  fi
  if [ -z "$impact" ]; then
    impact=$anchor_impact
  fi
  impact=$(normalize_impact "$impact")

  acquire_report_lock "$events_dir"
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

  sh "$SCRIPT_DIR/build-index.sh" --events-file "$events_file" >/dev/null

  printf 'FRICTION_EVENTS_FILE=%s\n' "$events_file"
  printf 'FRICTION_EVENT_ID=%s\n' "$event_id"
  printf 'FRICTION_RECURS=%s\n' "$anchor_id"
  printf '\nAnchor %s "%s" now x%s\n' "$anchor_id" "$anchor_title" "$((anchor_count + 1))"
  scan_output=$(store_scan "" "" "" "$event_id")
  tb_traps=$(scan_field "$scan_output" META 3)
  tb_clusters=$(scan_field "$scan_output" META 2)
  if [ -n "$tb_clusters" ]; then
    printf 'open clusters: %s | known traps: %s (%s)\n' \
      "$tb_clusters" "${tb_traps:-0}" "$events_dir/known-traps.md"
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
    src_fields="$(json_string "kind" "$source_kind"),$(json_string "ref" "$source_ref")"
    if [ -n "$source_claim" ]; then src_fields="$src_fields,$(json_string "claim" "$(sanitize_text "$source_claim")")"; fi
    src_line_val=$(safe_int "$source_line")
    src_end_line_val=$(safe_int "$source_end_line")
    if [ "$src_line_val" -gt 0 ]; then src_fields="$src_fields,$(json_number "line" "$src_line_val")"; fi
    if [ "$src_end_line_val" -gt 0 ]; then src_fields="$src_fields,$(json_number "end_line" "$src_end_line_val")"; fi
    sources_json="[{${src_fields}}]"
  else
    die "Missing required source: provide --source-ref (and --source-kind) or use --from-json with a sources array. Ask: what did you trust that betrayed you?"
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

# Validate narrative floors (blank-guards only), then apply caps
validate_narrative_length "actual_outcome" "$actual_outcome" 15
validate_narrative_length "expected_outcome" "$expected_outcome" 15
validate_narrative_length "reading" "$reading" 30
validate_narrative_length "decision" "$decision" 15
actual_outcome=$(cap_narrative "actual_outcome" "$actual_outcome")
expected_outcome=$(cap_narrative "expected_outcome" "$expected_outcome")
reading=$(cap_narrative "reading" "$reading")
decision=$(cap_narrative "decision" "$decision")
pivot_information=$(cap_narrative "pivot_information" "$pivot_information")
if [ -n "$note" ]; then
  note=$(cap_narrative "note" "$note")
fi

reading_length=$(printf '%s' "$reading" | wc -c | tr -d ' ')
if [ "$reading_length" -lt 200 ]; then
  {
    printf 'INFO: reading is %s chars. A future reader should be able to form their own\n' "$reading_length"
    printf 'opinion from your account alone. If there is more to tell, consider:\n'
    rotated_questions reading 2
  } >&2
fi
decision_length=$(printf '%s' "$decision" | wc -c | tr -d ' ')
if [ "$decision_length" -lt 150 ]; then
  {
    printf 'INFO: decision is %s chars. The weighing is the data: options seen, set aside,\n' "$decision_length"
    printf 'and the license for any deviation. If there is more to tell, consider:\n'
    rotated_questions decision 2
  } >&2
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

acquire_report_lock "$events_dir"

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

sh "$SCRIPT_DIR/build-index.sh" --events-file "$events_file" >/dev/null

printf 'FRICTION_EVENTS_FILE=%s\n' "$events_file"
printf 'FRICTION_INDEX_FILE=%s\n' "$index_file"
printf 'FRICTION_EVENT_ID=%s\n' "$event_id"
printf 'FRICTION_RECURRENCE_KEY=%s\n' "$recurrence_key"
if [ -n "$repo_root" ]; then
  printf 'FRICTION_REPO_ROOT=%s\n' "$repo_root"
fi

# Talkback: the store briefs the agent at the point of action
printf '\n'
scan_output=$(store_scan "" "$actual_outcome" "$tags_csv" "$event_id")
print_talkback "$scan_output"
printf 'If this trap bites again: sh %s/report-friction.sh --recur %s --actual-outcome "..."\n' "$SCRIPT_DIR" "$event_id"
printf 'To add tags: sh %s/report-friction.sh --add-tags %s "tag1,tag2"\n' "$SCRIPT_DIR" "$event_id"
