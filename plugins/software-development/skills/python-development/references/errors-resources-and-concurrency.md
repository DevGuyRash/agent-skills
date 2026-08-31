# Errors, Resources, and Concurrency

Read this reference for exception handling, resource ownership, subprocesses, threads, processes, async code, cancellation, or task lifetimes.

## Keep exception boundaries meaningful

- Catch the narrowest exceptions the boundary can handle.
- Translate exceptions only when the receiving layer needs a stable domain error; preserve the cause with explicit chaining where useful.
- Let cancellation, termination, and programmer defects propagate unless the boundary has a documented responsibility.
- Use `finally` for unconditional cleanup and `else` when success-only work should remain outside the protected block.
- Avoid bare `except`, silent swallowing, and logging the same failure at every layer.

Exception messages are diagnostics, not always stable API. Exception types and timing may be public contracts.

When concurrent work can fail more than once, preserve the repository's aggregation contract rather than silently selecting the first or last failure. Account for the minimum interpreter before using exception-group syntax or APIs.

## Make resource ownership explicit

Prefer context managers for owned files, sockets, transactions, locks, temporary directories, and similar resources. Do not close resources borrowed from callers. For multiple dynamic resources, use an exit stack consistent with project compatibility.

Generators and lazy iterators defer work and errors; preserve their consumption and cleanup semantics when refactoring. Ensure partially initialized resources are cleaned up on failure.

Acquisition and release form one protocol. If cleanup is asynchronous or can itself fail or be cancelled, retain its handle, drive it to a terminal state within the owning boundary, and preserve the primary failure according to the public contract. Garbage collection and interpreter shutdown are not deterministic resource owners.

## Preserve the concurrency model

Do not mix sync, threads, processes, async, or framework schedulers casually. Determine which layer owns the executor, event loop, task group, shutdown, and backpressure policy.

For async work:

- Do not call blocking I/O or CPU-heavy work on the event-loop thread without an intentional offload.
- Await or otherwise retain responsibility for every created task through success, failure, or cancellation; structured scopes are preferred when the supported runtime and framework provide them.
- Treat cancellation as a delivered request, not terminal evidence. Perform bounded cleanup, settle owned children, and propagate cancellation unless the contract explicitly transforms it. Shielding changes cancellation delivery; it does not transfer ownership or settle the protected task.
- Place concurrency limits, queue capacity, and timeouts at the boundary that owns the constrained resource. Include every buffering stage when deriving the real in-flight bound.
- Preserve context propagation and framework lifecycle hooks.

For threads, processes, interpreters, and executors, account for shared-state synchronization, serialization/start-method constraints, shutdown, exception delivery, and platform differences. Do not rely on the GIL, incidental bytecode atomicity, or built-in container locking as a synchronization or memory-ordering contract. Avoid wait-for cycles such as work occupying a bounded executor while waiting for work queued to that same executor. Cancelling a future or async waiter may not stop already-running thread or process work; the owner still needs a terminal settlement policy.

Treat queues and worker pools as protocols, not containers. Define capacity, producer completion, consumer termination, failure propagation, task accounting, and the owner of every join. Terminal signaling must remain deliverable under full-capacity and failure conditions; a sentinel per consumer is only one possible design.

## Run subprocesses as typed boundaries

Prefer argument sequences and `shell=False` when invoking a program directly. If shell syntax is genuinely required, make the shell and quoting contract explicit. Define expected exit codes, timeout, working directory, environment inheritance, encoding, and stdout/stderr handling. Captured pipes are bounded queues: drain all owned streams concurrently or use a repository-appropriate communication primitive. On timeout or cancellation, request termination as required, finish draining, reap the process, and then report the terminal outcome. Never treat captured output, a sent signal, or a timeout exception as proof that the process has exited.

When the contract owns a POSIX process group or another descendant boundary, direct-child exit and pipe EOF do not prove that boundary is empty: descendants can close inherited descriptors and keep executing. Retain valid termination authority through the grace interval, apply the declared escalation independently of direct-child communication settlement, and avoid signaling a recycled group identifier after authority is lost.
