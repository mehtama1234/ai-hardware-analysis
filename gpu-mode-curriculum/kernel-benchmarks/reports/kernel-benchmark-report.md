# Kernel Benchmark Report

Generated: `2026-08-31T01:52:58.280944+00:00`

Benchmarks: 14
Passed: 14
Failed: 0

## Runtime Readiness

- `torch_available`: `True`
- `torch_device`: `cpu`
- `nvcc`: `False`
- `hipcc`: `False`
- `nvidia_smi`: `False`
- `triton_available`: `True`

## Results

| Benchmark | Family | Shape | Status | Median seconds | Device |
|---|---|---|---|---|---|
| vector-copy-contiguous-64k | memory | small | passed | 0.00035776 | cpu |
| vector-copy-contiguous-1m | memory | medium | passed | 0.00435604 | cpu |
| vector-copy-strided-64k-s4 | memory | strided | passed | 0.00028816 | cpu |
| vector-copy-strided-64k-s16 | memory | strided | passed | 0.00051647 | cpu |
| reduction-sum-max-128k | reduction | medium | passed | 0.00037910 | cpu |
| reduction-sum-max-1m | reduction | large | passed | 0.00198343 | cpu |
| softmax-8x256 | normalization | narrow | passed | 0.00019314 | cpu |
| softmax-4x1024 | normalization | wide | passed | 0.00008190 | cpu |
| layernorm-8x256 | normalization | narrow | passed | 0.00025953 | cpu |
| layernorm-4x1024 | normalization | wide | passed | 0.00017416 | cpu |
| matmul-64 | matmul | small-square | passed | 0.00016445 | cpu |
| matmul-128 | matmul | medium-square | passed | 0.00021118 | cpu |
| fused-mlp-16x128 | fusion | small-hidden | passed | 0.00130725 | cpu |
| fused-mlp-8x256 | fusion | medium-hidden | passed | 0.00096464 | cpu |
