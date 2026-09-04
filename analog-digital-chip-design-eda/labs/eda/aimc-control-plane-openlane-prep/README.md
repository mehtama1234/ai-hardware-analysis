# Lab: AIMC Control Plane OpenLane Prep

This lab packages the AIMC control-plane RTL for a future physical-design run. It does not claim that placement, routing, timing closure, DRC, or LVS have been completed. The local tool check found Yosys and Icarus Verilog on `PATH`, but not OpenLane, OpenROAD, OpenSTA, or a Liberty timing library.

## Workflow Contract

Consumes: control-plane RTL, timing constraints, OpenLane package files, local tool availability, and Yosys lowering evidence.

Produces: an OpenLane-ready design package, readiness result, exploratory physical-flow reports, and a compact metrics summary.

Supports: the claim that the request-level controller has a named physical-flow package and can be reviewed as a layout candidate in the local open-source flow.

Refuses: measured board latency, measured power, clean clock-tree signoff, analog macro integration, production tapeout, and silicon behavior.

Handoff: this page is an early physical-flow boundary. It feeds the EDA evidence story, but stronger claim readiness should use the later scheduler/governor pages and the board/power measurement boundary.

## Object

The object being prepared is the digital controller that chooses:

```text
digital fallback
analog projection
analog batched decode
```

The physical-design question is whether this controller can become placed and routed geometry while preserving the clocked decision and meeting timing.

## Constraint

OpenLane/OpenROAD needs more than Verilog. A physical flow also needs:

- top-module name
- design source files
- clock port and clock period
- reset assumptions
- floorplan utilization target
- placement and routing assumptions
- process design kit setup
- standard-cell Liberty timing files
- design-rule and layout-versus-schematic checks

This lab supplies the design-side inputs we can define now. It leaves PDK-specific paths and real flow execution for the machine where OpenLane/OpenROAD is available.

## Files

- `src/aimc_control_plane.v`: local copy of the controller RTL
- `config.json`: OpenLane-style design configuration
- `config.tcl`: compatibility configuration for older `flow.tcl` OpenLane runs
- `constraint.sdc`: clock and simple input/output delay assumptions
- `src/constraint.sdc`: SDC copy for older OpenLane design-folder conventions
- `pin_order.cfg`: stable pin-order intent for review

## Concrete Design Move

Check whether this machine can run the package:

```bash
./scripts/check_aimc_openlane_readiness.sh
```

Current readiness result:

```text
OK      design file config.json
OK      design file config.tcl
OK      design file constraint.sdc
OK      design file pin_order.cfg
OK      design file src/aimc_control_plane.v
OK      design file src/constraint.sdc
OK      config.json parses
OK      yosys -> /usr/bin/yosys
OK      packaged RTL lowers in Yosys
WARN    openlane host command not on PATH
WARN    openroad host command not on PATH
OK      OpenLane source -> /home/mehtama1/eda-tools/OpenLane
OK      docker command -> /usr/bin/docker
OK      docker daemon responds
OK      OpenLane Docker image present
```

So the design package is ready for an OpenLane run attempt. After pulling the architecture-specific OpenLane image and enabling Sky130 under `/home/mehtama1/eda-tools/pdks`, the CTS-enabled flow reached detailed placement and placement-stage STA. See `openlane-partial-run-report.md` for the exact run directory, area, slack, and remaining CTS boundary.

A no-CTS exploratory flow completed through routing, extraction, GDS generation, LVS, DRC, antenna checking, and final report generation. See `openlane-no-cts-final-report.md` for final views, area, timing, DRC, LVS, and antenna evidence. See `openlane-no-cts-metrics-summary.md` for the generated compact metrics table. This is useful physical-flow evidence, but it does not replace CTS-enabled clock-tree signoff.

Run these local checks first:

```bash
iverilog -o ../../digital/aimc-control-plane-rtl/aimc_control_plane_tb ../../digital/aimc-control-plane-rtl/aimc_control_plane.v ../../digital/aimc-control-plane-rtl/aimc_control_plane_tb.v
vvp ../../digital/aimc-control-plane-rtl/aimc_control_plane_tb
cd ../../digital/aimc-control-plane-synthesis
yosys synth_aimc_control_plane.ys
```

When OpenLane is available, the intended next command shape is:

```bash
./scripts/run_aimc_openlane_flow.sh
```

The helper stages this design into `/home/mehtama1/eda-tools/OpenLane/designs/aimc_control_plane` and runs `flow.tcl -design aimc_control_plane`. It stops early if Docker is unavailable or the OpenLane image is missing.

To run the no-CTS exploratory flow:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_control_plane_no_cts CONFIG_NAME=config_no_cts ./scripts/run_aimc_openlane_flow.sh
```

To regenerate the compact metrics summary after a run:

```bash
python3 labs/eda/aimc-control-plane-openlane-prep/extract_openlane_metrics.py
```

## Measurement

The first physical-flow measurements should be:

- synthesis success under the selected standard-cell library
- floorplan utilization
- placement legality
- routed congestion
- worst negative slack and total negative slack
- DRC violation count
- LVS result if the flow reaches layout checking
- final area and cell count

The most important timing question is simple:

```text
Can path[1:0] and reason[2:0] be produced in time for the scheduler to use them?
```

## Failure Mode

The failure mode is confusing a prepared design package with a physical implementation. This folder is an input to a future flow. It proves that we have named the design, constraints, and expected evidence. It does not prove that the controller has been placed, routed, timed, or signed off.
