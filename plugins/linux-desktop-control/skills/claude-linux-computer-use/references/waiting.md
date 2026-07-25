# Waiting, Polling, and Watching

Desktop work is full of asynchronous boundaries: app boots, endpoint
binds, background jobs, long verifications. The failure modes are
wasted turns (polling too often), premature exits (incomplete state
lists), and false conclusions (treating silence as success).

## No arbitrary sleeps

- You SHALL NOT wait with fixed or chained sleeps when a condition can
  be observed. Use a condition-based wait: an until-loop on the actual
  signal (file exists, endpoint answers, process gone), through the
  host's background-wait facility when one exists. Some agent harnesses
  block chained sleeps outright — the condition-based form is both
  allowed and correct.
- WHEN only one completion notification is needed THEN you SHOULD run
  the wait as a single background command that exits when the condition
  holds, rather than a long-lived watcher that emits events.

## Exhaustive terminal states

Polling a job or app through a state machine fails quietly when your
list of states is incomplete.

- WHEN exiting a watch loop on state values THEN you SHALL enumerate the
  TERMINAL states explicitly and treat every unknown or intermediate
  state as "keep waiting" — never the reverse. A watcher that exits on
  "anything I didn't list" stops on the first phase you had not seen
  yet (this exact bug: a live "editing" phase missing from a case list
  ended a watch mid-job).
- WHEN a watch can end for reasons other than success (failure,
  cancellation, timeout) THEN your filter SHALL match every terminal
  outcome, not only the happy path. Silence must never be
  distinguishable from "still running".

## Notification budget

- Watchers that emit on every state change spend a full agent turn per
  event. WHEN intermediate states carry no decision THEN you SHALL watch
  silently and emit only on terminal states (or on the specific states
  you will act on).
- A timeout is itself evidence: report *what did not happen* (the
  endpoint never bound, the phase never left X) rather than re-arming
  the same watch unchanged. Re-arm only with something different — a
  longer horizon chosen from data, a corrected state list, a different
  signal.

## Load sensitivity

Timing- and focus-dependent GUI behavior degrades under host load in
ways that look like product bugs:

- Parallel heavy jobs (compilers, other agents) on the same host can
  starve a windowed test of CPU long enough for focus loss, missed
  animation frames, and menu auto-closes.
- WHEN a GUI verification depends on focus, animation timing, or
  sub-second settle windows THEN you SHALL run it on a quiet host and
  record that requirement next to the check. A check that fails only
  under load and passes when quiet — with the mechanism identified
  (e.g., focus-state evidence captured at failure) — is an environment
  constraint to document, not a retry candidate.

## Probes during waits

While waiting for an unhealthy app or endpoint, the wait itself must be
passive. Active probing during boot or recovery can destroy the state
being waited for (see the lifecycle reference). The wait signal should
be an observation that cannot perturb: file existence, process table,
port state — not a client call into the thing that is still coming up.

## Diagnosing before re-waiting

- WHEN a wait times out twice THEN you SHALL stop and inspect the world
  (process table, endpoint files, logs, who else is running) before any
  third wait. Two timeouts is a diagnosis trigger, not a tuning
  problem.
