# AIMC Tile-Service Scheduler OpenLane Metrics Summary

This file is generated from local no-CTS OpenLane run artifacts.

## Run

```text
run_dir: /home/mehtama1/eda-tools/OpenLane/designs/aimc_tile_service_scheduler_physical/runs/aimc_tile_service_scheduler_clean_no_cts
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

## Final Artifact Check

```text
signoff/aimc_tile_service_scheduler_physical.gds: present
signoff/aimc_tile_service_scheduler_physical.lef: present
signoff/aimc_tile_service_scheduler_physical.lib: present
signoff/aimc_tile_service_scheduler_physical.sdf: present
signoff/aimc_tile_service_scheduler_physical.spice: present
routing/aimc_tile_service_scheduler_physical.def: present
routing/aimc_tile_service_scheduler_physical.nl.v: present
```

## Manufacturability

```text
Total Magic DRC violations is 0
Design is LVS clean.
Pin violations: 0
Net violations: 0
```

## Timing And Fanout Boundary

```text
setup_violating_paths_found: false
max_slew_violations: 0
max_fanout_violations: 1
max_cap_violations: 0
clock_fanout: 25
```

## Interpretation

The no-CTS flow proves that the registered-boundary scheduler wrapper can pass synthesis, placement, routing, extraction, GDS generation, DRC, LVS, and antenna checks in this exploratory setup.

It does not prove clock-tree signoff. The remaining fanout violation is the open physical-design object, and the clock net is the violator because CTS is disabled.
