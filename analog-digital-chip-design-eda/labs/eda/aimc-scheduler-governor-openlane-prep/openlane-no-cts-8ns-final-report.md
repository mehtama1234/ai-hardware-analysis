# AIMC Scheduler/Governor 8 ns No-CTS OpenLane Report

This report records the 8 ns no-CTS OpenLane run for `aimc_scheduler_governor_physical`, the registered wrapper around the integrated scheduler/governor policy.

## Command

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_scheduler_governor_no_cts_8ns CONFIG_NAME=config_no_cts_8ns AIMC_OPENLANE_PREP=aimc-scheduler-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_scheduler_governor_physical AIMC_OPENLANE_RTL=aimc_scheduler_governor.v ./scripts/run_aimc_openlane_flow.sh
```

## Result

```text
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

## What Passed

The 8 ns run completed. It produced routed and signoff artifacts:

```text
aimc_scheduler_governor_physical.gds
aimc_scheduler_governor_physical.lef
aimc_scheduler_governor_physical.lib
aimc_scheduler_governor_physical.sdf
aimc_scheduler_governor_physical.spice
aimc_scheduler_governor_physical.def
aimc_scheduler_governor_physical.nl.v
```

The physical checks are clean:

```text
Total Magic DRC violations is 0
Design is LVS clean.
Pin violations: 0
Net violations: 0
```

The extracted timing summary is clean at the relaxed period:

```text
setup_violating_paths_found: false
max_cap_violations: 0
```

## First-Principles Reading

The 8 ns result says something specific. It does not say the analog foundation-model accelerator is solved. It says the digital referee around analog compute can be turned into physical geometry when the timing question is made honest.

The block receives a proposed analog service event. It then asks:

```text
is a usable tile available?
is the requested tile healthy enough?
is maintenance more urgent than service?
is the residual error already too high?
has calibration become too old?
is this path too sensitive for analog error?
would this token spend too much accumulated error?
```

The final output is the control-plane answer:

```text
analog
digital fallback
recalibrate
probe
```

This is the practical bridge between analog in-memory compute and a serving system. The crossbar can multiply through conductance and current, but it cannot decide when its own answer should be trusted. The digital policy makes that trust decision explicit. It turns analog use into a checked choice instead of a permanent routing assumption.

The 5 ns and 8 ns runs together are more valuable than a single success. They show the measured cost of making the policy explicit. A bare scheduler is small. A bare governor is small. The integrated policy has a longer path because it must combine availability, health, calibration age, sensitivity, and accumulated error before it allows analog service.

## Remaining Boundary

```text
max_slew_violations: 59
max_fanout_violations: 5
clock_fanout: 58
```

This is still a no-CTS run. The clock tree is not a signed-off object, and the slew/fanout warnings should be addressed before this block is treated as a production macro.

The bounded claim is:

```text
At an 8 ns exploratory no-CTS timing boundary, the registered integrated scheduler/governor wrapper completes OpenLane with clean DRC, LVS, antenna, setup, and hold checks.
```

The next design question is architectural. If the serving system needs a 5 ns policy cycle, the policy should be pipelined or partly precomputed. If 8 ns is acceptable for the control-plane cadence, this block can remain a single-cycle referee around a faster analog datapath.
