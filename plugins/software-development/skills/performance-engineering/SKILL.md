---
name: performance-engineering
description: Use when latency, throughput, CPU, memory, allocation, I/O, scale, or cost is explicit. Requires measurement; exclude unknown-cause regressions and speculative tuning.
---

# Performance Engineering

Make performance work falsifiable. Define what should improve, measure a
representative baseline, localize the limiting resource, and compare the result
without silently spending correctness or another resource.

## Define the performance contract

Before changing implementation, establish:

- the metric and unit, such as p99 latency, throughput, peak resident memory,
  allocations, artifact size, energy, or cost per operation;
- the target or decision threshold;
- the workload, input distribution, concurrency, scale, and steady-state or
  cold-start conditions that matter;
- correctness, security, reliability, readability, and resource guardrails;
- the environment and repository-native command used for comparison.

If the request is merely “make it faster,” derive a decision-relevant criterion
from available product or operational evidence. Do not invent a target whose
tradeoffs belong to the user or system owner.

## Establish a trustworthy baseline

Run the unchanged system under the chosen workload. Preserve raw results and
enough environment metadata to reproduce the comparison. Use repeated or
interleaved measurements when noise could change the decision.

Read [measurement-validity.md](<skills-file-root>/references/measurement-validity.md) before
designing a new benchmark, comparing noisy results, measuring JIT or managed
runtimes, or translating a microbenchmark result into a system-level claim.
Read [complexity-and-data-structures.md](<skills-file-root>/references/complexity-and-data-structures.md)
when the requested result depends on input growth, repeated passes, allocation
shape, or choosing a data structure or algorithm.

## Find the limiting path

Profile the representative workload with the least-distorting tool available.
Select CPU, allocation, heap, I/O, lock, scheduler, trace, or system counters
based on the metric. Attribute cost to a path and input before optimizing it.

Algorithmic complexity helps predict scaling, but an asymptotic improvement is
not runtime evidence. Constant factors, cache behavior, allocation, vectorization,
contention, and realistic input sizes can reverse an intuition.

## Run one supported experiment

1. State the bottleneck hypothesis and predicted metric effect.
2. Choose the smallest change that tests it without violating guardrails.
3. Keep the benchmark and environment comparable to the baseline.
4. Verify functional correctness before accepting the measurement.
5. Compare magnitude, variability, and any shifted resource cost.
6. Keep the change only when the evidence justifies its complexity and tradeoffs.

Re-profile after a meaningful win: the bottleneck may move. Stop when the target
is met, the next opportunity is outside scope, uncertainty exceeds the apparent
gain, or further cost is not justified.

## Match evidence to the claim

- Use end-to-end or workload benchmarks for user-visible latency and throughput.
- Use microbenchmarks to isolate a known hot operation, not to stand in for the
  whole product.
- Report latency distributions for tail-sensitive systems; an average can hide
  the requested regression.
- Include memory, I/O, cost, or energy deltas when the optimization can exchange
  one resource for another.
- Test scaling at relevant sizes when the claim concerns complexity or capacity.

## Compose with neighboring skills

- When a slowdown's cause is unknown, systematic debugging leads until evidence
  identifies the cause. Use this skill to validate the proposed performance fix.
- Let refactoring own a local behavior-neutral restructuring when performance
  evidence has already selected it; this skill still owns the before/after claim.
- Let language, runtime, database, and platform skills select appropriate tools
  and interpret domain-specific profiles.
- Let test-driven development protect intentional behavior changes; benchmarks
  do not replace correctness tests.

## Completion evidence

Report the criterion, workload, environment, baseline, profile evidence, change,
after measurements, variability, and guardrail results. State whether the target
was met and name limitations that prevent a broader claim.

Do not promise improvement from Big-O analysis alone, require one statistical
test or percentage threshold for every workload, optimize dead code, discard
negative results, or hide memory, security, reliability, and maintenance costs.
