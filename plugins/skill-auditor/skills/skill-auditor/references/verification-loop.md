# Verification Loop

Two loops are in play and they are easy to conflate. The target's loop is what keeps its executor
going and tells it when to stop; your loop is how you confirm a proposed fix worked. The first is the
subject of this question. The second is how you finish any question.

## The target's loop

A skill without a loop leaves its executor with no way to know it is finished. The common outcomes
are grinding past the point of value and stopping early with an unstated gap — both invisible to the
maintainer, because neither produces an error.

You SHALL check whether the target answers all five:

1. What keeps the executor going — the condition under which more work is still warranted.
2. What stops it — a done-check stated so the executor can run it against its own output.
3. What bounds it — a budget in attempts, time, or scope, so a target that never satisfies the
   done-check still terminates.
4. Where it escalates — who receives the work and what accompanies it.
5. What it does when nobody can answer — because escalation to an absent maker is a hang, not a
   handoff.

WHEN the target has no done-check THEN you SHALL treat that as the leading finding for this question
regardless of what else is missing. The other four control a loop; without the first there is no loop
to control.

WHEN a target's loop section prescribes working method rather than continuation, stopping, or
escalation THEN you SHALL report it as misplaced: loop controls govern *when*, never *how*. Method
belongs in the domain sections, where the executor can replace it.

### Unverified is not failed

A target that collapses "I could not check this" into "this failed" produces false negatives its
maintainer will chase. A target that collapses it into success ships unverified work as verified,
which is worse.

You SHALL check that the target names a distinct outcome for work it could not execute, and that the
outcome carries the blocker. WHEN execution is unavailable and the target has no such outcome THEN
its executor has only two labels for three states.

### Leaving a trace

A done-check the executor can run says whether the work succeeded. It does not say what happened on
the way, and a skill whose failures are undiagnosable without a rerun spends the rerun to learn what
the first run already knew.

You SHALL check that a target leaves enough behind to diagnose a failure without repeating it: which
step ran, what it was given, what it observed. WHEN a target captures artifacts THEN you SHALL check
that they carry no credentials or unrelated private data, because an attached artifact is a
published one.

WHEN a target's work is long-running or resumable THEN you SHALL check that its recorded state is
enough to resume from rather than restart. A checkpoint that cannot be resumed from is a log.

### Failure handling

WHEN the target's workflow has three or more steps THEN each step's success or failure SHALL be
independently detectable, and the target SHALL say whether a failed step means retry, restart, or
abort. A workflow that detects only its final failure cannot tell the executor which step to redo.

## Your loop

A proposed fix is incomplete until you can say whether it worked and what to do when it did not.

You SHALL define success before listing edits, and you SHALL include a verification plan in every
Improvement Brief.

WHEN your recommendation changes metadata THEN you SHALL rerun the trigger eval set.
WHEN it changes workflow or structure THEN you SHALL rerun at least one representative task.

The recovery loop: make the smallest change addressing the leading failure, rerun the most relevant
eval or task, compare against the prior result, and keep the change only if the evidence improved.
The order carries the hazard — a change kept without a comparison is a change kept on faith, and the
next change will be built on it.

WHEN a fix does not improve the result THEN you SHALL record the assumption that failed before trying
the next change, so the same assumption is not retried in a different shape.

WHEN deterministic scripts exist THEN you MAY use them for structural evidence, but you SHALL NOT
substitute them for behavioral verification. A script confirms a file has the shape you expect; it
cannot confirm the skill changed what the agent did.

## Minimal regression set

A verification plan usually covers:

- one trigger or packaging check tied to the changed boundary
- one representative task tied to the changed workflow
- one structural check tied to the changed files

## Deliverables

You SHALL state:

1. the exact checks to rerun
2. what result counts as success
3. what to try next if the result does not improve
