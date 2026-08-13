# Node.js Services and Operations

Load this reference for servers, CLIs, streams, subprocess orchestration, timeouts, signals, shutdown, or operational evidence.

## Servers and Requests

- Set request, header, body, upstream, idle, and shutdown bounds according to the service and framework contract.
- Validate and authorize input before consequential work; parameterization and parsing do not replace authorization.
- Propagate cancellation when a client disconnects or an upstream deadline expires and downstream APIs support it.
- Separate expected client or operational errors from programmer defects and infrastructure failure.
- Avoid returning internal stack traces, secret-bearing causes, or raw dependency errors to callers.
- Respect framework-specific proxy, address, streaming, and error-routing behavior rather than recreating it generically.

## Streams and Backpressure

- Prefer the repository/runtime pipeline abstraction when it correctly joins errors, teardown, and backpressure.
- Do not collect an unbounded stream merely to use a simpler buffer API.
- Account for object mode, encoding boundaries, partial chunks, early consumer exit, and double settlement.
- Verify both producer and consumer cleanup on success, error, timeout, and cancellation.
- Measure high-water marks or concurrency only when workload evidence requires tuning.

## Lifecycle and Shutdown

- Identify which resources the component owns: listeners, servers, connections, workers, child processes, timers, and temporary files.
- On shutdown, stop accepting work, drain or cancel bounded in-flight work, close owned resources, and set an outcome the supervisor can interpret.
- Make cleanup idempotent so signal, error, and normal completion paths can converge safely.
- Respect the deployment platform's termination signal and grace period.
- Do not call `process.exit()` before buffered output and cleanup complete unless immediate termination is the explicit safety behavior.

## Errors and Observability

- Attach context at boundaries while preserving stable error identity or codes used by callers.
- Log once at the layer that owns operational reporting; avoid log-and-rethrow duplication.
- Include request or job correlation through the repository's existing mechanism when concurrency makes attribution difficult.
- Keep secrets, tokens, credentials, and sensitive payloads out of errors, logs, metrics, and traces.
- Treat uncaught exceptions and unhandled rejections as loss of a known-safe state unless the application's supervision contract proves otherwise.

## Verification

- Exercise startup, success, expected failure, cancellation, and bounded shutdown.
- Check exit codes and stdout/stderr contracts for CLIs.
- Check that tests leave no servers, timers, sockets, workers, or subprocesses alive.
- Use representative load and failure injection only when the task owns performance or resilience testing.
