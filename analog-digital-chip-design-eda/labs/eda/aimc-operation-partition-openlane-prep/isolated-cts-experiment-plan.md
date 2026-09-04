# Isolated CTS Experiment Plan

The unresolved object is not synthesis, placement, routing, DRC, LVS, or antenna checking. Those already completed in the no-CTS run. The unresolved object is clock tree synthesis.

Both CTS-enabled OpenLane attempts reached:

```text
[INFO CTS-0049] Characterization buffer is: sky130_fd_sc_hd__clkbuf_8.
[INFO CTS-0038] Number of created patterns = 50000.
```

The helper `run_isolated_cts_experiment.sh` copies the OpenLane issue reproducible and runs only the CTS reproducer. This makes each test cheaper and cleaner than rerunning the whole flow.

The packaged reproducer calls `openroad`. On this machine, use:

```bash
AIMC_CTS_RUNNER=docker ./run_isolated_cts_experiment.sh single_corner
```

That runs the copied reproducer inside the same OpenLane Docker image used by the full flow.

## Experiments

`baseline` runs the copied reproducible without changes. It checks whether the packaged reproducer repeats the same behavior outside the full OpenLane run.

`single_corner` sets `CTS_MULTICORNER_LIB=0`. It asks whether CTS characterization is getting expensive because it is considering slow, typical, and fast corners at once.

Current result: the Docker-backed run used only the typical library, reached the same `sky130_fd_sc_hd__clkbuf_8` characterization buffer, and continued from 50000 to 100000 created patterns before timeout. Multi-corner library loading is therefore not the main cause.

`small_clusters` sets:

```text
CTS_SINK_CLUSTERING_SIZE=8
CTS_SINK_CLUSTERING_MAX_DIAMETER=12
```

It asks whether smaller sink groups reduce the characterization search space.

Current result: the Docker-backed run reached the same `sky130_fd_sc_hd__clkbuf_8` characterization buffer and continued from 50000 to 100000 created patterns before termination. Smaller sink clusters did not remove the CTS boundary.

`no_post_processing` sets:

```text
CTS_DISABLE_POST_PROCESSING=1
```

It asks whether the post-CTS cleanup stage is part of the stall. If the run still stops at pattern creation, post-processing is not the first problem.

## How To Read Results

The useful result is not simply pass or fail. The useful result is where the run stops:

```text
before CTS reads the design -> packaging or environment problem
before characterization buffer -> library or constraint problem
at 50000 patterns -> CTS characterization/search problem
after CTS -> later legalization/timing/routing problem
```

If all variants stop at the same 50000-pattern line, the next move is to inspect OpenROAD CTS characterization settings or use a newer OpenROAD/OpenLane build. If one variant advances beyond CTS, that variant gives the next configuration to fold back into the OpenLane prep.

## Boundary

These experiments do not change the analog foundation-model architecture. They test whether the digital wrapper around the operation-placement policy can receive a real clock tree in this local toolchain.
