#!/usr/bin/env python3
"""Order-aware per-store lifecycle reducer for friction event stores.

The single implementation of open/closed semantics. Every consumer (query,
reports, filing talkback, the --recur probe, the resolution writer, cluster
hints, the trap publisher, the session hook) derives lifecycle state from this
script's output instead of re-deriving it.

Semantics, per store, in physical stream order (the stream is append-only, so
line order is the clock):

  - a friction record opens its own cluster;
  - a resolution closes every anchor its `resolves` list reaches (recurrence
    ids are followed to their friction anchor, at most 5 hops);
  - a later recurrence whose chain lands on a closed anchor reopens it;
  - a later resolution closes it again.

Legacy tolerance: records without `kind` are v4 friction events; `fingerprint`
is the recurrence-key fallback; dangling pointers are state no-ops; malformed
lines are skipped (writers validate the stream separately).

Output is one JSON object:

  open       record id -> bool for every friction and recurrence record.
             Recurrence records inherit their anchor's state, pre-folded; a
             recurrence whose anchor cannot be resolved stays true (it is an
             unresolved sighting).
  anchor_of  recurrence id -> friction anchor id (chains pre-followed).
  kinds      record id -> kind (friction | recurrence | resolution).
  anchors    anchor id -> {open, closed_by, reopened_by, sightings,
             first_seen, last_seen, key, impact, title}.
  counts     {records, friction, recurrence, resolution, open_anchors,
             open_recurring_clusters}.

open_recurring_clusters counts distinct recurrence keys with total sightings
of 2 or more across the anchors sharing the key and at least one of those
anchors open - the "repeated open trap" number surfaced by filing talkback.
"""

import argparse
import json
import re
import sys
from pathlib import Path

MAX_HOPS = 5


def clean_title(rec):
    text = rec.get("title") or rec.get("actual_outcome") or ""
    return re.sub(r"\s+", " ", text).strip()[:60]


def read_records(events_path):
    order = []
    if not events_path.is_file():
        return order
    for raw in events_path.open(encoding="utf-8", errors="replace"):
        raw = raw.strip()
        if not raw:
            continue
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(rec, dict):
            continue
        order.append(rec)
    return order


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events-file", required=True)
    args = parser.parse_args()

    order = read_records(Path(args.events_file))

    records = {}
    for rec in order:
        rid = rec.get("event_id") or ""
        if rid:
            records[rid] = rec

    def anchor_target(start):
        """Follow recurrence chains from an id to its friction anchor id."""
        rec = records.get(start)
        hops = 0
        while rec is not None and (rec.get("kind") or "friction") == "recurrence" and hops < MAX_HOPS:
            rec = records.get(rec.get("recurs") or "")
            hops += 1
        if rec is not None and (rec.get("kind") or "friction") == "friction":
            return rec.get("event_id") or ""
        return ""

    anchors = {}
    anchor_of = {}
    kinds = {}
    counts = {"records": 0, "friction": 0, "recurrence": 0, "resolution": 0}

    for rec in order:
        rid = rec.get("event_id") or ""
        kind = rec.get("kind") or "friction"
        if kind not in ("friction", "recurrence", "resolution"):
            kind = "friction"
        counts["records"] += 1
        counts[kind] += 1
        if rid:
            kinds[rid] = kind
        when = (rec.get("recorded_at") or "")[:10]

        if kind == "friction":
            if not rid:
                continue
            anchors[rid] = {
                "open": True,
                "closed_by": "",
                "reopened_by": "",
                "sightings": 1,
                "first_seen": when,
                "last_seen": when,
                "key": rec.get("recurrence_key") or rec.get("fingerprint") or "",
                "impact": rec.get("impact") or "",
                "title": clean_title(rec),
            }
        elif kind == "recurrence":
            aid = anchor_target(rec.get("recurs") or "")
            if not aid or aid not in anchors:
                continue
            if rid:
                anchor_of[rid] = aid
            state = anchors[aid]
            state["sightings"] += 1
            if when > state["last_seen"]:
                state["last_seen"] = when
            if not state["open"]:
                state["open"] = True
                state["reopened_by"] = rid
        else:
            for target in rec.get("resolves") or []:
                if not isinstance(target, str):
                    continue
                aid = target if target in anchors else anchor_target(target)
                if aid and aid in anchors:
                    state = anchors[aid]
                    state["open"] = False
                    state["closed_by"] = rid

    open_map = {}
    for rid, kind in kinds.items():
        if kind == "friction":
            open_map[rid] = anchors[rid]["open"] if rid in anchors else True
        elif kind == "recurrence":
            aid = anchor_of.get(rid, "")
            open_map[rid] = anchors[aid]["open"] if aid in anchors else True

    sightings_by_key = {}
    open_keys = set()
    for state in anchors.values():
        key = state["key"]
        if not key:
            continue
        sightings_by_key[key] = sightings_by_key.get(key, 0) + state["sightings"]
        if state["open"]:
            open_keys.add(key)

    counts["open_anchors"] = sum(1 for state in anchors.values() if state["open"])
    counts["open_recurring_clusters"] = sum(
        1 for key, total in sightings_by_key.items() if total >= 2 and key in open_keys
    )

    json.dump(
        {
            "events_file": args.events_file,
            "open": open_map,
            "anchor_of": anchor_of,
            "kinds": kinds,
            "anchors": anchors,
            "counts": counts,
        },
        sys.stdout,
        ensure_ascii=False,
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
