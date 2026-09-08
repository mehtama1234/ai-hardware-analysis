# Kernel Benchmark Report

Generated: `2026-09-07T06:58:58.616862+00:00`

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
| vector-copy-contiguous-64k | memory | small | passed | 0.00528082 | cpu |
| vector-copy-contiguous-1m | memory | medium | passed | 0.03086989 | cpu |
| vector-copy-strided-64k-s4 | memory | strided | passed | 0.00068073 | cpu |
| vector-copy-strided-64k-s16 | memory | strided | passed | 0.03372995 | cpu |
| reduction-sum-max-128k | reduction | medium | passed | 0.00044343 | cpu |
| reduction-sum-max-1m | reduction | large | passed | 0.01902599 | cpu |
| softmax-8x256 | normalization | narrow | passed | 0.00136030 | cpu |
| softmax-4x1024 | normalization | wide | passed | 0.00010510 | cpu |
| layernorm-8x256 | normalization | narrow | passed | 0.00030033 | cpu |
| layernorm-4x1024 | normalization | wide | passed | 0.00019949 | cpu |
| matmul-64 | matmul | small-square | passed | 0.00070078 | cpu |
| matmul-128 | matmul | medium-square | passed | 0.00297278 | cpu |
| fused-mlp-16x128 | fusion | small-hidden | passed | 0.00089765 | cpu |
| fused-mlp-8x256 | fusion | medium-hidden | passed | 0.00116861 | cpu |
