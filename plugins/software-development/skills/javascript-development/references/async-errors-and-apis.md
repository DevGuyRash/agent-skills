# JavaScript Async, Errors, and APIs

Load this reference for promises, events, cancellation, concurrency, resource lifetime, or public failure behavior.

## Promises and Concurrency

- Return or await promises along every relevant path. If work is intentionally detached, attach rejection handling and expose failure through the repository's logging or supervision mechanism.
- Use sequential awaiting when order, dependency, resource bounds, or failure cutoff requires it.
- Use concurrent aggregation only for independent work. Know whether fail-fast behavior, all outcomes, or first success matches the contract.
- Bound fan-out when input size is not tightly bounded.
- Avoid `async` promise constructors and unnecessary promise wrapping; connect completion and failure directly.
- Preserve the difference between synchronous throws and asynchronous rejection when callers can observe it.

## Cancellation and Cleanup

- Propagate an existing `AbortSignal` rather than inventing an incompatible cancellation channel.
- Check cancellation at meaningful boundaries and remove abort listeners after settlement.
- Clean up timers, subscriptions, event listeners, streams, locks, and acquired resources through the API's supported lifecycle.
- Make timeout behavior distinguishable from cancellation and underlying failure when recovery differs.
- Avoid races between completion, cancellation, and cleanup by making settlement ownership explicit.

## Errors

- Throw `Error` instances or repository-defined error types, not bare strings.
- Preserve the original error as `cause` when adding actionable context and the supported runtime allows it.
- Do not catch merely to log and rethrow if that duplicates reporting or leaks sensitive data.
- Catch at a boundary that can recover, translate, add context, or guarantee cleanup.
- Use stable error classes or codes for machine decisions when the existing API supports them; do not make new callers parse prose.

## API Contracts

- Define whether callbacks can run synchronously, once, repeatedly, or after disposal.
- Keep event names, payload shapes, return values, error modes, and ordering stable unless the task changes the contract.
- Validate untrusted data at the boundary where assumptions become program invariants.
- Avoid boolean-heavy signatures when callers cannot tell what each flag means; follow established API style before introducing an options object.
- Document only constraints that callers cannot infer from types, names, and ordinary behavior.

For host-specific event-loop, stream, process, or filesystem behavior, compose with the appropriate runtime skill rather than encoding it here.
