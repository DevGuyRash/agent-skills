# Plugin Fit

Use this reference when the decision depends on how bundled capabilities coexist, select one another,
share state or authority, and compose into a package-level outcome. Host ingestion, publication,
installed-copy, and manifest questions belong to [host contracts](host-contracts.md).

Keep package evidence separate from skill evidence. Each bundled skill needs its own behavioral proof
for a task-value claim. Package routing, coexistence, shared resources, hooks, commands, and
integration boundaries need package-level evidence. A sound manifest cannot rescue a harmful skill,
and one useful skill cannot establish plugin-wide value.

Isolation can miss package effects. Passive descriptions, shared references, overlapping routes,
hook state, common tools, and one skill's output can change another skill's trajectory without either
failing alone. When the package claim depends on composition, exercise the installed composition and
consequential handoff. Do not replace that evidence with more isolated skill runs.

Inspect authority and downstream state along activated package paths when one capability can affect
another. A benign isolated artifact does not establish safe composition when outputs, side effects,
trust cues, or permissions cross capability boundaries. Exercise external effects only in an
authorized disposable environment or faithful simulation. [SCR-Bench](https://arxiv.org/abs/2606.15242v1)
supplies fixed-version external evidence for this activated-path risk; the target's composition
remains the audit evidence.

Observe sibling routing on the live host when overlapping descriptions or exclusions could change
which skill is selected. Static text can expose a plausible collision, but only activation evidence
shows what the host did. A one-way textual mention is not automatically a defect; the material issue
is whether intended work loses a reachable owner or reliably routes to the wrong one.

Reconcile declared selection with the executed handoff when a catalog, manifest, context, prompt, or
host adapter can choose a capability. The existence of a capability file and runnable command does
not show that the published capability selects that file, reaches that command, or obtains the
promised result. Follow the actual owner or consumer through downstream input and observable output.
Individual happy paths do not establish the cross-surface route, and unknown host composition keeps
the consequence conditional rather than making source contradictions irrelevant.

For release readiness, distinguish a demonstrated broken handoff from an unestablished one. An
unknown host layer can keep a defect conditional, but it cannot supply positive evidence that a
published capability is reachable or complete. Hold only the affected readiness claim, name the
missing observation, and avoid asserting that no external layer exists.

If the user narrows a multi-skill audit, make the uncovered skills and package surfaces visible. Do
not describe a partial node audit as a clean plugin audit.

`scripts/plugin_check.sh` reports manifest presence, shared-field differences, catalog version facts,
license-file reachability, tracking state, and installed-versus-source drift for bundled skill trees
when those surfaces can be located. It does not infer that dual manifests, bundled skills,
description equality, or cross-host version equality are universally required. It also does not
compare hooks, commands, MCP servers, host registries, or other package surfaces outside the skill
trees. Its `unchecked` output is an evidence gap, not success, and every observation still requires
target and host interpretation.

Conclude in ordinary language whether the composed package fulfills each claim, what runtime evidence
supports it, and what change or observation could reopen it.
