# AIMC Operation Partition CTS Debug Summary

This file is generated from local OpenLane run artifacts. It separates the completed no-CTS physical evidence from the CTS boundary.

## No-CTS Clock Checks

```text
run_dir: /home/mehtama1/eda-tools/OpenLane/designs/aimc_operation_partition_physical/runs/aimc_operation_partition_no_cts
flow_status: flow completed
max_slew_violations: 84
max_fanout_violations: 1
max_cap_violations: 0
clock_fanout: 83
```

## CTS Attempts

### full_input_output_wrapper

```text
run_dir: /home/mehtama1/eda-tools/OpenLane/designs/aimc_operation_partition_physical/runs/aimc_operation_partition_cts
exists: true
reached_cts: true
characterization_buffer: sky130_fd_sc_hd__clkbuf_8
created_patterns: 50000
flow_status: flow failed
issue_reproducible: true
```

### lean_output_registered_wrapper

```text
run_dir: /home/mehtama1/eda-tools/OpenLane/designs/aimc_operation_partition_output_registered/runs/aimc_operation_partition_output_registered_cts
exists: true
reached_cts: true
characterization_buffer: sky130_fd_sc_hd__clkbuf_8
created_patterns: 50000
flow_status: flow failed
issue_reproducible: true
```

## Isolated CTS Experiments

### single_corner

```text
log: /tmp/aimc-operation-partition-cts-experiments/single_corner/experiment-single_corner.log
exists: true
reached_cts: true
characterization_buffer: sky130_fd_sc_hd__clkbuf_8
last_created_patterns: 100000
completed: false
openroad_missing: false
```

### small_clusters

```text
log: /tmp/aimc-operation-partition-cts-experiments/small_clusters/experiment-small_clusters.log
exists: true
reached_cts: true
characterization_buffer: sky130_fd_sc_hd__clkbuf_8
last_created_patterns: 100000
completed: false
openroad_missing: false
```

## Interpretation

Both CTS-enabled attempts reached OpenROAD CTS, selected the same clock characterization buffer, and stopped at the same pattern count. The isolated single-corner and small-cluster experiments also reached the same characterization buffer and continued pattern creation beyond 50000. The no-CTS run remains valid routed-layout evidence, but the unresolved object is the clock tree.

The next experiment should isolate CTS itself: run the packaged reproducible with changed CTS characterization or clustering settings before changing the transformer partition logic again.
