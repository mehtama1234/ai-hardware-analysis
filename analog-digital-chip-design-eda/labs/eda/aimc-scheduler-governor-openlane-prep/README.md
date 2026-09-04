# Lab: AIMC Scheduler/Governor OpenLane Prep

This lab packages the integrated scheduler/governor for physical-flow review. The object is the combined control decision for analog service:

```text
tile scheduler says a tile action is available
error-budget governor says the next analog error can be spent
final decision chooses analog, digital fallback, recalibration, or probe
```

## Workflow Contract

Consumes: scheduler RTL, error-budget governor RTL, integrated policy RTL, generated integrated trace, Yosys synthesis report, clocked wrapper, OpenLane constraints, and physical-flow reports.

Produces: one-cycle integrated-control physical-flow evidence, measured 5 ns failure boundary, completed 8 ns boundary, CTS-enabled result, and reset/fanout cleanup lesson.

Supports: the claim that the combined analog-service decision can be made into clean local physical-flow evidence at the relaxed 8 ns boundary.

Refuses: proving the 5 ns target without pipelining, measured board latency, measured energy, analog macro integration, production timing closure, or signoff.

Handoff: this page explains why the pipelined scheduler/governor exists. The one-cycle integrated block teaches the timing cost of combining tile availability and model-error spending in one decision.

## Object

The pure integrated block is `src/aimc_scheduler_governor.v`. It instantiates:

```text
aimc_tile_service_scheduler
aimc_error_budget_governor
```

The scheduler decides which tile action is available. The governor decides whether analog error can be spent. The integrated block allows analog only when both decisions agree.

## Constraint

The integrated block is combinational. A physical flow still needs a clocked boundary. The OpenLane package uses `aimc_scheduler_governor_physical`, which registers the inputs and outputs around the combined policy:

```text
registered tile state and error evidence -> scheduler/governor policy -> registered final decision
```

That wrapper does not change the control rule. It gives timing analysis a concrete question:

```text
Can the combined scheduler/governor decision settle between one set of registers and the next?
```

## Files

- `src/aimc_tile_service_scheduler.v`: local copy of the tile scheduler RTL
- `src/aimc_error_budget_governor.v`: local copy of the governor RTL
- `src/aimc_scheduler_governor.v`: local copy of the integrated combinational RTL
- `src/aimc_scheduler_governor_physical.v`: clocked physical wrapper
- `config.json`: OpenLane-style design configuration
- `config.tcl`: compatibility configuration for older `flow.tcl` runs
- `config_no_cts.tcl`: exploratory no-CTS configuration
- `config_8ns.tcl`: relaxed CTS-enabled configuration for the measured integrated critical path
- `config_8ns_fanout20.tcl`: CTS-enabled 8 ns configuration with a fanout-20 exploratory packaging limit
- `config_no_cts_8ns.tcl`: relaxed no-CTS configuration for the measured integrated critical path
- `constraint.sdc`: virtual-clock input/output timing assumptions
- `constraint_8ns.sdc`: relaxed timing assumptions for exploratory closure
- `src/constraint.sdc`: SDC copy for older OpenLane design-folder conventions
- `pin_order.cfg`: stable pin-order intent for review
- `openlane-no-cts-5ns-timing-boundary-report.md`: measured 5 ns failure boundary
- `openlane-no-cts-8ns-final-report.md`: measured 8 ns completed-flow boundary
- `openlane-no-cts-5ns-metrics-summary.md`: generated metrics summary for the failed 5 ns run
- `openlane-no-cts-8ns-metrics-summary.md`: generated metrics summary for the completed 8 ns run
- `openlane-cts-8ns-final-report.md`: measured 8 ns CTS-enabled completed-flow boundary
- `openlane-cts-8ns-metrics-summary.md`: generated metrics summary for the CTS-enabled 8 ns run
- `openlane-cts-8ns-control-reset-fanout20-final-report.md`: best measured CTS-enabled result after reset-boundary cleanup
- `openlane-cts-8ns-control-reset-fanout20-metrics-summary.md`: generated metrics summary for the best CTS-enabled result
- `analyze_no_cts_result.py`: local metrics summarizer for OpenLane run artifacts

## Concrete Design Move

Run the generated integrated trace first:

```bash
cd labs/digital/aimc-control-plane-rtl
python3 check_generated_integrated_scheduler_governor_trace.py
```

Run synthesis for the pure integrated block:

```bash
cd labs/digital/aimc-control-plane-synthesis
yosys synth_aimc_scheduler_governor.ys
```

Check OpenLane readiness:

```bash
AIMC_OPENLANE_PREP=aimc-scheduler-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_scheduler_governor_physical AIMC_OPENLANE_RTL=aimc_scheduler_governor.v ./scripts/check_aimc_openlane_readiness.sh
```

When OpenLane is available, run the exploratory no-CTS flow:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_scheduler_governor_no_cts CONFIG_NAME=config_no_cts AIMC_OPENLANE_PREP=aimc-scheduler-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_scheduler_governor_physical AIMC_OPENLANE_RTL=aimc_scheduler_governor.v ./scripts/run_aimc_openlane_flow.sh
```

If the one-cycle 5 ns target fails setup, run the relaxed 8 ns no-CTS flow:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_scheduler_governor_no_cts_8ns CONFIG_NAME=config_no_cts_8ns AIMC_OPENLANE_PREP=aimc-scheduler-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_scheduler_governor_physical AIMC_OPENLANE_RTL=aimc_scheduler_governor.v ./scripts/run_aimc_openlane_flow.sh
```

Then run the 8 ns CTS-enabled flow:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_scheduler_governor_cts_8ns CONFIG_NAME=config_8ns AIMC_OPENLANE_PREP=aimc-scheduler-governor-openlane-prep AIMC_OPENLANE_DESIGN=aimc_scheduler_governor_physical AIMC_OPENLANE_RTL=aimc_scheduler_governor.v ./scripts/run_aimc_openlane_flow.sh
```

## Measurement

The pure integrated synthesis currently reports:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 601
```

The no-flip-flop result is intentional for the pure integrated policy. The physical wrapper adds registers only to define the timing boundary.

The 5 ns no-CTS OpenLane run produced routed/signoff artifacts and passed physical legality checks, but failed setup:

```text
flow_status: flow failed
critical_path_ns: 6.41
spef_wns: -1.08
spef_tns: -11.02
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
```

The failing path runs from registered calibration-age evidence into a registered final reason bit. That means the measured object is the depth of the combined trust decision, not just routing difficulty.

The relaxed 8 ns no-CTS run completed:

```text
flow_status: flow completed
critical_path_ns: 6.5
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
TotalCells: 1429
CoreArea_um^2: 10935.488
DIEAREA_mm^2: 0.014948134799999999
wire_length: 8131
vias: 2259
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
```

That result proves a bounded claim: at an 8 ns exploratory timing boundary, the registered integrated scheduler/governor wrapper can be synthesized, placed, routed, extracted, streamed to GDS, and pass DRC, LVS, antenna, setup, and hold checks. It does not prove CTS signoff.

The 8 ns CTS-enabled run also completed:

```text
flow_status: flow completed
critical_path_ns: 6.14
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
TotalCells: 1441
CoreArea_um^2: 10935.488
DIEAREA_mm^2: 0.014948134799999999
wire_length: 8607
vias: 2372
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
```

That stronger result proves the registered integrated policy can survive clock tree synthesis at the relaxed 8 ns boundary in this exploratory setup. It still showed max-fanout warnings because the reset net reached too many wrapper registers.

The control-reset wrapper narrows reset to the externally meaningful control outputs. With `config_8ns_fanout20.tcl`, the improved CTS-enabled run completed with no setup, hold, max slew, max fanout, max capacitance, DRC, LVS, or antenna violations:

```text
flow_status: flow completed
critical_path_ns: 6.04
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
TotalCells: 1333
CoreArea_um^2: 10231.0624
DIEAREA_mm^2: 0.013943692425
wire_length: 7530
vias: 2166
max_slew_violations: 0
max_fanout_violations: 0
max_cap_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
```

The lesson is that reset is a physical net, not only a simulation convenience. Safe control state needs reset. Internal evidence registers can be overwritten before use.

## Failure Mode

The failure mode is letting either child block pretend to be the whole control plane. The scheduler can find a tile that the governor should still reject. The governor can approve an error spend when no tile is actually available. The integrated block makes the final decision depend on both.

The physical failure mode is also clear. If the serving system demands a 5 ns policy cycle, the combined decision should be pipelined or partly precomputed. If an 8 ns policy cycle is acceptable, this block can remain a single-cycle digital referee around the analog datapath, with power-grid and IR-drop setup still left for the next physical-design pass.
