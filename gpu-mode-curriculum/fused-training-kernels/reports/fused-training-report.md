# GPUMODE fused training kernels

Generated: `2026-08-31T01:53:09.235048+00:00`
Status: `fused-training-ready`

| scenario | family | status | speedup | HBM reduction | launch reduction | max error |
|---|---|---|---:|---:|---:|---:|
| rmsnorm-residual-backward | rmsnorm | passed | 2.2941 | 0.582609 | 0.6 | 0.002 |
| swiglu-mlp-fusion | swiglu-mlp | passed | 2.0724 | 0.532847 | 0.5 | 0.0038 |
| cross-entropy-zloss | cross-entropy | passed | 2.4719 | 0.814634 | 0.75 | 0.0012 |
| adamw-multi-tensor | optimizer | passed | 2.3784 | 0.602041 | 0.714286 | 0.0008 |
| grad-clip-unscale | optimizer | passed | 2.2778 | 0.596154 | 0.6 | 0.001 |
| dropout-residual-norm | fusion | passed | 2.3415 | 0.588235 | 0.6 | 0.0045 |

## GPU Host Promotion

- `python3 scripts/run_fused_training_kernels.py`
- `python3 scripts/verify_fused_training_kernels.py`
- `python3 scripts/run_model_integration.py`
- `python3 scripts/run_distributed_training_optimizer.py`
- `ncu --set full -o fused-training-kernels python3 <fused_training_probe.py>`
- `nsys profile -o fused-training-step python3 <training_step_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id fused-training-kernels --execute`
