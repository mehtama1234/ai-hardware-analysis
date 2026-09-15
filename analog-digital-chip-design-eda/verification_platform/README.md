# Verification platform primitives

This package is the first implementation slice of the evidence-backed AI verification platform. It is deterministic infrastructure for agent proposals; it does not make an LLM claim or mark closure without tool evidence.

The main entry points are:

- `ingest_markdown()` — parse explicit `REQ-ID: text` requirements and hash the source;
- `build_collateral_package()` / `verify_collateral_package()` — create and independently verify a typed intake manifest for specifications, RTL, testbenches, reference models, register specs, protocol plans, and constraints; structured entities retain source digests, are reparsed during verification, and conflicts, entity drift, invalid source records, or ready/blocked status inconsistency block the package;
- Register-spec collateral records also retain the canonical normalized-IR schema and digest, which are independently recomputed during package verification.
- `plan_ir()` and `write_sva_module()` — produce conservative, traceable SVA plans and source;
- `proposal_from_agent_payload()` — admit model-suggested SVA only after revision, syntax, and structural signal-scope validation;
- `invoke_assertion_backend()` — invoke the configured local or OpenAI-compatible backend for `generate_assertion` and route its raw response through that admission gate;
- The top-level runner then performs a same-run Verilator frontend check and records lowering/compile feedback; this is validation evidence, not a formal proof;
- `run_pipeline()` — persist ingestion, planning, generation, and tool execution in one run root;
- The explicit SVA lowering boundary supports scalar compound Boolean implications (`&&`/`||`) with overlapped and one-cycle-delayed timing, while nested or otherwise unsupported expressions remain visibly blocked;
- `run_command()` — execute a tool without a shell and record logs, status, and artifact hashes; with `VERIFICATION_EXECUTION_SANDBOX=isolated` it launches Linux tools in private user, PID, mount, and network namespaces;
- `run_four_workstream_pipeline()` — coordinate specification planning, Icarus scheduling checks, Verilator lint, structural extraction, and protocol-sequence compilation with checkpointed evidence;
- Every orchestrated run emits `four-workstream-tier-evidence.json`, a six-tier machine-readable inventory covering lint/policy, compiled simulation, block/protocol regression, formal/debug, SVM, and optimization/release inputs; tier status is descriptive evidence and does not bypass closure or human approval.
- The CLI options `--collateral-root` and repeated `--collateral-entry KIND PATH` attach the typed collateral intake to the same run; a blocked intake blocks planning and a ready package is included in the planning checkpoint.
- The CLI options `--agent-team-input` and `--agent-team-backend` run an explicit bounded role sequence with shared evidence and prior validated handoffs, writing `agents/agent-team-result.json`; role or evidence failures block the planning checkpoint.
- The CLI option `--assertion-agent-backend local` or `openai_compatible` invokes assertion generation from the same run’s plan and RTL-derived signal inventory;
- The CLI option `--protocol-require-generated-sequence` makes executable protocol evidence fail closed unless every no-shell execution command contains the exact generated sequence path; the Colab demo enables this binding gate.
- Assertion-agent execution covers every planned requirement in a batch artifact. If the installed SVA frontend rejects a supported operator, the explicit lowered checker is compiled separately and the fallback is recorded;
- Its optional `agent_backend="local"` or `"openai_compatible"` path sends only the structured debug package to a validated diagnosis agent; model output remains review-only and cannot assert closure;
- Its optional `repair_agent_backend="local"` or `"openai_compatible"` path receives the bounded replay-slice context and can return a source-revision- and evidence-bound, exact-text review-only patch candidate after diagnosis; it does not mutate RTL, apply a patch, or claim closure;
- `parse_failure()`, `signal_values()`, and `dependency_cone()` — extract focused debug evidence;
- `build_replay_slice()` — create a bounded, RTL-digest-bound replay context; and
- `extract_structural_ir()` / `run_functional_equivalence()` — extract Yosys structural context and require an actual solver proof before calling two RTL tops equivalent;
- `generate_hierarchical_filtered_dut(..., module_targets=...)` — optionally reduce supported leaf-module bodies within a retained static hierarchy; multi-statement lines, child-containing targets, and unsupported constructs block, and callers must run the hierarchical Yosys equivalence gate;
- `align_signals()` — produce deterministic one-to-one cross-language matches while recording the individual name, trace, and structural-neighbor score components used for each match;
- `bind_frontier_to_causal_graph()` — bind the first divergent waveform event to incoming structural causal edges and their RTL source locations; this is review evidence, not an automatic root-cause claim;
- The orchestrator exposes that binding status and source-location evidence in its debug result, and the Colab/CI path checks that the binding is available.
- `align_cdfg_signals()` — derive structural neighbors from reference/RTL CDFG artifacts, perform the same conservative one-to-one alignment, and persist CDFG digests, counts, score components, and claim boundaries;
- The provider-free Colab reference input exercises this alignment path with a checked-in golden/RTL CDFG and cycle traces; alignment availability does not claim semantic equivalence.
- The four-workstream structural stage also emits `parser-cdfg.json`, a Yosys-elaborated signal/cell connectivity graph with source and tool provenance;
- `evaluate_closure()` and `build_pov_report()` — enforce evidence gates and summarize pilot metrics;
- `yosys_sat_prove()` — run bounded SAT invariants; and
- `run_yosys_assertion_proof()` — run a formal top with `-prove-asserts` and classify bounded results as proven, counterexample, unknown, or blocked with hash-bound provenance; and
- `run_verilator_compiled_simulation()` — compile RTL and an explicit C++ harness, execute the binary, and require a runtime pass marker; and
- The CLI option `--compiled-sim-rtl` may select a separate clean/reference RTL source set for the compiled-simulation tier while primary RTL remains under formal/debug analysis; both source sets are hashed in their own evidence records.
- `run_synthesizable_checker()` — compile a synthesizable reference checker with RTL and a deterministic harness, require a clean pass marker, and block on an injected mismatch; it also records host-readable cycle/actual/expected mismatch records for replay handoff and optionally parses `SVM_CYCLES cycles=N` into host-observed throughput; this is SVM compile/run evidence, not FPGA timing or utilization evidence; and
- The CLI option `--svm-rtl` may select a clean/reference RTL source set for the SVM tier while the primary RTL remains the formal/debug target; the SVM checker, harness, and selected sources are independently hashed.
- `probe_verilator_options()` — test optional Verilator flags such as `--timing` and persist available/unsupported capability evidence before scheduling timing experiments; and
- `probe_verilator_capability_matrix()` — test requested Verilator flags against a real RTL lint invocation and fail closed when any requested option is unsupported; and
- The CLI option `--scheduling-regression-source` attaches a runtime time-zero fixture. Its result distinguishes normal completion, test failure, timeout/deadlock, premature time-zero termination, and missing stimulus, and non-passing outcomes block the run.
- `run_cooperative_scheduler()` provides deterministic reference semantics for cycle waits, event waits, time-zero progress, deadlock, and zero-cycle livelock; it is scheduler-model evidence, not a claim of Verilator/UVM/C++20 support.
- `run_cpp_coroutine_probe()` compiles and runs a real C++20 `<coroutine>` fixture with bounded evidence; this separates host-language coroutine capability from the installed Verilator version and does not claim UVM support.
- `run_cpp_coroutine_probe(..., required_markers=...)` can additionally require ordered time-zero and event-progress markers, providing executable cooperative-scheduling evidence rather than compiler support alone; it still does not claim Verilator/UVM behavior.
- `probe_uvm_runtime()` records the presence of an explicit `uvm_pkg.sv` and simulator executable with a self-digested, fail-closed capability artifact; scaffold generation or package presence is not treated as UVM runtime proof.
- `generate_uvm_agent()` emits the standard `uvm_macros.svh` include and `uvm_pkg::*` import so the scaffold has explicit package dependencies when a UVM-capable simulator is supplied.
- `run_uvm_compile()` validates those capabilities, executes a caller-supplied simulator command without a shell, and records compile evidence separately from UVM scheduling, functional coverage, and runtime-compatibility claims.
- The CLI options `--uvm-source`, `--uvm-root`, and `--uvm-compile-command COMMAND.json` attach that compile evidence to the same four-workstream run; the command JSON must be a list of arguments and is never interpreted by a shell.
- `load_openlane_metrics()` normalizes supported QoR column aliases and rejects conflicting duplicate aliases before metrics enter optimization state.
- Optimization recommendations carry canonical candidate-configuration and exact-RTL-source digests; measured results that provide either digest must match before entering persistent optimization history. Persisted runs also retain a relative metrics-artifact path beside its digest.
- The CLI options `--svm-checker-source`, `--svm-harness`, and `--svm-harness-top` attach an optional synthesizable-checker stage; its result is included in the hash-verified planning evidence.
- `scripts/run_time_zero_regression_matrix.py` runs the checked-in five-case scheduling corpus and uploads its machine-readable classifications in CI.
- The CLI options `--assertion-formal-source`, `--assertion-formal-top`, and `--assertion-formal-sequence` attach an explicit formal-model bundle to a four-workstream run. A counterexample is retained as failure evidence and is never converted into a closure claim.
- `authorize()` / `apply_to_copy()` — require human approval for intent-changing repairs; and
- `build_repair_patch_candidate()` — validate an agent-supplied exact-text `before`/`after` edit against the current source digest and unique-match precondition without applying it; and
- `run_approved_repair_retest()` — apply an approved exact-text repair only to a copy, rerun the identical command scope, and persist hash-bound retest evidence. A passing retest also requires the canonical source hash to remain unchanged after the command completes.
- The CLI option `--approved-repair` connects that API to the four-workstream run. It requires an explicit `human_approved` flag, keeps the destination inside the run root, and records the retest under the debug checkpoint; it never mutates canonical RTL. With `proposal_from_agent: true`, the approved retest consumes the validated repair-agent patch candidate from the same run instead of duplicating patch text in the approval request.
- `scripts/run_four_workstream_repair_matrix.py` first creates a fresh Icarus baseline for each of the four checked-in seeded counter, arbiter, decoder, and FIFO failures, then runs the repair contract; its per-design candidate/retest references and self-digest make the matrix auditable, while its claim remains bounded to copy-only retest evidence.
- `scripts/run_four_workstream_assertion_matrix.py` exercises the local specification-grounded assertion-agent contract across those four seeded designs and requires every planned proposal to pass the explicit lowering/compiler gate; its self-digested report is admission and compilation evidence, not formal proof.
- `load_systemrdl_spec()` — parse the supported, fail-closed SystemRDL subset into the same register IR used by the JSON and IP-XACT frontends.
- The IP-XACT frontend accepts the standard omitted-field-access case as read/write while continuing to reject unknown explicit access policies.
- `verify_register_bundle()` — verify artifact hashes and exact register/field offsets, widths, resets, access policies, and generated semantics across RTL, C headers, RAL metadata, and scoreboard output; it also rejects artifact paths escaping the bundle; rehashing a semantically changed artifact does not bypass this gate.

`scripts/generate_register_bundle.py` accepts `--format systemrdl` (or detects
`.rdl`/`.systemrdl`) and emits the same hash-verified RTL, C-header, RAL, and
scoreboard bundle.

The seeded executable example is in `../benchmarks/seeded_counter`. It intentionally fails, which verifies that the platform preserves failure evidence instead of reporting a false pass.

After the six implementation stages are verified, `scripts/release_four_workstream_pipeline.py`
can create a release manifest. It requires a reviewer, an approval note, and
the explicit `--approve` flag; release is never inferred from passing tests.

The provider-free reference path is also wired into
`.github/workflows/verification-pilot.yml`: CI runs the platform tests, the
Colab-compatible six-stage demo, checkpoint resume auditing, and uploads the
evidence. CI does not promote a release.

Every four-workstream run also emits `four-workstream-evidence-manifest.json`,
a content-addressed inventory of the generated evidence. The workflow
checkpoint records that manifest so the later human-approved release can
verify the same evidence set; checkpoint resume also rechecks the hashes inside
the manifest, including recorded file sizes, safe relative paths, and
unlisted-file detection. The manifest explicitly records only intentional
exclusions such as the mutable checkpoint and run summary.

The four-workstream CLI accepts optional debug and optimization inputs. A debug
JSON object supplies `waveform`, `rtl`, `signal`, `observed`, `reference`,
`for_evidence`, and `against_evidence`. It may also supply
`filtered_dut_output` and, for hierarchy-preserving reconstruction,
`filtered_dut_top`; the orchestrator emits the filtered source and requires a
Yosys equivalence result before accepting it. It may also supply
`reference_cdfg`, `rtl_cdfg`, `reference_traces`, and `rtl_traces`; the
orchestrator writes a CDFG-derived alignment artifact and marks ambiguous or
unresolved matches as review-required. An optimization JSON file
supplies a list of predicted candidates. Both outputs remain reviewable and
hash-bound. Optimization state can be persisted and reloaded only when its
content digest, Pareto frontier, and measured-run schema agree; measured
results can be atomically appended, so stale agent recommendations cannot
overwrite newer history. The CLI can also accept one explicit
`--optimization-measurement` JSON object after proposal ranking to record a
proxy or full observation in the same source-bound state.
Each recorded observation may also carry the EDA tool, source digest, and
configuration digest used to produce its metrics. Direct proxy/full command
execution additionally returns the SHA-256 of `metrics.json`, which can be
stored in the optimization history.

The specification planner also supports explicit Boolean requirements such as
`valid implies ready` and `req is high and then ack is high on the next cycle`;
it preserves the named identifiers and emits same-cycle (`|->`) or next-cycle
(`|=>`) SVA accordingly. It also supports bounded fixed-cycle responses such
as `req is high and ack is high 3 cycles later`, emitting `req |-> ##3 ack`
for explicit history-register lowering. More ambiguous temporal wording
remains unplanned for human review.

One explicit compound antecedent is also supported: `valid and ready implies
accepted` emits `(valid && ready) |-> accepted`, while `valid or ready requires
accepted` emits `(valid || ready) |-> accepted`. Nested or ambiguous expressions
remain blocked for review.

Fixed repetition is also supported for requirements such as `req stays high
for 3 consecutive cycles and resp is high afterwards`; this emits
`req[*3] |-> resp` and uses the existing bounded repetition counter lowering.

Bounded hold-until wording is supported for requirements such as `req remains
high until ack is high within 3 cycles`; it emits a bounded sequence and lowers
it to an explicit pending-state register and deadline counter. Bounds above
16 cycles remain blocked for review.

Coverage-gap proposals can be supplied with `--protocol-coverage-gaps`. They
are validated and deterministically appended to the protocol plan before
sequence generation; the augmented plan is recorded as reviewable evidence.
An observed report can be supplied with `--protocol-coverage-report`; it is
copied into the run, parsed under the coverage schema, and converted into a
hashable gap-ranking artifact for the next proposal iteration. The option may
be repeated with reports in measurement order; the pipeline records a
monotonic `protocol/coverage-convergence.json` trajectory and marks it
`converged` only when the final report reaches its declared total.

The CLI option `--protocol-execution-command COMMAND.json` runs a
caller-supplied no-shell command against the generated sequence and requires
its `PROTOCOL_SEQUENCE_COVERAGE covered=N total=M` marker. This records
executable-sequence progress, not DUT functional coverage or protocol
correctness proof. Repeating the option records an ordered executable-run
convergence trajectory and requires monotonic progress to a complete final
sequence.

When assertion generation is enabled, that ranking artifact is included in
the assertion-agent evidence and request context. It guides proposal choice
but does not count as coverage proof.

Assertion admission is specification-grounded: model payloads containing RTL
text, implementation context, or waveform data are rejected. The agent may
resolve names from the declared structural signal set, but cannot introduce
functional identifiers outside that set.

The structural stage can also emit a connected functional context for selected
parser-CDFG targets with repeated `--structural-partition-target` options. The
result is written to `structural/functional-cdfg-partition.json`, is bound to
the parser-CDFG digest, and is blocked when the dependency cone exceeds its
bounded size. It is agent context only; functional equivalence still requires
an explicit solver run.

When bounded multi-agent requests are enabled, the resulting team artifact is
added to downstream diagnosis, repair, and assertion-agent evidence, and its
team digest is recorded in each downstream result. The bounded validated role
handoffs are also passed into those requests, with their count recorded for
traceability.

Logic-aware debug packages independently validate causal-graph schema, node
and edge references, temporal ordering, acyclicity, and the graph digest
before producing a diagnosis. Invalid causal context is blocked.

## Execution-in-the-loop LLM agent

`../scripts/run_llm_agent_benchmark.py` runs the 11-case reference corpus through typed, evidence-bound proposals, deterministic checker execution, and adversarial review. Use `VERIFICATION_LLM_BATCH_COMMAND` for a resident local/open model worker; `../scripts/mock_llm_backend.py` is a transport fixture and `../scripts/hf_llm_batch_backend.py` serves the cached Hugging Face model. The real-model gate is `../scripts/verify_llm_model_evaluation.py`. Fixture results validate the harness only; model quality requires a real model artifact that passes every gate.
