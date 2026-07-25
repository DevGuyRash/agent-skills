# Friction Diagnostics Improvement Report

**Report ID:** `a13a0ba6-0c89-4d13-99e1-efc5c96c6f64`  
**Generated:** 2026-07-14  
**Scope:** Friction Diagnostics capture, Friction Mend, persistence, lifecycle, feed-forward integration, packaging, tests, and real use during the EdgeCourt build  
**Disposition:** Read-only assessment and implementation proposal; no plugin source changes were made by this review

## Executive verdict

The EdgeCourt engagement produced enough real evidence to improve Friction Diagnostics materially. The correct response is a focused hardening program, not a wholesale redesign.

The plugin's cognitive kernel is strong:

> Capture a genuine divergence between prediction and reality while the prior belief is still recoverable; preserve what supported that belief, what actually happened, and the information that would have changed the decision; converge later through deliberate mending.

That model proved useful across browser tooling, GUI integration, Rust compilation, filesystem behavior, parallel-agent interference, test timing, contract interpretation, and data identity. It is meaningfully different from an error log, issue tracker, generic telemetry system, or postmortem template.

The implementation surrounding that core is not yet safe or correct enough to serve as a universal foundational substrate. The highest-leverage work is concentrated:

1. Make persistence secure and unambiguous.
2. Fix lifecycle and cross-store identity.
3. Ground the feed-forward trap artifact in the canonical corpus.
4. Make read operations genuinely read-only.
5. Separate ambient activation, capture, inspection, proposal, and applied mending.
6. Test resulting behavior instead of emitted wording.
7. Prove one complete real-world Mend cycle before expanding the ontology substantially.

The most important preservation principle is equally clear: do not weaken the surprise gate while hardening everything around it.

## Evidence and method

This report is self-contained, but its conclusions were derived from direct inspection and deterministic probes of:

- Both complete logging and mending skills.
- The event schema, field rubrics, integration documentation, and Mend playbook.
- Capture, recurrence, resolution, query, reporting, clustering, summary, hook, and trap-publication scripts.
- Codex and Claude plugin manifests.
- Packaging configuration, vendored copies, local verification recipes, and CI selection.
- Trigger prompts and behavioral-eval artifacts.
- The prior long-form improvement report present in the repository.
- EdgeCourt's durable event corpus: 19 records comprising 14 anchors and 5 recurrences.
- A cross-repository corpus that contained 91 raw records at the end of the audit: 74 anchors, 17 recurrences, and zero resolutions. Eight of those anchors were audit findings created while exercising the plugin itself.
- Sparse thread evidence around browser failures, GUI integration defects, Playwright timeouts, parallel-agent conflicts, file truncation, and recovery work.
- Five independent subagent reviews covering thread evidence, logging, mending, packaging/evals, and a skeptical no-change case.

Verification completed during the review:

- All 18 POSIX smoke-test sections passed.
- All 34 relevant packaging and plugin-port unit tests passed.
- Vendored shared copies were byte-identical.
- Static Codex and Claude plugin validation passed.
- The plugin round-tripped through the host converter without plugin-specific warnings.
- Live `codex plugin list` and `claude plugin list` could not run because their optional native binaries were absent.
- The smoke suite passed despite four newly reproduced lifecycle or integrity defects. That is a test-scope problem, not evidence that the defects are theoretical.

The review distinguished three evidence classes:

- **Verified defect:** reproduced directly or demonstrated by implementation and live corpus evidence.
- **Evidence-backed pilot:** a product change supported by real incidents but not yet proven enough to mandate broadly.
- **Future option:** an architectural direction that should remain optional until an actual environment demands it.

## Holistic assessment

### The product's core idea is already strong

The surprise gate is the product's most important mechanism. It correctly excludes:

- Expected red tests.
- Engineered error paths.
- Known external limitations.
- Ordinary task status.
- New user instructions.
- Failures that supplied no reusable learning.

That restraint kept the corpus comparatively high-signal. Expanding capture to every inconvenience would destroy the product's differentiation.

The combination of expectation, prediction basis, actual result, response context, and pivot information also worked. It preserved why an agent's model was wrong rather than merely storing the final error.

EdgeCourt examples include:

- A chart default changing because another workflow introduced a lower-granularity coverage row.
- Delayed modal focus erasing user and test input.
- Shell controls accepting interaction before initial routing completed.
- Same-payload ingests colliding because identity still depended on coarse time.
- A successful global ingest leaving an already-open page stale.
- Shared ports and DTO definitions changing during parallel-agent work.
- A failed patch unexpectedly truncating an untracked source file.

These are integration-level model failures that ordinary logs flatten into symptoms.

### Capture worked; the learning loop did not close

The EdgeCourt corpus demonstrates successful logging:

- Repeated Chrome availability failures used one anchor and cheap recurrence pointers.
- Repeated Playwright timeout behavior falsified the initial causal hypothesis without rewriting history.
- Session references distinguished root and subagent activity.
- The bounded dashboard made orientation much cheaper than reading the full stream.
- Several events were captured before code changes, preserving the original model.

However:

- The observed cross-repository corpus contained zero formal resolutions.
- No observed repository had a published `known-traps.md`.
- At least eight EdgeCourt anchors described fixes or guardrails completed during the same task, yet all remained open according to corpus lifecycle.
- Two browser-related clusters reached three sightings without becoming feed-forward knowledge.
- A later session retried the unsupported browser snapshot operation despite earlier exact captures.

This does not prove that Mend is ineffective. Mend is intentionally user-request-only, and no complete real Mend cycle occurred. It does prove that the claimed capture -> mend -> resolve -> distill -> feed-forward loop is not yet operationally established.

The next major product experiment should therefore be one genuine Mend cycle, not a large speculative schema expansion.

### The model is general; the current adapter is not

The cognitive model plausibly generalizes to writing, research, design, operations, physical observations, and decision-making.

The current implementation is specifically:

- Filesystem-dependent.
- Linux/POSIX-oriented.
- Git-repository-centric.
- Text-evidence-centric.
- Single-host.
- Dependent on shell, `jq`, Python, Git, hashing utilities, and a packaged Linux renderer.

That limitation is acceptable when stated honestly. It becomes a problem when the local JSONL adapter is treated as the universal product itself.

The appropriate architecture is hybrid:

1. A tiny ambient prediction-divergence policy.
2. A capture skill for explicit composition and manual filing.
3. An explicit Mend workflow for convergence and source changes.
4. One deterministic persistence implementation.
5. Local JSONL as the initial single-host adapter.
6. Optional storage adapters only when real environments require them.

### Mending targets the wrong abstraction

The current outcome contract expects the mender to edit the `sources[].ref` artifact that misled the agent or close the event as `wontfix`.

Real incidents do not fit that binary. The correct prevention surface may be:

- A tool implementation.
- A wrapper.
- A capability preflight.
- A runtime assertion.
- A test.
- A workflow ordering change.
- Configuration.
- Documentation placement.
- A known-trap warning.
- An upstream issue plus a local mitigation.

The prediction basis is evidence about why the agent believed something. It is not necessarily the artifact that should be changed.

### Explicit separation remains important

Capture and Mend should remain separate. One surprising event should not autonomously rewrite instructions.

The separation should become precise:

- Capture owns new worthwhile divergences, known-trap occurrences, and explicit requests to log an incident.
- Mend owns requests to triage, resolve, cluster, distill, or repair an existing corpus.
- Inspection and proposal must be distinct from application.
- Reviewing the plugin itself should not make both skills compete for ownership.

## What worked and should be preserved

- The strict surprise gate.
- Immediate capture at divergence.
- Cheap recurrence pointers.
- Non-destructive duplicate-key soft stops.
- Expected-versus-actual structure.
- Prediction basis and pivot information.
- The free-form note escape hatch.
- Capture/Mend separation.
- Local-first operation with no required network service.
- Bounded dashboards and trap artifacts.
- Append-only resolution as a concept.
- Store talkback after filing.
- Session attribution.
- Legacy-record compatibility.
- Mechanical clustering being explicitly nonbinding.
- Human judgment over automatic semantic merging.
- Original evidence remaining available behind bounded summaries.

## Atomistic findings

### P0: lifecycle correctness

#### 1. A recurrence does not reopen a resolved cluster

The reporter says:

> `File as recurrence (reopens the cluster)`

Lifecycle queries construct a permanent set of every anchor ever named by a resolution. A later recurrence cannot remove an anchor from that set.

Verified sequence:

1. File an anchor.
2. Resolve it.
3. Follow the advertised `--recur` path.
4. Query open anchors and recurrences.
5. Both queries return zero.

The smoke test asserts that the words `reopens the cluster` are printed but never follows the advice and tests resulting state.

Recommended correction:

- Implement one order-aware lifecycle reducer shared by query, reporting, dashboard, talkback, and clustering.
- Use physical stream order, not one-second timestamps, as the authoritative order within a JSONL store.
- Define either:
  - recurrence after the latest resolution reopens; or
  - an explicit `reopen` record is required.
- Test file -> resolve -> recur -> open -> resolve again -> closed across every consumer.

#### 2. Cross-repository lifecycle collides on local IDs

Every store begins with `evt-0001`. Cross-repository queries flatten all stores and compare bare event IDs.

Verified result:

- Repository A resolves its `evt-0001`.
- Repository B has an unrelated open `evt-0001`.
- A combined `--scan-dirs --open` query incorrectly closes B's event too.

Recommended correction:

- Use `(canonical store ID, event ID)` as identity, or assign globally unique internal record IDs.
- Attach physical source-store provenance while loading; do not trust only the record's own `events_file`.
- Qualify every cross-store recurrence, resolution, and trap pointer.
- Test two stores with colliding anchors, recurrences, and resolutions.

These lifecycle defects block any claim that cross-repository open/resolved reporting is trustworthy.

### P0: trap integrity and feed-forward safety

#### 3. `known-traps.md` accepts fabricated pointers and arbitrary prose

The trap publisher verifies only:

- At least one line begins with `- [`.
- No more than 15 such lines.
- Total output is at most 8 KB.

A disposable probe successfully published:

- A nonexistent key.
- Nonexistent `evt-9999`.
- Fabricated `x999`.
- Future date `2099-12-31`.
- Arbitrary trailing prose.
- A header reporting zero open events.

This file is intended to be read before acting, so unvalidated text is also a prompt-injection surface.

Recommended correction:

- Accept structured `key`, `anchor`, and bounded avoidance guidance.
- Derive counts, dates, state, and titles from the validated event store.
- Validate that the anchor exists, belongs to the key, is publishable, and uses qualified store identity.
- Reject extra lines, control characters, multiline guidance, and mismatched pointers.
- Generate Markdown mechanically.
- Mark event, transcript, tool, web, and existing trap content as untrusted evidence, never instructions.
- Add compare-and-swap publication so concurrent menders cannot silently overwrite one another.

#### 4. Trap decay cannot depend on absence of recurrence

The current guidance says traps that stop recurring should decay out. The trap file is itself a prevention mechanism. Non-recurrence may mean the warning is working.

Sunset traps only when there is positive evidence:

- The source or tool changed.
- The environment or version no longer applies.
- The hazard was tested as absent.
- The trap was superseded.
- An owner explicitly accepted retirement.

### P0: persistence security and durability

#### 5. The primary JSON path does not sanitize all persisted strings

JSON `sources[].ref` and `sources[].claim` can bypass the normal text sanitizer. Resolution references and other metadata have similar gaps. A synthetic bearer token survived unchanged in a disposable store.

Recommended correction:

- Parse first and recursively sanitize every persisted string using one canonical policy.
- Cover narratives, sources, tags, notes, titles, resolution action/ref/note, repository metadata, malformed-input diagnostics, summaries, and traps.
- State that `verbatim` means minimum necessary primary evidence after required privacy redaction.
- Test synthetic secrets through every field and every ingress/error route.
- Do not claim that pattern matching alone makes arbitrary diagnostic content safe.

#### 6. Store permissions depend on the caller's umask

The observed EdgeCourt event file was mode `0644`. It contained paths, reasoning, observations, and tool output.

Recommended correction:

- Set `umask 077` before creating store or temporary artifacts.
- Directories should be `0700`; files should be `0600`.
- Harden pre-existing permissive files safely.
- Reject unexpected symlink targets unless explicitly authorized.
- Test under `umask 0022`.

#### 7. A fresh repository can expose `.local/` to Git

The plugin creates `.local` but does not prove that it is ignored. A disposable first filing produced `?? .local/`.

Recommended correction:

- First-write preflight should verify the store is ignored.
- If the plugin creates the directory, create a scoped ignore boundary or fail with precise opt-in instructions.
- Add a regression asserting a fresh repository remains clean after first write.

#### 8. Locks can block forever

Capture, index, and resolution use directory-lock loops without a deadline. A crash after creating the lock directory but before publishing a valid PID can permanently block the writer.

Recommended correction:

- One shared lock implementation.
- Bounded timeout.
- Owner token with host, PID, creation time, and process-start identity.
- Safe stale-lock reclamation.
- Clear diagnostics and a read-only doctor command.
- `flock` when available with a deliberately tested fallback.
- Concurrency, interruption, dead-PID, reused-PID, and malformed-owner tests.

#### 9. A committed append can be reported as failure

The current sequence is:

1. Append canonical record.
2. Rebuild derived index.
3. Generate talkback.
4. Print durable receipt.

If derived work fails, the event may already exist while the command exits unsuccessfully. Retrying can create duplicates.

Recommended correction:

- Define append as the commit point.
- Emit a machine-readable receipt immediately after append.
- Treat derived-view failure as a warning.
- Add idempotency keys.
- Validate the existing stream before writing.
- Add fault injection after every stage.

#### 10. IDs are allocated from line count

`wc -l + 1` can collide with sparse, repaired, imported, malformed, or duplicated streams.

Use either:

- Maximum validated numeric ID plus one for the local display ID; or
- A globally unique internal ID with a separate local display sequence.

Reject duplicate IDs before append.

#### 11. Store-controlled data reaches executable contexts

The summary renderer interpolates a stored timestamp into Python source. JSON loading also uses shell `eval` over assignments derived from payload data, albeit shell-quoted.

Recommended correction:

- Pass data through arguments, stdin, or files.
- Remove stored-data interpolation into `python -c`.
- Remove JSON-to-shell `eval`.
- Add hostile-but-valid store fixtures proving no code or subprocess executes.

#### 12. `Append-only` is not currently true

`--add-tags` and alias operations rewrite prior event lines.

Either:

- Introduce append-only amendment records and derive effective metadata at read time; or
- Narrow the contract honestly to say narrative content is immutable while metadata may be atomically rewritten.

For a foundational audit stream, append-only amendments are the stronger design.

### P0: routing and read-only behavior

#### 13. `--repo-root` can label one repository while writing into another

When invoked from repository A with `--repo-root` B but without `--events-file`, physical storage can remain in A while metadata says B.

Recommended correction:

- One pure target resolver.
- Explicit events file has highest precedence.
- Explicit repository root controls both destination and recorded identity.
- Current working directory is only the fallback.
- Canonicalize and verify target/metadata agreement before writing.

#### 14. Store selection can split one repository's history

Selection prefers `.local` if it later appears; otherwise it chooses the lexicographically first `.local*`. A repository can begin logging in `.local-test`, later create `.local`, and silently fork its history.

This contributed to EdgeCourt appearing twice in the cross-repository report.

Recommended correction:

- First search for existing `.local*/reports/friction/events.jsonl`.
- If exactly one exists, continue using it.
- If several exist, require explicit selection or a durable store pin.
- Aggregate reports by canonical repository identity while disclosing constituent stores.

#### 15. Read-only queries create directories

A default `query-friction.sh` in a fresh repository creates `.local/` and then fails because no store exists.

Recommended correction:

- Readers use non-creating path discovery.
- Writers use creating path resolution.
- A missing store should produce a valid empty state or a non-mutating informational error.
- Snapshot the filesystem before and after query, report, cluster, doctor, and status commands in tests.

#### 16. Cross-repository reporting groups by recorded path but displays repository root

The live report displayed EdgeCourt twice because records in the same physical store contained both relative and absolute `events_file` metadata. Aggregation keyed on the stored path while the UI displayed the same repository root.

Recommended correction:

- Treat physical source-store identity as query-time provenance.
- Group repository summaries by canonical repository identity.
- Report repository count and store count separately.
- Do not let stale record metadata define the aggregation key.

### P0: verification and activation

#### 17. CI does not select the smoke suite for most plugin changes

The CI selector is tied to the packaged table-renderer watch set. Synthetic checks returned `false` for changes to:

- Capture writer scripts.
- Capture `SKILL.md`.
- Mend scripts.
- Hooks.
- Plugin metadata.

Normal repository verification also omitted the integrated smoke suite.

Recommended correction:

- Add one canonical `test-friction-diagnostics` command.
- Run it for any `plugins/friction-diagnostics/**` change.
- Include it in the normal repository verification path.
- Test the change detector itself.

#### 18. Trigger and behavioral eval files are not executed

The prompt fixtures are stored as JSON, but no runner invokes them. Existing positives often contain explicit words such as `surprised`, `log`, or `friction`, so they do not prove ambient mid-task activation.

Add trajectory-level evaluations covering:

- Unexpected reusable divergence during an unrelated task.
- Expected red test.
- Unexpected but non-reusable command failure.
- Known-trap recurrence.
- Similar symptom with a different preventive fact.
- Read-only plugin review.
- Explicit Mend request.
- No filing and no final mention.
- Filing during unrelated work with compact disclosure.
- Software, research, writing, design, operations, and non-text evidence.

#### 19. The smoke test protects false copy instead of behavior

All 18 sections passed while the false-reopen state, cross-store ID collision, fabricated trap publication, and read-only filesystem mutation remained reproducible.

The testing principle should be:

- Follow the action the product recommends.
- Observe resulting state through the public interface.
- Assert every consumer agrees.
- Do not treat emitted guidance text as proof of the operation it describes.

#### 20. Startup integration is overstated

The plugin says known traps are read at session start. The hook only exports session and transcript environment variables and intentionally emits no context. Trap reading requires manually installing an optional `AGENTS.md` snippet, which was not active in the audited repository.

Recommended correction:

- Preserve opt-in; automatic local-content injection has privacy and prompt-injection consequences.
- Qualify the claim as `read at session start when repository integration is enabled`.
- Add idempotent `enable-repo`, `status`, `doctor`, and `disable-repo` operations.
- Test main sessions, resumed sessions, and subagents across supported hosts.

#### 21. Manifest capability metadata says only `Read`

The plugin writes events, indexes, quarantine files, resolutions, and traps; Mend may edit project artifacts.

The manifest should accurately declare write capability if that field participates in permissions or user expectations.

### P1: reduce capture friction without weakening the gate

#### 22. `Minimal anchor` is not operationally minimal

The skill says short fields suffice, but the writer still requires the complete narrative field set and emits nudges for short reading and decision text.

Add a real minimal mode requiring:

- Best available primary evidence.
- Expected outcome and basis.
- One prediction basis.
- Workflow impact.
- Compact response-so-far.
- Key or computed fallback.

Do not issue depth nudges in minimal mode. Enrich append-only if the event recurs or proves consequential.

#### 23. Immediate filing and completed-history `decision` conflict

The skill says file at the moment of divergence, while `decision` asks for completed options, actions, and deviations. This encourages agents to wait until after fixing the problem.

Rename the concept to `response_so_far` or explicitly allow:

- Filed before responding.
- Only one option was visible.
- Response was reflexive.
- No response yet.

A later response or resolution record can add completion evidence.

#### 24. Evidence semantics overfit text

`Verbatim output`, mandatory quotation, and `what betrayed you` do not generalize to:

- Visual defects.
- Physical measurements.
- Missing events.
- State transitions.
- Stakeholder reactions.
- Correct documentation followed by an unsupported inference.

Use neutral prediction-basis language. Accept:

- Exact output when it exists.
- Exact wording when material.
- Measurement.
- Screenshot or artifact reference.
- State before/after.
- Explicit non-occurrence.
- Labeled firsthand observation.
- Honest uncertainty.

Do not force fabricated quotations.

#### 25. A pivot may be a minimal coupled set

The chart-default event required both:

- Coverage sorted ascending by granularity.
- Initial selection ignored the declared hourly default.

Neither fact alone explained the result.

Use `smallest sufficient actionable information unit`, allowing a tightly coupled set when one fact is insufficient.

#### 26. Workflow disruption is not consequence

`blocked | degraded | noisy | continued` describes the agent's workflow, not product or user consequence.

A noisy delayed-focus bug still erased input. A continued event could still produce false output or data exposure.

Retain workflow impact, and pilot an optional evidence-backed consequence field. Do not infer consequence automatically.

#### 27. Similarity guidance arrives too late

EdgeCourt filed two separate anchors for the exact same `incrementalAriaSnapshot` failure. Talkback reported a 1.00-similar prior event only after the new anchor had already been appended.

Add a pre-append high-confidence soft stop or atomic `convert this filing to a recurrence` action. Do not auto-merge semantically similar events.

#### 28. Recurrences need causal-model updates

The Playwright timeout recurrence falsified the original diagnosis. A recurrence currently has only actual outcome and free-form note.

Pilot optional:

- `hypothesis_update`
- `new_pivot_information`
- `what_differed`

This preserves cheap recurrence while recording why the prior workaround failed.

#### 29. Same symptom is not necessarily recurrence

The useful test is:

> Would the same missing information or upstream control have prevented both occurrences?

If yes, recurrence is appropriate.

If not, create a separate anchor and optionally relate it as:

- `related_to`
- `caused_by`
- `duplicate_of`
- `supersedes`

Pilot relationships; do not make them mandatory immediately.

### P1: make Mend represent reality

#### 30. Add dispositions beyond `mended` and prose-encoded `wontfix`

Useful dispositions include:

- `mended`
- `mitigated`
- `accepted_risk`
- `needs_evidence`
- `external_owner`
- `blocked`
- `invalid_or_noise`
- `duplicate`
- `superseded`
- `closed_no_further_action`

This prevents agents from choosing `wontfix` merely to satisfy a completion contract.

#### 31. Resolution requires verification evidence

A resolution currently needs only an action sentence; `ref` is optional.

A durable resolution should record:

- Disposition.
- What changed.
- Fix references.
- Verification status.
- Verification method and reference.
- Scope.
- Whether danger remains.
- Supersession relationships.

For `mended` and `mitigated`, require verification or an explicit unverified reason.

#### 32. Separate incident handling from hazard state

`At least one fix happened`, `the corpus was mended`, and `the danger can no longer recur` are different claims.

Track separately:

- Immediate incident handled.
- Prevention surface changed.
- Mend verified.
- Hazard still active.
- Further action required.

Until then, rename current `open` to `unmended anchor` and show anchor count separately from total open records.

#### 33. Add likely-repaired candidates, not automatic resolutions

Many EdgeCourt decisions say the source was changed and a regression added.

A read-only Mend report could flag likely resolution candidates based on:

- Decision text describing a change.
- Referenced files modified after the event.
- Verification references.
- No later recurrence.

These are hints requiring confirmation, never automatic closure.

#### 34. Add explicit inspect, propose, and apply modes

The trigger includes `review`, but the outcome contract assumes file edits, resolutions, and trap publication.

Modes should be explicit:

- Inspect/report: read-only.
- Propose: produce mends without applying them.
- Apply: mutate authorized artifacts and record provenance.

### P1: concurrent artifact safety

#### 35. Shared report filenames are collision-prone

The original improvement-report filename was reused by multiple concurrent agents and the user's intended copy was overwritten.

Recommended correction:

- Every independently produced report, proposal, export, and review artifact should receive a UUID or collision-resistant run ID at creation time.
- The UUID should be part of the filename and document metadata.
- A stable human-friendly filename may be generated later as an explicit pointer or selected canonical copy, never as the agents' shared write target.
- Artifact writers should use create-if-absent semantics by default and require an explicit overwrite flag.
- When a canonical pointer is needed, update it atomically after the uniquely named artifact has been verified.

This report follows that rule: `friction-diagnostics-improvement-report-a13a0ba6-0c89-4d13-99e1-efc5c96c6f64.md`.

### P2: bounded, evidence-backed scope expansion

The thread supports these expansions:

- Best-available non-text evidence.
- Durable outside-Git storage under an XDG user-state directory instead of system temp.
- Optional actor context for multi-agent events: task path, branch/worktree, command/PID, HEAD, and a privacy-conscious dirty-state indicator.
- Sparse, redacted transcript slices around event time rather than whole-transcript loading.
- Optional user-global tool/environment traps, kept separate from repository-domain traps.
- Qualified identities and storage adapters before multi-host sharing.
- Bounded queries, cursoring, field selection, and streaming before corpora reach thousands of records.

The thread does not yet justify:

- A mandatory remote service.
- A universal shared store.
- Autonomous Mend.
- Mandatory relationship or consequence fields.
- Automatic semantic merging.
- A fixed cross-domain taxonomy.
- Automatic global injection of local trap content.

## Workarounds observed in real use

### During EdgeCourt development

- Browser `domSnapshot()` failed with `incrementalAriaSnapshot is not a function`; screenshots and bounded DOM evaluation replaced it.
- Browser backends disappeared after successful discovery; sessions retried and retained fallbacks.
- Truncated command output contaminated JSON; outputs were recaptured with higher limits and parse/count checks.
- A shared Playwright timeout was split into an isolated test, then the diagnosis was revised when it recurred.
- A successful ingest left a page stale; refresh logic and an integrated GUI regression were added.
- Parallel-agent port reuse was handled by selecting a new isolated port rather than killing an unknown process.
- Concurrent DTO drift was escalated to the owning agent.
- A failed patch truncated an untracked file; the file was reconstructed and the server recompiled before continuing.
- Chart default, modal focus, and route-readiness defects were prevented through code changes and regression tests.

### During the plugin audit

- The bounded dashboard and targeted queries were used before reading full corpora.
- Explicit `--events-file` paths were used where repository routing or read-only behavior was suspect.
- The integrated smoke suite was run manually because normal CI selection did not cover the plugin's full surface.
- Direct artifact and event-corpus inspection replaced an unreliable thread lookup.
- Host-independent unit and conversion checks replaced unavailable live `codex` and `claude` plugin-list commands.
- A failed zsh glob was replaced with `find`-based discovery; this also exposed the need for cross-repository or global trap scope.
- Cross-repository lifecycle output was treated as raw evidence only after the bare-ID collision was reproduced.
- No real resolutions or trap files were published because the assignment asked for a proposal, not an applied Mend.
- A UUID-qualified filename was required after the shared conventional report name was overwritten by another agent.

Until persistence is hardened, cautious callers also need to:

- Pre-redact sensitive content.
- Use private umask settings.
- Pass an explicit canonical event path.
- Avoid relying on `--repo-root` for routing.
- Wrap writers in an external timeout if a stale lock is possible.
- Query before retrying an ambiguous failure.
- Avoid tag/alias mutation when strict append-only provenance matters.
- Interpret `open` as `no resolution record`, not `the product defect remains active`.
- Manually verify lifecycle rather than trusting the reopening message.

That is too much operational ceremony for a foundational substrate; the first implementation slice should eliminate these precautions.

## Recommended implementation order

### Phase 0: make existing claims true

1. Implement one order-aware, store-qualified lifecycle reducer.
2. Fix recurrence-after-resolution and cross-store ID collisions.
3. Ground trap publication in validated corpus records.
4. Make all readers non-creating and empty-state safe.
5. Enforce private storage modes and Git-ignore protection.
6. Recursively sanitize every persisted string.
7. Fix repository routing and stable store selection.
8. Add bounded locking and stale-lock recovery.
9. Establish append as commit point and add idempotent receipts.
10. Remove data-to-code interpolation and JSON-to-shell `eval`.
11. Resolve the append-only metadata contradiction.
12. Validate the complete existing stream before every write.
13. Add a read-only doctor for corruption, permissions, locks, routing, activation, and derived views.
14. Put the full plugin under one normal local/CI test target.
15. Make generated artifact names collision-resistant by default.

### Phase 1: reduce capture and activation friction

1. Separate Capture and Mend trigger ownership.
2. Add inspect/propose/apply Mend modes.
3. Implement a genuine compact anchor.
4. Replace blame- and text-dependent evidence language.
5. Make response reconstruction proportional.
6. Permit minimal coupled pivots.
7. Separate workflow impact from optional consequence.
8. Add pre-append high-confidence similarity routing.
9. Make final disclosure compact by default.
10. Qualify the session-start trap claim and add repository activation status.
11. Move outside-Git persistence to durable user state.
12. Minimize absolute path and session metadata.

### Phase 2: prove one Mend cycle

Use a real corpus and select:

- One repeated external/tool trap.
- One symptom family that may contain multiple root causes.
- One event whose source was fixed and verified during the original task.

Measure whether:

- An uninvolved mender can understand the records.
- Clustering uses the same-preventive-control rule.
- Verification evidence is sufficient.
- A trap line changes a later comparable session.
- A post-resolution recurrence correctly reopens.
- The upstream change reduces recurrence or enables earlier recognition.

Success is demonstrated prevention or earlier recognition, not merely lower open count.

### Phase 3: pilot ontology and scale changes

Only after that Mend pilot:

- Dispositions and verification records.
- Amendment records.
- Relationships.
- Typed non-text evidence.
- Optional consequence.
- Actor/workspace provenance.
- Federated global tool traps.
- Storage adapters.
- Pagination and large-corpus benchmarks.

## Metrics and Goodhart risks

Do not treat these as standalone success metrics:

- Events per day falling.
- Recurrence share rising.
- Open count falling.
- Resolution count rising.
- Trap count reaching the cap.

They can indicate improvement, under-reporting, over-grouping, premature `wontfix`, or worsening reliability.

More useful measures include:

- Time to verified mend.
- Age of high-impact unmended anchors.
- Verification coverage.
- Post-resolution recurrence rate.
- Failed-mend and reopened-cluster count.
- Time to recognition after a known trap.
- Accepted-risk inventory.
- Whether a trap was read before the relevant action.
- Whether later comparable work avoided or announced the same hazard.

## Explicit non-goals

- Do not replace the surprise gate with generic failure logging.
- Do not log every command or test failure.
- Do not treat expected red tests as friction.
- Do not automatically merge semantically similar events.
- Do not automatically rewrite instructions after one incident.
- Do not make mending autonomous.
- Do not load the full corpus into every session.
- Do not remove the bounded trap budget.
- Do not infer consequence from workflow disruption.
- Do not force a universal capture-time taxonomy.
- Do not make a remote service mandatory.
- Do not interpret absence of events as evidence of correct work.
- Do not treat event volume, recurrence share, or closure rate as success metrics by themselves.
- Do not adopt the entire proposed schema evolution in one migration.
- Do not abandon the local JSONL adapter for the single-host case merely because more scalable adapters may eventually exist.

## Readiness judgment

- **Cognitive kernel:** strong and worth preserving.
- **Logging usefulness:** demonstrated.
- **Cheap recurrence:** demonstrated.
- **Bounded corpus orientation:** demonstrated.
- **Local happy path:** functional.
- **Persistence safety:** not foundationally ready.
- **Lifecycle correctness:** not ready.
- **Cross-repository lifecycle reporting:** not trustworthy yet.
- **Trap publication integrity:** not ready.
- **Mend effectiveness:** unknown because no real complete cycle has occurred.
- **Non-software generality:** plausible, not yet demonstrated empirically.
- **Multi-host readiness:** no.
- **Highest-leverage engineering change:** one secure deterministic writer plus one order-aware, store-qualified lifecycle reducer.
- **Highest-leverage product experiment:** a real end-to-end Mend cycle with later behavioral verification.
- **Highest-leverage restraint:** preserve the surprise gate and resist turning the plugin into generic telemetry.

## Final recommendation

Friction Diagnostics has learned the right foundational lesson: the useful artifact is not the error alone, but the difference between the prior model and observed reality, captured before hindsight erases the decision context.

The next version should not primarily add more prose, taxonomy, or automation. It should make lifecycle, identity, privacy, publication integrity, read-only behavior, activation, and proof of mend true in code. Once those foundations are reliable, one real Mend cycle should determine which richer semantics actually earn their complexity.
