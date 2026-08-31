---
name: rust-panic-audit
description: Use when direct-panic auditing is explicit, policy-required, or material at a hostile-input, embedded, FFI, or high-availability boundary. Compose with rust-development; exclude routine review.
---

# Rust Panic Audit

This skill assesses direct panic surfaces in a declared Rust scope without claiming that the program is panic-free. Always use `rust-development` with it.

## Activation boundary

Use this skill only when at least one condition holds:

- the user explicitly requests a panic audit
- the repository's strict panic policy requires an audit of the selected scope
- direct panic behavior is part of the acceptance or risk decision at a hostile-input, embedded, FFI, or high-availability boundary

Ordinary Rust work remains panic-resistant, not panic-prohibited. Operational failures normally use recoverable errors; panics may still represent programmer defects or proven invariants. Tests, prototypes, and justified invariants may use `unwrap` or `expect` under the repository's policy.

Boundary presence alone does not activate a panic audit. For example, an FFI aliasing or layout review uses `unsafe-rust` without this skill unless direct panic or unwind exposure is also in scope. Add `async-rust` when task cancellation, executor behavior, or async synchronization matters.

## Establish the audit scope

Inspect the workspace manifest, toolchain files, Cargo configuration, package selection, features, targets, and existing lint configuration. Preserve those choices; never substitute a newer toolchain or `--all-features` silently.

Choose a profile:

- `core` checks direct unwrap/expect variants and explicit panic, todo, unimplemented, and unreachable constructs.
- `strict-boundary` also requests supported indexing/slicing, arithmetic, panic-in-result, and unwrap-in-result lints, and reviews production assertion and debug-assert candidates.

Use only the packages, targets, and features named by the user or established by the repository. If omitted, retain Cargo's repository-native defaults.

## Run the audit

When Python 3 is available, run:

```text
python3 <skills-file-root>/scripts/panic_audit.py \
  --manifest-path <Cargo.toml> \
  --profile core|strict-boundary \
  [--workspace] [--package <name> ...] [--all-targets] \
  [--no-default-features] [--all-features | --features <csv>] \
  [--target <triple>] [--timeout-seconds <seconds>] \
  [--max-command-output-bytes <bytes>] [--json]
```

The runner invokes the repository's Cargo and Clippy, selects restriction lints individually, and performs an independent lexical candidate scan. It preserves a member `--manifest-path` rather than silently auditing workspace defaults. It creates and removes an absent `Cargo.lock` only while file identity and content prove runner ownership. Each child command has a deadline, an output limit, and process-tree cleanup; exceeding a bound makes the audit incomplete.

The runner supports Cargo-default or `--all-targets` target selection. If the requested scope uses narrower Cargo target selectors such as `--lib`, `--bin`, or `--test`, run the exact repository-compatible Cargo and Clippy commands directly and mark the supplemental lexical result incomplete; do not broaden the scope and present it as equivalent. Even with `--all-targets`, the lexical pass excludes root conventional test/fixture directories and definitely test-only items; report that limit separately from compiler target coverage.

Cargo and Clippy execute repository build scripts and procedural macros with the caller's authority. The runner does not intentionally edit tracked files and detects tracked changes plus non-ignored untracked path-set changes outside Cargo's target directory, but it cannot prevent side effects, observe new ignored paths, or detect edits to an already-untracked file. Use a disposable worktree or stronger external sandbox whenever build code is untrusted or no repository mutation is acceptable; cleanup that isolation after the audit.

If Python is unavailable, run the equivalent repository-compatible Cargo and Clippy commands directly. State that the supplemental lexical pass was not available and keep the result incomplete wherever that gap matters.

Compiler-supported `#[expect(..., reason = "...")]` is the preferred scoped rationale. Do not introduce magic suppression comments. Retry a timed-out or output-limited command only after naming and correcting the cause or deliberately changing the corresponding bound; do not convert an incomplete run into clean evidence.

## Interpret the result

Read `<skills-file-root>/references/interpretation-and-residual-risk.md` before making a boundary assurance, interpreting an unavailable lint, or deciding whether a candidate is an accepted invariant.

Runner exits mean:

- `0`: requested checks completed and found no violations or review candidates
- `1`: compiler violations or lexical review candidates were found
- `2`: tooling failed, scope resolution failed, or the audit was incomplete

Treat compiler diagnostics as authoritative for supported direct lints. Treat lexical matches as candidates, not parsed proof. Review intentional expectations against the boundary contract rather than counting them as an automatic pass or failure.

## Completion evidence

Report the profile and exact manifest, packages, target mode or triple, default-feature choice, named features, and execution limits; compiler findings; lexical candidates; intentional expectations; unavailable lints; tooling gaps; worktree-side-effect evidence; and residual risk.

You may conclude: “no forbidden direct constructs found in the audited scope.” Never conclude “panic-free.”

Stop when every requested check has a recorded result or a named blocker and each finding has a disposition. If the build cannot reach the requested scope, return an incomplete audit with the failing command category and next repository-native check; do not weaken the scope silently.
