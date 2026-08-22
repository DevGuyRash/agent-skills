# C Ownership and Undefined Behavior

Read this reference for pointers, allocation, buffers, concurrency, parsers, or any path where object lifetime and bounds determine correctness.

## Write the resource contract

For every pointer crossing a function boundary, determine:

- object or buffer it may designate, including nullability;
- readable/writable extent and alignment;
- whether it is borrowed, retained, consumed, returned, or aliased;
- object lifetime and who ends it;
- allocator/deallocator family;
- synchronization required while aliases exist.

Keep this contract in types, names, nearby documentation, or established annotations. A comment that says only “pointer to data” does not carry the needed information.

## Guard the dangerous transitions

Before allocation or indexing, validate additions and multiplications without performing the overflowing expression first. Convert between signed, unsigned, and narrower types only after range checks appropriate to the destination. Keep pointer arithmetic within the relevant array-object rules; an integer address that appears in range is not by itself a valid C object access.

Do not read indeterminate values, use storage after lifetime ends, access outside an object, form invalid shifts, violate effective-type/aliasing rules, or race non-atomic accesses. Compiler optimization may exploit undefined behavior even when a debug build appears correct.

Use `memcpy` for bytewise representation transfer when its source, destination, size, and resulting object validity are established. Do not use casts or unions as portable type-punning by assumption.

## Strings and binary data

Carry lengths for untrusted or binary data. Establish whether a buffer includes a terminator and whether embedded NUL bytes are allowed. Check `snprintf`-style results for negative failure and required-length/truncation behavior according to the supported implementation. Do not call string APIs on untrusted storage until termination within the accessible extent is proven.

## Cleanup and partial construction

Initialize owned handles to a state the cleanup path can distinguish. Acquire resources in a visible order and release only those successfully acquired, in an order allowed by their dependencies. Set a pointer to null after free only when that prevents a real local reuse; it does not invalidate aliases and is not a global use-after-free defense.

## Concurrency

In C, a data race on ordinary memory is undefined behavior. Use the repository's mutex/atomic primitives and their memory-order contract. Do not add `volatile` as thread synchronization; it serves different implementation-defined and device-facing purposes. Define object lifetime relative to worker completion so teardown cannot race access.

## Verification

Test boundary sizes and injected failure where the harness supports it. Use supported AddressSanitizer, UndefinedBehaviorSanitizer, MemorySanitizer, ThreadSanitizer, static analysis, or fuzzing selectively; tool availability and coverage vary by compiler and platform. Review the contract even when tools are clean.

Primary anchors: [SEI CERT C Coding Standard](https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard), [Clang UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html), and the repository-selected C standard implementation documentation.
