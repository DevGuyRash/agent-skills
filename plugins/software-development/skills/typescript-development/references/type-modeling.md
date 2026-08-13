# TypeScript Type Modeling

Load this reference when designing or repairing domain types, unions, generics, narrowing, optional properties, or type-level utilities.

## Model Valid States

- Start from the domain's valid values and transitions rather than the current storage shape.
- Use a discriminant when variants require different fields or behavior. Keep the discriminant stable if callers serialize or switch on it.
- Use exhaustive checks where missing a new variant would be a defect; follow the repository's established assertion or `never` pattern.
- Avoid broad bags of optional fields when only particular combinations are valid.
- Distinguish `property?: T` from `property: T | undefined`; assignment behavior can also depend on `exactOptionalPropertyTypes`.
- Model absence as `null`, `undefined`, an omitted property, or a tagged result according to the actual boundary contract.

## Narrow from Evidence

- Narrow with control flow, discriminants, `typeof`, `instanceof`, property checks, or a validated predicate that actually proves the claimed type.
- Keep user-defined type guards small and test them as runtime code. An incorrect predicate can grant unsound access.
- Use assertion functions only when failure behavior and proof are explicit.
- Prefer `satisfies` when checking a value against a shape while retaining useful inference.
- Use assertions only when external evidence is stronger than the compiler can express. Keep the assertion near that evidence.
- Avoid chained casts through `unknown` as a routine compatibility technique.

## Use Generics to Preserve Relationships

- Introduce a type parameter when callers benefit from a relationship across parameters, properties, callbacks, or return values.
- Constrain a parameter only as much as the implementation requires.
- Prefer a concrete type when a parameter appears once and communicates no relationship.
- Preserve inference at call sites; unnecessary explicit generic arguments and return annotations can make APIs brittle.
- Use overloads when callers receive materially different types from distinct call forms and implementation checks uphold them. Otherwise prefer a union or options object that callers can understand.

## Advanced Types

- Use mapped and conditional types when they remove repeated, drift-prone declarations and remain readable in diagnostics.
- Beware distributive conditional types, recursive instantiation, large unions, and template-literal expansion when compiler performance matters.
- Keep nominal branding local to domains that truly require non-interchangeable structural values.
- Do not expose implementation-heavy utility types when a named public domain type would give callers a clearer contract.

Primary language authority: [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html) and [TSConfig reference](https://www.typescriptlang.org/tsconfig/).
