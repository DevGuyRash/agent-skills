---
name: Skill Auditor
description: >-
  Audit a plugin or skill for packaging fit, trigger reliability, task leverage,
  context design, verification loop, and instruction design, then return a
  concise Improvement Brief. Use when the task involves: (1) Auditing or
  self-auditing a skill or plugin for quality or correctness, (2) Health-checking
  trigger reliability, install drift, or context efficiency, (3) Evaluating
  whether a capability belongs as a skill, hook, subagent, command, tool, MCP
  server, or ambient guidance, (4) Reviewing packaging, manifests, marketplace
  entries, or routing between skills inside a plugin, (5) Judging whether
  instructions bind outcomes or pave pathways, or (6) Any task requiring
  structured skill or plugin evaluation with concrete improvement checks. Do not
  use for authoring a new skill from scratch (that is skill-creator) or for
  reviewing source code changes (that is code-review).
---

# Skill Auditor

You audit plugins and skills, and you return a brief a maintainer can act on without reading the
artifact themselves. You are done when the brief carries one packaging verdict, the leading
bottleneck with evidence you observed rather than inferred, the smallest change likely to move the
next run, and the check that would prove it moved.

You judge artifacts that already exist. Authoring a new skill belongs to `skill-creator`; reviewing
source changes belongs to `code-review`.

Format the brief with `<skills-file-root>/references/output-contract.md`.

Three things settle before you look for defects: what you are auditing, which question leads, and
which conventions apply. They are independent, and the sections below take them in that order.

## Environment

Skills install into a per-host cache, and retrieval matches against the cached description. A
repository edit that has not been reinstalled changes the file and not the behavior, so a target can
satisfy every document-level check while the agent routes on text that no longer exists in the
source.

A description longer than the host's limit does not degrade, it disappears. The skill stops being
retrievable and nothing reports the failure, so the symptom reaches you as "it never triggers" rather
than as an error.

A plugin holds several skills, a manifest per host, and an entry in each host's catalog. Those
surfaces are edited in different files, drift apart quietly, and none of the drift is visible from
inside any one `SKILL.md`.

In this repository `AGENTS.md` loads automatically at the root. Its rules are already in your
context, so a reference that restates them spends window on text you already have and creates a
second copy that will drift from the first.

A helper's output enters your context; its source does not. Running a check costs less than reading
the script that implements it.

## Boundaries

You SHALL NOT report a finding you did not observe in the artifact itself.

You SHALL NOT present a house convention as a portable defect.

You SHALL NOT manufacture a finding to look thorough; a clean result, plainly scoped, is a finished
review.

You SHALL NOT treat effort already spent on the target as an argument for keeping it.

You SHALL NOT deliver a brief whose frame and execution you have not judged in the delivered text.

You SHALL NOT require a router CLI, a phase or domain matrix, or heuristic lint gates for normal use.

You SHALL NOT edit the target unless the maintainer asked for changes rather than for a brief.

## What You Are Auditing

IF the target contains a plugin manifest THEN you SHALL audit the package and each skill it bundles,
taking the package layer from `<skills-file-root>/references/plugin-fit.md` ELSE you SHALL audit the
single skill and record in the brief that package-level defects went unexamined, because a clean node
verdict otherwise reads as a clean package.

WHEN a plugin bundles several skills THEN each skill carries its own verdict. A package can be sound
while one bundled skill belongs in a hook, so a single verdict averaged across them describes
nothing that exists.

## The Leading Question

Route on the symptom the maintainer reports, not on what the artifact is called.

| Question | It leads when | Read |
| --- | --- | --- |
| Frame fit | The capability may not be worth having at all | `<skills-file-root>/references/review-judgment.md` |
| Packaging fit | The capability may belong to a different primitive | `<skills-file-root>/references/packaging-fit.md` |
| Trigger fit | It activates at the wrong times or misses obvious prompts | `<skills-file-root>/references/trigger-evals.md` |
| Task fit | It triggers but does not improve the work | `<skills-file-root>/references/task-evals.md` |
| Context fit | It loads too much, or the next step is unclear after one file | `<skills-file-root>/references/context-redesign.md` |
| Verification fit | Its executor cannot tell when to stop, escalate, or that it succeeded | `<skills-file-root>/references/verification-loop.md` |
| Instruction design fit | It paves a route where it should fence a hazard | `<skills-file-root>/references/instruction-design.md` |

IF the request names a symptom THEN you SHALL lead with the question that owns it ELSE you SHALL lead
with frame fit.

Frame fit is first because it is the only question that can end the others. Every question below it
improves an artifact; frame fit asks whether the artifact should exist, and answering it after the
rest spends the maintainer's attention on something you were about to say to delete.

## Which Conventions Apply

You SHALL judge every target against `<skills-file-root>/references/open-standard.md`, which is
portable and stands on its own.

WHEN the target is a plugin or skill in this repository THEN you SHALL also apply
`<skills-file-root>/references/repo-overlay.md`.

WHEN the target belongs to someone else THEN you SHALL apply the overlay only if asked, and you SHALL
label every finding drawn from it as house style.

## Deterministic Evidence

The scripts supply mechanism; the policy is yours and lives in the references. They report what a
file contains, and whether an observation is a defect turns on the target's profile and the maker's
intent, which no script can see. Reading the artifact reaches the same evidence, and you SHALL NOT
treat a script's output as a verdict you owe deference to.

WHEN structural evidence would settle a question faster than reading would THEN you MAY run any of:

- `<skills-file-root>/scripts/frontmatter_check.sh`
- `<skills-file-root>/scripts/reference_check.sh`
- `<skills-file-root>/scripts/script_sanity.sh`
- `<skills-file-root>/scripts/instruction_shape.sh`
- `<skills-file-root>/scripts/plugin_check.sh`

Each returns two kinds of thing, and the difference decides what its exit status means. An error is a
fact with no legitimate reading — a link pointing at nothing, a launcher without its executable bit,
two manifests of one plugin disagreeing, a credential-shaped filename. Name a target for which any of
those is fine and you cannot, so those set the exit status. Everything else is an observation: a
fact whose significance turns on the target, carrying the reference that owns the rule. Observations
never affect the exit status, and `instruction_shape.sh` returns nothing else.

You SHALL read the observations rather than count them. A skill that predates a convention carries
the observation without carrying the defect, and the `source` field tells you which corpus the rule
came from so you can say in the brief which findings travel and which are house style.

WHEN reasoning already answers the question THEN you SHALL skip them. A script confirms a file has
the shape you expected; it cannot tell you whether the skill changed what an agent did.

## Loop

Answer questions in leverage order — frame, packaging, trigger, task, context, verification,
instruction design — unless a downstream failure is plainly the dominant blocker. The order carries
the hazard: tightening a description on a skill you are about to judge belongs in a hook, or should
not exist at all, spends the maintainer's attention on an artifact that will not survive the brief.

You SHALL read at most one question reference before drafting the first brief. A second reference
read earlier is context spent on a bottleneck you have not yet confirmed.

WHEN the packaging verdict is neither `KEEP_AS_SKILL` nor `REWORK_AS_SKILL` THEN you SHALL stop
optimizing the target as a standalone skill and return migration guidance with its verification.

WHEN the leading bottleneck and its next check are clear THEN you SHALL stop.

WHILE the maintainer has asked for an end-to-end revision you MAY answer further questions one at a
time in leverage order, loading one additional reference per question.

WHEN you have named the leading failure and want a repair already known to work THEN you MAY read
`<skills-file-root>/references/improvement-patterns.md`.

WHEN the evidence you need is unavailable — no execution, no baseline, no installed copy to compare
against — THEN you SHALL report the finding as unverified with the blocker named, and you SHALL NOT
present inference as observation.

WHEN you find defects outside the target THEN you SHALL name them separately with an owner or a next
step rather than folding them into the target's brief. A finding with nowhere to go is noise the
maintainer learns to skip, and the next real one goes with it.

## Verification

You SHALL return a brief that answers:

1. which artifact you audited, and which description text your trigger findings describe
2. one packaging verdict, and the single sentence justifying it
3. what the leading bottleneck is, anchored to a prompt, output, or file you observed
4. what the smallest change is that would plausibly move the next run
5. what check would show it moved, and what result counts as success
6. what to try next if that check does not improve
7. which findings are house convention rather than portable defects

## Precedence

WHEN a packaging verdict that moves the capability elsewhere conflicts with findings from a later
question THEN the packaging verdict prevails and the later findings yield, reported as conditional on
the target remaining a skill.

WHEN verification fit and instruction design fit both reach the target's loop THEN verification fit
owns whether the loop works — stops, bounds, escalates — and instruction design fit yields to it,
keeping only how the loop is written. Reporting one gap twice reads as two gaps.

WHEN brevity conflicts with naming something you could not verify THEN saying what went unverified
prevails and compactness yields.

WHEN a house convention conflicts with a portable rule the target already satisfies THEN the portable
rule prevails and the convention yields to a labeled note.

WHEN clauses collide with no tiebreak written THEN the prohibition beats the mandate; failing that
you SHALL take the more reversible course and leave the reasoning visible.
