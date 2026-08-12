# Instruction Design

Instruction-design fit asks whether a document directs the executor's intelligence or overrides it.

Task evals cannot reach this. Canonical tasks are the anticipated cases, so a document that paved a
single road passes them and fails only on the case its author never foresaw. That is why this
question exists separately from task fit.

This reference has two halves. The standard below is normative and reproduced verbatim. The findings
after it are what make the standard auditable — a standard that is only reproduced gets read,
admired, and reported as "seems fine."

**Who the standard addresses.** It is written to the *author of the artifact you are auditing*, not
to you. Where it says "you," read "the author of the target." Your role is to find where the target
departs from it and to name the departure as a defect with a location.

---

## Governing Architecture

These rules apply only when you create or revise instructions for another AI. They govern the instruction system, not the surrounding answer.

The executor's intelligence is the resource. Supply only what it cannot safely provide: mission, environment, relevant reality and authority, decision-relevant state, loop limits, success evidence, precedence, and interfaces. Leave reasoning and methods open unless the route itself carries a named hazard.

Treat the deliverable as an instruction system, not necessarily one prompt. Put stable intent in instructions; changing facts in context; mutable decisions in state; authority in permissions, tools, and schemas; persistence and stopping in the loop; correctness in tests; and handoff in the output contract. Do not duplicate controls.

Completeness means coverage of every material control need, not every possible concern. Remove anything whose absence would not weaken mission, authority, material hazards, continuity, verification, or handoff.

These functions are semantic contracts, not a reasoning sequence, template, or closed ontology. Omit, combine, or add as needed.

### Mission

Define the outcome, whom it serves, the current decision horizon, and what distinguishes done from plausible. Separate required properties from suggested methods. Keep later commitments conditional when earlier evidence could change them.

A mechanism chosen by the author remains a proposal unless the maker fixed it, the task delegates that decision, or a named requirement cannot otherwise be met. Binding force attaches to the required property and hazard. Preserve alternatives satisfying the same mission, boundaries, evidence, and interfaces.

### Environment

Supply what the executor cannot safely infer, inspect, or rediscover: resources, limits, permissions, dependencies, hazards, external effects, and consequential gaps. Explain non-obvious hazards through consequences; mark consequential gaps rather than guessing.

Keep consequential information's source and authority unambiguous. Preserve observation, assumption, proposal, commitment, and evidence distinctions wherever collapsing them could change truth, authorization, or verification. Do not surface the taxonomy merely to prove it exists. Encode any mandatory consequence once.

### State

Keep action-changing state recoverable across turns and handoffs: objective, settled decisions, assumptions, evidence, dependencies, blockers, alternatives, progress, and reopening conditions.

Choose prose, tables, logs, graphs, Mermaid, or another fitting representation. Every representation is a revisable projection, not canonical truth or a closed ontology. Replace it when understanding changes; absence from a view never excludes a possibility.

### Boundaries

Define prohibited outcomes, authority limits, approvals, and constraints whose violation would cause material harm, invalidate the work, or exceed the mandate. Prefer external enforcement where more reliable. State each boundary once.

### Loop

Define progress, continuation, stopping, completion, retry, escalation, handoff, budgets, and blocked behavior. Loop controls govern persistence and commitment, not internal reasoning. Bind only the current evidence horizon. A probe must be able to reopen what it tests; later commitments remain conditional while earlier evidence could invalidate them.

### Verification

Define observable evidence of completion, correctness, safety, and handoff. Prefer executable checks and/or observable evidence. Assertion alone is not evidence. Match verification strength to consequence.

### Precedence

Resolve foreseeable collisions among mission, authority, safety, correctness, scope, and reversibility. Do not invent exhaustive branches for unknown space. Where no safe residual is known, preserve uncertainty and stop or escalate.

### Output Contract

Specify audience, destination, interface or format, completion evidence, and conditions for claiming success. Impose structure or style only when it improves use.

### Binding Language

Use natural prose for purpose, facts, rationale, definitions, and open judgment. Address obligations directly to the executor. SHALL means required, SHALL NOT prohibited, SHOULD a strong default, and MAY permitted.

Use formal clauses only when literal compliance or auditability is part of the outcome: invariants, hard boundaries, recognizable triggers, necessary sequences, and precedence. A clause earns binding force only when it transfers a maker requirement, non-inferable constraint, or compensation for a demonstrated model weakness, and compliance can be checked.

Bind outcomes, not pathways. Prescribe sequence only when order carries a named hazard. Say each obligation once. Keep model-specific compensation separate from stable governance and tie it to an observed failure, evaluation, and removal condition.

Instructions must stand alone, preserve compliant routes, keep consequential information unambiguous, and place controls where it is most reliable.

Do not require private chain-of-thought, named reasoning methods, visible compliance theater, or proof that judgment occurred. Do not promote an inference, recommendation, or assumption into a maker-set requirement. Do not name this architecture or copy its structure unless doing so materially improves the produced artifact.

---

## Scope and placement

The standard governs an instruction system, not every sentence in an answer that happens to discuss
AI work. Identify the target's instruction boundary before judging it. A surrounding explanation is
not defective merely because it would be inappropriate as an executor obligation.

Judge coverage by what the system makes recoverable and enforceable, not by its headings or their
order. Mission, Environment, State, Boundaries, Loop, Verification, Precedence, Output Contract, and
Binding Language may be omitted, combined, renamed, or supplemented. A missing heading is never a
finding by itself; a missing function is a finding only when the target needs it to remain correct.

Check where each control lives. Stable intent belongs in instructions, changing facts in context,
mutable decisions in state, authority in permissions, tools, and schemas, persistence and stopping in
the loop, correctness in tests, and handoff in the output contract. Report a placement only when its
current location makes the control stale, unenforceable, irrecoverable, or ambiguous. Report every
duplicated control; repetition that carries no control is a context-cost question instead.

Judge completeness against material control needs, not a catalog of possible concerns. Report a gap
when it weakens mission, authority, material-hazard coverage, continuity, verification, or handoff;
report excess when removing it would weaken none of those functions.

## Outcomes and methods

Apply this question to any prescribed route: would replacing or reordering the method still satisfy
the maker, avoid every named hazard, and pass every check? If so, state the outcome and leave the route
open. If not, state the load-bearing sequence and the hazard that makes its order matter.

The finding runs in both directions:

1. **False procedure** — a method is mandatory even though only its result matters, closing compliant
   routes without protecting a named hazard.
2. **Missing procedure** — order carries a named hazard, but the instruction does not make the
   load-bearing sequence explicit.

Do not reduce this judgment to counting imperatives or ordered lists. A method can be a valid maker
requirement, and an outcome can be dangerously incomplete when sequence carries the hazard.

Mission is the same distinction at document scale. It should define the outcome, beneficiary,
decision horizon, and evidence that separates done from plausible. Later commitments remain
conditional while earlier evidence could change them. A mechanism selected by the author remains a
proposal unless the maker fixed it, the task delegates that decision, or no alternative can satisfy
a named requirement. Judge binding force against the required property and hazard, preserving other
routes that satisfy the same mission, boundaries, evidence, and interfaces.

Model-specific compensation is not stable governance. Report it when the target cannot name the
observed failure, the evaluation, or the condition under which the
compensation can be removed.

## Information and state

Check that consequential information keeps its source and authority unambiguous, and that
observations, assumptions, proposals, commitments, and evidence remain distinct wherever collapsing
them could change truth, authorization, or verification. Do not demand visible taxonomy labels when
the distinctions are already clear. A fact does not create an obligation by implication, and the
auditor must not promote an author's recommendation or its own inference into a maker requirement.

Environment should carry only what the executor cannot safely infer, inspect, or rediscover. A
non-obvious hazard needs its consequence; a consequential unknown stays a named gap rather than a
guess.

State should preserve action-changing information across turns and handoffs. Its representation is a
revisable view chosen for inspectability, not a canonical ontology. Report a state design that loses
settled decisions, live assumptions, evidence, dependencies, blockers, alternatives, progress, or
reopening conditions when those facts could change the next action.

## Authority and controls

Judge a boundary by the outcome it prevents and the authority that enforces it. Permissions, tools,
schemas, and checks are stronger than repeated prose when they can enforce the boundary directly;
text remains appropriate where interpretation is necessary. Do not invent an approval or authority
limit that the maker did not set.

Treat policy and mechanism as separate placement questions. Scripts and tools may observe,
transform, verify, or enforce. Their presence is not a defect, and
neither is a route that relies on them when they supply determinism, external reach, scale, or a more
reliable control. Report tooling only when it displaces open judgment without adding one of those
properties, or when it duplicates a control.

External effects and reversibility matter when they change authority, safety, or commitment. Check
that the target represents those consequences and honors any stated approval boundary before the
load-bearing act. What an action emits — a notice, receipt, publication, or other outward effect —
may have a different reversal path from the state change behind it. Do not infer a universal consent
gate from irreversibility alone.

Precedence should resolve foreseeable collisions among mission, authority, safety, correctness,
scope, and reversibility. When no safe residual is known, the target should preserve uncertainty and
stop or escalate; it does not need an exhaustive branch over unknown space.

## Persistence, verification, and handoff

Loop controls define progress, continuation, stopping, completion, retry, escalation, handoff,
budgets, and blocked behavior. They govern persistence and commitment, not private reasoning, and
bind only the current evidence horizon. A probe must be able to reopen the decision it tests, and
downstream commitment stays conditional while upstream evidence could invalidate it.

Verification needs observable evidence appropriate to the consequence. Assertion alone is not
evidence; prefer checks that the executor or recipient can run against the result.

The output contract should identify the audience, destination, interface or format, completion
evidence, and conditions for claiming success. Formatting requirements earn their place by improving
use, not by displaying conformance.

## Binding language and self-reference

Keep purpose, facts, rationale, definitions, and open judgment in natural prose. Address obligations
directly to the executor, use SHALL, SHALL NOT, SHOULD, and MAY with their defined strengths, and use
formal clauses only where literal compliance or auditability is part of the outcome, such as
invariants, hard boundaries, recognizable triggers, necessary sequences, and precedence. A binding
clause must transfer a maker requirement, a non-inferable constraint, or evidenced model
compensation, and its compliance must be checkable.

The closing prohibition is conditional. Naming the architecture, notation, headings, or structure is
a defect only when doing so does not materially improve the produced artifact. An Improvement Brief
may name the rule it evaluates because that attribution can make the brief actionable; an authoring
skill may also need to discuss instruction architecture directly. The script reports self-reference
as an observation, and you decide whether the exception applies before reporting a finding.

Instructions must not require private chain-of-thought, named reasoning methods, visible compliance
theater, or proof that judgment occurred. These demands constrain or expose internal reasoning
without improving the observable artifact.

## Findings this standard produces

Each row is a defect you can name with a location. Rows marked **script** have a matching observation
in `<skills-file-root>/scripts/instruction_shape.sh`, which reports evidence without deciding whether
the target is defective.

| Rule | Observable defect | |
| --- | --- | --- |
| Govern the instruction system, not the surrounding answer | Explanatory prose outside the instruction boundary is graded as an executor obligation | |
| Supply only material, non-inferable needs | Inferable facts or preferred methods consume instruction space without carrying mission, authority, material-hazard, continuity, verification, or handoff value | |
| Place each control where it is most reliable | Stable intent, changing context, mutable state, authority, tests, or handoff live where they become stale or unenforceable | |
| Do not duplicate controls | The same obligation appears more than once | script |
| Functions are semantic contracts, not a template or sequence | Missing, combined, renamed, or reordered headings are reported as defects | script |
| Mission defines outcome, beneficiary, horizon, required properties, and done | The mission narrates activity, omits who it serves, commits past available evidence, or cannot distinguish done from plausible | script |
| Environment carries non-inferable resources, limits, dependencies, hazards, effects, and gaps | Inferable background is repeated, a non-obvious hazard has no consequence, or an unknown is presented as fact | |
| Consequential information keeps source, authority, and status clear | An observation is labeled fact, a proposal appears settled, evidence loses provenance, or information silently creates a duty | |
| State preserves action-changing information | A handoff loses a settled decision, live assumption, dependency, blocker, alternative, progress marker, or reopening condition | |
| Representations remain revisable | A table, graph, taxonomy, or log is treated as canonical truth or as excluding unrepresented possibilities | |
| Boundaries define prohibited outcomes and authority | A material harm or authority limit is left ambiguous, or a control remains in prose when external enforcement would be more reliable | |
| Loop controls govern persistence and commitment | The loop prescribes internal reasoning, lacks a needed stop or escalation condition, or cannot reopen a tested decision | |
| Verification uses observable evidence | Completion rests on assertion, an unexecutable check, or evidence too weak for the consequence | |
| Precedence handles foreseeable collisions and unknown residuals | A likely collision has no winner, or an unsafe unknown residual does not preserve uncertainty and stop or escalate | |
| Output contracts define audience, destination, interface, evidence, and success | The recipient cannot tell where the result goes, how to consume it, or when success may be claimed | |
| Structure and style improve use | Required formatting exists only to display process or conformance | script |
| Obligations address the executor directly | Binding text speaks about a third-person executor instead of directing it | script |
| Binding modals retain their defined strengths | SHALL, SHALL NOT, SHOULD, and MAY are used inconsistently or with ambiguous force | script |
| Formal clauses make outcome-relevant compliance auditable | A preference becomes a mandate, a clause serves no invariant, boundary, trigger, necessary sequence, or precedence need, or compliance cannot be checked | |
| Bind outcomes, not pathways | A method is mandatory although another route could avoid every hazard and pass every check | |
| Prescribed sequence carries a named hazard | Order is mandatory without a load-bearing consequence, or a named ordering hazard lacks the necessary sequence | |
| Model compensation is evidence-bound and removable | A model-specific rule has no observed failure, evaluation, or removal condition | |
| Preserve compliant routes | A closed case list or tool path excludes unanticipated compliant approaches | |
| Do not require private reasoning artifacts or compliance theater | The target asks for chain-of-thought, a named reasoning ritual, visible compliance theater, or proof that judgment occurred | |
| Do not promote inference into maker requirements | An author or auditor recommendation is presented as a maker-set obligation | |
| Self-reference must materially improve the artifact | The target names or copies the architecture only to announce compliance | script |

## Corpus placement

This is house doctrine, not part of the open agent skills standard.

WHEN the target is a plugin or skill in this repository THEN you SHALL apply this reference by
default.
WHEN the target is a third-party skill THEN you SHALL apply it only if the user asks, and you SHALL
label every finding from it as house style rather than as a portable defect.
