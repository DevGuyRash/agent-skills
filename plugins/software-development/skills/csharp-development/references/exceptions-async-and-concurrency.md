# C# Exceptions, Async, and Concurrency

## Preserve failure and resource contracts

- Catch only exceptions the boundary can recover from, translate, or report. Broad application boundaries may catch `Exception`; ordinary library flow should not hide unknown failures.
- Preserve stack traces with `throw;` when rethrowing the current exception; `throw ex;` resets the apparent origin.
- Preserve the original exception as `InnerException` when translating and keep stable public exception behavior when callers depend on it.
- Use exception filters when they clarify a recovery condition without mutating state during selection.
- Dispose only resources the component owns. Use `using`/`await using` according to `IDisposable`/`IAsyncDisposable` lifetime and preserve the primary failure if cleanup also fails.
- Do not use finalizers as ordinary deterministic cleanup.

## Keep async APIs truthful

- Return `Task` or `Task<T>` for asynchronous work. Reserve `async void` for event-handler contracts where the caller cannot await.
- Avoid sync-over-async with `.Result`, `.Wait()`, or blocking waits when an async path can propagate; it can deadlock or exhaust threads depending on context.
- Use `ValueTask` only when repository/API constraints justify its consumption rules and measured allocation benefit.
- Observe every task's completion or assign it to an explicit supervised lifetime. Discarded tasks lose failures and ownership.
- Preserve the repository's synchronization-context policy. Do not mandate `ConfigureAwait(false)` everywhere or remove it mechanically.
- Keep blocking work and CPU work on execution mechanisms appropriate to the environment; `Task.Run` is not a universal async adapter.

## Propagate cancellation deliberately

- Accept and pass `CancellationToken` where the operation is meaningfully cancellable; do not invent tokens that no underlying work observes.
- Preserve the distinction among caller cancellation, timeout, and operation failure.
- Check cancellation at suitable boundaries and clean up registrations, timers, and partial state.
- Do not catch and convert `OperationCanceledException` into success unless the public contract explicitly defines that outcome.
- Bound retries and ensure side effects are safe before repeating a canceled or failed operation.

## Synchronize shared state

- Establish one coherent policy using `lock`, monitor primitives, semaphores, immutable handoff, atomics, channels, or concurrent collections.
- `volatile` and atomic reads/writes do not make a multi-step invariant atomic.
- Use concurrent collections for documented atomic operations; sequences of operations may still need coordination.
- Keep lock ordering and scope explicit. Avoid awaiting while holding a synchronous lock.
- Account for reentrancy, callbacks, cancellation, and disposal when holding or releasing synchronization primitives.
- Give background workers, channels, timers, and parallel loops bounded lifetime, shutdown, backpressure, and observed failure.

## Reject overbroad rules

- Do not make every method async, every result a `ValueTask`, or every collection concurrent.
- Do not require `ConfigureAwait(false)`, channels, immutable state, reactive streams, or one synchronization primitive everywhere.
- Do not ban all broad catches, locks, blocking calls, or fire-and-forget event handlers without considering the actual boundary.

Primary references: [exception guidance](https://learn.microsoft.com/dotnet/standard/exceptions/best-practices-for-exceptions), [async return types](https://learn.microsoft.com/dotnet/csharp/asynchronous-programming/async-return-types), [cancellation](https://learn.microsoft.com/dotnet/standard/threading/cancellation-in-managed-threads), [managed threading](https://learn.microsoft.com/dotnet/standard/threading/managed-threading-basics).
