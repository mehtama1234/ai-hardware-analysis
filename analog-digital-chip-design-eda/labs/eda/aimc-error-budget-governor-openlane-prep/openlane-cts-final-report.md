# AIMC Error-Budget Governor CTS OpenLane Report

This report records the CTS-enabled physical flow for `aimc_error_budget_governor_physical`, the registered-boundary wrapper around the pure error-budget governor.

## Command

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_error_budget_governor_cts CONFIG_NAME=config AIMC_OPENLANE_PREP=aimc-error-budget-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_error_budget_governor_physical AIMC_OPENLANE_RTL=aimc_error_budget_governor.v ./scripts/run_aimc_openlane_flow.sh
```

## Run Directory

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_error_budget_governor_physical/runs/aimc_error_budget_governor_cts
```

## Result

```text
flow_status: flow completed
total_runtime: 0h2m27s0ms
routed_runtime: 0h1m59s0ms
synth_cell_count: 190
TotalCells: 996
CoreArea_um^2: 7727.4112000000005
DIEAREA_mm^2: 0.0110846468
wire_length: 5584
vias: 1602
wns: -0.16
tns: -0.82
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 4.71
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

## What This Proves

The governor policy is tested in the pure RTL lab against the generated 32-token trace. This physical run answers a different question: whether the policy can be wrapped in registers and carried through a CTS-enabled layout flow.

The answer is yes for this exploratory setup. The flow completed synthesis, placement, clock tree synthesis, routing, extraction, final report generation, GDS generation, DRC, LVS, antenna checking, setup checking, and hold checking.

## Final Views

The run produced final physical and timing views under:

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_error_budget_governor_physical/runs/aimc_error_budget_governor_cts/results/signoff
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

## Timing Boundary

The final timing checks show:

```text
setup_violating_paths_found: false
max slew violation count 0
max fanout violation count 3
max cap violation count 0
```

The remaining fanout violations are:

```text
fanout43/X limit 10, fanout 20
fanout45/X limit 10, fanout 20
clkbuf_2_2__f_clk/X limit 10, fanout 13
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

## Bounded Claim

The useful claim is:

```text
The registered-boundary governor wrapper can complete a CTS-enabled OpenLane flow with clean routing DRC, Magic DRC, LVS, antenna checks, setup checks, and hold checks.
```

The unresolved objects are:

```text
max-fanout cleanup
unconstrained endpoint review for reason[3] and service_decision[1]
small-core power-grid packaging
```
