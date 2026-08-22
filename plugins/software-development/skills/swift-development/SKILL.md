---
name: swift-development
description: Use for substantive Swift source, SwiftPM, or tooling. Covers optionals, errors, ownership, concurrency, APIs, and ABI; exclude Apple-UI-only, signing, and Xcode-architecture work.
---

# Swift Development

Build and review Swift language and package code with explicit value, ownership, failure, compatibility, and concurrency contracts. Preserve the repository's Swift language mode, tools version, platforms, build system, and API commitments.

## Keep the boundary precise

Use this skill for Swift source, Swift packages, modules, libraries, command-line programs, tests, and language-level logic inside larger applications. Do not use it as the primary guide for SwiftUI/UIKit/AppKit architecture, navigation, accessibility, Apple design conventions, signing, provisioning, entitlements, Xcode project organization, assets, or release configuration. For those tasks, compose the appropriate Apple platform/UI workflow and use this skill only for the Swift language portion.

## Establish the contract

Inspect repository instructions, `Package.swift`, resolved dependencies, Xcode/build configuration when present, CI, and nearby code. Determine:

- Swift tools version, language mode, enabled upcoming features, and compiler floor;
- package products, targets, modules, supported platforms, and availability policy;
- public API, ABI/library-evolution, serialization, and Objective-C/C interoperability commitments;
- error, optional, ownership, concurrency, dependency, formatting, and lint conventions;
- repository-owned build and test commands.

Preserve those choices unless the request explicitly changes them. Do not upgrade Swift mode, platform floors, dependencies, concurrency checking, or package resolution incidentally.

## Load detail only when needed

| Situation | Read |
| --- | --- |
| ARC cycles, captures, value/reference semantics, async/await, actors, cancellation, `Sendable`, or isolation diagnostics | `<skills-file-root>/references/ownership-and-concurrency.md` |
| SwiftPM manifests, module/public API changes, availability, library evolution, Objective-C/C interop, or cross-platform builds | `<skills-file-root>/references/packages-interop-and-compatibility.md` |

Load only the reference that owns the current decision.

## Model values and interfaces

Prefer value semantics for independent values and reference identity where shared identity or lifecycle is part of the domain. Choose structs, classes, actors, enums, protocols, generics, and existentials from required semantics rather than style rules. Keep mutation and visibility as narrow as callers require.

Use optionals for meaningful absence and `throws` or the repository's result model for recoverable failure. Handle failure at the layer that can add actionable context or recovery. Avoid force unwraps and force casts at caller-controlled or environmental boundaries. Accept them only where a local invariant is reviewable or the repository explicitly treats violation as programmer error.

Avoid protocols, type erasure, dependency wrappers, and generic layers without a real substitution or testing boundary. Do not add Foundation or Apple-only APIs to a cross-platform target without checking its platform contract.

## Preserve ownership and concurrency

Make closure capture and object lifetime explicit where work is retained or escapes. Choose weak or unowned references from actual lifetime guarantees; neither is a universal cycle fix. Treat tasks, continuations, cancellation, actor isolation, and `Sendable` as observable contracts.

Follow the repository's selected concurrency checking mode. Do not silence isolation diagnostics with `@unchecked Sendable`, detached tasks, or unsafe continuations without a documented invariant. Cancellation is cooperative; check and propagate it where the operation's contract requires stopping.

## Protect compatibility

For public APIs, review source compatibility, overload resolution, default arguments, protocol conformances, enum exhaustiveness, availability, symbol exposure, and generated Objective-C names. Treat changes to actor isolation, `async`, `throws`, `Sendable`, ownership, and callback execution context as API changes. Keep implementation-only dependencies and platform types out of public signatures unless intentionally exposed.

## Verify with repository evidence

Run the repository's narrowest relevant format, build, lint, and test commands. When none are defined for a Swift package, use targeted SwiftPM build and test commands matching its products and configurations. Exercise supported language/platform configurations available locally and use CI for unavailable Apple or cross-platform targets.

Test success, absence, failure, cancellation, lifecycle, public API, and interop behavior relevant to the change. Compiler diagnostics and strict-concurrency checking are evidence, not substitutes for runtime and integration tests. Report unavailable platforms, toolchains, and interoperability consumers explicitly.

## Completion

Report value/ownership and failure choices, tools/platform contracts preserved, checks run, and any UI/platform or compatibility surface routed elsewhere or left unverified.
