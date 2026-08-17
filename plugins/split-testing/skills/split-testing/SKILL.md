---
name: split-testing
description: >-
  Design and run blinded comparative tests of any alternatives with variable
  conditions, runs, rounds, models, agents, and reviewers, including when a
  decision has no ready-made test tasks. Use for split testing, A/B or multi-way
  comparisons, repeated trials, blind evaluation, or evidence that one option
  performs better than another.
---

# Split Testing

Produce evidence that helps the user choose among any number or kind of alternatives. The decision,
not experiment ceremony, determines the conditions, cases, execution units, repetitions, models,
reviewers, rounds, and report. A large panel, precise score, or polished artifact is not success when
the evidence does not observe the property the user cares about.

## Decision and design

Establish the decision the result will change, the population it is meant to cover, the alternatives
or factors under comparison, and the smallest unit that can independently receive a condition. Keep
several outputs from one agent, team, session, or shared state as repeated observations of that unit,
not independent trials.

Before consequential cost or execution, give the user one coherent recommended design. Include the
defaults and assumptions that could change validity, safety, cost, or what the result means; ask only
questions whose answers could change that design. Begin once the user accepts it or delegates those
choices. Keep experiment rationale and development expectations in controller context, not blind
task prompts.

The topology is open: conditions may be paired, multi-way, factorial, bundled, or compared only along
the contrasts the decision needs. Runs may use individuals, teams, people, processes, models, hosts,
or systems. Honor user-selected models, efforts, reviewers, budgets, and conditions. Otherwise prefer
strong models and high reasoning effort for difficult semantic work when deployment fidelity, cost,
or latency is not itself under test.

Locate irreducible preference and decision authority. Reviewer agreement can assess whether evidence
and reasoning support a choice; it cannot supply an absent user's utility, risk tolerance, taste,
acceptance, or authority merely by being numerous or blinded. When alternatives remain on a real
frontier, apply only values the maker supplied or delegated, obtain evidence from the decision owner,
or preserve the result as conditional. Do not convert evaluator consensus into maker preference.

Do not instantiate an experiment merely because alternatives can be compared. When adopted
deterministic evidence already fixes the relevant factual consequences and only rightful preference
remains, the evidence result is the frontier itself. Additional executors or reviewers are warranted
only when they can observe a distinct unsettled property that could change the decision; re-reviewing
an evaluator-authored summary of settled facts does not qualify.

When variable agent behavior is plausible and no stronger evidence or user choice sets the initial
budget, use three fresh matched executions per key contrast. This is a modest starting budget, not a
power calculation or universal minimum. A deterministic counterexample may need less; a small or
unstable effect may need more. Replication must re-expose the source of variation: fresh generative
executions measure generative variability, while replaying an unchanged deterministic substep inside
one execution is only a consistency check. Freeze allocation, replacement, and stopping rules before
viewing results, and retain every attempt.

Open [comparative design](references/design.md) only when a live decision about task generation,
population, contrasts, replication, nuisance variation, or later rounds remains unresolved. Do not
batch-load references merely because the work spans a full comparison; load one only when its
non-inferable detail can change the current decision.

## Measurement validity

For causal evidence, the intended condition difference is the only systematic difference. Match or
account for task material, starting state, authority, tools, budgets, runtime, host, model, effort,
and other nuisance factors. Reconstruct the actual deployed input stack: role, precedence, timing,
tools, and ambient instructions matter, not only visible text. Treat inseparable changes as a compound
condition.

Observe each claimed property where it exists. When the decision depends on people or systems using,
understanding, playing, operating, perceiving, or benefiting from an alternative, obtain evidence
from that role or a faithful simulation. Artifact review can predict those outcomes only at a visibly
narrower strength. More reviewers do not turn an unobserved premise into observed behavior.

Preserve distributions, interactions, and failure boundaries that can change the decision. Equal
totals or averages do not establish equivalent behavior when case profiles differ and no governing
frequency, weight, loss, or invariance makes those differences immaterial.

Compare quantities only at a shared consequence boundary. A true value from each alternative does
not establish a meaningful difference when the values arise from different cases, populations,
deadlines, scales, or loss semantics. Preserve the governing denominator or normalize through an
adopted consequence model; otherwise present the observations separately rather than turning their
difference into a benefit.

The task, source, checker, simulator, oracle, reference answer, rubric, and reviewer interface form
one measurement system. They must agree with the maker's public contract and with every source branch
and population their conclusions claim to cover. Validate that a consequential checker rejects a
plausible wrong outcome. Label a partial model as partial; exhaustive computation over a simplified
contract is not exhaustive evidence for the original. A private answer key or prior validation is a
fallible measurement artifact, not maker authority; before candidate exposure, independent target
evidence must be able to correct or extend it rather than being forced into its existing categories.
Traceability is relational: the existence of an evidence bundle does not establish that a
consequential claim points to evidence bearing on it. A deterministic interface may enforce exact
claim-to-artifact linkage; whether the linked material actually supports the claim remains a semantic
judgment.

When the controller creates or materially adapts a consequential task, oracle, rubric, or composed
interface, obtain an independent semantic validation of the final executor- and reviewer-visible
instrument before candidate exposure. The validator sees every behavior-guiding condition layer but
no candidate output. This ordering protects held-out status; if it is missed, retain the work as
instrument evidence rather than confirmatory proof. Once candidates are exposed, a correction to the
task, key, oracle, or rubric creates a new prospective instrument rather than silently rewriting the
comparison they already saw.

Authority present only in an instrument author's or validator's ambient context governs that
agent's conduct; it does not become a criterion for the measured system unless the deployed
executor or reviewer stack adopts it. Validate the instrument against the exact deployed authority
boundary. A fresh or independent validator can still invalidate a sound instrument by importing a
parent repository rule, host convention, or evaluator preference that its subjects never received.

When the user has only an idea or alternatives, create held-out work from the intended use. It should
carry the real interacting goals, constraints, variance, and plausible failure pressure needed to
separate meaningful outcomes. Difficulty, prompt length, and case count are not discrimination.
Worker material contains the real outcome, facts, authority, inputs, constraints, and requested
artifact—never the experiment, suspected defect, condition identity, expected winner, grading logic,
or a preferred method that real users would not receive.

## Execution and custody

Freshness, isolation, immutable common inputs, condition-local state, committed artifacts, randomized
presentation, and reveal-after-judgment are observable boundaries rather than prompt assurances.
Match authority and collection interfaces across conditions, preserve traces and resource use when
they affect the decision, and treat rescue, asymmetric messages, leaked sibling state, or selective
regeneration as changed conditions.

Open [execution and custody](references/execution.md) only when a live launch, isolation, host, prompt
composition, or evidence-retention decision needs its detail. The optional
`scripts/split_test_workspace.py` supplies opaque workspaces, N-way review views, integrity hashes,
and reveal gating. Its `--help` and the reference are the usage contract. Do not inspect the helper
implementation during an ordinary comparison; this binding route compensates for observed
implementation-reading detours that consumed context without changing the experiment. If its
interface is insufficient, use a simpler valid custody system or leave the stronger claim unverified.
The helper never designs tasks, launches agents, selects models, grades results, or decides a winner.

## Review

When semantic reviewers can observe a still-unsettled property that could change the decision,
create and freeze an explicit rubric for the user's actual decision before they see candidates or
condition identities. Honor maker criteria. Where they are insufficient, research applicable
standards, established rubrics, domain authorities, and current evaluation evidence, then synthesize
only dimensions whose separate treatment can change this decision. Validate that the rubric can
distinguish plausible success, failure, tradeoff, and an unanticipated material concern. Calibrate a
rubric intended to predict a downstream outcome against applicable real observations, experts, or
trusted examples; coherence and judge agreement do not establish criterion validity.

The rubric is a measurement model, not a response template. Do not impose universal categories,
weights, totals, headings, word counts, fixed bands, or verdict vocabularies. A numeric tradeoff,
threshold, or tie band needs maker-fixed loss, empirical calibration, or a formal consequence model;
a plausible explanation written after choosing numbers is not a basis. Required information does not
make a literal worksheet necessary unless a consumer interface requires it or behavioral evidence
shows that the form improves validity without displacing judgment. Give all reviewers the same core
decision meaning while allowing declared specialist lenses. Grades or scores remain useful indexes
only when their values have observable meaning. Every semantic grade has reviewer-written Notes
grounded in support, counterevidence, and uncertainty. The bulk of each judgment is a free-form
comparative rationale explaining what mattered and why; request inspectable reasons, never private
chain-of-thought.

Preserve the source and force of every consequential criterion. A maker requirement, target truth,
adopted standard, observed outcome, and evaluator design preference are not interchangeable. A design
lens may judge usefulness without becoming a target conformance rule; a preferred diagnosis or repair
remains a hypothesis unless target authority or outcome evidence establishes it. Do not let a
recommendation-level criterion compensate for a false claim, omitted required property, or violation
of stronger authority unless the maker supplied that tradeoff through an applicable consequence
model.

Use trusted executable checks for facts they can decide and semantic reviewers for judgment. Blind
and counterbalance presentation when identity or order could bias it, preserve abstention or
indistinguishability, and commit exact judgments before reveal. Fact-check decisive reviewer
attributions and premises against the public contract and trusted outcomes. Agreement and arithmetic
cannot make a false premise true, average away a severe regression, or replace the execution
population. Give each evaluation layer a distinct evidentiary responsibility: an executor-created
review panel adds task evidence only when that panel is part of the condition or observes a property
the experiment's checks and outer review do not. Otherwise it is duplicated ceremony.
If a review layer's material findings concern only mistakes in the rubric, profile, or summary that
the same layer caused to exist, it has demonstrated self-generated process cost rather than target
value. Do not count repairing that intermediate as an improvement in the alternatives or task result.

Keep evidence about the alternatives separate from evidence about an artifact that describes them.
A reviewer may improve a report by making an already-available fact salient, but that is evidence
about the review-assisted production system, not new evidence about the alternatives or the rightful
decision-maker's preference. Attribute the improvement and its cost to that assistance, and do not
mistake a rescued output for correction of the earlier cause that omitted the fact.

Open [review design](references/review.md) only when rubric construction, grader choice, calibration,
presentation topology, blinding, or judgment reconciliation needs its detail.

## Interpretation and handoff

Decide correctness and material outcome quality before presentation, cost, or trajectory, then
include those operational effects when they change the choice. Preserve regressions and tradeoffs
that an aggregate would hide. Bind each claim to the actual tasks, units, conditions, exposure, and
concealment. A sound result may be a winner, context-dependent frontier, redesign, further test, or no
distinguishable difference.

Use observed differences to identify the earliest correctable cause in the tested system. A winner
label is not a diagnosis. Test a proposed foundational repair by changing that cause while preserving
unrelated conditions, rechecking the exposing boundary, and confirming on independent representative
work not used to design the fix. Keep the diagnosis or generalization provisional when intervention
or held-out confirmation is unavailable.

Write the primary result to a user-visible Markdown file with direct paths to the retained prompts,
artifacts, rubric, checks, traces, judgments, mappings, and data that support it. Report the supported
direction, material outcomes, scope and dependence limits, uncertainty, and reopening condition in
whatever shape best serves the decision. Use a table or generated visualization only when it makes a
material relationship clearer; retain its data and generation source and inspect the rendered result.
Delivery validity is a completion invariant, not an optional reproducibility claim. Before handoff,
the controller SHALL establish usability from the boundary the reader will actually receive, in a
view containing exactly the declared deliverable and explicitly declared external dependencies while
producer-only paths are unavailable. Every consequential local link must resolve and every claimed
executable must run through its delivered interface there. A producer-workspace check—even one named
"artifact-only"—or reviewer-side access to undeclared inputs does not establish this boundary. A
failed consequential check reopens the affected completion claim until it passes there or the report
truthfully narrows the claim; retain a needed dependency or expose stable external authority when
that better serves the deliverable.

Open [interpretation and reporting](references/interpretation-and-reporting.md) only when a live
causal, aggregation, uncertainty, or durable-handoff decision needs its detail. Stop when remaining
uncertainty would not change the current decision, or state what remains unverified when the evidence
cannot support a safe conclusion.
