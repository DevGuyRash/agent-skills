---
name: typescript-development
description: Use for substantive TypeScript, TSX, declarations, compiler settings, or typed APIs. Covers modeling, narrowing, and generics; exclude JavaScript-only and Node-runtime-only work.
---

# TypeScript Development

## Purpose

Use TypeScript to make real program invariants visible and maintainable without confusing static assurance with runtime validation. Fit changes to the repository's compiler, module, API, and tooling contracts.

## Compose Deliberately

- Use `javascript-development` for substantive plain JavaScript, JSDoc, or `checkJs` source work. Add this skill when TypeScript compiler configuration, declarations, project references, or typed consumers also change; use both when both artifact contracts are material.
- Add `nodejs-development` only for Node runtime APIs, package metadata, module loading, CLIs, servers, streams, or process behavior.
- Add the relevant UI framework, testing, migration, debugging, refactoring, security, or performance skill when that concern shapes the task.
- Do not load Node guidance merely because TypeScript tooling itself runs on Node.

## Establish the TypeScript Profile

Before editing:

1. Read repository instructions and nearby code.
2. Locate the effective `tsconfig`, including `extends`, project references, per-package overrides, and test/build configs.
3. Record relevant settings: target, libs, module, module resolution, JSX, strictness flags, emit mode, interop, and declaration output.
4. Identify supported runtimes, package boundaries, public exports, generated files, and the repository's package manager and lockfile.
5. Find the selected formatter, linter, test runner, type-check command, and build pipeline.
6. Distinguish compile-time input from runtime input and authored source from generated declarations or output.
7. Determine whether compatibility is against one frozen install/configuration or a moving supported matrix of compiler, resolver, runtime, dependency, and package-export versions.

Use the effective configuration as evidence. Do not infer behavior from a root `tsconfig` that a package does not actually use.

## Model the Domain, Not the Implementation Accident

- Represent valid states directly; use discriminated unions when variants have different required data or behavior.
- Keep nullable, optional, and absent-property semantics distinct when the domain or compiler settings distinguish them.
- Prefer inference for obvious local values and explicit types where they stabilize public contracts or clarify non-obvious intent.
- Use `unknown` for data whose type is not established, then narrow or validate it before use.
- Use `any` only at a justified escape boundary; contain it rather than obscuring it with assertions.
- Make generic parameters express a relationship between inputs and outputs. Remove generics that add no useful constraint.
- Prefer readable types over type-level computation that provides little caller value or harms compiler performance.
- Treat `readonly` as a static API promise, not proof of runtime immutability.

Read [type-modeling.md](<skills-file-root>/references/type-modeling.md) for unions, narrowing, generics, optionality, assertions, and mapped or conditional types.

## Guard Runtime Boundaries

TypeScript types are erased. Validate untrusted network, file, environment, storage, message, and deserialized input before relying on it.

- Reuse the repository's validator or parser rather than adding a second schema system casually.
- Derive types from runtime schemas, or schemas from a single authoritative model, when the existing stack supports that relationship.
- Keep assertions and non-null assertions close to the evidence that makes them safe.
- Preserve error, mutation, ownership, and async behavior; a cleaner type alone does not preserve runtime semantics.
- Do not use a cast to silence evidence of an incompatible API or unsafe value.

Read [boundaries-and-apis.md](<skills-file-root>/references/boundaries-and-apis.md) for parsing, type guards, exported types, declarations, compatibility, and interop.

## Preserve Module and API Contracts

- Treat exported values, types, overloads, declaration shapes, module conditions, and generic inference as caller-facing behavior.
- Account for type-only imports and exports, isolated transformation, and verbatim module settings before rewriting imports.
- Keep runtime and type namespaces distinct; a type import does not create a runtime value.
- Avoid ESM/CommonJS conversion or compiler-wide strictness changes unless the task owns that migration.
- Do not hand-edit generated `.d.ts`, transpiled JavaScript, source maps, or schema-derived types unless repository policy requires it.
- A clean type check is not direct runtime execution. When the supported runtime consumes emitted JavaScript, a loader/transform output, or native TypeScript syntax, verify that actual path separately.

## Verify with the Effective Project

Run the narrowest native checks first:

1. Focused behavior tests and type tests relevant to the change.
2. The package's configured type-check command or the correct project-reference build.
3. Existing lint and format checks for touched files.
4. The relevant build or runtime smoke test when emit, exports, declarations, or module resolution changed.
5. Broader consumers when a public type or package boundary changed, including a packed or external fixture when internal path aliases could hide declaration or export defects.

Read [compiler-and-verification.md](<skills-file-root>/references/compiler-and-verification.md) before changing compiler settings, package declarations, build integration, or compatibility targets.

Do not substitute an ad hoc `tsc` invocation for repository commands when they select different projects or transforms. Completion requires reporting checks run, behavior and type contracts verified, and any supported consumer or target not exercised.

## Avoid Universal Mandates

Do not mandate maximum strictness, explicit annotations everywhere, interfaces over aliases, enums or enum bans, functional or class style, one validation library, one module system, or a compiler/toolchain migration. Strengthen assurance where the repository and task can absorb the compatibility cost.
