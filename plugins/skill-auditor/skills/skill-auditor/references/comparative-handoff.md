# Comparative Handoff

Use this route when an unresolved audit claim needs newly designed comparative evidence. Skill Auditor owns why the evidence is needed, the exact claim it bears on, governing authority, materiality, the consequence of remaining unresolved, and the final audit disposition. `$split-testing` owns comparison design, evidence collection, review, and inference. Neither plugin acquires domain truth, rightful values, or authority merely through the handoff.

If Split Testing is available, supply the frozen request and require the reciprocal result. Skill Auditor verifies that returned evidence bears on the original claim before applying severity, repair, release, or reopening. The result cannot decide audit disposition on its own.

If Split Testing is unavailable, Skill Auditor MAY assess already-existing evidence against the claim. It SHALL NOT design or run a replacement comparison, reconstruct generic comparison methodology, or describe a local fallback as equivalent. When existing evidence is insufficient, emit the request envelope, leave the exact claim unresolved, and state the unresolved consequence for the audit.

## Request interface

The request schema is `comparative-evidence-request.v1`. Retain the exact frozen UTF-8 request bytes because the result digest binds those bytes, not parsed or reformatted JSON. Preserve unknown fields byte-for-byte in retained custody and preserve unknown fields semantically whenever the envelope is transmitted or extended. The object requires:

- `schema`: the exact request schema name.
- `claim_id`: the stable audit claim identity.
- `target_ref`: target identity plus the relevant source digest, version, or equivalent frozen reference.
- `authority_ref`: the governing authority and horizon for the claim.
- `claim`: the exact unresolved comparative claim.
- `decision_context`: the intended population, use, decision horizon, and other audit context that can change claim fit.
- `existing_evidence_refs`: direct references to existing evidence and its known limits; an empty list is valid.
- `closure_conditions`: one or more audit-defined conditions, each with a stable ID that is unique within the request plus a statement describing what would close, narrow, or leave the claim unresolved.
- `unresolved_consequence`: the audit consequence when no valid comparison is obtained.
- `prohibited_effects`: evidence, external effects, disclosures, costs, or other actions the comparison is not authorized to create.
- `extensions`: an optional open object for additional context.

The envelope MAY contain arbitrary additional fields. Consumers SHALL preserve them and SHALL NOT treat absence from the listed interface as exclusion of relevant context. The request SHALL NOT prescribe observations, cases, graders, scores, topology, result form, or benchmark lineage as auditor-chosen comparison design; those choices belong to Split Testing under the live decision and supplied authority. An adopted audit authority, standard, real consumer or deployment boundary, prohibited effect, or audit-owned closure condition is not a design prescription: identify it through the corresponding authority, decision, boundary, closure, or extension field so Split Testing can honor it within its actual authority.

## Result interface

The return schema is `comparative-evidence-result.v1`. The object requires:

- `schema`: the exact result schema name.
- `claim_id`: the original audit claim identity.
- `request_digest`: SHA-256 over the exact frozen UTF-8 request bytes.
- `tested_conditions`: exact identities or references for what was compared under the actual system policy.
- `conclusion`: an open expression of what the comparison supports; it is not a closed result enum.
- `closure_assessment`: exactly one entry for every request closure-condition ID and no unrequested IDs, with audit-interface status `closes`, `narrows`, or `does_not_resolve` and direct basis references when available.
- `evidence_refs`: direct locations for the retained evidence basis.
- `scope_and_limits`: material validity, population, horizon, tested-policy, and generalization limits.
- `uncertainty`: materially different unresolved sources kept distinct when their consequences or remedies differ, without fixed categories.
- `reopening_conditions`: changes or new evidence that would require reconsideration.
- `extensions`: an optional open object for additional return context.

The result MAY contain arbitrary additional fields and SHALL preserve unknown fields. Cases, exposures, attempts, resources, human assignments, source snapshots, executable states, or other modality-specific facts belong in referenced evidence only when applicable. Foundational findings must identify whether their support is observational, intervention-supported, or provisional without requiring a universal diagnosis field.

Skill Auditor SHALL reject a mismatched `claim_id`, request digest, omitted closure condition, irrelevant tested condition, unsupported generalization, or evidence reference that does not bear on the claim. A valid return remains evidence input to the audit; Skill Auditor retains rightful authority interpretation, materiality, severity, repair, release, reopening, and the final disposition.
