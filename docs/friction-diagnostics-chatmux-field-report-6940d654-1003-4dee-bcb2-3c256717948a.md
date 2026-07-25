# Friction Diagnostics: Chatmux Field Study and Foundational Plugin Review

**Report UUID:** `6940d654-1003-4dee-bcb2-3c256717948a`

**Created:** 2026-07-14

**Target repository:** `/home/rashino/repos/agent-tooling`

**Target plugin:** `plugins/friction-diagnostics`

**Audited revision:** `ff3e4f2bc2b634692f8ecc07549bf7bffaf253b9`

**Audited plugin version:** `5.1.3`

**Primary field case:** the multi-day Chatmux browser-extension build and qualification

**Scope:** Friction Diagnostics capture, Friction Mend convergence, persistence, reporting, integration, and verification

## Executive verdict

Yes. The Chatmux work produced enough real evidence to contribute dramatically to this plugin.

The evidence does not support replacing the premise. The premise is the strongest part: capture a genuine mismatch between prediction and reality while the prior model is still recoverable; preserve what supported the prediction, what the agent did, and what information would have changed the decision; then mend the resulting corpus deliberately rather than rewriting a system around one anecdote.

Chatmux validated that model across browser policy, browser capability skew, ephemeral handles, provider-specific editor behavior, browser-rendered SVG errors, documentation-helper failures, accessibility serialization, IndexedDB recovery, and desktop-control readiness. Nine events used one domain-neutral schema and remained intelligible days later without rereading the full transcript. That is strong field evidence for generality.

The implementation is not yet safe or coherent enough to be a foundational learning layer. The primary weaknesses are enforcement and lifecycle:

1. Capture worked, but the learning loop did not close. Chatmux ended with nine full events, zero recurrences, zero resolutions, and no `known-traps.md`, even though at least two recorded product defects were fixed and verified before the task ended.
2. The same lifecycle concepts are independently reimplemented in several shell/Python/jq reducers. They already disagree about reopening after recurrence, singleton versus recurring “clusters,” and cross-store event identity.
3. Storage and evidence handling do not meet the sensitivity implied by the data. The event stream can be world-readable under a common umask, structured source strings can bypass sanitization, malformed payloads can be echoed or quarantined verbatim, and repository routing can record one root while writing under another.
4. Mend’s feed-forward artifact is not grounded strongly enough. `update-traps.sh` accepts fabricated keys, anchors, counts, dates, and arbitrary prose.
5. The installed plugin does not itself ensure that known traps are read at session start. That behavior depends on an optional repository snippet, while the plugin manifest speaks as if it is automatic.
6. The smoke suite has useful breadth and all 18 scenarios pass, but CI does not select it for changes to most of the code it is meant to protect. Some tests also assert wording without asserting the behavior the wording promises.
7. Capture and Mend trigger descriptions overlap. The source repository simultaneously carries an older, incompatible `/tmp/skill-errors` logging policy, splitting evidence into two systems with different thresholds and no shared mend path.

The single highest-leverage engineering change is one canonical store engine that owns record validation, recursive sanitization, identity, locking, append commitment, chronological lifecycle reduction, query semantics, and derived metadata. Every current shell surface can remain as a thin compatibility wrapper. This is an evolutionary consolidation, not a product rewrite.

The single highest-leverage product change is a complete, tested learning loop:

```text
surprise → capture → recurrence or distinct event → cluster → source repair or
explicit disposition → verified resolution → grounded active trap if needed →
future session reads it → future behavior demonstrably changes
```

The current system has strong evidence through capture. It has mechanical tests for later steps but no real field proof that a trap changed a future session. The next release should first make existing claims true, then prove one complete loop before expanding the ontology.

## Priority summary

| Priority | Recommendation | Evidence class |
| --- | --- | --- |
| P0 | Centralize persistence and lifecycle in one canonical engine | Multiple confirmed reducer contradictions and duplicated implementations |
| P0 | Make storage private and sanitize every persisted or displayed string | Confirmed source-field sanitization bypass and permissive modes |
| P0 | Make logical repository routing match physical storage; make reads non-mutating | Confirmed `--repo-root` mismatch and read-side `.local` creation |
| P0 | Bound lock waiting and distinguish append commitment from derived-view failure | Confirmed ownerless-lock hang and post-append failure window |
| P0 | Fix chronological reopen and store-qualified identity | Confirmed resolution/recurrence contradiction and cross-store false closure |
| P0 | Validate trap pointers and derive key/count/date from the store | Confirmed fabricated trap publication |
| P0 | Run the complete plugin test target for every relevant plugin change | Confirmed CI selector returns false for core script changes |
| P1 | Split Capture and Mend triggers; retire the parallel `/tmp/skill-errors` policy | Direct instruction conflict |
| P1 | Use neutral prediction-basis and best-available-primary-evidence language | Chatmux non-text/composite observations and causal ambiguity |
| P1 | Add session-aware query/summary and unambiguous report terminology | Confirmed offset filtering and “open clusters” ambiguity |
| P1 | Add structured resolution dispositions, verification, prevention, and ownership | Chatmux contains fixed, mitigated, accepted, and external cases |
| P1 | Improve cluster hints using pivot and source evidence before outcome tokens | Chatmux hint output produced weak false-positive groups |
| Pilot | Add a lightweight explicit closure affordance for already-fixed, verified events | Chatmux ended with fixed defects still shown as unmended; safety shape unsettled |
| Pilot | Add minimal anchor plus append-only enrichment | Exact short outcomes and long hot-path records create real pressure; adoption cost unmeasured |
| Pilot | Add an optional verification-boundary structure | Repeated proxy-success versus end-state failures in Chatmux |
| Defer | Relations, amendments, consequence taxonomy, automatic active brief | Plausible but not yet necessary for correctness |
| Reject now | MCP service, database, distributed locking, remote store, domain-specific diagnostics | No field evidence justifies the complexity or bespoke scope |

## 1. Evidence, method, and epistemic labels

### 1.1 Evidence inspected

The review used the full shipped plugin surface relevant to capture and mending:

- Both `SKILL.md` files.
- Codex and Claude plugin manifests.
- The Claude session-start hook.
- The event schema and both shipped copies.
- The field rubrics, logging specification, integration guidance, and mend playbook.
- Capture, recurrence, query, report, summary, index, clustering, resolution, and trap scripts.
- The POSIX smoke suite.
- Trigger-prompt and behavioral-eval artifacts.
- CI change selection and the local `just` command surface.
- The Chatmux friction stream and dashboard.
- The agent-tooling friction stream, including the plugin’s own prior audit events.
- Independent sparse thread passes focused separately on holistic behavior, atomistic incidents, plugin implementation, and skeptical scope control.

### 1.2 Verification performed in this review

- Confirmed the source skills are byte-identical to the installed Codex cache for version `5.1.3`.
- Ran all 18 POSIX smoke scenarios successfully.
- Queried the Chatmux store and generated its stats and cluster hints.
- Queried the agent-tooling store and generated its stats.
- Confirmed five large shared artifacts are duplicated byte-for-byte across Capture and Mend: `_common.sh`, `query-friction.sh`, `generate-report.sh`, `build-index.sh`, and `friction-event-schema.json`.
- Confirmed the CI change selector returns `false` for `report-friction.sh`.
- Inspected the lifecycle reducers, path resolver, JSON bridge, write order, resolution writer, and trap publisher directly.
- Filed one immediate surprise, then closed it append-only as non-reproducible after direct source and smoke verification. This supplied a small real Mend interaction without changing plugin source.
- Filed two cheap recurrences: the ambiguous talkback cluster metric and the known zsh `status` special-variable trap reproduced by a delegated lock probe.
- Preserved other agents’ reports and created this UUID-specific report without overwriting them.

### 1.3 Evidence labels

- **Known** means directly observed in the Chatmux thread, reproduced in a disposable probe, read directly from current source, or emitted by the current event store.
- **Inferred** means a recommendation follows from known evidence but the proposed product shape has not been field-validated.
- **Not verified** marks an outside-world or future-behavior claim for which this review has no direct proof.
- **Rejected for now** means the idea may be architecturally possible but the current evidence does not justify its cost or scope.

## 2. The current product model

Friction Diagnostics is not a generic error logger. Its gate is cognitive:

1. Reality differed from a prediction.
2. The difference was genuinely surprising rather than engineered or expected.
3. Preserving it would change what a future session does.

A full friction record preserves:

- the observed outcome;
- the prior expectation and its grounding;
- the reporter’s reading from inside the decision;
- the action actually taken;
- the information that would have changed the decision;
- the prediction bases called `sources`;
- workflow impact;
- a stable recurrence key and tags.

A recurrence record is a cheap pointer saying an earlier trap bit again. A resolution record is append-only provenance that one or more anchors were mended or deliberately closed.

The storage model is one JSONL stream plus two derived views:

- `INDEX.md` is a bounded dashboard.
- `known-traps.md` is a bounded, curated feed-forward artifact.

Capture is deliberately immediate and divergent. Mend is deliberately user-invoked and convergent. That separation is correct and should remain.

## 3. Holistic review: is this the right generalized shape?

### 3.1 What is already right

#### The surprise gate is high-signal

Chatmux did not produce a dump of every failed test or command. It produced nine events with reusable learning. Expected Playwright failures, planned red tests, ordinary compilation errors, and routine status did not flood the stream.

#### Point-of-divergence capture preserves the failed model

The records retain what the agent actually believed before the outcome. This matters because a corrected model makes the old prediction look less reasonable than it felt in the moment.

#### `decision` and `pivot_information` are unusually valuable

The Chatmux records preserved actual operational pivots:

- stop the prohibited Chrome-internal-page path;
- switch to a dedicated Playwright profile for install automation;
- perform browser discovery, claim, inspection, and cleanup atomically;
- clear provider editors with selection and keyboard deletion, then verify;
- keep console errors release-blocking despite passing visible workflow assertions;
- use official documentation after the manual helper failed;
- restart Brave without overwriting apparently missing data;
- treat input acknowledgements as proxies and verify visible outcomes independently.

Those are the reusable parts of the incidents. A conventional error log would usually preserve only the symptom.

#### The source ontology generalized adequately

`artifact`, `instruction`, `tool`, `assumption`, `memory`, and `observation` covered the field corpus. No Chatmux-specific source kind is needed.

#### Recurrence should remain cheap

During this review, the known zsh trap and talkback ambiguity were recorded as recurrence pointers rather than rewritten narratives. That path reduced ceremony as intended.

#### Capture and Mend should remain separate

Immediate records should not advocate fixes. A later corpus-level pass should decide whether events share an information gap and whether the right response is a source edit, guardrail, documentation change, external escalation, accepted risk, or no action.

#### The bounded trap view is the right feed-forward shape

Future sessions should not load an unbounded JSONL corpus. A maximum of fifteen concise, grounded active hazards is a sensible product boundary.

### 3.2 The core holistic failure: capture is not yet a maintained learning loop

At the Chatmux cutoff:

- 9 full friction records existed.
- 0 recurrence records existed.
- 0 resolution records existed.
- 9 anchors were reported as open.
- 1 was classified blocked.
- no `known-traps.md` existed.

At least two anchors no longer described unresolved product work:

- The invalid SVG path was corrected and protected by browser diagnostics and regression coverage.
- The invalid `aria-pressed` serialization was changed to explicit string states and verified.

The dashboard still reported them as open because “open” means only “not named by a resolution record.” That is mechanically consistent but operationally misleading.

The current opt-in Mend boundary explains the result: ordinary implementation can fix the source, but only a later explicit mend session records closure. By then, the freshest verification evidence is scattered across the transcript, diffs, and test output.

The answer is not autonomous batch mending. The safer direction is a narrow, explicit, append-only closure affordance when the primary task already authorized the fix and verification is present. This should be piloted, not silently enabled.

Proposed pilot policy:

> WHEN work already authorized by the primary task independently fixes the source of a filed event AND the fix is verified THEN you MAY offer or append a narrowly scoped resolution record. You SHALL NOT expand the task, edit an additional source, or infer that passing unrelated tests proves closure.

Proposed receipt:

```sh
record-resolution.sh \
  --resolves evt-0005 \
  --disposition fixed \
  --action "Corrected the malformed SVG path and added regression coverage." \
  --verification "The mounted UI and console-diagnostics suite no longer emit the parser error." \
  --ref "chatmux-ui/src/components/primitives/icon.rs"
```

The filing talkback could print a ready-to-edit resolution command for the new anchor. It should not execute it automatically.

### 3.3 The second holistic failure: evidence is stored where work happened, not where the source is owned

Only two Chatmux events clearly belonged to Chatmux source code. Most involved other owners:

| Events | Likely owner |
| --- | --- |
| `evt-0001`–`evt-0003` | Chrome/Browser policy, documentation, capability negotiation, handle lifetime |
| `evt-0004` | Provider interaction semantics and adapter tests |
| `evt-0005`, `evt-0007` | Chatmux UI and regression tests |
| `evt-0006` | OpenAI Docs manual helper and fallback guidance |
| `evt-0008` | Brave/Chromium extension reload and IndexedDB behavior |
| `evt-0009` | Computer Use readiness and KDE/AT-SPI/screenshot integration |

All nine live in the Chatmux store because Chatmux was the active repository. That preserves task context, which is good, but creates a discovery gap: the source owner does not automatically receive the event, while a Chatmux mend session may lack authority to edit most cited sources.

Do not duplicate canonical records across repositories. Add a derived owner-centric query.

Possible derived owner record:

```json
{
  "event_store": "/home/rashino/repos/Chatmux/.local/reports/friction/events.jsonl",
  "event_id": "evt-0002",
  "source_owner_root": "/home/rashino/repos/agent-tooling",
  "source_component": "chrome-control"
}
```

Possible query:

```sh
friction report owner-queue \
  --scan-dirs ~/repos \
  --owner-root /home/rashino/repos/agent-tooling
```

WHEN you derive an owner queue THEN you SHALL preserve one canonical event, qualify its store identity, and retain the task repository and session reference.

WHEN source ownership cannot be derived safely THEN you SHALL label it unknown rather than copying the event or inventing an owner.

### 3.4 The third holistic failure: deterministic state is implemented several times

The plugin independently computes related concepts in:

- `report-friction.sh` talkback and duplicate detection;
- `query-friction.sh` open-state filtering;
- `generate-report.sh` dashboards and stats;
- `cluster-hints.sh` open groups;
- `record-resolution.sh` target and prior-resolution inspection;
- `update-traps.sh` indirectly through query;
- duplicated copies of common query/report/index/schema artifacts inside both skills.

This is the upstream defect class behind multiple atomistic failures. A wording patch in one script will not make the system coherent.

Recommended target architecture:

```text
SKILL.md policy/router
        │
thin compatibility launchers
        │
one canonical deterministic engine
        ├── resolve store for read/write
        ├── parse, coerce, redact, validate
        ├── acquire/recover/release lock
        ├── append and emit committed receipt
        ├── chronological lifecycle reducer
        ├── qualified cross-store identity
        ├── query/report projections
        └── grounded trap projection
```

A packaged Rust binary is a natural fit for this repository’s current distribution direction, but the requirement is one tested engine, not Rust for its own sake. A single Python implementation packaged with the skill could also remove reducer drift. The shell commands and output contracts can remain stable during migration.

WHEN you migrate to a canonical engine THEN you SHALL preserve the existing JSONL format or provide an explicit, reversible migration path.

WHEN compatibility wrappers remain THEN you SHALL test them against the same engine rather than keep a second lifecycle implementation.

### 3.5 The plugin is domain-general but environment-specific

The cognitive model generalizes beyond software. The current runtime does not: it is a Linux/POSIX filesystem tool that relies materially on `jq`, Python 3, common Unix text utilities, and a packaged Linux renderer for the preferred table.

That is acceptable if stated honestly. “Generalized” should mean the event model applies across domains, not that every host or storage topology is supported.

Do not infer a need for a daemon, remote service, database, network store, or distributed lock from domain generality. No field evidence supports those additions.

## 4. Atomistic field ledger: what happened during Chatmux

### 4.1 `evt-0001` — Chrome internal URL blocked

**Expectation:** the connected Chrome control surface could open `chrome://extensions/` for the extension inspection requested by the user.

**Actual:** Browser Use rejected the URL under browser security policy and explicitly prohibited indirect circumvention.

**Workaround:** stop that path; keep the authenticated connected browser for provider tabs and use a dedicated Playwright-launched profile for automated rebuild/install testing.

**Plugin contribution:** strong. The record preserved the policy boundary and the architecture change, reducing the risk that a later agent would try a prohibited workaround.

**Proper mend target:** Chrome/Browser capability and documentation, not Chatmux and not Friction Diagnostics.

### 4.2 `evt-0002` — documented DOM snapshot capability missing

**Expectation:** `domSnapshot()` would work after successful browser bootstrap, tab discovery, claiming, and screenshots because the API documentation advertised it.

**Actual:** `TypeError: o.incrementalAriaSnapshot is not a function`.

**Workaround:** keep the working Chrome connection and use screenshots, visible DOM inspection, and bounded read-only evaluation.

**Plugin contribution:** strong. The event distinguished a capability/version mismatch from page-state failure.

**Proper mend target:** capability handshake and conditional documentation.

### 4.3 `evt-0003` — browser handles were ephemeral

**Expectation:** browser and claimed-tab handles would remain usable across calls because the guidance said bindings persist and tabs should be reused.

**Actual:** `Browser is not available: ...`; the same extension instance appeared behind changing browser IDs.

**Workaround:** perform name → list → claim → inspect → clear atomically in one browser-client call.

**Plugin contribution:** strong. The record preserved a reusable orchestration constraint.

**Proper mend target:** handle-lifetime documentation or a stable instance selector.

### 4.4 `evt-0004` — `fill("")` returned success without clearing state

**Expectation:** Playwright `fill("")` would clear the exact editors it had filled.

**Actual:** ChatGPT and Gemini cleared; Claude and Grok still contained `CHATMUX_SELECTOR_PROBE` after successful calls.

**Workaround:** focus the exact editor, use Control+A and Backspace, and read state back before continuing.

**Plugin contribution:** strong preservation of the verification boundary.

**Plugin quality issue exposed:** the event used impact `continued`, although a provider-specific workaround was required; by the current definitions, `degraded` or `noisy` would be more consistent.

### 4.5 `evt-0005` — malformed SVG path escaped compilation and visible workflow assertions

**Expectation:** a compiling UI with passing journey assertions would mount without extension-origin console errors.

**Actual:** the browser reported an SVG path parser error.

**Workaround:** retain console errors as release-blocking diagnostics, preserve the trace/screenshots, correct the icon, and rerun.

**Plugin contribution:** strong. Together with Playwright diagnostics, it exposed a defect that compilation and visible workflow assertions missed.

**Lifecycle issue exposed:** the source was fixed and verified, but the anchor remains open in Chatmux because no resolution record was appended.

### 4.6 `evt-0006` — Codex manual helper lacked expected hash metadata

**Expectation:** the helper would return the manual because the OpenAI Docs skill routed broad Codex questions through it.

**Actual:** `Manual response is missing x-content-sha256.`

**Workaround:** treat the helper as unavailable, use official documentation, and verify the custom installation locally.

**Plugin contribution:** good. It preserved an instruction/helper mismatch and the fallback.

### 4.7 `evt-0007` — Leptos boolean binding produced invalid ARIA serialization

**Expectation:** binding a selected boolean to `aria-pressed` would produce `"true"`.

**Actual:** the rendered button had `aria-pressed=""` despite visible selection.

**Workaround:** keep the semantic Playwright assertion and serialize explicit `"true"`/`"false"` strings.

**Plugin contribution:** strong. It converted a framework/rendering surprise into a reusable component rule.

**Plugin quality issue exposed:** the accepted `decision` contained future intent—“will change the component”—even though the contract requires completed history.

**Lifecycle issue exposed:** the component was fixed and verified, but the anchor remains open.

### 4.8 `evt-0008` — Brave IndexedDB service stalled after extension reloads

**Expectation:** the same unpacked extension ID and browser profile would rehydrate persisted workspaces after reload.

**Actual:** the UI showed no workspaces, IndexedDB returned `UnknownError: Internal error`, and runtime messages remained pending; the LevelDB files remained intact, and a full Brave restart restored the workspace and transcript.

**Workaround:** do not create replacement state, inspect the existing store read-only, restart Brave through its supported path, and verify recovery.

**Plugin contribution:** very strong. The decision record helped avoid converting a transient service failure into destructive data replacement.

**Model pressure exposed:** the outcome combines exact console text with precise observations of absence, pending behavior, disk state, and recovery. “Verbatim, never paraphrase” is too narrow for this valid incident.

### 4.9 `evt-0009` — Computer Use readiness was only partial

**Expectation:** a readiness headline plus available window targeting and input backend meant screenshots, accessibility, stable focus, and verifiable clicks were usable.

**Actual:** AT-SPI connection failed, the portal screenshot was denied, coordinate clicks returned `ok:true` without visible action, and focus sometimes moved to another application.

**Workaround:** inspect per-channel errors, reacquire the target window before input, prefer keyboard/direct navigation, use Spectacle and KWin tools as fallbacks, and verify every action from a fresh screenshot.

**Plugin contribution:** very strong. The record preserved the critical distinction between a lower-layer acknowledgement and the intended visible outcome.

**Model pressure exposed:** several independently actionable failure channels are combined in one event because they occurred in one incident. The plugin lacks related-event or incident grouping.

## 5. Significant thread episodes that were not captured

The absence of a record is not proof that no friction occurred. The plugin itself documents this self-report ceiling. Sparse transcript review found three meaningful omissions.

### 5.1 Automated browser sign-in was rejected by provider anti-bot behavior

The user offered to sign into a persistent Playwright browser, then reported that none of the providers would allow login in that browser and that it appeared to be treated as a bot. The test architecture moved to the user’s already-authenticated Brave session.

This was a user-reported contradiction of the prepared test path and materially changed the plan. No event was filed.

Generalized lesson: user-reported evidence can invalidate an agent-created assumption and should be explicitly eligible for capture. The plugin should not add provider or browser lore.

### 5.2 A package-wide ESM change broke the CommonJS Playwright runner

Changing package-wide module mode to silence Node warnings caused `ReferenceError: require is not defined in ES module scope` in `scripts/run-playwright-suite.js`. The workaround was to remove the package-wide setting and rename only true ESM helpers/tests to `.mjs`.

This was a genuine change-induced regression with reusable configuration learning. It was not logged.

Generalized lesson: self-caused regressions are still friction when the actual outcome violated the prediction. The surprise gate should not be interpreted as “only external tools can betray the model.”

### 5.3 A second Computer Use readiness failure was not filed as recurrence

After `evt-0009`, `move_window` selected a GNOME-oriented backend on KDE and failed with a DBus `ServiceUnknown`. `kdotool` then performed window movement and activation successfully.

This was a second manifestation of partial or incorrectly summarized readiness. It was neither filed as recurrence nor separated as a related distinct event.

Generalized lesson: recurrence counts understate traps when the agent does not receive a lightweight candidate reminder after a fallback succeeds.

### 5.4 Proposed candidate audit, not automatic logging

An opt-in end-of-turn candidate audit could scan the current transcript for likely unrecorded divergences:

- nonzero exit or `ok:false` followed by a successful fallback;
- user corrections such as “that did not work” or “I cannot sign in there”;
- a documented capability missing at runtime;
- a new workaround immediately after a failed proxy signal.

The audit should display bounded excerpts and nearby event IDs. It must not auto-file.

WHEN a candidate audit surfaces a possible event THEN you SHALL still apply the genuine-surprise and future-value test before filing.

WHEN a candidate matches an existing key or known trap THEN you SHALL offer recurrence before a new full record.

## 6. What worked where the plugin could have failed

The report should not flatten the plugin into a defect list. Several mechanisms worked well in this field case.

- JSONL records remained readable and structurally intact.
- Session references were populated, making transcript drill-down possible.
- The source-kind model covered the incidents without domain-specific expansion.
- Exact shell-sensitive content survived the normal JSON-stdin path in the smoke suite.
- An empty-stdin filing attempt wrote nothing, named common causes, and printed a safe retry shape.
- Duplicate handling offers explicit recur-versus-distinct choices rather than silently merging.
- The current report/index surfaces remained bounded enough for the 9-event Chatmux corpus.
- The 18-scenario POSIX smoke suite passes.
- Capture remained mostly silent about expected failures and task status.
- During this review, an initially plausible event was preserved and then honestly closed as non-reproducible without editing history.
- A known shell trap was recorded cheaply as recurrence rather than recomposed.

These behaviors should remain regression-protected.

## 7. Atomistic implementation findings

### 7.1 P0 — structured evidence bypasses uniform sanitization

The JSON path coerces and serializes `sources` before the top-level narrative sanitization pass. The final writer inserts `sources_json` directly. A prior disposable probe stored a fake `sk-...` token in `sources[].claim` unchanged.

The same policy gap extends to other strings:

- source refs;
- resolution refs;
- resolution action and note depending on ingress;
- recurrence notes;
- tags and titles;
- malformed JSON diagnostics and quarantine content;
- trap text.

The plugin claims write-time sanitization is always applied. That claim is currently false.

Proposed correction:

- Parse first.
- Coerce legacy shapes.
- Recursively redact every string in every record kind.
- Validate the redacted record.
- Serialize once.
- Apply the same redaction to stderr excerpts, quarantine artifacts, index content, trap text, and talkback.

WHEN equivalent payloads enter through flags, a file, or stdin THEN you SHALL persist equivalent redacted records except for generated metadata.

WHEN secret-shaped text appears at any nesting level THEN you SHALL redact it before canonical append, diagnostics, quarantine, derived views, or talkback.

WHEN you document verbatim capture THEN you SHALL state that mandatory deterministic redaction takes precedence.

### 7.2 P0 — storage is not private by construction

Under a common `umask 022`, direct probes created the stream as `0644` and its directory as `0755`. The stream can contain user statements, absolute paths, session IDs, error text, source excerpts, and decision narratives.

Proposed correction:

- Set `umask 077` in every writer.
- Create directories as `0700`.
- Create events, indexes, traps, lock metadata, quarantines, and temporary files as `0600`.
- Safely harden existing compatible artifacts.
- Reject suspicious symlinked targets or require explicit acknowledgement.

WHEN you create any friction-store artifact THEN you SHALL make it user-only independent of the caller’s umask.

WHEN an existing artifact is more permissive THEN you SHALL harden it safely or fail with a precise remediation message.

### 7.3 P0 — malformed-input recovery can disclose the payload

On malformed JSON, the helper prints the offending raw line and can save the full payload for replay. Parsing failure is exactly where schema-aware redaction is least reliable.

The empty-input path worked well and should remain unchanged: it writes nothing and gives concise retry guidance.

For malformed nonempty input:

- print a bounded, best-effort-redacted excerpt;
- make full quarantine explicit or unmistakably warned;
- keep the quarantine parent private;
- state retention and deletion behavior;
- never echo a replay command containing payload text.

### 7.4 P0 — `--repo-root` can make metadata and storage disagree

The default event path is resolved from the current process’s Git root. `--repo-root` is later stamped into the record. A command in repository A with `--repo-root B` can therefore write under A while claiming B.

Proposed precedence:

1. `--events-file` explicitly selects the physical store.
2. Otherwise `--repo-root` selects the canonical store under that root.
3. Otherwise the current Git root is used.
4. Otherwise use the documented outside-repository location.

WHEN you receive `--repo-root B` from working directory A THEN you SHALL route to B and record B’s canonical root.

IF `--events-file` and `--repo-root` disagree THEN you SHALL reject the conflict or record both physical store and logical root explicitly; ELSE you SHALL record one consistent location.

### 7.5 P0 — read-only commands mutate clean repositories

`query-friction.sh` calls `default_events_file()`. That calls `local_dir_for_repo()`, which creates `.local` before the query discovers that no event file exists.

The code already contains `existing_local_dir_for_repo()`, demonstrating the intended distinction, but read paths do not consistently use it.

Proposed correction:

- `resolve_store_for_read` never creates.
- `resolve_store_for_write` may create under private modes.
- A missing store returns an empty result or a concise not-found status according to the command contract.

WHEN you run a read-only query or report in a clean repository THEN you SHALL create no file or directory.

### 7.6 P0 — stable store selection is not guaranteed

When `.local` is absent, the resolver chooses the alphabetically first `.local*` directory. If `.local` later appears, the canonical location changes. One repository can accumulate multiple event stores, and cross-repo reports can display duplicate repository rows with different counts.

The ambient snippet hardcodes `.local/reports/friction/known-traps.md`, even though the resolver may choose `.local-test`, `.local-cache`, or another local area.

Proposed correction:

- Store a small canonical-location marker at the repository root or always choose one stable documented path.
- Add a doctor command that detects multiple stores and proposes a safe merge/migration.
- Distinguish “stores scanned” from “unique repository roots” in reports.
- Make ambient trap discovery use the same resolver rather than a hardcoded path.

### 7.7 P0 — locks can block forever

Capture and resolution use a lock-directory loop with `sleep 1` and no deadline. If a lock lacks a usable PID, or if ownership metadata is ambiguous, the loop can wait indefinitely. A delegated probe required an external three-second timeout and exited `124`.

Proposed lock record:

```json
{
  "pid": 12345,
  "host": "machine-name",
  "process_start": "platform-specific start identity",
  "created_at": "2026-07-14T20:00:00Z",
  "nonce": "random owner token"
}
```

The engine should use a bounded wait, detect demonstrably stale owners, avoid PID-reuse mistakes, and report the lock path and bounded owner evidence on timeout.

WHEN a lock cannot be acquired before the deadline THEN you SHALL fail with an actionable message rather than wait forever.

WHEN the recorded owner is demonstrably stale THEN you MAY reclaim the lock atomically and you SHALL report that recovery.

The support claim should remain same-host and single-filesystem. Do not imply distributed correctness.

### 7.8 P0 — append commitment is reported too late

The writer appends the event, then rebuilds the index, then prints the event receipt. A derived-view failure can therefore produce a nonzero command after the canonical append already committed. An agent may retry and create a duplicate.

Proposed transaction boundary:

1. Validate existing stream integrity.
2. Build, redact, and validate the new record.
3. Acquire the lock.
4. Append the canonical record.
5. Emit `COMMITTED` with store-qualified record identity.
6. Release or retain the lock according to the index consistency design.
7. Rebuild derived views as repairable work.
8. Report derived failure separately without implying the append failed.

WHEN the canonical append succeeds THEN you SHALL emit an unambiguous committed receipt even if a later derived view fails.

WHEN the canonical append does not occur THEN you SHALL say explicitly that no record was filed.

### 7.9 P0 — recurrence after resolution does not reopen despite the advertised contract

The reporter says a recurrence against a resolved anchor “reopens the cluster.” Query, report, and cluster reducers instead build an unordered set of every ID ever resolved. Any later recurrence inherits permanent closure.

The existing smoke test checks only that the reporter prints the reopen wording. It does not append the recurrence and assert open state.

The product must choose one coherent chronological rule. The most natural append-only lifecycle is:

```text
anchor                         → open
anchor → resolution            → closed
anchor → resolution → recurrence → open
... → recurrence → resolution  → closed again
```

If the new event shares a symptom but the prior mend changed the causal model, it should be a distinct anchor rather than a recurrence.

WHEN a recurrence is appended after the latest resolution of its anchor THEN you SHALL report the anchor open.

WHEN a later resolution closes that anchor again THEN you SHALL report it closed.

WHEN a new incident has a different preventable cause THEN you SHALL support a distinct anchor even if surface text is similar.

### 7.10 P0 — cross-store event IDs collide

Every store starts at `evt-0001`. Multi-store query flattens records and treats bare event IDs as global. A resolution of repo A’s `evt-0001` can close repo B’s unrelated `evt-0001`.

Do not discard readable local IDs. Add durable qualified identity:

- `store_uid` generated once per canonical store;
- `record_uid` globally unique per record;
- `event_id` retained as the human-readable local sequence.

Legacy in-memory identity can be `(canonical events_file, event_id)` until a migration is justified.

WHEN you combine stores THEN you SHALL resolve relationships using qualified identity, never a bare local event ID.

### 7.11 P0 — event IDs are allocated from line count

New IDs are `wc -l + 1`. A corrupt, truncated, blank, or manually altered stream can reuse an ID. Different readers also vary in whether they skip malformed lines or fail.

The writer should validate the stream before allocation, recover the maximum valid local sequence, and use the globally unique record identity as the correctness key.

### 7.12 P0 — trap publication accepts fabricated evidence

`update-traps.sh` validates only:

- at least one line beginning `- [`;
- no more than fifteen such lines;
- a total byte cap.

It does not validate anchor existence, key match, recurrence count, last-seen date, open/active state, or arbitrary extra prose. A disposable probe published `evt-9999 x999, last 2099-12-31` against an empty store.

The model should supply only the avoidance guidance and anchor selection. The engine should derive the rest.

Possible structured input:

```json
{
  "anchor": "evt-0009",
  "avoidance": "Inspect per-channel readiness and verify the visible outcome independently."
}
```

The publisher derives key, qualified anchor, sightings, latest date, and lifecycle state.

WHEN a trap anchor does not exist or is not eligible THEN you SHALL reject publication.

WHEN a trap line claims key, count, or date metadata THEN you SHALL derive those values from the canonical store rather than trust caller prose.

### 7.13 P0 — trap replacement can drop unrelated entries

`update-traps.sh` replaces the entire file. In a scoped mend, a caller can accidentally omit traps outside the reviewed cluster.

Options:

- Require and verify a complete intended trap set after reading the current file.
- Prefer a structured upsert/remove interface that preserves untouched traps.

Trap publishing should also be semantically idempotent. Rewriting identical content solely to change a generated timestamp creates a false delta.

### 7.14 P0 — CI does not follow the plugin

The friction smoke job is selected through the packaged `friction_render_table` entry. A direct probe returned `false` for a change to `report-friction.sh`. The same is true for other core capture/mend scripts and contracts, while changing the smoke test itself returns `true`.

The current suite can therefore pass on main while changes to the behavior it covers never run it in CI.

Add a dedicated command, for example:

```sh
just test-friction-diagnostics
```

It should run for changes under the entire plugin root and relevant shared packaging/CI configuration.

WHEN any executable, schema, skill contract, hook, manifest, or test under the plugin changes THEN you SHALL run the complete plugin qualification job.

### 7.15 P0 — behavioral trigger evals are artifacts, not gates

Both skills ship trigger prompts, and Capture also ships behavior eval descriptions. No current local or CI command executes the trigger boundary as a host behavior test.

The most important negative gate remains essential: a deliberately red test should not become friction. Add actual host surfacing/behavior evaluation where available, with deterministic structural fallback when host execution is unavailable.

## 8. Capture-contract improvements

### 8.1 Split Capture and Mend trigger ownership

The Capture description says it also handles “review, mend, or distill friction.” Mend advertises “review, triage, mend, resolve, or distill.” This causes both to activate on a request such as this report and makes it unclear whether the Mend outcome contract requires actual source edits.

Recommended ownership:

- **Friction Diagnostics:** detect, capture, recur, query, and summarize genuine surprises.
- **Friction Mend:** review a corpus, cluster, repair, resolve, and publish grounded traps.

The descriptions should follow the repository’s numbered trigger-list convention.

### 8.2 Retire the incompatible `/tmp/skill-errors` policy

The repository-wide `AGENTS.md` requires logging any issue encountered while following a skill into a Markdown file under `/tmp/skill-errors`. That policy conflicts with Friction Diagnostics in threshold, location, schema, recurrence, lifecycle, and mending.

This review had to write both the canonical JSONL record and a separate `/tmp` error log for the same talkback terminology problem.

Replace the old policy with the canonical ambient snippet. If historical Markdown matters, provide a one-time importer that preserves the original file reference and labels the record legacy.

### 8.3 Replace blame language with prediction-basis language

“What did you trust that betrayed you?” assumes the cited source was at fault. In Chatmux, several sources were correct but incomplete signals, transient observations, or APIs whose success did not establish the desired state.

Prefer:

> What supported your prediction? For each basis, record what proposition you believed it established.

This retains the causal data without pre-judging blame.

### 8.4 Generalize exact evidence beyond text

“Paste it verbatim. Never paraphrase.” works for an error string. It is impossible for:

- a control that did not move;
- a missing response;
- a focus change;
- a visual layout defect;
- a timeout or non-occurrence;
- audio or physical behavior.

Chatmux `evt-0008` and `evt-0009` are valid precisely because they combine exact error text with precise observational prose.

Recommended contract:

> Preserve the best available primary evidence. Quote exact text where text exists. Otherwise describe the observation precisely, identify how it was observed, and label inference or paraphrase.

An optional `evidence` array would improve provenance without changing `sources`:

```json
{
  "evidence": [
    {"kind": "console", "text": "UnknownError: Internal error"},
    {"kind": "artifact", "ref": ".local/playwright-results/trace.zip"},
    {"kind": "observation", "text": "The workspace list rendered empty."}
  ]
}
```

This should be P1 or a pilot, not a P0 schema expansion. The immediate P1 is better language.

### 8.5 Make source claims consistent

The skill concept and field rubric say each source records the believed claim. The nested schema requires only `kind` and `ref`, and the JSON writer accepts a source without `claim`.

For a full event, the believed proposition is core mending data. Require it. For a minimal anchor, omission can be explicit and later enriched.

For documentation or instruction, quote the acted-on wording. For code, configuration, and data artifacts, identify the symbol/line/snippet and state the proposition inferred from it; a prose quote may not exist.

### 8.6 Add non-blocking semantic lint

Structural validation accepted several field-contract problems in the Chatmux corpus:

- future intent in `decision`;
- `continued` impact despite an explicit workaround;
- multiple source refs joined into one string;
- composite observations described as one “verbatim” actual outcome;
- independently actionable symptoms in one event.

Warnings can help without blocking capture:

- future/proposal language in `decision`;
- impact inconsistent with words such as workaround, retry, fallback, or blocked;
- source refs joined by “and” rather than separate entries;
- pivot information without a location;
- likely composite incident;
- artifact/instruction source missing a claim or exact location.

### 8.7 Remove arbitrary minimum lengths from exact evidence

The writer rejects a short exact outcome such as `EPIPE` because it does not meet the narrative floor. Padding the evidence makes it less verbatim, not more useful.

Require non-empty actual evidence. Use advisory quality checks on the explanatory fields. Do not require an error token to reach fifteen characters.

### 8.8 Pilot a true minimal anchor with append-only enrichment

The current “minimal anchor” still requires five narrative fields, a source, impact, and length floors. That is not operationally minimal.

Possible two-stage model:

```text
anchor: exact evidence + actual expectation + basis ref + impact
enrichment: reading + decision + pivot + full claims + tags
```

Enrichment should be a linked append-only record, not in-place mutation.

This is promising but should be measured. The Chatmux records are excellent partly because they are rich. Do not weaken full records before measuring filing cost and omission rates.

### 8.9 Reconcile “immediate filing” with completed-history `decision`

The policy says file at the moment of surprise. The schema requires a completed decision history, including options set aside and action taken. At the exact moment of divergence, the response may not yet exist.

The current escape—“filed before acting; no response yet”—is truthful but awkward. A minimal anchor plus later enrichment resolves the tension cleanly.

## 9. Mend-contract improvements

### 9.1 Use structured dispositions instead of overloading `wontfix`

The Chatmux corpus contains several distinct outcomes:

- `fixed`: malformed SVG and ARIA serialization corrected locally;
- `mitigated`: IndexedDB restart recovery and Computer Use verification procedure;
- `accepted`: Chrome internal-page security policy with an alternate architecture;
- `external`: capability/version skew and manual-helper defect owned elsewhere;
- `guarded`: console diagnostics retained so invalid SVG data becomes self-announcing;
- `not-reproducible`: the transient duplicate-output observation filed during this review;
- `noise` or `duplicate`: possible future cases.

Free-text `action` plus `wontfix` cannot express these cleanly. Recommended dispositions:

- `fixed`
- `guarded`
- `mitigated`
- `documented`
- `upstream-reported`
- `accepted-risk`
- `obsolete`
- `duplicate`
- `not-reproducible`
- `noise`
- `wontfix`

The list should be reduced after one real Mend evaluation; not every label must ship immediately.

### 9.2 Require verification and prevention evidence where applicable

A resolution should not be self-certifying prose.

Suggested fields:

```json
{
  "disposition": "fixed",
  "verification": "The exact console error is absent in the mounted UI suite.",
  "prevention": "Static SVG validation rejects malformed paths before browser execution.",
  "owner": "repo:/home/rashino/repos/Chatmux",
  "ref": "path or commit"
}
```

WHEN you record `fixed` or `guarded` THEN you SHALL include verification proportional to the original failure.

WHEN prevention is not implemented THEN you SHALL say so rather than invent a poka-yoke claim.

### 9.3 Separate work closure from active danger

An external environmental trap may require no further local work yet remain dangerous. A record can be closed as `accepted-risk` or `upstream-reported` while a grounded trap remains active.

Avoid treating “zero unmended anchors” as “no active hazards.” The dashboard can show:

- unmended learning records;
- active grounded traps.

Do not add a full incident-management state machine. A small distinction between closure disposition and trap eligibility is enough.

### 9.4 Improve cluster hints using the playbook’s own strongest evidence

The mend playbook says the best signals are:

1. same pivot information;
2. same source plus claim class;
3. only then surface-text similarity.

`cluster-hints.sh` currently emits exact recurrence-key groups and token overlap on `actual_outcome`. On Chatmux it grouped unrelated events because they shared `error` and paired two browser events on generic words, while failing to surface the broader Chrome-control family cleanly.

Add bounded views:

- normalized pivot groups;
- normalized `(source kind, source ref, claim class)` groups;
- recurrence-key groups;
- outcome-token candidates with strong stopword/boilerplate suppression;
- explanation of which features produced each candidate;
- confidence or evidence strength;
- a marker for transitive-only components.

Mechanical hints remain advisory. Do not auto-cluster or auto-resolve.

### 9.5 Make source-owner routing part of Mend preparation

Mend should be able to produce:

- local-source clusters that the current repository can repair;
- external-owner clusters to escalate or close with an explicit disposition;
- environmental traps that remain active after local closure.

This is a derived report over canonical records, not a new storage destination.

### 9.6 Prove a real end-to-end Mend cycle before expanding further

No Chatmux recurrence, resolution, or known-trap file existed at the field cutoff. The plugin’s own store now contains one resolution and two recurrences from this review, but not a demonstrated future-session avoidance.

Before adding a large ontology, run a real evaluation:

```text
capture a real surprise
→ observe a real recurrence
→ cluster with evidence
→ repair or explicitly disposition the source
→ record verification
→ publish a grounded trap if danger remains
→ start a later session that reads the trap
→ demonstrate that the later session behaves differently
```

The final step is the actual product outcome.

## 10. Reporting and integration findings

### 10.1 “Open clusters” names two different measures

The filing talkback printed `open clusters: 0` after each unique Chatmux event. `INDEX.md` simultaneously placed every unresolved singleton under `Open Clusters`.

Source inspection showed that talkback counts only open keys with at least two sightings, while the dashboard includes singleton anchors. The calculation can be defensible; the shared label is not.

This ambiguity directly misled the current review. After filing a new anchor, `open clusters: 0` was interpreted as a lifecycle failure and recorded as a recurrence of an existing talkback event. The correct description was “open recurring clusters with two or more sightings.”

Rename or align:

- `open anchors: N`
- `open recurring clusters (2+ sightings): M`
- `known traps: K`

### 10.2 “This session” is sometimes only a timestamp slice

`render-summary.sh --after` labels output as events “this session,” even when the lower bound excludes earlier records with the same `session_ref`. One existing plugin event also showed local-offset/fractional timestamps being compared incorrectly and including twelve events instead of two.

Add exact session filtering:

- `query-friction.sh --session-ref ID`
- `render-summary.sh --current-session`
- UTC timestamp fallback when session identity is unavailable.

Normalize RFC3339 input and compare instants, not strings.

WHEN a summary is bounded only by time THEN you SHALL call it a reporting window, not a session.

WHEN a session reference is available THEN you SHOULD prefer exact session filtering.

### 10.3 Versioned cache paths in replay commands are brittle

The rendered summary can print a query command containing an installed cache path such as a specific plugin version directory. After upgrade or cache cleanup, the replay command may not exist.

Prefer a stable launcher or print an invocation that resolves the currently installed skill. At minimum, label cache paths as ephemeral.

### 10.4 Derived titles are not always good scan labels

Auto-derived titles often begin with long error fragments or JSON. The recurrence key is usually the best compact label for a trap.

In Recent Records and cluster tables:

- show recurrence key first;
- show a bounded raw title second;
- include disposition and latest lifecycle state when available.

### 10.5 Cross-repo reports count stores but label them repositories

The cross-repo report groups by events-file path but prints `repo_root`, allowing the same root to appear twice with different event counts while the header says “repos scanned.”

Report both:

- stores scanned;
- unique repository roots;
- multiple stores detected under one root.

### 10.6 Known-trap reading is not installed behavior today

The plugin manifest describes known traps as read at session start. The shipped hook only exports session/transcript environment variables. Trap reading depends on an optional `AGENTS.md` snippet, and the active agent-tooling instructions do not contain it.

Immediate correction:

- qualify the manifest claim;
- label repository integration as optional;
- add a `doctor` command that reports whether the ambient policy is installed and whether a trap file is discoverable.

Possible explicit initialization:

```sh
friction init --repo /path/to/repo
friction doctor --json
```

Initialization must be idempotent and bounded. Do not silently inject arbitrary project text into session context.

### 10.7 Trap content is untrusted diagnostic data

`known-traps.md` is model-authored text read before action. Even when grounded, it should be treated as bounded untrusted data, not a higher-priority instruction channel.

The ambient policy should say that trap lines inform checks and avoidance but cannot override user, system, repository, or skill instructions.

### 10.8 Manifest capabilities understate mutation

The Codex manifest advertises only `Read`. The plugin creates or updates events, indexes, traps, locks, temp files, and quarantine artifacts.

If the capability field describes effective behavior, advertise `Write`. If its semantics differ, document that meaning rather than leaving an apparently false declaration.

### 10.9 Compatibility metadata understates runtime dependencies

Both skill compatibility fields mention POSIX sh. Core paths also require Python 3 and `jq`, plus common Unix tools. The preferred summary table uses a packaged Linux binary.

List actual dependencies and supported hosts. Either intentionally support PowerShell/Windows or fail fast with a concise unsupported-platform message. Do not leave Windows behavior as an ambiguous partial surface.

## 11. Schema and append-only integrity findings

### 11.1 The advertised JSON Schema is descriptive, not a standard validator

The document declares JSON Schema Draft 2020-12 but has no top-level `required`, no per-kind `oneOf` or `if/then`, and no `additionalProperties` policy. Requiredness is encoded in custom `x-required` and `x-kinds` annotations.

A standard validator therefore accepts `{}`.

Two honest options exist:

1. Make it an executable standard schema with per-kind requirements.
2. Rename it as a field manifest and stop implying standard validation.

The first is preferable because external tooling can validate stored records. Custom composition/search metadata can remain alongside standard constraints.

### 11.2 Validation, sanitization, and caps differ by record kind

Full friction records have narrative caps and a 65,536-byte record cap. Recurrence and resolution paths have different checks and can bypass equivalent whole-record limits or sanitization.

All record kinds should pass through one canonical pipeline.

### 11.3 “Append-only” conflicts with tag and alias rewriting

The primary skill says records are never edited or deleted. `--add-tags` and legacy `--add-aliases` rewrite the stream in place. The detailed logging spec acknowledges the exception; the main contract does not.

Choose a truthful minimal rule now:

- strict append-only, using annotation records; or
- append-only narrative/lifecycle history with explicitly mutable metadata.

Do not introduce a general amendment ontology solely for elegance. Pilot annotation records only if provenance for tag changes matters.

### 11.4 Store-controlled values reach executable contexts

The JSON bridge uses Python to emit shell assignments and then runs `eval` on the result. `shlex.quote` and fixed variable names reduce exploitability, but repository instructions explicitly prohibit `eval` on user-provided input.

Replace it with a non-evaluated transport:

- one canonical process that reads/writes JSON directly;
- NUL-delimited fields parsed without evaluation;
- a private temporary field directory;
- another mechanism with no code interpretation.

### 11.5 Session transcript path is exported but unused

The Claude hook exports both session reference and transcript path. Current plugin code consumes the reference but not the path.

Remove the unused export or add a clearly scoped consumer. Avoid collecting sensitive path metadata without a product use.

## 12. Recommended target command surface

The exact command names are illustrative. The essential goal is one engine and stable compatibility wrappers.

### 12.1 Inspect and initialize

```sh
friction doctor --json
friction init --repo /path/to/repo
```

`doctor` should report:

- resolved read and write store paths;
- store identity and integrity;
- permissions;
- lock state;
- multiple-store conflicts;
- session attribution availability;
- ambient policy installation;
- trap file existence and grounding status;
- runtime dependencies;
- host support.

`init` should install only explicit, bounded repository integration and be idempotent.

### 12.2 Capture

```sh
friction capture --from-json -
friction recur --anchor STORE_UID:evt-0009 --actual-outcome "..."
friction anchor --from-json -
friction enrich --anchor RECORD_UID --from-json -
```

The existing `report-friction.sh` flags remain a wrapper during migration.

### 12.3 Query

```sh
friction query --store PATH --open --format json
friction query --scan ~/repos --owner-root PATH --format md
friction query --current-session --format md
```

Default output should remain compact. Explicit full JSON can remain unbounded for local use, but Mend should begin from bounded cluster/source/pivot summaries rather than dumping the whole corpus by default.

### 12.4 Resolve

```sh
friction resolve \
  --anchor RECORD_UID \
  --disposition fixed \
  --action "..." \
  --verification "..." \
  --prevention "..." \
  --owner "repo:/path" \
  --ref "commit-or-path"
```

### 12.5 Publish traps

```sh
printf '%s\n' '{"anchor":"RECORD_UID","avoidance":"..."}' \
  | friction traps upsert --from-json -

friction traps remove --anchor RECORD_UID
friction traps verify
```

The engine derives all pointer metadata.

## 13. File-level change proposal

### 13.1 `skills/friction-diagnostics/SKILL.md`

- Limit trigger ownership to capture, recurrence, query, and summary.
- Use the numbered trigger-list description format.
- Replace blame language with prediction bases.
- Replace universal verbatim language with best-available primary evidence.
- State the redaction exception.
- Clarify minimal anchor versus full event.
- Link the integration and logging references conditionally.
- Rename ambiguous talkback/report concepts.
- Point to stable launchers rather than versioned cache paths.

### 13.2 `skills/friction-mend/SKILL.md`

- Own corpus review, clustering, repair, resolution, and trap publication exclusively.
- Keep mending user-invoked.
- Add structured dispositions and verification guidance.
- Distinguish closed work from active danger.
- Route external-owner clusters explicitly.
- Require grounded trap publication.
- Define one real end-to-end success criterion: future behavior changes.

### 13.3 Common store engine

- Centralize record parsing, legacy coercion, recursive redaction, standard validation, size caps, identity, locking, append receipts, and lifecycle.
- Centralize timestamp normalization and session filtering.
- Centralize store read/write resolution.
- Centralize cross-store qualified identity.
- Emit stable JSON for wrappers and human-readable compact errors.

### 13.4 `report-friction.sh`

- Become a compatibility wrapper.
- Remove `eval`.
- Emit committed receipt before derived work.
- Print open anchors and recurring clusters separately.
- Offer a ready-to-edit resolution command.
- Add semantic lint as warnings.

### 13.5 `query-friction.sh`

- Use non-mutating read discovery.
- Use chronological lifecycle.
- Qualify cross-store identities.
- Parse timestamps as instants.
- Add `--session-ref` and `--current-session`.
- Distinguish stores and repositories.

### 13.6 `generate-report.sh` and `build-index.sh`

- Consume the canonical reducer output.
- Show recurrence key as the primary scan label.
- Label unmended records accurately.
- Report stores and unique roots separately.
- Keep bounded defaults.

### 13.7 `cluster-hints.sh`

- Add pivot and source/claim groups.
- Improve stopwords and boilerplate suppression.
- Explain match features.
- Bound output and expose truncation.
- Keep all hints nonbinding.

### 13.8 `record-resolution.sh`

- Become a wrapper around canonical append.
- Add disposition, verification, prevention, owner, and qualified ref.
- Use the same redaction, caps, lock, and receipt contract as capture.

### 13.9 `update-traps.sh`

- Accept structured anchor plus avoidance text.
- Derive and validate metadata.
- Preserve untouched traps under scoped changes.
- Make identical publication a no-op.
- Treat content as untrusted diagnostic data.

### 13.10 `friction-event-schema.json`

- Add standard per-kind validation.
- Require source claims for full events.
- Add store/record identity.
- Add structured resolution fields.
- Add optional evidence only after the language change is validated.
- Keep custom composition and report metadata.

### 13.11 Manifests and hooks

- Correct the session-start trap-reading claim.
- Advertise effective write capability if appropriate.
- List true runtime dependencies.
- Remove unused transcript-path export or document its use.

### 13.12 Repository `AGENTS.md`

- Remove the parallel `/tmp/skill-errors` logging system.
- Install the canonical ambient surprise policy if the repository wants automatic capture expectations.
- Use the same resolver for trap discovery.

### 13.13 CI and local command surface

- Add `just test-friction-diagnostics`.
- Select it on every relevant plugin-root change.
- Run static shell checks, engine unit tests, integration tests, schema tests, trigger evals, and both host package validations.

## 14. Required verification matrix

### 14.1 Storage and privacy

- Under `umask 022`, directories are `0700` and files are `0600`.
- Existing permissive compatible paths are hardened or rejected clearly.
- Secret fixtures are redacted in every nested field and every record kind.
- Secret fixtures never appear raw in malformed-input stderr or quarantine receipts.
- Symlinked hostile store targets are rejected or explicitly acknowledged.

### 14.2 Routing and read behavior

- `--repo-root B` from repository A writes physically under B.
- Explicit `--events-file` precedence is deterministic.
- A read-only query in a clean repo creates nothing.
- Multiple `.local*` stores are detected and reported without silently switching canonical history.
- The ambient trap resolver finds the same store as the writer.

### 14.3 Locking and commitment

- Concurrent writers produce unique valid records.
- Ownerless and stale locks recover or time out within a bounded interval.
- Live locks time out with owner evidence and no corruption.
- Interruption removes only the caller’s own lock.
- Index failure after append still emits a committed receipt.
- Retry after a committed/derived-failure receipt does not duplicate automatically.

### 14.4 Lifecycle and identity

- `friction → resolution` is closed.
- `friction → resolution → recurrence` is open.
- `friction → resolution → recurrence → resolution` is closed.
- A distinct event after a changed causal model remains independent.
- Store A’s `evt-0001` never closes store B’s `evt-0001`.
- Corrupt or blank lines cannot cause record-identity reuse.

### 14.5 Trap integrity

- Unknown anchors are rejected.
- Key/count/date mismatches cannot be supplied by the caller.
- Resolved-and-removed dangers are ineligible.
- Closed-but-active accepted dangers can remain eligible under explicit disposition.
- Scoped updates preserve untouched traps.
- Identical semantic publication is a no-op.
- More than fifteen grounded traps and more than the byte cap are rejected without replacing the prior valid file.

### 14.6 Capture semantics

- A short exact outcome such as `EPIPE` is accepted.
- A full event without source claim is rejected with a concise eliciting question.
- A non-text observation is accepted without invented quoted text.
- User-reported contradiction can be captured with appropriate source kind.
- A future-tense decision produces a warning, not silent acceptance or hard failure.
- Impact/workaround mismatch produces a warning.
- Empty stdin writes nothing and provides the current concise recovery guidance.

### 14.7 Reporting

- Talkback separately reports open anchors and recurring clusters.
- Current-session summary filters by session reference.
- Offset timestamps are compared chronologically.
- Reports distinguish stores from unique roots.
- Replay commands survive plugin version changes.
- Default report output remains bounded.

### 14.8 CI and activation

- Every relevant plugin file change selects the complete test job.
- Capture and Mend trigger prompts are disjoint.
- Expected red tests do not trigger capture.
- Explicit review/mend requests trigger Mend.
- Both Codex and Claude package variants expose the intended skills.
- Manifest claims match effective hook and capability behavior.

## 15. Recommended delivery roadmap

### Phase 0 — make existing promises true

1. Private permissions and recursive redaction.
2. Correct repository routing and non-mutating reads.
3. Bounded locks and cleanup.
4. Committed receipt ordering.
5. One canonical chronological lifecycle reducer.
6. Store-qualified identity.
7. Grounded trap publishing.
8. Plugin-wide CI selection and a canonical local test command.
9. Regression tests for every confirmed defect.

### Phase 1 — clean product boundaries

1. Split Capture and Mend triggers.
2. Retire `/tmp/skill-errors` split logging.
3. Correct session-start, capabilities, and compatibility claims.
4. Add session-aware query and summary.
5. Rename ambiguous lifecycle/report labels.
6. Neutralize prediction-basis language and support non-text evidence.
7. Require source claims consistently.
8. Add semantic lint warnings.

### Phase 2 — prove and improve Mend

1. Run one complete real Mend-to-future-avoidance evaluation.
2. Add a small structured disposition set based on that evaluation.
3. Require verification for fixed/guarded outcomes.
4. Add pivot/source clustering hints.
5. Add owner-centric derived queues.
6. Pilot explicit in-task verified closure.
7. Pilot minimal anchors and append-only enrichment.

### Phase 3 — only after measurement

Consider optional evidence structures, related-event grouping, an unreviewed active brief, annotation records, path privacy modes, or larger-corpus pagination only after field data shows the need and validates the shape.

## 16. Things that should explicitly remain unchanged

- Do not log every tool error.
- Do not log expected negative tests, planned red states, or task status.
- Do not automatically convert candidates into events.
- Do not automatically merge events based on token or embedding similarity.
- Do not let capture records prescribe source fixes.
- Do not merge Capture and Mend into one cognitive phase.
- Do not auto-edit source artifacts from a single event.
- Do not close events merely because the main task completed or a broad test suite passed.
- Do not make `known-traps.md` an unreviewed event dump.
- Do not duplicate canonical events into every possible owner repository.
- Do not import Chrome, Brave, provider, KDE, Leptos, Node, Playwright, or Computer Use workarounds into the foundational plugin.
- Do not build a daemon, MCP service, database, remote store, or distributed lock without an actual shared-storage requirement.
- Do not weaken the rich full-record fields merely because they are long; first add and measure a separate minimal path.
- Do not make every proposed field mandatory in one schema revision.

## 17. Workarounds used in the field

This list is included to show what the plugin preserved and where it did not propagate knowledge. These are not proposals to make Friction Diagnostics domain-specific.

### Browser and extension testing

- Used a dedicated Playwright profile for rebuild/install automation because connected Chrome correctly blocked `chrome://extensions/` and prohibited indirect workarounds.
- Kept the authenticated Brave/Chrome provider tabs as the real provider surface.
- Reacquired and used Chrome browser handles atomically when cross-call handles proved ephemeral.
- Fell back from unavailable DOM snapshots to screenshots, visible DOM inspection, and bounded evaluation.

### Provider editors

- Used Control+A and Backspace for Claude and Grok after `fill("")` falsely appeared to clear them.
- Verified editor state after cleanup rather than treating the call receipt as proof.

### UI qualification

- Kept extension-origin console errors release-blocking even when workflow assertions passed.
- Retained traces and screenshots long enough to diagnose malformed SVG data.
- Tested ARIA state semantically rather than trusting visible checkmarks.

### Documentation tooling

- Switched to official documentation when the manual helper rejected a response missing the expected hash metadata.

### Persistence recovery

- Inspected the existing IndexedDB files read-only and restarted Brave instead of creating replacement workspaces when the browser storage service temporarily failed.

### Desktop control

- Inspected per-channel readiness rather than the aggregate headline.
- Reacquired the Brave window before input because other apps stole focus.
- Preferred keyboard and direct URL navigation when coordinate clicks were not visibly effective.
- Used Spectacle and KWin/kdotool as observable fallbacks when Computer Use screenshots or window movement failed.

### Around Friction Diagnostics itself

- Used explicit `--events-file` for safe read inspection.
- Queried JSONL directly to validate lifecycle and source details.
- Normalized summary bounds to UTC after offset filtering proved unreliable.
- Ran the smoke suite manually because CI selection does not follow core scripts.
- Interpreted `known-traps.md` as optional and currently absent, not automatically injected.
- Closed a non-reproducible event append-only rather than deleting it.
- Wrote a second `/tmp/skill-errors` artifact because the repository still mandates a parallel logging system.

## 18. Evidence boundaries and unresolved questions

### Known

- Chatmux capture was useful and cross-domain.
- Nine full events remained readable without the whole transcript.
- The corpus had no recurrence, resolution, or trap at the field cutoff.
- At least two fixed defects remained shown as open.
- The 18 POSIX smoke scenarios pass.
- Core CI selection is incomplete.
- Lifecycle, cross-store identity, routing, read mutation, trap grounding, lock waiting, permissions, and source sanitization have confirmed defects.
- Talkback and dashboard use “open clusters” differently.

### Inferred

- A single canonical engine will eliminate an entire class of reducer drift.
- Owner-centric derived queues will make cross-repository learning more actionable.
- Explicit verified closure will reduce stale backlog state if it remains narrow and auditable.
- Pivot/source-first hints will improve Mend preparation.
- Neutral evidence language will generalize better beyond text-heavy software incidents.

### Not verified

- A real published trap has changed a later session’s behavior.
- The proposed disposition vocabulary is the smallest sufficient set.
- Minimal anchors improve capture recall without degrading record quality.
- An active unreviewed brief improves coordination more than it adds noise.
- Large-corpus runtime performance requires pagination rather than bounded summaries.
- Windows support is worth the implementation cost.
- Any distributed or remote storage requirement exists.

## 19. Final assessment

### Holistic verdict

The frame is right. Friction Diagnostics should remain a generalized cognitive-debugging and learning-loop plugin, not a domain-specific troubleshooting bundle and not a generic error logger.

The product already captures the most valuable facts: prior prediction, prediction basis, actual outcome, decision history, and pivot information. Chatmux demonstrates that this model works across several very different technical surfaces.

### Atomistic verdict

The current implementation has foundational correctness and trust gaps. Several public claims—private-safe evidence handling, coherent open state, grounded traps, canonical repository storage, automatic trap reading, and test coverage—are not reliably true.

### Readiness

The capture concept is ready to preserve. The current implementation is not ready to be treated as an audit-grade or universally reliable foundation until the P0 storage, lifecycle, trap-integrity, routing, locking, and CI issues are fixed.

### Highest-leverage fix

Create one canonical, tested store engine and route every capture and Mend surface through it. That upstream change makes inconsistent lifecycle, sanitization, locking, identity, and validation far harder to reintroduce.

### Highest-leverage product proof

Run one real end-to-end Mend cycle and show that a later session reads a grounded trap and behaves differently. Until that happens, Capture is field-validated; the complete learning loop is not.

### Recommended decision

Proceed with targeted hardening and contract cleanup. Preserve the cognitive kernel. Pilot lifecycle ergonomics only after correctness is restored. Defer infrastructure expansion and bespoke domain logic.
