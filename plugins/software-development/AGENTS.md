# Software Development Plugin Authoring Contract

These rules apply only under `plugins/software-development/`.

The public catalog is exactly the 25 skill directories listed in this plugin's README. Keep them independently retrievable; do not add an umbrella skill, router skill, shared runtime reference, hook, agent, command, MCP server, LSP, CI template, Git wrapper, or bundled language server.

Every `SKILL.md` SHALL use a lowercase `name` slug that exactly matches its directory. This plugin follows the live Agent Skills specification even while unchanged legacy plugins elsewhere in the repository retain title-cased frontmatter. The H1 and `agents/openai.yaml` display name SHALL be title-cased.

Every skill SHALL keep its description between 120 and 220 characters and SHALL state both its positive activation boundary and its most important near-neighbor exclusion. Aggregate names plus descriptions SHALL remain at or below 4,800 characters.

Each `SKILL.md` SHALL remain between 1,000 and 1,500 estimated tokens. Each reference SHALL remain at or below 1,200 estimated tokens. References SHALL be linked directly from `SKILL.md`, loaded only on a stated condition, and SHALL NOT link to another reference.

Every skill SHALL ship `agents/openai.yaml`, `evals/trigger-prompts.json`, and `evals/evals.json`. Trigger fixtures SHALL include at least two implicit positives, one explicit invocation, two near-neighbor negatives, and one ambiguous composition case. Composition cases SHALL name expected and excluded skills, plus any external companion when the relevant specialist is outside this plugin. Each language skill SHALL have at least one task eval backed by a resolvable maintainer fixture. Evaluate observable outcomes and routing, not exact prose or private reasoning.

Repository conventions, supported versions, public contracts, build wrappers, and configured tools take precedence over generic guidance. Do not require the newest runtime, arbitrary code-size thresholds, blanket design patterns, universal coverage, or proof-of-process transcripts.

Only `skills/rust-panic-audit/scripts/panic_audit.py` may ship executable runtime code. Maintainer tests and eval fixtures stay outside runtime skill resources. Any budget or runtime-surface exception requires an eval-backed rationale in `MAINTAINERS.md` before release.
