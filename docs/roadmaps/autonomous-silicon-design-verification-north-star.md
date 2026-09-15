# North Star: evidence-grounded autonomous silicon design and verification

## Current physical qualification checkpoint (2026-09-13)

The 520000 candidate is a genuine layout/LVS breakthrough: hierarchy-preserving
extraction is DRC-clean, both preamp branches bind to the exact parent nets,
and independent parent LVS matches 13 devices and 13 nets uniquely. The same
candidate's extracted transient still fails functional qualification: the full
view produces about -49 mV for both input signs and no 0.9 V logic margin; a
device-only diagnostic preserves polarity but produces only about 0.23 mV.
Therefore analog authorization remains false. The next physical task is to
repair regeneration and pass extracted polarity plus margin, followed by
same-run noise, variation, energy, latency, and area measurements.

The first geometry-strengthening experiment at
`two-single-preamp-parent-wired-20260913T530000Z` widened the child diffusion
window without redesigning the parent route endpoints. Magic remained DRC-clean,
but the flattened devices retained child-local names and failed the strict
parent-binding gate. This experiment is rejected and is not analog evidence.
The 520000 candidate remains the authoritative baseline; the next redesign
must co-design device geometry, contacts, and parent routing, then repeat DRC,
strict binding, LVS, and extracted transient checks.

The subsequent parallel-finger experiments (541000--543000) added a matched
second NFET finger and iteratively removed source/drain shorts. The final
variant is DRC-clean and passes hierarchy-preserving parent-interface checks,
but flat extraction still leaves the new child devices under local port names,
so it does not pass the strict flat binding/LVS gate. These variants are
rejected; they demonstrate that increasing gain requires a physically aligned
cell and parent route, not an isolated geometry edit. The 520000 artifact
remains the accepted baseline for further redesign.

The flat parallel-device candidate at
`two-single-preamp-parent-flat-parallel-20260913T567000Z` is the strongest
redesign so far. After running Magic from the candidate directory, it produces
15 extracted MOS devices, DRC zero, exact parent gate/source/drain binding, and
a unique two-finger Netgen LVS match. At nominal bias it preserves both input
polarities, but its extracted output is only about 33--475 microvolts. Higher
bias reaches the voltage-margin threshold but loses one polarity case. This is
therefore a qualified physical experiment, not analog authorization; the next
task is balanced regeneration/operating-point design followed by the same
extracted transient gate.

The short-channel redesign at
`two-single-preamp-parent-flat-short-channel-20260913T570000Z` also passes
DRC, flat extraction, exact binding, and a unique two-finger LVS match. Its
four preamp devices use extracted `l=0.3` geometry, but the nominal transient
still reaches only about 20--490 microvolts. A three-finger short-channel
variant at `two-single-preamp-parent-flat-triple-short-20260913T581000Z`
passes DRC/LVS as well, yet loses one polarity and remains below 0.6 mV. The
two-finger short-channel design is therefore the best current electrical
candidate, not a qualified converter. Further width scaling alone is not
validated; the next redesign needs balanced latch/preamp regeneration.

An isolated-latch bias sweep confirms that the problem is architectural rather
than simply capacitive loading. With the same extracted latch and a +/-0.153 mV
ideal input, 0.25--8 uA bias produces only microvolts of differential output;
16 uA improves gain but remains below margin, while 20 uA and above drives the
pair into one-sided saturation that loses input polarity. Bias alone cannot
close the gate. The next physical increment is therefore a balanced
regenerative latch operating-point redesign, validated first at schematic
level and then through DRC, extraction, unique LVS, and the integrated
post-layout transient gate.

The real-target two-stage-preamp/latch handoff now runs end to end at
`+/-0.1529705854 mV`. It reaches approximately 1.8 V differential output for
both cases, but both cases choose the same polarity; only one of the two
polarity gates passes. The same-run preamp offset is approximately -0.237 V,
and the reported zero-input trim does not remove the directional imbalance at
the latch input. This is the current authoritative electrical blocker: the
next redesign must provide a genuinely balanced differential preamp/latch
handoff before physical converter authorization is possible.

## 1. Vision

Build a human-supervised engineering system that turns a structured hardware
requirement into a tested RTL implementation, a physically implemented chip
block, and a reviewable signoff package.

The system should shorten the distance between an engineering question and
reliable evidence. An agent may propose a plan, test, assertion, diagnosis,
repair, or physical-design experiment. Deterministic tools must execute and
check the proposal. A human remains responsible for approving intent-changing
repairs and final silicon signoff.

The North Star journey is:

```text
requirement
  -> typed design contract
  -> RTL and verification collateral
  -> simulation, lint, formal, and coverage
  -> failure localization and repair proposal
  -> human approval and identical-scope retest
  -> synthesis, placement, CTS, routing, and extraction
  -> STA, power/IR, DRC, LVS, antenna, and ERC
  -> signed, reproducible release package
```

This is an evidence-grounded automation platform, not a promise of zero bugs
or unattended tapeout.

## 2.1 Coverage of the technical-foundation proposal

The North Star includes the full technical-foundation proposal, but not every
technique is at the same maturity level. The following map prevents research
ideas from being mistaken for implemented project capabilities.

| Foundation proposal | North Star workstream | Current position |
|---|---|---|
| SystemRDL/IP-XACT single source of truth | R1 structured hardware knowledge | Research and adapter target |
| JSON blueprints, protocol flows, Jinja2/DSL collateral | R1 and Phase 4 collateral generation | Partial requirement-ID and typed-IR foundation |
| AST embeddings and graph partitioning | R1/R3 structural RTL analysis | Dependency and RTL inspection foundation; embeddings/GNN not yet proven |
| StateTune-style persistent memory and EHVI | R5 and Phase 3 optimization ledger | Experiment history and bounded optimization target |
| Verilator compiled simulation | R6 and Phase 5 accelerated backends | Icarus/Verilator reference execution exists; benchmark still required |
| C++20 coroutine/UVM execution | R6 | Research target; no claim of dynamic UVM coroutine performance |
| Synthesizable Verification Models and FPGA emulation | R6 and Phase 5 | Future adapter/research target; no FPGA evidence yet |
| Linting and static guardrails | Phase 1 | Open-source lint/compile checks are in the reference path |
| Specification-grounded SVA | R4 and Phase 1/4 | Conservative SVA infrastructure; broader solver qualification remains |
| Solver-in-the-loop formalization | R4 | Yosys/SAT foundation; JasperGold requires an authorized adapter run |
| AST lowering and CIRCT/MLIR LTL preservation | R4 and Phase 4 | Research target; not represented as completed implementation |
| Filtered-DUT signal slicing | R3 and Phase 1 | Dependency-cone and focused triage foundation exists |
| Golden-model comparison and State Frontier | R3 and Phase 6 | Requires a paired executable golden model and cycle-alignment benchmark |
| Causal graph and for/against debugging | R2/R3 | Planned diagnosis discipline; benchmark still required |
| Coverage-driven stimulus closure | R2 and Phase 1 | Coverage-gap proposals exist; convergence must be measured on a held-out set |
| RISC-V RVA23/vector microarchitecture | R7 and Phase 6 | System-context research input, not current AIMC block scope |
| Chiplet economics and disaggregated serving | R7 and Phase 6 | Architecture research context; requires separately sourced quantitative studies |
| Post-CMOS and converter limits | R7 and analog qualification | Physical-boundary research; cannot be inferred from digital RTL evidence |

The named frameworks in the proposal—HAVEN, STG, TVP, LongRTL, StateTune,
ProofLoop, ChatSVA, UVMarvel, VeriPilot, FVDebug, SVM, HMA-Serve, and EARTH—
are treated as literature or design-pattern references. They are not claims
that this repository implements those systems or reproduces their published
numbers. Each quantitative claim must receive a source, workload, baseline,
and reproduction method before entering the project scorecard.

The first real-model execution path is the Colab runner at
`analog-digital-chip-design-eda/colab/run_llm_agent_benchmark_local.sh`. It is
opt-in because it consumes GPU resources. The remote job downloads model
weights only inside the temporary Colab runtime, validates the 11-case
proposal contract, and returns evidence. It must pass grounding,
diagnosis-match, review-required, and adversarial-review checks before any
model result is included in the scorecard.

The runner installs the open-source RTL tools needed by the reference retest
inside the temporary runtime. The default model is
`Qwen/Qwen2.5-0.5B-Instruct`, but the model ID remains configurable so model
comparisons can be run under the same acceptance contract.

The first real-model run completed on a Tesla T4, while the 11-case reference
closure loop passed. The selected model failed the typed proposal contract on
all 11 cases because its outputs were incomplete; this is recorded as a
negative evaluation in
`docs/research/llm-agent-colab-evaluation-2026-09-13.md`. The result validates
the execution and rejection path, not model quality.

## 2. Canonical end-to-end implementation goal

The immediate flagship goal is:

> Take one real RTL block from written requirements through automated
> verification, human-approved repair, RTL-to-GDS implementation, STA,
> physical checks, and one reproducible release package.

The canonical design is the existing AIMC multi-clock control subsystem. It is
large enough to exercise clocks, resets, control state, data movement, timing,
and physical implementation, while remaining runnable in the local open-source
flow.

### Subgoal 1: Freeze the design contract

Document ports, registers or commands, clock domains, reset behavior, expected
latencies, error handling, and assumptions. Give each behavior a stable
requirement ID. Record the RTL, testbench, constraints, and tool versions.

**Exit evidence:** every important behavior has a requirement ID and a frozen
source/constraint hash.

### Subgoal 2: Build requirement-to-RTL traceability

For each requirement, identify the responsible RTL module or signal, test,
assertion, and resulting evidence. The trace must distinguish a requirement
from an implementation detail so buggy RTL cannot redefine intended behavior.

**Exit evidence:** an independent reviewer can follow each requirement through
RTL and checks to a run artifact.

### Subgoal 3: Establish a failing verification baseline

Run the original design through compilation, lint, simulation, waveform
generation, bounded formal checks, and the available coverage/check inventory.
Preserve at least one known failure or seeded fault so the system demonstrates
that it detects and records failure rather than manufacturing a pass.

**Exit evidence:** a baseline manifest contains commands, logs, waveforms,
failure classification, source hashes, and tool results.

### Subgoal 4: Localize the failure

Produce a compact diagnosis containing the failing requirement, first failing
cycle, expected and actual values, relevant signals, dependency cone, likely
source location, and competing explanations. The system proposes a diagnosis;
it does not silently edit RTL.

**Exit evidence:** the diagnosis points to a reviewable bounded slice and is
supported by waveform or checker evidence.

### Subgoal 5: Apply a bounded, approved repair

Represent the proposed repair with its requirement ID, source location,
hypothesis, expected effect, risk, original hash, and repaired hash. Require
human approval, apply the change only to a copy, and preserve the original
source unchanged.

**Exit evidence:** the approved repair is traceable, isolated, and does not
modify the canonical source.

### Subgoal 6: Retest under identical scope

Rerun the repaired design with the same testbench, inputs, assertions, clock
assumptions, formal bounds, and coverage scope. Compare baseline and retest
results and reject scope changes unless they are explicitly recorded and
approved.

**Exit evidence:** the original failure is closed, no regression is introduced,
and a clean checker confirms unchanged scope.

### Subgoal 7: Execute the accepted RTL through RTL-to-GDS

Use the accepted RTL revision—not an unrelated copy—as the physical-design
input. Run synthesis, floorplanning, placement, CTS, routing, extraction, and
layout export. Collect the netlist, DEF, GDS, LEF, LIB, SDC, SDF, and SPEF
views where produced.

**Exit evidence:** the physical run is cryptographically bound to the accepted
RTL and constraints.

### Subgoal 8: Run timing and physical checks

Record setup and hold STA, defined corners and modes, area, cell count,
fanout, DRC, LVS, XOR, antenna, ERC, and modeled IR-drop results. Classify
every warning as closed, accepted with rationale, blocked, or out of scope.

**Exit evidence:** there are no unexplained results. Remaining max-fanout or
other warnings are visible rather than hidden.

### Subgoal 9: Join the evidence

Create one release package containing the requirements, RTL, testbench,
assertions, baseline, diagnosis, approved repair, retest, synthesis and layout
views, timing and physical reports, commands, tool versions, hashes, and final
decision. Separate digital pass status from analog, commercial-tool, and
silicon status.

**Exit evidence:** the package states what passed, what failed, and what is
unsupported in plain language.

### Subgoal 10: Prove replay and mutation resistance

Extract the package into a clean directory and verify it independently. Then
mutate an RTL file, timing report, source hash, required artifact, or retest
scope and confirm that the checker rejects the package.

**Exit evidence:** the original package replays successfully and every tested
mutation is rejected.

### Definition of done for the flagship goal

The goal is complete only when one block starts from a written requirement,
passes through verified and approved RTL, reaches extracted RTL-to-GDS/STA and
physical checks, and produces a clean-checkout-verifiable package. This does
not require physical silicon, but it must clearly mark analog qualification,
commercial EDA signoff, package/board evidence, and silicon validation as
unavailable when they have not been performed.

## 3. What success looks like

An independent reviewer should be able to start from a versioned requirement,
replay the complete run, inspect the exact RTL and tests, see why a failure was
classified, approve or reject a bounded repair, verify that the retest scope
did not change, inspect the physical and timing reports, and reproduce the
final hashes.

The first success criterion is not an impressive demo. It is preservation of
meaning across representation changes:

```text
requirement -> RTL -> netlist -> layout -> extracted timing/physical evidence
```

At every boundary the system must answer:

- What was intended?
- What artifact was produced?
- Which tool checked it?
- What assumptions and limitations apply?
- What remains unproven?

## 4. Research program

### R1. Structured hardware knowledge

Research whether machine-readable requirements and syntax-aware RTL
representations reduce width, reset, address, protocol, and clocking errors
compared with text-only retrieval.

Concrete experiments:

- Compare Markdown-only, requirement-ID, SystemRDL, and IP-XACT inputs.
- Parse RTL into module, port, state, expression, clock, reset, and dependency
  records.
- Measure generated collateral compile rate, semantic error rate, and review
  effort.
- Require every generated item to point back to a source requirement and source
  span.

Research deliverable: a public corpus of small designs with typed contracts,
known bugs, expected collateral, and reproducible scoring.

### R2. Evidence-grounded agent behavior

Research whether an agent can improve verification and diagnosis when all
actions are constrained by typed schemas, tool execution, artifact hashes, and
human approval gates.

Concrete experiments:

- Give the agent seeded failures in FIFO, arbiter, register, handshake, and
  width-conversion designs.
- Compare free-form suggestions with evidence-bound proposals.
- Measure correct diagnosis, repair success, regression rate, unsupported-claim
  rate, and human review time.
- Include adversarial cases: stale artifacts, changed test scope, missing logs,
  false passes, and unsupported tools.

Research deliverable: a benchmark report showing where agents help and where
deterministic checks must reject them.

### R3. Logic-aware failure localization

Research whether dependency-cone slicing, waveform summarization, and
golden-model comparison identify the earliest meaningful divergence more
reliably than sending complete waveforms to a language model.

Concrete experiments:

- Build compact signal slices from failing assertions and observed mismatches.
- Record the first divergent cycle, state, signal, and requirement.
- Compare full-waveform, signal-slice, and state-frontier prompts.
- Score localization precision, repair quality, and token/runtime cost.

Research deliverable: a cycle-level debugging dataset and a validated triage
protocol.

### R4. Solver-in-the-loop formalization

Research how to generate conservative assertions from specifications without
allowing buggy RTL to redefine the specification.

Concrete experiments:

- Generate assertions only from typed requirements and explicit assumptions.
- Run syntax, elaboration, bounded SAT, and available formal proofs.
- Check vacuity, unreachable antecedents, ignored binds, and unconstrained
  inputs.
- Maintain separate statuses for proven, falsified, vacuous, inconclusive, and
  unsupported.

Research deliverable: an assertion-quality and contamination-resistance
benchmark. Commercial JasperGold claims must remain adapter-based until real
authorized runs exist.

### R5. Closed-loop physical design optimization

Research whether a stateful experiment ledger can choose useful RTL,
constraint, and physical-design experiments better than independent script
rewrites.

Concrete experiments:

- Store constraints, tool versions, floorplan settings, timing, area, routing,
  fanout, IR, and physical-check outcomes.
- Preserve rejected experiments and their failure reasons.
- Compare random search, rule-based search, and stateful Pareto-guided search.
- Require identical-scope reruns and hash-bound comparison.

Research deliverable: an open-source optimization corpus and a measured
improvement in time-to-acceptable design, without claiming universal speedups.

### R6. High-throughput execution and emulation

Research where compiled simulation, coroutine scheduling, and FPGA-assisted
verification provide real value for the target workloads.

Concrete experiments:

- Establish a baseline using Icarus, Verilator, and existing testbenches.
- Measure compile time, simulation time, memory, determinism, and debug
  visibility.
- Add a small C++/Verilator execution adapter before attempting dynamic UVM.
- Define an FPGA SVM only after the software protocol and reference model are
  stable.

Research deliverable: workload-specific measurements. Do not publish a broad
10x–720x claim until the comparison, workload, hardware, and methodology are
recorded.

### R7. Analog and system qualification boundaries

Research how digital control, analog converter behavior, model error, runtime
fallback, and physical evidence should be joined without promoting simulated
or synthetic values to measured hardware claims.

Concrete experiments:

- Keep digital, SPICE, extracted-layout, board, and silicon evidence in
  separate schemas.
- Propagate error budgets and operating ranges through the model/compiler path.
- Require physical profile measurements before authorizing analog execution.
- Record blocked gates as first-class results.

Research deliverable: one AIMC case study with an explicit evidence graph and
no ambiguous claim promotion.

## 5. Engineering roadmap

### Phase 0: Baseline and contract freeze

Goal: make the current work easy to reproduce.

Actions:

1. Freeze the multi-design verification pilot and the AIMC multi-clock RTL2GDS
   design as canonical fixtures.
2. Define common schemas for requirements, RTL sources, tool runs, failures,
   repairs, timing, physical checks, and release decisions.
3. Make every run record source hashes, tool versions, commands, scope IDs, and
   artifact hashes.
4. Publish one plain-language capability matrix.

Exit criteria: clean-checkout replay passes and every unsupported capability is
explicitly marked unsupported.

### Phase 1: Unified digital verification loop

Goal: connect requirements, tests, simulation, diagnosis, repair, and retest.

Actions:

1. Extend the existing requirement-ID ingestion into a typed contract.
2. Generate conservative tests and assertions with source traceability.
3. Run lint, simulation, waveform triage, and bounded formal checks.
4. Produce a repair proposal without modifying the original source.
5. Require human approval, apply the repair to a copy, and rerun identical
   scope.
6. Report coverage gaps and propose the next bounded test.

Exit criteria: the six-design pilot closes seeded failures with passing retests,
unchanged originals, valid evidence hashes, and adversarial mutation rejection.

### Phase 2: Connect verification to RTL2GDS

Goal: take a verified RTL revision into physical implementation automatically.

Actions:

1. Add a physical-flow adapter for Yosys/OpenLane/OpenROAD.
2. Bind the verified RTL revision and constraints to the physical run.
3. Collect synthesis, placement, CTS, routing, extraction, STA, DRC, LVS,
   antenna, XOR, ERC, and modeled IR results.
4. Detect whether a repair changes functional scope, clock assumptions, or
   physical inputs.
5. Produce one joined verification-to-layout release package.

Exit criteria: the canonical AIMC block can be replayed from the verified RTL
revision through extracted STA and physical checks, with all failures visible.

### Phase 3: Stateful timing and physical optimization

Goal: make physical experiments cumulative and decision-oriented.

Actions:

1. Add an experiment ledger and Pareto frontier for timing, area, power/IR,
   congestion, fanout, and physical violations.
2. Start with deterministic rule-based experiment selection.
3. Add model-assisted ranking only after the ledger is reliable.
4. Require every proposed ECO to have a hypothesis, bounded change, expected
   metric, rollback path, and identical-scope retest.
5. Close the remaining canonical max-fanout warning where it improves the
   design without reopening timing or physical failures.

Exit criteria: the system can explain why each experiment was selected,
accepted, or rejected, and can reproduce the selected result.

### Phase 4: Structured collateral and formal expansion

Goal: replace small custom contracts with standards-based collateral where it
adds measurable value.

Actions:

1. Add SystemRDL for a register-block benchmark.
2. Add IP-XACT only for interfaces that need component, bus, or memory-map
   interchange.
3. Generate RTL register logic, C headers, and UVM-style register collateral.
4. Add AST-backed structural queries and requirement-to-RTL trace links.
5. Expand formal adapters while preserving explicit proof-status categories.

Exit criteria: standards-based collateral reduces measurable errors or review
effort on the benchmark; otherwise it remains an optional adapter.

### Phase 5: Commercial and accelerated backends

Goal: validate portability beyond the open-source reference backend.

Actions:

1. Define adapter contracts for commercial simulation, formal, synthesis,
   place-and-route, STA, and EM/IR tools.
2. Reproduce the same block under an authorized project PDK and tool flow.
3. Add Verilator C++ execution measurements for selected workloads.
4. Prototype FPGA-assisted verification only for a stable reference model and
   protocol.
5. Preserve the same evidence and approval policies across all adapters.

Exit criteria: at least one authorized external flow produces independently
reviewed evidence. Tool familiarity must be claimed only for tools actually
used.

### Phase 6: AIMC and system-level qualification

Goal: join model, compiler, digital control, analog behavior, and physical
qualification without collapsing their evidence boundaries.

Actions:

1. Freeze one workload and one supported operating contract.
2. Connect compiler/runtime traces to the verified digital control path.
3. Connect qualified SPICE and extracted analog measurements to the error
   budget.
4. Add calibration, mismatch, PVT, thermal, package, board, and energy gates
   as evidence becomes available.
5. Keep CUDA, board, silicon, and energy claims blocked until their required
   measurements exist.

Exit criteria: a human reviewer can make a bounded model-to-chip decision and
see exactly which gates are digital, simulated, physical, measured, or blocked.

The accepted real-model diagnosis milestone is implemented through the Colab
runner and the one-design bridge
`analog-digital-chip-design-eda/scripts/run_llm_approved_counter_repair.py`.
The bridge remains review-gated and never edits canonical RTL without explicit
approval.
The current evidence-level join to the AIMC physical package is recorded in
`analog-digital-chip-design-eda/evidence/aimc-hardware-lab/llm-rtl2gds-handoff-latest.json`.
It deliberately records `same_design_run: false`; the next gate is a
model-generated repair proposal for the AIMC controller itself.

That mutation diagnosis and copy-only repair/retest are now implemented. The
mechanical evidence is under
`analog-digital-chip-design-eda/.artifacts/aimc-mutation-repair-retest/` and
proves the repaired copy passes the AIMC testbench while all seven RTL inputs
remain aligned with the physical-flow package. This is still not a
model-generated repair or signoff claim. The latest Colab attempt correctly
blocked because the model did not emit exact structured `before`/`after` RTL
text; the review-gated retest harness now rejects that case safely.

## 6. Measurable North Star metrics

Use baseline-relative measurements rather than unsupported universal targets.

| Area | Initial measure | Mature target |
|---|---|---|
| Reproducibility | Clean replay and hash verification | 100% canonical replay success |
| Verification | Correct seeded-failure classification | At least 95% on a held-out benchmark |
| Repair safety | Original source preserved; scope unchanged | 0 unauthorized source mutations |
| Debugging | First-divergence localization | Measurable improvement over full-waveform triage |
| Formal integrity | Assertion status and vacuity reporting | 0 silently accepted unsupported proofs |
| RTL2GDS | Stages and artifacts captured | Complete replay from RTL to extracted layout |
| Physical closure | Timing and physical checks reported | No unexplained signoff failures |
| Optimization | Experiment acceptance/rejection traceability | Better time-to-target than the fixed baseline |
| Runtime | Per-workload compile/simulation baseline | Measured improvement on selected workloads |
| Human effort | Review time per failure and release | Reduction demonstrated on a fixed benchmark |

Metrics such as “zero bugs,” “zero contamination,” or “720x faster” are not
default acceptance criteria. They require a defined population, baseline,
measurement procedure, and independent review.

## 7. Claim boundary

The project may currently claim:

- open-source RTL verification automation;
- evidence-bound diagnosis and human-approved repair/retest;
- local Yosys/OpenLane RTL-to-GDS and extracted STA experience;
- generated layout and physical-check artifacts;
- reproducible, hash-bound release packaging;
- a credible foundation for future agentic EDA research.

The project may not currently claim:

- Innovus, ICC2, or PrimeTime experience;
- commercial PDK or foundry tapeout signoff;
- dynamic UVM coroutine performance results;
- FPGA SVM or emulation results;
- JasperGold results without an authorized run;
- manufactured-silicon, board, package, measured-energy, or measured-analog
  qualification;
- fully autonomous or zero-bug operation.

## 8. Immediate next goal

The next meaty end-to-end increment is:

> Run one requirement-driven digital design through ingestion, test and
> assertion generation, simulation/formal checking, evidence-bound diagnosis,
> human-approved repair and retest, then send the accepted RTL revision through
> the existing OpenLane RTL2GDS/STA flow and emit one joined release package.

This goal is large enough to demonstrate the product thesis, small enough to
complete locally, and directly connected to the physical-design work already
done.

Acceptance gates:

1. The model emits an executable, schema-valid patch that exactly matches the
   diagnosed RTL failure, or the system rejects it.
2. A disposable copy compiles, simulates, and passes the same formal and
   regression scope after the patch.
3. The accepted RTL revision is hash-linked to the physical run; no
   same-design claim is made across unrelated artifacts.
4. OpenLane completes through extracted timing and physical checks with a
   reproducible, complete PDK. If the PDK cannot be repaired, that is recorded
   as environment evidence rather than silently treated as signoff.
5. A human approval record and manifest join the diagnosis, patch, retest, RTL,
   netlist, layout, timing, and physical-check artifacts.

Only after these gates pass should the project advance from a research
prototype to a stronger end-to-end demonstration. Innovus, ICC2, PrimeTime,
foundry signoff, FPGA emulation, and manufactured silicon remain separate
future evidence requirements.

The first generalization is now independently recorded in
`docs/research/multi-design-llm-repair-evaluation-2026-09-13.md`: a real Colab
model selected and passed an exact bounded repair for `seeded_counter`, in
addition to the AIMC repair. The next concrete gate is to package that second
design through formal checks and a physical-flow adapter, then produce a
second joined RTL2GDS handoff. This tests whether the architecture scales
beyond one controller and one mutation family.

That second-design gate is now complete. `seeded_counter` has a passing
model-generated repair, copy-only simulation retest, six-cycle specification
model proof, and an independent local RTL2GDS/STA/DRC/LVS handoff. The evidence
is recorded in
`docs/research/multi-design-llm-repair-evaluation-2026-09-13.md` and
`analog-digital-chip-design-eda/evidence/seeded-counter/model-repair-rtl2gds-handoff-20260913.json`.
The next scaling target is a third design with a temporal or interface failure,
multiple formal properties, and the same physical evidence contract.

Current checkpoint: the model/repair portions of gates 1, 2, 3, and 5 now pass
on the AIMC mutation. The final Colab artifact is under
`analog-digital-chip-design-eda/.artifacts/llm-agent-colab/aimc-llm-agent-bounded-repair-fixed-20260913/`.
The same repaired source was staged into OpenLane and is hash-linked in
`analog-digital-chip-design-eda/evidence/aimc-hardware-lab/model-generated-aimc-rtl2gds-handoff-20260913.json`.
That run passed routing, extracted three-corner STA, GDS generation, and
Magic/KLayout XOR, but failed LVS with 298 errors. Therefore the end-to-end
goal is not complete: the remaining technical task is to repair or replace the
PDK/library extraction setup and repeat the same-design run through clean LVS.

That checkpoint has now been completed locally. Using the preserved complete
Sky130 PDK, the exact model-generated repaired RTL completed OpenLane through
LVS. The final handoff is
`analog-digital-chip-design-eda/evidence/aimc-hardware-lab/model-generated-aimc-rtl2gds-handoff-final-20260913.json`,
and `scripts/check_model_generated_aimc_handoff.py` independently passes. The
evidence records byte-identical source staging, zero LVS errors, zero detailed
route DRC violations, extracted STA, GDS, and zero Magic/KLayout XOR.

This means the immediate local meaty goal is achieved. The next North Star
increment is broader generalization: repeat the same closed loop across a
held-out design family, use richer requirement/specification inputs, add
formal-property evidence, and demonstrate stateful timing/physical optimization
with explicit human review. Commercial Innovus/ICC2/PrimeTime, FPGA/emulation,
analog measurement, and manufactured silicon remain later evidence tiers.

The four-design aggregate is now captured by
`analog-digital-chip-design-eda/evidence/four-design-closed-loop-release-20260913.json`
and independently checked by
`analog-digital-chip-design-eda/scripts/check_three_design_release_manifest.py`.
The counter and timeout designs also have separately executed formal property
suites. The aggregate now includes a fourth, protocol-focused
`register_peripheral` design with model-selected address decoding, simulation,
formal, and physical evidence. AIMC’s scheduler/governor suite has also
passed, with scope explicitly limited to the combinational policy boundary,
not full multi-clock controller closure. The simulation-backed AIMC sequential
campaign now passes fourteen checks, covering reset and recovery, both
directions of two-stage CDC latency, repeated acceptance/fallback accounting,
and the accounting partition invariant; it is included in the aggregate as
temporal evidence, not exhaustive formal CDC proof. The next concrete
implementation step is measuring closed-loop latency and optimization-history
behavior.

The AIMC release now carries a distinct stateful formal suite as well:
Yosys SAT proves 20 single-clock micro-tile-controller assertions through
bounded depth 32. The proof covers reset state, monotonic saturated counters,
one-event counter increments, saturation behavior, and execution/reason
consistency. This is a
stronger assurance tier than simulation alone, while the multi-clock CDC
boundary remains explicitly simulation-backed.

The next generalization gate is also complete across four small digital
designs. In addition to AIMC and `seeded_counter`, `seeded_timeout` now has a
real Colab model-selected temporal repair, copy-only simulation retest,
specification-model formal proof, and independently checked OpenLane
RTL2GDS/extracted-STA handoff. Its evidence is recorded in
`analog-digital-chip-design-eda/evidence/seeded-timeout/model-repair-rtl2gds-handoff-20260913.json`.
The four-design result demonstrates that the loop is not tied to one Boolean
controller mutation, but it is still a bounded research prototype rather than
an autonomous production silicon engine.

The next concrete work is to strengthen assurance and optimization: add
exhaustive sequential CDC properties, measure repair/retest/review latency,
and implement persistent run-history feedback for timing/physical experiments.
The measurement layer now exists: the baseline package is
`analog-digital-chip-design-eda/evidence/closed-loop-measurement-20260913.json`
with append-only, hash-chained history at
`analog-digital-chip-design-eda/evidence/closed-loop-measurement-history.jsonl`.
It records model latency, per-design OpenLane runtime, warning counts, and
timed verification checks. The next optimization experiment is to run at least
two controlled physical-flow configurations, compare timing, area, and
warnings, and append both outcomes to the same history so the Pareto choice is
evidence-based.

The first controlled sweep is complete for the register peripheral. The
high-density configuration reduced die area from 0.0043055 mm² to 0.0021498
mm², while the low-density configuration completed faster (292.3 s versus
306.5 s); both passed local physical checks with zero SPEF timing violations.
The comparison is recorded at
`analog-digital-chip-design-eda/evidence/register-peripheral-density-optimization-20260913.json`
and appended to the history. It is a two-point Pareto result, not a universal
PPA conclusion. The next optimization step is to repeat the sweep on a larger
controller design and add explicit area/timing objective weights.
Commercial EDA tool
integration, FPGA/emulation, analog measurement, foundry signoff, and silicon
remain separate later evidence tiers.

The larger-controller optimization sweep is now complete as well. The same
model-generated repaired AIMC source was evaluated at low and high placement
density and passed the same local physical checks at both points. High density
reduced die area from 0.107877 mm² to 0.050354 mm², while low density reduced
flow runtime from 1,438.8 s to 989.9 s. Neither dominates the other, so both
are retained as Pareto candidates in
`analog-digital-chip-design-eda/evidence/aimc-density-optimization-20260913.json`.
The next local increment is not another arbitrary sweep: it is to add explicit
objective weights and a stateful recommendation step that chooses the next
configuration from the append-only history, while keeping human approval and
the existing fail-closed evidence gates.

That recommendation step is now implemented by
`analog-digital-chip-design-eda/scripts/recommend_next_physical_configuration.py`.
Its first output is
`analog-digital-chip-design-eda/evidence/next-physical-configuration-recommendation-20260913.json`;
with the default 50/30/20 area/runtime/timing weighting it recommends the
high-density AIMC candidate for human review. This closes the current local
optimization increment, but the North Star still requires broader design
families, stronger sequential/formal coverage, real tool integrations, and
hardware-backed evidence.

## 9. Current end-to-end checkpoint

The authenticated model-execution gate is now closed for this snapshot. Four
GPU-backed Colab artifacts were regenerated on a Tesla T4, restored locally,
hash-checked, and accepted by the bridge validators: KV-cache behavior, GPU
operator behavior, MTP precision behavior, and MiniDeepSeek parity. The
precision artifact correctly labels native FP8 as unavailable in that runtime;
emulated INT8/FP8 results are not presented as native hardware capability.

The digital silicon-design loop is also closed at its local research boundary:
four model-generated repairs passed simulation/formal checks and independent
OpenLane RTL2GDS, extracted STA, DRC/LVS, GDS, and XOR handoff checks. The
remaining open gate is analog converter qualification. The named candidate is
now a real, inspectable assembled extracted-RC object and passes a same-candidate
ngspice drive/settling test, but it is not yet a transistor-level converter.
Strict analog acceptance still requires, from that same physical candidate:

1. transistor-level row DAC, sample path, reference, mux, comparator, and SAR
   behavior;
2. integrated supply-energy and conversion-latency measurements;
3. noise, offset, mismatch, and PVT evidence;
4. extracted area plus DRC/LVS evidence; and
5. a break-even rerun using those measured values.

Therefore the accurate status is `gpu_ready=true`,
`analog_authorized=false`. The next meaty goal is to build and qualify that
single transistor-level converter candidate through the same evidence-bound
loop, while retaining the digital fallback until every analog gate passes.

The first extracted active-macro transient diagnostic has now been run on the
existing Sky130 hierarchical candidate. Both input cases converged, but the
decision differential was only about 2.33--2.45 mV and neither case reached the
0.9 V logic-margin criterion; only one polarity check passed. The boundary
audit also found no verified input-to-latch branch in the exact flat netlist.
This is valuable failure evidence, not converter qualification: the next
analog implementation task is to repair the physical signal path and expose a
verified transistor-level DAC/sample/comparator/SAR connection before taking
energy or break-even measurements.

A first routing-repair candidate was generated without overwriting the prior
layout and passed Magic DRC with zero reported errors. Extraction exposed an
electrical-short failure, however: the proposed metal-stack bridge collapsed
the analog input boundary and the independent boundary audit still found no
verified input-to-latch branches. The candidate is retained as a failed
routing experiment; it is not promoted or used for qualification. The next
repair must use a connectivity-aware route/LVS loop, not only geometric DRC.

The next isolated routing revision improved the result: Magic DRC remained at
zero, the extracted net no longer shorted `row_drive` to
`sar_comparator_input`, and the boundary auditor now recognizes both required
branches. The candidate still fails the next gate: extracted transient output
is only about 6.6 mV differential, with no 0.9 V logic margin, and Netgen LVS
reports a 12-versus-13-device mismatch plus pin/net mismatches against the
intended latch schematic. This advances the diagnosis from “missing input
connection” to “connected but electrically undersized/mismatched active path.”
It remains unqualified.

The timing/bias finding is now reproducible in
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/active-macro-timing-bias-campaign-20260913.json`.
At 20 microamperes tail bias, evaluation at 12 ns and 14 ns passed both
polarity cases and both logic-margin checks for the bounded ±50 mV nominal
test; evaluation at 8.2 ns and 10 ns passed the margin but only one polarity.
This establishes a candidate operating window for further design work, not
qualification: the full converter still lacks complete SAR/DAC functionality,
clean LVS, and variation/noise evidence.

A controlled bias sweep on the corrected extracted candidate separated the
electrical limits further. At the default 4 microampere tail bias, a 50 mV
differential produced only 13--27 mV output differential. At 20 microamperes,
the outputs reached logic-level magnitude (about 1.46--1.80 V), but the
negative input polarity still failed and the full extracted candidate remains
an LVS mismatch. Higher bias saturated both cases at the rail. The next
analog task is therefore to correct comparator regeneration/polarity and match
the extracted layout to its intended schematic; simply increasing bias is not
an acceptable fix.

The subsequent topology-isolation experiments are retained under
`evidence/aimc-simulator-adapters/active-converter-macro-candidate/`. The
cleanest revision remains Magic-DRC-clean, but Netgen still reports a
12-versus-13-device mismatch: the auxiliary two-transistor cell's extracted
source/drain ports do not bind to the intended `preamp_iso_tail_ext`,
`latch_sense_p_ext`, and `latch_sense_n_ext` nets. This is now a concrete
topology-integration defect, not an unresolved generic routing concern. The
next implementation must reconcile that cell's physical port geometry and
hierarchical extraction with the independent schematic before any analog
result is promoted.

The explicit-body preamp cell was subsequently made extraction-clean: its
ports now reach the gate contacts, Magic still reports zero DRC errors, and
Netgen reports `Circuits match uniquely` for the two-device cell. Integrating
that cell into the parent brings the extracted device count to the expected
13, but parent LVS still reports separate hierarchical child nets for the two
gate ports and fails top-level pin matching. The next repair is therefore a
parent routing/port-binding correction, with the cell itself retained as a
verified building block.

The preamp was then isolated as its own extracted-cell experiment in
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/active-converter-macro-candidate/preamp-port-candidate-20260913T220000Z`.
It has two extracted NFETs, five expected signal ports, and zero Magic DRC
errors. Netgen matches the two-device topology but reports a standalone
substrate-port mismatch; the next integration step is to expose an explicit
`vss_escape` body port in that cell and then reconnect the verified cell in the
parent macro. This is evidence of narrowed progress, not analog acceptance.

That cell-level repair is now complete in the independently extracted
`preamp-port-candidate-20260913T250000Z` artifact: Magic reports zero DRC
errors, the extracted cell exposes all six intended ports including
`vss_escape`, and Netgen reports two devices with a unique circuit match. The
remaining failure is specifically at parent integration: the wrapper does not
yet bind the child gate escapes to the parent `row_drive` and
`sar_comparator_input` routes. Parent-level LVS and analog qualification
therefore remain open.

The follow-up parent experiments confirm the boundary quantitatively: the
clean candidate extracts 13 devices and zero Magic DRC errors, while Netgen
still finds two namespaced child nets (`latch_sense_p_ext_uq0` and
`latch_sense_n_ext_uq0`) instead of binding those devices to the parent latch
nets. A label-only binding attempt did not establish physical connectivity,
and a long bridge attempt created a supply short. The next repair must use an
isolated parent routing channel with explicit contacts and prove the flattened
netlist, rather than relying on coincident labels.

The boundary auditor is now strict about this condition: it separately reports
`strict_parent_binding_passed`, requiring each extracted preamp device to use
the exact parent output, input, shared preamp tail, and body nets. The verified
standalone preamp passes that check; the integrated parent candidate fails it
because both child output nets still carry `_uq0` aliases. This turns the
hierarchical binding defect into an executable fail-closed gate for future
agent-generated layout candidates.

The extraction-aware routing experiment confirmed that nominal label rectangles
are insufficient for parent integration. The latest candidate remains DRC-clean
with 13 devices, but its extracted child diffusion terminals land on different
electrical nodes than the parent-side nominal rectangles; the attempted bridge
therefore binds a preamp terminal to `vdd_ext`. This candidate is rejected. The
next parent-layout generator must derive route endpoints from the flattened
extraction (and verify each endpoint's net) before emitting any bridge.

The latest parent-bound-cell experiment closes the hierarchical half of that
repair. The generated macro at
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/active-converter-macro-candidate/two-single-preamp-parent-wired-20260913T480000Z`
passes Magic DRC and hierarchy-preserving extraction. The independent checker
`scripts/check_hierarchical_preamp_binding.py` validates both exact child
contracts: P uses `preamp_iso_tail_ext`, `latch_sense_p_ext`, and `row_drive`;
N uses `preamp_iso_tail_ext`, `latch_sense_n_ext`, and
`sar_comparator_input`; both expose the explicit body escape. This is a
completed physical-interface milestone, not converter qualification.

The flat gate remains intentionally open. Flattened extraction still emits
the preamp devices with `iso_tail_ext` and the parent LVS comparison fails,
so the next implementation task is to make physical flattening preserve the
same net contract and then rerun full LVS and extracted transient tests.
Only after that may the project collect one same-run energy, latency, noise,
area, and break-even packet. Until then `analog_authorized` remains false.

The route revision at
`two-single-preamp-parent-wired-20260913T501000Z` removed the shared P/N
output rail and corrected the N-side route direction. A fresh Magic run still
reports zero DRC errors, both input-to-latch branches are visible, and the
output short is gone. The extracted transistor terminals nevertheless show
an incorrect source/drain-to-parent assignment, so strict binding and Netgen
parent LVS remain failed. This is the current physical endpoint for the next
repair; the candidate is not analog evidence.

The 513000 route revision is the strongest flat result so far. Fresh
extraction reports zero DRC errors; the P preamp is strictly bound to
`latch_sense_p_ext`, both latch branches are present, and Magic's equivalence
records show the N drain reaching `latch_sense_n_ext`. The N shared-tail port
still remains a child-local alias in the flattened device line, so strict
binding and parent LVS remain failed. This is a narrowed physical-interface
failure, not analog qualification.

The attempted clean-parent reconstruction at
`clean-parent-route-20260913T511000Z` was also rejected. Although Magic
reported zero DRC errors, extraction collapsed required signals onto the
`row_drive` net because removing all inherited parent geometry also removed
necessary layer-transition structure. The next repair must retain verified
latch access structures and remove only identified conflicting trunks; a
blanket scaffold strip is not a valid physical design method.

The next revision at
`two-single-preamp-parent-wired-20260913T503000Z` removed the inherited N
output escape that was reconnecting the N output to the shared tail. Fresh
extraction now shows no P/N output short, both input-to-latch branches are
present, and the hierarchical parent-interface gate still passes with DRC
zero. The remaining flat failure is the unresolved N-side terminal alias
(`latch_sense_n_ext_uq1`) and the associated source/drain mapping; parent LVS
and analog authorization remain closed.

## 10. Next meaty goal to pursue

The current implementation target is the agentic hardware failure-to-closure
loop defined in
`docs/roadmaps/next-meaty-goal-agentic-hardware-closure.md`. It is the next
end-to-end product slice: evidence-grounded LLM diagnosis, bounded repair,
human approval, copy-only identical-scope retest, local RTL-to-GDS checks, and
held-out-design generalization in one replayable release package.

The agent remains a proposing layer. Deterministic tools execute and validate
its work; human approval controls source-changing repairs; and analog,
measured-hardware, and production claims remain blocked until their own gates
pass.
