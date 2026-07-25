# Context Redesign

Context redesign keeps the active skill short, navigable, and progressively
disclosed.

## Loading Model

- Level 0 — metadata for retrieval
- Level 1 — a short `SKILL.md` that routes the workflow
- Level 2 — one question-specific reference at a time
- Level 3 — scripts or assets only on demand

## Context At Decision Time

File sizes are a proxy. What decides the outcome is what occupies the window when the agent chooses
its next action, and several sources of waste never show up in a line count.

You SHALL inspect:

- **What the skill puts in the window that it did not need to.** Script output enters context; script
  source does not. A helper that dumps a full report where a summary would decide the question spends
  the budget the layering was built to protect.
- **Whether invariants survive compaction.** A constraint stated once at the top of a long workflow is
  a constraint the agent may no longer hold when it reaches the step the constraint governs. Restated
  where it binds, it survives; stated only in a preamble, it does not.
- **Whether the skill dispatches work that should have been isolated.** Work whose intermediate output
  is large and whose result is small belongs behind a context boundary. Run inline, its byproducts
  crowd out the task.
- **Whether tool results are bounded.** A skill invoking commands with unbounded output has no context
  budget, whatever its files measure.

WHEN a target passes every size check and still exhausts context in practice THEN you SHALL look here
before proposing further trimming; cutting a file that was never the problem is motion without
improvement.

## Redesign Rules

You SHALL keep `SKILL.md` operational rather than encyclopedic.
You SHALL keep every active reference directly reachable from `SKILL.md`.
You SHALL keep active reference depth to one hop from `SKILL.md`.
WHEN theory, long examples, or pattern libraries are not needed for the current
question THEN you SHALL move them out of `SKILL.md`.
WHEN a reference mostly repeats `SKILL.md` THEN you SHALL collapse the
duplication into one source of truth.
WHEN scripts or assets are not needed for the current question THEN you SHALL
leave them unloaded.

## What To Inspect

- Top-level file size and navigability
- Directness of reference links
- Duplication between `SKILL.md` and references
- Whether scripts replace context instead of inflating it
- Whether the next step is obvious after reading only one file

## Trimming Plan

1. Keep the product summary.
2. Keep the question router.
3. Keep the output contract pointer.
4. Move theory, examples, and patterns into direct references.
5. Flatten any reference chain that requires opening another reference.

## Deliverables

You SHALL describe the main source of context waste.
You SHALL propose a trimming or restructuring plan.
You SHALL say which file should own each moved fact.
You SHALL include a verification step that proves a fresh agent can understand
the workflow from `SKILL.md` plus one next reference file.
