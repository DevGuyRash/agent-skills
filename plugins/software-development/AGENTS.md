# Software Development Plugin Authoring Contract

These rules apply only under `plugins/software-development/`.

The public catalog is exactly the 25 skill directories listed in this plugin's README. Keep them independently retrievable; do not add an umbrella skill, router skill, shared runtime reference, hook, agent, command, MCP server, LSP, CI template, Git wrapper, or bundled language server.

Every `SKILL.md` SHALL use a lowercase `name` slug that exactly matches its directory. The H1 and `agents/openai.yaml` display name SHALL be title-cased.

Each description SHALL state the skill's positive activation boundary and its most important near-neighbor exclusion when one exists.

References SHALL be linked directly from `SKILL.md`, loaded only on a stated condition, and SHALL NOT link to another reference.

Every skill SHALL ship `agents/openai.yaml`, `evals/trigger-prompts.json`, and `evals/evals.json`. Trigger and task evidence SHALL cover the skill's material activation, exclusion, composition, and outcome boundaries, including retained named regression probes and resolvable maintainer fixtures. Evaluate observable outcomes and routing, not exact prose, fixed fixture counts, or private reasoning.

Repository conventions, supported versions, public contracts, build wrappers, and configured tools take precedence over generic guidance. Do not require the newest runtime, arbitrary code-size thresholds, blanket design patterns, universal coverage, or proof-of-process transcripts.

Only `skills/rust-panic-audit/scripts/panic_audit.py` may ship executable runtime code. Maintainer tests and eval fixtures stay outside runtime skill resources. Any runtime-surface exception requires an eval-backed rationale in `MAINTAINERS.md` before release.
