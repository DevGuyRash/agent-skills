#!/usr/bin/env sh

set -eu

FORMAT=text

usage() {
    cat <<'EOF'
Usage: instruction_shape.sh <skill-directory> [--format json]

Report observations about the instruction design of SKILL.md:
  - SKILL.md line count
  - second-person address and third-person binds
  - modal case consistency
  - repeated branch outcomes
  - recognized instruction-function headings, without requiring headings or order
  - done-condition presence
  - the document naming its own notation

This reports; it does not judge. Whether an observation is a defect depends on
the target's profile and the maker's intent, which this script cannot see. Exit
status reflects only whether the report could be produced: 0 reported, 2 the
arguments or the target were unusable.

Scope: SKILL.md only. Reference files are read by the auditor; a reference whose
purpose is quoting a standard would trip the notation observation for doing its
job.
EOF
}

json_escape() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

fail_usage() {
    echo "error: $1" >&2
    [ -z "${2-}" ] || echo "hint: $2" >&2
    exit 2
}

# Body only: everything after the closing frontmatter delimiter.
extract_body() {
    awk '
        NR == 1 && $0 == "---" { in_fm = 1; next }
        in_fm && $0 == "---" { in_fm = 0; next }
        !in_fm { print }
    ' "$1"
}

# Join soft-wrapped prose so a clause spanning a line break matches as one unit.
# Documents here wrap near 100 columns; a line-oriented match would truncate any
# clause at the wrap point and report unrelated clauses as identical.
unwrap_prose() {
    awk '
        /^[[:space:]]*$/ || /^[|#>-]/ || /^[0-9]+\./ || /^[[:space:]]/ {
            if (buf != "") { print buf; buf = "" }
            print $0
            next
        }
        { if (buf == "") buf = $0; else buf = buf " " $0 }
        END { if (buf != "") print buf }
    ' "$1"
}

count_matches() {
    grep -oE "$1" "$2" 2>/dev/null | wc -l | tr -d ' '
}

print_text() {
    echo "REPORT instruction_shape"
    echo "skill_md_lines=$SKILL_MD_LINES"
    echo "second_person_refs=$YOU_COUNT"
    echo "third_person_binds=$THIRD_PERSON"
    echo "modal_case=$MODAL_CASE"
    echo "duplicate_branch_outcomes=$DUP_THEN"
    echo "function_headings_present=$FUNCTION_HEADINGS_PRESENT"
    echo "done_condition=$DONE_CONDITION"
    echo "notation_self_reference=$NOTATION_REF"
    echo "heading_count=$HEADING_COUNT"
    if [ -n "$HEADINGS" ]; then
        printf '%s\n' "$HEADINGS" | sed 's/^/heading: /'
    fi
    exit 0
}

print_json() {
    printf '{'
    printf '"script":"instruction_shape",'
    printf '"skill_dir":"%s",' "$(json_escape "$SKILL_DIR")"
    printf '"skill_md_lines":%s,' "$SKILL_MD_LINES"
    printf '"second_person_refs":%s,' "$YOU_COUNT"
    printf '"third_person_binds":%s,' "$THIRD_PERSON"
    printf '"modal_case":"%s",' "$MODAL_CASE"
    printf '"duplicate_branch_outcomes":%s,' "$DUP_THEN"
    printf '"function_headings_present":"%s",' "$(json_escape "$FUNCTION_HEADINGS_PRESENT")"
    printf '"done_condition":"%s",' "$DONE_CONDITION"
    printf '"notation_self_reference":"%s",' "$NOTATION_REF"
    printf '"heading_count":%s,' "$HEADING_COUNT"
    printf '"headings":[%s]' "$HEADING_JSON"
    printf '}\n'
    exit 0
}

HEADING_JSON=""
HEADINGS=""
HEADING_COUNT=0
SKILL_MD_LINES=0
YOU_COUNT=0
THIRD_PERSON=0
MODAL_CASE=consistent
DUP_THEN=0
FUNCTION_HEADINGS_PRESENT=""
DONE_CONDITION=no
NOTATION_REF=no
SKILL_DIR=""

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        --format) FORMAT="${2-}"; shift 2 ;;
        --format=*) FORMAT=${1#*=}; shift ;;
        -*) fail_usage "unknown flag: $1" ;;
        *)
            [ -z "$SKILL_DIR" ] || fail_usage "only one skill directory may be provided"
            SKILL_DIR="$1"; shift ;;
    esac
done

[ -n "$SKILL_DIR" ] || { usage >&2; exit 2; }

case "$FORMAT" in
    text|json) ;;
    *) fail_usage "unsupported format: $FORMAT" "use text or json" ;;
esac

[ -d "$SKILL_DIR" ] || fail_usage "skill directory not found: $SKILL_DIR"

SKILL_FILE="$SKILL_DIR/SKILL.md"
[ -f "$SKILL_FILE" ] || fail_usage "SKILL.md not found in $SKILL_DIR"

BODY_FILE="${TMPDIR:-/tmp}/instruction_shape.$$"
FLAT_FILE="${TMPDIR:-/tmp}/instruction_shape_flat.$$"
trap 'rm -f "$BODY_FILE" "$FLAT_FILE"' EXIT INT TERM
extract_body "$SKILL_FILE" >"$BODY_FILE"
unwrap_prose "$BODY_FILE" >"$FLAT_FILE"

SKILL_MD_LINES=$(wc -l < "$SKILL_FILE" | tr -d ' ')

YOU_COUNT=$(count_matches '\byou\b|\byour\b|\bYou\b|\bYour\b' "$BODY_FILE")
THIRD_PERSON=$(count_matches '[Tt]he executor (SHALL|shall|MAY|may|SHOULD|should)' "$BODY_FILE")

UPPER_SHALL=$(count_matches '\bSHALL\b' "$BODY_FILE")
LOWER_SHALL=$(count_matches '(^|[^A-Za-z])shall([^A-Za-z]|$)' "$BODY_FILE")
if [ "$UPPER_SHALL" -gt 0 ] && [ "$LOWER_SHALL" -gt 0 ]; then
    MODAL_CASE=mixed
fi

DUP_THEN=$(grep -oE 'THEN you SHALL [^.]*' "$FLAT_FILE" 2>/dev/null | sort | uniq -d | wc -l | tr -d ' ')

if grep -qiE '\bEARS\b|this notation|governing architecture|these instructions follow' "$BODY_FILE" 2>/dev/null; then
    NOTATION_REF=yes
fi

if grep -qiE 'done when|you are done|is complete when' "$BODY_FILE" 2>/dev/null; then
    DONE_CONDITION=yes
fi

HEADINGS=$(grep -E '^#{2,} +' "$BODY_FILE" 2>/dev/null | sed -e 's/^#* *//' || true)
if [ -n "$HEADINGS" ]; then
    HEADING_COUNT=$(printf '%s\n' "$HEADINGS" | sed '/^$/d' | wc -l | tr -d ' ')
    first=1
    while IFS= read -r heading; do
        [ -n "$heading" ] || continue
        [ "$first" -eq 1 ] || HEADING_JSON="$HEADING_JSON,"
        HEADING_JSON="$HEADING_JSON\"$(json_escape "$heading")\""
        first=0
    done <<EOF
$HEADINGS
EOF
fi

while IFS='|' read -r label pattern; do
    if grep -qiE "^#{2,} +.*$pattern" "$BODY_FILE" 2>/dev/null; then
        if [ -n "$FUNCTION_HEADINGS_PRESENT" ]; then
            FUNCTION_HEADINGS_PRESENT="$FUNCTION_HEADINGS_PRESENT,$label"
        else
            FUNCTION_HEADINGS_PRESENT="$label"
        fi
    fi
done <<'EOF'
Mission|Mission
Environment|Environment
State|State
Boundaries|Boundaries
Loop|Loop
Verification|Verification
Precedence|Precedence
Output Contract|Output([[:space:]]+Contract)?
Binding Language|Binding([[:space:]]+Language)?
EOF
[ -n "$FUNCTION_HEADINGS_PRESENT" ] || FUNCTION_HEADINGS_PRESENT="none"

case "$FORMAT" in
    json) print_json ;;
    text) print_text ;;
esac
