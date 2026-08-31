# Pressure and Coordination

Load this reference for queues, channels, streams, admission, shared state, locks, actors, or deadlock concerns.

## Choose a pressure contract

Bound execution and retained waiting separately. Select blocking/backpressure, rejection, drop-newest, drop-oldest, coalescing, or load shedding from required semantics; record which items were accepted, dropped, superseded, or rejected and how callers observe that result.

A bounded buffer does not automatically slow an independent push-only producer. Connect capacity to the producer when true backpressure is required, or declare the loss policy and observe it. On failure or shutdown, close admission, unblock producers and consumers, account for queued items, and prevent new execution unless drain-by-execution is explicit.

## Coordinate shared state

Name the synchronization or isolation boundary that owns each mutable invariant. Keep critical sections narrow, but do not split an atomic decision across waits or actor reentrancy without revalidation. Avoid holding locks across unknown callbacks, blocking I/O, task joins, or cross-component calls unless the selected protocol proves the ordering safe.

Use one consistent lock order or another demonstrated deadlock-avoidance protocol when operations acquire multiple resources. Treat atomics, lock-free structures, condition variables, actors, and concurrent collections according to the chosen language/runtime memory and progress guarantees; their names do not establish compound-operation atomicity.

## Preserve wakeup and progress

Wait in the platform's required predicate loop and make state changes plus notification ordering consistent with its condition semantics. Shutdown must wake every class of waiter that can otherwise block completion. Account for starvation and fairness only when the platform promises them or the application supplies an explicit policy.

## Avoid ownership cycles

Draw which component waits for which event during cleanup. Break cycles such as join-before-close, producer-waits-for-capacity while consumer-waits-for-producer-exit, or callback-unregister waits while a callback waits for the same lock. Structured syntax does not eliminate a terminal dependency cycle.
