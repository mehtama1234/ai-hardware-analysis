# AIMC Scheduler/Governor 8 ns CTS OpenLane Report

This report records the CTS-enabled 8 ns OpenLane run for `aimc_scheduler_governor_physical`, the registered wrapper around the integrated scheduler/governor policy.

## Command

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_scheduler_governor_cts_8ns CONFIG_NAME=config_8ns AIMC_OPENLANE_PREP=aimc-scheduler-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_scheduler_governor_physical AIMC_OPENLANE_RTL=aimc_scheduler_governor.v ./scripts/run_aimc_openlane_flow.sh
```

## Run Directory

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_scheduler_governor_physical/runs/aimc_scheduler_governor_cts_8ns
```

## Result

```text
flow_status: flow completed
total_runtime: 0h2m51s0ms
routed_runtime: 0h2m19s0ms
synth_cell_count: 266
TotalCells: 1441
CoreArea_um^2: 10935.488
DIEAREA_mm^2: 0.014948134799999999
wire_length: 8607
vias: 2372
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 6.14
suggested_clock_period: 8.0
suggested_clock_frequency: 125.0
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
linter_errors: 0
linter_warnings: 0
```

## What This Proves

The pure RTL tests prove that the integrated policy matches the generated 36-token trace. The CTS run answers a different question:

```text
Can the combined scheduler/governor policy be placed behind registers, given a real clock tree, routed, extracted, checked, and still meet an 8 ns timing boundary?
```

For this exploratory setup, the answer is yes.

The flow completed synthesis, placement, clock tree synthesis, routing, extraction, GDS generation, LVS, Magic DRC, antenna checking, setup checking, and hold checking.

## First-Principles Reading

The block is a digital referee around analog compute. The analog array may be able to compute a multiply-accumulate cheaply, but that is not enough. The serving system also needs to decide whether the analog answer is allowed for this token.

The scheduler supplies availability evidence:

```text
requested tile
tile health
busy state
maintenance budget
```

The governor supplies trust evidence:

```text
residual error
calibration age
path sensitivity
accumulated error
```

The integrated policy only allows analog service when both evidence streams agree. That is why the block is larger and deeper than either child block alone. It is not merely selecting a tile. It is also deciding whether the analog tile should be trusted.

The 5 ns run failed because that joined decision was too deep for one cycle. The 8 ns CTS run shows the same joined decision can survive a real clock-tree flow when the timing boundary is relaxed. This is the architectural fact the lab should teach: using analog compute in a foundation-model system saves work only after a digital policy spends error carefully enough to keep the model's state meaningful.

## Final Views

The run produced final physical and timing views under:

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_scheduler_governor_physical/runs/aimc_scheduler_governor_cts_8ns/results/signoff
```

Important files include:

```text
aimc_scheduler_governor_physical.gds
aimc_scheduler_governor_physical.lef
aimc_scheduler_governor_physical.lib
aimc_scheduler_governor_physical.sdf
aimc_scheduler_governor_physical.spice
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

The final typical-corner timing checks report no setup or hold violating paths:

```text
setup_violating_paths_found: false
max slew violation count 0
max fanout violation count 5
max cap violation count 0
```

The remaining fanout violators include:

```text
fanout66/X limit 10, fanout 20
fanout62/X limit 10, fanout 12
fanout67/X limit 10, fanout 12
```

OpenLane also scaled down the power grid because the block is small, and the IR-drop report warns that `VSRC_LOC_FILES` is not defined. Those warnings should be resolved before treating this as a production macro.

## Bounded Claim

The useful claim is:

```text
At an 8 ns timing boundary, the registered integrated scheduler/governor wrapper completes a CTS-enabled OpenLane flow with clean routing DRC, Magic DRC, LVS, antenna checks, setup checks, and hold checks.
```

The unresolved objects are:

```text
max-fanout cleanup
small-core power-grid packaging
IR-drop source-location setup
eventual macro integration with analog tile timing models
```
