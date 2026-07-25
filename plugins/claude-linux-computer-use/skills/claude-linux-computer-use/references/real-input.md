# Real Input vs Synthetic Input

Synthetic events (dispatched objects, scripted `.click()`, injected
keydowns) exercise an app's *handlers*. Real input additionally triggers
the platform's *default actions* — focus transfer, caret placement,
hit-testing, window-level shortcut interception. A whole class of bugs
is invisible to synthetic input and only appears for the human.

WHEN a verification passed with synthetic input but the human reports
failure THEN you SHALL treat "synthetic vs real" as a primary hypothesis,
not a last resort.

## What synthetic input cannot see

| Hidden mechanism | Symptom for the human | Honest check |
|---|---|---|
| Native focus/caret placement on press (a default action; stopping propagation does not stop it) | Focus or selection jumps somewhere unexpected; state "flips" after a click | Real pointer input, or instrument focus/selection state before+after |
| Window-level shortcut interception (global hotkeys, other extensions' key scopes) consuming REAL keys before app handlers | A shortcut "does nothing" for the user while scripted key events work | Send a real key press; enumerate the host app's global shortcut registrations for collisions |
| Hit-test occlusion (another element covers the control) | Button "doesn't work"; scripted `.click()` bypasses hit-testing and passes anyway | Hit-test at the point (`elementFromPoint`-class query) and require the target to own the point |
| Pointer-capture and coordinate-space APIs | Scripted pointer ids have no active pointer (capture calls throw); coordinate-based drivers desync under display/app zoom | Guard capture calls; prefer element-scoped driver actions over raw coordinates |
| Movement between press and release | "The button just didn't trigger" — a native click dies on a few pixels of drift | Test activation with drift, not only with a perfectly still click |

## The escalation ladder

Use the weakest input tier that can *prove* the outcome, and escalate
when a tier cannot represent what the human does:

1. Semantic/API action (the app's own commands, accessibility actions).
2. Element-scoped driver interaction (the driver computes coordinates —
   immune to zoom/scale desync that manual coordinate math suffers).
3. Real OS-level pointer/keyboard input.
4. The human (when real input under your control still cannot reproduce
   their environment: their plugins, their shortcuts, their display).

Trust cannot be faked at the property level: spoofing an `isTrusted`-
style flag on a synthesized event does not run the platform's default
actions. Genuine trusted input comes only from a real input driver or
the live app.

WHEN a defect only reproduces at a tier you cannot drive THEN you SHALL
say so explicitly rather than reporting the lower tier's pass as proof.

## Focus is load-bearing and environment-fragile

- Focus-gated behavior (widgets that only reveal, shortcuts that only
  fire, for a focused window) silently changes in headless or unfocused
  windows. Window managers in test displays may never grant focus, and
  heavy CPU load on the host can cause focus loss mid-test.
- WHEN a check depends on focus THEN you SHALL assert the focus state
  itself (`document.hasFocus()`-class evidence) as part of the check,
  and run timing- or focus-sensitive verification on a quiet host.
- Drivers and menus interact badly: real menus close on the window-focus
  churn that automation produces between steps. WHEN a transient surface
  (menu, popover) must survive multiple steps THEN you SHALL minimize
  round trips between them or re-open per step.

## Headless rendering honesty

Coordinate-level checks under a headless or test compositor have their
own traps, distinct from focus:

- Frozen animations: a headless compositor may never advance CSS
  animations, so an entrance transform can pin content off-screen
  forever — every DOM assertion stays green while every pixel hit-test
  fails. Neutralize entrance motion in the test environment (narrowly:
  the offending animation, not all motion).
- Stale scroll and reused windows: reused test windows carry scroll
  positions and view state from earlier flows. Normalize (scroll the
  target into view, or use a fresh window) before any coordinate
  interaction; DOM queries do not care, pixels do.

## Provenance and focus-restoration design

Two design-level rules that repeatedly separate "works for the script"
from "works for the human":

- WHEN programmatic and user actions share a code path but must behave
  differently THEN branch on event provenance (a user-event annotation,
  an `isTrusted`-class flag) rather than on the action having occurred.
  Platform-synthesized changes (focus restores, observers syncing state)
  arrive without provenance and must not trigger user-only behavior.
- Focus restoration is asynchronous and adversarial: a dismissing
  component (menu, dialog) restores focus AFTER your handler runs, and
  will yank focus you just took. Defer focus-taking work out of another
  component's dismiss cycle (next tick) instead of fighting it.

## Attributing mystery events

When state changes and nothing in your code explains it, instrument the
app's dispatch/entry point and capture stack traces per event
(wrap-and-log with the platform's error-stack facility). One captured
stack that shows a platform observer or framework internals — rather
than app code — redirects the whole investigation from "what did we
dispatch" to "what did the platform synthesize".

## Writing honest checks

- An occlusion bug is only testable by hit-testing; a passing scripted
  click is not evidence the control is reachable.
- Include at least one real-input path in acceptance checks for
  interactive chrome (buttons, pills, handles), and keep synthetic paths
  for logic-level assertions — both, not either.
- Trusted-input checks in harnesses have their own environment hazards
  (focus churn, zoom desync); when a harness cannot deliver a step with
  real input reliably, split the check: real input for the fragile
  surface, synthetic for the rest, and document why.
