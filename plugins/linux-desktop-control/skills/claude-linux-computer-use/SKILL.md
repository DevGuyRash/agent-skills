---
name: Claude Linux Computer Use
description: >-
  REQUIRED when Claude launches, restarts, scripts, waits on, or verifies
  desktop applications and their companion channels on a host machine — do
  not manage GUI app processes, drive an app CLI/eval bridge, or trust
  synthetic-input results without this skill active. Covers: (1) App process
  lifecycle: single-instance races, stale socket/lock recovery, detached
  launches, honest process counting, respawns and user contention, (2)
  Companion channels: CLI/IPC payload quoting, async result relay, probe
  sizing, boot-time bans, bridge daemon recovery, (3) Real vs synthetic
  input: what dispatched events hide (focus, caret, hotkey interception,
  hit-test occlusion) and the input escalation ladder, (4) Waiting
  discipline: condition-based waits, exhaustive terminal states, silent
  watchers, load-sensitive GUI checks, and (5) Shared-host hygiene: one
  writer per surface, ambient config leaking into fixtures, human-first
  etiquette. If the task touches a running desktop app, use this skill.
---

# Claude Linux Computer Use

Operate desktop applications as long-lived, shared, fragile systems —
not as targets that merely receive clicks. The sibling skill
**Linux Desktop Control** owns the per-action interaction contract
(routing, targeting, verification, recovery, portability); this skill
owns everything around the click: process lifecycle, scripting channels,
input realism, waiting, and coexistence with the human and other agents.

> The costliest desktop failures in the field were not missed clicks.
> They were self-inflicted: a probe that launched a second instance, a
> kill that raced a respawn, a synthetic test that passed while the real
> keystroke was consumed elsewhere, and a fixture that inherited the
> developer's live settings.

## Start Here

1. Identify which surfaces the task touches: app processes, a companion
   channel (CLI/socket/eval), input into a GUI, waits on async state, or
   a host shared with the human or other agents.
2. Read only the matching reference(s) from the index below before the
   first state-changing action on that surface.
3. Keep the sibling skill's rule in force throughout: an
   acknowledgement is not success — verify user-visible or persisted
   outcomes independently.

## Action Contract

1. WHEN a target app is single-instance THEN you SHALL treat every
   launcher or same-named CLI invocation during its boot or shutdown as
   a second-instance hazard, and you SHALL wait for a positive readiness
   signal before the first companion-channel call.
2. BEFORE terminating an app THEN you SHALL check for signs the human is
   actively using it; IF a terminated app reappears THEN you SHALL stop
   killing it and adapt.
3. WHEN counting or killing processes by pattern THEN you SHALL match
   the main process distinctively, exclude your own shell and matcher,
   and judge success by re-probing state — never by the kill command's
   exit code.
4. WHEN a companion endpoint is dead THEN you SHALL follow the stale-
   endpoint recovery ritual exactly once before re-diagnosing (see the
   lifecycle reference).
5. WHEN passing code or data through a companion CLI THEN you SHALL
   protect the payload from every parser boundary it crosses, and WHEN a
   probe is async THEN you SHALL relay results through a persisted
   artifact and treat a missing artifact as "the probe never ran".
6. WHEN a verification passed with synthetic input but the human reports
   failure THEN you SHALL treat real-vs-synthetic input divergence as a
   primary hypothesis and re-verify at a higher input tier.
7. WHEN asserting that a control is reachable THEN you SHALL hit-test at
   its point; a scripted click that bypasses hit-testing is not
   evidence.
8. WHEN waiting on any condition THEN you SHALL use condition-based
   waits (never chained sleeps), enumerate terminal states exhaustively,
   treat unknown states as "keep waiting", and emit notifications only
   for states you will act on.
9. WHEN a GUI verification depends on focus or sub-second timing THEN
   you SHALL run it on a quiet host and assert the focus/timing
   precondition as part of the check.
10. WHEN orchestrating multiple agents on one host THEN you SHALL grant
    one writer per mutable surface, serialize behind runtime lock
    rejections, and never parallelize GUI-touching work on one seat.
11. WHEN a test or fixture asserts on a configurable mode, layout, or
    default THEN the test SHALL pin that state itself; ambient values
    from live profiles are not stable inputs.
12. WHEN a subagent result shows zero tool activity or generic
    boilerplate THEN you SHALL treat it as a misfire and relaunch rather
    than integrate it.

## Reference Index

Load only the reference required for the current decision.

| Reference | Read when |
|---|---|
| `<skills-file-root>/references/app-lifecycle.md` | Launching, terminating, counting, or recovering an app; stale sockets/locks; respawns |
| `<skills-file-root>/references/companion-channels.md` | Driving an app through a CLI, socket, debug port, or eval bridge |
| `<skills-file-root>/references/real-input.md` | Choosing input tiers; a test passes but the user's input fails; occlusion, focus, or hotkey suspicion |
| `<skills-file-root>/references/waiting.md` | Any wait, poll, watcher, or timeout decision; flaky timing-dependent checks |
| `<skills-file-root>/references/host-hygiene.md` | Multiple agents or the human share the machine; fixtures inherit ambient state; contention suspicion |

## Completion Report

Report the requested outcome first with the sibling skill's status
vocabulary (`verified`, `unverified`, `blocked`, `not attempted`), then
any lifecycle actions taken that the user would notice (restarts,
killed processes, endpoint recoveries), and any standing constraint
discovered (load sensitivity, single-writer locks, respawn owners).
