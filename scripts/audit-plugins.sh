#!/usr/bin/env sh

set -eu

usage() {
    cat <<'EOF'
Usage: audit-plugins.sh [--errors-only] [plugin-name ...]

Gather what the skill-auditor's scripts can observe about every plugin, or the
named ones, and print it for a reader to judge.

The scripts report two kinds of thing. Errors are facts with no legitimate
reading — a link pointing at nothing, a required file absent, two manifests of
the same plugin disagreeing, a credential-shaped filename. There is no plugin
for which those are fine, so they set the exit status.

Everything else is an observation: a fact whose significance depends on the
target, carrying the reference that owns the rule. Lengths, naming, idiom, and
house conventions live here. They are printed and never fail, because whether
one is a defect depends on the target's age, profile, and intent, and no script
can see those.

  --errors-only   omit observations; print only what is broken

Exit: 0 no errors, 1 errors found, 2 unusable arguments.
EOF
}

REPO_ROOT=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
AUDITOR="$REPO_ROOT/plugins/skill-auditor/skills/skill-auditor/scripts"
SKILL_SCRIPTS="frontmatter_check reference_check script_sanity instruction_shape"
ERRORS_ONLY=0
TARGETS=""
ERROR_TOTAL=0
OBS_TOTAL=0
CHECKED=0
FAILED=""

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        --errors-only) ERRORS_ONLY=1; shift ;;
        -*) echo "error: unknown flag: $1" >&2; echo "hint: --errors-only, or a plugin name" >&2; exit 2 ;;
        *) TARGETS="$TARGETS $1"; shift ;;
    esac
done

if [ ! -d "$AUDITOR" ]; then
    echo "error: skill-auditor scripts not found at $AUDITOR" >&2
    exit 2
fi

if [ -z "$TARGETS" ]; then
    TARGETS=$(find "$REPO_ROOT/plugins" -mindepth 1 -maxdepth 1 -type d | sort | while IFS= read -r d; do
        printf '%s ' "$(basename "$d")"
    done)
fi

# Print a report, tally its two kinds, and remember whether it failed. The
# script's own exit status is the only thing that decides failure here; this
# runner adds no policy of its own.
run_report() {
    label="$1"
    shift
    status=0
    output=$("$@" 2>&1) || status=$?

    if [ "$status" -eq 2 ]; then
        echo "  $label: could not run"
        printf '%s\n' "$output" | sed 's/^/    /'
        FAILED="$FAILED
$label (could not run)"
        ERROR_TOTAL=$((ERROR_TOTAL + 1))
        return 0
    fi

    errs=$(printf '%s\n' "$output" | sed -n 's/^errors=//p' | head -1)
    obs=$(printf '%s\n' "$output" | sed -n 's/^observations=//p' | head -1)
    [ -n "$errs" ] || errs=0
    [ -n "$obs" ] || obs=0
    ERROR_TOTAL=$((ERROR_TOTAL + errs))
    OBS_TOTAL=$((OBS_TOTAL + obs))

    # The exit status decides, not the parsed count. A checker that crashes or
    # is killed emits no errors= line, and trusting the parse would report it
    # as clean — which is how a broken checker hides.
    if [ "$status" -ne 0 ]; then
        FAILED="$FAILED
$label"
        if [ "$errs" -eq 0 ]; then
            echo "  $label: exited $status without reporting an error"
            printf '%s\n' "$output" | sed 's/^/    /'
            return 0
        fi
    fi

    # A pure reporter emits neither count. Print it rather than swallow it.
    if [ "$errs" -eq 0 ] && [ "$obs" -eq 0 ] &&
       ! printf '%s\n' "$output" | grep -q '^observations='; then
        if [ "$ERRORS_ONLY" -eq 0 ]; then
            echo "  $label"
            printf '%s\n' "$output" | sed '1d' | sed 's/^/    /'
        fi
        return 0
    fi

    if [ "$errs" -eq 0 ] && { [ "$ERRORS_ONLY" -eq 1 ] || [ "$obs" -eq 0 ]; }; then
        return 0
    fi

    echo "  $label"
    if [ "$ERRORS_ONLY" -eq 1 ]; then
        # An ERROR line plus its indented continuation, stopping at the next
        # unindented line. Printing to end-of-output would sweep in the
        # observations, which errors-only exists to leave out.
        printf '%s\n' "$output" | awk '
            /^ERROR / { p = 1; print; next }
            p && /^[[:space:]]/ { print; next }
            { p = 0 }
        ' | sed 's/^/    /'
    else
        printf '%s\n' "$output" | sed '1,/^observations=/d' | sed 's/^/    /'
    fi
}

for plugin in $TARGETS; do
    plugin_dir="$REPO_ROOT/plugins/$plugin"
    # A named plugin that no longer exists is normal input: a change that
    # deletes or renames one still names it in the diff. Skipping keeps the
    # rest of the sweep running instead of aborting the whole audit.
    if [ ! -d "$plugin_dir" ]; then
        echo "$plugin: no such plugin directory — skipped"
        continue
    fi

    echo "$plugin"
    CHECKED=$((CHECKED + 1))

    run_report "$plugin: plugin_check" sh "$AUDITOR/plugin_check.sh" "$plugin_dir"

    for skill_md in "$plugin_dir"/skills/*/SKILL.md; do
        [ -f "$skill_md" ] || continue
        skill_dir=$(dirname "$skill_md")
        slug=$(basename "$skill_dir")
        for check in $SKILL_SCRIPTS; do
            run_report "$plugin/$slug: $check" sh "$AUDITOR/$check.sh" "$skill_dir"
        done
    done
done

echo
echo "plugins checked: $CHECKED"
echo "errors: $ERROR_TOTAL"
echo "observations: $OBS_TOTAL"

FAILED_TRIMMED=$(printf '%s\n' "$FAILED" | sed '/^$/d')

if [ "$ERROR_TOTAL" -eq 0 ] && [ -z "$FAILED_TRIMMED" ]; then
    echo "result: nothing broken"
    exit 0
fi

if [ "$ERROR_TOTAL" -eq 0 ]; then
    echo "result: a check failed without reporting an error — treat this as broken tooling"
else
    echo "result: $ERROR_TOTAL error(s) — each is broken for every target, not a matter of convention"
fi
printf '%s\n' "$FAILED_TRIMMED" | sed 's/^/  /'
exit 1
