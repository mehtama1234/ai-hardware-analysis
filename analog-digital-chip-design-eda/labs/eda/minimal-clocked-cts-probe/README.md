# Lab: Minimal Clocked CTS Probe

This lab is a control experiment for the AIMC operation-partition CTS issue. It asks a narrow question:

```text
Can the local OpenLane/OpenROAD stack build a clock tree for a tiny ordinary clocked design?
```

The AIMC operation-partition no-CTS flow already produced useful physical evidence, but CTS-enabled attempts kept creating characterization patterns and did not complete. A tiny clocked design separates two possibilities:

- the local CTS flow has a broad tool or configuration problem
- the AIMC operation-partition wrapper or constraints are causing a specific CTS problem

## Object

The probe is a small registered block named `toy_cts_probe`.

It has:

- one clock
- one reset
- an 8-bit input
- an 8-bit registered state
- a few simple output reductions

The logic has no analog meaning. That is the point. It is a plain digital clock-tree check.

## Files

- `src/toy_cts_probe.v`: tiny clocked RTL
- `config.json`: OpenLane-style configuration
- `config.tcl`: compatibility configuration for the local OpenLane `flow.tcl`
- `config_no_cts.tcl`: exploratory no-CTS variant
- `constraint.sdc`: top-level timing constraints
- `src/constraint.sdc`: constraint copy for older OpenLane design-folder conventions
- `pin_order.cfg`: stable pin order
- `run_openlane_probe.sh`: stages and runs the probe through the existing OpenLane helper
- `run_fixed_characterization_repro.sh`: copies the toy CTS issue reproducible and fixes the local CTS Tcl characterization argument construction inside the copy
- `openlane-cts-probe-report.md`: measured CTS result from the local run

## Concrete Design Move

First check that the package lowers in Yosys and that OpenLane inputs are present:

```bash
AIMC_OPENLANE_PREP=minimal-clocked-cts-probe AIMC_OPENLANE_DESIGN=toy_cts_probe ./scripts/check_aimc_openlane_readiness.sh
```

Run the CTS-enabled OpenLane probe:

```bash
cd labs/eda/minimal-clocked-cts-probe
PDK_ROOT=/home/mehtama1/eda-tools/pdks ./run_openlane_probe.sh
```

Run the no-CTS variant only if you need to compare against the AIMC no-CTS evidence:

```bash
cd labs/eda/minimal-clocked-cts-probe
PDK_ROOT=/home/mehtama1/eda-tools/pdks CONFIG_NAME=config_no_cts TAG=toy_cts_probe_no_cts ./run_openlane_probe.sh
```

## How To Read The Result

If the probe completes CTS, the local OpenLane/OpenROAD stack can build a clock tree for a simple design. The remaining AIMC CTS boundary is then likely tied to the operation-partition wrapper, its constraints, its clock-load shape, or its generated placement state.

If the probe reaches the same endless characterization-pattern behavior, the next work should focus on the local OpenLane/OpenROAD CTS setup before changing AIMC RTL again.

The measurement is not performance. The measurement is whether clock-tree synthesis completes and whether final signoff reports exist.

## Current Result

The CTS-enabled probe reached the same behavior as the AIMC operation-partition CTS attempts:

```text
[INFO CTS-0049] Characterization buffer is: sky130_fd_sc_hd__clkbuf_8.
[INFO CTS-0038] Number of created patterns = 50000.
[INFO CTS-0038] Number of created patterns = 100000.
```

The run was terminated after it did not complete in the observation window. OpenLane packaged an issue reproducible under:

```text
/home/mehtama1/eda-tools/OpenLane/designs/toy_cts_probe/runs/toy_cts_probe_cts/issue_reproducible
```

This changes the AIMC diagnosis. The same local CTS behavior appears on a tiny ordinary clocked design, so the next work should inspect CTS characterization settings or try a different OpenLane/OpenROAD build before changing AIMC RTL.

A copied-reproducible test also changed the local CTS Tcl from:

```text
lappend -max_cap ...
lappend -max_slew ...
```

to:

```text
lappend cts_characterization_args -max_cap ...
lappend cts_characterization_args -max_slew ...
```

That patched copy still reached 100000 created patterns and timed out. So the stalled behavior is not fixed only by passing max-cap and max-slew into `configure_cts_characterization`.

## Failure Mode

The failure mode is overreading a toy design. Passing this probe does not prove the AIMC operation-partition block is physically clean. It only proves that this local tool stack can complete CTS for a small ordinary clocked design.
