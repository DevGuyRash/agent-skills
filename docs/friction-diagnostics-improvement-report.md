# Friction Diagnostics: Foundational Improvement Report

**Status:** Read-only audit and proposal

**Date:** 2026-07-13

**Repository:** `agent-tooling`

**Target:** `plugins/friction-diagnostics`

**Audited commit:** `ff3e4f2bc2b634692f8ecc07549bf7bffaf253b9`

**Audited plugin version:** `5.1.3`

## Executive summary

Friction Diagnostics already has an unusually strong central idea: record the moment reality diverges from a prediction, preserve what supported the prediction, capture what actually happened, and identify the information that would have changed the decision. This is more valuable than an ordinary error log because it preserves the model failure behind the incident, not merely the incident itself.

The central model should not be replaced. It has already worked across browser tooling, UI behavior, test harnesses, data contracts, process coordination, patching, and one communication-scope correction. Broader applicability to writing, research, operations, creative work, organizational decisions, and physical-world tasks is plausible, but those domains have not yet been validated by a real corpus. The existing distinction between immediate capture and later mending is sound.

**One-sentence diagnosis:** Friction Diagnostics has the right cognitive kernel and the right capture/mend split, but the local store currently makes several promises it does not keep—private and canonical persistence, true lifecycle reopening, cross-store identity, and reliable feed-forward closure—and its strongest test suite is not an unavoidable CI gate.

The plugin is nevertheless not yet ready to claim universal, foundational, or multi-agent reliability without qualification. The most important problems are not philosophical. They are concrete delivery defects:

1. A recurrence filed after a resolution does not reopen the cluster, despite the CLI and specification saying it does.
2. Cross-store lifecycle queries compare per-file IDs as if they were globally unique, so resolving `evt-0001` in one repository can hide `evt-0001` in another.
3. Sensitive data can be persisted through unsanitized JSON source fields, and the primary event file is created with ordinary filesystem permissions rather than user-only permissions.
4. `--repo-root` can label an event as belonging to one repository while writing it into another repository's store.
5. A stale lock directory can block filing forever.
6. An append can succeed before a later index failure makes the command report failure, inviting duplicate retries.
7. The only integrated smoke suite can be skipped when most core plugin files change.
8. Read-side discovery can split one repository across multiple `.local*` stores, and a read-only query can create `.local` state.
9. The current lifecycle conflates “not formally mended” with “still unhandled”; the EdgeCourt corpus reports 14 open anchors even though several underlying product defects were repaired during ordinary work.
10. Recurrence can group a shared symptom after the anchor's causal explanation has been falsified, while the Mend clustering helper ignores the source and pivot fields the playbook calls primary.

The recommended direction is evolutionary:

- Preserve the surprise gate, worth test, recurrence pointers, bounded dashboard, bounded traps file, and capture/mend separation.
- Make lifecycle state store-qualified and order-sensitive first.
- Secure and unify the persistence path in the same immediate slice.
- Make the existing hybrid architecture explicit: ambient policy, capture skill, mend skill, and deterministic storage tooling.
- Make evidence language neutral and proportional without migrating the schema prematurely.
- Pilot verified closure and richer relationships only after repairing the existing lifecycle reducer.
- Turn the existing test artifacts into an enforced, cross-host verification surface.
- Run one real, user-authorized Mend session before claiming that mending ergonomics, trap publication, or future-session avoidance work in practice.

The plugin is useful for continued internal Linux use if callers accept privacy, stale-lock, routing, and lifecycle caveats. It is not yet ready to be presented as a safe foundational store. No MCP service, database, global identifier migration, or distributed adapter is justified by the present evidence.

### Decision matrix

| Priority | Decision | Change | Evidence class |
| --: | --- | --- | --- |
| P0 | Implement | Append-order lifecycle reopening and reclosing | Reproduced contract failure |
| P0 | Implement | Store-qualified identity for cross-store lifecycle | Reproduced cross-store false closure |
| P0 | Implement | User-only modes and uniform recursive redaction | Direct code evidence and controlled probes |
| P0 | Implement | Correct `--repo-root` routing and canonical paths | Controlled probe |
| P0 | Implement | Non-mutating read discovery and existing-store reuse | Controlled probe and real duplicate-store report |
| P0 | Implement | Bounded locks, pre-append integrity validation, full cleanup | Direct code evidence; stale-lock hang observed |
| P0 | Implement | Committed receipt before derived index/talkback work | Direct commit-order evidence |
| P0 | Implement | Remove `eval` and data interpolation into executable source | Direct code evidence and repository policy |
| P0 | Implement | CI selection for the whole plugin and one local test command | Reproduced selector gap |
| P1 | Implement | Disjoint Capture/Mend descriptions, compact disclosure, linked references | Static contract evidence and prior field friction |
| P1 | Implement | Source belief claims, session-aware summaries, correct repo/store labels | Reproduced contract gaps |
| P1 | Implement | Rename talkback's recurrence-threshold count and assert the new anchor is visible after append | Live audit surprise and source inspection |
| P1 | Implement | `Read, Write` capability and honest runtime metadata | Manifest and runtime inspection |
| Pilot | Measure first | Explicit verified closure during ordinary work | Strong EdgeCourt lifecycle evidence; false-closure risk remains |
| Pilot | Measure first | Structured Mend dispositions and validated trap upserts | Conceptual need; no real Mend corpus yet |
| Pilot | Measure first | Causal relationships and contradiction-aware clustering | EdgeCourt recurrence falsified its anchor; schema shape unsettled |
| Pilot | Measure first | Proportional narrative depth and compact anchors | Corpus suggests ceremony; no time-cost baseline |
| Defer | Do not build now | Object-valued evidence schema, `consequence`, amendment record kinds | Current strings/notes can carry the observed cases |
| Defer | Do not build now | Large-scale pagination/streaming redesign | Context cost observed; runtime scale failure not observed |
| Reject for now | Out of scope | MCP/service/database adapters, global ID migration, distributed actor/workspace ontology | No real multi-host requirement or evidence |

## 1. Purpose of this report

This report evaluates whether Friction Diagnostics is correctly framed, coherently designed, safely implemented, and sufficiently verified for its intended role as a generalized cognitive-debugging foundation.

The review answers five questions:

1. Should this capability remain a skill, or move to another product primitive?
2. Does its cognitive model generalize beyond software development?
3. Does the current implementation preserve data safely and durably?
4. Do its lifecycle and recurrence models represent what the corpus actually contains?
5. Do the tests prove the contract on the files and environments that matter?

No plugin behavior was changed during the audit. The report itself is the only intended deliverable. Temporary probes used disposable directories and synthetic data, then removed their outputs.

## 2. Current product model

### 2.1 Capture

The capture skill activates when reality behaves differently from what the agent predicted and recording that difference could change a future session's behavior.

It intentionally excludes:

- Expected failures.
- Engineered probes.
- Test failures that were predicted before implementation.
- Ordinary task status.
- Failures that do not create reusable learning.

A new friction event records:

- The actual outcome.
- The expected outcome and what grounded it.
- The reporter's reading of the situation from inside the decision.
- The response the reporter actually made.
- The information that would have changed the outcome.
- The sources or assumptions that supported the prediction.
- Workflow impact.
- A recurrence key and optional tags.

When the same trap appears again, the plugin supports a cheap recurrence record instead of requiring the full narrative again.

### 2.2 Mending

Friction Mend is the convergent workflow. It reviews accumulated events, groups events that share an underlying information gap, fixes the artifacts or instructions that misled the agent when possible, records append-only resolution provenance, and distills active recurring hazards into a short `known-traps.md` file.

Capture is meant to preserve unframed evidence at the moment of surprise. Mending is meant to impose taxonomy only after a corpus exists. This separation is one of the plugin's strongest design choices.

### 2.3 Persistence

Inside a Git repository, records are stored in a repo-local JSONL stream under a `.local*` directory. Outside a repository, storage falls back to a deterministic temporary path based on the current working directory.

The canonical stream currently contains three record kinds:

- `friction`: a full prediction-divergence account.
- `recurrence`: a pointer showing that an existing trap occurred again.
- `resolution`: provenance that one or more friction anchors were mended or deliberately closed.

Two derived files sit next to the stream:

- `INDEX.md`: a bounded dashboard.
- `known-traps.md`: a bounded feed-forward list intended to be read before future work.

The scripts also provide queries, aggregate reports, cross-repository reports, session summaries, recurrence detection, trap publication, and resolution recording.

## 3. Audit method and evidence

The audit used seven complementary lenses:

1. A complete read of both skills, their field rubrics, integration guidance, logging specification, mend playbook, schema, scripts, manifests, hooks, evaluations, and smoke tests.
2. A sparse review of the current EdgeCourt thread and its complete friction corpus for empirical behavior, including missed-capture candidates and events whose underlying product defect was later repaired.
3. A separately attributed review of the prior DiffHound corpus used by the first draft. DiffHound evidence is retained only where it supplies a distinct observed behavior; it is not described as evidence from the EdgeCourt thread.
4. A storage and CLI audit focused on privacy, concurrency, lifecycle, durability, routing, schema enforcement, and scale.
5. A trigger and instruction audit focused on false activation, progressive disclosure, ceremony, and cross-domain language.
6. A verification audit focused on what the committed tests actually run and prove.
7. An adversarial cross-domain review covering non-text observations, research uncertainty, creative judgment, physical-world incidents, sensitive information, and shared writers. Findings supported only by this lens are explicitly deferred.

The following checks were performed:

- All 18 committed POSIX smoke scenarios passed.
- Frontmatter checks passed for both skills.
- Script sanity checks passed, with only a warning that the top-level script surface is relatively large.
- Specification checks passed with minor warnings, including descriptions that do not follow the repository's numbered trigger-list convention.
- The reference checker found that `references/integration.md` and `references/logging-spec.md` are shipped but not linked from the capture skill.
- Strict internal Codex and Claude plugin validation passed with no warnings. Live external validation was not run: the installed wrappers lacked their platform-native optional binaries in this environment.
- Twelve simultaneous distinct filings produced twelve valid records with unique sequential identifiers in a delegated concurrency probe.
- A lock directory without a PID blocked indefinitely until an external timeout terminated the probe.
- A controlled sanitization probe confirmed that synthetic token-shaped text survived unchanged in JSON `sources[].ref` and `sources[].claim`.
- A controlled permissions probe created `events.jsonl` with mode `0644` under umask `0022`.
- A controlled routing probe executed from temporary repository A with `--repo-root` set to temporary repository B; the event was written to A but recorded B as its `repo_root`.
- An isolated lifecycle probe proved that `friction → resolution → recurrence` still produces zero open anchors even though the filing message says the recurrence reopens the cluster.
- An isolated two-store probe proved that resolving `evt-0001` in one store can remove an unrelated `evt-0001` from a cross-store open query.
- A query in a clean repository created a `.local` directory, proving that the nominally read-only path mutates workspace state.
- The EdgeCourt corpus contained 19 records at the audit cutoff: 14 full friction anchors, 5 recurrences, 0 resolutions, 4 distinct session references, and no `known-traps.md`.
- EdgeCourt's dashboard therefore classified all 14 anchors as open even though the current product code and event decisions show that several underlying defects were repaired during the same task.
- The prior DiffHound corpus contained 39 records at the audit cutoff: 27 full anchors, 12 recurrences, 0 resolutions, and no `known-traps.md`.
- The plugin audit itself filed 11 full anchors in `agent-tooling`: cross-repository label duplication, a round-trip validation-path mismatch, false recurrence-reopen behavior, unavailable host-native binaries, ungrounded trap publication, read-side directory creation, cross-store ID collision, non-injected known traps, zsh `path` and `status` special-variable traps, and ambiguous talkback labeling. No audit anchor was retrospectively edited or auto-closed.
- Neither real corpus has exercised a complete Mend cycle. Mend mechanics have smoke-test coverage; Mend ergonomics, resolution quality, trap maintenance, and future-session avoidance do not have real-world validation.
- The earlier DiffHound snapshot used in the first draft produced approximately 41 KB of open-event JSON and a 4.4 KB bounded dashboard. This is evidence of context cost, not yet evidence of runtime scalability failure.

These results establish that the happy-path capture implementation is substantive and useful. They also reveal several release-blocking defects for a foundational local store. They do not justify a distributed architecture or a large ontology migration.

## 4. Holistic review

At the product level, the answer is **yes: there is enough real experience to contribute dramatically without replacing the concept**. The EdgeCourt task alone generated useful records across seven distinct kinds of work, and the records preserved facts that ordinary error logs usually lose: the prior prediction, its basis, the choice made under that model, and the information that would have changed the choice.

The correct packaging remains a hybrid. Ambient instructions should make surprise detection and known-trap reading available during arbitrary work; the capture skill should own judgment and record composition; the Mend skill should remain explicitly invoked and own convergence; one deterministic local tool should own all persistence and lifecycle mechanics. Host hooks should enrich identity and fail open. A remote service is unnecessary for the validated local product.

The largest holistic defect is not capture quality. It is a broken learning loop:

1. Capture writes rich events during ordinary work.
2. Ordinary work often fixes the underlying defect immediately.
3. The capture workflow has no factual, verified closure path.
4. Mend is intentionally user-invoked and therefore may never run.
5. `known-traps.md` is never published, repaired events remain labeled open, and recurrent hazards are not fed forward before the next attempt.

EdgeCourt makes this concrete: 14 anchors and 5 recurrences were captured across four sessions, but there are zero resolutions and no known-trap file. At least the chart default, delayed focus, initial routing race, stale Case Files view, ingest identity, snapshot reference handling, and truncated-file recovery were addressed during the product task. The store does not represent that operational reality.

The user-only gate for batch mending should remain. The correction is to distinguish **factual closure of an already-verified in-task fix** from **corpus-wide mending judgment**, and to emit a bounded “mend suggested” signal when deterministic thresholds are crossed. Immediate closure should be an explicit, audited pilot—not autonomous self-exoneration.

The product's generality also needs precise language. The cognitive model is already general across multiple forms of agent work. The implementation is a local, filesystem-oriented Linux tool requiring a POSIX shell, `jq`, and Python 3. Domain generality does not require distributed storage. Host portability and multi-host persistence are separate ambitions and should not be smuggled into the immediate repair plan.

### 4.1 What is already strong

#### 4.1.1 The surprise gate

The question “Did reality diverge from a prediction, and would recording it change future behavior?” is the right gate. It avoids turning the system into a generic failure log or activity tracker.

#### 4.1.2 Explicit exclusions

Excluding predicted failures, engineered probes, and task status is essential. Without these exclusions, agents would fill the stream with expected red tests and ordinary progress updates, destroying signal quality.

#### 4.1.3 Capture at the point of divergence

Capturing the event when surprise occurs is valuable because the reporter still has access to its actual prior model. Post-hoc reconstruction encourages hindsight bias and corrected expectations.

#### 4.1.4 Prediction basis and pivot information

Recording what grounded the prediction and what information would have changed the choice makes the corpus mendable. Ordinary error logs rarely identify where missing information should have been surfaced.

#### 4.1.5 Cheap recurrence

Recurrence records reduced twelve repeated incidents to short pointers rather than forcing twelve full narratives. That is a significant context and attention saving.

#### 4.1.6 Capture/mend separation

The system does not automatically rewrite instructions based on one incident. It waits for deliberate corpus review. This reduces overreaction to one-off noise and lets taxonomy emerge from evidence.

#### 4.1.7 Bounded feed-forward artifacts

The dashboard and known-traps file deliberately remain small. Full precision stays in the event stream while only active, reusable guidance is loaded into future contexts.

#### 4.1.8 Append-only resolution provenance

Representing resolution as a new record rather than mutating the original event preserves the historical prediction and the later mend as separate facts.

#### 4.1.9 Store talkback

After filing, the store reports related events, recurrence counts, tag history, open clusters, and known-trap counts. This makes correct recurrence behavior less dependent on agent memory.

These strengths should be preserved through any redesign.

### 4.2 Evidence boundary

What is known:

- Capture produced useful, specific records under sustained real work.
- Cheap recurrence materially reduced repeated narrative cost.
- The local happy path and same-host concurrent append path work in the exercised cases.
- Several lifecycle, routing, redaction, permission, read-side mutation, and CI-selection promises fail in direct inspection or isolated probes.

What is inferred:

- A compact active-trap view and an explicit verified-closure path would reduce repeat work and stale backlog state.
- Better Mend preparation centered on source and pivot evidence would lower rediscovery cost.

What is not verified:

- No real Mend session has yet shown that a cluster was correctly root-caused, its source hardened, its resolution recorded, and its trap safely published.
- No later session has been observed reading a published trap and changing behavior.
- No precision/recall measurement exists for skill activation.
- No no-plugin control or measured filing-time baseline exists.
- No real non-software corpus validates physical, creative, stakeholder, or organizational ontology changes.
- No multi-host, shared-filesystem, or large-corpus benchmark justifies distributed adapters, globally unique IDs on disk, or 100,000-record requirements.

## 5. Findings

### 5.1 Persistence security and privacy

#### 5.1.1 JSON source fields bypass sanitization

Narrative fields are sanitized after JSON ingestion, but source objects from the recommended JSON path are validated, truncated, serialized, and then written without passing every string through the same sanitizer. Direct CLI source claims take a different path and are sanitized, so behavior differs by ingress method.

This is a serious defect because source references and claims are natural places for:

- URLs containing credentials or sensitive query values.
- API responses.
- Authorization headers.
- File paths containing account names.
- Snippets copied from configuration.
- Private user statements.

The persistence layer should recursively sanitize every persisted free-text field after parsing and before serialization, regardless of how the payload entered the system.

#### 5.1.2 Event files are not user-only by construction

The primary JSONL file is created by shell append under the caller's current umask. Under a normal `0022` umask, the controlled probe produced mode `0644`, making the record readable by other local users.

The store contains reasoning, paths, errors, source claims, and potentially private content. Security should not depend on the caller remembering a restrictive umask.

The writer should:

- Set `umask 077` before creating any store or temporary artifact.
- Create directories with mode `0700`.
- Create canonical and temporary files with mode `0600`.
- Harden existing files when safe.
- If hostile or shared repositories are in the threat model, refuse suspicious symlinked store targets unless the caller explicitly acknowledges the risk.

#### 5.1.3 Malformed payload recovery can expose raw secrets

When JSON parsing fails, the tool prints the offending raw line and saves the entire malformed payload for later replay. This is useful for recovery but unsafe by default.

Malformed input is precisely where schema-aware redaction is least reliable. The recovery path should therefore minimize data rather than preserve everything automatically.

Safer behavior would be:

- Print a bounded, best-effort-redacted excerpt rather than the raw line.
- Make full-payload quarantine explicit or clearly warned.
- Preserve the current `mkstemp` user-only file mode and ensure the quarantine parent directory is also private.
- Apply a retention or cleanup policy.
- Avoid copying payloads into repository-local paths when they may contain credentials.

The controlled concern is raw stderr output, full-payload retention, parent-directory privacy, location, and cleanup. The quarantine file descriptor itself is already created privately on the audited platform.

The documentation should state that “verbatim” always means “verbatim after mandatory secret redaction.”

#### 5.1.4 Resolution references and other metadata need the same policy

Resolution references, source references, tags, notes, and path metadata should not be exempt from the sanitization contract. A single schema-aware transformation should cover all persisted strings.

### 5.2 Repository routing is misleading

The JSON helper documents `--repo-root` as a way to resolve canonical storage from a repository root. In practice, default storage is derived from the current process's Git repository. The explicit value is later stamped into the event as metadata.

This can create a false record:

- Physical location: repository A.
- Recorded `repo_root`: repository B.

That breaks queries, cross-repository reports, audit provenance, and agent expectations.

The design should choose one of two honest contracts:

1. `--repo-root` controls both routing and recorded identity.
2. The flag is renamed to indicate that it only overrides recorded metadata.

The first option is preferable. Target resolution should be a pure function of explicit repository root, current working directory, and explicit events-file override, with canonical path validation.

### 5.3 Locking can block forever

The portable lock uses a lock directory plus a PID file. It can recover when the PID is numeric and no longer alive. It cannot recover safely when:

- The process is killed after creating the directory but before writing the PID.
- The PID file is malformed.
- The PID is reused by an unrelated live process.
- The lock exists on a filesystem shared by different hosts where local PID checks are meaningless.

The loop has no deadline and sleeps forever.

A shared lock helper should provide:

- A bounded wait.
- A clear timeout error naming the lock and owner evidence.
- An owner token containing host, PID, and preferably process-start identity.
- A creation timestamp or lease.
- Safe stale-lock reclamation.

Harden the existing atomic-directory lock first. Evaluate `flock` only if supported-host tests show a material benefit; do not weaken portability merely to change primitives.

Current shared-store claims should be scoped to concurrent writers on one host and one filesystem. Network filesystems, synchronized folders, multiple containers, and independent hosts require a different persistence adapter.

### 5.4 Append and receipt ordering can manufacture duplicates

The writer appends the canonical record, rebuilds the index, and only then prints the event identifier and success receipt. If index generation or post-append query work fails, the command can return failure even though the event already exists.

An agent may retry and create a duplicate recurrence or resolution.

The append should be the commit point. Immediately after a successful append, the tool should emit a machine-readable receipt containing the event identifier and canonical path. Index rebuilding and talkback should be treated as derived, recoverable work. Their failure should produce a warning and repair command, not erase knowledge of the successful append.

Call this a committed receipt unless the implementation adds and verifies an fsync boundary. Consider an idempotency key only if fault injection shows that ambiguity remains after receipt ordering is fixed.

### 5.5 Append-only semantics are internally inconsistent

The skill says records are never edited or deleted. The detailed logging specification documents an exception for adding tags and legacy aliases. The implementation rewrites the stream atomically to mutate the matching record.

This needs a product decision.

Preferred approach:

- Add an append-only metadata amendment record.
- Derive effective tags and aliases at read time.
- Preserve hashes of every prior line.

Simpler alternative:

- Explicitly narrow the claim to “event narratives are immutable; metadata may be atomically amended.”

For an audit-oriented foundational store, true append-only amendments are the stronger design.

### 5.6 Commit durability and record identity need hardening

Sequential identifiers are allocated from line count. This works when the append-only file is healthy and fully newline-terminated. It is vulnerable to misleading identity after:

- A partial final line.
- Manual blank lines or corruption.
- Disk-full interruption.
- Merge or synchronization conflicts.

For one local store, allocation from the maximum validated identifier under lock is safer. This is a hardening opportunity, not evidence that the current per-store identifier form must change. A future shared adapter would need a different identity design, but that is not immediate work.

The tool should also offer a read-only doctor and an explicit repair-tail workflow that quarantines damaged bytes rather than silently deleting them.

### 5.7 Store-controlled data reaches executable contexts

The session summary script interpolates `recorded_at` directly into Python source rather than passing it as an argument. A crafted syntactically valid JSONL store can therefore transform data into code.

The JSON ingestion helper also uses `eval` on generated shell assignments. Its current quoting makes the immediate path difficult to exploit, but it violates the repository's stated rule against `eval` on user input and creates unnecessary fragility.

Both paths should use explicit argument passing or a non-executable interchange format.

### 5.8 Temporary-file cleanup is incomplete

Several temporary event and rewrite files are not registered in a common cleanup trap. Interruption can leave sensitive temporary artifacts behind.

One cleanup registry should track every temporary path and remove it on normal exit, interrupt, or termination. Fault-injection tests should exercise interruption after lock creation, temporary creation, append, and derived report generation.

### 5.9 Trigger ownership overlaps

The capture skill says it applies to requests to log, review, mend, or distill friction. Friction Mend says it applies when the user asks to review, triage, mend, resolve, or distill logged friction.

This makes both skills plausible for the same request and weakens the intended capture/mend separation.

The trigger ownership should be explicit:

- **Capture:** a genuine prediction divergence occurs during work, a known trap recurs, or the user explicitly asks to log an incident.
- **Mend:** the user explicitly asks to review, triage, resolve, mend, or distill an existing friction log, backlog, corpus, dashboard, or traps file.
- **Neither:** the user asks to review the plugin itself, review unrelated work, fix an ordinary failure, or summarize a test result.

The capture description should remove “review, mend, or distill.” The Mend description should qualify “review” with an existing friction corpus or backlog.

### 5.10 The evidence model is too text-dependent

The current rubric requires verbatim actual evidence and at least one verbatim quote in every reading. This works for tool output and written instructions. It does not work universally.

Examples without a textual quote include:

- A layout looks visually unbalanced despite satisfying the grid.
- A physical component is warmer than predicted.
- A research measure moves in an unexpected direction.
- A stakeholder reacts differently than a plan predicted.
- A scene intended as tragic is experienced as comic.
- An expected event does not occur.
- A tacit assumption guides a reflexive action.

The correct general contract is best available primary evidence:

- Exact output when output exists.
- Exact quotation when wording exists.
- Measurement when something was measured.
- State transition when state changed.
- Explicitly labeled firsthand observation when no external record exists.
- Explicit absence when the surprise is non-occurrence.
- Honest uncertainty when evidence is incomplete.

The system should never force a fabricated quote merely to satisfy structure.

### 5.11 “Betrayal” assumes the wrong causal model

The phrase “what you trusted that betrayed you” is vivid but not neutral. A source can be accurate while the reader infers too much from it. A tool can behave correctly while an undocumented convention shaped the expectation. A person can provide reasonable information that becomes stale.

The neutral phrase should be “inputs that supported the prediction.” Mending can then determine whether the problem was:

- Incorrect content.
- Missing content.
- Poor placement or discoverability.
- Ambiguous wording.
- An unsupported inference.
- Stale information.
- Environmental behavior.
- A missing control or check.

### 5.12 Pivot information can be a set, not always one fact

Preferring one decisive fact is useful because it forces prioritization. Requiring exactly one fact can distort research, operational, creative, and organizational surprises.

The model should prefer the smallest actionable information unit while allowing:

- A coupled set of facts.
- Distributed knowledge held by multiple people.
- Information available only through a probe or experiment.
- A precedence rule between conflicting sources.
- “Unknowable in advance,” with an explanation.

### 5.13 Decision reconstruction should be proportional

For a serious policy deviation, reconstructing options, rejected alternatives, and perceived authority is highly valuable. For a low-impact first occurrence, forcing full choice architecture creates ceremony and encourages manufactured deliberation.

The rubric should allow:

- “I saw only one path.”
- “I responded reflexively and did not deliberate.”
- “I filed before responding.”
- A compact account for low-impact anchors.

Full decision reconstruction should remain mandatory for high-consequence events, instruction deviations, and cases where authorization or deliberate override is relevant.

### 5.14 Workflow impact is not consequence

The current impact values describe whether work stopped, degraded, became noisy, or continued. They do not describe the consequence of the error.

A workflow can continue smoothly while producing:

- A false result.
- A product defect.
- User-visible harm.
- Data exposure.
- Financial loss.
- Safety risk.
- A wrong strategic conclusion.

The product should preserve workflow disruption as one dimension and add an optional consequence or stakes dimension. The exact ontology should be tested before being made mandatory; the system should not infer severity without evidence.

### 5.15 Mandatory user-facing summaries are disproportionate

The skill calls the final summary a courtesy but requires the full renderer output to be pasted verbatim whenever an event was filed. In ordinary work this can visually dominate a response that is about something else.

The default should be:

- No mention when nothing was filed.
- A compact one-line disclosure when an event was filed during an unrelated task.
- A full table only when the user asked about friction, requested an audit trail, or the event materially changes the handoff.
- No raw query command in an ordinary product answer.

The full report remains available through the query tool and explicit summary command.

### 5.16 Lifecycle labels do not distinguish handled work from unmended learning

An event is currently open whenever no resolution record names it. This is internally consistent, but “open” is easy to read as “the immediate incident remains unresolved.”

The DiffHound corpus contains numerous events whose decision says that code or configuration was fixed and verified, yet all anchors remain open because no later mend session appended resolutions.

The lifecycle should distinguish:

- **Incident handled:** the immediate task recovered.
- **Source hardened:** the upstream information or control was changed and verified.
- **Needs evidence:** the event is worth retaining but cannot yet be resolved.
- **Active environmental trap:** the cause is external or immutable and remains relevant.
- **Closed as no further action:** retained historically but not worth further work.

Recording an immediate verified resolution should not require a separate batch mend when the active task already changed the betrayed source. Batch mending should remain responsible for cluster-level analysis, consolidation, and trap publication.

At minimum, dashboards should call unresolved anchors “unmended” rather than implying the incident itself is still broken.

### 5.17 Recurrence can over-group a symptom family

A recurrence is currently a pointer to one anchor and inherits the anchor's impact and explanatory context. In the observed corpus, Playwright locator failures were grouped under common anchors even when their causes included:

- Hidden alternate controls.
- Dynamic accessible-name changes.
- Duplicate live regions.
- Reused data attributes.
- Wrong hidden task views.
- Fuzzy matching against similar labels.

These share a symptom but not necessarily the same upstream prevention.

A useful rule is:

> Two events are recurrences when the same missing fact or upstream control would have prevented both.

When that is false, the relationship should be weaker:

- `related_to`: similar symptom or domain, different root cause.
- `caused_by`: a downstream manifestation of another event.
- `duplicate_of`: two anchors later determined to represent the same trap.

Recurrence records may also need optional occurrence-specific source or pivot details when the new occurrence differs materially from the anchor.

These relationships should be piloted before becoming required schema fields.

### 5.18 Concurrent semantic duplicates need a merge path

Two sessions filed nearly identical undocumented completion-field incidents twenty-seven seconds apart under different recurrence keys. The lock prevented write corruption but could not prevent semantic duplication because neither writer knew the other's intended taxonomy in advance.

Automatic semantic merging would be risky. The safer design is:

- Improve normalization and similarity suggestions.
- Keep filing conservative.
- Add append-only `duplicate_of` or cluster-merge provenance.
- Let Friction Mend consolidate anchors without rewriting history.

### 5.19 Mechanical similarity contains false positives

The current token-overlap helper proposed a cluster whose shared tokens were generic words such as “the” and “while.” This shows that raw token overlap is insufficient.

Improvement options include:

- Stop-word removal.
- Inverse-document-frequency weighting.
- Jaccard or cosine thresholds over distinctive tokens.
- Increased weight for shared source reference and pivot information.
- Bounded candidate explanations showing why the match was suggested.

Mechanical similarity should remain advisory and never silently merge events.

### 5.20 Query and reporting scale is unbounded

The canonical query slurps all matching records, materializes the complete result, and has no limit, field-selection, pagination, or cursor option. Friction Mend's first documented query asks for the entire open corpus.

This is acceptable for dozens of events and increasingly expensive for thousands. Pairwise token clustering is quadratic, every filing scans the full stream, and every filing rebuilds the full index.

The tools should add:

- `--limit` and explicit `--all`.
- Newest-first bounded defaults for agent-facing output.
- `--fields` or `--summary-only`.
- Cursor or date pagination.
- Streaming JSONL output.
- Bounded event identifiers per cluster with total and truncation metadata.
- Progressive mend flow: read dashboard and cluster hints first, then query selected anchors.
- Performance tests at 1,000, 10,000, and, if justified, 100,000 records.

### 5.21 The schema is descriptive rather than enforceable

The file advertises JSON Schema Draft 2020-12 but represents requiredness and record-kind applicability through custom `x-required` and `x-kinds` metadata. A standard validator accepts an empty object.

The design should either:

1. Become a real discriminated JSON Schema using `oneOf` or `if/then`, standard `required`, `minItems`, and record-kind constraints; or
2. Be renamed as a field catalog while a canonical validator implements the executable contract.

The writer should validate every new record. The reader may remain tolerant of documented legacy versions.

### 5.22 Existing-store corruption has no single policy

Some read paths validate every JSONL line and fail. Other scans silently skip malformed records. A full filing can append before index rebuilding discovers prior corruption.

The product needs one explicit policy:

- Fail before write and direct the user to a doctor command.
- Or quarantine and repair a damaged tail through a reviewed operation.
- Or tolerate malformed lines with a loud degraded-state warning.

Silently skipping corruption in one path while failing in another is not acceptable for an audit log.

### 5.23 CI does not follow the core plugin surface

The integrated smoke test is substantial, but the change detector is derived from the packaged render-table skill. Changes to core capture and mend scripts, schemas, hooks, and instructions can therefore skip the smoke job. The smoke test is also absent from the default `just test` and `just verify` recipes.

This is the highest-leverage verification correction because it makes existing tests matter on the changes they are intended to protect.

### 5.24 Trigger evaluations are not executed

The repository contains positive and negative trigger prompt files and behavioral eval descriptions. No runner or CI job consumes them.

As a result, nothing automatically proves:

- Capture activates when surprise emerges during work.
- Capture stays silent for expected failures.
- Capture and Mend are mutually exclusive where intended.
- A known recurrence uses the cheap path.
- An ordinary plugin review does not activate backlog mending.
- Behavior is equivalent across Codex and Claude.
- Non-code situations are classified correctly.

The trigger corpus is also too explicit: positive prompts generally contain words such as “surprised,” “log,” “record,” or “friction.” It does not test trajectories where a tool result unexpectedly changes the agent's model mid-task.

### 5.25 Cross-repository and portability tests are shallow

The current cross-repository smoke scans multiple stores nested under one temporary repository rather than two truly independent repositories with colliding local event identifiers.

It does not prove behavior for:

- Two real repositories with `evt-0001` in each.
- A directory outside Git.
- Multiple `.local*` candidates.
- Paths containing spaces or Unicode.
- Duplicate scan roots.
- Symlinked stores.
- Shared or remote filesystems.

The plugin validates for both supported hosts, but plugin round-trip validation is not continuously tied to every plugin change. The shell implementation is tested on Ubuntu rather than a deliberate POSIX shell matrix.

### 5.26 Some verification is nondeterministic

The interview-rotation test expects randomized questions to differ within a handful of attempts. The false-failure probability is low but unnecessary.

Production can remain randomized while tests receive an explicit seed.

### 5.27 Packaging and progressive-disclosure cleanup

Two active references are shipped but unreachable from the main skill. The skill body also contains policy, a full JSON payload, field definitions, exit codes, storage rules, query commands, summary rules, and a script catalog.

Recommended cleanup:

- Keep the surprise gate, exclusions, compact filing path, recurrence path, and capture/mend boundary in the main skill.
- Link a small reference index directly from the skill.
- Move detailed storage/query behavior and exit-code detail behind the logging specification.
- Rename `references/examples.md` to `field-rubrics.md`; it intentionally contains no worked examples.
- Update descriptions to the repository's numbered trigger-list convention.
- Update the Codex plugin interface capability from read-only to reflect that the plugin writes local state.

### 5.28 Resolved clusters do not reopen after recurrence

This is the most serious lifecycle defect found in the revised audit.

The capture CLI and logging specification explicitly say that filing a recurrence against a resolved anchor reopens the cluster. The query reducer instead treats an anchor as closed forever once its ID appears in any resolution. An isolated sequence proved the mismatch:

1. File `evt-0001`.
2. Resolve `evt-0001`.
3. File a recurrence against `evt-0001`.
4. Query open friction.
5. The result contains zero open anchors.

A regression after a mend is exactly the event that most needs renewed attention. Lifecycle must be derived from append order:

- A friction anchor opens the cluster.
- A resolution closes it.
- A later recurrence reopens it.
- A later resolution closes it again.

The same reducer must be used by queries, dashboards, statistics, filing talkback, cluster hints, cross-repository reports, and resolution duplicate checks. The current smoke test checks only that the CLI prints the words “reopens the cluster”; it does not verify state.

### 5.29 Cross-store lifecycle identity is incorrect

Event IDs are sequential within one file, not globally unique. Every repository can contain `evt-0001`. Cross-store queries currently slurp records into one array and compare resolution targets as unqualified ID strings.

An isolated two-store probe filed `evt-0001` in both stores and resolved it only in the first. The cross-store open query returned neither event. The resolution in repository A incorrectly closed repository B's event.

Backward-compatible repair does not require rewriting historical IDs. Read-side identity should be `(canonical physical store identity, event_id)`, and recurrence/resolution pointers should be scoped to their own stream. The reader should attach the actual input store identity rather than trusting self-reported `events_file` metadata.

### 5.30 Storage discovery can split a repository, and reads can write

Store resolution chooses `.local`, otherwise the lexicographically first `.local*` directory. It does not first discover an existing friction store. A repository with multiple local areas can therefore acquire parallel event streams, while the ambient snippet hardcodes only `.local/reports/friction/known-traps.md` and misses traps stored under `.local-test` or another valid local area.

The query path also calls a resolver that creates the chosen local directory. A controlled query in a clean repository created `.local` before failing to find an events file. A read-only diagnostic command should not mutate the workspace.

Split the resolver into:

- Read/discover mode: find existing stores and never create state.
- Write/create mode: prefer an existing friction store; if none exists and multiple `.local*` choices are plausible, follow explicit repository policy or return an ambiguity error.

The ambient trap reader should use the same canonical discovery mechanism as the writer.

### 5.31 Session summaries are time-window summaries

The summary script filters by timestamp, then labels its output “this session.” The query tool has no session filter. EdgeCourt has four distinct session references, including subagent activity, so unrelated records written during the same wall-clock window can be attributed to the wrong session.

The final audit reproduced this directly. A summary started immediately before the root agent's two filings rendered “3 event(s) this session” and included `evt-0011` from session `019f4cb3-…`, while the two root filings carried session `019f5c20-…`. The timestamp filter, not session identity, determined membership.

Add `--session-ref` to query and summary. When a current session identity is available, use it by default. When it is unavailable, label the result honestly as a time-window summary. `--all-sessions` should be explicit.

### 5.32 Source beliefs are required by the concept but optional in storage

The field rubric says every source should carry the belief it represented. The schema and JSON writer require only source kind and reference, and a full event with no source claim is accepted.

Without the prior belief, a mender cannot distinguish a misleading artifact from a correct artifact that the reporter misread. Require a nonblank claim for every full-event source. Keep recurrence records cheap and source-free. Replace the blame-oriented wording “what betrayed you” with “inputs that supported the prediction”; an input may be correct, stale, incomplete, poorly placed, or misinterpreted.

### 5.33 JSON exit-code behavior does not match the public contract

The skill says malformed or invalid `--from-json` payloads exit with code `2`. Several invalid payloads reach later shell validation and return `1` instead. Required fields and enums are duplicated across the schema-like catalog, JSON helper, flags path, and tests.

Use one validation path and reserve exit codes consistently by input mode. Keep legacy read tolerance separate from current write validation.

### 5.34 Mend has no real-world outcome validation

Both real corpora contain zero resolution records and no known-traps file. The Mend helper scripts pass smoke tests, but the following claims remain unverified:

- A model can form correct causal clusters from a real backlog.
- The chosen source edit actually removes the information gap.
- Resolution provenance is sufficient for later audit.
- A partial Mend does not erase unrelated traps.
- A published trap is read by a later session and changes behavior.
- Trap aging, removal, and reactivation behave correctly.

The immediate recommendation is not to add more mandatory taxonomy. Run one explicit end-to-end Mend pilot after the lifecycle and persistence defects are fixed.

### 5.35 Resolution outcomes are too binary and weakly verified

The written Mend contract effectively offers “mended” or `wontfix`, while real incidents include at least four states:

- Controllable root cause mended.
- Guard or mitigation added around an immutable source.
- Active external hazard accepted and retained as a trap.
- Obsolete or non-actionable record retired honestly.

The writer records an action string but does not require verification, require a reference, confirm that the reference exists, or distinguish whether the hazard remains active. Pilot a small structured contract—`mended`, `mitigated`, `external`, `not_actionable` plus `hazard_active`, references, verification, and residual risk—before making it canonical. A missing disposition can remain backward compatible.

### 5.36 Trap publication is replacement-oriented, not scoped or validated

The trap publisher atomically replaces the file and preserves the prior file on some validation failures, which is good. Its semantic checks are nevertheless too weak for a correctness-bearing startup artifact:

- A scoped Mend can erase unrelated traps because publication replaces the entire body.
- Concurrent publications are last-writer-wins and `--clear` is unlocked.
- Keys, anchor existence, counts, dates, active state, and duplicate entries are not reconciled against the event store.
- A query failure can be rendered as zero open events.
- The header says “auto-distilled” even though the model composes the contents.

Add a strict `--check`, store-backed validation, locked `--upsert` and `--remove-key`, explicit `--replace-all`, no-op behavior for an unchanged body, and an added/changed/removed receipt. Generated counts and dates should come from the store, not model transcription.

### 5.37 Clustering helpers ignore the playbook's primary evidence

The Mend playbook correctly prioritizes shared pivot information and shared source/claim classes. The helper tokenizes only `actual_outcome`, includes generic stop words, uses transitive union-find components, and can silently skip malformed JSON. A-B and B-C token overlap can therefore produce one cluster even when A and C share no evidence.

Keep clustering advisory. Improve candidate edges with explicit reasons:

- Same normalized source reference.
- Overlapping source claim.
- Overlapping pivot information.
- Rare shared outcome signature.
- Same recurrence key.

Show pairwise evidence, titles, impacts, and compact source/pivot summaries. Fail loudly on a malformed store. Do not automatically merge.

### 5.38 Cross-repository reports count stores but label repositories

The cross-repository report counts unique event files but labels rows with `repo_root`. Two stores under one repository therefore produce duplicate repository rows and inflate “repositories scanned.” This behavior has already appeared in the plugin's own friction corpus.

Report both `stores_scanned` and `repos_scanned`. Aggregate the repository view by canonical repository root and expose a separate per-store view only when requested.

### 5.39 Documentation and ambient-policy drift

The source manifests and skills are version `5.1.3`, while `context/state.md` still says `5.1.1` is live. The same repository's `AGENTS.md` also mandates a separate `/tmp/skill-errors/...` logger for skill problems, overlapping the plugin's narrower surprise gate, repo-scoped JSONL store, recurrence model, and silence rules.

This is not merely documentation polish. Two ambient diagnostic systems create inconsistent capture thresholds, duplicate storage, and competing mending workflows. Choose one foundational policy. The repository guidance should carry only the minimal surprise/recur/silence/trap-read contract and route the details to this plugin.

### 5.40 Filing talkback uses an ambiguous “open clusters” label

After this audit filed a new anchor, talkback reported `open clusters: 0` while the dashboard correctly reported 10 open anchors. Investigation showed that talkback counts only open recurrence keys with at least two sightings. The computation is internally consistent, but the label reads like the dashboard's general open count and made a successful new filing appear immediately closed or missing.

Rename the talkback metric to `repeated open clusters` or `open clusters with 2+ sightings`, and optionally report `open anchors` separately. Add a post-append invariant check that the newly committed anchor is visible to the lifecycle reducer; a genuine mismatch should degrade talkback explicitly rather than being hidden behind a zero.

## 6. Recommended target architecture

The strongest packaging is a deliberate hybrid.

### Layer 1: ambient surprise policy

A short host or repository instruction should carry only the universal gate:

1. If reality diverges from a prediction, assess whether the event would change future behavior.
2. If not, continue silently.
3. If it would, capture it immediately.
4. If it is the same root cause as a known trap, record a recurrence.
5. Do not file expected failures, engineered probes, or task status.

This layer makes mid-task activation possible without loading the complete workflow into every context.

The policy should also discover and read the canonical bounded trap view through the same store resolver as the writer. The separate `/tmp/skill-errors/...` policy in this repository should be migrated or retired so agents do not maintain two incompatible diagnostic systems.

### Layer 2: capture skill

The capture skill should own:

- Full event capture.
- Minimal anchors.
- Recurrence filing.
- Duplicate soft stops.
- Explicit user requests to log an incident.
- Compact disclosure of a filing.
- An explicit factual closure command when the current task has already fixed and verified the recorded source; this should begin as a measured pilot.
- A compact “Mend suggested” signal only when deterministic thresholds are crossed, such as a blocked unmended event, a third recurrence, or a configured backlog-age threshold.

It should not own backlog review, source editing, or trap distillation.

### Layer 3: mend skill

The mend skill should activate only for an existing corpus and should own:

- Cluster review.
- Root-cause analysis.
- Source hardening.
- Resolution provenance.
- Anchor consolidation relationships.
- Trap publication.
- Honest “leave open pending named evidence” outcomes.
- Structured verification and residual-hazard judgment.
- Scoped trap upserts and removals rather than implicit whole-file replacement.

A mend session should not be forced to classify every selected cluster as either fixed or `wontfix`. Insufficient evidence is a legitimate state.

### Layer 4: deterministic persistence tool

One canonical implementation should own:

- Path resolution.
- Input parsing.
- Schema validation.
- Recursive redaction.
- Permission enforcement.
- Locking.
- ID allocation.
- Append and fsync policy.
- Committed receipts.
- Optional idempotency only if fault tests justify it.
- Honest metadata-mutation semantics; amendment records only if audit-grade immutability is required.
- Corruption detection.
- Derived-view rebuilds.
- Store-qualified, append-order lifecycle reduction.
- Read-only discovery that cannot create repository state.
- Integrity diagnostics for malformed records, duplicate IDs, dangling pointers, path mismatches, and trap drift.

Shell wrappers may remain for portability, but they should delegate to this one writer rather than reimplementing policy across ingress paths.

### Layer 5: optional storage adapters — deferred

The current JSONL adapter is appropriate for the validated local product. Its internal operation boundary should avoid making future adapters impossible, but no adapter should be built without a real multi-host need. Possible future environments could use:

- Local POSIX JSONL.
- Host-managed key-value storage.
- MCP-backed storage.
- A local database.
- A shared service or database for team writers.
- A no-filesystem mode that returns a validated record for the caller to persist.

If multi-host or team support is later authorized, it will need globally unique record identifiers and explicit actor, workspace, and store provenance. That is a separate product track. The immediate cross-store collision can and should be fixed by qualifying legacy IDs with canonical store identity on reads; it does not require a UUID migration.

## 7. Proposed event-model evolution

Schema changes should be eval-driven. The following model is a direction to test, not a mandate to add every field immediately.

### 7.1 Revised meanings for existing fields

#### `actual_outcome`

Best available primary evidence. Exact output or quotation when available; otherwise a labeled observation, measurement, state change, absence, or uncertainty statement. Always subject to mandatory secret redaction.

#### `expected_outcome`

The prediction actually held before the divergence and what supported it. It must not be retrofitted using later knowledge.

#### `reading`

The reporter's model and sequence of interpretation. Quotations are required only when textual wording existed and materially informed the choice.

#### `decision`

The response actually made. It may state that no deliberation occurred, only one path was visible, or the record was filed before action. Deeper choice reconstruction is proportional to consequence and policy relevance.

#### `pivot_information`

The smallest actionable fact or coupled information set that would have changed the response, including where or how it could be obtained. It may be distributed, experimental, or genuinely unknowable in advance.

#### `sources`

Prediction bases: artifacts, instructions, tools, assumptions, memories, observations, people, or environmental signals that supported the expectation. A source need not be wrong.

#### `impact`

Rename or clarify this as workflow disruption: continued, noisy, degraded, or blocked.

### 7.2 Candidate optional fields

#### `consequence`

An evidence-backed account of output, user, data, safety, financial, legal, or decision harm. It should remain optional and should not be inferred when unknown.

#### `relation`

An append-only relationship to another event, with candidate kinds such as:

- Same root-cause recurrence.
- Related symptom family.
- Caused by.
- Duplicate of.

#### `disposition`

An append-only lifecycle record distinguishing:

- Incident handled.
- Source hardened and verified.
- Needs evidence.
- Active external trap.
- No further action.

This may be better represented through additional record kinds than mutable status fields.

#### `amendment`

Append-only changes to tags or other metadata, preserving prior event lines unchanged.

### 7.3 Recurrence test

The recurrence test should be semantic:

> Would the same missing information or upstream control have prevented both occurrences?

If yes, record a recurrence. If no, record a distinct event and optionally relate it to the prior symptom family.

## 8. Prioritized implementation plan

### Phase 0: immediate correctness and security

These should precede broader schema redesign:

1. Replace permanent-set lifecycle logic with one append-order reducer and prove `friction → resolution → recurrence → reopened → resolution → closed` everywhere.
2. Qualify cross-store event identity with canonical physical store identity and prove resolutions cannot leak across stores.
3. Enforce user-only filesystem modes.
4. Apply recursive sanitization to every persisted string.
5. Redact or minimize malformed-input diagnostics and quarantine.
6. Correct `--repo-root` storage routing and canonicalize all explicit paths.
7. Split read-only discovery from write/create resolution; prevent queries from creating `.local` state or splitting a corpus.
8. Replace unbounded lock loops with one bounded shared lock helper.
9. Validate store integrity before append.
10. Emit a **committed receipt** immediately after append; report derived-view failure as degraded success with a repair command. Reserve “durable” for an implementation that actually defines and verifies fsync semantics.
11. Remove data interpolation into Python source and remove `eval` from JSON ingestion.
12. Clean up every temporary artifact on success, error, timeout, and interruption.
13. Make the integrated smoke suite run for every plugin change.

Idempotency keys are deferred until receipt ordering and fault-injection tests show residual ambiguity. The observed code path creates duplicate risk, but this audit did not observe a retry-created duplicate.

### Phase 1: trigger and user-experience boundaries

1. Remove mend/review ownership from the capture description.
2. Narrow Mend to explicit existing-corpus work.
3. Replace blame-oriented evidence language with neutral prediction-basis language.
4. Make quotation requirements conditional on textual evidence.
5. Make narrative depth proportional.
6. Replace mandatory full summaries with compact default disclosure and opt-in detail.
7. Link active reference files and simplify the main capture skill.
8. Require a belief claim for every full-event source.
9. Add session-aware queries and summaries.
10. Correct cross-repository report labels and aggregation.
11. Correct plugin capability and runtime-dependency metadata.
12. Reconcile the repository's older `/tmp/skill-errors/...` policy with this plugin.

### Phase 2: lifecycle and relationship pilots

1. Rename dashboard “open” language to “unmended” before adding new states.
2. Pilot an explicit verified resolution for ordinary-task fixes; measure false closure before making it default.
3. Run one real end-to-end Mend on a repaired corpus: prepare, cluster, inspect artifacts, verify, record resolution, publish traps, and observe a later trap read.
4. Pilot `mended`, `mitigated`, `external`, and `not_actionable` dispositions with independent `hazard_active`, references, and verification.
5. Add locked, scoped trap upsert/remove operations and strict store-backed validation.
6. Improve mechanical clustering with source, claim, pivot, rare-token, and contradiction evidence.
7. Test `related_to`, `supersedes_hypothesis`, `split_from`, and `duplicate_of` in Mend output before adding canonical record kinds.
8. Test occurrence-specific details on recurrence records.
9. Separate workflow disruption from consequence only if real mends need the distinction.

These changes should first be evaluated against existing corpora rather than introduced as mandatory fields from theory alone.

### Phase 3: measured scale; adapters remain deferred

1. Add bounded query defaults, pagination, field selection, and streaming output.
2. Add corpus-scale performance tests.
3. Define the local persistence operation cleanly enough that future adapters are not coupled to shell details.
4. Do not introduce globally unique on-disk identifiers, actor/workspace provenance, MCP, database, or service-backed storage until a real multi-host use case exists.

## 9. Verification plan

### 9.1 Canonical test command and CI selection

Add one `test-friction-diagnostics` command and include it in the repository's normal test or CI surface. It should run whenever any of the following change:

- Any file under `plugins/friction-diagnostics`.
- Vendored shared scripts or schema.
- Plugin packaging metadata.
- The render-table crate or packaged renderer.
- Host-conversion behavior affecting the plugin.

### 9.2 Store-integrity tests

Add deterministic tests for:

- `friction → resolution → recurrence → open → resolution → closed` through every lifecycle consumer.
- Two physical stores with the same `evt-0001`; resolving one leaves the other open.
- Relative, absolute, and symlink-spelled store paths resolving to one physical store identity.
- Duplicate record IDs, dangling recurrence anchors, dangling resolutions, and recurrence cycles.
- 32 to 100 concurrent full filings.
- Mixed concurrent friction, recurrence, resolution, and amendment writes.
- Unique identifiers and zero lost records.
- Live lock waiting followed by success.
- Dead PID recovery.
- Missing and malformed PID recovery.
- Reused PID or owner mismatch.
- Bounded lock timeout.
- Process interruption before and after PID publication.
- Process interruption after temporary creation.
- Process interruption after append but before index rebuild.
- Index failure after successful append.
- A committed receipt immediately after append and degraded success after index failure.
- Idempotent retry after ambiguous failure, if idempotency remains necessary after the receipt fix.
- Disk-full or partial-tail simulation where feasible.
- Existing-store corruption and reviewed recovery.

### 9.3 Privacy tests

Table-drive every free-text field through fake secret shapes:

- Narrative fields.
- Source references and claims.
- Notes.
- Tags.
- Resolution action, reference, and note.
- URL user information and sensitive query parameters.
- Malformed payload excerpts.

Assert:

- No fake secret reaches the canonical stream.
- No fake secret reaches stderr.
- No fake secret reaches quarantine without explicit, user-only retention.
- Direct flags and JSON ingestion produce the same sanitized record.
- Files and directories use the required modes.
- Symlinked targets are handled according to policy.

### 9.4 Routing tests

Exercise:

- Current repository equals explicit repository root.
- Current repository differs from explicit repository root.
- Explicit events-file override.
- Directory outside Git.
- `.local`, `.local-test`, and multiple `.local*` candidates.
- Spaces, Unicode, and shell metacharacters in paths.
- Two independent repositories with colliding local event identifiers.
- Duplicate scan roots and symlinks.
- A read-only query in a clean repository; it must create no directories or files.
- One existing store under a non-lexicographically-first `.local*` directory; the writer and ambient trap reader must find it.
- Multiple empty `.local*` candidates; the tool must not silently split the stream.
- Cross-repository reporting with two stores under one repository; `repos_scanned` and `stores_scanned` must remain distinct.

### 9.5 Schema tests

Create a real per-kind validator and test:

- Valid friction, recurrence, resolution, relationship, and amendment records.
- Missing required fields.
- Empty sources.
- Invalid kinds.
- Incompatible fields for a record kind.
- Unknown future versions.
- Duplicate identifiers.
- Legacy v4 and v5.0 tolerance.
- Every writer's output against the canonical schema.
- Nonblank belief claims on every full-event source.
- Documented JSON-input exit codes for missing, blank, short, wrong-type, and invalid-enum fields.

### 9.6 Trigger evaluations

Turn trigger prompts into executable trajectory evaluations. Test both supported hosts with balanced positive and negative cases.

Required cases include:

- Unexpected tool behavior emerges during work without the user saying “friction.”
- A test fails exactly as predicted.
- A user explicitly asks to log a surprising incident.
- A user explicitly asks to mend an existing backlog.
- A user asks to review the plugin itself.
- An ordinary command fails and needs repair but produces no reusable surprise.
- A known root cause recurs.
- A similar symptom appears with a different preventive fact.
- Nothing is filed and no diagnostic mention appears.
- One event is filed during unrelated work and only compact disclosure appears.

The first executable matrix should cover the domains observed in real work: code, browser/tool behavior, UI, testing, data contracts, coordination, patching, and user corrections. Writing, research, creative work, organizational decisions, and physical-world observations should be added when real examples exist; synthetic cases alone must not be described as validation.

### 9.7 Lifecycle evaluations

Test:

- Immediate incident recovery without source hardening.
- Immediate source hardening and verification.
- Cluster-level mending.
- External immutable trap.
- Insufficient evidence left open.
- No actionable change recommended.
- Duplicate anchor consolidation.
- Recurrence after a prior resolution.
- Current-session versus time-window summaries with interleaved session references.
- Structured `mended`, `mitigated`, `external`, and `not_actionable` pilot dispositions.
- Active external hazards remaining in traps while verified mended hazards are removed.
- Scoped trap upsert/remove preserving unrelated entries.
- Trap validation against anchor, canonical key, sighting count, latest occurrence, and active state.
- One full real-corpus path: explicit Mend request → causal cluster → artifact inspection → verified source change → resolution receipt → trap publication → later session reads the trap.

### 9.8 Scale and output bounds

Generate deterministic corpora of 1,000 and 10,000 records before committing to a scale redesign. Measure:

- Filing latency.
- Index rebuild latency.
- Query memory and output size.
- Cluster-hint latency.
- Dashboard size.
- Session-summary size.
- Cross-repository report size.

Assert bounded sections and make intentionally unbounded modes explicit through `--all` or equivalent.

### 9.9 Determinism and portability

- Add a test seed for interview rotation.
- Run shell tests under the intended POSIX shells.
- Round-trip and validate the plugin for Codex and Claude on relevant changes.
- Verify vendored copies remain byte-identical to their declared source of truth.
- Test dependency-missing errors for Python, `jq`, and the packaged renderer.

## 10. Non-goals and cautions

The following changes should be avoided unless evidence later demands them:

- Do not replace the surprise gate with generic failure logging.
- Do not automatically file every error.
- Do not automatically merge semantically similar events.
- Do not infer consequence or severity from workflow disruption alone.
- Do not force a universal domain taxonomy into capture-time tags.
- Do not make mending autonomous.
- Do not load the full corpus into every session.
- Do not add a network service merely to make a local-first tool appear more sophisticated.
- Do not make every optional relationship or lifecycle concept a required field before evals demonstrate value.
- Do not treat absence of friction records as evidence that work was correct; unnoticed and deliberate deviations remain outside the instrument's observation boundary.

## 11. Expected outcomes

If the proposal is implemented successfully:

- A friction record can be filed without exposing it to other local users.
- Every ingress path applies the same validation and redaction policy.
- The canonical store cannot silently disagree with recorded repository identity.
- Lock failures are bounded and diagnosable.
- A successful append always yields a committed receipt even if derived reporting fails.
- Retry ambiguity is bounded and does not create duplicate records.
- The public immutability contract matches implementation; if audit-grade append-only metadata is chosen, changes are represented as amendments rather than rewrites.
- Capture and Mend activate on distinct, testable intents.
- Non-text and non-code surprises can be recorded honestly without invented quotes.
- Low-impact anchors are cheap, while serious deviations retain rich reasoning.
- Recurrence means shared root cause rather than merely similar symptoms.
- Immediate task recovery, source hardening, and unresolved learning are distinguishable.
- Ordinary user responses are not dominated by internal diagnostic appendices.
- Core plugin changes cannot bypass the integrated smoke suite.
- Agent-level trigger behavior is measured rather than assumed.
- The local JSONL adapter remains simple, and no remote adapter is built without a real requirement.

## 12. Final assessment

### Packaging verdict

**Hybrid recommended.** The plugin already approximates the correct structure but should make it explicit:

- Ambient policy for detecting worthwhile surprise.
- Capture skill for recording events and recurrences.
- Mend skill for explicit corpus review and feed-forward repair.
- Deterministic tool for safe persistence and queries.
- Optional host-specific identity enrichment.
- Storage adapters only after a real multi-host requirement is demonstrated.

### Whole-product judgment

Friction Diagnostics is conceptually coherent and meaningfully differentiated. Its strongest contribution is not the JSONL format or reporting scripts. It is the preservation of the reporter's prior model and the missing information that would have changed the decision.

The plugin is not fundamentally too bespoke. Its cognitive kernel is broadly general. The current implementation is, however, specifically shaped around filesystem-capable agents on Linux. That limitation is acceptable when stated honestly. Domain-general reasoning, host portability, and distributed persistence are different axes; the latter two are not prerequisites for a foundational cognitive model.

### Readiness

- **Internal single-host Linux usage:** useful but not safe-by-default until privacy, stale-lock, routing, and append/receipt defects are fixed.
- **Same-host multi-agent usage:** happy-path concurrent appends work, but lifecycle identity, stale locks, ambiguous post-append outcomes, and shared store discovery are not fault-hardened.
- **Foundational use across arbitrary domains:** the cognitive frame is promising; only software/agent-work and one communication correction have real corpus evidence.
- **Multi-host or shared-service substrate:** out of scope and unvalidated; do not build it yet.
- **Highest-leverage implementation fix:** make lifecycle append-order-correct and store-qualified, then secure and unify the persistence path.
- **Highest-leverage verification fix:** run the integrated smoke suite for every friction-diagnostics plugin change.
- **Highest-leverage learning-loop fix:** add an explicit verified-closure pilot and complete one real Mend-to-trap-to-future-session cycle.
- **Highest-leverage conceptual fix:** define evidence neutrally and recurrence causally while preserving the strict surprise gate.

## Appendix A: Principal implementation locations

The following repository locations contain the behaviors discussed in this report:

- Capture policy and field definitions: `plugins/friction-diagnostics/skills/friction-diagnostics/SKILL.md`
- Mend policy: `plugins/friction-diagnostics/skills/friction-mend/SKILL.md`
- Field-quality rubric: `plugins/friction-diagnostics/skills/friction-diagnostics/references/examples.md`
- Logging contract: `plugins/friction-diagnostics/skills/friction-diagnostics/references/logging-spec.md`
- Integration guidance: `plugins/friction-diagnostics/skills/friction-diagnostics/references/integration.md`
- Mend playbook: `plugins/friction-diagnostics/skills/friction-mend/references/mend-playbook.md`
- Record catalog/schema: `plugins/friction-diagnostics/skills/friction-diagnostics/friction-event-schema.json`
- Capture and recurrence writer: `plugins/friction-diagnostics/skills/friction-diagnostics/scripts/report-friction.sh`
- Common path, sanitizer, and schema helpers: `plugins/friction-diagnostics/skills/friction-diagnostics/scripts/_common.sh`
- Query implementation: `plugins/friction-diagnostics/skills/friction-diagnostics/scripts/query-friction.sh`
- Report generation: `plugins/friction-diagnostics/skills/friction-diagnostics/scripts/generate-report.sh`
- Session summary: `plugins/friction-diagnostics/skills/friction-diagnostics/scripts/render-summary.sh`
- Resolution writer: `plugins/friction-diagnostics/skills/friction-mend/scripts/record-resolution.sh`
- Cluster hints: `plugins/friction-diagnostics/skills/friction-mend/scripts/cluster-hints.sh`
- Trap publisher: `plugins/friction-diagnostics/skills/friction-mend/scripts/update-traps.sh`
- Integrated smoke suite: `plugins/friction-diagnostics/skills/friction-diagnostics/tests/smoke-posix.sh`
- CI selection: `.github/workflows/ci.yml`
- Local test surface: `justfile`
- Packaged-skill path configuration: `packaging/skills.toml`

## Appendix B: Recommended first delivery slice

A focused first implementation slice should include only the changes that remove immediate correctness risk:

1. One append-order lifecycle reducer shared by every read/report path.
2. Store-qualified lifecycle identity for cross-store reads.
3. One canonical writer with recursive redaction and user-only modes.
4. Correct explicit repository routing and non-mutating read discovery.
5. Pre-append integrity validation and bounded robust locking.
6. Committed receipt emission immediately after append, with derived-view failure reported as degraded success.
7. Removal of executable interpolation and `eval` ingestion.
8. Complete temporary cleanup and a clear append-only metadata decision.
9. One canonical `test-friction-diagnostics` command.
10. CI selection for the entire plugin tree.

That slice would materially improve the plugin without forcing premature changes to its event ontology. Trigger, disposition, relationship, cross-domain, and adapter evolution can then proceed through measured evaluations rather than speculation.

## Appendix C: Observed plugin-induced friction and workarounds

This appendix separates two categories that should not be conflated:

1. **Friction the plugin successfully captured:** an unrelated tool, test runner, browser, or instruction behaved unexpectedly, and Friction Diagnostics preserved the incident usefully.
2. **Friction caused by Friction Diagnostics itself:** the plugin's instructions, trigger model, scripts, storage, or output made the task harder, riskier, or less clear.

### C.1 Plugin-induced friction from the prior DiffHound audit

This subsection is retained from the report's first evidence pass and is explicitly attributed to DiffHound. In the current EdgeCourt review, the user deliberately requested both logging and mending, so dual activation in this task is not evidence of accidental trigger overlap.

| Plugin behavior | What happened | Why it mattered | Workaround used |
| --- | --- | --- | --- |
| Capture and Mend both claim “review” and mending language | A prior read-only plugin review made both skills appear applicable. | Dual activation increased instruction load and created a risk of accidentally running a mend workflow. | Both skills were read, but Friction Mend was used only as an analytical lens. Static description overlap remains real; the current EdgeCourt task does not independently prove behavioral overlap because the user explicitly invoked both. |
| Mandatory full session summary | A focused answer about Playwright test coverage ended with a Unicode table, event-store path, and raw shell query. | The diagnostic appendix visually dominated an unrelated product-status answer and exposed internal filesystem detail the user had not requested. | The required block was pasted because the skill used `SHALL`. The proposal changes the default to a compact one-line disclosure and reserves the table for explicit friction work. |
| “Courtesy” conflicts with `SHALL` | The summary was described as nonessential courtesy while being mandatory. | Agents cannot exercise proportional judgment when the instruction simultaneously says the output is optional in purpose and absolute in execution. | The mandatory path was followed. The report recommends removing the contradiction. |
| Full-event field ceremony for low-impact surprises | Low-impact tool and selector surprises required actual, expected, reading, decision, pivot, sources, impact, key, and often tags. | The DiffHound corpus concentrated substantial narrative cost on mostly `noisy` events. Some records became formulaic or contained reconstructed choice architecture disproportionate to the incident. | Short fields were used where validation allowed, but the skill's informational nudges still encouraged expansion. The proposal introduces proportional depth and a genuinely compact anchor. |
| Verbatim evidence requirement could not always be satisfied | At least one event stored a paraphrased `actual_outcome`, and another stored an imperative future instruction as `decision`. | The written quality contract was stronger than the validator and stronger than some real evidence permitted. The stream looked structurally valid while violating the intended epistemic contract. | Human review identified the mismatch after filing. There was no automated quality warning. |
| No ordinary-task resolution path | Many events described a fix and verification in `decision`, yet the dashboard still reported every anchor as open. | A separate user-authorized mend session was required merely to record that an in-task fix had already happened. This made “open” reflect process ceremony rather than operational state. | Events were left open because the user had not asked for mending. The audit interpreted “open” as “unmended,” not “incident still broken.” |
| Symptom-level recurrence | Multiple Playwright locator incidents were filed against the same anchor despite materially different causes. | The recurrence count became a count of a broad symptom family rather than one upstream trap. The inherited anchor source and pivot were not accurate for every occurrence. | Occurrence notes preserved some distinctions, and the later audit manually inspected each recurrence rather than trusting the aggregate key. |
| Near-simultaneous duplicate anchors | Two agents filed essentially the same undocumented child-result requirement under different keys within seconds. | Locking protected bytes but not semantic identity. Both events stayed as separate clusters. | The audit used token candidates and manual comparison to recognize the duplicate. No append-only merge relation currently exists. |
| Unbounded query output | The full open-event JSON query was already about 41 KB for only 21 anchors. | A Mend agent following the documented “read the open corpus” command can consume substantial context before deciding which clusters matter. | The audit used the 4.4 KB bounded `INDEX.md`, aggregate stats, and cluster hints first, then inspected targeted evidence. |
| Active references were not discoverable from the skill | The deterministic reference checker reported `integration.md` and `logging-spec.md` as unlinked. | Important caveats and exact storage semantics are shipped but are not reachable through the progressive-disclosure route. | The files were discovered through repository inventory rather than skill-directed navigation. |
| Core smoke suite not part of the normal local verification surface | `just test` and `just verify` did not run the plugin's integrated smoke suite. | A maintainer can receive a green normal test run after changing core writer behavior without exercising the writer lifecycle suite. | The smoke script was invoked manually during the audit. |
| CI change detection is tied to renderer packaging | Most writer, schema, hook, Mend, and instruction changes do not select the friction smoke job. | The strongest existing tests can be bypassed by the changes they are meant to protect. | The smoke suite and structural checks were run directly rather than relying on CI selection. |
| JSON source sanitization differed from CLI sanitization | Synthetic token-shaped text survived in JSON source references and claims. | The recommended JSON path was less safe than the secondary direct-flags path. | The audit used only fake tokens and disposable stores. Until fixed, callers must pre-redact source objects themselves. |
| Event-file permissions followed ambient umask | A controlled event store was created as `0644`. | The tool's privacy posture depended on the caller's shell configuration. | The probe used a disposable directory. The interim workaround is to run under `umask 077` and verify modes explicitly. |
| `--repo-root` did not route storage | A probe from repository A with repository B as `--repo-root` wrote into A while labeling the event B. | Physical and logical provenance diverged. | Reliable callers must currently pass an explicit `--events-file`; `--repo-root` alone cannot be trusted for routing. |
| Stale lock with no PID waited indefinitely | A delegated probe had to be killed by an external timeout. | A crash between lock-directory creation and PID publication can permanently block all future writers. | The probe wrapped the command in `timeout`. Until fixed, operators must inspect and remove stale locks manually after verifying no writer is active. |

### C.2 EdgeCourt field experience

The current EdgeCourt corpus contains 19 records: 14 anchors and 5 recurrences across four session references. The following table is the direct answer to “where could the plugin have helped more?” in this task.

| Observed situation | What worked | Remaining friction or missed support | Proposed generalized improvement |
| --- | --- | --- | --- |
| Chrome tab discovery succeeded, then the browser disappeared (`evt-0002`, `evt-0003`, `evt-0004`) | One rich anchor plus cheap recurrence records represented repeated failure well. | The records lack structured backend/resource identity that would distinguish the disappearing tab, profile, and bridge instance. | Capture agent task path, tool/plugin version, and contested resource when discoverable. |
| Chrome and in-app browser produced the exact same `incrementalAriaSnapshot` failure under two recurrence keys (`evt-0001`, `evt-0010`, `evt-0013`, `evt-0019`) | Later in-app occurrences used recurrence correctly. | User-authored keys let the same likely capability defect become two anchors. No preflight warned future sessions before the first retry. | Suggest semantic duplicates conservatively; publish a generated, bounded active-trap view for recurrent or blocked unmended hazards. |
| Truncated command output contaminated JSON fixtures (`evt-0005`) | The event preserved the false assumption about tool output and the corrective recapture. | The reporter had to summarize evidence manually after the unsafe output path. | Support `--actual-file` or stdin evidence capture with hash and a separate semantic title. |
| A second Settings timeout disproved the first timeout explanation (`evt-0008`, `evt-0009`) | Recurrence was cheap and preserved the repeated symptom. | The recurrence inherited an anchor whose causal reading had been falsified. | Require the same preventive fact, not merely the same symptom; pilot `supersedes_hypothesis` or `split_from` during Mend. |
| Global ingest succeeded but the open Case Files selector remained stale (`evt-0011`) | This was exemplary capture-before-fix: integration boundary, evidence, response, and pivot were all useful. | The subsequent verified product fix still appears mechanically open. | Add an explicit verified-closure pilot separate from batch mending. |
| Parallel work reused a port and changed a shared Rust DTO (`evt-0012`, `evt-0014`) | Subagents filed useful blocked/noisy records without editing another agent's owned work. | `session_ref` does not identify agent task, repository revision, changed symbol, or contested resource. | Auto-enrich with agent/task, revision, and structured resource metadata when available. |
| A failed multi-file patch truncated an untracked Rust file (`evt-0015`) | Logging stopped the agent from treating the failure as harmless and preserved the recovery pivot. | The preventive check never reached a startup trap because no Mend occurred. | Generate a capped active-trap view for blocked or recurrent unmended hazards; keep curated traps Mend-owned. |
| Chart default order, delayed modal focus, and late initial routing caused final integrated failures (`evt-0016`–`evt-0018`) | The records captured subtle integrated races rather than only syntax or unit failures. | All three repaired sources remain open in the diagnostic dashboard. | Rename current status to `unmended`; allow explicit verified closure with artifact/test provenance. |
| The user corrected an overbroad completion implication | Later communication separated implementation epics from external production validation. | No friction record was filed even though the user's correction exposed a wrong prior model of scope. | Make user corrections about scope, intent, completion, or factual claims explicit surprise candidates. |
| Chrome reported a profile `FILE_ERROR_NO_SPACE` warning despite ample host disk | The launch still proceeded and the warning was reported. | No minimal anchor was filed, so future recurrence cannot be distinguished from a one-off warning. | Add warning/transient examples to the minimal-anchor guidance without logging every warning. |

The most important aggregate result is the lifecycle gap: at least seven EdgeCourt events describe or correspond to a later product repair, but all 14 anchors remain open because no separate Mend was requested. This is evidence for an explicit verified-closure pilot, not for autonomous mending.

### C.3 Things that worked well across the field threads

The following behaviors reduced friction and should remain:

- JSON stdin safely carried shell-sensitive text without requiring fragile command-line quoting.
- Duplicate recurrence keys produced a non-destructive exit code and explicit `--recur` and `--distinct` alternatives.
- Recurrence records were much cheaper than full narratives.
- Store talkback surfaced prior events and recurrence counts without relying on agent memory.
- The bounded dashboard made corpus orientation substantially cheaper than reading the full stream.
- Session linkage correctly connected records to the active Codex thread.
- The smoke suite covered legacy coercion, lifecycle queries, trap publication, stateless invocation, and hook injection resistance.
- The capture/mend conceptual separation prevented one surprising incident from automatically rewriting project instructions.
- The plugin captured subtle verification errors, including a Playwright project-dependency repetition misunderstanding that was not a crash or syntax error.

### C.4 Unrelated friction that the plugin captured successfully in the prior DiffHound thread

Several incidents in the thread were not plugin defects. They demonstrate the value of the product:

- A browser launcher behaved differently under a sandbox.
- An extension installation raced browser readiness.
- Parallel browser profiles interfered with one another.
- Playwright selectors matched hidden, duplicated, or dynamically renamed controls.
- A process-wait tool reported that a completed process was still running.
- `web-ext` no longer accepted a previously expected placement of a headless flag.
- Comprehensive Playwright journeys exceeded an inherited overall deadline even though the expected UI had already rendered.
- Playwright project dependencies did not inherit repetition in the way the audit initially expected.

The plugin was useful in these cases because it preserved the difference between the prior expectation and the observed contract. Improvements to Friction Diagnostics should not weaken that behavior.

## Appendix D: Interim safe-operating procedure

Until the persistence defects are fixed, agents and maintainers can reduce risk with the following operating procedure.

### D.1 Before filing

1. Run under a restrictive umask:

   ```sh
   umask 077
   ```

2. Resolve the intended events file explicitly. Do not rely on `--repo-root` to route storage:

   ```sh
   events_file="/absolute/repo/.local/reports/friction/events.jsonl"
   ```

3. Create the parent directory privately and verify it is not a symlink:

   ```sh
   events_dir=$(dirname "$events_file")
   mkdir -p "$events_dir"
   chmod 700 "$events_dir"
   test ! -L "$events_dir"
   ```

4. Pre-redact all source references and claims. Do not assume the JSON path will sanitize them.

5. Do not put private conversation content, credentials, customer data, health information, or regulated data into `actual_outcome` merely to satisfy the verbatim requirement. Preserve the minimum evidence needed to understand the divergence.

### D.2 Filing

Use JSON stdin because it is safer for quotes and multiline text, but pass the canonical store explicitly:

```sh
printf '%s' "$payload" |
  sh scripts/report-friction.sh \
    --events-file "$events_file" \
    --from-json -
```

For environments where a stale lock is plausible, use an external deadline:

```sh
timeout 15s sh scripts/report-friction.sh \
  --events-file "$events_file" \
  --from-json payload.json
```

If the deadline expires:

1. Do not immediately delete the lock.
2. Inspect `.report-friction.lock/pid`.
3. Verify whether that exact process is an active writer.
4. If the lock has no valid owner and no writer is active, remove the stale lock directory.
5. Query the store before retrying; the event may already have been appended.

### D.3 After filing

1. Verify the event exists before retrying any ambiguous failure:

   ```sh
   sh scripts/query-friction.sh \
     --events-file "$events_file" \
     --date "$(date -u +%Y-%m-%d)" \
     --format json
   ```

2. Verify modes:

   ```sh
   chmod 600 "$events_file"
   chmod 600 "$(dirname "$events_file")/INDEX.md" 2>/dev/null || true
   ```

3. Prefer the bounded `INDEX.md` or aggregate reports before loading the full open corpus.

4. Avoid `--add-tags` if strict append-only provenance matters. Record the desired metadata separately until amendment records exist.

5. When the same task fixed the source, note the verification externally or run an explicitly authorized resolution command; otherwise remember that “open” means no formal resolution record, not necessarily unresolved product behavior.

### D.4 Rendering on unsupported hosts

The packaged table renderer is Linux-specific. Where the binary is unavailable, prefer Markdown or list output rather than trying to make the table renderer work through ad hoc installation:

```sh
sh scripts/render-summary.sh \
  --events-file "$events_file" \
  --date-from "$(date -u +%Y-%m-%d)" \
  --output-format markdown
```

The compatibility metadata should eventually state all required dependencies explicitly: Linux for the packaged renderer, POSIX shell, Python 3, and `jq`.

## Appendix E: Proposed CLI contract

This appendix separates immediate mechanics from pilot-only ideas. The exact command names may change, but the behavioral contract should be explicit and testable. A new native executable is not a prerequisite; existing scripts may implement this contract first.

### E.1 Canonical writer

```text
friction-store append
  --events-file PATH
  [--repo-root PATH]
  [--idempotency-key STRING]  # deferred until receipt fault tests justify it
  --json PATH|-
```

Success output should be compact and machine-readable:

```json
{"ok":true,"committed":true,"event_id":"evt-0042","events_file":"/absolute/path/events.jsonl","index_state":"rebuilt"}
```

If append succeeds but index rebuilding fails:

```json
{"ok":true,"committed":true,"event_id":"evt-0042","events_file":"/absolute/path/events.jsonl","index_state":"stale","warning":"index rebuild failed; run friction-store rebuild-index"}
```

The process should exit successfully because the canonical write committed. Derived-view failure must not make the write ambiguous.

If the same idempotency key is retried:

```json
{"ok":true,"committed":false,"duplicate_request":true,"event_id":"evt-0042","events_file":"/absolute/path/events.jsonl"}
```

### E.2 Query

```text
friction-store query
  --events-file PATH
  [--kind KIND]
  [--state STATE]
  [--id EVENT_ID]
  [--session-ref SESSION_REF]
  [--key KEY]
  [--source-kind KIND]
  [--source-text TEXT]
  [--after TIMESTAMP]
  [--before TIMESTAMP]
  [--limit N]
  [--cursor TOKEN]
  [--fields CSV]
  [--format jsonl|json|md]
  [--all]
```

Recommended defaults:

- Newest first.
- Limit 50 for human/agent output.
- Streaming JSONL for large results.
- `--all` required to remove the bound.
- A returned cursor when more results exist.
- Store-qualified identities whenever more than one physical store is queried.

### E.3 Resolution

```text
friction-store resolve
  --events-file PATH
  --resolves EVENT_ID[,EVENT_ID...]
  --disposition mended|mitigated|external|not_actionable
  --hazard-active true|false
  --action TEXT
  [--refs-json PATH|-]
  [--verification TEXT]
  [--residual-risk TEXT]
  [--idempotency-key STRING]
```

The command should be allowed in two contexts:

- Immediate factual recording after the active task already hardened and verified the source.
- Deliberate cluster closure during Friction Mend.

It should not itself claim that a source was fixed; it records a resolution the agent has already verified. This richer contract is a pilot, not part of the Phase 0 schema migration. For non-external mends, references and verification should be required. For external hazards, a reason and normally `hazard_active=true` should be required.

### E.4 Relationship

This command is a deferred pilot. Improve recurrence guidance before adding a canonical relationship record kind.

```text
friction-store relate
  --events-file PATH
  --from EVENT_ID
  --to EVENT_ID
  --kind related_to|caused_by|duplicate_of
  [--note TEXT]
```

This is append-only provenance. It does not rewrite either event.

### E.5 Metadata amendment

This command is deferred until audit-grade immutability is a settled requirement. The immediate repair may instead state the current contract honestly: narrative fields are immutable, while tag/alias metadata is atomically mutable.

```text
friction-store amend
  --events-file PATH
  --event EVENT_ID
  --add-tags TAG[,TAG...]
  [--note TEXT]
```

The effective tag set is derived from the original event plus later amendments. Existing event lines never change.

### E.6 Doctor

```text
friction-store doctor
  --events-file PATH
  [--repair-tail-preview]
  [--check-permissions]
  [--check-lock]
  [--check-derived-views]
```

Doctor should detect:

- Invalid JSON lines.
- Partial final records.
- Duplicate identifiers.
- Wrong permissions.
- Symlinked paths.
- Stale locks.
- Store metadata that disagrees with physical location.
- Schema-version incompatibility.
- Stale or missing derived views.

Repair must be previewed. Damaged bytes should be quarantined with user-only permissions and never silently discarded.

### E.7 Error format

Errors should remain short and actionable:

```text
error: friction store lock did not clear within 15s
hint: run friction-store doctor --events-file /path/events.jsonl --check-lock
```

No normal error should print an entire payload, stack trace, authorization header, or source claim.

## Appendix F: Proposed record examples

These examples illustrate behavior, not accepted schema changes. In particular, the object-valued evidence examples below are exploratory. The smallest justified copy change keeps `actual_outcome` as a string and defines it as the best available primary evidence: exact text when available, otherwise a measurement, state transition, explicit absence, uncertainty statement, or labeled firsthand observation.

### F.1 Textual tool surprise

```json
{
  "kind": "friction",
  "actual_outcome": {
    "type": "text",
    "value": "error: unknown option '--headless'",
    "redacted": false
  },
  "expected_outcome": "The documented top-level --headless flag would be accepted.",
  "reading": "I used the command form shown by the prior tool version. The parser rejected that placement before the browser started.",
  "decision": "I checked current help, moved the browser flag behind the argument-forwarding option, and reran successfully.",
  "pivot_information": {
    "value": "The current help places browser arguments behind --arg.",
    "location": "web-ext run --help"
  },
  "prediction_bases": [
    {
      "kind": "memory",
      "ref": "prior web-ext invocation",
      "claim": "--headless is a top-level run flag"
    }
  ],
  "workflow_impact": "noisy",
  "consequence": {
    "observed": "lost_time",
    "severity": "low"
  }
}
```

### F.2 Non-text visual surprise

```json
{
  "kind": "friction",
  "actual_outcome": {
    "type": "observation",
    "value": "At 200% zoom, the primary action overlapped the status panel and could not be clicked.",
    "evidence_refs": ["screenshot:popup-200-percent.png"],
    "certainty": "firsthand"
  },
  "expected_outcome": "The popup would remain usable at browser text zoom up to 200%.",
  "reading": "The layout used fixed vertical dimensions, and I assumed the existing responsive width rules also covered text growth. The overlap appeared only after zooming.",
  "decision": "I captured the screenshot, stopped the release check, and opened the layout constraint for investigation.",
  "pivot_information": {
    "value": "The rendered control heights at 200% zoom exceed the fixed container height.",
    "location": "browser rendering measurement"
  },
  "prediction_bases": [
    {
      "kind": "assumption",
      "ref": "responsive layout coverage",
      "claim": "responsive width behavior also preserves vertical usability under text zoom"
    }
  ],
  "workflow_impact": "blocked",
  "consequence": {
    "observed": "user_visible_accessibility_defect",
    "severity": "high"
  }
}
```

### F.3 Research surprise with coupled pivot information

```json
{
  "kind": "friction",
  "actual_outcome": {
    "type": "measurement",
    "value": "The intervention group improved on the proxy metric but declined on the preregistered primary outcome.",
    "evidence_refs": ["analysis:table-4", "protocol:primary-outcome"]
  },
  "expected_outcome": "Improvement in the proxy would correspond to improvement in the primary outcome.",
  "reading": "The proxy had tracked the primary outcome in earlier cohorts. I treated that historical correlation as stable under this intervention.",
  "decision": "I withheld the success claim and reran the analysis by cohort and measurement timing.",
  "pivot_information": {
    "value": [
      "The intervention directly affects the proxy's measurement process.",
      "The historical relationship was estimated in cohorts without this intervention."
    ],
    "location": ["measurement protocol", "cohort analysis"]
  },
  "prediction_bases": [
    {
      "kind": "observation",
      "ref": "historical cohort analysis",
      "claim": "proxy and primary outcome moved together"
    }
  ],
  "workflow_impact": "continued",
  "consequence": {
    "potential": "false efficacy conclusion",
    "severity": "high"
  }
}
```

### F.4 Relationship instead of recurrence

```json
{
  "kind": "relationship",
  "relation": "related_to",
  "from": "01J-EVENT-B",
  "to": "01J-EVENT-A",
  "reason": "Both appeared as ambiguous accessible-name failures, but one was caused by a hidden duplicate control and the other by a dynamic label mutation. The same preventive fact would not have prevented both."
}
```

### F.5 Immediate verified resolution

```json
{
  "kind": "resolution",
  "resolves": ["01J-EVENT-A"],
  "action": "The source instruction was corrected to show the accepted flag placement.",
  "verification": "The documented command was executed from a clean environment and completed successfully.",
  "ref": "path:docs/tooling.md",
  "resolution_scope": "source_hardened"
}
```

### F.6 Append-only metadata amendment

```json
{
  "kind": "amendment",
  "amends": "01J-EVENT-A",
  "add_tags": ["cli", "version-drift"],
  "note": "Tags added during corpus review; original event remains unchanged."
}
```

## Appendix G: File-level implementation backlog

This backlog is intentionally specific. Exact line numbers will move as implementation proceeds.

### G.1 Capture skill

File: `plugins/friction-diagnostics/skills/friction-diagnostics/SKILL.md`

Changes:

1. Rewrite the description using the repository's numbered trigger convention.
2. Remove “review, mend, or distill friction.”
3. Add an explicit negative route to Friction Mend.
4. Replace mandatory verbatim evidence with best available primary evidence and conditional quotation.
5. Replace “trusted that betrayed you” with neutral prediction-basis language.
6. Permit the smallest coupled pivot information set.
7. Clarify that redaction precedes persistence even when verbatim evidence exists.
8. Make capture depth proportional to consequence and policy relevance.
9. Replace the mandatory full summary with compact disclosure plus opt-in full rendering.
10. Add a direct reference index for field rubrics, logging/storage, and integration.
11. Correct the append-only claim or remove mutable tag operations.
12. Document dependencies and the single-host storage boundary accurately.
13. Make user corrections about scope, intent, completion, or factual claims explicit surprise candidates.
14. Clarify that a minimal anchor is a concise full event unless a reduced record type is deliberately introduced later.

Acceptance criteria:

- Capture and Mend have mutually exclusive explicit prompt triggers.
- A non-text observation can satisfy the contract without fabricated quotation.
- An ordinary task with one filing ends with at most one compact line unless the user requested friction details.
- Every active reference is directly reachable from the skill.

### G.2 Mend skill

File: `plugins/friction-diagnostics/skills/friction-mend/SKILL.md`

Changes:

1. Qualify “review” as review of an existing friction corpus, backlog, dashboard, or traps file.
2. Allow “left open pending named evidence” as an honest result.
3. Allow “no change recommended” without forcing `wontfix` when evidence is insufficient.
4. Target the earliest controllable surface, not necessarily `sources[].ref`.
5. Define recurrence as shared preventive information or control.
6. Document relationship and duplicate-anchor consolidation when available.
7. Treat recurrence share and event volume as descriptive metrics, not success targets.
8. Orient from bounded dashboard and cluster hints before querying the full corpus.
9. Distinguish factual verified closure during ordinary work from explicit corpus-wide mending.
10. Require a real end-to-end Mend pilot before claiming behavioral effectiveness.

Acceptance criteria:

- “Review this plugin” does not activate Mend.
- “Review the open friction backlog” does activate Mend.
- A cluster can remain open with a named evidence requirement.
- A source that was accurate but misread can be mended through placement, prompt, check, or decision-rule changes rather than being labeled incorrect.

### G.3 Common helpers

File: `plugins/friction-diagnostics/skills/friction-diagnostics/scripts/_common.sh`

Changes:

1. Add one canonical storage-target resolver accepting explicit repo root and events-file override.
2. Canonicalize and validate paths.
3. Split non-mutating read discovery from write/create resolution.
4. Prefer an existing friction store across `.local*`; reject ambiguous creation rather than selecting lexicographically.
5. Add restrictive-mode helpers.
6. Add one recursive redaction implementation or route all redaction through the canonical writer.
7. Add one bounded lock helper shared by capture, index, resolution, and trap publication.
8. Add one append-order lifecycle reducer keyed by canonical physical store plus event ID.
9. Remove ad hoc JSON extraction where a real parser is available.
10. Add dependency checks with concise hints.
11. Separate local single-host behavior from future shared adapters.

Acceptance criteria:

- CWD and explicit repository root can differ without metadata/storage disagreement.
- Read-only queries create no files or directories.
- Two stores containing the same local event ID cannot affect each other's lifecycle.
- Every created canonical or temporary artifact is user-only.
- One lock implementation passes live, dead, missing-owner, malformed-owner, and timeout tests.

### G.4 Capture writer

File: `plugins/friction-diagnostics/skills/friction-diagnostics/scripts/report-friction.sh`

Changes:

1. Replace JSON-to-shell `eval` with argument-safe structured transfer.
2. Sanitize all source objects after parsing.
3. Redact malformed-input diagnostics.
4. Make quarantine explicit or bounded and private.
5. Validate the existing store before append.
6. Preserve the current per-store identifier contract unless a measured collision remains after locking fixes.
7. Add idempotency only if receipt fault tests show remaining ambiguity.
8. Emit the committed receipt immediately after append.
9. Treat index/talkback failure as a warning after commit.
10. Register every temporary file in cleanup traps.
11. Replace tag/alias rewrites with append-only amendments or narrow the immutability claim.
12. Add an explicit compact-output mode for agent callers.
13. Require a nonblank belief claim for every full-event source.
14. Make JSON input validation and exit codes match the documented contract.
15. Rename `open clusters` talkback to disclose its two-sighting threshold and assert that the newly appended anchor is lifecycle-visible.

Acceptance criteria:

- Direct flags and JSON stdin produce identical sanitized records.
- A post-append index failure still returns the committed event ID.
- If idempotency is implemented, retrying the same idempotency key produces no second record.
- Killing the process at every fault-injection point leaves either no record or one valid committed record, never an ambiguous corrupt tail.

### G.5 Resolution writer

File: `plugins/friction-diagnostics/skills/friction-mend/scripts/record-resolution.sh`

Changes:

1. Use the canonical writer and lock helper.
2. Sanitize `ref` and every other free-text field.
3. Canonicalize the physical events path and derive repository ownership from the store, not the caller's current directory.
4. Support primary JSON stdin for shell-sensitive actions and references.
5. Support an explicit pilot for immediate verified resolution provenance.
6. Emit receipt before derived queries and index work.
7. Pilot structured disposition, hazard-active state, references, verification, and residual risk.
8. No-op an unchanged duplicate resolution; allow a legitimate re-close after a later recurrence.

Acceptance criteria:

- A resolution cannot be duplicated by an ambiguous retry.
- Resolution recording cannot expose a token-shaped value in `ref`.
- Resolving another repository's store from an arbitrary current directory records the owning repository.
- A recurrence after resolution reopens; a later resolution closes it again.
- Existing friction and recurrence records remain byte-identical.

### G.6 Query and reports

Files:

- `plugins/friction-diagnostics/skills/friction-diagnostics/scripts/query-friction.sh`
- `plugins/friction-diagnostics/skills/friction-diagnostics/scripts/generate-report.sh`
- `plugins/friction-diagnostics/skills/friction-diagnostics/scripts/render-summary.sh`

Changes:

1. Use the one store-qualified, append-order lifecycle reducer.
2. Add `--id`, `--session-ref`, lifecycle, resolver, source-kind, and source-text filters.
3. Correct repository/store aggregation and report both counts.
4. Add limit, cursor, fields, summary-only, and explicit-all controls after the basic lifecycle fixes.
5. Stream large JSONL results rather than materializing them in shell variables when scale tests justify it.
6. Escape Markdown table content.
7. Pass timestamps as Python arguments.
8. Make session summaries use the current session when available and label time-only fallbacks honestly.
9. Keep dashboard section bounds and add tests proving them at scale.
10. Add an integrity report for malformed records, duplicate IDs, dangling pointers, path mismatches, and trap drift.
11. Clarify which report types are intentionally unbounded.

Acceptance criteria:

- Default query output remains within a documented bound.
- A 10,000-record store can be oriented without loading the full corpus.
- Crafted record text cannot break Markdown structure or become executable code.

### G.7 Cluster hints

File: `plugins/friction-diagnostics/skills/friction-mend/scripts/cluster-hints.sh`

Changes:

1. Remove common stop words.
2. Weight distinctive terms rather than counting raw overlap.
3. Include source and pivot similarity.
4. Bound event identifiers per cluster.
5. Return total counts and truncation markers.
6. Explain why each candidate was suggested.
7. Fail loudly on malformed stores.
8. Show pairwise evidence as well as connected components so transitive overlap is visible.
9. Replace quadratic comparison when scale tests justify it.

Acceptance criteria:

- Generic shared words cannot create a candidate cluster.
- The nearly identical child-language events are suggested as duplicates.
- Broad Playwright locator symptoms are not automatically treated as the same root cause.

### G.8 Trap publisher

File: `plugins/friction-diagnostics/skills/friction-mend/scripts/update-traps.sh`

Changes:

1. Add locked `--check`, `--upsert`, and `--remove-key` operations.
2. Make whole-file replacement explicit with `--replace-all`.
3. Validate keys, anchors, active state, sightings, latest occurrence, and uniqueness against the canonical store.
4. Reject query failure as unknown rather than converting it to zero open events.
5. No-op unchanged bodies and print added/changed/removed keys.
6. Change “auto-distilled” to “tool-published”; model judgment composes the text.

Acceptance criteria:

- A scoped Mend cannot erase unrelated traps.
- Concurrent clear and publication operations serialize.
- Invalid, duplicate, stale, or mismatched trap pointers are rejected.
- Active external hazards may remain while verified mended hazards are removed.

### G.9 Schema

File: `plugins/friction-diagnostics/skills/friction-diagnostics/friction-event-schema.json`

Changes:

1. Decide whether it is an executable schema or a field catalog.
2. If executable, add standard required fields and per-kind discriminated constraints.
3. Require at least one prediction basis for full friction records unless a documented exception applies.
4. Define additional-properties behavior.
5. Add relationship and amendment kinds only after eval validation.
6. Preserve a tolerant legacy-reader contract.
7. Generate or validate hardcoded enums from the canonical schema.

Acceptance criteria:

- A standard Draft 2020-12 validator rejects `{}`.
- Every emitted new record validates.
- Legacy records remain readable without pretending they satisfy the newest writer contract.

### G.10 CI and local command surface

Files:

- `.github/workflows/ci.yml`
- `justfile`
- `packaging/skills.toml`
- `scripts/package_skills.py`

Changes:

1. Add `test-friction-diagnostics` to the local command surface.
2. Include it in normal test or CI verification.
3. Watch the complete plugin tree, shared vendored sources, packaging metadata, and renderer.
4. Run plugin round-trip validation for both hosts when the plugin changes.
5. Add shell/static checks appropriate to the declared POSIX contract.
6. Keep renderer packaging checks separate from behavioral plugin selection.

Acceptance criteria:

- Changing capture writer, Mend writer, schema, hook, reference, manifest, or test selects the plugin verification job.
- `just test-friction-diagnostics` reproduces the CI behavior locally.
- A change cannot receive a green plugin check without running the integrated lifecycle suite.

### G.11 Plugin metadata

File: `plugins/friction-diagnostics/.codex-plugin/plugin.json`

Changes:

1. Advertise write capability because the plugin's primary behavior persists local files.
2. Keep the default prompt focused on capture, not mending.
3. Ensure long and short descriptions reflect the capture/mend split.
4. Keep Codex and Claude descriptions semantically aligned through conversion tests.

Acceptance criteria:

- Plugin UI metadata does not describe a write-producing plugin as read-only.
- Capture and Mend remain separately discoverable.

## Appendix H: Decision log for recommendations

### H.1 Recommendations supported by direct implementation evidence

These can proceed without further product discovery:

- Append-order lifecycle reopening and reclosing.
- Store-qualified cross-store lifecycle identity.
- User-only permissions.
- Uniform sanitization.
- Correct repository routing.
- Non-mutating read discovery and canonical `.local*` store reuse.
- Bounded stale-lock behavior.
- Committed receipt ordering.
- Pre-append integrity validation.
- CI selection for the complete plugin.
- Removal of data interpolation into executable source.
- Resolution of the append-only contradiction.
- Direct links to active references.
- Session-aware summary labeling.
- Correct repository/store report aggregation.

### H.2 Recommendations supported by this corpus but needing a pilot

- Immediate verified resolution during ordinary tasks.
- Distinguishing recurrence from related symptoms.
- A duplicate-anchor relationship.
- Structured Mend dispositions and hazard-active state.
- Scoped, store-validated trap publication.
- Source/pivot/contradiction-aware clustering.
- Workflow disruption separated from consequence.
- Proportional narrative depth.
- Compact default disclosure.

These should be tested against existing events before becoming mandatory schema changes.

### H.3 Recommendations supported mainly by adversarial cross-domain reasoning

- Object-valued non-text evidence.
- Coupled pivot information.
- Physical-world and creative-work examples.
- Shared-service or MCP storage adapters.
- Team-level actor and workspace provenance.

These are not empirically proven by the current mostly software-oriented corpus. The first three should be validated with real non-code use before locking the ontology. The last two solve a separate distributed-product problem and are not required for domain-general cognition.

### H.4 Explicitly rejected directions

- Replacing the plugin with a generic issue tracker.
- Filing every command failure.
- Automatically rewriting instructions after one event.
- Automatically merging events based on similarity.
- Making a remote service mandatory.
- Building MCP, database, or service adapters before a real multi-host requirement exists.
- Replacing the current per-store IDs solely to solve a read-side namespacing bug.
- Requiring every proposed new field in the first migration.
- Treating higher event volume or recurrence share as a success metric by itself.
- Hiding all friction logging from users; compact disclosure remains appropriate.

## Appendix I: Reproduction and audit commands

The following commands identify the audited revision and reproduce the non-destructive checks used in the final pass. Controlled fault probes used disposable repositories and stores; their observed outcomes are described in the findings rather than embedded as reusable destructive scripts.

### I.1 Revision and corpus counts

```sh
git rev-parse HEAD

jq -r '.kind // "friction"' \
  /home/rashino/repos/EdgeCourt/.local/reports/friction/events.jsonl |
  sort | uniq -c

jq -r '.kind // "friction"' \
  /home/rashino/repos/DiffHound/.local/reports/friction/events.jsonl |
  sort | uniq -c

stat -c '%a %n' \
  /home/rashino/repos/EdgeCourt/.local/reports/friction \
  /home/rashino/repos/EdgeCourt/.local/reports/friction/events.jsonl
```

### I.2 Integrated behavior and host-package structure

```sh
bash plugins/friction-diagnostics/skills/friction-diagnostics/tests/smoke-posix.sh

python3 scripts/plugin_port.py validate \
  plugins/friction-diagnostics --host codex --no-external

python3 scripts/plugin_port.py validate \
  plugins/friction-diagnostics --host claude --no-external
```

Both internal validations reported `status: success` with no warnings. `--no-external` is material: this does not claim that the unavailable native host CLIs were exercised.

### I.3 Skill-auditor structural checks

```sh
AUDITOR=/home/rashino/.codex/plugins/cache/agent-tooling/skill-auditor/1.0.0/skills/skill-auditor/scripts
ROOT=plugins/friction-diagnostics/skills

for skill in friction-diagnostics friction-mend; do
  "$AUDITOR/frontmatter_check.sh" "$ROOT/$skill"
  "$AUDITOR/reference_check.sh" "$ROOT/$skill"
  "$AUDITOR/script_sanity.sh" "$ROOT/$skill"
  "$AUDITOR/spec_check.sh" "$ROOT/$skill"
done
```

Observed result:

- Both frontmatter checks passed.
- Both script-sanity checks passed with one large-script-surface warning each.
- Both specification checks passed with minor warnings.
- Mend's reference check passed.
- Capture's reference check failed because `references/integration.md` and `references/logging-spec.md` are active but not linked from `SKILL.md`.

### I.4 Vendored-copy equality

```sh
sha256sum \
  plugins/friction-diagnostics/skills/friction-diagnostics/scripts/_common.sh \
  plugins/friction-diagnostics/skills/friction-mend/scripts/_common.sh \
  plugins/friction-diagnostics/skills/friction-diagnostics/scripts/query-friction.sh \
  plugins/friction-diagnostics/skills/friction-mend/scripts/query-friction.sh \
  plugins/friction-diagnostics/skills/friction-diagnostics/scripts/generate-report.sh \
  plugins/friction-diagnostics/skills/friction-mend/scripts/generate-report.sh \
  plugins/friction-diagnostics/skills/friction-diagnostics/scripts/build-index.sh \
  plugins/friction-diagnostics/skills/friction-mend/scripts/build-index.sh \
  plugins/friction-diagnostics/skills/friction-diagnostics/friction-event-schema.json \
  plugins/friction-diagnostics/skills/friction-mend/friction-event-schema.json
```

Each declared capture/Mend pair was byte-identical at the audited commit. That is a current success and a future drift risk; it is not evidence that both packaged copies are independently exercised.

### I.5 CI change-selection probe

```sh
for item in \
  plugins/friction-diagnostics/skills/friction-diagnostics/SKILL.md \
  plugins/friction-diagnostics/skills/friction-diagnostics/scripts/report-friction.sh \
  plugins/friction-diagnostics/skills/friction-mend/scripts/record-resolution.sh \
  plugins/friction-diagnostics/hooks/hooks.json \
  plugins/friction-diagnostics/.codex-plugin/plugin.json \
  crates/render-table/src/main.rs \
  plugins/friction-diagnostics/skills/friction-diagnostics/tests/smoke-posix.sh \
  packaging/skills.toml
do
  printf '%s\n' "$item" |
    python3 scripts/package_skills.py matches-changed-files \
      --skill friction_render_table \
      --include-tests \
      --changed-files-file /dev/stdin
done
```

The selector returned `false` for the capture skill, capture writer, Mend writer, hook, and Codex manifest. It returned `true` for the render-table crate, the friction smoke test itself, and `packaging/skills.toml`. This directly supports the CI path-coverage finding.

### I.6 Field-corpus inspection

```sh
sh plugins/friction-diagnostics/skills/friction-diagnostics/scripts/query-friction.sh \
  --events-file /home/rashino/repos/EdgeCourt/.local/reports/friction/events.jsonl \
  --open --kind friction --format json

sh plugins/friction-diagnostics/skills/friction-mend/scripts/cluster-hints.sh \
  --events-file /home/rashino/repos/EdgeCourt/.local/reports/friction/events.jsonl
```

The raw corpus remains the evidence source. The report does not require the reader to trust generated prose as a substitute for it.
