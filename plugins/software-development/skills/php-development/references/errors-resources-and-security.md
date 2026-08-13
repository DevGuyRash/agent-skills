# Errors, Resources, and Security

Read this reference for `Throwable`, error handling, cleanup, streams, transactions, workers, serialization, SQL, encoding, secrets, or untrusted input.

## Keep failure boundaries meaningful

`Throwable` covers both `Error` and `Exception`. Catch the narrowest useful type and only where the layer can recover, translate, add boundary context, report once, or guarantee cleanup.

- Preserve the prior throwable when translating to a domain exception.
- Use `finally` for unconditional release and rollback behavior.
- Do not suppress diagnostics with `@` as a default or convert every warning/deprecation to an exception without understanding framework behavior.
- Avoid broad `catch (Throwable)` that turns programming/runtime errors into ordinary results.
- Treat exception type, error reporting, and deprecation behavior as observable interfaces.

## Make resource ownership explicit

Close owned streams, locks, transactions, temporary files, and processes deterministically. Do not close borrowed resources. Avoid relying on destructors for correctness, especially in long-running workers, shutdown, cycles, or Fiber-related lifetimes.

Across PHP versions, several former resources are objects. Do not use `is_resource()` or resource-specific cleanup as a universal test without checking the API and supported versions.

## Protect trust boundaries

- Never pass untrusted data to `unserialize()`, regardless of `allowed_classes`; use a safe interchange format.
- Parameterize SQL data. Place identifiers and query structure behind a finite allowlist because placeholders cannot bind them.
- Encode output for its actual HTML, attribute, URL, JavaScript, JSON, header, or other context, preferably through the owning framework's escaping interface.
- Use password hashing/verification APIs rather than general hashes or custom salts.
- Use cryptographic random APIs for secrets and constant-time comparison for secret values.
- Keep secrets out of source, output, logs, exception text, command arguments where exposed, fixtures, and package artifacts.
- Validate upload, archive, stream-wrapper, URL, and filesystem destinations before crossing a trusted boundary.

Production diagnostics should be logged through the application's controlled interface, not displayed to users. Do not treat `filter_var()` with its default filter as sanitization.

## Preserve worker and process behavior

For long-running PHP runtimes, account for state retained beyond one request, connection reuse, signal/shutdown behavior, and framework reset hooks. Fibers are a cooperative primitive, not a complete async policy; event loops, cancellation, and lifecycle belong to the selected runtime or framework.

When invoking processes, define arguments, shell use, environment, working directory, timeout, exit status, and stream handling explicitly.
