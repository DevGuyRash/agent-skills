# Verify Desktop Outcomes

Separate capability exposure, live operation, and product effect. Verification
is a second observation, not a restatement of the action response.

## Live Capability Evidence

| Channel | Evidence required to call it operational |
|---|---|
| Targeting | Uniquely list, identify, activate, and refind the intended window |
| Semantic | Read current accessible state and transact an action or value operation |
| Observation | Capture or independently inspect the relevant current UI |
| Keyboard | Send targeted input and observe its effect in the intended target |
| Pointer | Derive coordinates from current geometry and observe the intended effect |
| Geometry | Read bounds, request a change, and confirm final bounds |
| Verification | Observe the requested postcondition independently of delivery acknowledgement |

Probe only channels needed for the task. A diagnostic summary may establish
availability, but only a current low-risk transaction establishes operation.

## Action Evidence Record

Before each state change, retain:

- **Target:** stable identity plus the evidence that distinguishes it.
- **Precondition:** smallest observed state needed to act safely.
- **Action:** one bounded operation and the channel used.
- **Expected transition:** concrete, user-visible change.
- **Independent observation:** state read after the action.
- **Disposition:** `verified`, `unverified`, `blocked`, or `not attempted`.

Keep this record in conversation context. Refresh it after navigation, relaunch,
process replacement, focus change, workspace switch, or display reconfiguration.

WHEN evaluating the independent postcondition THEN you SHALL require evidence
that distinguishes success from plausible alternatives. A disappeared dialog,
navigation, or absence of an error is insufficient when cancel, close, crash, or
unrelated navigation could produce the same observation. In that case, observe
the persisted value, confirmation state, or downstream product effect; otherwise
report `unverified`.

## Focus Discipline

Activation is not durable proof of focus. Immediately before targeted input,
refind the intended target and compare it with the focused target when that
evidence is available. After input, verify the effect belongs to the same target.

WHEN a target-scoped lookup can uniquely identify and refind the intended
target THEN you SHALL use it instead of global desktop enumeration. IF global
enumeration is the only safe way to resolve ambiguity THEN you SHALL minimize
its use and SHALL NOT retain, restate, or report unrelated entries.

AFTER a target-scoped observation THEN you SHALL confirm that the response
actually resolved the intended target and that the returned scope remains
target-scoped. A requested selector is not evidence about the response. IF
resolution fails or the response falls back to broader desktop state THEN you
SHALL discard unrelated payload, SHALL NOT treat it as target evidence, and
SHALL NOT repeat the call without new evidence.

Use stable opaque identifiers as strings. Do not numerically transform window or
process identifiers, and do not choose among ambiguous matches by list order.

## Coordinate Discipline

Record image width and height, captured desktop bounds, crop origin, display
origin, and any resize scale. Convert coordinates only when this relationship is
known. Account for negative display origins and nonuniform layouts.

BEFORE inspecting or using a requested target-scoped image THEN you SHALL
confirm from returned metadata that the capture is cropped to the intended
target and is consistent with its current bounds. IF the response is broader,
unresolved, or lacks enough scope evidence THEN you SHALL discard the image and
obtain a narrower observation.

If an image was resized from captured size `(capture_w, capture_h)` to
`(image_w, image_h)`, a point maps proportionally only when the resize preserved
the entire capture without padding or cropping:

```text
desktop_x = capture_origin_x + image_x * capture_w / image_w
desktop_y = capture_origin_y + image_y * capture_h / image_h
```

Otherwise, obtain fresh metadata or avoid pointer input.

## Completion Report

Use this compact shape:

```text
Outcome: <requested result>
Status: verified | unverified | blocked | not attempted
Evidence: <independent post-action observation>
Degraded channels: <only channels proven unavailable>
Remaining action: <minimum user or system action, or none>
```

Minimize captured and reported information. Refer to unrelated applications or
screen content only when required to explain a targeting ambiguity or blocker.
