# AIMC Micro-Tile Controller No-CTS OpenLane Report

This report records the no-CTS exploratory physical flow for `aimc_micro_tile_controller` after adding tile identity, accept/fallback counters, reason-specific fallback counters, a registered `tile_health_action` policy output, and explicit recovery controls for recalibration and probing.

## Command

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_micro_tile_controller_recovery_probe_no_cts CONFIG_NAME=config_no_cts AIMC_OPENLANE_PREP=aimc-micro-tile-controller-openlane-prep AIMC_OPENLANE_DESIGN=aimc_micro_tile_controller ./scripts/run_aimc_openlane_flow.sh
```

## Run Directory

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_micro_tile_controller/runs/aimc_micro_tile_controller_recovery_probe_no_cts
```

## Result

```text
flow_status: flow completed
total_runtime: 0h4m41s0ms
routed_runtime: 0h3m14s0ms
synth_cell_count: 1338
TotalCells: 7612
CoreArea_um^2: 56168.8704
DIEAREA_mm^2: 0.06449743079999999
wire_length: 50119
vias: 11936
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 8.57
suggested_clock_period: 12.0
suggested_clock_frequency: 83.33333333333333
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
```

The linter reported:

```text
0 errors
0 warnings
```

## Final Views

The run produced final physical and timing views under:

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_micro_tile_controller/runs/aimc_micro_tile_controller_recovery_probe_no_cts/results/signoff
```

Important files include:

```text
aimc_micro_tile_controller.gds
aimc_micro_tile_controller.lef
aimc_micro_tile_controller.lib
aimc_micro_tile_controller.sdf
aimc_micro_tile_controller.spice
```

## Manufacturability

The manufacturability report says:

```text
Total Magic DRC violations is 0
Design is LVS clean.
Pin violations: 0
Net violations: 0
```

## Remaining Boundary

This is a no-CTS run. It does not prove clock-tree signoff.

The final STA report still has max-slew, max-fanout, and max-capacitance violations:

```text
max slew violation count 111
max fanout violation count 34
max cap violation count 1
clk limit 10, fanout 110
```

The setup and hold checks reported no violating paths after extraction:

```text
No paths found.
```

The useful claim is therefore bounded:

```text
The recovery/probe micro-tile controller can be synthesized, placed, routed, extracted, streamed to GDS, and pass DRC, LVS, and antenna checks in the no-CTS exploratory flow.
```

The unresolved object remains:

```text
clock-tree signoff, slew cleanup, fanout cleanup, and the one max-capacitance violation
```
