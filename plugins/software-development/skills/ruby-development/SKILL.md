---
name: ruby-development
description: >-
  Use for substantive Ruby source, gems, Bundler, or tooling. Covers dynamic behavior, APIs, errors, resources, concurrency, and tests; exclude Rails-only work.
---

# Ruby Development

## Purpose

Produce Ruby changes that respect the repository's supported interpreters, dependency graph, framework boundaries, public behavior, and verification commands. Adapt to the project instead of imposing a preferred Ruby style stack.

## Establish the repository contract

Before editing, inspect the smallest relevant project boundary:

- Local instructions and neighboring Ruby code.
- `.ruby-version`, version-manager files, `Gemfile`, lockfiles, gemspecs, and Bundler configuration.
- `required_ruby_version`, CI matrices, containers, deployment runtime, and native-extension constraints.
- Load paths, autoloading, executables, Rake tasks, generated files, and framework lifecycle.
- Configured tests, type tooling, formatter, linter, documentation, and task-runner commands.

Repository evidence and supported consumers take precedence. Do not silently replace Bundler, the test framework, RuboCop or Standard, RBS or Sorbet, the package layout, or the minimum Ruby version.

## Load detail only when needed

- Read `<skills-file-root>/references/project-and-verification.md` for Ruby versions, Bundler, gems, dependencies, native extensions, project metadata, or verification changes.
- Read `<skills-file-root>/references/apis-and-types.md` for public methods, keyword arguments, blocks, constants, metaprogramming, signatures, RBS, Sorbet, or compatibility work.
- Read `<skills-file-root>/references/errors-resources-and-concurrency.md` for exceptions, cleanup, transactions, threads, processes, Fibers, Ractors, cancellation, or long-running workers.
- Read `<skills-file-root>/references/security-and-framework-boundaries.md` for commands, serialization, templates, SQL, paths, secrets, dynamic dispatch, Rails, or another framework boundary.

Do not load unrelated references.

## Implement within the contract

- Use syntax and core APIs supported by the declared minimum Ruby version.
- Preserve observable behavior unless the requested change intentionally revises it.
- Keep load order, autoloading, constant resolution, and dependency direction consistent with the project.
- Prefer direct objects, messages, collections, and blocks; add abstraction or metaprogramming only for a demonstrated contract or repeated variation.
- Preserve the distinction among positional arguments, keywords, splats, keyword splats, and blocks.
- Follow the repository's mutation and bang-method conventions; do not infer safety from punctuation alone.
- Use the established typing system only where it improves a real boundary.
- Rescue only where code can recover, translate, add boundary context, retry deliberately, or clean up.
- Make ownership of files, sockets, transactions, locks, threads, and subprocesses explicit.
- Keep comments and documentation focused on contracts, invariants, compatibility constraints, and surprising intent.

## Preserve interfaces

Review these compatibility surfaces before refactoring:

- Require paths, constants, autoload names, visibility, inheritance, and refinement scope.
- Method names, positional and keyword parameters, defaults, block requirements, and return values.
- Enumerator behavior when no block is given, laziness, mutation, identity, equality, and ordering.
- Exception classes, messages when asserted, callbacks, hooks, and framework conventions.
- CLI arguments, exit status, stdout/stderr, environment variables, serialized forms, and gem metadata.

Do not turn an internal cleanup into an accidental gem or application migration.

## Avoid universal policy

Do not mandate Rails patterns, service objects, one style tool, frozen string literals, exhaustive signatures, immutable value objects, monads, Active Record, or one test framework. Do not rewrite working Ruby merely to match a popular style guide.

## Verify proportionately

- Run the narrowest repository-owned example or test that proves the changed behavior.
- Invoke tools through the project's Bundler or task-runner interface when that is its contract.
- Run configured style, static/type, and documentation checks when their scope is affected.
- Expand to integration or full suites for shared constants, callbacks, monkey patches, autoloading, or public APIs.
- Exercise supported Ruby versions and platforms when syntax, dependencies, native gems, or concurrency behavior changed.
- Build and inspect the gem when gemspec, executables, files, or package metadata changed.

Do not claim compatibility from the local Ruby alone. Name unavailable runtimes, services, or tools and the verification gap they leave.

## Compose with focused skills

Use Rails or other framework guidance, plus security, database, performance, debugging, testing, refactoring, or release skills when those concerns drive the task. This skill owns Ruby semantics and repository fit, not their complete workflows.

## Completion condition

The requested behavior is implemented, affected interfaces are intentional, repository checks pass at the warranted scope, and any remaining runtime or consumer uncertainty is explicit.
