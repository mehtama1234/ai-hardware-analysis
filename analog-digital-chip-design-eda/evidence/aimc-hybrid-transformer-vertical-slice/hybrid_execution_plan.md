# Hybrid Transformer Vertical Slice

This package connects one three-block transformer-style MLP fixture to an explicit analog-memory, digital-support, and SRAM execution plan.

- analog operators: `12`
- digital support operators: `4`
- activations and partial sums: `local SRAM`
- simulator output comparison: `6.71635e-08` relative L2, pass `true`
- execution handoff: `run_hybrid_transformer_vertical_slice.py` validates the plan and emits the operator-level replay trace
- physical converter gate: `blocked_sar_source_common_mode`

## What This Proves

The calibrated CrossSim replay preserves the output of this deterministic fixture under its stated simulator assumptions. The execution plan makes the mixed-memory boundary explicit: fixed-weight MatMuls are analog candidates, while bias, nonlinear, residual, control, calibration, and fallback work remains digital with SRAM buffering.

## What It Does Not Prove

This is not pretrained transformer accuracy, a full attention execution, measured silicon, board runtime, measured power, thermal behavior, or production readiness. The physical Sky130 converter is not yet compatible with the simulator's 8-bit converter assumption because its corrected 4-bit high-code spacing is insufficient.

## Next Gate

Repair or replace the physical converter topology, then rerun the same plan with a converter profile that matches the analog simulator. After that, add the attention-shaped fixture while keeping dynamic attention selection, Softmax, normalization, KV-cache movement, and token decisions on the digital/SRAM path.
