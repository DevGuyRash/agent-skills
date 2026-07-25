# Shared-Host Hygiene

An agent rarely has the machine to itself. The human, other agents,
session managers, and test harnesses all share the same processes,
files, focus, and CPU. Most "mystery" failures on a desktop host are
contention or ambient state, not product bugs.

## The human outranks you

- The desktop belongs to its user. WHEN evidence of live human use
  appears (an app you killed returns, edits you did not make, focus
  moving on its own) THEN you SHALL stop competing for that surface —
  pause lifecycle churn, say what you observed, and either coordinate or
  work on something else.
- App restarts are user-visible disruptions. You SHOULD batch restarts,
  announce them in your narration, and prefer in-app reload mechanisms.
  You SHALL NOT repeatedly kill something that keeps being relaunched.

## One writer per mutable surface

- Two writers on one workspace, profile, or document tree corrupt each
  other. WHEN orchestrating multiple agents THEN you SHALL give each
  writer a disjoint territory and keep everything else read-only.
- Queue or lock rejections from a runtime (a second job failing at
  submission) usually MEAN "a writer already holds this workspace".
  WHEN a parallel write-mode job fails immediately THEN you SHALL
  serialize behind the current holder rather than retrying into the
  lock.
- Desktop focus is itself shared mutable state: interleaved GUI actions
  from two actors invalidate each other's targeting. GUI-touching work
  does not parallelize on one seat.

## Ambient state leaks into fixtures

Sandboxes and test profiles inherit more of the developer's world than
expected:

- WHEN the code under test is *installed into* a live application (a
  repo that doubles as the app's plugin/extension directory) THEN the
  live profile's settings travel with it into any copy a harness makes.
  Real incident shape: a preference the user toggled in their live app
  steered an unrelated test's assertion days later.
- WHEN an assertion depends on a configurable mode, layout, or default
  THEN the test SHALL set that state itself rather than inheriting the
  ambient value. Pin what you assert on.
- Fixture profiles accumulate: settings persisted by one test leak into
  later tests and later runs. Treat persisted-preference writes inside
  tests as global side effects — reset them, or design assertions that
  do not care.

## Destructive tools run on copies

Migration, repair, "doctor", and cleanup commands are exercised against
a snapshot of real data in a throwaway location — never against the
live store — until they have proven themselves there. The live copy of
a user's data is not a test fixture.

## CPU contention breaks GUI truth

Heavy parallel jobs (builds, other agents' compilers) on the host
change GUI behavior: focus drops, animation frames stall, transient
surfaces auto-close. Verifications that depend on those properties are
only meaningful on a quiet host (see the waiting reference). Schedule
heavy background work and timing-sensitive GUI verification apart.

## Subagent fleets on one host

- Verify a subagent actually worked before consuming its output: a
  result with zero tool activity, or one that is generic boilerplate,
  is a misfire — relaunch it rather than integrating noise.
- One-shot delegation surfaces stay one-shot: a forwarder that launched
  a background job may be unable (by design) to poll or collect it.
  WHEN the runtime that owns the job exposes durable state (job files,
  state directories, logs) THEN you SHALL watch that state directly
  instead of re-tasking the forwarder.
- Background jobs owned by other runtimes keep running when your
  session ends or restarts. On session resume, re-discover what is
  still running before starting duplicates.
