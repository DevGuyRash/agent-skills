# PowerShell

Read this reference only for PowerShell scripts, modules, manifests, functions, or pipeline behavior.

## Establish edition and version

Determine Windows PowerShell versus PowerShell, supported versions, operating systems, remoting hosts, execution policy/signing constraints, and module dependencies. Preserve `.ps1`, `.psm1`, and `.psd1` ownership and exported members.

Do not introduce PowerShell 7-only operators or APIs into Windows PowerShell support, or assume Windows-only commands and path behavior in a cross-platform module.

## Preserve the object pipeline

PowerShell pipelines carry objects until a formatting or text boundary. Return or emit the objects consumers expect; do not replace them with `Format-*`, host-rendered text, or string concatenation inside reusable functions.

- Keep success output distinct from information, verbose, warning, error, debug, and progress streams.
- Avoid incidental success-stream output from helper calls; capture, return, or intentionally discard it.
- Preserve property names, types, ordering expectations, and enumeration behavior used by downstream commands.
- Perform formatting at the outer display boundary, not in reusable data-producing code.

Pipeline input, parameter sets, aliases, validation attributes, and exported function names are public interfaces. Use advanced-function features only when the repository contract benefits from them.

## Handle errors by category

Cmdlets can emit non-terminating errors that `try`/`catch` will not catch unless promoted, commonly with scoped `-ErrorAction Stop`. Do not set `$ErrorActionPreference` globally without understanding caller/module effects; scope and restore policy changes.

Native executables have their own exit codes. Check and preserve `$LASTEXITCODE` at the relevant boundary. `$?` and native-error integration vary by PowerShell version and preference settings, including `$PSNativeCommandUseErrorActionPreference`; do not assume cmdlet error semantics apply automatically.

Preserve the original error or exit code through `finally` and cleanup. Use `throw` or an error record consistent with the function's established contract.

## Invoke native commands deliberately

PowerShell parses and marshals native arguments differently across versions and platforms. Prefer explicit argument collections and test quoting at the supported boundary. Define working directory, environment, encoding, stdout/stderr, timeout, and acceptable exit codes.

Dispose owned .NET resources and stop owned jobs/processes in `finally`. Do not dispose objects supplied by the caller.

## Verify

Use the repository's supported PowerShell parser/import check, Pester suite, and PSScriptAnalyzer/formatter configuration when present. Test both object values and stream placement, terminating and non-terminating errors, native nonzero exits, module import/export, supported editions, and platform-sensitive paths where affected.
