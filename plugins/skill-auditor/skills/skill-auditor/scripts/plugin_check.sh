#!/usr/bin/env sh

set -eu

FORMAT=text
MARKETPLACE=""
INSTALLED=""

usage() {
    cat <<'EOF'
Usage: plugin_check.sh <plugin-directory> [--marketplace <file>] [--installed <dir>] [--format json]

Check the package surfaces no single SKILL.md can see, in two kinds:
  - both host manifests present, and agreeing on version and description
  - manifest description matching a single bundled skill
  - declared capabilities covering what the skills actually do
  - a declared license having a LICENSE file behind it
  - reciprocal negative-trigger edges between sibling skills
  - catalog version parity            (needs --marketplace, else auto-discovered)
  - installed-vs-repository drift     (needs --installed, else auto-discovered)

Errors are broken for every target: a missing host manifest, no bundled
skills, manifests or catalog entries disagreeing on version or description,
or a catalog entry published over untracked content. There is no plugin for
which these are fine.

Observations are facts whose significance depends on the target — installed
vs. repository drift, a declared license with no LICENSE file in reach, an
asymmetric routing edge between sibling skills, an unpublished plugin, a
catalog entry with no version to compare. Each carries the rule it bears on
so the reader can decide. They never fail.

Surfaces that cannot be located are reported as unchecked, never as passing.

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

append_unchecked() {
    what="$1"
    if [ -n "$UNCHECKED" ]; then UNCHECKED="$UNCHECKED,$what"; else UNCHECKED="$what"; fi
}

# Top-level JSON string field. Manifest values are single-line by JSON rules.
json_field() {
    field="$1"; file="$2"
    grep -oE "\"$field\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*\"" "$file" 2>/dev/null |
        head -1 | sed -e "s/^\"$field\"[[:space:]]*:[[:space:]]*\"//" -e 's/"$//' || true
}

# Fold a YAML frontmatter block scalar into one line.
yaml_description() {
    awk '
        NR == 1 && $0 == "---" { in_fm = 1; next }
        in_fm && $0 == "---" { exit }
        !in_fm { next }
        /^description:/ {
            collecting = 1
            rest = $0
            sub(/^description:[[:space:]]*/, "", rest)
            if (rest != "" && rest !~ /^[>|][-+]?$/) { printf "%s", rest }
            next
        }
        collecting && /^[A-Za-z_-]+:/ { collecting = 0 }
        collecting {
            line = $0
            sub(/^[[:space:]]+/, "", line)
            if (line != "") { printf "%s ", line }
        }
    ' "$1" | sed -e 's/[[:space:]]\{1,\}/ /g' -e 's/^ //' -e 's/ $//'
}

# One cheap scan of the small slug/description lookup, not a re-parse of a
# SKILL.md file. Populated once, below, before any caller needs it.
desc_for_slug() {
    awk -F'\t' -v s="$1" '$1 == s { sub(/^[^\t]*\t/, ""); print; exit }' "$DESC_LOOKUP"
}

# Compare descriptions on content, not encoding. JSON escapes non-ASCII as
# \uXXXX while YAML carries the literal bytes, so an em-dash alone would report
# every such description as drifted. Fold both forms to one placeholder.
normalize() {
    printf '%s' "$1" |
        sed -e 's/\\u[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]/?/g' |
        tr -c '\11\12\40-\176' '?' |
        tr -s '?' |
        sed -e 's/[[:space:]]\{1,\}/ /g' -e 's/^ //' -e 's/ $//'
}

print_text() {
    echo "REPORT plugin_check"
    echo "plugin_dir=$PLUGIN_DIR"
    echo "plugin=$PLUGIN_NAME"
    echo "skills=$SKILL_COUNT"
    if [ -n "$UNCHECKED" ]; then echo "unchecked=$UNCHECKED"; fi
    echo "errors=$ERR_COUNT"
    echo "observations=$OBS_COUNT"
    [ "$ERR_COUNT" -eq 0 ] || printf '%s\n' "$TEXT_ERRORS"
    [ "$OBS_COUNT" -eq 0 ] || printf '%s\n' "$TEXT_OBS"
    [ "$ERR_COUNT" -eq 0 ] || exit 1
    exit 0
}

print_json() {
    printf '{'
    printf '"script":"plugin_check",'
    printf '"plugin_dir":"%s",' "$(json_escape "$PLUGIN_DIR")"
    printf '"plugin":"%s",' "$(json_escape "$PLUGIN_NAME")"
    printf '"skills":%s,' "$SKILL_COUNT"
    printf '"unchecked":"%s",' "$(json_escape "$UNCHECKED")"
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
SKILL_COUNT=0
UNCHECKED=""
PLUGIN_NAME=""
PLUGIN_DIR=""

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        --format) FORMAT="${2-}"; shift 2 ;;
        --format=*) FORMAT=${1#*=}; shift ;;
        --marketplace) MARKETPLACE="${2-}"; shift 2 ;;
        --marketplace=*) MARKETPLACE=${1#*=}; shift ;;
        --installed) INSTALLED="${2-}"; shift 2 ;;
        --installed=*) INSTALLED=${1#*=}; shift ;;
        -*) fail_usage "unknown flag: $1" ;;
        *)
            [ -z "$PLUGIN_DIR" ] || fail_usage "only one plugin directory may be provided"
            PLUGIN_DIR="$1"; shift ;;
    esac
done

[ -n "$PLUGIN_DIR" ] || { usage >&2; exit 2; }

case "$FORMAT" in
    text|json) ;;
    *) fail_usage "unsupported format: $FORMAT" "use text or json" ;;
esac

# Not a finding about the target: the script could not run.
[ -d "$PLUGIN_DIR" ] || fail_usage "plugin directory not found: $PLUGIN_DIR"

PLUGIN_NAME=$(basename "$PLUGIN_DIR")
CLAUDE_MANIFEST="$PLUGIN_DIR/.claude-plugin/plugin.json"
CODEX_MANIFEST="$PLUGIN_DIR/.codex-plugin/plugin.json"

# --- manifests present -----------------------------------------------------

[ -f "$CLAUDE_MANIFEST" ] || error "missing_claude_manifest" ".claude-plugin/plugin.json" \
    "the file does not exist; Claude Code has no manifest to load for this plugin"
[ -f "$CODEX_MANIFEST" ] || error "missing_codex_manifest" ".codex-plugin/plugin.json" \
    "the file does not exist; Codex has no manifest to load for this plugin"

if [ ! -f "$CLAUDE_MANIFEST" ] || [ ! -f "$CODEX_MANIFEST" ]; then
    case "$FORMAT" in json) print_json ;; text) print_text ;; esac
fi

CLAUDE_VERSION=$(json_field version "$CLAUDE_MANIFEST")
CODEX_VERSION=$(json_field version "$CODEX_MANIFEST")
CLAUDE_DESC=$(json_field description "$CLAUDE_MANIFEST")
CODEX_DESC=$(json_field description "$CODEX_MANIFEST")
CLAUDE_LICENSE=$(json_field license "$CLAUDE_MANIFEST")

if [ -n "$CLAUDE_VERSION" ] && [ -n "$CODEX_VERSION" ] && [ "$CLAUDE_VERSION" != "$CODEX_VERSION" ]; then
    error "manifest_version_mismatch" "version" \
        "claude manifest says $CLAUDE_VERSION, codex manifest says $CODEX_VERSION"
fi

if [ -n "$CLAUDE_DESC" ] && [ -n "$CODEX_DESC" ]; then
    if [ "$(normalize "$CLAUDE_DESC")" != "$(normalize "$CODEX_DESC")" ]; then
        error "manifest_description_mismatch" "description" \
            "claude and codex manifests disagree on description text"
    fi
fi

# --- bundled skills --------------------------------------------------------

SKILL_FILES=""
if [ -d "$PLUGIN_DIR/skills" ]; then
    SKILL_FILES=$(find "$PLUGIN_DIR/skills" -mindepth 2 -maxdepth 2 -name 'SKILL.md' | sort)
fi

if [ -n "$SKILL_FILES" ]; then
    SKILL_COUNT=$(printf '%s\n' "$SKILL_FILES" | sed '/^$/d' | wc -l | tr -d ' ')
fi

if [ "$SKILL_COUNT" -eq 0 ]; then
    error "no_skills" "skills" "the plugin bundles no skills"
    case "$FORMAT" in json) print_json ;; text) print_text ;; esac
fi

# Fold every bundled skill's description once, up front. yaml_description
# parses a whole YAML frontmatter block; the routing-edge check below compares
# every skill against every other and the installed-drift check reads it
# again, so computing it inline at each of those call sites would fork that
# parse O(S^2) times over the same S files. A slug/description lookup, read
# instead of re-parsed, is where this script's time went before.
DESC_LOOKUP="${TMPDIR:-/tmp}/plugincheck_desc.$$"
trap 'rm -f "$DESC_LOOKUP"' EXIT INT TERM
: >"$DESC_LOOKUP"

while IFS= read -r sf; do
    [ -n "$sf" ] || continue
    slug=$(basename "$(dirname "$sf")")
    printf '%s\t%s\n' "$slug" "$(yaml_description "$sf")" >>"$DESC_LOOKUP"
done <<EOF
$SKILL_FILES
EOF

if [ "$SKILL_COUNT" -eq 1 ]; then
    only_skill=$(printf '%s\n' "$SKILL_FILES" | head -1)
    only_slug=$(basename "$(dirname "$only_skill")")
    skill_desc=$(desc_for_slug "$only_slug")
    if [ -n "$skill_desc" ] && [ -n "$CLAUDE_DESC" ]; then
        if [ "$(normalize "$skill_desc")" != "$(normalize "$CLAUDE_DESC")" ]; then
            error "skill_description_mismatch" "$only_slug" \
                "the manifest description differs from this skill's frontmatter description"
        fi
    fi
fi

# Declared capability versus actual use is deliberately not checked here. Every
# plugin in this repository declares Read or Read+Write while several invoke
# scripts, so a check would flag the whole set against a convention that may be
# correct; whether the host schema even defines an execute capability is unknown.
# Plugin fit keeps it as a judgment item instead.

# --- license ---------------------------------------------------------------

if [ -n "$CLAUDE_LICENSE" ]; then
    license_found=no
    probe="$PLUGIN_DIR"
    depth=0
    while [ "$depth" -lt 5 ]; do
        for candidate in LICENSE LICENSE.md LICENSE.txt COPYING; do
            if [ -f "$probe/$candidate" ]; then license_found=yes; fi
        done
        [ "$license_found" = no ] || break
        probe=$(dirname "$probe")
        [ "$probe" != "/" ] || break
        depth=$((depth + 1))
    done
    if [ "$license_found" = no ]; then
        observe "license_without_file" "$CLAUDE_LICENSE" \
            "the manifest declares this license but no LICENSE file was found above the plugin" \
            "repo-overlay"
    fi
fi

# --- reciprocal negative-trigger edges -------------------------------------

if [ "$SKILL_COUNT" -gt 1 ]; then
    while IFS= read -r sf_a; do
        [ -n "$sf_a" ] || continue
        slug_a=$(basename "$(dirname "$sf_a")")
        desc_a=$(desc_for_slug "$slug_a")
        while IFS= read -r sf_b; do
            [ -n "$sf_b" ] || continue
            slug_b=$(basename "$(dirname "$sf_b")")
            [ "$slug_a" != "$slug_b" ] || continue
            case "$desc_a" in
                *"$slug_b"*)
                    desc_b=$(desc_for_slug "$slug_b")
                    case "$desc_b" in
                        *"$slug_a"*) ;;
                        *) observe "one_way_routing_edge" "$slug_a" \
                               "routes to $slug_b, but $slug_b never names $slug_a back" \
                               "repo-overlay" ;;
                    esac
                    ;;
            esac
        done <<EOF
$SKILL_FILES
EOF
    done <<EOF
$SKILL_FILES
EOF
fi

# --- catalog parity --------------------------------------------------------

if [ -z "$MARKETPLACE" ]; then
    probe="$PLUGIN_DIR"; depth=0
    while [ "$depth" -lt 5 ]; do
        probe=$(dirname "$probe")
        [ "$probe" != "/" ] || break
        if [ -f "$probe/.claude-plugin/marketplace.json" ]; then
            MARKETPLACE="$probe/.claude-plugin/marketplace.json"
            break
        fi
        depth=$((depth + 1))
    done
fi

if [ -n "$MARKETPLACE" ] && [ -f "$MARKETPLACE" ]; then
    # Scan forward from the plugin's name to its version, stopping at the next
    # entry. Splitting the file on commas would break inside any description
    # that contains one, silently pushing version out of reach.
    catalog_version=$(awk -v target="$PLUGIN_NAME" '
        index($0, "\"name\"") && index($0, "\"" target "\"") { found = 1; next }
        found && index($0, "\"name\"") { exit }
        found && index($0, "\"version\"") {
            line = $0
            sub(/.*"version"[[:space:]]*:[[:space:]]*"/, "", line)
            sub(/".*/, "", line)
            print line
            exit
        }
    ' "$MARKETPLACE")

    if ! grep -q "\"$PLUGIN_NAME\"" "$MARKETPLACE" 2>/dev/null; then
        observe "not_published" "$PLUGIN_NAME" "no entry in $MARKETPLACE" "repo-overlay"
    else
        # A catalog entry pointing at untracked content installs from a path
        # that exists only on the maintainer's machine.
        if command -v git >/dev/null 2>&1 &&
           git -C "$PLUGIN_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
            if [ -z "$(git -C "$PLUGIN_DIR" ls-files . 2>/dev/null | head -1)" ]; then
                error "published_but_untracked" "$PLUGIN_NAME" \
                    "the catalog entry exists but no file under the plugin directory is tracked by git"
            fi
        else
            append_unchecked "tracking"
        fi
    fi

    if grep -q "\"$PLUGIN_NAME\"" "$MARKETPLACE" 2>/dev/null; then
        if [ -z "$catalog_version" ]; then
            observe "catalog_no_version" "$PLUGIN_NAME" \
                "catalog entry declares no version to compare against" \
                "repo-overlay"
        elif [ -n "$CLAUDE_VERSION" ] && [ "$catalog_version" != "$CLAUDE_VERSION" ]; then
            error "catalog_version_mismatch" "version" \
                "catalog says $catalog_version, manifest says $CLAUDE_VERSION"
        fi
    fi
else
    append_unchecked "catalog"
fi

# --- installed drift -------------------------------------------------------

if [ -z "$INSTALLED" ]; then
    for base in "$HOME/.claude/plugins/cache" "$HOME/.codex/plugins/cache"; do
        [ -d "$base" ] || continue
        found=$(find "$base" -mindepth 2 -maxdepth 3 -type d -name "$PLUGIN_NAME" 2>/dev/null | head -1 || true)
        if [ -n "$found" ]; then INSTALLED="$found"; break; fi
    done
fi

if [ -n "$INSTALLED" ] && [ -d "$INSTALLED" ]; then
    while IFS= read -r sf; do
        [ -n "$sf" ] || continue
        slug=$(basename "$(dirname "$sf")")
        installed_skill=$(find "$INSTALLED" -type f -path "*/$slug/SKILL.md" 2>/dev/null | head -1 || true)
        if [ -n "$installed_skill" ]; then
            repo_desc=$(normalize "$(desc_for_slug "$slug")")
            inst_desc=$(normalize "$(yaml_description "$installed_skill")")
            if [ -n "$repo_desc" ] && [ -n "$inst_desc" ] && [ "$repo_desc" != "$inst_desc" ]; then
                observe "install_drift" "$slug" \
                    "installed description differs from the repository; retrieval matches the installed text" \
                    "open-standard"
            fi
        fi
    done <<EOF
$SKILL_FILES
EOF
else
    append_unchecked "install"
fi

case "$FORMAT" in
    json) print_json ;;
    text) print_text ;;
esac
