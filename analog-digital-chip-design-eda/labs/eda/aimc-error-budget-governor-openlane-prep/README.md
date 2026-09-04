# Lab: AIMC Error-Budget Governor OpenLane Prep

This lab packages the error-budget governor for physical-flow review. The object is not the analog array and not the tile scheduler. The object is the small digital decision block that decides whether the next analog result is worth spending.

## Workflow Contract

Consumes: generated error-budget trace, governor RTL, residual and sensitivity fields, cumulative-error rule, clocked physical wrapper, Yosys synthesis report, and OpenLane physical-flow results.

Produces: governor physical-flow evidence, timing/routing/area metrics, DRC/LVS/antenna status, and remaining fanout or endpoint boundaries.

Supports: the claim that the analog-error spending rule can become a physical-flow object in this local setup.

Refuses: proving analog accuracy by itself, measured latency, measured energy, calibrated silicon behavior, or production controller signoff.

Handoff: this page is the physical-flow counterpart to the model-impact governor rows. Its evidence helps explain local control behavior, but the backend should still treat board runtime and power claims as needs-review unless measured records are attached.

## Object

The pure governor is `src/aimc_error_budget_governor.v`. It is combinational. It reads:

```text
sample_valid
analog_candidate
residual_q8
drift_age
sensitivity_q8
cumulative_error_q8
```

It emits:

```text
service_decision
tile_action
reason
next_cumulative_error_q8
```

The first-principles rule is that analog usefulness is not proven by a locally plausible multiply. The control plane also needs to know whether the model can afford the next analog error. A high residual, stale calibration, sensitive model path, or already-spent state budget can all make digital fallback the right answer.

## Constraint

The governor itself has no registers. A physical flow still needs a clocked boundary. The OpenLane package uses `aimc_error_budget_governor_physical`, which registers the inputs and outputs around the combinational governor:

```text
registered error evidence -> governor policy -> registered service decision
```

That wrapper does not change the policy. It gives timing analysis a concrete question:

```text
Can the governor decision settle between one set of registers and the next?
```

## Files

- `src/aimc_error_budget_governor.v`: local copy of the pure governor RTL
- `src/aimc_error_budget_governor_physical.v`: clocked physical wrapper
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

Run the generated governor trace first:

```bash
cd labs/digital/aimc-control-plane-rtl
python3 check_generated_error_budget_governor_trace.py
```

Run synthesis for the pure governor:

```bash
cd labs/digital/aimc-control-plane-synthesis
yosys synth_aimc_error_budget_governor.ys
```

Check OpenLane readiness:

```bash
AIMC_OPENLANE_PREP=aimc-error-budget-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_error_budget_governor_physical AIMC_OPENLANE_RTL=aimc_error_budget_governor.v ./scripts/check_aimc_openlane_readiness.sh
```

When OpenLane is available, run the exploratory no-CTS flow:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_error_budget_governor_no_cts CONFIG_NAME=config_no_cts AIMC_OPENLANE_PREP=aimc-error-budget-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_error_budget_governor_physical AIMC_OPENLANE_RTL=aimc_error_budget_governor.v ./scripts/run_aimc_openlane_flow.sh
```

Run the CTS-enabled flow:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_error_budget_governor_cts CONFIG_NAME=config AIMC_OPENLANE_PREP=aimc-error-budget-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_error_budget_governor_physical AIMC_OPENLANE_RTL=aimc_error_budget_governor.v ./scripts/run_aimc_openlane_flow.sh
```

## Measurement

The readiness check should prove:

- all package files exist
- `config.json` parses
- the packaged RTL lowers through Yosys
- the OpenLane source tree and Docker image are present

The pure governor synthesis currently reports:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 353
$_AND_: 126
$_MUX_: 88
$_NOT_: 13
$_OR_: 68
$_XOR_: 58
```

The no-flip-flop result is intentional for the pure governor. The physical wrapper adds registers only to define the timing boundary.

Current no-CTS physical run summary:

```text
flow_status: flow completed
synth_cell_count: 190
TotalCells: 998
CoreArea_um^2: 7727.4112000000005
DIEAREA_mm^2: 0.0110846468
wire_length: 5331
vias: 1543
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 4.85
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
linter_errors: 0
linter_warnings: 0
max slew violation count: 0
max fanout violation count: 3
max capacitance violation count: 0
```

This run is physical evidence that the registered-boundary governor wrapper can pass no-CTS synthesis, placement, routing, extraction, GDS generation, DRC, LVS, antenna, setup, and hold checks. The remaining physical-design object is clock-tree signoff, no-CTS fanout cleanup, two unconstrained endpoint warnings, and small-core power-grid packaging.

Current CTS-enabled physical run summary:

```text
flow_status: flow completed
synth_cell_count: 190
TotalCells: 996
CoreArea_um^2: 7727.4112000000005
DIEAREA_mm^2: 0.0110846468
wire_length: 5584
vias: 1602
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 4.71
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
linter_errors: 0
linter_warnings: 0
max slew violation count: 0
max fanout violation count: 3
max capacitance violation count: 0
```

The CTS-enabled run proves more than the no-CTS run: clock tree synthesis completed, and the block still routed, extracted, generated final views, and passed DRC, LVS, antenna, setup, and hold checks. It is still not a production closure claim. Three max-fanout violations remain, the checks report lists unconstrained endpoints on `reason[3]` and `service_decision[1]`, and the small-core power-grid scaling warning remains a packaging boundary.

## Failure Mode

The failure mode is claiming that error budget is one threshold. It is not. A high local residual, old calibration, sensitive model path, and spent cumulative state budget are different reasons to refuse analog service. The physical package must preserve that distinction through the reason code.

The second failure mode is hiding policy inside the wrapper. The wrapper should only register inputs and outputs. The policy must remain in the pure governor so it can be tested directly against the generated runtime trace.
