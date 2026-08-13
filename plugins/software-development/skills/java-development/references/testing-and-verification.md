# Java Testing and Verification

## Adapt to the existing test system

- Preserve JUnit 4, JUnit Jupiter, TestNG, Spock, or repository-specific conventions rather than migrating for preference.
- Reuse configured fixtures, extensions, parameterization, assertions, mocking tools, and test source sets.
- Test observable contracts. Avoid asserting incidental collection implementations, thread schedules, private methods, or exact exception text unless contractual.
- Keep unit, integration, functional, compatibility, and end-to-end tests in their configured tasks; a default `test` task may not run all of them.
- Make concurrent tests synchronize on events or bounded primitives rather than sleeps.

## Use a risk-shaped ladder

1. Compile the affected source set or module through the wrapper.
2. Run the focused test class or method using the repository's supported filter.
3. Run the affected module's full unit and relevant integration tasks.
4. Run configured formatting, Checkstyle, PMD, SpotBugs, Error Prone, nullness, coverage, or architecture checks.
5. Build and inspect the deployable or published artifact when packaging or public API changes.
6. Exercise the supported JDK/runtime matrix when version compatibility is at risk.

Do not add or enable an analyzer solely because it is listed here. Existing build configuration decides which checks are authoritative.

## Check specialized boundaries

- For overload or generic changes, compile representative callers as well as the implementation.
- For JPMS changes, test on the module path and check reflection/service loading.
- For serialization changes, test old/new fixtures or compatibility paths specified by the repository.
- For annotation processors, regenerate from a clean source state and verify generated output.
- For concurrency changes, combine deterministic lifecycle tests with stress or repeated execution when useful; no finite run proves every schedule.
- For performance claims, use a configured JMH or benchmark harness and route the measurement design to `performance-engineering`.

## Interpret evidence correctly

- Compilation on one JDK does not prove runtime compatibility with another.
- A passing unit task does not prove integration tasks, packaging, reflection, or service discovery.
- Java `assert` may be disabled and is not a substitute for a test assertion framework.
- Coverage is evidence of execution, not correctness; preserve repository thresholds without inventing new quotas.
- Mock verification proves interaction with the double, not compatibility with the real dependency.

## Recover and report

- Fix patch-caused focused failures before widening the suite.
- If dependency resolution, a service, a toolchain, or a runtime is unavailable, report the limitation and run the strongest unaffected checks.
- Separate an unrelated baseline failure from the patch; do not weaken tests or analyzers to obtain green output.
- Preserve failure seeds, temporary artifacts, and logs needed to reproduce nondeterministic failures without committing noise.

Primary references: [JUnit User Guide](https://docs.junit.org/current/user-guide/), [Maven Surefire](https://maven.apache.org/surefire/maven-surefire-plugin/), [Gradle Java testing](https://docs.gradle.org/current/userguide/java_testing.html).
