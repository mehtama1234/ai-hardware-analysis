# Next stage: repository-scale agentic verification

## End-to-end objective

Build a repository-scale autonomous hardware verification engineer that can
take a real open-source RTL project and a reproducible defect, construct
specification-grounded verification collateral, locate the defect, propose a
minimal repair, validate the repair with simulation and formal methods, and
produce a hash-bound review package. The system must work across multiple
files, build systems, languages, and native project regressions.

The current four-workstream prototype proves the orchestration and evidence
contracts on seeded designs. This next stage must make the model responsible
for substantive assertion, test, invariant, diagnosis, and patch proposals;
deterministic tools remain the independent judges. A proposal that merely
passes a formatting adapter is not counted as a successful model repair.

This direction is aligned with recent repository-scale evaluation in
[HWE-Bench](https://arxiv.org/abs/2604.14709), coverage-guided verification in
[AgentDV](https://arxiv.org/abs/2608.27148), structured testbench generation in
[STG](https://arxiv.org/abs/2606.12983), solver-in-the-loop assertion generation
in [ProofLoop](https://arxiv.org/abs/2604.23100), and open-source formal repair
in [RTL Repair Framework](https://arxiv.org/abs/2607.28877).

## Four workstreams

### 1. Repository-scale bug discovery and repair

Inputs are a versioned repository checkout, project build instructions, a
failure or mutation, and all relevant RTL, configuration, testbench, register,
and documentation files. Agents build a repository map, localize the failure
across file boundaries, propose a minimal patch, and run the native regression.

Required evidence:

- immutable base-commit and working-tree digests;
- file/dependency graph and selected context with source locations;
- model diagnosis and patch proposal with provenance;
- failing baseline and passing repaired-copy regression;
- unchanged-file and patch-minimality checks;
- held-out regression result, not only the targeted test.

Initial target: 50 real historical fixes from at least two open-source hardware
projects, with separate scores for localization, patch validity, targeted
fail-to-pass, and regression preservation.

### 2. Coverage- and mutation-guided verification closure

Agents generate structured tests and assertions, run them, inspect line,
branch, toggle, functional, and assertion coverage, and generate mutants that
must be detected. The loop continues until the coverage and mutation budgets
converge or the workflow stops with an explicit gap report.

Required safeguards:

- no credit for unreachable or vacuous assertions;
- mutation baselines must fail before a test is counted as detecting a bug;
- coverage must be tied to the generated artifact and source digest;
- false-pass mutations must be reported separately;
- the stopping decision must be reproducible from stored metrics.

Initial target: 100 seeded mutations across protocol, control, reset, register,
FIFO, CDC, and security behaviors; report mutation score, coverage deltas,
false-pass rate, runtime, and generated-artifact reuse.

### 3. Unbounded formal reasoning and proof repair

The bounded property flow is extended with candidate invariant and lemma
generation, assumption auditing, k-induction, IC3/PDR or a solver portfolio,
and counterexample-guided abstraction refinement. The language model proposes
lemmas and repairs; a formal engine must independently prove them.

Required evidence:

- bounded result and unbounded/inductive result as separate statuses;
- assumptions, reachable-state checks, and vacuity results;
- solver command, version, source digests, and proof artifacts;
- counterexamples for failed lemmas;
- replay from a clean checkout.

Initial target: prove a selected set of safety properties for all reachable
states on at least three multi-cycle designs, while detecting over-constrained
assumptions and rejecting bounded-only false closure.

### 4. Adversarial security and signoff evidence

A red-team agent creates RTL mutations, Trojan-like changes, unsafe assumptions,
CDC/reset faults, privilege violations, and register-map inconsistencies. A
blue-team workflow must detect, localize, explain, repair, and re-verify them.

Required evidence:

- mutation or threat origin and reproducible seed;
- detection mechanism: test, assertion, formal proof, or structural check;
- root-cause location and competing-hypothesis record;
- repaired-copy result and regression result;
- signed evidence manifest with explicit human-review state.

Initial target: a held-out adversarial suite with separate detection and repair
scores. Passing a test that is vacuous, unreachable, or silently missing from
the compiled property set receives zero credit.

## Shared architecture

```text
repository + spec + defect
        |
        v
typed repository map / Property IR / register and protocol IR
        |
        +--> test and assertion generation --> simulation + coverage + mutation
        |
        +--> diagnosis --> waveform/CEX/CDFG/state frontier
        |
        +--> invariant and lemma generation --> bounded + inductive formal
        |
        +--> repair proposal --> copy-only patch --> native regression
        |
        v
adversarial re-check --> hash-bound evidence --> human review
```

Every model action must carry the repository revision, relevant artifact
digests, evidence references, and a review-only status. Every tool result must
be replayable from a clean checkout. The system must distinguish:

1. model output availability;
2. syntactic and structural admission;
3. targeted behavioral success;
4. formal proof status;
5. regression preservation;
6. human approval and release status.

## Milestones

1. **M1 — benchmark harness:** containerized task manifest, repository snapshot,
   baseline/repaired-copy runner, native regression adapter, and result schema.
2. **M2 — mutation closure:** mutation generator, mutation oracle, coverage
   ingestion, vacuity/false-pass checks, and convergence report.
3. **M3 — proof closure:** invariant/lemma contracts, k-induction and solver
   portfolio adapters, assumption audit, and proof replay.
4. **M4 — adversarial signoff:** red/blue task schema, held-out security suite,
   signed evidence package, and human-review dashboard input.
5. **M5 — evaluation:** 50+ repository-scale fixes, 100+ mutations, three
   inductive proof targets, and a held-out adversarial suite with ablations.

## Implementation status

M1 has started in the verification platform. The repository benchmark module
now validates task manifests, creates explicit source snapshots, runs isolated
baseline and candidate commands without a shell, records stdout/stderr hashes,
checks canonical source immutability, and emits self-digested task and aggregate
reports. The CLI entry point is
`analog-digital-chip-design-eda/scripts/run_repository_scale_benchmark.py`.
The first runnable task is
`analog-digital-chip-design-eda/benchmarks/repository_scale/seeded_counter_task.json`.
Its demo has completed a real Icarus/VVP fail-to-pass run: baseline `fail`,
candidate `pass`, candidate source changed, canonical source unchanged, and no
unexpected changed files. This validates the benchmark contract on one seeded
repository task; it is not yet the 50-task evaluation.
The current implementation is a harness, not yet the 50-task evaluation: real
repository adapters and native project task manifests remain the next work.
The first non-seeded adapter is now present for the local OpenROAD-flow-scripts
checkout at commit `be0dca0b1`: `benchmarks/repository_scale/openroad_gcd_compile_task.json`
and `scripts/run_openroad_repository_task.py` run the native GCD RTL compile,
detect an undeclared-signal mutation, and prove canonical immutability. Its
claim level is explicitly compile-only; functional GCD validation remains
open.
The follow-on `openroad_gcd_functional_task.json` adds a disposable handshake
testbench and checks the repository revision before execution. At `be0dca0b1`,
the baseline GCD transactions pass, the swapped-operands mutant fails, and
candidate/canonical integrity checks pass. This exercises three operand pairs,
not complete GCD or project regression coverage.
The native OpenROAD agent adapter now runs the same bounded diagnosis-to-repair
contract at `be0dca0b1`: the swapped-operand mutant fails, the repair restores
the three-transaction GCD check, and the real checkout remains unchanged. This
is one native repository task, not yet broad OpenROAD regression coverage.
The native-repository extension now includes a second OpenROAD design family:
`scripts/run_openroad_fifo_agent_repair_closure.py` runs a reset-state mutation
against the asynchronous FIFO, routes the failure through the repository-agent
and copy-only repair path, and retests the repaired copy. The original FIFO
functional test did not observe the reset invariant and was rejected as
insufficient; a dedicated reset testbench was added, after which the mutation
was detected and repair closure passed. The independent checker is
`scripts/check_openroad_fifo_agent_repair_closure.py`. This is two native
design families at one pinned checkout, not broad repository generalization.

M2 has now started with `verification_platform/mutation.py`. It validates
mutation suites, applies exactly one source replacement in an isolated copy,
requires the unmutated command to pass, classifies mutant failure as detected,
and classifies mutant success as a false pass. The seeded Icarus/VVP mutation
matrix now spans eight designs and sixteen bug variants across arbiter,
decoder, FIFO, handshake, parity, register addressing, signed arithmetic, and
width adaptation. All 16/16 mutants were detected with zero false passes.
This remains a controlled matrix; scaling toward the planned 100+ mutation
evaluation is still open.
The matrix now has an explicit evaluation plan in
`benchmarks/repository_scale/seeded_mutation_evaluation.json`: eight mutation
variants are in the declared train split and eight variants are held out. The
reproducible evaluator reports 8/8 train and 8/8 held-out detection, both with
mutation score 1.0. This is a held-out controlled result, not evidence of
generalization to unseen repositories.

M3 has now started with `verification_platform/proof_closure.py`. Formal
records distinguish bounded results from inductive results and require an
assumption audit, reachable-state check, and non-vacuity status before calling
a property proven. Bounded-only results, over-constrained assumptions, and
counterexamples remain blocked states.
The platform now also exposes `run_yosys_inductive_proof`, which invokes
Yosys `sat -tempinduct -prove-asserts`, records the temporal-induction method,
and classifies the explicit induction-success marker separately from bounded
SAT output. A real constant-state invariant passes this adapter in the proof
closure regression; a full lemma-generation loop and multi-design proof suite
remain open.
The first mixed induction suite is now executable through
`scripts/run_inductive_proof_suite.py`: one constant invariant is proven and
the seeded counter and timeout models produce counterexamples, with all three
statuses matching the manifest expectations. This validates honest proof-state
classification, not three completed proofs.
The repair-side induction suite is now executable through
`scripts/run_repaired_inductive_suite.py`. It applies the known repairs only
to temporary copies and proves all three selected models—constant invariant,
counter hold, and timeout boundary—with Yosys temporal induction. The report
binds each repaired source hash and keeps the claim boundary to those three
disposable models.

M4 has now started with `verification_platform/security_closure.py`. The
security task contract records threat class, origin seed, detection mechanism,
localization, repaired-copy behavior, regression behavior, evidence, and human
review state. Machine checks alone produce `review_required`; `signed_off`
requires explicit human approval, while failed detection or regression is
blocked.
The first executable red/blue slice is
`scripts/run_security_regblock_demo.py`: a seeded unauthorized nonzero-address
register write is detected by the directed test and mutation oracle, the
repair/regression checks pass on the clean copy, and the resulting signoff
record correctly stops at `review_required`.

The repository-scale agent bridge is available through
`verification_platform/repository_agent.py`. It assembles bounded diagnosis,
next-test, repair-proposal, and review roles over the provider-neutral
agent-team contract. Outputs remain source-revision/evidence bound and
review-only; source mutation and proof still require deterministic tools and
explicit approval.
The debug-to-repair handoff now also includes a deterministic
`frontier-root-cause-candidates-v1` artifact. After a validated waveform/CDFG
frontier is found, the system ranks the exact RTL statements directly driving
the first divergent event, includes their source text and line numbers, and
binds the candidate list to the RTL and causal-binding digests. Diagnosis and
repair agents receive this list as constrained evidence. A directly driving
statement remains a review candidate, not a proven root cause.
When a repair proposal is admitted through the same path, its exact-text edit
must resolve to one of those ranked source lines. This prevents a patch from
being accepted merely because its `before` text matches somewhere else in the
dependency cone; the candidate remains review-only until copy-based retest and
human approval.
The debug package now also emits
`competing-root-cause-hypotheses-v1`: ranked candidates with separate FOR and
AGAINST evidence. Direct structural drivers rank above conservative assignment
fallbacks, but all hypotheses remain `review_required`. Diagnosis and repair
agents receive this set, preserving an explicit uncertainty boundary instead
of forcing a single root-cause claim.
The bridge has been exercised end to end through the JSONL local-backend
transport using `scripts/mock_repository_agent_backend.py`: all four role
handoffs were available and review-required. This validates transport and
grounding, not real-model quality.
The repository repair role now accepts optional exact before/after source
choices, and the Hugging Face transport binds those choices into the repair
proposal contract instead of treating the role as generic diagnosis. This
keeps model-generated repository edits bounded before they reach the
deterministic copy-only repair gate.
The central agent-team validator now also checks those raw repair fields before
admitting the handoff. A mock end-to-end run with exact choices passes this
gate, and an incorrect or missing choice is blocked. This closes the gap
between request-side repair constraints and the actual accepted agent
trajectory.
The negative path is covered by an orchestration test that supplies a
valid-looking repair proposal with the wrong exact source text and verifies
that the team rejects it as `blocked`.
Accepted repository-agent trajectories now persist the bounded repair payload
(`edit_operator`, `before`, and `after`) in both the role result and the
handoff record. The Colab replay emits that payload, making the proposal
directly consumable by the existing approval-gated copy-only repair adapter
without allowing the agent team to apply it itself.
When a repair source is supplied, the repository-agent runner now passes the
accepted bounded payload through `build_repair_patch_candidate`. The resulting
patch candidate is source-hash and unique-match checked and remains
`review_required`; the Colab replay produced a candidate at the expected
counter source line while leaving canonical RTL untouched. This closes the
agent-to-repair-adapter handoff, but not human approval or retest closure.
The matrix runner `scripts/run_seeded_repository_agent_matrix.py` now repeats
that agent-to-patch-candidate path across all eight seeded designs and bug
classes. The provider-free run produced 8/8 available four-role trajectories
and 8/8 source-validated `review_required` patch candidates. This demonstrates
matrix-level contract coverage, while model quality and repair correctness
remain separate evaluated claims.
The stronger seeded closure in
`scripts/run_seeded_agent_repair_closure.py` now runs all 16 mutations against
canonical reference executions, reconstructs a causal frontier even when a
failing VCD is truncated or has no value transition, and requires the repair
line to be one of the source-bound frontier candidates. The provider-free
matrix passes 16/16 with canonical sources unchanged. This remains a mock-agent
contract evaluation, not a real-model quality result.
The closure runner supports `--start-index` and `--max-tasks` for resumable
real-model evaluation. A one-task CPU probe using the cached
`Qwen/Qwen2.5-Coder-0.5B-Instruct` weights completed the canonical and causal
stages, but all four model-role calls timed out; its report correctly credited
no repair success. This is an execution-capacity result, not a model-quality
result, and the same slices should be run on a GPU-backed Colab session.
The Colab runner now accepts the same task-range flags and invokes the causal
checker in explicit partial mode for bounded slices; a one-task mock Colab
slice passed all nine of its declared machine stages. Full-suite mode remains
strict and requires all 16 causal-repair tasks.
The Colab shell launcher now exposes the same controls through
`COLAB_START_INDEX` and `COLAB_MAX_TASKS`, serializes them into the remote
configuration, and validates their ranges before session creation. An earlier
launcher attempt received `Service Unavailable` while assigning a T4 and was
correctly recorded as blocked. A later authenticated run obtained a Tesla T4
and completed the real-model benchmark and integrated four-workstream
pipeline; the retained artifacts are under
`.artifacts/llm-agent-colab/four-workstreams-integrated-closure-20260914/`.
The run used `Qwen/Qwen2.5-0.5B-Instruct`, passed 11/11 grounded diagnosis
cases plus the mutation, counter, timeout, and register repair contracts, and
left the integrated claim at `review_required`.
The Colab path includes
`colab/check_next_stage_real_colab.py`, an independent acceptance gate for the
repository-scale runner, and
`scripts/check_real_four_workstream_colab.py`, which independently validates
the retained benchmark, integrated pipeline, real-model provenance, 11/11
quality records, review-only repair candidate, and fail-closed claim status.
The latter checker passes on the retained Tesla T4 artifacts. These checks
prevent a fallback or partially completed Colab run from being counted as
real-model evidence.
The closure report now records explicit rates for canonical-reference validity,
causal localization, source-bound patching, repair retest, canonical
immutability, and end-to-end closure. The independent checker requires all six
rates to be 1.0 for the provider-free baseline; these are the comparison fields
to retain when real-model runs are available.
The debug package now also emits a deterministic `causal-timeline-v1` record.
It is anchored to the validated frontier event, includes only its causal
ancestors, orders them by simulated time and signal, and carries the source
causal-graph digest. Diagnosis and repair requests receive this timeline beside
the ranked candidates and FOR/AGAINST hypotheses. The timeline is explicitly
review evidence rather than a proof of root causality, preserving the
fail-closed boundary while giving agents a compact cycle-ordered failure
narrative.
An independent timeline verifier now checks the graph binding, event values,
frontier termination, predecessor references, deterministic ordering, and
self-digest before the timeline is accepted by the debug package. Tampering is
therefore blocked at the package boundary instead of being left for a model or
human to notice later.
The matrix integrity checker is included as a distinct stage in both the
parent aggregate and the Colab runner. It validates all eight per-task run
records, four-role trajectories, exact repair payloads, source revisions, and
review-only patch candidates. The aggregate now includes the parameterized
100-mutant campaign and its independent integrity checker, and the
security-policy campaign plus its independent integrity checker are required;
the integrated formal-proof closure and its checker are also required; the
specification-grounded assertion matrix and its checker are also required; the
native OpenROAD FIFO repair closure and its integrity checker are also
required; the aggregate therefore has 55 stages. The independent
aggregate checker passes the complete report.
The aggregate now also includes a real historical OpenLane repair replay:
commit `fe0ba006` replaced an identity comparison (`matches is []`) with a
value comparison (`matches == []`) in `gui.py`. The new disposable task
injects the pre-fix expression, observes the native empty-results regression,
routes the exact repair through the repository-agent contract, retests the
repaired copy, and independently checks the self-digested report. The 32-stage
aggregate and its independent checker both pass; this is one historical fix,
not yet the planned 50-fix generalization benchmark.
The aggregate now includes a second real historical replay from the other
native repository: OpenROAD commit `bad83a4f1` fixed report-gallery handling
when generated images end in `.webp.png`. The task injects the pre-fix
extension filter, observes the empty-gallery regression, applies the exact
bounded repair through the agent path, and verifies the repaired gallery and
canonical immutability. The 34-stage aggregate and independent checker pass,
but this is still two historical fixes rather than the planned 50.
The aggregate now includes a third historical OpenLane replay from commit
`0e33bf4c`: an unset `TCL8_5_TM_PATH` environment variable caused startup to
fail. The task isolates that initialization block with a Tcl harness, applies
the exact bounded repair in a disposable copy, and verifies startup succeeds
while the canonical checkout remains unchanged. The 36-stage aggregate and
independent checker pass; the historical corpus is now three fixes across two
repositories.
The aggregate now includes a fifth historical OpenLane replay from commit
`7ea7a2ae`: automatic I/O placement previously ran even when
`FP_PIN_ORDER_CFG` was supplied. The Tcl regression confirms the pre-fix
behavior, routes the one-condition repair through the agent contract, and
confirms that constrained placement suppresses `place_io`. The 40-stage
aggregate and independent checker pass; the historical corpus is now five
fixes across two repositories.
The aggregate now includes the first third-repository replay from Sandia's
`cross-sim`, commit `d9548c0`: row and column parasitic resistances were
swapped for column-fed matrix-vector multiplication. The harness executes the
historical `mvm_parasitics` function against an asymmetric numerical case,
routes the exact repair through the agent contract, and independently checks
the repaired result. The 42-stage aggregate and checker pass; the historical
corpus is now six fixes across three repositories.
The repository-scale expansion also adds a deterministic historical-fix
candidate miner and independent checker. Against the three local upstream
repositories it found 162 unique fix/bug/regression candidates, while keeping
all entries explicitly `candidate_only` until their regressions are replayed.
This supplies a real queue for the 50-fix held-out benchmark without turning
discovery into validation. The 44-stage aggregate includes both mining gates.
The candidate miner now derives a deterministic hash-based development versus
held-out split and records both key sets in the manifest. The current 162
candidate inventory passes the split checker with more than 15 held-out
entries, establishing an evaluation boundary before repair work is expanded.
The OpenLane `0687a36b` resizer-environment replay is also registered and
independently checked, bringing the validated corpus to eight
development-split fixes. The OpenLane `f4f8dad8` replay additionally checks
that `FP_DEF_TEMPLATE` suppresses automatic IO placement, bringing the
validated corpus to nine. The OpenLane `18a1df43` replay also validates the
`apply_route_obs` diagnostic-label correction, bringing the development-split
validated corpus to ten.
The aggregate also includes the OpenLane `cb59d1f8` IO-sequence return-contract
replay and its integrity checker. The historical corpus is now seven
validated fixes across three repositories, while the held-out split remains
protected by the replay-scope gate.
An additional split-integrity gate records the ten validated replay commits
and rejects any overlap with the held-out keys. The 55-stage aggregate
therefore protects the evaluation boundary as well as discovering candidates.
The aggregate now includes a fourth historical OpenLane replay from commit
`c5763988`: clock-port validation previously rejected indexed bits of a
multi-bit input bus. The disposable regression uses a JSON netlist and an
indexed clock-port check, routes the exact repair through the agent contract,
and independently validates the repaired result. The 38-stage aggregate and
independent checker pass; the historical corpus is now four fixes across two
repositories.
The formal-closure path now requires a typed `assumption-audit-v1` artifact.
Every declared assumption must have a matching digest-valid solver reachability
result from the same source revision; stale, missing, unknown, or unreachable
evidence blocks closure. The repaired multi-cycle induction suite passes all
three disposable cases, while the closure contract still distinguishes that
bounded project evidence from general silicon correctness. A suite-loaded
Verilator compilation once hit the existing 60-second process limit; the exact
test passed in isolation, so this is recorded as capacity sensitivity rather
than a functional regression.
The integrated formal runner now executes bounded proof, temporal induction,
reset-assumption reachability, typed assumption auditing, and final closure
classification for all three disposable repaired models. All three close as
`proven`; its independent checker validates the child records, assumption-audit
digests, closure digests, and suite report before accepting the result.
The coverage workstream now includes
`scripts/run_seeded_parameterized_mutation_campaign.py`, which deterministically
generates 100 unique behavior-changing mutants across eight RTL families and
reports per-source detection metrics. The original one-scenario testbenches
detected 74/100, exposing 26 false passes. Independent multi-scenario campaign
testbenches then raised this to 100/100 detected, zero false passes, and zero
blocked runs. This is a mutation score for the declared 100-case campaign—not
an exhaustive proof of the eight designs—but it is the first repository-scale
coverage-closure result with explicit family-level accounting.
The independent mutation checker caught and the producer fixed a stale
campaign self-digest caused by adding metadata after the initial report hash.
The corrected campaign now passes both the 100/100 mutation run and the
independent child-record/report integrity check.
The specification-grounded auto-formalization matrix now runs four designs
(counter, arbiter, decoder, and FIFO) through requirement extraction, typed
assertion-agent admission, explicit SVA lowering/compiler validation, and
evidence emission. All four pass, and the independent matrix checker confirms
the self-digest and every result/agent/validation artifact. This is compilation
and admission evidence, not a formal-proof or signoff claim.
The adversarial-security workstream now includes
`scripts/run_security_regblock_campaign.py`: eight distinct register-policy
attacks spanning unauthorized addresses, write-enable bypass, reset integrity,
data corruption, and address-map remapping. Every task is detected, localized,
repaired starting from the adversarial candidate, retested on that repaired
copy, and regressed against the canonical source. Per-task digests prove the
mutant differs, the repaired copy matches canonical, and canonical RTL is
unchanged; all eight machine checks pass, while every result remains
`review_required` until a human approves it. This extends the prior single
red/blue task into a machine-auditable policy campaign without claiming
security certification.
The new `scripts/run_seeded_agent_repair_closure.py` extends this from
patch-candidate validation to disposable repair closure across all sixteen
mutation variants. Each mutated copy fails the original check, the bounded
agent repair is applied only to a separate copy, the repaired check passes,
and the canonical source remains unchanged: 16/16 tasks passed with the mock
transport. This is benchmark-evaluation approval only; production edits still
require the explicit human approval gate.
The agent-team transport now binds each role's expected proposal kind into the
backend request, and the resident Hugging Face adapter honors that binding for
repository diagnosis, next-action, and repair roles. This prevents a valid
model response from being misclassified solely because the transport used a
generic task string.
M3 also has a typed proof-agent trajectory in
`verification_platform/proof_agent.py`: an LLM may propose a `lemma` and a
reviewer may propose an assumption/reachability action, but neither role can
claim proof. The local fixture exercises both handoffs under the same
review-only contract.
An actual cached Qwen2.5-Coder 0.5B CPU probe was also attempted. The model
weights loaded, but generation exceeded the backend's 30-second request
budget, so all four role results were correctly recorded as `blocked`; this is
an execution-capacity limitation, not evidence of model quality.
The local model transport now accepts `VERIFICATION_LLM_TIMEOUT_SECONDS`, and
the Colab launcher sets a 300-second request budget so model loading and
generation are not conflated with a fixed 30-second protocol timeout. A
matching timeout policy now applies to the OpenAI-compatible local adapter as
well. A follow-up CPU initialization probe still exceeded the available local
window;
no real-model quality claim is made until the GPU run completes.

The current slices are now composed by
`scripts/run_next_stage_milestone.py`. Its verified aggregate run passed the
repository fail-to-pass task, sixteen-variant mutation closure, three repaired inductive
proofs, security red/blue checks, the three-vector OpenROAD GCD task, the native
OpenROAD FIFO functional task, the AES-128 known-answer task, the four-role fixture-agent handoff, and the
sixteen-task disposable agent-repair closure, plus the native OpenROAD compile
suite and agent-repair closure. The security component remains
`review_required` inside the report by design; aggregate pass means every
declared machine stage completed, not that security signoff was automatic.
The aggregate command now accepts `--agent-backend mock|local`, and agent-team
records include per-role latency. `mock` remains the provider-free
reproducibility path; `local` uses the configured JSONL model backend and is
the path intended for Colab/GPU execution.
Repository diversity now includes a second native checkout: the
`openlane-native-compile` aggregate stage runs Yosys syntax/elaboration checks
over three OpenLane designs at revision `ff5509f6` (timeout, counter, and
peripheral). All 3/3 pass. This broadens tool/repository coverage, but remains
a compile/elaboration result rather than a full OpenLane physical-design or
signoff result. The new `openroad-native-compile` stage performs the same
native check over GCD and AES at revision `be0dca0b1`; both 2/2 designs pass.
The `openroad-fifo-functional` stage also passes a real asynchronous-clock
FIFO write/read transaction at that revision, including synchronized status
and data sampling. This is one functional transaction, not CDC stress or full
project regression coverage.
The `openroad-aes-functional` stage also passes the standard AES-128
known-answer vector (`000102...0f`, `001122...ff` -> `69c4e0...c55a`) at the
same pinned revision. This is one deterministic vector, not exhaustive
cryptographic verification. The `openroad-aes-agent-repair-closure` stage
then mutates the first ciphertext-byte round-key selection, observes the
known-answer failure, repairs it through the bounded agent contract, and
passes the repaired copy while leaving the native checkout unchanged.
The `openlane-timeout-agent-repair-closure` stage extends the same bounded
repair loop to the OpenLane timeout design: its baseline boundary check fails,
the repair passes, and the source digest remains unchanged. The report binds
this working-tree artifact to OpenLane revision `ff5509f6` and its exact source
SHA-256, so it is not presented as a historical upstream fix.
An attempted native OpenLane counter flow reached the flow runner but was
blocked by the checkout's missing/incompatible container manifest: the two
available Ciel Sky130 versions do not currently satisfy OpenLane's expected
container metadata. No physical-flow pass is claimed until that environment
is repaired or reproduced in a pinned container/Colab environment.
The aggregate now also runs `scripts/run_coverage_gap_agent.py`, which converts
the incomplete seeded coverage report into a source-bound, review-required
next-test proposal. It deliberately does not count the proposal as coverage
until an executable rerun produces new evidence.
The executable rerun is now present in `scripts/run_seeded_coverage_closure.py`.
It runs a baseline test and a targeted test against an isolated repaired copy,
binds both results to the same declared counter task revision, and compares
the same four functional points. The observed result is 2/4 before and 4/4
after (`+2`, `converged`). The aggregate milestone includes this stage, so the
coverage proposal is now connected to a real before/after evidence artifact.
The Colab-facing next-stage entry point is now
`analog-digital-chip-design-eda/colab/run_next_stage_colab.py`. It packages the
held-out mutation evaluation, coverage closure, repaired induction, security
red/blue checks, an eight-design repository-agent matrix, sixteen-task agent
repair closure, and a focused repository-agent handoff into one fresh,
self-digested bundle. Its provider-free replay passes all eight components;
`--require-real-agent`
requires an explicitly configured model worker and therefore cannot silently
substitute the fixture backend.
The Colab gate accepts both one-request and resident JSONL batch workers. The
batch transport was previously exercised with six components and completed successfully,
which is the intended lower-overhead path for the 8-design agent matrix and its
sixteen-task repair-closure extension.
The remote launcher
`analog-digital-chip-design-eda/colab/run_next_stage_agent_matrix_remote.sh`
is prepared for an authenticated T4 run. It pins the model download inside the
runtime, invokes the resident batch worker, downloads the self-digested report,
and cleans up its uniquely named session. Its remote step wrapper now converts
installation, model-download, process, and timeout failures into bounded
step records so the final summary remains recoverable. A launch attempt on 2026-09-14 was
rejected by Colab with `TooManyAssignmentsError` because two pre-existing T4
sessions already occupied assignment capacity; no existing session was reused
or modified. A subsequent uniquely named launch received an HTTP 503 from the
Colab assignment service before session creation. The launcher now records
that external failure in `colab-launch-failure.json` and exits without claiming
model or verification evidence; the retry produced that artifact and did not
reuse or modify either existing session.

An independent checker is now available at
`scripts/check_next_stage_milestone.py`. Against the latest 55-component
aggregate report it verified the expected component set, zero return codes,
`all_passed=true`, and the report SHA-256 digest. This checker validates report
integrity; it does not upgrade review-required security or model claims.
The next-stage local closure is now also a dedicated CI job in
`.github/workflows/verification-pilot.yml`. It runs the held-out mutation,
coverage, induction, security, 8-design agent matrix, matrix-integrity check,
and focused contract tests using only open-source tools and the mock transport.
The exact CI command sequence was replayed locally: all machine stages passed
and 27 focused tests passed.
The script `scripts/run_repository_agent_approved_retest.py` now bridges an
agent run into the existing approval-gated retest API. Without `--approve` it
creates only a self-digested `review_required` package containing the exact
source edit and does not create the destination copy. Approval requires both a
reviewer identity and an approval note; only then may the existing copy-only
retest run. This review-only path was exercised against the seeded counter
agent run and passed its no-mutation boundary.

The held-out agent-repair evaluator is now available at
`analog-digital-chip-design-eda/scripts/run_heldout_agent_repair_evaluation.py`.
It derives train and held-out ranges from the declared mutation evaluation
plan, preserves suite order, runs both splits through the isolated
repair-closure harness, and reports separate closure rates. Its independent
checker is
`analog-digital-chip-design-eda/scripts/check_heldout_agent_repair_evaluation.py`.
The provider-free control run passed 8/8 train and 8/8 held-out repairs with
exact task identity and digest checks. This demonstrates split hygiene and
evaluation plumbing; because it uses the mock transport, it is not
real-model generalization evidence. A real Colab run is the next required
measurement. The authenticated Colab benchmark runner now invokes this
evaluator with its resident model worker, downloads the held-out report, and
requires the independent checker before the Colab job can report success.
The Hugging Face worker and agent-team envelope now retain
`_model_generated_fields` and `model_selected_repair` metadata. The strict
real-backend checker requires a 1.0 model-selected-repair rate on both splits;
request-bound repair text alone cannot satisfy that gate. The mock control
continues to pass closure while reporting a 0.0 model-selection rate, making
the distinction explicit.
An attempted real held-out launch on 2026-09-14 was rejected by the Colab
assignment service with HTTP 503 before session creation. The improved launcher
retained this as
`analog-digital-chip-design-eda/.artifacts/llm-agent-colab/agent-heldout-20260914b/colab-launch-failure.json`;
it confirms that no model or verification evidence was produced.
The benchmark launcher now uses the same bounded assignment retry policy as the
next-stage launcher. A two-attempt retry on 2026-09-14 received HTTP 503 on
both attempts, recorded `assignment_attempts: 2`, and confirmed
`session_created: false` in
`.artifacts/llm-agent-colab/agent-heldout-retry2-20260914/colab-launch-failure.json`.
This improves recoverability without weakening the fail-closed evidence gate.
The one-shot Hugging Face backend was then aligned with the resident worker:
it now shares typed prompts and request-bound repair/assertion/lemma fields,
and resolves the local Hugging Face hub snapshot when no explicit model path is
provided. A corrected one-task Qwen CPU probe reached the model worker but
timed out during inference at the configured 300-second role budget. This is
recorded as an execution-capacity result, not model-quality evidence. The
backend and agent-team regression tests pass, and the full repository suite
passes 663 tests.

## Non-goals and claim boundaries

- This is not a claim of zero-bug silicon or automatic production release.
- FPGA frequency, commercial EDA equivalence, and physical signoff remain
  separate claims requiring their own evidence.
- A benchmark result on seeded toy designs is not a repository-scale result.
- LLM rationale is not proof; only replayable tool evidence can establish the
  corresponding technical status.
The development replay queue now contains exactly 40 candidates after
excluding the ten validated commits and the held-out set. Its independent
queue checker passes, so the remaining path to the 50-fix target is explicit
and scope-controlled. The 55-stage aggregate includes both queue gates.
