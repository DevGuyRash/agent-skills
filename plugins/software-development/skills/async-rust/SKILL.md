---
name: async-rust
description: Use for Rust async runtimes, task lifecycles, cancellation, backpressure, Send boundaries, or pinning. Always compose with rust-development; exclude synchronous-only work.
---

# Async Rust

Design and verify asynchronous Rust whose lifecycle, cancellation, and resource behavior remain correct under interleaving.
Always use this skill with `$rust-development`; this specialist does not replace ordinary Rust API and Cargo guidance.

## Establish the async contract

Inspect the repository before changing code. Determine:

- runtime and version, executor topology, enabled features, and test support;
- whether futures must be `Send`, may remain local, or cross task/thread boundaries;
- ownership of spawned tasks and the shutdown or cancellation contract;
- concurrency and backpressure limits;
- timeout, retry, ordering, and partial-progress semantics;
- which operations are blocking, cancellation-safe, or externally side-effecting.

Preserve the selected runtime and abstractions unless the request explicitly changes them.
Do not introduce a second runtime or replace runtime primitives for personal preference.

## Load detail only when needed

| Situation | Read |
| --- | --- |
| Using `select`, timeouts, retries, spawned work, streams, bounded queues, or graceful shutdown | `<skills-file-root>/references/cancellation-and-lifecycle.md` |
| Resolving `Send`/`'static` failures, isolating blocking work, choosing runtime boundaries, or writing async tests | `<skills-file-root>/references/send-runtime-and-tests.md` |

Load only the reference that owns the current decision.

## Model progress and ownership

Make the unit of work and its owner explicit.
Prefer scoped or supervised tasks when a caller must observe completion or failure.
Detach work only when independence, error reporting, and shutdown behavior are deliberate.
Retain join handles or cancellation tokens when the lifecycle requires control.

Use bounded concurrency when input can outrun downstream work.
Choose buffering from an explicit throughput and memory contract, not an arbitrary large capacity.
Avoid holding a synchronous lock guard across `.await` unless that guard and critical section are designed for it.

## Treat every await as an interruption point

At each `.await`, identify state already mutated, resources held, and externally visible effects.
Assume the future may be dropped there unless its owner proves otherwise.
Keep multi-step state transitions restartable, guarded, or completed by an owner that outlives the waiting future.

Do not assume a timeout stops the underlying operation.
Do not retry a non-idempotent operation without a deduplication or reconciliation contract.
Preserve errors from spawned work instead of logging and forgetting them by default.

## Keep blocking work off constrained executors

Classify filesystem, DNS, compression, foreign calls, CPU-heavy loops, and synchronization by the runtime and platform actually used.
Move genuinely blocking or CPU-heavy work through the repository's established blocking boundary.
Do not wrap an operation in async syntax and assume it became nonblocking.

## Preserve async interfaces

Avoid async traits, boxed futures, pinning, or streams unless the caller needs that abstraction.
Keep borrowing futures local when possible; require `'static` only at boundaries that retain the future.
Treat changes to `Send`, `Sync`, cancellation, ordering, buffering, and wake behavior as API changes.

## Verify concurrency behavior

Run the repository's targeted Rust checks and async tests.
Prefer deterministic coordination, paused/controlled time when the runtime supports it, and bounded timeouts at the test harness edge.
Avoid sleep-based correctness assertions and unbounded waits.

Exercise cancellation before progress, cancellation after partial progress, task failure, shutdown with work in flight, capacity exhaustion, and the required ordering semantics.
Use concurrency-model tools only where configured and applicable; their clean result is evidence, not proof for every schedule.

## Completion

Report the runtime contract preserved, task ownership, cancellation points, backpressure behavior, checks run, and any schedule or platform surface left unverified.
