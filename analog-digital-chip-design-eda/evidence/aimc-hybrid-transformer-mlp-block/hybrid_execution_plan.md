# Transformer MLP Block Hybrid Execution Plan

A single transformer-style MLP block with four fixed-weight MatMuls mapped to analog memory and bias, nonlinear, gating, residual, calibration, and fallback operations kept digital.

- analog operators: `4`
- digital support operators: `4`
- calibrated CrossSim relative L2: `4.94498e-08`
- physical converter gate: `blocked_sar_source_common_mode`

This is a deterministic fixture replay, not pretrained transformer token accuracy or hardware evidence.
