# Trigger Evals

Trigger evaluation treats `name` and `description` as a retrieval surface, not
as a static lint target.

## Evaluate the text that loads

Skills install into a per-host cache. Routing happens against the cached description, so a repository
edit that has not been reinstalled changes the file and not the behavior.

You SHALL establish which description is live before generating prompts. WHEN the installed and
repository descriptions differ THEN you SHALL run the eval set against the installed text, report the
divergence as its own finding, and say which text your findings describe. Evaluating the repository
copy and reporting on routing describes a skill that is not the one running.

Plugin fit covers the drift check itself.

## Required Eval Set

You SHALL generate:

- 1–2 explicit prompts that clearly ask for the capability
- 2–3 implicit prompts that describe the intended use case without naming the skill
- 2 adjacent negative controls that should not trigger the skill
- 1 ambiguous prompt near the boundary

You SHALL test the metadata boundary before rewriting deeper workflow content.

## What To Observe

For each prompt, note:

- Would the current metadata activate?
- Should it activate?
- What term or omission caused the result?
- What is the smallest metadata change that improves precision?

## Diagnosis Questions

WHEN the skill misses explicit or implicit prompts THEN you SHALL look for
missing task-family terms, missing file-format terms, or missing user-language
synonyms.
WHEN the skill activates on adjacent tasks it should avoid THEN you SHALL look
for overloaded nouns, generic verbs, or broad phrases such as "helps with."
WHEN the name is overloaded but the description is precise THEN you SHOULD
rewrite the name only if description tightening is not enough.
WHEN the description tries to enumerate every possible case THEN you SHOULD cut
examples until only discriminating terms remain.

## Metadata Rewrite Order

1. Tighten or expand the description.
2. Remove generic words that create false positives.
3. Add missing terms that recover false negatives.
4. Rename the skill only when the name itself is misleading.

## Sibling Skills

A negative control drawn from an unrelated domain proves little. The prompts that actually misroute
are the ones a co-bundled or adjacent skill also claims.

WHEN the target ships alongside other skills THEN you SHALL draw at least one negative control from
the nearest sibling's territory, because siblings are where overlapping trigger language is most
likely and least visible.

You SHALL check whether sibling descriptions claim the same work. Overlapping language between two
skills produces routing that depends on which description the agent weighed first, and neither
skill's own metadata reveals the conflict.

WHEN a description names another skill in a negative trigger THEN you SHALL verify that the named
skill claims the work in its own description. A one-way edge routes traffic away from one skill
without routing it into anywhere.

## Deliverables

You SHALL report the eval prompts you used.
You SHALL describe false positives, false negatives, and boundary ambiguity.
You SHALL propose rewritten metadata before proposing structural rewrites.
WHEN the trigger issue is minor and workflow quality is good THEN you SHOULD
limit the change plan to metadata only.

## Quick Checks

- Does the description say both what the skill does and when to use it?
- Would a user prompt that never names the skill still match?
- Is there at least one realistic nearby task that should not trigger it?
- Does the ambiguous prompt reveal overshoot or undershoot?
