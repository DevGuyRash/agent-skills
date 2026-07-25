# Field Report: linux-desktop-control, Claude Perspective

- **Report ID:** 06a7dd5a-7a64-4b1a-9006-f874e7dca475
- **Author:** Claude (Claude Code session), writing from direct field
  experience; three subagent transcript miners supplied corroborating
  evidence and items outside the author's working memory.
- **Subject:** the `linux-desktop-control` plugin in this repository —
  what it would have contributed to a real, long, desktop-adjacent
  session it was NOT available for, and what was added as a result.
- **Deliverables shipped with this report:** a new Claude-targeted
  skill `claude-linux-computer-use` inside the plugin (SKILL.md + five
  references), a `.claude-plugin/plugin.json` manifest, and Claude
  marketplace registration. All validated (see §7).

---

## 1. Method and evidence base

This report is grounded in one ~17-round working session plus its
predecessor in the same thread: building and shipping an Obsidian
plugin (Rust/WASM core, TypeScript shell, CodeMirror widgets), with
repeated live deployments into the author's running desktop app,
end-to-end tests driving a real windowed app under xvfb, a companion
CLI (`obsidian eval`-style bridge) as the main verification channel,
and a closing phase that orchestrated multiple write-mode subagents on
one machine. The session never had this plugin loaded.

Three transcript miners re-read the session sparsely with different
lenses (app lifecycle + IPC; trusted-vs-synthetic input + GUI
verification; orchestration + waiting + host hygiene) and returned 42
evidence-anchored lessons between them, including incidents from early
thread segments outside the author's summarized context (a companion
bridge-daemon crash class; a stuck synthetic key writing garbage into a
user document).

Honest scope note: this was an IDE-heavy session *around* a desktop
app, not a pixel-driving session. The findings therefore concentrate on
the operational shell around GUI interaction — lifecycle, channels,
input realism, waiting, host sharing — and say little about screenshot
targeting or accessibility-tree interaction, which the existing skill
already covers and this session barely exercised.

## 2. The plugin as found (so this report is self-contained)

`plugins/linux-desktop-control/` contains one skill (same name),
published **for Codex only** (`.codex-plugin/plugin.json`; the Claude
marketplace did not list it). The skill is a capability-driven
*interaction contract*: route work to the narrowest capable surface
(browser automation vs. desktop control vs. API vs. tests); build a
live capability record (available → operational → effect-verified);
target uniquely before sending input; verify every state change by an
independent observation; recover per channel with a bounded retry
budget; map image↔desktop coordinates explicitly; report
`verified | unverified | blocked | not attempted`; minimize captured
information. Four references (routing, verification, recovery,
portability) total ~250 lines. The writing is disciplined EARS-style
and deliberately implementation-agnostic.

## 3. Holistic assessment

**The existing skill is right, and it is aimed at the moment of
interaction.** Its core stance — an acknowledgement is not success;
verify user-visible outcomes independently — is exactly the stance this
session converged on unprompted (every round ended with a live
verification in the real app). Had it been loaded, none of its content
would have caused friction, and its verification vocabulary would have
sharpened several of my completion reports.

**But almost none of this session's expensive failures happened at the
moment of interaction.** They happened in the layers the plugin does
not address:

| Layer | Share of session's desktop friction | Existing coverage |
|---|---|---|
| App process lifecycle (races, stale sockets, respawns) | high | one clause ("invalidate caches after relaunch") |
| Companion CLI/eval channels (quoting, async relay, boot bans) | high | none |
| Real-vs-synthetic input divergence | high (two shipped-bug classes) | none |
| Waiting/monitoring discipline | medium | one line ("no arbitrary sleeps") |
| Shared-host hygiene (multi-agent, ambient state, load) | medium | one line ("keep desktop ops serialized") |

The holistic conclusion: **extend, don't rework.** The plugin needed a
second skill that owns "everything around the click," complementary to
the existing skill's per-action contract, cross-referencing rather than
duplicating it. That is what was added. The alternative — growing the
existing skill — was rejected because (a) the existing skill is
Codex-addressed and shipping; (b) its progressive-disclosure budget is
healthy and these five domains would triple it; (c) the request was
explicitly for a Claude-targeted skill.

**On "would nothing have been acceptable":** for the existing skill's
own content, essentially yes — I found no incorrect instruction in it,
and I deliberately changed none of it. The contribution is additive.

## 4. Atomistic findings

Each finding: what actually happened → the workaround used in the field
→ whether the plugin-as-found would have helped → where the lesson now
lives. "Ref:" names files under
`plugins/linux-desktop-control/skills/claude-linux-computer-use/references/`.

### 4.1 App lifecycle

1. **Probe-during-boot destroyed the IPC endpoint.** Any companion-CLI
   invocation while the single-instance app was booting spawned a second
   instance that unlinked the shared socket on exit. This was the single
   most repeated self-inflicted failure of the session. Workaround: a
   written recovery ritual (remove stale socket, SIGTERM the main pid,
   relaunch detached, wait ≥15 s with zero CLI calls). Plugin-as-found:
   no help. Ref: `app-lifecycle.md` (launching; recovery ritual),
   `companion-channels.md` (timing discipline).
2. **Stale socket file blocked the next bind.** In-app toggles
   re-attached to the dead inode; only deleting the file recovered.
   Plugin-as-found: no help. Ref: `app-lifecycle.md`.
3. **Process counting lied.** `pgrep -f` on an Electron app matched
   GPU/network/renderer helpers ("instances=4" was one app) and, worse,
   matched the agent's own invoking shell; signal kills exited nonzero
   (code 144) even when they worked. Two false "dual instance" scares
   and one killed probe resulted. Workarounds: match the main process's
   distinctive command line; exclude the shell; judge kills by
   re-probing state. Plugin-as-found: no help. Ref: `app-lifecycle.md`
   (counting honestly; terminating).
4. **Kill-vs-respawn fights.** The app kept reappearing (session
   restore / the human relaunching it); the agent initially kept
   killing it. Workaround: stop, observe who respawns it, adapt; late
   in the session, when the app was found closed at night, the agent
   correctly declined to relaunch it at all. Plugin-as-found: partial —
   its approval-boundary clause gestures at this; nothing states "the
   respawner outranks you." Ref: `app-lifecycle.md`, `host-hygiene.md`
   (human outranks you).
5. **Detachment and session env.** Bare relaunches died silently
   (missing Wayland/session env), leaving readiness waits hanging with
   nothing to observe; `setsid`/`systemd-run --user` launches survived.
   Plugin-as-found: no help. Ref: `app-lifecycle.md`.
6. **Lazy activation.** The plugin under test wasn't loaded until a
   relevant document was opened (a lazy-loader deferred it); absence in
   the runtime was misread as breakage until the activation condition
   was triggered. Plugin-as-found: no help. Ref: `app-lifecycle.md`.
7. **CLI shim vs. launcher name collision.** The companion CLI and the
   app launcher shared a binary name; probing the wrong one pokes the
   user's live session. Plugin-as-found: no help. Ref:
   `companion-channels.md`.

### 4.2 Companion channels

8. **Arg parser ate the payload.** The CLI's `key=value` parser
   mis-split JavaScript containing `=>`; template literals and arrow
   functions broke parsing ("Missing required parameter",
   "Unexpected end of input"). Workarounds: always pass
   `code='<payload>'` explicitly; rewrite payloads with `function(){}`
   and string concatenation. Plugin-as-found: no help. Ref:
   `companion-channels.md` (payload survival).
9. **Async results were unreachable.** The eval bridge could not await
   promises and swallowed console output. Workaround: have the app
   persist results to a file via its own storage API (write chained so
   the bridge awaits it), then read the file from the shell; treat a
   missing file as "the probe never ran," not as an empty result.
   Plugin-as-found: no help. Ref: `companion-channels.md`.
10. **Big probes failed silently; act/measure raced repaints.**
    Workarounds: decompose into tiny single-value probes; make
    mutate-and-measure probes atomic with internal retry; never trust
    observations captured mid-reload. Plugin-as-found: partial (its
    verification doctrine covers the observation half). Ref:
    `companion-channels.md`.
11. **Bridge daemons died and stuck keys corrupted user data** (from
    the thread's earlier segment): the IPC daemon needed an idempotent
    detached respawn, and a wedged synthetic typing path once wrote a
    repeating character into the user's real note — clipboard-set +
    single paste chord replaced long synthetic typing. Plugin-as-found:
    no help. Ref: `companion-channels.md` (bridge daemons).

### 4.3 Real vs. synthetic input (two shipped-bug classes found ONLY here)

12. **The caret escape.** A real mousedown on text-less widget chrome
    let the browser place the native caret outside a
    `contenteditable=false` island — `stopPropagation` was irrelevant
    because default actions are not handlers — flipping an entire
    rendered block to raw text for the user. Untestable and invisible
    with dispatched events; reproduced only under a real input driver;
    root-caused by wrapping the state sink and capturing
    `Error().stack` per mutation (the stack named the platform's
    MutationObserver, not app code). Plugin-as-found: no help (its
    verification contract validates outcomes, but nothing warns that
    synthetic input cannot exercise default actions). Ref:
    `real-input.md` (hidden-mechanism table; attributing mystery
    events).
13. **The stolen hotkey.** A third-party global hotkey consumed the
    real Ctrl+Enter at window level before the app's handler; synthetic
    keydowns dispatched at the element skipped the window path, so the
    test suite stayed green while the user's key "did nothing."
    Workaround: enumerate the host's global hotkey registrations to
    find the thief; defend with a focus-scoped override that stands
    down when the inner handler already consumed the event.
    Plugin-as-found: no help. Ref: `real-input.md`.
14. **Occlusion.** Controls were unclickable because a sibling overlay
    painted over them, while scripted `.click()` (which bypasses
    hit-testing) passed. The honest assertion was
    `elementFromPoint(center)` resolving to the control.
    Plugin-as-found: partial (target-identification clauses point the
    right direction; the specific "scripted clicks bypass hit-testing"
    trap is absent). Ref: `real-input.md`.
15. **Drift tolerance.** Real clicks drift a few pixels between press
    and release; a zero-drift activation design read as "the button
    just didn't trigger." `setPointerCapture` also throws for synthetic
    pointer ids (guard it). Plugin-as-found: no help. Ref:
    `real-input.md`.
16. **Coordinate space desync.** Raw driver coordinates desynced under
    app zoom; element-addressed driver clicks (driver computes the
    center) stayed correct and remained trusted input. Plugin-as-found:
    **yes — this is its coordinate-mapping doctrine**; the addition is
    only the "prefer element-addressed actions" default. Ref:
    `real-input.md`.
17. **Focus is environment-fragile.** Headless windows lost focus
    nondeterministically under CPU load; focus-gated app behavior
    changed between identical runs; drivers' focus churn closed real
    menus between steps. Workarounds: assert `document.hasFocus()`-class
    evidence inside the check; split fragile-vs-incidental steps across
    input tiers; run focus-dependent verification on a quiet host.
    Plugin-as-found: no help. Ref: `real-input.md`, `waiting.md`.
18. **Headless compositors freeze animations; reused windows carry
    stale scroll** — DOM assertions stay green while every pixel-level
    check fails. Workarounds: neutralize entrance motion narrowly in
    test environments; normalize scroll before coordinate work.
    Plugin-as-found: no help. Ref: `real-input.md` (headless rendering
    honesty).
19. **Provenance gating and adversarial focus restore** (design-level):
    platform-synthesized changes (focus restores, observer syncs) must
    not trigger user-only behavior — branch on event provenance; and a
    dismissing menu restores focus AFTER your handler, yanking focus
    you just took — defer focus-taking work one tick. Plugin-as-found:
    no help. Ref: `real-input.md`.

### 4.4 Waiting and monitoring

20. **Chained sleeps were rejected by the harness** (three times) and
    were wrong anyway. Workaround: condition-based waits (until-loops on
    the actual signal) and single background commands that exit when
    the condition holds. Plugin-as-found: partial (one line: no
    arbitrary sleeps). Ref: `waiting.md`.
21. **A watch loop enumerated live phases and treated the default as
    terminal** — the first unlisted live phase ("editing") ended the
    watch mid-job. The corrected loop inverted the logic: enumerate the
    small stable TERMINAL set; everything unknown keeps waiting.
    Plugin-as-found: no help. Ref: `waiting.md` (exhaustive terminal
    states).
22. **Per-phase-change watchers burned a full agent turn per event**
    across a long external job; the fix was silent-until-terminal
    watchers. Two watchdog timeouts were then correctly read as
    evidence ("the endpoint never bound") rather than re-armed
    unchanged. Plugin-as-found: no help. Ref: `waiting.md`.

### 4.5 Shared-host hygiene and orchestration

23. **Workspace write-lock.** Launching two write-mode subagent jobs on
    one checkout: the second failed at queue time. Workaround:
    serialize writers, partition file territories explicitly in every
    dispatch prompt. Plugin-as-found: no help. Ref: `host-hygiene.md`.
24. **One-shot forwarders refused follow-up by design.** The delegation
    surface could launch a job but not poll it; the coordinator had to
    locate the runtime's own on-disk job ledger
    (`state.json`, `jobs/*.log` under the plugin's data dir) and watch
    phases directly. Plugin-as-found: no help. Ref: `host-hygiene.md`
    (subagent fleets).
25. **A subagent misfired with boilerplate and zero tool calls**;
    detected via usage stats and relaunched with a more explicit
    opener. Plugin-as-found: no help. Ref: `host-hygiene.md`.
26. **Ambient state steered a test days later.** The repo doubled as
    the live app's plugin directory, so the developer's live settings
    (`data.json`) traveled into every sandbox copy; a preference the
    user had clicked in their real app flipped an unrelated test's
    layout assertion. Workaround: tests pin every mode they assert on.
    Plugin-as-found: no help. Ref: `host-hygiene.md` (ambient state
    leaks).
27. **CPU contention from parallel agents broke GUI truth.** With other
    agents' compilers saturating the host, the windowed test display
    lost focus and a focus-gated test failed deterministically —
    passing again on a quiet machine. Plugin-as-found: no help. Ref:
    `host-hygiene.md`, `waiting.md`.
28. **Destructive tooling ran against copies.** Migration/repair
    commands were smoke-tested against a copy of real data, never the
    live store. Plugin-as-found: partial (approval-boundary clause).
    Ref: `host-hygiene.md`.

## 5. What was delivered

A second skill inside the plugin:
`plugins/linux-desktop-control/skills/claude-linux-computer-use/`

- `SKILL.md` (107 lines): router + a 12-clause action contract carrying
  only the cross-cutting rules; mandatory-pattern description
  (985/1024 chars) addressed to Claude, mirroring how the sibling
  addresses Codex; explicit division of labor with the sibling skill
  (it owns the per-action interaction contract; this owns lifecycle,
  channels, input realism, waiting, host sharing).
- `references/app-lifecycle.md` (91), `companion-channels.md` (81),
  `real-input.md` (~110), `waiting.md` (76), `host-hygiene.md` (84):
  one domain each, 4.x findings generalized to any app/host — no app
  names, no host paths, no tool-brand dependencies (named commands like
  `setsid`/`pgrep` appear as examples of capability classes, with the
  class stated so substitutes remain valid).
- Packaging: `.claude-plugin/plugin.json` added (plugin published for Claude at 1.0.0, matching the Codex manifest); plugin registered in the root Claude marketplace manifest.
  The Codex catalog entry is untouched; the Codex-addressed sibling
  skill is untouched.

Design choices that keep it non-brittle to upstream change: rules are
phrased against mechanisms (single-instance semantics, parser
boundaries, default actions, stacking of terminal states) rather than
against today's tool names or APIs; every named tool is an example of a
class, not a dependency; nothing encodes a path, service name, port, or
vendor behavior that an upstream release could invalidate.

## 6. Deliberately NOT proposed

- **No changes to the existing sibling skill.** Nothing in it was
  contradicted by field experience; rewording its Codex-addressed
  description for dual-host use is a separate, whole-plugin decision.
- **No merger of the two skills.** Peak-context budgets and the
  distinct trigger surfaces argue for two skills with one boundary
  sentence each.
- **No scripts.** None of the lessons reduce to deterministic logic
  worth a bundled script yet; the recovery ritual is five steps whose
  specifics (which files, which signals) are app-dependent.
- **No screenshot/multi-monitor guidance.** This session barely
  exercised that surface; the sibling's portability reference already
  covers coordinate mapping, and the author's host-specific monitor
  rules are correctly private per-machine configuration, not plugin
  material.
- **No duplication of the verification contract.** The new skill
  states once that the sibling's contract applies unchanged and adopts
  its status vocabulary.
- **No "computer-use MCP" specifics.** Tier systems, tool loading, and
  request/approval flows are host-runtime instructions that hosts
  already inject; encoding them would be brittle and redundant.

## 7. Validation status

- `plugin_port.py validate plugins/linux-desktop-control --host claude`:
  success; external validator passed; 0 warnings.
- Round-trips to Codex and back per repo policy: success, 0 warnings;
  converted artifacts left in `.local/tmp/` scratch (not committed).
- Description length 985/1024; no CRLF anywhere in the new skill; all
  files within the repo's context-budget guidance (SKILL.md 107 lines;
  references 76–110; peak context ≈ SKILL.md + one reference).
- Not validated: real-session trigger behavior (does the description
  fire when it should for live Claude sessions?) — this requires
  installed-cache updates after a push (the marketplaces track the
  GitHub remote, so local changes reach installed hosts only
  post-push) and a fresh session; recommend a follow-up field session
  and, if drift appears, a `skill-auditor` pass.

## 8. Closing answer to the prompt's first question

Yes — but with the honest boundary drawn: this session taught a great
deal about *operating around* desktop applications (five domains,
28 findings above, two of which were shipped-bug classes invisible to
synthetic testing), and comparatively little about the pixel-targeting
surface the existing skill already owns. The contribution reflects
exactly that split: everything learned was added; nothing beyond the
evidence was invented.
