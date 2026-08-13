# Project Contract and Verification

Read this reference for Python version, environment, dependency, toolchain, test, or project-metadata work.

## Discover the project shape

Inspect the files that actually govern the affected package:

- `pyproject.toml`, `setup.cfg`, `setup.py`, `tox.ini`, `noxfile.py`, and task-runner files.
- `requires-python`, environment markers, classifiers, CI matrices, containers, and deployment manifests.
- Lockfiles and configuration for uv, Poetry, PDM, pip-tools, Hatch, Pipenv, or another repository-selected frontend.
- `pytest`, `unittest`, doctest, Hypothesis, coverage, mypy, Pyright, Ruff, Flake8, Black, or other configured tools.
- Import layout, generated sources, and application entry points.

Use the nearest project boundary in a monorepo. A root configuration does not automatically govern every nested package.

## Resolve the interpreter contract

The supported range comes from the combined repository contract, not from the local `python --version` alone. Reconcile metadata, CI, runtime images, framework support, and documented consumers. Treat classifiers as descriptive unless the project makes them normative.

Do not use syntax or library APIs newer than the minimum supported interpreter. If declarations disagree, surface the inconsistency instead of choosing the newest value silently.

Use the repository's environment command. Do not mutate a global interpreter or create a second lockfile. Avoid broad dependency resolution when a locked install or targeted update satisfies the task.

## Change dependencies deliberately

- Distinguish runtime, optional, development, and build dependencies.
- Preserve markers, extras, indexes, hashes, and platform constraints.
- Update the lock only with the owning tool and only when resolution is intended.
- Verify imports from the repository's configured environment rather than relying on an unrelated global interpreter.
- Do not hand-edit generated lock or metadata files unless their tool explicitly supports it.

## Choose verification from repository interfaces

Prefer commands exposed by the project or CI. A common evidence ladder is:

1. Syntax/import or focused test for the changed unit.
2. Relevant formatter/linter/type-check target.
3. Package or integration suite affected by the change.
4. Supported-version matrix for compatibility-sensitive work.
Do not assume `pytest`, strict typing, coverage thresholds, or a formatter is required when the repository does not establish it. Conversely, do not skip configured checks because a different local tool reports success.

Report command, scope, interpreter, result, and any missing service or platform needed for stronger evidence.
