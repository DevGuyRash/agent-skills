Friction diagnostics v5.2.0 (hardened; installed copies still carry the previous version until reinstalled):

- Reinstall both harnesses (`scripts/install-all --<host>-only --source ~/repos/agent-tooling --include friction-diagnostics`) so Claude's version-keyed cache picks up 5.2.0; Codex references the tree live and already sees it. Push to GitHub main and re-add the remote source when remote-tracked installs are wanted.
- Live-verify on Claude: boundary presence lines at session start in a repo with open events; filing right after a resume stamps the CURRENT session id (sidecar); `pgrep -af zsh` shows no duplicate FRICTION_ export growth.
- Live-verify on Codex: the ported SessionStart hook fires; note whether hook stdout enters context (boundary lines are best-effort there); filing under `codex exec` still stamps CODEX_THREAD_ID (native ids now outrank the sidecar by design).
- Trigger boundary probes (`evals/trigger-prompts.json` in both skills) still need a formal skill-surfacing eval run per harness (blind behavior already matched all probe expectations, including the TDD-red gate, on both hosts).
- 5.2.0 reopen semantics flip previously-closed recurrence-after-resolution events open on real stores; INDEX/stats/talkback counts shift on first regeneration — expected, announce once per store if anyone asks.
- The mend half has still never run end-to-end on a real corpus (345 anchors across 7 repos, 1 self-referential resolution, 0 published trap files); the first real mend session is the outstanding validation experiment, user-invoked.
- After 2-4 weeks of v5.2 data, review `generate-report.sh --report-type stats` against the v4 baseline (targets: noisy+continued <40%; pivot_information and decision top-5 trigram share <25% with high distinct-openers, vs 94% hindsight baseline; recurrence records >0; key collisions ~0; ≥1 resolution filed; ≥1 session observed avoiding a known trap).
- Optional global traps tier (`~/.local/share/agent-friction/known-traps.md`, mend-skill promotion, snippet reads repo-local then global) was deliberately deferred.

Skill-auditor 2.0.0 surfaced 11 errors across the repo that nothing was running before. Each is broken for every target, not a convention:

- `excel-foundry/scripts/excel-foundry` and four `gitops-workflow` launchers (`ensure-worktree.sh`, `reconcile-tree.sh`, `recover-repo-state.sh`, `repo-state.sh`) lack the executable bit and cannot be invoked.
- `goalspec` catalog says 1.8.1, manifest says 4.0.0, and the catalog description still describes the pre-decision-funnel design. `playwright-testing` catalog 1.0.0 vs manifest 1.2.0.
- `linux-desktop-control` host manifests disagree on description; `claude-linux-computer-use` has a manifest error. Both were published from untracked content at the time of the audit.
- No LICENSE file exists behind the MIT declaration in every manifest (reported as an observation, not an error — the file may sit above the search depth).

Run `just audit-plugins --errors-only` for the current list. CI gates only the plugins a change touches, so these block nobody until someone edits the plugin that owns them.

Active risks:

- GoalSpec V4 still needs a live decision-funnel gauntlet across Codex and Claude before claiming behavioral success; grade design clarity, convergence quality, artifact restraint, probe quality, default handling, and product regressions.
- Friction diagnostics was hanging on a Windows event stream via stale `.report-friction.lock`; 5.2.0 bounds the wait (FRICTION_LOCK_TIMEOUT, ownerless-lock reclaim) — confirm on the Windows stream next time it is exercised, then drop this line.
- Excel Foundry cloud commands still need opt-in live Graph/Fabric/Power BI validation with tenant env vars and safe test resources before any cloud surface is promoted to supported.
- Claude `agents/*.md` surfaces are now reported as `preserved_only` in claude→codex conversion but still have no Codex mapping; decide whether a Codex-side agent equivalent should exist or whether preserved-only is the end state.
- Skill-auditor 2.0.0 has produced exactly one Improvement Brief (target: gitops-workflow), written and graded by the same context that built the skill. It satisfied the output contract mechanically, but nobody independent has judged whether the brief is *good*, and there is no baseline comparison against what the 1.0.0 auditor would have said for the same target. Treat the outcome as demonstrated once, not validated.
