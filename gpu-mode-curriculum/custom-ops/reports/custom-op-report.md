# PyTorch Custom Op Report

Generated: `2026-08-31T01:53:03.842682+00:00`
Compiled extension status: `source-only`

| case | dtype | shape | status | max abs error | grad x error | fused median s | elements/s |
|---|---|---:|---|---:|---:|---:|---:|
| small-mlp | float32 | 4x128 | passed | 1.19209e-07 | 1.22236e-07 | 0.00043330 | 1181615.7554 |
| decoder-hidden | float32 | 8x768 | passed | 4.76837e-07 | 1.08933e-06 | 0.00069980 | 8779650.9309 |
| wide-ffn | float32 | 16x3072 | passed | 4.76837e-07 | 1.07288e-06 | 0.00139210 | 35307910.0526 |
| bf16-transformer | bfloat16 | 8x1024 | passed | 0.03125 | 0.015625 | 0.00065105 | 12582769.8766 |

## Source Promotion

- `custom-ops/csrc/fused_bias_gelu_residual.cpp` defines the PyTorch extension binding.
- `custom-ops/csrc/fused_bias_gelu_residual_kernel.cu` contains the CUDA kernel skeleton and launcher contract.
- Local CPU fallback verifies forward and backward numerics before accelerator promotion.
