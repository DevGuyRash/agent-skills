---
name: rust-development
description: Use for substantive Rust source, Cargo, or tooling. Covers ownership, APIs/errors, workspaces, MSRV, and verification; compose async-rust, unsafe-rust, or rust-panic-audit as needed; exclude workflow-only work.
---

# Rust Development

Build and review ordinary Rust while preserving the repository's toolchain, public contracts, and verification surface. Prefer code whose ownership and failure behavior are visible at its boundaries.

## Establish the contract

Before changing code, inspect the nearest `Cargo.toml`, workspace manifest, lockfile policy, CI, and contributor instructions. Determine:

- crate role: library, binary, procedural macro, test support, or workspace tooling;
- selected edition, minimum supported Rust version, feature policy, targets, and `no_std` status;
- public API and serialization compatibility requirements;
- repository-owned format, lint, build, and test commands.

Preserve those choices unless the request explicitly changes them. Do not upgrade the edition, MSRV, dependencies, feature defaults, or lockfile incidentally.

## Compose focused skills

- Load `$async-rust` alongside this skill for futures, runtimes, tasks, cancellation, async I/O, or code that awaits.
- Load `$unsafe-rust` alongside this skill for unsafe blocks or functions, raw pointers, FFI, layout assumptions, pin projections, or unsafe trait implementations.
- Load `$rust-panic-audit` alongside this skill for a direct-panic audit of a declared Rust scope; keep its audit procedure out of this core.

## Load detail only when needed

| Situation | Read |
| --- | --- |
| Designing a fallible public API, deciding whether panic is acceptable, or changing error context | `<skills-file-root>/references/fallibility.md` |
| Changing features, workspace structure, Cargo metadata, MSRV, platform gates, or dependency exposure | `<skills-file-root>/references/cargo-contracts.md` |
| Changing synchronous threads, channels, shared state, worker shutdown, or atomics | `<skills-file-root>/references/sync-concurrency.md` |

Do not load a reference for a local implementation that does not touch its decision.

## Shape the change

Model invariants with types and ownership before adding runtime checks. Prefer borrowing for temporary access and ownership transfer when the callee must retain or consume a value. Choose concrete types by default; introduce traits or generics when a real substitution boundary needs them. Keep conversions explicit at trust, precision, and allocation boundaries.

Use iterators, pattern matching, and standard-library types when they make intent clearer, not as style quotas. Avoid cloning merely to satisfy the borrow checker; first decide which component should own the value. Accept a clone when it is the clearest correct tradeoff and its cost fits the path.

## Make failure intentional

Treat unexpected panic as an API decision, not a blanket syntax ban. Return `Result` or `Option` for recoverable conditions the caller can act on. Reserve assertions and panic for violated invariants, impossible states, or process-level policies that are explicit in context. Add error context at boundaries where it identifies the failed operation without leaking secrets. Do not discard an error or convert it to a default unless the contract defines that recovery.

Use `unwrap` or `expect` only when the invariant is local and reviewable, or in tests and tightly scoped startup code where aborting is the stated policy. Prefer an explanatory `expect` message over repeating the operation.

## Preserve interfaces

Keep visibility as narrow as the callers require. For public types and functions, consider semver impact, downstream inference, exhaustiveness, feature availability, and documented error behavior. Do not expose an implementation dependency through a public signature accidentally. Keep platform-specific code behind the existing `cfg` and feature structure.

## Verify with repository evidence

Run the repository's narrowest relevant format, build, lint, and test commands first. When no commands are defined, use targeted Cargo checks appropriate to the affected crate and feature/target set. Compile meaningful feature combinations rather than assuming the default feature set represents every supported build. Treat Clippy, compiler warnings, and static analysis as evidence, not substitutes for behavior tests.

Exercise success, recoverable failure, boundary values, and the changed public contract. If a target or feature cannot run locally, report the exact unverified surface rather than silently shrinking support.

## Completion

Report the behavior changed, compatibility choices preserved, checks run, and any target, feature, or failure path left unverified.
