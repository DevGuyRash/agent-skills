# Field rubrics

This file defines what each field must satisfy. It contains **no complete good examples, by design**: worked examples become templates — measured on the v4 corpus, models converged on example phrasings and openers within days. Properties constrain quality without providing sentences to imitate. Write every field in your own words, in whatever structure the incident actually had.

A field passes when it satisfies its properties. Failure classes below show *structural* ways fields go wrong; they are classes, not phrases — avoiding the class matters, avoiding specific words does not.

The questions themselves are prompts, not perimeters: they pre-structure answers, and what they do not ask about is systematically at risk of omission. If something mattered that no question asked about, include it — whatever fits no field goes in `note`, the deliberately question-less free slot. The question shape never excuses omission.

---

## `actual_outcome`

Properties — all must hold:
- Contains the outcome verbatim: exact error text, output lines, exit code, or the sentence as written.
- A stranger could judge what happened from this field alone, without trusting your interpretation.
- No paraphrase, no summary verbs ("it errored", "it failed to parse") in place of the evidence itself.

Failure classes:
- **Paraphrase**: describing the outcome instead of pasting it. The evidence is gone; only your reading of it remains.
- **Over-capture**: pasting an entire log when three lines carry the signal. Keep the load-bearing lines; the cap is 20,000 chars but the target is the minimum a stranger needs.

## `expected_outcome`

Properties:
- States the prediction you actually held before acting — not what you now know you should have expected.
- Names what grounded it: a quoted sentence, a past experience, a convention, an inference.

Failure classes:
- **Retrofitted expectation**: writing the expectation you should have had. The record exists to expose the gap between your real model and reality; a corrected expectation erases the data.
- **Groundless expectation**: "I expected it to work" with no source. If you cannot name the grounding, say that — it is itself the finding.

## `reading`

Properties — all must hold:
- Contains at least one verbatim quote of wording you acted on (from a doc, an instruction, an output, or your own stated assumption).
- Names what you consulted before acting, in the order you consulted it.
- Locates the moment of divergence: the specific point where reality stopped matching your model.
- A reader could form their own opinion of your reasoning from this account alone — including disagreeing with you.
- Written from inside the decision as it unfolded, not from above it afterward.

Failure classes:
- **Verdict without account**: a conclusion about what went wrong with no trace of how you got there. The conclusion is the least valuable part; the path is the data.
- **Fix leakage**: prescribing what should change. Mending is a separate activity; a record that argues for a fix has stopped observing and started advocating.
- **Outside-narrator voice**: analyzing your own actions as a detached third party. The value of this field is the view from inside — what you knew, when you knew it.
- **Compression to one sentence**: if the whole account fits in one sentence, either the incident was not worth filing or the account is missing its decision points.

## `decision`

Properties — all must hold:
- Reports the response you actually made, in past tense — an action already taken (retried, worked around, escalated, continued unchanged), never a proposal.
- Names the options you saw at that moment and the ones you set aside — or states honestly that you saw only one path, or that you filed before acting and have not yet responded (that too is the response so far).
- When the action deviated from anything documented as required, states the license you operated under at the time — the permission as you held it while choosing, including "I did not register the requirement as applying here" when that is the truth. Unnoticed is different from waived, and the difference is the data.
- A reader could reconstruct your choice architecture from this field alone — and disagree with the choice.

Failure classes:
- **Counterfactual drift**: writing what you would do now or should have done. The record is history; the moment "would" or "should have" appears, the field has left it.
- **Outcome without deliberation**: "retried and it worked" with no trace of options seen or license held. The action alone is nearly worthless at corpus scale; the weighing is what the mend loop needs.
- **Retrofitted authorization**: a justification composed at filing time that did not operate at decision time. If the skip happened without deliberation, say so.
- **Fix leakage**: proposing what the misleading sources should say. Your own completed response belongs here; their correction belongs to mending.

## `pivot_information`

Properties:
- Names a piece of *information* (a fact, a line, a behavior, a state) — not an action you should have taken and not a judgment of yourself.
- States where that information lives: a specific file, a doc section, a command's output, a person, or nowhere.
- If it lives somewhere you could have looked, says what looking would have cost.
- When you caught the friction before harm, forward-looking: the fact a future agent should check first, or which source should yield.
- Honest escape when true: `none — the outcome was unknowable in advance, because ...`

Failure classes:
- **Self-verdict**: an answer about your behavior rather than about missing information. The mend loop can relocate information; it cannot retroactively improve your diligence.
- **Unlocated fact**: naming the fact but not where it lives. Location is what makes the gap mendable.
- **Circular pivot**: restating the catch as the gap ("had I read both first the conflict would have surfaced — which is what happened"). When the outcome was a successful catch, the pivot is forward-looking: the fact to check first, or the precedence between the conflicting sources — something a future agent can act on, not a description of what you already did.

## `sources`

Properties:
- Each entry names one thing you *trusted*, with the `claim` you believed about it.
- `kind` reflects what the trusted thing is, not where friction surfaced: a file that lied is an `artifact`; a belief with no backing is an `assumption`; a behavior you relied on is a `tool`; something you recalled rather than consulted is a `memory`.
- For `artifact` and `instruction`, `claim` quotes the text you acted on verbatim.

Failure classes:
- **Ref dumping**: filing the tool that displayed the error as the source. The terminal did not betray you; whatever you trusted did.
- **Missing claim**: a ref with no claim leaves the mend loop guessing what belief to correct.
- **Observed-truth in claim**: writing what the source actually turned out to contain ("expected X; it actually contains Y") into `claim`. The claim is the prior belief only; reality's half of the gap already lives in `actual_outcome`. A claim that carries the correction erases the record of what you believed.

## `recurrence_key`

Properties:
- 2–5 hyphenated words you would recognize and search for if this bit you again next month.
- Stable across days and phrasings: name the trap, not this occurrence.
- Omitted when unsure — a content-derived fallback is computed, and a wrong key is worse than none.
