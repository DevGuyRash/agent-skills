# Field rubrics

This file defines what each field is. It contains **no complete good examples, by design**: worked examples become templates — measured on the v4 corpus, models converged on example phrasings and openers within days. Definitions constrain quality without providing sentences to imitate. Write every field in your own words, in whatever structure the incident actually had.

Failure classes below name *structural* ways fields go wrong. They are classes, not phrases — avoiding the class matters, avoiding specific words does not.

---

## `actual_outcome`

The best primary evidence you have of the divergence. Where text exists — an error string, output lines, an exit code, a sentence as written — that text is the evidence, pasted rather than described. Where no text exists, the evidence is a labeled firsthand observation, a measurement, a before-and-after state, or an explicit non-occurrence, and labeling it as such is what keeps it honest.

Short is fine when the evidence is short: `EPIPE` is a complete outcome. Write-time redaction runs before anything is stored, so a redacted quote is still the quote. A stranger reads this field alone and judges what happened without trusting your interpretation.

Failure classes:
- **Paraphrase**: a summary standing in for text you had and could have pasted. The defect is availability — describing output you were looking at, not labeling an observation where no text existed.
- **Invented verbatim**: a quoted string composed to fill the shape of evidence. Worse than an honest observation, because it sends mending at a sentence nobody wrote.
- **Over-capture**: pasting an entire log when three lines carry the signal. Keep the load-bearing lines; the cap is 20,000 chars, but the target is the minimum a stranger needs.

## `expected_outcome`

The prediction you actually held before acting — not what you now know you should have expected — together with what grounded it: a quoted sentence, a past experience, a convention, an inference.

Failure classes:
- **Retrofitted expectation**: writing the expectation you should have had. The record exists to expose the gap between your real model and reality; a corrected expectation erases the data.
- **Groundless expectation**: "I expected it to work" with no source. If you cannot name the grounding, say that — it is itself the finding.

## `reading`

The account from inside the decision as it unfolded, not from above it afterward: what you consulted and in what order, what you believed it said, and the specific point where reality stopped matching your model. A reader forms their own opinion of your reasoning from this account alone — including disagreeing with you.

Quote the wording you acted on where there is wording to quote. Where what you acted on was an inference, a habit, or a recollection, say so; an invented quote is the worse error.

Failure classes:
- **Verdict without account**: a conclusion about what went wrong with no trace of how you got there. The conclusion is the least valuable part; the path is the data.
- **Fix leakage**: arguing for a change instead of tracing the path. A record that argues for a fix has stopped observing and started advocating.
- **Outside-narrator voice**: analyzing your own actions as a detached third party. The value of this field is the view from inside — what you knew, when you knew it.
- **Compression to one sentence**: if the whole account fits in one sentence, either the incident was not worth filing or the account is missing its decision points.

## `decision`

The response you actually made, in past tense — an action already taken (retried, worked around, escalated, continued unchanged), never a proposal. It names the options you saw at that moment and the ones you set aside, or states honestly that you saw only one path, or that you filed before acting and have not yet responded — that too is the response so far.

When the action deviated from anything documented as required, it states the license you operated under at the time: the permission as you held it while choosing, including "I did not register the requirement as applying here" when that is the truth. Unnoticed is different from waived, and the difference is the data. A reader reconstructs your choice architecture from this field alone, and disagrees with the choice.

Failure classes:
- **Counterfactual drift**: writing what you would do now or should have done. The record is history; the moment "would" or "should have" appears, the field has left it.
- **Outcome without deliberation**: "retried and it worked" with no trace of options seen or license held. The action alone is nearly worthless at corpus scale; the weighing is what the mend loop needs.
- **Retrofitted authorization**: a justification composed at filing time that did not operate at decision time. If the skip happened without deliberation, say so.
- **Fix leakage**: proposing what the misleading sources should say. Your own completed response belongs here; their correction belongs to mending.

## `pivot_information`

A piece of *information* — a fact, a line, a behavior, a state — not an action you should have taken and not a judgment of yourself, together with where that information lives: a specific file, a doc section, a command's output, a person, or nowhere. If it lives somewhere you could have looked, it says what looking would have cost.

When you caught the friction before harm, it is forward-looking: the fact a future agent should check first, or which source should yield. The honest escape when true: `none — the outcome was unknowable in advance, because ...`

Failure classes:
- **Self-verdict**: an answer about your behavior rather than about missing information. The mend loop can relocate information; it cannot retroactively improve your diligence.
- **Unlocated fact**: naming the fact but not where it lives. Location is what makes the gap mendable.
- **Circular pivot**: restating the catch as the gap ("had I read both first the conflict would have surfaced — which is what happened"). When the outcome was a successful catch, the pivot is forward-looking: the fact to check first, or the precedence between the conflicting sources — something a future agent can act on, not a description of what you already did.

## `sources`

The inputs that supported your prediction, each with the `claim` you believed about it. A source need not have been wrong: it may have been stale, incomplete, misplaced, or over-read, and which of those it was is mending's call.

`kind` reflects what the input is, not where friction surfaced: a file that misled is an `artifact`; a belief with no backing is an `assumption`; a behavior you relied on is a `tool`; something you recalled rather than consulted is a `memory`. For `artifact` and `instruction`, `claim` quotes the text you acted on where text exists.

Failure classes:
- **Ref dumping**: filing the tool that displayed the error as the source. The terminal did not shape your prediction; whatever you consulted or assumed did.
- **Missing claim**: a ref with no claim leaves the mend loop guessing what belief to correct.
- **Observed-truth in claim**: writing what the source actually turned out to contain ("expected X; it actually contains Y") into `claim`. The claim is the prior belief only; reality's half of the gap already lives in `actual_outcome`. A claim that carries the correction erases the record of what you believed.

## `recurrence_key`

2–5 hyphenated words you would recognize and search for if this bit you again next month, stable across days and phrasings: it names the trap, not this occurrence. Omitted when unsure — a content-derived fallback is computed, and a wrong key is worse than none.
