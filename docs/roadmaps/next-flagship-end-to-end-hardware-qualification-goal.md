# Flagship end-to-end goal: evidence-carrying agentic hardware qualification

## Executive objective

Build one reproducible, reviewable, end-to-end hardware engineering system that
can move from a real model and hardware requirement to a bounded ship/no-ship
decision without confusing proposal, simulation, physical implementation, or
measured silicon evidence.

The system should accept a versioned workload, executable requirements,
structured design collateral, RTL, analog/mixed-signal constraints, and
available tool capabilities. It should then plan and execute verification,
localize a seeded or naturally occurring failure, ask an agent for an
evidence-grounded diagnosis and bounded repair, require a human decision for
any intent-changing action, retest the disposable repaired copy at identical
scope, carry the accepted digital design through physical implementation, join
it to the model-to-chip qualification package, and emit a signed evidence
bundle that says exactly what passed, what failed, what is blocked, and who
approved the decision.

The product claim is deliberately narrower and stronger than autonomous
tapeout:

> An agent can reduce the cost and time of hardware verification and
> qualification while deterministic tools, immutable evidence, independent
> checkers, and human approval control every state-changing transition and
> every release claim.

The final system must make unsupported claims impossible to promote by
accident. A green digital run must not become a silicon claim. A clean OpenLane
run must not become foundry signoff. A synthetic converter profile must not
become measured energy or accuracy. A valid LLM response must not become an
approved repair.

## The journey to close

```text
model and hardware collateral intake
  -> versioned workload and requirement contract
  -> typed design / protocol / physical constraint IR
  -> capability-aware verification and qualification plan
  -> generated tests, assertions, scoreboards, and measurement requests
  -> deterministic baseline simulation, formal, lint, and structural analysis
  -> waveform / counterexample / state-frontier causal localization
  -> evidence-grounded agent diagnosis
  -> bounded repair proposal and adversarial review
  -> explicit human approval or rejection
  -> disposable-copy patch application
  -> identical-scope digital retest
  -> repository-scale held-out replay
  -> synthesis, placement, CTS, routing, extraction, STA, DRC, LVS, and ERC
  -> compiler/runtime/model-to-chip qualification
  -> physical converter and measured-hardware evidence ingestion
  -> signed release manifest and ship/no-ship decision
  -> clean-checkout replay and long-term audit
```

Every arrow is an evidence boundary. The system must preserve the input and
output digests, tool versions, capability decisions, source revision, scope,
operator identity, and claim class for every transition.

## Why this is the next flagship goal

The repository already contains strong slices of the required system:

- a provider-free public digital verification release;
- seeded failures, generated checks, formal evidence, simulation, triage,
  bounded repair, and retest artifacts;
- repository-scale historical repair replays;
- proof-carrying closure certificates;
- real multi-module RTL structural and causal-localization evidence;
- four real causal-agent repair trajectories;
- an RTL-to-GDS bridge for a local AIMC control subsystem;
- a replayable model-to-chip software qualification package;
- profile-driven hybrid execution and deterministic fallback accounting; and
- explicit fail-closed boundaries for analog, GPU, measured-hardware, and
  production claims.

The next step is to stop treating these as adjacent demonstrations and make
them one acceptance journey. The flagship milestone is complete only when an
independent reviewer can begin with the package, reproduce the baseline
failure, inspect what the agent saw, verify the proposed change, approve or
reject it, reproduce the retest and physical evidence, and make a bounded
release decision without relying on hidden state or trust in the orchestrator.

The current provider-free aggregate checkpoint now passes all 163 declared
components, including the real-design catalog, four causal-agent trajectories,
1,000-mutation closure, held-out split plumbing, formal/coverage/security
checks, OpenROAD tasks, historical repairs, and the specification-grounded
assertion matrix. Its compact repository receipt is
`.artifacts/flagship-next-stage-20260915-receipt.json`. This is meaningful
integration evidence, but its claim boundary remains local seeded, OpenROAD,
and fixture-agent acceptance; it is not model generalization, silicon signoff,
or production readiness.

The four real causal-agent classes have also been rebuilt from the current
checkout: CSR peripheral, AIMC operation partition, AIMC error budget, and
multi-clock CDC. Their causal reports, package digest, and four independently
checked disposable-copy repairs are recorded in
`.artifacts/flagship-four-causal-agent-20260915-receipt.json`. The local
verified RTL-to-GDS bridge independently passes source alignment and physical
package recheck; commercial EDA, analog, measured-hardware, and silicon gates
remain separate.

The first authenticated real-model run is preserved under
`.artifacts/real-model-colab/20260915T173123Z/`. Qwen
`Qwen/Qwen2.5-0.5B-Instruct` ran on a Tesla T4, and the primary benchmark
passed 11/11 grounded, diagnosis-matching, adversarially accepted cases with
three unsafe-claim rejections. The same run correctly remains blocked for the
full four-workstream matrix and held-out repair generalization: the matrix
failed its expected classifications and the train/held-out repair closure was
0/16 with zero model-selected repairs. This is model-evaluation evidence, not
generalization proof or release authorization.

The first replay also exposed and closed an integration defect in the causal
frontier contract: when a seeded bug leaves an output stuck, the output has no
VCD transition at the first divergent reference timestamp. The debugger now
binds that observed frontier sample explicitly, preserves the digest-bound
waveform/source contract, and uses deterministic RTL assignment localization
when no structural edge is available. The four-design repair matrix and the
full provider-free four-workstream wrapper now pass all four disposable-copy
repairs, while the real-model path remains separately measured and fail-closed.

## Core design principles

### Evidence before agency

Agents may plan, summarize, diagnose, propose tests, propose assertions,
propose repairs, and suggest the next experiment. They may not invent tool
results, edit canonical source, suppress a failure, broaden a claim, or declare
closure. The deterministic platform owns parsing, hashing, execution, scope,
policy, and release status.

### Immutable source and disposable change

Canonical RTL, analog netlists, workloads, calibration data, and requirements
are content-addressed. Repairs apply only to disposable copies. The original
source hash is checked before and after every run. Any mismatch fails the run.

### Identical-scope retest

The post-repair run must use the same design inputs, tests, assertions, formal
properties, assumptions, clocks, resets, timeouts, tool capability, and
coverage contract as the baseline unless a reviewer-approved scope change is
recorded. A passing result with a smaller or altered scope is not closure.

### Claim separation

The release manifest distinguishes at least `passed`, `failed`,
`review_required`, `blocked`, `modeled`, `measured`, `not_run`, and
`unauthorized`. Digital correctness, physical implementation, model quality,
analog qualification, GPU performance, measured energy, silicon behavior, and
production readiness are separate claim classes.

### Independent verification

The tool that produces a report cannot be the only tool that decides whether
the report is valid. Every major package needs an independent checker that
recomputes hashes, validates schema and scope, rejects stale artifacts, checks
source immutability, and verifies the stated claim boundary.

### Honest negative results

The system is successful when it proves that a path is not yet qualified. A
profile that routes to fallback, a converter that misses voltage margin, a
formal property that is vacuous, or a physical gate that is unavailable must
remain visible and actionable rather than being replaced by optimistic prose.

## System contracts

### 1. Workload and requirement contract

Freeze the model revision, operator graph, tensor shapes, dtypes, seeds,
calibration split, held-out split, expected outputs, tolerance policy,
latency/energy accounting scope, and all source hashes. Each hardware
requirement receives a stable ID and a measurable acceptance predicate.

The contract must cover both the digital design and model-to-chip path:

- protocol and register semantics;
- clock, reset, and CDC assumptions;
- numerical tolerance and error budget;
- fallback and timeout policy;
- conversion, buffering, and data-movement rules;
- physical timing, area, DRC, LVS, antenna, and ERC expectations; and
- the evidence tier required for each claim.

### 2. Typed collateral and IR contract

Ingest the supported subset of SystemRDL/IP-XACT-like register collateral,
protocol descriptions, RTL, software headers, UVM metadata, clock/reset
constraints, physical constraints, workload tensors, and converter profile
families into typed intermediate representations.

The IR must preserve hierarchy, source locations, requirement IDs, temporal
properties, clock domains, reset guards, parameter values, and digest-bound
relationships. Silent assertion deletion, lost reset guards, dropped binds,
or untracked source substitution must be fatal errors.

### 3. Baseline execution contract

Run the strongest available deterministic stack: parsing, structural checks,
lint, simulation, formal, mutation testing, coverage, waveform capture,
dependency slicing, and tool-specific physical checks. Record unavailable tools
as blocked rather than replacing them with inferred success.

The baseline must include a real failure for benchmark cases. Expected seeded
failures are evidence that the harness can detect the defect; they are not
regressions in the harness.

### 4. Causal-debugging contract

For every failure, produce a compact but replayable explanation containing the
first divergent cycle or event, observed and expected values, dependency cone,
causal frontier, relevant clock/reset context, competing explanations, and
evidence references.

For waveforms and formal traces, the system should build cycle-indexed causal
graphs and align RTL state with a reference model where one exists. The agent
receives a digest-bound slice, not an unbounded unverified transcript, and its
diagnosis must identify the exact design revision and evidence it used.

### 5. Repair contract

Every proposal must be schema-valid, source-grounded, bounded to an allow-listed
operator or exact before/after edit, and explicit about expected effect and
risk. It must not claim verification closure. An adversarial checker must
reject unsupported files, ambiguous edits, broad rewrites, stale evidence,
source-hash mismatch, or a proposal that changes the test scope.

Human approval must name the reviewer, proposal digest, source digest, scope,
reason, and decision. Rejection is a first-class outcome.

### 6. Retest contract

Apply the approved change only to a disposable copy. Re-run the identical
baseline scope, then independently compare:

- source and patch digests;
- test and assertion inventories;
- formal assumptions and solver settings;
- simulation inputs, clocks, resets, and timeouts;
- coverage and mutation results;
- failure and repair traces; and
- canonical-source immutability.

The retest must demonstrate that the original failure is gone and that
representative neighboring behavior has not regressed.

### 7. Physical handoff contract

The repaired RTL entering synthesis must be byte-identical to the approved
disposable copy, and the physical run must bind its source digest to the
release manifest. The package must independently check synthesis, placement,
CTS, route, extraction, STA, DRC, LVS, antenna, ERC, GDS, LEF, LIB, SDC, SPEF,
and SDF evidence when the tools exist.

Local open-source flows may establish implementation evidence. They must not
be labeled commercial EDA signoff, foundry signoff, tapeout readiness, or
silicon correctness.

### 8. Model-to-chip qualification contract

Run one frozen transformer slice through digital reference execution, nominal
and adverse converter profiles, hybrid execution, compiler partitioning,
runtime scheduling, transfer accounting, calibration, error budgeting, and
deterministic fallback.

Compiler and runtime traces must agree on tensor identity, operator order,
partition, conversion count, bytes moved, retry behavior, and fallback reason.
Synthetic profiles remain modeled or counterfactual. Fresh GPU, SPICE, board,
and silicon measurements replace only their corresponding evidence inputs;
they do not change the workload or authorization contract.

## Workstreams and acceptance gates

### Workstream A: production-shaped evidence plane

Implement one canonical evidence schema and release manifest spanning digital,
physical, model-to-chip, and measured-hardware records. Add content-addressed
artifact storage, run isolation, provenance, signed reviewer receipts, export,
import, clean extraction, and independent verification.

Acceptance gates:

- every artifact has a source/tool/input digest;
- stale or modified artifacts are rejected;
- unsafe paths and canonical-source mutation are rejected;
- the manifest separates claim classes and unsupported gates;
- a clean checkout can replay the package; and
- a reviewer can inspect the complete decision without hidden database state.

### Workstream B: real-design agentic closure benchmark

Expand beyond selected fixtures using at least 50 historical fixes from at
least three repositories, with at least 15 held out until evaluation. Include
CSR/protocol, reset, CDC, timing, synthesis, physical, numerical-policy, and
security failures.

Acceptance gates:

- every baseline failure is reproduced;
- diagnosis accuracy, repair success, abstention, false-pass rate, patch size,
  wall time, and human review effort are reported separately;
- held-out task identity and split digests are independently checked;
- canonical repositories remain unchanged; and
- the real model is evaluated separately from provider-free control runs.

### Workstream C: proof-carrying repair closure

Bind requirements to assertions, tests, formal properties, mutations, coverage,
security checks, and retest results. Require a closure certificate that a
second checker can validate without trusting the original orchestrator.

Acceptance gates:

- at least 10 designs or blocks and 1,000 parameterized mutations;
- no accepted false pass in the independent checker;
- each repair has pre-repair failure evidence and post-repair proof or bounded
  closure evidence;
- vacuous, unreachable, over-constrained, or deleted checks are rejected;
- coverage loss is rejected or explicitly approved; and
- privilege, reset, isolation, and information-flow checks are represented.

### Workstream D: scalable semantic debugging

Make causal localization useful on large hierarchical and multi-clock designs
by combining structural IR, dependency-cone slicing, waveform causality,
formal counterexamples, golden-model alignment, and typed temporal IR.

Acceptance gates:

- at least 10 multi-module designs including multi-clock and reset behavior;
- at least 90% held-out localization to the correct module and cycle;
- no false pass from an empty property set, dropped bind, lost reset guard, or
  invalid lowering;
- filtered slices compile and replay identically to the full-design failure;
  and
- context reduction, localization accuracy, repair success, and cost are
  measured against full-context prompting.

### Workstream E: structured collateral through physical signoff

Connect one nontrivial block from executable register/protocol specification to
RTL, C headers, UVM models, simulation, formal, synthesis, physical design,
STA, DRC, LVS, and a signed release decision.

Acceptance gates:

- generated RTL, software definitions, UVM metadata, and checks agree;
- timing, area, power, DRC, LVS, antenna, and ERC are individually evidenced;
- unavailable tools remain visibly blocked;
- the physical result is reproducible from clean checkout; and
- the release package distinguishes local implementation evidence from
  commercial and measured signoff.

### Workstream F: model-to-chip and physical qualification

Join the verified digital design to the frozen workload and profile-driven
hybrid execution. Later ingest qualified converter data, fresh GPU data,
board measurements, and silicon results through narrow adapters.

Acceptance gates:

- all profile classes run against identical held-out inputs;
- fallback decisions are deterministic and per-vector explainable;
- compiler/runtime traces agree;
- mutation and clean-extraction replay reject tampered inputs;
- analog authorization stays false until converter gates pass; and
- measured energy, latency, yield, and accuracy are never inferred from
  synthetic or fixture evidence.

## Phased execution plan

### Phase 0: freeze the current baseline

Preserve the current repository state, acceptance manifests, milestone 161
evidence, public reference result, local unified result, and claim boundary in
a remote checkpoint. Record dirty-path and artifact inventories before further
changes.

### Phase 1: join the four real causal-agent classes

Make the CSR, CDC, operation-partition, and error-budget trajectories share one
schema, one closure orchestrator, one reviewer boundary, one independent
checker, and one release manifest. Prove that all four can be exported,
replayed, and rejected under mutation.

### Phase 2: execute a real held-out model evaluation

Run the packaged Colab task with an authenticated model. Preserve every model
request, response, retry, latency, selected diagnosis, abstention, and repair
decision. Compare it to the provider-free control without blending the scores.

### Phase 3: complete proof-carrying breadth

Move from generated stress designs to production-shaped real RTL. Add formal
assumption audits, coverage closure, security policies, and larger mutation
campaigns. Require no false passes from the independent certificate checker.

### Phase 4: complete one structured-spec-to-GDS slice

Choose one multi-clock register/protocol block and drive RTL, headers, UVM,
simulation, formal, synthesis, STA, DRC, LVS, and artifact export from the
same typed source contract. Preserve unsupported commercial-tool gates.

### Phase 5: bind to model-to-chip qualification

Run the frozen transformer workload with the verified digital path, profile
family, compiler/runtime trace, error budget, and deterministic fallback.
Make the package answer whether the hybrid path is locally promising, has no
cost advantage, or remains unresolved.

### Phase 6: accept real physical and measured evidence

Only after independent converter, GPU, board, and silicon evidence is available
should the corresponding adapters be populated. Re-run the same decision logic
without changing the workload, requirements, or claim taxonomy.

### Phase 7: commercial pilot readiness

Add managed persistence, tenant isolation, enterprise identity/RBAC, object
storage, observability, backup/restore, key rotation, customer EDA adapters,
and signed pilot measurements. Keep these controls distinct from the local
reference-release result.

## Metrics that matter

The flagship package must report more than pass counts:

- diagnosis accuracy and localization accuracy;
- repair success, abstention, regression, and false-pass rates;
- mutation detection and formal proof/unknown/vacuity rates;
- assertion integrity and coverage delta;
- context reduction and causal-frontier quality;
- wall-clock, tool time, model latency, and human review effort;
- patch size, source-touch count, and approval-to-retest time;
- physical timing, area, power-model scope, DRC/LVS/antenna/ERC status;
- model accuracy, fallback rate, transfer bytes, runtime, and error budget;
- evidence completeness, replay success, and tamper rejection; and
- the number of claims that are passed, blocked, modeled, measured, or
  unauthorized.

The dashboard must never collapse these dimensions into one unsupported
confidence score.

## Definition of done

The flagship goal is complete when all of the following are true:

1. An independent reviewer can reproduce the baseline from a clean checkout.
2. The package identifies the exact requirement, source revision, failure event,
   causal evidence, and model context shown to the agent.
3. The agent output is schema-valid, source-grounded, bounded, and independently
   checked.
4. Human approval or rejection is explicit and digest-bound.
5. The repair is applied only to a disposable copy.
6. The retest proves identical scope and canonical-source immutability.
7. Held-out real designs test generalization rather than fixture memorization.
8. A proof-carrying certificate binds simulation, formal, mutation, coverage,
   security, and assertion-integrity evidence.
9. Accepted RTL is hash-linked to physical implementation evidence.
10. The frozen workload and compiler/runtime path replay deterministically.
11. Analog, GPU, energy, board, silicon, yield, and production claims remain
    blocked unless their independent evidence exists.
12. The final release manifest supports a bounded ship/no-ship decision from
    the package alone and can be rechecked by an independent verifier.

## Explicit non-goals

This goal does not promise unrestricted autonomous RTL generation, unattended
tapeout, replacement of qualified EDA signoff, fabricated analog data, fresh
GPU measurements without a GPU, measured energy without instrumentation,
silicon correctness without silicon, or production readiness without managed
customer infrastructure.

The system is valuable precisely because it makes those boundaries visible,
machine-checkable, and difficult to bypass.

## Canonical next command sequence

The next implementation cycle should begin with the current provider-free
acceptance and checkpoint, then run the four-class real-agent package through
the independent checker:

```bash
python3 scripts/run_local_unified_release_acceptance.py
python3 scripts/check_local_unified_release_acceptance.py
python3 scripts/build_local_checkpoint_manifest.py
python3 scripts/check_real_four_causal_agent_colab_package.py \
  /tmp/next-stage-milestone-161-four-causal-agent-20260915
python3 scripts/build_flagship_end_to_end_release.py \
  --output .artifacts/flagship-end-to-end-release.json
python3 scripts/check_flagship_end_to_end_release.py \
  .artifacts/flagship-end-to-end-release.json
```

After that control path is green, the highest-value external increment is the
authenticated real-model Colab evaluation. The highest-value local increment
is the first held-out real design through causal diagnosis, bounded repair,
identical-scope retest, and physical handoff under the same manifest contract.
