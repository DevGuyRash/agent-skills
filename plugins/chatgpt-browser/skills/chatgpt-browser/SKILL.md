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

- The user's explicit browser choice SHALL win. Otherwise you SHALL use the host's `Browser` capability when available, then another suitable host-provided interactive browser that can reuse the user's authorized session. You SHALL NOT select standalone or external Playwright while a suitable built-in browser capability exists. Standalone automation MAY be used when no suitable built-in capability exists. You SHALL follow the selected capability's own mechanics and SHALL NOT install or improvise browser control without authority. Playwright-compatible methods exposed inside the selected built-in browser surface are part of that surface, not standalone or external Playwright.
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
- Before creating a tab, inventory the host-owned identities of existing tabs. Track the host-owned identity returned for every tab created by this invocation; active-tab position, variable names, worktree identity, URLs, and page labels do not establish ownership.

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
- When a user says to use a label that corresponds to a model, compact preset, or reasoning-effort option, interpret it as that selection. This meaning takes precedence over the same label in account-plan UI; bare `Pro` means the Pro selection unless the user explicitly refers to an account, plan, or subscription.
- Treat model selection as one composed state that may appear as a compact Power preset or as separate advanced Model and Effort controls. An explicitly named dimension wins; otherwise match the requested label against the compact preset and every advanced dimension while preserving unrelated selections.
- Scope matching and verification to the active selector or composer control; account-plan badges and unrelated page text are not selection evidence.
- Never silently substitute or declare a requested selection unavailable until every live selection dimension has been inspected.
- Before sending, require positive visible evidence of the intended selection. If verification is absent or inconclusive, do not send.
- Discover available ChatGPT apps, tools, connectors, and custom GPTs from the live UI.
- Select the exact requested app or GPT and verify its active identity before adding context. Report restrictions it imposes on models, tools, or context.
- Never silently replace an unavailable app or GPT.
- Treat installation, connection, third-party sign-in, consent, permission grants, purchases, publication, messages, and other outward actions as separate authorization boundaries. Ask the user to perform authentication or consent personally.

## Maintain a reasoning conversation

- These invariants govern every message you send to ChatGPT, including the opening, questions, corrections, disagreements, and follow-ups. The conversation SHALL remain a continuation of the user's task; it SHALL NOT become a sequence of tasks authored by you.
- Speak with ChatGPT conversationally as a reasoning collaborator with independent judgment. Use the conversation for genuine inquiry, brainstorming, feedback, disagreement, and exploration. You SHALL NOT address ChatGPT as an executor receiving a work order or turn your message into an instruction brief or specification unless that form is itself required by the user or a real consumer interface.
- Carry forward the user's desired result, authorized decision-relevant reality, genuine fixed requirements, and needed inputs. You MAY state what you observe, think, doubt, or disagree with and ask genuine questions that arise from the work. Those contributions SHALL retain their actual authority: your perspective is not a user requirement, settled decision, or task boundary.
- A question, proposed direction, downstream need, or anticipated next step that originates with you SHALL remain evidence about the state of the work. You SHALL NOT convert it into ChatGPT's assignment, required deliverable, scope, agenda, decomposition, completion standard, answer form, or presumed direction.
- You SHALL own context integrity, browser custody, authority preservation, observable verification, and truthful representation of your perspective. When judgment is delegated to higher-reasoning ChatGPT, ChatGPT SHALL own every task judgment left open by the user and any real consumer interface, including whether your framing is sound, which open issues matter, and what response best advances the user's outcome. You SHALL NOT prescribe or constrain how it derives or expresses that response beyond requirements actually set by the user or a real consumer interface.

## Supply reliable context

- Supply or attach every authorized, decision-relevant local input that ChatGPT cannot inspect; a local path alone does not grant access. Avoid duplicate copies of the same current context in one turn.
- When a plan or artifact is under review, you SHALL supply the complete current artifact. You SHALL NOT replace the reviewed object with a summary, selected questions, or a template for ChatGPT's response.
- Before sending, verify filenames, attachment count, previews, and completed uploads; remove only duplicate or stale attachments added by the current invocation. Ask before changing attachments that were already present.
- Compare the before/after attachment inventory before removing anything; treat an attachment with uncertain identity as pre-existing protected state.
- When identity matters, add a filename plus revision, digest, inventory, or unique marker and verify it from the attachment surface.
- Keep short text inline. Long pasted text may appear as an attachment-like pill, currently familiar as `Pasted text`; this still supplies the text, so do not repaste it merely because it left the visible composer body.
- Inspect the whole composer and attachment tray; an unchanged editable text body does not prove that a paste or attachment failed.
- Expect images and documents to appear as thumbnails, filename pills, or previews. Wait for processing to finish before sending.
- If an input limit or unsupported type blocks context, split or bundle it while preserving identity and order.
- When starting or moving to a fresh chat, supply the complete current baseline. Use patches only while that baseline remains reliable, identifying each patch's base revision and affected files. When patches accumulate, files are substantially replaced, or state is lost, resend the complete current baseline rather than extend the patch history.
- Exclude credentials, secrets, browser data, generated dependencies, build outputs, and irrelevant history.

## Send, wait, and return the result

- Recognize that sending can permanently retain the prompt and attachments.
- Before sending, verify chat durability, Project association, model and reasoning or GPT selection, prompt, and attachments.
- Send once, identify the resulting user turn, and bind every later wait and read check to the same tab, chat, turn, and generation. Confirm either unambiguous live activity or a newly completed response surface belonging to that turn. Do not resend merely because a host wait or browser operation ends.
- Treat an enabled same-turn stop, cancel, or interrupt action—and any live thinking, searching, tool use, streaming, or continuation status—as activity. Identify controls from their current semantic role and state, not a fixed label, icon, class, or coordinate. Never activate an answer-sooner control or send a follow-up, `continue`, correction, or steering prompt while activity remains unless the user has explicitly supplied you with mid-turn instructions.
- After a response, you SHALL NOT request a rewrite, refinement, expansion, reduction, or reorganization merely to make the answer fit your preferred next step. You MAY continue with new or corrected decision-relevant reality, an observably unmet user-set or external interface, or a genuine material question, disagreement, or uncertainty that could change the user's outcome or the correctness of work serving it. Preserve its actual authority and leave the response judgment to ChatGPT.
- Do not infer a stall or completion from elapsed time, unchanged response text or DOM length, repeated activity wording, an operation timeout, a substantial-looking response, or completed-looking controls.
- Prefer a native semantic wait only when the current host has demonstrated that it tracks the same turn and cannot report completion while activity persists. Otherwise use bounded external host waits; after each resumption, inspect only the same activity signal. Continue a host-provided wait or continuation handle when available.
- Claim natural completion only when the new same-turn response surface is present, no live activity or continuation status remains, and the activity signal is unambiguously absent on two checks separated by a settle wait. If activity reappears, restart settling. If activity was never observed, require independent positive identification of the new same-turn response; absence alone is not completion evidence.
- An explicit stopped or interrupted state is not natural completion. Any ambiguous check, failed operation, navigation, tab closure, execution-context loss, or inability to associate state with the same turn is inconclusive. Two endpoint samples do not prove literal continuous absence; when such proof is required, report inconclusive.
- Keep waiting in the host. Do not implement waiting through page-executed observers, timers, polling, network requests, persisted scripts, DOM mutation, clicks, or event dispatch, because those create uncontrolled page state and can outlive browser custody. Do not impose a short overall deadline; continue bounded waits without narrating unchanged state.
- Give the complete send/wait/read cycle exclusive use of its tab. Concurrent agents use separate tabs and preferably separate chats, or serialize the cycle. Never coordinate browser ownership through repository files, temporary files, page globals, or shared locks.

### Read the complete response

- After settled completion, read the complete final response, including relevant collapsed or continued content. Waiting without reading is incomplete.
- Do not call a response or code block truncated merely because extracted DOM text ends abruptly. If syntax ends mid-expression, rendered height conflicts with extracted text, or a long region contains lazy or virtualized space, scroll through that region to materialize it and reread overlapping chunks.
- Continue until the relevant region has no unmaterialized content and no continuation control remains. Deduplicate overlaps and verify expected beginnings and endings or syntax before relying on consequential code.
- Prefer scrolling and materialization over a copy control that could overwrite protected clipboard state. Request continuation only after proving the content is genuinely absent.
- Verify each requested artifact in the surface that carries its payload. A completed response shell, label, control, or extracted text does not establish that a file, image, diagram, citation, or app result is usable; if applicable processing or materialization still leaves it unavailable, report inconclusive without assigning a cause.
- Return the actual findings to the calling task. Preserve a useful durable chat and return its identity or URL when helpful.
- Extract a temporary-chat result before leaving. Avoid abandoned drafts, pending uploads, and duplicate attachments.
- After extracting a result and resolving its draft, uploads, attachments, dialogs, and generation state, close only a tab whose tracked created identity still resolves unambiguously. Closing it does not delete a durable chat; return the chat identity or URL when that is the retained artifact.
- Treat uncertain or rebound tab identity as pre-existing protected state and do not close it. Keep a verified created tab open only when the user asked for the live page or unresolved state requires a handoff, and make that disposition explicit.
