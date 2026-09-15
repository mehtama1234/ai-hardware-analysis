# LLM-Assisted Auto-Formalization Extension Plan

## Purpose

This document defines the next technical program for extending the existing
agentic hardware-closure system into a specification-grounded,
solver-validated SystemVerilog Assertion (SVA) auto-formalization pipeline.

The current system already provides a trustworthy outer control plane:

```text
LLM diagnosis -> bounded RTL repair -> simulation/formal verification
               -> RTL-to-GDS evidence -> hash-bound release manifest
```

The extension adds the missing formalization plane:

```text
natural-language requirement
        -> verification intermediate representation
        -> candidate SVA
        -> compiler/lowering checks
        -> formal proof and vacuity analysis
        -> bounded property repair
        -> evidence consumed by the existing closure system
```

The objective is not autonomous tapeout. The objective is to reduce the
engineering effort required to produce useful, reviewable formal properties
while preserving specification integrity, deterministic tool evidence, and a
human-controlled release boundary.

The verified implementation stages can be promoted to a release manifest only
through `scripts/release_four_workstream_pipeline.py`, which verifies all
checkpointed artifact hashes and requires explicit reviewer approval.

The conservative planner grammar now includes identifier-preserving same-cycle
and next-cycle Boolean implications; unsupported temporal wording remains
explicitly queued for review rather than guessed.

It also recognizes one explicit compound Boolean antecedent, such as “valid
and ready implies accepted” or “valid or ready requires accepted,” and maps it
to the corresponding `&&` or `||` SVA expression. Nested or ambiguous Boolean
language remains queued for review.

It also supports bounded fixed-cycle responses up to 64 cycles, bounded response
windows up to 16 cycles, and lowers them to explicit history-register checks;
richer temporal expressions remain open.

Assertion-agent admission rejects functional RTL, implementation-context, and
waveform fields in model responses. Structural signal names may be supplied for
name resolution, but assertion logic must remain specification-grounded.

Bounded hold-until responses are also supported for wording such as “request
remains high until acknowledge is high within 3 cycles.” They are lowered to a
pending-state register and deadline counter; the bound is limited to 16 cycles.

The planner can additionally derive bounded fixed consecutive repetition from
explicit wording and route it through the existing counter-based lowering.

Measured protocol coverage rankings are also supplied to assertion-agent
requests as review context; they guide the next proposal but are not treated
as coverage proof. Repeated reports can now be supplied in measurement order;
the pipeline records a monotonic, hash-bound coverage-convergence trajectory
and marks it converged only when the declared total is reached.

The provider-free Colab demonstration now exercises this combined path with a
seeded coverage report, one validated agent-team handoff, and downstream
assertion-agent provenance.

When the bounded team is enabled, downstream diagnosis, repair, and assertion
requests now carry the validated team artifact and record its digest, making
the role handoff traceable through the later workstream outputs. The bounded
handoff conclusions are also supplied as structured request context, with
handoff counts recorded in downstream results.

Debug-package construction also independently validates causal-graph integrity
before diagnosis, including referenced nodes, temporal ordering, acyclicity,
and self-digest correctness.

## Current implementation status

The repository already contains a partial reference implementation of all four
workstreams. The following status is the authoritative boundary for this
roadmap:

| Workstream | Implemented now | Still open |
|---|---|---|
| Auto-formalization | Typed verification IR, deterministic requirement planning with generic signal/control identifier extraction for reset/hold/increment forms, specification-digest-bound assertion proposals, an LLM-payload-to-SVA adapter with revision and structural-signal scope gates, direct local/OpenAI-compatible `generate_assertion` backend invocation, bounded multi-agent role handoffs with shared evidence and validated proposal chaining, top-level four-workstream CLI integration for assertion-agent execution, a Qwen JSONL worker contract for assertion generation, same-run Verilator frontend validation and explicit lowering feedback for admitted assertions, explicit trace-vacuity feedback and digest-bound replacement refinement in the top-level workflow, proposal-level bounded solver vacuity evidence over validated scalar Boolean branches, bounded Yosys signal and conjunction/disjunction branch antecedent reachability evidence, multi-file RTL-bundle solver-vacuity execution wired into the four-workstream CLI/checkpoint, a reusable hash-bound Yosys `-prove-asserts` result classifier, port-validated DUT/assertion wrapper generation with compile evidence, explicit opt-in hierarchical observation of declared internal DUT signals with compile evidence, SVA generation, real Qwen provenance, formal/simulation evidence, explicit clock/reset/one-cycle lowering for seeded properties, simple and scalar compound Boolean implications with overlapped/one-cycle-delayed lowering, bounded `a ##N b |-> c` shift-register lowering, fixed and bounded consecutive `a[*N:M] |-> b` counter lowering, fixed-count and ranged non-consecutive `a[=N:M]`/`a[->N:M]` counter lowering, digest-bound solver-feedback refinement with signal-scope limits, trace-based antecedent vacuity gating, and review-only scalar candidates from counterexamples | General natural-language-to-SVA generation, other temporal operators, nested or richer compound temporal expressions, context-rich counterexample synthesis, solver-complete vacuity proof, and automatic binding of assertions to arbitrary unvalidated internal DUT interfaces |
| Execution acceleration | Icarus execution, Verilator lint capability reporting and orchestrated lint, optional Verilator flag capability probing, a real-RTL Verilator capability matrix with fail-closed unsupported-option evidence, bounded tool runners, waveform artifacts, measured OpenLane runs, time-zero lint guardrails, a lint-before-compiler scheduling gate, an executable Icarus time-zero regression fixture, a checked-in five-case time-zero matrix with classified runtime outcomes for normal/failure/timeout/premature/missing-stimulus scheduling cases, a four-workstream CLI/status orchestrator with hash-verified checkpoints and generated-sequence compilation, a runnable provider-free Colab entry point, a provider-free CI reference job that runs the six-stage demo and checkpoint audit, an opt-in Verilator C++ compile-and-run smoke stage with pass-marker evidence, an optional synthesizable-checker compile/run stage with cycle/actual/expected mismatch records, mismatch detection, host-observed SVM cycle throughput markers, and checkpoint evidence, a deterministic cooperative scheduler model with time-zero/event/deadlock evidence, a real C++20 coroutine compile/run probe with required time-zero/event-progress markers, and an explicit self-digested UVM package/simulator capability probe | Verilator coroutine/UVM execution, broader version-specific time-zero runtime corpus, FPGA deployment/SVM timing and utilization evidence, and production-grade tiered CI |
| Logic-aware debugging | Failure parsing, VCD extraction, dependency graphs and deterministic backtrace paths, bounded expression-level dependency CDFG with source locations, parser-backed Yosys signal/cell CDFG extraction, conservative single-module dependency-cone reconstruction into filtered DUTs with explicit hierarchy/unsupported-construct blocking, hierarchy-preserving static-instance filtered DUT reconstruction that drops unrelated modules, opt-in conservative leaf-module dependency-cone slicing inside retained hierarchies with unsupported-construct blocking, Yosys functional-equivalence gating for reduced single-module DUTs and namespaced hierarchical slices, first-divergence records, a self-digested causal event graph, source-location and RTL-digest-bound causal edges, balanced `FOR`/`AGAINST` diagnosis, a composed hash-bound debug package, first multi-signal aligned state-frontier records, a bounded RTL-digest-bound replay-slice manifest, deterministic global one-to-one cross-language signal matching with disclosed ambiguity, optional structural-neighbor similarity, persisted score components, and CDFG-derived cross-language alignment with graph digests, adjacency provenance, and explicit non-equivalence claim boundaries, an approval-gated copy-only repair/retest API with identical command scope, exact-text hash-bound repair candidate validation without source mutation, optional approved repair retest in the four-workstream orchestrator/CLI with canonical-source preservation and checkpoint evidence, an explicit `proposal_from_agent` mode that consumes the same-run validated repair candidate, optional debug execution in the four-workstream orchestrator/CLI with checkpoint advancement, an opt-in validated local/OpenAI-compatible diagnosis-agent step, an opt-in validated local/OpenAI-compatible repair-agent step that can emit an exact edit from bounded replay context, and durable hash-verified local workflow checkpoints with CLI resume auditing | Semantic hierarchical slicing across arbitrary module bodies and constructs, richer golden-model control/data-flow alignment across implementations, full state-frontier attribution, general agent-generated patch synthesis beyond bounded exact-text edits, and durable distributed execution |
| Structured collateral and EDA optimization | Typed hash-bound collateral intake for specifications, RTL, testbenches, reference models, register specs, protocol plans, and constraints with structured entity extraction and conflict detection, typed RTL inventory, Yosys-backed structural RTL IR, parser-backed Yosys signal/cell CDFG emitted and gated by the four-workstream structural stage, deterministic bounded structural partitions, digest-bound connected functional CDFG dependency partitions for selected targets, solver-backed Yosys functional-equivalence gate for distinct reference/candidate tops, deterministic UVM scaffold, schema-bound protocol-plan DSL and sequence generator, deterministic coverage-gap augmentation, monotonic measured coverage-convergence trajectories with explicit converged/active status, typed hashable optimization state with failure/sensitivity/prior records and Pareto validation, bounded runtime-aware candidate selection with explicit explore/exploit/diversify/repair/prior-refinement modes, proxy-metric promotion/rejection gate, provenance-checked measured-result recording, bounded proxy/full command execution with machine-readable QoR ingestion, strict OpenLane `metrics.csv` QoR adapter with conflicting-alias rejection, digest-checked persisted optimization state with atomic stale-state-resistant appends, source-revision-aware repeated pipeline runs, and optional same-run proposal-to-measurement recording in the four-workstream CLI, `register-spec-v1` RTL/C-header/UVM-RAL/scoreboard generation, behavioral `RW`/`RO`/`W1C` shadow semantics, exact cross-artifact register/field semantic verification that cannot be bypassed by rehashing generated output, conservative IP-XACT and fail-closed SystemRDL subset frontends, and optional optimization proposal execution in the four-workstream orchestrator/CLI with checkpoint advancement | Full SystemRDL/IP-XACT coverage, full UVM simulator integration, measured coverage convergence across executable generated sequences, functional AST-to-RTL partition reconstruction, and integration with production EDA command sets and metric naming variants |

The first executable register-collateral slice is available at
`benchmarks/register_peripheral/structured_register_spec.json`. It is
generated with:

Each four-workstream pipeline invocation also emits a
`four-workstream-evidence-manifest.json` content-addressed inventory and
attaches it to the workflow checkpoint, making the combined evidence set
auditable before human-approved release.

```text
python3 scripts/generate_register_bundle.py \
  benchmarks/register_peripheral/structured_register_spec.json \
  .artifacts/structured-register-bundle
```

The command validates a hash-bound bundle containing synthesizable RTL, a C
header, and UVM/RAL metadata. The generated RTL is also compiled with Icarus.
This proves the initial structured-collateral boundary; it does not yet prove
that the hand-written `register_peripheral` RTL has been replaced by the
generated implementation.

Protocol transactions are represented separately as a validated
`protocol-plan-v1` DSL and compiled into a handshake-safe SystemVerilog
sequence:

```text
python3 scripts/generate_protocol_sequence.py \
  benchmarks/register_peripheral/protocol_sequence.json \
  .artifacts/structured-register-bundle/peripheral_sequence.sv
```

The generated sequence is compile-checked with Icarus. It is a deterministic
transaction generator. The four-workstream CLI can now accept validated
coverage-gap transaction proposals, deterministically augment the plan, and
compile the resulting sequence. It can also ingest a measured coverage report
and emit a deterministic gap-ranking artifact. The orchestrator now also
supports an ordered set of no-shell executable-sequence commands, parses their
measured progress markers, and records a monotonic convergence trajectory that
blocks on regressions or incomplete final execution. UVM capability probing and
an explicit no-shell UVM compile adapter, plus optional runtime marker
validation reachable through the four-workstream CLI, are integrated into the same
orchestrator and checkpoint manifest; full UVM runtime/scheduling compatibility
and DUT functional-coverage convergence remain future work.

The provider-free Colab/CI reference run now exercises this path using the
checked-in CSR fixture and records a measured `2/2` executable-sequence result;
the Colab checkpoint and artifact-manifest audits pass with that evidence
included.

An authenticated Colab run on 2026-09-14 executed the real-model benchmark
with `Qwen/Qwen2.5-0.5B-Instruct` on a Tesla T4. Its 11/11 case acceptance
contract passed, including grounded diagnosis, adversarial review, mutation
diagnosis, and seeded repair checks. The downloaded artifact is retained at
`.artifacts/llm-agent-colab/four-workstreams-real-20260914/`; this is real
model provenance and proposal-quality evidence, not autonomous release or
silicon-correctness evidence.

The same Colab run now also compiles and executes the clean seeded-counter
reference RTL with the C++ Verilator smoke harness. The intentionally buggy
RTL remains the separate formal/debug input, so acceleration success and bug
detection are reported as distinct evidence rather than merged into one claim.

It also runs the small synthesizable counter checker against that clean
reference, records no mismatch over four host-observed cycles, and emits the
SVM evidence artifact. This establishes the software compile/run boundary;
FPGA frequency, utilization, and system-level emulation remain unclaimed.

The Colab reference run also executes the checked-in normal-completion
time-zero fixture and records `normal_completion`, with the classified runtime
artifact linked into the checkpoint. This is fixture-level scheduler evidence;
it does not establish native Verilator coroutine/UVM compatibility.

It now runs the complete five-case time-zero matrix before the main pipeline,
includes its classified artifacts in the same evidence manifest, and exposes
the matrix status and case count to the Colab/CI contract.

The Colab run also ingests the specification, primary RTL, protocol plan, and
structured register specification through the typed collateral package, so
planning receives source-digest-bound structured input in addition to the
execution evidence.

## Scope and non-goals

### In scope

- Natural-language requirements to structured verification plans.
- Verification-plan to SVA candidate generation.
- Specification-grounded contamination controls.
- Open-source SVA compilation and lowering.
- Solver-in-the-loop proof, vacuity, and counterexample feedback.
- Bounded multi-agent orchestration with typed artifacts.
- Evaluation on seeded bugs and temporal corner cases.
- Hash-linked evidence integrated with the existing release manifest.

### Explicitly out of scope for the first implementation

- Autonomous tapeout approval.
- Analog verification or analog authorization.
- Measured-silicon qualification.
- Replacement of commercial signoff tools.
- Unbounded autonomous agent loops.
- Treating a solver `PASS` as sufficient evidence without checking that
  assertions were compiled, active, and non-vacuous.

## Design principles

1. **The specification is authoritative.** Functional intent must originate
   from the natural-language requirement or an approved verification plan.
   RTL may be consulted for signal names, directions, widths, hierarchy, and
   syntactic compatibility, but not to invent functional intent.

2. **Every model output is a proposal.** The model cannot directly authorize
   a repair, release, or claim. Typed validators and formal tools determine
   whether a proposal is admissible.

3. **Fail closed.** Missing provenance, unsupported syntax, stale hashes,
   empty property sets, vacuity, scope drift, and ambiguous requirements must
   block a claim rather than silently downgrade it.

4. **Keep artifacts immutable and inspectable.** Every stage emits a file,
   schema, digest, tool version, and parent-artifact reference.

5. **Start with one vertical slice.** The seeded counter design is the first
   complete target. Generality comes after the complete path is trustworthy.

## Target architecture

```text
Requirement package
  - natural-language specification
  - requirement IDs
  - clock/reset declarations
  - assumptions and exclusions
             |
             v
SpecParser / VerificationPlanner
             |
             v
Verification IR
             |
       +-----+------+
       |            |
       v            v
SignalMapper   SVAComposer
       |            |
       +-----+------+
             v
       Candidate SVA package
             |
             v
  Compiler / lowering boundary
             |
             v
   SymbiYosys + solver + vacuity checks
             |
       +-----+------+
       |            |
       v            v
  Proof result   Counterexample
       |            |
       +-----+------+
             v
     bounded PropertyRepairer
             |
             v
   approved formal evidence
             |
             v
 Existing agentic hardware closure
```

The orchestrator owns budgets, schemas, hash validation, retries, and state
transitions. Agents provide structured proposals only.

## Phase 1: Verification intermediate representation

Create a typed verification IR between prose and SVA. A minimal instance is:

```json
{
  "requirement_id": "counter_wraps",
  "statement": "When the counter is at MAX and increment is asserted, the next count is zero.",
  "clock": "clk",
  "reset": {"signal": "rst", "active": 1},
  "antecedent": {
    "kind": "and",
    "terms": ["count == MAX", "increment"]
  },
  "consequent": "count_next == 0",
  "temporal_window": {"operator": "|=>", "delay": 1},
  "signals": ["clk", "rst", "count", "increment"],
  "assumptions": [],
  "unresolved_questions": []
}
```

The IR should distinguish:

- boolean expressions;
- sequences;
- properties;
- clocks and reset semantics;
- assumptions;
- signal references and widths;
- temporal operators;
- confidence and unresolved ambiguity.

Required metadata:

- specification digest;
- requirement ID;
- generator/model provenance;
- parent artifact digest;
- schema version;
- parser and tool versions.

An IR with unresolved functional ambiguity must not be synthesized into a
release-quality assertion. It may be emitted as a review candidate.

## Phase 2: Specification-grounded SVA generation

Implement an SVA composer that converts approved IR into candidate properties,
for example:

```systemverilog
assert property (
  @(posedge clk) disable iff (rst)
  (count == MAX && increment) |=> count == 0
);
```

Each generated property package must include:

- the requirement ID;
- the exact specification digest;
- the SVA text;
- clock and reset interpretation;
- referenced signals;
- assumptions;
- unsupported constructs, if any;
- generation model and prompt/template digest;
- a contamination-policy result.

The model must not receive active RTL while deciding the functional meaning of
the property. If RTL context is provided, it must be a separate signal-mapping
tool result limited to structural facts.

Add a negative contamination test in which buggy RTL contradicts the
specification. The generated property must follow the specification and expose
the bug, not encode the buggy implementation as a passing assertion.

## Phase 3: Compiler and lowering boundary

The first implementation should use a conservative wrapper strategy: lower
properties into an explicitly instantiated checker that the open-source
frontend retains during elaboration. Do not rely on a `bind` directive unless
the resulting design contains machine-checked evidence that the bound checker
was compiled and active.

Add an explicit lowering pipeline for the subset needed by the first vertical
slice:

### Clock alias injection

Turn implicit property clocks into an explicit clocked form:

```systemverilog
always @(posedge clk)
  assert property (property_body);
```

### `disable iff` extraction

Preserve reset-abort semantics as an explicit guard in the lowered checker.
Tests must distinguish reset-active behavior from ordinary antecedent failure.

### Sequence-delay lowering

For supported constant delays, lower `##N` into explicit state or shift-register
logic, retaining the original operator, delay, and source digest in metadata.

### Unsupported syntax

Unsupported operators must produce `unsupported` with a reason and block a
formal-coverage claim. They must never be silently dropped.

Every lowering pass must emit:

- original SVA;
- lowered representation;
- transformation name and version;
- source-to-output mapping;
- compiler diagnostics;
- input and output digests.

After the first working subset, evaluate Property IR and CIRCT's LTL dialect as
the long-term representation. The purpose is to preserve temporal structure
for optimization and analysis instead of accumulating ad-hoc text rewrites.

## Phase 4: Solver-in-the-loop validation

For every candidate property:

1. Compile the property and checker.
2. Prove it with SymbiYosys and the configured backend.
3. Verify that the property set is non-empty and active.
4. Run vacuity analysis or an equivalent antecedent-activation check.
5. Classify the result as `proven`, `falsified`, `vacuous`, `timeout`, or
   `unsupported`.
6. Convert diagnostics and counterexamples into a bounded structured repair
   prompt.
7. Permit only a small configured number of property-repair iterations.
8. Re-run the identical formal scope and compare scope hashes.

The repair agent may change the candidate property or its lowering annotation,
but it may not change the specification, RTL, proof scope, clock, reset, or
assumptions without a new human review boundary.

A solver `PASS` is admissible only when:

- assertions compiled successfully;
- the checker was retained and active;
- the property was exercised or shown non-vacuous;
- the formal scope matches the requested scope;
- the source and tool digests are bound into the evidence.

## Phase 5: Bounded multi-agent orchestration

Use specialized roles with narrow responsibilities and typed outputs:

| Agent | Responsibility | Cannot do |
|---|---|---|
| `SpecParser` | Extract requirements and ambiguity | Read implementation behavior as intent |
| `SignalMapper` | Map approved names to RTL interface facts | Change functional meaning |
| `SVAComposer` | Produce candidate SVA from IR | Authorize evidence |
| `CompilerAgent` | Explain diagnostics and request supported lowering | Silently discard syntax |
| `FormalAgent` | Classify proof, vacuity, timeout, and CEX | Declare release approval |
| `PropertyRepairer` | Make bounded property-only revisions | Edit RTL or assumptions without review |
| `ReviewAgent` | Check contamination and evidence completeness | Override formal results |

The deterministic orchestrator must enforce:

- maximum interaction rounds;
- maximum candidate count;
- allowlisted tools and files;
- JSON schema validation;
- no hidden state between runs;
- hash-bound parent/child artifacts;
- explicit human approval for scope or implementation changes.

## Phase 6: Evaluation suite

Build a small but adversarial benchmark before broadening the system. It
should include:

- correct and seeded-buggy counters;
- FSM transition properties;
- reset and clock-domain cases;
- one-cycle and multi-cycle temporal behavior;
- unsupported SVA constructs;
- intentionally vacuous antecedents;
- `bind`-only checker modules;
- specifications that deliberately contradict the RTL.

Report these metrics independently:

- IR extraction accuracy;
- SVA syntax correctness;
- compilation correctness;
- checker-retention rate;
- non-vacuity rate;
- functional correctness against the specification;
- seeded-bug detection rate;
- property-repair success rate;
- false-positive rate;
- average latency and retry count;
- provenance and evidence completeness.

Do not report only solver pass rate. A high pass rate can indicate that
properties are vacuous, discarded, or contaminated.

## First vertical-slice acceptance test

The first milestone is complete only when this path works on the seeded
counter:

```text
natural-language requirement
        -> verification IR
        -> Qwen-generated SVA
        -> explicit assertion lowering
        -> SymbiYosys proof/vacuity check
        -> bounded property repair
        -> existing closure evidence and release manifest
```

The decisive acceptance test is:

> Deliberately buggy RTL must produce a formal failure from a
> specification-grounded assertion, while an assertion that merely mirrors
> the buggy RTL must be rejected, flagged as contaminated, or fail the
> meaningfulness checks.

Additional gates:

- no empty-property-set `PASS`;
- identical formal scope before and after repair;
- all generated properties trace to a specification requirement;
- all lowering transformations are digest-bound;
- all model outputs retain execution provenance;
- no analog authorization is implied;
- release remains human-gated.

## Integration with the current repository

The existing agentic closure runner, independent checkers, Colab model
benchmark, physical handoff, API, UI, and release manifest should remain the
outer governance layer. The new pipeline should add formalization artifacts
under a distinct evidence namespace, for example:

```text
.artifacts/llm-agent/autoformalization/<run-id>/
  requirement-package.json
  verification-ir.json
  signal-map.json
  sva-candidates.json
  lowered-properties.json
  formal-results.json
  vacuity-results.json
  repair-trace.json
  autoformalization-summary.json
```

The summary should be consumed by the existing closure and release validators,
which should continue to enforce source matching, formal scope, physical
evidence, human signoff, and the analog boundary.

## Recommended implementation order

1. Verification IR schema and validator.
2. Seeded-counter specification parser and deterministic SVA composer.
3. Qwen-backed composer with contamination and provenance checks.
4. Explicit checker-wrapper lowering and empty-property-set detection.
5. SymbiYosys proof and vacuity classification.
6. Bounded property repair using formal diagnostics.
7. Evidence packaging and integration with the existing manifest.
8. Adversarial benchmark and metrics.
9. Additional SVA operators and multi-agent roles.
10. Property IR/CIRCT investigation and migration plan.

This ordering ensures that each research feature is attached to a working,
auditable artifact chain and that the system gains capability without weakening
the closure guarantees already implemented.

## Complementary workstream: verification execution acceleration

Auto-formalization improves what the agent asks the tools to verify. It does
not, by itself, make repeated verification fast enough for large designs. A
second workstream is therefore required to reduce the execution cost of the
agent loop.

The current repository has model execution on Colab/T4, deterministic
simulation/formal checks, OpenLane physical evidence, and release governance.
It does not yet provide Verilator UVM execution, time-zero scheduling
regression coverage, or FPGA-hosted synthesizable reference models. These
capabilities should be added as an acceleration layer, not treated as already
achieved functionality.

### Target combined architecture

```text
LLM specification/SVA agent
        ↓
formal and simulation feedback
        ↓
bounded RTL/property repair
        ↓
fast Verilator regression
        ↓
formal verification
        ↓
FPGA/SVM system-level validation
        ↓
OpenLane physical evidence
        ↓
human-gated release manifest
```

The software simulator, formal engine, and FPGA emulator have different
purposes. Verilator provides rapid block-level and integration feedback;
formal tools provide exhaustive reasoning within their modeled scope; and an
FPGA reference model can provide high-throughput system-level checking. None
of these stages may silently substitute for another stage's evidence.

### Acceleration phase A: compiled software simulation

Integrate Verilator first on the seeded counter and a small UVM-like or
coroutine-based testbench. Establish a reproducible baseline against the
existing simulator, recording:

- compile command and Verilator version;
- simulation runtime and compile time;
- waveform format and digest;
- test and seed;
- assertion results;
- peak memory;
- simulator-result equivalence.

Where supported by the selected Verilator version, evaluate dynamic timing,
C++20 coroutine compilation, SVA assertion support, and FST tracing. The exact
flags must be discovered and validated against the installed tool rather than
copied as an unconditional assumption. A typical candidate configuration may
include dynamic timing, coroutine support, assertions, and FST tracing, but a
failed or unsupported flag must fail clearly in CI.

The first performance claim should be modest: demonstrate that the compiled
simulation is functionally equivalent to the reference simulation and measure
the speedup on the same workload. Do not claim UVM compatibility or native
system-level throughput from a small smoke test.

### Acceleration phase B: time-zero and scheduler reliability

Create a dedicated regression suite for initialization and cooperative
scheduling hazards. It should include:

- dynamic class construction in initialization blocks;
- nested constructors and virtual-interface registration;
- `#0` delays and `#1step` timing guards;
- objection raise/drop sequences;
- fork/join and event waits at time zero;
- multiple asynchronous clocks;
- premature `$finish` detection;
- an intentionally empty or inactive property set.

The harness must distinguish these outcomes:

```text
normal completion
formal/test failure
timeout or deadlock
premature time-zero termination
missing stimulus
```

A simulation that exits at time zero, clears objections before stimulus, hangs,
or produces no expected activity must be `blocked`, not `passed`.

Add deterministic lint rules for the patterns that the project chooses to
support, including unsafe dynamic construction, constructor delays, and
unprotected objection handling. These rules should report file, line, rule
identifier, severity, and remediation guidance. They should be tested against
both positive and negative examples. Version-specific Verilator regressions
must be recorded as tool compatibility data and reproduced with minimized
testcases; external issue or patch claims should not be treated as repository
evidence until locally reproduced.

### Acceleration phase C: tiered cloud CI

Introduce a tiered pipeline suitable for both human commits and agent
proposals:

```text
Tier 1: deterministic lint and policy checks
        ↓
Tier 2: Verilator compilation and smoke simulation
        ↓
Tier 3: block-level regression and waveform checks
        ↓
Tier 4: formal proof, vacuity, and counterexample analysis
        ↓
Tier 5: FPGA/SVM emulation for selected system workloads
        ↓
Tier 6: OpenLane physical handoff and human review
```

Every tier should emit a machine-readable result, toolchain digest, source
digest, workload/seed, elapsed time, and parent artifact digest. Agents should
receive Tier 1–4 diagnostics through bounded APIs; FPGA submission and release
claims remain explicitly gated operations.

The CI design should also track practical resource constraints, especially
Verilator C++ compilation memory, parallel job count, FPGA availability, and
artifact size. A performance optimization is useful only if its resource
requirements and reproducibility are recorded.

### Acceleration phase D: synthesizable verification model

An SVM should be attempted only after the software and scheduling stages are
stable. Begin with a small synthesizable reference model, such as a counter or
limited RISC-V instruction subset, rather than immediately converting a full
software ISS.

The initial SVM must define:

- the reference-model state and update semantics;
- the DUT-to-reference observation interface;
- mismatch detection and cycle alignment;
- reset and exception behavior;
- synthesis constraints and resource utilization;
- on-chip trace capture;
- host-readable mismatch records;
- a replay path for high-granularity debugging.

The DUT and SVM should share the FPGA clock domain where appropriate, with
explicit handling for clock crossings and backpressure. The first success
criterion is not a headline frequency; it is agreement with the software
reference model over reproducible workloads and correct mismatch localization.

For a larger CPU-class SVM, later milestones may add pipelining, batching,
state squashing, speculative checking, and a dual execution/debug mode. Those
features require measured FPGA results: frequency, throughput, LUTs, FFs,
BRAMs, DSPs, host traffic, mismatch latency, and debug-trace capacity.

### Acceleration acceptance criteria

The acceleration workstream is complete for the first vertical slice only
when:

- Verilator and the reference simulator agree on functional outcomes;
- time-zero deadlock and premature-termination tests are detected and fail
  closed;
- lint, compile, simulation, formal, and artifact digests are CI-linked;
- agent retries consume bounded, reproducible execution budgets;
- a small synthesizable checker agrees with the software reference model;
- injected DUT bugs are detected and replayable;
- performance claims include measured workload and resource context;
- the existing human approval and analog-disabled release boundary remains
  unchanged.

### Relationship to the auto-formalization workstream

The two workstreams meet at the formal and evidence interfaces:

```text
Auto-formalization:    requirement -> SVA -> proof result
Execution acceleration: testbench/RTL -> fast simulation/emulation result
                                      \         /
                                       evidence package
                                             ↓
                                   existing closure manifest
```

Auto-formalization should use fast Verilator feedback for compilation and
simulation triage, while retaining formal proof and vacuity checks as separate
gates. The SVM should supply high-volume system-level evidence, but it must not
authorize an assertion, repair, or release by itself.

The combined long-term goal is a cloud-native, agent-compatible verification
pipeline that provides rapid deterministic feedback without allowing speed,
parallelism, or hardware acceleration to weaken specification grounding or
human control of release claims.

## Complementary workstream: logic-aware RTL debugging

Auto-formalization produces properties and execution acceleration produces
faster results. A third workstream is needed to explain failures and localize
the earliest point where the RTL diverges from intended behavior. This is the
logic-aware debugging layer.

The current repository provides a bounded RTL repair loop and preserves formal
and simulation evidence, source hashes, and verification scope. It does not
yet implement waveform back-tracing, recursive dependency slicing,
cross-language golden-model alignment, causal counterexample graphs, or a
durable resumable workflow. Those capabilities should be added explicitly and
should not be implied by the existing repair loop.

### Target debugging architecture

```text
simulation failure or formal counterexample
                 ↓
waveform/CEX normalizer
                 ↓
RTL AST and dependency graph
                 ↓
backward slice from failed signal/property
                 ↓
earliest divergent cycle (state frontier)
                 ↓
causal graph and competing hypotheses
                 ↓
FOR / AGAINST diagnostic review
                 ↓
minimal repair context
                 ↓
bounded RTL repair and identical retest
```

The deterministic graph and trace algorithms should establish the evidence.
The LLM should summarize, rank, and propose explanations within that evidence;
it should not invent a causal path that is absent from the trace or RTL graph.

### Debugging phase A: failure and waveform normalization

Define a common failure schema for simulation and formal results:

```json
{
  "failure_id": "counter_wraps_failure_001",
  "source_digest": "...",
  "property_id": "counter_wraps",
  "failure_kind": "formal_counterexample",
  "clock": "clk",
  "start_cycle": 0,
  "end_cycle": 8,
  "failing_cycle": 6,
  "observations": [
    {"signal": "count", "cycle": 5, "value": 15},
    {"signal": "increment", "cycle": 5, "value": 1}
  ],
  "waveform_digest": "...",
  "formal_trace_digest": "..."
}
```

The normalizer should convert supported VCD/FST/formal-counterexample formats
into a bounded, cycle-indexed representation. It should record timescale,
clock mapping, reset interpretation, unknown-value handling, and truncation.
An incomplete or ambiguous trace must be reported as incomplete rather than
presented to the model as complete evidence.

### Debugging phase B: recursive dependency slicing

Build an AST-derived dependency graph whose nodes represent signals,
expressions, assignments, registers, ports, and module instances. Starting at
the failed output or assertion signal, traverse drivers backward through
combinational and sequential logic. At hierarchy boundaries, map child ports to
parent nets and continue the traversal.

The slicer should emit:

- selected source files and line locations;
- selected statements and expressions;
- driver and fan-in edges;
- register and clock boundaries;
- unresolved black boxes or dynamic constructs;
- top-level inputs controlling the slice;
- the original design digest and slice digest.

The result must be a compile-ready Filtered DUT or checker context. If
reconstructing a syntactically valid slice is unsafe, the system should retain
the original source and emit a structured context manifest instead of silently
rewriting semantics.

The first useful slice is not necessarily the smallest textual slice. It must
preserve the state, reset, clock, and control context needed to reproduce the
failure. Slice reduction is therefore subject to a replay test: removing a
selected dependency must either preserve the failure or be recorded as an
intentional abstraction.

### Debugging phase C: state-frontier detection

When a golden reference model is available, align RTL and reference traces by
cycle and compare corresponding state variables. The state frontier is the
earliest cycle at which an aligned internal state diverges, not merely the
cycle at which the final output fails.

For a golden variable `p` and RTL signal `v`, alignment may combine:

- names and documentation;
- structural neighbors and hierarchy;
- control and data-flow graph similarity;
- runtime trace correlation;
- explicit human mappings for ambiguous cases.

Ambiguous mappings must remain unresolved until reviewed. A guessed mapping
must not be used as root-cause evidence.

The frontier artifact should contain:

- aligned signal pair;
- first divergent cycle;
- prior cycles showing agreement;
- values on both sides of the divergence;
- controlling assignments and conditions;
- source locations;
- mapping confidence and unresolved alternatives.

### Debugging phase D: causal graphs and balanced diagnosis

Convert a formal counterexample or normalized waveform into a causal graph.
Nodes represent signal assignments at specific cycles; edges represent
structural driver relationships and permitted temporal transitions. The graph
must retain enough metadata to trace every proposed causal explanation back to
RTL and trace evidence.

Use a graph scanner to identify candidate suspicious nodes, then require the
diagnostic model to produce both sides of each hypothesis:

```text
FOR:     evidence that the node contradicts the requirement or reference
AGAINST: evidence that the node is expected under the design's actual context
```

This balanced output is a guardrail against flagging legitimate stalls,
backpressure, reset behavior, or pipeline latency as bugs. A hypothesis should
be ranked only from observed trace values, dependency edges, specification
terms, and tool diagnostics.

The final diagnostic package should include:

- ranked root-cause hypotheses;
- causal timeline;
- state frontier, when a reference is available;
- FOR and AGAINST evidence;
- minimal RTL context;
- proposed patch and affected lines;
- confidence and unresolved questions;
- parent artifact digests.

### Debugging phase E: durable orchestration and repair memory

Long-running debug jobs should be resumable. The workflow state should record
the completed stage, tool invocation, model response, artifact digests, retry
budget, and approval status. A restart must resume from a validated checkpoint,
not silently repeat earlier stages with different inputs.

The first implementation may use the existing API/CLI state machine and
filesystem evidence bundles. A later implementation can evaluate Temporal or
another durable workflow engine when jobs span remote simulators, FPGA queues,
or human review pauses.

Verified repair memory should be indexed by structural and semantic features,
not text similarity alone. Candidate keys may include AST subtree shape,
register/control pattern, property kind, failure class, and proof outcome. A
retrieved repair is guidance only; it must pass the same compilation, formal,
regression, provenance, and human-approval gates as a newly generated repair.

### First debugging vertical slice

Implement the following on the existing seeded counter:

1. Inject a known RTL bug.
2. Capture a failing simulation or formal trace.
3. Normalize the trace into cycle-indexed evidence.
4. Build the RTL dependency graph.
5. Back-trace from the failed counter output or property.
6. Emit a minimal replayable context slice.
7. Identify the earliest divergent cycle.
8. Ask Qwen for FOR and AGAINST hypotheses.
9. Generate a bounded repair proposal.
10. Re-run the identical verification scope.
11. Package the diagnosis, patch, replay, and digests for human review.

The decisive acceptance test is:

> The system must identify the first incorrect state transition and produce a
> repair whose retest passes, while preserving a replayable causal path from
> the failure back to the RTL source and specification requirement.

### Debugging acceptance criteria

The first slice is complete only when:

- every diagnostic claim maps to a trace observation or RTL graph edge;
- the selected context can reproduce the failure;
- the state frontier is earlier than or equal to the output mismatch when a
  valid golden model exists;
- FOR and AGAINST evidence is present for every ranked hypothesis;
- ambiguous signal mappings are disclosed and block unsupported claims;
- repair edits are bounded and hash-linked;
- identical simulation/formal scope is re-run after repair;
- deadlocks, incomplete traces, and missing signals fail closed;
- the existing human approval and analog-disabled release boundaries remain
  unchanged.

### Relationship to the other workstreams

The three technical layers now have distinct responsibilities:

```text
Auto-formalization       requirement -> IR -> SVA -> formal result
Logic-aware debugging    failure -> slice -> frontier -> root cause -> patch
Execution acceleration   RTL/testbench -> fast simulation/emulation result
                                   \       |       /
                                    \      |      /
                                      evidence package
                                             ↓
                                  existing closure manifest
```

Auto-formalization supplies specification-grounded properties. Logic-aware
debugging explains failures and constrains repair context. Verilator and FPGA
acceleration reduce feedback latency. The existing closure system remains the
governance layer that binds all evidence and requires human approval before a
release claim.

## Complementary workstream: structured collateral and EDA optimization

The preceding workstreams improve formalization, diagnosis, and execution. A
fourth workstream makes the inputs and generated collateral structurally
reliable and enables evidence-driven physical-design optimization.

The current repository has compatible foundations—structured JSON evidence,
hash-bound manifests, OpenLane execution, physical metrics, source matching,
bounded LLM actions, deterministic register collateral, a protocol-plan
generator, and bounded structural partitions—but it does not yet provide broad
structured ingestion of technical collateral, full UVM simulator integration
beyond explicit compile evidence,
partition reconstruction/equivalence, or persistent EDA optimization memory.

### Target collateral-to-closure architecture

```text
technical collateral
  PDFs / IP-XACT / SystemRDL / register maps / protocol specifications
                          ↓
               parser and schema validator
                          ↓
                  typed hardware IR
                 /         |         \
                v          v          v
       synthesizable RTL  C headers  UVM/RAL model
                |          |          |
                +----------+----------+
                           ↓
                 deterministic testbench
                           ↓
             simulation/formal/coverage feedback
                           ↓
          bounded agent proposals and stateful EDA tuning
                           ↓
                  physical-design evidence
                           ↓
                existing release manifest
```

The LLM should extract, classify, and propose structured plans. Deterministic
parsers, schema validators, templates, and compilers should produce the final
RTL, drivers, testbench components, and protocol transactions.

### Structured ingestion and verification IR

Define a canonical collateral package that preserves both source material and
normalized structure. It should support, incrementally:

- natural-language requirements;
- register maps and bitfields;
- clock, reset, and interrupt relationships;
- protocol interfaces and transaction rules;
- IP-XACT or SystemRDL inputs;
- physical constraints and tool configuration;
- source locations and extraction confidence.

Every normalized item must retain:

- source-document digest;
- page, section, or XML path;
- schema version;
- parser version;
- units and numeric widths;
- unresolved ambiguities;
- parent/child artifact digests.

Text retrieval can provide context, but a text chunk must not be treated as the
authority for widths, offsets, timing, or access semantics when a structured
source exists. Conflicting sources should produce an explicit conflict rather
than an arbitrary model choice.

### Deterministic testbench and protocol generation

For each supported interface, represent the physical and behavioral contract
as validated artifacts such as:

```json
{
  "interface": "wishbone",
  "clock": "clk",
  "reset": {"signal": "rst", "active": 1},
  "signals": {
    "adr": {"direction": "input", "width": 32},
    "dat_w": {"direction": "input", "width": 32},
    "stb": {"direction": "input", "width": 1},
    "ack": {"direction": "output", "width": 1}
  },
  "transactions": [
    {"name": "register_write", "steps": ["drive", "wait_ack", "sample"]}
  ]
}
```

Use protocol-specific templates and a small sequence DSL to generate drivers,
monitors, scoreboards, and stimulus. The DSL should express legal operations
such as register writes, reads, polling, resets, and value sweeps without
requiring the LLM to write arbitrary concurrent SystemVerilog.

The closed loop is:

```text
validated blueprint → deterministic generation → compile → simulate
                    → coverage analysis → targeted DSL proposal → repeat
```

Generated code must be checked for compile success, interface consistency,
clock/reset safety, protocol legality, and coverage attribution. Coverage
closure must not be represented by a model-generated claim alone.

### Executable register specification

The first high-value vertical slice should use a single structured register
specification as the source for:

```text
SystemRDL/IP-XACT-like source
        ├── synthesizable register RTL
        ├── C/C++ driver headers
        ├── UVM RAL model
        └── scoreboard/shadow-register semantics
```

The generated artifacts must agree on address offsets, widths, reset values,
field access behavior, and side effects, including at least `RW`, `RO`, and
`W1C` behavior plus reserved bits and reset behavior.

Add a machine-checkable cross-artifact comparison. A mismatch in address,
width, reset value, or access semantics must block the build and identify the
source field responsible.

The current deliverable uses a versioned JSON register IR and a conservative
IP-XACT register-subset frontend. The frontend covers the common register,
field, offset, width, reset, and access-policy elements and maps them into the
same downstream IR. Full standards coverage and a SystemRDL frontend remain
open, without changing the downstream consumers.

### AST representation and design partitioning

Parse RTL into an AST and, where useful, control/data-flow graphs. Preserve:

- module and instance hierarchy;
- declarations and widths;
- procedural regions;
- assignments and conditions;
- registers and clock domains;
- dependency edges;
- source locations.

Use this structure for context selection, debugging slices, template retrieval,
and local optimization. Do not begin with a GNN or a large learned partitioner.
First establish deterministic connected-subgraph partitioning with compile and
equivalence checks. A learned similarity model can be evaluated after a
verified structural baseline exists.

Any partition/reconstruction flow must prove that ports and widths, hierarchy
connections, and clock/reset boundaries are preserved; that the reconstructed
design compiles; and that behavior is equivalent for the declared scope, or
that the abstraction is explicitly marked and reviewed.

### Stateful physical-design optimization

Extend the existing OpenLane handoff into an evidence-gated optimization loop.
Persist a typed record for every candidate configuration:

- baseline constraints and initial search bounds;
- tool parameters and source digest;
- synthesis, placement, routing, and signoff status;
- timing metrics such as WNS/TNS;
- area and, when available, power;
- failure category and diagnostic evidence;
- runtime and resource usage;
- sensitivity observations;
- non-dominated Pareto candidates;
- parent run and configuration digests.

The optimizer may use explore, exploit, repair, diversify, and prior-refinement
modes, but every candidate must pass schema and hard-constraint checks before a
physical run. Start with a small deterministic grid or Bayesian baseline. Add
multi-fidelity scheduling only after candidate identity and metric collection
are stable.

The agent may propose tool parameters; it may not alter the design source,
constraints, or acceptance criteria without explicit review. A favorable WNS,
area, or power result is an optimization observation, not a signoff claim.

### First structured-collateral vertical slice

Implement the following on a small CSR/register block:

1. Define a versioned structured register specification.
2. Validate addresses, widths, reset values, and access policies.
3. Generate synthesizable RTL.
4. Generate C headers.
5. Generate a UVM-style register model and scoreboard.
6. Compile and simulate all generated consumers together.
7. Exercise `RW`, `RO`, and `W1C` behavior.
8. Compare the hardware, driver, and model representations automatically.
9. Record the artifacts and cross-check results in the existing manifest.

The decisive acceptance test is:

> One executable register specification must generate mutually consistent RTL,
> software definitions, and verification models, and an injected mismatch in
> any generated consumer must be detected before release.

### Structured-collateral acceptance criteria

The first slice is complete only when:

- every generated artifact traces to a structured source field;
- ambiguous or conflicting collateral blocks generation;
- generated interfaces compile with exact widths and directions;
- protocol sequences are legal and deterministic;
- register offsets, resets, and side effects agree across consumers;
- AST partitions preserve the declared structural/equivalence scope;
- optimization runs preserve candidate, tool, and metric provenance;
- physical results are reproducible for the same source and configuration;
- the existing human approval and analog-disabled release boundaries remain
  unchanged.

### Relationship to the complete program

The four workstreams now form a coherent stack:

```text
Structured collateral     collateral → typed IR → deterministic artifacts
Auto-formalization        requirement → IR → SVA → formal result
Logic-aware debugging     failure → slice → frontier → root cause → patch
Execution acceleration    RTL/testbench → fast simulation/emulation
                                      ↓
                         hash-bound evidence and state memory
                                      ↓
                              human-gated closure
```

This is the long-term architecture for an agent-compatible hardware
engineering system: agents help interpret specifications, diagnose failures,
and explore optimization choices, while structured representations,
deterministic generators, EDA tools, immutable evidence, and human review
control what can become an engineering or release claim.

Optimization recommendations now carry a canonical candidate-configuration
digest, and supplied measurement digests are checked against that identity
before a result is appended to persistent state. This binds measured QoR to
the exact proposed parameter set; it does not establish physical signoff.
The orchestration path also records the digest of the exact RTL source set
used for the run and checks a supplied measurement source digest against it.
Measured runs retain the relative metrics-artifact path beside its digest for
later evidence lookup.

Logic-aware debug packages also bind a divergent state frontier to the
corresponding causal-graph event, incoming structural edges, and available
RTL source locations. This improves review traceability without claiming that
the first driver is automatically the complete root cause.
The four-workstream result now exposes this binding and the reference Colab/CI
path checks that it is available.

The assertion-agent contract is now exercised by
`scripts/run_four_workstream_assertion_matrix.py` across the seeded counter,
arbiter, decoder, and FIFO designs. The matrix requires specification-bound
agent proposals and successful explicit lowering/compiler validation; it does
not claim formal proof or signoff. The bounded lowering subset includes
literal decode/grant mappings, numeric invariants, and full-gated one-cycle
increments. It now also includes direct `$onehot` and `$onehot0` predicate
requirements, including the conservative “at most one active bit” wording,
with explicit predicate lowering and compiler validation.
