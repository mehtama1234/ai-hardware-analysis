# Lab: AIMC Micro-Tile Controller OpenLane Prep

This lab packages the integrated AIMC micro-tile controller for physical-flow evidence.

The object is the digital boundary that connects three decisions:

```text
operation placement
analog tile readout correction
final accept or fallback
```

The analog array is still abstract. The physical object here is the controller that decides whether a corrected analog tile result is allowed to affect model state.

## Object

The top module is `aimc_micro_tile_controller`.

It instantiates:

- `aimc_operation_partition`
- `aimc_tile_readout`

The controller does not trust analog output on the same cycle that it chooses analog placement. It starts a readout, waits one cycle, then accepts the corrected value or forces digital fallback.

The top-level interface now includes a tile identifier plus accepted/fallback accounting. A readout failure records `last_fallback_tile_id` and increments `fallback_count`; a valid readout increments `accepted_count`; residual and stale-calibration failures increment their own counters. The physical controller can now expose whether the analog path is mostly accepted or mostly refused, and whether refusal is caused by bad correction or stale evidence.

The matching first-principles article is `docs/concepts/analog-placement-is-not-analog-acceptance.md`.

## Files

- `src/aimc_micro_tile_controller.v`: integrated controller top
- `src/aimc_operation_partition.v`: operation placement rule
- `src/aimc_tile_readout.v`: ADC-code correction and fallback rule
- `config.json`: OpenLane-style design configuration
- `config.tcl`: compatibility configuration for local OpenLane `flow.tcl`
- `config_no_cts.tcl`: no-CTS exploratory configuration
- `constraint.sdc`: timing constraints
- `src/constraint.sdc`: constraint copy for older OpenLane design-folder conventions
- `pin_order.cfg`: stable pin-order intent
- `openlane-no-cts-final-report.md`: measured no-CTS physical-flow result
- `analyze_no_cts_result.py`: regenerates a compact metrics, artifact, manufacturability, and fanout summary
- `openlane-no-cts-metrics-summary.md`: generated compact summary

## Concrete Design Move

Check readiness:

```bash
AIMC_OPENLANE_PREP=aimc-micro-tile-controller-openlane-prep AIMC_OPENLANE_DESIGN=aimc_micro_tile_controller ./scripts/check_aimc_openlane_readiness.sh
```

Run the no-CTS exploratory flow:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_micro_tile_controller_recovery_probe_no_cts CONFIG_NAME=config_no_cts AIMC_OPENLANE_PREP=aimc-micro-tile-controller-openlane-prep AIMC_OPENLANE_DESIGN=aimc_micro_tile_controller ./scripts/run_aimc_openlane_flow.sh
```

Regenerate the compact evidence summary:

```bash
cd labs/eda/aimc-micro-tile-controller-openlane-prep
python3 analyze_no_cts_result.py
```

CTS is not the first target in this lab because the same local OpenLane/OpenROAD CTS characterization behavior already appeared on a tiny clocked toy design. The bounded goal here is placement, routing, extraction, manufacturability checks, and timing-report evidence without claiming clock-tree signoff.

## Measurement

The first useful physical measurements are:

- synthesis cell count
- floorplan area
- placement legality
- route completion
- worst negative slack under the exploratory setup
- DRC violations
- LVS result if signoff reaches that stage
- antenna violations

Current no-CTS run summary:

```text
flow_status: flow completed
synth_cell_count: 1338
TotalCells: 7612
CoreArea_um^2: 56168.8704
DIEAREA_mm^2: 0.06449743079999999
wire_length: 50119
vias: 11936
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 8.57
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
max slew violation count: 111
max fanout violation count: 34
max capacitance violation count: 1
```

This run is physical evidence for the expanded controller interface with `tile_id`, `last_fallback_tile_id`, `fallback_count`, `accepted_count`, `residual_fallback_count`, `stale_fallback_count`, registered `tile_health_action`, and recovery controls for calibration and probe evidence. The useful result is bounded: the recovery/probe controller passes no-CTS placement, routing, extraction, GDS generation, DRC, LVS, and antenna checks. The remaining physical-design object is clock-tree signoff plus slew, fanout, and one max-capacitance violation.

The linter reported zero warnings after explicit signed-width cleanup in the tile readout arithmetic and reason-code path.

The final views include GDS, LEF, Liberty, SDF, and SPICE. This is useful physical evidence for the integrated digital controller shape, with the CTS boundary still open.

## Failure Mode

The failure mode is claiming a finished chip block from a no-CTS flow. This lab can produce useful physical-flow evidence, but it does not prove clock-tree signoff. The local CTS issue must be resolved before the controller is treated as physically closed.
