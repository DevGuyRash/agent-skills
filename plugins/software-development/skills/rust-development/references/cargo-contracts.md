# Cargo and Compatibility Contracts

Read this reference only when the change touches Cargo resolution, published surfaces, workspace structure, features, toolchain support, or target selection.

## Discover before editing

Inspect the workspace root and affected package manifests together. Record the repository's:

- edition, `rust-version`, toolchain file, resolver, and release profile choices;
- lockfile policy for libraries, binaries, examples, and workspace roots;
- default features, additive feature expectations, optional dependencies, and `cfg` aliases;
- supported targets, `no_std`/`alloc` combinations, and platform-specific dependencies;
- publishing metadata, public dependency exposure, and generated-code policy.

The absence of an explicit MSRV is not permission to choose one. Infer only what current CI and documentation establish; otherwise leave it unchanged and name the uncertainty.

## Preserve feature semantics

Features are additive build-time configuration, not mutually exclusive runtime modes unless the project explicitly enforces that policy. Avoid making a previously optional dependency unconditional or enabling its default features accidentally. When a feature changes public items or trait implementations, test the supported combinations that observe those differences. Use target-specific dependency tables and `cfg` expressions consistently with the existing manifest.

Do not assume `--all-features` is a valid product configuration: some repositories intentionally define incompatible feature sets. Follow their matrix.

## Protect compatibility

For published libraries, review changes to public signatures, trait implementations, type inference, feature availability, re-exports, default generic parameters, and enum exhaustiveness. Avoid exposing dependency-owned types or feature flags unless they are part of the intended API. Keep crate names, binary names, paths, metadata keys, and build-script outputs stable unless the request changes their contract.

Treat `Cargo.lock` changes according to repository policy. Do not refresh unrelated packages or widen version requirements to make a local build convenient.

## Build scripts and generated code

Build scripts execute during compilation. Keep their inputs declared, outputs deterministic where practical, rerun directives accurate, and host-versus-target assumptions explicit. Do not read network resources, credentials, or undeclared host state unless the repository contract deliberately requires it. For generated bindings or code, preserve the canonical regeneration command and avoid hand-editing generated output without its source.

## Verification

Use the repository's feature and target matrix. At minimum, compile the affected package in every changed configuration that is locally available and run the tests that exercise public behavior. Report unavailable targets rather than substituting the host build.

Primary anchors: [Cargo reference](https://doc.rust-lang.org/cargo/reference/), [Cargo features](https://doc.rust-lang.org/cargo/reference/features.html), and [Rust reference: conditional compilation](https://doc.rust-lang.org/reference/conditional-compilation.html).
