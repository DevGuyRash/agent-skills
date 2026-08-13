# Java Errors and Concurrency

## Preserve exception contracts

- Follow the existing API's checked-versus-unchecked policy. Changing a checked exception, runtime type, wrapping layer, or declared signature can break consumers.
- Catch only exceptions the boundary can recover from, translate, or enrich. Do not catch `Throwable` in ordinary application or library flow.
- Preserve the cause when translating with an exception constructor that accepts it.
- Use try-with-resources for owned `AutoCloseable` values when it matches the lifetime. Inspect suppressed exceptions when cleanup competes with a primary failure.
- Do not swallow failures or log-and-rethrow at every layer; choose the boundary that owns reporting.
- Keep messages useful but do not make callers parse them when a type, cause, or stable field can carry the contract.

## Respect interruption and cancellation

- Treat `InterruptedException` as a control signal. Propagate it when the signature permits, or restore the interrupt flag when translating or terminating work.
- Do not continue a retry loop after interruption without an explicit contract.
- Give timeouts a unit, clock assumption, and cleanup path. Preserve the distinction among timeout, cancellation, interruption, and operation failure.
- When composing futures, decide which executor runs each stage and how cancellation and exceptional completion propagate.

## Apply the Java Memory Model

- Establish a happens-before relationship for shared mutable state using synchronization, locks, volatile publication, atomics, concurrent collections, or task handoff.
- `volatile` supplies visibility and ordering for the variable; it does not make a multi-step state transition atomic.
- Keep invariants protected by one coherent synchronization policy. Mixing locks and unsynchronized access defeats the policy.
- Avoid calling unknown, blocking, or reentrant code while holding a lock unless the contract and ordering are explicit.
- Use concurrent collections for their documented atomic operations, not as proof that multi-operation workflows are atomic.

## Own tasks and executors

- Give every submitted task an owner, bounded queue or admission policy where needed, shutdown path, and observed failure.
- Reuse repository-managed executors rather than creating an unbounded pool per call.
- Distinguish CPU-bound work from blocking work when sizing or selecting an executor.
- Observe `Future`, `CompletionStage`, or task failures; fire-and-forget is an explicit error and lifecycle policy.
- Preserve thread-local, security, logging, and request context only through mechanisms the repository already establishes.

## Treat newer concurrency features as versioned choices

- Use virtual threads for suitable blocking workloads only when the supported JDK and operational environment allow them; they do not make CPU work faster or shared state safe.
- Do not pool virtual threads reflexively or introduce them without checking pinning, thread-local, monitoring, and framework assumptions.
- Treat structured-concurrency and scoped-value APIs according to their status in the target JDK; preview APIs require explicit build and runtime enablement.
- Do not use parallel streams as a general executor abstraction.

## Reject overbroad rules

- Do not require reactive APIs, `CompletableFuture`, virtual threads, immutable data, or one concurrency library for every task.
- Do not ban synchronized blocks, locks, checked exceptions, or all broad catches; top-level containment boundaries may legitimately differ from library code.
- Do not convert synchronous public APIs to asynchronous ones without a compatible end-to-end lifecycle.

For memory-model and API details, select the specification edition matching the repository's effective target JDK. Primary references: [Java Language Specification index](https://docs.oracle.com/javase/specs/jls/), [Java API specification index](https://docs.oracle.com/en/java/javase/), and [virtual threads (JEP 444)](https://openjdk.org/jeps/444).
