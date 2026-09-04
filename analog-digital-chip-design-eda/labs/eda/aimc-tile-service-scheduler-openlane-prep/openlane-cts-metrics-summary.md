# AIMC Tile-Service Scheduler OpenLane Metrics Summary

This file is generated from local CTS-enabled OpenLane run artifacts.

## Run

```text
run_dir: /home/mehtama1/eda-tools/OpenLane/designs/aimc_tile_service_scheduler_physical/runs/aimc_tile_service_scheduler_cts
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
max_fanout_violations: 2
max_cap_violations: 0
clock_fanout: missing
```

## Interpretation

The CTS-enabled flow proves that the registered-boundary scheduler wrapper can pass synthesis, placement, CTS, routing, extraction, GDS generation, DRC, LVS, antenna checks, setup checks, and hold checks in this exploratory setup.

It is not yet a production macro. The remaining physical-design boundary is max-fanout cleanup on generated clock buffers, review of the unconstrained endpoint report, and small-core power-grid packaging.
