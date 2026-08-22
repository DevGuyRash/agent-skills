# Friction Diagnostics: Foundational Improvement Report

**Artifact ID:** `8731ddc8-0958-43b5-bcf1-39cce80e38ae`

**Recreated:** 2026-07-14

**Status:** Self-contained technical audit and implementation proposal

**Repository:** `agent-tooling`

**Target:** `plugins/friction-diagnostics`

**Evidence baseline:** commit `ff3e4f2bc2b634692f8ecc07549bf7bffaf253b9`, plugin version `5.1.3`

**Scope note:** This is the collision-safe reconstruction of the report produced from the DiffHound development thread and a direct audit of Friction Diagnostics. It does not depend on the overwritten, unsuffixed report. The UUID is part of the filename and document metadata so another agent can create a different report without silently replacing this artifact.

## Technical summary

Friction Diagnostics has the right foundational idea: preserve the moment reality contradicts a prediction, together with the evidence that supported the prediction and the information that would have changed the decision. That is more useful than a conventional error log because it records the failed model behind the error, not merely the visible symptom.

The concept should be retained. The immediate-capture versus later-mending split is especially strong. During the DiffHound build, the plugin successfully captured surprises involving browser automation, authenticated third-party pages, extension behavior, UI affordances, Playwright workflows, console inspection, packaging, data contracts, test tooling, and agent coordination. Cheap recurrence records also prevented repeated failures from requiring complete narratives each time.

The implementation is not yet safe enough to call a universal or audit-grade foundation. The largest concerns are concrete:

1. JSON source references and claims can bypass sanitization.
2. The primary event stream can be created with mode `0644`, exposing potentially sensitive reasoning to other local users.
3. Malformed-input diagnostics and quarantine behavior can preserve or print raw secrets.
4. `--repo-root` can record repository B while physically writing into repository A.
5. A stale or incomplete lock directory can block forever.
6. The event append happens before derived index, talkback, and receipt work, so a committed record can be reported as a failed command and retried as a duplicate.
7. The store is described as append-only while `--add-tags` and `--add-aliases` rewrite existing records.
8. Sequential IDs are allocated from line-oriented assumptions that become fragile around corruption or partial writes.
9. Stored values reach executable contexts through Python-source interpolation and shell `eval`.
10. Capture and Mend trigger descriptions overlap.
11. The mandatory evidence language assumes every surprise has verbatim text, which excludes valid visual, physical, behavioral, and non-occurrence evidence.
12. “What betrayed you” incorrectly assumes the source was at fault rather than stale, incomplete, ambiguous, or reasonably misread.
13. Mandatory full filing summaries create visible friction in unrelated user-facing work.
14. “Open” means “no formal resolution record,” not necessarily “the product incident remains broken.”
15. Recurrence can incorrectly merge events that share a symptom but not a preventable cause.
16. Queries and reports are unbounded, while the normal Mend entry point asks for the entire open corpus.
17. The schema looks like JSON Schema Draft 2020-12 but uses nonstandard applicability metadata, so a standard validator does not enforce the intended record contract.
18. Corruption handling differs across readers and writers.
19. The substantial smoke suite is not guaranteed to run for changes to the whole plugin.
20. Trigger-prompt artifacts are stored but not executed as behavioral evaluations.

The right response is evolutionary rather than architectural overreach. Preserve the cognitive kernel and repair the local system first. The highest-value delivery slice is a single deterministic persistence implementation with recursive redaction, user-only permissions, canonical routing, bounded locks, pre-append integrity validation, an unambiguous committed receipt, consistent lifecycle reduction, and CI that follows every plugin change. Then tighten the skill boundaries and evidence language. Richer relationships, consequence fields, alternative storage adapters, and distributed operation should be piloted only when real evidence justifies them.

### Priority decisions

| Priority | Recommendation | Why now |
| --: | --- | --- |
| P0 | Sanitize every persisted string and every diagnostic path | A controlled probe preserved token-shaped content in JSON source fields. |
| P0 | Enforce `0700` directories and `0600` files | A controlled probe created the canonical stream as `0644` under a common umask. |
| P0 | Make explicit repository roots control physical routing | Current behavior can make recorded provenance disagree with storage reality. |
| P0 | Replace infinite lock waits with bounded, inspectable ownership | A lock directory without a usable PID required an external timeout. |
| P0 | Treat append as a visible commit and make derived work recoverable | A later failure can otherwise invite a duplicate retry. |
| P0 | Remove executable interpolation and `eval` from data paths | Stored or user-provided values should remain data. |
| P0 | Make the smoke suite unavoidable for plugin changes | Existing tests cannot protect code paths when change selection skips them. |
| P1 | Make Capture and Mend trigger ownership disjoint | Current descriptions both claim review and mending language. |
| P1 | Generalize evidence to “best available primary evidence” | Verbatim text is not available for every valid surprise. |
| P1 | Use neutral “prediction bases” language | A source can be correct even when an inference was too strong. |
| P1 | Default to compact filing disclosure | Full renderer output can dominate unrelated answers. |
| P1 | Distinguish unmended learning from an unhandled incident | “Open” currently carries both meanings. |
| P1 | Add bounded query defaults and progressive Mend discovery | Full-corpus materialization already created avoidable context cost. |
| Pilot | Add append-only relations and metadata amendments | The need is credible, but the ontology should be tested on real clusters first. |
| Pilot | Separate workflow disruption from consequence | The distinction matters, but mandatory consequence taxonomy could create new ceremony. |
| Defer | MCP, database, or shared-service persistence | No demonstrated requirement justifies this complexity yet. |

## 1. What the plugin is and why it matters

Friction Diagnostics is intended to capture genuine surprise: reality behaves differently from what the agent predicted, and preserving the divergence would change how a future session works.

That gate deliberately excludes ordinary failures. A test written to fail before implementation is not friction. A deliberately invalid input is not friction. A known failure path exercised by a probe is not friction. Routine task status is not friction. Those outcomes match the model held before the action.

A useful friction event contains six kinds of information:

- What actually happened.
- What was expected.
- What supported that expectation.
- How the reporter interpreted the situation before hindsight corrected the model.
- What response the reporter made.
- What smallest information unit would have changed that response.

The last item—pivot information—is central. It converts an anecdote into an upstream design question: where could the missing fact, affordance, instruction, guard, or probe have appeared earlier?

The plugin has two deliberately different modes:

- **Capture** preserves evidence at the moment of divergence, before the original mental model disappears.
- **Mend** reviews accumulated records, identifies common causes, repairs misleading artifacts or missing controls, records the resolution, and distills active hazards into a bounded `known-traps.md` view.

This separation should remain. Immediate capture protects epistemic fidelity. Delayed mending protects against rewriting a system around a single noisy incident.

The local implementation stores records in a repository-scoped JSONL stream, creates a bounded `INDEX.md`, and can publish a bounded `known-traps.md`. Record kinds include full friction anchors, cheap recurrence pointers, and later resolutions.

## 2. Scope and evidence

This report combines direct source inspection, controlled probes, committed test execution, and field experience from the DiffHound extension build.

### 2.1 Files inspected

The audit covered the whole shipped plugin surface relevant to capture and mending:

- `plugins/friction-diagnostics/skills/friction-diagnostics/SKILL.md`
- `plugins/friction-diagnostics/skills/friction-mend/SKILL.md`
- Both copies of `friction-event-schema.json`
- `references/logging-spec.md`
- `references/integration.md`
- `references/examples.md`
- `references/mend-playbook.md`
- Capture and Mend shell scripts
- Capture and Mend manifests
- Host hooks and plugin metadata
- Trigger prompts and other eval artifacts
- `tests/smoke-posix.sh`
- Repository `justfile` and CI change-selection logic

### 2.2 Field corpus

At the audited snapshot, the DiffHound corpus contained 33 records:

- 21 full friction anchors.
- 12 recurrence records.
- 0 formal resolution records.

The corpus covered browser-extension development, console and GUI testing, authenticated external pages, Playwright behavior, backend-independent tests, selector design, packaging, agent handoffs, and one communication-scope correction. This is enough to show that the core model works across multiple forms of software product work. It is not enough to claim empirical validation for every writing, research, creative, organizational, or physical-world domain.

### 2.3 Verification performed

The following checks were completed during the audit:

- All 18 committed POSIX smoke scenarios passed.
- Skill frontmatter checks passed.
- Script sanity checks passed.
- Specification checks passed with minor warnings.
- Internal Codex and Claude package validation passed.
- Twelve concurrent distinct filings produced twelve valid records with unique identifiers.
- A stale-lock probe did not recover and had to be terminated with an external timeout.
- A sanitization probe showed that synthetic secret-shaped content survived in JSON `sources[].ref` and `sources[].claim`.
- A permissions probe created `events.jsonl` as mode `0644` under umask `0022`.
- A repository-routing probe executed inside repository A with `--repo-root` set to repository B; the record was stored under A while claiming B.
- The earlier open-corpus query produced roughly 41 KB of JSON, while the bounded index was roughly 4.4 KB.
- The reference checker found active shipped references that the main skill did not link.

### 2.4 Evidence labels used in this report

- **Observed** means a behavior was reproduced, a committed test was run, or code directly establishes it.
- **Inferred** means the recommendation follows from observed behavior but has not yet been validated as a product change.
- **Adversarial** means a cross-domain or edge-case review found a plausible limitation without a real corpus proving its frequency.

This report does not claim that a real end-to-end Mend cycle was validated. The field corpus had no formal resolutions, and no later session was observed reading a newly published trap and demonstrably changing behavior.

## 3. What should be preserved

### 3.1 The surprise gate is correctly framed

“Did reality diverge from a prediction, and would this record change future behavior?” is a high-signal gate. It prevents the product from becoming a generic error logger.

### 3.2 Expected failures remain excluded

The explicit exclusion of red tests, engineered probes, and deliberate error paths is essential. Capturing them would bury genuine model failures in normal verification traffic.

### 3.3 Point-of-divergence capture preserves the prior model

Once the correct explanation is known, people and agents reconstruct the earlier expectation too cleanly. Capturing before the model updates preserves what was genuinely believed.

### 3.4 Pivot information makes records actionable

The record asks what would have changed the response, not just what caused the visible failure. That points directly toward better instructions, affordances, checks, or probes.

### 3.5 Cheap recurrence reduces ceremony

The DiffHound corpus contained 12 recurrence records. Requiring a full narrative for every repeat would have been wasteful and likely would have suppressed capture.

### 3.6 Capture and Mend are conceptually distinct

The architecture correctly separates evidence preservation from later convergence. The problem is trigger wording overlap, not the separation itself.

### 3.7 Bounded feed-forward artifacts are the right shape

The complete JSONL stream can remain precise and historical. The dashboard and trap view should remain intentionally small enough for future agents to read cheaply.

### 3.8 Append-only resolution provenance is valuable

A later resolution should not rewrite the original prediction. Keeping both facts allows a reviewer to see what was believed, what changed, and how the upstream source was hardened.

### 3.9 JSON through stdin worked well

The primary JSON-stdin path safely handled quotes, backticks, multiline strings, and shell-sensitive text in normal operation. That path should remain the preferred user interface after its sanitizer and validation boundaries are fixed.

### 3.10 Duplicate soft stops and recurrence alternatives worked

When the writer detected a likely duplicate, it offered recur-versus-distinct choices instead of silently merging records. This is safer than automatic semantic deduplication.

### 3.11 Store talkback is directionally useful

Briefing the filer on related events, recurrence history, and traps immediately after a write reduces dependence on agent memory. It should remain, but only after the commit receipt and with clearer labels.

## 4. Detailed findings and requested changes

### 4.1 JSON source fields bypass uniform sanitization

**Evidence:** Narrative fields pass through sanitization after JSON ingestion, but source objects from the JSON path are validated, truncated, serialized, and persisted without applying the same recursive transformation to every contained string. The direct flag path behaves differently. A controlled probe preserved synthetic token-shaped content in `sources[].ref` and `sources[].claim`.

**Why it matters:** Source fields are likely to contain URLs, headers, file paths, API excerpts, configuration snippets, private user statements, and copied error context. They are not lower risk than narrative fields.

**Desired change:** One canonical transformation should recursively visit every persisted string after parsing and before serialization, regardless of ingress path or record kind. It should cover source references, source claims, resolution references, notes, tags, paths, titles, quarantine diagnostics, and future optional fields.

WHEN equivalent payloads enter through flags, a JSON file, or JSON stdin THEN the writer SHALL persist byte-equivalent sanitized records except for system-generated metadata.

WHEN a secret fixture appears at any nesting depth THEN the writer SHALL redact it before canonical append, diagnostic output, quarantine, index generation, or talkback.

### 4.2 Canonical files are not private by construction

**Evidence:** Under a common `0022` umask, a controlled filing created `events.jsonl` with mode `0644`.

**Why it matters:** The stream can contain reasoning, local paths, private statements, tool output, and sensitive failure evidence. Relying on callers to remember a restrictive umask is not a safe default.

**Desired change:** The canonical writer should set `umask 077`, create store directories as `0700`, create canonical and temporary files as `0600`, and harden existing compatible paths. Suspicious symlinks should be rejected or explicitly acknowledged.

WHEN the writer creates any store, lock metadata, quarantine file, index, trap file, or temporary artifact THEN it SHALL create the artifact with user-only permissions.

WHEN an existing artifact is more permissive THEN the writer SHALL either harden it safely or fail with a precise remediation message.

### 4.3 Malformed-input recovery can disclose the very data it failed to parse

**Evidence:** The malformed JSON path prints the offending line and can save the full payload for replay.

**Why it matters:** Parsing failure removes the schema boundaries that normal redaction depends on. A malformed payload may contain credentials precisely where the parser cannot identify them.

**Desired change:** Print a bounded, best-effort-redacted excerpt. Make full-payload quarantine opt-in or unmistakably warned. Keep its parent directory private, include retention guidance, and never echo a replay command containing plaintext content.

WHEN malformed input contains a secret fixture THEN stderr SHALL NOT contain the raw fixture.

WHEN the tool quarantines a payload THEN the receipt SHALL disclose the private path, retention behavior, and deletion command without repeating the payload.

### 4.4 `--repo-root` can lie about physical provenance

**Evidence:** A controlled command run in temporary repository A with `--repo-root` pointing at temporary repository B wrote the canonical event under A and stamped B into `repo_root`.

**Why it matters:** Queries, reports, provenance, and agent expectations can all disagree about where the canonical record lives.

**Desired change:** `--repo-root` should control both routing and recorded identity. Explicit `--events-file` should remain the highest-precedence override. Paths should be canonicalized before comparison and receipt generation.

WHEN `--repo-root B` is supplied from working directory A THEN the writer SHALL route to B's canonical store and record B's canonical root.

IF `--events-file` and `--repo-root` conflict THEN the writer SHALL either reject the conflict or record both physical store and logical repository explicitly; it SHALL NOT silently fabricate consistency.

### 4.5 Stale locks can hang forever

**Evidence:** A lock directory without a usable PID caused the writer to wait indefinitely. The audit used an external timeout to regain control.

**Why it matters:** A killed writer can turn all future capture into a permanent hang. PID reuse and multi-host filesystems make a bare PID insufficient even when it exists.

**Desired change:** Centralize locking in one helper with a bounded wait, host identity, PID, process-start evidence when available, creation timestamp, owner token, and safe stale reclamation. Keep the current atomic-directory approach unless a tested alternative improves the supported host matrix.

WHEN a lock cannot be acquired before the configured deadline THEN the command SHALL fail with the lock path and bounded owner evidence.

WHEN the owner is demonstrably stale THEN the command MAY reclaim the lock atomically and SHALL report that recovery.

The current support claim should remain scoped to same-host writers on one filesystem. A network share or synchronized folder is not proven safe.

### 4.6 A committed append can be reported as failure

**Evidence:** The writer appends the canonical record before rebuilding derived views and printing the event receipt. If index or talkback work fails, the command can exit unsuccessfully after the record already exists.

**Why it matters:** Agents commonly retry failed commands. Here, a retry may create a duplicate because the first append actually committed.

**Desired change:** Define append as the commit point. Immediately print a machine-readable committed receipt containing event ID, canonical store, record kind, and idempotency key if one exists. Treat index and talkback as recoverable derived work. A derived failure should return degraded success plus a repair command.

WHEN canonical append succeeds THEN the writer SHALL emit the committed receipt before running noncanonical derived work.

WHEN index generation fails after append THEN the command SHALL NOT imply that no event was filed.

Do not call the receipt “durable” unless the implementation defines and tests its `fsync` boundary.

### 4.7 “Append-only” conflicts with in-place metadata rewriting

**Evidence:** The logging specification says records are never edited or deleted, then documents `--add-tags` and `--add-aliases` as exceptions that rewrite a matching record.

**Why it matters:** Audit semantics should be unambiguous. A user deciding whether to trust hashes or immutable history should not discover a broad exception later.

**Desired change:** Prefer append-only amendment records that derive effective tags and aliases at read time. If that is judged too expensive, narrow the public promise to “event narratives are immutable; selected metadata may be atomically amended.”

WHEN strict append-only mode is enabled THEN metadata changes SHALL create new amendment records and SHALL NOT replace prior JSONL lines.

### 4.8 Sequential identity assumes a healthy line stream

**Evidence:** Event allocation relies on line-oriented state. Blank lines, partial final records, manual edits, or synchronization conflicts can make line-derived allocation misleading.

**Why it matters:** Identity is used for recurrence, resolution, and cross-report references.

**Desired change:** Allocate from the maximum validated per-store identifier under lock, not raw line count. Add a read-only `doctor` command and an explicit repair-tail operation that quarantines damaged bytes rather than deleting them silently.

WHEN the stream contains malformed or duplicate identifiers THEN the writer SHALL refuse append until the operator runs or explicitly authorizes repair.

### 4.9 Stored data reaches executable contexts

**Evidence:** `render-summary.sh` interpolates a stored timestamp into generated Python source. `report-friction.sh` also uses shell `eval` while transferring JSON-derived assignments.

**Why it matters:** Data should remain data even if a store is manually crafted or corrupted. Quoting that appears adequate today is a fragile security boundary and conflicts with the repository's stated preference against `eval` on user input.

**Desired change:** Pass values as command arguments, stdin, or a machine-readable temporary object. Replace dynamic variable access with explicit mappings or a single Python validation/serialization boundary.

You SHALL NOT interpolate store-controlled or payload-controlled strings into executable Python or shell source.

### 4.10 Temporary cleanup is incomplete

**Evidence:** Not every temporary event, rewrite, and derived artifact is registered in one cleanup path.

**Why it matters:** Interruptions can leave sensitive material behind or produce ambiguous next-run state.

**Desired change:** Use one cleanup registry for temporary files and locks. Exercise interruption immediately after lock creation, temporary creation, canonical append, metadata rewrite, and index start.

WHEN the process exits normally, errors, receives an interrupt, or times out THEN it SHALL remove every owned temporary artifact without removing a committed canonical record.

### 4.11 Capture and Mend claim overlapping work

**Evidence:** The capture description includes requests to log, review, mend, or distill friction. Friction Mend also claims review, triage, mending, resolution, and distillation.

**Why it matters:** A request to review the plugin or its corpus can surface both skills, load two substantial instruction sets, and blur whether the agent is authorized to modify sources or merely analyze them.

**Desired change:** Make the boundaries explicit:

- Capture activates on a genuine prediction divergence, a known recurrence, or an explicit request to log one incident.
- Mend activates on an explicit request to review, triage, resolve, mend, or distill an existing friction corpus, backlog, dashboard, or trap file.
- Neither activates merely because the user asks to review the plugin implementation, fix an ordinary error, or summarize test output.

WHEN a prompt asks to review the Friction Diagnostics plugin itself without asking to inspect an event corpus THEN Mend SHALL NOT activate merely because the word “review” appears.

### 4.12 The evidence contract assumes text exists

**Evidence:** The current rubric requires verbatim actual evidence and at least one verbatim quotation in the reading.

**Why it matters:** Valid surprises can be visual, physical, behavioral, temporal, or defined by an absence:

- A dialog looks clipped even though layout metrics pass.
- A component becomes warmer than predicted.
- A stakeholder response differs from the plan.
- A measure moves in an unexpected direction.
- A scene intended as solemn is perceived as comic.
- An expected browser action never occurs.

Forcing a quote in these cases encourages fabrication.

**Desired change:** Require the best available primary evidence:

- Exact output when output exists.
- Exact wording when wording exists.
- A measurement when measured.
- A before/after state transition when state changed.
- A labeled firsthand observation when no external record exists.
- An explicit non-occurrence when the surprise is an absence.
- Honest uncertainty when evidence is incomplete.

WHEN no textual evidence exists THEN the record SHALL accept a labeled observation, measurement, state transition, or non-occurrence without requiring an invented quotation.

### 4.13 “What betrayed you” presupposes blame

**Evidence:** The skill and schema repeatedly describe sources as “what you trusted that betrayed you.”

**Why it matters:** The source may be accurate while the reporter extrapolates too far. It may be stale, ambiguous, misplaced, incomplete, or correct only in another environment. A person or tool need not have failed for the prediction to be unsupported.

**Desired change:** Use “inputs that supported the prediction” or “prediction bases.” During Mend, classify the gap as incorrect content, missing content, ambiguity, stale information, poor placement, unsupported inference, environmental behavior, or missing control.

This neutral language improves both cross-domain generality and root-cause accuracy.

### 4.14 Pivot information can be a coupled set

**Evidence:** The current framing strongly prefers one decisive fact.

**Why it matters:** Some decisions depend on a minimal set rather than one fact: a metric plus its denominator, a policy plus an exception, a browser state plus an extension permission, or observations held by multiple people.

**Desired change:** Prefer the smallest actionable information unit while allowing a coupled set, a precedence rule, a required probe, distributed knowledge, or “unknowable in advance.”

WHEN no single fact would have changed the decision THEN the record SHALL accept the smallest coupled set and explain why the elements are jointly necessary.

### 4.15 Decision reconstruction should scale with stakes

**Evidence:** The full rubric asks for choices, rejected alternatives, and perceived authority even when a first occurrence was low impact or reflexive.

**Why it matters:** Mandatory deep reconstruction creates ceremony and encourages invented deliberation.

**Desired change:** Allow compact truthful statements such as “I saw one path,” “I reacted reflexively,” or “I filed before responding.” Keep full reconstruction for blocked work, consequential outcomes, instruction deviations, authorization questions, and deliberate overrides.

### 4.16 Workflow impact is not consequence

**Evidence:** Current values describe whether work continued, became noisy, degraded, or blocked.

**Why it matters:** Work can continue while producing a false conclusion, user-visible defect, data leak, financial loss, or safety risk. Conversely, blocked work may have no external consequence.

**Desired change:** Preserve workflow disruption as one dimension. Pilot an optional consequence field for output, user, data, financial, legal, safety, or decision harm. Do not infer severity when evidence is absent.

### 4.17 Full user-facing summaries are disproportionate by default

**Evidence:** The skill calls the final summary a courtesy but requires the renderer output to be pasted whenever an event was filed. In the DiffHound thread this added a large diagnostic footer to work whose primary subject was the product.

**Why it matters:** The logging system becomes part of every answer and competes with the user's requested deliverable.

**Desired change:** Use progressive disclosure:

- Say nothing when no event was filed.
- Use one compact line when a filing happened during unrelated work.
- Show the full table when the user requested friction analysis, an audit trail, or when the event materially changes the handoff.
- Keep query commands out of ordinary product answers unless needed.

WHEN a filing is incidental to another task THEN the final response SHOULD disclose only the event ID and a short reason.

### 4.18 “Open” conflates unmended learning with an unhandled incident

**Evidence:** The DiffHound corpus contained zero formal resolution records even though ordinary product work repaired several immediate failures. Every anchor therefore remained mechanically open.

**Why it matters:** Readers can reasonably interpret “open” as “the product remains broken,” while the store actually means “no later resolution record names this anchor.”

**Desired change:** Rename the current state to `unmended` or explain it prominently. Later, pilot explicit append-only dispositions such as:

- Incident handled.
- Source hardened and verified.
- Needs evidence.
- Active environmental trap.
- Closed as no further action.

Immediate verified closure should remain explicit and auditable; the capture workflow should not silently declare itself mended.

### 4.19 Recurrence can over-group a symptom family

**Evidence:** During browser and Playwright work, similar locator symptoms could arise from hidden alternate controls, dynamic accessible names, duplicate live regions, reused test attributes, stale views, or fuzzy matching. The visible symptom was similar, but the upstream prevention differed.

**Why it matters:** A recurrence inherits the anchor's explanation. If the root cause differs, the corpus becomes causally misleading.

**Desired change:** Use this semantic test:

> Two occurrences are recurrences when the same missing fact or upstream control would have prevented both.

If that is false, file a distinct anchor and optionally relate it as `related_to`, `caused_by`, or `same_symptom_as`. Relationships should be piloted before becoming mandatory schema.

### 4.20 Concurrent semantic duplicates need a merge path, not automatic merging

**Evidence:** A write lock can protect bytes while two agents still file semantically equivalent anchors because neither knows the other's intended taxonomy.

**Why it matters:** Storage concurrency and semantic concurrency are different problems.

**Desired change:** Keep filing conservative. Improve suggestions, then allow an append-only `duplicate_of` or `merged_into` relationship during Mend. Preserve both original records and the later consolidation decision.

### 4.21 Mechanical clustering produces weak matches

**Evidence:** Token overlap produced candidates connected by generic words such as “the” and “while.”

**Why it matters:** False candidate groups waste Mend attention and can encourage bad recurrence classification.

**Desired change:** Add stop-word removal, distinctive-token weighting, source-reference overlap, pivot overlap, recurrence-key evidence, and an explanation for every candidate edge. Keep clustering advisory; never merge silently.

### 4.22 Query and reporting defaults are unbounded

**Evidence:** The canonical query materializes all matching records. It has no limit, cursor, field projection, or explicit `--all`. The first documented Mend query asks for the complete open corpus. The DiffHound snapshot produced about 41 KB of open JSON versus a 4.4 KB bounded index.

**Why it matters:** Full-corpus loading consumes agent context before the user has selected a cluster. Pairwise hinting also becomes expensive as the corpus grows.

**Desired change:** Add newest-first bounded defaults, `--limit`, `--all`, `--fields`, cursor or date pagination, streaming JSONL, and bounded cluster-member displays with total counts. Mend should read the dashboard and cluster hints first, then query selected anchors.

WHEN a query omits `--all` and `--limit` THEN it SHALL use a documented bounded default and report truncation.

### 4.23 The advertised schema is not an executable standard schema

**Evidence:** The file declares JSON Schema Draft 2020-12 but expresses record-kind requirements through custom `x-required` and `x-kinds` metadata. A normal validator accepts objects that the writer rejects, including an empty object.

**Why it matters:** Tooling and humans may assume the file is the canonical executable contract when it is actually a field catalog plus custom semantics.

**Desired change:** Either implement a discriminated schema with standard `required`, `oneOf`, or `if/then`, or rename the file as a field catalog and designate one canonical validator. Current writes should be strict; documented legacy reads can remain tolerant.

### 4.24 Corruption policy changes by code path

**Evidence:** Some readers fail on malformed JSONL while others skip malformed records. A writer can append before a later derived-view rebuild discovers older corruption.

**Why it matters:** An audit-oriented store cannot silently omit evidence in one command and reject the same store in another.

**Desired change:** Choose one policy: fail before write and direct the user to `doctor`, or quarantine only a demonstrably damaged tail through an explicit repair operation. Every command should report degraded state consistently.

WHEN any preexisting nonblank line is malformed THEN canonical append SHALL NOT proceed silently.

### 4.25 CI selection does not follow the plugin

**Evidence:** The integrated smoke test is substantial, but CI change selection is derived from the packaged render-table skill rather than every capture and Mend file. The smoke suite is also absent from the normal local `just test` or `just verify` surface.

**Why it matters:** A strong test that does not run for the code it protects is not a release gate.

**Desired change:** Add one `test-friction-diagnostics` command and trigger it whenever any file under `plugins/friction-diagnostics/`, relevant packaging code, or its CI selector changes. Include it in the normal verification command.

### 4.26 Trigger eval artifacts are not executed

**Evidence:** Positive and negative prompt files exist, but no committed runner proves whether either host surfaces and follows the intended skill.

**Why it matters:** Static prompt examples do not establish activation precision, Capture/Mend exclusivity, cheap recurrence behavior, silence for expected failures, or parity between Codex and Claude.

**Desired change:** Run a small deterministic cross-host behavioral matrix. Include mid-task trajectories where surprise emerges from a tool result; do not rely only on prompts containing “surprised,” “log,” or “friction.”

### 4.27 Cross-repository and portability coverage is shallow

**Evidence:** The existing cross-repository smoke uses multiple stores under one temporary repository rather than independent repositories with colliding local identifiers. The supported shell path is primarily exercised on Ubuntu.

**Why it matters:** It does not prove behavior for paths with spaces or Unicode, directories outside Git, multiple `.local*` choices, symlinks, duplicate scan roots, two repositories each containing `evt-0001`, or different POSIX shells.

**Desired change:** Add true independent repositories, identifier collisions, ambiguous store discovery, non-Git operation, path edge cases, symlink policy, and an intentional shell/host matrix.

### 4.28 Some tests are probabilistic without need

**Evidence:** The interview-rotation test expects randomized questions to differ within a small number of attempts.

**Why it matters:** The false-failure probability is low but avoidable.

**Desired change:** Keep production randomness and add an explicit seed or deterministic test fixture.

### 4.29 Progressive disclosure and reference routing are incomplete

**Evidence:** `references/integration.md` and `references/logging-spec.md` are shipped but not directly linked from the capture skill. The skill body simultaneously contains policy, payload examples, fields, exit codes, storage rules, query commands, and a script catalog.

**Why it matters:** Important detail is both hidden and duplicated. Agents pay a large context cost while still missing active references.

**Desired change:** Keep the surprise gate, exclusions, compact capture path, recurrence path, and Capture/Mend boundary in `SKILL.md`. Link a small reference index. Put storage and exit-code detail in the logging specification. Rename `references/examples.md` to `field-rubrics.md` unless real worked examples are added.

### 4.30 Capability metadata understates writes

**Evidence:** The Codex-facing interface advertises a read capability even though normal operation writes repository-local state.

**Why it matters:** Hosts and users should not discover mutation only after activation.

**Desired change:** Advertise `Read, Write` or the host-equivalent local-state capability and list the real runtime requirements: POSIX shell, `jq`, and Python 3 where applicable.

## 5. Target architecture

The recommended architecture is a deliberate hybrid with four immediate layers and one deferred extension point.

### 5.1 Ambient surprise policy

The always-available instruction should be short:

1. Detect a prediction divergence.
2. Apply the worth-logging test.
3. File a new anchor or cheap recurrence immediately when useful.
4. Stay silent for expected failures, probes, and status.
5. Read the bounded active-trap view before work when one exists.

This layer makes capture available during arbitrary tasks without loading every field rule and script into the context.

### 5.2 Capture skill

Capture should own:

- New full anchors.
- Cheap recurrence records.
- Duplicate soft stops.
- Explicit user requests to log an incident.
- Evidence composition and proportional depth.
- A compact success disclosure.

Capture should not own backlog review, source editing, cluster convergence, trap publication, or broad resolution judgment.

### 5.3 Mend skill

Mend should activate only for an existing corpus and own:

- Cluster review.
- Root-cause analysis.
- Source or instruction hardening.
- Resolution provenance.
- Relationship and duplicate consolidation.
- Trap publication and removal.
- Honest “needs evidence” or “active external hazard” outcomes.

### 5.4 Deterministic persistence component

One canonical implementation should own:

- Read-only discovery versus write/create resolution.
- Path canonicalization.
- Parsing and current-write validation.
- Legacy-read tolerance.
- Recursive redaction.
- Permission enforcement.
- Lock acquisition and bounded recovery.
- ID allocation.
- Pre-append integrity checks.
- Append and receipt ordering.
- Derived-view rebuilding.
- Queries, lifecycle reduction, and store identity.
- Doctor and explicit repair operations.

Shell wrappers may remain, but they should delegate to one implementation rather than reproduce rules in several scripts.

### 5.5 Optional adapters are a future boundary, not current work

The local JSONL adapter is appropriate for the validated use case. A clean internal operation boundary may later support a host key-value store, local database, MCP service, shared database, or no-filesystem return mode. None should be built without a concrete requirement and threat model.

## 6. Event-model evolution

The current schema should evolve only where evidence shows that the existing meaning distorts records. This section separates recommended semantic clarification from optional new fields.

### 6.1 Revised meanings for existing fields

#### `actual_outcome`

The best available primary evidence of the divergence. Prefer exact output or wording when it exists. Otherwise accept a measurement, state transition, labeled firsthand observation, explicit non-occurrence, or honest uncertainty. Mandatory secret redaction applies before persistence.

#### `expected_outcome`

The prediction actually held before the result, plus enough context to understand its basis. It must not be rewritten using knowledge obtained afterward.

#### `reading`

The reporter's interpretation and sequence of reasoning from inside the decision. A quotation is required only when specific wording materially supported the interpretation.

#### `decision`

The response actually made. Valid compact values include “I saw one path,” “I reacted without deliberation,” and “I captured the event before acting.” High-stakes or policy-relevant events should preserve alternatives and perceived authority in greater depth.

#### `pivot_information`

The smallest actionable information unit that would have changed the response, including where it could have been surfaced. It may be one fact, a coupled set, a precedence rule, the result of a probe, distributed knowledge, or genuinely unknowable in advance.

#### `sources`

Inputs that supported the prediction. A source object should include a kind, precise reference, and the claim believed about it. The source need not be wrong; Mend determines whether the gap was in content, freshness, placement, ambiguity, inference, environment, or a missing control.

#### `impact`

Clarify this as workflow disruption rather than severity: continued, noisy, degraded, or blocked.

### 6.2 Candidate append-only extensions

These are pilots, not immediate mandatory fields.

#### `consequence`

An evidence-backed description of output, user, data, financial, legal, safety, or decision harm. It should remain optional and should never be guessed.

#### `relation`

An append-only record connecting two anchors. Candidate kinds:

- `same_root_cause`
- `same_symptom`
- `caused_by`
- `duplicate_of`
- `supersedes_hypothesis`
- `split_from`

The record should identify both store-qualified targets, the reporter, the evidence supporting the relationship, and when it was asserted.

#### `amendment`

An append-only change to tags, aliases, title metadata, or another explicitly amendable field. Readers derive effective metadata without rewriting the original line.

#### richer `resolution`

A future resolution may distinguish:

- `mended`: the controllable source was changed and verified.
- `mitigated`: a guard reduced risk while the underlying source remains.
- `external`: the hazard is outside control and remains active.
- `not_actionable`: the record is retained but no action is warranted.

Useful optional fields include `hazard_active`, `verification`, `references`, `residual_risk`, and `resolved_targets`.

### 6.3 Recurrence decision rule

The rule should be causal enough to protect the corpus and simple enough to use in the moment:

> Would the same missing information or upstream control have prevented both occurrences?

If yes, file a recurrence. If no, file a distinct anchor and optionally create a relationship later. Similar error strings alone are insufficient.

## 7. Proposed command contract

The exact executable name is less important than having one canonical contract. The examples below use `friction-store` to make the separation from current wrappers explicit.

### 7.1 Append

```text
friction-store append \
  --repo-root /absolute/repository \
  [--events-file /absolute/repository/.local/reports/friction/events.jsonl] \
  [--idempotency-key UUID] \
  --from-json -
```

Example success receipt:

```json
{
  "status": "committed",
  "event_id": "evt-0042",
  "kind": "friction",
  "store": "/absolute/repository/.local/reports/friction/events.jsonl",
  "repo_root": "/absolute/repository",
  "derived": {
    "index": "updated",
    "talkback": "updated"
  }
}
```

Example degraded success:

```json
{
  "status": "committed_with_warning",
  "event_id": "evt-0042",
  "kind": "friction",
  "store": "/absolute/repository/.local/reports/friction/events.jsonl",
  "warning": {
    "stage": "index",
    "code": "DERIVED_VIEW_FAILED",
    "repair": "friction-store rebuild --events-file /absolute/repository/.local/reports/friction/events.jsonl"
  }
}
```

The command must not return a “nothing filed” error after either receipt.

### 7.2 Query

```text
friction-store query \
  --repo-root /absolute/repository \
  --kind friction,recurrence,resolution \
  --state unmended \
  --limit 25 \
  --fields event_id,recorded_at,title,impact,recurrence_key \
  --format json
```

Additional options:

- `--cursor TOKEN`
- `--after ISO_TIMESTAMP`
- `--before ISO_TIMESTAMP`
- `--session-ref ID`
- `--all-sessions`
- `--all`
- `--format jsonl|json|markdown`

WHEN results are truncated THEN the output SHALL include total-known count when cheaply available, returned count, truncation state, and a continuation cursor.

### 7.3 Resolve

```text
friction-store resolve \
  --repo-root /absolute/repository \
  --target evt-0042 \
  --disposition mended \
  --action "Made repository routing derive from the explicit root" \
  --verification "Independent A-to-B routing test passed" \
  --reference plugins/friction-diagnostics/skills/friction-diagnostics/scripts/_common.sh
```

The target identity is scoped to the canonical store. A future shared adapter may use globally unique record IDs, but the local repair does not require rewriting historical IDs.

### 7.4 Relate

```text
friction-store relate \
  --from evt-0042 \
  --to evt-0031 \
  --kind duplicate_of \
  --evidence "Both were prevented by the same repository-root routing check"
```

This appends a relation record. It does not rewrite either anchor.

### 7.5 Amend

```text
friction-store amend \
  --target evt-0042 \
  --add-tag storage-routing \
  --reason "Assigned during Mend after root-cause verification"
```

This appends an amendment record. It does not replace the original event line.

### 7.6 Doctor

```text
friction-store doctor \
  --repo-root /absolute/repository \
  --format json
```

The doctor should inspect without mutation:

- Directory and file permissions.
- Symlink policy.
- Parse validity for every nonblank line.
- Duplicate identifiers.
- Monotonic or otherwise valid ID allocation.
- Dangling recurrence, relation, amendment, and resolution pointers.
- Recorded versus physical store mismatches.
- Stale locks and owner evidence.
- Derived index freshness.
- Trap-view consistency.
- Multiple plausible stores in one repository.

Repairs should be separate, explicit commands. Read-only diagnosis should never create `.local` directories.

### 7.7 Error shape

Machine-readable errors should contain a stable code, stage, whether a canonical append occurred, and a safe remediation. For example:

```json
{
  "status": "failed",
  "committed": false,
  "code": "LOCK_TIMEOUT",
  "stage": "lock",
  "message": "Could not acquire the store lock before the 10-second deadline",
  "lock": "/absolute/repository/.local/reports/friction/.report-friction.lock",
  "owner": {
    "host": "workstation",
    "pid": 1234,
    "created_at": "2026-07-14T12:00:00Z"
  }
}
```

Error output must never contain raw secret fixtures used in the rejected payload.

## 8. File-level implementation backlog

This section is deliberately specific so an implementer can translate the report into issues without reverse-engineering the proposal.

### 8.1 `skills/friction-diagnostics/SKILL.md`

Requested changes:

1. Remove “review, mend, or distill” from the capture trigger description.
2. Keep the worth-logging test and expected-failure exclusions near the top.
3. Replace “what you trusted that betrayed you” with “inputs that supported the prediction.”
4. Replace universal verbatim requirements with the best-available-primary-evidence rule.
5. State that exact quotes are required when wording existed and mattered, not for every record.
6. Allow coupled pivot information and honest unknowability.
7. Allow compact decision accounts for low-stakes or reflexive cases.
8. Default to a one-line filing disclosure outside friction-focused work.
9. Link `references/logging-spec.md`, `references/integration.md`, the field rubric, and an actual examples file if one exists.
10. Keep only the compact JSON-stdin and recurrence paths in the main skill; move the complete script catalog and exit-code detail behind references.

Acceptance criteria:

WHEN a mid-task tool result unexpectedly contradicts an assumption THEN the trigger eval SHALL select Capture.

WHEN a user asks to review the plugin source without asking to inspect events THEN the trigger eval SHALL NOT select Mend merely because “review” appears.

WHEN a valid surprise has only visual evidence THEN the skill SHALL guide the agent to label the observation instead of fabricating a quote.

### 8.2 `skills/friction-mend/SKILL.md`

Requested changes:

1. Narrow the description to explicit work on an existing friction corpus or backlog.
2. Make dashboard-first, bounded discovery the default.
3. Require the mender to inspect source and pivot evidence before accepting mechanical clusters.
4. Allow `needs_evidence` and active external hazards; do not force binary fixed-versus-wontfix closure.
5. Make scoped trap upsert/removal the default instead of whole-file replacement.
6. Require verification evidence and residual-risk notes for serious resolutions.
7. Keep actual source editing user-authorized; a read-only audit must not silently mutate the corpus or product sources.

### 8.3 `scripts/_common.sh` in both skill copies

Requested changes:

1. Extract one canonical path resolver with separate read and write modes.
2. Make explicit repository roots control routing.
3. Prefer an existing canonical friction store before creating a new `.local*` choice.
4. Return an ambiguity error when several plausible stores exist and policy cannot choose safely.
5. Add `ensure_private_dir`, `ensure_private_file`, `canonical_path`, `safe_temp`, and centralized cleanup helpers.
6. Add one bounded lock implementation shared by append, resolution, index, and trap publication.
7. Remove dynamic `eval`-based data transfer.
8. Ensure vendored helper copies remain byte-equivalent or are generated from one source.

### 8.4 `scripts/report-friction.sh`

Requested changes:

1. Route flags and JSON through one parsed internal record.
2. Recursively sanitize that record once after parsing.
3. Validate the current-write schema before locking.
4. Acquire the bounded canonical lock.
5. Validate existing store integrity before allocating an ID.
6. Allocate from validated store state.
7. Append the canonical record.
8. Emit the committed receipt immediately.
9. Rebuild index and talkback as derived work.
10. On derived failure, return committed-with-warning rather than an ambiguous general failure.
11. Replace in-place `--add-tags` and `--add-aliases` with append-only amendment mode, or narrow the immutability claim until that migration is complete.
12. Sanitize malformed-input stderr and quarantine behavior.
13. Use stable exit codes consistently for JSON input failures.

### 8.5 `scripts/report-friction-json.sh`

Requested changes:

1. Keep it as a truly thin wrapper or remove it in favor of a single entry point.
2. Ensure `--repo-root` and `--events-file` precedence matches the canonical writer.
3. Do not add a second validation, sanitization, or path-resolution implementation.

### 8.6 `scripts/build-index.sh`

Requested changes:

1. Use the shared bounded lock.
2. Accept only a validated canonical store.
3. Write private temporary and final files.
4. Make failure after canonical append recoverable through a separate rebuild command.
5. Label unresolved anchors `unmended` until richer lifecycle semantics are implemented.

### 8.7 `scripts/query-friction.sh`

Requested changes:

1. Make default operation read-only and non-creating.
2. Add `--limit`, `--all`, `--fields`, cursor/date pagination, `--session-ref`, and JSONL streaming.
3. Report truncation explicitly.
4. Use one corruption policy.
5. Attach canonical physical store identity to every result.
6. Keep per-store IDs scoped to that store in cross-repository operations.

### 8.8 `scripts/render-summary.sh`

Requested changes:

1. Remove stored-value interpolation into Python source.
2. Use session identity when available.
3. When only a timestamp boundary is available, label the output “time-window summary,” not “this session.”
4. Default to a compact one-line disclosure for unrelated work.
5. Keep the full table as explicit detailed output.

### 8.9 `scripts/generate-report.sh`

Requested changes:

1. Use bounded query primitives instead of separately slurping and filtering full stores.
2. Distinguish `stores_scanned` from `repositories_scanned`.
3. Aggregate repository views by canonical repository root.
4. Show bounded member lists with totals and truncation metadata.
5. Use the same lifecycle reducer as queries and talkback.

### 8.10 `skills/friction-mend/scripts/record-resolution.sh`

Requested changes:

1. Delegate to the canonical persistence path.
2. Require store-qualified target resolution.
3. Validate that every target exists in the chosen store.
4. Accept structured disposition, verification, references, hazard state, and residual risk during a pilot.
5. Emit the same committed receipt format as capture.
6. Never permit a resolution in one store to affect an identical local ID in another.

### 8.11 `skills/friction-mend/scripts/cluster-hints.sh`

Requested changes:

1. Remove stop words and weight distinctive tokens.
2. Use normalized source reference, source claim, pivot information, recurrence key, and rare outcome signature.
3. Show why every edge was suggested.
4. Avoid transitive merging when only A-B and B-C overlap.
5. Fail loudly or mark degraded state on malformed records.
6. Keep all suggestions advisory.

### 8.12 `skills/friction-mend/scripts/update-traps.sh`

Requested changes:

1. Add strict `--check` validation against the canonical store.
2. Add locked `--upsert` and `--remove-key` operations.
3. Make `--replace-all` explicit rather than implicit.
4. Preserve unrelated traps during a scoped Mend.
5. Generate counts and dates from store data rather than model transcription.
6. Emit added, changed, removed, and unchanged counts.
7. Protect `--clear` with the same lock and authorization rules.

### 8.13 `friction-event-schema.json`

Requested changes:

1. Choose executable standard JSON Schema or clearly name the artifact a field catalog.
2. If standard schema is chosen, discriminate record kinds with standard keywords.
3. Require nonblank source claims for full anchors.
4. Encode current writes separately from documented legacy-read tolerance.
5. Apply string bounds and enumerations consistently.
6. Add relation, amendment, consequence, and richer disposition only after pilots establish their shape.
7. Keep the Capture and Mend schema copies identical or generated.

### 8.14 `tests/smoke-posix.sh`

Add deterministic cases for:

- Nested sanitizer coverage across all string fields.
- Malformed secret-bearing input with safe stderr and quarantine.
- `0600` files and `0700` directories under permissive umask.
- Repository A invoking `--repo-root B`.
- Explicit store/root conflict.
- Lock directory without PID.
- Malformed PID.
- PID reuse evidence where supported.
- Lock timeout and safe reclamation.
- Interruption at every write phase.
- Canonical append success followed by forced index failure.
- Duplicate retry prevention or explicit committed receipt.
- Partial final JSONL line.
- Blank lines and duplicate identifiers.
- Read-only query in a clean repository leaving the workspace unchanged.
- Multiple `.local*` candidates.
- Spaces and Unicode in paths.
- Independent repositories with colliding event IDs.
- True append-only amendment behavior.
- Deterministic interview selection with a test seed.

### 8.15 CI, `justfile`, manifests, and plugin metadata

Requested changes:

1. Add `just test-friction-diagnostics`.
2. Include it in the normal repository verification surface.
3. Trigger the CI job on every plugin file, relevant packaging file, and selector change.
4. Run frontmatter, manifest completeness, reference reachability, schema validation, smoke tests, trigger evals, and both host package validations.
5. Round-trip both host variants before a release.
6. Advertise local write capability honestly.
7. List runtime dependencies and portability scope.

## 9. Verification plan

The plugin should not be called foundational merely because the happy path works. Verification needs to prove the boundaries that matter: secrecy, commitment, identity, lifecycle, activation, portability, and bounded output.

### 9.1 Canonical local command

One command should run the complete plugin verification surface:

```text
just test-friction-diagnostics
```

It should execute, in a deterministic order:

1. Skill frontmatter and description validation.
2. Manifest completeness and unexpected-file checks.
3. Reference reachability.
4. Shell syntax and static checks.
5. Executable schema tests for every record kind.
6. Capture and Mend smoke tests.
7. Privacy and sanitizer tests.
8. Lock and fault-injection tests.
9. Cross-repository identity and routing tests.
10. Query bound and corruption tests.
11. Trigger and silence evaluations.
12. Codex and Claude port/validation checks.

WHEN this command exits successfully THEN every shipped file relevant to normal plugin behavior SHALL have been included by at least one structural, behavioral, or package-integrity check.

### 9.2 Store-integrity matrix

| Scenario | Required result |
| --- | --- |
| Empty new store | First valid append commits one parseable record and produces private derived artifacts. |
| Healthy existing store | Next ID is allocated under lock without rewriting earlier lines. |
| Blank line | Policy is explicit and consistent; no identity is derived from raw line count. |
| Partial final line | Append refuses and points to doctor/repair. |
| Malformed middle line | Append refuses; readers do not silently omit it. |
| Duplicate ID | Doctor reports both locations; append refuses. |
| Dangling recurrence | Doctor reports the missing target. |
| Dangling resolution | Doctor reports the missing target. |
| Forced index failure | Canonical append receipt remains visible and repair is possible without refiling. |
| Interrupt before append | No canonical record and no owned temporary artifact remain. |
| Interrupt after append | Exactly one canonical record remains; receipt/recovery state is unambiguous. |
| Twelve concurrent writers | Twelve valid unique records, no truncation, no interleaving. |
| Stale lock | Recovery or bounded timeout occurs; no indefinite wait. |

### 9.3 Privacy matrix

Use a synthetic secret fixture in every writable string location:

- Each narrative field.
- Title.
- Tag and alias.
- Source reference and source claim.
- Notes.
- Resolution action, reference, and verification.
- Relation evidence.
- Amendment reason.
- Repository and event-file metadata when caller-controlled.
- Malformed JSON before and after the syntax error.

For each ingress path—flags, JSON file, and JSON stdin—assert the fixture is absent from:

- `events.jsonl`
- `INDEX.md`
- `known-traps.md`
- stdout
- stderr
- quarantine files
- temporary files that remain after exit
- lock owner metadata

The test should also inspect mode bits under umasks `0022`, `0002`, and `0000`.

### 9.4 Routing and identity matrix

Create two genuine Git repositories A and B, each with an `evt-0001`. Test:

1. Running in A without overrides routes to A.
2. Running in A with `--repo-root B` routes to B.
3. Running in A with explicit B events file records physical B identity honestly.
4. Conflicting explicit root and explicit store produces a documented error or explicit dual provenance.
5. Querying both repositories never treats the two `evt-0001` values as the same record.
6. A resolution or amendment in A cannot affect B.
7. Duplicate scan roots are deduplicated by canonical path.
8. Paths with spaces and Unicode work.
9. Symlink behavior follows one tested policy.
10. A read in a clean repository creates no files or directories.

### 9.5 Schema matrix

Test every record kind with:

- Minimal valid current record.
- Fully populated current record.
- Missing required field.
- Blank required field.
- Unknown enum.
- Wrong scalar/container type.
- Empty sources array for a full anchor.
- Missing source claim.
- Oversized string and array.
- Unexpected property, according to the chosen policy.
- Valid documented legacy record.
- Invalid legacy record that must not be coerced silently.

The standard schema validator and canonical writer should agree for current records. If they intentionally differ for legacy reads, the tests should name that boundary.

### 9.6 Trigger and silence matrix

The evaluation corpus should test trajectories, not just obvious keywords.

Positive examples:

- A command succeeds but produces an undocumented output shape that invalidates the next step.
- A GUI button appears enabled but performs no action.
- A browser locator matches a hidden control rather than the visible one.
- A document instruction was followed correctly but is stale.
- An expected event does not occur and this changes the workflow.
- A known trap recurs during unrelated product work.

Negative examples:

- A red test written before implementation fails exactly as expected.
- An invalid-input test returns the expected error.
- A user asks for task status.
- A linter finds an ordinary issue without contradicting a prediction.
- A user asks to review the plugin source, not its event corpus.
- A user declines logging.

Mend-specific examples:

- Review the existing friction backlog and identify clusters.
- Resolve a named anchor after inspecting the source.
- Distill active traps from selected unresolved anchors.
- A scoped Mend must not rewrite unrelated traps.

Every case should run on both supported hosts where their skill-surfacing harness permits it. Results should record activation, nonactivation, selected skill, and whether behavior followed the intended boundary.

### 9.7 Lifecycle matrix

Even before richer dispositions exist, one reducer should drive query, dashboard, stats, talkback, and resolution checks. Test sequences such as:

- Anchor only.
- Anchor then recurrence.
- Anchor then resolution.
- Anchor, resolution, then later recurrence.
- Anchor, resolution, recurrence, then second resolution.
- Two stores with identical local IDs and a resolution in only one.
- Resolution of multiple targets.
- Duplicate resolution attempt.
- Relationship or amendment that must not change lifecycle.

For each sequence, assert the same open/unmended result across every derived view.

### 9.8 Scale and output bounds

Generate synthetic stores at 1,000 and 10,000 records before discussing 100,000-record support. Measure:

- Append latency.
- Lock hold time.
- Pre-append validation time.
- Bounded query latency and memory.
- Full explicit `--all` query cost.
- Index rebuild time.
- Cluster-hint time.
- Agent-visible output size.

The goal is not a premature performance target. The goal is to prove that default commands remain bounded and to identify the point where JSONL needs a different index strategy.

### 9.9 Portability and determinism

At minimum, exercise the declared POSIX shell surface on the actual supported host matrix. Include clean environments with only documented dependencies, paths containing spaces and Unicode, different locale settings, and deterministic random seeds for interview tests.

Round-trip the plugin through both host packaging directions and validate both converted variants. The smoke suite should operate on the source plugin, while package validation should prove that every required file survives conversion.

## 10. Plugin-induced friction observed during the audit

The audit itself exposed product friction separate from the defects being catalogued. These points matter because a foundational diagnostic system should not make ordinary work materially harder.

### 10.1 Capture and Mend both appeared relevant

**What happened:** A read-only review of the plugin and accumulated lessons matched language in both skill descriptions.

**Why this was friction:** Loading both instruction sets increased context and created a risk that a read-only proposal would drift into actually resolving events, editing sources, or publishing traps.

**Workaround used:** The Mend instructions were treated only as an analytical lens. No resolution or trap publication was performed, because the user asked for a proposal rather than an operational Mend.

**Permanent correction:** Make the descriptions disjoint as specified in finding 4.11.

### 10.2 The mandatory full summary competed with the user's requested handoff

**What happened:** Filing during the prior product work implied that the complete renderer output should be pasted into an answer about the extension.

**Why this was friction:** The diagnostic footer was large relative to the product update and exposed implementation-oriented commands the user had not asked to see.

**Workaround used:** The filing was disclosed compactly where possible, while full corpus detail remained available through the report scripts.

**Permanent correction:** Make compact disclosure the default and reserve the full table for friction-focused work.

### 10.3 Verbatim requirements did not fit every GUI observation

**What happened:** Some extension and browser surprises were perceptual or behavioral rather than a stable line of text—for example, a control's visual affordance or a GUI flow that did not visibly change state.

**Why this was friction:** The rubric encouraged searching for a quote even when the strongest evidence was a screenshot, state transition, or observed absence.

**Workaround used:** The observer described the primary visual or behavioral fact and used console or DOM evidence where available, while avoiding an invented quotation.

**Permanent correction:** Adopt the best-available-primary-evidence rule.

### 10.4 The stale-lock path required an external kill boundary

**What happened:** A synthetic lock directory without usable owner metadata caused the writer to wait without a deadline.

**Why this was friction:** The plugin offered no self-contained recovery or bounded error.

**Workaround used:** The probe was wrapped with an external `timeout` command. After termination, the lock was inspected manually before removal.

**Permanent correction:** Implement bounded shared locking and a read-only doctor.

### 10.5 Repository routing required bypassing the documented convenience

**What happened:** `--repo-root` affected recorded metadata without reliably controlling physical storage from another working repository.

**Why this was friction:** The advertised flag could produce a plausible but false record.

**Workaround used:** An explicit absolute `--events-file` was passed whenever the physical target mattered.

**Permanent correction:** Make repository-root resolution canonical and test A-to-B routing.

### 10.6 Privacy depended on caller discipline

**What happened:** The canonical stream inherited permissive mode bits, and JSON source strings did not share the narrative sanitizer.

**Why this was friction:** Every caller had to remember security steps that should belong to the store.

**Workaround used:** The audit set `umask 077`, pre-redacted JSON source fields, and hardened created files with `chmod 600` after confirming their paths.

**Permanent correction:** Enforce privacy inside the writer and test it under permissive umasks.

### 10.7 A failed command could not be assumed to mean “nothing was filed”

**What happened:** Inspection showed that append precedes index, talkback, and final receipt work.

**Why this was friction:** Blind retry was unsafe.

**Workaround used:** After any ambiguous failure, the canonical stream was inspected or queried before retrying.

**Permanent correction:** Emit a committed receipt immediately after append and make derived failures explicit warnings.

### 10.8 Full-corpus reading consumed unnecessary context

**What happened:** The open JSON query was about 41 KB, while the bounded index was roughly 4.4 KB.

**Why this was friction:** The prescribed Mend entry point loaded far more evidence than needed for initial triage.

**Workaround used:** The bounded index, aggregate stats, and cluster hints were inspected before targeted event queries.

**Permanent correction:** Make bounded progressive discovery the documented and enforced default.

### 10.9 Strict immutability required avoiding a documented command

**What happened:** `--add-tags` rewrites a prior JSONL line even though the store is described as append-only.

**Why this was friction:** A caller could not simultaneously follow the command documentation and preserve strict historical immutability.

**Workaround used:** Post-hoc tag mutation was avoided when immutability mattered; taxonomy notes were kept outside the canonical rewrite path.

**Permanent correction:** Add amendment records or narrow the public immutability claim.

### 10.10 Renderer support was not universal

**What happened:** Rich table rendering was not equally available on every host surface used during the work.

**Why this was friction:** The instruction assumed one presentation mechanism even though correctness did not depend on it.

**Workaround used:** A plain Markdown table or concise list was used as a readable fallback.

**Permanent correction:** Treat rich rendering as optional presentation and specify a stable text fallback.

### 10.11 Existing tests had to be invoked manually

**What happened:** The normal local and CI selection surfaces could skip the integrated plugin smoke suite.

**Why this was friction:** Confidence required knowing and running a separate script directly.

**Workaround used:** `tests/smoke-posix.sh` was invoked manually, and package/frontmatter/specification checks were run separately.

**Permanent correction:** Add the canonical local command and broaden CI selection.

## 11. Interim safe-operating procedure

Until the persistence implementation is repaired, callers can reduce risk with the following temporary procedure. This is not a substitute for fixing the plugin.

### 11.1 Before filing

1. Resolve the intended canonical store explicitly.
2. Use an absolute `--events-file` when filing outside the target repository's working directory.
3. Set a restrictive umask:

   ```text
   umask 077
   ```

4. Pre-redact narrative fields and every `sources[].ref` and `sources[].claim` value.
5. Inspect the store for malformed trailing data before an important append.
6. If a lock exists, verify that no live writer owns it before considering removal.

### 11.2 During filing

1. Prefer JSON through stdin for shell-sensitive content.
2. Wrap unattended filing with a bounded external timeout.
3. Use a new full anchor unless the same missing information or upstream control clearly explains the prior event.
4. Avoid copying secrets into malformed payload probes.
5. Capture stdout and stderr separately when the success state matters.

### 11.3 After filing

1. Confirm the new event ID exists in the canonical stream.
2. Confirm the record points to the intended repository and events file.
3. Harden permissions to `0600` if the current writer did not do so.
4. If the command failed after a possible append, query before retrying.
5. Inspect the bounded index rather than loading the entire corpus by default.
6. Avoid `--add-tags` when strict append-only history matters.
7. Use a compact user-facing disclosure unless the user asked for the full audit trail.

### 11.4 Lock recovery

You SHALL NOT delete a lock merely because a filing is slow.

IF the lock owner is demonstrably absent and no writer holds the target THEN you MAY remove the stale lock directory and retry once.

IF ownership cannot be established THEN you SHALL preserve the lock and escalate rather than risk concurrent writes.

## 12. What worked where the plugin could have failed

The audit should not be read as a rejection of the product. Several mechanisms were robust and useful:

- JSON stdin preserved quotes, backticks, multiline content, and literal shell syntax without expansion damage in the exercised happy path.
- Duplicate detection stopped likely duplicate anchors and offered explicit recur-versus-distinct options.
- Recurrence records made repeated browser and selector failures much cheaper to capture.
- Store talkback exposed relevant history immediately after filing.
- The bounded dashboard provided a much more context-efficient overview than the full open query.
- Session references, when present, improved traceability from records back to agent work.
- All 18 committed POSIX smoke scenarios passed.
- Same-host concurrent distinct writes remained parseable and received unique identifiers in the exercised 12-writer probe.
- The conceptual Capture/Mend split protected against immediate overfitting to a single surprise.
- The plugin captured subtle failures of verification semantics—not only command crashes—including cases where a tool or workflow appeared successful but proved less than the agent assumed.
- The worth-logging test filtered ordinary expected red tests and deliberate probes out of the corpus.
- The event shape preserved decision context that conventional logs would have lost.

These successes are the reason to harden the existing design rather than replace it.

## 13. Example records for the generalized model

These examples are illustrative contracts, not a demand to migrate the schema immediately. They demonstrate how the revised language supports different domains without weakening evidence quality.

### 13.1 Textual tool surprise

```json
{
  "kind": "friction",
  "actual_outcome": "Command exited 0, but the generated package omitted manifest.json.",
  "expected_outcome": "Exit 0 meant the complete distributable package had been produced.",
  "reading": "I treated process success as package completeness and moved to installation without inspecting the archive inventory.",
  "decision": "I attempted installation, then stopped when the host rejected the package.",
  "pivot_information": "A post-build inventory showing required package members, surfaced before the success receipt.",
  "sources": [
    {
      "kind": "tool",
      "ref": "package command exit status",
      "claim": "A zero exit status establishes that every required distributable member exists."
    }
  ],
  "impact": "degraded",
  "recurrence_key": "package-success-with-missing-required-member",
  "tags": ["packaging", "verification"]
}
```

Why this is useful: the record distinguishes command success from artifact completeness. The mend is not “handle the install error”; it is “make build success contingent on an inventory contract.”

### 13.2 Visual surprise without a fabricated quote

```json
{
  "kind": "friction",
  "actual_outcome": "Firsthand observation: at 320 CSS pixels wide, the primary action is visible but its label is clipped after the first six characters; screenshot reference ui-narrow-01.png.",
  "expected_outcome": "The responsive layout would preserve the full primary action label at the supported narrow viewport.",
  "reading": "Automated overflow checks passed, so I inferred that all important control labels remained usable.",
  "decision": "I paused release QA and reproduced the viewport manually.",
  "pivot_information": "A narrow-viewport assertion that checks visible accessible text for the primary action, not only container overflow.",
  "sources": [
    {
      "kind": "observation",
      "ref": "responsive smoke-test result",
      "claim": "No detected horizontal overflow implied the primary action remained fully legible."
    }
  ],
  "impact": "noisy",
  "recurrence_key": "overflow-pass-label-clipped",
  "tags": ["visual", "responsive", "accessibility"]
}
```

Why this is useful: the record uses a labeled observation and screenshot reference because no textual system message exists. It does not invent a quote merely to satisfy structure.

### 13.3 Research surprise with coupled pivot information

```json
{
  "kind": "friction",
  "actual_outcome": "The treatment segment improved conversion by 8%, while the retained-user count fell by 14% relative to control.",
  "expected_outcome": "A conversion improvement of this size would indicate a net-positive treatment effect.",
  "reading": "I interpreted the headline conversion rate without checking whether the denominator and retention composition changed.",
  "decision": "I initially recommended rollout, then withdrew the recommendation when the retention cut was added.",
  "pivot_information": "The coupled set of conversion numerator, eligible-user denominator, and 30-day retained-user count by treatment arm.",
  "sources": [
    {
      "kind": "artifact",
      "ref": "experiment summary table",
      "claim": "The displayed conversion lift was sufficient to judge net product impact."
    }
  ],
  "impact": "degraded",
  "recurrence_key": "headline-rate-without-composition-guard",
  "tags": ["research", "denominator", "decision-quality"]
}
```

Why this is useful: no single fact is enough. The smallest actionable pivot is a coupled metric set.

### 13.4 Distinct anchor related by symptom

```json
{
  "kind": "relation",
  "from": {
    "store": "/repo/.local/reports/friction/events.jsonl",
    "event_id": "evt-0048"
  },
  "to": {
    "store": "/repo/.local/reports/friction/events.jsonl",
    "event_id": "evt-0032"
  },
  "relation_kind": "same_symptom",
  "evidence": "Both failed as Playwright strict-mode locator errors, but one was caused by a hidden alternate control and the other by two visible controls sharing the same accessible name. The same upstream control would not prevent both."
}
```

Why this is useful: the records remain discoverably related without making the later event inherit a false root cause.

### 13.5 Verified resolution

```json
{
  "kind": "resolution",
  "targets": [
    {
      "store": "/repo/.local/reports/friction/events.jsonl",
      "event_id": "evt-0042"
    }
  ],
  "disposition": "mended",
  "hazard_active": false,
  "action": "Changed explicit repository-root handling so physical routing and recorded identity derive from the same canonical root.",
  "verification": "A command executed in repository A with --repo-root B wrote only to B, and a conflicting explicit events file was rejected.",
  "references": [
    "plugins/friction-diagnostics/skills/friction-diagnostics/scripts/_common.sh",
    "plugins/friction-diagnostics/skills/friction-diagnostics/tests/smoke-posix.sh"
  ],
  "residual_risk": "Shared network filesystems remain outside the supported contract."
}
```

Why this is useful: the resolution separates the code change, proof, and remaining boundary.

### 13.6 Append-only metadata amendment

```json
{
  "kind": "amendment",
  "target": {
    "store": "/repo/.local/reports/friction/events.jsonl",
    "event_id": "evt-0042"
  },
  "changes": {
    "add_tags": ["storage-routing", "provenance"]
  },
  "reason": "Assigned during Mend after confirming the shared root cause."
}
```

Why this is useful: later taxonomy is visible without modifying the historical event.

## 14. Prioritized delivery roadmap

### Phase 0: correctness, privacy, and enforced tests

This phase is the minimum safe local-store release.

1. Centralize path resolution and make `--repo-root` truthful.
2. Split read-only discovery from write/create behavior.
3. Enforce user-only permissions.
4. Recursively sanitize every persisted and displayed string.
5. Make malformed-input recovery safe.
6. Centralize bounded lock ownership and cleanup.
7. Validate the store before append.
8. Emit the committed receipt before derived work.
9. Remove `eval` and executable interpolation.
10. Add doctor and explicit repair-tail behavior.
11. Add one canonical local test command.
12. Make CI select that command for every plugin change.

Exit criteria:

WHEN Phase 0 is complete THEN the privacy, routing, lock, fault-injection, corruption, and CI-selection matrices in section 9 SHALL pass on both packaged host variants.

### Phase 1: trigger precision and lower-friction use

1. Make Capture and Mend descriptions disjoint.
2. Replace blame-oriented source language.
3. Generalize evidence beyond text.
4. Permit coupled pivot information.
5. Scale decision reconstruction with stakes.
6. Use compact filing disclosure by default.
7. Link active references and slim the main skill.
8. Add bounded query defaults and session-aware summaries.
9. Correct capability and dependency metadata.
10. Add deterministic trigger and silence evaluations.

Exit criteria:

WHEN Phase 1 is complete THEN the same behavioral prompt matrix SHALL demonstrate intended activation, nonactivation, and Capture/Mend exclusivity on both supported hosts.

### Phase 2: lifecycle and relationship pilots

1. Rename current “open” state to “unmended” where appropriate.
2. Run one user-authorized, real end-to-end Mend on an existing corpus.
3. Pilot richer resolution dispositions and explicit verification.
4. Pilot append-only amendments.
5. Pilot relations for same symptom, causal dependency, duplicate, and superseded hypothesis.
6. Add scoped locked trap upsert and removal.
7. Observe whether a later session reads a published trap and changes behavior.
8. Measure false closure and false recurrence grouping before making new fields mandatory.

Exit criteria:

WHEN Phase 2 is complete THEN at least one real cluster SHALL have source inspection, an evidence-backed mend or explicit residual hazard, a resolution record, a validated trap update when needed, and a later-session observation of the feed-forward behavior.

### Phase 3: measured scale

1. Add bounded cursor pagination and streaming output.
2. Measure 1,000- and 10,000-record stores.
3. Optimize only the demonstrated bottleneck.
4. Decide whether full-index rebuild on every append remains acceptable.
5. Keep alternative adapters deferred unless a real multi-host workflow appears.

## 15. Non-goals and cautions

### 15.1 Do not turn the plugin into telemetry for every failure

The surprise gate is more valuable than event volume. Expected failures and routine status should remain excluded.

### 15.2 Do not auto-mend from one incident

Immediate automatic source rewriting would destroy the capture/mend separation and encourage overfitting.

### 15.3 Do not infer consequence or severity

The system may preserve a reported consequence. It should not manufacture one from keywords or workflow disruption.

### 15.4 Do not silently merge semantic duplicates

Similarity can suggest candidates. Consolidation should remain an append-only, reviewable decision.

### 15.5 Do not claim distributed safety from local locking

Same-host JSONL writes do not establish safety on network filesystems, synchronized folders, containers with independent PID spaces, or multiple hosts.

### 15.6 Do not build an MCP service or database merely for architectural cleanliness

The current evidence supports repairing local persistence. A service introduces authentication, availability, tenancy, migration, and operational concerns without a demonstrated need.

### 15.7 Do not make every proposed field mandatory at once

Relations, consequence, amendments, and richer dispositions should be tested against actual Mend work. A foundational model becomes brittle when theory is mistaken for observed need.

### 15.8 Do not hide unsupported claims behind passing smoke tests

The 18-scenario suite establishes substantial happy-path and compatibility behavior. It does not establish complete privacy, crash consistency, multi-host safety, activation precision, or real-world Mend effectiveness.

## 16. Decision log

### 16.1 Implement now: directly evidenced

- Uniform recursive redaction.
- Private filesystem modes.
- Safe malformed-input handling.
- Truthful repository routing.
- Bounded locks.
- Committed receipt ordering.
- Removal of executable interpolation and `eval`.
- Consistent cleanup.
- Honest append-only semantics.
- Store integrity checks.
- CI selection for the full plugin.
- Bounded query defaults.
- Disjoint Capture/Mend descriptions.
- Best-available-primary-evidence language.
- Neutral prediction-basis language.
- Compact filing disclosure.
- Linked active references.
- Honest write-capability metadata.

### 16.2 Pilot: supported by observed pressure but shape unsettled

- Append-only metadata amendments.
- Related-versus-recurrence relationships.
- Richer resolution dispositions.
- Explicit verified closure during ordinary work.
- Separate consequence dimension.
- Scoped trap upsert and removal.
- More sophisticated cluster suggestions.

### 16.3 Adversarial recommendations requiring real-domain validation

- Physical-world measurement evidence.
- Creative-response evidence.
- Distributed organizational knowledge as pivot information.
- Person or environmental-signal source kinds.
- Safety-specific consequence ontology.

### 16.4 Explicitly deferred

- Remote service persistence.
- MCP-backed canonical storage.
- Shared database tenancy.
- Globally unique identifier migration for the local JSONL product.
- Mandatory actor/workspace ontology.
- Automatic semantic merging.
- Automatic source edits.

## 17. Further questions that should remain open

1. What is the measured precision and recall of Capture activation on real mid-task surprises?
2. Does a compact anchor preserve enough evidence for a later mender, and where is the lower bound?
3. How often do current recurrences share only symptoms rather than preventive causes?
4. What fraction of unmended anchors were already handled during ordinary work?
5. Can explicit verified closure be added without encouraging self-exonerating or premature resolution?
6. Which trap-publication operation best preserves unrelated entries during a scoped Mend?
7. Does a future session actually read `known-traps.md`, and can changed behavior be observed?
8. At what corpus size does full-stream validation or index rebuilding become the dominant cost?
9. Which non-software domains generate enough real events to justify new source or consequence types?
10. Are multi-host writers a real requirement, or is local per-repository storage the correct permanent boundary?

## 18. Final assessment

### Product verdict

Friction Diagnostics is the right product shape for preserving reusable surprise. Its distinctive value is the combination of prior prediction, prediction basis, actual evidence, decision context, and pivot information. That cognitive kernel is stronger than ordinary logging and generalized successfully across the different kinds of agent work encountered during the DiffHound build.

### Implementation verdict

The current version is useful for controlled internal local use, but it should not yet be described as a safe audit-grade or universal foundation. Privacy, routing, locking, commit signaling, schema enforcement, corruption handling, trigger ownership, and CI selection all need concrete repair.

### Highest-leverage change

Build one deterministic persistence boundary and make every ingress path, lifecycle command, query, and derived view use it. That single move eliminates the largest classes of divergence: inconsistent sanitization, misleading routing, unbounded locks, ambiguous commit state, duplicated validation, and inconsistent identity.

### What should happen next

Implement Phase 0 as one coherent delivery slice, not a series of cosmetic documentation edits. Then tighten the skill language and run cross-host behavioral evals. Only after the local store and trigger boundaries are reliable should the team pilot richer relationships, resolutions, and trap lifecycle.

### Readiness statement

- **Concept:** ready to preserve and invest in.
- **Capture happy path:** substantively working.
- **Local persistence security:** not ready without hardening.
- **Failure and recovery semantics:** not ready.
- **Trigger precision:** not yet automatically demonstrated.
- **Mend mechanics:** smoke-tested but not field-validated end to end.
- **Cross-domain generality:** conceptually strong, empirically incomplete.
- **Multi-host or shared-service operation:** not established and not currently justified.

The recommendation is therefore: **proceed after the named Phase 0 corrections, preserve the cognitive model, and resist premature platform expansion.**
