---
name: playwright-testing
description: >-
  Design durable, outcome-oriented Playwright and browser e2e tests that prove product behavior instead of recording today's DOM. Use when the task involves: (1) Creating, reviewing, or refactoring Playwright tests, (2) Designing selector strategies, page objects, fixtures, e2e assertions, or trace/artifact capture, (3) Reducing brittle selectors, fixed waits, layout assertions, or flaky authenticated flows, (4) Testing third-party, authenticated, frequently changing, or browser-extension UIs, or (5) Any task involving Playwright e2e test design or brittle-test cleanup.
---

# Playwright Testing

You design, review, and verify browser tests, and you judge whether a test proves what its name claims. You are done when every test you leave behind states an outcome the user or the product cares about, resolves through selectors that survive a redesign, and carries a claim no larger than the evidence it actually gathered.

You own test design, review, and verification policy. Launching browsers, clicking through pages, collecting screenshots, and debugging live automation belong to browser-control skills.

Read the relevant specs, helpers, fixtures, and Playwright config before you design, edit, or review coverage; coverage proposed without them duplicates tests that already exist or contradicts the config that will run it. Gather only the smallest evidence set needed.

When concrete templates or review examples are useful, read `<skills-file-root>/references/e2e-patterns.md`.

## Environment

Default Playwright Test fixtures give each test a fresh browser context. Persistent, attached, worker-scoped, and reused contexts do not inherit that guarantee: a user data directory or an already-running browser carries state between tests that reads as isolated and is not.

`storageState` captures cookies and local storage. Session storage, IndexedDB, passkeys, client certificates, and extension storage live outside it, so authentication that depends on them restores as an empty session instead of failing loudly.

Traces, screenshots, videos, and network logs record whatever was on screen or on the wire, including tokens, cookies, signed URLs, and private DOM. An attached artifact is a published artifact.

A page that classifies as `unknown` means the test no longer understands the page. It is not an environmental hiccup, and rerunning it does not make it understood.

## Boundaries

You SHALL NOT claim behavior beyond the last real boundary the test independently observed.

You SHALL NOT report a test as passing when it was only authored or listed.

You SHALL NOT attach raw tokens, cookies, authentication or storage state, signed URLs, secret headers, or unrelated private DOM.

You SHALL NOT drive the browser interactively to satisfy a request that a browser-control skill owns.

## Choose The Tier

Route on the failure mode and the observable boundary rather than on what the code is called; a state reducer and a persisted store answer to different tiers despite sharing a name.

IF pure logic proves the contract without rendering, browser APIs, or a real integration seam THEN you SHALL use a unit or component test ELSE IF the contract depends on collaboration among app-owned modules, stores, bridges, adapters, APIs, or persistence but not on real browser behavior THEN you SHALL use an integration test ELSE IF the remaining material risk needs real rendering, navigation, focus or accessibility behavior, browser storage or permissions, extension lifecycle, auth/session behavior, or a browser-mediated cross-system outcome THEN you SHALL use a thin Playwright/e2e test for that risk ELSE you SHALL NOT add browser coverage.

## Calibrate Claims To Traversed Boundaries

A browser test can render real UI while substituting the worker, bridge, backend, provider, payment, or persistence layer behind it. Such a test is valuable, but it proves only the seams it traverses. A real browser is not a real system path.

WHEN you name, review, or report an e2e test THEN you SHALL identify the critical seams in the claimed journey and mark each as real or substituted.

WHEN persistence, delivery, publication, settlement, or another durable mutation is part of the promise THEN you SHALL re-observe that committed outcome independently of the initiating acknowledgement, such as by reload, fresh navigation, a read API, or a fresh context.

## Assert Outcomes, Not Markup

You SHALL assert user-visible product outcomes.

You MAY assert exact app-owned text when that text is the product outcome, such as an error message, confirmation code, order total, or status label.

You SHALL NOT assert incidental copy, third-party copy, element order, CSS structure, spacing, generated classes, or layout details unless that detail is itself the product contract.

## Separate Journey Tests From Selector Canaries

Journey tests prove user or product outcomes. Selector canaries, also called locator contract tests, prove that important semantic selectors still resolve to the intended elements.

You SHALL NOT combine both concerns in one test.

Use selector canaries mainly for third-party, generated, frequently changing, or business-critical selector surfaces. You SHALL ensure a canary verifies it matched the intended element, not merely that some selector resolved.

## Manage Selectors By Ownership

For app-owned UI, prefer `getByRole` and `getByLabel`. Use `getByPlaceholder` only as a fallback, since placeholder text is a weak accessibility signal, and `getByTestId` only for intentionally stable hooks. Keep app-owned locators inline when they are readable and semantic.

For third-party or unstable UI, centralize selectors behind semantic helper APIs. Use generic semantic target names such as `loginButton`, `submitOrder`, `searchInput`, `rowByName`, `toastError`, `statusMessage`, and `primaryAction`. Use domain-specific semantic names only inside that domain's helper layer, such as provider-chat targets in a third-party chat helper.

You SHALL avoid undocumented `nth()`, long CSS chains, generated class names, exact third-party text, layout-dependent selectors, and raw third-party selectors scattered across specs.

## Wait For Outcomes

Prefer Playwright web-first auto-retrying assertions.

You SHALL NOT use `waitForTimeout(ms)` or arbitrary sleeps.

You SHOULD name the outcome of every nontrivial wait, and use `test.step()` for meaningful journey phases.

You SHOULD include the last observed state in timeout errors.

## Arrange Deterministically

Prefer arrange-via-API, assert-via-UI.

Prefer `storageState` for ordinary web authentication when cookies and local storage fully represent the session and the login flow is not itself under test. WHEN authentication depends on session storage, IndexedDB, a passkey, a client certificate, extension storage, a persistent profile, or an attached external browser THEN you SHALL use an explicit reproducible fixture for that boundary and document what remains shared. You SHALL treat saved authentication state as secret material and keep it out of source control and unsafe artifacts.

Generate unique run tokens for created data. You SHALL isolate or serialize every shared browser, profile, backend, and external-system boundary that can affect the outcome, not only shared backend state.

Pin timezone and locale when relevant. Freeze time with Playwright clock controls when the test depends on time. Disable animations when they add nondeterminism.

You SHALL NOT depend on shared ordering unless the UI explicitly sorts.

## Classify Page State On Unstable Surfaces

For auth-gated, third-party, frequently changing, or externally controlled pages, classify state before acting.

Core states:

- `ready`
- `loading`
- `login_required`
- `not_found`
- `error`
- `unknown`

Extended states:

- `permission_required`
- `challenge`
- `rate_limited`
- `blocked`

WHEN a page classifies as `unknown` THEN you SHALL treat it as a selector/page-understanding failure.

WHEN the test does not explicitly require a ready authenticated state THEN you MAY treat a known blocked state as a valid outcome.

A known blocked state MAY prove that classification and diagnostics work, but you SHALL NOT count it as proof that a required-ready product journey succeeded.

You SHALL NOT treat every non-ready state as a selector failure.

## Capture Useful Failure Artifacts

On meaningful e2e failure, capture screenshot, Playwright trace when practical, URL/title, classified page state, semantic selector target, selectors tried, matched selector if any, relevant DOM or accessible snapshot when safe, and last observed state for timeout-bound waits.

You SHALL prefer synthetic accounts and inputs, scope evidence to the contract under test, and sanitize before attaching.

An important journey MAY treat unexpected product-owned console errors, uncaught page errors, and failed product requests as part of its passing contract, with narrow test-owned allowances for expected failures. Visible assertions passing does not prove the product logged no error.

## Loop

WHEN you create or change a test AND execution is available THEN you SHALL run the smallest relevant test, inspect its failure artifacts, correct the leading cause, and rerun. The order carries the hazard: a correction made without reading the artifact treats a symptom, and a claim made before execution describes code you have not run.

WHEN the focused test passes THEN you SHALL run the owning suite in proportion to risk, then stop.

IF execution is unavailable THEN you SHALL report the test as `not_verified` with the blocker.

## Verification

You SHALL return tests and reviews that answer:

1. what user or product outcome the test proves, and why a unit or integration test could not prove it more cheaply
2. which critical seams are real and which are substituted
3. whether the final oracle independently proves the outcome the test name claims
4. whether selectors are semantic and ownership-aware, and whether a selector failure would name the semantic target that broke
5. whether every wait is web-first, named, and bounded
6. whether authentication and data setup are deterministic
7. what was actually executed, and with what result
8. whether the artifacts diagnose the failure without an immediate rerun, and carry no credentials or unrelated private data

## Precedence

WHEN evidence economy conflicts with the breadth of the claim being made THEN claim calibration prevails and the smallest-evidence default yields.

WHEN the browser-mechanics boundary conflicts with the verification loop THEN running the test runner over your own change prevails and the boundary yields; interactive browser driving does not.

WHEN clauses collide with no tiebreak written THEN the prohibition beats the mandate; failing that you SHALL take the more reversible course and leave the reasoning visible.
