---
name: refactoring
description: Use for nontrivial restructuring when declared behavior stays unchanged. Covers baselines, modularity, cohesion, and duplication; exclude features, fixes, migrations, and tuning.
---

# Refactoring

Improve internal structure without changing the behavior that matters to users,
consumers, or operators. Make the preservation boundary explicit so “cleanup”
does not silently become a feature, fix, or migration.

## Define what must stay stable

Inspect the repository and name the observable surfaces relevant to the change:

- public APIs and supported call patterns;
- outputs, errors, exit status, ordering, and side effects;
- serialized data, persisted state, protocols, and generated artifacts;
- contractual timing, concurrency, or resource behavior;
- extension points and downstream consumers known to the repository.

Do not preserve every accidental quirk by default. Distinguish declared or
relied-upon behavior from an assumption, suspected bug, or intentionally allowed
change. Read [preservation-surfaces.md](<skills-file-root>/references/preservation-surfaces.md) when
the boundary includes published interfaces, data, concurrency, or side effects.

## Establish a baseline

Use existing tests and the smallest relevant build, type, lint, or behavior
checks. When important behavior lacks coverage, add characterization evidence
that passes on the current implementation before restructuring. Record any
surface that cannot be verified.

A passing characterization baseline is correct for refactoring. Do not alter
the code or expectation merely to manufacture a test-driven failure.

## Choose a coherent transformation

State the structural problem and the intended improvement: for example,
separating responsibilities, removing duplication, clarifying data flow,
shrinking coupling, or creating a stable seam. Prefer a change that can be
reviewed and reversed independently.

Use repository and language idioms. Do not introduce a design pattern,
abstraction, dependency, class, or new file merely to display modularity. A
smaller or more local solution is often the better refactor.

## Transform under evidence

1. Make one meaningful structural change.
2. Run the narrowest checks that can detect drift at its preservation boundary.
3. Inspect the diff for accidental behavior, formatting, generated-file, or
   dependency changes.
4. Continue while the next step advances the stated structural objective and
   remains within scope.

Automated rename, move, extraction, and inline tools are useful when their
semantic model matches the language and repository. Verify their result; tool
success is not evidence that reflective lookups, configuration, serialization,
or external consumers remained compatible.

## Control scope

Keep large mechanical changes separate from semantic restructuring when that
makes review and rollback clearer. Small local cleanup may remain with a nearby
behavior change when it does not obscure the behavioral diff.

Stop and reclassify the work when the desired result requires changing a public
contract, fixing behavior, altering performance as an acceptance criterion, or
running old and new representations through a transition.

## Compose with neighboring skills

- Use test-driven development for explicit new or corrected behavior, not for a
  behavior-neutral baseline.
- Let behavior-preserving migration own compatibility windows, coexistence,
  cutover, rollback, and retirement across version or representation boundaries.
- Let performance engineering lead when a measured performance result is the
  objective; a structural change may be its implementation.
- Let trunk-based development split a large refactor into independently safe
  integrations. Repository Git and review tooling execute those integrations.
- Let language and framework skills supply semantic refactoring constraints.

## Completion evidence

Claim the refactor complete only when:

- the structural objective is achieved without unrelated redesign;
- the declared behavior surfaces have equivalent before-and-after evidence;
- relevant checks pass and the diff contains no unexplained behavior change;
- unverified surfaces, downstream coordination, and follow-up work are explicit.

Do not mandate SOLID rewrites, universal file or line limits, separate pull
requests for every cleanup, whole-repository consistency work, or abstraction
for its own sake. Treat KISS, DRY, YAGNI, and SOLID as questions about the
current change: prefer the simplest sufficient design, remove duplication only
when one authority safely serves the consumers, defer unsupported extension
points, and apply responsibility/dependency heuristics only where they reduce a
demonstrated coupling problem. Incidental similarity does not require a shared
abstraction.
