#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname "$0")" && pwd)
# shellcheck disable=SC1091
. "$SCRIPT_DIR/_common.sh"

print_help() {
  cat <<'EOF'
Usage:
  sh scripts/generate-report.sh [--events-file PATH | --scan-dirs DIR [DIR...]] [filters] [report options]

Input:
  --events-file PATH        Single events file (default: auto-detected)
  --scan-dirs DIR [DIR...]  Recursively discover all events.jsonl files under
                            the given directories matching
                            */.local*/reports/friction/events.jsonl

Filters:
  --impact VALUE
  --fingerprint VALUE
  --tag VALUE               Substring match across tags
  --tag-exact VALUE         Exact tag match
  --alias VALUE             Substring match across aliases
  --alias-exact VALUE       Exact alias match
  --text PATTERN            Case-insensitive substring search across narrative fields
  --date YYYY-MM-DD
  --date-from YYYY-MM-DD
  --date-to YYYY-MM-DD
  --after ISO-TIMESTAMP     Filter events with recorded_at > TIMESTAMP
  --source-ref PATH

Report:
  --report-type TYPE        index|stats|cross-repo|per-repo|timeseries
                            index: synthesis dashboard (bounded size)
                            stats: health metrics incl. noise and convergence
  --group-by VALUE          impact|alias|tag
  --format md|json
  --output PATH
  --help
EOF
}

events_file=${FRICTION_EVENTS_FILE-}
scan_dirs=
impact=
fingerprint=
tag=
tag_exact=
alias_filter=
alias_exact=
text=
date_exact=
date_from=
date_to=
after=
source_ref=
report_type=index
group_by=
format=md
output_path=

append_multiline() {
  current=$1
  value=$2
  if [ -n "$current" ]; then
    printf '%s\n%s\n' "$current" "$value"
  else
    printf '%s\n' "$value"
  fi
}

while [ $# -gt 0 ]; do
  case "$1" in
    --events-file) events_file=${2-}; shift 2 ;;
    --scan-dirs)
      shift
      while [ $# -gt 0 ]; do
        case "$1" in
          --*) break ;;
          *)
            scan_dirs=$(append_multiline "$scan_dirs" "$1")
            shift
            ;;
        esac
      done
      ;;
    --impact) impact=${2-}; shift 2 ;;
    --fingerprint) fingerprint=${2-}; shift 2 ;;
    --tag) tag=${2-}; shift 2 ;;
    --tag-exact) tag_exact=${2-}; shift 2 ;;
    --alias) alias_filter=${2-}; shift 2 ;;
    --alias-exact) alias_exact=${2-}; shift 2 ;;
    --text) text=${2-}; shift 2 ;;
    --date) date_exact=${2-}; shift 2 ;;
    --date-from) date_from=${2-}; shift 2 ;;
    --date-to) date_to=${2-}; shift 2 ;;
    --after) after=${2-}; shift 2 ;;
    --source-ref) source_ref=${2-}; shift 2 ;;
    --report-type) report_type=${2-}; shift 2 ;;
    --group-by) group_by=${2-}; shift 2 ;;
    --format) format=${2-}; shift 2 ;;
    --output) output_path=${2-}; shift 2 ;;
    --help|-h) print_help; exit 0 ;;
    *) die "Unknown argument: $1" ;;
  esac
done

case "$report_type" in
  index|stats|cross-repo|per-repo|timeseries) ;;
  *) die "Unsupported report type: $report_type" ;;
esac

case "$format" in
  md|json) ;;
  *) die "Unsupported format: $format" ;;
esac

case "$group_by" in
  ''|impact|alias|tag) ;;
  *) die "Unsupported group-by value: $group_by" ;;
esac

if [ -n "$group_by" ] && [ "$report_type" != "timeseries" ]; then
  die "--group-by is only supported with --report-type timeseries"
fi

if ! command -v jq >/dev/null 2>&1; then
  die "jq is required for generate-report.sh"
fi

resolved_events_file_count=0
if [ -n "$scan_dirs" ]; then
  set --
  while IFS= read -r dir; do
    [ -n "$dir" ] || continue
    set -- "$@" "$dir"
  done <<EOF
$scan_dirs
EOF
  [ "$#" -gt 0 ] || die "--scan-dirs requires at least one directory"
  discovered=$(discover_events_files "$@" || true)
  if [ -z "$discovered" ]; then
    die "No events.jsonl files found under the provided scan dirs"
  fi
  events_files=$discovered
else
  if [ -z "$events_file" ]; then
    events_file=$(default_events_file)
  fi
  [ -f "$events_file" ] || die "Events file not found: $events_file"
  events_files=$events_file
fi

set --
while IFS= read -r file; do
  [ -n "$file" ] || continue
  set -- "$@" "$file"
  resolved_events_file_count=$((resolved_events_file_count + 1))
done <<EOF
$events_files
EOF
[ "$resolved_events_file_count" -gt 0 ] || die "No events files resolved"

if [ "$report_type" = "index" ] && [ "$resolved_events_file_count" -ne 1 ]; then
  die "--report-type index requires exactly one events file"
fi
if [ "$report_type" = "stats" ] && [ "$resolved_events_file_count" -ne 1 ]; then
  die "--report-type stats requires exactly one events file"
fi

# Build query command
set -- "$SCRIPT_DIR/query-friction.sh"
if [ -n "$scan_dirs" ]; then
  set -- "$@" --scan-dirs
  while IFS= read -r dir; do
    [ -n "$dir" ] || continue
    set -- "$@" "$dir"
  done <<EOF
$scan_dirs
EOF
else
  set -- "$@" --events-file "$events_file"
fi

[ -n "$impact" ] && set -- "$@" --impact "$impact"
[ -n "$fingerprint" ] && set -- "$@" --fingerprint "$fingerprint"
[ -n "$tag" ] && set -- "$@" --tag "$tag"
[ -n "$tag_exact" ] && set -- "$@" --tag-exact "$tag_exact"
[ -n "$alias_filter" ] && set -- "$@" --alias "$alias_filter"
[ -n "$alias_exact" ] && set -- "$@" --alias-exact "$alias_exact"
[ -n "$text" ] && set -- "$@" --text "$text"
[ -n "$date_exact" ] && set -- "$@" --date "$date_exact"
[ -n "$date_from" ] && set -- "$@" --date-from "$date_from"
[ -n "$date_to" ] && set -- "$@" --date-to "$date_to"
[ -n "$after" ] && set -- "$@" --after "$after"
[ -n "$source_ref" ] && set -- "$@" --source-ref "$source_ref"
set -- "$@" --format json

filtered_tmp=$(mktemp)
report_tmp=$(mktemp)
cleanup() {
  rm -f "$filtered_tmp" "$report_tmp"
}
trap cleanup EXIT HUP INT TERM

sh "$@" >"$filtered_tmp"

generated=$(date -u '+%Y-%m-%d %H:%M:%S UTC')

case "$report_type" in
  index)
    # Synthesis dashboard: bounded sections regardless of corpus size. The
    # full manifest lives in events.jsonl and is reachable via query-friction.
    jq --arg generated "$generated" '
      def count_rows(stream):
        [stream | select(. != null and . != "")]
        | group_by(.)
        | map({value: .[0], count: length})
        | sort_by([-.count, .value]);
      def record_kind: (.kind // "friction");
      def record_key: (.recurrence_key // .fingerprint // "");
      def short_title: ((.title // .actual_outcome // .action // "") | gsub("\\s+"; " ") | .[0:60]);

      . as $events
      | ($events | sort_by(.recorded_at // "", .event_id // "")) as $sorted
      | ($sorted | map(select(record_kind == "resolution"))) as $resolutions
      | ($resolutions | map(.resolves // []) | flatten | unique) as $resolved_ids
      | ($sorted | map(select(record_kind == "friction"))) as $frictions
      | ($sorted | map(select(record_kind == "recurrence"))) as $recurrences
      | ($frictions | map(select((.event_id // "") as $i | ($resolved_ids | index($i)) == null))) as $open_frictions
      | {
          report_type: "index",
          index_rebuilt: $generated,
          repo_root: ($sorted[-1].repo_root // ""),
          events_file: ($sorted[-1].events_file // ""),
          earliest_event: ($sorted[0].recorded_at // ""),
          latest_event: ($sorted[-1].recorded_at // ""),
          totals: {
            records: ($sorted | length),
            friction: ($frictions | length),
            recurrence: ($recurrences | length),
            resolution: ($resolutions | length),
            open: ($open_frictions | length),
            resolved: (($frictions | length) - ($open_frictions | length)),
            blocked_open: ($open_frictions | map(select((.impact // "") == "blocked")) | length)
          },
          open_clusters: (
            $frictions
            | group_by(record_key)
            | map(select((.[0] | record_key) != ""))
            | map(
                . as $group
                | ($group | map(.event_id // "")) as $anchor_ids
                | ($recurrences | map(select((.recurs // "") as $a | ($anchor_ids | index($a)) != null))) as $recs
                | ($group + $recs) as $sightings
                | {
                    key: ($group[0] | record_key),
                    sightings: ($sightings | length),
                    anchor: ($group | last | .event_id // ""),
                    title: ($group | last | short_title),
                    last_seen: (($sightings | map(.recorded_at // "") | max // "")[0:10]),
                    open: ([$group[] | select((.event_id // "") as $i | ($resolved_ids | index($i)) == null)] | length > 0),
                    impact_mix: ($sightings | count_rows(.[] | .impact // empty) | map("\(.value) x\(.count)") | join(", "))
                  }
              )
            | map(select(.open))
            | sort_by([-.sightings, .last_seen])
            | .[:15]
          ),
          recent: (
            $sorted
            | .[-10:]
            | map({
                event_id: (.event_id // ""),
                kind: record_kind,
                date: ((.recorded_at // "")[0:10]),
                title: short_title,
                impact: (.impact // "")
              })
            | reverse
          ),
          source_refs: (count_rows($frictions[] | (.sources // [])[]? | .ref // empty) | .[:8]),
          source_kinds: (count_rows($frictions[] | (.sources // [])[]? | (.kind // .type) // empty)),
          resolutions: (
            $resolutions
            | .[-10:]
            | map({
                event_id: (.event_id // ""),
                resolves: ((.resolves // []) | join(", ")),
                action: ((.action // "") | gsub("\\s+"; " ") | .[0:60])
              })
            | reverse
          ),
          date_counts: ([count_rows($sorted[] | (.recorded_at // "")[0:10])[]] | sort_by(.value) | .[-14:])
        }
    ' "$filtered_tmp" >"$report_tmp"
    ;;
  stats)
    # Health metrics: noise volume, recurrence adoption, dedup integrity, and
    # opening-trigram concentration (the convergence measure; hindsight_v4 is
    # the legacy baseline the v5 fields are compared against).
    jq --arg generated "$generated" '
      def count_rows(stream):
        [stream | select(. != null and . != "")]
        | group_by(.)
        | map({value: .[0], count: length})
        | sort_by([-.count, .value]);
      def record_kind: (.kind // "friction");
      def record_key: (.recurrence_key // .fingerprint // "");
      def pct($count; $total):
        if $total <= 0 then "0%"
        else ((($count * 10000 / $total) | floor) / 100 | tostring) + "%"
        end;
      def percentile($p):
        sort | if length == 0 then 0 else .[([((length * $p / 100) | floor), length - 1] | min)] end;
      def trigram: ascii_downcase | [scan("[a-z]+")] | .[0:3] | join(" ");
      def trigram_stats(stream):
        [stream | select(. != null and . != "") | trigram | select(. != "")] as $tris
        | ($tris | length) as $n
        | (count_rows($tris[]) | .[:5]) as $top
        | {
            samples: $n,
            distinct_openers: ($tris | unique | length),
            top5_share: (if $n == 0 then "0%" else pct(($top | map(.count) | add // 0); $n) end),
            top_openers: ($top | map({opener: .value, count: .count}))
          };

      . as $records
      | ($records | sort_by(.recorded_at // "", .event_id // "")) as $sorted
      | ($sorted | map(select(record_kind == "resolution"))) as $resolutions
      | ($resolutions | map(.resolves // []) | flatten | unique) as $resolved_ids
      | ($sorted | map(select(record_kind == "friction"))) as $frictions
      | ($sorted | map(select(record_kind == "recurrence"))) as $recurrences
      | ($frictions | map(select((.event_id // "") as $i | ($resolved_ids | index($i)) == null))) as $open_frictions
      | (($sorted[-1].recorded_at // "")[0:10]) as $window_end
      | (if $window_end == "" then ""
         else ($window_end | strptime("%Y-%m-%d") | mktime - 13 * 86400 | strftime("%Y-%m-%d"))
         end) as $window_start
      | ($sorted | map(select($window_start != "" and ((.recorded_at // "")[0:10]) >= $window_start))) as $window_records
      | ([$frictions[] | (.sources // [])[]?] | length) as $source_entries
      | ([$frictions[] | (.sources // [])[]? | select(((.kind // .type) // "") == "other")] | length) as $other_sources
      | {
          report_type: "stats",
          index_rebuilt: $generated,
          events_file: ($sorted[-1].events_file // ""),
          totals: {
            records: ($sorted | length),
            friction: ($frictions | length),
            recurrence: ($recurrences | length),
            resolution: ($resolutions | length),
            open: ($open_frictions | length),
            resolved: (($frictions | length) - ($open_frictions | length))
          },
          impact: count_rows(($frictions + $recurrences)[] | .impact // empty),
          window_14d: {
            start: $window_start,
            end: $window_end,
            records: ($window_records | length),
            per_day: ((($window_records | length) * 10 / 14) | floor / 10)
          },
          recurrence_share: pct(($recurrences | length); (($frictions | length) + ($recurrences | length))),
          key_collisions: (
            $frictions
            | group_by(record_key)
            | map(select((.[0] | record_key) != "" and length > 1))
            | {
                keys: length,
                examples: (sort_by(-length) | .[:5] | map({key: (.[0] | record_key), events: length}))
              }
          ),
          top_keys: (
            $frictions
            | group_by(record_key)
            | map(select((.[0] | record_key) != ""))
            | map(
                . as $g
                | ($g | map(.event_id // "")) as $ids
                | {
                    key: ($g[0] | record_key),
                    sightings: (($g | length) + ($recurrences | map(select((.recurs // "") as $a | ($ids | index($a)) != null)) | length)),
                    open: ([$g[] | select((.event_id // "") as $i | ($resolved_ids | index($i)) == null)] | length > 0)
                  }
              )
            | sort_by(-.sightings)
            | .[:10]
          ),
          field_lengths: {
            reading: ([$sorted[] | .reading // empty | length] | {median: percentile(50), p95: percentile(95)}),
            decision: ([$sorted[] | .decision // empty | length] | {median: percentile(50), p95: percentile(95)}),
            pivot_information: ([$sorted[] | .pivot_information // empty | length] | {median: percentile(50), p95: percentile(95)})
          },
          convergence: {
            reading: trigram_stats($sorted[] | .reading),
            decision: trigram_stats($sorted[] | .decision),
            pivot_information: trigram_stats($sorted[] | .pivot_information),
            hindsight_v4: trigram_stats($sorted[] | .hindsight)
          },
          source_kinds: count_rows($frictions[] | (.sources // [])[]? | (.kind // .type) // empty),
          other_kind_share: pct($other_sources; $source_entries)
        }
    ' "$filtered_tmp" >"$report_tmp"
    ;;
  cross-repo)
    jq --arg generated "$generated" '
      def pct($count; $total):
        if $total <= 0 then "0%"
        else (((($count * 100) / $total) + 0.5) | floor | tostring) + "%"
        end;
      def count_rows(stream):
        [stream | select(. != null and . != "")]
        | group_by(.)
        | map({value: .[0], count: length})
        | sort_by([-.count, .value]);
      def count_rows_pct(stream; $total):
        count_rows(stream) | map(. + {percent: pct(.count; $total)});

      . as $events
      | ($events | sort_by(.recorded_at // "", .event_id // "")) as $sorted
      | ($sorted | length) as $total
      | {
          report_type: "cross-repo",
          index_rebuilt: $generated,
          repos_scanned: ([ $sorted[] | .events_file // empty ] | unique | length),
          total_entries: $total,
          repos: (
            [ $sorted[]
              | {repo_root: (.repo_root // ""), events_file: (.events_file // "")}
            ]
            | group_by(.events_file)
            | map({
                repo_root: .[0].repo_root,
                events_file: .[0].events_file,
                entries: length
              })
            | sort_by([-.entries, .repo_root, .events_file])
          ),
          impact_summary: count_rows($sorted[] | .impact // empty),
          alias_counts: count_rows_pct($sorted[] | (.aliases // [])[]? // empty; $total),
          tag_counts: count_rows_pct($sorted[] | (.tags // [])[]? // empty; $total),
          key_counts: (count_rows($sorted[] | (.recurrence_key // .fingerprint) // empty) | .[:10])
        }
    ' "$filtered_tmp" >"$report_tmp"
    ;;
  per-repo)
    jq --arg generated "$generated" '
      def pct($count; $total):
        if $total <= 0 then "0%"
        else (((($count * 100) / $total) + 0.5) | floor | tostring) + "%"
        end;
      def count_rows(stream):
        [stream | select(. != null and . != "")]
        | group_by(.)
        | map({value: .[0], count: length})
        | sort_by([-.count, .value]);
      def count_rows_pct(stream; $total):
        count_rows(stream) | map(. + {percent: pct(.count; $total)});

      . as $events
      | ($events | sort_by(.recorded_at // "", .event_id // "")) as $sorted
      | {
          report_type: "per-repo",
          index_rebuilt: $generated,
          repos: ([ $sorted[] | .events_file // empty ] | unique | length),
          total_entries: ($sorted | length),
          repo_summaries: (
            [ $sorted[] ]
            | group_by(.events_file // "")
            | map(
                . as $repo_events
                | ($repo_events | sort_by(.recorded_at // "", .event_id // "")) as $repo_sorted
                | ($repo_sorted | length) as $total
                | {
                    repo_root: ($repo_sorted[-1].repo_root // ""),
                    events_file: ($repo_sorted[-1].events_file // ""),
                    entries: $total,
                    earliest_event: ($repo_sorted[0].recorded_at // ""),
                    latest_event: ($repo_sorted[-1].recorded_at // ""),
                    impact_summary: count_rows($repo_sorted[] | .impact // empty),
                    alias_counts: count_rows_pct($repo_sorted[] | (.aliases // [])[]? // empty; $total),
                    tag_counts: count_rows_pct($repo_sorted[] | (.tags // [])[]? // empty; $total),
                    key_counts: (count_rows($repo_sorted[] | (.recurrence_key // .fingerprint) // empty) | .[:10])
                  }
              )
            | sort_by([-.entries, .repo_root, .events_file])
          )
        }
    ' "$filtered_tmp" >"$report_tmp"
    ;;
  timeseries)
    jq --arg generated "$generated" --arg group_by "$group_by" '
      def group_values($group):
        if $group == "" then ["count"]
        elif $group == "impact" then [(.impact // "")]
        elif $group == "alias" then (.aliases // [])
        elif $group == "tag" then (.tags // [])
        else []
        end
        | map(select(. != null and . != ""));

      . as $events
      | [ $events[] | select((.recorded_at // "") | length >= 10) | . + {event_date: (.recorded_at[0:10])} ] as $dated
      | if $group_by == "" then
          {
            report_type: "timeseries",
            index_rebuilt: $generated,
            group_by: "",
            columns: ["count"],
            rows: (
              [ $dated[] | .event_date ]
              | group_by(.)
              | map({date: .[0], count: length})
              | sort_by(.date)
            )
          }
        else
          (
            [ $dated[] | group_values($group_by)[] ] | unique | sort
          ) as $columns
          | {
              report_type: "timeseries",
              index_rebuilt: $generated,
              group_by: $group_by,
              columns: $columns,
              rows: (
                [ $dated[]
                  | . as $event
                  | group_values($group_by)[]
                  | {date: $event.event_date, key: ., value: 1}
                ]
                | group_by(.date)
                | map(
                    . as $date_rows
                    | {date: .[0].date}
                    + (
                        reduce $columns[] as $column
                          ({};
                           . + {
                             ($column):
                               (
                                 [$date_rows[] | select(.key == $column)]
                                 | length
                               )
                           })
                      )
                  )
                | sort_by(.date)
              )
            }
        end
    ' "$filtered_tmp" >"$report_tmp"
    ;;
esac

case "$format" in
  json)
    result=$(cat "$report_tmp")
    ;;
  md)
    case "$report_type" in
      index)
        result=$(jq -r '
          def md_table_row($cells): "| " + ($cells | join(" | ")) + " |";
          def md_table($headers; $rows; $empty_msg):
            if ($rows | length) == 0 then $empty_msg
            else
              md_table_row($headers)
              + "\n| " + ([$headers[] | gsub("."; "-")] | join(" | ")) + " |"
              + "\n" + ([$rows[] | md_table_row(.)] | join("\n"))
            end;

          "# Friction Dashboard\n\n"
          + "**Rebuilt:** \(.index_rebuilt) | **Span:** \((.earliest_event // "")[0:10]) to \((.latest_event // "")[0:10])\n"
          + "**Records:** \(.totals.records) (\(.totals.friction) friction, \(.totals.recurrence) recurrences, \(.totals.resolution) resolutions)\n"
          + "**Open:** \(.totals.open) | **Resolved:** \(.totals.resolved) | **Blocked open:** \(.totals.blocked_open)\n"
          + "\n## Open Clusters (top \(.open_clusters | length))\n\n"
          + md_table(["Key", "Sightings", "Anchor", "Title", "Last seen", "Impact"];
              [.open_clusters[] | [
                .key, (.sightings | tostring), .anchor, .title, .last_seen, .impact_mix
              ]];
              "_No open clusters._")
          + "\n\n## Recent Records (last \(.recent | length))\n\n"
          + md_table(["ID", "Kind", "Date", "Title", "Impact"];
              [.recent[] | [.event_id, .kind, .date, .title, .impact]];
              "_No records._")
          + "\n\n## Top Sources\n\n"
          + md_table(["Ref", "Records"];
              [.source_refs[] | [.value, (.count | tostring)]];
              "_No sources recorded._")
          + (if (.source_kinds | length) > 0 then
              "\n\n**Source kinds:** " + ([.source_kinds[] | "\(.value) x\(.count)"] | join(", "))
            else "" end)
          + "\n\n## Resolutions (last \(.resolutions | length))\n\n"
          + md_table(["ID", "Resolves", "Action"];
              [.resolutions[] | [.event_id, .resolves, .action]];
              "_No resolutions yet._")
          + "\n\n## Date Distribution (last \(.date_counts | length) active days)\n\n"
          + md_table(["Date", "Count"];
              [.date_counts[] | [.value, (.count | tostring)]];
              "_No date counts available._")
        ' "$report_tmp")
        ;;
      stats)
        result=$(jq -r '
          def md_table_row($cells): "| " + ($cells | join(" | ")) + " |";
          def md_table($headers; $rows; $empty_msg):
            if ($rows | length) == 0 then $empty_msg
            else
              md_table_row($headers)
              + "\n| " + ([$headers[] | gsub("."; "-")] | join(" | ")) + " |"
              + "\n" + ([$rows[] | md_table_row(.)] | join("\n"))
            end;

          "# Friction Stats\n\n"
          + "**Generated:** \(.index_rebuilt)\n"
          + "**Records:** \(.totals.records) (\(.totals.friction) friction, \(.totals.recurrence) recurrences, \(.totals.resolution) resolutions) | **Open:** \(.totals.open) | **Resolved:** \(.totals.resolved)\n"
          + "\n## Volume\n\n"
          + "- Window \(.window_14d.start) to \(.window_14d.end): \(.window_14d.records) records (\(.window_14d.per_day)/day)\n"
          + "- Recurrence share (cheap repeats vs full events): \(.recurrence_share)\n"
          + "- Key collisions (distinct friction events sharing one key; target 0): \(.key_collisions.keys)"
          + (if (.key_collisions.examples | length) > 0 then
              " — " + ([.key_collisions.examples[] | "\(.key) x\(.events)"] | join(", "))
            else "" end)
          + "\n\n## Impact\n\n"
          + md_table(["Impact", "Count"];
              [.impact[] | [.value, (.count | tostring)]];
              "_No events._")
          + "\n\n## Top Keys\n\n"
          + md_table(["Key", "Sightings", "Open"];
              [.top_keys[] | [.key, (.sightings | tostring), (if .open then "yes" else "no" end)]];
              "_No keys._")
          + "\n\n## Field Lengths (chars)\n\n"
          + md_table(["Field", "Median", "P95"];
              [["reading", (.field_lengths.reading.median | tostring), (.field_lengths.reading.p95 | tostring)],
               ["decision", (.field_lengths.decision.median | tostring), (.field_lengths.decision.p95 | tostring)],
               ["pivot_information", (.field_lengths.pivot_information.median | tostring), (.field_lengths.pivot_information.p95 | tostring)]];
              "_No data._")
          + "\n\n## Convergence (top-5 opening-trigram share; lower is healthier)\n\n"
          + md_table(["Field", "Samples", "Distinct openers", "Top-5 share", "Most common opener"];
              [(.convergence | to_entries[]) | [
                .key,
                (.value.samples | tostring),
                (.value.distinct_openers | tostring),
                .value.top5_share,
                ((.value.top_openers[0].opener // "") + (if (.value.top_openers[0].count // 0) > 0 then " x\(.value.top_openers[0].count)" else "" end))
              ]];
              "_No narrative fields._")
          + "\n\n_hindsight_v4 is the legacy baseline; compare pivot_information against it._\n"
          + "_Read top-5 share together with distinct openers: high share with many distinct openers is benign form convergence (the eliciting question orders narratives); high share with few distinct openers is template capture — the v4 disease was semantic monoculture, not opener form._\n"
          + "\n## Source Kinds\n\n"
          + (if (.source_kinds | length) > 0 then
              ([.source_kinds[] | "\(.value) x\(.count)"] | join(", "))
              + " | other share: \(.other_kind_share) (high other = ontology strain)"
            else "_No sources._" end)
        ' "$report_tmp")
        ;;
      cross-repo)
        result=$(jq -r '
          def md_table_row($cells): "| " + ($cells | join(" | ")) + " |";
          def md_table($headers; $rows; $empty_msg):
            if ($rows | length) == 0 then $empty_msg
            else
              md_table_row($headers)
              + "\n| " + ([$headers[] | gsub("."; "-")] | join(" | ")) + " |"
              + "\n" + ([$rows[] | md_table_row(.)] | join("\n"))
            end;
          "# Cross-Repo Friction Index\n\n"
          + "**Index rebuilt:** \(.index_rebuilt)\n"
          + "**Repos scanned:** \(.repos_scanned)\n"
          + "**Total entries:** \(.total_entries)\n\n"
          + "## Repos\n\n"
          + (if (.repos | length) == 0 then "_No repos matched._"
             else ([.repos[] | "- `\((if (.repo_root // "") != "" then .repo_root else .events_file end))` — \(.entries) events"] | join("\n")) end)
          + "\n\n## Impact Summary\n\n"
          + md_table(["Impact", "Count"];
              [.impact_summary[] | [.value, (.count | tostring)]];
              "_No events._")
          + "\n\n## Aliases\n\n"
          + md_table(["Alias", "Count", "%"];
              [.alias_counts[] | [.value, (.count | tostring), .percent]];
              "_No aliases recorded._")
          + "\n\n## Tags\n\n"
          + md_table(["Tag", "Count", "%"];
              [.tag_counts[] | [.value, (.count | tostring), .percent]];
              "_No tags recorded._")
          + "\n\n## Top Keys\n\n"
          + md_table(["Key", "Count"];
              [.key_counts[] | [.value, (.count | tostring)]];
              "_No keys._")
        ' "$report_tmp")
        ;;
      per-repo)
        result=$(jq -r '
          def md_table_row($cells): "| " + ($cells | join(" | ")) + " |";
          def md_table($headers; $rows; $empty_msg):
            if ($rows | length) == 0 then $empty_msg
            else
              md_table_row($headers)
              + "\n| " + ([$headers[] | gsub("."; "-")] | join(" | ")) + " |"
              + "\n" + ([$rows[] | md_table_row(.)] | join("\n"))
            end;
          "# Per-Repo Friction Report\n\n"
          + "**Index rebuilt:** \(.index_rebuilt)\n"
          + "**Repos:** \(.repos) | **Total entries:** \(.total_entries)\n"
          + (if (.repo_summaries | length) == 0 then "\n_No repos matched._"
             else (
               .repo_summaries
               | map(
                   "\n---\n\n## \((if (.repo_root // "") != "" then .repo_root else .events_file end))\n"
                   + "**Entries:** \(.entries) | **Earliest:** \((.earliest_event // "")[0:10]) | **Latest:** \((.latest_event // "")[0:10])\n\n"
                   + "### Impact\n\n"
                   + md_table(["Impact", "Count"];
                       [.impact_summary[] | [.value, (.count | tostring)]];
                       "_No events._")
                   + "\n\n### Aliases\n\n"
                   + md_table(["Alias", "Count", "%"];
                       [.alias_counts[] | [.value, (.count | tostring), .percent]];
                       "_No aliases._")
                   + "\n\n### Tags\n\n"
                   + md_table(["Tag", "Count", "%"];
                       [.tag_counts[] | [.value, (.count | tostring), .percent]];
                       "_No tags._")
                 )
               | join("")
             )
            end)
        ' "$report_tmp")
        ;;
      timeseries)
        if [ -n "$group_by" ]; then
          result=$(jq -r '
            . as $report
            | if (.rows | length) == 0 then
                "# Friction Time Series (by \($report.group_by))\n\n_No dated events matched._"
              else
                (["Date"] + $report.columns) as $headers
                | (
                    [
                      "# Friction Time Series (by \($report.group_by))",
                      "",
                      "| " + ($headers | join(" | ")) + " |",
                      "|" + ($headers | map("-" * (length + 2)) | join("|")) + "|"
                    ]
                    + (
                        $report.rows
                        | map(
                            . as $row
                            | ([$row.date] + ($report.columns | map(($row[.] // 0) | tostring))) as $cells
                            | "| " + ($cells | join(" | ")) + " |"
                          )
                      )
                  )
                | join("\n")
              end
          ' "$report_tmp")
        else
          result=$(jq -r '
            if (.rows | length) == 0 then
              "# Friction Time Series\n\n_No dated events matched._"
            else
              (
                [
                  "# Friction Time Series",
                  "",
                  "| Date | Count |",
                  "|------|-------|"
                ]
                + (.rows | map("| \(.date) | \(.count) |"))
              )
              | join("\n")
            end
          ' "$report_tmp")
        fi
        ;;
    esac
    ;;
esac

if [ -n "$output_path" ]; then
  printf '%s\n' "$result" >"$output_path"
else
  printf '%s\n' "$result"
fi
