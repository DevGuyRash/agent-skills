---
name: go-development
description: >-
  Use for substantive Go source, modules, or tooling. Covers APIs, errors, context, concurrency, resources, and tests; exclude framework-only and workflow-only work.
---

# Go Development

Produce Go changes that fit the repository's declared language, module, API, and verification contract.

## Establish repository truth

Before editing:

1. Read repository instructions and the files surrounding the change.
2. Locate `go.mod`, any `go.work`, nested modules, vendor state, build tags, generated-file markers, and CI matrices.
3. Resolve the effective Go and toolchain requirements from repository files; do not assume the newest installed release.
4. Discover repository commands, wrappers, generators, linters, and test conventions before choosing commands.
5. Determine whether the target is an application, command, internal package, or public module and which compatibility promises apply.
6. Trace callers, implementations, tests, and ownership of mutable or concurrent state before changing an interface.
7. Treat generated files as outputs; edit their source or generator unless the repository explicitly says otherwise.

Repository constraints and supported consumers prevail over this skill's defaults. Do not upgrade Go, dependencies, directives, or tooling unless the task requires it.

## Load only the needed guidance

Read one matching reference before implementation. Read a second only when the task crosses both decision areas.

| Task | Reference |
| --- | --- |
| Language semantics, package/API design, data ownership, interfaces, or generics | [language-and-api.md](<skills-file-root>/references/language-and-api.md) |
| Errors, context propagation, goroutines, channels, synchronization, or cancellation | [errors-and-concurrency.md](<skills-file-root>/references/errors-and-concurrency.md) |
| Modules, workspaces, dependencies, build constraints, generation, or toolchain compatibility | [modules-and-tooling.md](<skills-file-root>/references/modules-and-tooling.md) |
| Tests, fuzzing, race checks, static analysis, benchmarks, or release evidence | [testing-and-verification.md](<skills-file-root>/references/testing-and-verification.md) |

## Implement the smallest compatible change

- Preserve observable behavior and exported contracts unless the requested change intentionally alters them.
- Prefer the repository's existing package boundaries and idioms over a new abstraction or architecture.
- Keep ownership, cancellation, blocking, and error behavior explicit at the boundary where they matter.
- Use syntax and standard-library APIs available to every supported Go version.
- Add a dependency, interface, generic abstraction, goroutine, or global only when the task supplies a concrete need.
- Preserve serialization, command, environment, filesystem, and network contracts used by callers.
- Update comments when exported behavior or a non-obvious invariant changes; do not narrate mechanics.
- Keep unrelated formatting, dependency, generated, and module-file churn out of the patch.

## Compose without absorbing sibling work

- Add the framework-specific skill for framework APIs, lifecycle, configuration, or generated code.
- Add `test-driven-development` for changed executable behavior or a known bug whose prior behavior can be demonstrated by an automated test.
- Add `systematic-debugging` for open-ended diagnosis, `refactoring` for structural redesign, or `performance-engineering` for measured optimization.
- Add `trunk-based-development` for branching, integration, or delivery policy.
- Do not turn those workflows into Go-specific mandates.

## Verify proportionately

Start with the narrowest repository-supported check that can fail for the change, then widen only as risk warrants:

1. Format and compile the affected package or command.
2. Run the focused tests, then the affected module or repository suite.
3. Run configured vet, lint, generation, race, fuzz, or compatibility checks when relevant.
4. Inspect module, workspace, generated, and public-API diffs for unintended changes.

If a check cannot run, distinguish an environment or dependency limitation from a product failure. Do not treat formatting, compilation, or a cached result as evidence beyond what it actually exercised. When fresh execution matters or relevant inputs are outside the test-cache key, use the repository convention or `-count=1`; do not clear caches reflexively.

## Report completion

Claim completion only after the requested behavior is implemented, risk-proportionate checks pass, and skipped checks and risks are explicit. If a material compatibility choice cannot be resolved from repository evidence, stop before the irreversible change and ask; absent an answer, preserve the current contract and mark the path unverified.

State the behavior changed, compatibility decisions, commands run and results, checks skipped with reasons, and remaining risks. Mention any intentional public API, module, dependency, concurrency, or generated-output change.

## Avoid blanket mandates

Do not impose universal bans or quotas for `panic`, globals, `init`, interfaces, generics, channels, table-driven tests, file size, package size, or third-party libraries. Judge each against the repository contract and the concrete failure mode.
