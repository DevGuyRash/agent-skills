---
name: php-development
description: >-
  Use for substantive PHP source, Composer, or tooling. Covers types, APIs, errors, resources, and security-sensitive behavior; exclude framework-only work.
---

# PHP Development

## Purpose

Produce PHP changes that fit the repository's supported runtime, SAPIs, extensions, Composer graph, public contracts, framework lifecycle, and verification surface. Keep PHP language policy separate from optional interoperability and framework conventions.

## Establish the repository contract

Before editing, inspect the smallest relevant package or application boundary:

- Local instructions and neighboring PHP code.
- `composer.json`, `composer.lock`, autoload sections, scripts, plugins, and Composer configuration.
- Declared PHP and `ext-*` requirements, `config.platform`, CI matrices, containers, deployment SAPI, loaded extensions, and relevant `php.ini` behavior.
- Framework/bootstrap entry points, generated or cached files, public namespaces, and package shape.
- Configured tests, static analyzers, style tools, refactoring tools, and repository commands.

Repository and consumer evidence take precedence. Do not silently change the framework, package layout, style standard, analyzer, test runner, dependency policy, or minimum PHP version.

## Load detail only when needed

- Read `<skills-file-root>/references/project-and-verification.md` for runtime versions, SAPIs, Composer, extensions, dependencies, project metadata, tests, or verification work.
- Read `<skills-file-root>/references/types-and-public-apis.md` for `strict_types`, coercion, declarations, PHPDoc, public signatures, named arguments, inheritance, or compatibility.
- Read `<skills-file-root>/references/errors-resources-and-security.md` for `Throwable`, error handling, cleanup, streams, transactions, workers, serialization, SQL, output encoding, secrets, or untrusted input.
- Read `<skills-file-root>/references/interoperability-and-style.md` for PSR/PER decisions, autoload interoperability, shared interfaces, formatting, comments, or framework boundaries.

Do not load unrelated references.

## Implement within the contract

- Use syntax and APIs supported by the declared minimum PHP version and required extensions.
- Preserve externally observable behavior unless the requested change intentionally revises it.
- Follow existing namespace, autoload, bootstrap, and framework lifecycle decisions.
- Use accurate native declarations where supported; use analyzer-aware PHPDoc only when it adds information PHP cannot express.
- Follow repository policy for `declare(strict_types=1)`; do not add it mechanically to legacy files.
- Make coercion and comparison behavior explicit at trust and public API boundaries.
- Catch only where code can recover, translate, add boundary context, or clean up.
- Make ownership of streams, locks, transactions, temporary files, processes, and long-lived services visible.
- Keep comments and docblocks focused on contracts, invariants, analyzer-only information, and non-obvious rationale.

## Preserve interfaces

Review these compatibility surfaces before refactoring:

- Namespace and class names, Composer autoload paths, public constants, properties, and visibility.
- Parameter names, position, defaults, by-reference behavior, variadics, native/PHPDoc types, and return values.
- Inheritance variance, interfaces, traits, attributes, magic methods, and reflection-visible metadata.
- Exceptions, warnings, deprecations, resource ownership, serialization, and framework hooks.
- CLI arguments, exit status, streams, environment/configuration, HTTP messages, and database behavior.

Named arguments make public parameter names observable. Do not turn an internal cleanup into an accidental package API migration.

## Avoid universal policy

Do not mandate latest PHP, strict types everywhere, PSR-12 or Coding Style PER, PSR-4, Composer, `src/` and `tests/`, one class per file, exhaustive types, immutable/final classes, one analyzer, or one test framework. Do not install framework architecture as language policy.

## Verify proportionately

- Run the narrowest repository-owned test or check proving the changed behavior.
- Run configured static analysis and style checks when their scope is affected.
- Run Composer validation after metadata or lock changes and verify lock consistency deliberately.
- Check the actual runtime/platform requirements when PHP, extension, SAPI, or deployment compatibility changed.
- Expand to integration or full suites for shared APIs, bootstrap, framework lifecycle, serialization, or dependency changes.
- Build or inspect package artifacts when distribution files, autoloading, or metadata changed.

Do not use ignored platform requirements as success evidence. Name unavailable runtimes, extensions, services, or tools and the gap they leave.

## Compose with focused skills

Use Laravel, Symfony, WordPress, Drupal, Magento, Doctrine, template-engine, security, database, performance, debugging, testing, refactoring, or release guidance when those concerns drive the task. This skill owns PHP semantics and repository fit.

## Completion condition

The requested behavior works, affected interfaces are intentional, Composer and repository checks pass at the warranted scope, and remaining runtime or consumer uncertainty is explicit.
