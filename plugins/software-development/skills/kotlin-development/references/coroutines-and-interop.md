# Kotlin Coroutines and Interop

## Harden platform null boundaries

- Treat Java platform types as unchecked evidence, not as non-null guarantees. Validate or adapt them at the narrowest boundary with domain context.
- Preserve and interpret Java nullness annotations according to the repository's compiler settings and annotation ecosystem.
- Do not spread defensive `!!` or nullable types through Kotlin solely because one Java boundary is uncertain.
- Check generic arguments, arrays, SAM conversions, raw types, and mutability when Java types cross the boundary.

## Own coroutine lifecycles

- Launch work in a scope whose owner, parent job, cancellation, and failure policy match the component lifecycle.
- Prefer structured concurrency. Use a detached or global scope only when process-lifetime ownership is explicit and independently supervised.
- Propagate suspending APIs rather than inserting `runBlocking` inside suspend-capable code. Use blocking bridges only at genuine synchronous entrypoints.
- Select a dispatcher for the operation and repository architecture; do not hardcode one when the caller or framework owns execution context.
- Keep blocking calls off a constrained coroutine dispatcher through the repository's established boundary.
- Observe failures from `launch`, `async`, channels, and flows according to their builder semantics; do not discard deferred results.

## Preserve cancellation

- Cancellation is cooperative and commonly represented by `CancellationException`. Do not swallow it in broad exception handling.
- Put cleanup in `finally`; use `NonCancellable` only for the smallest suspending cleanup that must complete.
- Bound retries, polling, buffers, fan-out, and flow collection. Check cancellation in CPU-heavy loops.
- Distinguish timeout, cancellation, upstream failure, and empty completion in public behavior.
- Do not use delays as synchronization in tests or production coordination.

## Maintain Java/JVM compatibility

- Inspect emitted JVM signatures when changing default arguments, properties, companion members, inline/value classes, wildcards, overloads, or suspend functions.
- Add `@JvmOverloads`, `@JvmStatic`, `@JvmName`, wildcard annotations, or `@Throws` only for a demonstrated Java-call-site contract.
- Remember that Kotlin does not enforce Java checked exceptions; Java consumers may still require declared exception metadata.
- Preserve Java bean/property expectations, null annotations, visibility, and overload resolution where callers depend on them.
- Treat inline public function bodies as compatibility surface because consumer bytecode may contain them.

## Keep Multiplatform boundaries honest

- Put portable behavior in the appropriate common source set and platform behavior in target source sets.
- Do not call JVM APIs from common code or assume all targets share threading, reflection, filesystem, exception, or test behavior.
- Use `expect`/`actual` only for a real platform boundary and preserve target completeness.
- Verify every affected target available in the repository, not only JVM compilation.

## Reject overbroad rules

- Do not require coroutines, Flow, `suspend`, `GlobalScope` bans without exception, or one dispatcher for all work.
- Do not blanket-add Java interop annotations or generate overloads that expand a public API without need.
- Do not treat Android lifecycle rules as core coroutine or Kotlin rules; route them to the Android skill.

Primary references: [coroutine basics](https://kotlinlang.org/docs/coroutines-basics.html), [cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html), [Java interop](https://kotlinlang.org/docs/java-interop.html), [Multiplatform source sets](https://kotlinlang.org/docs/multiplatform-discover-project.html).
