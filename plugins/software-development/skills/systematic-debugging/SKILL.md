---
name: systematic-debugging
description: Use for bugs, failures, crashes, hangs, unexpected output, or regressions with unknown cause. Own reproduction, hypotheses, and probes; exclude known-cause implementation.
---

# Systematic Debugging

Turn an unexplained failure into a supported causal account, then make the smallest durable correction. Preserve evidence and let each probe change what you believe; do not accumulate speculative fixes.

## Triage before diagnosis

Establish expected behavior, actual behavior, affected scope, severity, and the best-known onset. During an active incident, protect users, data, and system stability first when delay would increase harm. Rollback, isolate, shed load, or disable a path as authorized while preserving useful evidence.

Containment is not proof of root cause. Keep the temporary mitigation distinct from the later diagnosis and permanent repair.

## Build a reliable problem statement

- Capture the exact error, stack, failing assertion, or externally observable symptom without exposing credentials or unrelated private data.
- Record the relevant environment, input, frequency, and known-good comparison.
- Reproduce with the smallest faithful case when feasible.
- If the issue is intermittent, retain its signature and occurrence conditions rather than declaring it unreproducible and guessing.
- Inspect recent code, dependency, configuration, traffic, and environment changes that plausibly intersect the symptom.

## Localize the failure

Model the path from input to symptom. Compare a failing case with a nearby working case and inspect the first point where their states diverge. At component boundaries, observe what enters, what exits, and which assumptions hold; instrument only what discriminates among plausible causes.

Read [difficult-failures.md](<skills-file-root>/references/difficult-failures.md) for intermittent, concurrent, distributed, environment-specific, or cross-component failures.

## Test hypotheses

1. State a falsifiable cause or interacting causal set and the evidence that makes it plausible.
2. Choose the smallest safe observation or change that distinguishes it from the leading alternative.
3. Predict the result before running the probe.
4. Run the probe under a controlled exposure sufficient to distinguish the live alternatives.
5. Record whether the result supports, weakens, or leaves the hypothesis open.
6. Remove temporary changes or deliberately retain useful instrumentation.

Change one decision-relevant variable at a time when attribution matters. A negative result is progress when it removes a plausible cause. Revisit the system model when successive probes fail to discriminate; no fixed attempt count proves that the architecture is wrong.

For intermittent or probabilistic failures, record the attempted exposures—runs, operations, schedules, seeds, duration, or load—and what a clean result excludes. One non-occurrence is not proof of repair unless the probe is deterministically discriminating.

Continue only while a safe probe can change the next decision within scope. Stop when no such probe remains, required authority is absent, or evidence cost exceeds the task's consequence; report the blocker and the evidence needed.

## Repair the supported cause

Once evidence supports a cause strongly enough for the consequence:

- choose the narrowest correction that addresses the cause rather than merely hiding the observed symptom;
- add a regression check when it can reproduce the failure reliably and adds durable value;
- verify the original reproducer, relevant surrounding checks, and the actual user- or system-visible outcome;
- remove unsafe diagnostic artifacts and review retained telemetry for cost, sensitivity, and usefulness.

When retry, timeout, validation, or fallback is the correct response to an external condition, document the condition it handles; resilience can be a root-cause-aware repair rather than a symptom patch.

## Compose with neighboring skills

- Unknown cause takes precedence over test-driven development and performance engineering. After diagnosis, use them for a regression fix or measured optimization as appropriate.
- Incident-response guidance owns coordination, communication, and operational authority; this skill owns technical diagnosis.
- Language, framework, database, and platform skills own domain-specific tools and semantics.
- Refactoring is not a diagnostic probe unless the structural change has a specific falsifiable prediction and remains reversible.

## Stop and report

Claim resolution only when the supported cause or causal set is corrected, the original failure no longer occurs under a faithful and sufficiently discriminating exposure, and relevant regressions pass. Otherwise report the issue as mitigated, narrowed, blocked, or unverified, with:

- observations and reproduction status;
- exposure count or conditions and the detection limit of a clean run when non-occurrence is probabilistic;
- supported and rejected hypotheses;
- changes or mitigations applied;
- the remaining uncertainty and next discriminating evidence needed.

Do not require a universal four-phase ritual, exhaustive log dumps, complete source reading, a failing automated test for every repair, or root cause before an urgent safety-preserving containment action.
