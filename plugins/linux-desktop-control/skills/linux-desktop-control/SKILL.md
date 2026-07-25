---
name: Linux Desktop Control
description: >-
  REQUIRED when Codex will inspect, control, troubleshoot, or verify a Linux
  desktop UI — do not operate native GUI surfaces without this skill active.
  Covers: (1) Native applications, system UI, panels, launchers, and dialogs,
  (2) Browser chrome, extension managers, downloads, permissions, and developer
  tools, (3) Authenticated desktop-browser state unavailable to isolated
  automation, (4) Readiness or recovery for targeting, screenshots,
  accessibility, keyboard, pointer, or window geometry, and (5) OS-level
  interactive GUI testing. Use browser automation instead for ordinary
  DOM-first page work. If the task involves Linux desktop control, use this skill.
---

# Linux Desktop Control

Use host-provided desktop capabilities as an orchestration surface. This skill
does not supply screenshot, accessibility, input, portal, compositor, or window
management implementations.

> A tool acknowledgement is not product success. Success requires observing the requested user-visible state after the action.

## Start Here

1. Read `<skills-file-root>/references/routing.md` and choose the narrowest
   capable surface.
2. Discover the tools callable in this thread. Treat configuration, installed
   software, documentation, and previous sessions as non-authoritative.
3. Build a live capability record for targeting, semantic access, observation,
   keyboard, pointer, geometry, and verification.
4. Record the intended target, pre-state, expected transition, and independent
   observation in conversational scratch state.
5. Execute one bounded state-changing step at a time and verify it before
   continuing.

Keep desktop-changing operations serialized. Focus is shared mutable state, so
parallel GUI actions can invalidate otherwise-correct targeting.

## Capability Record

Track each channel independently:

- `available`: a potentially relevant capability is exposed;
- `operational`: a current, low-risk transaction succeeded;
- `effect verified`: the requested UI state was observed independently.

Aggregate readiness is a routing hint. It is not evidence that every channel is
operational. Read `<skills-file-root>/references/verification.md` before
claiming an interaction succeeded or before translating image coordinates into
desktop coordinates.

## Action Contract

1. WHEN native desktop control is required THEN you SHALL discover the capabilities callable in the current thread.
2. WHEN capability state is unknown, stale, or contradicted by an operation THEN you SHALL probe the relevant channel with a live, low-risk transaction.
3. BEFORE sending input THEN you SHALL uniquely identify and activate the intended target.
4. BEFORE changing state THEN you SHALL record the expected user-visible transition and the smallest useful pre-state.
5. WHEN multiple operational channels exist THEN you SHALL prefer semantic action or value setting, followed by targeted keyboard input, followed by pointer input derived from fresh visual geometry.
6. AFTER a state-changing action THEN you SHALL independently observe its expected postcondition.
7. WHEN a tool reports success but the expected state does not change THEN you SHALL classify the result as `unverified`.
8. WHEN an action is `unverified` THEN you SHALL refresh target and focus state before making at most one bounded retry through a different operational channel.
9. WHEN navigation, relaunch, restart, process replacement, workspace change, or display reconfiguration occurs THEN you SHALL invalidate cached window, accessibility, and coordinate identities.
10. WHEN one capability fails THEN you SHALL degrade only that capability and retain independently proven channels.
11. WHEN a target cannot be distinguished safely THEN you SHALL NOT send input until the ambiguity is resolved.
12. WHEN an image is resized, cropped, scaled, or assembled from multiple displays THEN you SHALL establish its mapping to desktop coordinates before pointer input.
13. WHEN the pointer coordinate space cannot be established THEN you SHALL NOT use blind coordinate interaction.
14. WHEN a permission request is denied, canceled, or ends without a grant THEN you SHALL NOT repeat it indefinitely.
15. WHEN a safe native recovery capability is needed THEN you SHALL discover whether an appropriate installed utility exists before proposing or invoking it.
16. WHEN using a native fallback THEN you SHALL verify its outcome through a separate observation channel.
17. WHEN the requested operation is destructive, externally consequential, or permission-changing THEN you SHALL preserve the host's approval and authorization boundary.
18. IF no desktop-control capability is callable THEN you SHALL report that limitation and route to a browser tool, direct API, test harness, or user-assisted step; ELSE you SHALL use only capabilities proven in this session.
19. WHEN reporting completion THEN you SHALL label the result as `verified`, `unverified`, `blocked`, or `not attempted`.
20. WHEN a target-scoped lookup can uniquely identify and refind the intended target THEN you SHALL use it instead of global desktop enumeration; IF global enumeration is the only safe discovery path THEN you SHALL minimize its use and SHALL NOT retain, restate, or report unrelated entries.
21. AFTER a target-scoped observation THEN you SHALL verify that the response resolved the intended target and that its returned scope matches that target; IF resolution fails or the response broadens scope THEN you SHALL discard unrelated payload, SHALL NOT use it as target evidence, and SHALL NOT retry without new evidence.
22. BEFORE inspecting or using a requested target-scoped image THEN you SHALL confirm that returned metadata proves the capture is cropped to the intended target; IF scope is absent, broader, or inconsistent with target bounds THEN you SHALL discard it and obtain a narrower observation.

## Failure Handling

Read `<skills-file-root>/references/recovery.md` when a readiness result and a
real operation disagree, focus changes, a target disappears, input has no
visible effect, permissions block a channel, or the backend does not implement
an advertised operation.

Do not replace observable waits with arbitrary sleeps. Do not repeat an action
without new target or capability evidence. Do not infer success from an exit
code, delivery receipt, or lack of an error.

Read `<skills-file-root>/references/portability.md` when display scaling,
multiple monitors, session type, compositor behavior, accessibility exposure,
or a native fallback affects the control plan.

## Reference Index

Load only the reference required for the current decision.

| Reference | Read when |
|---|---|
| `<skills-file-root>/references/routing.md` | Selecting desktop control versus browser automation, APIs, or tests |
| `<skills-file-root>/references/verification.md` | Probing channels, mapping coordinates, recording evidence, or reporting status |
| `<skills-file-root>/references/recovery.md` | A channel, target, permission, or expected effect fails |
| `<skills-file-root>/references/portability.md` | Session, display, compositor, or fallback differences matter |

## Completion Report

Report the requested outcome first, followed by its status, the observation that
supports that status, any degraded channels, and any remaining user action.
Mention only target information needed to understand the result. Do not expose
unrelated window titles or screen content.
