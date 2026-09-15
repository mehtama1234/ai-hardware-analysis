# Next four SOTA workstreams

## Purpose

The current project has a bounded four-workstream reference flow and a
38-stage repository-scale acceptance run. The next step is not to add more
isolated demos. It is to test whether the same evidence-first agent loop can
generalize across real repositories, produce proof-carrying repairs, reason
over large designs, and connect digital verification to physical signoff.

The target end-to-end loop is:

```text
requirement and repository collateral
  -> structural representation
  -> agent plan or candidate
  -> deterministic EDA execution
  -> failure evidence
  -> localized diagnosis
  -> bounded repair proposal
  -> independent proof, simulation, coverage, and security checks
  -> identical-scope retest
  -> signed evidence package
```

An agent may propose work. Deterministic tools and independent checkers decide
whether the work is admissible. Human approval remains required for an
intent-changing repair or release promotion.

## Workstream 1: Repository-scale generalization benchmark

### Technical goal

Build a benchmark of at least 50 real historical hardware-tool fixes from at
least three open-source repositories, with the original failing revision, the
historical fix, a minimized executable regression, and a held-out evaluation
split. Measure whether agents can discover and repair bugs they did not see in
the development examples.

### Required system behavior

- Mine candidate fixes from upstream history and classify their failure mode.
- Reconstruct a deterministic regression from the issue, test, or changed
  behavior.
- Run the pre-fix version and record a genuine failure.
- Ask the agent for a bounded patch with source revision, evidence references,
  rationale, and exact edit scope.
- Apply the patch only to a disposable copy.
- Retest the repaired copy with an independent checker.
- Verify that the canonical checkout and the held-out source are unchanged.

### Acceptance gates

- 50 or more distinct fixes; at least 15 held out until evaluation.
- At least three repositories and at least five bug categories.
- Baseline failure reproduced for every accepted case.
- Repaired pass, canonical immutability, and report-integrity checks for every
  case.
- Report agent success, false-pass rate, abstention rate, patch size,
  diagnosis time, and human review time separately.

### Why this is deeper

The current four historical replays prove the contract works on selected
cases. This workstream tests generalization, data leakage, and whether the
agent is useful beyond fixtures designed during development.

## Workstream 2: Proof-carrying autonomous repair closure

### Technical goal

Turn a generated repair into a machine-checkable closure certificate that
combines specification-grounded assertions, simulation, mutation testing,
formal counterexamples or proofs, coverage change, and security-policy checks.

### Required system behavior

- Bind every assertion and test to a stable requirement ID and source digest.
- Generate both positive properties and adversarial negative tests.
- Use formal solving to classify each property as proven, falsified, or
  undetermined; detect vacuous and over-constrained properties.
- Use mutation testing to show that the checks detect representative bugs.
- Require assumptions to be explicit, reachable, digest-bound, and reviewed.
- Re-run the identical scope after an approved repair.
- Refuse release if any required evidence is missing, stale, vacuous, or
  contradictory.

### Acceptance gates

- At least 10 designs or blocks and at least 1,000 parameterized mutations.
- Zero accepted false passes in the independent checker.
- Every repaired case has a counterexample before repair and a post-repair
  proof or bounded closure result.
- Coverage must increase or be explained by an approved scope change; hidden
  coverage loss is a failure.
- Security checks must include privilege, reset, isolation, and information-
  flow policies, with review-required status for unresolved findings.

### Why this is deeper

The current system validates pieces of assertion, mutation, induction, and
security flows. This workstream makes them one anti-contamination contract so
that a passing generated assertion cannot be mistaken for design correctness.

## Workstream 3: Scalable semantic debugging and compiler/IR execution

### Technical goal

Debug failures in designs too large for a single LLM context by combining
parser-backed AST/CDFG slicing, causal counterexample graphs, golden-model
alignment, and a preserved temporal intermediate representation.

### Required system behavior

- Parse the complete design into a source-digest-bound structural index.
- Build a minimal compile-ready filtered DUT from a target signal or failed
  property, preserving hierarchy and clock/reset context.
- Convert waveforms and formal counterexamples into cycle-indexed causal
  graphs.
- Align RTL state with a C/Python reference model where one exists and report
  the first divergent state frontier.
- Present competing FOR and AGAINST explanations before ranking a root cause.
- Preserve SVA temporal structure through a typed property IR or equivalent
  lowering boundary; reject silent assertion deletion.
- Use compact slices for the repair agent and replay the proposed fix against
  the original design.

### Acceptance gates

- At least 10 multi-module designs, including multi-clock and reset behavior.
- At least 90% of accepted failures localized to the correct module and cycle
  on a held-out set.
- No false pass caused by an empty property set, dropped bind, lost reset
  guard, or invalid lowering.
- Slice compilation and replay must be independently checked against the
  full-design result.
- Measure context reduction, localization accuracy, repair success, and
  wall-clock cost against full-context prompting.

### Why this is deeper

The current project has dependency graphs, frontier records, and bounded
filtered context. This workstream tests whether those structures remain
correct and useful on genuinely large, hierarchical, temporally complex RTL.

## Workstream 4: Structured collateral through physical signoff

### Technical goal

Connect executable requirements and register/protocol specifications to
generated RTL, software headers, UVM models, simulation, physical
implementation, timing, and a signed release decision.

### Required system behavior

- Ingest a versioned SystemRDL/IP-XACT subset plus protocol and clock/reset
  constraints into a typed intermediate representation.
- Generate synthesizable register RTL, C headers, UVM RAL metadata, bus
  adapters, scoreboards, and requirement-linked checks from the same source.
- Run deterministic simulation, formal, lint, synthesis, placement, CTS,
  routing, extraction, STA, DRC, LVS, antenna, and ERC adapters where the
  tool capability exists.
- Maintain persistent optimization state for timing, area, power, runtime,
  failures, sensitivities, and Pareto trade-offs.
- Keep software, digital, physical, and measured-hardware claims separate.
- Produce a clean-checkout replayable package with source/tool/artifact
  hashes and explicit unsupported gates.

### Acceptance gates

- One nontrivial multi-clock block completed from executable spec to physical
  checks using the same register and protocol source.
- Generated RTL, driver definitions, and UVM model pass cross-artifact
  consistency checks.
- Physical results are reproduced from a clean checkout with identical scope.
- Timing, area, power, DRC, LVS, antenna, and ERC results are individually
  evidenced; unavailable tools remain blocked rather than inferred.
- A reviewer can make a bounded ship/no-ship decision from the package alone.

### Why this is deeper

This is the point where agentic RTL verification becomes a hardware
engineering product. It tests whether structured agent outputs survive the
interfaces between requirements, software, RTL, EDA compilers, and physical
signoff.

## Sequencing

Workstream 1 should be expanded first because it supplies an honest held-out
evaluation for the others. Workstream 2 should then define the release
certificate. Workstream 3 should improve diagnosis and scale. Workstream 4
should integrate the proven loop with the existing RTL-to-GDS and AIMC
qualification paths.

The four workstreams are complete only when each has independent evidence and
the joined package distinguishes `passed`, `review_required`, `blocked`, and
`not_run`. A green orchestration status alone is never sufficient for a
silicon or customer signoff claim.

## Current position

Workstream 1 has reached its initial 50-fix benchmark gate. Workstream 2 now
has an initial independent certificate layer that binds the aggregate to
simulation, mutation, formal, coverage, security, and assertion-integrity
artifacts. A separate scalable campaign now passes 1,000/1,000 mutations
across 10 generated executable designs with zero false passes. The remaining
Workstream 2 gap is production-RTL breadth and the full assumption/coverage
audit; the generated campaign is stress evidence, not production coverage. A
separate real-design catalog now passes on ten multi-module RTL targets with
source digests and compile evidence; functional localization on those targets
has now started with one real OpenLane peripheral replay. The first replay
passes baseline failure, agent repair, repaired simulation, and integrity
checks; localization coverage across the remaining targets remains open.
The multi-clock subsystem now also has an independently passing CDC repair
replay, and an AIMC operation-partition replay independently passes a
boundary-condition mutation. The fourth replay adds an AIMC error-budget
policy boundary. The real-design set therefore includes CSR, multi-clock, and
control-decision behavior; broader localization remains open.
Real waveform causal localization now also passes on the AIMC target: the
first divergent output event is identified, bound to its causal driver, and
linked to the mutated RTL assignment with a digest-checked timeline. The same
causal contract now passes on the real multi-clock hierarchy, including a
held-value frontier at the synchronized output and the two-stage CDC chain.
That causal report is now consumed by the real agent repair trajectory; the
repair certificate binds the report digest and frontier before copy-only
retest.

The operation-partition causal report is now consumed by a second real agent
repair trajectory. Its first-divergence frontier, causal-report digest, agent
context, and repaired copy are independently checked. The expanded 153-stage
aggregate and proof certificate pass at
`/tmp/next-stage-milestone-153-operation-causal-agent-20260915/`.

The error-budget policy boundary now has the same causal-localization and
causal-agent repair contract. Its same-cycle `reason` divergence is source
bound, consumed by the repair agent, and independently checked after retest.
The resulting three-class causal-agent aggregate and proof certificate pass at
`/tmp/next-stage-milestone-157-error-causal-agent-20260915/`.

The CSR peripheral path now also passes the causal-agent contract. Its
sequential `control` divergence is source bound, consumed by the repair agent,
and independently checked after retest. The four-class aggregate and proof
certificate pass at
`/tmp/next-stage-milestone-161-four-causal-agent-20260915/`.

The repository currently has the reference implementation, real Colab model
execution artifacts, parameterized mutation and security campaigns, formal
closure, assertion grounding, and a verified 161-stage aggregate. It has fifty
historical fix replays across OpenLane, OpenROAD, and cross-sim, plus 291
mined candidates with 58 held out in a protected split. Those results justify
starting these four workstreams; they do not satisfy their final acceptance
gates.
The real causal-agent task is now packaged for GPU execution, including the
real OpenLane source and digest-bound causal report. Its offline bundle smoke
test passes; a live Qwen run remains dependent on Colab session availability.
The four-class Colab handoff is now packaged as one reproducible archive with
all four real OpenLane source sets and causal reports. Its offline extraction
smoke test passes all four agent repairs and independent checkers; live Qwen
execution remains the next external gate.

The first Workstream 1 held-out repair evaluator has now been exercised as a
provider-free control. It preserves the declared train/held-out ordering and
passes 8/8 train cases plus 8/8 held-out cases through the isolated repair
closure harness; its independent checker verifies task identity and report
digests. The control reports zero model-selected repairs by design, so it is
split-hygiene and evaluator evidence, not LLM generalization evidence. The
real-model Colab runner already invokes the same evaluator with a resident
GPU model and requires the strict real-backend checker before accepting the
result.

The repository-scale benchmark CLI now has matching top-level execution and
independent validation entry points:
`scripts/run_repository_scale_benchmark.py` and
`scripts/check_repository_scale_benchmark.py`. The checker validates report,
record, snapshot, result, and changed-file digests without importing the
benchmark implementation, so a green runner result alone cannot satisfy the
evidence gate.

After these entry-point changes, the complete digital verification-platform
suite passes 371 tests. The canonical local unified release acceptance also
passes with decision
`local_unified_reference_and_model_to_chip_package_ready_for_signoff`, and
its independent checker reports no blockers. This closes the local regression
gate; it does not replace the required real-model Colab measurement.

A local cached Qwen2.5-Coder-0.5B checkpoint was also probed against the real
JSONL backend. The weights loaded successfully, but CPU inference did not
produce a typed proposal within a 120-second bounded probe, and the one-task
repair run therefore returned `blocked` with zero model-selected repairs.
This is recorded as execution-capacity evidence only; it is not a model
quality result and does not justify relaxing the evidence timeout or claiming
generalization.

Workstream 3 has now moved beyond source cataloging: the durable structural-IR
runner and independent checker pass on all 10 real multi-module targets. The
runner excludes testbench-only source files, includes the required I/O library
for the I²C target, and records source revisions, module counts, IR paths, and
IR digests. It now also emits parser-backed signal/cell CDFGs and independently
checks their node/edge counts and digests on all 10 targets. The runner now
also creates one bounded backward dependency slice per target, with all 10
slices `ready` and between 4 and 431 selected nodes under the 512-node bound.
The checker independently recomputes each backward cone and compares its
selected nodes and edges with the stored slice.
This is a parser/representation/context-reduction gate only; functional
localization and held-out first-divergence accuracy remain open.
