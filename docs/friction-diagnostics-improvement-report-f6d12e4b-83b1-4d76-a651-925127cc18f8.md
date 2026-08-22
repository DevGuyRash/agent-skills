# Friction Diagnostics Improvement Report — the mica marathon field study

**Report ID:** f6d12e4b-83b1-4d76-a651-925127cc18f8 **Date:** 2026-07-18 **Author:** the agent that lived the session under study (Claude, primary thread), with two transcript-mining subagents **Plugin under review:** `plugins/friction-diagnostics` (skills `friction-diagnostics` v5.1.3 + `friction-mend` v5.1.3, SessionStart hook), in `/home/rashino/repos/agent-tooling`

---

## 0. What this report is and how to read it

This is a field study, not a design review. One continued Claude Code conversation (session ids `aaa35ccf` → … → `d9824d96` → `2feccc82` across restarts; transcript ~50 MB; roughly Jul 12–18) rebuilt an Obsidian plugin ("mica", Rust WASM core + TypeScript shell) through ~17 feedback rounds: parser rewrites, drag-and-drop, grid semantics, four multi-layer root-cause hunts, a four-agent polish fleet, and dozens of deploys against a live vault. The friction-diagnostics plugin was installed and armed the whole time.

**The headline finding: the session generated at least 22 distinct friction episodes, of which ~20 pass the plugin's own worth-logging test — and the visible session filed zero of them contemporaneously.** Two records were filed by one earlier incarnation of the same conversation (`d9824d96`, whose window is compacted out of the author's memory); everything else landed in competing sinks (the project's own AGENTS.md doctrine file, `state.md`, and long commit messages) or nowhere at all.

Evidence base:

- Full read of both SKILL.mds, `hooks/hooks.json`, `hooks/friction-session-env.sh`, `references/integration.md`, `references/mend-playbook.md`, and the script inventory.
- Hands-on exercise of `report-friction.sh`: one scratch filing (via `--events-file`) plus **three real events filed into the mica store during this review** (evt-0007 `synthetic-events-mask-native-defaults`, evt-0008 `obsidian-relaunch-races-dying-instance`, evt-0009 `codex-forwarder-one-shot-scope`) — so the filing UX claims below are observed, not read.
- The mica repo's live store: `/home/rashino/repos/mica/.local/reports/friction/` (6 records before this review, spanning Jul 8–18; **no `known-traps.md`; zero resolutions; INDEX shows 5 open clusters**).
- Two subagents that sparsely sampled the 50 MB transcript with different lenses (a friction census; a plugin-fit/trigger diagnosis). Their quantitative claims are marked as theirs.
- Prior improvement reports in `docs/` were skimmed to avoid re-proposing known items; where this report corroborates one (notably `a13a0ba6`'s "capture worked; the learning loop did not close"), it says so and adds fresh evidence rather than repeating the argument.

Two honest scope notes. First, the author reviewed a plugin whose job is to catch the author's own blind spots; the two subagent lenses and the live store were used as external checks precisely because self-report is weak evidence here. Second, the session predates none of the plugin — everything reviewed was live and available the entire time, which is what makes the zero-invocation figure meaningful.

---

## 1. The session in numbers

From the transcript miners (sampled, not exhaustive; counts are grep-based):

| Metric | Value |
| --- | --- |
| Transcript size / span | ~50 MB, ~5 days, 2 compactions |
| Feedback rounds / commits | ~17 rounds / 65 commits |
| `cargo test --workspace` gates | 47 |
| `xvfb-run` e2e suite runs | 153 |
| Obsidian relaunches (deploy ritual) | 36 |
| Background `task-notification`s / Monitor events | 154 / 82 |
| Distinct friction episodes identified post-hoc | 22 |
| Episodes passing the worth-logging test | ~20 |
| Episodes that RECURRED within the session | 8 families (one 11×, one 8×, one 5×) |
| Contemporaneous friction filings in the visible window | **0** |
| Filings by a sibling incarnation of the same conversation | 2 (evt-0005/0006) |
| Times the skill's trigger text was in context | 3 (session start, one skill-listing refresh, one late listing) |
| Occurrences of the word "surprise" in 50 MB (outside skill listings) | ~2 (both product copy) |
| Occurrences of "silently" / "no-op" / "flake" / "stale" | 44 / 130 / 89 / 117 |

The last two rows are the trigger-design finding in miniature: the plugin listens for a word the working vocabulary never uses.

---

## 2. Holistic assessment

### 2.1 The core diagnosis: capture is attention-bound, not mechanics-bound

Filing an event is cheap and pleasant. Exercised live: one tool call, sub-second, and the talkback (event id, recurrence key, cluster/trap counts, ready-made `--recur` command) is genuinely useful. **The mechanics are not the bottleneck and should not be the focus of further engineering.**

What failed is attention economics. The session ran in tight loops — fix → gate (2-min background run) → deploy (socket ritual) → commit — saturated with interrupt-driven notifications (154 task notifications; one 8-minute stretch had 12 phase-oscillation events from a background Codex job). Every natural pause was pre-claimed by a competing distillation task: "While the gate runs, recording the hard-won doctrine in AGENTS.md" is a literal quote, and it has siblings at every pause point. The plugin's exact trigger condition was even _verbalized_ — "my model is missing something" — and the next action was forensics, not filing. The reflective act the plugin needs never had a scheduling slot.

This is the difference between this report and a design critique: the design assumes surprise produces a reflective beat; in a real high-pressure session, surprise produces _escalated instrumentation_. The plugin must either attach to beats that already exist (commits, session boundaries, compaction) or accept capture rates near zero for exactly the sessions that generate the most friction.

### 2.2 The competing-sink problem is real, user-mandated, and unaddressed

Midway through the session the user explicitly ordered lessons written into the project's own AGENTS.md ("update AGENTS.md … so we don't make the same mistake … add as much foundational knowledge as possible"). From then on, every root-cause produced doctrine: 58 "doctrine" mentions, four capital-R "Root-caused" narratives — all landing in AGENTS.md or commit bodies. The project file did, in-repo and user-visibly and _with the fix attached_, nearly everything the plugin's stated purpose describes ("so that instructions and environments can be mended and future sessions avoid known traps").

The SKILL.md never articulates what filing adds **when the lesson already has a home**. The honest answer exists — the event is the _cross-session, cross-repo index_ of the lesson; it carries recurrence counts, machine-queryable structure, and mend provenance that a doctrine bullet cannot — but the skill doesn't say it, and mid-session the third full write-up of an already-committed, already-doctrinized lesson lost every time. Worse, the skill _forbids_ the part the agent values most ("Do not propose fixes inside records"), making the filing feel like the strictly-worse sibling of the doctrine bullet.

### 2.3 The learning loop never closed (corroborating report `a13a0ba6` with fresh evidence)

The mica store demonstrates the open loop concretely: 10 days of history, 5 open clusters, **zero resolutions, no `known-traps.md` ever distilled** — so the one feed-forward affordance the capture side promises ("WHEN `known-traps.md` exists THEN read it before acting") had nothing to read, all session, in the very repo where two of its anchored traps re-bit (the Xvfb-empty-reading-view trap and the persisted-state e2e flake both recurred; the session's own words for the socket trap were "the classic state" — a textbook `--recur` moment against an anchor it never knew existed). Capture without the loop is a write-only diary; the store's unique value stayed invisible because it only speaks _after_ a filing, and there were no filings.

### 2.4 Invisible by design and by accident simultaneously

Three compounding invisibilities:

1. **The ambient integration was never installed.** `references/integration.md` ships a paste-ready AGENTS.md snippet whose entire purpose is to keep the policy in working context. The mica repo — which has the events store, meaning someone used the plugin there — never received the snippet. Nothing in the plugin detects or even mentions this gap at runtime.
2. **The trigger text was 10–40 MB behind the working position** for most of the session, and both compaction summaries carried loop state but zero friction-policy words. After each compaction, the skill effectively did not exist.
3. **The no-mention rule extinguishes the deliberation precursor.** "WHEN you filed nothing … you SHALL NOT mention friction diagnostics … anywhere in your response" is correct as user-facing etiquette, but for an LLM the externalized "is this friction?" check is often the _only_ mechanism by which the act happens. As phrased, the rule suppresses the check itself. The silent default becomes silent never.

The comparison case (miner finding): the only skills that reliably fired all session had imperative, domain-anchored triggers ("REQUIRED when any part of the task touches Rust — do not write Rust without this skill active"). Reflective self-diagnostic triggers did not fire once. Trigger phrasing is a lever with empirically demonstrated throw.

### 2.5 What the plugin gets deeply right (preserve these)

- **The worth-logging test** is the correct gate; post-hoc it cleanly sorted the 22 episodes (20 in, 2 marginal) with no ambiguity.
- **The field design** (`actual_outcome` verbatim-first, `reading` from inside the decision, `pivot_information` as an information-gap not a self-verdict, `sources[].claim` as prior-belief-only) produced records during the live filings that a stranger could judge. The discipline of "no fixes in records" is right _for the record_ — the problem is only that its value isn't argued.
- **The talkback loop** ("the store briefs you at the point of action") is the correct inversion — no pre-query needed.
- **Logging-only default posture with mend gated on user request** proved exactly right: an unsupervised mend during this session's fix-loops would have been noise.
- **Storage resolution** (repo `.local` area, `--events-file` override) behaved perfectly in hands-on use, including the scratch-store trial.
- **The exit-3 duplicate soft-stop** design was not triggered live but reads correct.

### 2.6 Verdict

The plugin is a well-built instrument pointed slightly away from where surprise actually happens, silent at the moments it must speak, and mute about its value against the sinks that outcompete it. Every high-value change is in the trigger surface, the ambient presence, and the loop closure — not in the recorder. "Nothing" was a permitted answer; the evidence does not support it, but it _does_ support a narrow answer: fix presence and attribution, and change very little else.

---

## 3. Atomistic findings

Ordered by severity. Each has evidence and a concrete, checkable change. File paths are relative to `plugins/friction-diagnostics/`.

### A1 — Session attribution is wrong in continued conversations (bug, live-proven twice)

**Evidence.** During this review, the live environment of session `2feccc82` carried `FRICTION_SESSION_REF=d9824d96-…` — a _previous_ incarnation of the same conversation. The three events filed during this review (evt-0007/8/9) are all stamped `session_ref: d9824d96…`, verifiably wrong. Independently, the transcript miner found session `aaa35ccf`'s shells carrying `1e9c6540` (its predecessor). Mechanism: `friction-session-env.sh` appends exports to `CLAUDE_ENV_FILE`; that file's contents survive process restarts within a continued conversation, so the last-written ref — possibly several restarts stale — wins. The hook's own comment ("the env file is per-session, so concurrent sessions in one repo attribute correctly") is false for the continued-conversation case, which for long work is the _common_ case. `transcript_path` goes stale identically, so a mend session drilling into "the transcript for this event" opens the wrong file.

**Change.** Stop treating the env var as authoritative. Have the hook write `{session_id, transcript_path, written_at}` to a sidecar (e.g. next to the events file or under the plugin data dir), and make `resolve_session_ref` in `scripts/_common.sh` prefer the sidecar when its `written_at` is newer than the env-derived value's provenance; keep env as fallback for hosts without the hook. Acceptance check: file an event immediately after a `--resume`/restart and assert `session_ref` equals the _current_ session id.

### A2 — The hook pollutes every process listing (plugin-caused friction, felt directly)

**Evidence.** Because the exports live in `CLAUDE_ENV_FILE`, every `zsh -c` command line carries ~560 characters of `export FRICTION_SESSION_REF=… FRICTION_TRANSCRIPT_PATH=…` preamble (duplicated up to 4× with two different session ids in observed snapshots). During the socket-recovery episodes — exactly the moments of highest time pressure — `pgrep -af`/`ps` scans returned walls of this noise; the author hit it repeatedly while hunting Obsidian pids. The miner located three byte offsets in the transcript where the pollution visibly degraded debugging output.

**Change.** Same fix as A1 (sidecar file instead of env), which removes the strings from command lines entirely. If env must stay, dedupe before append (skip when the same var=value pair already exists in the file). Acceptance check: mid-session `pgrep -af zsh` shows no `FRICTION_` strings.

### A3 — The trigger vocabulary does not match how surprise presents (design, empirically quantified)

**Evidence.** In 50 MB of a friction-dense session, the plugin's listening vocabulary ("surprise", "diverged from what you predicted") occurs ~zero times in working text, while the actual carriers of surprise occur hundreds of times: "silently" (44), "no-op" (130), "flake" (89), "stale" (117), plus the recurring shapes: a test that fails only in the sandbox, a green test masking a real-input bug, an edit script that half-applied, a background job phase-oscillating, a tool refusing scope, a deploy ritual misbehaving _again_. The exclusion clause ("intended test failures … are not friction") actively points away from the session's dominant surprise channel — 153 e2e runs — because a red test reads as "the test doing its job" even when the failure _reason_ was an environment betrayal.

**Change (specific text).** Rework the description's middle sentence to name the empirical carriers:

> …a tool, command, instruction, document, or assumption behaved differently than expected — including: a test that fails only in CI/e2e/sandbox (or passes there and fails for real users), a flaky or intermittent failure, an edit or command that silently no-opped, a background job or deploy that hung, oscillated, or timed out, a tool that refused, mangled, or mis-scoped a request, or a known trap biting again.

And narrow the exclusion to the _reason_: "Outcomes you predicted **for the reason you predicted** are not friction; a failure you expected whose cause turns out different **is**." Acceptance check: the description contains "flaky", "silently", "only in CI", "known trap biting again", and the reason-scoped exclusion.

### A4 — No presence at the beats the workflow actually has (design; highest-leverage single change)

**Evidence.** 65 commits; all four "Root-caused" narratives were composed at commit time; the census shows the least disruptive filing moments were the root-cause confession lines and the per-round commit/summary beats. The store also stayed silent at session start/resume/compaction despite holding `--recur` anchors for two traps the session re-hit.

**Change (two parts, both rate-limited and silent-when-empty).**

1. _Commit-coupled nudge:_ a PostToolUse hook matching `git commit` Bash invocations that injects at most one context line — "Root-caused something you didn't predict this round? File it or `--recur` (friction-diagnostics)." — throttled via touch-file to once per N minutes. The narrative is already being written at that moment; the nudge lands where the words are.
2. _Store speaks at boundaries:_ extend the SessionStart hook (and register for resume/compaction sources if the host exposes them) to emit ≤2 context lines **only when the repo store has open events**: "friction store: 5 open — top keys: `obsidian-relaunch-races-dying-instance` ×2, `synthetic-events-mask-native-defaults` ×1 … (`--recur` targets exist)." This is the known-traps affordance made real even before mend has ever run, and it survives compaction — the exact moment the census shows unlogged knowledge dying (the CLI named-params lesson recurred immediately after compaction 2).

Acceptance checks: hook emits nothing on empty stores; ≤2 lines otherwise; the commit nudge appears at most once per throttle window.

### A5 — Filing cost is unpriced when the lesson already has a sink (design)

**Evidence.** Every mid-session lesson was already being written once into a commit body and once into AGENTS.md doctrine; the skill demands a third, longest composition (5 narrative fields with min-length floors) and forbids including the fix. The sink won 22 out of 22 times.

**Change.** (1) One sentence in the SKILL.md Policy: "File even when the lesson is going into a commit message or repo doc — the record is the cross-session index of that lesson, and its `sources[].ref` may simply point at it." (2) A _pointer mode_ in `report-friction.sh`: when a source ref matches `commit:<hash>` or `<file>#<anchor>`, relax the narrative minimums so a 3–4 line filing validates. The full elicitation stays the default; the pointer mode prices the marginal filing at ~15 seconds when the narrative demonstrably exists elsewhere. Acceptance check: a pointer-mode filing under current floors succeeds and the record round-trips through `query-friction.sh`.

### A6 — The no-mention rule suppresses the deliberation that precedes filing (design, one-word-class fix)

**Evidence.** Section 2.4. The rule as written bars mentioning friction diagnostics "anywhere in your response," which in practice extinguishes the internal check.

**Change.** Rephrase to target user-facing chatter only: "Never _narrate to the user_ the decision not to file, and never mention filings you didn't make — but you MAY consider filing silently at any point." Acceptance check: the SHALL NOT clause names narration/chatter, not consideration.

### A7 — Schema drift across record generations is undocumented (hygiene)

**Evidence.** mica's store holds records with `hindsight` (older generation) alongside the current contract's `pivot_information`/`decision`/`note`. The INDEX renders both fine; whether `cluster-hints.sh`/mend treat old-generation records as field-poor is unverified. Nothing documents the compatibility stance.

**Change.** A short "Record generations" note in the mend playbook: readers MUST treat `hindsight` as the ancestor of `pivot_information`+`decision` and never require fields a record's generation predates. If any script keys on the new fields' presence, add the fallback. Acceptance check: `cluster-hints.sh` and `query-friction.sh --format md` produce sane output on a store mixing both generations (mica's store is a ready fixture).

### A8 — Recurrence keys are undiscoverable until after the first talkback (minor)

**Evidence.** The socket ritual bit 8+ times before any filing existed; when finally filing evt-0008, the author had to invent the key blind. The `--recur` path presumes you know the anchor; the talkback teaches it only after a filing, and `known-traps.md` (the other discovery channel) did not exist.

**Change.** Covered almost entirely by A4's boundary summary (which lists open keys). Additionally, `report-friction.sh` could accept `--recur-key <key>` as an alternative to `--recur <event-id>` (resolve the key to its anchor; error listing candidates on ambiguity), so remembering the semantic name suffices. Acceptance check: `--recur-key obsidian-relaunch-races-dying-instance` resolves to evt-0008.

### A9 — The session-summary SHALL is fragile across continued conversations (minor)

**Evidence.** The sibling incarnation (`d9824d96`) filed evt-0005/0006; whether its final response included the mandated `render-summary.sh` output is unknowable from here — but the rule keys on "since your last assistant turn," which compaction and restarts make ambiguous. (This review complies for its own filings; see the summary at the end of the accompanying conversation turn.)

**Change.** Anchor the summary boundary to something durable: "since the newest `resolution`/summary marker in the store" or simply "records filed today," both computable from the store itself rather than from conversation memory. Acceptance check: the summary command's suggested invocation in SKILL.md derives its lower bound from the store, not the conversation.

---

## 4. Workarounds used in the observed session (things the plugin could have absorbed or indexed)

Recorded here because each is exactly the kind of operational knowledge that died in context instead of landing in the store:

1. **Codex plugin state read directly** (`~/.claude/plugins/data/codex-inline/state/<repo>/state.json` + `jobs/<id>.log`) after `codex:codex-rescue` forwarders refused follow-up by contract and `/codex:status` was model-blocked. Now filed as evt-0009.
2. **Pre-relaunch death verification** for the Obsidian socket ritual (`pgrep -cf … == 0` before `setsid`), discovered after four dueling-instance episodes. Now filed as evt-0008; the mendable artifact is mica's AGENTS.md ritual, which mandates the wait _after_ relaunch but not the check _before_.
3. **Trusted-input e2e via WebDriver element clicks** after synthetic events proved blind to native default actions (three separate shipped bugs). Now filed as evt-0007.
4. **Monitor phase-vocabulary discovery by observation** — a Monitor exited early because "editing" wasn't in its live-phase case list; the phase vocabulary lives only in the codex plugin's `state.json`. Unfiled (judged self-inflicted configuration rather than a misleading source; borderline under the current exclusion, in-scope under A3's reason-scoped rewrite).
5. **Windowed transcript sampling** (grep -b + byte-offset dd/sed reads) for mining a 50 MB JSONL without context overflow — used by both subagents in this review; generalizable to the mend playbook's "Transcript drill-down" section.
6. **`--events-file` scratch trial before first real filing** — worked perfectly; worth one line in the SKILL.md as the sanctioned way to rehearse without touching a real store.

## 5. Things that worked where the plugin was absent

For calibration, the sinks that _did_ capture lessons, and what they lack that the store has:

| Sink | What it captured | What it cannot do |
| --- | --- | --- |
| mica `AGENTS.md` doctrine | ~25 distilled bullets incl. all flagship root-causes, with fixes | No recurrence counts, no cross-repo reach, no machine queryability, no provenance chain; grows unboundedly; per-repo only |
| `state.md` | Deferred decisions, watch-items; one entry converted a false bug-hunt into a feature build (row-resize "regression") | Deliberately deletes resolved items — the history the store keeps is exactly what it discards |
| Commit messages | Narrative root-causes with diffs attached | Discoverable only by archaeology; never re-enter working context |
| Compaction summaries | Loop state | Demonstrably dropped operational trivia (the named-params lesson recurred immediately post-compaction) |

The plugin's pitch against these sinks writes itself from this table — but today the SKILL.md doesn't make it. That's finding A5.

## 6. Scope expansion assessment (grounded, mostly negative)

Considered against real session needs, honestly:

- **Cross-repo reporting** — already exists (`generate-report.sh --cross-repo`); the session's friction spanned mica and agent-tooling's own codex plugin, and the existing mechanism suffices once events exist. _No expansion needed._
- **Auto-capture from failing commands/hooks** — tempting (exit-144 recurred 11× undiagnosed) but wrong: it inverts the worth-logging gate and would flood the store with predicted failures. The commit-nudge (A4) is the right compromise. _Rejected._
- **Mend automation** — the session's fix-loops confirm the logging-only default; auto-mend would have collided with in-flight work. _Rejected; keep as-is._
- **A "capture-rate" metric** — one cheap addition with observed value: `generate-report.sh --report-type stats` could report events-per-active-day and days-since-last-filing, giving mend sessions (and users) the signal that a store is under-capturing relative to activity — this session's store would have shown 10 active days / 2 filings, a visible anomaly. _Modest yes._
- **Host-capability mapping (round 1's computer-use collapse)** — real pain, wrong plugin; belongs in host tooling. The friction store is the right place to _record_ such collapses (census #1 was log-worthy and unfiled), not to manage capabilities. _Rejected as scope; covered by A3's vocabulary widening._

## 7. Recommended implementation order

1. **A1 + A2** (attribution sidecar; de-pollute process listings) — a correctness bug with live evidence, small and self-contained.
2. **A4** (boundary presence + commit nudge) — the single highest-leverage capture-rate change; everything else assumes events exist.
3. **A3 + A6** (trigger vocabulary; no-mention rephrase) — text-only, zero risk, directly evidenced.
4. **A5** (additive-sink sentence + pointer mode) — one script change, one sentence.
5. **A8, A9, A7** (recur-by-key; store-anchored summary bound; generation note) — hygiene, as convenient.
6. Section 6's stats addition — with any mend-side release.

A deliberate non-recommendation: do not add ceremony to the recorder itself (more fields, mandatory interviews, validation layers). The hands-on filings were the best part of the product. The problem was never the pen; it was that the pen was in a drawer nobody opened.

## 8. Appendix A — the 22-episode census (transcript miner, condensed)

Line anchors refer to the `aaa35ccf` transcript. "Landed" = where the lesson was durably recorded, if anywhere.

| # | Episode | Root cause (as eventually found) | Worth test | Landed | Recurred |
| --- | --- | --- | --- | --- | --- |
| 1 | Computer-use/portal collapse driving live Obsidian (L176–503) | Never diagnosed; abandoned for CLI+e2e | Yes | Nowhere | ~10× |
| 2 | Editor click never ran in e2e (L1200) | Own root-guard allowlist swallowed mousedown | Yes | Fix only | Family → #15/#17/#19 |
| 3 | CLI bring-up: socket absent; `code=` named params (L1334) | CLI binds at app start; eval named-params only | Yes | Habit only | Yes — post-compaction |
| 4 | Left-clip fix didn't hold (L1649→L2052) | Theme rule gated on line-numbers ON; fixture had them OFF | Yes | Fixture + armor spec + AGENTS.md | Shipped-fix recurrence |
| 5 | Socket death/EADDRINUSE ritual (11 anchors) | Boot-time CLI spawns second instance unlinking socket; stale file blocks rebind | Yes | AGENTS.md + state.md | 8+× (most-recurrent) |
| 6 | `elementFromPoint` null mid-drag (L2648) | Fixture theme entrance animation frozen at 0% off-screen by sandbox compositor | Yes | snippet + AGENTS.md | No (3 instrumentation cycles) |
| 7 | No-op drop gaps / forced swap (L2347; L4897) | UI offered what reducer rejects | Yes | AGENTS.md | Yes — second manifestation caused by first fix |
| 8 | Friendly `tab:` glue absorbs insertions (L3632) | Closer-free grammar absorbs to EOF | Yes | AGENTS.md | Family → #13 |
| 9 | Scripted-edit half-applications (L3705; L4396) | Unasserted `str.replace` | Yes | AGENTS.md ("cost us two shipped half-changes") | ≥2× |
| 10 | Grid drag produced nothing (L3835) | Nested `data-mica-idx` poisoned membership via descendant selector | Yes | AGENTS.md | No |
| 11 | Dead settings (L3881) | Unverified wiring; literal-seeded controls | Yes | AGENTS.md | No |
| 12 | See-through popover (L4220) | Theme's rgba token inherited; `/ 1` alpha strip | Yes | AGENTS.md | No |
| 13 | Parser silently hid fixture tab (L4421) | Friendly-tab double-wrap inside `:::tabs` | Yes | Commit | Family of #8 |
| 14 | Source-tint 1-in-3 flake (L4923) | Obsidian's own preview widget requires FOCUS; programmatic cursor without focus impossible-user-state | Yes | AGENTS.md + commit | 3× before cornered |
| 15 | Last-tab ✕ dead / strip crossings (L5063; L6820) | Sibling stacking contexts swallow clicks at crossings | Yes | AGENTS.md (law named on 2nd hit) | R12→R16 pair |
| 16 | Drag-merge + phantom newline (L5767) | Reducer blank-line separator model; parser granularity | Yes | Reducer fix + pins | No |
| 17 | Reveal-flip trusted-input saga (L6487) | Native caret parked in chrome; MutationObserver sync annotated as user select | Yes | 2 AGENTS.md bullets + 4-layer defense | Internal (first fix failed) |
| 18 | Ctrl+Enter eaten by Completr (L6830) | Window-level hotkey consumes real keys; synthetic keydowns bypass | Yes | AGENTS.md + Scope fix | No |
| 19 | Widget menus never close (L6827) | Root-guard stopPropagation starves Obsidian's close listener | Yes | AGENTS.md | Family of #2/#17 |
| 20 | Word-diff never worked (L7921) | `similar` inline emphasis silently thresholds dissimilar pairs | Yes | Commit only | No (never worked) |
| 21 | Harness-rule bumps (5 anchors) | Blocked sleep / read-before-edit rules | Weak yes | Nowhere | 5+× |
| 22 | Exit code 144 signature (11 hits) | **Never diagnosed** | Yes | Nowhere | 11× |

Counter-example proving recorded state works when it exists: a `state.md` deferral note instantly converted a user "regression" report (row resizing) into a correctly-scoped feature build.

## 9. Appendix B — records filed during this review

Filed into `/home/rashino/repos/mica/.local/reports/friction/events.jsonl` as live exercise and to seed the anchors this session lacked:

- **evt-0007** `synthetic-events-mask-native-defaults` — the three-bug class (native caret, Completr hotkey, WebDriver focus churn) where synthetic-event e2e stayed green while real input failed; sources: the assumption that synthetic dispatch equals user input.
- **evt-0008** `obsidian-relaunch-races-dying-instance` — the deploy-ritual race; source: mica AGENTS.md's ritual, which omits the pre-relaunch death check.
- **evt-0009** `codex-forwarder-one-shot-scope` — codex-rescue's by-contract refusal of follow-up plus the one-write-task-per-workspace queue failure; workaround (plugin state files) recorded in `pivot_information`.

All three are stamped with the stale session ref `d9824d96` — the live demonstration of finding A1.

## 10. Closing

The instrument is good. The session it slept through was the richest friction environment it will ever see: 22 episodes, three flagship multi-day hunts, one trap that bit eleven times without a name. Everything this report recommends aims at one outcome — that the next such session files five events instead of zero, because the store spoke first, the trigger spoke the session's language, the commit beat asked one quiet question, and the record cost fifteen seconds when the narrative already existed. The recorder itself should be left alone.
