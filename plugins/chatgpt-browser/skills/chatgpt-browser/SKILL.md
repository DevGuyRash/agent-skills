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

Use ChatGPT through the user's authorized interactive browser while preserving
conversation placement, context integrity, and external-effect boundaries.

## Respect ownership and authority

- Use the host's authorized interactive-browser control capability for browser selection,
  navigation, inspection, clicks, typing, screenshots, and recovery mechanics. If no such
  capability is available, report that limitation; do not install or improvise one without
  authority.
- Use this skill only for ChatGPT-specific conversation judgment. Leave generic browser
  work, browser testing, OpenAI API work, and generic second-model review to their owners.
- Reuse the signed-in browser and useful ChatGPT tabs when available.
- If ChatGPT is signed out, ask the user to sign in manually in that browser and continue
  after confirmation.
- Never request, enter, inspect, or extract passwords, cookies, tokens, local storage, or
  browser profiles.
- Inspect the live UI. Do not rely on fixed selectors, labels, model catalogs, upload
  limits, or remembered account capabilities.

Treat effects separately:

- Inspecting account, chat, Project, selection, attachments, and response state is
  read-only.
- Creating a Project or chat, uploading context, and sending a message are persistent
  mutations.
- Connecting or authorizing an app, granting permissions, purchasing, publishing, or
  invoking an outward action requires separate user authority.
- Existing Projects, chats, drafts, files, credentials, grants, and history are protected
  state. Never delete, rename, move, edit, or archive them without explicit authority.
- Before leaving any chat, resolve the loss risk from its unsent draft, pending
  attachments, or active generation. Do not clear or overwrite pre-existing composer
  state to make room for the new task.
- If a current tab contains a draft, pending attachment, or active generation, perform
  fresh work in a different tab object. Verify the tab identities differ before
  navigation, retain the protected tab unchanged, and stop for direction if separation
  cannot be established.

## Orient before acting

- Inspect the signed-in state, current Project and chat, chat durability, selected model
  and reasoning level, selected app or GPT, composer, attachments, and generation state.
- Refresh only when the page is stale or failed. First protect or resolve any unsent
  draft, pending upload, or active generation that a refresh could lose.
- After refresh or navigation recovery, reverify the account, Project and chat, model and
  reasoning level, app or GPT, composer, and attachments.

## Place the conversation

Apply this precedence:

1. Follow the user's explicit choice of existing chat, new chat, Project, ordinary chat,
   or temporary chat.
2. Otherwise, enter a relevant existing Project and create a fresh chat inside it.
3. If no relevant Project exists, ask before creating one.
4. If durable organization is unnecessary or declined, use a temporary chat for
   disposable work, or an ordinary chat when requested.

- Enter a Project before creating its chat, then visibly verify that the new chat belongs
  to that Project before sending substantive context.
- Create a concise task- or domain-oriented Project name only after authorization.
- Prefer multiple focused chats in one Project over one indefinitely growing thread.
- Do not assume another Project chat's discussion or files are active context.
- Prefer a fresh chat to repurposing an existing thread unless the user chose that thread.
- Verify temporary mode before sending. Treat it as disposable and potentially
  unrecoverable; extract the needed result before leaving.
- Do not claim temporary-chat Project inheritance, file persistence, or recoverability
  without current visible evidence.
- Start a fresh chat when the subject changes materially, patch history becomes long,
  files are substantially replaced, stale assumptions repeat, context becomes confused,
  or answer quality declines. Do not impose a universal turn count.

## Select models, apps, and GPTs

- Preserve the current model and reasoning level when the user does not specify them.
- When requested, choose the exact currently available model and reasoning level, then
  verify the visible selection before sending.
- Never silently substitute. If the requested selection is unavailable, report the live
  available state and ask for direction.
- Discover available ChatGPT apps, tools, connectors, and custom GPTs from the live UI.
- Select the exact requested app or GPT and verify its active identity before adding
  context. Report restrictions it imposes on models, tools, or context.
- Never silently replace an unavailable app or GPT.
- Treat installation, connection, third-party sign-in, consent, permission grants,
  purchases, publication, messages, and other outward actions as separate authorization
  boundaries. Ask the user to perform authentication or consent personally.

## Supply reliable context

- Supply every local file or fact on which the answer depends to the current chat. A
  local path alone does not give ChatGPT access.
- Put the task, constraints, and requested output in ordinary composer text. Paste or
  attach the required current context once.
- Before sending, verify filenames, attachment count, previews, and completed uploads;
  remove only duplicate or stale attachments added by the current invocation. Ask before
  changing attachments that were already present.
- Compare the before/after attachment inventory before removing anything; treat an
  attachment with uncertain identity as pre-existing protected state.
- Add filenames plus a revision, digest, inventory, or unique marker when identity
  matters. Ask ChatGPT to confirm that identity before relying on a consequential answer.
- Keep short text inline. Long pasted text may appear as an attachment-like pill, currently
  familiar as `Pasted text`; this still supplies the text, so do not repaste it merely
  because it left the visible composer body.
- Inspect the whole composer and attachment tray; an unchanged editable text body does
  not prove that a paste or attachment failed.
- Expect images and documents to appear as thumbnails, filename pills, or previews. Wait
  for processing to finish before sending.
- If an input limit or unsupported type blocks context, split or bundle it while
  preserving identity and order.
- Start a fresh chat with the complete current baseline needed for the task.
- Send later changes as patches only while that baseline remains reliable. Identify each
  patch's base revision and affected files.
- When the thread grows long, patches accumulate, or ChatGPT loses state, resend the
  current complete files instead of extending the historical patch chain.
- When moving to another chat, resend all relevant current files.
- Exclude credentials, secrets, browser data, generated dependencies, build outputs, and
  irrelevant history.

## Send, wait, and return the result

- Recognize that sending can permanently retain the prompt and attachments.
- Before sending, verify chat durability, Project association, model and reasoning or GPT
  selection, prompt, and attachments.
- Send once. Wait until generation is visibly complete, even when reasoning takes many
  minutes.
- Do not treat partial streaming, a pause, or a browser timeout as a final answer.
- Before retrying a stalled request, establish that the original generation will not
  continue or duplicate.
- Read the complete final response, including relevant collapsed or continued content.
  Waiting without reading is incomplete.
- Return the actual findings to the calling task. Preserve a useful durable chat and
  return its identity or URL when helpful.
- Extract a temporary-chat result before leaving. Avoid abandoned drafts, pending uploads,
  and duplicate attachments.
