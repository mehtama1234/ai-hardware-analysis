# Minimal Clocked CTS Probe Report

This report records the control experiment for the AIMC operation-partition CTS boundary.

## Command

```bash
cd labs/eda/minimal-clocked-cts-probe
PDK_ROOT=/home/mehtama1/eda-tools/pdks ./run_openlane_probe.sh
```

## Run Directory

```text
/home/mehtama1/eda-tools/OpenLane/designs/toy_cts_probe/runs/toy_cts_probe_cts
```

## What Completed Before CTS

The flow passed:

```text
lint
synthesis
synthesis STA
initial floorplanning
IO placement
tap/decap insertion
PDN
global placement
placement STA
placement resizer
detailed placement
post-placement STA
```

The synthesis result was tiny:

```text
synth_cell_count: 42
DFF: 8
TotalCells: 141
CoreArea_um^2: 2781.4176
critical_path_ns: 11.0
suggested_clock_period: 10.0
suggested_clock_frequency: 90.9090909090909
```

## CTS Result

The probe reached CTS:

```text
[STEP 12]
Running Clock Tree Synthesis
```

The CTS log then reached the same characterization behavior seen in the AIMC operation-partition attempts:

```text
[INFO CTS-0049] Characterization buffer is: sky130_fd_sc_hd__clkbuf_8.
[INFO CTS-0038] Number of created patterns = 50000.
[INFO CTS-0038] Number of created patterns = 100000.
```

The run did not complete in the observation window and was terminated. OpenLane packaged an issue reproducible at:

```text
/home/mehtama1/eda-tools/OpenLane/designs/toy_cts_probe/runs/toy_cts_probe_cts/issue_reproducible
```

## Interpretation

This is the important comparison result: the same local OpenLane/OpenROAD stack shows the same CTS characterization pattern behavior on a tiny ordinary clocked design.

That means the AIMC operation-partition CTS boundary should not be treated first as an AIMC RTL bug. The no-CTS AIMC run still provides useful routed-layout evidence, and the CTS failure is now better framed as a local CTS/toolchain configuration problem until a known-good clocked design passes CTS in the same environment.

## Characterization-Argument Patch Test

The local OpenLane CTS script constructs `cts_characterization_args`, but the packaged script used this shape:

```text
lappend -max_cap ...
lappend -max_slew ...
```

The probe script `run_fixed_characterization_repro.sh` copied the toy CTS issue reproducible and changed those lines inside the copy to:

```text
lappend cts_characterization_args -max_cap ...
lappend cts_characterization_args -max_slew ...
```

Command:

```bash
cd labs/eda/minimal-clocked-cts-probe
TOY_CTS_TIMEOUT_SECONDS=180 ./run_fixed_characterization_repro.sh
```

Result:

```text
result,timeout
[INFO]: Running Clock Tree Synthesis...
[INFO CTS-0049] Characterization buffer is: sky130_fd_sc_hd__clkbuf_8.
[INFO CTS-0038] Number of created patterns = 50000.
[INFO CTS-0038] Number of created patterns = 100000.
```

That means the local Tcl argument construction is suspicious and should be fixed upstream or in a pinned local copy, but it is not by itself enough to complete CTS in this environment.

The next useful work is to try a different OpenLane/OpenROAD build or compare OpenROAD CTS defaults more directly. Changing the AIMC partition logic is not the best first move.
