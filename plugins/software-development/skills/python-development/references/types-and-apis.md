# Types and Public APIs

Read this reference when changing annotations, signatures, imports, data models, decorators, or public behavior.

## Respect runtime semantics

Annotations can be inspected at runtime by frameworks, serializers, dependency injection, and user code. Before changing them, inspect the supported Python version and the repository's handling of postponed evaluation, forward references, and `typing.get_type_hints()`.

Use native syntax only when the minimum interpreter supports it. Keep `.pyi` stubs, overloads, generated clients, and `py.typed` distribution state aligned with implementations when they form part of the package contract.

## Preserve call and import contracts

Treat these as public when downstream code can observe them:

- Module paths, re-exports, `__all__`, plugin entry points, and import-time side effects.
- Positional-only, positional-or-keyword, and keyword-only parameters; names, defaults, and accepted sentinels.
- Sync versus async call shape, iterator versus materialized return, and context-manager protocol.
- Exceptions, warnings, mutability, ordering, equality, hashing, and serialization behavior.
- Decorator metadata and callable signatures used by introspection.

Avoid mutable default arguments unless shared state is the explicit contract. Use a distinct sentinel when `None` is a valid input rather than overloading its meaning.

## Apply typing proportionately

- Match the configured checker and strictness; mypy, Pyright, Pyre, and runtime validators do not interpret every construct identically.
- Prefer accurate, readable types over annotations that merely silence the checker.
- Use `Protocol`, generics, overloads, `TypedDict`, or constrained type variables when they express a real consumer contract.
- Use `Any`, casts, and ignores narrowly, with a reason when the limitation is not obvious.
- Do not annotate every local, replace ordinary classes with dataclasses, or introduce a typing dependency without repository evidence.

Structural typing, nominal interfaces, duck typing, and concrete classes are all valid. Select the smallest surface that communicates the actual substitution requirement.

## Document decisions, not syntax

Follow the repository's docstring convention. Public docstrings should state behavior, parameters only when useful, return meaning, raised exceptions that callers handle, and important side effects. Comments should explain invariants, compatibility constraints, or surprising tradeoffs.

Do not duplicate a fully expressive signature in prose or promise implementation details as permanent API.
