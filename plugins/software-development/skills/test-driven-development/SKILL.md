---
name: test-driven-development
description: Use for changed executable behavior or a known bug when a test can show the gap. Own red, green, and cleanup; exclude unknown-cause diagnosis and behavior-neutral refactors.
---

# Test-Driven Development

Use a discriminating test to define one behavior increment, demonstrate that the current system lacks it, and keep implementation feedback short. Treat the observed failure as evidence, not as a ceremony.

## Establish the next behavior

1. Inspect the repository's existing test layout, commands, naming, and helpers.
2. Resolve the expected outcome from the governing requirement, public contract, consumer, or authorized decision when tickets, current code, tests, and documentation disagree; do not let the implementation under repair define its own oracle.
3. Express one observable outcome and the conditions under which it holds.
4. Choose the cheapest test boundary that can disprove the desired behavior.
5. Identify the production change that would make the test pass.

Prefer a stable public seam over private implementation details. Include a negative or error case when it materially distinguishes the contract, rather than satisfying a fixed test-count rule.

## Demonstrate the gap

- Add the smallest test that expresses the selected behavior.
- Run the narrowest authoritative repository command that executes it, and prove the test reaches its decisive assertion rather than merely compiling or exiting successfully.
- Confirm it fails because the behavior is absent or incorrect.
- When practical, show the test accepts a known conforming implementation and rejects the unchanged defect or a controller-independent counterexample; a red caused by setup, a test hook, or an evaluator fingerprint is not behavioral discrimination.
- Repair test setup, compilation, or environment errors before interpreting the result as a meaningful failure.
- If the test passes, determine whether the behavior already exists, the test is non-discriminating, or a different boundary is required.

Do not weaken a correct expectation merely to obtain a convenient failure.

## Satisfy the behavior

- Change production code only enough to satisfy the behavior and relevant existing contracts.
- Re-run the focused test, then the smallest relevant surrounding suite.
- Treat unrelated failures as distinct evidence; do not silently update their expectations or broaden the implementation.
- Add another behavior increment only after the current evidence is green.

## Improve under green

Refactor when the passing implementation or test contains consequential duplication, unclear intent, or avoidable coupling. Keep the behavior boundary fixed and re-run relevant checks after meaningful structural changes. It is valid to make no refactoring change.

## Select honest tests

Read [test-selection.md](<skills-file-root>/references/test-selection.md) when choosing among characterization, unit, integration, contract, property, or end-to-end tests, or when doubles and nondeterminism could make the evidence misleading.

Default to tests that:

- fail when the promised behavior breaks;
- assert outcomes rather than incidental call structure;
- remain deterministic and isolated enough for their intended test layer;
- use repository conventions instead of introducing a parallel harness.

## Compose with neighboring skills

- When a failure's cause is unknown, diagnose it with systematic debugging first. Once cause and expected correction are known, use this skill for a regression test and fix when feasible.
- For behavior-neutral restructuring, use refactoring; its baseline test should normally pass before and after the change, not be forced into a false red.
- For migrations, let behavior-preserving migration own compatibility and cutover. Use TDD only for explicit behavior deltas or isolated new behavior.
- Let language, framework, and test-domain skills supply idioms and commands.

## Handle non-TDD paths honestly

Do not delete existing work merely because a test was not written first. For generated code, exploratory spikes, unavailable automation, or already-written implementations, use the strongest feasible characterization or verification and report that the work was not test-driven. Convert durable learned behavior into regression coverage when that provides value.

## Completion evidence

Before claiming the increment complete, report:

- the behavior proved and the test boundary used;
- the observed pre-change failure and why it was relevant, or why no honest red was available;
- when claiming test-first execution, evidence that the meaningful red occurred before the production change rather than only a green final artifact;
- the focused and surrounding passing checks;
- any unverified behavior, test limitation, or intentionally deferred case.

Do not require a test for every function, universal coverage thresholds, mock-free code, pristine unrelated output, or transcript-shaped compliance.
