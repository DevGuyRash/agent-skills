# C++ Ownership and Lifetimes

Read this reference for resource ownership, borrowed views, callbacks, moves, exceptions, synchronization, or suspected lifetime failure.

## Map the ownership graph

For each object or resource, identify its owner, observers, destruction point, thread affinity, and whether ownership can transfer or be shared.

- Prefer direct values when identity and independent lifetime are unnecessary.
- Use RAII owners for resources requiring release on every exit path.
- Use `unique_ptr` for exclusive heap ownership when indirect storage is needed.
- Use `shared_ptr` only for genuine shared lifetime; define how cycles are prevented.
- Use raw pointers/references or view types for non-ownership when nullability and valid duration remain clear.

Smart pointers do not repair a confused ownership graph. Avoid heap allocation and reference counting when a value or scoped owner is sufficient.

## Protect borrowed state

Check that `string_view`, `span`, iterator, range, reference, pointer, and callback captures cannot outlive or be invalidated by their owner.
Review temporaries, container growth/erase, moves, asynchronous retention, lambda capture, and return-value boundaries.
Do not infer safety from `const`; it restricts mutation through that access path, not object lifetime or mutation through aliases.

After move, rely only on guarantees of the moved-from type and repository contract. Do not add blanket resets unless callers need a stronger postcondition.

## Exceptions and RAII

Construct objects so partially completed acquisition is owned immediately by a local RAII object.
Keep destructors non-throwing under the repository's exception policy.
When translating exceptions, retain actionable context and avoid slicing or catch-all suppression.
When exceptions are disabled, use the established status/result mechanism consistently rather than introducing a parallel model.

Declare `noexcept` for a semantic guarantee, not an optimization ritual. Review called operations and future maintenance implications.

## Concurrency

A data race is undefined behavior. Tie shared mutable state to a synchronization contract and keep lock ownership scoped.
Avoid calling unknown/reentrant code while holding a lock unless the protocol requires it.
For atomics, state the invariant and ordering relation; do not treat `volatile` as synchronization.
Ensure worker completion precedes destruction of observed state.

## Verification

Test copy/move, self-assignment if supported, partial construction, exception/error exits, view invalidation, callback retention, teardown, and contention relevant to the API. Use configured sanitizers and static analysis, then still review every lifetime edge they may not execute.

Primary anchor: [C++ Core Guidelines: resource management](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#S-resource), plus the repository-selected standard library and compiler documentation.
