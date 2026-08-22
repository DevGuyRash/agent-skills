# Interpretation and Reporting

Use this reference when aggregation, causal diagnosis, uncertainty, or the durable handoff remains unresolved.

## Interpret at the assigned level

Interpret results at the level where conditions were independently assigned. Preserve case, round, executor, reviewer, and shared-context dependence. More artifacts or judgments do not create more independent units.

Decide semantic correctness and material outcome quality first. Then consider retries, trajectory, tool use, time, tokens, cost, and operational burden when they change the choice. A polished artifact produced after an orchestrator rescued a failed run is evidence about the rescued system, not the original condition.

The same applies when a review layer makes an already-available fact salient. Credit the resulting artifact improvement to the review-assisted system, but do not report reviewer agreement as new evidence about the alternatives or as authority for an absent decision-maker's values. If the claimed foundational repair is earlier than the review layer, test that earlier change without the rescue before generalizing.

Bind comparative claims to what each unit actually encountered. An executor assigned one alternative cannot be counted as choosing it over alternatives it never saw. A later reviewer can compare those artifacts without retroactively giving the executors a shared denominator. Separate diagnostic failure discovery from prevalence and representative generalization.

Report effects and uncertainty at a strength the design supports. A small exploratory set can reveal mechanisms, counterexamples, or promising directions without establishing a stable population rank. When formal estimates matter, respect pairing, clustering, repeated measures, missing runs, adaptive stopping, and multiple contrasts. Majority vote, rubric total, leaderboard position, token ratio, or smallest p-value cannot decide the result alone.

Keep every material regression visible. A valid counterexample to a required property can outweigh many routine successes without estimating its frequency. If alternatives trade off rather than one dominating, return that frontier instead of inventing a scalar winner.

After reveal, resolve preferences against the concealed mapping and position schedule. Exclude a preference that follows a label, position, unsupported attribution, or false decisive premise from condition-quality evidence. Preserve it as evidence about the measurement system. A private oracle can override a reviewer only after its agreement with the public task and governing authority has been independently established.

Stop when the evidence supports the current decision and remaining uncertainty would not change it. The correct outcome may be a winner, context-dependent direction, redesign, further discriminating round, or no distinguishable difference. Reopen when the tested population, condition, task, host, model, harness, criterion, or consequential upstream fact changes.

## Correct foundations, not reports

Trace a consequential difference through the condition, the execution behavior it changed, and the resulting outcome far enough to identify the earliest actionable cause supported by evidence. A plausible root-cause story, repeated surface symptom, or reviewer preference is not proof. Use traces, counterexamples, condition reduction, or a targeted follow-up to distinguish rival causes.

Treat diagnosis and repair as separate claims. Where feasible, change the earliest alleged cause while preserving unrelated conditions and test whether the predicted behavior and outcome change without a new material regression. Recheck the boundary that exposed the failure and independent representative work not used to design the change. Without intervention or held-out confirmation, keep the causal or generalization conclusion provisional.

No-effect and harmful-effect results are valuable. They may justify reducing, redesigning, or removing an intervention instead of adding more instructions, agents, rubrics, or presentation.

[CausalFlow](https://arxiv.org/abs/2605.25338v1) provides fixed-version external evidence that validated minimal counterfactual repairs can outperform heuristic refinement across several agent-task families. It supports demanding a tested intervention; it does not make a local causal story true.

## Durable handoff

Write a user-visible Markdown report whose shape follows the decision. It must leave the reader able to recover:

- the direction or claim supported at the tested scope;
- the outcomes, regressions, tradeoffs, and costs that drive it;
- the assignment, exposure, concealment, and dependence limits needed to interpret it;
- direct paths to retained prompts, artifacts, rubric, checks, traces, judgments, mappings, and data;
- material uncertainty and the condition that would reopen the result.

These are information needs, not mandatory headings or order. Keep raw evidence in files and quote only the smallest decisive portions. Make delivered links resolve from the report; temporary evaluator paths or uncopied local logs are not handoff evidence.

Use a compact table when exact comparisons are small. Add a chart, topology view, or other visual only when it materially clarifies distributions, dependence, scaling, uncertainty, or tradeoffs. SVG is a portable vector default. Generate figures from retained data with an available Python library or a small standard-library emitter, retain the generation source or command, label units, sample size, missingness, uncertainty, and transformations, and inspect the rendered result. Do not add a visualization because the package mentions one.

Apply the delivery invariant in `SKILL.md` to the artifact the reader will actually receive. A link, script, notebook, command, or generated figure that works only while producer-only paths remain visible is not delivered evidence. The artifact may retain what it needs, identify stable external authority, or state a narrower dependency and verification claim. Preserve failed boundary checks as open evidence rather than letting a later successful but weaker check erase them.

## Evaluation-system validity

The task, launcher, tools, sandbox, retries, checker, rubric, reviewer brief, and report transform are part of the measured system. Inspect samples and traces for contamination, shortcuts, evaluation awareness, broken authority, false checker acceptance, condition-specific rescue, and criteria that reward the wrong outcome. Exclude or qualify compromised observations rather than averaging them into a reassuring result.

[OpenAI's evaluation-validity guidance](https://openai.com/index/trustworthy-third-party-evaluations-foundations/) supports disclosing the claim, tested system, harness, budget, elicitation, and validity checks. The local contract remains runtime authority; the rolling source is a reopening signal.
