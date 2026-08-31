# Go Errors and Concurrency

## Keep errors inspectable

- Return errors for failures callers can reasonably handle. Reserve `panic` for unrecoverable initialization, violated internal invariants, or APIs whose established contract requires it.
- Preserve error identity with `%w` when callers should be able to use `errors.Is` or `errors.As`; use `%v` when intentionally hiding the underlying identity.
- Treat exported sentinel errors and concrete error types as API. Changing wrapping, identity, comparability, or fields can break callers.
- Add operation or resource context once, near the boundary where it becomes useful. Avoid repetitive wrappers that obscure the causal chain.
- Do not match error strings when an identity, type, or stable predicate exists.
- Handle an error once: recover, translate, or propagate it. Log-and-return usually duplicates reporting at another layer.
- Keep cleanup reliable with `defer`; preserve the primary failure when cleanup also fails according to the repository's policy.

## Propagate context intentionally

- Accept `context.Context` as the first parameter for request-scoped work; do not pass `nil`.
- Propagate deadlines, cancellation, and request-scoped values rather than replacing a caller's context without reason.
- Call the returned cancel function when creating a derived context, unless ownership is explicitly transferred.
- Do not store contexts in structs or use them as optional-argument bags without a framework-specific contract that justifies it.
- Check cancellation at blocking or long-running boundaries. Preserve meaningful cancellation and deadline errors.

## Own concurrent work

- Give every goroutine an owner, termination condition, and observed outcome. A fire-and-forget goroutine is a resource and error-lifecycle decision.
- Cancellation is a signal, not a join. When cleanup or observable effects depend on completion, the owner must wait for every started goroutine and observe its outcome before releasing shared state.
- Establish who closes a channel. Normally the sending owner closes it; receivers must not close a channel merely to stop producers.
- Account for nil channels, closed-channel zero values, buffered capacity, and select fairness when they affect behavior.
- Prefer direct synchronous code until concurrency provides a concrete latency, throughput, or isolation benefit.
- Bound fan-out, queues, retries, and background work. Propagate shutdown rather than leaking goroutines.
- Use `sync.Mutex`, atomics, channels, or immutable handoff according to the state transition; none is universally superior.
- Remember that map access and compound read-modify-write operations require synchronization when shared.
- Keep lock scope and order explicit. Do not call unknown or blocking code while holding a lock unless the contract requires it.
- Goroutine return alone establishes no happens-before relation with another goroutine; use the synchronization event that publishes completion and the state being observed.

## Diagnose concurrent failures

- Reproduce under the repository's supported race detector when available, but do not treat a clean race run as proof of correctness.
- Check goroutine dumps, cancellation paths, channel ownership, queue bounds, and waits before adding sleeps or retries.
- In tests, synchronize on observable events rather than timing guesses.
- Preserve scheduler independence; do not rely on goroutine execution order unless synchronization establishes it.

## Reject overbroad rules

- Do not ban all `panic`, require channels for every coordination problem, or require a goroutine per request.
- Do not add `errgroup`, worker pools, atomics, or context parameters merely to appear idiomatic.
- Do not convert deliberate synchronous APIs into asynchronous ones without an end-to-end lifecycle contract.

Primary references: [`errors` package](https://pkg.go.dev/errors), [`context` package](https://pkg.go.dev/context), [memory model](https://go.dev/ref/mem), [race detector](https://go.dev/doc/articles/race_detector).
