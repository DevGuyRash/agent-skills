---
name: shell-development
description: >-
  Use for substantive shell scripts, shell modules, or shell-based automation. Select rules by the declared interpreter; covers POSIX sh, Bash, PowerShell, and an explicit fallback for other shells. Excludes incidental one-liners.
---

# Shell Development

## Purpose

Produce maintainable shell changes that preserve the repository's execution environment, command interfaces, stream behavior, failure semantics, and security boundaries. Detailed dialect guidance covers POSIX sh, Bash, and PowerShell; other shells use the bounded fallback below.

## Resolve the dialect first

Determine the interpreter for every changed artifact from the strongest available evidence:

1. The configured runner, CI `shell`, task runner, service unit, or invoking command.
2. The shebang and documented deployment shell.
3. File extension, module manifest, repository configuration, and nearby syntax.
4. Supported operating systems, shell editions, and minimum versions.

Execution configuration outranks a misleading extension. If evidence conflicts or a requested change would alter the interpreter contract, surface that decision instead of blending dialects.

For another shell such as zsh or fish, use its official documentation and the repository's supported-version tests as syntax authority. Apply this skill's repository-contract, interface, process, security, and verification guidance, but do not infer compatibility from another dialect or claim language-specific coverage this skill does not provide. Recommend a dedicated skill only when recurring work justifies one; do not invent a sibling that is not installed.

## Load the matching reference only

- Read `<skills-file-root>/references/posix-sh.md` for artifacts executed as POSIX `sh` or required to run across POSIX-conforming shells.
- Read `<skills-file-root>/references/bash.md` for artifacts explicitly executed by Bash.
- Read `<skills-file-root>/references/powershell.md` for PowerShell scripts, modules, manifests, functions, or pipeline behavior.
- Read `<skills-file-root>/references/concurrency-and-processes.md` when work starts background jobs, runs units concurrently, manages timeouts or cancellation, or owns a subprocess tree.
- Also read `<skills-file-root>/references/process-security.md` when the task handles untrusted values, secrets, privileges, destructive paths, temporary files, remote input, or external process construction.

Load one dialect reference per changed artifact. A multi-dialect task may require more than one, but do not merge their syntax or error models.

## Establish the repository contract

Inspect local instructions, neighboring scripts, task/CI definitions, supported platforms, pinned shell versions, environment inputs, dependencies, linters, formatters, and tests. Identify who invokes the script and what consumes its output.

Preserve repository choices. Do not silently replace shell, introduce Bash into POSIX sh, upgrade PowerShell edition, add a formatter, or rewrite a working script in another language.

## Preserve command interfaces

Treat these as externally observable:

- Arguments, options, defaults, environment variables, configuration precedence, and current directory assumptions.
- Exit status, stdout, stderr, logging format, pipeline values, and machine-readable output.
- Signals, traps, cancellation, timeouts, retries, idempotency, and cleanup.
- Filesystem effects, permissions, temporary paths, locks, subprocess trees, and privilege changes.
- Sourced functions, exported names, PowerShell module members, and dot-sourcing behavior.

Do not print progress to stdout when callers parse it. Do not hide a failed native command behind a successful later command.

## Implement within the dialect

- Quote and structure values according to the selected shell; quoting rules are not portable across dialects.
- Keep data separate from code and pass external-command arguments without reparsing when the dialect permits.
- Check status at the boundary that knows which exit codes are acceptable.
- Make resource and temporary-file ownership explicit on success, error, interruption, and cancellation.
- Bound concurrency from one aggregate budget, settle every admitted unit, and define output ordering and partial-failure behavior.
- Preserve byte/text encoding, line endings, locale, and stream behavior where consumers depend on them.
- In PowerShell, preserve object-pipeline values rather than flattening them to display text.
- In PowerShell, distinguish terminating errors, non-terminating errors, and native-process exit codes explicitly.

## Avoid universal policy

Do not mandate `set -e`, `set -u`, `pipefail`, one quoting slogan, one formatter, ShellCheck, PSScriptAnalyzer, Pester, Bats, advanced functions, or a rewrite threshold. These choices depend on dialect, version, repository contracts, and failure model.

## Verify proportionately

- Run the dialect's parse/syntax check using the supported interpreter.
- Run configured lint, format-check, static analysis, or tests for the touched scope.
- Exercise success, expected failure, empty/unusual values, signal or cancellation, and cleanup paths that changed.
- Verify exit status and stdout/stderr or object-pipeline output separately.
- Test supported shells, editions, operating systems, and CI environments when portability-sensitive behavior changed.

Do not claim portability from one local interpreter. Name unavailable shells, versions, platforms, commands, privileges, or services and the gap they leave.

## Compose with focused skills

Use CI, security, deployment, debugging, testing, refactoring, or release skills when those concerns drive the task. This skill owns shell semantics, dialect routing, and repository fit.

## Completion condition

The script behaves correctly under its declared interpreter, preserves intentional command and stream contracts, passes repository checks at the warranted scope, and leaves no hidden dialect or platform assumption.
