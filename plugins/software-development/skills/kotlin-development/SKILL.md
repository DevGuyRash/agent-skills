---
name: kotlin-development
description: >-
  Use for substantive Kotlin source, builds, or tooling. Covers nullability, JVM interop/ABI, coroutines, and cancellation; exclude Android/framework-only work without Kotlin changes.
---

# Kotlin Development

Produce Kotlin changes that fit the repository's declared compiler, targets, interop, API, and verification contracts.

## Establish repository truth

Before editing:

1. Read repository instructions and the code surrounding the requested behavior.
2. Locate Gradle or Maven wrappers, version catalogs, convention plugins, source sets, generated sources, and CI matrices.
3. Resolve Kotlin, language/API, plugin, JVM toolchain/target, Java, and platform versions from repository configuration rather than local installations.
4. Determine whether the target is JVM, JavaScript, Native, Wasm, or Multiplatform and which source set owns the behavior.
5. Discover repository test tasks, formatters, analyzers, code generation, binary/API validation, and packaging commands.
6. Identify Java and other platform callers, public library consumers, reflection/serialization use, and coroutine-scope ownership before changing an API.
7. Treat generated code, wrappers, lock files, and published API dumps as governed outputs.

Repository configuration and supported consumers prevail over this skill's defaults. Do not upgrade Kotlin, Gradle, plugins, targets, or dependencies unless the task requires it.

## Load only the needed guidance

Read one matching reference before implementation. Read a second only when the task crosses both decision areas.

| Task | Reference |
| --- | --- |
| Kotlin semantics, types, collections, equality, extension functions, or API design | [language-and-api.md](<skills-file-root>/references/language-and-api.md) |
| Null boundaries, coroutines, cancellation, Java/JVM interop, or Multiplatform behavior | [coroutines-and-interop.md](<skills-file-root>/references/coroutines-and-interop.md) |
| Compiler/target compatibility, Gradle/Maven, source sets, dependencies, generation, or packaging | [build-and-compatibility.md](<skills-file-root>/references/build-and-compatibility.md) |
| kotlin.test, JUnit/Kotest, coroutine tests, analyzers, API checks, or release evidence | [testing-and-verification.md](<skills-file-root>/references/testing-and-verification.md) |

## Implement the smallest compatible change

- Preserve observable behavior and public contracts unless the request intentionally changes them.
- Follow existing naming, packages, source-set boundaries, null conventions, coroutine ownership, and Java interop before introducing alternatives.
- Use language, standard-library, and compiler features available to every supported target.
- Keep nullability, mutability, ownership, blocking, cancellation, and dispatch behavior explicit where callers observe them.
- Add an abstraction, dependency, coroutine layer, Flow, opt-in API, or compiler plugin only for a concrete need.
- Preserve serialization, reflection, Java signatures, generated names, and binary behavior used by consumers.
- Update KDoc or comments when a public contract or non-obvious invariant changes; do not narrate mechanics.
- Keep unrelated formatting, generated, dependency, and build-file churn out of the patch.

## Compose without absorbing sibling work

- Add an Android-specific skill for lifecycle, Compose, resources, Gradle Android Plugin, manifest, or Android API behavior.
- Add the relevant framework skill for server, persistence, UI, serialization, or dependency-injection semantics.
- Add `test-driven-development` for changed executable behavior or a known bug whose prior behavior can be demonstrated by an automated test. Add the other method skills only when their intent or evidence is present.
- Add `trunk-based-development` for branch and integration policy.
- Use `java-development` too when a mixed JVM API change affects Java source or contracts.

## Verify proportionately

Start with the narrowest repository-supported check that can fail for the change, then widen according to risk:

1. Compile the affected source set or module with the repository wrapper.
2. Run focused tests, then affected target and integration tasks.
3. Run configured formatting, static analysis, code generation, API/ABI validation, and packaging checks.
4. Inspect build, dependency, generated, source-set, and public-signature diffs.

If a check cannot run, separate environment or dependency limitations from product failures. Do not claim success from IDE analysis, compilation of one target, or a single platform test.

## Report completion

Claim completion only after the requested behavior is implemented, risk-proportionate checks pass, and skipped checks and risks are explicit. If a material compatibility choice cannot be resolved from repository evidence, stop before the irreversible change and ask; absent an answer, preserve the current contract and mark the path unverified.

State the behavior changed, target and compatibility decisions, wrapper commands and results, checks skipped with reasons, and remaining risks. Mention intentional API, dependency, coroutine, interop, source-set, or generated-output changes.

## Avoid blanket mandates

Do not impose universal rules for `!!`, `lateinit`, data classes, immutability, expression bodies, scope functions, extension functions, coroutines, Flow, Arrow, test frameworks, line length, or file size. Apply the repository contract and the concrete hazard.
