#!/usr/bin/env sh

set -eu

FORMAT=text

usage() {
    cat <<'EOF'
Usage: reference_check.sh <skill-directory> [--format json]

Report what is true of a skill's references, in two kinds.

Errors are broken for every target: a link pointing at a file that does not
exist. There is no skill for which that is fine, so it fails.

Observations are reference-graph facts whose significance depends on the target
— an unlinked file or a reference that points to another reference. They never
fail.

Exit: 0 no errors, 1 errors found, 2 the arguments or the target were unusable.
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

# An error is a fact with no legitimate reading: broken for every target, on
# every host, at any age. Only these may fail.
error() {
    code="$1"
    subject="$2"
    fact="$3"

    if [ "$ERR_COUNT" -gt 0 ]; then
        ERR_JSON="$ERR_JSON,"
    fi
    ERR_JSON="$ERR_JSON{\"code\":\"$(json_escape "$code")\",\"subject\":\"$(json_escape "$subject")\",\"fact\":\"$(json_escape "$fact")\"}"
    ERR_COUNT=$((ERR_COUNT + 1))

    TEXT_ERRORS="$TEXT_ERRORS
ERROR $code: $subject
  $fact"
}

# An observation is a fact plus, where one exists, the documented rule it bears
# on. It carries no severity: ranking these is the reader's judgment, and a
# script that ranked them would be deciding for a target it cannot see.
observe() {
    code="$1"
    subject="$2"
    fact="$3"
    source_ref="${4-}"

    if [ "$OBS_COUNT" -gt 0 ]; then
        OBS_JSON="$OBS_JSON,"
    fi
    OBS_JSON="$OBS_JSON{\"code\":\"$(json_escape "$code")\",\"subject\":\"$(json_escape "$subject")\",\"fact\":\"$(json_escape "$fact")\""
    if [ -n "$source_ref" ]; then
        OBS_JSON="$OBS_JSON,\"source\":\"$(json_escape "$source_ref")\""
    fi
    OBS_JSON="$OBS_JSON}"
    OBS_COUNT=$((OBS_COUNT + 1))

    TEXT_OBS="$TEXT_OBS
$code: $subject
  $fact"
    if [ -n "$source_ref" ]; then
        TEXT_OBS="$TEXT_OBS
  source: $source_ref"
    fi
}


normalize_link() {
    case "$1" in
        '<skills-file-root>'/*) printf '%s\n' "${1#<skills-file-root>/}" ;;
        *) printf '%s\n' "$1" ;;
    esac
}

collect_skill_links() {
    grep -oE '(<skills-file-root>/)?references/[A-Za-z0-9._/-]+\.md' "$1" 2>/dev/null | sort -u || true
}

print_text() {
    echo "REPORT reference_check"
    echo "skill_dir=$SKILL_DIR"
    echo "linked_references=$LINKED_COUNT"
    echo "active_references=$ACTIVE_COUNT"
    echo "errors=$ERR_COUNT"
    echo "observations=$OBS_COUNT"
    [ "$ERR_COUNT" -eq 0 ] || printf '%s\n' "$TEXT_ERRORS"
    [ "$OBS_COUNT" -eq 0 ] || printf '%s\n' "$TEXT_OBS"
    [ "$ERR_COUNT" -eq 0 ] || exit 1
    exit 0
}

print_json() {
    printf '{'
    printf '"script":"reference_check",'
    printf '"skill_dir":"%s",' "$(json_escape "$SKILL_DIR")"
    printf '"linked_references":%s,' "$LINKED_COUNT"
    printf '"active_references":%s,' "$ACTIVE_COUNT"
    printf '"error_count":%s,' "$ERR_COUNT"
    printf '"errors":[%s],' "$ERR_JSON"
    printf '"observation_count":%s,' "$OBS_COUNT"
    printf '"observations":[%s]' "$OBS_JSON"
    printf '}\n'
    [ "$ERR_COUNT" -eq 0 ] || exit 1
    exit 0
}

TEXT_ERRORS=""
ERR_JSON=""
ERR_COUNT=0
TEXT_OBS=""
OBS_JSON=""
OBS_COUNT=0
LINKED_COUNT=0
ACTIVE_COUNT=0
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

# These are not findings about the target. They mean the script could not run.
[ -d "$SKILL_DIR" ] || fail_usage "skill directory not found: $SKILL_DIR"
SKILL_FILE="$SKILL_DIR/SKILL.md"
[ -f "$SKILL_FILE" ] || fail_usage "SKILL.md not found in $SKILL_DIR"

REFS_FILE="${TMPDIR:-/tmp}/refcheck_refs.$$"
LINKS_FILE="${TMPDIR:-/tmp}/refcheck_links.$$"
WORK_FILE="${TMPDIR:-/tmp}/refcheck_work.$$"
trap 'rm -f "$REFS_FILE" "$LINKS_FILE" "$WORK_FILE"' EXIT INT TERM

RAW_LINKS=$(collect_skill_links "$SKILL_FILE")
NORMALIZED_LINKS=""

if [ -n "$RAW_LINKS" ]; then
    while IFS= read -r raw_link; do
        [ -n "$raw_link" ] || continue
        rel_path=$(normalize_link "$raw_link")

        case "$raw_link" in
            '<skills-file-root>'/*)
                observe "nonportable_reference_prefix" "$raw_link" \
                    "the path uses a host placeholder instead of a skill-root-relative resource path" \
                    "open-standard"
                ;;
        esac

        if [ -n "$NORMALIZED_LINKS" ]; then
            NORMALIZED_LINKS="$NORMALIZED_LINKS
$rel_path"
        else
            NORMALIZED_LINKS="$rel_path"
        fi

        if [ ! -f "$SKILL_DIR/$rel_path" ]; then
            error "missing_reference_file" "$rel_path" \
                "SKILL.md links this path; no file exists there"
        fi

    done <<EOF
$RAW_LINKS
EOF
fi

if [ -n "$NORMALIZED_LINKS" ]; then
    LINKED_COUNT=$(printf '%s\n' "$NORMALIZED_LINKS" | sed '/^$/d' | sort -u | wc -l | tr -d ' ')
fi

REFERENCE_DIR="$SKILL_DIR/references"
if [ -d "$REFERENCE_DIR" ]; then
    ACTIVE_REFS=$(find "$REFERENCE_DIR" -type f -name '*.md' | sort)
else
    ACTIVE_REFS=""
fi

if [ -n "$ACTIVE_REFS" ]; then
    ACTIVE_COUNT=$(printf '%s\n' "$ACTIVE_REFS" | sed '/^$/d' | wc -l | tr -d ' ')

    # Three facts about every reference, one pass each. Asking per reference
    # instead would fork three processes per file to do microseconds of work,
    # which is where this script's time went before.
    # Literal prefix strip, not sed: a directory name containing |, [, or *
    # would be read as a regex, which both crashes and false-positives.
    : >"$REFS_FILE"
    while IFS= read -r ref_path; do
        [ -n "$ref_path" ] || continue
        printf '%s\n' "${ref_path#"$SKILL_DIR"/}"
    done <<EOF | sort -u >"$REFS_FILE"
$ACTIVE_REFS
EOF
    printf '%s\n' "$NORMALIZED_LINKS" | sed '/^$/d' | sort -u >"$LINKS_FILE"

    comm -23 "$REFS_FILE" "$LINKS_FILE" >"$WORK_FILE"
    while IFS= read -r rel_ref; do
        [ -n "$rel_ref" ] || continue
        observe "unlinked_reference" "$rel_ref" \
            "the file exists but no path in SKILL.md points at it" \
            "SKILL.md"
    done <"$WORK_FILE"

    find "$REFERENCE_DIR" -type f -name '*.md' \
        -exec grep -lE '(<skills-file-root>/)?references/[A-Za-z0-9._/-]+\.md' {} + 2>/dev/null \
        | sort >"$WORK_FILE" || true
    while IFS= read -r ref_file; do
        [ -n "$ref_file" ] || continue
        observe "nested_reference_link" "${ref_file#"$SKILL_DIR"/}" \
            "this reference links another reference" \
            "SKILL.md"
    done <"$WORK_FILE"
fi

case "$FORMAT" in
    json) print_json ;;
    text) print_text ;;
esac
