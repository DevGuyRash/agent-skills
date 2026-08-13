---
name: cpp-development
description: Use for substantive C++ source, build-classified headers, or tooling. Covers RAII, templates, undefined behavior, ABI, and errors; exclude C-only work.
---

# C++ Development

Build and review C++ with explicit ownership, lifetime, error, ABI, and compilation contracts.
Preserve the repository's selected standard, compiler/standard-library matrix, build system, and public compatibility.

## Classify the language first

Treat `.cc`, `.cpp`, `.cxx`, module files, and compiler invocations as stronger evidence than syntax resemblance.
For `.h` files, inspect compile commands, build targets, includers, language flags, and public compatibility requirements.
Use `$c-development` instead when the header is C-only.
Compose both skills for a C API header intentionally consumed by C++.
Do not infer the language from `.h` alone.

## Establish the contract

Inspect repository instructions, build files, CI, dependency metadata, and nearby code. Determine:

- selected C++ standard and accepted compiler extensions;
- compiler and standard-library families, minimum versions, targets, warnings, and sanitizers;
- ownership, exception, RTTI, allocation, threading, and error conventions;
- public API, ABI, visibility, module/header, and binary-compatibility requirements;
- repository-owned format, build, static-analysis, test, and benchmark commands.

Preserve those choices unless the request explicitly changes them.
Do not upgrade the standard, compiler floor, dependencies, warning policy, exception/RTTI mode, or ABI incidentally.

## Load detail only when needed

| Situation | Read |
| --- | --- |
| Ownership transfer, views, iterators, callbacks, moves, RAII, exceptions, concurrency, or lifetime failures | `<skills-file-root>/references/ownership-and-lifetimes.md` |
| Templates, concepts, public headers/modules, ODR, linkage, shared libraries, ABI, or build configuration | `<skills-file-root>/references/templates-abi-and-build.md` |

Load only the reference that owns the current decision.

## Shape ownership and interfaces

Prefer values for independent value-like state and RAII owners for resources.
Use references, pointers, spans, views, and iterators as non-owning vocabulary only when their valid lifetime and nullability are clear.
Choose `unique_ptr`, `shared_ptr`, weak observation, or a raw non-owner from the actual ownership graph; do not replace every pointer mechanically.

Keep interfaces narrow and make ownership transfer visible.
Avoid returning or storing views into temporaries, moved-from objects, reallocated containers, or owners whose lifetime is not tied to the view.
Treat move operations as state transitions with documented valid post-move use where callers depend on it.

## Use language mechanisms deliberately

Prefer standard algorithms and library types when supported and clearer than handwritten control flow.
Introduce templates, concepts, inheritance, type erasure, or metaprogramming only for a real variation or constraint boundary.
Avoid abstraction layers built only to anticipate hypothetical implementations.

Follow the repository's exception and error model.
Use `noexcept` only when the operation satisfies that contract; termination caused by a false declaration is observable behavior.
Keep destructors and cleanup paths safe during partial construction and stack unwinding where exceptions are enabled.

## Preserve compiled boundaries

Treat public type layout, inline definitions, virtual tables, name mangling, calling convention, allocator ownership, exception propagation, and standard-library types as ABI-relevant when binary consumers exist.
Keep implementation details out of public headers when compile-time or ABI coupling is not intended.
Respect the repository's export macros, visibility, module boundaries, and explicit-instantiation strategy.

Do not assume header-only, modules, PImpl, `constexpr`, concepts, or the newest standard is universally better.
Choose them from supported toolchains and product constraints.

## Verify with repository evidence

Run the repository's narrowest relevant build and tests under its configured warnings.
Compile impacted configurations, compiler/standard-library variants, and C consumers of shared headers where applicable.
Use configured static analysis and sanitizers for lifetime, race, and undefined-behavior risks; clean tooling is evidence, not proof.

Exercise construction failure, destruction, copy/move, empty/boundary inputs, iterator/view invalidation, exception or error paths, and concurrency relevant to the change.
For untrusted parsers, plugins, privileged code, or native boundaries, also compose the applicable security workflow.
Report unsupported compilers, link modes, architectures, or ABI consumers explicitly.

## Completion

Report ownership/lifetime choices, standard and ABI contracts preserved, checks run, and any configuration or boundary left unverified.
