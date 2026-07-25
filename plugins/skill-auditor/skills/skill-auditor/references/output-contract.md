# Output Contract

The default output is a concise Improvement Brief a maintainer can act on immediately.

You SHALL include every required section, keep the brief readable without its appendices, and ground
`Key evidence` in at least one observed prompt, output, or file anchor.

WHEN detailed evidence helps THEN you MAY append eval tables, deterministic check output, or
before/after notes after the brief.

You SHALL NOT default to a large taxonomy table, a long audit dissertation, or a script dump. The
brief competes for the maintainer's attention with the work it is asking them to do; length spends
that attention before the recommendations arrive.

## Required template

```markdown
# Improvement Brief: <target>

## Scope
<plugin with N skills, or a single skill — and, when they differ, which description text you evaluated>

## Direction
<proceed | proceed corrected | wrong shape | wrong problem | undetermined | not worth doing>
<why, in a sentence or two, and the evidence that would flip it>

## Packaging verdict
<KEEP_AS_SKILL | REWORK_AS_SKILL | MIGRATE_TO_AGENTS | MIGRATE_TO_HOOK | MIGRATE_TO_SUBAGENT |
 MIGRATE_TO_COMMAND | MIGRATE_TO_EXPLICIT_PROMPT | MIGRATE_TO_TOOL | MIGRATE_TO_MCP |
 HYBRID_RECOMMENDED>

## One-sentence diagnosis
<What is most fundamentally wrong or right>

## Key evidence
- <one prompt, output, or file observation>
- <one prompt, output, or file observation>

## Top issues
1. <issue> — <file:line> — <the fix, or "fix unknown, needs investigation">
2. <issue> — <file:line> — <the fix, or "fix unknown, needs investigation">
3. <issue> — <file:line> — <the fix, or "fix unknown, needs investigation">

## Recommended changes
1. <the text as it should read, not a description of it>
2. <the text as it should read, not a description of it>
3. <the text as it should read, not a description of it>

## Verification plan
- <test>
- <test>
- <test>

## Optional appendices
- Deterministic checks
- Eval cases
- Before/after notes
```

## Briefing rules

You SHALL lead with the direction judgment, plain and reasoned, never diluted beneath a defect list.
A maintainer who reads three fixes before learning the thing should not exist has been told to spend
attention you were about to say was wasted.

You SHALL stand an existence-threatening finding alone under a clear-error standard, never as an item
in a list.

You SHALL give each finding a location and a fix, or say "fix unknown, needs investigation". A
finding naming what is wrong without saying what to write instead is a todo, and it costs another
round trip before anything improves.

WHEN a finding is serious THEN you SHALL add the poka-yoke line: the upstream change that makes that
error class impossible, or failing that, self-announcing. Repairing the instance and leaving the
class reachable means the same finding returns under a different name.

You SHALL mark each claim knowledge, inference, or guess, and you SHALL say "not verified" where you
could not check rather than delivering an inference in the register of an observation.

You SHALL keep the diagnosis to one sentence, keep `Key evidence` observed rather than abstract,
limit the issue and change lists to the highest-leverage items, and always include a verification
plan.

WHEN the target is a plugin THEN you SHALL add a `## Plugin-level findings` section before
`## Top issues`, carrying one verdict line per bundled skill plus the package-level defects. A
package can be misassembled while every skill inside it is sound, so a single verdict cannot carry
both.

WHEN a plugin's bundled skills warrant different verdicts THEN the `## Packaging verdict` line SHALL
carry the package's own verdict and say that the skills differ, pointing at the per-skill lines. You
SHALL NOT average them: a plugin holding one sound skill and one that belongs in a hook has no
single verdict, and inventing one hides the finding that matters.

WHEN the installed and repository descriptions differ THEN you SHALL say so in `Scope` rather than
burying it among the issues. It changes which artifact every trigger finding describes.

WHEN a finding comes from house convention rather than the portable standard THEN you SHALL label it
as such, so a maintainer working outside this repository can tell which findings travel.

WHEN nothing survives examination THEN you SHALL return a clean brief that names what you checked. A
clean result, plainly scoped, is a finished audit; manufacturing a finding to look thorough spends
the maintainer's attention on nothing.
