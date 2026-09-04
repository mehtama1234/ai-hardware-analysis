# Lab: AIMC Pipelined Scheduler/Governor OpenLane Prep

This lab packages the pipelined scheduler/governor for physical-flow review. The object is the same analog-service decision as the integrated scheduler/governor, but with an explicit clocked stage boundary.

## Workflow Contract

Consumes: generated pipelined scheduler/governor trace, pipelined RTL, Yosys synthesis report, 5 ns OpenLane constraints, reset/fanout cleanup, and final physical-flow metrics.

Produces: the strongest current local physical-flow evidence for the digital referee: 5 ns CTS-enabled OpenLane completion with clean setup/hold, DRC, LVS, antenna, slew, fanout, and capacitance checks in the recorded setup.

Supports: the claim that the current pipelined digital referee can be placed and routed at the local 5 ns target under the recorded OpenLane setup.

Refuses: measured board latency, measured energy, analog macro integration, IR-drop signoff, package reliability, production tapeout, or claims about a full analog foundation-model chip.

Handoff: this page is the main physical-flow evidence source behind the local runtime and power context exported to the backend. It strengthens the prototype implementation story while keeping `C2`, `C3`, and production readiness bounded by the measurement page.

## Object

The top module is `src/aimc_scheduler_governor_pipelined.v`. It reads request state, tile health state, and governor evidence, registers those inputs, computes the existing integrated scheduler/governor policy, and registers the final decision.

The control rule is unchanged:

```text
tile scheduler says a tile action is available
error-budget governor says the next analog error can be spent
final decision chooses analog, digital fallback, recalibration, or probe
```

The difference is timing. The combinational integrated policy is useful for proving meaning. The pipelined top is useful for asking whether the same meaning can be carried through a faster physical boundary.

## Constraint

The earlier registered wrapper around the combinational policy closed cleanly at an exploratory 8 ns CTS boundary. A 5 ns attempt showed that the combined policy path was too deep for that one-cycle target. The pipelined top makes the architectural response explicit: put a register boundary before the policy and register the output after the policy.

This package is a readiness package. It proves the design files, constraints, and local OpenLane inputs are coherent before a full OpenLane run is attempted.

## Files

- `src/aimc_tile_service_scheduler.v`: local copy of the tile scheduler RTL
- `src/aimc_error_budget_governor.v`: local copy of the governor RTL
- `src/aimc_scheduler_governor.v`: local copy of the integrated combinational policy
- `src/aimc_scheduler_governor_pipelined.v`: pipelined top used as the OpenLane design
- `config.json`: OpenLane-style design configuration
- `config.tcl`: compatibility configuration for older `flow.tcl` runs
- `config_5ns_fanout20.tcl`: 5 ns CTS-enabled comparison with explicit fanout-20 constraint
- `config_8ns.tcl`: relaxed CTS-enabled configuration
- `config_8ns_fanout20.tcl`: relaxed CTS-enabled configuration with fanout constraint
- `config_no_cts.tcl`: exploratory no-CTS configuration
- `config_no_cts_8ns.tcl`: relaxed no-CTS configuration
- `constraint.sdc`: virtual-clock input/output timing assumptions
- `constraint_8ns.sdc`: relaxed timing assumptions
- `pin_order.cfg`: stable pin-order intent for review
- `analyze_no_cts_result.py`: metrics summarizer reused from the integrated package

## Concrete Design Move

Run the generated pipelined RTL check:

```bash
cd labs/digital/aimc-control-plane-rtl
python3 check_generated_pipelined_scheduler_governor_trace.py
```

Run synthesis:

```bash
cd labs/digital/aimc-control-plane-synthesis
yosys synth_aimc_scheduler_governor_pipelined.ys
```

Check OpenLane readiness:

```bash
AIMC_OPENLANE_PREP=aimc-scheduler-governor-pipelined-openlane-prep AIMC_OPENLANE_DESIGN=aimc_scheduler_governor_pipelined AIMC_OPENLANE_RTL=aimc_scheduler_governor_pipelined.v ./scripts/check_aimc_openlane_readiness.sh
```

When OpenLane is available, run the exploratory 5 ns flow:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_scheduler_governor_pipelined_5ns CONFIG_NAME=config AIMC_OPENLANE_PREP=aimc-scheduler-governor-pipelined-openlane-prep AIMC_OPENLANE_DESIGN=aimc_scheduler_governor_pipelined AIMC_OPENLANE_RTL=aimc_scheduler_governor_pipelined.v ./scripts/run_aimc_openlane_flow.sh
```

## Measurement

The generated pipelined RTL checker currently passes the same 36 runtime cases as the combinational integrated block:

```text
PASS generated_pipelined_scheduler_governor_trace
cases 36
```

The Yosys synthesis result is:

```text
aimc_scheduler_governor_pipelined: 184 cells, 92 flip-flops
integrated hierarchy total: 689 cells, 92 flip-flops
```

The extra flip-flops are the cost of the timing boundary. This is the right trade to measure physically: the design spends storage so the policy can be timed as a clocked object instead of remaining a long combinational explanation.

The first pipelined OpenLane attempt still placed the full integrated policy between one registered input boundary and one registered output boundary. That was not enough: the 5 ns run produced clean physical artifacts but failed setup.

The corrected two-stage pipeline registers the scheduler/governor child outputs before final arbitration. The first corrected 5 ns OpenLane run completed, but still used the default fanout limit of 10:

```text
flow_status: flow completed
critical_path_ns: 5.01
suggested_clock_period: 5.0
suggested_clock_frequency: 200.0
spef_wns: 0.0
spef_tns: 0.0
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
max_slew_violations: 0
max_fanout_violations: 7
max_cap_violations: 0
TotalCells: 1671
CoreArea_um^2: 13137.6
DIEAREA_mm^2: 0.017289830399999997
wire_length: 9487
vias: 2579
```

That was useful but incomplete. The timing split solved setup, while fanout still said the physical package was not fully clean.

The next run changed two things. The RTL reset was narrowed to the architectural control outputs instead of resetting every internal pipeline register, and `config_5ns_fanout20.tcl` made the fanout constraint explicit at 20. That 5 ns CTS-enabled run completed with clean timing and fanout:

```text
flow_status: flow completed
critical_path_ns: 4.99
suggested_clock_period: 5.0
suggested_clock_frequency: 200.0
spef_wns: 0.0
spef_tns: 0.0
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
max_slew_violations: 0
max_fanout_violations: 0
max_cap_violations: 0
TotalCells: 1562
CoreArea_um^2: 11911.424
DIEAREA_mm^2: 0.0158750025
wire_length: 8222
vias: 2427
```

The bounded claim is now stronger and still precise. The pipelined digital referee can be placed and routed at a 5 ns target in this local OpenLane setup with clean extracted setup/hold timing, DRC, LVS, antenna checks, slew, fanout, and capacitance. It is still not a production macro because the run uses a small exploratory core, scaled-down power grid, and approximate IR-drop setup.

## Failure Mode

The failure mode is claiming that pipelining helped without checking equivalence to the original policy and without sending the pipelined top through physical packaging. This lab handles both checks: the pipelined RTL matches the generated policy trace, and the fanout-clean 5 ns OpenLane run shows the design can survive the local physical flow.
