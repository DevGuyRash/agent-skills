# Blind Execution and Custody

Use this reference when prompt composition, isolation, launch parity, host choice, or evidence custody
remains unresolved.

## Executor-visible material

Give each execution unit only the real work outcome, inputs, facts, authority, constraints, and
requested artifact. Do not disclose the experiment, condition identity, development history,
expected winner, suspected defect, review criteria, sibling runs, or evaluator theory unless one is
part of the real deployed task. Do not prescribe a workflow or reasoning method unless the maker's
interface or a named hazard requires it.

Presentation metadata is input. Filenames, headings, task labels, directory names, or fixture
descriptions can reveal evaluator intent even when prompt prose is neutral. Preserve names from the
real interface; use opaque or task-natural identifiers for controller-only meaning.

Reconstruct the final deployed payload after condition insertion and launcher composition. A policy,
system instruction, skill, or other governing layer flattened into an ordinary user message is a
different condition. Validate the role, precedence, timing, tools, and ambient instructions the
subject actually receives. Every behavior-guiding common layer needs a condition-independent source;
the evaluator's desired behavior does not become common input merely because it is accurate.

## Freshness, parity, and collection

Give every independent execution a fresh context and condition-neutral workspace. Keep common inputs
immutable and mutable state local to the unit. Isolation covers caches, temporary names, services,
credentials, queues, rate limits, and any other resolvable namespace—not only the visible directory.
If state crosses units, invalidate or qualify every affected observation rather than calling the
shared access parity.

Match model version, reasoning effort, tools, permissions, budget, retry policy, starting state,
launcher, and output contract unless the design varies one. Preserve every attempt and its status.
A parent rescue, asymmetric status message, selective rerun, or best-looking regeneration changes
the condition.

Resolve the actual working root and artifact-collection boundary before launch. A prompt cannot make
a read-only destination writable or override a host-owned project root. If output lands outside the
declared boundary, do not copy it back and count the run retroactively; correct the harness and obtain
a fresh result or keep the limitation visible.

Match concurrency to demonstrated runtime and custody capacity rather than nominal agent slots.
Storage, authentication, service saturation, file descriptors, or another shared resource can
correlate failures. Preserve those attempts as harness evidence and replace only runs invalidated by
a predeclared symmetric rule.

Treat orchestration traffic as input. Sibling names, broad agent listings, status messages, outputs,
or controller notes contaminate freshness when visible. Even a non-substantive message sent to only
one matched run is an asymmetric exposure.

Record the exact prompt, resolved condition and environment, model/host/version/effort, output,
artifacts, relevant trace, tool authority, token or cost evidence, timing, exit, activation where
applicable, and unexpected intervention. An output can be correct while its trajectory proves that
the tested system failed and an orchestrator repaired it.

## Optional structural helper

The workspace helper requires Python 3.9 or later and a POSIX filesystem for its lock and permission
boundary. Use it only when opaque workspaces, N-way review views, integrity checks, and reveal gating
reduce material risk. Read [the helper contract](helper-contract.md) only when operating that helper.
Its implementation and tests are inactive package code; do not inspect them during an ordinary
comparison. If the documented interface is insufficient, use another valid custody system rather
than paying an implementation-reading detour.

## Stable host examples

The installed host's current `--help` is the executable authority. These examples use core long-form
flags and placeholders rather than model names. They establish fresh non-resumed sessions and
explicit settings; they do not confine filesystem reads by themselves.

Codex:

```sh
codex exec --ephemeral --model "$MODEL" \
  --config "model_reasoning_effort=\"$EFFORT\"" \
  --cd "$WORKSPACE" --json - <"$PROMPT_FILE" >"$TRACE_FILE"
```

Claude:

```sh
(cd "$WORKSPACE" && claude --print --no-session-persistence \
  --model "$MODEL" --effort "$EFFORT" \
  --output-format stream-json <"$PROMPT_FILE") >"$TRACE_FILE"
```

Confirm that each requested model and effort actually resolved, and record fallback rather than
assuming it. Use permissions, containers, isolated users, or another observable boundary when
read isolation matters. Do not apply a host's bare or safe mode to only one condition unless that
mode is the condition.
