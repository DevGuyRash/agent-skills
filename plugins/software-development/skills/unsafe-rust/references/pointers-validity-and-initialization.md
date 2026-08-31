# Pointers, Validity, and Initialization

Read this reference for raw-pointer access, address conversion, manual allocation or ownership, `MaybeUninit`, `UnsafeCell`, volatile access, or construction of references and slices.

## Preserve origin and range

A pointer is not merely an integer address. Prefer pointer APIs that preserve provenance; use exposed- or no-provenance APIs only when the external address protocol requires them and follow that API's exact access limits. Do not present an experimental aliasing model as the Rust language contract.

Prove the complete accessed range lies within the allocation required by the operation, with checked element-to-byte and layout arithmetic. Pointer offset and difference operations, slices, and dynamically sized values have same-allocation, metadata, and `isize::MAX` constraints. Zero length or a zero-sized type does not waive the non-null and alignment requirements for references and slices.

## Create references only after validity

A raw pointer may be null, dangling, misaligned, or point at invalid or uninitialized bytes; a reference may not. Establish liveness, alignment, pointee validity, range, and aliasing before creating `&T`, `&mut T`, `Box<T>`, or a slice, even if safe code will not immediately dereference it. Tie any returned lifetime to an owner or borrow that actually keeps the storage and access rights alive.

Use raw-borrow syntax when taking a reference would itself be invalid, such as for a packed field or mutable static, but remember that this only postpones the proof until access. `UnsafeCell` relaxes shared immutability for its contents; it does not permit aliasing `&mut` references or data races.

## Track initialization and ownership

For `MaybeUninit` or spare capacity, track the exact initialized subset as authoritative state. On failure or panic, drop each initialized value exactly once and no uninitialized value; dropping `MaybeUninit<T>` does not drop `T`. Do not assume all-zero bytes are a valid `T`, and do not duplicate ownership with repeated pointer reads or `assume_init_read` for non-`Copy` values.

When reconstructing `Box`, `Vec`, `Rc`, `Arc`, or another owner from raw parts, prove the required allocation origin, allocator, layout and alignment, length, capacity, initialized elements, metadata, and uniqueness. Reconstruct or deallocate exactly once, and keep the terminal owner clear on every error path.

## Volatile and hardware access

Volatile access is externally observable, not atomic or synchronizing. For Rust allocations, ordinary provenance, aliasing, validity, and race rules still apply. For memory outside Rust allocations, follow the hardware contract and the volatile operation's special requirements; state access width, alignment, side effects, ordering, and what prevents traps or conflicting access.

Primary anchors: [`std::ptr`](https://doc.rust-lang.org/std/ptr/), [behavior considered undefined](https://doc.rust-lang.org/reference/behavior-considered-undefined.html), [`MaybeUninit`](https://doc.rust-lang.org/std/mem/union.MaybeUninit.html), [`UnsafeCell`](https://doc.rust-lang.org/std/cell/struct.UnsafeCell.html), and [`Vec::from_raw_parts`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.from_raw_parts).
