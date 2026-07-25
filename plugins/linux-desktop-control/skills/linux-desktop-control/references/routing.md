# Routing Desktop Work

Choose the surface that owns the requested outcome. Desktop simulation is a
last-mile interaction mechanism, not a default replacement for semantic tools.

## Ownership Matrix

| Requested surface | Primary owner |
|---|---|
| Page DOM, forms, navigation, and page accessibility | Browser automation |
| Existing browser profile when the browser connector can reach the surface | Browser connector |
| Repeatable browser product regression | End-to-end browser tests |
| Browser chrome, extensions, downloads, developer tools, or native browser dialogs | Desktop control |
| Native application, panel, launcher, settings surface, or system dialog | Desktop control |
| Pure service, adapter, or backend behavior | Unit or integration tests |
| OS-level visual or interaction proof | Desktop control |

## Selection Questions

Answer in order:

1. What observable result would prove the request complete?
2. Which surface owns that result: API, page, browser chrome, native app, or OS?
3. Can a semantic connector or lower test tier prove it without simulated input?
4. Does the task require existing desktop-only state or a native permission UI?
5. Is independent observation available after the action?

Prefer the narrowest capable surface. A direct API is stronger for data state; a
browser tool is stronger for page content; desktop control is necessary when
the interaction or proof crosses into native UI.

## Boundary Transitions

A workflow may change owners. Re-route when:

- page content opens a native chooser or permission dialog;
- browser automation reaches extension or browser settings UI it cannot inspect;
- a native application opens a web page that a browser tool can handle better;
- a GUI action can be arranged or verified through an app-owned API;
- repeatability becomes the goal and the workflow should become an automated test.

Preserve the verified state at each transition. Do not assume a browser target,
window target, or authentication context transfers automatically between tools.

## Decision Outcomes

- **Desktop selected:** name the target surface and required proof.
- **Different tool selected:** route immediately and avoid probing desktop channels.
- **Mixed workflow:** assign each phase to one owner and define the handoff state.
- **No capable surface:** identify the missing capability and minimum user action.
