# AIMC Operation Partition CTS Attempt Report

This report records the CTS-enabled OpenLane attempts for physical wrappers around `aimc_operation_partition`.

The compact generated summary is `cts-debug-summary.md`.

The isolated CTS experiment helper is `run_isolated_cts_experiment.sh`.

## Why This Was Tried

The no-CTS flow completed and produced routed layout, GDS, LVS, DRC, antenna, SPEF, SDF, and timing reports. But its final check report had clock-related violations:

```text
max slew violation count 84
max fanout violation count 1
```

The violating pins were clock pins, and the fanout violation was on `clk`:

```text
clk fanout 83, limit 10
```

That is exactly what a no-CTS wrapper run should expose. The design has many input and output registers, and the unbuilt clock tree drives them directly.

## Full Wrapper Command

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_operation_partition_cts CONFIG_NAME=config AIMC_OPENLANE_PREP=aimc-operation-partition-openlane-prep AIMC_OPENLANE_DESIGN=aimc_operation_partition_physical AIMC_OPENLANE_RTL=aimc_operation_partition.v ./scripts/run_aimc_openlane_flow.sh
```

Run directory:

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_operation_partition_physical/runs/aimc_operation_partition_cts
```

## Full Wrapper Result

The flow passed:

```text
lint
synthesis
synthesis STA
floorplan
IO placement
tap/decap insertion
PDN
global placement
placement STA
placement resizer
detailed placement
post-placement STA
```

It reached clock tree synthesis:

```text
[STEP 12]
Running Clock Tree Synthesis
```

The CTS log then reached:

```text
[INFO CTS-0049] Characterization buffer is: sky130_fd_sc_hd__clkbuf_8.
[INFO CTS-0038] Number of created patterns = 50000.
```

The process did not advance after that point in the observed window, so it was terminated. OpenLane packaged an issue reproducible under the CTS run directory.

## Lean Wrapper Attempt

The next design move was to reduce clock load. The first physical wrapper registered every operation input and output, which made the no-CTS clock net drive 83 flip-flops. A second wrapper, `aimc_operation_partition_output_registered`, registers only `placement[1:0]` and `reason[3:0]`. The combinational partition inputs remain external.

Command:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_operation_partition_output_registered_cts CONFIG_NAME=config_output_registered AIMC_OPENLANE_PREP=aimc-operation-partition-openlane-prep AIMC_OPENLANE_DESIGN=aimc_operation_partition_output_registered AIMC_OPENLANE_RTL=aimc_operation_partition.v ./scripts/run_aimc_openlane_flow.sh
```

Run directory:

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_operation_partition_output_registered/runs/aimc_operation_partition_output_registered_cts
```

The lean wrapper passed lint, synthesis, synthesis STA, floorplanning, IO placement, tap/decap insertion, PDN, global placement, placement STA, placement resizer, detailed placement, and post-placement STA.

It then reached CTS and stopped at the same point:

```text
[INFO CTS-0049] Characterization buffer is: sky130_fd_sc_hd__clkbuf_8.
[INFO CTS-0038] Number of created patterns = 50000.
```

That run was also terminated and OpenLane packaged an issue reproducible under the lean-wrapper CTS run directory.

## Interpretation

This does not contradict the no-CTS result. It explains its remaining warning. The no-CTS result proved that the design can be placed, routed, extracted, streamed to GDS, and checked for DRC/LVS/antenna without routing violations. It also showed that the clock net is not clean without a clock tree.

The second attempt is important because it reduced the wrapper register count but still hit the same CTS behavior. That means the next work should isolate the OpenLane/OpenROAD CTS configuration, not only shrink the RTL wrapper. The project should not claim CTS signoff until that is resolved.

## Isolated Single-Corner Experiment

The first isolated experiment used the lean output-registered reproducible and disabled CTS multi-corner libraries:

```bash
AIMC_CTS_RUNNER=docker AIMC_CTS_TIMEOUT_SECONDS=180 ./run_isolated_cts_experiment.sh single_corner
```

The first host attempt failed because `openroad` is not on the host `PATH`. The helper was then updated to run the reproducible inside the OpenLane Docker image.

The Docker-backed run reached CTS with only the typical library:

```text
define_corners Typical
read_liberty -corner Typical ./tmp/cts/cts.lib
```

It still selected the same characterization buffer and kept creating patterns:

```text
[INFO CTS-0049] Characterization buffer is: sky130_fd_sc_hd__clkbuf_8.
[INFO CTS-0038] Number of created patterns = 50000.
[INFO CTS-0038] Number of created patterns = 100000.
```

The run timed out and was terminated. This means multi-corner library loading is not the main cause of the CTS boundary.

## Isolated Small-Cluster Experiment

The next isolated experiment kept the same lean output-registered reproducible but changed CTS sink clustering:

```bash
AIMC_CTS_RUNNER=docker AIMC_CTS_TIMEOUT_SECONDS=180 ./run_isolated_cts_experiment.sh small_clusters
```

The variant set:

```text
CTS_SINK_CLUSTERING_SIZE=8
CTS_SINK_CLUSTERING_MAX_DIAMETER=12
```

It reached the same CTS point, selected the same characterization buffer, and continued pattern creation past the point where the full OpenLane run had already stopped advancing:

```text
[INFO CTS-0049] Characterization buffer is: sky130_fd_sc_hd__clkbuf_8.
[INFO CTS-0038] Number of created patterns = 50000.
[INFO CTS-0038] Number of created patterns = 100000.
```

The run was terminated after it exceeded the timeout. Smaller sink clusters did not remove the CTS characterization boundary.

## Next Design Moves

The minimal clocked CTS probe in `labs/eda/minimal-clocked-cts-probe` reached the same local CTS behavior on an ordinary tiny registered design:

```text
[INFO CTS-0049] Characterization buffer is: sky130_fd_sc_hd__clkbuf_8.
[INFO CTS-0038] Number of created patterns = 50000.
[INFO CTS-0038] Number of created patterns = 100000.
```

That makes the immediate diagnosis broader than the AIMC wrapper. The next fixes should target the local CTS/toolchain behavior directly:

1. Run `no_post_processing` only as a negative control; if it still stops at pattern creation, post-processing is not involved.
2. Treat the local CTS Tcl argument construction as suspicious, but do not assume it is the whole fix. A copied toy reproducible with corrected `lappend cts_characterization_args ...` lines still reached 100000 created patterns and timed out.
3. Try a different OpenLane/OpenROAD build or finish the local OpenROAD build already running outside this project.
4. Return to AIMC wrapper changes only after a known-good clocked design passes CTS in the same environment.

The important lesson is first-principles: a combinational policy may be easy to synthesize, but a physical chip still needs a clock network for the wrapper that samples and exposes that policy.
