# Helper Contract

Load this route only after deterministic custody or durable view packaging has been selected. The bundled `split-test` tool preserves mechanical commitments, native payloads, and package integrity; it does not define comparison policy, create observations, compose instructions, launch workers, choose reviewers, judge semantic validity, invent criteria or scores, aggregate evidence, render authored views, or select a winner.

Use `<skills-file-root>/scripts/split-test` on POSIX hosts and `<skills-file-root>/scripts/split-test.ps1` from PowerShell. The launchers select a supported committed binary and fail concisely when the host is unsupported. Commands emit compact JSON or JSONL on success and short `error:` plus `hint:` lines on ordinary failure.

## Role-neutral custody

```text
split-test init ROOT
split-test add-commitment ROOT COMMITMENT_SPEC.json
split-test add-work-set ROOT WORK_SET_SPEC.json
split-test prepare-work ROOT SET_ID UNIT_ID WORK_SPEC.json
split-test seal-work ROOT SET_ID UNIT_ID TERMINAL.json
split-test close-work-set ROOT SET_ID CLOSURE.json
split-test publish ROOT PUBLICATION_SPEC.json
split-test reveal ROOT REVEAL_SPEC.json
split-test events ROOT [SCOPE_ID] --format jsonl
split-test receipt ROOT [SCOPE_ID]
split-test status ROOT
```

`ROOT` is an explicit absolute path. `init` accepts only an existing empty directory and makes controller custody private. Every later command verifies the content-addressed event chain and retained sealed payloads from any current working directory. Canonical manifests contain relative paths; operational output contains absolute paths.

The open schemas are `split-testing-workspace.v2`, `split-testing-commitment.v2`, `split-testing-work-set.v2`, `split-testing-work.v2`, `split-testing-terminal.v2`, `split-testing-work-closure.v2`, `split-testing-publication.v2`, and `split-testing-reveal.v2`. Supplied specifications retain their original bytes and unknown fields. A commitment may contain any prospective controller policy. The helper binds references to frozen commitments without requiring policy categories or judging their adequacy.

`prepare-work` freezes the work specification and every declared effective-input file before returning a dedicated absolute workspace. Record unavailable ambient inputs as unavailable; never reconstruct or invent them. Directory separation is not an access-control, memory, freshness, blinding, or process boundary. The helper exposes no worker-side controller mutation command, but it cannot prevent a worker with the same host authority from reaching the custody root or sibling paths; enforce consequential separation through the worker's user, container, sandbox, mounted paths, or tool permissions.

`seal-work` captures the workspace into an independently retained controller payload without changing the source and records one `split-testing-terminal.v2` event. Later source mutation or absence is reportable operational state; it cannot rewrite or invalidate an intact retained payload. Its `event` is only `returned`, `spawn-failed`, `timed-out`, `signaled`, `controller-aborted`, or `lost`. Further observed facts remain uninterpreted. A mechanical event never establishes task success, admissibility, semantic correctness, or valid infrastructure.

`close-work-set` must account for every frozen unit and rejects silent omission, addition, or replacement. Closure finalizes the set: first-time `prepare-work` and `seal-work` operations are then forbidden, while an exact replay of an already retained operation remains idempotent. A missing unsealed workspace can be accounted for truthfully as `lost`; its absence is not converted into task failure or a globally invalid controller history. `publish` must account for every frozen work-set unit as admitted or excluded with a reason and the applicable frozen commitment references. Admission and sealing remain separate from semantic validity. The helper retains excluded and failed work.

Blind publication uses deterministic opaque identifiers scoped by a private workspace secret and the publication identity. Published paths and identifiers do not reveal private condition meaning, but the helper cannot detect identity leaked inside controller-authored or native payload content. `reveal` creates a physically separate package and refuses to proceed until every named closure prerequisite exists and verifies; a blind package never contains a concealed mapping.

State-changing commands serialize controller writes under a lock. Workers never append to shared JSONL. Before a generated record or output becomes visible, its pending crash marker binds the exact custody-record digest; recovery fails closed if those bytes changed. If a retained or public effect exists but its exact bound custody record does not, recovery preserves the original marker and fails closed rather than letting another input adopt that effect. Each event binds both its decision-relevant content digest and the exact generated custody-record bytes; `events` emits that verified chain as a deterministic control-plane projection, not the evidence source of truth. Repeating a completed command with unchanged input is idempotent, while reuse of an identity with different bytes fails.

When an event history would waste agent context, `events` accepts `--after-sequence N` and `--max-items N`; omitting them returns the complete selected history. These filters change only the emitted projection, never retained custody. A bare `SCOPE_ID` selects `work-set:<id>`. Use the canonical typed forms `commitment:<id>`, `work-set:<id>`, `work:<set-id>/<unit-id>`, `publication:<id>`, or `reveal:<id>` for every other scope; typed compound work references keep duplicate unit IDs and namespace collisions distinct.

`status` verifies controller records and retained evidence, and reports later live-workspace drift or absence as nonfatal operational diagnostics. The retained sealed payload remains publication authority unless a prospectively frozen controller policy gives that source-state observation another consequence.

The portable capture profile binds relative topology, regular-file bytes, empty directories, symlink targets, and executable-bit state. It rejects absolute or escaping symlinks and unsupported special files. It deliberately excludes hardlink identity, ownership, non-executable permission details, timestamps, ACLs, extended attributes, sparse layout, and platform metadata from portable-content claims. Capture never changes source permissions.

The assurance is content-addressed, consistency-checked, and append-only through the public interface under a trusted-controller model. The internal chain is not hostile-user tamper evidence. `receipt` emits a compact chain-head checkpoint; claim tamper evidence only relative to an externally retained receipt, signature, transparency record, Git checkpoint, or equivalent trusted anchor.

All schema-1 workspaces and commands, and the unreleased round/run/review schema-2 workspace, are rejected. There is no migration, compatibility reader, legacy verifier, or fallback writer.

## Durable derived views

```text
split-test view seal ROOT VIEW_SPEC.json
split-test view verify ROOT
split-test view receipt ROOT
split-test view serve ROOT [--bind 127.0.0.1] [--port 0]
```

`VIEW_SPEC.json` uses `schema: derived-evidence-view.v1`, non-empty `source_refs`, and non-empty relative `entrypoints`. It may include `derivation_refs`, `runtime_refs`, `external_dependencies`, `interpretive_disclosures`, `extensions`, and arbitrary unknown fields. Supplied bytes are retained exactly. A reference object containing `path` declares a local package asset; an opaque value may identify externally retained evidence or a dependency.

`view seal` captures the arbitrary authored payload and writes a deterministic manifest plus an offline evidence-reader shell. `view verify` checks path containment, entrypoints, declared local assets, captured digests, mutation, and package consistency without running authoring code or interpreting the view. `view receipt` emits an externally retainable checkpoint. `view serve` verifies the retained package, then injects an ephemeral delivery nonce only into the served shell response and requires the matching virtual marker through a read-only loopback HTTP boundary and capability-scoped URL for correct MIME handling; the nonce and URL are operational access state, not evidence or shareable publication links.

The evidence reader displays package identity, source and derivation references, dependencies, disclosures, entrypoints, and raw-evidence access while embedding authored entrypoints inside the declared browser boundary. A directly opened snapshot exposes technical metadata and static inspection only; it does not execute or navigate active authored content. Use `view serve` for active entrypoints and correct MIME handling. The loopback server reads each response into a verified buffer and is not a streaming or range-media server; use a fit authoring or delivery environment when large or seekable media requires one. Packages use no CDN, network dependency, service worker, analytics, or hidden persistence. Blind and revealed readers are physically separate packages.

If an authored entrypoint communicates with the reader, use the open `evidence-view-message.v1` envelope. Technical events may cover readiness, resizing, and opening an opaque evidence reference; arbitrary namespaced events and unknown payload fields remain allowed. The transport standardizes the boundary, not the evidence semantics.

The reader and helper do not choose visual form, transformation, meaning, aggregation, or utility. If a view can change the consumer's action, treat its presentation as an observation instrument and test the relevant effect. The orchestrator remains responsible for semantic inspection, regeneration claims, accessibility inspection, and verification at the delivered consumer boundary.
