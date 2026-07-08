Friction diagnostics v5.1.1 (live on BOTH hosts from the local working tree):

- Both harnesses installed via `scripts/install-all --<host>-only --source ~/repos/agent-tooling --include friction-diagnostics`; both marketplaces currently point at the LOCAL tree. Push to GitHub main and re-add the remote source when remote-tracked installs are wanted. Note the host difference: Claude caches by version (content changes need a version bump), Codex references the tree live.
- Blind-validated on both hosts (routing, decision quality, control silence, session_ref): Claude via the SessionStart hook, Codex via native CODEX_THREAD_ID; sandboxed codex filing works under workspace-write. Findings recorded in FD/references/integration.md.
- CLAUDE_ENV_FILE propagation to subagents and resumed sessions is undocumented upstream; verify once in a live session and note the result in integration.md.
- Trigger boundary probes (`evals/trigger-prompts.json` in both skills) still need a formal skill-surfacing eval run per harness (blind behavior already matched all probe expectations, including the TDD-red gate, on both hosts).
- After 2-4 weeks of v5.1 data, review `generate-report.sh --report-type stats` against the v4 baseline (targets: noisy+continued <40%; pivot_information and decision top-5 trigram share <25% with high distinct-openers, vs 94% hindsight baseline; recurrence records >0; key collisions ~0; ≥1 resolution filed; ≥1 session observed avoiding a known trap).
- Optional global traps tier (`~/.local/share/agent-friction/known-traps.md`, mend-skill promotion, snippet reads repo-local then global) was deliberately deferred.

Active risks:

- GoalSpec V4 still needs a live decision-funnel gauntlet across Codex and Claude before claiming behavioral success; grade design clarity, convergence quality, artifact restraint, probe quality, default handling, and product regressions.
- Friction diagnostics helper is hanging on this Windows event stream; do not leave stale `.report-friction.lock` behind after attempts to log.
- Excel Foundry cloud commands still need opt-in live Graph/Fabric/Power BI validation with tenant env vars and safe test resources before any cloud surface is promoted to supported.
- Claude `agents/*.md` surfaces are now reported as `preserved_only` in claude→codex conversion but still have no Codex mapping; decide whether a Codex-side agent equivalent should exist or whether preserved-only is the end state.
