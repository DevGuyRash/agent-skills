# Application Lifecycle

Rules for starting, stopping, counting, and coexisting with desktop
applications. The unit of care is the app's *external state*: processes,
lock and socket files, and the human who may be using it right now.

## Launching

- WHEN you launch a GUI application from a tool shell THEN you SHALL
  detach it from that shell (`setsid`, `systemd-run --user`, or the
  host's equivalent) so it survives the shell and inherits the session's
  display environment. A plain `&` child of an ephemeral shell can die
  with the shell or lose its display/session variables — and a launch
  missing the session environment exits silently, leaving your readiness
  wait hanging until timeout with nothing to observe.
- WHEN an app is single-instance THEN you SHALL treat every launcher
  invocation — including CLI subcommands that share the launcher's
  binary name — as a potential second-instance trigger. A second
  instance can seize and then destroy shared endpoints (sockets, locks)
  on its way out.
- AFTER launching THEN you SHALL wait for a positive readiness signal
  (endpoint exists, window appears, health probe answers) before the
  first companion-channel call. You SHALL NOT probe the app during its
  boot window: for some apps a probe IS a launch.

## Terminating

- BEFORE killing an app THEN you SHALL confirm the human is not actively
  using it (recent window focus, user-initiated relaunches, edits
  appearing that you did not make). IF the app keeps reappearing after
  termination THEN you SHALL stop killing it and adapt — the respawner
  is a session manager or the user, and both outrank you.
- You SHOULD prefer the app's own reload/refresh mechanism over a
  process kill when one exists; a kill destroys window state, unsaved
  UI state, and shared endpoints.
- AFTER sending a termination signal THEN you SHALL allow a settle
  period and re-verify the process table before relaunching. Relaunching
  into a dying instance creates the dual-instance race above.
- Signal-based teardown commands (`pkill`, `kill`) routinely exit
  nonzero even when they worked (the signal itself is the "error").
  WHEN judging teardown success THEN you SHALL probe process and
  endpoint state afterwards, and SHALL NOT trust the exit code.

## Counting processes honestly

- Multiprocess GUI apps (Electron, Chromium-family, anything with GPU or
  network helpers) show many processes for one running instance. WHEN
  deciding "is it running" or "how many instances" THEN you SHALL match
  the main process's distinctive command line, not a substring that
  helpers also carry.
- `pgrep -f` / `pkill -f` match full command lines, including the shell
  that is running your own check. WHEN pattern-matching processes THEN
  you SHALL exclude your own shell and the matcher itself, or narrow the
  pattern until self-matches are impossible. A pattern kill that matches
  its own invoking shell reports failure and can terminate your probe.

## Stale endpoints and recovery

Abnormal exits leave socket/lock files behind, and a stale file blocks
the next bind. In-app toggles usually re-attach to the dead inode; only
removing the file and restarting cleanly recovers.

The recovery ritual, in order, when an app's companion endpoint is dead:

1. Remove the stale endpoint file(s).
2. Terminate every instance of the app; verify the process table is
   actually empty (see counting rules above).
3. Relaunch once, detached.
4. Wait for the endpoint with a condition-based wait — no companion
   calls at all during the wait.
5. Verify with one low-risk probe before real work.

- WHEN the ritual fails once THEN you SHALL re-diagnose (who recreated
  the endpoint? did something respawn?) rather than looping the ritual.

## Lazy activation

Presence in configuration is not "loaded". Hosts and launchers may defer
plugin/extension activation until a relevant document or surface is
opened. WHEN a component you expect is absent THEN you SHALL trigger its
activation condition (open the document type it handles) before
concluding it is broken or missing.

## Attribution discipline

On a live desktop, unexpected UI (dialogs, pickers, focus changes) may
be the echo of your own probes. WHEN you observe surprising app state
THEN you SHALL first check whether your own recent action caused it
before treating it as a defect or as user action.
