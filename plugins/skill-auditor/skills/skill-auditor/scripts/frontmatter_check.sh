#!/usr/bin/env sh

set -eu

FORMAT=text

usage() {
    cat <<'EOF'
Usage: frontmatter_check.sh <skill-directory> [--format json]

Report what is true of SKILL.md frontmatter, in two kinds.

Errors are broken for every target: absent frontmatter, a missing name, a
missing or empty description. A skill with no description has no retrieval
surface and can never be matched, on any host.

Observations are facts whose significance depends on the target — slug shape,
title-casing, name/slug correspondence, description length against the
documented limit, and whether the description follows the house numbered
trigger-list pattern. Each carries the rule it bears on. They never fail.

Description quality is not assessed. A word count cannot tell whether a
description discriminates, so judging that is left to the reader.

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

# Broken for every target: no legitimate skill lacks these.
error() {
    if [ "$ERR_COUNT" -gt 0 ]; then ERR_JSON="$ERR_JSON,"; fi
    ERR_JSON="$ERR_JSON{\"code\":\"$(json_escape "$1")\",\"subject\":\"$(json_escape "$2")\",\"fact\":\"$(json_escape "$3")\"}"
    ERR_COUNT=$((ERR_COUNT + 1))
    TEXT_ERRORS="$TEXT_ERRORS
ERROR $1: $2
  $3"
}

# A fact whose significance depends on the target, carrying the rule it bears
# on so the reader can decide rather than obey.
observe() {
    source_ref="${4-}"
    if [ "$OBS_COUNT" -gt 0 ]; then OBS_JSON="$OBS_JSON,"; fi
    OBS_JSON="$OBS_JSON{\"code\":\"$(json_escape "$1")\",\"subject\":\"$(json_escape "$2")\",\"fact\":\"$(json_escape "$3")\""
    [ -z "$source_ref" ] || OBS_JSON="$OBS_JSON,\"source\":\"$(json_escape "$source_ref")\""
    OBS_JSON="$OBS_JSON}"
    OBS_COUNT=$((OBS_COUNT + 1))
    TEXT_OBS="$TEXT_OBS
$1: $2
  $3"
    [ -z "$source_ref" ] || TEXT_OBS="$TEXT_OBS
  source: $source_ref"
}

load_frontmatter() {
    skill_file="$1"
    first_line=$(head -1 "$skill_file" 2>/dev/null || true)
    if [ "$first_line" != "---" ]; then
        return 1
    fi

    closing_line=$(awk 'NR > 1 && $0 == "---" { print NR; exit }' "$skill_file")
    [ -n "$closing_line" ] || return 1
    sed -n "2,$((closing_line - 1))p" "$skill_file"
}

extract_description() {
    fm_block="$1"
    desc_line=$(printf '%s\n' "$fm_block" | grep -n '^description:' | head -1 || true)
    [ -n "$desc_line" ] || return 1

    desc_start=$(printf '%s' "$desc_line" | cut -d: -f1)
    desc_full_line=$(printf '%s\n' "$fm_block" | sed -n "${desc_start}p")
    desc_raw=$(printf '%s\n' "$desc_full_line" | sed 's/^description:[[:space:]]*//')
    desc_indent=$(printf '%s\n' "$desc_full_line" | awk 'match($0, /^[[:space:]]*/){ print RLENGTH }')

    case "$desc_raw" in
        ">"|">-"|">+"|"|"|"|-"|"|+")
            desc_text=$(
                printf '%s\n' "$fm_block" | tail -n +"$((desc_start + 1))" | awk -v min_indent="$((desc_indent + 1))" '
                    function line_indent(text) {
                        match(text, /^[[:space:]]*/)
                        return RLENGTH
                    }

                    {
                        if ($0 ~ /^[[:space:]]*$/) {
                            if (seen_content) {
                                printf " "
                            }
                            next
                        }

                        if (line_indent($0) < min_indent) {
                            exit
                        }

                        seen_content = 1
                        sub(/^[[:space:]]*/, "", $0)
                        printf "%s ", $0
                    }
                '
            )
            ;;
        *)
            desc_text="$desc_raw"
            ;;
    esac

    printf '%s' "$desc_text" | sed "s/^['\"]//;s/['\"]$//"
}

print_text() {
    echo "REPORT frontmatter_check"
    echo "skill_dir=$SKILL_DIR"
    echo "name=$NAME_VALUE"
    echo "description_chars=$DESC_CHARS"
    echo "errors=$ERR_COUNT"
    echo "observations=$OBS_COUNT"
    [ "$ERR_COUNT" -eq 0 ] || printf '%s\n' "$TEXT_ERRORS"
    [ "$OBS_COUNT" -eq 0 ] || printf '%s\n' "$TEXT_OBS"
    [ "$ERR_COUNT" -eq 0 ] || exit 1
    exit 0
}

print_json() {
    printf '{'
    printf '"script":"frontmatter_check",'
    printf '"skill_dir":"%s",' "$(json_escape "$SKILL_DIR")"
    printf '"name":"%s",' "$(json_escape "$NAME_VALUE")"
    printf '"description_chars":%s,' "$DESC_CHARS"
    printf '"error_count":%s,' "$ERR_COUNT"
    printf '"errors":[%s],' "$ERR_JSON"
    printf '"observation_count":%s,' "$OBS_COUNT"
    printf '"observations":[%s]' "$OBS_JSON"
    printf '}\n'
    [ "$ERR_COUNT" -eq 0 ] || exit 1
    exit 0
}

TEXT_ERRORS=""
TEXT_OBS=""
ERR_JSON=""
OBS_JSON=""
ERR_COUNT=0
OBS_COUNT=0
NAME_VALUE=""
DESC_CHARS=0
SKILL_DIR=""

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --format)
            FORMAT="${2-}"
            shift 2
            ;;
        --format=*)
            FORMAT=${1#*=}
            shift
            ;;
        -*) fail_usage "unknown flag: $1" ;;
        *)
            [ -z "$SKILL_DIR" ] || fail_usage "only one skill directory may be provided"
            SKILL_DIR="$1"
            shift
            ;;
    esac
done

[ -n "$SKILL_DIR" ] || { usage >&2; exit 2; }

case "$FORMAT" in
    text|json) ;;
    *) fail_usage "unsupported format: $FORMAT" "use text or json" ;;
esac

# Not findings about the target: the script could not run.
[ -d "$SKILL_DIR" ] || fail_usage "skill directory not found: $SKILL_DIR"

SKILL_FILE="$SKILL_DIR/SKILL.md"
[ -f "$SKILL_FILE" ] || fail_usage "SKILL.md not found in $SKILL_DIR"

if ! FRONTMATTER=$(load_frontmatter "$SKILL_FILE"); then
    error "frontmatter_missing" "SKILL.md" \
        "no readable YAML frontmatter; the skill exposes no metadata to match against"
    case "$FORMAT" in
        json) print_json ;;
        text) print_text ;;
    esac
fi

NAME_VALUE=$(printf '%s\n' "$FRONTMATTER" | sed -n 's/^name:[[:space:]]*//p' | head -1 | sed "s/^['\"]//;s/['\"]$//")
if [ -z "$NAME_VALUE" ]; then
    error "name_missing" "frontmatter" "no name field; the skill has no display identity"
else
    DIR_NAME=$(basename "$SKILL_DIR")

    # Naming is house convention. A skill authored to a different standard, or
    # predating this one, can carry any of these on purpose.
    if ! printf '%s' "$DIR_NAME" | grep -Eq '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'; then
        observe "slug_format" "$DIR_NAME" \
            "the directory slug is not lowercase alphanumeric with single hyphens" \
            "open-standard"
    fi
    if printf '%s' "$DIR_NAME" | grep -q -- '--'; then
        observe "slug_double_hyphen" "$DIR_NAME" \
            "the directory slug contains consecutive hyphens" \
            "open-standard"
    fi
    SLUG_LEN=$(printf '%s' "$DIR_NAME" | wc -c | tr -d ' ')
    if [ "$SLUG_LEN" -gt 64 ]; then
        observe "slug_length" "$DIR_NAME" \
            "the directory slug is $SLUG_LEN characters" \
            "open-standard"
    fi

    if ! printf '%s' "$NAME_VALUE" | grep -Eq '^[A-Z][A-Za-z0-9]*([ ][A-Z][A-Za-z0-9]*)*$'; then
        observe "name_not_title_case" "$NAME_VALUE" \
            "the name field is not title-cased with spaces" \
            "repo-overlay"
    fi

    # Body only. Scanning the whole file would let a "# comment" inside the
    # frontmatter win over the real H1.
    H1_VALUE=$(awk '
        NR == 1 && $0 == "---" { in_fm = 1; next }
        in_fm && $0 == "---" { in_fm = 0; next }
        !in_fm && /^# / { sub(/^# */, ""); print; exit }
    ' "$SKILL_FILE" 2>/dev/null || true)
    if [ -n "$H1_VALUE" ] && [ "$H1_VALUE" != "$NAME_VALUE" ]; then
        observe "h1_name_mismatch" "$H1_VALUE" \
            "the body's H1 differs from the frontmatter name \"$NAME_VALUE\"" \
            "repo-overlay"
    fi

    EXPECTED_NAME=$(printf '%s' "$DIR_NAME" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')
    if [ "$NAME_VALUE" != "$EXPECTED_NAME" ]; then
        observe "name_slug_mismatch" "$NAME_VALUE" \
            "the name is not the title-cased form of the slug \"$DIR_NAME\" (expected \"$EXPECTED_NAME\")" \
            "repo-overlay"
    fi
fi

if ! DESCRIPTION=$(extract_description "$FRONTMATTER"); then
    error "description_missing" "frontmatter" \
        "no description field; the skill has no retrieval surface and can never be matched"
else
    DESC_CHARS=$(printf '%s' "$DESCRIPTION" | wc -c | tr -d ' ')
    if [ "$DESC_CHARS" -eq 0 ]; then
        error "description_empty" "frontmatter" \
            "the description is empty; the skill has no retrieval surface"
    fi
    if [ "$DESC_CHARS" -gt 1024 ]; then
        observe "description_length" "frontmatter" \
            "the description is $DESC_CHARS characters, over the documented limit of 1024" \
            "open-standard"
    fi
    if ! printf '%s' "$DESCRIPTION" | grep -qE '\(1\).*\(2\)'; then
        observe "description_no_trigger_list" "frontmatter" \
            "the description does not contain the numbered trigger list pattern (1)...(2)..." \
            "repo-overlay"
    fi
fi

case "$FORMAT" in
    json) print_json ;;
    text) print_text ;;
    *)
        echo "error: unsupported format: $FORMAT" >&2
        exit 2
        ;;
esac
