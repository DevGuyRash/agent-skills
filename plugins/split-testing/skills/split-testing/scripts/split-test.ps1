[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $ForwardedArguments
)

$ErrorActionPreference = 'Stop'
$skillRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$isWindowsHost = $env:OS -eq 'Windows_NT'
if (-not $isWindowsHost) {
    [Console]::Error.WriteLine('error: split-test.ps1 supports Windows hosts only')
    [Console]::Error.WriteLine('hint: on Linux or WSL, run scripts/split-test')
    exit 2
}

$architecture = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString()
$platformId = switch ($architecture) {
    'X64' { 'windows-x86_64' }
    'Arm64' { 'windows-aarch64' }
    default {
        [Console]::Error.WriteLine("error: unsupported Windows architecture for split-test: $architecture")
        [Console]::Error.WriteLine('hint: use a supported x86_64 or aarch64 package')
        exit 2
    }
}

$binary = Join-Path $skillRoot "dist/$platformId/split-test.exe"
if (Test-Path -LiteralPath $binary) {
    $item = Get-Item -LiteralPath $binary -Force
    if ($item.PSIsContainer -or $null -ne $item.LinkType) {
        [Console]::Error.WriteLine("error: packaged split-test binary is not a regular file: $binary")
        [Console]::Error.WriteLine('hint: reinstall a verified Split Testing package')
        exit 2
    }
    if ($null -eq $env:RUST_BACKTRACE) {
        $env:RUST_BACKTRACE = '0'
    }
    & $binary @ForwardedArguments
    exit $LASTEXITCODE
}

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $skillRoot '../../../..'))
$workspaceManifest = Join-Path $repoRoot 'Cargo.toml'
$crateManifest = Join-Path $repoRoot 'crates/split-test/Cargo.toml'
if ((Test-Path -LiteralPath $workspaceManifest) -and (Test-Path -LiteralPath $crateManifest) -and (Get-Command cargo -ErrorAction SilentlyContinue)) {
    if ($null -eq $env:RUST_BACKTRACE) {
        $env:RUST_BACKTRACE = '0'
    }
    & cargo run --quiet --locked --manifest-path $workspaceManifest -p split-test --bin split-test -- @ForwardedArguments
    exit $LASTEXITCODE
}

[Console]::Error.WriteLine("error: missing packaged split-test binary at $binary")
[Console]::Error.WriteLine("hint: reinstall a package containing the $platformId release artifact")
exit 127
