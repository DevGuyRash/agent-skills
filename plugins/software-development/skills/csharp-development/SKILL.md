---
name: csharp-development
description: >-
  Use for substantive C# source, projects, or .NET tooling. Covers nullability, disposal, async, APIs, and targets; exclude framework-only ASP.NET/EF and workflow-only work.
---

# C# Development

Produce C# changes that fit the repository's declared SDK, language, target-framework, API, and runtime contracts.

## Establish repository truth

Before editing:

1. Read repository instructions and the code surrounding the requested behavior.
2. Locate `global.json`, solution/project files, `Directory.Build.*`, `Directory.Packages.props`, NuGet configuration, lock files, generated sources, and CI matrices.
3. Resolve the SDK, target frameworks, C# language version, nullable context, implicit usings, runtime identifiers, and supported consumers from repository files.
4. Discover repository scripts, restore/build/test/pack commands, formatters, analyzers, source generators, and API compatibility checks.
5. Determine whether the target is an application, tool, internal assembly, or published library and which source, binary, behavioral, and serialization contracts apply.
6. Trace implementations, callers, reflection, dependency injection, native/platform use, and async/concurrency ownership before changing an API.
7. Treat generated code, lock files, central package files, and API baselines as governed outputs.

Repository configuration and supported consumers prevail over this skill's defaults. Do not upgrade the SDK, language version, target frameworks, packages, or analyzers unless the task requires it.

## Load only the needed guidance

Read one matching reference before implementation. Read a second only when the task crosses both decision areas.

| Task | Reference |
| --- | --- |
| C# semantics, nullable references, values, records, equality, LINQ, or API design | [language-and-api.md](<skills-file-root>/references/language-and-api.md) |
| Exceptions, disposal, tasks, cancellation, synchronization, or concurrent state | [exceptions-async-and-concurrency.md](<skills-file-root>/references/exceptions-async-and-concurrency.md) |
| SDK/MSBuild compatibility, projects, target frameworks, NuGet, generation, or packaging | [projects-and-compatibility.md](<skills-file-root>/references/projects-and-compatibility.md) |
| xUnit/NUnit/MSTest, focused tests, analyzers, API checks, or release evidence | [testing-and-verification.md](<skills-file-root>/references/testing-and-verification.md) |

## Implement the smallest compatible change

- Preserve observable behavior and public contracts unless the request intentionally changes them.
- Follow existing namespace, nullability, exception, disposal, async, dependency, and construction patterns before introducing alternatives.
- Use language and BCL APIs available to every supported target framework and runtime.
- Keep ownership of disposable resources, tasks, cancellation, synchronization, and mutable state explicit.
- Add an abstraction, package, source generator, result type, mediator, or concurrency mechanism only for a concrete need.
- Preserve serialization, reflection, COM/native, configuration, and generated contracts used by consumers.
- Update XML documentation or comments when a public contract or non-obvious invariant changes; do not narrate mechanics.
- Keep unrelated formatting, generated, package, and project-file churn out of the patch.

## Compose without absorbing sibling work

- Add framework-specific skills for ASP.NET Core, Entity Framework, Blazor, MAUI, Unity, Orleans, or other framework lifecycle and configuration semantics.
- Add `test-driven-development` for changed executable behavior or a known bug
  whose prior behavior can be demonstrated by an automated test.
- Add `systematic-debugging`, `refactoring`, or `performance-engineering` for their respective cross-language workflows.
- Add `trunk-based-development` for branch and integration policy.
- Add native-language or platform skills when interop changes cross those boundaries.

## Verify proportionately

Start with the narrowest repository-supported check that can fail for the change, then widen according to risk:

1. Restore when required and compile the affected project or target framework with repository commands.
2. Run focused tests, then affected solution and integration tasks.
3. Run configured formatting, analyzers, source generation, API compatibility, trimming/AOT, and packaging checks.
4. Inspect project, package, generated, target-framework, and public-API diffs.

If a check cannot run, separate environment or dependency limitations from product failures. Do not claim success from IDE analysis, compilation of one target framework, or restore alone.

## Report completion

Claim completion only after the requested behavior is implemented, risk-proportionate checks pass, and skipped checks and risks are explicit. If a material compatibility choice cannot be resolved from repository evidence, stop before the irreversible change and ask; absent an answer, preserve the current contract and mark the path unverified.

State the behavior changed, framework and compatibility decisions, commands and results, checks skipped with reasons, and remaining risks. Mention intentional API, package, nullable, async, target-framework, generated, or packaging changes.

## Avoid blanket mandates

Do not impose universal rules for `var`, records, nullable enablement, immutability, `ConfigureAwait(false)`, `ValueTask`, dependency injection, result types, test frameworks, file-scoped namespaces, line length, or class size. Apply the repository contract and concrete hazard.
