# End-to-End Goal: Evidence-Backed AI Verification Platform

This roadmap covers **Analog Design**, **Digital Design**, and **EDA** verification as one evidence-backed engineering flow. **AI For EDA** remains bounded by deterministic tools and reviewable evidence; the analog in-memory work remains the mixed-signal case study.

## North-star objective

Build a production-shaped, agentic verification platform that takes a semiconductor team's specifications and design collateral, creates a reviewable verification plan, executes simulation and formal workflows, explains failures using logic-aware evidence, and tracks requirements through closure.

The platform must help a verification engineer move from:

```text
specification -> verification intent -> executable checks -> tool execution
             -> failure localization -> root-cause hypothesis -> repair/retest
             -> coverage evidence -> requirement closure
```

The platform is successful when it reduces engineering uncertainty and manual effort inside a real verification flow. A fluent answer or generated test is not evidence of success. Every material claim must be tied to a source revision, tool invocation, waveform or counterexample, coverage result, and reproducible run record.

## What we are building

This is a verification execution and evidence system with AI agents, not a general-purpose hardware chatbot. The deterministic system owns parsing, schemas, tool invocation, run isolation, artifact hashing, traceability, and policy gates. Agents propose plans, queries, tests, assertions, diagnoses, and next actions. Humans approve changes that can affect design intent or closure.

The first release should support four connected workflows:

1. **Plan:** derive requirements, interfaces, assumptions, clocks, resets, properties, tests, and coverage goals from specifications and RTL.
2. **Run:** compile and execute simulation, lint, formal, and coverage jobs through existing EDA tools and CI environments.
3. **Debug:** cluster failures, identify the first meaningful divergence, trace the failing signal through the RTL dependency cone, and compare passing and failing runs.
4. **Close:** show which requirements are proven, tested, covered, blocked, or falsely marked complete, with evidence and review history.

## Core platform model

All collateral is converted into a versioned verification intermediate representation (IR). The IR links:

```text
requirement <-> interface/signal <-> property <-> test <-> tool run
            <-> waveform/counterexample <-> coverage result <-> closure decision
```

The IR must preserve source location, repository revision, elaboration configuration, simulator/formal tool version, command line, environment, inputs, outputs, and artifact hashes. Retrieval may use embeddings, but protocol widths, timing rules, register fields, reset semantics, and property relationships must come from typed structures and deterministic parsers.

The execution layer provides adapters for the tools customers already use. An adapter must report command, status, logs, warnings, compilation failures, timeouts, seed, configuration, and produced artifacts. An agent cannot declare a pass when the tool did not run, a bind/property was discarded, coverage is vacuous, or required artifacts are missing.

## Product workstreams

### 1. Collateral ingestion and verification IR

Ingest specifications, RTL/SystemVerilog, interfaces, register maps, UVM components, assertions, test plans, simulator logs, formal traces, waveforms, coverage databases, and CI metadata. Parse RTL and protocol structures where possible, retain raw source references, and expose a queryable graph for agents and user interfaces.

The acceptance test is a set of seeded width, reset, clock, and protocol traps. Retrieval must return the correct source evidence, and generated plans must not silently invent or change those facts.

### 2. Specification-grounded planning and generation

Generate a requirement matrix, verification strategy, test scenarios, assertions, coverage points, and environment dependencies. Generate UVM or directed-test code only after the plan is approved, using typed templates and dependency ordering. Generate SVA from specification evidence and require compilation, bounded proof, and vacuity checks before presenting a property as useful.

The review surface must show what was generated, which requirement motivated it, what assumptions it makes, and what tool result supports it.

### 3. Execution-in-the-loop regression control

Agents must be able to invoke simulators, linters, formal engines, synthesis checks, and coverage jobs within isolated, reproducible runs. They may retry bounded operational failures such as missing generated files or a known compile flag, but they must not alter design intent without approval.

The system records all attempts, including failures and timeouts. A run is complete only when its expected outputs exist and pass artifact integrity checks.

### 4. Logic-aware debug and root-cause analysis

For an assertion failure, mismatch, or formal counterexample, identify the first meaningful divergence rather than summarize an entire waveform. Parse the RTL dependency graph, back-trace the failing signal, construct a relevant cone, extract a compact temporal trace, and compare against a passing run or golden reference.

The result is a ranked root-cause hypothesis with signal values, source locations, timing, related requirements, and links to the exact evidence. The engineer can accept, reject, or correct the hypothesis, creating feedback for evaluation.

### 5. Coverage and closure management

Combine requirement, functional, code, assertion, and regression coverage. Detect unreachable or redundant tests, vacuous properties, stale results, configuration mismatches, and requirements whose apparent closure depends on an invalid run.

The closure view must answer: what remains unverified, why it remains unverified, which next run has the highest expected value, and what evidence is required before sign-off.

### 6. Mixed-signal and hardware-aware case study

Use the existing AIMC and converter work as the first technically difficult demonstration. The platform should ingest the GPT-2/WikiText workload, finite-reference calibration profile, SPICE converter evidence, RTL/controller traces, extracted-layout checks, holdout results, and repeated-decision latch failures.

It must explain the distinction between software-level workload agreement, circuit-level simulation qualification, physical-layout and electrical-margin qualification, and measured hardware latency and energy. This case proves that the platform can preserve uncertainty and reject an attractive but unsupported hardware claim.

The current execution target is the model-to-chip qualification loop for the
GPT-2 projection slice. The loop is considered physically eligible only after
one unchanged converter contract passes every required process corner, an
independent mismatch population reports accepted-map yield, and matched
converter/array/controller/data-movement energy coefficients are captured. The
Colab campaign runner, physical qualification gate, fail-closed checker, and
energy measurement contract are the executable handoff for this target. Until
those gates close, the verified T4 GPU path remains authoritative and the
system must not claim analog speedup or energy savings.

## Delivery stages

### Stage 1: benchmark and evidence foundation

Create a small reproducible benchmark containing open RTL designs, specifications, seeded bugs, simulation traces, formal counterexamples, coverage reports, and the existing AIMC artifacts. Implement the IR, provenance ledger, artifact hashing, and deterministic validation gates.

### Stage 2: execution and triage vertical slice

Support one simulator and one formal flow end to end. Run regressions, cluster failures, perform signal back-tracing, compare passing and failing traces, and produce cited diagnosis reports. Establish baseline engineer time and diagnosis accuracy before adding more autonomy.

### Stage 3: planning, generation, and closure

Add requirement extraction, test and assertion planning, template-based generation, vacuity detection, coverage prioritization, and human approval checkpoints. Measure whether generated artifacts compile, prove, improve coverage, and survive review.

### Stage 4: customer pilot shape

Package adapters, access controls, run isolation, audit logs, dashboards, and CI integration. Test the system against a customer's representative block or an equivalent benchmark using their normal simulator, formal tool, regression database, and review process.

## Proof-of-value metrics

The pilot must report before-and-after measurements, not subjective impressions:

- time from failure to accepted root-cause diagnosis;
- percentage of failures correctly localized to the first meaningful divergence;
- duplicate failures collapsed into actionable clusters;
- generated tests and properties that compile and pass review;
- coverage gained per compute hour;
- number of redundant regression jobs avoided;
- percentage of requirements with complete traceability;
- vacuous, stale, or invalid closure claims detected; and
- engineer review time per regression or closure decision.

The system may show no improvement on a metric. That result is retained as evidence and used to change the workflow or reject the use case.

## Definition of done

The end-to-end goal is complete only when a clean, versioned run can:

1. ingest a specification and RTL revision;
2. produce a traceable verification plan;
3. generate or select executable checks;
4. run simulation/formal/coverage tools through recorded adapters;
5. detect and classify an injected failure;
6. localize its likely cause with waveform or counterexample evidence;
7. propose a bounded repair or next experiment for human review;
8. rerun the affected checks; and
9. produce a closure report whose claims are reproducible from stored artifacts.

The current repositories already provide the workload, circuit evidence, validation discipline, failure-analysis examples, and documentation needed for the benchmark. They do not yet constitute the platform. The next engineering target is the typed evidence and execution layer that connects those artifacts to a real verification workflow.

The first implementation slice now lives in `verification_platform/`: `ir.py` defines the versioned graph root and requirement/evidence types, `ledger.py` provides content hashing and validated tool-run provenance, and `runner.py` executes one shell-free command while recording logs, timeout or failure state, and artifact hashes. Its tests establish deterministic serialization, duplicate-ID rejection, run-root containment, and explicit pass/fail/blocked outcomes.

The first executable benchmark now lives in `benchmarks/seeded_counter/`. It pairs a specification with intentionally faulty SystemVerilog, runs Icarus, captures a VCD, and emits a triage report identifying the first divergence (`counter_q`, cycle 1) and the seeded RTL location. This is the initial execution and root-cause contract that later adapters and agents must satisfy.

The benchmark now uses `verification_platform/triage.py` rather than a benchmark-specific parser. A parsed failure projects into `verification-ir.json` with hashed log and waveform evidence, giving the execution, diagnosis, and traceability layers a shared handoff.

`verification_platform/ingest.py` now converts explicit `REQ-ID: requirement text` lines into a specification IR and records the specification hash. The benchmark emits both `specification-ir.json` and failure `verification-ir.json`, preserving the plan-to-execution boundary without guessing requirements from prose.

`verification_platform/planner.py` adds the next gate: recognized requirement forms become traceable SVA check plans through conservative templates, while unsupported requirements remain unplanned for human review. The seeded benchmark emits `verification-plan.json` containing two generated checks.

`verification_platform/closure.py` adds evidence-gated closure evaluation. A failed requirement cannot be promoted to proven, and a passing status requires both linked artifacts and a recorded passed tool run. The seeded failing run emits `closure-report.json` with an explicit failed decision.

Root-cause reports now locate the unique `SEEDED_BUG` marker in the current RTL source at runtime and reject ambiguous markers. This keeps the diagnosis tied to the actual source revision as the benchmark evolves.

`verification_platform/pov.py` aggregates these artifacts into a hashed proof-of-value report with requirement, planned-check, triage, and closure counts. It states its run-root boundary explicitly and does not convert an observed failure into a success claim.

`verification_platform/coverage.py` parses bounded JSON coverage evidence and rejects impossible counts. The seeded run records a functional coverage result of 0/1 alongside its failed assertion, keeping execution status and coverage status distinct.

`verification_platform/generator.py` renders approved plans into a traceable `generated_checks.sv` artifact. Generated assertions retain their requirement IDs and rationale for human review before tool execution.

The benchmark failure IR now hashes and links the full reproducibility set: `spec.md`, RTL, testbench, generated checks, verification plan, simulation log, and VCD waveform. A diagnosis therefore cannot be detached from the exact inputs that produced it.

`verification_platform/uvm.py` provides a deterministic UVM interface, transaction, and agent scaffold from validated signal names. It is deliberately reviewable source until a target UVM library and simulator adapter prove compilation.

`verification_platform/policy.py` enforces human approval for actions that change design intent or closure state, while allowing read-only analysis. This is the control boundary for agentic repair and sign-off workflows.

`verification_platform/claims.py` adds domain-aware evidence gates for the mixed-signal case study. A simulation waveform cannot satisfy a measured-hardware latency claim; each claim declares the evidence kind it requires.

PoV reports can now include these domain-aware claims and show each as `proven` or `unsupported` next to the digital verification metrics.

`verification_platform/repair.py` creates bounded, requirement-linked repair proposals without editing RTL. The seeded enable-guard proposal stays `review_required` until a human approval is supplied, after which a separate retest may be launched.

Approved proposals can now be applied only to a separate copy with an exact single-occurrence precondition. The original RTL remains unchanged, and the copied source becomes the input to a subsequent recorded retest.

An explicit compiler check shows that the generated concurrent SVA is rejected by the installed Icarus version. `verification_platform/sva.py` records that capability failure as an `iverilog-sva` tool run; an SVA-capable simulator is required before these plans can be promoted from reviewable to executable.

The same probe records the installed Verilator result as `verilator-sva`; it also rejects the generated `|=>` properties. Tool capability is therefore a measured adapter result, not an assumption in the planning layer.

`verification_platform/pipeline.py` composes ingestion, planning, SVA generation, and tool execution into one deterministic invocation that persists each stage artifact in a run directory. This is the first agent-facing workflow entry point.

The pipeline passes its generated IR, plan, and SVA files to the provenance ledger as expected artifacts, so the execution record hashes the complete planning-to-tool handoff.

`verification_platform/procedural.py` provides the open-source execution fallback: recognized plans become ordinary clocked SystemVerilog checks using `$display`, which can be compiled by Icarus even when concurrent SVA is unavailable. The seeded benchmark emits `procedural_checks.sv` alongside the SVA artifact.

The generated procedural checker compiles successfully with the installed Icarus toolchain, while the concurrent SVA artifact remains separately labeled as unsupported by that tool. This is the first executable open-source assertion backend.

Execution IDs are now stable for a command and source revision, with an explicit `run_id` override for repeated seeds or regression jobs. Wall-clock duration remains metadata rather than identity, preserving reproducibility across reruns.

`verification_platform/clustering.py` groups repeated failures by observable signal mismatch while preserving their cycles. This supplies the first regression-level measure for duplicate failures collapsed into actionable clusters.

`verification_platform/regression.py` coordinates multiple isolated tool jobs under one evidence root and reports pass, fail, blocked, failure, and cluster counts. It is the initial regression-level PoV harness.

`write_regression_report()` persists those aggregate counts with stable run summaries and a report digest, making regression PoV metrics reproducible after the process exits.

`verification_platform/logic.py` extracts a conservative dependency cone through simple RTL assignments. It supplies focused signal context for debug while leaving complex procedural or generated logic explicitly outside this first parser’s claim boundary.

`verification_platform/waveform.py` now reads VCD declarations and value changes and confirms that a triage value is present in the waveform. The benchmark reports this as `waveform_confirmation`, keeping log-derived failures checked against a signal trace.

`verification_platform/formal.py` adds a Yosys syntax/elaboration preflight adapter. Formal-stage runs are recorded with their own tool identity and provenance, keeping formal readiness separate from simulation pass or failure.

The same adapter now supports bounded Yosys SAT invariants (`yosys_sat_prove`). A passing proof is recorded as a formal tool run with logs and provenance; solver or elaboration failures remain failed or blocked rather than being treated as proof.

`parse_yosys_sat_result()` converts Yosys terminal markers into `proven`, `counterexample`, or `unknown`, establishing the structured formal-result boundary used by counterexample extraction.

`parse_yosys_counterexample()` now extracts Yosys `sat -show` time, signal, decimal, and binary rows from a model-found log. `yosys_sat_prove()` requests the shown signal, and tests verify that an actual failing Yosys run preserves the counterexample in `stdout.log` for downstream triage.

`benchmarks/seeded_counter/retest_benchmark.py` now closes the repair loop: it applies the bounded enable-guard proposal only with explicit approval, writes a separate repaired RTL copy, recompiles and reruns it through recorded Icarus/VVP adapters, and emits a second verification IR plus closure report with all three seeded requirements proven. The original defect source remains unchanged, so the benchmark demonstrates review-gated repair, retest, and reproducible closure rather than silently mutating design collateral.

`verification_platform/mixed_signal.py` adds an explicit AIMC collateral manifest. The checked-in [verification-platform-mixed-signal-manifest.json](../../evidence/aimc-hardware-lab/verification-platform-mixed-signal-manifest.json) hashes simulation, physical-layout, and board-runtime artifacts while requiring separate qualification evidence kinds. It therefore marks simulation evidence as present but leaves physical qualification and measured-hardware latency unsupported, matching the current hardware gate instead of promoting artifact presence into a hardware claim.

`build_pov_report()` can now embed that mixed-signal manifest into the digital run report, preserving one proof-of-value artifact with benchmark closure metrics and the AIMC claim boundary. The embedded manifest remains content-addressed and retains unsupported claim statuses.

`coverage.py` now ranks uncovered coverage items by deterministic gap size and emits a concrete next evidence-producing action. PoV reports include these actions, while keeping them explicitly separate from proof: an uncovered item is a work queue entry until a new run supplies valid evidence.

The seeded benchmark root-cause report now includes the extracted RTL dependency cone. The parser recognizes procedural guard conditions and filters literal suffixes such as `4'd1`, so the faulty counter path shows the absence of `enable` as inspectable evidence rather than returning a misleading literal-derived signal.

Formal model traces now share the simulation triage schema: `counterexample_to_failure()` selects the first violating shown value from a Yosys `sat -show` trace and projects it into the common `Failure` record. This keeps formal and simulation diagnosis compatible while preserving the original formal log as evidence.

`session.py` adds a monotonic, hashed lifecycle ledger for agentic runs. The seeded retest records `created → planned → executed → triaged → repair_review → retested → closed`, with the repair decision attributed to a human approval event. Invalid stage skips are rejected, making workflow state auditable independently of model output.

`capabilities.py` records open-source backend availability as `available` or `blocked`. The seeded run now persists `tool-capabilities.json`, measuring Icarus, Verilator, Yosys, and SBY availability instead of assuming a customer toolchain or silently treating missing UVM/formal infrastructure as executable.

PoV reports now include a toolchain section with the capability inventory and available/blocked counts. A customer pilot can therefore distinguish a verification failure from a backend that was never executable in the captured environment.

The seeded benchmark and approved retest now pass `procedural_checks.sv` into the real Icarus compile command. The generated open-source checker is therefore part of the executable evidence path, while the concurrent SVA artifact remains separately labeled as unsupported by the installed tools.

`benchmarks/seeded_counter/run_end_to_end.py` packages the complete baseline-to-retest workflow behind one command and writes `runs/end-to-end-summary.json`. The summary expects a classified baseline failure followed by a passing approved retest, with links to the triage report, closure report, and session ledger.

The retest now writes its own specification IR, verification plan, functional coverage, and PoV report, embedding the AIMC manifest. The passing digital closure and unsupported physical claims can therefore be reviewed together from the retest run directory.

The retest also regenerates `generated_checks.sv` and `procedural_checks.sv` from its own specification before compiling the repaired RTL. No executable check artifact is borrowed from the baseline run.

The baseline benchmark now uses the recorded `run_command()` adapters for both Icarus compilation and VVP simulation. Its failure IR includes those tool runs, logs, and waveform artifacts, so the initial failure and the approved retest share the same provenance contract.

The one-command benchmark now also runs a bounded Yosys SAT proof against `formal_constant.sv`, records its provenance ledger, and requires `proof_result: proven` for an overall successful workflow. Simulation failure, approved retest, and formal proof are now visible in one reproducible summary.

It also runs `formal_bad.sv` as a controlled negative formal case. The summary records `proof_result: counterexample` and the projected `Failure(cycle=2, signal=q, expected=0, actual=1)`, demonstrating that formal debug enters the same triage schema as simulation failures.

PoV reports now include generation accounting for the SVA, procedural, and UVM artifacts. This shows whether source was emitted, whether the procedural fallback was available for execution, and which generated artifacts remain review-only under the measured tool capabilities.

Generation accounting also includes SHA-256 hashes for every emitted artifact, tying review and execution claims to the exact generated source.

The top-level `end-to-end-summary.json` now carries its own SHA-256 digest over the baseline, retest, formal, and trace-comparison results, giving the complete benchmark outcome a stable integrity marker.

`artifacts.py` adds a run-level content-addressed inventory. The one-command benchmark writes `runs/artifact-manifest.json`, listing every evidence file, byte size, and SHA-256 hash while excluding the manifest itself to avoid recursive identity.

`verify_artifact_manifest()` rechecks the manifest digest, missing files, and per-file hashes after a run is copied or transferred. Evidence bundles now have an explicit post-run integrity check.

The one-command workflow now executes that integrity check before returning success and records the result under `artifact_integrity` in `end-to-end-summary.json`. A tampered or incomplete evidence bundle cannot satisfy the benchmark gate.

PoV reports expose the artifact-manifest verification result when a run-local manifest is present, and explicitly report `manifest missing` otherwise. Integrity status is therefore visible alongside closure and execution metrics.

PoV requirement metrics now include `unplanned`, calculated from ingested requirements minus generated checks. The seeded benchmark reports one unplanned reset requirement, preserving the human-review queue instead of implying complete planning coverage.

The end-to-end summary now reports before/after PoV deltas: proven-requirement count and functional-coverage percentage for the baseline and approved retest. The seeded flow demonstrates a three-requirement proof gain and coverage improvement from 0% to 100%.

PoV execution metrics also aggregate recorded tool duration, providing a reproducible compute-time baseline for pilot comparisons rather than relying on subjective speed claims.

`actions.py` adds a bounded agent next-action policy. PoV reports now recommend triage, backend recovery, human review of unplanned requirements, coverage targeting, or sign-off in a fixed priority order; the policy never authorizes a design-intent change by itself.

`adapter.py` defines a reusable `AdapterSpec` and `execute_adapter()` boundary for customer simulators, formal engines, linters, and coverage tools. Every adapter delegates to the same shell-free runner and expected-artifact gate, so swapping in a customer backend preserves provenance semantics.

`planning_summary()` now records the exact planned requirement IDs and per-requirement reasons for unplanned work. The seeded run persists `planning-summary.json`, giving an agent or reviewer an actionable queue rather than only an aggregate count.

PoV requirement metrics now embed that planning queue, so the report carries both the aggregate gap and the exact human-review items with their reasons.

Closure evaluation now keeps requirements open whenever the IR contains a failed or blocked tool run, even if another run passed and evidence files exist. This prevents stale or mixed-run evidence from promoting a requirement to proven.

The approved retest now persists the same `planning-summary.json` as the baseline path, preserving the reset requirement's human-review status in the passing report.

The baseline benchmark now embeds the AIMC mixed-signal manifest when writing its PoV report, so `run_end_to_end.py` regenerates both baseline and retest reports with the same digital-versus-hardware claim boundary.

`verify_pov_digest()` validates a stored PoV report against its canonical content and rejects post-generation edits. Hashes are now an enforceable integrity gate rather than display metadata.

`run_command()` now blocks a tool run when any declared expected artifact is missing, recording the missing paths in metadata. The baseline benchmark was corrected to place its VVP binary inside the adapter run root, and the full flow continues to pass with complete compile and waveform artifacts.

PoV reports now summarize the verification IR's execution records by tool and status. The report can distinguish a failed verification run, a blocked adapter, and an absent execution record without relying on prose status fields.

The Yosys SAT adapter now records `metadata.proof_result` independently of process status. A successfully executed Yosys command that finds a model is therefore recorded as an executed run with `counterexample`, while a no-model result is recorded as `proven`.

PoV execution metrics now aggregate those formal outcomes as `proof_results`, keeping process health and verification meaning visible in separate fields.

`waveform.assess_vacuity()` checks whether an assertion trigger value occurred in the captured VCD. The seeded baseline records the `enable == 1` hold trigger as `vacuous`, making the missing stimulus explicit rather than allowing an unexercised property to masquerade as coverage or proof.

`rtl.py` adds typed SystemVerilog collateral ingestion for simple module declarations. The seeded run persists `rtl-collateral.json` with hashed source evidence and module port directions, kinds, and ranges, giving agents deterministic interface facts for planning and retrieval.

`retrieval.py` adds a deterministic lexical retrieval index over specification and RTL collateral. Retrieved snippets carry source line, path, and content hash; retrieval is an evidence locator, while typed parsers remain authoritative for widths, protocol facts, and reset semantics. The seeded run persists `retrieval-index.json` as part of its reproducibility set.

`waveform.compare_traces()` compares passing and failing VCD samples for a signal and reports the first value/time divergence or a length mismatch when one run terminates earlier. The one-command seeded summary now includes this comparison as explicit debug evidence.

The UVM scaffold now emits the dependency-ordered interface, transaction, driver, monitor, agent, scoreboard, and environment classes. It remains reviewable source until a UVM-capable simulator is available, but the generator now exposes the complete component chain required for customer-tool compilation.

The versioned specification IR now embeds generated check records and validates every check's `requirement_id` against the ingested requirements. The seeded benchmark persists the two recognized checks directly in `specification-ir.json`; unsupported reset planning remains visible as an unplanned requirement rather than an invented check.

Both baseline and retest runs now emit the dependency-ordered `uvm-counter-agent.sv` scaffold from the typed counter interface. The artifact is included as reviewable generation evidence and remains blocked from execution when the capability inventory lacks a UVM simulator.

## Boundaries and assumptions

The first implementation is simulation- and formal-first. It does not require fabricated silicon or an analog-memory board. Hardware measurements become necessary only for claims about physical analog execution, measured latency, energy, yield, or silicon behavior. The platform should support those measurements later through instrument and board adapters, while keeping simulation, formal, and physical evidence explicitly separate.

The initial implementation target is open source: Icarus and Verilator for simulation and lint, Yosys SAT for bounded formal checks, and lightweight procedural or Python-driven testbenches where a full UVM library is unavailable. The platform may still emit standard SVA and UVM source for review and for later customer-tool execution, but it must label unsupported constructs rather than silently treating generated source as executable.

External papers, product claims, and named commercial systems must be source-checked before being used in customer-facing material. The project itself should rely on reproducible tool outputs and benchmark results rather than unverified literature summaries.
