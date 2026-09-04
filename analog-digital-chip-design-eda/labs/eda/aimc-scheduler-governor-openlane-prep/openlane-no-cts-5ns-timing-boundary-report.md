# AIMC Scheduler/Governor 5 ns Timing Boundary Report

This report records the 5 ns no-CTS OpenLane run for `aimc_scheduler_governor_physical`, the registered wrapper around the integrated scheduler/governor policy.

## Command

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_scheduler_governor_no_cts CONFIG_NAME=config_no_cts AIMC_OPENLANE_PREP=aimc-scheduler-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_scheduler_governor_physical AIMC_OPENLANE_RTL=aimc_scheduler_governor.v ./scripts/run_aimc_openlane_flow.sh
```

## Result

```text
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

## What Failed

The run produced final layout views and passed the physical checks that ask whether the shapes are legal and match the netlist:

```text
Total Magic DRC violations is 0
Design is LVS clean.
Pin violations: 0
Net violations: 0
```

The failure is timing. The routed design could not make the combined policy decision within one 5 ns cycle. The worst path reported by extracted timing goes from a registered calibration-age input to a registered final-reason output:

```text
startpoint: policy.drift_age[0]
endpoint: policy.final_reason[1]
data arrival time: 6.41 ns
data required time: 5.34 ns
slack: -1.08 ns
```

## First-Principles Reading

The scheduler/governor block asks one question:

```text
Should this token use analog compute now?
```

That question is not a single comparison. It joins two forms of evidence.

The scheduler evidence asks whether a tile can serve the request. It looks at tile health, requested tile identity, busy state, and maintenance budget.

The governor evidence asks whether analog error can be spent. It looks at residual error, calibration age, path sensitivity, and cumulative error.

The final reason code is where those two evidence streams meet. A reason bit is not just a label. It is the encoded explanation of the control decision. When `drift_age[0]` influences `final_reason[1]`, the design is deciding whether old calibration should turn an analog request into fallback or recalibration. That path crosses several policy tests before it reaches the output register.

At 5 ns, the physical layout says the logic is too deep for a one-cycle decision. This is useful evidence. It tells us that the integrated control policy is no longer a tiny combinational selector. It is becoming a real control-plane object with a measured latency boundary.

## Remaining Boundary

```text
setup_violating_paths_found: true
max_slew_violations: 59
max_fanout_violations: 2
max_cap_violations: 0
clock_fanout: 58
```

This is a no-CTS run, so the clock tree is not a signed-off object. The useful claim is bounded:

```text
The integrated scheduler/governor can be synthesized, placed, routed, extracted, streamed to GDS, and pass DRC, LVS, and antenna checks, but the one-cycle 5 ns policy path does not close.
```

The next design move is not to hide the failure. It is to choose the architecture boundary: relax the cycle time, pipeline the policy, precompute some governor evidence, or split decision and explanation into separate timing paths.
