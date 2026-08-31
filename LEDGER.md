# Quality Improvement Ledger

This ledger accumulates evidence-backed lessons from skill design, evaluation, and agent execution for later transfer into `skill-auditor` and a future prompt-engineering skill. Entries are observations and design candidates, not current repository requirements. `Port status: unimplemented` means the lesson has not yet been encoded and validated in either destination.

Each entry records the quality effect, the evidence that can falsify it, the smallest reusable rule it suggests, and conditions that limit the rule. New evidence should revise or retire an entry rather than creating a second source of truth for the same lesson.

## Software-development skill index

These are the final campaign decisions for plugin version 1.1.0. “Retained without measured lift” means the bounded wording is factually justified and survived review, but the matched projects did not establish a causal improvement; it is not an effectiveness claim. The authoritative evidence synthesis is `.local/evals/software-development-20260829/reports/final-campaign-report.md`.

| Skill | Highest-value candidate improvement | Evidence status |
| --- | --- | --- |
| `async-rust` | Separate future drop, cancellation request, blocking-work termination, external-effect reconciliation, and owned join; consult the selected runtime’s operation-level contract. | Accepted split evidence |
| `behavior-preserving-migration` | Track authority at every transition state and distinguish rollback from forward recovery after target-side writes. | Proposed revision deleted; control preferred by both recovery reviewers |
| `c-development` | Treat resize, retained callbacks, partial startup, overlap-safe borrowed input, stop/wake/join, and teardown as explicit ownership transitions. | Corrective revision accepted; machine 2/3 → 3/3 |
| `concurrency-engineering` | Own admission, pressure, cancellation, terminal outcomes, synchronization, and useful parallelism across language-specific runtimes. | New skill accepted; degrading corrective wording deleted (2/3 → 1/3) |
| `cpp-development` | Define fallible-mutation postconditions and require exception-safe admission plus owned completion without accidental public-header or ABI churn. | Corrective revision accepted; machine tie and blinded semantic preference |
| `csharp-development` | Preserve all `Task.WhenAll` failures when required; make channels, async streams, pipes, cancellation, disposal, and process-tree ownership explicit. | Foundational revision retained without measured lift; tied corrective wording deleted |
| `go-development` | Correct cache-evidence scope, resolve `go`/toolchain semantics by supported horizon, distinguish cancellation from join, and verify exact positive plus negative build selections. | Foundational revision retained; degrading corrective wording deleted (3/3 → 2/3) |
| `java-development` | Add process-pipe lifecycle, collect-all versus fail-fast outcomes, real cancellation propagation, and explicit reactive admission/full-buffer policy. | Accepted split evidence |
| `javascript-development` | Make JSDoc/checkJs an executable JavaScript-owned boundary and clarify language-module versus Node package-resolution ownership. | Foundational revision retained without measured lift; tied corrective wording deleted |
| `kotlin-development` | Condition structured concurrency on the selected library/targets; define supervision, failure aggregation, Flow/channel pressure, callback teardown, and JVM process ownership. | Corrective revision retained for compiler and cancellation correctness; 0/3 tie, no measured lift |
| `nodejs-development` | Distinguish event loop, libuv pool, workers, and subprocesses; bound queues and reconcile error/exit/close/cancellation before teardown. | Accepted split evidence |
| `performance-engineering` | Add causal offered-work, queueing, tail, parallel-scaling, contention/locality, and resource-ceiling guidance through conditional references. | Foundational revision retained without measured lift; loss-biased percentile contract hardened post-reveal |
| `php-development` | Separate native runtime types, analyzer assumptions, and executed validation; strengthen reusable-worker, Fiber/event-loop, and subprocess cleanup. | Accepted split evidence |
| `python-development` | Separate static annotations from runtime validation; preserve framework task groups, process/pipe/descendant cleanup, and caller-selected multiprocessing contexts. | Corrective revision accepted; machine tie and blinded semantic preference |
| `refactoring` | Require evidence of a concrete structural improvement as well as preservation across external, generated, reflective, concurrent, and binary surfaces. | Revision accepted by both blinded reviewers; machine 0/3 tie retained as a limitation |
| `ruby-development` | Separate static/runtime typing from domain validation and make runtime/framework-specific cancellation plus child reaping and pipe drainage explicit. | Accepted split evidence |
| `rust-development` | Expose Cargo’s executable trust boundary, distinguish host and compilation targets, preserve the supported feature matrix, and bound every retained worker-pool path. | Foundational revision retained; degrading corrective wording deleted (2/3 → 1/3) |
| `rust-panic-audit` | Withdraw unenforced read-only claims; correct Cargo scope, target/feature selection, authority, timeout, output, lockfile, and mutation contracts. | Accepted split evidence |
| `shell-development` | Qualify POSIX.1-2024 `pipefail`, provide an honest zsh/fish fallback, and own process groups, descendants, jobs, traps, and primary status. | Accepted split evidence |
| `sql-development` | Add plan/statistics/skew/spill/cast/index tradeoff guidance and host-adapter cancellation, parameter-type, cursor, transaction, and pooled-state ownership. | Revision retained; machine tie and blinded semantic advantage |
| `swift-development` | Define task-group failure policy, distinguish buffered `AsyncStream` from backpressure, and own process/pipe/resource teardown without forcing new packages. | Revision accepted; machine 1/3 → 3/3 and blinded preference |
| `systematic-debugging` | Replace one-run non-occurrence with discriminating exposure evidence and permit causal sets rather than forcing a single root cause. | Foundational revision retained without measured lift; 0/3 tie exposed a shared provenance gap |
| `test-driven-development` | Establish oracle authority before the red, defer mechanism choice, and require a test that discriminates the intended behavior from a false green. | Foundational revision retained without measured lift; 0/3 tie exposed shared test-discrimination gaps |
| `trunk-based-development` | Replace universal independent revertibility and daily quotas with dependency-visible revert, containment, or forward-repair paths and independently healthy slices. | Revision accepted by both blinded reviewers; shared validator limitation preserved |
| `typescript-development` | Clarify checkJs ownership, moving versus fixed resolution profiles, declarations/consumer evidence, and separate direct runtime execution from static checking. | Revision accepted; machine 2/3 → 3/3 and blinded preference |
| `unsafe-rust` | Qualify negative-impl and provenance volatility, distinguish FFI unwind contracts, and cover edition-gated unsafe syntax and safe-caller exploitability. | Accepted split evidence |

## Evaluation and evidence

### L-001 — Structural validity is not task value

- Port status: unimplemented.
- Quality effect: schema checks, packaging validation, trigger corpora, and prose rubrics can all pass while a skill has no demonstrated effect on a real task.
- Evidence: the software-development structural suite passes while most task evals remain prose-only or use tiny non-falsifying fixtures; the current campaign therefore requires matched executable projects and independent outcome validation.
- Transfer candidate: `skill-auditor` should distinguish structural, routing, execution, and task-value claims and refuse to promote evidence across those boundaries.
- Limiting condition: structural checks remain necessary release evidence; this entry says they are insufficient alone, not unimportant.

### L-002 — A control is valid only when skill availability is falsified

- Port status: unimplemented.
- Quality effect: a nominal no-skill arm can silently load user-installed skills through a launcher or shared agent home, erasing the causal contrast.
- Evidence: the first clean-home probe was contaminated because the user `codex` launcher restored `/home/rashino/.codex`; direct invocation of the resolved Codex binary with a fresh home produced `SKILL_UNAVAILABLE` in control and `LOCAL_SKILL_ACTIVE` in treatment.
- Transfer candidate: require a positive treatment probe and a negative control probe at the actual host boundary before admitting behavioral evidence.
- Limiting condition: the exact binary and home mechanism are host-specific; the invariant is exclusive capability visibility.

### L-003 — Blinding needs operating-system isolation when same-user reads are possible

- Port status: unimplemented.
- Quality effect: opaque labels do not hide held-out fixtures or condition identity from an executor that can read sibling directories, user skill homes, or controller records.
- Evidence: the campaign’s Bubblewrap probe loaded a repository-local treatment skill while hiding the repository, user skill directory, controller state, and other trial workspaces.
- Transfer candidate: make the custody threat model explicit; use process or operating-system isolation when helper-level anonymization cannot prevent same-user reads.
- Limiting condition: helper-level custody is sufficient when executors cannot inspect controller storage by construction.

### L-004 — Forward evidence must be prospective and append-only

- Port status: unimplemented.
- Quality effect: editing tasks, rubrics, replacement rules, or stopping criteria after seeing candidate output creates overfit and converts confirmation into another diagnostic iteration.
- Evidence: the split-test campaign freezes two diagnostic and two held-out confirmation projects per skill, retains every attempt, and permits replacement only for predeclared infrastructure failures.
- Transfer candidate: `skill-auditor` should require pre-exposure instrument hashes, explicit replacement rules, and a new hidden instrument after a confirmation-driven revision.
- Limiting condition: exploratory diagnostics may iterate openly when they are not represented as confirmation evidence.

### L-005 — Outcome vectors are more honest than arbitrary aggregate scores

- Port status: unimplemented.
- Quality effect: a weighted total can hide a correctness regression behind style or speed gains and makes conclusions depend on unvalidated weights.
- Evidence: this campaign records deterministic checks, contract preservation, scope discipline, verification quality, completion rate, and blind semantic judgments separately.
- Transfer candidate: compare material outcomes and tradeoffs directly; aggregate only when the decision maker has supplied a defensible utility model.
- Limiting condition: a domain may legitimately have a validated score or maker-set threshold.

### L-006 — Source identity is part of behavioral evidence

- Port status: unimplemented.
- Quality effect: testing a working-tree skill, installed cache, or stale marketplace copy without identifying which one ran makes a result irreproducible and can attribute behavior to the wrong artifact.
- Evidence: the campaign freezes an immutable baseline plugin digest, snapshots each candidate, invokes the host with a clean home, and records the exact skill tree supplied to treatment.
- Transfer candidate: retain host version, model, skill source, content digest, loaded reference identity, and project digest with every behavioral run.
- Limiting condition: source identity does not by itself prove activation or use; it composes with routing and task evidence.

### L-007 — Relative-path success is not portable execution evidence

- Port status: unimplemented.
- Quality effect: helpers and manifests can appear correct only because the controller happened to run from the author’s working directory or because parent directories already existed.
- Evidence: the split-test initializer rejected an absolute target whose intermediate parent was absent, and prior integrity manifests failed when checked from the wrong directory.
- Transfer candidate: require absolute-path and unrelated-CWD probes, explicit parent preconditions, and path-independent error recovery for agent-facing tools.
- Limiting condition: a deliberately CWD-relative interface is acceptable when that contract is explicit and tested from both valid and invalid locations.

## Instruction architecture and routing

### L-008 — Add conditional depth, not always-loaded breadth

- Port status: unimplemented.
- Quality effect: placing every advanced concern in `SKILL.md` raises peak context on every activation and can reduce task focus even when the facts are correct.
- Evidence: the performance review found important missing systems topics, but the lean design is two conditionally loaded references while preserving the current compact router.
- Transfer candidate: put stable mission and routing in the skill body; route independently triggered detail to one-hop references with explicit loading conditions.
- Limiting condition: an invariant needed on every activation belongs in the body even if it costs context.

### L-009 — Ownership boundaries should follow the artifact and executable contract

- Port status: unimplemented.
- Quality effect: overlapping vocabulary can activate multiple generic skills while still omitting the one that owns the real runtime or compiler boundary.
- Evidence: JSDoc/checkJs source edits are JavaScript-owned, compiler configuration and declarations are TypeScript-owned, and native Node TypeScript execution requires Node plus TypeScript rather than JavaScript by default.
- Transfer candidate: define a primary owner for each artifact and add siblings only for a material consumer, runtime, compiler, lifecycle, or compatibility surface.
- Limiting condition: genuine cross-artifact changes should compose; avoiding overlap must not suppress necessary owners.

### L-010 — A handoff must name a reachable fallback

- Port status: unimplemented.
- Quality effect: “route to the focused skill” fails when no such skill is installed, leaving framework and language variants ownerless or inviting the agent to apply an adjacent skill incorrectly.
- Evidence: current Python, Ruby, PHP, zsh, and fish guidance contains handoffs whose focused companion may be absent.
- Transfer candidate: when a preferred companion is unavailable, name the authoritative fallback, preserve its lifecycle/configuration, and disclose that no focused skill owned the work.
- Limiting condition: do not duplicate a present companion skill’s detailed guidance in the fallback.

### L-011 — Version facts should be evidence horizons, not timeless rules

- Port status: unimplemented.
- Quality effect: unqualified claims about standards, runtimes, package managers, and APIs become false while their underlying decision invariant remains useful.
- Evidence: POSIX.1-2024 specifies `pipefail`, invalidating the unqualified statement that it is non-POSIX, while many supported shells and older POSIX targets still lack it.
- Transfer candidate: bind advice to the repository’s declared version/edition and retain the observed current version in evidence rather than durable instructions.
- Limiting condition: stable language semantics may be stated directly when the supported horizon makes them invariant.

## Foundational engineering lessons

### L-012 — Cancellation is a request, not proof of completion

- Port status: unimplemented.
- Quality effect: releasing shared state after signalling cancellation can leave tasks, goroutines, threads, workers, subprocesses, callbacks, or descendants running against destroyed resources.
- Evidence: the same lifecycle gap recurs across Go, Node, Python, Ruby, PHP, C, C++, Kotlin, C#, Swift, and Rust research.
- Transfer candidate: require an owner, an admission stop, a cancellation protocol, outcome observation, and a join or equivalent terminal boundary before dependent resource destruction.
- Limiting condition: detached work is valid only when another explicit owner assumes its lifetime and outcome contract.

### L-013 — Static type evidence is not runtime validation

- Port status: unimplemented.
- Quality effect: annotations, casts, stubs, PHPDoc, RBS, TypedDict, or analyzer assertions can satisfy a checker while malformed or unauthorized external values still enter the program.
- Evidence: Python, Ruby, PHP, JavaScript/JSDoc, and TypeScript reviews independently identified this boundary.
- Transfer candidate: ask which boundary actually parses, validates, authorizes, and rejects runtime data; test malformed values there.
- Limiting condition: runtime-enforced declarations can reject some values, but they still do not establish domain validity or authorization.

### L-014 — Process ownership includes pipes, status, descendants, and escalation

- Port status: unimplemented.
- Quality effect: waiting for or killing one process can deadlock on full pipes, lose the primary error, leak a zombie, or leave descendants running.
- Evidence: Node, Python, Ruby, PHP, Shell, Java, Kotlin, C#, and Swift research all surfaced incomplete subprocess lifecycle contracts.
- Transfer candidate: define argument construction, environment/CWD, output bounds or drainage, spawn failure, exit/status collection, timeout, graceful termination, escalation, descendant ownership, and cleanup ordering.
- Limiting condition: platform and framework facilities own the exact process-tree semantics; generic guidance should preserve rather than invent them.

### L-015 — Intermittent non-occurrence needs an exposure statement

- Port status: unimplemented.
- Quality effect: one passing rerun can be mistaken for a fix to a stochastic, timing-sensitive, or long-horizon failure.
- Evidence: systematic-debugging currently says to run a probe once where possible and to show the failure no longer occurs without requiring attempts, exposures, a deterministic scheduler, or a detection limit.
- Transfer candidate: record the minimum observations needed to discriminate hypotheses and state what a clean run does and does not establish.
- Limiting condition: one observation can be decisive when the probe deterministically separates the alternatives.

### L-016 — Test-first work needs an authoritative oracle before a red test

- Port status: unimplemented.
- Quality effect: a fast red-green loop can faithfully encode the wrong outcome when tickets, implementation, tests, and consumer contracts disagree.
- Evidence: the TDD review found no explicit authority check before the agent commits to a mechanism and expected result.
- Transfer candidate: resolve material ambiguity from the governing requirement or consumer contract before treating a failing test as the target.
- Limiting condition: exploratory characterization may intentionally record current behavior without declaring it correct.

### L-017 — Refactoring must prove both preservation and structural value

- Port status: unimplemented.
- Quality effect: passing tests can coexist with a rewrite that adds indirection, preserves the original ownership problem, or damages an unobserved ABI/reflection/serialization surface.
- Evidence: the current refactoring skill has strong preservation surfaces but no executable evidence that the stated structural objective was achieved.
- Transfer candidate: require the least expensive checks that observe every declared preservation surface plus concrete evidence of the removed dependency, duplicated authority, lifecycle coupling, or similar problem.
- Limiting condition: no universal complexity or line-count metric establishes structural improvement.

### L-018 — Migration rollback changes meaning after target-side writes

- Port status: unimplemented.
- Quality effect: routing traffic back to a stale source after the target accepts authoritative writes can lose or resurrect data while being mislabeled as rollback.
- Evidence: migration research identified missing authority-transfer and post-cutover-write handling in the current generic guidance; the first dual-store instrument also accepted an implementation that disabled every rollback because it tested only the forbidden post-write direction and never proved that pre-write rollback remained reachable.
- Transfer candidate: at every rollback point, state the authority, how post-cutover writes reach it, and when the only safe path becomes forward recovery.
- Limiting condition: pre-write cutovers and fully reversible replicated systems may retain a true rollback path.

### L-019 — Cached results prove only the cache-keyed condition

- Port status: unimplemented.
- Quality effect: rejecting all cached evidence wastes time, while accepting it as fresh execution can miss untracked external inputs or environment changes.
- Evidence: Go’s current top-level wording is stricter than the official test-cache contract and its own detailed reference.
- Transfer candidate: state the scope of cached evidence; bypass it only when freshness matters or relevant inputs fall outside the cache key.
- Limiting condition: repository policy may require fresh execution for a particular release or investigation.

### L-020 — Performance conclusions need a causal resource and workload ledger

- Port status: unimplemented.
- Quality effect: a faster microbenchmark can hide dropped work, coordinated omission, queue growth, oversubscription, shifted cost, external ceilings, or a new tail-latency failure.
- Evidence: performance research identified missing offered/admitted/completed/error counts, open-versus-closed load, parallel scaling, contention/false sharing, locality/NUMA, and CPU/memory/I/O/network ceilings.
- Transfer candidate: require a representative workload, causal perturbation, correctness guardrails, offered and completed work accounting, concurrency/queue state, limiting-resource evidence, and a stopping rule.
- Limiting condition: load model, counters, topology, and thresholds must come from the actual system rather than a universal checklist.

### L-021 — SQL row correctness and optimizer correctness are separate surfaces

- Port status: unimplemented.
- Quality effect: semantically correct SQL can still fail operationally because estimates, statistics, skew, spills, parameter types, casts, or index costs produce an unsafe or unstable execution path.
- Evidence: the SQL review found strong relational semantics but only minimal plan guidance and no executable plan/statistics fixture.
- Transfer candidate: distinguish result cardinality from estimated cardinality; compare estimated and actual work, sent parameter types, spills, access-path loss, and read/write/storage tradeoffs under a disposable workload.
- Limiting condition: node names, metrics, safe plan commands, and estimator behavior are vendor- and version-specific.

### L-022 — Immutable sources need an explicit writable-copy boundary

- Port status: unimplemented.
- Quality effect: preserving source permissions during a fixture copy can make the executor’s private project read-only, while weakening permissions on the source destroys custody.
- Evidence: the first frozen-case smoke run failed before model execution because `copytree` preserved the seed directory’s read-only mode and Git could not initialize the destination.
- Transfer candidate: hash and freeze the source, create a private copy, then explicitly grant mutation only to that copy and verify the source digest afterward.
- Limiting condition: copy mechanisms that intentionally normalize destination permissions may already provide this boundary, but it must be observed rather than assumed.

### L-023 — Generated-file policy is part of a task instrument

- Port status: unimplemented.
- Quality effect: build caches, bytecode, test reports, and generated artifacts can dominate diffs, obscure semantic review, or be silently deleted even when some are repository-owned outputs.
- Evidence: the successful harness smoke produced Python bytecode in an otherwise tiny patch because the fixture had no generated-file policy. Later, all 24 first C++ trial artifacts passed their substantive behavior checks but were rejected because four validators promoted “generated paths are ignored” into the undeclared requirement “no ignored build output exists”; agents had correctly run the repository build and left its ignored `build/` products.
- Transfer candidate: every executable fixture should identify ignored ephemeral outputs, required generated outputs, and the command that validates or refreshes the latter; evaluators should not apply a universal cleanup list.
- Limiting condition: an intentionally generated artifact is part of the result when the repository declares it authoritative or distributable.

### L-024 — Post-hoc integrity detection is not read-only enforcement

- Port status: unimplemented.
- Quality effect: a tool can detect a tracked mutation after executing repository code yet still leave the user’s source, caches, external files, credentials, or network state changed while claiming the run was read-only.
- Evidence: adversarial `rust-panic-audit` probes let both a build script and a procedural macro overwrite a tracked file; the runner returned incomplete afterward but did not prevent or restore the mutation.
- Transfer candidate: distinguish non-mutating tool code, post-run integrity observation, rollback, and externally enforced read-only execution; claim only the strongest property actually enforced at the executable boundary.
- Limiting condition: trusted build-time code may be acceptable in a disclosed native mode, but trust is not equivalent to enforcement.

### L-025 — Requested scope and effective tool scope must agree

- Port status: unimplemented.
- Quality effect: a report can appear complete while lexical selection, compiler package selection, default features, target kinds, target triples, tests, doctests, and workspace/member defaults cover different programs.
- Evidence: the panic-audit runner can select workspace default members lexically while Cargo compiles an explicitly requested member; it also lacks no-default-feature and target-triple controls and can record `workspace` even when a package silently wins.
- Transfer candidate: report requested and effective scope separately, reject contradictory selectors, and fail incomplete whenever any claimed surface lacks corresponding executable evidence.
- Limiting condition: multiple evidence mechanisms may intentionally cover different surfaces when the report names the union, overlap, and residual gaps precisely.

### L-026 — Agent-facing tools need bounded execution and bounded default output

- Port status: unimplemented.
- Quality effect: a valid analysis can hang indefinitely, exhaust memory on captured output, or consume the agent’s context with an unbounded report.
- Evidence: `rust-panic-audit` captures complete Cargo/Clippy output without a timeout and emits every finding in pretty-printed JSON; build scripts, proc macros, wrappers, or the network can therefore stall or flood it.
- Transfer candidate: add per-step deadlines, process-tree cleanup, streaming or bounded capture, compact defaults, deterministic truncation counts, and an explicit full-report destination.
- Limiting condition: a caller may request an unabridged artifact when its destination and resource budget are explicit; the interactive default should remain bounded.

### L-027 — Evaluation plans must reopen when toolchain reality differs

- Port status: unimplemented.
- Quality effect: treating an assumed local compiler or runtime as available can turn a real-project evaluation into a prose substitute or an unreported coverage gap.
- Evidence: discovery confirmed current native toolchains for most languages but found no Swift, Kotlin, PowerShell, or .NET SDK despite the initial plan naming only the first three as container lanes.
- Transfer candidate: probe the exact executable capability before freezing an instrument, then either supply an isolated pinned environment or narrow the claim explicitly.
- Limiting condition: a parser-only or structural task may not require execution, but it cannot establish runtime behavior or build compatibility.

### L-028 — Blind artifacts must retain case-aligned decision context

- Port status: unimplemented.
- Quality effect: anonymizing only candidate outputs can leave reviewers judging code without the exact task and rubric, while a global brief can misalign requirements when multiple cases are shuffled into opaque blocks.
- Evidence: the split helper copies each run’s artifact but not its input; the initial harness brief combined rubrics without a reliable case-to-block mapping.
- Transfer candidate: place the condition-neutral task and case rubric beside every anonymous sample, while keeping controller provenance and condition identity outside the view.
- Limiting condition: a single shared task may live once in the reviewer brief when every presented artifact unambiguously shares it.

### L-029 — Filesystem hiding fails if a privileged runtime socket remains visible

- Port status: unimplemented.
- Quality effect: an executor inside a nominally hidden filesystem can use Docker, Podman, or another privileged service socket to mount host paths that the outer namespace concealed.
- Evidence: the initial Bubblewrap design read-only-bound `/`, which retained `/run/docker.sock` even though campaign and user-skill directories were overmounted.
- Transfer candidate: include service sockets and alternate authority channels in the custody threat model; hide them or replace them with a narrowly scoped controller interface.
- Limiting condition: an unprivileged socket whose server independently enforces the same path and authority boundary may be safe, but namespace appearance alone does not establish that.

### L-030 — Release identity must have one mechanically checked authority

- Port status: unimplemented.
- Quality effect: stale versions or capability claims in prose make users and evaluators reason about a package other than the artifact they actually installed.
- Evidence: both software-development manifests declare v1.0.1 while the README still declared v1.0.0; the README also promoted a post-hoc tracked-file check into a non-mutation guarantee that the panic-audit adversarial probe disproved.
- Transfer candidate: derive or verify release identity and executable capability claims against manifests and behavioral tests, and phrase weaker observed properties without strengthening them in documentation.
- Limiting condition: deliberately independent compatibility or protocol versions may differ when their authorities and meanings are explicit.

### L-031 — Isolation masks must preserve transitive runtime dependencies

- Port status: unimplemented.
- Quality effect: hiding a directory can remove an unrelated capability through symlinks, sockets, loaders, certificates, or resolver files even when its public path appears outside the mask.
- Evidence: masking `/run` removed privileged service sockets but made `/etc/resolv.conf` dangle on this host because its resolved file lives under `/run/systemd/resolve`; restoring only that read-only file preserved DNS while keeping the broader runtime tree absent.
- Transfer candidate: resolve and probe the dependency graph of every masked path at the real execution boundary, restore only the least-authority inputs required by the task, and retest both exclusion and intended capability.
- Limiting condition: the concrete dependency and restoration path are environment-specific; do not hard-code this host’s resolver layout as a universal design.

### L-032 — A common eval prompt must not supply the treatment's distinctive contribution

- Port status: unimplemented.
- Quality effect: an otherwise realistic matched task can erase the measured difference when it tells every condition the diagnosis, workflow, counterfactuals, or verification method that the skill is supposed to contribute.
- Evidence: first-pass performance prompts named the exact bottlenecks and isolated repairs, while first-pass TDD prompts prescribed meaningful-red and discrimination steps; independent reviewers therefore blocked them even though seed/oracle polarity was correct.
- Transfer candidate: keep common inputs complete about the desired outcome, authoritative contract, available observations, constraints, and completion evidence, but leave the treatment-owned reasoning or method absent unless the user would necessarily provide it.
- Limiting condition: a maker-fixed method is part of the task contract and must remain common to every condition; such a case evaluates execution of that method, not whether the skill discovers it.

### L-033 — Plausible output is not evidence that the measured mechanism produced it

- Port status: unimplemented.
- Quality effect: relational checks over one report can accept fabricated counters, hashes, percentiles, or selections while the defective engine remains untouched.
- Evidence: disposable mutations hard-coded acceptable performance reports around the original completion-paced load generator and scaling model; the rolling-envelope validator also accepted a CLI that fabricated empty consumer results, and the cohort-router validator accepted incorrect target-native data because its comparison evidence was derived from candidate-owned request/error summaries rather than backend results.
- Transfer candidate: invoke the underlying behavior across hidden counterfactual configurations, derive expected invariants independently, and bind public reports to those observed results; include shortcut mutations in validator tests.
- Limiting condition: an output-only contract may legitimately care only about bytes at the boundary, but then provenance or internal repair must not be claimed.

### L-034 — A passing test command does not establish a discriminating test

- Port status: unimplemented.
- Quality effect: a candidate can delete meaningful tests, substitute a tautology, and retain a green runner while supplying production code that no regression test protects.
- Evidence: all four first-pass TDD validators accepted the oracle production change after the real tests were replaced by one always-true assertion; fixed-point semantic probes also missed over-broad or capped implementations.
- Transfer candidate: when test quality is part of the claim, verify that submitted tests execute the promised production boundary and fail under an independent behavior-breaking mutation or counterfactual, while preserving freedom in test organization.
- Limiting condition: mutation is one discrimination probe, not a universal testing methodology; destructive or nondeterministic systems may need a safer equivalent.

### L-035 — Policy text must be checked through the policy's consumer

- Port status: unimplemented.
- Quality effect: searching for required substrings accepts commented-out ignore rules, stale examples, and prose that names a policy without enforcing it.
- Evidence: the first performance and TDD instruments passed generated-file checks after `.gitignore` was replaced with comments containing the expected tokens, while `git check-ignore` showed representative artifacts were not ignored; the rolling-envelope migration instrument reproduced the same false positive with every required pattern commented out.
- Transfer candidate: validate policy through the repository tool or consumer that gives it effect, using representative positive and negative artifacts rather than textual presence alone.
- Limiting condition: syntax or text checks remain useful when the text itself is the delivered contract; they should not be promoted into behavioral evidence.

### L-036 — Disposable tooling must neutralize user policy it does not intend to test

- Port status: unimplemented.
- Quality effect: a supposedly isolated fixture can fail, prompt interactively, or inherit unrelated behavior from global Git, compiler, package-manager, shell, or credential configuration.
- Evidence: a controller-created baseline commit inherited mandatory user commit signing and failed through the 1Password agent until `commit.gpgsign=false` was scoped to that disposable commit.
- Transfer candidate: identify which ambient policies are part of the experiment, explicitly neutralize only the rest at the narrowest command boundary, and record the effective configuration when it matters to evidence.
- Limiting condition: repository-owned policy must remain active when the task is intended to exercise it; isolation must not silently bypass the contract under test.

### L-037 — An authority transition must be challenged at the transition boundary

- Port status: unimplemented.
- Quality effect: proving validation on a healthy artifact and then exercising cutover separately does not prove that cutover is gated by that evidence; an implementation can pass both checks while trusting a phase label after the artifact diverges.
- Evidence: the checkpointed-archive validator accepted an implementation with the cutover-time validation call removed, and the dual-store validator accepted cutover with its store-divergence guard removed because neither validator corrupted the governed state immediately before the authority transition.
- Transfer candidate: create an independently observed divergence, corruption, stale checkpoint, or missing proof immediately before the transition and require refusal without authority mutation; then repair the state and require the same transition to succeed.
- Limiting condition: when an external transaction or type system makes invalid state unrepresentable at the transition boundary, evidence of that enforcement can replace a mutation probe.

### L-038 — State-machine evidence needs both allowed and forbidden reachability

- Port status: unimplemented.
- Quality effect: a validator that checks only rejection can reward an implementation that rejects every operation, while a validator that checks only success can reward one that ignores safety gates.
- Evidence: the dual-store validator accepted a coordinator whose `rollback()` always raised `ForwardRecoveryRequired`; it proved unsafe rollback was blocked after a target-authoritative write but never proved staged or pre-write rollback remained available.
- Transfer candidate: for every consequential gate, exercise an adjacent allowed state and forbidden state with the same operation, then observe both the returned outcome and protected-state transition.
- Limiting condition: one-sided evidence is sufficient when the public contract intentionally permits only one side and no reachable valid state requires the other.

### L-039 — Checkpoint recovery must distinguish valid progress from valid-but-wrong progress

- Port status: unimplemented.
- Quality effect: checksums and parseability can prove that bytes are internally valid while still resuming from a prefix belonging to another source, silently replacing the intended migration history.
- Evidence: the checkpointed-archive validator accepted removal of the source-prefix comparison because its interruption probe appended only an invalid partial tail to an otherwise correct source prefix.
- Transfer candidate: test incomplete and corrupt tails separately from a fully valid but semantically foreign prefix, and bind retained progress to immutable source identity before resuming.
- Limiting condition: content-addressed formats whose identity cryptographically commits to the authoritative source may establish this binding without a separate record-by-record comparison.

### L-040 — Credential secrecy needs enforcement at the worker boundary

- Port status: unimplemented.
- Quality effect: clearing inherited environment and hiding the user home still leaves a controller credential readable when the controller and its generated shell commands share a mount namespace and user identity.
- Evidence: the first live control and treatment probes both observed `$CODEX_HOME/auth.json` as readable despite the outer Bubblewrap mask; after selecting a Codex filesystem permission profile that denies the controller home to tool calls, both actual worker-shell probes observed it as unreadable while the Codex controller remained authenticated.
- Transfer candidate: separate controller-required secrets from worker authority, enforce denial through the exact child-execution boundary, record the effective profile, and probe non-readability without opening the secret; do not rely on prompt secrecy or path obscurity.
- Limiting condition: the mechanism is host-specific; Codex permission profiles and legacy `sandbox_mode` do not compose, and every supported platform needs an executable denial probe rather than assumed parity.

### L-041 — A completion marker must be content-bound, not merely present

- Port status: unimplemented.
- Quality effect: treating any `result.json` as completion lets truncated, stale, cross-run, or post-finalization-mutated evidence be skipped as if it were a valid attempt.
- Evidence: harness tests reject an empty result, mismatched design identities, missing artifacts, altered project bytes, altered logs, and inconsistent public evidence; the successful smoke round then re-entered idempotently and skipped only after all bindings revalidated.
- Transfer candidate: write completion atomically and last, bind it to immutable design identity plus digests of every consequential artifact and trace, and revalidate those bindings before reuse.
- Limiting condition: an external content-addressed store or transactional database may supply the atomicity and integrity boundary, but a filename or success flag alone does not.

### L-042 — Evaluation infrastructure is part of the tested condition identity

- Port status: unimplemented.
- Quality effect: a run can change meaning without changing its nominal task or skill when the launcher, helper, permission profile, model host, resolver input, or prompt composer changes between design and execution.
- Evidence: the hardened round design records and rechecks per-run hashes for the case, task, composed prompt, rubric, skill source, harness, split helper, Codex package/version, permission profile, and resolved DNS input; changing harness code forces replacement IDs rather than resuming stale runs.
- Transfer candidate: freeze every behavior-guiding layer whose change could alter outcome or custody, while excluding incidental producer state that cannot reach the executor or reviewer.
- Limiting condition: identity evidence establishes which system ran, not that the system was correct; semantic and behavioral validation remain separate.

### L-043 — Timeout ownership includes descendants and output channels

- Port status: unimplemented.
- Quality effect: terminating only the direct child can leave work, locks, network effects, or output pipes alive, while reading unbounded pipes into memory can defeat the controller before its timeout fires.
- Evidence: the harness self-test launches a descendant that creates a new session and ignores `SIGTERM`; timeout cleanup prevents its delayed write, while a separate probe terminates output beyond the declared capture limit without accumulating an unbounded buffer.
- Transfer candidate: launch in an owned process/session boundary, discover and terminate descendants, bound each output channel while streaming, and treat cleanup or capture-limit failure as infrastructure failure rather than task evidence.
- Limiting condition: a container, job object, cgroup, or managed runtime may provide stronger tree ownership; use its observable completion contract instead of duplicating a weaker process walk.

### L-044 — Validators execute untrusted candidate behavior too

- Port status: unimplemented.
- Quality effect: isolating the coding agent but running its submitted tests, imports, build scripts, plugins, or binaries in the controller namespace reopens hidden fixtures, sibling conditions, credentials, service sockets, and ambient policy.
- Evidence: the validator harness now runs inside its own cleared-environment Bubblewrap namespace with the case read-only, only its private project writable, the user home and runtime tree masked, privileged sockets absent, and only the resolved read-only DNS dependency restored; deterministic isolation tests exercise each boundary.
- Transfer candidate: apply the custody and authority threat model to every executable evidence producer, not only the primary agent, and bind validator outputs to the isolated project actually inspected.
- Limiting condition: a validator that performs only trusted non-executable byte inspection may need a narrower boundary, but that limitation must be mechanically enforced rather than inferred from intent.

### L-045 — A read-only prompt is not a write boundary

- Port status: unimplemented.
- Quality effect: an auditor can produce valuable findings yet still mutate the artifact it was asked only to inspect, contaminating independence and making later attribution ambiguous.
- Evidence: the migration instrument auditor was explicitly told not to edit any repository file but strengthened three Ledger entries and added three more while reporting its otherwise useful read-only validator counterexamples.
- Transfer candidate: give independent reviewers an OS-read-only source, an isolated writable scratch space, and a response-only output channel; verify source digests after review and classify unauthorized writes separately from semantic finding quality.
- Limiting condition: a reviewer intentionally authorized to repair artifacts is not read-only; its findings can still be independent only if candidate exposure and edit provenance remain explicit.

### L-046 — Remove only controller artifacts proven to be controller-owned

- Port status: unimplemented.
- Quality effect: runtime-created empty directories can create false scope failures and noisy diffs, while a universal cleanup rule can silently delete legitimate repository configuration or generated deliverables.
- Evidence: credential-safe task smokes produced empty `.codex/` and control-side `.agents/` directories before validation; deleting those only when empty preserved nonempty candidate-owned content. Later isolated reviewer executions produced nonempty `.git` runtime state without any reviewer `git init` command; reviewer workspaces reserve that path because their sole authorized deliverable is `judgment.md`. A subsequent treatment-path audit showed that recursively deleting the controller-injected `.agents` parent also deleted a candidate-authored `.agents/candidate-note.txt`, proving that path ancestry is not ownership.
- Transfer candidate: identify controller-created paths prospectively, remove them only under an independently checkable ownership predicate, and let nonempty or repository-owned content remain visible to evaluation.
- Limiting condition: when the repository contract declares the same path generated or authoritative, that contract controls cleanup and the controller should use a noncolliding state location instead.

### L-047 — Layer-specific evidence can survive an invalid overall attempt

- Port status: unimplemented.
- Quality effect: discarding every observation from a failed attempt loses useful infrastructure evidence, while counting the attempt as task-quality evidence overstates what it established.
- Evidence: the third live smoke round failed its overall validator only because of an empty controller-created `.codex/` directory, yet its retained shell trace directly established credential denial, repository hiding, socket hiding, environment clearing, DNS reachability, and skill separation before a fresh fully valid round confirmed the complete path.
- Transfer candidate: retain all attempts, attribute each observation to the layer it actually tests, and admit an attempt to comparative outcome analysis only when its predeclared completion contract passes.
- Limiting condition: a compromised custody or provenance boundary can invalidate even apparently local observations when the observation itself could have been fabricated or contaminated.

### L-048 — Evaluation identity must cover every executable input

- Port status: unimplemented.
- Quality effect: hashing nominal source while excluding executable caches, generated code, plugins, or loader inputs permits behavior to change without changing the recorded condition identity.
- Evidence: an independent harness audit generated different Python bytecode, restored the source bytes and timestamp, and observed `digest_unchanged=True` while import executed the altered cached behavior; the campaign harness and case digests had excluded `__pycache__` and therefore could not bind what ran. A later campaign-wide scan also found one pre-exposure `.pyc` inside the supposedly source-only immutable baseline snapshot, forcing cache removal and a new mode-aware baseline identity before any baseline round. During the unsafe-Rust re-audit, a nominally read-only reviewer import created `common.cpython-314.pyc` in the mutable harness and the executable-cache gate correctly rejected all four admissions until the exact cache was removed and reviewer commands were constrained to `python3 -B`.
- Transfer candidate: reject unexpected executable caches and generated inputs at every custody boundary, direct unavoidable caches to disposable controller-owned storage, and regression-test identity with a behavior-changing cache rather than a presence-only fixture.
- Limiting condition: a runtime configured to ignore all caches and generated inputs can establish the same property through executable configuration evidence, but exclusion from a digest alone is not evidence that an input is unreachable.

### L-049 — A boundary test needs a controller-owned observation

- Port status: unimplemented.
- Quality effect: asking the evaluated agent to report whether a secret, path, socket, or namespace was reachable allows hardcoded expected claims to pass after the actual isolation boundary regresses.
- Evidence: the live boundary smoke validator trusted candidate-authored `probe.json` booleans; replacing execution with the expected booleans would pass, even though the retained executor transcript happened to contain credible point-in-time shell observations.
- Transfer candidate: observe the boundary through a fixed controller instrument or authenticated structured transcript, compare the candidate report against that independent observation, and include a hardcoded-report adversary that must fail.
- Limiting condition: a candidate-produced attestation can be authoritative only when a separate trusted mechanism binds it to the exact execution and prevents candidate fabrication.

### L-050 — Blinded publication must consume finalized results

- Port status: unimplemented.
- Quality effect: copying a live artifact tree into a blinded review view can publish partial work, post-finalization mutations, or a run that never satisfied its completion contract while preserving a misleadingly strong custody record for the copy itself.
- Evidence: the split-testing helper strongly hashes what it copies but does not consult campaign `result.json`, claims, completion state, artifact digest, or record-evidence bindings before anonymization.
- Transfer candidate: put a harness-owned admission wrapper before anonymization, revalidate every terminal record and live artifact digest, enforce size limits, and refuse the entire publication when any assignment is partial, failed, unclaimed, mutated, or otherwise inadmissible.
- Limiting condition: a transactional content-addressed result store may make finalization and publication one operation; a manual operator recheck is not an equivalent durable gate.

### L-051 — Evidence retention and runtime cleanup are separate obligations

- Port status: unimplemented.
- Quality effect: deleting failed attempts erases diagnostic evidence, but retaining controller credentials, mount placeholders, injected treatments, validation copies, or Git scaffolding contaminates later inspection and can leak operational state.
- Evidence: eight retained smoke claims had only five terminal results, and failed attempts retained controller-created `codex-home`, `.agents`, `.git`, `.codex`, and validation state because exceptions bypassed late cleanup. A later post-run validation probe left both a completed `result.json` and an `infrastructure_failure` `failure.json` for one identity, making terminal state ambiguous.
- Transfer candidate: write a distinct atomic terminal infrastructure-failure record for every claimed attempt, retain bounded candidate output and logs, and remove prospectively identified controller-owned runtime state in `finally` without erasing candidate-owned evidence.
- Limiting condition: forensic preservation may intentionally retain runtime state in a separately access-controlled evidence store; it must not remain mixed with reusable trial inputs or reviewer artifacts.

### L-052 — Output budgets must cover disk evidence, not only process streams

- Port status: unimplemented.
- Quality effect: bounded stdout and stderr do not prevent a candidate from exhausting storage or reviewer context through huge project trees, individual files, binary diffs, or anonymized copies.
- Evidence: a deterministic audit probe produced a 2,400,130-byte patch despite the harness's one-megabyte process-capture limit, and neither artifact copying nor blinded publication enforced file-count, largest-file, or total-byte ceilings.
- Transfer candidate: predeclare independent limits for project bytes, file count, largest file, diff bytes, and published-view bytes; measure and record each dimension before finalization and again before publication; classify overflow as infrastructure-invalid evidence.
- Limiting condition: genuinely large-artifact tasks need an explicit case-specific budget or external object-store interface, not an implicit unlimited local tree.

### L-053 — Executable validation should be offline by default

- Port status: unimplemented.
- Quality effect: candidate code executed during validation can use outbound services, ambient localhost, changing remote state, or cross-run communication as an oracle even when the coding agent itself was isolated.
- Evidence: a validator namespace probe showed the validator and host shared the same network namespace and exposed `/proc/net`; candidate tests and build hooks therefore retained host-network reachability.
- Transfer candidate: unshare validator networking by default, regression-test namespace separation and failed outbound access, and supply network behavior only through a bounded controller-owned fixture whose identity is part of the case.
- Limiting condition: a task whose contract inherently requires a real external service needs an explicit recorded capability and reproducibility strategy; it should not inherit ambient networking accidentally.

### L-054 — Publication integrity is an end-to-end chain

- Port status: unimplemented.
- Quality effect: individually atomic result files, artifact hashes, anonymized copies, and private mappings can still describe different source states when no single admission path binds them together.
- Evidence: the harness binds completed artifacts internally and the split helper binds copied views internally, but the independent audit found no enforced transition connecting the finalized harness record to the helper's live source snapshot.
- Transfer candidate: make one verifiable chain bind claim, immutable design, terminal result, source artifact digest, admission decision, anonymized copy, reviewer judgment, and reveal mapping; every transition must fail closed on identity drift.
- Limiting condition: the chain may span several transactional systems, but each handoff needs an authenticated content identity and explicit terminal state rather than filename or timing assumptions.

### L-055 — Component correctness does not bind a consumer to the component

- Port status: unimplemented.
- Quality effect: testing a library mechanism and its CLI output separately can accept a consumer that prints plausible captured output without invoking the mechanism at all.
- Evidence: both performance diagnostic validators accepted replacement CLIs containing static oracle JSON even though independent model probes and the original library implementation remained correct.
- Transfer candidate: vary a controller-owned input or dependency across the public consumer boundary and require the consumer's observed result to track the independently predicted mechanism result; include a static-output substitution adversary.
- Limiting condition: a truly generated static artifact can be correct when generation is the declared interface, but then provenance and regeneration—not runtime invocation—become the mechanism that must be bound.

### L-056 — Finite examples cannot prove an unbounded contract without relations

- Port status: unimplemented.
- Quality effect: a validator whose largest numeric value, string, fragment, or collection size is visible through a finite matrix rewards implementations that work only up to that boundary while claiming support for every valid input.
- Evidence: accepted mutations capped offered load at 1000, truncated arrivals at 16, capped revisions at 32-bit maximum, capped retries at 8, handled journal tails only through 100 bytes, and normalized Unicode names only through 20 characters—the exact observed validation maxima. After validators moved their ranges, a fresh audit again passed caps at 8,191 work items, 5,003 requests, `10^40` offered load, 19 placements, 1,007 arrivals, and four domains, proving that larger finite examples alone only relocate the overclaim. Debugging validators later passed repairs restricted to known ID prefixes, hook-enabled execution, or payloads below 500 bytes, showing that finite shape families are as exploitable as numeric maxima.
- Transfer candidate: combine independently generated values beyond visible examples with scale, composition, decomposition, permutation, and other contract-derived metamorphic relations so arbitrary caps change an observable relation; bound resource use without silently bounding the published domain.
- Limiting condition: exhaustive enumeration is valid for a genuinely finite declared domain, and an intentional operational bound should be stated and enforced as part of the contract rather than hidden in tests.

### L-057 — A candidate-controlled discriminator can reward detecting the evaluator

- Port status: unimplemented.
- Quality effect: mutating production behavior and accepting any candidate-test failure as regression evidence lets a meaningless test fail on the validator's monkeypatch fingerprint instead of the bug's contract.
- Evidence: all four TDD validators accepted oracle production code after the meaningful test was replaced by an assertion on the public function's `__name__`; the validator monkeypatch changed that name, so the repository suite failed only under evaluation and was misclassified as discriminating. Four performance validators later accepted trivial tests that recognized injected names such as `validatorCandidateMeasure`, `validatorCandidateRun`, or `validatorCandidatePlan` and failed only under the predictable evaluator mutation.
- Transfer candidate: keep the counterfactual and observation channel outside candidate control, compare exact contract-relevant outcomes, vary mutation mechanisms, and include evaluator-fingerprint tests as adversaries; a nonzero candidate-suite exit is not sufficient evidence.
- Limiting condition: candidate tests can remain evidence when the controller independently attributes their failure to the intended behavioral delta and rules out unrelated collection, import, fixture, and evaluator-detection failures.

### L-058 — Final state cannot establish temporal development order

- Port status: unimplemented.
- Quality effect: an excellent final implementation with tests does not prove that an authoritative test failed before production changed, so a final-state project alone cannot measure the central red–green process contribution of TDD guidance.
- Evidence: all four TDD projects can inspect only submitted code and tests after the task; their tasks specify settled behavior and regression coverage but retain no independently controlled pre-change test event.
- Transfer candidate: when process order is the treatment claim, use an instrumented development loop or staged task with controller-owned checkpoints that records the pre-fix failing test, the minimal transition, and the post-fix pass; report final quality and temporal compliance as separate outcomes.
- Limiting condition: if the skill is evaluated only for final regression quality rather than process adherence, final-state evidence is sufficient but the narrower claim must be explicit.

### L-059 — Deterministic reports must exclude incidental timing

- Port status: unimplemented.
- Quality effect: embedding tool-reported durations, random temp paths, timestamps, or scheduler noise in validator evidence makes unchanged cases produce different records and weakens byte-level custody and rerun comparison.
- Evidence: repeated performance diagnostic validators produced different JSON hashes solely because captured `go test` duration varied between values such as 0.006 and 0.007 seconds.
- Transfer candidate: normalize evidence to stable exit status, selected semantic diagnostics, and content hashes; keep timing only when it is the measured outcome and then use a predeclared statistical record rather than incidental command prose.
- Limiting condition: performance experiments inherently observe time, but their deterministic metadata and stochastic measurements should be separated so provenance remains stable while distributions remain analyzable.

### L-060 — Hidden checks do not replace repository-owned regression protection

- Port status: unimplemented.
- Quality effect: a submission can satisfy an external evaluator while deleting the focused tests required to protect the repository after that evaluator disappears.
- Evidence: all four refactoring validators passed after their oracle's focused seam, ownership, hierarchy, or authority regression tests were removed, even though controller-owned hidden behavior and structure checks still passed.
- Transfer candidate: execute the submitted regression test and independently mutate the governed behavior or structure so that test must fail for the intended reason; evaluate external correctness and durable repository protection as separate properties.
- Limiting condition: a repository may intentionally centralize tests in an external conformance suite, but that authority and its continued availability must be part of the declared maintenance contract rather than inferred from a one-off validator.

### L-061 — A closed vocabulary is not semantic authority

- Port status: unimplemented.
- Quality effect: AST or text checks that recognize selected spellings can report one authority while ordinary aliases, `getattr`, wrappers, delegated callables, comparisons, or tables implement a second reachable authority with identical semantics.
- Evidence: refactoring validators missed duplicate configuration parsing and NaN classification expressed through ordinary `getattr` calls while continuing to report a single extracted authority.
- Transfer candidate: prefer controller-owned behavioral seams, call-count/decision instrumentation, mutation testing, or typed semantic analysis over enumerating syntax; maintain an equivalent-expression adversary family whenever syntax inspection remains necessary.
- Limiting condition: a deliberately restricted DSL or lint contract may define syntax itself as the governed property, in which case the vocabulary must be complete and parser-backed rather than presented as proof of runtime semantics.

### L-062 — Candidate-emitted observations cannot authenticate their causes

- Port status: unimplemented.
- Quality effect: realistic event names, traces, counters, or reports can be fabricated while the real declaration, runtime path, or mechanism remains broken.
- Evidence: the plugin-path debugging validator accepted wrong lowercase deployment declarations and a deleted regression after the candidate-owned matrix emitted healthy path and load events; other debugging cases reported causal reconciliation true under fabricated healthy events even when controller probes exposed the restored core defect.
- Transfer candidate: derive consequential observations from controller-owned inputs and direct artifact/runtime inspection, bind them to the exact scenario, and treat candidate telemetry only as a claim to corroborate; include fabricated-event adversaries.
- Limiting condition: candidate telemetry can become authoritative when cryptographically or transactionally emitted by a trusted instrument the candidate cannot alter and bound to the execution under review.

### L-063 — Answer-bearing diagnostics erase treatment contrast

- Port status: unimplemented.
- Quality effect: a debugging evaluation that names the failing boundary, ownership edge, divergent field, or exact repair route gives the control condition the central causal contribution the debugging skill is meant to add.
- Evidence: candidate-visible incident bundles named finalization, transport identity, exact path/case disagreement, or broker subscription ownership, making otherwise complex projects primarily implementation exercises rather than tests of systematic diagnosis. Performance diagnostic prompts similarly prescribed the sweep, causal controls, accounting ledger, no-stall comparison, selection rule, reproducibility, and focused tests, leaving little distinctive experimental method for the treatment to contribute.
- Transfer candidate: expose raw symptoms, chronology, environment contrasts, and reproducible observations while withholding the causal boundary; keep decisive controller probes hidden and judge diagnosis, repair, and verification as distinct outcomes.
- Limiting condition: when the user's real task already supplies a settled diagnosis, implementation quality is the correct target and no incremental diagnostic claim should be made.

### L-064 — Every reported outcome dimension needs its own valid evidence

- Port status: unimplemented.
- Quality effect: an aggregate failure can hide a false-positive sub-dimension, corrupting later vector analysis even when the overall pass/fail result is conservative.
- Evidence: three debugging validators correctly failed fabricated-probe/core-defect submissions overall because hidden mechanism tests failed, yet their separate `causal-report-reconciles` dimension still reported true.
- Transfer candidate: define an independent observable for each preserved outcome dimension, force that dimension false under a targeted counterexample, and never infer one dimension from aggregate status or another dimension's evidence.
- Limiting condition: tightly coupled properties may share raw observations, but the implication from those observations to each reported conclusion must still be separately valid.

### L-065 — Controller runtime preconditions must not leak into task evidence

- Port status: unimplemented.
- Quality effect: an evaluator or reviewer can fail before doing any semantic work because its host runtime expects repository trust, writable aliases, credentials, or another controller concern that the reviewed artifact neither owns nor should be asked to repair.
- Evidence: both first blinded reviewer attempts exited before a model turn because their intentionally non-Git private workspaces omitted Codex's explicit `--skip-git-repo-check` execution flag; terminal records and empty transcripts proved this was infrastructure rather than judgment quality.
- Transfer candidate: identify and satisfy host-runtime preconditions in the controller, expose only task-relevant state to the worker, and classify pre-turn failures as infrastructure with replacement identities rather than negative task evidence.
- Limiting condition: when repository trust itself is the behavior under test, it belongs in the task condition and must remain symmetric rather than being bypassed by controller configuration.

### L-066 — Audit isolation must not mutate the evidence it protects

- Port status: unimplemented.
- Quality effect: recursively changing permissions on finalized inputs can invalidate mode-aware identities, alter executable behavior, and make an otherwise independent audit consume a different artifact from the one admitted for review.
- Evidence: making the canonical harness and retained v9 smoke root read-only changed the harness digest from `22f53f60ea029639e9dd2f1989d3c474d92992477de0026a8ca566e981995397` to `84b65b95061f0205d1010866cca785839f9b79d7d8833e627e76241fa72f8d55`; the recursive operation also changed retained evidence modes, so the prior chain can no longer validate as current evidence.
- Transfer candidate: enforce reviewer immutability with a controller-owned copy, read-only bind mount, immutable snapshot, or filesystem policy whose application is outside the admitted tree; bind the audit to the preexisting identity and verify that identity both before and after review.
- Limiting condition: permission normalization may be legitimate before an artifact is finalized when the normalized modes are included in its declared identity; it is not a transparent isolation step after admission.

### L-067 — Tool names do not identify the executable under evaluation

- Port status: unimplemented.
- Quality effect: resolving a compiler, interpreter, build tool, or validator helper from ambient `PATH` can substitute an intercept, version manager, wrapper, or networked shim whose startup behavior and semantics dominate the measured task while being misattributed to candidate code.
- Evidence: the C pthread validator resolved `cc` to `/home/rashino/.local/share/dev-cache/intercepts/cc`; tracing showed that shim traversing a large shared cache until both seed and oracle hit a 25-second outer timeout, whereas the system compiler produced a seed failure in 0.18 seconds and an oracle pass in 0.59 seconds.
- Transfer candidate: resolve each executable to an explicit controller-owned identity, record its path and version or digest, pass configured tools through every consumer such as `make`, and classify unexpected wrapper startup as infrastructure; test with a hostile PATH-precedence shim.
- Limiting condition: a wrapper may itself be the declared toolchain interface, but then its identity, cache/network capabilities, startup budget, and reproducibility are part of the evaluation condition rather than ambient implementation detail.

### L-068 — Classifier-blocked reviewers produce no task evidence

- Port status: unimplemented.
- Quality effect: a read-only software reviewer can be stopped before analysis when adversarial-testing vocabulary resembles a restricted domain; counting that outcome against an artifact confounds policy-routing behavior with artifact quality and silently reduces independent coverage.
- Evidence: three local software-instrument or harness audits were blocked as possible cybersecurity risk before returning findings, including an audit limited to deterministic tests, content identities, temporary cleanup, process completion, and blinded review ordering.
- Transfer candidate: record pre-review classifier stops as infrastructure, preserve the exact requested scope, replace the reviewer identity, and rephrase around concrete software-quality properties without weakening the acceptance contract; require a completed independent report before claiming review coverage.
- Limiting condition: genuinely restricted work must remain stopped or follow its authorization path; rephrasing is appropriate only when the underlying task is plainly benign and unchanged.

### L-069 — Value equality is not exact type validation

- Port status: unimplemented.
- Quality effect: languages with coercive or overlapping equality can admit wire and control values from the wrong domain, such as booleans accepted as counters or floating-point values accepted as integer schema versions and offsets.
- Evidence: four migration validators accepted `2.0` as schema version `2`, `True` as write count or quantity `1`, and `4.0` or `152.0` as integer checkpoint and index offsets while producing the exact oracle report hashes.
- Transfer candidate: validate the exact declared primitive type before value or range checks, exercise adjacent coercible types at every serialization and CLI boundary, and keep parsing separate from domain validation so conversion cannot erase the original type error.
- Limiting condition: explicit coercion is valid when the public contract defines it; the accepted source forms and loss rules must then be tested as behavior rather than inherited from host-language equality.

### L-070 — Opaque identifiers must remain opaque and complete

- Port status: unimplemented.
- Quality effect: truncating, normalizing, stringifying, or globally reusing identifiers can merge distinct operations, tenants, currencies, cohorts, or retries while ordinary short examples continue to pass.
- Evidence: migration validators accepted identifiers truncated after eight or 64 characters, boolean IDs stringified as `"True"`, and one request ID reused across tenants so a later cohort overwrote an earlier accepted reservation and broke its retry.
- Transfer candidate: preserve identifier type and full byte or code-point sequence, test long shared prefixes with distinct suffixes, empty and non-string values, composition with every scoping key, and retry behavior before and after authority changes.
- Limiting condition: a declared canonicalization or bounded identifier format may transform input, but collision resistance, rejection rules, and scope must be part of the contract and verified at the canonical boundary.

### L-071 — Refusal is a state transition with a nonmutation postcondition

- Port status: unimplemented.
- Quality effect: checking only that an operation returned an error can accept an implementation that partially mutates routing, cohort, backend, pending, or authority state before refusing, leaving the system less safe than before the gate.
- Evidence: a failed canary preparation returned refusal while adding the tenant to `canary_tenants`; other migration gaps omitted durable pending intent or trusted incomplete synchronization scope despite apparently correct surface outcomes.
- Transfer candidate: snapshot every protected authority and data structure before each refused transition, compare complete state afterward, include injected partial-progress failures, and separately prove the adjacent allowed transition succeeds.
- Limiting condition: an operation may intentionally record an audit or retry marker on refusal, but that mutation must be declared, isolated from governed state, and included in the expected postcondition.

### L-072 — Target verification needs an authority independent of candidate readers

- Port status: unimplemented.
- Quality effect: asking candidate code to parse, checksum, summarize, and then validate its own target can turn internally consistent corruption into authoritative evidence, especially when expected digests are derived from the unchanged source instead of observed target bytes.
- Evidence: a checkpointed archive with a valid checksum but amount changed from `1200` to `9999` passed candidate `validate()`, matched source-derived evidence, and became target-authoritative because the validator never independently parsed the pack.
- Transfer candidate: have the controller independently decode and authenticate target bytes, derive count and digest from that observation, compare it with source semantics, and inject valid-but-wrong target data immediately before authority transition.
- Limiting condition: a separately trusted parser may be reused when its identity and independence are established; the candidate-controlled implementation under evaluation cannot authenticate itself by assertion.

### L-073 — Fault-injection interfaces need closed names and complete edges

- Port status: unimplemented.
- Quality effect: an unknown failure-point label that silently runs normally makes misspelled or stale tests look successful, while testing only selected interruption points leaves reachable partial states without a safe retry, rollback, or forward-recovery path.
- Evidence: multiple migration cases accepted unsupported failure labels, and the archive oracle could not recover from pending-before-pack or pack-before-operation-metadata states even though other interruption windows passed.
- Transfer candidate: enumerate accepted injection points through a discoverable interface, reject unknown names, map each point to one state-changing edge, and require a controller-observed terminal recovery outcome for every reachable edge.
- Limiting condition: probabilistic or schedule-driven fault injection need not expose a finite name set, but its realized edge and recovery evidence must be recorded so an untriggered fault cannot be mistaken for a passing test.

### L-074 — Distinct authority roles require an anti-alias invariant

- Port status: unimplemented.
- Quality effect: source/target, control/treatment, primary/shadow, or old/new roles can satisfy each local API while sharing one backing object, causing writes intended for observation or isolation to mutate the authoritative state.
- Evidence: the cohort-router oracle accepted the same backend object as both source and target; shadow traffic then produced a target reservation and target mutation despite the no-target-mutation contract.
- Transfer candidate: reject role aliasing at construction or prove the required invariant under shared backing state; test direct object identity plus distinct wrappers over the same storage, and bind role separation to the actual mutation boundary.
- Limiting condition: intentional shared storage is valid when the architecture defines isolation within that storage, but the isolating key, transaction, or namespace must be the tested authority rather than role names alone.

### L-075 — Isolation should expose an allowlist, not mask a guessed denylist

- Port status: unimplemented.
- Quality effect: binding the whole filesystem read-only and hiding selected paths leaves every unanticipated directory as a side channel for sibling conditions, campaign state, fixtures, caches, or reviewer mappings.
- Evidence: validator and reviewer sandboxes masked the user directory, `/tmp`, and `/run`, yet an independent validator read an unrelated controller sentinel from `/var/tmp` and passed on that ambient state while all 13 harness tests remained green.
- Transfer candidate: construct a minimal filesystem view from explicit runtime and task inputs, add negative sentinels in multiple unrelated roots, and treat any newly required path as an audited capability rather than extending a growing mask list.
- Limiting condition: a system whose purpose is whole-filesystem inspection necessarily needs broad visibility, but then condition isolation must come from a separate snapshot or namespace rather than selective hiding.

### L-076 — One attempt needs one authoritative terminal envelope

- Port status: unimplemented.
- Quality effect: separate success and failure markers can coexist after late validation, making retries, publication, and summaries choose among contradictory terminal truths based on filename order or implementation accident.
- Evidence: a controller-success result followed by failed post-run validation retained `result.json` with `completion_state: complete` and added `failure.json` with `completion_state: infrastructure_failure` for the same run identity. Later, an async-Rust publication claim created before anonymization had no terminal failure state: helper or filesystem failure left only the claim, and retry was rejected. A subsequent harness fixed publication but could still copy one blinded reviewer judgment, fail on the second, and leave neither a round completion nor a retry path. The admitted harness gives both publication and review their own content-bound claims, stages every judgment before publishing any, rolls back partial and temporary files on failure, writes a sole attempt-numbered failure artifact, and admits retry only when rollback and frozen publication, harness, helper, and reviewer-record identities match.
- Transfer candidate: model terminalization as one atomic compare-and-set over a single envelope, preserve superseded payloads only as content-bound diagnostics beneath that envelope, reject any legacy sibling markers during validation and skip decisions, give every durable claim an explicit failure transition plus retry or recovery contract, and fault-inject every multi-destination commit after each individual destination rather than testing only pre-commit failure.
- Limiting condition: append-only event stores may retain several state-transition events, but one reducer with an authenticated ordering rule must derive the sole current terminal state.

### L-077 — Experimental design commitments must survive every handoff

- Port status: unimplemented.
- Quality effect: randomization, counterbalancing, reviewer-order reversal, holdout separation, and condition assignment can be correct when created yet silently disappear during publication or review if later stages validate only artifact bytes.
- Evidence: round creation assigned opposite A/B orders to two semantic reviewers, but publication, review, reveal, and the 13-test suite never read `candidate_order`; presenting both reviewers the same order would therefore remain admissible.
- Transfer candidate: bind each design commitment into the admission record, revalidate it immediately before every consumer and before reveal, and include a mutation test that changes only the commitment while leaving candidate artifacts intact.
- Limiting condition: a commitment may intentionally be changed before exposure through a new randomized design identity; it must not drift under the original identity.

### L-078 — Validators must not invent an undeclared canonical representation

- Port status: unimplemented.
- Quality effect: a hidden check that requires one literal path, spelling, ordering, formatting, or implementation token can reject behaviorally equivalent solutions and turn a method-neutral task into an undisclosed conformance exercise.
- Evidence: a plugin-path validator rejected `./plugins/JsonExport.py` even though both declarations normalized to the same existing checked-in module and both environments loaded and executed it with strict malformed and absent rejection; only raw-string equality with `plugins/JsonExport.py` failed. A C mutation matrix also initially treated `memcpy` as wrong where the public extent invariant proves source and destination cannot overlap, and treated a stored discard-mode value as wrong even though queued work is cleared atomically and the value is then observationally irrelevant.
- Transfer candidate: derive acceptance from the public semantic contract, normalize representations at the declared boundary, and include at least one equivalent representation as a must-pass adversary alongside malformed and genuinely distinct must-fail cases.
- Limiting condition: canonical bytes or spelling may itself be the public contract for signatures, wire formats, reproducible manifests, or policy; in that case the canonical requirement must be explicit and consumer-validated.

### L-079 — Adversarial size tests must fail before expensive realization

- Port status: unimplemented.
- Quality effect: a validator that asks an invalid-size implementation to allocate or touch the claimed extent can turn a simple semantic rejection test into an unbounded memory or time sink, delaying every mutation and making denial of service indistinguishable from a hard case.
- Evidence: removing a 32-bit representability guard caused the fallible-buffer probe to request and initialize more than four GiB; the candidate validator consumed the entire 60-second outer budget instead of reporting the wrong status immediately.
- Transfer candidate: intercept resource acquisition at a small deterministic ceiling, record that acquisition was attempted, return a controlled failure, apply a short child-runtime bound, and treat timeout as explicit rejection evidence rather than letting the evaluation controller crash.
- Limiting condition: performance or capacity evaluations may intentionally realize large resources, but their budgets and isolation must be explicit and independent from ordinary semantic boundary tests.

### L-080 — Mutation operators need explicit anchor cardinality and path coverage

- Port status: unimplemented.
- Quality effect: a lexical mutation that assumes one occurrence may crash when equivalent logic is duplicated, while silently mutating only one occurrence can leave another execution path correct and produce a false conclusion about validator discrimination.
- Evidence: the frame-buffer oracle serializes the length in both growth and no-growth branches; a little-endian mutant expected one four-line anchor, found two, and aborted the 28-mutant campaign before producing dispositions.
- Transfer candidate: declare and assert the expected anchor count, state whether the defect is one-site or cross-path, mutate every intended semantic occurrence, compile before validation, and classify anchor drift as instrument infrastructure failure rather than mutant acceptance or rejection.
- Limiting condition: syntax-aware or generated mutation systems can identify semantic sites without literal anchors, but they still need a stable target identity and an explicit disposition when source evolution removes or multiplies that target.

### L-081 — Resource exhaustion is an infrastructure terminal, never a quality verdict

- Port status: unimplemented.
- Quality effect: collapsing quota exhaustion, unavailable models, or reviewer interruption into a failed treatment or a passed audit biases comparisons and can release unevaluated work merely because the evidence-producing path disappeared.
- Evidence: the fresh harness, performance, migration, and debugging reviewers all terminated with the same account-level usage-limit message before returning reports; none produced task-level findings despite their assigned artifacts remaining available.
- Transfer candidate: give infrastructure terminals a separate outcome class, retain immutable inputs and completed evidence, leave the affected quality gate pending, permit replacement identities after capacity returns, and exclude interrupted attempts from treatment-effect interpretation while still reporting resource cost and delay.
- Limiting condition: a candidate that itself exhausts a declared task budget is a task outcome when the controller and budget remain healthy; the distinction depends on which authority exhausted which resource.

### L-082 — Disposable outputs and recoverable experiment definitions need different lifetimes

- Port status: unimplemented.
- Quality effect: placing the only mutation controller, case generator, or trial manifest in a temporary directory makes an unfinished evaluation irreproducible when ordinary cleanup, session changes, or another worker removes it, even if every retained result remains intact.
- Evidence: the active 28-variant C mutation controller disappeared from `/tmp` between verification turns while its instrument inputs and prior output remained; the matrix could not be rerun until the controller definition was reconstructed.
- Transfer candidate: keep controller source and immutable experiment definitions in ignored campaign state with identity hashes for the duration of in-flight work, create candidate projects only in automatically cleaned temporary roots, and delete the controller when its bound final report makes it redundant.
- Limiting condition: a controller generated deterministically from a retained manifest may itself remain disposable when regeneration is executable, version-bound, and tested.

### L-083 — Failure handlers must be executable evidence paths

- Port status: unimplemented.
- Quality effect: a validator or production component can implement the intended happy path yet lose all structured diagnostics when its exception handler references an unbound name, assumes fields that are absent precisely on failure, or raises while formatting the original error.
- Evidence: plugin-path validation correctly encountered a case-mismatched missing declaration, then its broad recovery clause referenced unbound `JSONDecodeError`; the validator emitted a traceback instead of its required compact JSON failure report.
- Transfer candidate: execute every declared recovery branch with representative exceptions, keep handler dependencies explicitly qualified or imported, make fallback serialization minimal and total, and assert that the original failure becomes one bounded terminal record with a nonzero exit status.
- Limiting condition: truly unrecoverable process failures may bypass application-level reporting, but the controller must still classify their absent terminal envelope as infrastructure rather than silently inferring task failure.

### L-084 — Temporal method claims require controller-owned checkpoints

- Port status: unimplemented.
- Quality effect: a polished final repository cannot prove whether a regression test failed before production changed, so inferring TDD sequence from the final patch rewards unverifiable narrative and collapses process quality into artifact quality.
- Evidence: the four TDD validators could prove final behavior and test discrimination but had no observation from the earlier red state; a one-shot read-only controller checkpoint now records unchanged production, a failing repository suite, the test-tree identity, and whether tests changed before the implementation transition.
- Transfer candidate: report process order and final artifact quality as separate outcome dimensions, authenticate each checkpoint from execution records, bind checkpoint test identity to final regression evidence when the test was newly authored, and make absence or misuse visible rather than reconstructing chronology from prose.
- Limiting condition: when a suitable failing regression already exists, unchanged-production failure may establish red without a new test-tree change, and later additive tests need not invalidate that evidence.

### L-085 — Regression discrimination must not depend on candidate-recognizable evaluator mutation

- Port status: unimplemented.
- Quality effect: monkeypatching the submitted implementation through `sitecustomize`, function names, or private wrappers lets submitted tests detect the evaluator instead of detecting the contract violation, producing a perfect mutation result with no durable repository protection.
- Evidence: all four original TDD instruments used candidate-importing `sitecustomize` mutations and accepted evaluator-discriminator tests; repaired validators copy the exact submitted tests into controller-owned workspaces and run them against independent reference, original, and adjacent violating public implementations.
- Transfer candidate: keep the submitted test bytes fixed, vary only controller-owned implementations behind the same public interface, require a valid reference to pass, require declared violating counterfactuals to fail, and include evaluator-fingerprint adversaries in the mutation matrix.
- Limiting condition: runtime interception is valid when interception itself is the public boundary under test and candidate tests cannot observe or branch on its identity; otherwise independent implementations provide stronger evidence.

### L-086 — Existing red tests and newly authored red tests have different custody contracts

- Port status: unimplemented.
- Quality effect: requiring every TDD trial to change tests before the first red run encourages pointless churn when a focused regression already fails, while allowing test drift after a newly authored red checkpoint can sever the evidence from the final durable test.
- Evidence: `retry-attempt-limit` begins with a focused failing attempt-count test, whereas the conflict, journal, and Unicode cases begin green and require a new or corrected regression; the former accepts later additive test improvement, while the latter binds the red checkpoint's test-tree digest to the final submitted tests.
- Transfer candidate: classify the pre-change test state before defining the temporal gate, preserve a suitable existing regression when present, and require identity continuity only where it is needed to connect a newly authored red test to the final artifact.
- Limiting condition: a test may legitimately be refined after an initial meaningful red; if that route is allowed, retain controller-owned semantic evidence that the original and final tests target the same missing outcome rather than relying on byte identity.

### L-087 — Sample ceilings need explicit cap counterfactuals

- Port status: unimplemented.
- Quality effect: hidden checks that exercise only revisions up to 32 bits, retry limits up to eight, fragments below 100 bytes, or names below 20 characters admit implementations that hard-code the observed test ceiling while appearing general.
- Evidence: the first TDD audit identified exactly those four accepted ceilings; repaired checks added large integer revisions, retry limits above eight, multi-kilobyte crash tails, long shared-prefix Unicode names, and controller-owned cap mutants that the submitted regression suites must reject.
- Transfer candidate: for every sampled numeric or size domain, state any real product bound or add a just-outside-sample and substantially wider case, pair it with a cap mutant, and keep resource realization bounded so generality checks cannot become denial-of-service paths.
- Limiting condition: a documented operational maximum is a legitimate contract; test its boundary and rejection behavior instead of treating all finite limits as defects.

### L-088 — Behavioral equivalence includes evaluation strategy and failure behavior

- Port status: unimplemented.
- Quality effect: expressions that return the same values on ordinary inputs can differ materially in short-circuiting, side effects, exceptions, allocation, or ordering, so a must-pass alternative can reveal that the validator—or the alternative itself—misclassified equivalence.
- Evidence: a proposed conflict-classifier alternative replaced chained `and` with `all((...))`; tuple construction eagerly evaluated `revision > 0` for string revisions and raised `TypeError`, while the original short-circuited after the type guard and returned the declared conflict outcome. The must-pass matrix rejected the alternative.
- Transfer candidate: define equivalence over the complete observable contract, including exceptions and effect order, exercise invalid and boundary inputs against every must-pass alternative, and preserve lazy evaluation when later predicates are safe only after earlier guards.
- Limiting condition: eager evaluation is interchangeable when every operand is total and effect-free over the declared domain; that property must be established rather than assumed from truth-table similarity.

### L-089 — Freeze semantics must be exercised after the freeze

- Port status: unimplemented.
- Quality effect: an instrument can pass immediately before freezing yet become unable to validate afterward when copied read-only modes block private patching, cleanup, compilation, or fixture generation; a pre-freeze pass therefore does not prove the admitted artifact is executable.
- Evidence: all four TDD cases passed during `--freeze`, which validates before removing write bits, then every post-freeze oracle rerun failed because controller-owned counterfactual workspaces inherited 0444 seed modes and could not apply the reference patch. The first Go freeze later reproduced the same class one layer deeper: each validator copied its frozen seed into a submitted-test counterfactual and failed when overwriting the retained read-only test file.
- Transfer candidate: after final permissions and identity are applied, rerun seed/oracle polarity from unrelated working directories, make only disposable copies owner-writable inside validators, and require the frozen identity to remain unchanged before and after execution.
- Limiting condition: a validator that performs no writes to copied inputs may safely preserve frozen modes, but its post-freeze execution must still prove that assumption.

### L-090 — Counterfactuals should terminate through the contract boundary

- Port status: unimplemented.
- Quality effect: a mutant that removes an event another test waits on can consume the whole outer timeout and prevent the validator from emitting a disposition, turning an easy semantic defect into infrastructure failure and slowing every repeated matrix.
- Evidence: the refactoring `drop-callbacks` mutant made the controller-owned lifecycle test block forever on `callbackStarted`; the validator exited without JSON only after its timeout, so no mutant rejection was admissible.
- Transfer candidate: design wrong-but-terminating counterfactuals that preserve progress signals while corrupting the asserted value or order, impose short per-probe deadlines with structured timeout dispositions, and reserve hangs for dedicated liveness tests with explicit controller handling.
- Limiting condition: when termination itself is the governed property, a timeout is valid negative evidence only if the controller captures it as a bounded task outcome rather than crashing the evaluation path.

### L-091 — Runtime call-stack intersection can evidence coherent authority without a syntax ontology

- Port status: unimplemented.
- Quality effect: enumerating parser, reflection, or numeric-classification spellings misses ordinary aliases and wrappers, while requiring one named function or file rejects valid restructurings; observing the real operations and their production stacks can locate the common boundary and expose duplicate authorities.
- Evidence: semantic probes observed config open, JSON parse, plugin import, numeric classification, and consumer-policy events. `getattr`-based implementations inside the extracted authority passed, but behavior-neutral duplicate `getattr` paths in the command or wire consumer removed the non-command common stack boundary and failed only the ownership dimension.
- Transfer candidate: instrument stable runtime operations at controller-owned seams, collect every relevant production stack across independent consumers, identify the deepest resolvable common callable, invoke it directly, and separately observe consumer-only operations; retain must-pass alias/wrapper alternatives and must-fail duplicate-authority variants.
- Limiting condition: profiling and audit events are runtime-specific and may omit custom implementations or optimized calls; use them only where the declared environment exposes stable events, combine them with behavioral contracts, and do not promote a missing event into proof that an operation is absent.

### L-092 — A strong failure guarantee spans every reachable failure source

- Port status: unimplemented.
- Quality effect: rolling back only the named domain exception can make focused tests pass while allocation, copying, conversion, callback, or commit failure still leaves earlier mutations visible.
- Evidence: a C++ ledger mutant appended directly and resized back only for `std::runtime_error`; decoder-failure regressions passed, but controller-owned `std::bad_alloc` injection exposed partially appended state. Two-stage implementations that completed all fallible work in private state before swap passed.
- Transfer candidate: enumerate the operations that may fail before claiming a strong guarantee, inject representative failures at each reachable transition, compare exact pre/post state and future usability, and prefer private staging plus one non-failing commit when the contract requires all-or-nothing behavior.
- Limiting condition: a repository may promise only a basic or explicitly partial-success guarantee; preserve and test that declared state instead of imposing rollback universally.

### L-093 — Cancellation request and terminal completion are different lifecycle events

- Port status: unimplemented.
- Quality effect: destroying captured or observed state after requesting cancellation can race work that was already admitted or started, causing post-close callbacks, use-after-free, lost outcomes, or unloaded-code execution.
- Evidence: the C++ `cancel-without-wait` mutant requested cancellation for every scheduler job but returned before a synchronized blocked callback was released; the repaired cases required a terminal `wait` for every admitted job, rejected later submissions, and proved no callback occurred after close returned.
- Transfer candidate: model admission, cancellation request, callback/effect completion, outcome observation, and join as separate events; bind destruction and unload to the owned terminal boundary, including partial startup and error paths.
- Limiting condition: a scheduler may define successful cancellation as a synchronous terminal operation; rely on that only when the selected runtime contract explicitly guarantees it and the integration test observes the same boundary.

### L-094 — Source genericity and legacy binary compatibility need different consumers

- Port status: unimplemented.
- Quality effect: a fresh source test can pass while old objects lose required symbols, and a precompiled compatibility test can pass while a supposedly generic template supports only a finite fixture list.
- Evidence: the C++ template instrument links an immutable old object against candidate `int` and `double` symbols and separately compiles an independent user-defined `Revision` type. A size-capped generic implementation preserved the legacy consumer and submitted small fixture but failed the independent source consumer; both header-inline and included-`.tpp` authorities passed.
- Transfer candidate: test promised binary surfaces with unchanged prebuilt consumers and symbol evidence, test source extensibility with fresh independently chosen types or implementations, and include a finite-registry/cap counterfactual without requiring one template layout.
- Limiting condition: a closed supported type set may intentionally use explicit instantiation; in that case publish and test that finite contract rather than claiming open genericity.

### L-095 — Validator feature flags carry executable prerequisites

- Port status: unimplemented.
- Quality effect: enabling a stronger check without its runtime prerequisites can make every valid candidate fail for infrastructure reasons, while the resulting command-line error can look like candidate incompatibility if the controller does not classify it separately.
- Evidence: the Go fan-out validator set `CGO_ENABLED=0` for isolation while invoking `go test -race`; the selected Go toolchain correctly rejected every race-enabled probe because its race runtime requires cgo on Linux, including the valid oracle.
- Transfer candidate: resolve and probe the prerequisite closure of every validation mode before freezing—compiler, linker, cgo, sanitizer runtime, target support, privileges, and external services—then bind that environment into the instrument identity and classify prerequisite loss as infrastructure failure.
- Limiting condition: prerequisites vary by selected toolchain and target; do not generalize Linux cgo requirements into a universal property of all race detectors or platforms.

### L-096 — Reference patches should be derived from complete desired artifacts

- Port status: unimplemented.
- Quality effect: hand-maintained unified-diff hunk counts and partial deletion ranges drift easily, making the private reference solution fail before semantic validation and wasting evaluation cycles on malformed infrastructure.
- Evidence: the first bounded-fan-out oracle patch omitted the tail of the replaced function and retained stale hunk counts after a Go-version correction; `git apply` rejected it as corrupt. A mechanically generated diff between the complete seed and desired files applied cleanly.
- Transfer candidate: author and format complete desired artifacts, generate the patch mechanically, prove it applies to the exact seed and reconstructs byte-identical desired files, then run the validator before assigning or freezing an identity.
- Limiting condition: a tiny reviewed patch may be authored directly, but application, reconstruction, and seed/oracle polarity remain mandatory evidence.

### L-097 — The declared language version governs syntax even under a newer toolchain

- Port status: unimplemented.
- Quality effect: an agent running a recent compiler can accidentally introduce syntax unavailable under the module or package's declared language version, creating a forward-toolchain-only solution while appearing locally modern and correct.
- Evidence: the first Go fan-out oracle used integer `range`, a language feature newer than the retained `go 1.20` directive; the construct was removed before oracle admission even though the installed toolchain itself was Go 1.27.
- Transfer candidate: treat the declared language/edition/source level as the syntax authority, compile through that mode with the newest supported toolchain and oldest supported mode where feasible, and include a version-gated syntax counterfactual in compatibility-sensitive evaluations.
- Limiting condition: a task may explicitly raise the language version; then migration compatibility and downstream tool support become part of the change rather than reasons to retain old syntax.

### L-098 — Concurrency tests must assign roles by observed admission, not intended input order

- Port status: unimplemented.
- Quality effect: a test that assumes a particular input reaches a semaphore, worker, callback, or failure point first can hang or pass according to scheduler choice, especially when the counterfactual intentionally changes admission structure.
- Evidence: the bounded-fan-out submitted test made input `1` the failing worker and input `2` the cleanup worker. The correct worker pool consumed queued inputs predictably, but the unbounded seed launched every goroutine and did not guarantee which values acquired the first two semaphore slots; when input `1` was not admitted, the test waited forever for a failure that could not occur.
- Transfer candidate: assign failure, blocking, and cleanup roles from controller-observed admission ordinals or explicit handshakes; make input identity data rather than schedule authority; bound every negative wait and rerun the counterfactual repeatedly under race/scheduler variation before freeze.
- Limiting condition: ordering by input is valid when the public contract explicitly guarantees FIFO admission and the test observes that same boundary; goroutine creation order alone is not such a guarantee.

### L-099 — Production correctness and regression custody are separate outcomes

- Port status: unimplemented.
- Quality effect: collapsing a behaviorally correct repair with inadequate submitted tests into one generic failure hides whether the agent misunderstood runtime semantics or merely failed to leave durable repository protection; passing hidden tests alone can likewise overstate task completion.
- Evidence: three non-timeout Go trial artifacts passed every controller-owned production, compatibility, and hygiene check but failed only when their exact submitted tests were run against the original defect. They were correctly nonpassing under tasks that explicitly required discriminating regressions, yet their production behavior evidence remains distinct.
- Transfer candidate: report production behavior, contract preservation, submitted-test discrimination, and process/resource completion as separate dimensions; require all declared dimensions for task success while preserving layer-specific evidence for diagnosis and skill revision.
- Limiting condition: when a task does not require repository-owned regression changes, submitted-test custody is not an implicit obligation; hidden or external verification may be the appropriate durable authority.

### L-100 — State queries need bounded projections

- Port status: unimplemented.
- Quality effect: a status command that emits every run, metadata field, path, and reviewer assignment forces the caller to consume or truncate large context merely to learn one state value, increasing latency and hiding the requested signal.
- Evidence: querying whether two published Go rounds were anonymized emitted roughly sixteen thousand tokens of assignments and run metadata; the output was truncated even though only `state: anonymized` and reviewer-order commitments were needed.
- Transfer candidate: provide compact default status plus explicit `--fields`, `--summary-only`, pagination, and separate content retrieval; make the compact projection identity-bound to the same canonical state rather than a second drifting source.
- Limiting condition: publication, audit, or export commands may intentionally return complete bounded records; the problem is unfiltered output on a routine state query, not comprehensive evidence itself.

### L-101 — The initiating terminal condition must survive cleanup fallout

- Port status: unimplemented.
- Quality effect: terminating a resource after timeout, cancellation, overflow, or protocol failure can trigger secondary broken-pipe, closed-stream, task-cancellation, or join errors; returning whichever completion is observed first can erase the actionable public failure and make behavior scheduler-dependent.
- Evidence: the first Java process-runner draft killed the child as soon as a drainer crossed its per-stream bound, after which the sibling pipe closed and surfaced `IOException: Stream closed`; naive future collection could return that cleanup consequence instead of the declared `OutputLimitException`. The admitted oracle selects the initiating limit failure as primary and retains every distinct drain or cleanup failure as suppressed evidence, and the hidden overflow fixture requires the typed limit outcome after forced termination. Async-Rust semantic reviewers independently found that several machine-green timeout repairs discarded a later `JoinError`; the held-out precedence fixture now forces a blocking worker to fail during cooperative stop and requires the API to retain both the initiating timeout and terminal join failure while releasing capacity.
- Transfer candidate: define precedence among simultaneous terminal causes at the public boundary, collect all owned outcomes before returning, preserve non-primary failures through causes or suppression, and test the initiating failure while deliberately provoking cleanup fallout.
- Limiting condition: some APIs intentionally expose an unordered aggregate or only one opaque terminal status; do not invent precedence where the contract does not distinguish causes, but still prevent cleanup artifacts from replacing a promised typed outcome.

### L-102 — A seeded defect must remain valid outside the governed dimension

- Port status: unimplemented.
- Quality effect: when an intentionally broken baseline also fails to compile, start, parse, or satisfy unrelated public contracts, candidate work and evaluator rejection can target the accidental defect instead of the behavior the skill is meant to influence.
- Evidence: the first Java outcome-collector seed encoded the intended fail-fast loss but also assigned a wildcard-captured stream result to an incompatible generic list, so every validator layer failed at `javac` before asynchronous semantics ran. After repairing only the generic accumulation, the seed compiled and passed its basic public test, failed the hidden collect-all behavior, and the unchanged oracle passed all checks.
- Transfer candidate: admit seeds through build, public baseline, API, environment, and hygiene checks before preserving the intended hidden failure; require each must-fail variant to differ from an admitted artifact only in the named governed dimension.
- Limiting condition: compilation or startup may itself be the defect under study; in that case it is the governed dimension and the task, rubric, and validator should identify it explicitly rather than presenting a runtime repair.

### L-103 — Interruption may propagate only after owned cleanup reaches its declared boundary

- Port status: unimplemented.
- Quality effect: killing a child and calling `Future.cancel`, `shutdownNow`, or an equivalent interruption API can still leave admitted cleanup work executing after the public call throws, so teardown races survive under the appearance of correct interruption propagation.
- Evidence: the first Java process-runner oracle reaped its child, canceled three futures, called `shutdownNow`, restored interrupt status, and rethrew `InterruptedException`, yet two of ten sandbox stress sequences observed a non-daemon drainer alive after return. The repaired path awaits executor termination uninterruptibly, suppresses a bounded cleanup failure onto the original interruption, and passed ten of ten repetitions plus the final matrix and post-freeze checks.
- Transfer candidate: on every interruption path, separate cancellation request, resource termination, admitted-work join, cleanup-failure observation, interrupt restoration, and propagation; assert physical terminal state after the call, not only the exception type or cancellation flag.
- Limiting condition: a boundary that explicitly transfers cleanup ownership to another durable supervisor may propagate earlier, but the transfer and its observable terminal contract must be real rather than implied by a wrapper state.

### L-104 — Runtime dependency closure includes symlink targets outside mounted roots

- Port status: unimplemented.
- Quality effect: exposing an executable tree in an isolated environment does not make the runtime complete when files under that tree resolve into an unmounted configuration root; ordinary library operations can fail while compiler and startup smoke checks still pass.
- Evidence: the validator sandbox read-only mounted `/usr`, including the JDK binaries, but `/usr/lib/jvm/default/conf` resolves to `/etc/java-openjdk`. Because that target was absent, `Files.createTempFile` failed with `NoSuchFileException` for `conf/security/java.security`. Binding the narrow target and adding a namespace regression restored the Java oracle, and all 26 harness tests passed under the repaired harness.
- Transfer candidate: resolve symlink chains for every selected executable and runtime resource during environment admission, bind or package the complete minimal target closure, and execute a representative standard-library probe inside the final namespace rather than checking path presence outside it.
- Limiting condition: a statically linked or deliberately hermetic runtime may have no external target closure; prove that from the shipped artifact and final namespace rather than assuming it from installation layout.

### L-105 — Proving non-return needs an observation interval after the triggering event

- Port status: unimplemented.
- Quality effect: checking an `alreadyReturned` flag immediately after a worker observes cancellation can let an early-returning mutant pass when the caller thread has not yet received another scheduling turn, making result classification depend on scheduler timing.
- Evidence: the first Java cancellation mutant removed the physical join, but its public test sometimes observed `cancelReturned == false` immediately after the task counted down its interruption latch. Three complete matrix runs all passed yet emitted different failing-check sets. Holding user code behind a release barrier and requiring the canceller's completion latch to remain unobserved for a bounded interval produced five byte-identical concurrent mutant dispositions and restored byte-identical full matrices across three CWDs.
- Transfer candidate: trigger the governed event through a barrier, give the supposedly early path a bounded opportunity to publish completion while the terminal path remains impossible, then release and prove eventual completion; record timeout as structured negative evidence rather than using an unbounded wait or instantaneous flag read.
- Limiting condition: an API may expose a linearizable state transition that can be read atomically after the trigger; when that guarantee is part of the contract, a separate scheduling interval is unnecessary.

### L-106 — Batch success must aggregate every item, not inherit the last command's status

- Port status: unimplemented.
- Quality effect: a shell loop or orchestration group can report success when earlier items failed if its exit status comes only from the final successful iteration, allowing partial evidence to masquerade as a complete gate.
- Evidence: the first three-CWD Java pre-freeze wrapper printed six report-schema errors for its early cases, then later cases passed; every group returned status zero and produced matching two-line outputs because the loop's final command succeeded. Adding fail-fast behavior and an exact expected line count made incomplete groups nonpassing.
- Transfer candidate: collect a status for every dispatched item, require the expected cardinality and identities, fail the batch when any item is missing or nonzero, and compare complete normalized outputs only after aggregation succeeds.
- Limiting condition: intentionally best-effort batches may continue after failures, but their aggregate must explicitly report partial success and failed identities rather than returning an undifferentiated success status.

### L-107 — Process IDs belong in a shell-native collection

- Port status: unimplemented.
- Quality effect: serializing multiple child PIDs into one scalar and relying on implicit word splitting is shell-dependent; a waiter can treat the entire string as one job, compare empty outputs, and clean storage while children are still running.
- Evidence: a five-run zsh stress wrapper accumulated PIDs into a space-prefixed scalar, and `wait` rejected the combined value as one unknown job. All five evidence files were still empty when hashed and were removed before the child processes completed. Replacing the scalar with a native zsh array yielded five completed, byte-identical dispositions and no surviving controllers.
- Transfer candidate: retain process handles in the orchestration language's native collection, wait each resolved child, aggregate every status before reading outputs, and verify no child remains before cleanup.
- Limiting condition: a strictly selected shell with specified splitting semantics can use a documented scalar protocol, but a native array or higher-level process API remains clearer and less fragile.

### L-108 — Evaluator evidence must satisfy its interface before it can support a verdict

- Port status: unimplemented.
- Quality effect: semantically correct checks are inadmissible when their report violates the controller schema, and schema rejection can hide which candidate behavior actually passed or failed.
- Evidence: four Java validators allowed failure evidence up to 1,300 characters while the campaign parser caps it at 1,000; seed checks ran but the harness rejected six reports before polarity could be established. Bounding validator evidence at 950 characters restored parseable seed/oracle reports without weakening any check.
- Transfer candidate: preflight validator output against the exact consumer schema—including keys, types, cardinality, size, aggregate consistency, and exit-code agreement—using both passing and deliberately failing fixtures before evaluation begins.
- Limiting condition: an unstructured human-only investigation may not need a machine schema, but its conclusions are not interchangeable with identity-bound automated evidence until a stable interface is supplied.

### L-109 — A prospective trial must execute from immutable dependency bytes, not a live path

- Port status: unimplemented.
- Quality effect: recording a helper's hash in a design does not make later executions reproducible when each run rereads the same mutable worktree path; an unrelated concurrent edit can split one round across different infrastructure states or strand the remaining assignments.
- Evidence: both first Java rounds pinned split-testing helper SHA-256 `562897…` and completed several valid runs. Another task then replaced that worktree file with an uncommitted schema-2 implementation at `a15664…`; later runs correctly refused to start with helper-mismatch infrastructure failures. The contaminated rounds were retained unrevealed, and complete replacement rounds were created against a read-only campaign copy whose bytes match the original pinned digest.
- Transfer candidate: at round admission, copy every executable dependency into controller-owned read-only storage, bind the immutable path and digest into the design, and launch every run from that snapshot; treat any live-path drift as infrastructure failure and replace the complete prospective round rather than mixing attempts.
- Limiting condition: a content-addressed immutable store may safely serve the dependency directly without another copy, provided retention and path resolution are guaranteed for the round's full lifetime.

### L-110 — Hidden verification cannot strengthen the declared contract

- Port status: unimplemented.
- Quality effect: an evaluator can classify every valid implementation as wrong when a hidden check silently promotes one conventional implementation choice into a requirement absent from the task, skill, or public interface; unanimous failure can then be misread as an agent or treatment defect.
- Evidence: all six Java process candidates passed public tests, Java 17 compatibility, submitted-regression custody, hygiene, child reaping, worker join, and typed interruption propagation, then failed only a hidden requirement to restore interrupt status before directly rethrowing `InterruptedException`. The task required propagation, while the skill permits direct propagation and requires restoration when translating interruption into another result. After removing the undeclared gate, a structurally valid alternative that deliberately omitted restoration passed the full matrix and all six replacement task artifacts passed. An unsafe-Rust foreign-owner validator later accepted every behavioral and regression check but rejected a valid implementation solely because release logic lived in `src/owner.rs` instead of literal tokens in `src/lib.rs`; replacing the positive source-shape gate with behavior plus negative fixture-control checks admitted the module-split implementation while still rejecting the semantic mutant and diagnostic spoof.
- Transfer candidate: derive every hidden assertion from a traceable declared property, admit at least one materially different valid alternative for each implementation-sensitive boundary, preserve check-level evidence, and treat broad isolated failure against an otherwise standard behavior as a possible validator defect before attributing it to candidates.
- Limiting condition: interrupt restoration or another convention is valid to require when the public contract, selected framework, or task explicitly promises it; the evaluator must bind and expose that authority rather than infer universality from common practice.

### L-111 — Compatibility floors must remain executable under the selected verifier

- Port status: unimplemented.
- Quality effect: retaining an old declared language or API floor can become impossible under a newer compiler's warnings-as-errors policy when that verifier deprecates the floor itself; suppressing the warning hides a changed support relationship, while blindly raising the floor can break users.
- Evidence: Kotlin compiler 2.4.10 emits a deprecation warning for language version 2.0, and the instrument's governed warnings-as-errors policy turned that warning into failure before candidate behavior ran. The admitted projects use their declared compatible 2.2 floor instead of suppressing the verifier or claiming continued 2.0 coverage.
- Transfer candidate: model product compatibility, compiler acceptance, language/API mode, warning policy, and runtime target as distinct constraints; verify each supported combination with a toolchain that still accepts it, and treat loss of verifier support as an explicit support-matrix decision rather than source-code failure.
- Limiting condition: a repository may deliberately suppress a known tool deprecation to preserve a still-supported floor; that is valid only when another executable path continues to verify the promised floor and the suppression has a review or removal condition.

### L-112 — Suspension can preserve a failure contract without preserving object identity

- Port status: unimplemented.
- Quality effect: asserting reference identity for an exception or failure object across asynchronous boundaries can reject correct behavior when the runtime wraps, copies, reconstructs, serializes, or stack-recovers the failure while preserving its promised semantics.
- Evidence: Kotlin coroutine stack recovery copied exceptions crossing suspension boundaries, so identity checks failed even though class, message, cause, cancellation behavior, and cleanup evidence were preserved. The corrected cases compare the public semantic contract and retain cleanup suppression across the recoverable cause chain.
- Transfer candidate: specify which failure properties are public—type, code, message, cause, suppression, ordering, cancellation classification, or exact identity—and test only the promised subset across task, process, RPC, actor, and coroutine boundaries; include one runtime transformation counterfactual before making identity a gate.
- Limiting condition: exact object identity is valid when callers use it as a documented token or the boundary explicitly promises pass-through without transformation; then the implementation and test must select an abstraction that can uphold that promise.

### L-113 — A lifecycle test's control plane must remain independently schedulable

- Port status: unimplemented.
- Quality effect: a test can deadlock the scheduler or event loop that must deliver cancellation, timeout, release, or observation, making the harness—not the implementation—the reason the governed lifecycle never advances.
- Evidence: the first Kotlin blocking-cancellation fixture waited on an operating-system latch inside `runBlocking`, preventing the coroutine assigned to cancel the operation from running. Replacing scheduler control with suspending handshakes and reserving the OS latch for the simulated blocking source restored deterministic progress.
- Transfer candidate: keep the test control plane on an independent thread, executor, clock, or cooperative suspension path; map which actor must schedule every trigger and release before running the test; place bounded deadlines around each rendezvous and emit the stalled actor as structured evidence.
- Limiting condition: intentionally blocking the only scheduler is valid when starvation or event-loop obstruction is the property under test, but the trigger and watchdog must then be owned outside that scheduler.

### L-114 — Concurrency bounds need a closed admission barrier before release

- Port status: unimplemented.
- Quality effect: releasing permits or workers before every intended first-wave observer has recorded its state lets scheduler order masquerade as a valid bound, so a correct implementation can fail or an over-admitting one can escape observation.
- Evidence: the first Kotlin bounded-batch fixture allowed early workers to advance while later first-wave observers had not yet recorded admission. The repaired fixture requires every observer in the bounded wave to cross a barrier before any worker or permit can proceed.
- Transfer candidate: define the exact admission linearization point, hold completion impossible until the full observation cohort reaches a controller-owned barrier, assert the maximum and identities while the system is quiescent, then release and prove eventual terminal completion.
- Limiting condition: streaming or open-ended systems may not have a finite cohort barrier; use a controller-owned gate at the admission seam plus a bounded observation window and explicit arrival accounting instead.

### L-115 — Nested timeout budgets must compose into one terminal evidence budget

- Port status: unimplemented.
- Quality effect: individually bounded subprocesses can still exceed their parent's deadline when they run sequentially, causing the controller to kill the validator before it emits JSON and converting an ordinary candidate hang into infrastructure loss.
- Evidence: the first Kotlin confirmation validator allowed three sequential 120-second test phases beneath a 180-second outer ceiling; one hanging candidate produced no report. Replacement identities cap each phase at 45 seconds, and a public-test hang counterfactual returned complete structured non-pass evidence in about 90 seconds under the unchanged outer ceiling.
- Transfer candidate: calculate the worst-case sum of sequential child deadlines, startup and cleanup margins, retries, and serialization before admission; require that every fault path can emit a bounded terminal envelope within the parent budget, and execute an actual hang in each sequential position.
- Limiting condition: parallel child budgets compose by the critical path rather than simple summation, but cancellation and join margins still belong in the parent budget and must be measured under the selected concurrency limit.

### L-116 — Candidate self-verification and controller verification are separate evidence channels

- Port status: unimplemented.
- Quality effect: a candidate can be unable to download a toolchain or dependency in its restricted environment while the controller has complete pinned offline assets; collapsing those channels either discards valid private evidence or falsely claims the candidate ran checks it could not run.
- Evidence: Kotlin task agents encountered DNS resolution failure while attempting the repository's download-backed local test entrypoint, yet the controller reconstructed SHA-pinned compiler and coroutine assets from private instrument chunks and independently validated each submitted artifact.
- Transfer candidate: record candidate-run checks and controller-run checks separately with their environments and dependency identities, prefer repository-local or preprovisioned candidate verification where practical, and never rewrite an unavailable candidate check into a claimed pass because private validation later succeeded.
- Limiting condition: when the task explicitly requires an offline or hermetic developer workflow, candidate inability to run the governed checks is itself a product failure even if a privileged controller can validate behavior.

### L-117 — Operational handoff instructions are executable claims, not trusted memory

- Port status: unimplemented.
- Quality effect: a precise-looking resumed command can still point to a stale or imagined file location, wasting work and potentially bypassing the canonical controller when long-running state outlives the context that produced the handoff.
- Evidence: the resumed Kotlin handoff said to execute `check_case.py` inside each instrument directory, but the campaign owns one centralized `harness/check_case.py --case <dir>`; both first resumed checks failed with missing-file errors before the canonical path was rediscovered.
- Transfer candidate: persist canonical commands or machine-readable entrypoints beside active state, resolve every referenced path before execution, prefer discoverable `--help` interfaces over copied command prose, and treat resumability notes as hypotheses until a cheap read-only existence and identity probe passes.
- Limiting condition: content-addressed immutable entrypoints can be trusted across handoffs when their path, digest, retention, and invocation contract are all bound and executable in the resumed environment.

### L-118 — Cancellation must be re-observed at the admission linearization seam

- Port status: unimplemented.
- Quality effect: a waiter whose cancellation token is already canceled can still enter user work when a semaphore permit, queue slot, pooled connection, or other admission resource becomes available concurrently; checking cancellation only while waiting leaves a race in which canceled work starts after the public cancellation boundary.
- Evidence: one of eight concurrent C# reference validations reported that caller cancellation failed to reach every pending outcome. The outcome oracle used `SemaphoreSlim.WaitAsync(token)`, but a canceled waiter sometimes acquired a permit released by the first operation and invoked the callback. Calling `ThrowIfCancellationRequested` immediately after acquisition and before user work eliminated the reproduction across concurrent validator stress and three byte-identical mutation matrices from unrelated working directories.
- Transfer candidate: define the exact point where work becomes admitted, observe cancellation immediately on the acquired side of that point, release the acquired resource in every non-admitted path, and test the race with cancellation and permit release synchronized to the same barrier; do not infer a closed admission gate from a cancellable wait alone.
- Limiting condition: an admission primitive may explicitly guarantee that cancellation linearizes before every later successful acquisition; when the selected runtime documents and the integration test proves that guarantee, a separate post-acquisition check may be redundant.

### L-119 — Generated artifacts, not authoring literals, are the transport contract

- Port status: unimplemented.
- Quality effect: code embedded across template, patch, raw-string, shell, JSON, or source-generator layers can be syntactically correct in the authoring language while interpolation, escaping, or line continuation silently changes the bytes eventually compiled or executed.
- Evidence: the C# instrument builder crossed JavaScript template transport, a patch, Python raw strings, and shell generation. `${...}` was first interpreted by the outer template, while trailing backslashes were consumed and patch `+` markers became literal compiler arguments; the builder looked plausible but emitted malformed commands. Replacing multiline generated invocations with single-line commands and validating the emitted runner restored every case.
- Transfer candidate: minimize parser-layer crossings, pass argument vectors or structured data instead of reconstructed command strings, render into a disposable destination, then parse, compile, execute, and where useful byte-compare the emitted artifact before assigning an identity; treat the authoring literal only as input evidence.
- Limiting condition: a file written directly through one well-specified serialization layer may need only ordinary parse or compile verification; byte-golden tests are most valuable where multiple interpreters or escaping domains compose.

### L-120 — A persistent native callback and its handle form one disposal lease

- Port status: unimplemented.
- Quality effect: releasing a native handle exactly once is insufficient when native code retains a managed callback or concurrent calls can still use that handle; disposal can race in-flight emission, allow a callback after state destruction, collect the delegate too early, or pair allocation with the wrong release path.
- Evidence: the C# native-lifetime instrument registers a Cdecl callback under a signed 64-bit owned handle and races `Emit` against repeated concurrent `Dispose`. Both the `SafeHandle` reference and an interlocked raw-handle alternative passed only when callback rooting, admission closure, in-flight completion, exactly-once native release, and no-post-dispose callback behavior were one coherent lifetime; the semantic mutant failed that boundary.
- Transfer candidate: derive the managed signature from the native header, bind the allocator/free pair and one release owner, root callbacks for the complete registration lifetime, prevent new operations once disposal linearizes, hold a safe handle reference or equivalent lease across every native call, wait or synchronize any admitted callback/use before successful disposal returns, and stress GC plus concurrent teardown.
- Limiting condition: when the native contract invokes the callback only synchronously during one call and retains neither callback nor handle, the lease can end at that call boundary; do not impose persistent-registration machinery on a genuinely synchronous ABI.

### L-121 — Nested process isolation must remain under one terminal cleanup authority

- Port status: unimplemented.
- Quality effect: a subprocess placed in a new session or process group can escape an outer controller’s timeout kill, while a normally completed command can still leave descendants alive; removing its temporary directory then hides the surviving work and lets one evaluation contaminate later tasks.
- Evidence: the cleanup audit after the first C# process trial found 31 orphaned `process-helper.sh hang` descendants whose validator directories had already been removed. Composing inner deadlines beneath the parent stopped the outer-timeout escape, but the first replacement matrix still left three descendants because timeout-only cleanup did not run when a defective regression exited nonzero normally. The admitted validator inspects and terminates residual command groups after every completion, treats success-with-descendants as failure, and left no residue under a hang counterfactual, repeated concurrent matrices, three-CWD pre/post-freeze checks, and the complete replacement round.
- Transfer candidate: choose one authority that can enumerate and terminate the entire descendant closure—prefer a controller-owned cgroup, job object, container, or equivalent durable boundary; keep every nested isolation domain subordinate to it, compose inner deadlines with cleanup margin, clean on success, failure, cancellation, and timeout, and perform a post-run orphan audit before deleting state or claiming completion.
- Limiting condition: a command contract may intentionally transfer durable background work to another named supervisor; then terminal cleanup means proving that transfer and excluding the supervised process from the caller-owned set, not killing it indiscriminately.

### L-122 — A process audit must not satisfy its own search predicate

- Port status: unimplemented.
- Quality effect: substring-searching a process table can report false survivors because the shell, search tool, or inline audit program contains the exact target text in its own command line; cleanup can be declared failed or an unrelated process can be terminated from observer-induced evidence.
- Evidence: after the corrected C# replacement round, a broad `/proc` command-line substring scan reported three helper processes, but all three were the active zsh and Python audit commands carrying the search literal. Parsing NUL-delimited arguments and requiring executable `/bin/sh`, an exact validator fixture path in argument one, and `hang` in argument two reported zero actual helpers.
- Transfer candidate: prefer controller-owned cgroup, job, container, or recorded PID/identity membership; when process-table search is necessary, match executable identity and structured argument positions, exclude the observer and ancestors explicitly, verify start time or namespace where PID reuse matters, and inspect exact matches before signaling anything.
- Limiting condition: a kernel or supervisor query over an identity-bound membership set does not include the textual observer and avoids this specific self-match, though stale membership and PID reuse still require their own handling.

### L-123 — A recurring verification lesson is not adopted until the operation is mechanized

- Port status: unimplemented.
- Quality effect: documenting a failure mode can improve later reasoning yet still permit the exact defect to recur in copied one-off commands; repeated verification then produces avoidable false evidence even though the lesson is nominally known.
- Evidence: immediately after L-122 captured process-audit self-matching, the JavaScript post-matrix audit again searched arbitrary command-line arguments and counted its own two Python layers. Replacing the prose-shaped inline probe with a reusable helper that identifies the executed script position, exact controller identity, validator roots, and temporary directory prefixes produced a self-excluding zero-residue result.
- Transfer candidate: when an observed lesson governs a repeated deterministic operation, encode it once in a tested script, schema, linter, template, or external control; route future workflows through that interface and retain prose for mission, interpretation, and exceptions rather than as the only enforcement surface.
- Limiting condition: rare judgment-heavy events may not justify automation, and a brittle checker can be worse than a clear instruction; mechanize only the stable observable predicate while leaving context-dependent decisions open.

### L-124 — Repository-aware diagnostics require a proven identity boundary

- Port status: unimplemented.
- Quality effect: invoking Git or another ancestor-discovering tool inside a copied artifact can silently inspect a parent repository when the artifact's own metadata was removed, producing a plausible but completely wrong diff, status, or policy context.
- Evidence: archived JavaScript trial projects no longer contained their temporary `.git` directories. `git -C <artifact>` therefore walked upward into the live agent-tooling repository and printed thousands of unrelated current changes; explicit seed-to-artifact filesystem comparison recovered the candidate-only delta without mutating either tree.
- Transfer candidate: before every repository-aware diagnostic, resolve and compare the exact top-level identity to the intended subject; for archives use a retained manifest, content digest, patch artifact, or no-index comparison that cannot discover an ancestor, and reject output whose resolved root is outside the evidence unit.
- Limiting condition: a deliberately nested worktree may inherit parent repository context by contract; in that case the parent identity is intended, but the artifact boundary and comparison base must still be explicit.

### L-125 — Cancellation forwarding and operation startup share one linearization contract

- Port status: unimplemented.
- Quality effect: a wrapper and operation can jointly lose cancellation even when the derived signal is correctly aborted if their startup contract is ambiguous; forwarding before deferred invocation is valid only when the operation checks pre-aborted state before listening for future events.
- Evidence: five JavaScript timeout candidates deferred `operation(signal)`, forwarded caller abort first, and then hung in a hidden operation that registered only an abort listener after receiving an already-aborted signal. Node exited 13 for unsettled top-level await. The seed itself established deferred invocation, while the oracle silently switched to synchronous invocation; the hidden callback, not the candidates, violated the pre-aborted-signal protocol, so the case was excluded and replaced.
- Transfer candidate: define whether cancellation before the operation-start seam prevents invocation or invokes with an already-aborted token; preserve that timing contract, require every callee entry path to check pre-aborted state before listener registration, and make wrappers join the operation's terminal outcome after requesting cancellation. Test abort exactly between wrapper entry, derived-signal creation, operation invocation, listener attachment, and first suspension.
- Limiting condition: a level-triggered cancellation primitive whose registration immediately reports prior cancellation does not lose the event, but startup ordering and whether the operation should run after cancellation remain public contract decisions.

### L-126 — Cleanup obligations begin at admission, not cancellation request

- Port status: unimplemented.
- Quality effect: a cancellation test can reject correct work-avoidance by demanding cleanup from an operation that never started, thereby turning one scheduler policy—invoke after cancellation—into an undeclared universal contract.
- Evidence: JavaScript timeout R2 explicitly preserved deferred invocation. One control and one treatment candidate observed caller abort before their operation microtask, declined to invoke the operation, and rejected with the exact caller reason. The hidden test marked both wrong only because its `cleaned` flag remained false, although no operation had been admitted and therefore no operation cleanup existed.
- Transfer candidate: define the admission linearization point; before it, cancellation may close admission and requires only wrapper-owned cleanup, while after it, cancellation must reach the admitted operation and the wrapper must join its terminal cleanup. Test both routes and record whether invocation occurred before asserting operation cleanup.
- Limiting condition: an API may explicitly promise that every accepted call invokes user work exactly once even if cancellation arrives before scheduling; then invocation is already committed at call acceptance and cleanup obligations follow that declared boundary.

### L-127 — Boundary-byte normalization requires format-specific authority

- Port status: unimplemented.
- Quality effect: a generic text helper can make prose look tidy while silently invalidating executable payloads whose final spaces, blank context lines, delimiters, signatures, or framing bytes are structural.
- Evidence: the Node HTTP oracle was generated by `difflib.unified_diff` with hunk header `@@ -1,17 +1,52 @@`. The shared writer's whole-document `rstrip()` removed the hunk's final context-only blank line, leaving only 16 old-side and 51 new-side lines; ordinary `git apply` rejected the patch as corrupt while `--recount` proved the remaining body itself was coherent.
- Transfer candidate: assign normalization at the serializer for the declared format, preserve executable and signed payloads byte-for-byte, parse or apply the emitted artifact using its real consumer before identity assignment, and reserve generic whitespace cleanup for formats whose grammar explicitly permits it.
- Limiting condition: canonicalization is appropriate when the target format defines it and both producer and consumer bind the same canonical representation; the hazard is unowned normalization, not normalization itself.

### L-128 — Terminal evidence belongs to the resource owner

- Port status: unimplemented.
- Quality effect: a lifecycle checker can reject correct cleanup by observing a peer, wrapper, cache, or projection whose state propagates after the owner has already reached its terminal boundary.
- Evidence: the Node HTTP oracle closed admission, escalated the stuck ordinary connection, and completed the server close callback, but the public test demanded that the remote `ClientRequest.destroyed` flag already be true. That flag belongs to the client-side wrapper and can lag the server transport boundary; querying the server's own connection set directly is the relevant return-time evidence.
- Transfer candidate: identify the component that owns admission and release, assert its terminal state at settlement, and test peer-visible propagation separately when needed for cleanup or an explicit end-to-end promise; do not substitute a convenient remote projection for owner state.
- Limiting condition: when the API contract explicitly promises coordinated end-to-end acknowledgement, peer state is part of completion evidence, but the acknowledgement mechanism must be named rather than inferred from local teardown.

### L-129 — Convenience adapters carry their complete settlement contract

- Port status: unimplemented.
- Quality effect: wrapping callbacks or events in a convenient promise can introduce implicit rejection, cancellation, listener cleanup, or multiplicity rules that change the workflow even when the requested success event is correct.
- Evidence: the Node HTTP fixture used `events.once(request, "close")` only to await cleanup and separately consumed the expected forced-close error. The returned promise nevertheless rejected on `ECONNRESET` because Node's non-error `once` adapter installs its own error failure channel; an explicit close-only promise matched the intended control plane.
- Transfer candidate: inspect and test the full settlement semantics of event-to-promise, callback-to-promise, retry, timeout, and stream adapters; choose or build an adapter whose success, error, cancellation, listener-removal, and repeated-event behavior matches the contract rather than relying on its surface name.
- Limiting condition: when the adapter's documented failure channels exactly match the operation's intended terminal outcomes, using the standard adapter is clearer and safer than a custom wrapper.

### L-130 — An asynchronous test gate must not monopolize the progress it awaits

- Port status: unimplemented.
- Quality effect: polling shared state by repeatedly awaiting resolved promises can make a test scheduler-specific, starve valid implementations, and convert an observational wait into the cause of a hang.
- Evidence: the Node stream hidden test looped on `await Promise.resolve()` until a transform exposed its signal. The async-generator oracle happened to enter that seam in time, while a valid Transform-stage alternative required Node stream/next-tick scheduling that the endless microtask chain starved; the checker timed out without testing cancellation.
- Transfer candidate: expose a controller-owned latch, barrier, channel, callback, or promise resolved exactly at the causal seam; await that gate with an independent deadline and allow the runtime's complete scheduler to progress. Use polling only with a real bounded delay or scheduler yield whose fairness is part of the tested platform contract.
- Limiting condition: a finite microtask drain is useful when the contract specifically concerns microtask ordering and the iteration bound is explicit; the defect is unbounded scheduler-biased polling for implementation-neutral progress.

### L-131 — End-to-end pressure is the composition of every owned queue

- Port status: unimplemented.
- Quality effect: code can be locally backpressured yet exceed an end-to-end memory or work budget because source prefetch, transforms, channels, batching, retries, protocol buffers, and destination queues each retain bounded items whose capacities add or otherwise compose.
- Evidence: a Node pipeline with source prefetch plus Transform writable/readable watermarks and a one-slot destination admitted three items while the first destination write was held. The checker allowed only two because it equated the destination watermark with the whole pipeline; the eager seed admitted all eight, so a declared three-slot fixture budget preserved discrimination without requiring the oracle's topology.
- Transfer candidate: inventory every queue and in-flight stage along the path, derive a global item/byte/work budget including multiplicative fan-out and retry copies, configure local limits from that budget, and test the maximum at a controlled downstream stall. State whether limits count queued, active, transformed, and protocol-buffered work.
- Limiting condition: a zero-copy or rendezvous pipeline may have no intermediate retention and can legitimately bind source admission directly to destination capacity; prove that topology rather than assuming it for interchangeable implementations.

### L-132 — Root parameters must name their authority domain and relation

- Port status: unimplemented.
- Quality effect: generic names such as root, base, hidden root, workspace, or context can refer to a repository boundary, private-state directory, mount source, containment authority, or artifact namespace; a plausible wrong choice can invalidate an entire batch before useful work begins.
- Evidence: the split controller's `--hidden-root` was supplied as the campaign's `.split-testing` state directory. All twelve Node diagnostic assignments failed before model launch because the implementation instead requires the exact Git repository root that contains the campaign and will be hidden from workers; the error `campaign root escapes campaign root` did not identify the two distinct paths or expected relation.
- Transfer candidate: name root parameters by authority and role, validate inter-root containment/equality once before fan-out, print received and expected resolved paths with a recovery hint, and ship one executable invocation test covering the documented topology. Treat similarly named roots from another layer as non-interchangeable until their relation is proven.
- Limiting condition: a single-root tool with one unambiguous filesystem domain does not need verbose naming, but the moment two roots coexist their authority and containment contract must be explicit.

### L-133 — Canonicalize domain identity before entering a coercive container

- Port status: unimplemented.
- Quality effect: a map, database, serializer, filesystem, URL router, cache, or language runtime can normalize distinct source identifiers into the same storage key, silently overwriting data before later validation has a chance to notice.
- Evidence: PHP arrays normalize decimal integer strings, booleans, floats, and null into integer or string keys. The admitted array fixture requires an injective type-tagged representation before insertion; both valid implementations preserve int `1`, string `"1"`, boolean `true`, and null as four ordered entries, while the raw-key seed and present-null mutant fail public and hidden checks.
- Transfer candidate: define identity in the source domain, enumerate the destination's normalization and comparison rules, canonicalize and validate before insertion, reject duplicate canonical identities before overwrite, and test adversarial pairs that differ before but collide after normalization. Preserve missing, null, false, zero, and empty values when the domain distinguishes them.
- Limiting condition: deliberate equivalence classes such as case-insensitive usernames may normalize multiple spellings to one identity; then collision handling and provenance must be an explicit domain rule rather than accidental container behavior.

### L-134 — Strictness is often an interaction-edge policy, not a component attribute

- Port status: unimplemented.
- Quality effect: labeling a library or function “strict” can hide that coercion, validation, serialization, authorization, retry, or compatibility behavior is selected by the caller, adapter, transport, or defining edge; testing from one side then gives false package-wide confidence.
- Evidence: PHP scalar argument coercion follows the caller file, while scalar return enforcement follows the file defining the function. The admitted API fixture preserves a weak legacy gateway and strict direct callers around the same `Repeater` method while also binding named parameter compatibility; both structurally different implementations pass, and the renamed-parameter mutant fails.
- Transfer candidate: locate the authority that selects policy for each direction of an interaction, test every supported edge separately, and describe the boundary in terms of observable calls and returns rather than attaching one global adjective to the component. Include adapters, callbacks, reflection, generated clients, and named arguments where they change the edge.
- Limiting condition: a process-isolated protocol that validates one canonical wire representation at ingress and egress may centralize strictness in one component; prove that no alternate caller path bypasses it.

### L-135 — Subprocess I/O is a wait-for graph with one terminal join

- Port status: unimplemented.
- Quality effect: individually reasonable operations—write stdin, read stdout, read stderr, request termination, collect status—can deadlock or lose output when bounded channels form a cycle or settlement occurs before every owned edge becomes terminal.
- Evidence: the PHP process seed writes all stdin, then drains stdout, then stderr; a child that fills both output pipes before reading input deadlocks. The stream-select oracle and a materially different file-backed descriptor implementation both pass high-input, dual-output, nonzero-exit, literal-argument, timeout, and reap checks. A mutant that stops draining stderr becomes nonterminal, and a descendant-spawning hanging test is converted into bounded structured failure with no residue.
- Transfer candidate: draw producer/consumer dependencies for stdin, stdout, stderr, control, exit, and descendants; make every bounded edge progress concurrently or replace it with an owned non-cyclic descriptor; treat termination as a request; drain terminal data, obtain trustworthy status, reap, and verify the complete owned process closure before returning.
- Limiting condition: when all streams are redirected to seekable files or inherited endpoints with independently proven capacity and ownership, concurrent pipe pumping may be unnecessary, but deadline, exit, reaping, and cleanup obligations remain.

### L-136 — Executable consumers own artifact schemas and freeze semantics

- Port status: unimplemented.
- Quality effect: an internally coherent builder can emit cases, locks, manifests, or prompts that its real executor rejects—or worse, preserve hidden oracle material—when it duplicates the consumer's schema and custody logic instead of invoking the production interface.
- Evidence: the first Python freezer wrote a custom `case.json` and `instrument.lock.json` that local validators accepted but `harness/common.py` would reject, and its build tree temporarily retained `.oracle`. Switching to the harness-owned `check_case.py --freeze` enforced the exact six-key case schema, seed-fail/oracle-pass lock, instrument digest, oracle reconstruction, oracle-tree removal, and read-only modes before any model exposure.
- Transfer candidate: make the production parser/freezer/compiler the admission authority, round-trip every generated artifact through it, reject unknown and missing fields, and prove that privileged construction inputs are absent from the published unit before assigning identity.
- Limiting condition: a separately implemented producer is safe when a versioned conformance suite proves byte- and behavior-equivalence to every supported consumer; that suite, not shared intent, is the authority.

### L-137 — Runtime identity is a relation, not one canonical path string

- Port status: unimplemented.
- Quality effect: resolving symlinks can falsely reject a deliberately governed invocation path, while checking only the path can miss replacement of the executable target; either scalar view loses part of the runtime contract.
- Evidence: `/usr/bin/python3` was the declared invocation and `sys.executable` path, but `Path.resolve()` produced the versioned target, so the first Python validator rejected every seed and oracle before behavior checks despite matching executable bytes and version. The admitted validator separately binds invocation path, existence, target bytes, runtime-reported version, and runtime-reported executable.
- Transfer candidate: represent tool identity as the required invocation name/path, resolved target closure where relevant, content digest, reported version/build, and selected environment; compare each field according to its authority instead of collapsing them through canonicalization.
- Limiting condition: a content-addressed executable invoked directly with no aliases or dynamic loader/configuration closure may be identified by one path/digest pair, but the execution environment still needs its own binding.

### L-138 — Passing verification needs loaded-code provenance

- Port status: unimplemented.
- Quality effect: a test can pass against an older global install, sibling checkout, editable package, cache, generated output, or ancestor repository while the submitted source remains unexecuted, turning a green result into evidence about the wrong subject.
- Evidence: the Python metadata fixture places an older `parcelcalc` first on `PYTHONPATH`; its seed runner appends the repository `src` path and imports the external copy. The admitted oracle and import-spec alternative both print and independently verify that `parcelcalc.__file__` belongs to the submitted checkout while preserving the selected interpreter and metadata contract.
- Transfer candidate: for import-, plugin-, module-, schema-, or repository-sensitive checks, record and validate the resolved origin of loaded code and configuration alongside the command result; seed an adversarial competing installation to prove the check discriminates provenance.
- Limiting condition: a hermetic build or namespace that makes every out-of-unit origin unrepresentable may derive provenance from the sandbox manifest, but that containment must be executable evidence rather than an assumption.

### L-139 — Wrapper transparency is a vector of observable contracts

- Port status: unimplemented.
- Quality effect: a wrapper can preserve returned values while breaking descriptor binding, sync/async or generator classification, keyword names, defaults, annotations, metadata, introspection, registration identity, exception timing, or static consumers.
- Evidence: the Python decorator seed returns the original coroutine object but is a callable instance without function descriptor binding or coroutine-function identity. The oracle and a manually metadata-assigned alternative pass bound/unbound signature, keyword-only default, name/docstring, awaitable result, and coroutine classification checks; a `functools.wraps` mutant with a synchronous forwarding function still fails coroutine shape.
- Transfer candidate: inventory the wrapper surfaces consumers observe, preserve only the declared vector, and test calls plus reflection/registration/static artifacts independently; do not infer transparency from `*args, **kwargs`, one metadata helper, or matching output alone.
- Limiting condition: an intentionally opaque adapter may replace the wrapped API with a new declared contract; then preserving old introspection or call shape is unnecessary, but the migration must be explicit.

### L-140 — Changing I/O topology can remove a settlement witness

- Port status: unimplemented.
- Quality effect: replacing bounded pipes with seekable files can eliminate deadlock yet also eliminate EOF/closure pressure that previously kept the caller waiting for descendants, allowing the group leader to exit while a child still executes unnoticed.
- Evidence: the Python file-backed subprocess alternative drained complete high-volume output and waited for the immediate process, but its first version returned after SIGTERM killed only the leader while a grandchild ignored SIGTERM. Because files never waited for descendant-held pipe closure, the hidden process check found the live child. Independent process-group liveness and escalation made the alternative valid.
- Transfer candidate: whenever buffering, transport, persistence, or redirection topology changes, re-derive both progress and completion witnesses; retain an explicit terminal join over the complete ownership domain instead of relying on incidental EOF, backpressure, handle closure, or leader exit.
- Limiting condition: a supervisor, job object, cgroup, or protocol acknowledgement may provide a topology-independent group completion witness; when present and verified, stream closure need not carry that role.

### L-141 — Asynchronous dispatch acknowledgment is not completion

- Port status: unimplemented.
- Quality effect: an orchestrator can lose custody of live work when a launch API returns a session or job handle with empty immediate output and the caller treats that response as terminal success; duplicate launches, premature publication, or cleanup races can follow.
- Evidence: the parallel Python round launch returned two background execution handles after the nested command yield. The composing script printed only each command's empty output and discarded the structured handles, briefly making both rounds look finished while 24 Luna tasks were active. Process and record inspection recovered the existing controller PIDs, prevented duplicate dispatch, and monitored them to terminal records before publication.
- Transfer candidate: model launch, accepted, running, terminal, and collected as distinct states; retain every returned handle in durable orchestration state, wait or poll that exact handle, require a terminal envelope and expected artifact cardinality, and never infer completion from an empty output channel.
- Limiting condition: an API documented to block until terminal state and return no resumable handle may collapse acknowledgment and completion, but wrappers that add yielding or background sessions must preserve the distinction.

### L-142 — Credential custody and credential liveness are separate evidence

- Port status: unimplemented.
- Quality effect: a correctly permissioned, byte-stable credential snapshot can expire or be revoked between successful campaigns, causing every worker in a fan-out to fail before producing a task attempt while filesystem and harness checks remain green.
- Evidence: all 24 Ruby R1 split-test assignments failed at the model boundary with HTTP 401 using the previously valid mode-600 temporary auth snapshot; a credential from the current local authority had different bytes and passed an exact Luna-medium endpoint probe before replacement rounds were allocated.
- Transfer candidate: bind credential provenance and custody without exposing contents, then run one minimal endpoint- and model-specific liveness probe immediately before expensive fan-out; allocate fresh identities after a failed sealed batch and classify pre-attempt authentication failures as infrastructure, never task outcomes.
- Limiting condition: an execution service that atomically exchanges short-lived credentials per assignment may make a separate preflight stale quickly; the service should then own refresh and return an authenticated admission receipt with each launch.

### L-143 — Cleanup must cover the callee's runtime closure, not only caller-created files

- Port status: unimplemented.
- Quality effect: a temporary-directory cleanup plan can remove the input file it created yet leave sessions, logs, caches, or configuration generated by the invoked tool, making successful probes leak state or fail their own teardown.
- Evidence: the isolated Codex auth probe created additional files beneath its temporary `CODEX_HOME`; a trap that knew only about `auth.json` removed that file but could not remove the now-nonempty directory. A depth-first identity-scoped cleanup removed the complete generated closure.
- Transfer candidate: treat a delegated temporary root as one owned artifact domain, inspect or recursively enumerate its post-run closure without following symlinks, and remove children depth-first before claiming cleanup; verify absence at the exact resolved root.
- Limiting condition: an external sandbox or disposable mount that is destroyed atomically already supplies the closure operation, but its destruction still needs observable completion evidence.

### L-144 — Container identity is an invariant over the full residency interval

- Port status: unimplemented.
- Quality effect: aligning equality and hash functions at insertion time is insufficient when a key's identity fields can later change; the container's stored index becomes stale, so even lookup by the same object or an equivalent instance can fail.
- Evidence: the Ruby Hash-key fixture requires normalized exact-class `eql?`/`hash` agreement and stable identity after insertion. Both the frozen value-object oracle and a materially different private-identity implementation pass Hash lookup and Set deduplication, while the mutable seed and object-identity hash mutant fail.
- Transfer candidate: define canonical identity before insertion, keep every identity field stable while resident, prevent aliasing from caller-owned mutable inputs, and test lookup/deduplication with distinct equivalents before and after attempted mutation; otherwise remove and reinsert through an owning API that rebuilds the index.
- Limiting condition: identity-based containers deliberately ignore value mutation, and some containers expose an explicit, correctly owned reindex operation such as Ruby `Hash#rehash`; those are valid when every mutation path invokes the protocol before any observation.

### L-145 — Queue closure, drain, worker settlement, and failure observation are distinct events

- Port status: unimplemented.
- Quality effect: closing a queue can wake consumers without proving queued work drained, producer pressure ended, workers terminated, or worker exceptions reached the owner; a bounded producer can still deadlock after consumers fail.
- Evidence: the Ruby queue seed closes and joins on success, and `Thread#join` propagates a simple failure, yet all workers can die while the producer remains blocked on a full `SizedQueue`. The admitted closure-based and sentinel-based implementations keep failed workers draining or otherwise preserve progress, settle every thread, and only then raise the primary producer or worker failure. One no-skill trial fixed behavior but failed because its tests still passed the deadlocking seed.
- Transfer candidate: specify capacity, producer ownership, terminal signaling, drain behavior after failure, one terminal event per consumer where needed, failure precedence, and the terminal join that proves every owned worker settled; test success, producer failure, all-consumer failure under pressure, and residue separately.
- Limiting condition: a structured runtime or framework may couple queue cancellation, child settlement, and failure propagation in one verified primitive; then use that primitive's documented terminal operation instead of rebuilding the protocol manually.

### L-146 — A residue audit is only as complete as its command grammar

- Port status: unimplemented.
- Quality effect: a process audit can report a clean system while live work survives when its executable allowlist or option parser does not recognize the runtime and cannot recover the script or artifact identity from the command line.
- Evidence: the campaign residue auditor recognized Python, shell, and Node command forms but initially ignored Ruby entirely. After adding Ruby option parsing, direct probes recover scripts behind `--disable-gems` and `-I` forms, the real Ruby controller/validator/temp audit reports no residue, and a separate `/proc/*/cwd` check reports no process beneath any Ruby trial workspace.
- Transfer candidate: derive the audit grammar from every executor actually used, test representative option and inline-code forms, supplement argv identity with CWD, process-group, cgroup/job, open-handle, or artifact-root evidence, and seed one known live process per runtime to prove detection before trusting a clean result.
- Limiting condition: an external supervisor that enumerates exact job identities independent of executable syntax can make command parsing unnecessary; its job-to-artifact binding and terminal state must still be verified.

### L-147 — Tool identity includes its transitive executable and configuration closure

- Port status: unimplemented.
- Quality effect: pinning the top-level compiler or package-manager executable does not make a build reproducible when that tool discovers helpers, wrappers, linkers, documentation generators, configuration, or dynamic resources outside the governed boundary.
- Evidence: the first Rust validator pinned exact Cargo and rustc paths, but Cargo launched `/usr/bin/rustdoc` through the workstation Rustup shim. Direct checks passed until documentation compilation exercised this undeclared executable. The admitted harness binds the complete Rust 1.94.1 toolchain directory read-only, hashes rustc, Cargo, and rustdoc separately, and sanitizes `PATH` for both task and validator sandboxes.
- Transfer candidate: trace the selected command's actual process/configuration closure under representative modes, bind every decision-relevant executable and config source, and test at least one path that invokes each transitive helper; report any intentionally ambient component as an explicit limitation.
- Limiting condition: a statically linked, content-addressed single executable with configuration and resources embedded may have no external executable closure, but kernel, loader, target, and environment assumptions can still affect behavior.

### L-148 — Direct validation and production-sandbox validation are different evidence boundaries

- Port status: unimplemented.
- Quality effect: a direct oracle or narrow connectivity probe can pass while the production sandbox still hides a toolchain, config directory, device, certificate, resolver behavior, or service needed by the real workflow.
- Evidence: Rust seeds, oracles, and the mutation matrix validated directly with the home-hosted Rust 1.94.1 toolchain, while the first Bubblewrap task/validator path could not see that same toolchain beneath its tmpfs home. Later, an async-Rust reviewer namespace reached an external endpoint with a short `curl` probe yet the real Codex workflow repeatedly failed through the systemd stub resolver and timed out; mounting the authoritative upstream resolver produced a complete high-reasoning Codex judgment while the same execution recorded zero connections to live controller loopback and host-address sentinels.
- Transfer candidate: execute the frozen oracle or capability probe through the exact production command, client, sandbox, mounts, resolver, environment, working directory, limits, duration, and identity checks used for the real artifact; when the boundary must both allow and deny capabilities, establish both properties in the same production-shaped execution and retain narrower probes only as diagnostic evidence.
- Limiting condition: when direct and production execution are literally the same content-addressed environment and command path, one run can satisfy both claims, but that identity must be mechanically established rather than inferred.

### L-149 — Diagnostic payloads are governed by their consumer schema

- Port status: unimplemented.
- Quality effect: a validator can correctly detect a defect yet be rejected as infrastructure failure when an evidence field, finding list, log, or serialized tree exceeds the harness's cardinality or size contract.
- Evidence: a Rust validator emitted semantically useful compiler/test evidence longer than the split harness's 1,000-character per-check limit. The admitted validator deterministically caps evidence below the boundary while preserving pass/fail identity and keeps verbose detail in controller-owned logs.
- Transfer candidate: validate producer output against the exact downstream schema before admission, default to compact bounded summaries, retain counts and truncation markers, and route full diagnostics to a separately bounded artifact that consumers request explicitly.
- Limiting condition: an interface with streaming backpressure, pagination, and no bounded envelope may not need field truncation, but it still needs total-resource, cancellation, and terminal-completeness contracts.

### L-150 — Cleanup ordering is part of evidence admission

- Port status: unimplemented.
- Quality effect: removing generated state eventually is insufficient when artifact-size, executable-cache, secret, or symlink gates inspect the tree earlier; valid source can be rejected or sensitive/generated material can be copied before cleanup runs.
- Evidence: Rust harness V2 deleted ignored Cargo outputs after validation, which made publication small, but two confirmation R3 runs failed first because target binaries exceeded the 8 MiB per-file evidence limit before deletion. V3 performs ignore-authoritative cleanup immediately after protected-state checks and before evidence limits or validation-copy construction; all 12 R4 artifacts then remained 9–13 KiB and target-free.
- Transfer candidate: map every observation and copy boundary, place cleanup after the last operation that legitimately needs generated state but before the first gate or snapshot that must exclude it, and add a fixture whose generated output violates the downstream limit to prove ordering.
- Limiting condition: generated outputs that are themselves required deliverables must not be deleted; they need a separately declared artifact class, limits, provenance, and review path.

### L-151 — Packaging failure does not retroactively become a task outcome

- Port status: unimplemented.
- Quality effect: completed task artifacts can be semantically valid yet unusable for blinded review because publication size, secrecy, portability, or custody fails; counting them as ordinary task passes or losses conflates subject behavior with evidence transport.
- Evidence: Rust R2 produced 24 complete machine-validated task records, including a 0/3 versus 3/3 feature-isolation pattern, but publication predicted 707,877,480 bytes after Cargo targets remained in artifacts and correctly refused the round. The records are retained as packaging-calibration evidence, while prospectively allocated R3/R4 identities supply the valid review population.
- Transfer candidate: distinguish task terminal state, evidence admissibility, publication, reviewability, and interpretation; preserve failed-boundary records under immutable identities, exclude the whole affected comparison, repair infrastructure prospectively, and never overwrite sealed outcomes.
- Limiting condition: if a publication failure is provably independent of condition and a predeclared lossless transformation can be applied without changing artifact identity or reviewer information, the design may permit recovery; that transformation and proof must precede observation.

### L-152 — Replacement rounds are a check on small-panel effect stability

- Port status: unimplemented.
- Quality effect: a dramatic difference in a few stochastic agent runs can disappear or reverse under an unchanged task and treatment, so early numerical separation can cause prompt overfitting and false transfers into general guidance.
- Evidence: unpublished Rust diagnostic R2 scored feature isolation at 0/3 no-skill versus 3/3 revised-skill. The prospectively valid R3 replacement on the same frozen case and treatment scored 2/3 versus 2/3. No semantic evidence justified treating the first panel as a stable treatment effect.
- Transfer candidate: preserve per-run outcomes, require a prospectively admissible replacement after infrastructure failure, analyze cases and phases separately, and port only mechanisms supported by artifacts, independent review, and replicated behavior—not the largest observed delta.
- Limiting condition: deterministic systems with exhaustive inputs and byte-identical outputs may need no stochastic replication; the admission boundary and oracle still must be valid before the result is interpreted.

### L-153 — Process closure and temporary-filesystem closure need independent proofs

- Port status: unimplemented.
- Quality effect: killing a validator process group does not prove its temporary directory was removed, and deleting a temporary directory does not prove descendants stopped; either survivor can contaminate later runs or retain sensitive state.
- Evidence: an interrupted Rust mutation-matrix run initially left both a validator process and its `rust-mutation-matrix-*` directory. Process-group termination and directory cleanup required distinct recovery actions, after which the structural auditor checked `/proc` identities/CWDs and exact temporary prefixes independently.
- Transfer candidate: assign one ownership identity to each process group/job and one to each temporary artifact root, install independent terminal cleanup paths for both, and verify zero survivors in both domains after normal completion, timeout, interruption, and controller failure.
- Limiting condition: an external sandbox that atomically destroys its process namespace and ephemeral filesystem can couple both closures, but the caller still needs observable proof that destruction reached terminal state.

### L-154 — Treatment assignment and treatment exposure are different evidence

- Port status: unimplemented.
- Quality effect: a run assigned to a skill can behave exactly like control when routing never loads the skill; excluding that run overstates content efficacy, while attributing its outcome to the skill text misdiagnoses a delivery failure as a reasoning failure.
- Evidence: in async-Rust R1, the sole revised-skill framed-reader failure never opened `async-rust/SKILL.md`, while the other eleven treatment runs did. After the activation boundary became mandatory and keyword-specific, all six R2 treatment runs opened the skill and both routed references. Unsafe-Rust R1 then exposed the same distinction at larger scale: the revised source was assigned to twelve runs but opened in only nine, with one miss each on foreign ownership, pinned destruction, and thread affinity. Intention-to-treat machine outcomes remained tied at 9/12 while the revised condition averaged 116.8 versus 101.8 seconds and about 229,479 versus 184,485 input tokens; the three non-openers remain treatment-delivery failures rather than post-hoc exclusions or evidence about unread body content. In the prospective unsafe-Rust repair round, V2 opened in 3/3 runs and its relevant reference opened in 2/3, versus V1 opening in 2/3 and never loading that reference; V2 passed 2/3 against control 1/3 and V1 0/3, but one fully exposed V2 run still omitted readiness while one V2 run that skipped the reference passed.
- Transfer candidate: bind treatment assignment, availability, activation, relevant-reference routing, mechanism adoption, and task outcome separately; use assigned-condition results as the primary comparison, then use controller-observed exposure to diagnose delivery without treating a file open as proof of compliance or excluding misses post hoc.
- Limiting condition: exposure telemetry must come from controller-observed tool or file access rather than a candidate claim, and observing it must not reveal condition identity to blinded reviewers.

### L-155 — Resumable state must encode the protocol, not the implementation accident

- Port status: unimplemented.
- Quality effect: a retryable, cancellable, or incrementally decoded operation can appear to preserve progress while deriving authority from buffer capacity, poll count, allocation shape, cursor coincidence, or another representation detail that changes independently of the protocol.
- Evidence: the only async-Rust R1 framed-reader treatment failure used `Vec::capacity()` as the frame length. Both blinded reviewers identified that allocator-derived value as the cause of the hidden failure. The revised guidance names declared length plus consumed offset as authoritative state, and every subsequently exposed framed-reader treatment produced a machine-valid persistent state machine.
- Transfer candidate: identify the protocol facts that survive interruption, store those facts explicitly, and test resumption after partial progress while perturbing allocation, chunking, polling, and buffering independently.
- Limiting condition: a representation property may itself be authoritative when the public protocol defines it; the defect is borrowing accidental implementation state as domain truth without that contract.

### L-156 — A shared shutdown boundary requires request fan-out before per-member joins

- Port status: unimplemented.
- Quality effect: aborting and awaiting children one at a time lets settling an early child release, wake, or unblock a later child before that later child has received the common shutdown request, so work can cross a boundary the owner claims is closed.
- Evidence: blinded async-Rust review found a machine-green task-group implementation that sequentially aborted and awaited handles. A new held-out fixture makes the first task's destructor release the second task; the sequential seed crosses the boundary, while abort-all-then-join implementations and a materially different reverse-join alternative pass the four-disposition mutation matrix.
- Transfer candidate: when one event defines a cohort-wide stop boundary, close admission and deliver the stop or abort request to the complete owned cohort before awaiting any member; then observe every terminal outcome under the declared failure policy.
- Limiting condition: protocols with dependency-ordered shutdown may intentionally sequence requests, but the ordering and the work allowed between stages must be part of the contract rather than an accidental consequence of awaiting one member.

### L-157 — Post-generation validation is still execution by the candidate

- Port status: unimplemented.
- Quality effect: hiding oracle and held-out material from the generating agent is insufficient when the submitted build, tests, macros, fixtures, or runtime code later execute in a validator namespace that mounts those materials; candidate code can read the answer key after generation and condition its behavior on private evidence.
- Evidence: the first unsafe-Rust validator mounted each complete case directory during candidate test execution, exposing `.oracle/`, `oracle.patch`, hidden checks, task, and review files. An independent auditor reproduced that visibility from a disposable candidate, so the pre-freeze instruments were rejected despite passing their seed/oracle and mutation matrices. The replacement harness mounts only a scrubbed read-only validator bundle and has an executable regression proving that the producer case, oracle, task, and review material are absent.
- Transfer candidate: model every phase that executes submitted code as candidate execution, enumerate its complete readable and writable namespace, and supply only the minimum phase-specific inputs; make forbidden held-out paths executable negative assertions before candidate exposure.
- Limiting condition: some white-box tests necessarily link or inject held-out test logic at runtime; that does not justify exposing oracle solutions, controller records, sibling candidates, condition identity, or material unrelated to the exact phase.

### L-158 — Candidate-reported diagnostics are not independent oracle evidence

- Port status: unimplemented.
- Quality effect: a hidden test can appear to observe allocator use, destructor execution, thread affinity, cleanup, or another internal event while actually trusting a wrapper method the candidate can spoof, allowing the original defect to remain behind fabricated counters.
- Evidence: an independent auditor produced three candidates that passed the first unsafe-Rust validators while retaining the wrong allocator release path, raw deallocation without `Drop`, or an unsafe thread-affine transfer; each spoofed the candidate-owned diagnostic surface the hidden test trusted. The replacement cases observe governed fixture-owned signals directly, keep candidate code away from diagnostic control symbols, and reject the three seeded bypasses in the prospective counterfactual matrix.
- Transfer candidate: locate the authority that owns the event being claimed and collect evidence directly from that governed boundary; treat candidate-supplied summaries, counters, flags, logs, and health methods as untrusted projections unless the claim is specifically about that projection.
- Limiting condition: candidate-owned telemetry is valid product evidence when its accuracy is itself part of the public contract and is cross-checked against an independent source; it is not an independent oracle merely because a hidden test calls it.

### L-159 — Resetting shared diagnostics is not test isolation under parallel execution

- Port status: unimplemented.
- Quality effect: tests that reset process-global counters can corrupt each other's observation windows under the default parallel runner, creating nondeterministic failures or false passes even when each test is locally correct.
- Evidence: the first unsafe-Rust foreign-allocation fixture split global allocation/release assertions across hidden tests; concurrent resets and increments raced despite atomic counters. Combining the complete ownership sequence under one test-owned observation interval removed cross-test interference and produced byte-identical pre-freeze dispositions across unrelated working directories.
- Transfer candidate: give each concurrent test an instance-scoped evidence channel, or serialize the complete reset-trigger-observe interval when the production seam is necessarily global; atomics protect individual operations, not multi-step test transactions.
- Limiting condition: a runner configured and verified to execute the relevant tests serially may safely use a global reset protocol, but that execution policy is part of the evidence identity and must not be inferred from local runs.

### L-160 — Auto-trait reasoning must follow the value actually captured

- Port status: unimplemented.
- Quality effect: proving that a wrapper is `Send` or `Sync` does not prove that a closure or async block carries the wrapper; precise capture can select an inner field directly and bypass the wrapper's intended authority, cleanup, or trait boundary.
- Evidence: the first unsafe-Rust thread-affinity seed wrapped a `!Send` native value in a type with `unsafe impl Send`, but the worker closure captured the inner field precisely rather than the wrapper, so the intended transfer mechanism was not the mechanism actually compiled. Forcing whole-wrapper consumption made the seed exercise the claimed unsafe boundary before the case was admitted.
- Transfer candidate: inspect the compiler-observed capture and generated future/closure type at the actual move boundary; design ownership APIs that consume the complete capability rather than relying on lexical nesting to preserve an auto-trait claim.
- Limiting condition: an opaque function call or field privacy boundary can force whole-value transfer; verify that property in the selected edition/compiler instead of assuming it from source appearance.

### L-161 — Presence in current documentation does not establish stable availability

- Port status: unimplemented.
- Quality effect: durable guidance can accidentally prescribe nightly or experimental APIs when a current official documentation page displays them alongside stable items, making a foundational skill fail on the repository's declared stable toolchain.
- Evidence: Rust's current `Drop` documentation exposes `Drop::pin_drop`, but its stability marker identifies the API as nightly experimental. The unsafe-Rust revision therefore states the stable pinned-destruction contract without naming that method as generally available.
- Transfer candidate: before promoting a documented API into durable instructions, inspect its stability, feature gate, edition, platform, and minimum-version markers; preserve the invariant in timeless guidance and leave the selected mechanism conditional on the repository's executable horizon.
- Limiting condition: a repository explicitly pinned to nightly or an experimental feature may use it, but the feature gate and compatibility commitment belong in mutable project context rather than universal skill guidance.

### L-162 — Recovery boundaries must not catch intentional control-flow exits

- Port status: unimplemented.
- Quality effect: a broad recovery wrapper can convert a normal help request, declared exit code, cancellation signal, or framework control-flow exception into an operational failure, producing misleading diagnostics and preventing callers from distinguishing intended termination from broken execution.
- Evidence: the unsafe-Rust review controller wrapped its entry point with `except BaseException`; Python `argparse` implements `--help` as `SystemExit(0)`, so the controller printed `error: 0` and returned status 2 even though parsing succeeded and no review claim existed. Narrowing the recovery boundary to ordinary exceptions plus `KeyboardInterrupt` preserved failure terminalization while allowing `SystemExit` to retain its intended status, and a new subprocess regression test made the help path executable evidence.
- Transfer candidate: enumerate the language or framework's non-error control-flow exits before writing a top-level recovery boundary, catch only failures the boundary can validly terminalize, preserve intentional exit status and signal semantics, and test help, success, declared failure, interruption, and unexpected exception as separate paths.
- Limiting condition: a process supervisor may intentionally normalize every child termination into one external envelope, but it must preserve the original termination class and status as data rather than mislabeling successful control flow as an exception.

### L-163 — Thread creation is not resource readiness, and handle drop is not settlement

- Port status: unimplemented.
- Quality effect: a synchronous client can return a half-live worker-owned resource when thread creation is mistaken for resource construction, and it can abandon teardown when dropping a join handle is mistaken for waiting; thread affinity may be locally correct while the public lifecycle contract is still false.
- Evidence: all six unsafe-Rust R1 thread-affinity submissions removed the invalid `unsafe impl Send` transfer and constructed, used, and dropped the native session inside the worker, yet every held-out check failed because `SessionClient::new()` returned immediately after `thread::spawn` without observing readiness. The six artifacts collapsed to three source variants shared across conditions, all lacking a startup result. A prospective three-way repair round then produced 1/3 valid control artifacts, 0/3 valid V1 artifacts, and 2/3 valid V2 artifacts; exactly the three implementations with an explicit startup rendezvous passed, while all nine preserved owner-thread destruction and terminal join. Rust's stable thread contract returns a `JoinHandle` from spawn without saying the new closure has completed initialization, documents that dropping the handle detaches the thread, and makes `join` the completion boundary that includes thread-local destructors and synchronizes prior operations with its return.
- Transfer candidate: represent worker-owned resource startup, readiness or failure, command admission, shutdown request, owner-thread destruction, and settlement as distinct observable states; a synchronous constructor exposes the client only after readiness or failure, and a synchronous owner drop closes admission and reaches settlement without prescribing a particular channel or synchronization primitive.
- Limiting condition: an explicitly asynchronous or lazy API may expose a pending client before resource readiness, and an external executor may own settlement instead of a local join handle; the readiness, failure, and teardown semantics must then be explicit in that public contract and independently observable.

### L-164 — Repository-native analyzers need an effect boundary, not a read-only myth

- Port status: unimplemented.
- Quality effect: a helper that runs repository-native compilers, linters, build scripts, or procedural macros can present false assurance if it claims read-only execution while those tools still execute with repository authority and mutate the worktree.
- Evidence: the original local `rust-panic-audit` runner invoked Cargo and Clippy, ignored untracked files in its integrity snapshot, and could return `clean` after a `build.rs` wrote `side-effect.txt` into the repository. The hardened revision now names build-script authority explicitly, detects tracked-content changes plus non-ignored untracked path-set changes outside Cargo's target directory, and marks those effects incomplete instead of clean; a real integration case reproduces the side effect and now exits `2`.
- Transfer candidate: whenever a skill executes repository-native tooling, state the strongest true effect boundary, observe post-run mutations at the repository boundary the tool can actually touch, and reserve “read-only” for environments that enforce non-mutation outside the tool itself.
- Limiting condition: post-hoc mutation checks still do not prevent execution, roll back side effects, or observe ignored paths or edits to already-untracked files; true non-mutation requires external isolation or a disposable copy.

### L-165 — Reachability rules beat path names in lexical auditing

- Port status: unimplemented.
- Quality effect: lexical scanners that treat filenames or directory names as semantic truth can silently omit reachable production code and certify a scope as clean when compiled behavior still includes the omitted source.
- Evidence: the original `rust-panic-audit` scanner skipped every directory named `test` or `tests`, which excluded reachable `src/tests/mod.rs` production code. The hardened revision limits those path exclusions to root conventional test and fixture directories while keeping nested production modules in scope, and both unit and real integration tests now cover the case.
- Transfer candidate: use path heuristics only where the build or language contract makes them authoritative; when a nested path may still be compiled as production code, keep it in scope or derive exclusion from build metadata rather than naming convention alone.
- Limiting condition: some ecosystems do define test-only roots by convention and tooling contract, so a root path exclusion can be valid when that contract is explicit and verified against the selected target mode.

### L-166 — A selected member manifest is not a workspace-default alias

- Port status: unimplemented.
- Quality effect: tools that normalize a member `--manifest-path` back to workspace defaults can analyze the wrong package while still sounding precise, which corrupts both findings and clean conclusions.
- Evidence: the original `rust-panic-audit` package selection always fell back to `workspace_default_members` when the caller chose a non-root member manifest without explicit `--package` or `--workspace`. The hardened revision resolves the selected manifest against workspace package manifests and preserves that exact member when it is not the workspace root; a unit regression now locks this behavior.
- Transfer candidate: when a workflow accepts both workspace roots and member manifests, treat the selected manifest path as primary scope evidence and reconcile defaults only after proving the path designates the workspace root rather than a specific member.
- Limiting condition: repositories with generated manifests, symlink indirection, or tool-specific wrapper manifests may require an additional resolution layer, but that layer must still preserve the caller's exact selected package set rather than silently broadening or substituting it.

### L-167 — Boundary auditors must not absorb adjacent safety domains by lexical convenience

- Port status: unimplemented.
- Quality effect: a skill that broadens its lexical matcher beyond its declared evidence class can create false failures, blur composition boundaries, and teach the wrong retrieval surface even if the broader construct is genuinely risky.
- Evidence: the original `rust-panic-audit` scanner reported `unwrap_unchecked()` as a direct panic candidate even though current Clippy panic lints do not treat it as direct-panic evidence. The hardened revision removes `unwrap_unchecked` from this skill's direct matcher while adding `std::panic::panic_any` and `std::panic::resume_unwind`, which are actual direct panic interfaces according to Rust's primary panic documentation and the Clippy lint index.
- Transfer candidate: keep each skill's evidence surface aligned with the strongest authoritative signal for its declared boundary; route adjacent risks to the neighboring skill instead of broadening one skill merely because the syntax is easy to match.
- Limiting condition: a broader lexical surface can still be useful as advisory evidence when the skill explicitly presents it as cross-skill composition or a secondary note rather than as the primary pass/fail boundary.

### L-168 — Internal execution bounds are part of the tool contract, not just harness hygiene

- Port status: unimplemented.
- Quality effect: a repository helper that relies only on outer harness timeouts or memory limits can hang, leak descendants, or flood context when called directly, even if it appears safe inside one testing environment.
- Evidence: the original `rust-panic-audit` runner used unbounded `subprocess.run(... capture_output=True ...)` with no timeout, no descendant cleanup, and pretty-printed full JSON output. The hardened revision runs child commands in dedicated process groups, enforces per-command deadlines, caps combined output bytes, kills surviving descendants, and emits compact JSON by default; focused regression tests now prove timeout cleanup and output-limit behavior, and the full suite passes end to end.
- Transfer candidate: place deadlines, output bounds, and child-settlement rules inside the callable helper itself whenever the helper may be run outside the original harness, then keep the outer harness as an additional guard rather than the only one.
- Limiting condition: inner bounds still need values that fit the task domain, and some workflows legitimately require caller-selected overrides; those overrides belong to explicit parameters and must be reported as part of the evidence identity.

### L-169 — Producer-context validation does not prove the delivered validator boundary

- Port status: unimplemented.
- Quality effect: a seed/oracle pair can pass when the validator runs beside its source case yet fail or leak held-out material when the production harness delivers only a scrubbed bundle, so local correctness can certify an interface the real evaluator never provides.
- Evidence: the first rust-panic diagnostic validator read seed and hidden files relative to `__file__` and passed direct admission because the producer case directory was present. The production harness intentionally copied only `validate.py` and streamed private seed/hidden bytes on stdin, causing the same oracle to fail before candidate exposure. Converting the validator to that exact private-input interface restored the required seed-fail/oracle-pass split in production.
- Transfer candidate: admit evaluator logic through the exact packaging, mounts, inputs, environment, executable path, and isolation boundary used after delivery; treat producer-side runs as development diagnostics unless executable evidence proves boundary equivalence.
- Limiting condition: when producer and delivered execution are content-addressed instances of the same declared interface and namespace, one run may cover both, but that identity must include privileged inputs and path visibility rather than source bytes alone.

### L-170 — Executing candidate builds makes build surfaces part of the checker threat model

- Port status: unimplemented.
- Quality effect: governed source and hidden tests do not remain authoritative when validation executes candidate-controlled build scripts, compiler configuration, toolchain selectors, symlinks, macros, or test processes in a writable tree before observing the claimed behavior.
- Evidence: an independent gate found that the first rust-panic validator allowed added `build.rs` and `.cargo/config.toml` files to rewrite production source or the injected hidden test during Cargo execution. The admitted case rejects symlinks, non-regular entries, all `.cargo` paths, conventional build scripts, and toolchain selectors before copying or running the submission; it also checks governed files and direct constructs before Cargo and runs the exact hidden target before candidate-authored tests. Independent counterexamples for build scripts, Cargo config, and symlinks now fail at the pre-execution surface gate.
- Transfer candidate: enumerate every code/configuration surface the selected build and test commands can execute or resolve, close or govern those surfaces before the first execution, order authoritative observations ahead of untrusted code, and prove the boundary with one counterexample per materially distinct hook class.
- Limiting condition: a hermetic build service may intentionally execute arbitrary submitted build logic when it provides a separate immutable source snapshot, private-test custody, network/process/filesystem containment, and outcome observations that candidate code cannot rewrite; the authority still belongs to that enforced boundary rather than to prose.

### L-171 — Test-profile behavior is not production-profile behavior

- Port status: unimplemented.
- Quality effect: an implementation can satisfy every debug/test check while retaining the production defect behind `cfg(test)`, `debug_assertions`, optimization-sensitive behavior, panic strategy, feature selection, or another profile-dependent branch.
- Evidence: the first rust-panic hidden check used only ordinary `cargo test`. An independent reviewer constructed the valid concern that tag `1` could return the typed error only when debug assertions were enabled and panic through an unscanned `assert!` or indexing path in production. The admitted hidden check runs the exact integration target with `--release --no-default-features`, and a concrete `assert!(cfg!(debug_assertions))` candidate passes the narrow lexical check but fails the release hidden behavior while the oracle still passes.
- Transfer candidate: derive validation modes from the deployed contract, exercise every materially distinct build/profile/feature/target selection needed by that contract, and use behavioral counterexamples rather than trying to enumerate every syntax that could encode a profile-dependent defect.
- Limiting condition: a library explicitly supported only in one test-equivalent profile may need no cross-profile check; that support horizon must be a declared product constraint, not inferred from the evaluator's convenient default.

### L-172 — Mode-aware identities must be computed after mode finalization

- Port status: unimplemented.
- Quality effect: hashing an artifact before applying its final executable/read-only modes creates an identity that fails immediately after freezing and can obscure whether content or authority changed.
- Evidence: the rust-panic instrument's first manual lock hashed the writable tree and then removed write bits; the harness digest includes POSIX modes, so the lock mismatched without any content edit. The admitted case delegates freezing to the production `check_case.py --freeze` path, which normalizes modes first, computes the digest over the final tree, updates the excluded lock record, and verifies read-only state.
- Transfer candidate: define which metadata is identity-bearing, finalize it before hashing, and use the production freezer or a conformance-tested equivalent; verify the identity after every custody transition without recursively modifying the admitted tree.
- Limiting condition: content-only identities intentionally ignore permissions when execution and authority are governed elsewhere, but that omission must be explicit and cannot support claims about executable or immutable state.

### L-173 — A checker must bind the requested property, not the oracle's chosen mechanism

- Port status: unimplemented.
- Quality effect: a deterministic validator can reject every correct artifact when it silently turns the oracle's file layout, helper choice, sequence, or data structure into a requirement the task never imposed; unanimous failure then measures checker overconstraint rather than agent quality.
- Evidence: rust-panic R1 asked for a regression test under `crates/gateway/tests/`. All nine agents added a behaviorally discriminating test to the existing integration-test file and repaired the production behavior, but the validator governed that file byte-for-byte and accepted only a newly added file because the oracle happened to use one. Both blinded reviewers exposed the mismatch after commitment. The R1 machine aggregate was invalidated, and prospective R2 accepts any changed or added integration test whose candidate version fails on the seed while an independent hidden release test protects the documented public contract. The unchanged R1 artifacts all pass the R2 checker, as does the structurally different separate-file oracle.
- Transfer candidate: derive each check from an explicit required property, admit materially different compliant alternatives before exposure, and keep preservation invariants in independent hidden observations rather than freezing an editable artifact solely because the oracle left it unchanged; when a post-reveal mismatch appears, preserve the round, invalidate the affected claim, and allocate fresh identities under a corrected prospective instrument.
- Limiting condition: a maker may legitimately require an exact filename, API, algorithm, or sequence; the validator may bind that mechanism when the requirement is explicit and decision-relevant, not merely because one reference implementation uses it.

### L-174 — Review custody must include the candidate's real output contract

- Port status: unimplemented.
- Quality effect: a blinded reviewer can falsely report a missing handoff, explanation, citation, migration note, or generated artifact when the execution captured it but the publication layer omitted that output class from the anonymous bundle.
- Evidence: both rust-panic R2 reviewers said no handoff artifact was supplied and therefore could not judge the task's required scope/evidence/residual-risk report. Post-reveal controller records show every run ended with a substantive final agent message, including manifest, package, target/features, findings, checks, and residual-risk content; the publisher exposed only the project, patch, validator evidence, task, and rubric. Handoff-absence judgments were excluded from interpretation because reviewers never received the candidate-owned output.
- Transfer candidate: trace every required output from execution capture through anonymization into the reviewer interface, publish a bounded immutable representation of each candidate-owned output class, and add a preflight fixture whose only differentiating evidence lives in the final response; do not let controller logs become a post-reveal substitute for blinded review.
- Limiting condition: when the product contract is exclusively the repository artifact and explicitly excludes prose or external outputs, the final response may be irrelevant; the review brief must then omit any dimension that the bundle cannot contain.

### L-175 — Portability claims require a declared standards and deployment horizon

- Port status: unimplemented.
- Quality effect: timeless-sounding guidance can become factually wrong when a standard adopts an extension while deployed implementations remain split, causing agents either to reject a conforming feature or to use it on older targets that do not support it.
- Evidence: the shell skill said unconditionally that `pipefail` was not POSIX and forbade it in POSIX sh. POSIX.1-2024 now specifies pipeline status with `pipefail`, while the skill's concrete dash fixture still lacks that option. The revision binds use to the repository's declared shell/version matrix and makes the dash eval's exclusion target-specific.
- Transfer candidate: express portability against both a named specification horizon and the actual deployment matrix; when those differ, distinguish standards conformance from ecosystem availability and test the exact targets instead of promoting either into a universal rule.
- Limiting condition: a repository pinned to one implementation can use its supported behavior without a broader standards matrix, but it must not relabel that implementation choice as universal portability.

### L-176 — An exclusion without an available route is a retrieval dead end

- Port status: unimplemented.
- Quality effect: telling an agent to route a domain to nonexistent guidance produces either refusal or improvised use of a nearby language whose superficially similar syntax has different semantics.
- Evidence: the shell skill excluded zsh and fish and directed agents to their “own language guidance,” but the repository ships no such skills and its trigger probes explicitly prevented this skill from activating. The revision now activates for substantive shell work, uses official interpreter documentation and repository tests as the bounded fallback, applies only cross-shell contracts, and forbids fabricated Bash compatibility or claims of dedicated coverage.
- Transfer candidate: before excluding a near-neighbor, verify the promised route exists in the delivered environment; otherwise supply an honest, bounded fallback and make any new specialized skill conditional on demonstrated recurring demand and maintenance value.
- Limiting condition: stopping is still correct when no authoritative source or safe verification surface is available; the fallback preserves a route to evidence, not permission to guess.

### L-177 — Parallelism needs one aggregate budget and complete settlement

- Port status: unimplemented.
- Quality effect: per-loop throttles and worker counts can multiply across nested jobs, while fire-and-forget or fail-fast returns can leave admitted work, output pipes, locks, and descendants unresolved even when latency improves.
- Evidence: PowerShell documents that each `ForEach-Object -Parallel -AsJob` instance can run up to its own throttle, so several outer jobs multiply total concurrency. The previous shell guidance merely said to wait for owned jobs. The revision adds a conditional lifecycle reference requiring one aggregate concurrency, queue, and output budget; admission closure before teardown; an input-to-handle ledger; stream draining; and terminal observation of every admitted unit.
- Transfer candidate: treat admission, active work, queued work, output retention, cancellation, and settlement as one resource system; optimize only after naming the user-visible constraint and preserve a sequential path when coordination or contention dominates.
- Limiting condition: a durable external scheduler may own admission and settlement, but the script must then hand off through an observable accepted-work contract instead of silently abandoning local handles.

### L-178 — A process handle does not prove descendant closure

- Port status: unimplemented.
- Quality effect: killing or waiting for a direct PID, shell job, PowerShell job, runspace, or remote job can leave grandchildren alive or report completion before the intended execution domain is settled.
- Evidence: POSIX `wait` observes children known to the current shell environment; Bash jobspec support depends on job-control mode; Bash signal behavior changes when the shell and child share a process group; and PowerShell distinguishes `Start-Process -Wait`, `Wait-Process`, jobs, remoting, and platform-specific child lifetime. The revised shell guidance names these as distinct ownership domains and requires a mechanism whose cancellation closure matches the declared contract.
- Transfer candidate: define the owned execution closure before choosing wait or cancellation primitives, retain the authority needed to settle that closure, and verify absence of orphaned work after success, failure, timeout, and interruption.
- Limiting condition: when descendants intentionally outlive the caller, detached survival is part of the public contract and needs an explicit external owner rather than cleanup assertions.

### L-179 — “Argument list” is not evidence of an argv boundary

- Port status: unimplemented.
- Quality effect: an API named `ArgumentList` can still join values into a command string, and a shell can switch parsing models by version, platform, executable type, or wrapper, so array-shaped source code may preserve quoting bugs or injection authority.
- Evidence: Microsoft documents platform- and version-sensitive native argument passing in PowerShell 7.3+, legacy raw-command behavior for Windows batch and command scripts, and `Start-Process -ArgumentList` joining values into one command line. The revised skill separates direct `&` invocation, `Start-Process`, and `cmd.exe`/batch passage and requires an argv-observing probe at every supported boundary.
- Transfer candidate: identify the final parser and operating-system invocation interface, then verify the arguments received rather than inferring structure from the caller API's type or name; avoid raw command-string boundaries for untrusted values when a real structured interface is available.
- Limiting condition: a command-string interface can be valid for trusted, fixed grammar when exact parser-specific quoting is deliberate and regression-tested; it is not interchangeable with structured execution.

### L-180 — Emitting an error is not the same as failing for the caller

- Port status: unimplemented.
- Quality effect: code can print error-looking output while leaving caller-visible success, or can turn benign native stderr into failure, when stream records, control flow, automatic variables, and host process exit are collapsed into one error model.
- Evidence: PowerShell distinguishes `Write-Error`, `$PSCmdlet.WriteError()`, `throw`, `$?`, `$LASTEXITCODE`, native stderr redirection, and `pwsh -File` versus `pwsh -Command`; several behaviors changed across PowerShell 7.2 and 7.4. The revised reference and evals require the function and entry-point contract to be tested from the caller across supported invocation forms and versions.
- Transfer candidate: specify failure at the interface that consumes it—returned value, typed error, exception/control transfer, stream record, process status, or protocol envelope—and test that observable rather than treating diagnostic text as proof.
- Limiting condition: interactive commands may intentionally report recoverable non-terminating errors while continuing; success and failure semantics should follow that established interface rather than a universal fail-fast policy.

### L-181 — Deterministic audit observations need target authority before they become defects

- Port status: unimplemented.
- Quality effect: automatically “fixing” a generic checker observation can violate the target repository's explicit delivery contract even when the check accurately reports a portable divergence.
- Evidence: the Skill Auditor reference checker correctly observed that five shell references use `<skills-file-root>` instead of plain relative paths and labeled the prefix nonportable under its open-standard lens. This repository's governing `AGENTS.md` explicitly permits and defines that placeholder for skill-local resources, and strict Codex/Claude validation plus both conversion round trips preserved the links. The observation is true, but it is not a defect under the stronger applicable authority.
- Transfer candidate: make deterministic reporters emit facts with source and scope, then require semantic interpretation against target authority and the actual delivery boundary before assigning severity or triggering mutation.
- Limiting condition: on a target that adopts only plain relative Open Agent Skills paths and has no host placeholder contract, the same observation may identify a real portability defect.

### L-182 — Signal tests must control inherited dispositions, not just handlers installed by the subject

- Port status: unimplemented.
- Quality effect: a cancellation test can falsely report that a program ignores an interrupt when the test launcher itself started the background process with that signal ignored and the child inherited the disposition across `exec`.
- Evidence: the shell diagnostic's first interrupt probe launched a Bash fixture as an asynchronous job from a non-interactive Bash controller. Bash deliberately makes asynchronous commands ignore `SIGINT` and `SIGQUIT` when job control is unavailable; the fixture's descendants inherited that state, so signaling the owned process group did not exercise the fixture's intended trap. The admitted probe resets `SIGINT` and `SIGTERM` dispositions in the child immediately before `exec`.
- Transfer candidate: make signal disposition, mask, process group, session, controlling terminal, and launcher behavior part of the test fixture; independently prove that the injected signal reaches a minimal control subject before attributing the response to the program under test.
- Limiting condition: inherited ignored dispositions may be the actual deployment contract for daemonized or supervised work, in which case the test should preserve them and assess the program against that environment rather than normalize them.

### L-183 — Bounded final output does not prove bounded live retention or continued drainage

- Port status: unimplemented.
- Quality effect: a program can truncate its final report yet accumulate every byte in memory, or stop reading at the reporting cap and deadlock writers on full pipes; output-length assertions alone therefore admit both resource exhaustion and hangs.
- Evidence: the shell diagnostic separates two hidden observations: FIFO drainers with a bounded retained prefix and complete byte counters test continued consumption, while a strict multi-megabyte writer under a file-size/resource limit makes premature pipe closure and masked writer failure observable. The earlier output-only oracle could not distinguish these behaviors.
- Transfer candidate: independently bound admission, active work, in-flight buffers, retained output, and published output; test producers that exceed the retention cap, require drainage through terminal status, and make any writer-side broken pipe or nonzero status affect the aggregate result.
- Limiting condition: a deliberately backpressured protocol may stop reading to enforce a hard producer contract, but the caller-visible failure and cancellation closure must then be explicit and tested instead of presented as successful truncation.

### L-184 — Delivered-boundary validation must consume the exact private payload supplied to the worker

- Port status: unimplemented.
- Quality effect: a validator that reopens a controller-local path can pass a different tree from the one actually mounted, copied, anonymized, or delegated, invalidating isolation and allowing source-state drift to masquerade as candidate behavior.
- Evidence: the shell diagnostic's first validator accepted a local project path even though the execution harness delivered the project as a private input payload. The admitted interface consumes the candidate tree from the delivered stdin boundary, identifies that payload, and hashes the frozen instrument and treatments separately.
- Transfer candidate: bind validation to the same immutable bytes and interface the worker received; record source, delivered, and observed identities when translation is unavoidable, and fail closed when the boundary cannot be reconstructed.
- Limiting condition: a shared immutable content-addressed store can safely be reopened by identity when both producer and consumer verify the same object and no mutable path is treated as authority.

### L-185 — Shell-native parameter names can silently mutate process environment

- Port status: unimplemented.
- Quality effect: a seemingly local variable assignment can alter exported execution state when the shell exposes special tied parameters, causing subsequent tool lookup or subprocess behavior to fail far from the assignment.
- Evidence: in zsh, `path` is a special array tied to `PATH`; assigning a task-local value to `path` replaced executable search paths during harness work. Renaming the variable restored command discovery without any toolchain change.
- Transfer candidate: avoid generic names that collide with the active shell's special parameters, run automation under a declared shell, and pass execution-critical values as explicit arguments rather than relying on mutable ambient state.
- Limiting condition: intentionally assigning the special parameter is appropriate when changing command resolution is the objective, but it should be scoped and followed by an observable lookup check.

### L-186 — Long-running evaluations must re-resolve mutable installed capabilities at execution boundaries

- Port status: unimplemented.
- Quality effect: an evaluation can silently follow stale protocols or invoke vanished artifacts when a plugin cache changes between planning and execution, even though the source repository and task appear unchanged.
- Evidence: the split-testing capability visible at campaign planning was version 1.0.1; before the shell round executed, that cache entry disappeared and 2.0.0 became installed with a different custody protocol and helper binary. The round was reinitialized prospectively under the completely reread 2.0.0 instructions rather than mixing versions.
- Transfer candidate: resolve and hash instruction, executable, and dependency identities immediately before commitment and again before each authority-changing boundary; if they drift before exposure, restart prospectively, and if they drift after exposure, retain the attempt and classify the effect without silently switching protocols.
- Limiting condition: content-addressed, immutable dependencies mounted for the full run need no repeated discovery, but their availability and identity still belong in the evidence record.

### L-187 — Evaluation publication must carry the complete candidate-owned output contract

- Port status: unimplemented.
- Quality effect: fixing a known publication omission only in prose leaves future rounds vulnerable to the same false-negative review; the harness must make the output class a first-class, hashed artifact.
- Evidence: the shell harness now extracts the terminal agent message into `artifact/final-response.md`, includes it in evidence identity, and has a unit test proving publication of that boundary. This operationalizes the rust-panic lesson in L-174 before the shell commitment rather than correcting reviewer interpretation after reveal.
- Transfer candidate: turn every demonstrated custody lesson into an executable invariant at the earliest shared layer, with a discriminating test whose only decisive evidence crosses the repaired boundary.
- Limiting condition: the added artifact is useful only when the task's real output includes a handoff; repository-only tasks should explicitly exclude prose dimensions rather than publish irrelevant text.

### L-188 — Blinding must scan native handoffs, not just controller-authored labels and paths

- Port status: unimplemented.
- Quality effect: opaque directory names do not preserve blinding when an executor repeats a private condition, run ID, source path, or treatment digest inside its final response or artifact; one leak can let a reviewer infer an entire grouped comparison.
- Evidence: Split Testing 2.0 generated opaque shell-round identifiers, but `control-r1` appeared twice in one retained `final-response.md`. The prospectively frozen view builder rejected the package before reviewer launch. Native sealed evidence stayed unchanged; a second derived view replaced exact controller IDs with `[opaque-run-id]`, disclosed that transformation, and exposed no private mapping to reviewers.
- Transfer candidate: enumerate identity-bearing tokens before exposure, scan every candidate-owned output class after native sealing, fail before review on a match, retain the native payload, and permit only a mechanically narrow, uniformly applied, disclosed derived-view redaction whose private map remains outside the reviewer boundary.
- Limiting condition: free-form content can reveal identity semantically without containing an enumerated token; high-stakes blinding may need an independent leak reviewer or stronger generation isolation, while an unblinded evaluation needs no redaction ceremony.

### L-189 — Preservation checkers must observe before they normalize permissions

- Port status: unimplemented.
- Quality effect: a validator can manufacture the exact mutation it later attributes to a candidate, producing universal false failures and misleading semantic reviewers even when patches stayed within scope.
- Evidence: the shell seed fixed `.runtime.lock` at mode 0444. The execution harness made the delivered tree owner-writable, and the hidden validator again called `make_owner_writable(candidate)` before comparing governed-file modes. Every condition therefore reported a 0644 violation, while no candidate patch touched the file. The governed-file observation and aggregate pass bit were invalidated after reveal; separable lifecycle and test observations remained usable.
- Transfer candidate: observe protected bytes and metadata at the delivered boundary before any normalization; when tools need writable copies, exclude protected metadata from the claim or restore and verify it explicitly. Admission must include a fixture whose decisive invariant is read-only mode and must assert that both oracle and structurally different valid artifacts pass the entire checker.
- Limiting condition: when permissions are deliberately outside the artifact contract, use a content-only identity and do not emit permission-preservation findings.

### L-190 — A separable invalid observation need not erase an entire retained round

- Port status: unimplemented.
- Quality effect: treating one checker defect as either harmless or globally fatal discards valid evidence or launders invalid evidence; both responses obscure what was actually learned.
- Evidence: the shell validator's governed-file mode check was invalid, which also made its aggregate `passed` field unusable. Its independently reported hidden lifecycle, regression discrimination, syntax, submitted-test, generated-file, residue, and non-mutation checks did not depend on the mode comparison and remained content-addressed. The report excludes the bad dimension, preserves every attempt, and narrows the decision claim instead of rerunning or rewriting history.
- Transfer candidate: design instruments with independently attributable observations, record dependency edges among checks, invalidate the smallest affected claim after a demonstrated defect, and require a fresh prospective round only when the defect could alter allocation, exposure, behavior, or the decision-relevant contrast.
- Limiting condition: when checks share mutated state, stopping rules, adaptive prompts, or a common parser whose defect can affect all outcomes, the evidence may not be separable and the round can be globally uninterpretable.

### L-191 — Hand-written option parsers need a progress invariant

- Port status: unimplemented.
- Quality effect: consuming an option and its operand with `shift N` before proving the operand exists can leave the argument count unchanged on failure, causing malformed invocations to loop forever instead of returning the documented usage status.
- Evidence: both blinded shell reviewers independently noticed the Bash pattern `value=${2-}; shift 2`. A bounded post-reveal probe confirmed seven of nine submissions hung on a lone `--jobs`; only two returned status 64. The final skill now requires every option-loop branch to advance or exit, validates operands before shifting, and adds a focused eval for missing, empty, repeated, option-looking, and `--` boundaries.
- Transfer candidate: express parser progress as an invariant, validate arity before state mutation, and test malformed inputs under a deadline with caller-visible status and streams; apply the principle to any parser that can accept input without consuming it.
- Limiting condition: parser combinators or framework parsers may enforce progress and arity structurally, but their error mapping and deployed invocation boundary still need verification.

### L-192 — Frozen effective inputs can preserve operability through live dependency rollback

- Port status: unimplemented.
- Quality effect: a long evaluation can become impossible to close when the installed plugin cache removes the exact helper after outputs exist; switching to whatever is now installed would change the custody protocol after exposure.
- Evidence: Split Testing 2.0.0 was committed and captured as an effective input for every shell unit, then the live cache rolled back to 1.0.1 before reviewer sealing. The repository's current 2.0.0 binary had a different digest, but the retained effective-input object remained executable and byte-identical to the committed helper, allowing seal, close, status, receipt, and reveal without a protocol substitution.
- Transfer candidate: capture execution-critical tools as immutable effective inputs before work begins, verify executable mode and digest, and document a controller recovery route that invokes the retained object when the ambient installation disappears; never treat a matching version label as identity.
- Limiting condition: retained executables can depend on uncaptured loaders, libraries, kernels, services, or credentials; capture or identify those dependencies when their drift could change behavior.

### L-193 — Reviewer conclusions must be reconciled with retained atomic observations

- Port status: unimplemented.
- Quality effect: a strong semantic review can still miscount passes, conflate an aggregate bit with its components, or summarize a group inconsistently; copying the narrative directly into a decision turns a review aid into unverified authority.
- Evidence: both shell reviewers correctly preferred the anonymous revision group and identified the same material runtime failures, but one summary described two discriminating revision suites while retained validator records show all three rejected the seed. Interpretation used the machine count, preserved both judgments, and excluded reviewer claims derived from the invalid governed-mode check.
- Transfer candidate: require reviewers to cite native evidence, preserve their free-form judgment, then mechanically reconcile decisive counts and identities against atomic records after reveal; report disagreements and corrections rather than silently editing reviewer output.
- Limiting condition: machine records do not override semantic judgment on properties they do not observe; reconciliation establishes factual inputs and provenance, not a universal scoring hierarchy.

### L-194 — Equal pass counts do not erase semantic quality differences, but neither do they prove effectiveness

- Port status: unimplemented.
- Quality effect: reducing a comparative evaluation to aggregate pass counts can hide materially safer lifecycle structure and better regression coverage, while promoting reviewer preference into a causal win can overstate evidence when both groups pass the same executable observations.
- Evidence: across 30 Java executions, control and the frozen skill treatment each passed 12 of 15 validators. In the corrected process round, both reversed-order reviewers preferred treatment on cleanup, ownership, and verification quality; in the broader confirmation round, reviewers found mixed per-sample advantages despite universal passes. The decision retains the semantic findings but explicitly reports no machine pass-rate separation.
- Transfer candidate: preserve atomic executable outcomes and independent semantic judgments as distinct evidence classes; interpret convergent qualitative findings without manufacturing a score, and phrase effectiveness claims at the narrowest level the contrast actually separates.
- Limiting condition: when the evaluation's success contract is wholly captured by a valid executable oracle, equal outcomes can be a genuine tie; semantic complexity should not override the contract merely because it looks more sophisticated.

### L-195 — Interrupt propagation and interrupt-status preservation are separate observables

- Port status: unimplemented.
- Quality effect: Java code can correctly propagate `InterruptedException` while violating an API that separately promises the caller will observe its interrupt flag set; conversely, universally restoring before ordinary propagation can invent a contract the platform does not require.
- Evidence: the first Java process fixture required both propagation and restored caller-visible status. All six control/treatment submissions caught the exception for cleanup and rethrew it with the flag still cleared, so all failed the same hidden lifecycle check. The revised skill now makes restoration conditional on the API contract and asks tests to assert the flag when it is part of that contract.
- Transfer candidate: decompose cancellation and interruption into exception/control transfer, status or token state, owned-work settlement, cleanup, and caller-visible result; state and test each required observable independently instead of treating one as proof of the others.
- Limiting condition: a Java method that directly propagates `InterruptedException` normally need not restore the flag unless its contract requires it; translating or swallowing interruption generally does require restoration or another explicit terminal policy.

### L-196 — Authority-changing wrappers are protocol boundaries, not convenience aliases

- Port status: unimplemented.
- Quality effect: invoking an underlying state mutation can produce the correct domain result while bypassing admission, receipt, audit, or custody effects that only the wrapper owns; a non-idempotent wrapper may then be unable to reconstruct those effects.
- Evidence: after both Java corrected-process reviewers were sealed, the controller directly invoked the frozen Split Testing helper's `reveal` command. The mapping and judgments were valid, but `reveal_round.py` refused the already-revealed workspace and could no longer create its canonical reveal admission. A separate recovery record preserves hashes and narrows the claim without fabricating the missing receipt.
- Transfer candidate: classify wrappers that add authority, custody, validation, accounting, or publication as the only supported mutation interface; expose read-only low-level commands separately, and make wrapper recovery idempotent or provide a verified receipt-reconstruction command when safe.
- Limiting condition: a wrapper that adds no observable or authoritative semantics may be a convenience alias, but that equivalence should be executable and documented rather than inferred from shared underlying code.

### L-197 — A noncompiling test is an unavailable observation, not weak evidence

- Port status: unimplemented.
- Quality effect: semantic reviewers can find a production patch plausible while the submitted regression never enters the executable boundary; counting that as partial correctness launders untested behavior and hides instruction failures in imports, scopes, compiler versions, or diagnostics.
- Evidence: the Kotlin rounds repeatedly produced coroutine tests that failed before execution—unscoped `launch`, suspend calls outside a coroutine, a wrong `Channel` package, and warnings promoted to errors. Hidden behavior checks could not run because the validator compiled submitted tests into the same source set. The reports retain static observations but classify the behavioral result as unavailable/failing.
- Transfer candidate: admit the verification artifact through the exact deployed compiler, runner, warnings, feature gates, and dependency surface before consuming its behavioral claims; represent compile failure separately from observed product failure while allowing either to reject the submission contract.
- Limiting condition: a separately compiled hidden suite can still establish production behavior when public tests fail, but it does not retroactively make the submitted regression usable or satisfy a task that requires maintainable tests.

### L-198 — Cancellation teardown must break the wait-for-unblock cycle before joining

- Port status: unimplemented.
- Quality effect: structured syntax can still deadlock when cancellation waits for blocking work to finish and the blocking work can finish only after a resource is closed by cleanup scheduled after that wait.
- Evidence: multiple Kotlin owned-reader submissions used `runInterruptible`, `await`, or `join` before guaranteed close. The instrument included a source that ignores thread interruption and returns only after `close`; those implementations could not reach cleanup. The revised skill initiates the actual unblock action at cancellation onset and only then awaits the owned terminal boundary.
- Transfer candidate: draw the terminal dependency rather than trusting a cancellation primitive's name; for each owned operation identify what makes it stop, issue that action before joining, preserve the initiating terminal cause, and deterministically prove no owned work remains.
- Limiting condition: when the underlying operation is documented and tested to stop on the cancellation primitive itself, a separate close-before-join action may be unnecessary or harmful; the actual operation contract decides.

### L-199 — Cancellation has a pre-acquisition boundary and a terminal identity boundary

- Port status: unimplemented.
- Quality effect: code can honor cancellation eventually yet still perform forbidden side effects before noticing an already-aborted request, or can complete with a newly synthesized cleanup error instead of the exact reason callers use for identity-sensitive control flow.
- Evidence: Node reviewers found child wrappers that launched despite a pre-aborted signal and stream implementations that failed exact abort-reason checks. The revised skill checks cancellation before acquisition when the contract promises no side effects, preserves `signal.reason` identity when contractual, and keeps later teardown failures from silently replacing the primary terminal cause.
- Transfer candidate: specify cancellation at both boundaries: what may be acquired or started after cancellation is already known, and which exact value/type/status crosses the terminal interface after cleanup; separately prove owned-resource settlement.
- Limiting condition: an API may deliberately acquire enough state to report or compensate an already-canceled request, and some interfaces promise only an equivalent error category rather than object identity; follow the declared contract.

### L-200 — A test file outside the authoritative runner is documentation, not regression protection

- Port status: unimplemented.
- Quality effect: a focused consumer test can look excellent in a patch and even pass when manually invoked while every normal CI and developer workflow silently omits it.
- Evidence: multiple Node dual-package submissions added strong external-consumer files that were not selected by `tests/run.sh`; reviewers had to distinguish their manual value from default-path verification. Other lifecycle tests lacked a reliable terminal marker or listened on the wrong object, so mere process completion did not establish the intended assertion.
- Transfer candidate: require every claimed regression to be reached by the repository's authoritative test command, prove the test reaches its decisive assertion, and show it rejects the seed defect as well as accepting the repair.
- Limiting condition: intentionally manual conformance or release probes can be valid artifacts, but their invocation condition must be part of the release contract and they must not be represented as default regression coverage.

### L-201 — Validate required presence before value semantics or identity normalization

- Port status: unimplemented.
- Quality effect: code can correctly normalize identifiers, preserve present-null, reject duplicates, and still accept malformed data because it reads/defaults/skips a record before proving that a required field exists.
- Evidence: all six PHP array-identity submissions failed the independent missing-payload contract. Their public tests explicitly accepted a missing payload as absent output or present-without-value, so strong collision coverage for `0`, `false`, empty string, integer strings, and `null` could not rescue the wrong schema boundary.
- Transfer candidate: order validation by dependency: prove required structure/presence, then validate type and canonical identity, then enforce duplicates and insert; include missing, present-null, defaulted, and malformed cases as separate regression observations.
- Limiting condition: optional fields or tolerant ingestion may deliberately default or skip missing values, but that policy must be explicit and should not bypass validation of other required fields or identities.

### L-202 — Direct-child settlement and pipe EOF do not establish descendant settlement

- Port status: unimplemented.
- Quality effect: a process wrapper can drain both streams, reap the leader, and still return while an owned descendant executes after closing inherited descriptors; conditional escalation tied only to communication timeout misses that state.
- Evidence: Python confirmation reviewers identified several wrappers that sent group KILL only when the TERM-phase `communicate()` timed out. Their supplied fixture kept a pipe open and passed, but a descendant that closes pipes before ignoring TERM would let communication finish and suppress escalation. Both reviewers treated unconditional post-grace group authority in other samples as the safer contract.
- Transfer candidate: define terminal settlement over the actual ownership boundary—leader, process group, job object, cgroup, container, or supervisor—and test a descendant that releases observation channels while continuing work; keep escalation authority valid independently of pipe/leader settlement.
- Limiting condition: signaling a process group after the leader is reaped can race identifier reuse; the controller must retain valid authority or use a stronger platform primitive rather than blindly sending to a stale numeric ID.

### L-203 — Failure cancellation must stop new admission from becoming new execution

- Port status: unimplemented.
- Quality effect: a worker pool can release its producer, preserve the primary exception, and join every thread yet still execute all queued work after failure, delaying terminal observability and triggering side effects the cancellation policy intended to prevent.
- Evidence: Ruby confirmation reviewers found queue implementations whose surviving workers continued popping and running pending operations after another worker recorded the primary failure. Fast fixtures eventually joined and passed, but a slow or blocking queued operation could indefinitely obstruct shutdown. The refined skill separates discard/accounting from execution-drain policy.
- Transfer candidate: after the first terminal failure, close admission, unblock producers, prevent new operations from starting unless drain-by-execution is explicit, account for discarded items, and settle every worker before exposing the primary failure.
- Limiting condition: transactional, audit, or best-effort batch APIs may intentionally finish already admitted work after one failure; that collect-all/drain contract must be explicit and should not be mislabeled cancellation.

### L-204 — Exact-limit output is not truncation without evidence beyond the limit

- Port status: unimplemented.
- Quality effect: marking an output truncated merely because retained bytes equal capacity produces false loss signals for an exactly-at-limit stream and can change caller retries, diagnostics, or billing.
- Evidence: a Ruby process-runner sample passed common checks but reviewers identified a false truncation flag at the exact bound. The refined instruction requires observing at least one byte beyond retained capacity—while continuing the declared drain policy—before setting truncation.
- Transfer candidate: separate retained length from total observed length; use a one-byte overflow probe or full byte counter and test below, exactly at, and above the bound, including EOF and concurrent failure.
- Limiting condition: a protocol may define a hard maximum where exactly filling the buffer is itself a violation, but then the contract is capacity admission rather than observational truncation and should be named accordingly.

### L-205 — A winning control outcome and terminal cleanup are orthogonal state

- Port status: unimplemented.
- Quality effect: a cancellation path can wait for complete cleanup yet still return success or the wrong error when the raw operation promise competes with a cancellation branch that cannot settle until that same operation ends.
- Evidence: all six JavaScript timeout R3 submissions passed the common terminal-join validator. Reviewer probes that made abort cleanup fulfill or reject with a different error reproduced false success in one treatment sample and wrong-error rejection in one control sample; both defects were hidden when cleanup always rejected with `signal.reason`.
- Transfer candidate: when a control outcome must dominate after winning, record it immediately, join the operation independently as cleanup, then publish the recorded outcome; test cleanup fulfillment and an unrelated cleanup rejection as distinct cases.
- Limiting condition: some APIs intentionally let a later operation result or cleanup failure supersede cancellation; that precedence must be an explicit public contract rather than an accidental promise-race ordering.

### L-206 — Borrowed-buffer overlap exists even when storage does not move

- Port status: unimplemented.
- Quality effect: a transactional resize implementation can pass allocation-failure and relocation tests yet still invoke undefined behavior when a same-buffer append fits in spare capacity and uses `memcpy` on overlapping ranges.
- Evidence: blinded C review found paired passing artifacts whose public tests forced reallocation for every alias case; both retained `memcpy` on the no-growth borrowed path. A separate slack-pointer probe also distinguished implementations that validated only logical bytes from those that treated unused capacity as external input.
- Transfer candidate: when an interface permits input borrowed from destination storage, test growing and non-growing overlap separately, validate against logical extent before mutation, and use a movement operation whose overlap contract matches every path.
- Limiting condition: `memcpy` remains correct when the API and proven extents establish non-overlap; do not mandate `memmove` for unrelated copies.

### L-207 — A supported build matrix needs negative neighbors

- Port status: unimplemented.
- Quality effect: testing only declared target tuples can pass while build constraints silently advertise complete implementations for unsupported architectures, operating systems, or cgo combinations.
- Evidence: both Go confirmation reviewers found artifacts that selected and compiled correctly for all four supported tuples but also selected unsupported `linux/arm64`, `windows/arm64`, or `js/amd64` combinations. The common validator did not reject that contract expansion.
- Transfer candidate: pair positive target-matrix checks with representative adjacent unsupported tuples, and distinguish compile-only cross-target verification from execution in a declared emulator or target environment.
- Limiting condition: repositories that intentionally support every tuple matching a broad constraint should test capability properties rather than inventing a closed negative matrix.

### L-208 — Admission accounting must survive failure after work starts

- Port status: unimplemented.
- Quality effect: synchronizing submit and close can repair the main race while still hanging shutdown or leaking work if scheduling succeeds and subsequent outcome registration, container growth, or bookkeeping throws.
- Evidence: C++ confirmation reviewers preferred implementations with one submit/close boundary but independently identified samples where `jobs_.push_back(job)` could throw after scheduling, leaving an in-flight counter nonzero and the started job outside terminal accounting. Some fixes also changed a governed public header to add synchronization state.
- Transfer candidate: identify the admission linearization point, make registration and counters exception-safe, cancel and observe started-but-unregistered work, and verify lifecycle repair independently from public API/ABI preservation.
- Limiting condition: runtimes with atomic spawn-and-register primitives may enforce this structurally; the failure boundary still needs evidence at the actual adapter.

### L-209 — Frozen reviewer intent does not substitute for actual reviewer identity

- Port status: unimplemented.
- Quality effect: reporting the model named in a design after a different reviewer actually ran fabricates provenance and can hide capability or custody limitations.
- Evidence: the frozen C/C++/Go designs named Sol-high, but that model was unavailable through the active subagent surface. Actual GPT-5.4/high auditors completed the blinded judgments. The reports preserve that identity and the missing old reviewer-harness limitation instead of asserting canonical wrapper execution.
- Transfer candidate: bind reviewer evidence to the executed model, effort, isolation, view digest, judgment digest, and custody path; treat design intent and runtime identity as separate fields and fail closed on mismatch.
- Limiting condition: exact model labels may be unavailable on some hosts; record the strongest observable runtime identity and narrow claims accordingly.

### L-210 — Repeated cross-language lifecycle defects justify a general concurrency owner

- Port status: unimplemented.
- Quality effect: duplicating fragments of admission, pressure, cancellation, terminal observation, synchronization, and parallel-scaling guidance across language skills leaves common omissions and makes improvements drift.
- Evidence: the same missing boundaries recurred independently in Rust, Java, JavaScript, Kotlin, Node, Python, Ruby, C, C++, C#, Swift, shell, SQL adapters, and performance work. A new `concurrency-engineering` skill now owns those invariants while language skills retain runtime-specific semantics.
- Transfer candidate: create a composable general skill when a stable invariant recurs across many domains and no existing owner covers the whole decision; keep exact runtime primitives and version facts in focused siblings.
- Limiting condition: composition has context cost and retrieval risk. Retain the general owner only if blinded trials show task value beyond the language skill alone and routing tests avoid redundant activation.

### L-211 — Admission closure and terminal selection are separate protocol state

- Port status: unimplemented.
- Quality effect: a stream or queue can correctly stop admission and drain ordinary work yet still publish the wrong terminal outcome when close, failure, invalid demand, or cancellation arrive before the terminal callback is delivered.
- Evidence: concurrency confirmation probes found implementations where `offer(1); close(); fail(...); request(1)` discarded an accepted item and replaced a previously committed graceful close with failure. Other variants suppressed invalid demand merely because admission was closed, even though no terminal signal had been delivered.
- Transfer candidate: model admission state, committed terminal cause, drain ownership, and terminal delivery separately; declare precedence, keep protocol obligations live through the required horizon, and test interleavings rather than individual methods in isolation.
- Limiting condition: some APIs intentionally allow failure to preempt a pending graceful close or declare close to mean only “no more admission.” Follow the public contract; the invariant is explicit state and precedence, not universal close-wins behavior.

### L-212 — Bounded admission does not bound the system

- Port status: unimplemented.
- Quality effect: a worker pool can advertise a bounded job channel while unbounded result transport, reorder buffers, retry state, or detached test supervisors still permit unbounded retention or lifecycle escape.
- Evidence: both canonical Rust confirmation reviewers preferred control overall despite tied machine passes because treatment variants more often paired bounded jobs with unbounded results or returned on a missing outcome before all worker joins. A generated lockfile and detached timeout helper also reduced scope and cleanup quality without helping product behavior.
- Transfer candidate: enumerate and bound every retained work and outcome path, preserve one terminal accounting outcome per accepted item, and prevent early propagation from bypassing join-all settlement; apply the same ownership rule to test supervisors.
- Limiting condition: an intentionally unbounded durable log or externally supervised execution domain may be valid when its capacity, owner, and failure policy are explicit; do not relabel it a bounded pool.

### L-213 — A passing hidden validator does not erase source-visible protocol defects

- Port status: unimplemented.
- Quality effect: deterministic validators can pass every sample while blinded source review identifies untested callback ordering, terminal precedence, or exceptional-path accounting failures.
- Evidence: all twelve concurrency executions passed the hidden machine validator, yet canonical and supplementary reviewers independently found subscription-handshake reentrancy, invalid-demand-after-close, executor-rejection drain ownership, and close/fail precedence gaps. Rust confirmation likewise tied on machine outcomes while both canonical reviewers selected control on lifecycle quality.
- Transfer candidate: preserve machine outcome vectors and independent semantic review as separate evidence; when they disagree, add the smallest discriminating probe and narrow or reopen the claim instead of allowing either surface to overrule the other by convention.
- Limiting condition: source review can also invent unreachable concerns. Promote a finding only when the relevant path is contractually reachable or a disposable probe reproduces it.

### L-214 — Cancellation classification belongs to terminal state, not exception vocabulary

- Port status: unimplemented.
- Quality effect: treating every `OperationCanceledException` or similarly named error as cancellation can erase a real fault, while publishing caller cancellation before owned operations settle can leave work running after the terminal interface returns.
- Evidence: every C# complete-outcome sample missed some caller-cancellation settlement. Reviewers also found both over-broad and under-broad exception-type classification: a faulted task carrying `OperationCanceledException` is not equivalent to a task whose terminal state is canceled, and a synchronous throw before task creation is a separate boundary.
- Transfer candidate: classify from the runtime's settled task/outcome state, define synchronous invocation failure independently, stop new admission, signal only owned cancellation, await every admitted operation, then publish the declared terminal cause.
- Limiting condition: an API may deliberately normalize several failure categories into cancellation; that is a public translation policy and should be tested as such rather than inferred from the exception class name.

### L-215 — Idempotent destruction does not make callback disposal race-free

- Port status: unimplemented.
- Quality effect: a native `Destroy` operation can tolerate duplicate calls while the wrapper still destroys state underneath an active or late callback, frees a rooted delegate too early, or publishes disposal before callbacks have exited.
- Evidence: a C# treatment sample removed synchronization because destruction appeared idempotent and the hidden concurrent-disposal check reproduced double destruction. Other samples passed only when they closed callback admission, held rooting through the registration lifetime, waited active callbacks, and shared one terminal transition across disposers.
- Transfer candidate: separate unregister/admission closure, active-callback count, rooted callback lifetime, exactly-once destruction, and disposal publication; exercise disposal while a callback is held and concurrent repeated disposal.
- Limiting condition: a platform primitive may itself provide quiescent unregister-and-destroy semantics. When it does, bind the wrapper to that documented guarantee rather than duplicating synchronization.

### L-216 — A corrective trial needs the rejected treatment as its comparator

- Port status: unimplemented.
- Quality effect: comparing a post-review correction only with no skill can show generic value while leaving the actual corrective claim unidentified; the correction may still be no better than the exact guidance it replaces.
- Evidence: nine post-reveal language corrections were frozen into new candidate trees and paired against their corresponding rejected treatment snapshots under a dedicated harness that requires a source for both `control` and `revision`. Each prospective case targets the revealed boundary without reusing the earlier task artifact.
- Transfer candidate: when a treatment is revised because of observed failure, freeze both pre-correction and post-correction inputs and evaluate them on new discriminating work; reserve no-treatment controls for the separate question of whether the skill adds value at all.
- Limiting condition: if the old treatment cannot be reconstructed with trustworthy identity, use the strongest retained effective input and explicitly narrow the causal claim rather than fabricating a comparator.

### L-217 — An oracle must satisfy the full system bound, not merely the task's visible queue

- Port status: unimplemented.
- Quality effect: an admitted instrument can encode the same defect it is intended to detect, causing valid bounded designs to be compared against an oracle that still permits unbounded retention or deadlock under backpressure.
- Evidence: the inherited Rust worker-pool oracle used a bounded work `sync_channel` but an unbounded result channel. Replacing the result path with a bounded channel exposed a producer/consumer cycle, which required an owned producer plus continuous result drainage and one terminal accounting record per accepted job.
- Transfer candidate: mutation-audit the oracle itself against every declared bound and terminal property; enumerate work, result, reorder, retry, log, and supervisor paths, then apply pressure on both ingress and egress before freezing the instrument.
- Limiting condition: an unbounded durable system of record can be intentional when its capacity, owner, persistence, and failure policy are explicit; it must not silently stand in for a bounded in-memory path.

### L-218 — Cloning an instrument requires rebinding every self-identity

- Port status: unimplemented.
- Quality effect: a copied evaluator can silently read governed files or hidden probes from its predecessor, so the new task appears frozen while execution actually validates the old case.
- Evidence: the cloned Rust corrective validator retained both the former `CASE_ID` and an absolute former `CASE_DIR`; direct execution therefore ignored the new hidden contract until those values were rebound to the current file location. Other cloned validators used relative self-discovery and did not share the defect.
- Transfer candidate: derive case roots from the running artifact, keep case identity in one manifest, and add an unrelated-copy admission probe that fails if any validator path or identifier points outside the frozen case directory.
- Limiting condition: an absolute content-addressed dependency can be legitimate when it is deliberately shared and included in the instrument identity; the problem is undeclared predecessor coupling.

### L-219 — Counterfactual discrimination does not prove behavioral testing

- Port status: unimplemented.
- Quality effect: a submitted test suite can pass the oracle and fail every frozen mutant by inspecting implementation text, while never invoking the public behavior the evaluation claims to exercise.
- Evidence: fresh adversarial audit reproduced source-inspection-only passing suites across all four TDD instruments—conflict response, retry limit, journal recovery, and Unicode lookup. The retry case additionally accepted a red checkpoint whose test digest did not match the final submitted suite.
- Transfer candidate: include behaviorally equivalent source rewrites, require observation through the public seam, and bind authenticated process checkpoints to the final test bytes or a verified additive-only relation; treat return-code matrices as necessary but not sufficient.
- Limiting condition: source or bytecode inspection is itself valid when structural conformance is the declared contract; do not mislabel that artifact as runtime regression evidence.

### L-220 — Validation sandboxes must mount the exact runtime identity they verify

- Port status: unimplemented.
- Quality effect: a case can pass direct validation and fail or disappear under the release wrapper because its pinned compiler lives outside the sandbox's mounted runtime surface.
- Evidence: the generic corrective harness exposed `/usr` but not the pinned Rust toolchain under `/home/rashino/.rustup`; the specialized Rust harness carried that mount. Reusing the generic wrapper produced an infrastructure failure unrelated to the candidate or oracle.
- Transfer candidate: make executable identity and sandbox reachability one admission contract, run the validator through the exact release wrapper from an unrelated working directory, and reject direct-only evidence when the production custody path differs.
- Limiting condition: a runtime wholly contained in the project or standard mounted system tree needs no extra bind, but its executable and dependencies still need identity evidence proportionate to the claim.

### L-221 — A failed canonical review remains evidence, not a blank to overwrite

- Port status: unimplemented.
- Quality effect: replacing a failed governed reviewer attempt with an unlabelled fallback makes a complete-looking record at the cost of false provenance and hides whether failure was caused by model access, custody, timeout, or the candidate itself.
- Evidence: several corrective rounds reached terminal reviewer failures after valid publication. The campaign retained those attempts, commissioned fresh blinded recovery judgments through a separately identified reviewer path, and recorded decisions without manufacturing the missing canonical admission receipt.
- Transfer candidate: preserve every terminal attempt and its identity; classify a fallback as new evidence with its own model, isolation, inputs, and authority, and narrow the claim when the canonical workflow did not finish.
- Limiting condition: an idempotent governed recovery command may legitimately reconstruct a receipt when it can revalidate every original invariant and records that reconstruction explicitly.

### L-222 — Published candidates should exclude reproducible build residue

- Port status: unimplemented.
- Quality effect: compiled output, dependency caches, coverage, and profiles can dominate blinded-review context, reveal irrelevant environment details, and exhaust evidence-size gates without improving the reviewer’s ability to judge the source change.
- Evidence: prospective TypeScript and other generated-output projects required publication cleanup and explicit artifact policies before their views fit the campaign’s bounded evidence surface; reviewers still needed the final executable behavior and declaration contract, not dependency or cache trees.
- Transfer candidate: distinguish required deliverables from reproducible residue, retain compact hashes and verification records for regenerated outputs, and publish only artifacts needed to reproduce or judge the claimed contract.
- Limiting condition: generated runtime files, declarations, lockfiles, binaries, or migration output are primary deliverables when consumers actually receive them; do not delete governed outputs merely because they are generated.

### L-223 — Validators should resist realistic gaming without pretending to defeat omniscience

- Port status: unimplemented.
- Quality effect: designing against an all-knowing malicious candidate tends to produce brittle source-shape gates and false rejections, while ignoring cheap implementation-coupled tricks permits tests that discriminate mutants without exercising behavior.
- Evidence: refactoring and TDD instrument audits exposed both failure modes: source-inspection tests could defeat mutation matrices, but over-constraining candidate source layout or test organization rejected ordinary helpers and Go `testdata` fixtures.
- Transfer candidate: state the executor threat model, protect controller-owned variants and hidden checks, include behaviorally equivalent rewrites, and accept ordinary repository testing idioms unless the task actually prohibits them.
- Limiting condition: adversarial security evaluation may require a stronger attacker model and external enforcement; ordinary coding-skill evaluation should not claim that level of resistance.

### L-224 — A hand-authored patch is not an oracle until it applies and executes

- Port status: unimplemented.
- Quality effect: a semantically plausible unified diff can have stale hunk counts, path assumptions, or context and fail before the intended behavior is ever observed.
- Evidence: prospective instrument construction repeatedly found manually drafted oracle patches that required application repair before seed/oracle polarity could be frozen.
- Transfer candidate: apply every patch to a pristine copy from an unrelated working directory, run the complete validator, and freeze the resulting source and outcome digests rather than trusting visual inspection.
- Limiting condition: an already-materialized content-addressed oracle tree needs no patch-application gate, but still needs executable polarity evidence.

### L-225 — Test custody includes fixtures and support resources, not only test-source filenames

- Port status: unimplemented.
- Quality effect: transplanting only files matching `*_test.go` or another runner naming convention can make a correct candidate fail because standard fixture directories, embedded resources, helpers, or configuration disappear in the controller workspace.
- Evidence: the refactoring r2 validator rejected a passing Go test that read `flow/testdata/fixture.txt`; preserving the candidate’s complete test surface while swapping only the controller-owned implementation fixed the false rejection and retained mutant discrimination.
- Transfer candidate: define the test support surface at the repository or package boundary and replace the implementation under test, rather than guessing support files from one filename pattern.
- Limiting condition: untrusted executable fixtures may require a narrower allowlist or isolated runner; custody should preserve legitimate dependencies without silently granting broader authority.

### L-226 — Controller timeouts are ordinary failed evidence when the candidate caused the wait

- Port status: unimplemented.
- Quality effect: allowing a candidate’s hanging test to escape as a harness exception discards a meaningful failure, blocks round publication, and invites selective replacement of the worst outputs as “infrastructure.”
- Evidence: the first refactoring prospective round leaked `TimeoutExpired` and produced controller failures. The replacement validator converts bounded test expiry into an ordinary nonzero outcome and structured JSON, while true controller or custody faults remain infrastructure failures.
- Transfer candidate: set nested bounds, translate candidate-controlled expiry into a terminal failed check, and reserve replacement eligibility for failures outside the candidate’s authority.
- Limiting condition: an unavailable runtime, corrupted frozen input, or controller crash before candidate exposure remains infrastructure and should not count against a condition.

### L-227 — Container bind paths are resolved in the daemon’s namespace

- Port status: unimplemented.
- Quality effect: a validator can create a fixture inside a process-private mount namespace and then ask Docker to bind that path, only for the daemon to see the host path instead and run against missing or stale data.
- Evidence: the Swift instrument’s first hidden-test design placed injected files under Bubblewrap-private `/tmp`; Docker resolved the bind from the host namespace. Injecting into the controller project with `finally` cleanup made the exact hidden file visible to the daemon and left no residue.
- Transfer candidate: identify which process resolves every mount source, materialize input in that namespace, bind the smallest read-only surface, and verify cleanup on success, failure, and interruption.
- Limiting condition: rootless or in-process container runtimes may share the caller’s mount namespace; inspect the deployed runtime rather than applying Docker daemon semantics universally.

### L-228 — An audit must not mutate the executable tree it hashes

- Port status: unimplemented.
- Quality effect: importing Python validation modules can create `__pycache__` inside a frozen harness, changing its digest and causing later publication or reveal to fail because the act of inspection altered evidence identity.
- Evidence: a direct harness audit created bytecode cache files that blocked a later reveal until they were removed; subsequent commands used `-B`, disabled bytecode before imports, and checked the harness for executable caches.
- Transfer candidate: make audits read-only by construction, disable or redirect interpreter caches before the first import, and verify the governed tree digest both before and after inspection.
- Limiting condition: disposable build trees may intentionally cache compilation, but cached output must live outside the immutable authority surface and be excluded by an explicit identity rule.

### L-229 — The documented test entrypoint is part of the verification contract

- Port status: unimplemented.
- Quality effect: invoking a convenient compiler or hidden command directly can pass while the repository’s promised runner is stale, non-executable, uses the wrong pinned runtime, or silently omits tests.
- Evidence: the Swift instrument admitted only after the validator hashed and executed the exact `tools/test.sh` entrypoint; Node and TypeScript reviews separately found strong tests that bypassed package exports or were not selected by the authoritative runner.
- Transfer candidate: identify, hash when custody matters, and execute the same entrypoint maintainers and CI are expected to use; treat supplementary direct probes as additional evidence rather than substitutes.
- Limiting condition: a task may explicitly ask to create or repair the entrypoint, in which case the pre-change runner is the defect and the new interface becomes authoritative only after end-to-end validation.

### L-230 — Package-boundary tests should traverse the published path

- Port status: unimplemented.
- Quality effect: importing `dist/index.js` or another internal path can prove local code behavior while missing broken export maps, declaration routing, module mode, packed-file omissions, or consumer resolution.
- Evidence: blinded TypeScript reviewers repeatedly distinguished tests using a package self-reference from relative `dist` imports; the prospective treatment’s stronger samples paired runtime validation with external declaration-consumer evidence and achieved a `3/3` versus `2/3` executable result.
- Transfer candidate: test source behavior, built output, and the actual published/self-reference import as distinct surfaces; include a consumer compile or execution outside the package when that boundary is part of the contract.
- Limiting condition: private applications with no package consumer may have no published boundary; do not invent one when direct runtime execution is the deployment interface.

### L-231 — Plan assertions should target access properties, not incidental operator names

- Port status: unimplemented.
- Quality effect: requiring one exact index name or plan node can reject an equivalent safe access path after harmless schema, optimizer, or version changes, while a named node alone does not prove tenant isolation, locking, row bounds, or spill behavior.
- Evidence: SQL instrument hardening replaced exact-name expectations with checks for the required tenant-scoped access and concurrency properties under the disposable workload.
- Transfer candidate: assert semantic predicates and bounded work—filters, lock behavior, row/result limits, casts, estimates versus actuals, and prohibited full-scan or spill conditions—then retain the native plan as evidence.
- Limiting condition: a governed migration may intentionally require a specific index or hint for compatibility; that maker-set mechanism should be tested directly and version-scoped.

### L-232 — Test-count quotas are a weak proxy for discriminating verification

- Port status: unimplemented.
- Quality effect: requiring an arbitrary number of tests rewards duplicated shallow fixtures and can still miss the single counterexample that separates the intended contract from a false green.
- Evidence: prospective task/rubric repairs removed numeric test expectations and instead required deterministic assertions that rejected the seed or controlled mutants through the public seam.
- Transfer candidate: align task, rubric, and validator on observable contract distinctions, runner reachability, assertion causality, and seed/oracle discrimination; count tests only when a maker explicitly requires a conformance matrix.
- Limiting condition: regulated suites may mandate enumerated cases or coverage thresholds, but those are external requirements rather than universal evidence of quality.

### L-233 — A tied or degrading corrective round is evidence for deletion

- Port status: unimplemented.
- Quality effect: retaining every plausible refinement steadily grows context and can reduce task focus even when blinded trials show that the added wording does not help or makes outcomes worse.
- Evidence: corrective rounds led to reversion of the Go, JavaScript, C#, Rust, and concurrency expansions when the predecessor won or the result tied without a semantic advantage; C++, C, and Python corrections were retained only where new executable or blinded evidence separated them.
- Transfer candidate: compare a correction to the exact predecessor on new work, default to the leaner input when machine outcomes and blinded semantics do not separate, and retain a no-lift clause only for a stable hazard whose omission is independently demonstrated and causes no observed degradation.
- Limiting condition: small samples are uncertain and safety-critical invariants may merit retention without measured uplift; state that rationale narrowly and schedule stronger confirmation rather than calling the correction effective.

### L-234 — A percentile is undefined until its outcome population is named

- Port status: unimplemented.
- Quality effect: a candidate can appear to improve p99 by rejecting work before timing begins or omitting timed-out operations, so success-conditioned latency falls precisely because caller outcomes degraded.
- Evidence: every performance prospective artifact failed the frozen loss-aware decision contract, and the matched machine outcome tied `0/3` versus `0/3`. Post-reveal hardening now requires separate offered, admitted, completed, rejected, timed-out, and failed populations; it retains caller-observed timeout latency where defined without inventing latency for pre-service rejection.
- Transfer candidate: bind each statistic to an explicit population, report loss/error outcomes separately, and make the overall decision fail or remain undefined when a guardrail is exceeded; include a counterexample proving that dropping slow work cannot create a win.
- Limiting condition: a service may deliberately shed before admission and report admitted-work latency, but the shedding outcome and offered-load contract remain part of the caller-visible decision rather than hidden samples.

### L-235 — Bounded submission and outcome collection must make progress concurrently

- Port status: unimplemented.
- Quality effect: bounding both work and result paths can create a producer/consumer cycle when the controller finishes submitting before it starts draining completions, even though every individual queue is correctly bounded.
- Evidence: refactoring and Rust worker-pool oracle audits reproduced deadlock or incomplete settlement until an owned producer submitted while the controller continuously collected exactly one terminal outcome per accepted item.
- Transfer candidate: model progress dependencies across admission and completion paths; start the consumer before a bounded producer can block, close only from the owning side, and verify acceptance accounting, result drainage, cancellation, and join under pressure.
- Limiting condition: runtimes with a combined work-stealing or structured task-group primitive may guarantee progress through another mechanism; test the selected runtime contract rather than mandating one topology.

### L-236 — Actor isolation does not preserve a decision across suspension

- Port status: unimplemented.
- Quality effect: an actor can check capacity or absence, suspend for external work, and resume after another call changed the state, causing oversubscription, duplicate effects, or cleanup of another operation’s reservation.
- Evidence: the Swift prospective reservation lifecycle improved from `1/3` control to `3/3` treatment. Stronger artifacts reserved actor-owned state before leaving isolation, associated cleanup with an operation identity, and reconciled cancellation or authorization failure when re-entering the actor.
- Transfer candidate: identify actor decisions whose validity must survive `await`; reserve or version the relevant state before suspension, then commit or release only the matching operation after external work settles.
- Limiting condition: a suspension-free isolated operation or an idempotent external action may need no reservation; do not add state when reentrancy cannot invalidate the decision.

### L-237 — Validation grammars should accept semantically equivalent evidence forms

- Port status: unimplemented.
- Quality effect: a validator can reject every correct artifact because it recognizes headings but not numbered increments, converting a presentation choice into a false behavioral failure and obscuring real candidate differences.
- Evidence: all six trunk-based rollout projects passed repository tests and manual old/new protocol review, but the frozen plan validator reported `sections=0` for every nonempty numbered-list plan. Both reversed-label reviewers still preferred treatment after examining the actual ordered increments, while preserving the shared machine failure.
- Transfer candidate: validate semantic units through a small explicit manifest or a vocabulary-tolerant parser with adversarial positive and negative fixtures; keep manual semantic evidence separate when the frozen recognizer fails.
- Limiting condition: a governed output schema may intentionally require exact headings or fields; then presentation is part of the contract and should be stated before execution rather than inferred by the validator.

### L-238 — Final correctness cannot reconstruct test-first chronology

- Port status: unimplemented.
- Quality effect: a correct final implementation and green final suite do not prove that the decisive test existed, ran, and failed for the intended reason before production changed.
- Evidence: all six TDD final implementations satisfied the business behavior, but no submission established an authenticated red for the exact final test bytes, and every suite missed the frozen prefix-identity and bounded-revision counterexamples. The matched machine result tied `0/3` versus `0/3`.
- Transfer candidate: when process order is part of the claim, retain a minimal authenticated checkpoint linking repository state, exact test content, authoritative runner, meaningful failing assertion, and subsequent green; independently mutation-check the final suite through the public seam.
- Limiting condition: many maintenance tasks care only about final behavior, not TDD chronology. Require process evidence only when the method itself is requested or audited.

### L-239 — Immutable source modes must not make transformation staging immutable

- Port status: unimplemented.
- Quality effect: a converter can correctly copy a frozen or read-only source tree and then fail when its own target normalization tries to rewrite frontmatter, producing a release blocker unrelated to plugin semantics.
- Evidence: both final software-development roundtrips failed with `PermissionError` after copied `0444` skill files reached `write_frontmatter`. Restoring live-source authoring modes unblocked the immediate release, and `plugin_port.py` now adds only owner-write permission inside its staging copy, preserves execute bits and symlinks, and has a regression test proving the source stays `0444` while converted output succeeds.
- Transfer candidate: distinguish immutable input authority from writable transformation staging; copy content and executable identity first, grant minimal write authority only inside the new tree, never follow symlinks during mode changes, and test a read-only source fixture end to end.
- Limiting condition: a byte-for-byte archival copier should preserve modes exactly and perform no normalization. The writable-staging rule applies when producing a transformed artifact, not when mode identity is itself the deliverable.

### L-240 — Authoritative inventory prose needs one executable source of truth

- Port status: unimplemented.
- Quality effect: a release can add a valid component, update manifests, README, tests, and reports, yet leave one nested instruction file with an old hardcoded count that tells future agents the new component is outside the contract.
- Evidence: the final independent audit found `plugins/software-development/AGENTS.md` still declared exactly 25 skills while the shipped tree, README, manifests, decisions, and maintainer contract contained 26. The fix removed the duplicated number, delegated inventory authority to README plus the exact-set contract test, and added a regression assertion that rejects reintroduced hardcoded catalog counts.
- Transfer candidate: keep mutable inventory in one machine-checked source, let prose name that authority without copying its count, and include nested instruction surfaces in consistency tests whenever they can change future executor behavior.
- Limiting condition: a maker-set fixed cardinality can itself be a durable invariant; when it is, test every authoritative duplicate or generate them from the same source rather than relying on review memory.
