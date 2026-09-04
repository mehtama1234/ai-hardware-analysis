# AIMC Scheduler/Governor OpenLane Metrics Summary

This file is generated from local CTS-enabled OpenLane run artifacts.

## Run

```text
run_dir: /home/mehtama1/eda-tools/OpenLane/designs/aimc_scheduler_governor_physical/runs/aimc_scheduler_governor_cts_8ns_control_reset_fanout20
flow_status: flow completed
total_runtime: 0h2m50s0ms
routed_runtime: 0h2m20s0ms
synth_cell_count: 266
TotalCells: 1333
CoreArea_um^2: 10231.0624
DIEAREA_mm^2: 0.013943692425
wire_length: 7530
vias: 2166
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 6.04
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
max_slew_violations: 0
max_fanout_violations: 0
max_cap_violations: 0
clock_fanout: missing
```

## Interpretation

The CTS-enabled flow proves that the registered-boundary integrated scheduler/governor wrapper can pass synthesis, placement, CTS, routing, extraction, GDS generation, DRC, LVS, antenna checks, setup checks, and hold checks in this exploratory setup.

It is not yet a production macro. If the selected run still reports fanout violations, those remain part of the packaging boundary. Otherwise the remaining physical-design boundary is small-core power-grid packaging, IR-drop source-location setup, and eventual integration with analog tile timing models.
