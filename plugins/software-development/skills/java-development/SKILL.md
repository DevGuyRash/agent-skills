---
name: java-development
description: >-
  Use for substantive Java source, builds, or tooling. Covers JDK compatibility, APIs, exceptions, resources, concurrency, and ABI; exclude framework-only work.
---

# Java Development

Produce Java changes that respect the repository's declared JDK, bytecode, build, API, and runtime contracts.

## Establish repository truth

Before editing:

1. Read repository instructions and the code surrounding the requested behavior.
2. Locate Maven or Gradle wrappers, parent/build files, modules, toolchains, `module-info.java`, version catalogs, generated sources, and CI matrices.
3. Resolve the compile JDK, `--release` or source/target level, runtime JDKs, and supported consumers; do not infer them from the installed JVM.
4. Discover repository test tasks, integration-test boundaries, formatters, analyzers, annotation processors, and packaging commands.
5. Determine whether the target is an application, internal component, or published library and which source, binary, behavioral, and serialization compatibility promises apply.
6. Trace overloads, implementations, callers, reflective use, service loading, and concurrency ownership before changing an API.
7. Treat generated sources, wrapper files, and dependency locks as governed outputs rather than casual edit targets.

Repository configuration and supported consumers prevail over this skill's defaults. Do not upgrade the JDK, language level, build tool, plugins, or dependencies unless the task requires it.

## Load only the needed guidance

Read one matching reference before implementation. Read a second only when the task crosses both decision areas.

| Task | Reference |
| --- | --- |
| Java semantics, collections, generics, null contracts, equality, streams, or public API design | [language-and-api.md](<skills-file-root>/references/language-and-api.md) |
| Exceptions, resources, interruption, executors, futures, virtual threads, or shared state | [errors-and-concurrency.md](<skills-file-root>/references/errors-and-concurrency.md) |
| JDK/bytecode compatibility, Maven, Gradle, JPMS, dependencies, generation, or packaging | [build-and-compatibility.md](<skills-file-root>/references/build-and-compatibility.md) |
| JUnit/TestNG, focused tests, analyzers, integration tests, or release verification | [testing-and-verification.md](<skills-file-root>/references/testing-and-verification.md) |

## Implement the smallest compatible change

- Preserve observable behavior and public contracts unless the request intentionally changes them.
- Follow existing packages, naming, nullness annotations, exception policy, and construction patterns before introducing alternatives.
- Use language and library features available to every supported compile and runtime target.
- Keep ownership of resources, tasks, executors, cancellation, and mutable state explicit.
- Add an abstraction, dependency, annotation processor, reflection path, or concurrency mechanism only for a concrete need.
- Preserve wire formats, persistence formats, service registrations, command behavior, and reflective contracts used by consumers.
- Update Javadoc or comments when a public contract or non-obvious invariant changes; do not narrate mechanics.
- Keep unrelated formatting, generated, dependency, and build-file churn out of the patch.

## Compose without absorbing sibling work

- Add the framework-specific skill for Spring, Jakarta EE, Android, persistence, dependency-injection, or framework lifecycle semantics.
- Add `test-driven-development` for changed executable behavior or a known bug whose prior behavior can be demonstrated by an automated test.
- Add `systematic-debugging`, `refactoring`, or `performance-engineering` for their respective cross-language workflows.
- Add `trunk-based-development` for branch and integration policy.
- Use the Kotlin skill as well when a mixed JVM API change crosses Java/Kotlin boundaries.

## Verify proportionately

Start with the narrowest repository-supported check that can fail for the change, then widen according to risk:

1. Compile the affected source set or module with the repository wrapper.
2. Run focused tests, then the affected module and integration tasks.
3. Run configured format, static analysis, annotation processing, compatibility, and packaging checks.
4. Inspect build, dependency, generated, module-descriptor, and public-API diffs.

If a check cannot run, separate environment or dependency limitations from product failures. Do not claim success from compilation alone, an IDE result, or a single unsupported runtime.

## Report completion

Claim completion only after the requested behavior is implemented, risk-proportionate checks pass, and skipped checks and risks are explicit. If a material compatibility choice cannot be resolved from repository evidence, stop before the irreversible change and ask; absent an answer, preserve the current contract and mark the path unverified.

State the behavior changed, compatibility decisions, wrapper commands and results, checks skipped with reasons, and remaining risks. Mention intentional API, dependency, module, concurrency, generated-source, or packaging changes.

## Avoid blanket mandates

Do not impose universal rules for checked versus unchecked exceptions, `Optional`, records, immutability, streams, interfaces, dependency injection, virtual threads, test frameworks, line length, or class size. Apply repository policy and the concrete contract.
