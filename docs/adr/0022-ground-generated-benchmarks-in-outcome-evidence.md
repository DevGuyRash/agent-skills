# ADR 0022: Do not prescribe benchmark seeds without behavioral gain

- Status: Accepted
- Date: 2026-08-17

## Decision

Do not add benchmark-seed instructions merely because a respected external system uses them. Retain the existing decision- and population-grounded task-generation contract unless a prospective intervention materially improves held-out benchmark quality. External guidance may reopen a test; it does not earn permanent context by being plausible or authoritative for a different product.

## Why

Artificial Analysis's Optima eval-prep skill independently emphasizes real instances, accepted outputs, outcome evidence, mistakes people actually make, and clean inputs that penalize invented findings. It also preserves realistic structure and messiness when confidential sources require generated stand-ins. Those are sensible sources for a benchmark designer to consider, while its fixed ZIP documents, intake sequence, read-only grader constraint, and exact handoff form serve the Optima product interface rather than this domain-free comparison system. The consulted source was revision [`28c7b9e`](https://github.com/ArtificialAnalysis/optima/blob/28c7b9e1c0f428607c6a5a79334da86815956008/skills/optima-eval-prep/SKILL.md).

A fresh high-reasoning matched trial compared the existing Split Testing instruction with a candidate that added the portable-looking Optima principles. Both produced substantial maintenance-triage benchmarks from the same historical record. The blind reviewer preferred the existing instruction: the candidate chose a less literal output interface and allowed the history's subtle imminent-failure pattern to survive its hard safety gate, while the existing version made every unsafe shutdown delay disqualifying. A condition-blind fact-check narrowed the interface criticism and corrected the raw case-count interpretation, but confirmed the consequential gate difference. The added wording therefore did not earn its context cost. One pair does not establish that the principle is harmful in general; it does establish that this intervention lacks the improvement evidence required for adoption.

## Consequences

The Split Testing source remains unchanged by the Optima review. Benchmark authors retain freedom to use real outcomes, clean controls, synthetic cases, or other evidence as the decision requires under the existing held-out-work and measurement-validity contracts.

Reopen this decision when a different, prospectively frozen wording or mechanism improves benchmark quality on more than one dissimilar held-out task without weakening interface fidelity, hazard coverage, discrimination, or context discipline.
