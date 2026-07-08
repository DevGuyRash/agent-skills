# Final Plan: GoalSpec V2 as a Planning Kernel

## Summary

Rebuild GoalSpec as a small markdown-first planning skill, not a contract compiler or execution runtime.

GoalSpec V2 should shift intent interpretation left by producing durable goal briefs and goal maps that preserve:

- source wording
- interpretation and interpretation risk
- real “done means” outcomes
- positive constraints
- negative invariants
- stop/ask conditions
- reproducible evidence recipes tied directly to done-means

It should not mechanically govern execution. No default CLI, hooks, hash locks, graph runtime, auto-advance, evidence capture, campaign state, custom reviewer agents, or verifier-as-authority model.

The core principle:

> GoalSpec disciplines judgment; it does not replace judgment with machinery.

## Key Decisions

- Use a hard V2 break, but sequence it safely:
  - First build V2 alongside recoverable V1 behavior.
  - Run behavioral A/B: V1 vs V2 vs raw/no-system.
  - Score final product outcome first, auditability second.
  - Then remove V1 from the shipped/default surface once V2 wins or ties on product quality.
- Store generated artifacts in the repo’s context convention:
  - prefer `.local*/context/` when present
  - otherwise use `context/`
  - GoalSpec artifacts live under `context/goals/`
- Keep launch-ready `/goal ...` handoff prompts.
- Status is bookkeeping only, never proof.
- Evidence is a reproducible recipe for a reviewer or fresh agent, not self-certification.
- Final validation goals are used for multi-goal/integration-sensitive maps.
- Audit-class verifiers/reviewers may return later as explicit opt-in add-ons, not default GoalSpec.

## Package Shape

Keep only the lightweight authoring surface:

- `SKILL.md`
- `references/goal-format.md`
- `references/goalmap-format.md`
- `references/examples.md`
- `references/anti-patterns.md`
- `references/execution-prompt.md`
- `templates/goal.md`
- `templates/GOALMAP.md`

Remove the old default runtime surface:

- lifecycle scripts
- hooks
- hash/lock scripts
- graph/ledger tooling
- campaign runtime
- auto-advance
- focus/current/rendered state
- evidence capture runtime
- custom reviewer agents
- old `.goals/current.md` templates and fixtures
- docs that frame GoalSpec as a contract compiler or automation governor

Update plugin manifests to describe GoalSpec as a portable goal-brief/map authoring skill.

## Goal Brief Format

Every executable goal uses this format:

```md
# Goal: <Outcome>

Status: pending | active | done | blocked | deferred

## Intent
Source wording:
> ...

Interpretation:
...

Interpretation Risk:
- Low/Medium/High: ...

## Done Means
- Observable user/system outcome...
- Workflow/output behavior that must be true...

## Constraints
Positive anchors that shape the work:
- Reuse/match/preserve...

## Invariants
Things that must not be violated:
- Must not...
- Existing behavior remains...

## Stop / Ask Conditions
Stop before proceeding if:
- Interpretation Risk is High and the missing decision affects product shape.
- A constraint conflicts with a Done Means item.
- The goal cannot be completed without violating an invariant.

## Evidence Recipe
A reviewer or fresh agent can confirm each Done Means item, including the highest-risk one, by:
- Run/check/review <specific command, workflow, artifact, or source-grounded review>.
- Expected result: <observable result>.

## Completion Notes
Filled only after execution:
- What changed:
- Evidence produced:
- Remaining risks:
```

Required semantics:

- `Done Means` is the real acceptance surface.
- `Evidence Recipe` must demonstrate the Done Means, not an easier adjacent claim.
- If a Done Means item, especially the highest-risk one, has no reproducible check, say so explicitly and route it to Stop / Ask or Remaining Risks.
- `Constraints` are positive anchors: reuse this, preserve this shape, match this pattern.
- `Invariants` are prohibitions or preserved truths: do not break this, do not introduce that.
- Avoid a default “Non-Goals” section. Use scope wording or follow-up notes only when needed.

## GoalMap Format

For large PRDs, roadmaps, or multi-goal work, create:

- `context/goals/GOALMAP.md`
- child goal briefs under `context/goals/`

`GOALMAP.md` contains:

- product loop or north-star outcome
- inherited global constraints and invariants
- stable source anchors using source identifiers plus quoted text, not brittle file-line dependence
- child goal status table
- final validation goal when the work is multi-goal or integration-sensitive
- launch-ready handoff prompt

If an existing roadmap or PRD already has structure, reuse it. Do not invent a parallel taxonomy. Do not create one mega-goal with thin children. Every child goal uses the same rich brief format.

## Execution Handoff

Default map handoff prompt:

```text
/goal Read context/goals/GOALMAP.md, its product loop, global constraints, and global invariants. Work the goals one at a time in status order. For each goal, read the brief. If Interpretation Risk is High or any Stop / Ask Condition is met, stop and ask before proceeding; do not guess to maintain momentum. Otherwise do the work needed to satisfy Done Means while preserving Constraints and Invariants. Record Evidence as a reproducible recipe: exact command/workflow/artifact/source review plus expected result a reviewer can re-run or inspect. The Evidence Recipe must confirm each Done Means item, including the highest-risk one, not an easier adjacent claim. Update Status and Completion Notes as bookkeeping only. When all implementation goals are done, run the final validation goal and present its evidence recipe/results plus the status table for acceptance; do not self-close the map.
```

For standalone goals, emit a shorter version pointing directly at the goal brief.

## Evidence Guidance

Use the strongest applicable evidence without universalizing coding tests:

- User-facing workflow: e2e or integration proof when practical.
- CLI/API/public interface: representative real invocation.
- Core logic: automated tests for representative success and failure paths.
- Data/artifact transformation: parser or consumer validation plus source preservation check.
- Non-code/policy/research/planning: source-grounded review, decision record, artifact walkthrough, or stakeholder acceptance criteria.

Evidence is not the authority. The real question is whether the Done Means are met.

## Implementation Changes

- Rewrite GoalSpec docs around “planning kernel,” “goal brief,” “goal map,” “done means,” “constraints,” “invariants,” and “evidence recipe.”
- Remove legacy terminology from the default surface:
  - contract compiler
  - verifier as oracle
  - lock
  - hash
  - auto-advance
  - campaign runtime
  - current/focus/rendered state
  - lifecycle authority
- Keep old terms only in `anti-patterns.md` where useful.
- Replace examples with three canonical cases:
  - short vague prompt
  - structured output task
  - large PRD/roadmap decomposition
- Ensure examples demonstrate:
  - source quotes
  - interpretation risk
  - done-means phrased as outcomes
  - positive constraints
  - negative invariants
  - stop/ask triggers
  - evidence recipes tied to done-means
  - launch-ready handoff text

## Test Plan

- Package-shape tests:
  - manifests load
  - expected docs/templates exist
  - legacy runtime files are absent from default package
  - plugin description no longer advertises locks, hooks, campaigns, evidence capture, or automation governance
- Example-quality tests:
  - examples use outcome wording, not implementation-step wording
  - every example has source wording, interpretation risk, done-means, constraints, invariants, stop/ask, and evidence recipe
  - evidence recipes explicitly bind to Done Means
  - status is described as bookkeeping only
- Behavioral A/B before declaring success:
  - V1 vs V2 vs raw/no-system
  - cases: vague prompt, structured output, PRD/roadmap
  - primary score: final product outcome quality
  - secondary score: intent preservation and auditability
- Portability checks:
  - GoalSpec smoke test
  - Codex/Claude plugin roundtrips
  - plugin validation for both hosts
  - `just test-plugin-port`
  - `git diff --check`

## Assumptions

- V2 is a hard break from the current GoalSpec runtime model.
- No CLI ships by default.
- No hooks, lock files, graph state, auto-advance, custom agents, or evidence runtime remain in the default product.
- The default system is markdown-first and agent-judgment-first.
- Poka-yoke lives in the bindings:
  - Interpretation Risk binds to Stop / Ask.
  - Constraints bind product shape.
  - Invariants bind safety/preservation.
  - Evidence Recipe binds directly to Done Means.
- GoalSpec’s goal is not to mechanically prove execution truth. Its goal is to make the next agent start with the right intent, boundaries, and proof expectations.
