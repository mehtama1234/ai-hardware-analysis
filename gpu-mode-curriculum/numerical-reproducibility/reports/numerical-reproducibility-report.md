# GPUMODE Numerical Reproducibility

Generated: `2026-08-31T01:53:22.197431+00:00`
Status: `reproducibility-ready`

| mode | category | status | tolerance | repeat drift | reference error | cosine |
|---|---|---|---:|---:|---:|---:|
| fp32-deterministic | strict | passed | 1e-06 | 0.0 | 0.0 | 1.00000238 |
| fp32-reversed-reduction | order-sensitive | passed | 0.0001 | 0.0 | 5.341e-05 | 1.0000025 |
| tf32-like | fast-math | passed | 0.005 | 0.0 | 0.00490952 | 1.00000238 |
| bf16-like | low-precision | passed | 0.2 | 0.0 | 0.15905762 | 1.00000191 |
| fp8-like | calibration-required | tolerance-review | 2.0 | 0.0 | 3.00914764 | 0.99987316 |

## Reduction Order

- max order delta: `0.0`
- status: `passed`

## GPU Host Promotion

- `CUBLAS_WORKSPACE_CONFIG=:4096:8 python3 scripts/run_numerical_reproducibility.py`
- `NVIDIA_TF32_OVERRIDE=0 python3 scripts/verify_numerical_reproducibility.py`
- `HIP_VISIBLE_DEVICES=0 python3 scripts/run_numerical_reproducibility.py`
- `nsys profile -o numerical-reproducibility python3 <precision_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id numerical-reproducibility --execute`
