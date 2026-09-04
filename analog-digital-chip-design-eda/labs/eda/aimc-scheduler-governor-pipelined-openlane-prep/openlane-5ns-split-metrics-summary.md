# AIMC Pipelined Scheduler/Governor 5 ns OpenLane Metrics Summary

This file is generated from local OpenLane run artifacts for the corrected two-stage pipelined scheduler/governor.

## Run

```text
run_dir: /home/mehtama1/eda-tools/OpenLane/designs/aimc_scheduler_governor_pipelined/runs/aimc_scheduler_governor_pipelined_5ns_split
flow_status: flow completed
total_runtime: 0h3m14s0ms
routed_runtime: 0h2m40s0ms
synth_cell_count: 299
TotalCells: 1671
CoreArea_um^2: 13137.6
DIEAREA_mm^2: 0.017289830399999997
wire_length: 9487
vias: 2579
wns: -0.39
tns: -2.47
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 5.01
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
signoff/aimc_scheduler_governor_pipelined.gds: present
signoff/aimc_scheduler_governor_pipelined.lef: present
signoff/aimc_scheduler_governor_pipelined.lib: present
signoff/aimc_scheduler_governor_pipelined.sdf: present
signoff/aimc_scheduler_governor_pipelined.spice: present
routing/aimc_scheduler_governor_pipelined.def: present
routing/aimc_scheduler_governor_pipelined.nl.v: present
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
max_fanout_violations: 7
max_cap_violations: 0
clock_fanout: missing
```

## Interpretation

The flow asks whether the corrected two-stage scheduler/governor policy can close at a 5 ns clock boundary after synthesis, placement, CTS, routing, extraction, and signoff checks.

For this run, setup and hold are clean at the final extracted timing check. The final metric row still reports earlier WNS/TNS fields from intermediate timing stages, but `spef_wns` and `spef_tns` are both zero and the final signoff checks report no setup paths. Detailed routing DRC, Magic DRC, LVS, and antenna checks are also clean.

The remaining boundary is max fanout. The run reports seven max-fanout violations at the typical corner, plus the same small-core power-grid scaling and approximate IR-drop setup warnings seen in the earlier exploratory runs. The timing split solved the 5 ns setup problem; it did not finish reset/control fanout cleanup.
