# Kotlin Testing and Verification

## Adapt to the repository

- Preserve `kotlin.test`, JUnit 4/5, Kotest, Spek, or platform-specific frameworks and their configured runners.
- Reuse repository fixtures, coroutine test utilities, assertions, mocking tools, source sets, and naming.
- Test observable behavior rather than private structure, incidental coroutine scheduling, collection implementation, or exact generated names unless contractual.
- Keep common tests portable and platform tests in their owning source sets.
- Do not migrate test frameworks or add an assertion/mocking dependency for preference.

## Use a risk-shaped ladder

1. Compile the affected source set or module through the repository wrapper.
2. Run the focused test using the configured target and filter.
3. Run affected target, integration, and Multiplatform test tasks.
4. Run configured formatting, ktlint, detekt, compiler-warning, API/ABI, serialization, coverage, or dependency checks.
5. Build and inspect the published or deployable artifacts when signatures, metadata, or packaging changed.
6. Exercise supported compiler/platform matrices when compatibility is at risk.

Do not install or enable a tool merely because it appears in this list. Repository configuration decides which checks apply.

## Test coroutine behavior deterministically

- Use the repository's coroutine test scheduler and dispatcher injection where configured.
- Assert cancellation, completion, ordering, and failure through observable events rather than real-time sleeps.
- Advance virtual time deliberately and ensure child jobs complete or cancel before the test exits.
- Test blocking bridges separately from suspending logic.
- Preserve `CancellationException` behavior and verify cleanup paths.

## Check interop and platform boundaries

- Compile representative Java callers when Kotlin JVM signatures change.
- Verify nullable Java inputs, checked-exception metadata, overloads, properties, and generated names at the caller boundary.
- For Multiplatform changes, run each affected target that the environment supports and report unavailable targets.
- Regenerate and inspect code or API dumps through their owning tasks.
- For Android behavior, use the Android skill and its unit/device/instrumentation verification surface.

## Interpret evidence correctly

- IDE analysis is not a repository build.
- JVM compilation does not prove other targets or Java source compatibility.
- A passing common test does not prove target-specific actual implementations.
- Coverage records execution, not correctness; preserve configured thresholds without inventing quotas.
- A passing mocked test does not prove serializer, framework, native, or Java integration.

## Recover and report

- Fix patch-caused focused failures before widening.
- If a toolchain, SDK, native host, simulator, dependency, or service is unavailable, report it and run the strongest unaffected checks.
- Separate unrelated baseline failures; do not weaken lint, compiler, or tests to obtain green output.
- Preserve seeds and diagnostic inputs needed to reproduce nondeterministic failures.

Primary references: [Kotlin testing](https://kotlinlang.org/docs/jvm-test-using-junit.html), [`kotlin.test`](https://kotlinlang.org/api/core/kotlin-test/), [coroutine testing](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/).
