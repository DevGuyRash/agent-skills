# Types and Public APIs

Read this reference for strict typing, coercion, declarations, PHPDoc, signatures, named arguments, inheritance, or compatibility.

## Apply PHP typing accurately

Scalar typing is coercive by default. `declare(strict_types=1)` is per file, affects scalar declarations, and uses the calling file's mode for argument calls. It is not a property attached solely to the function declaration.

Follow repository policy. Adding strict mode to a legacy caller can change behavior; omitting it from a strict codebase can weaken the intended boundary.

- Use native parameter, return, property, and constant types supported by the minimum PHP version.
- Preserve nullable, union, intersection, DNF, literal, `mixed`, `never`, and variance semantics deliberately.
- Use PHPDoc for analyzer generics, shapes, templates, conditional types, or other information not expressible natively.
- Match the selected PHPStan/Psalm dialect and generated-file ownership.
- Do not duplicate obvious native declarations or claim precision the runtime does not uphold.

## Preserve public API behavior

PHP 8 named arguments bind to parameter names. Treat public names, position, defaults, by-reference markers, and variadics as compatibility surface even where inheritance checks do not catch name changes.

Also preserve:

- Namespace and class names, autoload paths, aliases, visibility, constants, and property initialization.
- Return value and mutation behavior, exception/deprecation behavior, and magic-method signatures.
- Interface, parent, and trait contracts, including covariance, contravariance, and property invariance applicable to the supported version.
- Attributes, reflection metadata, serialization, callable shape, and framework-discovered conventions.

Use deprecation and migration paths for intentional library changes rather than silent signature rewrites.

## Control coercion at boundaries

PHP comparisons and scalar contexts can coerce values. Parse and validate external strings into the intended domain before authorization, identity, range, or persistence decisions. Prefer strict comparison when type identity matters, but do not ban loose comparison where coercion is the explicit contract.

Distinguish missing, `null`, `false`, zero, and empty strings when the domain distinguishes them. Avoid blanket truthiness rewrites that collapse valid states.

## Document durable contracts

Follow repository docblock style. Document analyzer-only types, templates, side effects, ownership, deprecations, and exceptions callers handle. Do not add docblocks to every symbol, restate native signatures, or treat an unaccepted draft standard as universal PHP policy.
