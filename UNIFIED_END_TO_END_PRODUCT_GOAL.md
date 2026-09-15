# Unified end-to-end product goal

## Objective

Deliver a commercially credible, evidence-first AI hardware verification and
inference qualification platform. A user must be able to start with model and
semiconductor collateral, execute a reproducible digital verification flow,
qualify the mixed-signal implementation that supports it, and make a bounded
ship/no-ship decision from one reviewable evidence package.

The product journey is:

```text
collateral and workload intake
 -> typed design/model contract
 -> verification and qualification plan
 -> generated checks and execution
 -> failure localization and root-cause analysis
 -> human-reviewed repair or calibration
 -> identical-scope retest and comparison
 -> coverage, accuracy, latency, energy, and yield metrics
 -> signed release decision and exportable evidence bundle
```

## Product boundary

The deterministic platform owns parsing, schemas, source and artifact hashes,
tool invocation, run isolation, capability detection, policy gates, and
release claims. AI agents may propose plans, tests, assertions, diagnoses,
repairs, and next experiments. They may not invent evidence, silently mutate
source, promote blocked capabilities, or claim verification closure without
the required tool output and human decision.

The open-source digital flow is the reference backend. Icarus, Verilator,
Yosys/SymbiYosys, Python models, SPICE, and checked-in evidence are sufficient
to prove the workflow. Proprietary simulators, formal tools, emulators,
regression databases, and silicon measurements enter through adapters and are
not fabricated when unavailable.

## Delivery phases

1. **Reference verification product:** collateral ingestion, typed IR/RAG,
   planning, procedural and SVA generation, simulation/formal execution,
   waveform and dependency-cone triage, bounded repair, retest, comparison,
   coverage, lifecycle audit, browser UX, CLI/API, and immutable bundles.
2. **Public benchmark:** run the same journey across several open RTL designs
   with seeded bugs, formal counterexamples, coverage gaps, stale/missing
   artifacts, and adversarial user flows. Publish reproducible accuracy,
   debug-time, review-effort, traceability, and invalid-closure metrics.
3. **AIMC qualification case study:** connect workload/model evidence to
   converter, array, controller, data-movement, SPICE, layout, calibration,
   mismatch, and hardware-runtime evidence. Keep software agreement,
   simulation qualification, physical qualification, and measured hardware
   claims separate; unsupported gates remain visibly unsupported.
4. **Commercial pilot deployment:** add managed persistence and object storage,
   enterprise identity/RBAC, tenant and per-job isolation, observability,
   backup/restore and key rotation, CI integration, customer EDA adapters, and
   signed pilot measurement on representative collateral.

## Definition of done

An independent reviewer can reproduce a versioned run from the shipped
artifacts, understand every failed or blocked stage, inspect the exact source
and waveform/counterexample evidence, approve or reject a bounded change,
confirm that retest scope is unchanged, and verify the hashes and sign-off
receipt. The release reports both digital verification closure and AIMC
qualification status, including explicit evidence gaps and customer-owned
production gates.

This goal is simulation-first and does not require proprietary tools or real
silicon to complete its reference release. Customer infrastructure and
measured hardware are required only for the corresponding commercial and
physical qualification gates.

## Current evidence and next executable increment

The reference verification slice is already executable: the maintained
deployment and platform suite passes its local checks, and the multi-design
open-source pilot passes all eleven retests with intact artifact, session,
summary, taxonomy, scope, and release digests. The pilot deliberately starts
each design with a seeded failure, so its eleven baseline failures are expected
evidence rather than regressions in the harness.

The public reference contract is now locally closed. The canonical command
`python3 scripts/run_public_reference_acceptance.py` rebuilds the pilot and
scorecard, verifies the evidence hashes, builds and verifies the source-only
archive, replays it from a clean extraction, and runs the deterministic
browser/API adversarial gate. Its acceptance record is
`.artifacts/public-reference-acceptance.json`; the decision is bounded to
reference-release readiness and does not authorize AIMC or hardware claims.

The next local-only increment is the model-to-chip software qualification
slice: take the frozen transformer workload through the digital reference,
profile-driven hybrid simulator, compiler/runtime trace, error budget, and
fallback decision in one reproducible package. Physical, GPU, and measured
hardware gates remain separate future inputs rather than prerequisites for
this software closure.

The canonical joined local command is now
`python3 scripts/run_local_unified_release_acceptance.py`. It runs the public
digital reference acceptance, synthetic customer-pilot certification, and
model-to-chip qualification orchestrators,
then records one hash-bound decision package. A green result means the local
software/reference package is ready for sign-off; it does not change the
physical, GPU, or measured-hardware gate state.
The independent verifier is
`python3 scripts/check_local_unified_release_acceptance.py`; it rejects stale
decision digests, missing stages, unsafe paths, and changed bound artifacts.
The non-destructive checkpoint command is
`python3 scripts/build_local_checkpoint_manifest.py`; it records repository
heads, dirty-path counts, and acceptance-artifact hashes without creating a
commit or changing evidence.

The current gate audit reports 110 of 118 production controls verified. The
remaining eight are customer-owned deployment and pilot controls: managed
state, versioned evidence storage, enterprise identity, isolated execution,
centralized operations, customer EDA adapters, disaster recovery/key rotation,
and a signed measured pilot. The AIMC physical evidence audit currently passes
21/21 implemented checks but leaves the nominal continuous-SAR map in
qualification-open status. These are explicit evidence gaps, not failures of
the open-source reference workflow.

The first cross-domain release artifact is now generated at
`analog-digital-chip-design-eda/.artifacts/unified-hardware-verification-release.json`.
It binds the digital pilot release to the AIMC evidence manifest, verifies the
referenced hashes, and emits `blocked_pending_qualification` while physical
and measured-hardware claims remain unsupported.

The AIMC case study now also has a portable local qualification bundle. Running
`python3 scripts/run_local_derived_qualification.py` rebuilds the digital
qualification and counterfactual sensitivity reports, exports a ZIP evidence
archive, and checks all source hashes in fresh temporary directories. The
bundle's decision is `digital_reference_and_deterministic_fallback_only`; it is
reviewable software/model evidence and does not close the physical or measured
hardware gates.

The local reference backend path is also smoke-verified through model intake,
analysis, quantization, runtime/baseline comparison, evidence preview and
import, persistence, run comparison, and ZIP archive retrieval. The current
smoke result reports six declared evidence sources, five imported local
artifacts, four supported bounded claims, and `decision=needs rewrite`; this is
reference-product evidence, not a measured hardware qualification result.

The provider-free customer-pilot certification path is also closed locally.
`python3 analog-digital-chip-design-eda/scripts/run_customer_pilot_certification_gate.py`
passes three isolated synthetic projects, recovery and adversarial checks,
public-archive replay, and commercial-handoff verification. Its result is
synthetic reference evidence only; the eight remaining production controls
(managed state, storage, enterprise identity, isolation, operations,
customer-specific adapters, disaster recovery/key rotation, and a signed
customer pilot) remain intentionally customer- or infrastructure-owned.

The next local-only meaty goal is specified in
`docs/roadmaps/next-local-meaty-goal-replayable-model-to-chip-package.md`.
It closes the replayable digital-to-hybrid software decision loop across a
versioned profile family, compiler/runtime trace, deterministic fallback, and
mutation-resistant archive. It does not promote synthetic profiles to physical
evidence or authorize CUDA, board, silicon, or energy claims.

The broader North Star and the canonical flagship implementation goal are
specified in
`docs/roadmaps/autonomous-silicon-design-verification-north-star.md`. That
roadmap connects the existing verification pilot to the AIMC RTL-to-GDS/STA
flow through ten explicit subgoals, from requirement freeze and failure
diagnosis through approved repair, physical implementation, signoff evidence,
and clean-checkout replay.

The first executable bridge for that flagship goal is
`analog-digital-chip-design-eda/scripts/run_verified_rtl2gds_bridge.py`. It
checks the canonical AIMC RTL simulation, verifies byte-identical alignment
with the RTL consumed by the existing OpenLane package, and independently
rechecks the aligned physical signoff manifest. Its result is local
open-source evidence only. The corresponding
`check_verified_rtl2gds_bridge.py` command independently validates the joined
report and reruns the physical-package check.

The next meaty goal to pursue is the agentic hardware failure-to-closure loop
defined in
[`docs/roadmaps/next-meaty-goal-agentic-hardware-closure.md`](docs/roadmaps/next-meaty-goal-agentic-hardware-closure.md).
It makes the LLM diagnosis, bounded repair, human approval, identical-scope
retest, RTL-to-GDS evidence, and held-out-design generalization one explicit
acceptance journey. Analog authorization remains fail-closed until its
independent physical converter gates pass.

The deeper SOTA follow-on is defined in
[`docs/roadmaps/next-four-sota-workstreams.md`](docs/roadmaps/next-four-sota-workstreams.md):
repository-scale generalization, proof-carrying repair closure, scalable
semantic debugging with compiler/IR support, and structured collateral through
physical signoff. These are proposals with explicit acceptance gates, not
claims that the current reference flow has already completed them.

The flagship integrated goal that should guide the next implementation cycle
is documented in
[`docs/roadmaps/next-flagship-end-to-end-hardware-qualification-goal.md`](docs/roadmaps/next-flagship-end-to-end-hardware-qualification-goal.md).
It joins the real causal-agent repair trajectories, proof-carrying closure,
RTL-to-GDS evidence, model-to-chip qualification, and eventual physical and
measured-hardware adapters into one independently replayable decision package.

The repository-scale implementation now passes a 161-stage aggregate.
Fifty historical repairs have been independently replayed across OpenLane,
OpenROAD, and cross-sim. A deterministic miner found 291 additional upstream
fix candidates, including 58 held out, and a 40-item development-only replay queue excludes both the
validated commits and the held-out evaluation split. The 50-fix benchmark gate
is now satisfied; the aggregate status remains evidence of workflow integrity,
not a claim of broad production generalization or silicon signoff.

The held-out repair evaluator has also passed its provider-free control run:
8/8 declared development cases and 8/8 declared held-out cases pass through
the isolated closure harness, with independent task-identity and digest
checks. This validates split hygiene and the evaluation plumbing only; the
control intentionally reports zero model-selected repairs. A real Qwen result
still requires an authenticated Colab GPU execution through the resident
model runner and strict real-backend checker.

Workstream 2 now has a proof-carrying closure certificate. The
certificate binds the aggregate report and independently checked simulation,
mutation, formal, coverage, security, and assertion-integrity artifacts by
content digest. It is emitted by `scripts/build_proof_carrying_closure_certificate.py`
and independently checked by `scripts/check_proof_carrying_closure_certificate.py`.
The updated certificate and independent checker pass against
`/tmp/next-stage-milestone-143-operation-20260915/`.

The real-design increment now catalogs and compiles ten distinct multi-module
RTL targets from the local OpenLane and OpenROAD-flow-scripts repositories,
with source digests and hierarchy metadata. This establishes the real-design
corpus gate; functional mutation localization, multi-clock failure replay, and
production-design coverage remain separate claims.

The first real functional replay now passes on the OpenLane two-module
`peripheral` hierarchy: an unauthorized CSR write fails on the mutated copy,
the agent repair restores address decoding, and the repaired copy passes with
canonical source unchanged. This is one real protocol invariant, not closure
of all ten designs. The second real replay is the multi-clock CDC case: the
two-stage maintenance-budget synchronizer is mutated, the failure occurs in
the CDC testbench, and the agent repairs the uniquely scoped sequence.
The third real replay covers an AIMC operation-partition decision boundary:
mutating the stale-calibration condition causes a focused behavioral test to
fail, and the agent repairs the disposable copy with canonical source
unchanged. These are three real invariants, not full production closure.
The fourth real replay covers the AIMC error-budget governor: mutating the
drift-age boundary causes the policy test to fail, and the agent repair passes
with canonical source unchanged. The updated aggregate and proof certificate
pass at `/tmp/next-stage-milestone-145-error-budget-20260915/`.
The refreshed aggregate adds a real waveform causal-localization gate and its
independent checker; the proof certificate passes at
`/tmp/next-stage-milestone-147-causal-20260915/`.
The updated package also includes sequential multi-clock causal localization
and its independent checker at
`/tmp/next-stage-milestone-149-multiclock-causal-20260915/`.
The latest package adds causal-evidence consumption by the real multi-clock
agent repair trajectory and passes at
`/tmp/next-stage-milestone-151-causal-agent-20260915/`.
The operation-partition causal report is now consumed by a second real agent
repair trajectory. Its digest-bound frontier and repaired retest pass as part
of `/tmp/next-stage-milestone-153-operation-causal-agent-20260915/`, and the
aggregate plus independent proof certificate pass.
The error-budget policy boundary now has the same causal-localization and
causal-agent repair contract, yielding three real causal-agent failure
classes. The expanded aggregate and proof certificate pass at
`/tmp/next-stage-milestone-157-error-causal-agent-20260915/`.
The CSR peripheral path now also passes the contract, completing four real
causal-agent failure classes. The aggregate and proof certificate pass at
`/tmp/next-stage-milestone-161-four-causal-agent-20260915/`.
The real-model handoff is now packaged for Colab: the OpenLane RTL, causal
report, verification platform, and model backend are bundled together. The
bundle passes an offline extraction-and-repair smoke test; live Qwen execution
still requires an available Colab GPU session.
The four-class handoff is now also packaged by
`scripts/package_real_four_causal_agent_colab_task.py`; its offline smoke test
executes all four real repair trajectories and their independent checkers.
