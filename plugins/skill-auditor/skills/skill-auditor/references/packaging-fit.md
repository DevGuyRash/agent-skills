# Packaging Fit

Packaging fit decides whether the target capability should stay a skill or move to a better
primitive. It is first in the leverage order because every other question optimizes an artifact this
one may decide should not exist.

## What to read

You SHALL read the target `SKILL.md`, and beyond it only the directly referenced files a packaging
decision actually needs.

WHEN the target relies on host-specific conventions THEN you SHALL identify its profile against the
open standard before calling any convention a defect.

## Decision lens

Four questions, in order:

1. Is the capability reusable across tasks or repositories?
2. Can activation be described clearly in metadata?
3. Is the value ambient policy, explicit workflow, executable code, or host-executed behavior?
4. Does the best design combine several primitives?

Question 4 is the one most often skipped. A capability that splits cleanly into a hook plus a small
skill is a better answer than either alone, and `HYBRID_RECOMMENDED` exists so you are not forced to
pick a loser.

## Verdicts

You SHALL state exactly one verdict, chosen by the condition that matches:

| Verdict | Condition |
| --- | --- |
| `KEEP_AS_SKILL` | Reusable expertise, retrieved on demand, and metadata already triggers it well |
| `REWORK_AS_SKILL` | Belongs as a skill but needs metadata, structure, or workflow changes |
| `MIGRATE_TO_AGENTS` | Ambient project guidance, coding policy, or house style the model should always have |
| `MIGRATE_TO_HOOK` | Behavior that must fire on an event, with no model judgment involved |
| `MIGRATE_TO_SUBAGENT` | The value is isolated context or a narrowed tool surface, not the instructions |
| `MIGRATE_TO_COMMAND` | An explicit entry point the user invokes by name, with arguments or modes |
| `MIGRATE_TO_EXPLICIT_PROMPT` | Needs no packaging at all — the user asking directly works as well |
| `MIGRATE_TO_TOOL` | Deterministic execution, external data, or generated artifacts rather than instructions |
| `MIGRATE_TO_MCP` | Access to external systems or shared services is the capability |
| `HYBRID_RECOMMENDED` | The strongest design splits the work across several of the above |

Three distinctions worth holding apart, because collapsing them produces a verdict that sounds right
and fixes nothing:

**Ambient guidance versus a hook.** Both are "always on." Ambient guidance is text the model reads
and may weigh against other instructions; a hook is code the host runs whether the model agrees or
not. WHEN the requirement is that something *always happens* rather than that the model always
*knows* something THEN the answer is a hook — a skill or an ambient note describing automatic
behavior is behavior that silently does not happen.

**A skill versus a subagent.** Both package expertise. The subagent's distinguishing value is a
context boundary: work that would flood the main window, or that needs a smaller tool surface than
the caller has. WHEN the instructions would work fine inline and the only gain is tidiness THEN it is
a skill.

**A command versus an explicit prompt.** Both are user-initiated. A command earns its packaging with
arguments, modes, or a body too long to retype. WHEN neither holds THEN the honest verdict is that no
artifact is needed.

## Output requirements

You SHALL explain the verdict in one sentence before listing any fix.

WHEN the verdict is neither `KEEP_AS_SKILL` nor `REWORK_AS_SKILL` THEN you SHALL stop optimizing the
target as a standalone skill and return migration guidance instead. Continuing to tune a description
on a skill you have just judged should be a hook spends the maintainer's attention on an artifact
that will not exist.

WHEN you recommend migration THEN you SHALL list the smallest set of content that moves and name the
primitive each piece belongs to.

You SHALL include a verification plan showing how the new packaging would be confirmed to reduce
false triggers or workflow confusion.

## What the capability is allowed to do

Choosing the primitive settles what a capability *is*; it does not settle what it may reach. A skill
declaring no tool scope inherits whatever the caller has, so a narrow capability runs with a wide
surface and nothing records that the mismatch exists.

WHEN a target performs destructive, outward, or credential-touching work THEN you SHALL check
whether it scopes its tool surface, and you SHALL report an unscoped one as a finding rather than as
a default.

WHEN a target declares a tool scope THEN you SHALL check the declaration against what the workflow
actually invokes. A scope narrower than the work blocks the skill at the moment it is needed; a
scope wider than the work is a permission nobody chose.

WHEN the host's scoping vocabulary is not documented anywhere you can read THEN you SHALL say the
schema is unverified rather than assert a defect, because a convention shared by every skill in a
repository is as likely to be correct as to be a shared mistake.

## Evidence that decides it

- Reuse across tasks or repositories
- Whether retrieval must be implicit or the user will always ask
- Reliance on scripts, CLIs, or external services
- Whether the behavior must be guaranteed or merely known
- Whether context isolation is the point
- Ambient repository policy or house style

## Anti-patterns

WHEN a skill mostly restates repository-wide policy THEN you SHALL treat it as a packaging mistake
rather than a metadata problem. Tightening the description of a skill that should not be retrieved at
all improves nothing.

WHEN a skill exists only to wrap one command and carries no reusable judgment THEN you SHALL treat it
as a tool candidate.

WHEN a skill bundles ambient policy together with an explicit workflow THEN you SHALL separate the
layers before scoring either, because the bundle's trigger surface is the union of two different
activation profiles and will misfire on both.
