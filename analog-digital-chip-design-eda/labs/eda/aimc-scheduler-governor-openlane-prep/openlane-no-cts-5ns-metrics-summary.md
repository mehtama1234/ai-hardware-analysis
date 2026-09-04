# AIMC Scheduler/Governor OpenLane Metrics Summary

This file is generated from local no-CTS OpenLane run artifacts.

## Run

```text
run_dir: /home/mehtama1/eda-tools/OpenLane/designs/aimc_scheduler_governor_physical/runs/aimc_scheduler_governor_no_cts
flow_status: flow failed
total_runtime: 0h1m50s0ms
routed_runtime: 0h1m17s0ms
synth_cell_count: 266
TotalCells: 1481
CoreArea_um^2: 11369.654400000001
DIEAREA_mm^2: 0.015293996625000002
wire_length: 8778
vias: 2369
wns: -1.07
tns: -8.63
spef_wns: -1.08
spef_tns: -11.02
critical_path_ns: 6.41
suggested_clock_period: 6.08
suggested_clock_frequency: 164.4736842105263
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
setup_violating_paths_found: true
max_slew_violations: 59
max_fanout_violations: 2
max_cap_violations: 0
clock_fanout: 58
```

## Interpretation

The no-CTS flow asks whether the combined scheduler/governor policy can settle between one input register boundary and one output register boundary.

At 5 ns the answer is no: the physical route is clean, but setup fails. At 8 ns the answer is yes for this exploratory wrapper: the flow completes with clean DRC, LVS, antenna, setup, and hold checks. It still does not prove clock-tree signoff.
