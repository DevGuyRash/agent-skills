---
name: c-development
description: Use for substantive C source, build-classified headers, or tooling. Covers ownership, bounds, undefined behavior, ABI, and errors; exclude C++-only work.
---

# C Development

Build and review C whose ownership, bounds, lifetime, ABI, and failure contracts are explicit. Preserve the repository's selected standard, compiler extensions, platforms, and build system.

## Classify the language first

Treat `.c` and the compiler invocation as stronger evidence than syntax resemblance. For `.h` files, inspect compile commands, build targets, includers, `extern "C"` use, and public compatibility requirements. Use `$cpp-development` instead when the header is C++-only. Compose both skills when a header is intentionally consumed by C and C++. Do not infer the language from `.h` alone.

## Establish the contract

Inspect repository instructions, build files, CI, compiler flags, and nearby code. Determine:

- selected C standard and permitted compiler/platform extensions;
- compiler families, warning policy, architectures, data models, and endianness;
- allocator, ownership, threading, error, logging, and cleanup conventions;
- public header, ABI, binary compatibility, and foreign-consumer requirements;
- repository-owned format, build, static-analysis, test, sanitizer, and fuzz commands.

Preserve those choices unless the request explicitly changes them. Do not upgrade the language standard, compiler floor, dependency set, warnings, or ABI incidentally.

## Load detail only when needed

| Situation | Read |
| --- | --- |
| Pointer arithmetic, allocation, buffers, ownership transfer, concurrency, parsing, or suspected undefined behavior | `<skills-file-root>/references/ownership-and-undefined-behavior.md` |
| Public headers, FFI, shared libraries, struct layout, wire/file formats, compiler or OS portability | `<skills-file-root>/references/abi-and-portability.md` |

Load only the reference that owns the current decision.

## Shape ownership and cleanup

Give each resource one identifiable owner and one release contract. Document whether parameters and returned pointers are borrowed, transferred, retained, nullable, counted, or NUL-terminated where types cannot express it. Keep allocation and deallocation families paired. Use a single cleanup path, including `goto cleanup`, when it makes partially acquired resources visibly correct.

Initialize state before a failure path can inspect or release it. After transfer or release, prevent accidental reuse through control flow and local state appropriate to the codebase. Do not add reference counting, global singletons, or wrapper layers without a real ownership need.

## Make bounds and arithmetic explicit

Validate sizes before allocation, multiplication, addition, narrowing, pointer movement, and indexing. Keep byte counts distinct from element counts. Account for the terminating NUL only when the representation requires one. Use length-aware operations whose truncation and termination behavior is understood on every target.

Treat signedness, integer promotions, shifts, overflow, and sentinel conversions as semantic decisions. Do not assume a successful allocation proves the requested size calculation was valid.

## Preserve failure behavior

Follow the repository's status-code, `errno`, out-parameter, nullable-result, or structured-error convention. Check return values that affect correctness and capture transient error indicators before another call overwrites them. Leave output parameters and resources in their documented state on every failure path. Do not log and continue when the caller contract requires propagation or rollback.

## Keep portability deliberate

Use fixed-width integers for exact-width external representations, not as a universal replacement for natural size types. Do not assume pointer width, `char` signedness, alignment, byte order, structure padding, or atomic lock-freedom. Treat compiler extensions, pragmas, attributes, packed layouts, VLAs, and platform APIs according to the declared target matrix.

Avoid universal style mandates such as banning all macros or `goto`, requiring the newest C standard, or forcing one allocation pattern. Judge each mechanism by its contract and repository policy.

## Verify with repository evidence

Run the repository's narrowest relevant build and tests under the configured warnings. Compile every impacted target/configuration available locally, including C++ consumers of shared headers where applicable. Use configured static analysis, sanitizers, and fuzzers for high-risk paths; a clean run samples behavior and does not prove absence of undefined behavior.

Exercise empty, maximum, malformed, partial-failure, allocation-failure, aliasing, and cleanup cases relevant to the change. For hostile input or privileged/native boundaries, also compose the applicable security workflow. Report unsupported compilers, architectures, sanitizers, or ABI consumers explicitly.

## Completion

Report ownership and bounds contracts, standard/toolchain choices preserved, checks run, and any target or undefined-behavior risk left unverified.
