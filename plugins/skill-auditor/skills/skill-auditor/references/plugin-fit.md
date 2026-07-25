# Plugin Fit

Plugin fit covers what no single skill can see: the package that ships the skills, the manifests that
describe it, the catalogs that publish it, the copy that actually loads, and the routing between
sibling skills inside it.

A plugin holds N skills plus optional `hooks/`, `agents/`, and `commands/`, two manifests
(`.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`), and an entry in each host's
marketplace catalog. Every one of those is a surface that can disagree with the others, and every
disagreement is invisible from inside any one `SKILL.md`.

WHEN the target path contains a plugin manifest THEN you SHALL audit at plugin level and treat each
bundled skill as a node beneath it.
WHEN the target path is a bare skill directory THEN you SHALL audit that node alone and say so in the
brief, because package-level defects stay unexamined and a clean node verdict would otherwise read as
a clean package.

## The copy that loads is not the copy in the repo

Skills install into a per-host cache. The description that decides whether a skill triggers is the
cached one, so a repository edit that has not been reinstalled changes nothing about routing. A
target can therefore pass every document-level check while the agent routes on text that no longer
exists in the source.

You SHALL compare the installed description against the repository description before reporting any
trigger finding. WHEN they differ THEN the installed text is what you SHALL evaluate for trigger fit,
and the divergence itself is a finding.

This is the one check that changes the meaning of another question's result rather than adding a
finding of its own.

## Manifest coherence

| Check | Defect |
| --- | --- |
| Both host manifests exist for a plugin published to both catalogs | Package installs on one host only |
| `version` agrees across both manifests | Hosts disagree about what is installed |
| `description` agrees across both manifests and the bundled `SKILL.md` | The catalog advertises behavior the skill no longer has |
| `license` declared and a LICENSE file present | A license claim with nothing behind it |
| Host publication matches shipped capability | A host-specific plugin published to a host that cannot run it |

**Declared capabilities are a known gap, not a check.** The manifest is a promise to the host about
what the package needs, so a skill invoking shell scripts under a read-only declaration looks like a
misdeclaration. But the capability vocabulary each host actually accepts is not documented anywhere
this skill can read, and a whole repository declaring the same value is as likely to be the
convention as to be a shared defect. You SHALL treat a capability declaration as a finding only when
you can point to the host's own schema, and you SHALL say the schema is unverified when you cannot.

## Catalog parity

Marketplace entries drift because they are edited in a different file from the manifests they
describe.

You SHALL compare, for every published plugin: the version in each catalog against the version in
each manifest, and the catalog description against the current skill description. WHEN a catalog
describes an older design than the skill now implements THEN you SHALL report it as a discovery
defect rather than a documentation nit — the catalog text is what a user reads when deciding whether
to install.

You SHALL verify that every published plugin is tracked by version control. A catalog entry pointing
at an untracked directory installs from a path that exists only on the maintainer's machine.

## Cross-skill routing

Sibling skills inside one plugin form a routing surface. Their descriptions are the edges: a negative
trigger naming another skill tells the agent where to go instead.

You SHALL check that sibling descriptions do not claim the same territory. Overlapping trigger
language between co-bundled skills produces nondeterministic routing that neither skill's own
metadata reveals.

You SHALL check that a negative trigger naming a sibling has its counterpart in that sibling. A
one-way edge routes traffic out of one skill without routing it in anywhere, so the skill that should
have received the work never advertises that it handles it.

WHEN two sibling skills are genuinely two halves of one workflow THEN you SHALL verify each names the
other and each states which half it owns. Splitting a capability without writing both edges is the
common failure, and it surfaces as the agent picking whichever description it saw first.

## Harness surfaces

`hooks/`, `agents/`, and `commands/` are packaging decisions, not implementation details. Each answers
a different question than a skill does, and a capability in the wrong one either never fires or fires
when nobody asked.

| Surface | What belongs there |
| --- | --- |
| `skills/` | On-demand expertise the agent retrieves when a task matches |
| `hooks/` | Behavior the host executes on an event, with no model decision involved |
| `agents/` | Work needing isolated context or a narrowed tool surface |
| `commands/` | An explicit entry point the user invokes by name |

WHEN a bundled skill describes always-on or event-triggered behavior THEN you SHALL evaluate it for
`MIGRATE_TO_HOOK` during packaging fit — a skill cannot guarantee it runs, and behavior described as
automatic but packaged as retrievable is behavior that silently does not happen.

WHEN a plugin ships hooks THEN you SHALL check that the hook's effect is documented somewhere the
agent will read it. A hook that mutates the environment without a corresponding note in any bundled
skill produces state the agent cannot account for.

## Deliverables

You SHALL name the plugin-level verdict separately from the per-skill verdicts, because a package can
be misassembled while every skill inside it is sound.

You SHALL report install drift before trigger findings, since drift determines which text the trigger
findings apply to.

You SHALL include, for each finding, the two surfaces that disagree and which one you treated as
authoritative.
