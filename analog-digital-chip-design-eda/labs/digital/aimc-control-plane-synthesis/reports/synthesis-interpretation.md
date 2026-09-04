# AIMC Control Plane Synthesis Interpretation

The object being checked is the translation from readable RTL policy into lowered digital logic.

The source RTL is `../aimc-control-plane-rtl/aimc_control_plane.v`. It chooses one of three paths:

```text
digital fallback
analog projection
analog batched decode
```

It also emits a reason code, so the decision is explainable in simulation and later in system traces.

## What Yosys Proved

Yosys successfully read the Verilog, checked the `aimc_control_plane` top module, lowered the clocked always block, optimized the logic, mapped it into simple cells, and wrote `aimc_control_plane_synth.v`.

The report shows:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 277
$_DFF_PN0_: 4
$_DFF_PN1_: 1
$_MUX_: 22
$_AND_: 113
$_OR_: 64
$_XOR_: 55
$_NOT_: 18
```

The five flip-flop bits are the registered outputs:

```text
path[1:0] + reason[2:0]
```

The Boolean cells and muxes implement the priority decision:

```text
resident weights
healthy tile threshold
estimated error threshold
stale calibration and weak tiles
long-context single decode
batched decode
default analog path
```

## What This Means

The serving policy is no longer only a Python model or architecture paragraph. It has a digital circuit form. The circuit has a clock, reset, input state, registered path output, and registered reason output.

That is a meaningful EDA step because synthesis changed the representation:

```text
policy idea -> RTL -> lowered cells and flip-flop bits
```

The decision was preserved well enough for Yosys to produce a netlist-like Verilog artifact.

## What This Does Not Prove

This report does not prove physical timing. It does not include a standard-cell library, placed cells, routed wires, clock tree, power grid, or extracted parasitics.

It also does not prove that the policy thresholds are optimal. The thresholds are design choices. They must later be tied to measured analog error, cache traffic, converter cost, calibration data, and model-state tolerance.

The next evidence step is timing and physical implementation. The useful question becomes:

```text
Can this control decision arrive in time to steer the scheduler for the next request phase?
```

## Operation Partition Synthesis

The second RTL object is `../aimc-control-plane-rtl/aimc_operation_partition.v`. It chooses the hardware home for one transformer operation:

```text
digital
analog
hybrid
```

It also emits a reason code. The reason says whether the decision came from a digital-only rule, a fixed-weight analog opportunity, a hybrid candidate, missing resident weights, high state error, high attention-selection flips, high token-choice flips, stale weak tiles, or an unknown operation.

Yosys successfully read the Verilog, checked the `aimc_operation_partition` top module, lowered the combinational always block, optimized the logic, mapped it into simple cells, and wrote `aimc_operation_partition_synth.v`.

The report shows:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 338
$_AND_: 112
$_MUX_: 39
$_NOT_: 50
$_OR_: 87
$_XOR_: 50
```

There are no flip-flop cells in this result. That is expected. The operation partition is a combinational decision from current operation class and current evidence:

```text
op class
resident weights
state-error estimate
attention-selection flip estimate
token-choice flip estimate
calibration age
weak tile count
```

This connects the analog transformer simulator to hardware logic. The simulator estimates when analog fixed projections, analog logits, analog attention, or stale tiles are acceptable. The RTL turns those estimates into a placement code that a scheduler can use.

The result still does not prove physical timing, standard-cell area, power, or the truth of the input estimates. It proves a narrower but useful thing: the first-principles operation map can be encoded as checkable digital logic.

## Tile Readout Synthesis

The third RTL object is `../aimc-control-plane-rtl/aimc_tile_readout.v`. It controls the boundary between analog measurement and model state:

```text
ADC code
calibrated zero code
gain correction
bias correction
residual check
calibration-age check
saturation check
valid or fallback decision
```

Yosys successfully read the Verilog, checked the `aimc_tile_readout` top module, lowered the clocked always block, mapped the arithmetic and comparisons into simple cells, and wrote `aimc_tile_readout_synth.v`.

The report shows:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 1556
$_DFF_PN0_: 21
$_AND_: 718
$_MUX_: 62
$_NOT_: 41
$_OR_: 276
$_XOR_: 438
```

The 21 flip-flop bits are the registered public outputs after optimization:

```text
corrected_value[15:0] + output_valid + fallback + reason[3:0]
```

The large Boolean cell count comes from the fixed-point multiply, signed add, saturation comparisons, residual comparison, calibration-age comparison, and priority choice of reason code.

This is a useful hardware step because it moves the analog tile boundary from prose into a circuit candidate. The ADC output is not treated as a model value. It becomes a measured input to a digital correction and acceptance rule. If the residual is too high, calibration is stale, the tile is disabled, or the corrected value saturates, the circuit refuses the analog result.

The result still does not prove physical timing or that the correction parameters are correct. It proves the narrower translation claim: digital correction and fallback around an analog tile can be encoded, simulated, lowered, and inspected.

## Integrated Micro-Tile Controller Synthesis

The integrated top is `../aimc-control-plane-rtl/aimc_micro_tile_controller.v`. It composes operation placement with tile readout acceptance:

```text
partition permits analog
tile readout samples ADC code
controller waits one cycle
valid corrected result is accepted
invalid readout forces digital fallback
```

Yosys reports for the full hierarchy:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 2990
$_DFF_PN0_: 110
$_AND_: 954
$_MUX_: 757
$_NOT_: 100
$_OR_: 451
$_XOR_: 618
```

The important point is not the raw cell count. It is the preserved boundary: analog placement is separate from analog acceptance, and recovery is separate from ordinary serving. The synthesized controller contains a one-bit pending state, pending tile id, registered execution path, registered reason code, last fallback tile id, fallback counter, accepted counter, residual-fallback counter, stale-calibration fallback counter, registered tile health action, the operation-partition logic, and the tile-readout correction logic. The recovery inputs add steering logic around the existing health register: calibration done can restore a recalibrating tile, while probe request, probe pass, and probe fail control the only path back from disablement.

## Error-Budget Governor Synthesis

The sixth RTL object is `../aimc-control-plane-rtl/aimc_error_budget_governor.v`. It controls the decision to spend another analog result:

```text
local residual
calibration age
model-path sensitivity
cumulative model-state error
```

Yosys reports:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 353
$_AND_: 126
$_MUX_: 88
$_NOT_: 13
$_OR_: 68
$_XOR_: 58
```

There are no flip-flop bits because the governor is a combinational policy block. That is the intended first boundary. The block does not remember the whole serving history. It receives a cumulative state-error estimate and decides whether the next analog operation can be allowed, should request recalibration, should disable the tile path, or should fall back to digital.

The useful proof is the generated trace. The Python runtime writes 32 token cases to CSV and Verilog include. The Verilog testbench checks each one. That caught a real implementation issue during development: the `drift_age * 3` term initially used a narrow Verilog multiply and truncated part of the risk score. Widening that arithmetic made the RTL match the generated trace. That is exactly why the analog model and RTL must be tied together by generated cases.

## Integrated Scheduler/Governor Synthesis

The seventh RTL object is `../aimc-control-plane-rtl/aimc_scheduler_governor.v`. It combines two smaller decisions:

```text
scheduler -> which tile action is available
governor -> whether the next analog error should be spent
```

Yosys reports:

```text
Number of memories: 0
Number of processes: 0
Number of cells: 601
```

The generated 36-token trace caught a real scheduler issue while this block was being built. The scheduler knew only tile 2 could serve in one case, but a Verilog helper function still returned tile 0. Replacing the selector functions with explicit continuous assignments made both the standalone scheduler trace and the integrated trace pass. The lesson is simple: small policy helpers are still hardware, and the generated trace must cover cases where the first tile is unavailable.
