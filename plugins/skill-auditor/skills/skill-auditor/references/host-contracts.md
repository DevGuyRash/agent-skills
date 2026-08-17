# Host Contracts

Use this reference when the audit decision depends on what a host ingests, publishes, installs,
updates, resolves, or executes. Repository source, runtime ingestion, public submission, installed
state, and end-to-end invocation are separate evidence boundaries.

Identify the manifests, marketplace entries, installed caches, and host versions actually in scope.
Repository source is not runtime evidence when a host loads a cached copy. Compare the active skill
metadata and executable package with source before attributing routing or behavior to a recent edit.
When several cached copies exist and the active one cannot be identified, retain the ambiguity.

For a release-readiness claim on a mutable host-owned surface, retain current primary authority for
the release channel actually in scope and identify the consulted horizon. A bundled reporter,
repository schema, installed validator, or passing local host establishes only the contract and
version it implements; it cannot silently stand in for a newer publication or submission contract.
When current authority conflicts with an installed validator, preserve both observations and hold the
affected readiness claim until the intended channel is established.

Retain enough claim-specific source evidence for a fresh checker to recover a consequential external
premise without relying on the auditor's characterization. A moving URL alone may establish where to
look while leaving what was consulted unreproducible or unavailable. Preserve the source identity,
horizon, applicable passage or faithful concise note, and any ambiguity that could change the
finding; do not copy a large document or turn source capture into a report ritual.

For the hosts this repository publishes, OpenAI's rolling [plugin build
reference](https://developers.openai.com/plugins/build/plugins), [skill metadata
reference](https://developers.openai.com/plugins/build/skills), [submission error
reference](https://developers.openai.com/plugins/deploy/submission-errors), and current [Codex raw
manifest parser](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/manifest.rs)
describe different parts of the current contract. Anthropic's [Claude Code plugin
reference](https://code.claude.com/docs/en/plugins-reference) and [skill
reference](https://code.claude.com/docs/en/slash-commands) likewise separate package and skill
runtime behavior. Follow their current links rather than copying volatile allowed values into this
skill, and retain the exact source revision when reproducibility matters.

For an ingestion claim, follow the host's raw deserializer and resolution path through the form the
target actually supplies. A normalized type, prose example, validation schema, or official scaffold
may expose a narrower or different representation while the loader accepts a legacy form. Preserve
that source conflict and test the real consumer instead of turning one layer's shape into a rejection
claim.

Current Codex compatibility note, checked 2026-08-16: the rolling [raw manifest
parser](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/manifest.rs) accepts either
a string or a list for `interface.defaultPrompt`. A normalized list type, current array-shaped
example, or publication form therefore does not establish raw ingestion rejection. Recheck the raw
parser at the intended host revision before relying on this note. This compensation remains because
separate held-out audits repeatedly promoted the normalized representation into a false release
blocker; remove or revise it when the raw consumer contract changes or the failure no longer recurs.

A host-facing manifest or metadata object is one adopted interface boundary. Reconcile its
consequential declarations against the governing contract before claiming that boundary ready;
checking selected familiar fields cannot establish that the object as a whole is accepted. Host
ingestion and publication or listing policy are independent: passing or failing one cannot establish
the other. When current sources and an installed implementation disagree, preserve the conflict,
consulted version, and narrower claim.

In a broad plugin audit, unspecified publication intent does not make an available current-contract
conflict disappear. Surface the conflict and condition its consequence on the channel that adopts
the contract. If current authority cannot be obtained, retain that boundary as unverified. Ambiguity
can narrow a disposition; it cannot turn an observable incompatibility into an inspected pass.

A bundled command, path, or resource reference is part of the published invocation boundary. Prove
it from the working directory and package location the consumer actually supplies; execution through
an auditor-chosen target-relative path establishes only that direct invocation. When the host
provides a loaded-plugin or loaded-skill directory interface, reconcile the target command against
that interface and retain an installed or faithful unrelated-working-directory check for readiness.

For every published host, verify that the manifest exists and that shared identity, version,
description, license claim, and declared package surface do not contradict one another or the
catalog. A manifest can legitimately expose host-specific metadata; parity concerns the shared
promise, not byte identity. Different host-facing versions are an observation, not a defect without
a target-owned unified-release promise, a consumer equality requirement, or demonstrated stale or
unreachable updates.

A declared license identifier can incorporate terms by reference. Establish whether the inspected
tree is the intended distributed payload or only a source fragment; when that boundary is unknown,
condition the distribution consequence instead of silently treating the snapshot as complete.
Reconcile the actual in-scope payload with the authoritative text for that identifier, such as the
canonical [SPDX License List](https://spdx.org/licenses/), before treating identifier parity as
distribution readiness or a missing conventional filename as the defect. State only the notice,
grant, attribution, source, or delivery consequence the adopted terms and observed payload actually
establish. Bind the repair to those delivered terms; a conventional plugin-root license file is one
possible implementation, not a mandatory layout unless the actual copy or consumer interface makes
it so.

Treat permissions and capabilities against a documented host schema and the work the package really
performs. Do not invent an unsupported capability vocabulary. A package that cannot execute on one
host should not be published there merely for catalog symmetry.

Do not infer a custom manifest field's semantics from its spelling, location, or resemblance to
another host's schema. Establish the consumer and the authority defining what it may infer. A label
is not necessarily a resource path, exhaustive inventory, trigger, runtime input, or enforced promise
until the target, governing schema, or observed consumer makes it one. Once adoption is established,
judge only the relationship it actually declares.

Match executable probes to the claimed boundary. Direct invocation does not establish host failure
unless host authority or an observed host run supplies materially equivalent invocation,
interpreter, permissions, arguments, environment, and collection semantics. A passing direct probe
also cannot establish that a host-owned adapter works. Exercise the repository's converter and
round-trip contract when the target claims dual-host portability; structural preservation is not
proof that the destination host loads or can use the result.

Conclude which host boundary the evidence actually closes, what remains conditional, and what new
observation could reopen it. Do not mutate user-level host state merely to turn an unknown into a
result.
