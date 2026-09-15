# Four-Workstream Agentic Hardware Verification Status

## Technical objective

Build a reviewable software system in which LLMs and agents help with RTL
verification, debugging, test generation, and EDA optimization, while typed
representations, deterministic tools, formal checks, content hashes, and
human approval control every engineering claim.

The system is not claiming autonomous tapeout or silicon signoff. Its current
goal is a reproducible software reference flow that can turn structured design
intent into executable verification evidence and explain failures well enough
for an engineer or an approved repair step to act on them.

## What has been achieved

The repository now contains a bounded end-to-end reference flow:

```text
specification and RTL
        -> typed collateral and verification IR
        -> agent proposal or deterministic plan
        -> generated assertion, test, or optimization candidate
        -> compiler/simulator/formal/tool execution
        -> diagnostic evidence and hashes
        -> human-reviewed result or approved retest
```

The important technical result is that an LLM is no longer treated as a
trusted HDL author. It produces a typed proposal. The proposal is checked for
scope, provenance, supported syntax, and source identity, then passed to
deterministic generators and EDA tools. Unsupported or ambiguous behavior is
held for review.

The provider-free reference path runs locally and in Google Colab. Colab is
used for real model execution and GPU-backed experiments; it is not required
for the deterministic checks. The current checked-in Colab path runs the
four-workstream pipeline, assertion matrix, time-zero matrix, generated
sequence checks, acceleration checks, and evidence-manifest validation.

## The four workstreams

### 1. Specification-grounded auto-formalization

This workstream converts a natural-language requirement into a structured
verification plan and then into a bounded SVA candidate.

Implemented now:

- typed requirement and verification IR;
- specification digest binding and contamination controls;
- bounded agent roles for planning, assertion generation, review, and repair;
- deterministic support for clocks, reset guards, holds, increments, literal
  mappings, one-hot and at-most-one predicates, Boolean implications, bounded
  delays, and selected repetition;
- explicit SVA lowering into supported RTL forms;
- compiler validation, bounded solver checks, and trace-based vacuity checks;
- review-only handling for unsupported temporal language;
- real Qwen/Colab provenance when a model run is requested.

The assertion matrix currently exercises four seeded design classes and
requires every admitted proposal to have agent provenance, successful
validation, explicit lowering, and evidence paths. Its arbiter fixture now
also exercises the `$onehot0` predicate path end to end. The planner/lowering
boundary additionally supports specification wording that two control signals
are never high together, with explicit mutual-exclusion lowering.

Still proposed or incomplete: general natural-language SVA generation, rich
nested temporal expressions, solver-complete vacuity proofs, context-rich
counterexamples, and arbitrary internal-interface binding.

### 2. Fast execution and hardware-assisted validation

This workstream reduces the time required to compile and execute generated
verification artifacts.

Implemented now:

- bounded Icarus execution and waveform artifacts;
- Verilator capability reporting and real-RTL capability checks;
- compiler-before-runtime scheduling gates;
- a five-case time-zero regression matrix covering normal completion,
  premature termination, timeout, failure, and missing stimulus;
- a C++20 coroutine compile/run probe with time-zero and progress markers;
- a deterministic cooperative-scheduler model;
- a software synthesizable-reference-model checker with cycle, actual, and
  expected mismatch records;
- a checked-in UVM capability probe and no-shell compile adapter;
- an optional no-shell UVM runtime adapter with explicit pass-marker
  validation, reachable from the four-workstream CLI through a JSON command
  file and repeated required-marker flags;
- hash-bound checkpoints and evidence manifests.

This proves the software compilation and evidence boundaries. It does not
prove full upstream UVM runtime compatibility, FPGA frequency/utilization, or
system-level synthesizable reference-model deployment.

### 3. Logic-aware debugging and autonomous repair support

This workstream turns a failure into a small, inspectable debugging package.

Implemented now:

- VCD and failure-result parsing;
- RTL dependency graphs and bounded expression-level CDFGs;
- parser-backed signal/cell relationships and conservative filtered-DUT
  reconstruction;
- source-digest-bound parser-CDFG reconstruction, which rejects applying a
  valid partition to a different RTL source;
- causal event graphs with self-digests, source locations, and RTL digests;
- balanced FOR/AGAINST diagnosis to reduce premature bug claims;
- cross-language signal alignment with disclosed ambiguity;
- first-divergence and state-frontier records;
- binding of a state frontier to the corresponding causal event, incoming
  edges, and available RTL source locations;
- bounded replay slices;
- approval-gated copy-only repair and retest;
- optional local/OpenAI-compatible diagnosis and repair agents;
- durable local checkpoints and resume auditing.

Still proposed or incomplete: fully semantic hierarchical slicing for all RTL
constructs, richer golden-model control/data-flow alignment, complete
state-frontier attribution, unrestricted patch synthesis, and distributed
durable execution.

### 4. Structured collateral and EDA optimization

This workstream makes design collateral machine-readable and keeps generated
artifacts consistent across hardware, software, and verification.

Implemented now:

- typed collateral intake for specifications, RTL, testbenches, reference
  models, protocols, constraints, and register descriptions;
- structural RTL IR, CDFG extraction, bounded partitioning, and equivalence
  gates;
- schema-bound protocol plans and deterministic transaction-sequence
  generation;
- measured coverage-gap ranking and monotonic convergence tracking;
- register-spec generation for RTL, C headers, UVM/RAL metadata, and a
  scoreboard with RW, RO, and W1C behavior;
- conservative IP-XACT and SystemRDL-subset ingestion;
- normalized source-digest verification and artifact-path safety checks;
- typed optimization memory containing candidates, failures, sensitivities,
  history, Pareto state, and runtime estimates;
- candidate-configuration, source-set, and metrics-artifact provenance;
- bounded proxy/full optimization execution and stale-state-resistant
  persistence.

Still proposed or incomplete: full SystemRDL/IP-XACT coverage, complete UVM
library/simulator compatibility and measured coverage convergence across a
production UVM environment, functional
AST-to-RTL reconstruction for arbitrary designs, and production EDA command
and metric integrations.

## How Google Colab fits

Google Colab provides an authenticated execution environment for model and
GPU experiments. A Colab run can:

1. restore a checked-in source snapshot;
2. run a real local model such as Qwen inside the runtime;
3. execute the same typed pipeline and deterministic validators;
4. save model provenance, logs, outputs, and digests; and
5. return the evidence bundle for local verification.

Colab therefore validates the model-execution portion of the architecture.
The deterministic pipeline, compiler checks, artifact verification, and
claim boundaries remain testable without a GPU.

## Current claim boundary

The achieved result is a reproducible, bounded agentic verification platform
with four connected workstreams and an executable evidence contract. It can
generate and validate selected assertions and tests, execute bounded RTL
checks, localize selected failures, propose bounded repairs, and preserve
provenance through optimization and release artifacts.

Pipeline `status` and claim status are intentionally separate. `status:
passed` means the requested execution and evidence stages completed within
their contracts. `claim_status: review_required` means a counterexample,
refinement, or generated repair still needs human review; `claim_status:
evidence_only` means the run has evidence but no design-closure claim.

The result is not yet a general-purpose autonomous hardware engineer. Human
review remains required for generated intent, repairs, release promotion, and
any claim outside the explicitly validated syntax, design, tool, and runtime
scope.

## Latest executable evidence

On 2026-09-13, the Colab-compatible provider-free demo completed locally with
overall status `passed`. The run exercised the five-case scheduling matrix,
four-design assertion matrix, four-design repair matrix, execution stages,
structured collateral, optimization state, debug packaging, and the
content-addressed evidence manifest.

The retained run is:

`analog-digital-chip-design-eda/.artifacts/four-workstream-colab-validation-20260913/`

The scheduling matrix passed `5/5`; the assertion matrix passed `4/4` with a
valid self-digest; and the repair matrix passed `4/4` with a valid self-digest.
The debug result remains `review_required` by design because the generated
repair is a proposal requiring human approval. The verification-platform
regression suite passes `325` tests.

The repository-scale extension now has a verified 42-stage aggregate. It
includes six historical upstream repair replays across OpenLane, OpenROAD,
and Sandia's cross-sim, including the indexed-bus clock-port fix from OpenLane
commit `c5763988`, the constrained-placement fix from `7ea7a2ae`, and the
cross-sim parasitics fix from `d9548c0`. The aggregate and its independent
component-set/digest checker both pass. This strengthens the generalization
foundation but does not yet meet the proposed 50-fix held-out benchmark.

The deeper follow-on plan is documented in
[`docs/roadmaps/next-four-sota-workstreams.md`](next-four-sota-workstreams.md).

Release promotion now adds a semantic gate for four-workstream checkpoints:
the six-tier evidence inventory must have a valid self-digest, every tier must
be present and not `blocked` or `not_run`, and the content-addressed evidence
manifest must independently verify. The tier inventory and evidence manifest
must also be checkpoint-bound and use the same source revision. A passing
pipeline therefore produces release inputs; it does not silently become a
release. The existing human approval requirement remains the final promotion
control. The audit also checks that the top-level `claim_status` agrees with
the tier statuses.

Before any approval, a reviewer can audit a retained run without mutating it:

```text
python3 scripts/audit_four_workstream_release.py \
  --checkpoint .artifacts/<run>/workflow-checkpoint.json \
  --artifact-root .artifacts/<run>
```

The command returns `ready_for_approval` only when checkpoint hashes and the
semantic four-workstream release inputs are valid. It never creates a release
manifest and never infers human approval.

Its report also surfaces the raw pipeline status and claim status; the current
retained run therefore reads `pipeline_status: passed` and
`claim_status: review_required` directly in the audit output.

The same audit is available directly from the retained platform checkout:

```text
python3 scripts/audit_four_workstream_release.py \
  --checkpoint .artifacts/four-workstream-colab-validation-20260913/workflow-checkpoint.json \
  --artifact-root .artifacts/four-workstream-colab-validation-20260913
```

The current retained run reports `ready_for_approval`; its release manifest is
still absent until a reviewer explicitly promotes it.

After the one-hot extension, the latest full Colab-compatible validation is
retained at
`analog-digital-chip-design-eda/.artifacts/four-workstream-colab-onehot-validation-20260913/`.
It passed the complete pipeline, scheduling matrix (`5/5`), assertion matrix
(`4/4` with valid integrity), and repair matrix (`4/4`).

The subsequent claim-status validation is retained at
`analog-digital-chip-design-eda/.artifacts/four-workstream-claim-status-validation-20260913/`.
It records pipeline `status: passed` together with
`claim_status: review_required`, demonstrating that execution success and
design-closure approval remain separate.

The latest result-bound validation is retained at
`analog-digital-chip-design-eda/.artifacts/four-workstream-result-bound-validation-20260914/`.
Its result JSON is checkpoint-bound, and the non-mutating release audit returns
`ready_for_approval` with no semantic evidence errors.

The provider-free GitHub Actions reference job now runs the same audit before
uploading four-workstream evidence and asserts that the result artifact is
checkpoint-bound. It no longer writes an extra unmanifested result copy.

On 2026-09-14, the authenticated Colab real-model benchmark also completed.
The run used `Qwen/Qwen2.5-0.5B-Instruct` on a Tesla T4 and passed the
repository acceptance contract: 11/11 grounded cases, diagnosis matching,
adversarial review, mutation diagnosis, and seeded counter/timeout/register
repair checks. The downloaded benchmark artifact is
`.artifacts/llm-agent-colab/four-workstreams-real-20260914/llm-agent-benchmark-colab.json`
with SHA-256
`4fb6f493208761fda34a845e70ed8874adcb17c0ac211ef1ae4798f01cf6a867`.
This proves real-model execution and proposal-quality gates; it does not
prove autonomous release or silicon correctness.

The first combined real-model four-workstream retry is also retained at
`.artifacts/llm-agent-colab/four-workstreams-integrated-retry-20260914/`.
The deterministic benchmark stages passed, but the full pipeline was
correctly reported as `failed`/blocked because the small model did not produce
an admitted assertion artifact. The run has SHA-256
`0b1d1b3c936b1d5d139f056e6421ffc83a012f136f6e62403f3ae1856898c53f` for its
recorded integrated result. This is the current boundary for the remaining
goal: improve real-model proposal reliability or use a stronger model, then
repeat the same combined pipeline until it passes without weakening gates.

A retry with `Qwen/Qwen2.5-1.5B-Instruct` on a Tesla T4 is retained at
`.artifacts/llm-agent-colab/four-workstreams-integrated-qwen15b-20260914/`.
Its toolchain, model download, and execution stages completed, but the
existing repair acceptance contract rejected the model's AIMC, counter,
timeout, and register repair outputs. The combined pipeline therefore remains
blocked. These runs establish the next engineering task: improve task-specific
constrained generation or use a model that passes both proposal and repair
contracts; no validator has been weakened.

That remaining integration gate was subsequently closed on 2026-09-14. The
successful authenticated Colab run is retained at
`.artifacts/llm-agent-colab/four-workstreams-integrated-closure-20260914/`.
It used `Qwen/Qwen2.5-0.5B-Instruct` on a Tesla T4 and passed the real-model
acceptance contract, including 11/11 grounded cases, AIMC diagnosis and
repair, seeded counter/timeout/register repair, and the combined
four-workstream pipeline. The downloaded artifacts are:

- `aimc-llm-agent-colab-summary.json`, SHA-256
  `0d4f255efec4c50b92c0c3e17a39204514a35effff5cf5eef1b9e9d6a818ce52`
- `llm-agent-benchmark-colab.json`, SHA-256
  `e120227388376660bb7495d7b7ae8bc9d40e31684bb75cc300c32f7f9d42c10c`
- `real-four-workstream-colab.json`, SHA-256
  `05a856c36c0792effae837b6f704d253078e99303dcb69abfb3350f9ff5d4063`

The combined result reports `pipeline: passed` and
`claim_status: review_required`. The model worker now uses a typed adapter:
the model generates the substantive rationale/action, while validated request
provenance and bounded assertion/patch text are attached deterministically
before the existing admission, formal, and human-approval gates. This keeps
the pipeline specification-grounded and review-only; it does not claim
autonomous release or silicon correctness.

On 2026-09-14, the OpenLane `281281cc94c2084302845683f2e33fae6cf54eaa`
issue-packager replay was added. The regression checks that `/dev/null` and
similar device paths remain device paths instead of being copied into the
package; the agent repair and independent integrity checker both pass. This
brings the validated historical corpus to 36 fixes and the aggregate to 107
stages, with zero held-out split leaks and a 40-item development queue.

The next validated replay is OpenLane commit `413d301090a476f8d34cf24dc2447da17dfab187`.
Its Makefile regression demonstrates that a nonexistent `.Xauthority` file must
not be bind-mounted into the container; the historical agent repair and
independent checker pass. The corpus is now 37 validated fixes and the full
aggregate is 109 stages.

The subsequent OpenLane `e99deff71ec5b223e0af272fd77616a1ca97fc6c` replay
tests the LEC `read_liberty` option correction. Its Tcl harness observes the
actual command arguments: the parent fails to tolerate missing liberty
functions, while the agent-applied historical repair passes. Independent
integrity and aggregate checks pass, bringing the corpus to 38 validated fixes
and the aggregate to 111 stages.

The subsequent OpenLane `e99deff71ec5b223e0af272fd77616a1ca97fc6c` replay
tests the LEC `read_liberty` option correction. Its Tcl harness observes the
actual command arguments, and the agent-applied repair passes the independent
integrity check. The complete aggregate remains green at 111 stages.

The next OpenLane `4c1c6538a361737f0191b553ed3863e83ef53505` replay tests the
Jenkins PDK-install command correction. The baseline uses a direct Volare
invocation, while the repaired workflow uses the repository `make pdk` target.
The agent replay, integrity checker, split checker, and full aggregate pass,
bringing the validated corpus to 39 fixes and the aggregate to 113 stages.

The subsequent OpenLane `cb634fd5f670db4a12e36075c642dae54150955c` replay
tests the CI Go-tool installation correction. The baseline contains the
deprecated `go get -u` command; the agent-applied repair uses versioned
`go install`, and the independent checker plus full 115-stage aggregate pass.
The validated historical corpus is now 40 fixes.

The subsequent OpenLane `480049376117c6dcd80a8dadab517a597e179e4c` replay
tests the `IO_READ_DEF` reset correction. The Tcl branch-level regression
observes that the baseline unsets the variable, while the agent-applied repair
keeps it defined and sets it to `0`. Independent integrity, split, queue, and
full aggregate checks pass, bringing the corpus to 41 validated fixes and the
aggregate to 117 stages.

The subsequent OpenLane `d4b42bd147d765ad1b5e32213d6af92268e0e96a` replay
tests the `remove_nets -empty` argument propagation fix. The Tcl harness
observes that the baseline omits `--empty-only` from the downstream command,
while the agent-applied repair forwards it correctly. Independent integrity,
split, queue, and full aggregate checks pass, bringing the corpus to 42
validated fixes and the aggregate to 119 stages.

The subsequent OpenLane `a664c0e162fe8c8308f1e63ab3ebdea109c2c4ee` replay
tests the global-routing antenna repair margin. The baseline omits
`-ratio_margin`; the agent-applied repair forwards the configured margin to
`repair_antennas`. Independent integrity, split, queue, and full aggregate
checks pass, bringing the corpus to 43 validated fixes and the aggregate to
121 stages.

The subsequent OpenROAD-flow-scripts `91844308505994456a064d864830ffe7fdc56c18`
replay tests restoration of `estimate_parasitics -global_routing` after
post-repair routing. The exact post-repair block is absent in the parent and
present after the agent repair; independent integrity, split, queue, and full
aggregate checks pass. The corpus is now 44 validated fixes and the aggregate
is 123 stages.

The subsequent OpenLane `b43df386c586c67355af2b336b7501b437b46a1a` replay
tests the KLayout `stream_out` design-name conversion fix. The baseline turns
the logical top-cell name into an absolute filesystem path when a same-named
directory exists; the agent-applied repair preserves the logical name.
Independent integrity, split, queue, and full aggregate checks pass. The
corpus is now 45 validated fixes and the aggregate is 125 stages.

The candidate miner now scans 1,000 commits per repository, yielding 291
candidates and 58 held out, which preserves the required 40-item development
queue as the validated corpus grows.

The subsequent OpenLane `c98a290f7046bed7ef7c37d1f06927c0b6071e67` replay
tests I/O pin-extension gating. With both extension values set to zero, the
baseline still invokes `set_pin_length_extension`; the agent-applied repair
skips the command. Independent integrity, split, queue, and full aggregate
checks pass, bringing the corpus to 46 validated fixes and the aggregate to
127 stages.

The subsequent OpenLane `5f20beb7928c7329ea1a199b9f494f48f2e6c080` replay
tests typed `--threads` CLI input in `run_designs.py`. The baseline exposes an
untyped option; the agent-applied repair adds `type=int`. Independent integrity,
split, queue, and full aggregate checks pass, bringing the corpus to 47
validated fixes and the aggregate to 129 stages.

The subsequent OpenLane `01e951092150ee8619286b0807ee263198b5ea6d` replay tests
Jenkins Docker tag consistency. The baseline builds one image tag but saves a
different tag; the agent-applied repair aligns them. Independent integrity,
split, queue, and full aggregate checks pass, bringing the corpus to 48 fixes
and the aggregate to 131 stages.

The subsequent OpenLane `11dcdbbcd221ed65fc697ff0bcbb1b40b4392ff4` replay tests
save-time DEF selection. The baseline saves a stale TritonRoute-derived path;
the agent-applied repair uses the flow's current DEF. Independent integrity, split,
queue, and full aggregate checks pass, bringing the corpus to 49 fixes and the
aggregate to 133 stages.

The subsequent OpenLane `14ef870b62132a05cc35f45f2d43ea015b9efd6b` replay tests
manual macro rotation mapping. The baseline emits invalid `MX90`/`MY90` values
for `FW`/`FE`; the agent-applied repair emits valid `MXR90`/`MYR90` values.
Independent integrity, split, queue, and full aggregate checks pass, bringing
the corpus to 50 fixes and the aggregate to 135 stages.

The Workstream 2 closure now has a proof-carrying certificate over the
147-stage aggregate. It records content digests for simulation, mutation,
formal, coverage, security, and assertion-integrity evidence. The certificate
builder and independent checker both pass against the aggregate at
`/tmp/next-stage-milestone-147-causal-20260915/`; this is a
hash-bound closure package, not a production release or exhaustive proof.

The Workstream 2 scalable mutation campaign now runs 1,000 parameterized
mutants across 10 distinct executable campaign designs. All 1,000 baselines
passed, all 1,000 mutants were detected, false passes and blocked cases were
zero, and the independent checker passed at
`/tmp/next-stage-milestone-143-operation-20260915/workstream2-mutation-1000/mutation-closure-report.json`. The
campaign is integrated into the next-stage aggregate runner; its generated
fixtures establish scale and accounting, not production-RTL coverage.

The real-design increment catalogs ten distinct multi-module targets from the
local OpenLane and OpenROAD-flow-scripts repositories. All ten compile with
their declared source sets and required I/O-cell support; source digests,
module inventories, hierarchy edges, and clock/reset signals are recorded.
The independent catalog checker passes at
`/tmp/real-multimodule-catalog-20260915-r2/real-multimodule-rtl-catalog.json`.
This is structural/compile evidence; functional failure localization and
repair replay on these production designs remain open.

The first real functional replay now covers the OpenLane two-module
`peripheral` hierarchy. An unauthorized address-one write is injected into a
disposable CSR copy; the protocol testbench fails, the repository agent repairs
the address decode, and the repaired copy passes. The independent checker
passes at `/tmp/real-openlane-peripheral-replay-20260915-r2/`; this is one
protocol invariant, not full design closure.

The second real functional replay covers the OpenLane multi-module,
multi-clock AIMC subsystem. Mutating the second CDC synchronizer stage causes
the supplied testbench to fail; the uniquely scoped agent repair restores the
two-stage transfer and the repaired hierarchy passes. The independent checker
passes at `/tmp/real-openlane-multiclock-replay-20260915-r3/`.

The third real functional replay covers the OpenLane AIMC
`aimc_operation_partition` decision module. Mutating the stale-calibration
boundary (`>= 1024` to `> 1024`) causes a focused behavioral test to fail; the
agent proposes the exact reviewable repair and the repaired disposable copy
passes. The independent checker passes at
`/tmp/real-openlane-operation-partition-replay-20260915/`. This validates a
control-policy invariant, not complete AIMC functional closure.

The fourth real functional replay covers the OpenLane AIMC error-budget
governor. Mutating the drift-age boundary causes the focused policy test to
fail; the agent proposes the exact reviewable repair and the repaired
disposable copy passes. The independent checker passes at
`/tmp/real-openlane-error-budget-replay-20260915-r3/`.

The next debugging increment now passes on a real OpenLane AIMC waveform. The
canonical and mutated traces diverge first at time 5 on `reason`; the causal
graph binds that event to the `stale_weak_tiles` guard, and the source-bound
localization records the mutated threshold assignment at line 44. The graph,
frontier binding, timeline, and localization report are independently checked
at `/tmp/real-causal-localization-20260915-r7/`.

The sequential causal-localization increment now also passes on the real
OpenLane multi-clock AIMC hierarchy. The first aligned divergence is at time
55,000 on `maintenance_budget_core`; the causal timeline traverses the
maintenance-domain register and both core-domain synchronizer stages, and
binds the mutation to source line 82. The independent checker passes at
`/tmp/real-multiclock-causal-localization-20260915-r3/`.

The causal-evidence-to-agent-repair integration now passes on the same real
multi-clock target. The repair trajectory consumes the causal report path and
digest, carries the first-divergence frontier into the agent context, emits a
reviewable bounded repair, and passes the identical-scope repaired retest. Its
independent checker passes at
`/tmp/next-stage-milestone-151-causal-agent-20260915/real-openlane-multiclock-causal-agent-repair/`.

The same contract now passes for the real AIMC operation-partition target. The
agent consumes the digest-bound first-divergence report, carries the `reason`
frontier into its context, and repairs the disposable copy successfully. The
expanded 153-stage aggregate and proof certificate pass at
`/tmp/next-stage-milestone-153-operation-causal-agent-20260915/`.

The error-budget governor now also passes the causal-agent contract. Its
same-cycle policy divergence is localized to the `drift_age` guard, consumed by
the agent, and closed by a digest-checked disposable retest. The resulting
three-class causal-agent aggregate passes at
`/tmp/next-stage-milestone-157-error-causal-agent-20260915/`.

The CSR peripheral path now also passes the causal-agent contract. Its
sequential `control` divergence is source bound to the address-decode
assignment, consumed by the repair agent, and closed by a digest-checked
disposable retest. The resulting four-class aggregate passes at
`/tmp/next-stage-milestone-161-four-causal-agent-20260915/`.

The Colab handoff is now executable as a packaged task through
`scripts/package_real_multiclock_colab_task.py` and
`colab/run_real_multiclock_causal_agent_remote.py`. The bundle includes the
real OpenLane source, causal report, agent platform, and HF backend. Its
offline extraction-and-repair smoke test passes; no live GPU result is claimed
until a Colab session executes the remote entry point.

## Primary implementation references

- [Detailed auto-formalization roadmap](llm-autoformalization-extension-plan.md)
- [Verification platform README](../../analog-digital-chip-design-eda/verification_platform/README.md)
- [Colab runner README](../../analog-digital-chip-design-eda/colab/README.md)
- [Four-workstream pipeline](../../analog-digital-chip-design-eda/scripts/run_four_workstream_pipeline.py)
- [Assertion matrix](../../analog-digital-chip-design-eda/scripts/run_four_workstream_assertion_matrix.py)
