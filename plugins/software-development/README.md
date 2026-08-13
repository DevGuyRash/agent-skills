# Software Development

`software-development` v1.0.0 is a dual-host, skills-only plugin for focused
language guidance and engineering methods. It is instruction-first: the only
runtime helper is the Rust panic-audit runner, which may write Cargo build
cache but does not modify tracked repository files.

## Catalog

Language skills:

- `rust-development`, `python-development`, `javascript-development`
- `typescript-development`, `go-development`, `java-development`
- `kotlin-development`, `csharp-development`, `c-development`
- `cpp-development`, `swift-development`, `ruby-development`
- `php-development`, `shell-development`, `sql-development`

Engineering-method skills:

- `test-driven-development`, `systematic-debugging`, `refactoring`
- `performance-engineering`, `trunk-based-development`
- `behavior-preserving-migration`

Focused specialists:

- `nodejs-development`
- `async-rust`, `unsafe-rust`, `rust-panic-audit`

There is no umbrella development skill. Language skills activate only for
maintained artifacts they substantively affect. Method skills activate from
intent or evidence. Node.js composes with JavaScript or TypeScript; Rust
specialists compose with Rust; embedded SQL composes with its host language.
Routine Git/GitHub operations and conceptual questions activate none of these
skills.

Codex exposes the skills through its native picker and invocations such as
`$rust-development`. Claude Code exposes namespaced invocations such as
`/software-development:rust-development`.

## Migration from the retired plugins

This is a clean identity cutover. Remove the old packages, add this one, then
start a fresh task or restart the host so the cached skill inventory changes.
Scope flags may be added to the commands when the installation is not in the
default scope.

```text
codex plugin remove rust-development@agent-tooling
codex plugin remove gitops-workflow@agent-tooling
codex plugin add software-development@agent-tooling

claude plugin remove rust-development@agent-tooling
claude plugin remove gitops-workflow@agent-tooling
claude plugin install software-development@agent-tooling
```

`scripts/install-all` installs the new catalog entry but intentionally does not
uninstall already installed legacy packages.

## Verification

From the repository root:

```text
python3 -m unittest discover plugins/software-development/tests
python3 scripts/plugin_port.py validate plugins/software-development --host codex
python3 scripts/plugin_port.py validate plugins/software-development --host claude
just audit-plugins software-development
```

Maintainer acceptance, context budgets, and exception policy are documented in
`MAINTAINERS.md`. Skill-specific trigger and task fixtures are canonical under
each skill's `evals/` directory; cross-skill routing cases are under `evals/`.
