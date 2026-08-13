# APIs and Types

Read this reference for method signatures, keywords, blocks, constants, metaprogramming, RBS, Sorbet, or public compatibility.

## Preserve Ruby call semantics

Ruby 3 separates positional hashes from keyword arguments. Treat parameter kind and forwarding as behavior:

- Preserve positional, optional, rest, keyword, required-keyword, keyword-rest, and block parameters.
- Use `...` or explicit forwarding only when supported by the minimum Ruby and compatible with introspection needs.
- Keep legacy `ruby2_keywords` behavior only where the supported range and delegation contract require it.
- Do not rename public keywords casually; callers may bind them by name.

Blocks also form API. Preserve whether a method requires a block, yields values, returns an Enumerator without one, forwards the block, performs non-local control flow, or retains the block beyond the call.

## Protect public surfaces

Consider require paths, constants, method visibility, inheritance hooks, mixin order, refinements, callbacks, and monkey patches. Public behavior may include mutability, object identity, equality/hash behavior, ordering, laziness, and exceptions.

When using `method_missing`, implement compatible discovery such as `respond_to_missing?` and preserve forwarding. Prefer ordinary methods when the dynamic surface is finite and known. Avoid changing global core classes for local convenience.

## Use typing by repository contract

RBS, Steep, Sorbet RBI, inline annotations, and runtime validation are distinct systems. Inspect generated-file ownership and the configured checker before editing signatures.

- Keep implementation, checked signatures, and published gem artifacts aligned.
- Model useful public boundaries and complex internal contracts; do not type every local by default.
- Preserve nilability, block types, generics, overload behavior, and variance expected by the selected system.
- Use escape hatches narrowly and explain non-obvious checker limitations.
- Do not introduce a second type system or convert generated signatures by hand.

Duck typing, modules, concrete classes, data objects, Struct, and framework models are all valid. Choose from repository needs, not a universal architecture.

## Document durable behavior

Follow the project's RDoc, YARD, or plain-comment convention. Document public behavior, side effects, raised exceptions callers handle, mutation, thread safety, and non-obvious constraints. Avoid narrating Ruby syntax or promising private implementation details.
