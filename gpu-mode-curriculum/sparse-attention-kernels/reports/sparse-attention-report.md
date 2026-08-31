# GPUMODE sparse attention kernels

Generated: `2026-08-31T01:53:09.139992+00:00`
Status: `sparse-attention-ready`

| scenario | pattern | status | density | speedup | HBM reduction | load balance | max error |
|---|---|---|---:|---:|---:|---:|---:|
| block-sparse-prefill | block-sparse | passed | 0.25 | 2.7368 | 0.749878 | 0.986 | 0.0028 |
| sliding-window-long-context | sliding-window | passed | 0.16 | 3.5224 | 0.839939 | 0.888 | 0.0032 |
| dilated-global-hybrid | dilated-global | passed | 0.22 | 2.9355 | 0.779878 | 0.972 | 0.0045 |
| ragged-paged-decode | ragged-paged | passed | 0.12 | 2.8387 | 0.868281 | 0.752 | 0.0025 |
| neighborhood-vision-attention | neighborhood | passed | 0.18 | 2.6812 | 0.819817 | 0.916 | 0.0038 |
| topk-routing-attention | topk | passed | 0.2 | 2.4299 | 0.799756 | 0.864 | 0.0065 |

## GPU Host Promotion

- `python3 scripts/run_sparse_attention_kernels.py`
- `python3 scripts/verify_sparse_attention_kernels.py`
- `python3 scripts/run_attention_serving_stack.py`
- `python3 scripts/run_flash_attention_backward.py`
- `ncu --set full -o sparse-attention-kernels python3 <sparse_attention_probe.py>`
- `nsys profile -o sparse-attention-ragged-decode python3 <ragged_decode_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id sparse-attention-kernels --execute`
