# AIMC Scheduler/Governor OpenLane Metrics Summary

This file is generated from local no-CTS OpenLane run artifacts.

## Run

```text
run_dir: /home/mehtama1/eda-tools/OpenLane/designs/aimc_scheduler_governor_physical/runs/aimc_scheduler_governor_no_cts_8ns
flow_status: flow completed
total_runtime: 0h1m43s0ms
routed_runtime: 0h1m13s0ms
synth_cell_count: 266
TotalCells: 1429
CoreArea_um^2: 10935.488
DIEAREA_mm^2: 0.014948134799999999
wire_length: 8131
vias: 2259
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 6.5
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

## Final Artifact Check

```text
signoff/aimc_scheduler_governor_physical.gds: present
signoff/aimc_scheduler_governor_physical.lef: present
signoff/aimc_scheduler_governor_physical.lib: present
signoff/aimc_scheduler_governor_physical.sdf: present
signoff/aimc_scheduler_governor_physical.spice: present
routing/aimc_scheduler_governor_physical.def: present
routing/aimc_scheduler_governor_physical.nl.v: present
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
max_slew_violations: 59
max_fanout_violations: 5
max_cap_violations: 0
clock_fanout: 58
```

## Interpretation

The no-CTS flow asks whether the combined scheduler/governor policy can settle between one input register boundary and one output register boundary.

At 5 ns the answer is no: the physical route is clean, but setup fails. At 8 ns the answer is yes for this exploratory wrapper: the flow completes with clean DRC, LVS, antenna, setup, and hold checks. It still does not prove clock-tree signoff.
