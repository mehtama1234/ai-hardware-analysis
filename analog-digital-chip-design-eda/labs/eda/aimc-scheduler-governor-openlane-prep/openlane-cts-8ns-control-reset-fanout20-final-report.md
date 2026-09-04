# AIMC Scheduler/Governor Control-Reset Fanout20 CTS Report

This report records the best integrated scheduler/governor physical-flow result so far. It uses the control-reset wrapper and the 8 ns fanout-20 CTS configuration.

## Command

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_scheduler_governor_cts_8ns_control_reset_fanout20 CONFIG_NAME=config_8ns_fanout20 AIMC_OPENLANE_PREP=aimc-scheduler-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_scheduler_governor_physical AIMC_OPENLANE_RTL=aimc_scheduler_governor.v ./scripts/run_aimc_openlane_flow.sh
```

## Result

```text
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
max_slew_violations: 0
max_fanout_violations: 0
max_cap_violations: 0
```

## What Changed

The first 8 ns CTS run reset every wrapper register. That made reset a high-fanout physical net. The control-reset wrapper changes the reset boundary:

```text
reset final_decision and final_reason
do not reset internal evidence pipeline registers
do not reset selected_tile or next_cumulative_error_q8
```

This is not a functional shortcut. It separates safe control state from data state.

`final_decision` and `final_reason` are the outputs that tell the serving system whether analog work is allowed. They need a deterministic reset value. `selected_tile` and `next_cumulative_error_q8` are meaningful only after the policy has sampled valid evidence. Resetting them made the physical net larger without adding useful safety.

## Comparison

```text
original 8 ns CTS:
  TotalCells: 1441
  CoreArea_um^2: 10935.488
  wire_length: 8607
  vias: 2372
  critical_path_ns: 6.14
  max_fanout_violations: 5

control-reset fanout20 8 ns CTS:
  TotalCells: 1333
  CoreArea_um^2: 10231.0624
  wire_length: 7530
  vias: 2166
  critical_path_ns: 6.04
  max_fanout_violations: 0
```

## First-Principles Reading

A reset is not free. In RTL it can look like a harmless way to make every register start at zero. In physical design, it becomes a wire that must reach many storage elements. If the reset drives too many sinks, the design spends buffers, area, wire, and timing effort on a state that may not need to be controlled.

The integrated scheduler/governor shows this clearly. The safe state of the block is not "every internal number equals zero." The safe state is:

```text
external control says do not use analog compute
external reason says there is no valid service decision yet
```

Once that is true, internal evidence registers can be unreset pipeline storage. They will be overwritten by sampled tile and error evidence before their values are trusted.

This is the right lesson for analog foundation-model hardware. The digital referee must be conservative at the boundary where it authorizes analog compute. It does not need to force every internal scratch value to a reset value. Physical design rewards that distinction.

## Bounded Claim

The useful claim is:

```text
At an 8 ns control-plane timing boundary with fanout-20 packaging, the registered integrated scheduler/governor wrapper completes a CTS-enabled OpenLane flow with clean routing DRC, Magic DRC, LVS, antenna checks, setup checks, hold checks, max slew, max fanout, and max capacitance checks.
```

The remaining objects are:

```text
small-core power-grid packaging
IR-drop source-location setup
macro integration with analog tile timing and loading models
```
