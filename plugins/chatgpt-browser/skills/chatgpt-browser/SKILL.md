---
name: chatgpt-browser
description: >-
  Operate ChatGPT in a user-authorized interactive browser across models,
  reasoning levels, Projects, ordinary or temporary chats, attachments and
  pasted context, apps and custom GPTs, response waiting, and thread hygiene.
  Use when an agent is asked to interact with ChatGPT through a browser; do
  not use for OpenAI API calls, ordinary web browsing, non-ChatGPT browser
  tasks, or generic second-model review unless the user specifically requests
  ChatGPT in the browser.
---

# ChatGPT Browser

Use ChatGPT through the user's authorized interactive browser while preserving conversation placement, context integrity, and external-effect boundaries.

## Respect ownership and authority

- Use the host's authorized interactive-browser control capability for browser selection, navigation, inspection, clicks, typing, screenshots, and recovery mechanics. If no such capability is available, report that limitation; do not install or improvise one without authority.
- Use this skill only for ChatGPT-specific conversation judgment. Leave generic browser work, browser testing, OpenAI API work, and generic second-model review to their owners.
- Reuse the signed-in browser and useful ChatGPT tabs when available.
- If ChatGPT is signed out, ask the user to sign in manually in that browser and continue after confirmation.
- Never request, enter, inspect, or extract passwords, cookies, tokens, local storage, or browser profiles.
- Inspect the live UI. Do not rely on fixed selectors, labels, model catalogs, upload limits, or remembered account capabilities.

Treat effects separately:

- Inspecting account, chat, Project, selection, attachments, and response state is read-only.
- Creating a Project or chat, uploading context, and sending a message are persistent mutations.
- Connecting or authorizing an app, granting permissions, purchasing, publishing, or invoking an outward action requires separate user authority.
- Existing Projects, chats, drafts, files, credentials, grants, and history are protected state. Never delete, rename, move, edit, or archive them without explicit authority.
- Before leaving any chat, resolve the loss risk from its unsent draft, pending attachments, or active generation. Do not clear or overwrite pre-existing composer state to make room for the new task.
- If a current tab contains a draft, pending attachment, or active generation, perform fresh work in a different tab object. Verify the tab identities differ before navigation, retain the protected tab unchanged, and stop for direction if separation cannot be established.

## Orient before acting

- Inspect the signed-in state, current Project and chat, chat durability, selected model and reasoning level, selected app or GPT, composer, attachments, and generation state.
- Refresh only when the page is stale or failed. First protect or resolve any unsent draft, pending upload, or active generation that a refresh could lose.
- After refresh or navigation recovery, reverify the account, Project and chat, model and reasoning level, app or GPT, composer, and attachments.

## Place the conversation

Apply this precedence:

1. Follow the user's explicit choice of existing chat, new chat, Project, ordinary chat, or temporary chat.
2. Otherwise, enter a relevant existing Project and create a fresh chat inside it.
3. If no relevant Project exists, ask before creating one.
4. If durable organization is unnecessary or declined, use a temporary chat for disposable work, or an ordinary chat when requested.

- Enter a Project before creating its chat, then visibly verify that the new chat belongs to that Project before sending substantive context.
- Create a concise task- or domain-oriented Project name only after authorization.
- Prefer multiple focused chats in one Project over one indefinitely growing thread.
- Do not assume another Project chat's discussion or files are active context.
- Prefer a fresh chat to repurposing an existing thread unless the user chose that thread.
- Verify temporary mode before sending. Treat it as disposable and potentially unrecoverable; extract the needed result before leaving.
- Do not claim temporary-chat Project inheritance, file persistence, or recoverability without current visible evidence.
- Start a fresh chat when the subject changes materially, patch history becomes long, files are substantially replaced, stale assumptions repeat, context becomes confused, or answer quality declines. Do not impose a universal turn count.

## Select models, apps, and GPTs

- Unless the user explicitly requests a different selection or asks not to maximize capability, choose the live UI's most capable model and highest reasoning effort compatible with the requested app, GPT, tools, and context. Report any compatibility constraint that prevents this default.
- Interpret a user-supplied label that matches any live model, compact preset, or reasoning-effort option as a request for that selection, even when the same word also appears in account-plan UI. A bare label such as `Pro` means the matching selection, not account status, unless the user explicitly refers to an account, plan, or subscription.
- Treat model selection as one composed state that may appear as a compact Power preset or as separate advanced Model and Effort controls. An explicitly named dimension wins; otherwise match the requested label against the compact preset and every advanced dimension while preserving unrelated selections.
- Scope matching and verification to the active selector or composer control; account-plan badges and unrelated page text are not selection evidence.
- Never silently substitute or declare a requested selection unavailable until every live selection dimension has been inspected.
- Before sending, require positive visible evidence of the intended selection. If verification is absent or inconclusive, do not send.
- Discover available ChatGPT apps, tools, connectors, and custom GPTs from the live UI.
- Select the exact requested app or GPT and verify its active identity before adding context. Report restrictions it imposes on models, tools, or context.
- Never silently replace an unavailable app or GPT.
- Treat installation, connection, third-party sign-in, consent, permission grants, purchases, publication, messages, and other outward actions as separate authorization boundaries. Ask the user to perform authentication or consent personally.

## Supply reliable context

- Supply every local file or fact on which the answer depends to the current chat. A local path alone does not give ChatGPT access.
- Put the task, constraints, and requested output in ordinary composer text. Paste or attach the required current context once.
- If the selected model or reasoning effort is more capable than the calling agent, treat the ChatGPT target as the task's orchestrating reasoner and the caller as its context supplier; use the same posture whenever the user chose it to obtain stronger reasoning.
- Give that target a concise task summary, desired outcome, relevant context, settled decisions, invariants and authority boundaries, required deliverables, and observable proof of completion; present consequential unknowns as questions for it to resolve. Leave decomposition, scaffolding, procedures, named reasoning methods, and implementation choices to it unless the user fixed them or a named constraint or hazard makes them necessary.
- Before sending, verify filenames, attachment count, previews, and completed uploads; remove only duplicate or stale attachments added by the current invocation. Ask before changing attachments that were already present.
- Compare the before/after attachment inventory before removing anything; treat an attachment with uncertain identity as pre-existing protected state.
- Add filenames plus a revision, digest, inventory, or unique marker when identity matters. Ask ChatGPT to confirm that identity before relying on a consequential answer.
- Keep short text inline. Long pasted text may appear as an attachment-like pill, currently familiar as `Pasted text`; this still supplies the text, so do not repaste it merely because it left the visible composer body.
- Inspect the whole composer and attachment tray; an unchanged editable text body does not prove that a paste or attachment failed.
- Expect images and documents to appear as thumbnails, filename pills, or previews. Wait for processing to finish before sending.
- If an input limit or unsupported type blocks context, split or bundle it while preserving identity and order.
- Start a fresh chat with the complete current baseline needed for the task.
- Send later changes as patches only while that baseline remains reliable. Identify each patch's base revision and affected files.
- When the thread grows long, patches accumulate, or ChatGPT loses state, resend the current complete files instead of extending the historical patch chain.
- When moving to another chat, resend all relevant current files.
- Exclude credentials, secrets, browser data, generated dependencies, build outputs, and irrelevant history.

## Send, wait, and return the result

- Recognize that sending can permanently retain the prompt and attachments.
- Before sending, verify chat durability, Project association, model and reasoning or GPT selection, prompt, and attachments.
- Send once, then confirm one live-derived signal that this generation is active in the same tab, chat, and turn. Do not resend merely because a wait ends.
- Never activate a control that offers to answer sooner while a reasoning run is active, currently familiar as `Answer now` or any equivalent. Preserve the selected model and effort through normal completion; the control's presence is evidence of activity, not completion.
- Give the complete send/wait/read cycle exclusive use of its tab. Concurrent agents use separate tabs and preferably separate chats, or serialize the cycle. A shared worktree does not establish browser ownership; never coordinate browser use through repository files, temporary files, page globals, or shared locks.
- Treat partial streaming and pauses as active work while the confirmed signal remains. Treat failed or timed-out browser operations, ambiguous predicates, navigation, tab closure, and execution-context loss as inconclusive rather than complete.

### Choose a waiting path

Prefer a native semantic conditional wait only when the current host and version have demonstrated that it honors the required condition and duration. Its completion signal must belong to the same tab, chat, turn, and generation; it must be impossible to satisfy while generation remains active; and it must mean settled completion. A documented timeout parameter or an active control becoming hidden does not prove those properties.

The following is host-side JavaScript shape, not code for execution inside the page. Derive every locator and state from the current semantic or accessibility UI.

```js
async function waitWithVerifiedNativeLocator({
  active,
  activeState,
  settledCompletion,
  completionState,
  readActive,
  activeTimeoutMs,
  completionTimeoutMs,
}) {
  try {
    await active.waitFor({
      state: activeState,
      timeoutMs: activeTimeoutMs,
    });

    await settledCompletion.waitFor({
      state: completionState,
      timeoutMs: completionTimeoutMs,
    });

    const activeNow = await readActive();

    return activeNow === false
      ? { status: "complete" }
      : { status: "inconclusive", reason: "postcondition_failed" };
  } catch {
    return { status: "inconclusive", reason: "native_wait_failed" };
  }
}
```

If native waiting is unavailable or ends prematurely, use the longest external host wait demonstrated to be reliable, then resume and perform exactly one immediate active-state check. Keep only `{ seenActive, settling }` in current task context. If the host supplies a continuation or wait handle, continue that handle instead of re-entering the model. Without one, sparse resumptions cannot be eliminated; keep them silent and minimal.

The following is also host-side JavaScript shape, never page-executed code:

```js
const initialWaitState = Object.freeze({
  seenActive: true,
  settling: false,
});

async function nextSparseWaitStep(
  state,
  readActive,
  { sparseSleepMs, settleSleepMs },
) {
  if (
    !Number.isFinite(sparseSleepMs) ||
    !Number.isFinite(settleSleepMs) ||
    sparseSleepMs <= 0 ||
    settleSleepMs <= 0
  ) {
    return {
      status: "inconclusive",
      reason: "invalid_wait_duration",
      state,
    };
  }

  let active;

  try {
    active = await readActive();
  } catch {
    return {
      status: "inconclusive",
      reason: "state_check_failed",
      state,
    };
  }

  if (active !== true && active !== false) {
    return {
      status: "inconclusive",
      reason: "state_check_inconclusive",
      state,
    };
  }

  if (active) {
    return {
      status: "waiting",
      state: { seenActive: true, settling: false },
      sleepMs: sparseSleepMs,
    };
  }

  if (!state.seenActive) {
    return {
      status: "inconclusive",
      reason: "active_not_confirmed",
      state,
    };
  }

  if (!state.settling) {
    return {
      status: "waiting",
      state: { seenActive: true, settling: true },
      sleepMs: settleSleepMs,
    };
  }

  return {
    status: "complete",
    state: { seenActive: true, settling: true },
  };
}
```

- Initialize `initialWaitState` only after positively confirming active generation.
- Make `readActive()` return `true` or `false` only for an unambiguous inspection of the same live signal in the same tab and chat; make ambiguity return another value or throw.
- When a step returns `waiting`, invoke the external host wait for `sleepMs`. On resumption, do not inspect or explain anything else; run the next step with the returned state.
- Reset settling when activity reappears. Two absent endpoint samples separated by the settle wait are the strongest fallback available from sparse sampling. If literal continuous-absence proof is required, return inconclusive instead of claiming completion.
- Do not impose a short overall deadline. Generations lasting 23 minutes or longer can be ordinary active work. Continue bounded waits without narrating unchanged state.
- The sparse host-side loop above is the only polling pattern permitted here. Never build the wait inside page execution or replace that loop with in-page observers, timer promises, polling, network requests, DOM mutation, clicks, event dispatch, or persisted scripts.

### Read the complete response

- After settled completion, read the complete final response, including relevant collapsed or continued content. Waiting without reading is incomplete.
- Do not call a response or code block truncated merely because extracted DOM text ends abruptly. If syntax ends mid-expression, rendered height conflicts with extracted text, or a long region contains lazy or virtualized space, scroll through that region to materialize it and reread overlapping chunks.
- Continue until the relevant region has no unmaterialized content and no continuation control remains. Deduplicate overlaps and verify expected beginnings and endings or syntax before relying on consequential code.
- Prefer scrolling and materialization over a copy control that could overwrite protected clipboard state. Request continuation only after proving the content is genuinely absent.
- Verify each requested artifact in the surface that carries its payload. A completed response shell, label, control, or extracted text does not establish that a file, image, diagram, citation, or app result is usable; if applicable processing or materialization still leaves it unavailable, report inconclusive without assigning a cause.
- Return the actual findings to the calling task. Preserve a useful durable chat and return its identity or URL when helpful.
- Extract a temporary-chat result before leaving. Avoid abandoned drafts, pending uploads, and duplicate attachments.
- Before creating a tab, inventory the host-owned identities of existing tabs. Track the host-owned identity returned for each tab the invocation creates; active-tab position, variable names, worktree identity, URLs, and page labels do not establish ownership.
- After extracting a result and resolving its draft, uploads, attachments, dialogs, and generation state, close only a tab whose tracked created identity still resolves unambiguously. Closing it does not delete a durable chat; return the chat identity or URL when that is the retained artifact.
- Treat uncertain or rebound tab identity as pre-existing protected state and do not close it. Keep a verified created tab open only when the user asked for the live page or unresolved state requires a handoff, and make that disposition explicit.
