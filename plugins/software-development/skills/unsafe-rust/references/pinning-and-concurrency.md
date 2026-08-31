# Pinning and Unsafe Concurrency

Read this reference for pin projection, address-sensitive state, custom futures, atomics, lock-free structures, or unsafe `Send`/`Sync` implementations.

## Pinning

Pinning is a library contract about movement through a pinned pointer; it does not physically freeze memory or make self-reference safe by itself. Identify which fields are structurally pinned, which may move, when the value becomes pinned, and which safe operations can reach the backing pointer.

For every unchecked pin construction or projection, prove the pointee remains valid at the same address until its destructor returns or panics and that safe pointer operations cannot move it. Review replacement, swap, storage reuse, `ManuallyDrop`, panic during initialization or destruction, and projection of generic fields. Pinned destruction must act as though it receives `Pin<&mut Self>`; a structurally pinned value must be dropped before its storage is invalidated, and `repr(packed)` is incompatible with this guarantee. Prefer an established projection facility already selected by the repository when it encodes the needed contract.

## Unsafe `Send` and `Sync`

An unsafe implementation makes a global claim about all values of the type and every safe operation exposed on them. Inventory interior mutability, aliases, foreign handles, thread affinity, destructors, callbacks, auto-trait effects, and generic parameters. Use negative or conditional implementations where supported by the design rather than asserting unconditional thread safety. `UnsafeCell` permits interior mutation but provides no synchronization; do not infer `Sync` from internal locking without checking every access path and guard lifetime.

## Thread-affine owners

A thread-affine resource belongs to one execution context for its complete lifetime: construction, every use, and destruction. Do not make the resource `Send` merely to move it to that context; move only commands, results, or another capability whose transfer is valid. Check what a closure or future actually captures, because lexical nesting does not prove that it carries the wrapper whose auto-trait contract was reviewed.

When a synchronous constructor starts an owner thread, expose the client only after the owner has reported either successful resource construction or startup failure. Bound command admission and backpressure. During shutdown, stop admission, request teardown, destroy the resource on its owner thread, and join or otherwise settle that owner before the owning API returns; dropping a `JoinHandle` detaches rather than settles the thread.

## Atomics and lock-free code

State the shared invariant, linearization points, ownership and reclamation strategy, and required happens-before relationships before choosing orderings. Reclaim only after every possible observer has lost access. Choose the weakest ordering only when its proof is clear; `SeqCst` is not a substitute for a coherent algorithm, and relaxed ordering is not an optimization quota. Account for ABA, integer wraparound, spurious compare-exchange failure, publication, teardown, mixed-size overlap, and conflicting atomic and non-atomic access.

Unsafe code that is race-free on one architecture may fail on a weaker memory model. Keep supported targets in the verification plan.

## Verification

Test the safe abstraction at startup, under contention, and through shutdown, including initialization failure, immediate post-construction observation, closed channels, worker panic, and ordinary owner drop where relevant. Use model checking or sanitizers when the repository supports them, with bounded state spaces and stated assumptions. Review the algorithm against Rust's current atomic and primitive documentation; a clean stress run, one architecture, or an incomplete weak-memory model does not establish soundness.

Primary anchors: [`std::pin`](https://doc.rust-lang.org/std/pin/), [`Send` and `Sync`](https://doc.rust-lang.org/nomicon/send-and-sync.html), [`std::thread`](https://doc.rust-lang.org/std/thread/), [`JoinHandle`](https://doc.rust-lang.org/std/thread/struct.JoinHandle.html), and [`std::sync::atomic`](https://doc.rust-lang.org/std/sync/atomic/).
