# GPUMODE persistent kernels

Generated: `2026-08-31T01:52:59.478298+00:00`
Status: `persistent-kernels-ready`

| scenario | family | strategy | occupancy | speedup | HBM reduction | resident CTA/SM | status |
|---|---|---|---:|---:|---:|---:|---|
| persistent-row-softmax-long-context | softmax | persistent-row | 1.0 | 1.6364 | 0.2593 | 7 | passed |
| persistent-matmul-square | matmul | persistent-cta | 1.0 | 1.4103 | 0.3333 | 2 | passed |
| grouped-gemm-moe-experts | grouped-gemm | persistent-grouped | 0.5 | 1.6552 | 0.4444 | 2 | passed |
| persistent-layernorm-batch | normalization | persistent-vector | 1.0 | 1.3636 | 0.2 | 8 | passed |
| persistent-attention-prefill | attention | persistent-block | 0.5 | 1.4286 | 0.3939 | 1 | passed |
| persistent-overregistered-gemm-review | matmul | persistent-cta | 0.5 | 1.2 | 0.375 | 1 | review |

## GPU Host Promotion

- `python3 scripts/run_persistent_kernels.py`
- `python3 scripts/verify_persistent_kernels.py`
- `python3 kernel-benchmarks/kernels/triton/softmax_layernorm.py`
- `python3 kernel-benchmarks/kernels/triton/matmul_mlp.py`
- `ncu --set full -o persistent-kernels python3 <persistent_kernel_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id persistent-kernels --execute`
