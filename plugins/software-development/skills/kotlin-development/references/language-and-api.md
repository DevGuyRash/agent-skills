# Kotlin Language and API Design

## Preserve the supported contract

- Treat configured Kotlin `languageVersion`, `apiVersion`, compiler/plugin version, platform targets, and explicit-API mode as compatibility constraints.
- Version-gate syntax, standard-library calls, opt-in APIs, compiler features, and generated behavior.
- For published libraries, preserve source, binary, behavioral, reflection, serialization, and Java-call-site compatibility.
- Check default arguments, named calls, component functions, extension resolution, inline bodies, and generated JVM signatures before changing public declarations.

## Model nullability and initialization

- Use nullable types when absence is part of the contract; validate unexpected nulls at the boundary rather than spreading uncertainty inward.
- Treat `!!` as an assertion with a runtime failure, not automatically an error or a proof. Keep it only where an invariant is established and clearer alternatives do not preserve intent.
- Use `lateinit` only when staged initialization is real and its runtime failure mode is acceptable; do not replace every nullable property with it.
- Remember that safe calls and Elvis expressions can hide an unexpected absence when the operation is required.
- Do not rely on smart casts across mutable, open, or concurrently changing properties when the compiler cannot establish stability.

## Understand values, equality, and collections

- `==` uses structural equality and `===` referential identity. Arrays require content-oriented APIs when element equality is intended.
- Data-class equality, hashing, copying, and destructuring derive from primary-constructor properties; `copy` is shallow.
- Avoid mutating values used in hash or ordering contracts while they are collection keys or members.
- Kotlin read-only collection interfaces do not guarantee immutable backing storage. Copy at a boundary when isolation is contractual.
- Use sequences for laziness or pipeline behavior that benefits from them; do not assume they are faster than eager collections.
- Preserve collection order, duplicate, null, and mutability behavior that callers observe.

## Design APIs without ceremony

- Prefer a class, interface, function, sealed hierarchy, value class, or type alias according to the actual domain and target support; none is a universal default.
- Use declaration-site and use-site variance to express real producer/consumer relationships without hiding unsafe casts.
- Keep extension functions discoverable and scoped. They dispatch statically and do not override members; import and receiver type can change resolution.
- Use scope functions when receiver/result behavior is immediately clear. Nested chains are not inherently more idiomatic.
- Preserve intentional default and named parameters; changing parameter names can break Kotlin source callers even when JVM descriptors remain stable.
- Avoid exposing mutable implementation state or platform-only types from common/public APIs without an explicit contract.

## Comments and style

- Follow repository formatting and lint configuration; the official conventions are defaults, not authority over local code.
- Document nullability, ownership, thread safety, blocking, coroutine context, exceptions, platform differences, and opt-in requirements when callers need them.
- Explain reasons and invariants rather than restating syntax.
- Keep a small change local; do not invent a DSL, builder, sealed hierarchy, or functional abstraction without a concrete payoff.

## Reject overbroad rules

- Do not ban `!!`, `lateinit`, mutable collections, inheritance, exceptions, or platform types categorically.
- Do not require data classes, expression bodies, exhaustive `when`, extension functions, scope functions, immutable collections, or Arrow everywhere.
- Do not enable explicit API mode or change repository-wide style as part of an unrelated fix.

Primary references: [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html), [null safety](https://kotlinlang.org/docs/null-safety.html), [equality](https://kotlinlang.org/docs/equality.html), [collections overview](https://kotlinlang.org/docs/collections-overview.html).
