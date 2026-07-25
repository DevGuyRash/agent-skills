#!/usr/bin/env sh

set -eu

FORMAT=text

usage() {
    cat <<'EOF'
Usage: script_sanity.sh <skill-directory> [--format json]

Report what is true of a skill's files, in two kinds. Most checks cover only
the top-level scripts in scripts/; the secret-file scan covers the whole
skill directory, since a credential can be committed anywhere in it.

Errors are broken for every target: a launcher without its executable bit, a
script with no shebang, CRLF in a script whose shebang the shell must read, a
filename matching a credential-naming pattern anywhere in the skill. A
carriage return after `#!/usr/bin/env sh` makes the interpreter unfindable, and
a committed credential file is unsafe, on every target.

Observations are facts whose significance depends on the target, each carrying
the rule it bears on — including a script that creates temporary files but has
no trap to remove them. They never fail.

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

error() {
    if [ "$ERR_COUNT" -gt 0 ]; then ERR_JSON="$ERR_JSON,"; fi
    ERR_JSON="$ERR_JSON{\"code\":\"$(json_escape "$1")\",\"subject\":\"$(json_escape "$2")\",\"fact\":\"$(json_escape "$3")\"}"
    ERR_COUNT=$((ERR_COUNT + 1))
    TEXT_ERRORS="$TEXT_ERRORS
ERROR $1: $2
  $3"
}

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

has_crlf() {
    awk '/\r$/ { found = 1; exit 0 } END { exit(found ? 0 : 1) }' "$1"
}

is_text_like_file() {
    [ -s "$1" ] || return 0
    LC_ALL=C grep -Iq . "$1"
}

requires_launcher_contract() {
    case "$1" in
        *.sh) return 0 ;;
        *.*) return 1 ;;
        *) return 0 ;;
    esac
}

print_text() {
    echo "REPORT script_sanity"
    echo "skill_dir=$SKILL_DIR"
    echo "script_count=$SCRIPT_COUNT"
    echo "errors=$ERR_COUNT"
    echo "observations=$OBS_COUNT"
    [ "$ERR_COUNT" -eq 0 ] || printf '%s\n' "$TEXT_ERRORS"
    [ "$OBS_COUNT" -eq 0 ] || printf '%s\n' "$TEXT_OBS"
    [ "$ERR_COUNT" -eq 0 ] || exit 1
    exit 0
}

print_json() {
    printf '{'
    printf '"script":"script_sanity",'
    printf '"skill_dir":"%s",' "$(json_escape "$SKILL_DIR")"
    printf '"script_count":%s,' "$SCRIPT_COUNT"
    printf '"error_count":%s,' "$ERR_COUNT"
    printf '"errors":[%s],' "$ERR_JSON"
    printf '"observation_count":%s,' "$OBS_COUNT"
    printf '"observations":[%s]' "$OBS_JSON"
    printf '}\n'
    [ "$ERR_COUNT" -eq 0 ] || exit 1
    exit 0
}

TEXT_ERRORS=""; TEXT_OBS=""
ERR_JSON=""; OBS_JSON=""
ERR_COUNT=0; OBS_COUNT=0
SCRIPT_COUNT=0
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

# Whole-directory scan, not scripts/-only: a committed credential is broken
# for every target regardless of which subdirectory it lands in. One find
# pass lists every match; no per-file subprocess is spawned for it.
CRLF_FILE="${TMPDIR:-/tmp}/scriptsanity_crlf.$$"
trap 'rm -f "$CRLF_FILE"' EXIT INT TERM
SCRIPTS_DIR="$SKILL_DIR/scripts"

SECRET_FILES=$(find "$SKILL_DIR" -type f \( -name '.env' -o -name '.env.*' -o -name 'credentials.*' -o -name '*secret*' -o -name '*token*' \) \
    -not -path '*/.git/*' -not -path '*/__pycache__/*' -not -path '*/.pytest_cache/*' \
    -not -name '*.py' -not -name '*.sh' -not -name '*.md' | sort)
if [ -n "$SECRET_FILES" ]; then
    while IFS= read -r secret_file; do
        [ -n "$secret_file" ] || continue
        error "secret_pattern_file" "${secret_file#"$SKILL_DIR"/}" \
            "the filename matches a credential-naming pattern (.env, credentials.*, *secret*, *token*), which risks a committed credential"
    done <<EOF
$SECRET_FILES
EOF
fi

# CRLF anywhere in the skill's text files, in one pass. Runs before the
# scripts/ early-return: a skill with no scripts/ still has references and a
# SKILL.md that can carry CRLF. Inside an executable this is an error — the
# carriage return joins the interpreter path and the shebang fails — and that
# case is caught in the per-script loop below.
find "$SKILL_DIR" -type f \
    \( -name '*.md' -o -name '*.py' -o -name '*.rs' -o -name '*.toml' \
       -o -name '*.yml' -o -name '*.yaml' -o -name '*.json' -o -name '*.sh' \) \
    -not -path '*/.git/*' -not -path '*/__pycache__/*' -not -path '*/.pytest_cache/*' \
    -exec grep -lI "$(printf '\r')$" {} + 2>/dev/null | sort -u >"$CRLF_FILE" || true
while IFS= read -r crlf_file; do
    [ -n "$crlf_file" ] || continue
    # Files under scripts/ are handled by the per-script loop below; reporting
    # them here too would double-count. Everywhere else the same distinction
    # still applies — an executable's shebang breaks, a data file's does not.
    case "$crlf_file" in
        "$SCRIPTS_DIR"/*) continue ;;
    esac
    if [ -x "$crlf_file" ]; then
        error "crlf_in_executable" "${crlf_file#"$SKILL_DIR"/}" \
            "the file is executable and uses CRLF; the carriage return becomes part of the interpreter path and the shebang fails"
    else
        observe "crlf" "${crlf_file#"$SKILL_DIR"/}" \
            "the file uses CRLF line endings" \
            "open-standard"
    fi
done <"$CRLF_FILE"

if [ ! -d "$SCRIPTS_DIR" ]; then
    case "$FORMAT" in json) print_json ;; text) print_text ;; esac
fi

# Recursive on purpose: a helper under scripts/lib/ that the launcher sources
# is as unrunnable without its executable bit or shebang as the launcher is.
TOP_LEVEL_SCRIPTS=$(find "$SCRIPTS_DIR" -type f \
    -not -path '*/__pycache__/*' -not -path '*/.pytest_cache/*' | sort)
if [ -n "$TOP_LEVEL_SCRIPTS" ]; then
    SCRIPT_COUNT=$(printf '%s\n' "$TOP_LEVEL_SCRIPTS" | sed '/^$/d' | wc -l | tr -d ' ')
fi

if [ -n "$TOP_LEVEL_SCRIPTS" ]; then
    while IFS= read -r script_file; do
        [ -n "$script_file" ] || continue
        script_name=$(basename "$script_file")
        script_rel=${script_file#"$SKILL_DIR"/}
        is_text_like_file "$script_file" || continue

        executable=false
        [ ! -x "$script_file" ] || executable=true
        shebang=$(head -1 "$script_file" 2>/dev/null || true)
        launcher=false
        ! requires_launcher_contract "$script_name" || launcher=true

        # A carriage return lands inside the interpreter path, so the shell
        # cannot find it. Broken for every target that runs the script.
        if has_crlf "$script_file"; then
            if [ "$launcher" = true ] || [ "$executable" = true ]; then
                error "crlf_in_executable" "$script_rel" \
                    "the script uses CRLF; the carriage return becomes part of the interpreter path and the shebang fails"
            else
                observe "crlf" "$script_rel" \
                    "the file uses CRLF line endings" \
                    "open-standard"
            fi
        fi

        if [ "$launcher" = true ]; then
            if [ "$executable" != true ]; then
                error "not_executable" "$script_rel" \
                    "a launcher without its executable bit cannot be invoked"
            fi
            case "$shebang" in
                '#!'*) ;;
                *) error "missing_shebang" "$script_rel" \
                       "a launcher with no shebang has no interpreter to run under" ;;
            esac
        elif [ "$executable" = true ]; then
            case "$shebang" in
                '#!'*) ;;
                *) error "missing_shebang" "$script_rel" \
                       "the file is executable but has no shebang" ;;
            esac
        fi

        # Cleanup handler, but only where there is something to clean up. A
        # script that creates no temporary file has nothing to remove, so
        # demanding a trap of every script reports noise on most of them and
        # trains the reader to ignore the one case that matters.
        if [ "$launcher" = true ] && grep -qE 'mktemp|\$\$|TMPDIR|/tmp/' "$script_file" 2>/dev/null; then
            if ! grep -q 'trap ' "$script_file" 2>/dev/null; then
                observe "script_no_trap" "$script_rel" \
                    "the script creates temporary files but has no trap handler" \
                    "open-standard"
            fi
        fi
    done <<EOF
$TOP_LEVEL_SCRIPTS
EOF
fi

case "$FORMAT" in
    json) print_json ;;
    text) print_text ;;
esac
