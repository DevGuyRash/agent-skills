---
name: concurrency-engineering
description: Use when task, thread, actor, worker, callback, cancellation, backpressure, synchronization, or parallel-execution contracts materially shape software behavior. Compose with language/runtime and performance skills; exclude trivial async syntax and Rust-runtime work owned by async-rust.
---

# Concurrency Engineering

Design concurrent work as an ownership and lifecycle contract. Make admission, progress, failure, cancellation, pressure, and terminal completion observable without imposing one language, runtime, scheduler, or synchronization primitive.

## Compose at the executable boundary

- Add the language and runtime skills that own actual task, thread, process, event-loop, actor, channel, lock, or memory-model semantics.
- Let `async-rust` own Rust async runtime and future-specific work; use this skill with it only when a cross-language or architecture-wide concurrency contract also needs one owner.
- Add `performance-engineering` when parallelism, worker count, latency, throughput, or resource use is an acceptance criterion. Concurrency can improve throughput or responsiveness, but concurrent syntax is not performance evidence.
- Let `systematic-debugging` lead while the cause of a race, hang, starvation, or slowdown is unknown.

Do not activate this skill for an isolated `async` function, ordinary promise return, or thread-safe collection use when no material lifecycle, pressure, synchronization, or parallel-execution decision changes.

## Define the concurrent contract

Before changing implementation, establish:

- which operation owns each task, thread, worker, callback registration, queue, or subprocess;
- when work becomes admitted or externally visible and the maximum in-flight or retained work;
- result ordering, partial progress, failure aggregation or cutoff, and retry behavior;
- cancellation sources, what actually makes work stop, and which terminal outcome has precedence;
- synchronization, isolation, memory visibility, reentrancy, and blocking constraints supplied by the selected platform;
- the terminal boundary after which captured state and dependent resources may be released.

Keep detached work only when another explicit supervisor owns its lifetime and outcome.

## Load only the relevant detail

| Situation | Read |
| --- | --- |
| Task ownership, cancellation, timeouts, cleanup, callbacks, subprocesses, or shutdown | `<skills-file-root>/references/lifecycle-and-cancellation.md` |
| Queues, channels, streams, admission, backpressure, shared state, locks, actors, or deadlock | `<skills-file-root>/references/pressure-and-coordination.md` |
| Parallel algorithms, worker sizing, fairness, deterministic tests, races, or liveness evidence | `<skills-file-root>/references/parallelism-and-verification.md` |

Load the smallest set that owns the live decision.

## Preserve terminal ownership

Admit work before invoking an operation that starts eagerly. When cancellation, timeout, shutdown, or failure occurs, stop new admission, issue the operation-specific unblock or cancellation action, observe every admitted outcome, and join or otherwise terminalize owned execution before releasing state it can reach. Cancellation request, caller wakeup, direct-child exit, pipe closure, and task-handle drop are not interchangeable with terminal completion.

Define primary and secondary failure precedence rather than letting race timing select it. Preserve exact reason, status, or error identity when the public contract requires it, while retaining cleanup failures through an explicit secondary channel.

## Bound pressure and parallelism

Select buffering, blocking/backpressure, dropping, coalescing, rejection, or load shedding from the product contract. Bound both executing and queued work; a worker limit applied after promises, tasks, or requests have already started does not control admission.

Scale parallel work only while representative evidence shows useful improvement within CPU, memory, I/O, connection, downstream, ordering, and failure guardrails. Budget nested pools and fan-out together.

## Verify behavior, not timing luck

Use barriers, handshakes, controlled executors, virtual time, model checking, race detectors, or platform-native test facilities when available. Prove the intended ordering or bound directly; sleeps and one clean stress run are weak evidence. Cover cancellation before admission, during execution, and during cleanup; early consumer exit; failure while producers or submitters are blocked; duplicate or late callbacks; and terminal absence of owned work.

## Completion evidence

Report the ownership and admission model, pressure policy, failure/cancellation precedence, terminal boundary, platform contract used, checks run, and any scheduler, load, target, or liveness horizon not exercised. Do not claim race freedom, fairness, deadlock freedom, or scalability beyond the evidence and platform guarantees.
