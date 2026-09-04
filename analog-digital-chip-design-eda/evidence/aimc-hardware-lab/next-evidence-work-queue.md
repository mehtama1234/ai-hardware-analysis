# Next AIMC Evidence Work Queue

This file is generated from the current AIMC system state.

- package: `pkg-e931662a01293df2`
- proof status: `PASS`
- supported lab claims: `3`
- needs-review lab claims: `2`
- production claim: `blocked`

## E1. Larger real-model ONNX simulator slice

- claim target: strengthen C4 and residual-aware placement
- status: local_fixture_selected
- why next: The current best local fixture is deep-transformer-mlp-stack.onnx with 12 fixed-weight MatMul rows. The next stronger step is replacing that fixture with a real uploaded or imported model slice.
- object: one uploaded ONNX slice with fixed-weight MatMul rows, digital support ops, real initializer weights, and a digital reference output
- method: use the selected local ONNX fixture as the current rehearsal path, then rerun the same extractor, simulator exporters, and guarded importer on a real uploaded model slice

Acceptance evidence:

- ONNX fixture inventory names the selected current local fixture and fixed-weight MatMul count
- strict AIHWKIT or CrossSim payload exists for the larger ONNX slice
- payload names target object, device assumptions, array assumptions, ADC bits, DAC bits, temperature boundary, and voltage boundary
- guarded importer accepts the payload or records a threshold-fail rejection
- residual-aware placement records source policy fixed_weight_matmul_family_match against package pkg-e931662a01293df2

Blocked until: not blocked locally; stronger proof waits for a real uploaded or imported model slice

Refused claim: does not prove full foundation-model accuracy, measured board latency, measured energy, calibrated silicon, or production readiness

## E2. AIHWKIT positive residual mapping

- claim target: turn AIHWKIT from run evidence into positive simulator evidence where justified
- status: post_layout_candidate_gate_chain_passed_waiting_for_real_values
- why next: The local converter handoff is complete, the one-command submission path exists, preflight can separate shape mistakes from missing files, and a concrete candidate workspace now exists. The candidate transition chain is now proven: the progress gate distinguishes scaffold from complete package, the preflight gate rejects the scaffold and accepts a complete temporary package, and the submission gate rejects the scaffold while writing complete temporary output only outside canonical accepted evidence. The one-command readiness runner currently reports candidate_not_ready_for_strict_submission with 22 preflight issues, so it is the command to rerun after real files and values are filled. The workspace audit still reports 29 placeholder fields and 3 missing or unresolved files. The fill checklist turns those gaps into 32 exact edit items across area, break_even, energy, extraction, files, identity, latency, noise, provenance, simulation. The candidate identity initializer is identity_initializer_ready: it can stamp one shared run id and file names, passes identity validation, does not touch the source scaffold, and leaves strict validation blocked until template status and real values are replaced. The real-candidate builder command now gives the handoff a direct path from existing extracted files plus numeric converter terms into the candidate payload before preview or submission. The submission preview is blocked_before_submission with 22 strict issues and would_write_accepted_evidence=False, so accepted evidence is still protected before the real package is filled. The generated real-run recipe has 9 ordered steps, and the coverage audit reports 32/32 checklist fields covered with 0 uncovered payload blocker fields. The next proof is to work through that checklist: replace the scaffold with a real extracted netlist, real model files, a source break-even rerun artifact, and numeric post-layout simulation or measured silicon values. Only after that should `python3 scripts/run_converter_post_layout_candidate_readiness.py` run cleanly and allow the strict submission command to write accepted evidence.
- object: the same fixed-weight MatMul family currently represented by the analog-allowed rows
- method: adjust mapping, scaling, calibration, converter circuit assumptions, sharing policy, or device assumptions outside the guarded claim path, then rerun held-out payloads without relaxing the importer threshold

Acceptance evidence:

- AIHWKIT residual diagnostic ranks worst rows before any threshold or mapping change
- AIHWKIT ideal-forward mapping proof shows shape and transpose correctness before noisy forward tuning
- AIHWKIT forward-setting sweep names the passing settings and their max residuals
- AIHWKIT physical-setting review compares the passing setting to the current tile ADC/DAC boundary
- AIHWKIT current-tile replay measures the same rows under the existing 4-bit DAC and 6-bit ADC boundary
- AIHWKIT converter upgrade target records the 10-bit input, 12-bit output, six-bit input gap, and six-bit output gap
- AIHWKIT converter cost model estimates energy and comparison cost for the stronger converter boundary
- AIHWKIT target noise sensitivity records the highest all-pass nonzero output-noise setting
- AIHWKIT converter break-even records the rows, sharing, array-saving, and digital-fallback assumptions needed before the target can beat digital
- converter circuit evidence contract records the ADC/DAC energy, latency, noise, area, and sharing fields needed to replace the break-even assumptions
- local converter circuit estimate fills that contract with planning numbers while staying not claim-ready
- converter circuit-simulation estimate narrows the target with explicit settling, quantization, noise, latency, energy, area-proxy, and sharing terms while staying not replacement-ready
- converter SPICE handoff spec defines row-DAC settling, SAR readout, shared-converter loading, and energy-accounting testbenches
- row-DAC settling SPICE evidence passes the simple 10-bit row-driver load against the half-LSB settling rule
- SAR readout SPICE evidence passes the simple 12-bit sampled-readout load against the half-LSB decision rule
- shared converter loading SPICE evidence passes the simple muxed readout load against the half-LSB decision rule
- converter supply-energy SPICE evidence records positive integrated row-drive, ADC-reference, and mux energy on a named rail
- converter post-layout readiness names the extracted parasitic, energy, latency, noise, area, sharing, and break-even rerun fields required before replacement
- converter post-layout evidence contract defines the importable payload shape and keeps the placeholder not claim-ready
- converter post-layout payload validator rejects the placeholder and waits for a real extracted payload
- converter post-layout break-even rerun path rejects non-evidence inputs and waits for a validator-passing payload
- converter post-layout strict intake rejects shape-correct payloads whose referenced files are missing
- converter post-layout positive path proves strict validation and rerun can pass with temporary synthetic files
- converter post-layout submission path provides one command for strict validation, break-even rerun, and submission report writing
- converter real payload package names the required payload, netlist, model files, and rerun artifact
- converter payload preflight reports missing-file payloads as not ready and complete temporary payloads as ready without accepted evidence
- converter candidate workspace provides payload, netlist, models, and rerun staging folders while rejecting the default scaffold
- converter candidate workspace audit reports the scaffold placeholder count and missing file count before preflight
- converter candidate fill checklist turns the audit into exact field and file edits before preflight
- converter candidate gate chain proves progress, preflight, and strict submission transitions without persisting canonical accepted evidence
- converter candidate readiness runner gives one command for audit, checklist, progress, and preflight before strict submission
- AIHWKIT larger or calibrated payload reports accuracy_impact.pass true
- guarded importer accepts the AIHWKIT payload without --expect-reject
- current-state summary records at least one larger AIHWKIT outcome as wrote_payload without threshold_fail
- allowed rows remain explicit: dense1.matmul, dense2.matmul

Blocked until: not blocked locally; run_converter_post_layout_candidate_readiness.py is ready and now needs real netlist/model/rerun files and numeric post-layout simulation or measured silicon values

Refused claim: does not allow threshold-fail AIHWKIT output to support positive analog placement

## E3. CrossSim layout-risk adapter

- claim target: separate array-layout risk from model-level simulator residual
- status: supported
- why next: The first local layout-risk adapter exists and covers 2 CrossSim-backed analog rows. The next upgrade is stronger physical evidence: extracted parasitics or a fuller crossbar simulation flow.
- object: one analog tile candidate with row count, column count, conductance range, bit slicing, DAC precision, ADC range, wire assumptions, and column-current range
- method: keep the current generated layout-risk record as the local review boundary, then replace local estimates with extracted macro parasitics or a stronger crossbar flow

Acceptance evidence:

- layout-risk JSON names array size, wire assumptions, ADC range, DAC precision, bit slicing, and column-current range
- record links back to residual-aware placement source
- record preserves accepted source deep_transformer_mlp_stack
- frontend and current-state summary refuse to treat it as analog macro signoff

Blocked until: not blocked locally; stronger proof waits for extracted macro parasitics or fuller crossbar simulation

Refused claim: does not prove full analog macro layout, extraction, DRC/LVS signoff, or silicon behavior

## E4. Measured board runtime trace

- claim target: upgrade C2 from needs review to supported
- status: open
- why next: The current runtime evidence is local RTL/runtime behavior. Measured latency needs a real board or instrumented runtime trace.
- object: one board or instrumented runtime execution of the same package and workload
- method: record package ID, workload ID, board ID, board revision, runtime version, runtime trace ID, start/end timestamps, fallback events, repeated runs, p50, p95, and host-overhead boundary

Acceptance evidence:

- measured board runtime payload passes /evidence/validate-measured
- local board ID and local/not-measured provenance are absent
- claim readiness moves C2 to supported for the exact setup
- C3 remains needs review unless matching measured power is attached

Blocked until: real board or stronger instrumented runtime source is available

Refused claim: does not prove measured energy, measured power, calibrated silicon, production readiness, or another board

## E5. Synchronized measured power trace

- claim target: upgrade C3 from needs review to supported
- status: open
- why next: Energy is voltage times current over the same runtime window. A measured power artifact is not enough if it describes a different run.
- object: meter-backed voltage/current samples for the same package, workload, board, runtime trace ID, and run window as the runtime trace
- method: record meter, measured rail, sampling rate, voltage/current samples, integration timestamps, energy, average power, peak power, thermal samples, repeated-run count, and host-overhead boundary

Acceptance evidence:

- measured power payload passes /evidence/validate-measured
- runtime and power records share runtime trace ID, package ID, workload ID, board ID, start time, and end time
- claim readiness moves C3 to supported
- mismatched runtime_trace_id still keeps C3 needs review in regression tests

Blocked until: meter or instrumented power source is available for the same runtime trace

Refused claim: does not prove production power, another workload, another temperature, or signoff energy
