# FFI, ABI, Assembly, and Layout

Read this reference when Rust crosses a foreign ABI or relies on representation, calling convention, callback, symbol, instruction, target-feature, or allocator contracts.

## Define the boundary explicitly

Record the exact ABI, symbol names, target data model, ownership transfer, nullability, buffer lengths, string encoding, alignment, threading, callback lifetime, and error channel. Use generated or authoritative foreign declarations when available; keep handwritten declarations synchronized with their source headers.

An `unsafe extern` block asserts that every declaration matches reality. Mark an individual foreign item safe only when no extra caller obligation remains. For unsafe attributes such as exported names or link sections, document the program-wide symbol, linkage, and placement invariant rather than treating the attribute wrapper as proof.

`repr(C)` gives C-compatible layout rules for the annotated Rust type; it does not make every field value valid, stabilize a Rust ABI, or prove the foreign declaration matches. Do not pass Rust-layout enums, trait objects, slices, `String`, `Vec`, or references across an ABI unless a documented adapter defines their representation and lifetime.

## Contain foreign data

Validate nullability, lengths, integer conversions, discriminants, alignment, and initialization before constructing Rust references or values. Copy or wrap foreign data according to the ownership contract. Never free memory through a different allocator unless the interface guarantees compatibility.

Keep opaque foreign handles opaque. Pair acquisition and release in a safe owner when possible, and define whether release may occur on any thread. For callbacks, define registration, deregistration, concurrency, reentrancy, context-pointer lifetime, and the terminal event that proves callback quiescence before reclamation.

## Panic and error boundaries

Do not allow unwinding to cross a boundary whose ABI does not permit it. Use an unwind-permitting ABI only when cross-language unwinding is intentional and supported; do not assume `catch_unwind` can safely catch foreign exceptions. Foreign non-local jumps must not skip live Rust frames or destructors. Translate errors and panic policy at the boundary using the repository's established mechanism, and preserve foreign error indicators before another call overwrites them.

## Layout-sensitive code

Check size and alignment for every supported target, not only the host. Avoid transmute when field-wise conversion or byte APIs can express the contract. Account for padding, endianness, zero-sized fields that may share addresses, union interpretation, and Rust value validity. Never form a reference to an insufficiently aligned packed field; use raw access with the correct unaligned operation when the format requires it.

## Assembly, intrinsics, and target features

For inline assembly, state the instruction and ABI contract: inputs, outputs, clobbers, preserved registers, stack rules, memory effects, control flow, and permitted options. For intrinsics or `target_feature`, prove runtime hardware support before the call unless the enclosing target contract already guarantees it. Compile and test every supported architecture-specific path; a host-only success does not validate another instruction set or calling convention.

## Verification

Compile both sides from the authoritative declarations. Add size, alignment, or offset assertions only where those values are contractual. Test null, zero-length, maximum-length, callback-after-cancel, foreign failure, unwind policy, and release paths as applicable. Use target CI for ABI or instruction variants unavailable locally.

Primary anchors: [Rust Reference unsafety](https://doc.rust-lang.org/reference/unsafety.html), [Rustonomicon FFI](https://doc.rust-lang.org/nomicon/ffi.html), [Rust Reference type layout](https://doc.rust-lang.org/reference/type-layout.html), [inline assembly](https://doc.rust-lang.org/reference/inline-assembly.html), and the foreign platform's ABI specification.
