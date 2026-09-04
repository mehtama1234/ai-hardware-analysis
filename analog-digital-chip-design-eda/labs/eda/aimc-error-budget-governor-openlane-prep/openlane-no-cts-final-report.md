# AIMC Error-Budget Governor No-CTS OpenLane Report

This report records the no-CTS exploratory physical flow for `aimc_error_budget_governor_physical`, the registered-boundary wrapper around the pure error-budget governor.

## Command

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_error_budget_governor_lint_clean_no_cts CONFIG_NAME=config_no_cts AIMC_OPENLANE_PREP=aimc-error-budget-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_error_budget_governor_physical AIMC_OPENLANE_RTL=aimc_error_budget_governor.v ./scripts/run_aimc_openlane_flow.sh
```

## Run Directory

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_error_budget_governor_physical/runs/aimc_error_budget_governor_lint_clean_no_cts
```

## Result

```text
flow_status: flow completed
total_runtime: 0h1m36s0ms
routed_runtime: 0h1m6s0ms
synth_cell_count: 190
TotalCells: 998
CoreArea_um^2: 7727.4112000000005
DIEAREA_mm^2: 0.0110846468
wire_length: 5331
vias: 1543
wns: -0.16
tns: -0.82
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 4.85
suggested_clock_period: 5.0
suggested_clock_frequency: 200.0
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
linter_errors: 0
linter_warnings: 0
```

## Final Views

The run produced final physical and timing views under:

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_error_budget_governor_physical/runs/aimc_error_budget_governor_lint_clean_no_cts/results/signoff
```

Important files include:

```text
aimc_error_budget_governor_physical.gds
aimc_error_budget_governor_physical.lef
aimc_error_budget_governor_physical.lib
aimc_error_budget_governor_physical.sdf
aimc_error_budget_governor_physical.spice
```

## Manufacturability

The manufacturability report says:

```text
Total Magic DRC violations is 0
Design is LVS clean.
Pin violations: 0
Net violations: 0
```

## Remaining Boundary

This is a no-CTS run. It does not prove clock-tree signoff.

The final STA checks show:

```text
max slew violation count 0
max fanout violation count 3
max cap violation count 0
clk limit 10, fanout 40
```

The setup and hold checks reported no violating paths after extraction:

```text
No paths found.
```

The checks report also lists two unconstrained endpoints:

```text
reason[3]
service_decision[1]
```

OpenLane also scaled down the power grid because the block is small, and the IR-drop report warns that `VSRC_LOC_FILES` is not defined. Those are acceptable for this exploratory wrapper run, but they should be revisited before treating the governor as a production macro.

The useful claim is therefore bounded:

```text
The registered-boundary governor wrapper can be synthesized, placed, routed, extracted, streamed to GDS, and pass DRC, LVS, antenna, setup, and hold checks in the no-CTS exploratory flow.
```

The unresolved objects are:

```text
clock-tree signoff
no-CTS fanout violations
unconstrained endpoint review for reason[3] and service_decision[1]
small-core power-grid packaging
```
