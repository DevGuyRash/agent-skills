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

When you are writing instructions for another agent — the executor. Address every line to it as
"you"; text about the executor rather than to it reads as background and goes unfollowed.

The executor's intelligence is the resource these instructions direct. Fence the hazards, fix the
outcome, check the result, and leave the route to the executor. The path you did not anticipate is
often the better one, and it stays reachable only where the document has not paved a single road.

### Document shape

Build in this order. A section with nothing to say is omitted, not padded.

1. Mission — what the executor produces and what done means. Prose plus invariants.
2. Environment — facts the executor cannot infer or safely rediscover: names, limits, quirks,
   hazards, and why each hazard is real. Hazards include what an action emits — a receipt or notice
   sent on completion has its own reversibility, separate from the state change behind it. Where a
   fact you need is unknown to you, name it as a gap with the behavior that degrades without it,
   rather than guess. If the executor can infer it from what it can see, leave it out.
3. Boundaries — prohibitions and hard stops. Where the environment could enforce one instead (a
   permission, a tool setting, a missing capability, an automatic check), note that in brackets
   rather than restating the rule more forcefully.
4. Loop — persistence, budgets, stop conditions, escalation: what keeps the executor going, what
   stops it, where it hands off, what it does when no one can answer. Loop controls govern when to
   continue, stop, or escalate — never how to work.
5. Verification — the checks that define done, written so the executor or anyone else can run them
   against the work alone. A document whose done-criteria cannot be checked is not finished.
6. Precedence — who wins when clauses collide.
7. Output contract — format and destination of the work.

### What earns a binding clause

A binding clause is one the executor must obey or a check must verify. Admit one only if it transfers
something the executor lacks: a fact about the world, a requirement of the maker, or a compensation
for a known weakness. If it transfers nothing, or its check cannot be named in one sentence, write
prose or write nothing.

Bind outcomes, not pathways. State every requirement as the result that must hold plus the fences
around it, and leave the route free. Write positive procedure — this, then this — only where order
itself carries the hazard, and name that hazard beside the steps. The test: if the executor reordered
or replaced the steps while avoiding every named hazard and passing every check, would the maker
care? No — write fence and outcome; the path belongs to the executor. Yes (consent before an
irreversible act; read the state before retrying) — the sequence is the requirement; write it with
its hazard attached. A procedure that cannot name its hazard is a preference wearing a mandate;
convert it.

Before compressing a domain into invariants, enumerate its known failure modes. Any failure mode the
invariants do not plainly absorb keeps its own one-line clause. Compression that loses a hazard is a
defect, not a saving.

### Forms

Modals: SHALL (must), SHALL NOT (must not), SHOULD (strong default), MAY (option). Say a thing once,
precisely, rather than restating absolutes for emphasis.

Invariant — holds always, checked against the artifact, never the actions:
You SHALL <outcome that must hold>.
You SHALL NOT expand an invariant into trigger cases; where only the outcome is required, a case list
is the defect.

Factored invariants — three or more sharing a stem:
You SHALL return work that:

1. <outcome>
2. <outcome>

Each line binds independently.

Table — three or more clauses sharing a modal and an action shape, differing only in slot values.
State the binding once in the header; each row plus the header must reconstruct a complete clause.
Number rows that other clauses cite. A clause that is load-bearing alone, or quoted elsewhere, stays
a sentence.

Fence: You SHALL NOT <prohibition>.

Trigger: WHEN <condition> THEN you SHALL <action>. Conditions may name judgment categories — the
request's purpose, the input's intent — not only surface features. Define each category in prose
before its first use.

Mode: WHILE <state> you SHALL <behavior>.

Branch: IF <test> THEN you SHALL <A> ELSE IF ... ELSE you SHALL <B>. Every chain ends in ELSE. Route
on purpose categories by default; enumerate literal cases only where a misroute is costly enough that
the decision must be auditable by reading. No branch may share its neighbor's outcome — merge them.

Loop controls (trigger-shaped by nature):
WHEN <done-check passes> THEN you SHALL stop.
WHEN <budget of attempts or time> is spent THEN you SHALL stop or escalate with what you have and
what remains.
IF no one can answer THEN you SHALL act under the stated stakes, prefer the more reversible course,
and leave the reasoning visible.

Tiebreak — wherever two clauses can collide, name the loser:
WHEN <A> conflicts with <B> THEN <winner> prevails and <loser> yields.

Residual: WHEN clauses collide with no tiebreak written THEN the prohibition beats the mandate;
failing that you SHALL take the more reversible course and escalate.

### Register discipline

Keep host prose natural; convert only genuine control clauses. The maker's intent, the reason each
hazard is real, and the definitions of the judgment categories your conditions use stay in prose —
they are what let the executor handle the case no clause anticipated and choose the route no clause
prescribed. Where a definition or rule needs an example, attach one or two lines inside it at the
point of use — never a separate examples section.

Cut prose that narrates process, praises, or restates what the executor can infer.

Never name this notation, reference this document, or comment on compliance. Write as if this is
simply how the executor's instructions are.

---

## One bounded carve-out

The closing line binds the artifacts you audit. It does not bind your brief.

A document written under the standard must not name the notation or comment on its own compliance —
an artifact that discusses its own conformance has spent context on something the executor cannot
act on. Your Improvement Brief is the opposite case: reporting conformance is its entire function.
Cite the standard by rule and quote the target's text. WHEN you find a target that names the notation
or discusses its own compliance THEN you SHALL report it as a defect against this rule.

---

## The routing rule

Most instruction-design defects reduce to one branch, applied per passage:

> IF the process is itself the requirement THEN state the procedure with the hazard that makes its
> order required ELSE state the outcome and leave the route free.

This is the standard's own test applied to prose rather than only to binding clauses: would the maker
care if the executor reordered or replaced the steps while avoiding every named hazard and passing
every check?

The finding runs in **both** directions, and the second is the more dangerous one because a
one-sided reading passes it silently:

1. **False procedure** — steps written where the outcome was the requirement. Over-constrains the
   executor and closes off the route nobody anticipated. Tell: a procedure with no hazard beside it.
2. **Missing procedure** — an outcome stated where the sequence was load-bearing, leaving the hazard
   unfenced. Tell: a named hazard with no ordering word. *"Present the diff and get approval before
   applying"* carries its requirement in "before"; delete that word and the clause permits the exact
   thing it exists to prevent. Consent before an irreversible act, reading state before a retry, and
   Loop sections generally live here.

You SHALL NOT reduce this to counting imperatives. A check that flags every ordered step is a style
rule, not a finding, and rebuilds the heuristic lint gate this skill exists to avoid.

## Outcome-oriented prose

Distinct from binding outcomes rather than pathways, which governs binding clauses only. This governs
everything else — prose, section headings, and the done-definition. A document can carry sound
outcome-bound clauses inside process-narrating prose under step-named headings.

**The heading test, one sentence:** can you tell from the heading what will be true once that section
is satisfied? `Wait For Outcomes` and `Assert Outcomes, Not Markup` pass. `Default Workflow` and
`Start Here` name a phase of work instead.

**The done-definition** is the same rule at document scale. A Mission that opens "You are done when
every test you leave behind states an outcome the user cares about" fixes a condition. A Mission that
describes what the executor will do next fixes a sequence. Absence of any done-condition is a prompt
to look, not a verdict on its own.

## Policy and mechanism

Instructions carry policy: what counts as acceptable, what the outcome must be, what is forbidden.
Scripts supply mechanism: they observe, transform, and report. A target that lets a script decide
acceptability has moved policy into a place the executor cannot reason about — an exit code carries
no argument, admits no profile, and cannot be weighed against anything.

This is the standard's outcome-versus-pathway rule wearing a different hat. A workflow the executor
cannot complete without running a particular script is a paved road with an exit status, and it
fails the same test: could the executor reach the outcome another way while avoiding every named
hazard?

The separation to look for: the script reports what it found, the instructions say what that means,
and the executor MAY reach the same evidence by reading instead.

**The test that decides it, in one question: can you name a legitimate target for which this is
fine?**

A link pointing at a file that does not exist fails on no host, at no age, under no convention —
there is no such target, so a script may fail on it. A four-hundred-line reference, a lowercase name
field, a four-word description, and a missing path prefix all have obvious legitimate targets, so a
script that fails on them is enforcing taste as breakage.

That test sorts a target's own tooling into two shapes, and you SHALL check that its scripts keep
them apart:

| Shape | Content | Exit |
| --- | --- | --- |
| Error | The artifact is broken. Dead links, absent required files, internal contradictions between two files that describe the same thing | non-zero |
| Observation | A fact whose significance depends on the target. Lengths, naming, idiom, house conventions | zero |

WHEN a target's script fails on something with a legitimate reading THEN you SHALL report it,
because wired into a gate it blocks work on a rule its author never agreed to and no one wrote down.

WHEN a target's script reports a fact without the rule it bears on THEN you SHALL report that too. A
bare observation forces the reader to either obey blindly or ignore blindly; the same fact carrying
"this is house convention, portable targets may differ" lets two readers reach opposite verdicts and
both be right.

WHEN a script's non-zero exit encodes a convention rather than a breakage THEN you SHALL report it,
because wired into a gate it blocks work on a rule its author never agreed to.

WHEN instructions defer to a script's verdict rather than to their own stated policy THEN you SHALL
report it: the maker's intent has been delegated to whatever the script happened to implement, and
the two drift apart silently.

WHEN a script must run for the workflow to proceed at all THEN you SHALL check that the hazard
requiring it is named. Absent a hazard, the requirement is a preference, and the script has become
the pathway the standard says not to pave.

### Tooling where a paragraph would do

The other direction of the same defect, and the easier one to miss because it looks like diligence.
A capability that could have been a paragraph of guidance is instead a bounded script the executor
must run, and the workflow is written around invoking it rather than around the outcome.

The cost is not the script. It is the ceiling. A script encodes the approach its author could think
of, and it performs exactly that well forever; a paragraph naming the outcome and its hazards is
read by whatever executor arrives, and gets better as they do. Tooling that replaced judgment locks
the capability to the day it was written.

Read a target's scripts against what they replace:

WHEN a script's whole content is a decision an executor could make from a paragraph THEN you SHALL
report the tooling as the defect, not its implementation. The fix is deleting it and stating the
outcome.

WHEN a script exists for a reason a paragraph cannot supply — determinism across runs, reaching
external state, a transformation too large or too exact to do by hand, an operation that must be
identical every time — THEN it earns its place, and you SHALL say so rather than treating every
script as suspect.

The question to ask of each one: if the executor deleted this and were told only what must be true
at the end, would the result be worse? WHEN the honest answer is no THEN the script is a road paved
over a capability the executor already had.

## Irreversibility

The standard puts hazards in Environment and names consent before an irreversible act as the case
where sequence is the requirement. Both are easy to lose when a document is otherwise well built,
because nothing about a clean structure forces the question to be asked.

Two things need finding. The first is the act itself: publishing, deploying, sending, deleting,
paying, or overwriting, reached without an approval step ahead of it. The second is subtler and the
standard states it directly — what an action *emits* has its own reversibility, separate from the
state change behind it. A deploy that also notifies a channel has two irreversible parts, and
rolling back the first does not recall the second.

WHEN a target performs or generates outward or destructive actions THEN you SHALL check that consent
is required before the act rather than reported after it, and that the ordering word is present. An
approval mentioned without "before" permits the thing it exists to prevent.

WHEN a target's reversibility is not obvious from the act THEN you SHALL check that the instructions
say which steps can be taken back. An executor that cannot tell will either freeze on safe work or
proceed on unsafe work, and both failures look like judgment errors rather than missing facts.

## Findings this standard produces

Each row is a defect you can name with a location. Rows marked **script** have a matching observation
in `<skills-file-root>/scripts/instruction_shape.sh`, which counts and reports but never decides —
the judgment stays yours in every row, and a target that never adopted this doctrine can carry the
observation without carrying the defect.

| Rule | Observable defect | |
| --- | --- | --- |
| Address the executor as "you" | Third-person "the executor shall"; text about rather than to | script |
| Build in the document order | Sections out of order, or present but carrying no content | script |
| A section with nothing to say is omitted | Padded or ceremonial section | |
| Environment names the hazard and why it is real | Hazard asserted with no reason attached | |
| Environment names unknown facts as gaps | A guess presented as a fact | |
| Bind outcomes, not pathways | Steps written where the outcome was the requirement | |
| Order carries its hazard | Procedure with no hazard beside it — a preference wearing a mandate | |
| Sequence written where sequence is required | Outcome stated where the ordering word was load-bearing | |
| A clause transfers a fact, requirement, or weakness-compensation | Clause restating what the executor can infer from what it sees | |
| A clause's check is nameable in one sentence | Unverifiable clause | |
| Failure modes enumerated before compression | An invariant that silently absorbed and lost a hazard | |
| Invariants are not expanded into trigger cases | Case list where only the outcome was required | |
| Every IF chain ends in ELSE | Non-exhaustive branch | script |
| No branch shares its neighbor's outcome | Duplicate branches that should merge | script |
| Tiebreak wherever clauses can collide | Collision with no loser named | |
| Residual clause present | No fallback for collisions with no tiebreak written | script |
| Say a thing once, precisely | Restated absolutes for emphasis; inconsistent modal case | script |
| Table only for 3+ clauses sharing modal and shape | Table used where a clause is load-bearing alone or cited elsewhere | |
| Factored invariants for 3+ sharing a stem | Repeated stems written longhand | |
| Keep host prose natural | Over-converted — every sentence a clause | |
| Examples attached at point of use | Separate examples section | script |
| Cut prose that narrates, praises, or restates | Ceremonial filler | |
| Never name the notation or comment on compliance | Document discusses its own conformance | script |
| Headings name a state, not a step | Heading names a phase of work | script |
| Mission defines done as a condition | No done-condition anywhere in the document | script |
| Loop controls govern when, never how | Loop section prescribing working method | |
| Scripts report; instructions judge | A script's exit status encodes a convention rather than a breakage | |
| Policy stays in the instructions | Instructions defer to a script verdict instead of stating what it means | |
| A required script names its hazard | The workflow cannot proceed without a script and no hazard is given | |
| The executor may reach the outcome another way | No route to the result exists except the provided tooling | |
| A failing check has no legitimate target | A script fails on something a reasonable target could do on purpose | |
| An observation carries the rule it bears on | A bare fact the reader can only obey or ignore blindly | |
| Tooling earns its place | A script whose content is a decision a paragraph could have handed to the executor | |
| Determinism, reach, or scale justifies a script | Tooling treated as suspect when it does something prose cannot | |
| Irreversible acts carry a consent gate before them | An outward or destructive action with no approval step ahead of it | |
| What an action emits is treated as its own hazard | A notice, receipt, or publication whose reversibility is never considered | |
| Reversibility is stated where it is not obvious | The executor cannot tell which steps it can take back | |

## Corpus placement

This is house doctrine, not part of the open agent skills standard.

WHEN the target is a plugin or skill in this repository THEN you SHALL apply this reference by
default.
WHEN the target is a third-party skill THEN you SHALL apply it only if the user asks, and you SHALL
label every finding from it as house style rather than as a portable defect.
