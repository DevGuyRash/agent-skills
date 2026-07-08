#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname "$0")" && pwd)
# shellcheck disable=SC1091
. "$SCRIPT_DIR/_common.sh"

print_help() {
  cat <<'EOF'
Usage:
  sh scripts/cluster-hints.sh [--events-file PATH] [--all]

Read-only mechanical starting points for clustering. Emits JSON with two
views: key_groups (records sharing a recurrence key) and token_candidates
(open events whose outcome texts share distinctive tokens). Hints inform;
they never bind — clustering judgment belongs to the mend agent.

Options:
  --events-file PATH   Events file (default: repo-derived)
  --all                Include resolved events (default: open only)
  --help
EOF
}

events_file=${FRICTION_EVENTS_FILE-}
include_all=0

while [ $# -gt 0 ]; do
  case "$1" in
    --events-file) events_file=${2-}; shift 2 ;;
    --all) include_all=1; shift ;;
    --help|-h) print_help; exit 0 ;;
    *) die "Unknown argument: $1" ;;
  esac
done

if [ -z "$events_file" ]; then
  events_file=$(default_events_file)
fi
[ -f "$events_file" ] || die "Events file not found: $events_file"

if ! command -v python3 >/dev/null 2>&1; then
  die "python3 is required for cluster-hints.sh"
fi

python3 -I - "$events_file" "$include_all" <<'PY'
import json, re, sys
from pathlib import Path

events_path = Path(sys.argv[1])
include_all = sys.argv[2] == "1"

MAX_KEY_GROUPS = 50
MAX_TOKEN_CANDIDATES = 25
MIN_SHARED_TOKENS = 3


def toks(text):
    t = (text or "")[:400].lower()
    t = re.sub(r"'[^']*'", " ", t)
    t = re.sub(r'"[^"]*"', " ", t)
    t = re.sub(r"/\S*", " ", t)
    t = re.sub(r"[0-9a-f]{6,}", " ", t)
    t = re.sub(r"[0-9]+", " ", t)
    t = re.sub(r"[^a-z]+", " ", t)
    return {w for w in t.split() if len(w) >= 3}


records = []
for raw in events_path.open(encoding="utf-8", errors="replace"):
    raw = raw.strip()
    if not raw:
        continue
    try:
        records.append(json.loads(raw))
    except json.JSONDecodeError:
        continue

resolved = set()
for rec in records:
    if (rec.get("kind") or "friction") == "resolution":
        resolved.update(rec.get("resolves") or [])

frictions = [r for r in records if (r.get("kind") or "friction") == "friction"]
recurrences = [r for r in records if (r.get("kind") or "friction") == "recurrence"]


def key_of(rec):
    return rec.get("recurrence_key") or rec.get("fingerprint") or ""


def is_open(rec):
    return (rec.get("event_id") or "") not in resolved


def date_of(rec):
    return (rec.get("recorded_at") or "")[:10]


# --- Key groups ---
groups = {}
for rec in frictions:
    k = key_of(rec)
    if k:
        groups.setdefault(k, []).append(rec)

recur_by_anchor = {}
for rec in recurrences:
    anchor = rec.get("recurs") or ""
    if anchor:
        recur_by_anchor.setdefault(anchor, []).append(rec)

key_groups = []
for k, members in groups.items():
    ids = [m.get("event_id") or "" for m in members]
    recs = [r for i in ids for r in recur_by_anchor.get(i, [])]
    group_open = any(is_open(m) for m in members)
    if not include_all and not group_open:
        continue
    dates = sorted(d for d in (date_of(r) for r in members + recs) if d)
    span = 0
    if len(dates) >= 2:
        from datetime import date
        first = date.fromisoformat(dates[0])
        last = date.fromisoformat(dates[-1])
        span = (last - first).days
    key_groups.append({
        "key": k,
        "event_ids": ids,
        "sightings": len(members) + len(recs),
        "open": group_open,
        "first_seen": dates[0] if dates else "",
        "last_seen": dates[-1] if dates else "",
        "span_days": span,
    })
key_groups.sort(key=lambda g: (-g["sightings"], g["key"]))
key_groups_total = len(key_groups)
key_groups = key_groups[:MAX_KEY_GROUPS]

# --- Token-overlap candidates (union-find over pairwise shared tokens) ---
pool = [r for r in frictions if include_all or is_open(r)]
token_sets = {(r.get("event_id") or ""): toks(r.get("actual_outcome") or "") for r in pool}
ids = [i for i, t in token_sets.items() if i and t]

parent = {i: i for i in ids}


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[rb] = ra


for idx, a in enumerate(ids):
    for b in ids[idx + 1:]:
        if len(token_sets[a] & token_sets[b]) >= MIN_SHARED_TOKENS:
            union(a, b)

components = {}
for i in ids:
    components.setdefault(find(i), []).append(i)

token_candidates = []
for members in components.values():
    if len(members) < 2:
        continue
    shared = set.intersection(*(token_sets[m] for m in members))
    token_candidates.append({
        "event_ids": sorted(members),
        "count": len(members),
        "shared_tokens": sorted(shared)[:8],
    })
token_candidates.sort(key=lambda c: (-c["count"], c["event_ids"]))
token_candidates_total = len(token_candidates)
token_candidates = token_candidates[:MAX_TOKEN_CANDIDATES]

print(json.dumps({
    "events_file": str(events_path),
    "scope": "all" if include_all else "open-only",
    "key_groups": key_groups,
    "key_groups_total": key_groups_total,
    "key_groups_truncated": key_groups_total > len(key_groups),
    "token_candidates": token_candidates,
    "token_candidates_total": token_candidates_total,
    "token_candidates_truncated": token_candidates_total > len(token_candidates),
}, ensure_ascii=False, indent=2))
PY
