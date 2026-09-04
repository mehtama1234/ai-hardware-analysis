# AIMC Evidence Ledger

This ledger lists the current hardware-lab evidence for the analog in-memory compute workbench.

It is the bridge between the hardware repo and the old frontend/backend workbench. The current exporter turns the main rows into JSON evidence that the old backend can import into a deployment package.

The first export now exists at:

- `evidence/aimc-hardware-lab/manifest.json`
- `evidence/aimc-hardware-lab/import-batch.json`
- `evidence/aimc-hardware-lab/compiler_mapping.json`
- `evidence/aimc-hardware-lab/analog_error_simulation.json`
- `evidence/aimc-hardware-lab/board_runtime.json`
- `evidence/aimc-hardware-lab/power_thermal.json`
- `evidence/aimc-hardware-lab/task_accuracy.json`

## Evidence To Claim Map

The backend claim IDs are:

- `C1`: compiler placement is evidence-backed.
- `C2`: latency is evidence-backed.
- `C3`: energy is evidence-backed.
- `C4`: accuracy is evidence-backed.
- `P1`: production readiness.

The current hardware-lab evidence affects them this way:

- `compiler_mapping.json` feeds `C1`. It contains operator placement rows, analog candidates, digital fallback rows, tile shape, DAC/ADC assumptions, and backend-derived placement rows. It supports a placement discussion. It refuses to prove that placement is safe on silicon.
- `analog_error_simulation.json` feeds `C4`. It contains the local nonideality chain: signed conductance, row drop, DAC quantization, programmed and drifted cells, ADC readout, and final residual. It supports a local analog-error statement. It refuses calibrated silicon behavior.
- `task_accuracy.json` feeds `C4`. It contains the toy transformer-sensitivity proxy: allowed fixed-projection cases, fallback cases, candidate metric, tolerance, and pass/fail. It supports a local model-sensitivity statement. It refuses full pretrained-model quality.
- `board_runtime.json` feeds `C2` and helps `C3`. It contains the local RTL/runtime trace, generated model-impact governor cases, fallback events, synthesis context, and OpenLane context. It supports a local runtime/control-path discussion. It refuses measured board latency.
- `power_thermal.json` feeds `C3`. It contains an OpenLane-derived control-block estimate, area, critical path, cell count, assumed room-temperature boundary, and a clear `not_measured_hardware` marker. It supports a needs-review energy discussion. It refuses measured power or thermal behavior.
- `physical_flow.json` feeds `C5`. It contains the selected OpenLane routed-result summary for the pipelined scheduler/governor: flow status, final artifact presence, timing numbers, DRC/LVS/antenna checks, and the signoff boundary. It supports a bounded digital physical-flow claim. It refuses analog macro integration, full-chip signoff, measured power, package reliability, calibrated silicon, or production readiness.
- `cross-repo-loop-proof.json` and `cross-repo-loop-proof.md` do not directly feed one claim ID. They prove the loop around the claims: backend placement, lab import, governor generation, RTL check, AIHWKIT/CrossSim adapter status, evidence export, backend import, and claim-readiness refresh all run together.

The current backend result is deliberately mixed: `C1`, `C4`, and `C5` are supported; `C2` and `C3` need review; `P1` remains blocked.

The backend import and claim-status rules are explained in `evidence-import-and-claim-readiness-first-principles.md`.

The measurement boundary for upgrading `C2` and `C3` is explained in `board-and-power-measurement-boundary.md`. That page defines what must be present before local runtime and OpenLane-derived power estimates become measured board latency and measured energy evidence.

Run:

```bash
python3 scripts/export_aimc_hardware_lab_evidence.py
```

Before exporting evidence, the lab can import the restored backend's model-to-placement artifact:

```bash
python3 scripts/import_backend_hardware_placement.py
```

That step writes `backend-hardware-placement-governor-input.csv`, which is appended to the model-impact governor request table and then checked by the Verilog governor trace.

The cross-repo loop proof is:

```bash
python3 scripts/prove_cross_repo_aimc_loop.py
```

It writes the reviewable proof artifacts here:

- `evidence/aimc-hardware-lab/cross-repo-loop-proof.json`
- `evidence/aimc-hardware-lab/cross-repo-loop-proof.md`

Expected summary:

```text
PASS cross_repo_aimc_loop
backend_operators,5
backend_analog_candidates,2
governor_rows,10
backend_governor_rows,5
rtl,pass
export_items,6
backend_import_accepted,6
strict_tool_evidence_imported,True
```

The exporter validates the generated payloads against the restored old backend's evidence schema when that backend source is available locally.

The first live backend import was also tested against the restored FastAPI app on port `8025`. The old backend now exposes a direct package endpoint for the sibling repo batch:

```text
POST /deployment-packages/{package_id}/hardware-lab-evidence
```

The old frontend calls this endpoint through the `Import Hardware Lab` button.

Sample package:

```text
pkg-e931662a01293df2
```

Live evidence brief:

```text
http://127.0.0.1:8025/deployment-packages/pkg-e931662a01293df2/evidence-brief.md
```

Live import result:

```text
accepted 6 ordinary records plus strict simulator/tool sidecar imported separately
rejected 0
strict_tool_evidence_imported true
```

Live claim-readiness result:

```text
Compiler placement is evidence-backed: supported
Latency is evidence-backed: needs review
Energy is evidence-backed: needs review
Accuracy is evidence-backed: supported
Digital physical flow is evidence-backed: supported
Production readiness: blocked
```

This is the intended behavior. Local lab evidence can support narrow placement and accuracy claims. Local runtime and local OpenLane-derived power estimates move latency and energy into needs-review territory, while measured-latency, measured-energy, and production-readiness claims remain refused until stronger evidence exists.

The next evidence upgrade is not another estimate. It is a synchronized board and power run where the runtime trace, voltage/current samples, thermal setup, workload, and host-overhead rule all describe the same window. That upgrade path is specified in `board-and-power-measurement-boundary.md`.

## How The Pages Should Connect

Every page in this system should be judged by the same chain:

```text
model graph
  -> placement boundary
  -> analog error source
  -> model sensitivity
  -> digital governor decision
  -> RTL and EDA proof
  -> backend evidence import
  -> claim readiness
```

If a page explains a concept but does not name its input artifact, output artifact, supported claim, and blocked claim, it is still too loose. The page may be readable, but it is not yet part of the workflow.

Current graph-driven evidence status:

```text
backend hardware-placement rows: 5
model-impact governor request rows: 10
RTL governor checked cases: 10
backend imported evidence records: 5
```

The 10 governor cases combine the original local transformer sensitivity cases with backend-derived ONNX placement rows from package `pkg-e931662a01293df2`.

## Claim Boundary

Allowed:

This repo contains a local educational proof slice for analog in-memory foundation-model hardware. It measures analog tile error, tests where that error matters in a transformer-style path, converts model impact into hardware-sized governor fields, checks those fields against Verilog RTL, synthesizes the control logic, and records OpenLane physical-design evidence for the pipelined scheduler/governor.

Not allowed:

This does not prove a production analog foundation-model chip. It does not include calibrated silicon, full AIHWKIT or CrossSim agreement, analog macro layout, board traces, measured power, measured thermal behavior, package reliability, test insertion, or signoff tapeout evidence.

## Evidence Rows

### Analog Crossbar Comparison

Status: simulated.

Source artifacts:

- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/spice-crossbar-comparison.csv`
- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/spice-crossbar-comparison.md`

Command:

```bash
cd labs/analog/analog-in-memory-foundation-model-hardware
python3 python/spice_crossbar_comparison.py
```

What this proves:

The local analog calculation can be compared against a SPICE-style crossbar model for selected cases.

What it does not prove:

It does not prove full array layout, full parasitics, process variation, or measured silicon.

Next proof:

Add a CrossSim-style layout-risk adapter and later compare to a stronger external crossbar simulator.

### Signed-Weight Analog Mapping

Status: simulated.

Source artifacts:

- `measurements/spice-signed-crossbar-comparison.csv`
- `measurements/spice-signed-crossbar-comparison.md`

Command:

```bash
cd labs/analog/analog-in-memory-foundation-model-hardware
python3 python/spice_signed_crossbar_comparison.py
```

What this proves:

Signed model weights need a differential or equivalent mapping. A negative weight is not simply a negative resistor; the circuit must represent positive and negative contribution through a concrete physical scheme.

What it does not prove:

It does not prove the best signed-memory cell or final analog macro design.

Next proof:

Tie the signed-weight mapping to placement output from the ONNX/compiler path.

### Row-Wire Drop

Status: simulated.

Source artifacts:

- `measurements/spice-row-drop-comparison.csv`
- `measurements/spice-row-drop-comparison.md`

Command:

```bash
cd labs/analog/analog-in-memory-foundation-model-hardware
python3 python/spice_row_drop_comparison.py
```

What this proves:

Row wires are part of the computation. If voltage falls along the row, cells do not all see the same input.

What it does not prove:

It does not prove final extracted layout behavior.

Next proof:

Feed row length, wire resistance, tile size, and bit slicing into a layout-risk record.

### Converter Boundary Sweep

Status: simulated.

Source artifacts:

- `measurements/converter-boundary-sweep.csv`
- `measurements/converter-boundary-sweep.md`

Command:

```bash
cd labs/analog/analog-in-memory-foundation-model-hardware
python3 python/converter_boundary_sweep.py
```

What this proves:

ADC and DAC precision are not peripheral details. They set how much continuous analog behavior becomes a bounded digital decision.

What it does not prove:

It does not prove final converter area, energy, bandwidth, or layout.

Next proof:

Connect converter settings to the old backend's timing, energy, and hardware-cost reports.

### Tile Operating Point

Status: simulated.

Source artifacts:

- `measurements/tile-operating-point.csv`
- `measurements/tile-operating-point.md`

Command:

```bash
cd labs/analog/analog-in-memory-foundation-model-hardware
python3 python/tile_operating_point.py
```

What this proves:

The tile needs a selected operating point: activation range, DAC bits, ADC bits, residual budget, and current range.

What it does not prove:

It does not prove that this operating point is optimal or safe for a fabricated chip.

Next proof:

Compare this operating point with AIHWKIT-style simulation and layout-risk estimates.

### Analog Nonideality Stack

Status: simulated.

Source artifacts:

- `measurements/analog-nonideality-stack.csv`
- `measurements/analog-nonideality-stack.md`

Command:

```bash
cd labs/analog/analog-in-memory-foundation-model-hardware
python3 python/analog_nonideality_stack.py
```

What this proves:

The analog tile is a measurement chain, not a perfect matrix multiply. The current final residual is represented as `final_residual_q8 = 12`.

What it does not prove:

It is not calibrated silicon evidence.

Next proof:

Export this residual into the old backend as analog simulation evidence and compare it with AIHWKIT when available.

### Model Sensitivity

Status: simulated.

Source artifacts:

- `measurements/measured-tile-transformer-impact.csv`
- `measurements/measured-tile-transformer-impact.md`

Command:

```bash
cd labs/analog/analog-in-memory-foundation-model-hardware
python3 python/measured_tile_transformer_impact.py
```

What this proves:

The same analog residual has different meaning in different model locations. Fixed projection can remain within budget, while attention and logits can be too sensitive.

What it does not prove:

It is not a full pretrained-model benchmark.

Next proof:

Drive the sensitivity cases from a graph placement pass instead of only local test policies.

### Model-Impact Governor Requests

Status: generated hardware input.

Source artifacts:

- `measurements/model-impact-governor-requests.csv`
- `measurements/model-impact-governor-requests.md`
- `labs/digital/aimc-control-plane-rtl/generated_model_impact_governor_cases.vh`

Command:

```bash
cd labs/analog/analog-in-memory-foundation-model-hardware
python3 python/model_impact_governor_requests.py
```

What this proves:

Model behavior and backend graph placement can be compressed into hardware-sized fields such as residual, sensitivity, cumulative error, and expected governor action. The current request table contains both local transformer sensitivity rows and backend-derived ONNX placement rows.

What it does not prove:

It does not prove full runtime scheduling until the integrated controller consumes the same rows.

Next proof:

Generate integrated scheduler/governor cases from these model-impact rows.

### RTL Governor Check

Status: RTL-verified.

Source artifacts:

- `labs/digital/aimc-control-plane-rtl/aimc_model_impact_governor_tb.v`
- `labs/digital/aimc-control-plane-rtl/check_generated_model_impact_governor_trace.py`

Command:

```bash
cd labs/digital/aimc-control-plane-rtl
python3 check_generated_model_impact_governor_trace.py
```

What this proves:

The Verilog governor makes the expected accept/refuse decision for model-impact cases generated from the analog/model CSV and the backend-derived placement rows.

What it does not prove:

It does not prove every possible state, physical timing, or production verification coverage.

Next proof:

Add a combined scheduler/governor model-impact checker.

### Integrated Runtime RTL Checks

Status: RTL-verified.

Source artifacts:

- `measurements/integrated-scheduler-governor-runtime.csv`
- `labs/digital/aimc-control-plane-rtl/check_generated_integrated_scheduler_governor_trace.py`
- `labs/digital/aimc-control-plane-rtl/check_generated_pipelined_scheduler_governor_trace.py`

Command:

```bash
./scripts/check_aimc_bridge.sh
```

What this proves:

Generated scheduler/governor traces match RTL behavior for current local runtime cases.

What it does not prove:

The current integrated traces are not yet driven directly by the model-impact placement rows.

Next proof:

Unify model-impact rows and integrated scheduler/governor rows.

### Synthesis Evidence

Status: synthesized.

Source artifacts:

- `labs/digital/aimc-control-plane-synthesis/reports/`
- `labs/digital/aimc-control-plane-synthesis/reports/synthesis-interpretation.md`

Command:

```bash
./scripts/check_aimc_bridge.sh
```

What this proves:

The RTL control blocks can be lowered by Yosys into logic for the selected educational flow.

What it does not prove:

It does not prove final timing, routing, physical legality, power, or manufacturability.

Next proof:

Summarize synthesis cell counts into importable backend evidence.

### OpenLane Physical-Design Evidence

Status: routed educational-flow evidence.

Source artifacts:

- `labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/openlane-5ns-control-reset-fanout20-metrics-summary.md`

Command:

```bash
./scripts/run_aimc_openlane_flow.sh
```

What this proves:

The pipelined scheduler/governor has a successful OpenLane result under the recorded 5 ns and fanout-20 setup. The report records clean timing, DRC, LVS, antenna, slew, fanout, and capacitance checks for that flow.

What it does not prove:

It is not signoff-quality tapeout evidence.

Next proof:

Export OpenLane metrics into the old backend's hardware evidence panel and connect it to tapeout-risk wording.

## Whole-Bridge Check

Status: project-verified.

Command:

```bash
./scripts/check_aimc_bridge.sh
```

Current expected result:

```text
PASS aimc_bridge_check
50/50 gates
```

What this proves:

The current local hardware-lab proof chain regenerates analog reports, generated RTL cases, RTL simulations, synthesis checks, OpenLane readiness checks, AIHWKIT/CrossSim adapter availability and smoke-run status, optional simulator payload-run summary, workload-shaped simulator payloads for backend-selected analog candidates, tensor-shaped simulator payloads for backend analog MatMul candidates, trained-weight simulator payloads for the uploaded tiny MLP analog MatMul weights, projection-stack simulator payloads for a larger four-MatMul ONNX fixture, transformer-MLP-block simulator payloads with nonlinear and residual operations kept digital, calibrated transformer-MLP-block simulator payloads with held-out affine correction, calibrated deep transformer-MLP-stack simulator payloads with held-out affine correction, attention-block simulator payloads for static projections with dynamic attention kept digital, calibrated attention-block simulator payloads with held-out affine correction, calibrated residual governor bridge decisions, source-matched residual-aware placement decisions, hardware-lab evidence export, strict analog simulator/tool evidence export, site build, dry-run simulator payload examples, project validation, analog simulator adapter contract validation, guarded simulator payload import checks, old-backend evidence import, backend residual-aware placement API and archive checks, and claim-readiness refresh.

What it does not prove:

It does not prove measured board latency, measured power, calibrated silicon, analog macro integration, production signoff, or tapeout readiness.

Next proof:

Add measured board runtime, synchronized power, or physical macro evidence under the existing source-matched placement rule.

The exporter, backend import endpoint, frontend hardware-lab panel, power/thermal estimate record, physical-flow record, simulator availability and smoke-run status report, optional small-fixture simulator payloads, workload-shaped simulator payloads for selected analog candidates, tensor-shaped simulator payloads for backend MatMul candidates, trained-weight simulator payloads for the tiny MLP ONNX model, projection-stack simulator payloads for a larger four-MatMul ONNX fixture, raw and calibrated transformer-MLP-block simulator payloads, calibrated deep transformer-MLP-stack simulator payloads, raw and calibrated attention-block simulator payloads, dry-run simulator payload examples, analog simulator adapter output contract, guarded simulator payload import path, source-matched residual-aware placement, and cross-repo proof now exist. The next proof is stronger evidence, not broader wording: real board runtime, synchronized power measurement, and analog macro/layout evidence.
