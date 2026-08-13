---
name: unsafe-rust
description: Use when Rust work changes unsafe blocks, pointers, FFI, layout, provenance, aliasing, or unwind boundaries. Always compose with rust-development; exclude safe-only Rust.
---

# Unsafe Rust

Make each unsafe boundary small, necessary, and justified by invariants that safe callers cannot violate.
Always use this skill with `$rust-development`; ordinary ownership, API, Cargo, and failure guidance still applies.

## Establish the boundary

Inspect the code, target, compiler policy, dependencies, and existing safety documentation before editing.
Identify:

- the unsafe operation and why safe Rust cannot express the required behavior adequately;
- which party establishes each precondition and for how long it remains true;
- allocation origin, object lifetime, aliasing, alignment, initialization, and mutability rules;
- unwind, panic, thread, signal, and callback boundaries;
- supported architectures and layout or ABI assumptions;
- the safe API that prevents callers from violating the invariants.

Do not use unsafe merely to silence the borrow checker, remove a check, or imitate an optimization without evidence and a maintained contract.

## Load detail only when needed

| Situation | Read |
| --- | --- |
| Crossing C or another ABI, using `repr`, unions, variadics, callbacks, or foreign allocation | `<skills-file-root>/references/ffi-and-layout.md` |
| Implementing pin projection, self-reference, atomics, lock-free code, or unsafe `Send`/`Sync` | `<skills-file-root>/references/pinning-and-concurrency.md` |

Load only the reference relevant to the boundary under change.

## State the safety contract

For every public `unsafe fn`, unsafe trait, and unsafe implementation boundary, document caller obligations and the consequences of violation.
For each unsafe operation, keep the proof close enough that a reviewer can connect preconditions to evidence.
Use a focused `SAFETY` comment when it records that connection; avoid ceremonial comments that merely restate the operation.

Distinguish requirements enforced by types from those enforced by runtime checks, privacy, construction paths, or external contracts.
If safe callers can reach undefined behavior, the abstraction is unsound even when current callers behave correctly.

## Minimize authority

Keep unsafe blocks narrower than the surrounding algorithm.
Perform validation and ordinary control flow in safe code where practical.
Return a safe abstraction whose constructors establish the invariant and whose methods preserve it.
Avoid exposing raw pointers, unrestricted lifetimes, or mutable aliases beyond the layer that needs them.

Use explicit unsafe blocks inside `unsafe fn` bodies so each unsafe operation remains visible.
Do not broaden visibility or weaken types to make the implementation convenient.

## Review memory behavior

Check provenance, bounds, alignment, initialization, validity, aliasing, lifetime, and deallocation for every pointer-derived access.
Account for zero-sized types, integer overflow in layout math, partial initialization, destructor behavior, and panic/unwind paths where applicable.
Use `MaybeUninit`, pointer reads/writes, and ownership reconstruction only according to their exact standard-library contracts.
Never create references before their validity and aliasing requirements are established.

## Verify without overclaiming

Run repository-native Rust checks and focused behavioral tests first.
Add tests at the safe boundary, including invalid inputs that should be rejected before unsafe execution.
Use Miri, sanitizers, loom-style modeling, or target-specific tests when supported and relevant.

Passing tests or dynamic tools samples executions; it does not prove the unsafe contract.
Review the written invariant against every constructor, mutation path, destructor, callback, and concurrency edge.
If a supported target or tool is unavailable, name that gap explicitly.

## Completion

Report why unsafe remains necessary, the caller and implementation obligations, how the safe surface enforces them, evidence run, and assumptions not mechanically verified.
