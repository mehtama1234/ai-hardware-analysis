# AIMC Tile-Service Scheduler CTS OpenLane Report

This report records the CTS-enabled physical flow for `aimc_tile_service_scheduler_physical`, the registered-boundary wrapper around the pure tile-service scheduler.

## Command

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_tile_service_scheduler_cts CONFIG_NAME=config AIMC_OPENLANE_PREP=aimc-tile-service-scheduler-openlane-prep AIMC_OPENLANE_DESIGN=aimc_tile_service_scheduler_physical AIMC_OPENLANE_RTL=aimc_tile_service_scheduler.v ./scripts/run_aimc_openlane_flow.sh
```

## Run Directory

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_tile_service_scheduler_physical/runs/aimc_tile_service_scheduler_cts
```

## Result

```text
flow_status: flow completed
total_runtime: 0h2m14s0ms
routed_runtime: 0h1m48s0ms
synth_cell_count: 78
TotalCells: 447
CoreArea_um^2: 3578.432
DIEAREA_mm^2: 0.005844193625000001
wire_length: 2406
vias: 722
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 2.52
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

The scheduler policy is still tested in the pure RTL lab. This physical run answers a different question: whether the scheduler can be wrapped in registers and carried through a CTS-enabled layout flow as a small digital block.

The answer is yes for this exploratory setup. The flow completed synthesis, placement, clock tree synthesis, routing, extraction, final report generation, GDS generation, DRC, LVS, antenna checking, setup checking, and hold checking.

## Final Views

The run produced final physical and timing views under:

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_tile_service_scheduler_physical/runs/aimc_tile_service_scheduler_cts/results/signoff
```

Important files include:

```text
aimc_tile_service_scheduler_physical.gds
aimc_tile_service_scheduler_physical.lef
aimc_tile_service_scheduler_physical.lib
aimc_tile_service_scheduler_physical.sdf
aimc_tile_service_scheduler_physical.spice
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
max fanout violation count 2
max cap violation count 0
```

The two remaining fanout violations are generated clock-buffer outputs:

```text
clkbuf_1_0__f_clk/X limit 10, fanout 14
clkbuf_1_1__f_clk/X limit 10, fanout 11
```

The setup and hold checks reported no violating paths after extraction:

```text
No paths found.
```

The checks report also lists one unconstrained endpoint, `reason[3]`. That needs review before treating the wrapper as closed timing evidence. It may be a reporting artifact from the generated output boundary, but it should not be ignored.

OpenLane also scaled down the power grid because the block is small. That is acceptable for this exploratory wrapper run, but it should be revisited before treating the block as a production macro.

## Bounded Claim

The useful claim is:

```text
The registered-boundary scheduler wrapper can complete a CTS-enabled OpenLane flow with clean routing DRC, Magic DRC, LVS, antenna checks, setup checks, and hold checks.
```

The unresolved objects are:

```text
max-fanout cleanup on generated clock buffers
unconstrained endpoint review for reason[3]
small-core power-grid packaging
```
