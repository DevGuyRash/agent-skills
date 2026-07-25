# Open Standard

Portable checks. These hold for any skill on any host and are stated in full here, because this
reference travels to machines that have no repository conventions to consult.

House conventions layer on top of these and live in the repository overlay.

## Identify what you are auditing first

The same product philosophy applies across hosts; the details do not. Applying a host's conventions
to a target that never adopted them manufactures defects.

| Profile | Cues | What changes |
| --- | --- | --- |
| `open-standard` | Relative paths, one-hop references, portable frontmatter | These checks alone |
| `claude-skill` | Claude-specific packaging or invocation guidance | Expect Claude host assumptions |
| `codex-skill` | `.agents/skills`, `$skill-name`, `agents/openai.yaml`, `AGENTS.md` layering | Expect layered repo guidance and Codex discovery |
| `copilot-skill` | Prompt files, always-on instructions, Copilot agent packaging | Expect host-specific discovery |
| `internal-house-style` | Organization-specific policy, wrappers, or naming | Local overlays, never universal requirements |
| `auto` | Mixed or incomplete evidence | Infer carefully and report the uncertainty |

You SHALL infer the profile from file locations, frontmatter, examples, and ambient repository
guidance.
WHEN the evidence mixes hosts THEN you SHALL report `auto` rather than assert false certainty.
WHEN a rule is house style rather than a portable requirement THEN you SHALL label the finding as
profile-specific.

WHEN the target is a plugin or skill in this repository THEN you SHALL additionally apply the
repository overlay, which `SKILL.md` routes you to.

You SHALL NOT present house rules as universal defects. WHEN relative paths and one-hop references
satisfy this standard THEN you SHALL treat them as correct regardless of what a stricter local
convention would require.

## Metadata

The `name` and `description` are the retrieval surface. Everything else in the file is invisible
until they match.

- `description` states what the skill does and when to use it. A description giving only one of the
  two cannot be matched against a user's request.
- The description carries discriminating terms, not an exhaustive case list.
- Long descriptions risk a silent load failure on some hosts. Where a host documents a limit, treat
  it as hard: an over-length description does not degrade, it disappears.
- A skill with predictable false positives ends its description with an explicit negative trigger.

The directory name is the invocation slug, and the standard constrains its shape: lowercase
alphanumeric characters and single hyphens, no leading or trailing hyphen, no consecutive hyphens,
and at most 64 characters. A slug outside that shape may still resolve on a permissive host, so what
you are judging is portability rather than breakage — a skill that will only ever run on one host has
a legitimate reason to differ, and one meant to travel does not.

How the `name` field relates to the slug is not settled by this standard. Hosts and repositories
differ, so treat any rule about title-casing or deriving one from the other as house convention.

Script coverage: `<skills-file-root>/scripts/frontmatter_check.sh`.

## Progressive disclosure

- Level 0 — metadata for retrieval
- Level 1 — a short `SKILL.md` that routes
- Level 2 — one reference at a time, loaded on a stated condition
- Level 3 — scripts and assets on demand

`SKILL.md` answers what the skill is, what workflow the agent is in, and what to read next, then
stops. Detailed procedures, full rubrics, and extended specifications belong in references.

Each fact lives in exactly one place. A rule stated in both `SKILL.md` and a reference will drift,
and the drift is silent because neither copy knows about the other.

A reference that exists but that `SKILL.md` never links is shipped weight nobody loads: it inflates
what the skill ships without ever reaching the agent's context, and because nothing points at it,
nothing forces it to stay current as the rest of the skill changes around it.

References do not point to other references. A reader who must open a second file to understand the
first has lost the budget the layering was meant to save.

Script coverage: `<skills-file-root>/scripts/reference_check.sh` for link integrity, orphaned
references, and nesting.

## File hygiene

All shipped text files use LF line endings. Shell scripts carry the executable bit and a valid
shebang. A script without either fails at the moment the agent needs it, with an error that describes
the symptom rather than the cause.

The one legitimate exception is a fixture whose entire purpose is exercising CRLF-detection logic
itself — a test input deliberately carrying CRLF so the check that flags CRLF has something real to
catch. That CRLF is the thing under test, not an accident, and flagging it as a hygiene defect would
be flagging the test for doing its job.

CRLF inside an executable script does not get this exception: it is a hard error regardless of what
the file is for. The carriage return lands inside the interpreter path, so `#!/usr/bin/env sh`
resolves as a missing binary and the shebang fails before the script's own logic — including any CRLF
check it might perform — ever runs.

Script coverage: `<skills-file-root>/scripts/script_sanity.sh`.

## Names that cross a boundary

Every name in documentation — roles, phases, modes, parameter values — is the exact string the CLI or
API accepts. One canonical form appears everywhere: docs, `--help`, error messages, and outputs.

WHEN a CLI accepts named values THEN it offers a way to list them.
WHEN documentation uses a friendly name differing from the accepted value THEN it includes the
mapping.

## Error messages

Errors are for the agent that must recover from them, not the human reading a log.

- No stack traces in normal errors.
- One to three lines; detail behind a verbosity flag.
- An error for an unrecognized value names the valid alternatives.
- A consistent shape, so the agent can parse what to do next.

## Output size

- Output is compact by default; verbosity is requested.
- Commands with unbounded output offer filtering or pagination.
- Metadata and content are separately requestable.

Script output enters the agent's context; script source does not. A command that dumps everything
spends the budget the skill's layering was designed to protect.

## Cold start

The skill is usable on first run without installing a toolchain, compiling source, or downloading
large dependencies.

WHEN compiled tools are included THEN a prebuilt binary ships and the wrapper prefers it over
building.
WHEN runtime dependencies are required THEN they are documented and their absence produces an
actionable error rather than a crash.

## Idempotency

Identical re-runs on unchanged input produce identical output. Non-deterministic values are avoided
in default output or deterministically seeded.

Scripts creating temporary files remove them on EXIT, INT, and TERM. A skill documenting "create X"
is safe to re-run when X exists.

Script coverage: `<skills-file-root>/scripts/script_sanity.sh` reports a missing trap handler wherever a
script creates temporary files.

## Error recovery

WHEN a workflow has three or more steps THEN each step's success or failure is independently
detectable.
WHEN a step fails THEN the skill says whether to retry, restart, or abort.

A script exiting zero after a significant sub-task failed silently is worse than one that fails
loudly, because the agent proceeds on a false premise. Partial output from a failed run does not
corrupt a re-run or mix old and new results.

## Credential safety

- No credentials committed, echoed, logged, or printed in normal or error output.
- Error messages do not include command lines carrying credential flags or headers.
- Shell tracing is disabled around credential handling.
- No `eval` on user-provided input.

Script coverage: `<skills-file-root>/scripts/script_sanity.sh` scans for secret-pattern filenames.

## Composition

WHEN a skill consumes another skill's output THEN the integration point is tested end to end: run the
producer, run the consumer against its real output, confirm no manual step was required in between.
