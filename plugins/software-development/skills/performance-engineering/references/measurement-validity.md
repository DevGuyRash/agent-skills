# Measurement Validity

Read this reference when designing or interpreting performance measurements.

## Preserve comparability

Use the same code mode, compiler settings, dependency versions, machine class,
power policy, resource limits, background load, data set, and workload shape for
baseline and candidate when possible. Record unavoidable differences and avoid
attributing their effect to the code change.

Interleave baseline and candidate runs when machine state drifts over time.
Repeat enough times to distinguish the decision-relevant effect from ordinary
variance; no universal repetition count fits every workload.

## Control runtime state

Decide whether the product promise concerns cold start, warm steady state, or
both. Treat cache population, JIT compilation, tiered optimization, garbage
collection, connection pools, lazy initialization, and data warming consistently.
Do not discard warmup if cold behavior is the requested metric.

Prevent compilers from removing or precomputing microbenchmark work. Keep setup,
input generation, and teardown outside the timed region unless they are part of
the product operation. Consume results in the framework-supported way.

## Use representative inputs

Cover realistic sizes, distributions, hit rates, contention, and failure paths.
Uniform random data can hide skew, locality, compression, duplicate keys, and
hot partitions. A benchmark corpus is part of the claim; version or describe it
well enough to reproduce the result without exposing sensitive production data.

## Choose useful statistics

Report the statistic the criterion names. For latency-sensitive work, include
relevant percentiles and sample counts; for throughput, include concurrency and
backpressure; for memory, distinguish peak, retained, allocated, and resident
memory. Means and standard deviations alone may not describe multimodal or
heavy-tailed results.

Use confidence intervals, resampling, or a suitable comparison test when the
decision needs statistical support. Statistical significance does not establish
practical importance, and a percentage improvement without variability can be
noise.

## Profile without confusing observer cost

Sampling profilers generally distort less than exhaustive tracing, while traces
can reveal sequencing and waits that samples miss. Compare a profiled run with
an unprofiled measurement when overhead may alter behavior. A profiler identifies
where resources are spent; it does not by itself prove which change will help.

## Make the scope of the claim explicit

A microbenchmark supports a claim about the measured operation under its inputs.
Carry the candidate into an integration, load, or end-to-end measurement before
claiming product-level impact. If the broader signal disagrees, investigate
frequency, shifted bottlenecks, resource contention, and measurement mismatch.

## Preserve correctness and tradeoffs

Run functional checks on the optimized path. Compare output, errors, side
effects, numerical tolerance, concurrency guarantees, and failure behavior as
appropriate. Report exchanged resources—such as lower CPU for higher memory—or
added complexity alongside the measured benefit.
