# AIMC Tile-Service Scheduler No-CTS OpenLane Report

This report records the no-CTS exploratory physical flow for `aimc_tile_service_scheduler_physical`, the registered-boundary wrapper around the pure tile-service scheduler.

## Command

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_tile_service_scheduler_clean_no_cts CONFIG_NAME=config_no_cts AIMC_OPENLANE_PREP=aimc-tile-service-scheduler-openlane-prep AIMC_OPENLANE_DESIGN=aimc_tile_service_scheduler_physical AIMC_OPENLANE_RTL=aimc_tile_service_scheduler.v ./scripts/run_aimc_openlane_flow.sh
```

## Run Directory

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_tile_service_scheduler_physical/runs/aimc_tile_service_scheduler_clean_no_cts
```

## Result

```text
flow_status: flow completed
total_runtime: 0h1m16s0ms
routed_runtime: 0h0m51s0ms
synth_cell_count: 78
TotalCells: 450
CoreArea_um^2: 3578.432
DIEAREA_mm^2: 0.005844193625000001
wire_length: 2237
vias: 686
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 2.51
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
/home/mehtama1/eda-tools/OpenLane/designs/aimc_tile_service_scheduler_physical/runs/aimc_tile_service_scheduler_clean_no_cts/results/signoff
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

## Remaining Boundary

This is a no-CTS run. It does not prove clock-tree signoff.

The final STA checks show:

```text
max slew violation count 0
max fanout violation count 1
max cap violation count 0
clk limit 10, fanout 25
```

The setup and hold checks reported no violating paths after extraction:

```text
No paths found.
```

OpenLane also scaled down the power grid because the block is small. That is acceptable for this exploratory wrapper run, but it should be revisited before treating the block as a production macro.

The useful claim is therefore bounded:

```text
The registered-boundary scheduler wrapper can be synthesized, placed, routed, extracted, streamed to GDS, and pass DRC, LVS, antenna, setup, and hold checks in the no-CTS exploratory flow.
```

The unresolved object remains:

```text
clock-tree signoff and the no-CTS clock fanout violation
```
