# Portable Linux Desktop Control

Base decisions on capabilities rather than desktop names. Session type and
compositor family explain likely behavior, but a live transaction remains the
source of truth.

## Environment Inventory

Collect only facts needed by the requested operation:

- graphical session type, such as Wayland or X11;
- active compositor or window-manager family;
- display count, origins, logical sizes, scales, and rotations;
- target application's accessibility exposure;
- callable host-provided channels;
- installed native utilities relevant to a failed channel.

Do not turn inventory into a prerequisite checklist. A partially configured
environment can still support a verified workflow through surviving channels.

## Capability-First Expectations

| Environment characteristic | Planning implication |
|---|---|
| Wayland session | Input, capture, and window control may be mediated independently |
| X11 session | Global coordinates may be available, but focus and effect still require verification |
| Stacking desktop | Window activation and geometry may come from separate integrations |
| Tiling environment | Requested geometry may be advisory or compositor-controlled |
| Accessibility-aware app | Semantic interaction may be stronger than visual coordinates |
| App without accessible state | Keyboard or visual control may be required |
| Multiple or scaled displays | Image pixels and logical desktop coordinates may differ |
| Headless session | Native GUI control may be unavailable even when binaries are installed |

These are hypotheses for selecting probes, not permission to claim support.

## Display and Image Portability

Treat desktop coordinates as a global logical space that may include negative
origins. Treat every image as its own pixel space. Record the relationship before
mapping a point between them.

Rebuild the relationship after display hot-plug, scale change, rotation,
workspace change, target movement, or fresh capture with different bounds.

## Fallback Discovery

When a host channel fails, discover rather than assume:

1. Identify the failed capability, not merely the failed tool.
2. Inspect available native utilities and their current command discovery.
3. Choose the narrowest utility that can target the required surface.
4. Prefer nonpersistent, reversible operations.
5. Verify the result through a different channel.

Examples in one environment are evidence about a capability class, not a
portable dependency. Never encode a local utility path, service name, or fixed
backend namespace into the core workflow.

## Validation Claims

Report physical testing only for environments actually exercised. Use
transcript-driven fixtures to test reasoning about other environment families,
and label those fixtures as simulated rather than live compatibility proof.
