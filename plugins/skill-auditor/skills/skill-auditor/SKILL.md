---
name: skill-auditor
description: Audit an existing skill or plugin for material evidence about target authority, executable behavior, host contracts, instruction design, and task value. Use for evidence-driven quality reviews, self-audits, release-risk investigation, or suspected packaging, routing, source, context, verification, or task-value drift. Do not use to author a new skill or review ordinary source-code changes.
---

# Skill Auditor

Determine whether an existing skill or plugin earns its place, what materially weakens it, and what
evidence supports changing, retaining, narrowing, or removing it. Serve the maintainer's decision,
not the appearance of audit thoroughness. A clean result is valid when the inspected scope and its
limits are clear.

Authoring a new skill belongs to `skill-creator`. Ordinary source-code review belongs to the
repository's code-review workflow. Do not modify the audited target unless the user asks for changes.
Target immutability includes incidental files or metadata produced by inspection tools, not only
deliberate source edits. An audit also does not authorize installation, registration, publication,
cache mutation, or other user-level or external writes. Use an actually disposable profile or
faithful simulation when a host observation requires mutation; otherwise leave that claim unverified.

## Evidence and authority

Inspect the target and the live surfaces that control its behavior. A finding gains force from a
target-owned outcome, maker or repository authority, an adopted consumer or standard, or a
demonstrated consequence. A familiar package shape, validator, helper, domain norm, safer design, or
evaluator expectation supplies none of those by itself. Without the governing link, preserve the
structural observation, possible consequence, and evidence that would establish adoption rather than
promoting a preference into a defect. Apply the [portable skill contract](references/open-standard.md)
only when the target adopted it.

An adopted declaration can incorporate an external contract instead of repeating its terms locally.
Establish the consumer meaning, scope, and horizon of that declaration, then apply only the terms it
actually incorporates. Do not demote an incorporated obligation to optional hygiene, or expand it
into unrelated ecosystem preference.

Ambient repository, host, or controller instructions govern the auditor where they apply; they do
not become requirements of a copied, external, or independently governed target unless the target or
user adopts them. Preserve that boundary in delegated work as well as the final disposition.

Begin with the target's declared entry points, adopted references, consequential executables, tests,
and fixtures. Treat unselected auditor references, scripts, and tests as inactive package context;
do not inventory or batch-open them. Open a focused reference only when a current target decision
remains unresolved and the reference owns non-inferable authority or design detail needed to settle
it. Several references may serve genuinely independent live decisions, but package breadth or a
full-audit label is not evidence that they are active. A fixed reference count is not the goal.

Treat declarations, checkers, and passing examples as target evidence, not independent proof. Seek
safe evidence capable of falsifying every consequential property that could change disposition or
repair. For durable state or external effects, inspect reachable completion, partial-failure, and
repeat behavior when those transitions could change the repair boundary; keep independently promised
effects separate. Where authority differs between logical roles, establish that runtime identity does
not collapse them: permission to replace, expose, or mutate one role does not transfer through an
alias or shared object to an independently protected role. Derive probes from the target and plausible
operating boundary, not a stock edge inventory. A failing probe can establish a defect without
establishing the smallest safe repair.
Before calling a repair narrow, safe, or sufficient, retain evidence that distinguishes the failed
property from consequential adjacent behavior the change must preserve; a proposed future test does
not establish that present boundary.

Discovery breadth and disposition are separate. A boundary is worth exposing when its behavior could
change repair scope, but classify what appears only at the strength of a target-owned promise,
adopted authority, or demonstrated consequence. Absence of a named guarantee does not erase a
reachable harmful state; report the state and consequence without inventing the missing guarantee.
A deterministic blocker can end unnecessary task-value proof, but it does not make other
independently repair-changing surfaces inspected. Stop before observations that would change no
material decision.

Report material defects by default and allow a clean result. Calibrate severity from the reachable
population, demonstrated consequence, and resulting repair or release decision—not from a domain
label, extreme hypothetical, probe existence, or finding count. When scope or meaning is genuinely
unsettled, preserve the ambiguity and evidence needed to resolve it without assuming either the
broadest contract or that the observed behavior is harmless.

A contradiction establishes that the represented states cannot all be fulfilled; it does not select
which meaning the maker intended. When plausible repairs serve different meanings, preserve the
alternatives and the evidence or maker decision needed to choose instead of promoting the auditor's
interpretation into repair authority.

Keep target coherence distinct from external consumer enforcement. A target-authored ordinary-
language limit, allowlist, cross-file declaration, or maker-bound order supplies its expressed scope;
reachable target behavior that contradicts it is an internal inconsistency even when host behavior
is unavailable. Consumer evidence is still required for consumer-assigned meaning and claims about
what that consumer blocks, transforms, or permits. Unknown enforcement may narrow compatibility or
exploitability consequences, not erase a demonstrated target contradiction. Likewise, a component
result establishes an end-to-end outcome only when the adopted composition supplies the relevant
invocation and collection semantics.

When order carries a named hazard, trace it through the composed workflow rather than inspecting an
atomic helper alone. Incompatible adopted orders are an internal contradiction even when the intended
resolution is unknown. Keep independently promised outcomes distinct whenever different evidence
could change their repair or release status.

For a consequential broad audit, coverage is an evidence claim. Continue while a credible uninspected
surface could change the repair or release decision; otherwise state the inspected boundary and
remaining risk without calling the result exhaustive. Fresh discovery or coverage review can expose
an omission when its isolation, authority boundary, and raw return are real, but neither agent count
nor agreement closes the target. Repeated held-out trials showed generic extra passes duplicating the
first findings, importing ambient authority, and adding unsafe host probes while missing the same
publication boundary. Use another context only when it observes a distinct unresolved property; do
not make a reviewer topology the evidence. A repeated look in one context is not independent, and an
unexecuted assignment is no evidence at all. Aggregate distinct supported findings and calibrate each
independently.

A task-value claim requires decision-linked behavioral evidence after deterministic target inspection
has established that the claim is still material. Open [task-value evidence](references/task-value-evidence.md)
only for that decision. Explicit task trials do not prove implicit activation; use [trigger
evidence](references/trigger-evals.md) when retrieval is at issue.

For plugins, preserve per-skill task evidence and separately examine package behavior. Route
manifest, catalog, installed-copy, host-ingestion, or publication questions to [host
contracts](references/host-contracts.md); route sibling routing, composition, and package handoff to
[plugin fit](references/plugin-fit.md); and route delivery-primitive questions to [packaging
fit](references/packaging-fit.md). In a broad plugin audit, each represented consumer boundary that
could change release or repair must be reconciled against authority current for its actual horizon or
visibly excluded from the claim. A core skill blocker can decide release without closing an
independently repair-changing host or package boundary.

## Instruction and context judgment

Use [instruction design](references/instruction-design.md) as the default design lens for AI
instruction systems. The linked block is adopted authority for the Skill Auditor's source repository;
it governs an audited target only while that target is under the same authority or separately adopts
it. Elsewhere, departures support evidence-backed design risks and recommendations, not target
conformance failures or maker requirements. Exact procedure is legitimate when required by a maker
interface, named hazard, external contract, or observed model failure; procedural form alone is not a
defect. The target artifact repeating its own preferred method does not independently establish that
the maker fixed that method. Preserve the required outcome while asking whether the constraint
improves behavior or instead creates template lock, visible reasoning theater, displaced grounding,
or verification detours. The linked reference supplies deeper repair guidance when that distinction
is material; its core judgment does not require preloading it in every audit. Scripts may own
deterministic inspection, transformation,
custody, or fragile interfaces; semantic policy, quality judgment, and instruction sufficiency stay
with the agent unless a governing interface assigns them elsewhere. Judge the composed behavior, not
a helper in isolation. When observed failures have accumulated into many narrow compensations, test
whether one earlier semantic control can preserve the demonstrated benefits with less attention
displacement. Empirical origin does not make duplicated clauses or case-shaped procedures
foundational; only the behavior they preserve earns continued context.

When context loading or external sources could change a finding, use [context and source
evidence](references/context-and-source-evidence.md). Package size, file count, link presence, and
prompt length are observations, not quality verdicts.

Apply the [repository overlay](references/repo-overlay.md) only where ambient repository authority
governs the target. These routes are not a complete concern inventory; follow target evidence
elsewhere when needed.

## Deterministic helpers

Bundled scripts are optional deterministic reporters, not audit phases. Treat them as inactive until
a live target uncertainty calls for an observation one of them owns; a full-audit label or the mere
presence of several reporters does not activate a suite. Use the selected reporter's `--help` as its
invocation contract, do not preload implementations merely to run them, and do not treat output as a
policy verdict. Inspect and exercise target scripts, hooks, schemas, or other executable mechanisms
when their behavior is consequential; prose about them is not a substitute.

## Completion

Give the maintainer the supported direction, material evidence and consequences, smallest viable
repair when one exists, and uncertainty or reopening conditions that could change the decision. Use
the presentation that makes those facts easiest to act on. Coverage is sufficient when another
independently discoverable defect would no longer change the repair boundary or release claim—not
when a familiar section is filled, the first blocker is found, or every imaginable concern is named.
Do not convert a desired coverage method into an executed fact. If the audit relies on a fresh pass,
retained host provenance must establish the separate context, input boundary, and returned
observations; otherwise omit the claim and preserve the coverage limitation.

Trace a recommended change to the earliest supported cause in the instruction, mechanism, consumer,
or evidence system instead of polishing the visible audit symptom. Treat both the diagnosis and the
repair as claims: when feasible, change that cause without changing unrelated conditions, recheck
the boundary that exposed it, and confirm on independent representative work. If intervention or
held-out confirmation is unavailable, keep the causal or generalization claim provisional. A blind
preference for a revised artifact is not by itself evidence that its foundation was corrected.

Audit delivery validity at the boundary the maintainer will actually receive. Use target-relative
paths for target facts and delivered evidence-root paths for retained trials. When disposable work
and the requested artifact differ, assume only the requested artifact will survive: a `work/` path,
temporary file, local hash log, or uncopied helper result is not maintainer evidence. Establish
whether consequential links and executable evidence work in a view containing exactly the declared
deliverable and explicitly declared dependencies while producer-only paths are unavailable.
Origin-workspace success—even when described as an artifact-only check—or auditor-side access to
undeclared inputs is not delivery proof. Treat an unresolved failed consequential check as open
evidence against the affected completion claim; the target may instead retain the dependency,
identify stable external authority, or truthfully narrow the claim.
Any consequential delivered executable SHALL resolve each declared dependency through its stated
consumer interface without recreating producer-only directory topology. Naming the dependency while
hard-coding its producer-relative location does not satisfy this boundary.

Stop when no material issue remains hidden behind missing evidence and every claimed improvement has
an observable test. If the evidence cannot support a safe residual conclusion, state what remains
unverified and stop or escalate. User authority and portable requirements outrank house preference;
safety, correctness, and honest evidence outrank brevity or the desire to finish.
