---
name: trunk-based-development
description: Use when integration strategy needs mergeable slices, short branches, safe incomplete work, or divergence recovery. Excludes routine Git/PR operations, CI, releases, and governance.
---

# Trunk-Based Development

Keep integration frequent by designing changes that can reach a healthy shared trunk independently. Own the integration strategy and change boundaries; defer concrete Git, hosting, CI, release, and governance operations to their owners.

## Read the repository before prescribing flow

Inspect the default branch, contribution guidance, protection and required checks, existing release model, deployment coupling, and current worktree state. Treat repository policy as authoritative. Trunk-based development is compatible with direct integration, short-lived reviewed branches, and merge queues.

Do not bypass required review, signed commits, status checks, protected branches, or user approval in the name of speed.

## Define the integration goal

State the smallest outcome that can merge while leaving trunk buildable, testable, and safe for its normal deployment model. Identify dependencies, compatibility constraints, incomplete behavior, and the evidence each increment needs before integration.

Frequent integration is the objective; daily merging and low active-branch count are useful team diagnostics, not hard timers or quotas for every repository.

## Slice the work

Prefer increments that are:

- independently buildable and testable;
- reviewable as one coherent purpose;
- backward compatible with adjacent deployed or in-flight code;
- safe to revert without removing later unrelated work;
- small enough to integrate before assumptions drift.

Read [small-batch-patterns.md](<skills-file-root>/references/small-batch-patterns.md) when a feature, refactor, or migration appears too large to merge safely in one short-lived line of work.

## Keep incomplete work safe

Choose the least costly technique that preserves normal trunk behavior:

- a compatible seam or branch-by-abstraction for structural work;
- an inactive code path or short-lived feature flag for releasable software;
- additive schema or API changes before consumer migration;
- a sequence of vertical slices when each slice can deliver usable behavior.

Give transitional code and flags an owner and removal condition. Do not require flags when an unreleased library, local tool, or simple compatible slice does not benefit from runtime gating.

## Integrate and recover deliberately

Route branch, commit, push, review, and merge operations through the repository's normal Git and hosting capabilities. Select merge, rebase, squash, or queue behavior from repository policy rather than imposing a universal history style.

When the branch has diverged, first preserve user changes and determine its dependencies. Prefer reslicing or updating against current trunk before adding more work. If integrated code breaks trunk, prioritize a small repair when it is immediately clear and verifiable; otherwise use the repository's authorized revert or containment path.

## Compose with neighboring skills

- Project Harness owns creation or repair of CI workflows and local task entry points. This skill can state the feedback needed for frequent integration.
- Git and GitHub skills own commits, branches, pushes, pull requests, review, merge queues, and remote mutations.
- Release and governance capabilities own versions, release branches, deployment, rulesets, approvals, and organization policy.
- Refactoring and behavior-preserving migration own code transformation and compatibility semantics; this skill helps slice them for integration.
- Test-driven development and language skills supply per-increment code evidence.

## Completion evidence

For planning, provide the ordered increments, dependency edges, safety mechanism for incomplete work, verification per increment, and cleanup conditions. For an executed integration, report the actual repository checks and resulting state; do not infer success from a push or merge response alone.

Do not mandate Conventional Commits, branch-name enumerations, worktrees, direct commits to trunk, squash merging, feature flags, code freezes, or release policy.
