# TypeScript Compiler and Verification

Load this reference when compiler settings, project references, emit, declarations, package boundaries, or verification commands are in scope.

## Resolve the Effective Configuration

- Find the config used by the edited package and command, including inherited configs and command-line overrides.
- Check target and libs separately: emitted syntax support and available ambient APIs are different decisions.
- Align module and module resolution with the runtime or bundler that consumes the output.
- Account for JSX mode, `isolatedModules`, verbatim module syntax, declaration settings, path mappings, and project references when relevant.
- Treat path aliases as compile-time configuration unless the runtime/bundler also resolves them.
- Do not assume `noEmit` represents the production build when another transformer emits code.

## Change Settings Deliberately

- Scope stricter checks to the smallest compatible project when a repository is migrating incrementally.
- Estimate downstream diagnostics and emitted-code or declaration changes before changing a shared base config.
- Do not paper over new diagnostics with broad excludes, blanket `skipLibCheck`, or widespread assertions without locating their source.
- Keep test, tool, server, browser, and production configs aligned only where they share an actual runtime contract.
- Preserve generated-file exclusions and build-info locations.

## Verification Layers

- Run the repository's focused behavior tests; a clean type check does not prove runtime behavior.
- Run the configured type-check or build command for the affected project and its declared dependents.
- Use type-focused fixtures or compile-time assertions when inference, rejected inputs, or declaration compatibility is the behavior under test.
- Inspect emitted JavaScript when module interop, decorators, class fields, downlevel iteration, or helpers can affect runtime behavior.
- Inspect generated declarations when a library's public API changes.
- Run a supported consumer or package-boundary smoke test when exports or declaration resolution changed.

## Tooling and Dependencies

- Preserve the selected package manager, lockfile, compiler source, linter integration, formatter, test runner, and build transformer.
- Avoid invoking a globally installed compiler whose version differs from the repository.
- Keep compiler, runtime, framework, and `@types` versions compatible; do not upgrade unrelated packages as incidental cleanup.
- If checks disagree, compare their working directories, configs, file sets, environments, and installed dependency graphs before weakening any check.

Report exact commands and the project/config they exercised. Name untested supported targets and downstream consumers explicitly.
