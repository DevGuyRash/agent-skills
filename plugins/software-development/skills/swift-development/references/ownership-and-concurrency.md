# Swift Ownership and Concurrency

Read this reference for ARC, escaping closures, retained work, value/reference decisions, async/await, actors, continuations, cancellation, or sendability/isolation diagnostics.

## Value and reference lifetime

Use a value type when copies should behave as independent values. Account for copy-on-write storage and nested reference members rather than assuming every struct is deeply independent. Use a class or actor when stable identity and shared lifecycle are intended.

For escaping closures, identify captured objects, capture strength, release point, and execution context. A weak capture introduces optional absence; an unowned capture traps if its lifetime proof is wrong. Choose from the real lifecycle and handle the resulting state. Break cycles at the ownership edge that should not retain, rather than applying weak captures mechanically.

## Structured task ownership

Prefer child tasks when work belongs to a scope and its result/failure should be observed there. Unstructured or detached tasks require an explicit owner, cancellation path, priority/task-local decision, and error-reporting destination. Do not create a task solely to escape actor isolation or suppress a compiler error.

Cancellation is cooperative. Define which effects may have occurred before cancellation, whether cleanup is required, and how cancellation propagates to child or wrapped operations. A timeout or canceled waiter does not prove independently owned work stopped.

## Actor isolation and sendability

State which actor or synchronization boundary owns mutable state. Avoid unnecessary actor hops, but do not use nonisolated or unsafe annotations to bypass a real data race. Treat a `Sendable` conformance as a claim about safe transfer under the repository's language mode and compiler checks. Use `@unchecked Sendable` only with a documented synchronization/immutability invariant that all safe APIs preserve.

Review values live across suspension, callback execution context, global/main-actor requirements, and reentrancy after each await. Actor isolation prevents simultaneous unsynchronized access; it does not make a multi-await transaction atomic.

## Continuations and bridging

Resume checked continuations exactly once on every completion path and never retain them indefinitely. Define cancellation and late-callback behavior when bridging callback APIs. Preserve executor/actor expectations when a foreign or legacy API chooses the callback thread.

## Verification

Use deterministic task coordination instead of sleep-based assertions. Test cancellation at multiple progress points, retained captures and deallocation, callback duplication/omission, actor reentrancy, task failure, and shutdown. Run the repository's selected strict-concurrency diagnostics without upgrading its language mode implicitly.

Primary anchors: [The Swift Programming Language](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/), [Swift concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/), and accepted [Swift Evolution proposals](https://www.swift.org/swift-evolution/).
