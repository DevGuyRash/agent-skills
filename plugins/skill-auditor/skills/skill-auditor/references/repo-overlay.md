# Repo Overlay

House conventions for skills and plugins in this repository, layered on top of the portable checks in
the open standard.

`AGENTS.md` is loaded automatically at the repository root, so its rules are already in your context.
This file points at them and names what to verify; it does not restate them. A copy of a rule is a
copy that drifts, and the drift is silent because neither copy knows the other exists.

WHEN you audit a target outside this repository THEN you SHALL NOT apply this file, and you SHALL
label as house style any finding you carry over anyway.

## Checklist

Read the named `AGENTS.md` section, then verify the column beside it.

| `AGENTS.md` section | Verify | Script |
| --- | --- | --- |
| Command Isolation: Environment Variables Do NOT Persist Across Commands | Multi-command workflows pass state as explicit flags, never as exported variables between steps | |
| Skill authoring: `<skills-file-root>` | In-skill references are portable: use either consistent relative paths or the placeholder form, never machine-specific absolute paths | `reference_check.sh` |
| Plugin installation and portability | See below — the largest gap in a per-skill audit | `plugin_check.sh` |
| Skill authoring: frontmatter and naming | Slug format, name/slug contract for the applicable skill generation, H1/display-name intent, and description length | `frontmatter_check.sh` |
| Skill authoring: progressive disclosure and context budgets | Numeric line and token budgets only — SKILL.md and reference size targets, peak-context ceiling; router shape, one-fact-one-place, and no-nesting are the open standard's | `instruction_shape.sh`, `reference_check.sh` |
| Skill authoring: subagent dispatch prompt design | See below | |

Scripts live in `<skills-file-root>/scripts/`. An empty Script column means the check is yours to
make; no script exists because none can make it without guessing.

`AGENTS.md` also documents file hygiene, name consistency between docs and CLI, error messages
designed for agents, output size discipline, cold-start readiness, integration testing across
skills, idempotency and state isolation, error recovery, and credential safety. Each of those
sections restates a rule the open standard already states in full, so this checklist leaves them out
on purpose — they were read and matched against the open standard, not overlooked. WHEN you audit
any of those nine axes THEN you SHALL read the open standard's section for it; the `AGENTS.md` prose
is the same rule in a second place.

## Conventions with legitimate exceptions

Two more checklist items are this repository's convention rather than the open standard's, and each
has a legitimate counter-case.

Legacy title-casing `name` and deriving it from the directory slug (`name_not_title_case`,
`name_slug_mismatch`) remains allowed for skills not explicitly included in a naming migration.
Newly authored or deliberately migrated skills use the slug verbatim in frontmatter and place the
human-facing title in the H1 and host metadata.

Requiring the literal `<skills-file-root>` prefix on in-skill path references is no longer a
repository rule. A portable skill may use relative paths instead; the thing to verify is one-hop
reachability and consistency within the skill, not one specific path spelling.

## Description structure

Descriptions remain retrieval metadata, not mini-workflows. Verify that they front-load what the
skill does, the concrete work that activates it, and the most important sibling exclusion when
routing would otherwise collide.

WHEN a target claims to be required but uses passive opt-in framing THEN you SHALL report the
mismatch between the skill's stated importance and its actual activation posture.
WHEN a target uses mandatory framing without meeting the when-to-use criteria THEN you SHALL report
it as a trigger-precision defect, since a skill that always fires is a skill that fires on tasks it
does not improve.

The repository no longer requires the numbered `(1)... (2)...` trigger-list pattern. It is one
possible formatting choice, not a rule to audit.

## Plugin installation and portability

This section governs the surface a per-skill audit cannot see, and it is the most common source of
defects in this repository.

Verify the mandatory pre-push gate ran for any change touching `plugins/`: round-trip each changed
plugin through the other host and back, then validate each converted variant for its target host.
Conversion artifacts are scratch evidence and are not committed.

Verify that host publication matches executable capability — a plugin published to a host that cannot
run what it ships installs and then fails at use.

Note the `--source` persistence trap documented in the section: an installation source persists as
the durable marketplace source. A testing-only invocation therefore leaves durable state, so a target
whose documentation treats it as ephemeral is documenting a behavior the tool does not have.

Plugin fit carries the full package-level check set; `SKILL.md` routes you to it when the target is a
plugin.

## Subagent dispatch

Read §Skill authoring: subagent dispatch prompt design for the four requirements. What to verify:

The dispatch prompt is self-contained — task, scope, forbidden actions, output template, and agent
identity all present, because the subagent cannot see the orchestrator's context and will
confabulate whatever the prompt omits.

Forbidden actions are listed explicitly rather than implied by omission.

The output contract is a template, not prose describing what to return.

WHEN a skill defines multiple dispatch roles THEN all roles share one structural template with
domain-specific content swapped in. A role markedly shallower than its siblings is under-specified,
and the section names the threshold.

## Context budgets

The section states the numeric targets. Two notes on applying them:

The line limits are proxies for the token budgets, not independent rules. A file under the line limit
that blows the token budget is still a defect; report the budget, not the line count. The converse
holds too: a file over the limit that is genuinely a router — an index, a dispatch table — may be
fine. Treat the 500-line and 300-line numbers as signals that invite a look, not verdicts on their
own.

Peak context is what matters — `SKILL.md` plus the one reference the workflow actually loads next.
Summing every reference in the directory measures a state that never occurs.

## CLI-served self-documentation

An optional pattern, not a requirement. WHEN a target has no CLI THEN this section produces no
finding, and you SHALL NOT recommend adding one to satisfy it. The section itself is explicit that
routing through a CLI is a `SHOULD` for skills that already have one.

WHEN a target does route guidance through a CLI THEN verify the `SKILL.md` fallback exists: the agent
must be able to proceed when the CLI is unavailable.
