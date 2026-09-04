# AIMC Control Plane OpenLane Partial Run Report

This report records the first real OpenLane run attempt for the AIMC control-plane RTL.

## Run Identity

```text
OpenLane root: /home/mehtama1/eda-tools/OpenLane
PDK root: /home/mehtama1/eda-tools/pdks
PDK: sky130A
Standard-cell library: sky130_fd_sc_hd
Design: aimc_control_plane
Run directory: /home/mehtama1/eda-tools/OpenLane/designs/aimc_control_plane/runs/RUN_2026.08.29_09.56.38
```

The run used the Docker-wrapped OpenLane `flow.tcl` path. The earlier direct host invocation failed because `/tool_metadata.yml` exists inside the container, not on the host.

## What Was Fixed Before The Run

The OpenLane image existed only as the unsuffixed tag at first. This OpenLane Makefile runs the architecture-suffixed image, so the `-amd64` image was pulled:

```text
ghcr.io/the-openroad-project/openlane:ff5509f65b17bfa4068d5336495ab1718987ff69-amd64
```

The default PDK root `/home/mehtama1/.ciel` was root-owned, so Sky130 was enabled under a user-writable path:

```text
/home/mehtama1/eda-tools/pdks
```

## Evidence Produced

The flow reached these stages:

- Verilator lint
- synthesis
- synthesis STA
- initial floorplan
- IO placement
- tap/decap insertion
- PDN generation
- global placement
- global-placement STA
- placement resizing
- detailed placement
- detailed-placement STA
- CTS start

The run was manually stopped during CTS after the CTS log stopped advancing for several minutes. Therefore this is not a completed physical implementation.

## Key Measurements

Floorplan:

```text
core area box: 5.52 10.88 40.48 43.52
die area box: 0.0 0.0 46.26 56.98
floorplanned width: 34.96
floorplanned height: 32.64
```

Synthesis mapped the controller to Sky130 standard cells:

```text
Number of cells: 43
sky130_fd_sc_hd__dfrtp_2: 4
sky130_fd_sc_hd__dfstp_2: 1
Chip area for module aimc_control_plane: 434.166400
```

Detailed-placement STA reported:

```text
tns 0.00
wns 0.00
setup worst slack 6.00
hold worst slack 1.54
Design area 571 u^2
Utilization 50%
```

These numbers are meaningful but not final. They are pre-route or placement-stage evidence, not routed signoff evidence.

## Warnings And Boundaries

OpenLane warned during floorplanning:

```text
Current core area is too small for the power grid settings chosen.
The power grid will be scaled down.
```

That is plausible for a very small controller, but it should be revisited if this block becomes part of a larger scheduler or top-level chip.

The synthesis check report also emitted driver warnings for `path` and `reason` after one mapped check stage. The flow continued and produced later placement STA, but the warning should be investigated before treating the run as clean signoff evidence.

## What This Proves

This proves that the AIMC control-plane RTL can enter a real Sky130 OpenLane flow, pass lint, synthesize to standard cells, floorplan, pass through placement, and produce timing numbers at the detailed-placement stage.

It also proves the project now has a working path from:

```text
first-principles serving policy
-> RTL controller
-> Yosys synthesis
-> OpenLane Sky130 physical-flow attempt
```

## What This Does Not Prove

This does not prove completed GDS, routed timing, DRC, LVS, antenna repair, extracted parasitics, package behavior, or manufacturability.

The next design move is to make CTS finish reliably or configure the run for a tiny controller block. After that, continue to routing and signoff reports.
