# AI Hardware Architecture To Working Lab Bridge

This page connects two local repos that are really one body of work.

`/home/mehtama1/git-repo/ai-hardware-analysis` contains the larger analog in-memory AI hardware architecture and a working software prototype. It has the product path, frontend workbench, FastAPI backend, ONNX model import, adapter/evidence system, simulator plan, compiler plan, tool integrations, evidence package, and tapeout-risk pages.

`/home/mehtama1/git-repo/analog-digital-chip-design-eda` contains the working chip-design lab. It turns pieces of that architecture into measurable artifacts: SPICE-style analog measurements, Python error models, transformer-impact checks, Verilog control logic, RTL simulations, synthesis, and OpenLane physical-design runs.

The old repo is the product workbench and architecture map. This repo is the circuit, RTL, and EDA bench.

## The Shared Question

Can foundation-model inference safely spend some of its matrix math on analog in-memory compute?

That question cannot be answered by saying analog multiply is energy efficient. It has to be answered by following the whole chain:

1. Which model operations are repeated enough to justify analog hardware?
2. Which weights can be placed in memory arrays?
3. Which activations can be converted into row voltages without losing too much information?
4. How much error comes from conductance variation, wire drop, programming error, drift, noise, and ADC quantization?
5. Where does that error enter the model?
6. Does it only move hidden state a little, or does it change an attention choice, class choice, token choice, or control action?
7. Can digital logic refuse analog execution when the error is too expensive?
8. Can the resulting controller become real gates and routed geometry?

The architecture repo names this chain. The working lab has started to build it.

## Source Architecture And Prototype In The Old Repo

The main source folder is:

`ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture`

The important source documents and prototype files are:

- `combined-system-end-to-end-workflow.html`: unified review page that orders the old frontend/backend, strategy pages, and this repo's hardware-lab evidence into one workflow.
- `README.md`: trained model to measured inference result path.
- `index.html`: frontend workbench prototype with model-fit, evidence, adapter, package, run-history, and review panels.
- `backend/main.py`: FastAPI backend that exposes model import, graph analysis, quantization, runtime profiling, baseline comparison, package generation, evidence import, claim readiness, and connector readiness endpoints.
- `backend/onnx_analyzer.py`: ONNX graph analysis and operator classification.
- `backend/model_store.py`: persisted models, projects, runs, and packages.
- `backend/adapters.py` and `backend/adapter_runs.py`: local and external-tool adapter registry and execution path.
- `backend/evidence_imports.py`, `backend/evidence_gates.py`, and `backend/claim_readiness.py`: evidence validation, evidence gating, and allowed-claim logic.
- `backend/deployment_package.py`: saved package and archive generation.
- `architecture.md`: frontend and backend workbench design.
- `simulation-to-silicon-first-principles-spec.md`: simulation, calibration, compiler, board, and silicon proof ladder.
- `aihwkit-tool-stack-plan.html`: IBM AIHWKIT role in analog workload simulation.
- `analog-mlir-to-silicon-compiler-plan.html`: compiler path from model operators toward analog execution.
- `analog-mlir-chip-target-roadmap.md`: lowering roadmap for analog compute targets.
- `analog-vs-digital-validation-process.html`: how analog proof differs from mature digital validation.
- `memory-technology-decision-plan.html`: when SRAM, ReRAM, MRAM, or other memory choices change the claim.
- `hardware-tapeout-risk-roadmap.html`: physical risks around converter cost, noise, thermal behavior, chiplets, and tapeout.
- `external-tool-integration-spec.md`: how tools such as AIHWKIT, CrossSim-style layout checks, MLIR, ONNX, TVM, IREE, board runtime, and power measurement should connect.

These files do more than define what a real analog in-memory inference product would need to prove. They already implement the first software slice: a model-fit backend, frontend review surface, local evidence adapters, package archive flow, and claim-readiness logic.

## Working Proofs In This Repo

This repo should now be treated as the hardware-proof extension of that product workbench.

The old backend can say: here is a model, here is the proposed analog/digital placement, here is the evidence still missing, and here is the allowed claim.

This repo can answer: here is the measured analog error model, here is the transformer sensitivity test, here is the generated hardware request, here is the Verilog decision, and here is the physical-design evidence for the controller.

### Analog Error Measurement

Working artifacts:

- `labs/analog/analog-in-memory-foundation-model-hardware/python/analog_nonideality_stack.py`
- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/analog-nonideality-stack.csv`
- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/analog-nonideality-stack.md`

What this proves:

The analog tile is not treated as a perfect matrix multiply. It is treated as a measurement chain. The lab tracks the path from activation code to row voltage, conductance-weighted current, column sum, nonideal drop, drift, noise, ADC code, and final digital residual.

What it does not prove yet:

It is still a local model, not calibrated silicon. It now connects to AIHWKIT and CrossSim through fixture-level simulator adapters, but it does not yet connect to a real PDK-level analog array, measured silicon, or board traces.

### Model Sensitivity

Working artifacts:

- `labs/analog/analog-in-memory-foundation-model-hardware/python/measured_tile_transformer_impact.py`
- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/measured-tile-transformer-impact.csv`
- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/measured-tile-transformer-impact.md`

What this proves:

The same tile error can be cheap in one model location and expensive in another. A fixed projection can tolerate a measured residual. Attention score paths and logit paths are more sensitive because a small numeric movement can change which item is selected.

What it does not prove yet:

It is a toy transformer-impact harness. It is not yet run on a full pretrained model, a full ONNX graph, a real dataset, or a customer workload.

### Digital Referee

Working artifacts:

- `labs/digital/aimc-control-plane-rtl/aimc_error_budget_governor.v`
- `labs/digital/aimc-control-plane-rtl/aimc_model_impact_governor_tb.v`
- `labs/digital/aimc-control-plane-rtl/generated_model_impact_governor_cases.vh`
- `labs/digital/aimc-control-plane-rtl/check_generated_model_impact_governor_trace.py`

What this proves:

The model-impact results are compressed into hardware-sized fields and checked against Verilog. The RTL governor accepts the low-risk analog path and refuses paths where sensitivity makes analog execution unsafe.

What it does not prove yet:

The model-impact governor is checked as a governor block. The next step is to feed these same model-impact rows through the integrated scheduler plus governor, so the service controller itself chooses analog, throttled analog, or digital fallback.

### Physical Digital Implementation

Working artifacts:

- `labs/eda/aimc-scheduler-governor-pipelined-openlane-prep`
- `labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/openlane-5ns-control-reset-fanout20-metrics-summary.md`
- `labs/digital/aimc-control-plane-rtl/aimc_scheduler_governor_pipelined.v`

What this proves:

The digital controller is not only pseudocode. A pipelined scheduler/governor version has been pushed through OpenLane with a 5 ns target and fanout constraint. The latest successful physical result is timing clean, DRC clean, LVS clean, antenna clean, and has no max slew, fanout, or capacitance violations.

What it does not prove yet:

This is an open-source educational flow, not signoff. It does not prove a production tapeout, final power integrity, scan/test insertion, packaging, analog macro integration, or measured silicon.

## Architecture Need To Working Artifact

Model import and workload fit:

- Old repo capability: import a trained ONNX model, analyze its graph, classify operators, estimate boundaries, and generate fit reports through the FastAPI backend and frontend.
- Done: the restored backend now emits a `hardware_placement` package artifact from the analyzed model graph. The current lab imports that artifact with `scripts/import_backend_hardware_placement.py`.
- Current working proof: package `pkg-e931662a01293df2` produces 5 operator rows, 2 analog candidates, 4 converter boundaries, and 3 fallback points. Those rows are appended to `model-impact-governor-requests.csv`, so the RTL governor sees both local transformer cases and backend-derived placement cases.
- Still missing: this is not yet a broad ONNX compiler. The live connection proves the first model-graph-to-lab path, not full coverage of arbitrary customer models.

First-principles page: `backend-hardware-placement-first-principles.md`.

AIHWKIT-style analog simulation:

- Old architecture need: simulate analog device noise, programming error, drift, update behavior, and converter precision against model accuracy.
- Done: the local analog nonideality stack and transformer-impact harness produce the residual and model-sensitivity rows used by the governor.
- Done: AIHWKIT is installed in the optional simulator environment and is part of the executable bridge. It runs small and model-shaped replay fixtures and writes strict simulator payloads.
- Still missing: stronger AIHWKIT agreement on larger model slices. The current larger AIHWKIT replays run but exceed the local residual threshold, so the guarded importer rejects them from positive simulator claims.

Adapter boundary: `aihwkit-crosssim-adapter-boundary.md`.

CrossSim-style layout risk:

- Old architecture need: estimate crossbar layout risk from wire resistance, array size, bit slicing, read noise, programming variation, and ADC range.
- Done: row-drop, converter-boundary, and tile operating-point measurements exist inside the analog lab.
- Done: CrossSim is installed in the optional simulator environment and is part of the executable bridge. It runs the same fixture family and writes strict simulator payloads that pass the guarded importer when their residual is inside the accepted boundary.
- Still missing: a richer layout-risk adapter that exposes tile size, wire assumptions, column current range, ADC range, bit slicing, and expected residual as a backend-importable physical-layout risk record.

Adapter boundary: `aihwkit-crosssim-adapter-boundary.md`.

Compiler and MLIR path:

- Old architecture need: lower model operations through an analog-aware compiler path, eventually MLIR, TVM, IREE, ONNX, or analog-MLIR.
- Done: backend hardware placement now emits operator decisions, converter boundaries, sensitivity classes, fallback points, and governor fields. The lab converts those rows into governor requests.
- Partial: this is a placement artifact and governor handoff, not a real MLIR lowering path.
- Still missing: a compiler-like pass that reads a tiny operator graph and emits an analog service schedule plus digital fallback schedule, then grows toward MLIR/TVM/IREE only after the small pass is checkable.

Runtime fallback:

- Old architecture need: runtime must choose analog only when error, latency, power, and sensitivity budgets allow it.
- Done: model-impact request generation produces 10 governor rows, including 5 backend-derived placement rows. The generated model-impact RTL checker passes all 10 cases.
- Partial: the integrated scheduler/governor trace exists and passes, but it is still not fully driven by the same backend-derived placement rows.
- Still missing: one unified integrated trace where backend placement, analog residual, model sensitivity, tile health, queue pressure, and cumulative error drive the full service controller.

Digital layout and EDA:

- Old architecture need: digital support logic must be physically realizable and not just a high-level policy.
- Done: Yosys synthesis reports and OpenLane prep/readiness checks exist for several AIMC control blocks. The pipelined scheduler/governor has recorded physical-flow evidence.
- Partial: the backend evidence export includes local OpenLane-derived power/thermal context, but this remains estimated evidence, not measured hardware power.
- Still missing: connect the generated model-impact controller cases directly to the latest physical-design report and document how the control policy changes area, timing, routing, and timing margin.

Evidence package:

- Old repo capability: frontend and backend already produce deployment packages, evidence gates, measurement evidence contracts, imported evidence records, review reports, decision reports, connector readiness, and claim-readiness outputs.
- Done: `scripts/export_aimc_hardware_lab_evidence.py` emits six backend-compatible evidence records, and the old backend imports them through `POST /deployment-packages/{package_id}/hardware-lab-evidence`.
- Current working proof: `scripts/prove_cross_repo_aimc_loop.py` checks backend health, backend placement, lab import, governor generation, RTL trace, AIHWKIT/CrossSim adapter availability, evidence export, backend import, and claim readiness. It writes `evidence/aimc-hardware-lab/cross-repo-loop-proof.md` and `.json`.
- Still missing: measured board latency, measured energy, calibrated silicon, analog macro layout, package reliability, and signoff-quality tapeout evidence.

Board and power measurement:

- Old architecture need: prove that a package ran on a named board and that runtime, voltage/current samples, thermal state, workload, and host-overhead boundary all refer to the same run window.
- Done: the current lab exports local `board_runtime` and `power_thermal` evidence records, and the backend imports them into claim readiness.
- Partial: the records are useful because they carry RTL, synthesis, OpenLane, and local estimate context, but they are not measured board or meter traces.
- Still missing: a real board or instrumented runtime trace, synchronized power measurement, measured supply voltage/current samples, thermal setup, repeated-run latency distribution, and uncertainty statement.

Measurement boundary: `board-and-power-measurement-boundary.md`.

## The Important Conceptual Connection

Analog in-memory compute is not a replacement for digital compute.

It is a way to spend physical error in exchange for lower data movement and lower multiply cost.

That trade only works when the digital system has a contract:

- this operation is allowed to be approximate
- this layer can absorb the residual
- this tile is healthy enough today
- this ADC range is not saturated
- this row voltage is inside the safe range
- this accumulated model error is still below the budget
- this output does not decide a brittle choice
- this runtime has a fallback path when the contract is broken

The old architecture repo describes and partially implements that contract as a product and software platform. The current lab turns parts of the contract into measurements, RTL, and EDA artifacts.

## Next Builds That Connect The Repos

### 1. Source Bridge Page

Keep this permanent page current as the map between old architecture specs, frontend/backend prototype, package/evidence flow, and working lab artifacts.

Done means:

- every major old architecture requirement has a matching current artifact or a clear missing build
- the old frontend/backend implementation is named as a real existing prototype, not treated as only theoretical writing
- the page is rendered in the local site
- stale language saying the old repo is missing is removed

Current status: done for the first connected proof slice. Keep it updated as AIHWKIT, CrossSim-style layout risk, and board/power work become real artifacts.

### 2. AIHWKIT Comparison Lab

Add a small optional lab that runs a tiny PyTorch network through IBM AIHWKIT if installed, or records a clear skipped state if it is not installed.

Done means:

- the lab explains the same weight, activation, noise, drift, and ADC questions in the language used by our local simulator
- the output has a comparison table between local residual and AIHWKIT-style residual
- the bridge checker records pass or intentional skip

### 3. Compiler Placement Mini-Pass

Extend the current backend `hardware_placement` handoff into a tiny compiler-like placement pass.

Done means:

- the script reads operators such as linear projection, attention score, softmax, MLP projection, normalization, and logits
- it emits analog candidates, digital-only operators, converter boundaries, partial-sum boundaries, and fallback points
- the output feeds the scheduler/governor trace
- the generated report names what is placement, what is sensitivity evidence, and what is still only a scheduling assumption

### 4. Integrated Runtime Controller

Extend the current model-impact governor work so backend placement rows and measured analog rows drive the integrated scheduler plus governor.

Done means:

- the same analog/model CSV rows generate integrated Verilog cases
- RTL proves analog is allowed only for the fixed-projection case
- stressed projection, attention-score, and logits cases fall back to digital
- the lab page explains the decision without vague claims

### 5. Evidence Ledger

Keep one evidence ledger for the analog AI hardware stack, shaped so the old FastAPI backend can ingest it as package evidence.

Done means:

- every claim is marked measured, simulated, synthesized, physically routed, estimated, skipped, or blocked
- every claim points to a command and output file
- every unsupported claim has a plain next action
- the ledger can be exported as JSON records compatible with the old repo's evidence import path
- the cross-repo proof report is linked as the executable check of the ledger

## What This Lets Us Say

Allowed claim:

This repo contains a working educational slice of an analog in-memory foundation-model accelerator stack. It measures local analog tile error, tests where that error matters in a transformer-style path, converts the model impact into hardware-sized control fields, checks those fields against Verilog RTL, and has pushed a related scheduler/governor controller through an OpenLane physical-design flow.

Not allowed yet:

This does not prove a production analog foundation-model chip. It does not yet include calibrated silicon, a full model compiler, measured AIHWKIT/CrossSim agreement, analog macro layout, board runtime traces, power-meter traces, package reliability, or signoff-quality tapeout evidence.
