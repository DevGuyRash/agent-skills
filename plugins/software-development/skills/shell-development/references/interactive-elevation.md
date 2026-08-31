# Interactive Elevation

Use elevation only when the requested task cannot be completed unprivileged. The user's authorization covers the exact task launched through a visible operating-system authentication or consent surface; it does not authorize unrelated administrative work.

## Invariants

- Resolve the operating system, current desktop or terminal session, trusted task, and supported elevation surface before launching anything.
- Keep the credential entirely between the user and the operating system. Never read, type, capture, relay, log, persist, request, or pre-answer it. Do not use `sudo -S`, a credential-bearing command argument or environment variable, `Start-Process -Credential`, or an inline password.
- Prefer a fixed, trusted executable or script with structured arguments. Do not concatenate task data into shell, AppleScript, or PowerShell source.
- Surface the prompt where the user can see what is requesting elevation. When a terminal prompt is required, discover an installed user-visible terminal and its documented execute/wait interface; do not transplant flags from another terminal emulator.
- Run the smallest privileged wrapper that contains the complete task. A sudo timestamp may be scoped to a process or terminal and must not be assumed to authorize an unrelated child such as Ansible.
- Wait for the owned process with a bound, preserve its exit status, and report an indeterminate still-running task without blindly retrying it.
- Fail closed with a user-runnable command when no supported visible surface exists. Never leave a password prompt in an invisible tool terminal.

## Linux and other sudo hosts

Use a visible terminal when sudo needs a terminal prompt. The Konsole `--separate -e` surface was exercised on a Linux workstation and opened a separate window with a real sudo prompt; the generalized structured-argument form below is syntax-tested. Replace the repository and task paths only with already resolved absolute trusted paths:

```bash
repo=/absolute/trusted/repository
task=/absolute/trusted/task

/usr/bin/konsole --separate -e \
  /usr/bin/bash --noprofile --norc -c '
    cd "$1" || exit 70
    shift
    exec "$@"
  ' visible-elevation "$repo" /usr/bin/sudo -k -- "$task"
```

This is a Konsole adapter, not a universal terminal command. For another installed terminal, inspect its own documented argument boundary and wait behavior first. Do not hard-code a terminal preference into portable policy.

When the current graphical session already has a trusted askpass program, resolve its absolute path from explicit system or repository configuration, verify its ownership and write permissions for the host, and pass it directly:

```bash
askpass=/absolute/trusted/askpass
if [[ -z $askpass || $askpass != /* || ! -x $askpass ]]; then
  printf '%s\n' 'No trusted graphical sudo askpass helper is configured.' >&2
  exit 69
fi

SUDO_ASKPASS=$askpass /usr/bin/sudo -k -A -- /absolute/trusted/task
```

Do not guess `DISPLAY`, `WAYLAND_DISPLAY`, `DBUS_SESSION_BUS_ADDRESS`, or another user's runtime directory. A locally exercised KDE credential-validation probe used `SUDO_ASKPASS=/usr/bin/ksshaskpass /usr/bin/sudo -A -v` inside the existing graphical session; that command validates only its own sudo context and is not evidence that a later child process inherits authorization. Prefer launching the exact privileged task directly as shown above.

## Windows with PowerShell 7

Use Windows UAC through the `runas` shell verb from an interactive Windows session. An administrator may receive a consent prompt while a standard user receives a credential prompt; either remains between Windows and the user. Keep both the PowerShell 7 installation and payload at administrator-protected paths. `ProcessStartInfo.ArgumentList` preserves individual arguments without constructing a PowerShell command string.

```powershell
if (-not $IsWindows) {
    throw 'This elevation adapter requires Windows.'
}

$programFiles = [Environment]::GetFolderPath(
    [Environment+SpecialFolder]::ProgramFiles
)
$taskPath = Join-Path $programFiles 'AgentTools\ElevatedTask.ps1'
$task = Get-Item -LiteralPath $taskPath -Force -ErrorAction Stop

if (
    $task.PSIsContainer -or
    (($task.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)
) {
    throw 'The elevated task must be a regular, non-reparse-point file.'
}

$pwsh = Join-Path $PSHOME 'pwsh.exe'
if (-not [IO.File]::Exists($pwsh)) {
    throw 'The current PowerShell 7 executable was not found.'
}

$startInfo = [Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $pwsh
$startInfo.UseShellExecute = $true
$startInfo.Verb = 'runas'

foreach ($argument in @(
    '-NoLogo'
    '-NoProfile'
    '-NonInteractive'
    '-File'
    $task.FullName
)) {
    [void] $startInfo.ArgumentList.Add($argument)
}

try {
    $process = [Diagnostics.Process]::Start($startInfo)
}
catch [System.ComponentModel.Win32Exception] {
    if ($_.Exception.NativeErrorCode -eq 1223) {
        throw 'Elevation was declined by the user.'
    }
    throw
}

if ($null -eq $process) {
    throw 'Windows did not start the elevated process.'
}

try {
    if (-not $process.WaitForExit(900000)) {
        throw 'The elevated task is still running after 15 minutes; do not retry it blindly.'
    }
    if ($process.ExitCode -ne 0) {
        throw "The elevated task failed with exit code $($process.ExitCode)."
    }
}
finally {
    $process.Dispose()
}
```

This adapter targets PowerShell 7 on Windows. PowerShell running on Linux or macOS must use that operating system's elevation surface instead. Validate the Windows implementation on an actual supported Windows host before claiming runtime acceptance.

## macOS

Use macOS authorization for a fixed, protected helper. Keep dynamic values out of AppleScript source:

```bash
/usr/bin/osascript <<'APPLESCRIPT'
do shell script (quoted form of "/Library/Application Support/AgentTools/elevated-task") with administrator privileges
APPLESCRIPT
```

The operating system owns the password or biometric prompt. macOS may reuse a recent authorization instead of displaying a fresh prompt; when fresh manual confirmation is required, use a discovered visible terminal with `sudo -k` rather than assuming AppleScript will reprompt. The helper must validate its own inputs, avoid secret output, and return a meaningful status. Validate this adapter on a supported macOS host before claiming runtime acceptance.

## Evidence boundary

The Konsole prompt surface and KDE `ksshaskpass` validation probe above were exercised on Linux, and every Bash block passes `bash -n`. The complete generalized Konsole command, direct askpass task, Windows UAC adapter, and macOS adapter are based on their platform interfaces but require runtime verification on their target systems. Never generalize acceptance from one operating system or terminal emulator.

Platform references: [Konsole command-line options](https://docs.kde.org/stable_kf6/en/konsole/konsole/command-line-options.html), [sudo manual](https://www.sudo.ws/docs/man/sudo.man/), [Windows UAC behavior](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/how-it-works), [.NET structured process arguments](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist), [.NET process verbs](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.verb), [PowerShell `Start-Process`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/start-process), and [AppleScript `do shell script`](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/reference/ASLR_cmds.html).
