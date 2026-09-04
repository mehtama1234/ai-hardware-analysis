# AIMC Scheduler/Governor OpenLane Metrics Summary

This file is generated from local CTS-enabled OpenLane run artifacts.

## Run

```text
run_dir: /home/mehtama1/eda-tools/OpenLane/designs/aimc_scheduler_governor_pipelined/runs/aimc_scheduler_governor_pipelined_5ns_control_reset_fanout20
flow_status: flow completed
total_runtime: 0h2m42s0ms
routed_runtime: 0h2m11s0ms
synth_cell_count: 299
TotalCells: 1562
CoreArea_um^2: 11911.424
DIEAREA_mm^2: 0.0158750025
wire_length: 8222
vias: 2427
wns: -0.33
tns: -2.04
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 4.99
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
max_fanout_violations: 0
max_cap_violations: 0
clock_fanout: missing
```

## Interpretation

The CTS-enabled flow asks whether the scheduler/governor decision can be routed as a clocked object at the selected clock period without hiding a timing, fanout, DRC, LVS, or antenna failure.

A passing run does not prove the full analog accelerator. It proves a narrower fact: this digital referee can be turned into placed-and-routed logic under the stated constraints. If fanout still violates the selected limit, that remains a physical packaging boundary. If fanout is clean, the remaining boundaries are small-core power-grid packaging, calibrated IR-drop source placement, and integration with analog tile timing models.
