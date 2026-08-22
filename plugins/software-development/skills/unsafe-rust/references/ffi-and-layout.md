# FFI and Layout

Read this reference when Rust crosses a foreign ABI or relies on representation, calling-convention, callback, or allocator contracts.

## Define the boundary explicitly

Record the exact ABI, symbol names, target data model, ownership transfer, nullability, buffer lengths, string encoding, alignment, threading, callback lifetime, and error channel. Use generated or authoritative foreign declarations when available; keep handwritten declarations synchronized with their source headers.

`repr(C)` gives C-compatible layout rules for the annotated Rust type; it does not make every field value valid, stabilize a Rust ABI, or prove the foreign declaration matches. Do not pass Rust-layout enums, trait objects, slices, `String`, `Vec`, or references across an ABI unless a documented adapter defines their representation and lifetime.

## Contain foreign data

Validate nullability, lengths, integer conversions, discriminants, alignment, and initialization before constructing Rust references or values. Copy or wrap foreign data according to the ownership contract. Never free memory through a different allocator unless the interface guarantees compatibility.

Keep opaque foreign handles opaque. Pair acquisition and release in a safe owner when possible, and define whether release may occur on any thread. For callbacks, define registration, deregistration, concurrency, reentrancy, context-pointer lifetime, and what proves no later callback can occur.

## Panic and error boundaries

Do not allow unwinding to cross a boundary whose ABI does not permit it. Translate errors and panic policy at the boundary using the repository's established mechanism. Preserve foreign error indicators before another call overwrites them.

## Layout-sensitive code

Check size and alignment for every supported target, not only the host. Avoid transmute when field-wise conversion or byte APIs can express the contract. Account for padding, endianness, packed-field alignment, union active-member rules on the foreign side, and validity requirements on the Rust side.

## Verification

Compile both sides from the authoritative declarations. Add size/alignment/offset assertions only where those values are contractual. Test null, zero-length, maximum-length, callback-after-cancel, foreign failure, and release paths as applicable. Use target CI for ABI variants unavailable locally.

Primary anchors: [Rustonomicon FFI](https://doc.rust-lang.org/nomicon/ffi.html), [Rust Reference type layout](https://doc.rust-lang.org/reference/type-layout.html), and the foreign platform's ABI specification.
