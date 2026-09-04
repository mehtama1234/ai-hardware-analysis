# Lab: AIMC Control Plane Timing Readiness

This lab asks what timing evidence exists for the AIMC control-plane RTL after the available local flow. The machine currently has Yosys and Icarus Verilog. It does not currently expose OpenSTA, OpenROAD, OpenLane, or a standard-cell Liberty file on `PATH`, so this lab is deliberately not called timing closure.

## Object

The first object being controlled is the clocked decision path inside `aimc_control_plane`.

The controller samples request and tile metadata, then registers:

```text
path[1:0]
reason[2:0]
```

The timing question is whether the combinational decision logic can settle before those output registers sample the next value.

The second object is the combinational decision path inside `aimc_operation_partition`. It does not register a request. It maps the current transformer operation class and current evidence into:

```text
placement[1:0]
reason[3:0]
```

The timing question for that module is different: can the placement decision settle soon enough for the scheduler or request controller that consumes it?

## Constraint

Simulation proves the decision sequence for chosen cases. Yosys synthesis proves the RTL can be lowered into primitive logic. Neither proves timing.

Real setup timing would need:

```text
clock period
library cell delays
wire delays
clock uncertainty
input arrival times
output required times
```

Without those, the honest result is timing readiness, not timing closure.

## Concrete Design Move

Run the RTL simulation:

```bash
iverilog -o ../../digital/aimc-control-plane-rtl/aimc_control_plane_tb ../../digital/aimc-control-plane-rtl/aimc_control_plane.v ../../digital/aimc-control-plane-rtl/aimc_control_plane_tb.v
vvp ../../digital/aimc-control-plane-rtl/aimc_control_plane_tb
```

Run synthesis:

```bash
cd ../../digital/aimc-control-plane-synthesis
yosys synth_aimc_control_plane.ys
yosys synth_aimc_operation_partition.ys
```

Run the structural timing-readiness analyzer:

```bash
cd ../../../eda/aimc-control-plane-timing-readiness
python3 analyze_timing_readiness.py
```

## Measurement

The analyzer reads both synthesized Verilog outputs and reports:

- registered output bits
- combinational operation-placement output bits
- primitive logic cell counts
- presence or absence of inferred memories
- presence or absence of unresolved behavioral processes
- the missing evidence needed for real timing closure

The current useful finding is that the request controller is small and purely combinational between input metadata and the five output register bits. The operation partition is purely combinational with no flip-flops. That makes both blocks good next candidates for a real static timing flow once a Liberty file and OpenSTA/OpenROAD path are available.

Current analyzer output:

```text
status,ready_for_sta_not_timing_closed
request_dff_bits,5
request_and_cells,113
request_or_cells,64
request_xor_cells,55
request_mux_cells,22
request_not_cells,18
request_no_memories,true
request_no_processes,true
request_path_output_lowered,true
request_reason_output_lowered,true
operation_dff_bits,0
operation_and_cells,112
operation_or_cells,87
operation_xor_cells,50
operation_mux_cells,39
operation_not_cells,50
operation_no_memories,true
operation_no_processes,true
operation_placement_output_lowered,true
operation_reason_output_lowered,true
claim,request_and_operation_partition_structure_available_but_timing_not_proven
```

## Failure Mode

The failure mode is saying "Yosys passed, so timing is fine." Yosys lowering is translation evidence. Timing closure is deadline evidence. A chip needs both.

This lab keeps the boundary clear: the design is ready for timing analysis, but timing is not proven until the same decision path is checked against real delay models and physical assumptions.
