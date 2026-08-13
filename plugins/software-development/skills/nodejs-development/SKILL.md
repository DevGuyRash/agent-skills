---
name: nodejs-development
description: Use for Node.js runtime or package work involving ESM/CJS resolution, exports, streams, buffers, processes, or resource lifecycles. Compose with JavaScript or TypeScript; exclude browser-only work.
---

# Node.js Development

## Purpose

Build Node.js software against repository runtime, package, module, resource,
and operational contracts. Keep language concerns in JavaScript or TypeScript.

## Compose Deliberately

- Add `javascript-development` when JavaScript source changes.
- Add `typescript-development` when TypeScript source, types, declarations, or compiler behavior changes.
- Use neither language sibling for a package-metadata or runtime investigation that does not touch its language concerns.
- Add method or domain skills only when those concerns shape the task.
- Do not use this skill for browser-only, edge-runtime-only, or package-manager-neutral language work.

## Establish the Node Profile

Before editing:

1. Read repository instructions and nearby package boundaries.
2. Identify supported Node versions from `engines`, version files, CI, containers, and deployment configuration.
3. Identify the package manager, workspace model, lockfile, install mode, registry, and repository scripts.
4. Determine ESM/CommonJS behavior from extensions, nearest `package.json`, maps, compiler output, and consumers.
5. Identify runtime topology: CLI, long-lived service, worker, serverless function, build tool, library, or mixed target.
6. Locate test/build commands and separate authored files from generated bundles, declarations, and vendored output.

When sources conflict, prefer the configuration used by CI and deployment, then report the inconsistency.

## Respect Runtime Semantics

- Use APIs supported by the declared Node range unless changing it is in scope.
- Preserve ESM/CommonJS entry points, package conditions, file extensions, and import timing unless the task owns a migration.
- Treat paths, file URLs, working directory, executable location, and module location as distinct concepts.
- Preserve claimed platform portability; distinguish path and URL semantics.
- Preserve encoding and binary/text distinctions when crossing buffers, streams, files, or network boundaries.
- Avoid synchronous filesystem or process work on latency-sensitive paths; it can be appropriate during startup, build steps, or small CLIs.
- Do not rely on mutable process-global state when concurrent tests, workers, requests, or embedded consumers can observe it.

Read [runtime-and-modules.md](<skills-file-root>/references/runtime-and-modules.md) for module resolution, filesystem, processes, workers, and runtime compatibility.

## Manage Async Resources and Lifecycle

- Decide whether work is buffered, streamed, sequential, concurrent, or cancellable before choosing an API.
- Honor stream backpressure; prefer established pipeline utilities when they match the repository's error and cleanup contract.
- Propagate cancellation and timeouts across owned operations, and clean up listeners, timers, sockets, files, subprocesses, and streams.
- Handle expected operational failures at a boundary that can recover, translate, retry safely, or terminate deliberately.
- Make shutdown stop new work, drain or cancel bounded in-flight work, close owned resources, and finish within the platform's grace period.
- Handle signals and unobserved failures under the application's supervision model; do not continue from unknown state.

Read [services-and-operations.md](<skills-file-root>/references/services-and-operations.md) for servers, CLIs, streams, subprocesses, signals, shutdown, and observability.

## Preserve Package Contracts

- Keep the selected package manager and lockfile; do not generate a competing lockfile.
- Treat entry points, exports, types, bins, files, engines, dependencies, and workspace links as distribution behavior.
- Add or upgrade dependencies only within task scope and review the effective lockfile and lifecycle-script changes.
- Keep runtime dependencies separate from development-only tooling and use peer or optional dependencies only for their actual package semantics.
- Verify published shape with the repository's pack or distribution workflow when package metadata changes.

Read [packages-and-dependencies.md](<skills-file-root>/references/packages-and-dependencies.md) for manifests, exports, workspaces, installation, and dependency review.

## Protect Host Boundaries

- Treat environment, arguments, files, network input, and IPC as untrusted until parsed.
- Do not pass untrusted input through a shell command string. Prefer argument-vector process APIs and explicit executable selection.
- Resolve and authorize filesystem targets before writing; account for traversal, symlinks, overwrite behavior, and permissions.
- Keep secrets out of source, command lines, error payloads, logs, and package artifacts.
- Do not assume environment variables are present, typed, secret, or reloadable.

## Verify in the Native Environment

Run the narrowest existing checks first:

1. Focused tests for runtime behavior, cleanup, failures, and package boundaries.
2. Repository lint, type, and format checks relevant to touched files.
3. A runtime, CLI, server, worker, or package smoke test on a supported Node version.
4. Pack/build checks when exports, bins, files, declarations, or dependencies change.
5. Broader integration tests when lifecycle, shared packages, or external resources change.

Where possible, detect leaked handles, incomplete shutdown, unobserved rejection,
and partial cleanup. Report commands, runtime, package manager, verified behavior,
and unavailable environments.

## Avoid Universal Mandates

Do not prescribe ESM or CommonJS, a package manager, framework, logger,
environment convention, dependency count, or server architecture universally.
