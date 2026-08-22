# Interpretation and Residual Risk

## Evidence classes

Compiler findings come from individually selected Clippy lints supported by the repository toolchain. They are authoritative for the construct and compiled configuration that produced the diagnostic. A configured deny level may make Cargo exit nonzero; when all errors are requested policy lints, that is a completed audit with findings rather than a tooling failure.

Lexical findings are review candidates. The scanner removes comments, normal and raw strings, nested block comments, conventional test paths, `#[test]` items, and definitely test-only `#[cfg(test)]` items before matching direct constructs. It is not a Rust parser: macros, unusual attributes, generated source layouts, and conditional compilation can change meaning.

An unavailable lint means the requested compiler evidence could not be obtained from the repository toolchain. The lexical pass may cover direct unwrap, expect, panic-family, and assertion syntax, but it does not replace semantic indexing, arithmetic, or result-return analysis.

## Expectations and invariants

Review each `#[expect(..., reason = "...")]` in context. A useful reason names the invariant or boundary that makes the construct intentional and remains true when the code changes. An expectation is scoped evidence of intent, not proof that the invariant holds.

Do not introduce a comment-based suppression language. Preserve repository lint configuration and use the compiler-supported expectation mechanism when the repository's minimum Rust version supports it. Otherwise follow the repository's existing scoped lint policy and report the compatibility limit.

## Required residual-risk statement

Every report retains the applicable limits:

- dependencies may panic internally
- indexing and custom trait behavior outside the selected coverage may panic
- allocation failure may abort or panic depending on environment
- omitted features, targets, and `cfg` branches were not compiled
- build scripts and procedural macros can execute outside the scanned source
- destructors may panic, including during unwinding
- poisoned locks and runtime configuration can expose panic paths
- FFI unwind behavior depends on ABI and boundary handling
- unexercised runtime paths are not disproved by static checks

Add concrete repository-specific risks discovered during the audit. Remove a generic item only when the evidence actually excludes it from the declared scope.

## Disposition

Classify each finding as a recoverable operational failure, programmer defect, proven invariant, test/prototype-only use, generated or excluded scope, or unresolved risk. A correction should preserve public error behavior and repository compatibility; do not replace a panic with a swallowed error or a fabricated default.

Re-run the same profile and scope after corrections. A clean direct scan plus passing repository verification supports only the bounded conclusion stated in the skill, never a whole-program guarantee.
