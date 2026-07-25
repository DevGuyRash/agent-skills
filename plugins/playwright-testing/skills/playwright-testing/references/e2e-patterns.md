# Playwright E2E Patterns

Use these examples as adaptable patterns, not as copy-paste contracts. Preserve the outcome, selector-ownership, deterministic setup, and artifact ideas while changing domain details to match the app under test.

## Outcome Journey Template

Use this for app-owned journeys such as checkout, record creation, dashboard filtering, or settings updates.

```js
test("user completes checkout and sees the order in history", async ({ page, request }) => {
  await test.step("arrange account and cart through API", async () => {
    // Seed deterministic state via the app's API, e.g.:
    // await request.post("/test/seed", { data: { cart: "..." } });
  });

  await test.step("submit order through the UI", async () => {
    await page.goto("/checkout");
    await expect(page.getByRole("heading", { name: "Checkout" })).toBeVisible();
    await page.getByRole("button", { name: "Place order" }).click();
    await expect(page.getByRole("status")).toContainText("Order confirmed");
  });

  await test.step("re-observe the durable order in history", async () => {
    const orderId = (await page.getByLabel("Order number").textContent())?.trim();
    expect(orderId).toBeTruthy();

    await page.goto("/orders");
    await expect(page.getByRole("link", { name: orderId })).toBeVisible();
  });
});
```

The confirmation status is useful intermediate evidence. WHEN durability is part of the contract THEN re-observe the committed state through an independent surface such as a reload, fresh navigation, or read API; do not stop at the acknowledgement.

## Selector Canary Template

Use this for uncontrolled, generated, third-party, frequently changing, or business-critical selectors. `findSemanticTarget` below is an illustrative helper, not a Playwright API; provide your own that tries each candidate locator and records which one matched.

```js
test("checkout submit selector still resolves", async ({ page }, testInfo) => {
  await page.goto("/checkout");

  const result = await findSemanticTarget(page, "submitOrder", [
    () => page.getByRole("button", { name: "Place order" }),
    () => page.getByTestId("submit-order"),
  ]);

  await testInfo.attach("selector-submitOrder.json", {
    body: JSON.stringify(result.report, null, 2),
    contentType: "application/json",
  });

  expect(result.matched, result.failureMessage).toBeTruthy();
  await expect(result.locator).toBeEnabled();
});
```

## State Classifier Template

For unstable surfaces, return structured state instead of booleans, and poll until a terminal state so a slow load is not misread as `unknown`.

```js
const TERMINAL = new Set(["ready", "login_required", "error", "blocked", "not_found"]);

// Poll until the page reaches a terminal state; a transient `loading` keeps polling.
async function waitForKnownState(page, { timeout = 10_000 } = {}) {
  const history = [];
  let state = { kind: "unknown" };

  try {
    await expect
      .poll(async () => {
        state = await observeState(page);
        history.push(state.kind);
        return TERMINAL.has(state.kind);
      }, { timeout })
      .toBe(true);
  } catch {
    state = {
      kind: "unknown",
      notes: [`No terminal state within ${timeout}ms; observed ${history.join(" -> ") || "nothing"}.`],
    };
  }

  return { ...state, url: page.url(), title: await page.title(), history };
}

// One observation. Check the strongest ready signal first, and treat duplicate
// controls as a page-understanding failure instead of catching the error away.
async function observeState(page) {
  const dashboard = page.getByRole("heading", { name: "Dashboard" });
  if ((await dashboard.count()) === 1 && (await dashboard.isVisible())) {
    return { kind: "ready", matchedSelectors: ["role=heading[name='Dashboard']"] };
  }

  const signIn = page.getByRole("button", { name: "Sign in" });
  const signInCount = await signIn.count();
  if (signInCount > 1) {
    return { kind: "error", notes: [`Ambiguous: ${signInCount} 'Sign in' controls; page not understood.`] };
  }
  if (signInCount === 1 && (await signIn.isVisible())) {
    return { kind: "login_required", matchedSelectors: ["role=button[name='Sign in']"] };
  }

  return { kind: "loading" }; // transient; caller keeps polling
}
```

This bounded settle fixes the classic single-shot pitfalls: a slow load resolves to `ready` instead of `unknown`, the stronger ready signal is checked before the weaker sign-in signal, ambiguity surfaces as `error` rather than being swallowed by a blanket `.catch()`, and the returned notes describe only checks the code actually performed.

## Third-Party Or Provider Surfaces

For third-party or frequently changing UIs, use domain-specific semantic names inside that helper layer. Examples may include chat-provider names such as `composer`, `sendButton`, or `assistantMessage`, but those should not be canonical generic examples for app-owned tests.

## Good And Bad Examples

Bad:

```js
await page.locator(".card > div:nth-child(3) button").click();
```

Good for app-owned UI:

```js
await page.getByRole("button", { name: "Place order" }).click();
```

Good for third-party UI:

```js
await selectors.find("submitOrder").click();
```

Bad:

```js
await page.waitForTimeout(5000);
```

Good:

```js
await expect(page.getByRole("status")).toContainText("Saved");
```

Bad: asserting a marketing tagline, third-party incidental text, generated class, or visual layout detail that is not the product contract.

Good: asserting an app-owned confirmation, status, total, ID, or durable semantic state.

## Review Checklist

- Does the test prove a user/product outcome?
- Is e2e the right tier?
- Are app-owned selectors role-based or stable?
- Are third-party selectors centralized?
- Are selector canaries separated from journeys?
- Does every wait have a named outcome?
- Are auth and data setup deterministic?
- Are page states classified where needed?
- Do failure artifacts identify the broken outcome or semantic selector?
