---
name: Playwright Testing
description: >-
  Design durable, outcome-oriented Playwright and browser e2e tests that prove product behavior instead of recording today's DOM. Use when the task involves: (1) Creating, reviewing, or refactoring Playwright tests, (2) Designing selector strategies, page objects, fixtures, e2e assertions, or trace/artifact capture, (3) Reducing brittle selectors, fixed waits, layout assertions, or flaky authenticated flows, (4) Testing third-party, authenticated, frequently changing, or browser-extension UIs, or (5) Any task involving Playwright e2e test design or brittle-test cleanup.
---

# Playwright Testing

Playwright/e2e tests are valuable when they prove product behavior that only a real browser can expose. This skill keeps those tests outcome-oriented, deterministic, and debuggable instead of tied to today's DOM shape.

This skill owns Playwright test design and review. Use existing Playwright or browser-control skills for mechanics such as launching browsers, clicking through pages, collecting screenshots, or debugging live automation.

## Start Here

Read the relevant test files, helper files, fixtures, and Playwright config before proposing new e2e coverage.

Decide which question is primary:

- test-tier fit
- system-boundary realism
- selector durability
- journey/canary split
- deterministic setup
- failure artifact quality

Gather only the smallest evidence set needed. WHEN a lower test tier can prove the behavior with less brittleness THEN you SHALL recommend that tier instead of adding e2e.

When concrete templates or review examples are useful, read `<skills-file-root>/references/e2e-patterns.md`.

## Choose The Test Tier First

WHEN pure logic or deterministic UI state can prove the behavior THEN you SHALL use unit or component tests.

WHEN the behavior is an app-owned contract such as API responses, stores, bridge messages, adapters, or state reducers THEN you SHALL use integration tests.

WHEN the behavior requires a real browser, real rendering, navigation, auth/session behavior, browser extension behavior, or cross-system workflow THEN you SHALL use Playwright/e2e.

IF a lower test tier can prove the outcome with less brittleness THEN you SHALL NOT add an e2e test.

## Calibrate Claims To Traversed Boundaries

A browser test can render real UI while substituting the worker, bridge, backend, provider, payment, or persistence layer behind it. Such a test is valuable, but it proves only the seams it actually traverses. A real browser is not a real system path.

WHEN you name, review, or report an e2e test THEN you SHALL identify the critical seams in the claimed journey and mark each as real or substituted.

You SHALL NOT claim behavior beyond the last real boundary the test independently observed.

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

For app-owned UI, prefer `getByRole` and `getByLabel`. Use `getByPlaceholder` only as a fallback, since placeholder text is a weak accessibility signal, and `getByTestId` only for intentionally stable hooks.

Keep app-owned locators inline when they are readable and semantic.

For third-party or unstable UI, centralize selectors behind semantic helper APIs.

Use generic semantic target names such as `loginButton`, `submitOrder`, `searchInput`, `rowByName`, `toastError`, `statusMessage`, and `primaryAction`.

Use domain-specific semantic names only inside that domain's helper layer, such as provider-chat targets in a third-party chat helper.

You SHALL avoid undocumented `nth()`, long CSS chains, generated class names, exact third-party text, layout-dependent selectors, and raw third-party selectors scattered across specs.

## Wait For Outcomes

Prefer Playwright web-first auto-retrying assertions.

You SHALL NOT use `waitForTimeout(ms)` or arbitrary sleeps.

You SHOULD name the outcome of every nontrivial wait, and use `test.step()` for meaningful journey phases.

You SHOULD include the last observed state in timeout errors.

## Arrange Deterministically

Prefer arrange-via-API, assert-via-UI.

Prefer `storageState` for ordinary web authentication when cookies and local storage fully represent the session and the login flow is not itself under test. WHEN authentication depends on session storage, IndexedDB, a passkey, a client certificate, extension storage, a persistent profile, or an attached external browser THEN you SHALL use an explicit reproducible fixture for that boundary and document what remains shared. You SHALL treat saved auth state as secret material and keep it out of source control and unsafe artifacts.

Generate unique run tokens for created data. Default Playwright Test fixtures isolate each test in a fresh browser context, but custom persistent, attached, worker-scoped, or reused contexts do not inherit that guarantee. You SHALL isolate or serialize every shared browser, profile, backend, and external-system boundary that can affect the outcome, not only shared backend state.

Pin timezone and locale when relevant. Freeze time with Playwright clock controls when the test depends on time.

Disable animations when they add nondeterminism.

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

WHEN a page classifies as `unknown` THEN you SHALL treat it as a selector/page-understanding failure, because the test does not understand the page.

WHEN the test does not explicitly require a ready authenticated state THEN you MAY treat a known blocked state as a valid outcome.

A known blocked state MAY prove that classification and diagnostics work, but you SHALL NOT count it as proof that a required-ready product journey succeeded.

You SHALL NOT treat every non-ready state as a selector failure.

## Capture Useful Failure Artifacts

On meaningful e2e failure, capture screenshot, Playwright trace when practical, URL/title, classified page state, semantic selector target, selectors tried, matched selector if any, relevant DOM or accessible snapshot when safe, and last observed state for timed waits.

An important journey MAY treat unexpected product-owned console errors, uncaught page errors, and failed product requests as part of its passing contract, with narrow test-owned allowances for expected failures. Visible assertions passing does not prove the product logged no error.

"Safe" means no raw tokens, cookies, auth/storage state, signed URLs, secret headers, or unrelated private DOM. You SHALL prefer synthetic accounts and inputs, scope evidence to the contract under test, and sanitize before attaching.

## Verify Before Claiming Pass

WHEN you create or change a test AND execution is available THEN you SHALL run the smallest relevant test, inspect failure artifacts, correct the leading cause, and rerun before reporting it as passing; then run the owning suite in proportion to risk.

You SHALL NOT report a test as passing when it was only authored or listed.

WHEN execution is unavailable THEN you SHALL report the test as `not_verified` with the blocker rather than as passing.

## Review Tests As Product Contracts

Review Playwright tests by asking:

- What user/product outcome does this prove?
- Could a unit or integration test prove it better?
- Which seams are real and which are substituted?
- Does the final oracle independently prove the outcome the test name claims?
- Are selectors stable and ownership-aware?
- Would a selector failure name the semantic target that broke?
- Are waits web-first, named, and bounded?
- Is auth/data setup deterministic?
- Was the changed test actually executed, and what ran?
- Are artifacts enough to debug without immediately rerunning, and free of credentials or unrelated private data?
