# Companion Channels (App CLIs, Sockets, Eval Bridges)

Many desktop apps expose a scripting channel: a companion CLI, a UNIX
socket, a debug port, or an in-app eval bridge. These channels are the
fastest way to drive and verify an app — and the easiest place to
corrupt your own session. Treat the channel as fragile transport with a
hostile parser on each side.

## Know which binary you are talking to

- The companion CLI's name may collide with the app's launcher. WHEN a
  command could resolve to either THEN you SHALL confirm which binary is
  on PATH before the first invocation — passing scripting arguments to
  the launcher can open windows or disturb the user's live session
  instead of talking to the IPC shim.

## Payload survival across parser boundaries

A payload crosses at least three parsers: your shell, the CLI's argument
parser, and the app's interpreter. Each has characters it will eat.

- WHEN a CLI parses `key=value` arguments THEN you SHALL pass code or
  data payloads as one explicitly named, single-quoted value. Payload
  characters that look like argument syntax (`=`, `=>`, spaces) mis-split
  otherwise.
- WHEN a payload still fails to parse THEN you SHALL rewrite it to avoid
  the outer parsers' trigger characters (classic JS example: `function`
  expressions instead of arrow functions, string concatenation instead
  of template literals) or move the payload into a file and pass the
  path.
- Long payloads mixing quoting styles, async constructs, and string
  building fail silently or mangle. You SHOULD decompose one big probe
  into several tiny ones, each returning a single value.

## Getting results back

Eval-style bridges typically return only a synchronous value: they
cannot await promises, and they swallow logging output.

- WHEN a probe is asynchronous THEN you SHALL have the app persist the
  result somewhere you can read out-of-band (a file the app writes via
  its own storage API, with the write chained so the bridge awaits it),
  then read that artifact from the shell.
- WHEN the result artifact is missing THEN you SHALL treat that as "the
  probe never ran" — a parse or quoting failure — not as an empty
  result. Fall back to a smaller probe.
- WHEN a probe both mutates and measures THEN you SHOULD make it atomic
  (one round trip that acts, waits internally, and returns the
  measurement). Separate act/measure calls straddle app rebuilds and
  race repaints.

## Timing discipline

- You SHALL NOT call the channel while the app is booting or shutting
  down (see the lifecycle reference: a call during boot can spawn a
  second instance and destroy the endpoint).
- One probe at a time, with a generous settle after actions that
  re-render or reload. Rapid-fire probing of an unhealthy channel makes
  the diagnosis worse and can itself be the destroyer.
- Results captured mid-reload (screenshots included) are not evidence.
  WHEN the app reloaded between your action and your observation THEN
  you SHALL re-observe.

## Bridge daemons

When the channel is served by a separate daemon or bridge process:

- Expect it to die with (or independently of) what it proxies. Keep an
  idempotent, detached respawn ready; verify respawn by a live probe,
  not by the spawn command's exit.
- Never let a wedged input path keep writing into user documents.
  Prefer clipboard-paste (set clipboard, send one paste chord) over long
  synthetic typing for large text: one stuck key repeating into a user
  file is data corruption.

## Verification stance

A channel acknowledgement is transport evidence only. The sibling
Linux Desktop Control skill's verification contract applies unchanged:
observe the user-visible or persisted outcome through an independent
read before reporting success.
