---
name: unsafe-rust
description: REQUIRED whenever Rust work touches `unsafe {}`, `unsafe fn`, `unsafe trait` or `unsafe impl`, `static mut`, unsafe extern items or blocks, `#[unsafe(...)]`, raw pointers or owners, `MaybeUninit`, FFI, ABI or layout, assembly or intrinsics, provenance or aliasing, pinning, unsafe `Send` or `Sync`, lock-free code, or thread-affine foreign handles. Do not write, review, debug, or scaffold these surfaces without this skill. Always compose with rust-development; exclude safe-only Rust. If unsafe Rust is in scope, use this skill.
---

# Unsafe Rust

Make each unsafe boundary small, necessary, and justified by invariants that safe callers cannot violate. Always use this skill with `$rust-development`; ordinary ownership, API, Cargo, and failure guidance still applies.

## Establish the boundary

Inspect the code, target, compiler policy, dependencies, and existing safety documentation before editing. Identify:

- the unsafe operation and why safe Rust cannot express the required behavior adequately;
- whether the code introduces an unchecked obligation for callers or implementors, or asserts that an existing obligation has been discharged;
- which party establishes each precondition and for how long it remains true;
- allocation origin, object lifetime, aliasing, alignment, initialization, and mutability rules;
- unwind, panic, thread, signal, and callback boundaries;
- supported architectures, hardware features, and layout or ABI assumptions;
- the safe API that prevents callers from violating the invariants.

Do not use unsafe merely to silence the borrow checker, remove a check, or imitate an optimization without evidence and a maintained contract.

## Load detail only when needed

| Situation | Read |
| --- | --- |
| Using raw pointers, manual allocation or ownership, `MaybeUninit`, `UnsafeCell`, volatile access, or pointer/address conversion | [pointers-validity-and-initialization.md](references/pointers-validity-and-initialization.md) |
| Crossing an ABI; using `repr`, unions, variadics, callbacks, unsafe attributes, inline assembly, intrinsics, or target features | [ffi-and-layout.md](references/ffi-and-layout.md) |
| Implementing pin projection, self-reference, atomics, lock-free code, unsafe `Send`/`Sync`, or a thread-affine owner | [pinning-and-concurrency.md](references/pinning-and-concurrency.md) |

Load every reference whose hazard is in scope, and no unrelated reference. For example, a foreign callback with concurrent or cancellable teardown needs the FFI and concurrency references, plus `$async-rust` when the owner is asynchronous.

## State the safety contract

Write the contract for every unsafe interface, including private ones; publish it in API documentation where callers or implementors must see it. At each unsafe block, unsafe implementation, external declaration, or unsafe attribute, keep the evidence close enough that a reviewer can connect every precondition to the fact that establishes it. Use a focused `SAFETY` comment for that connection, not to restate the operation.

Distinguish requirements enforced by types from those enforced by runtime checks, privacy, construction paths, or external contracts. If safe callers can reach undefined behavior, the abstraction is unsound even when current callers behave correctly.

## Minimize authority

Keep unsafe blocks narrower than the surrounding algorithm. Perform validation and ordinary control flow in safe code where practical. Return a safe abstraction whose constructors establish the invariant, whose private state represents it, and whose methods preserve it. Avoid exposing raw pointers, unconstrained lifetimes, or mutable aliases beyond the layer that needs them.

Use explicit unsafe blocks inside `unsafe fn` bodies so each discharged obligation remains visible, respecting the repository's `unsafe_op_in_unsafe_fn` policy. Do not broaden visibility or weaken types to make the implementation convenient.

## Review memory behavior

Check provenance, range, alignment, initialization, validity, aliasing, lifetime, and ownership for every pointer-derived access against the exact operation contract. Account for zero-sized types, overflow in layout math, partially initialized state, destructor behavior, and panic or unwind. Never create a reference before its validity and aliasing requirements hold; creating an invalid reference is not deferred until dereference.

## Verify without overclaiming

Run repository-native Rust checks and focused behavioral tests first. Add tests at the safe boundary, including invalid inputs that must be rejected before unsafe execution. Use Miri, sanitizers, concurrency modeling, layout randomization, or target-specific tests when supported and relevant.

Passing tests or dynamic tools sample executions; they do not prove the unsafe contract. Review the invariant against every constructor, mutation path, destructor, callback, and concurrency edge. Treat experimental aliasing models and incomplete memory-model guidance as diagnostics rather than stable language guarantees. If a supported target or tool is unavailable, name that gap explicitly.

## Completion

Report why unsafe remains necessary, the caller and implementation obligations, how the safe surface enforces them, evidence run, and assumptions not mechanically verified.
