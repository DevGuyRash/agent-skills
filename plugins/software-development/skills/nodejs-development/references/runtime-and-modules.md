# Node.js Runtime and Modules

Load this reference for Node version compatibility, ESM/CommonJS resolution, paths, files, processes, workers, or environment behavior.

## Runtime Contract

- Reconcile `engines`, version-manager files, CI matrices, containers, deployment configuration, and actual production constraints.
- Use the oldest supported version when evaluating API availability and syntax emitted by a compiler.
- Distinguish Node from browsers, service workers, edge runtimes, Electron, and compatibility layers even when they expose similar APIs.
- Feature detection can complement version policy, but it should not hide an unsupported deployment target.

## ESM and CommonJS

- Resolve semantics from the nearest package scope, filename extension, exports/imports conditions, loader hooks, and consuming toolchain.
- Preserve the difference between static imports, dynamic imports, and `require`, including timing, caching, live bindings, and cycle behavior.
- Use `import.meta.url` and URL conversion for module-relative resources in ESM; do not substitute the process working directory.
- Keep `__dirname`/`__filename` assumptions confined to CommonJS or explicit compatibility code.
- Treat default-import interop as toolchain-dependent. Test the actual supported consumer rather than relying on editor acceptance.
- Do not expose internal deep paths accidentally when changing an exports map.
- A dual ESM/CommonJS package can create separate instances or state. Add dual entry points only with a tested need and compatible design.

## Files, Paths, and Data

- Select synchronous versus asynchronous file APIs from execution context, latency, and simplicity—not a universal rule.
- Specify encoding when text is required; preserve `Buffer` or typed-array behavior for binary data.
- Use `path` and URL APIs appropriate to the value being handled. Account for Windows drive, UNC, separator, and case behavior when portability is claimed.
- Make overwrite, atomicity, permissions, temporary-file cleanup, and symlink behavior explicit for consequential writes.
- Avoid time-of-check/time-of-use security assumptions around mutable filesystem paths.

## Processes and Workers

- Prefer direct executable plus argument arrays over shell strings. Enable a shell only for syntax that genuinely requires it and constrain inputs.
- Decide how stdin/stdout/stderr are inherited, captured, streamed, and bounded.
- Handle subprocess exit, signal, spawn error, cancellation, and cleanup as separate outcomes.
- Use worker threads or child processes only when isolation or measured CPU-bound work warrants their complexity.
- Avoid sharing mutable process-global configuration across tests or request contexts unless ownership is explicit.

Primary authority: the repository version's documentation from the [Node.js documentation index](https://nodejs.org/docs/). Package and tool behavior may impose narrower contracts.
