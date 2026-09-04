# Lab: AIMC Tile-Service Scheduler OpenLane Prep

This lab packages the tile-service scheduler for physical-flow review. The object is not the analog array and not the per-tile readout controller. The object is the small system-level dispatcher that chooses analog service, recalibration, probe, or digital fallback from already-visible tile health states.

## Workflow Contract

Consumes: generated scheduler runtime trace, pure scheduler RTL, clocked physical wrapper, Yosys synthesis report, OpenLane package files, no-CTS result, and CTS-enabled result.

Produces: scheduler physical-flow evidence, area/timing/routing metrics, DRC/LVS/antenna status, and remaining fanout or packaging boundaries.

Supports: the claim that the tile-service dispatcher can be represented as a small physical-flow object in this local setup.

Refuses: proving tile trust, analog correctness, measured board latency, measured energy, package reliability, or production macro signoff.

Handoff: this page feeds the local runtime/control evidence that appears in `board_runtime.json`. It explains how the scheduler can be physically packaged, while the backend claim engine still keeps measured latency in needs-review state.

## Object

The pure scheduler is `src/aimc_tile_service_scheduler.v`. It is combinational. It reads:

```text
sample_valid
analog_candidate
requested_tile_id
tile0_health_action through tile3_health_action
tile_busy
maintenance_budget
```

It emits:

```text
service_decision
selected_tile
reason
```

The first-principles rule is that a scheduler should not create trust. It should spend trust that another block has already made visible. A tile controller records readout evidence and exposes a health action. The scheduler uses those health actions under a maintenance budget.

## Constraint

The scheduler itself has no registers. A physical flow still needs a clocked boundary. The OpenLane package uses `aimc_tile_service_scheduler_physical`, which registers the inputs and outputs around the combinational scheduler:

```text
registered tile state -> scheduler policy -> registered service decision
```

That wrapper does not change the scheduler rule. It gives timing analysis a concrete question:

```text
Can the service decision settle between one set of registers and the next?
```

## Files

- `src/aimc_tile_service_scheduler.v`: local copy of the pure scheduler RTL
- `src/aimc_tile_service_scheduler_physical.v`: clocked physical wrapper
- `config.json`: OpenLane-style design configuration
- `config.tcl`: compatibility configuration for older `flow.tcl` runs
- `config_no_cts.tcl`: exploratory no-CTS configuration
- `openlane-no-cts-final-report.md`: bounded physical-flow result
- `openlane-no-cts-metrics-summary.md`: generated compact metric summary
- `openlane-cts-final-report.md`: CTS-enabled physical-flow result
- `openlane-cts-metrics-summary.md`: generated CTS metric summary
- `analyze_no_cts_result.py`: extracts metrics from local OpenLane artifacts
- `constraint.sdc`: virtual-clock input/output timing assumptions
- `src/constraint.sdc`: SDC copy for older OpenLane design-folder conventions
- `pin_order.cfg`: stable pin-order intent for review

## Concrete Design Move

Run the generated scheduler trace first:

```bash
cd labs/digital/aimc-control-plane-rtl
python3 check_generated_scheduler_trace.py
```

Run synthesis for the pure scheduler:

```bash
cd labs/digital/aimc-control-plane-synthesis
yosys synth_aimc_tile_service_scheduler.ys
```

Check OpenLane readiness:

```bash
AIMC_OPENLANE_PREP=aimc-tile-service-scheduler-openlane-prep AIMC_OPENLANE_DESIGN=aimc_tile_service_scheduler_physical AIMC_OPENLANE_RTL=aimc_tile_service_scheduler.v ./scripts/check_aimc_openlane_readiness.sh
```

When OpenLane is available, run the exploratory no-CTS flow:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_tile_service_scheduler_clean_no_cts CONFIG_NAME=config_no_cts AIMC_OPENLANE_PREP=aimc-tile-service-scheduler-openlane-prep AIMC_OPENLANE_DESIGN=aimc_tile_service_scheduler_physical AIMC_OPENLANE_RTL=aimc_tile_service_scheduler.v ./scripts/run_aimc_openlane_flow.sh
```

Regenerate the compact evidence summary:

```bash
cd labs/eda/aimc-tile-service-scheduler-openlane-prep
python3 analyze_no_cts_result.py
```

Run the CTS-enabled flow:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_tile_service_scheduler_cts CONFIG_NAME=config AIMC_OPENLANE_PREP=aimc-tile-service-scheduler-openlane-prep AIMC_OPENLANE_DESIGN=aimc_tile_service_scheduler_physical AIMC_OPENLANE_RTL=aimc_tile_service_scheduler.v ./scripts/run_aimc_openlane_flow.sh
```

Regenerate the CTS summary:

```bash
cd labs/eda/aimc-tile-service-scheduler-openlane-prep
python3 analyze_no_cts_result.py /home/mehtama1/eda-tools/OpenLane/designs/aimc_tile_service_scheduler_physical/runs/aimc_tile_service_scheduler_cts openlane-cts-metrics-summary.md
```

## Measurement

The readiness check should prove:

- all package files exist
- `config.json` parses
- the packaged RTL lowers through Yosys
- the OpenLane source tree and Docker image are present

The pure scheduler synthesis currently reports:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 154
$_AND_: 22
$_MUX_: 58
$_NOT_: 30
$_OR_: 34
$_XOR_: 10
```

The no-flip-flop result is intentional for the pure scheduler. The physical wrapper adds registers only to define the timing boundary.

Current no-CTS physical run summary:

```text
flow_status: flow completed
synth_cell_count: 78
TotalCells: 450
CoreArea_um^2: 3578.432
DIEAREA_mm^2: 0.005844193625000001
wire_length: 2237
vias: 686
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 2.51
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
linter_errors: 0
linter_warnings: 0
max slew violation count: 0
max fanout violation count: 1
max capacitance violation count: 0
```

This run is physical evidence that the registered-boundary scheduler wrapper can pass no-CTS synthesis, placement, routing, extraction, GDS generation, DRC, LVS, antenna, setup, and hold checks. The remaining physical-design object is clock-tree signoff and the no-CTS clock fanout violation. OpenLane also scaled the power grid down because this wrapper is small; that is a packaging boundary to revisit before treating the scheduler as a production macro.

Current CTS-enabled physical run summary:

```text
flow_status: flow completed
synth_cell_count: 78
TotalCells: 447
CoreArea_um^2: 3578.432
DIEAREA_mm^2: 0.005844193625000001
wire_length: 2406
vias: 722
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 2.52
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
linter_errors: 0
linter_warnings: 0
max slew violation count: 0
max fanout violation count: 2
max capacitance violation count: 0
```

The CTS-enabled run proves more than the no-CTS run: clock tree synthesis completed, and the block still routed, extracted, generated final views, and passed DRC, LVS, antenna, setup, and hold checks. It is still not a production closure claim. Two max-fanout violations remain on generated clock buffers, the checks report lists one unconstrained endpoint on `reason[3]`, and the small-core power-grid scaling warning remains a packaging boundary.

## Failure Mode

The failure mode is claiming that a scheduler is correct because the physical package exists. The package only says the dispatcher can be made into a physical-flow object. Correctness still comes from the generated runtime trace, the Verilog scheduler checker, and the Yosys synthesis result.

The second failure mode is hiding policy inside the wrapper. The wrapper should only register inputs and outputs. The policy must remain in the pure scheduler so it can be tested directly against the generated runtime trace.
