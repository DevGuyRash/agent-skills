# Pinning and Unsafe Concurrency

Read this reference for pin projection, address-sensitive state, custom futures, atomics, lock-free structures, or unsafe `Send`/`Sync` implementations.

## Pinning

Pinning is a library contract about movement through a pinned pointer; it does not physically freeze memory or make self-reference safe by itself. Identify which fields are structurally pinned, which may move, when the value becomes pinned, and how destruction preserves the invariant.

Do not create unchecked pin projections until construction and field-access paths prove the pointee remains at a stable address for the required lifetime. Review replacement, swap, drop, panic during initialization, and projection of generic fields. Prefer established projection utilities already selected by the repository when they encode the needed contract.

## Unsafe `Send` and `Sync`

An unsafe implementation makes a global claim about all values of the type and every safe operation exposed on them. Inventory interior mutability, aliases, foreign handles, thread affinity, destructors, callbacks, and generic parameters. Use negative or conditional implementations where supported by the design rather than asserting unconditional thread safety. Do not infer `Sync` from internal locking without checking every access path and guard lifetime.

## Atomics and lock-free code

State the shared invariant, linearization points, memory reclamation strategy, and required ordering relationships before choosing orderings. Choose the weakest ordering only when its proof is clear; `SeqCst` is not a substitute for a coherent algorithm, and relaxed ordering is not an optimization quota. Account for ABA, integer wraparound, spurious compare-exchange failure, publication, teardown, and objects still observed by other threads.

Unsafe code that is race-free on one architecture may fail on a weaker memory model. Keep supported targets in the verification plan.

## Verification

Test the safe abstraction under contention and shutdown. Use model checking or sanitizers when the repository supports them, with bounded state spaces and stated assumptions. Review the algorithm against Rust's memory model and primitive documentation; a clean stress run does not establish soundness.

Primary anchors: [`std::pin`](https://doc.rust-lang.org/std/pin/), [`Send` and `Sync`](https://doc.rust-lang.org/nomicon/send-and-sync.html), and [`std::sync::atomic`](https://doc.rust-lang.org/std/sync/atomic/).
