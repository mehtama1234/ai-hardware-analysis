# AIMC Micro-Tile Controller OpenLane Metrics Summary

This file is generated from the local no-CTS OpenLane run artifacts.

## Run

```text
run_dir: /home/mehtama1/eda-tools/OpenLane/designs/aimc_micro_tile_controller/runs/aimc_micro_tile_controller_recovery_probe_no_cts
flow_status: flow completed
total_runtime: 0h4m41s0ms
routed_runtime: 0h3m14s0ms
synth_cell_count: 1338
TotalCells: 7612
CoreArea_um^2: 56168.8704
DIEAREA_mm^2: 0.06449743079999999
wire_length: 50119
vias: 11936
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 8.57
suggested_clock_period: 12.0
suggested_clock_frequency: 83.33333333333333
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
signoff/aimc_micro_tile_controller.gds: present
signoff/aimc_micro_tile_controller.lef: present
signoff/aimc_micro_tile_controller.lib: present
signoff/aimc_micro_tile_controller.sdf: present
signoff/aimc_micro_tile_controller.spice: present
routing/aimc_micro_tile_controller.def: present
routing/aimc_micro_tile_controller.nl.v: present
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
max_slew_violations: 111
max_fanout_violations: 34
max_cap_violations: 1
clock_fanout: 110
```

## Interpretation

The no-CTS flow proves that the integrated controller can pass synthesis, placement, routing, extraction, GDS generation, DRC, LVS, and antenna checks in this exploratory setup.

It does not prove clock-tree signoff. The remaining fanout violations are the open physical-design object, and the clock net is one of the violators because CTS is disabled.
