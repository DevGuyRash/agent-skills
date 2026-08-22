# Complexity and Data Structures

Read this reference when input growth, repeated passes, allocation shape, or a data-structure or algorithm choice may determine the performance result.

## Model the real operations

Name the input dimensions separately: records, keys, graph vertices and edges, payload bytes, concurrency, or retained history. State which operations dominate the workload and how often they occur. A useful complexity claim includes its assumptions, such as average versus worst-case lookup, ordered versus random input, bounded key size, or amortized growth.

Count full traversals, nested work, copying, allocation, sorting, hashing, and I/O as well as the most visible loop. Avoid replacing a clear linear pass with several nominally linear passes unless measured locality, simplicity, or reuse justifies it.

## Select structures from workload evidence

Compare candidates by the operations the workload actually needs:

- contiguous sequences for traversal, locality, and compact storage;
- maps or sets for keyed membership when hashing, equality, and memory cost fit;
- ordered structures when range queries, stable order, or worst-case bounds are part of the contract;
- queues, heaps, deques, bitsets, tries, or graph-specific structures only when their supported operations match a measured or scale-driven need.

Account for construction cost, memory overhead, cache behavior, mutation rate, ordering guarantees, adversarial inputs, and repository/library constraints. The asymptotically stronger structure is not automatically faster at the sizes that matter.

## Turn analysis into evidence

Use complexity reasoning to predict where scaling should bend and which input sizes expose it. Then measure representative points before and after the change. Report both the analytical bound and runtime evidence, including any range in which constant factors make the previous approach preferable.

Do not claim an algorithmic win from a microbenchmark that omits construction, conversion, or output costs paid by the real workload. Preserve correctness and resource guardrails while reducing time or space.
