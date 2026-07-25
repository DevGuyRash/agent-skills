# Recover Desktop Control

Recover per channel. Do not restart a whole workflow when an independent channel
and the target state remain valid.

## Recovery Matrix

| Observation | Interpretation | Response | Stop condition |
|---|---|---|---|
| Tools are not callable in this thread | Host capability is absent from current context | Route to another capable surface or request a fresh enabled session | Do not invent a namespace or command |
| Readiness says usable but a live probe fails | Readiness was presence-level or stale | Mark only the failed channel degraded and retain the transaction evidence | Do not repeat the same probe without changed state |
| Target list has several plausible matches | Target identity is ambiguous | Add stable attributes or ask for the minimum disambiguation | Do not send input by list position |
| Focus differs from the selected target | Focus was stolen or activation failed | Refind and reactivate the stable target, then recheck focus | Stop if focus cannot be established safely |
| Target disappears after navigation or restart | Cached identity is stale | Discard window, semantic, and coordinate state; discover again | Never reuse the old identity |
| Semantic tree is empty, stale, or disconnected | The target or accessibility session is not operational | Refresh once, then use another proven channel | Do not infer that all desktop control failed |
| Observation fails | Visual channel is unavailable or permission-limited | Use semantic or product-state evidence, or discover a safe observation fallback | Report `unverified` if no independent observation exists |
| Permission request is denied or canceled | User or host declined that channel | Preserve the decision and choose another channel | Do not loop or broaden permissions automatically |
| Keyboard delivery has no effect | Focus, target, or key path is wrong | Refresh target and pre-state before one alternate-channel attempt | Stop after the bounded retry |
| Pointer delivery has no effect | Coordinates, scaling, focus, or target may be wrong | Re-observe; prefer semantic or keyboard input; rebuild coordinates if needed | Never click repeatedly at the same point |
| Geometry operation is unsupported | Advertised surface exceeds active backend support | Discover a safe host-native geometry capability or report the limitation | Restore original geometry after testing |
| Independent evidence conflicts | The product state is uncertain | Preserve both observations and classify `unverified` | Do not select the more convenient observation |

## Native Fallback Qualification

A fallback is eligible only when all of these are known:

- it is installed and its current help or discovery output confirms the needed operation;
- it can target the intended surface without a fuzzy global match;
- its action is within the user's authorization;
- its result can be observed independently;
- it does not require an unapproved persistent system change.

Treat fallback command acceptance as transport evidence. Preserve the same
targeting and verification discipline used for host-provided controls.

## Retry Budget

One retry is justified only by new evidence: refreshed identity, corrected focus,
new geometry, changed permission state, or an alternate operational channel. If
none changed, stop and report the blocker instead of consuming more attempts.
