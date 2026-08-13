---
name: rust-panic-audit
description: Use when direct-panic auditing is explicit, policy-required, or material at a hostile-input, embedded, FFI, or high-availability boundary. Compose with rust-development; exclude routine review.
---

# Rust Panic Audit

This skill assesses direct panic surfaces in a declared Rust scope without
claiming that the program is panic-free. Always use `rust-development` with it.

## Activation boundary

Use this skill only when at least one condition holds:

- the user explicitly requests a panic audit
- the repository's strict panic policy requires an audit of the selected scope
- direct panic behavior is part of the acceptance or risk decision at a
  hostile-input, embedded, FFI, or high-availability boundary

Ordinary Rust work remains panic-resistant, not panic-prohibited. Operational
failures normally use recoverable errors; panics may still represent programmer
defects or proven invariants. Tests, prototypes, and justified invariants may
use `unwrap` or `expect` under the repository's policy.

Boundary presence alone does not activate a panic audit. For example, an FFI
aliasing or layout review uses `unsafe-rust` without this skill unless direct
panic or unwind exposure is also in scope. Add `async-rust` when task
cancellation, executor behavior, or async synchronization matters.

## Establish the audit scope

Inspect the workspace manifest, toolchain files, Cargo configuration, package
selection, features, targets, and existing lint configuration. Preserve those
choices; never substitute a newer toolchain or `--all-features` silently.

Choose a profile:

- `core` checks direct unwrap/expect variants and explicit panic, todo,
  unimplemented, and unreachable constructs.
- `strict-boundary` also requests supported indexing/slicing, arithmetic,
  panic-in-result, and unwrap-in-result lints, and reviews production assertion
  and debug-assert candidates.

Use only the packages, targets, and features named by the user or established
by the repository. If omitted, retain Cargo's repository-native defaults.

## Run the audit

When Python 3 is available, run:

```text
python3 <skills-file-root>/scripts/panic_audit.py \
  --manifest-path <Cargo.toml> \
  --profile core|strict-boundary \
  [--workspace] [--package <name> ...] [--all-targets] \
  [--all-features | --features <csv>] [--json]
```

The runner invokes the repository's Cargo and Clippy, selects restriction
lints individually, and performs an independent lexical candidate scan. Cargo
build-cache writes are allowed; the runner does not edit tracked files, copy
artifacts into the repository, or change lint and CI configuration.
Even with `--all-targets`, the lexical pass excludes conventional test-only
paths and items; report that limit separately from Cargo/Clippy target coverage.

If Python is unavailable, run the equivalent repository-compatible Cargo and
Clippy commands directly. State that the supplemental lexical pass was not
available and keep the result incomplete wherever that gap matters.

Compiler-supported `#[expect(..., reason = "...")]` is the preferred scoped
rationale. Do not introduce magic suppression comments.

## Interpret the result

Read `<skills-file-root>/references/interpretation-and-residual-risk.md` before
making a boundary assurance, interpreting an unavailable lint, or deciding
whether a candidate is an accepted invariant.

Runner exits mean:

- `0`: requested checks completed and found no violations or review candidates
- `1`: compiler violations or lexical review candidates were found
- `2`: tooling failed, scope resolution failed, or the audit was incomplete

Treat compiler diagnostics as authoritative for supported direct lints. Treat
lexical matches as candidates, not parsed proof. Review intentional
expectations against the boundary contract rather than counting them as an
automatic pass or failure.

## Completion evidence

Report the profile and exact packages, targets, and features audited; compiler
findings; lexical candidates; intentional expectations; unavailable lints;
tooling gaps; and residual risk.

You may conclude: “no forbidden direct constructs found in the audited scope.”
Never conclude “panic-free.”

Stop when every requested check has a recorded result or a named blocker and
each finding has a disposition. If the build cannot reach the requested scope,
return an incomplete audit with the failing command category and next
repository-native check; do not weaken the scope silently.
