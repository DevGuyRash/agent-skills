# Errors, Resources, and Concurrency

Read this reference for exception handling, resource ownership, subprocesses, threads, processes, async code, cancellation, or task lifetimes.

## Keep exception boundaries meaningful

- Catch the narrowest exceptions the boundary can handle.
- Translate exceptions only when the receiving layer needs a stable domain error; preserve the cause with explicit chaining where useful.
- Let cancellation, termination, and programmer defects propagate unless the boundary has a documented responsibility.
- Use `finally` for unconditional cleanup and `else` when success-only work should remain outside the protected block.
- Avoid bare `except`, silent swallowing, and logging the same failure at every layer.

Exception messages are diagnostics, not always stable API. Exception types and timing may be public contracts.

## Make resource ownership explicit

Prefer context managers for owned files, sockets, transactions, locks, temporary directories, and similar resources. Do not close resources borrowed from callers. For multiple dynamic resources, use an exit stack consistent with project compatibility.

Generators and lazy iterators defer work and errors; preserve their consumption and cleanup semantics when refactoring. Ensure partially initialized resources are cleaned up on failure.

## Preserve the concurrency model

Do not mix sync, threads, processes, async, or framework schedulers casually. Determine which layer owns the executor, event loop, task group, shutdown, and backpressure policy.

For async work:

- Do not call blocking I/O or CPU-heavy work on the event-loop thread without an intentional offload.
- Await or otherwise retain responsibility for created tasks; avoid orphaned background work.
- Treat cancellation as control flow, perform bounded cleanup, and propagate it unless the contract says otherwise.
- Use concurrency limits and timeouts at the boundary that knows the resource budget.
- Preserve context propagation and framework lifecycle hooks.

For threads and processes, account for shared-state synchronization, pickling/start-method constraints, shutdown, exception delivery, and platform differences. The GIL is not a substitute for a data-race or lifecycle analysis.

## Run subprocesses as typed boundaries

Prefer argument sequences and `shell=False` when invoking a program directly. If shell syntax is genuinely required, make the shell and quoting contract explicit. Define expected exit codes, timeout, working directory, environment inheritance, encoding, and stdout/stderr handling. Never treat captured output as proof of success without checking process status.
