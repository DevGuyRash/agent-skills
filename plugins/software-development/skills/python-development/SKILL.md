---
name: python-development
description: >-
  Use for substantive Python source, stubs, or pyproject tooling. Covers typing, exceptions, resources, and concurrency; exclude Q&A, scratch code, and distribution/publication-only work.
---

# Python Development

## Purpose

Produce Python changes that fit the repository's supported interpreters, dependency model, public contracts, and verification surface. Prefer the project's established choices over a generic Python stack.

## Establish the repository contract

Before changing code, identify the smallest relevant project boundary and inspect:

- Local instructions and nearby code that demonstrates established conventions.
- `pyproject.toml`, build-backend configuration, lockfiles, and tool-specific files.
- The declared Python range, CI matrix, container/runtime image, and deployment target.
- Package layout, import roots, entry points, generated files, and public modules.
- Configured tests, type checker, formatter, linter, and task runner commands.

Treat repository configuration and supported consumers as authoritative. Do not silently introduce a new package manager, layout, formatter, type checker, test framework, or minimum Python version.

## Load detail only when needed

- Read `<skills-file-root>/references/project-and-verification.md` when the task changes dependencies, environments, project metadata, tool configuration, tests, or supported Python versions.
- Read `<skills-file-root>/references/types-and-apis.md` when it changes annotations, public call signatures, imports, protocols, data models, decorators, or compatibility-facing behavior.
- Read `<skills-file-root>/references/errors-resources-and-concurrency.md` when it touches exceptions, cleanup, context managers, subprocesses, threads, processes, async code, cancellation, or task lifetimes.
Do not load unrelated references.

## Implement within the contract

- Write syntax and use standard-library APIs supported by the declared minimum interpreter.
- Preserve externally observable behavior unless the requested change intentionally revises it.
- Keep imports acyclic and dependency direction consistent with the existing package structure.
- Prefer clear Python data and control flow; introduce abstractions only when they clarify a real contract or repeated variation.
- Use native annotations where they are accurate and supported, but follow the repository's checker mode and annotation policy.
- Keep sync code sync unless concurrency is part of the requirement; do not introduce async as a style preference.
- Make ownership of files, connections, locks, tasks, and processes visible at the boundary that acquires them.
- Catch exceptions only where code can recover, translate, add boundary context, or perform cleanup.
- Keep comments and docstrings focused on public contracts, invariants, surprising constraints, and non-obvious rationale.

## Preserve interfaces

Consider these compatibility surfaces before refactoring:

- Import paths, exported names, call signatures, defaults, keyword names, and return shapes.
- Exception types, warning behavior, context-manager behavior, and iterator or generator timing.
- CLI arguments, exit status, stdout/stderr, environment variables, and configuration formats.
- Serialized data, database schemas, plugin hooks, framework callbacks, and typing artifacts such as stubs or `py.typed`.

Do not turn an internal cleanup into a public API migration accidentally.

## Avoid universal policy

Do not mandate `src/` layout, dataclasses, protocols, async, immutability, exhaustive annotations, one formatter, one test framework, or one packaging frontend. Do not replace working repository tools merely because another tool is currently popular.

## Verify proportionately

- Start with the narrowest repository-owned test or check that exercises the changed behavior.
- Run the configured formatter or style check, linter, and type checker when their scope is affected.
- Expand to the relevant package or full suite when the change can affect shared imports, public APIs, or runtime compatibility.
- Test against supported interpreter versions when version-sensitive syntax, dependencies, or behavior changed.

Do not claim checks passed when required interpreters, dependencies, services, or tools were unavailable. Report the exact evidence and remaining gap.

## Compose with focused skills

Use framework, database, security, performance, debugging, testing, refactoring, packaging, or release skills when those concerns drive the task. Packaging and publication are outside this core. This skill owns Python semantics and repository fit; it does not replace those workflows.

## Completion condition

The change is complete when the requested behavior works, affected interfaces remain intentional, repository-owned checks pass at the warranted scope, and any unverified compatibility surface is named explicitly.
