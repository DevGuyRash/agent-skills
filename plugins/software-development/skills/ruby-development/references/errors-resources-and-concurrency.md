# Errors, Resources, and Concurrency

Read this reference for exceptions, cleanup, transactions, threads, processes, Fibers, Ractors, or long-running workers.

## Keep rescue boundaries narrow

A rescue without an explicit class handles `StandardError`, not every `Exception`. Do not broaden it casually: process termination, interrupts, and other exceptional conditions need to propagate unless a top-level runtime boundary explicitly owns them.

- Rescue only failures the boundary can recover from, translate, retry, or report once.
- Preserve the original cause when raising a domain exception.
- Use `ensure` for unconditional cleanup and `else` for success-only work when it clarifies scope.
- Bound retries by attempt, time, idempotency, and backoff policy; do not use unbounded `retry`.
- Avoid rescuing and silently returning `nil` when callers need to distinguish absence from failure.

Exception class, timing, and sometimes message are observable contracts.

## Make ownership explicit

Use block forms for owned files, locks, temporary directories, database transactions, and APIs that guarantee release. Use `ensure` when no block API exists. Do not close caller-owned I/O or commit/rollback a transaction owned by another layer.

Long-running processes amplify leaked connections, subscriptions, threads, and class-level state. Verify both normal and exceptional shutdown paths.

## Preserve the concurrency model

Threads, processes, Fibers, schedulers, Ractors, and framework job systems have different sharing and lifecycle rules. Identify the project-selected model and the owner of startup, cancellation, backpressure, and shutdown before changing it.

- Do not treat an implementation's global lock as a complete synchronization guarantee.
- Protect shared mutable state or isolate it; account for callbacks that can interleave.
- Keep blocking work out of scheduler-sensitive paths unless explicitly delegated.
- Join, stop, or transfer ownership of started work; avoid orphan threads and child processes.
- Propagate worker failures through the framework's expected channel.
- Treat Ractor shareability and framework support as compatibility constraints, not a default architecture.

For subprocesses, pass command and arguments through a direct-execution API when possible. Define environment, working directory, timeout, exit status, stdout/stderr, signal, and cleanup behavior rather than relying on success-looking output.
