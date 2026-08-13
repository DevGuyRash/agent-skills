---
name: javascript-development
description: Use for substantive JavaScript, JSX, or JSDoc/checkJs work. Covers modules, promises, mutability, and prototypes; exclude TypeScript-only and Node-runtime-only work.
---

# JavaScript Development

## Purpose

Produce JavaScript that fits the repository's actual language level, runtime, module system, public contracts, and tooling. Prefer behavior-preserving, idiomatic changes over stylistic churn.

## Compose Deliberately

- Use `typescript-development` instead for work confined to TypeScript types or `.ts`/`.tsx` implementation. Use both only when both languages change.
- Add `nodejs-development` for Node runtime APIs, package metadata, module loading, CLIs, servers, streams, or process lifecycle.
- Add the relevant browser, framework, testing, debugging, refactoring, migration, security, or performance skill when that concern materially shapes the work.
- Do not load this skill merely because a tool happens to be implemented in JavaScript.

## Establish the Repository Contract

Before editing:

1. Read repository instructions and nearby code.
2. Identify supported runtimes and versions from manifests, CI, deployment files, browser targets, and tests.
3. Determine ESM/CommonJS and file-extension rules from `package.json`, filenames, bundler configuration, and imports.
4. Identify the selected package manager, lockfile, formatter, linter, type checker, test runner, and build commands.
5. Separate authored code from generated, vendored, minified, or compiled output.
6. Note observable contracts: exports, call shapes, mutation, ordering, timing, error behavior, and serialization.

When evidence conflicts, preserve the working repository contract and surface the conflict rather than silently imposing a convention.

## Implement with Semantic Intent

- Keep the change local unless broader cleanup is required for correctness.
- Preserve falsy values intentionally; choose `??` versus `||` from the domain semantics.
- Use strict equality by default, while retaining deliberate coercive comparisons when their contract is clear and tested.
- Distinguish missing properties, explicit `undefined`, and `null` when callers can observe the difference.
- Choose arrays, objects, `Map`, and `Set` for their key, ordering, identity, and serialization semantics—not fashion.
- Avoid hidden mutation and shared mutable state when they obscure ownership; do not clone data reflexively.
- Preserve prototypes, descriptors, symbols, and class identity when copying or adapting rich objects.
- Treat iteration order, sort stability, and locale-sensitive comparison as observable when output depends on them.
- Match the established functional, class-based, or procedural style unless changing it solves a concrete problem.

For detailed value, object, compatibility, and module guidance, read [language-and-modules.md](<skills-file-root>/references/language-and-modules.md).

## Make Async and Failure Behavior Explicit

- Decide whether work is sequential, concurrent, cancellable, or streaming before selecting an abstraction.
- Await or deliberately return every promise; make intentional background work observable and handle rejection.
- Bound concurrency when work can exhaust memory, connections, rate limits, or file descriptors.
- Preserve error identity and cause where callers inspect them; do not convert every failure to a generic message.
- Clean up listeners, timers, subscriptions, and resources on success, failure, and cancellation.

For promises, cancellation, event APIs, resource lifetime, and error contracts, read [async-errors-and-apis.md](<skills-file-root>/references/async-errors-and-apis.md).

## Preserve Public and Module Contracts

- Treat exported names, default versus named exports, module side effects, package entry points, and import timing as public behavior.
- Avoid ESM/CommonJS migration unless it is requested or necessary for the task.
- Do not add dependencies, change transpilation targets, or replace repository tooling without a task-specific reason.
- Keep environment-specific APIs behind an explicit boundary when code runs in more than one runtime.

## Verify in the Native Toolchain

Run the narrowest relevant existing checks first, then broader checks justified by the change:

1. Focused tests for changed behavior and edge cases.
2. The repository's lint, formatting, and static-analysis commands for touched files.
3. The relevant build or runtime smoke test under a supported target.
4. Broader tests when exports, shared modules, configuration, or dependency boundaries changed.

Read [testing-and-tooling.md](<skills-file-root>/references/testing-and-tooling.md) when selecting tests, changing dependencies, updating build targets, or diagnosing tool disagreement.

Completion requires behavior evidence beyond syntax validity. Report commands run, behavior verified, and any supported runtime or check that could not be exercised.

## Avoid Universal Mandates

Do not prescribe one formatter, semicolon policy, quote style, module system, class/function preference, immutability regime, test runner, bundler, or directory layout. Do not upgrade syntax or dependencies merely because newer options exist. Repository contracts and the requested outcome decide.
