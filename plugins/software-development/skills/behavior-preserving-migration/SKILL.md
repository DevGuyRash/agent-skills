---
name: behavior-preserving-migration
description: Use for API, schema, data, dependency, runtime, service, storage, or architecture transitions with declared compatibility, cutover, and rollback; exclude local refactors.
---

# Behavior-Preserving Migration

Move from a source implementation or representation to a target while preserving the declared compatibility envelope throughout transition and cutover. Preserve intentional contracts, not every undocumented quirk or known bug.

## Define the preservation contract

Identify the consumers and invariants that matter:

- APIs, protocols, schemas, serialized data, and supported version combinations;
- functional results, errors, ordering, side effects, and idempotency;
- data completeness, uniqueness, consistency, and authorization boundaries;
- availability, latency, capacity, and operational objectives;
- explicitly accepted behavior changes and consumers that must coordinate.

Separate facts, assumptions, proposed safeguards, and approved deltas. If the target intentionally changes behavior, keep that delta explicit and verify it as a behavior change rather than claiming complete preservation.

## Inventory the transition

Inspect source and target ownership, readers and writers, dependency direction, data volume, deployment order, rollback feasibility, and irreversible steps. Establish current contract or characterization evidence before changing either side. Name external consumers that repository tests cannot prove.

## Choose a risk-shaped path

Prefer the simplest path that meets the actual availability and rollback needs. A small offline migration may be safer than permanent dual operation; a high-risk published interface may require coexistence and staged traffic.

Read [transition-patterns.md](<skills-file-root>/references/transition-patterns.md) when choosing expand-and-contract, an adapter, strangler routing, shadow comparison, backfill, dual reads or writes, staged traffic, or an offline cutover.

## Make transition states valid

Design each intermediate state so supported old and new participants can coexist for the required window. Keep one authority for each mutable fact where possible. When replication or dual writes are unavoidable, define transaction ordering, idempotency, conflict handling, reconciliation, lag, and partial-failure recovery.

Do not assume writing source and target separately is atomic. A successful first write followed by a failed second write creates a state the plan must detect and repair.

## Migrate and compare

1. Add compatibility capacity before depending on it.
2. Move a bounded cohort, consumer, or data segment.
3. Compare semantic outputs, state, and operational signals at the declared boundary; use checksums or counts only where they prove the needed invariant.
4. Pause, repair, or roll back when a guardrail fails.
5. Expand only after the current stage's evidence supports it.

Preserve enough source state and compatibility to execute the promised rollback. When an irreversible transformation is necessary, require stronger preconditions, backup or reconstruction evidence, and explicit authority before commitment.

## Cut over and retire

Define the decision maker, readiness evidence, point of no return, rollback or forward-recovery path, and monitoring window. After cutover, prove that traffic, consumers, and data use the target as intended.

Remove the source path, adapters, flags, backfill machinery, and excess telemetry only after their dependents are absent and the rollback window has closed. Give transitional architecture an owner and cleanup condition so it does not become the permanent system accidentally.

## Compose with neighboring skills

- Let refactoring own local behavior-neutral transformations that do not require coexistence or cutover.
- Use test-driven development for approved new behavior or corrected bugs inside the migration; it does not own compatibility sequencing.
- Let trunk-based development turn the transition into independently integrable changes. Let release and deployment capabilities execute rollout policy.
- Let language, database, cloud, security, and framework skills supply mechanics and platform-specific safeguards.

## Completion evidence

Report preserved contracts, accepted deltas, migrated scope, comparison results, cutover state, rollback status, and remaining transitional components. Claim completion only when the target is authoritative, required consumers have moved, invariants hold, and cleanup is complete or deliberately scheduled with ownership.

Do not require zero downtime, strangler routing, dual writes, permanent adapters, or a universal ban on big-bang migration. Do not preserve a bug unless it is an explicit compatibility requirement, and do not infer equivalence from tests alone.
