# GPUMODE GPU Run Imports

Generated: `2026-09-08T06:44:22.126726+00:00`
Status: `import-ready`
Real measured runs: `3`

## Coverage

- `run_count`: `6`
- `host_count`: `6`
- `vendor_count`: `3`
- `vendors`: `['AMD', 'NVIDIA', 'unknown']`
- `measured_run_count`: `3`
- `sample_run_count`: `2`
- `host_collected_run_count`: `1`
- `promotion_step_count`: `32`
- `promotion_steps`: `['attention-serving-stack', 'bank-conflict-cuda', 'cuda-graphs-native', 'cuda-kernel-compile', 'distributed-collectives', 'distributed-training-optimizer', 'eager-kernel-suite-cuda', 'flash-attention-backward', 'full-gpu-regression', 'fused-training-kernels', 'low-precision-native', 'model-integration-gpu', 'neural-serving-cuda', 'paged-attention-cuda', 'paged-kv-gather-cuda', 'parallel-primitives', 'persistent-kernels', 'profiler-capture', 'rl-policy-quality-cuda', 'rl-simulation-cuda', 'rocm-hip-port', 'serving-tail-load-cuda', 'sparse-attention-kernels', 'speculative-decoding-serving', 'tensor-core-gemm', 'torch-custom-extension', 'trained-digits-quality-cuda', 'trained-neural-quality-cuda', 'triton-kernel-families', 'triton-kernel-sweep', 'triton-layout-cuda', 'vllm-serving-trace']`
- `passed_steps`: `63`
- `failed_steps`: `0`
- `unknown_steps`: `0`

## Validation

- `covered_gpu_host_steps`: `['attention-serving-stack', 'bank-conflict-cuda', 'cuda-graphs-native', 'cuda-kernel-compile', 'distributed-collectives', 'distributed-training-optimizer', 'eager-kernel-suite-cuda', 'flash-attention-backward', 'fused-training-kernels', 'low-precision-native', 'model-integration-gpu', 'neural-serving-cuda', 'paged-attention-cuda', 'paged-kv-gather-cuda', 'parallel-primitives', 'persistent-kernels', 'profiler-capture', 'rl-policy-quality-cuda', 'rl-simulation-cuda', 'rocm-hip-port', 'serving-tail-load-cuda', 'sparse-attention-kernels', 'speculative-decoding-serving', 'tensor-core-gemm', 'torch-custom-extension', 'trained-digits-quality-cuda', 'trained-neural-quality-cuda', 'triton-kernel-families', 'triton-kernel-sweep', 'triton-layout-cuda', 'vllm-serving-trace']`
- `missing_gpu_host_steps`: `[]`

## Imported Steps

| run | host | accelerator | step | status | metrics |
|---|---|---|---|---|---:|
| `sample-a100-gpu-run` | gpu-host-a100-reference | NVIDIA A100 | `cuda-kernel-compile` | passed | 2 |
| `sample-a100-gpu-run` | gpu-host-a100-reference | NVIDIA A100 | `triton-kernel-sweep` | passed | 2 |
| `sample-a100-gpu-run` | gpu-host-a100-reference | NVIDIA A100 | `torch-custom-extension` | passed | 2 |
| `sample-a100-gpu-run` | gpu-host-a100-reference | NVIDIA A100 | `model-integration-gpu` | passed | 2 |
| `sample-a100-gpu-run` | gpu-host-a100-reference | NVIDIA A100 | `vllm-serving-trace` | passed | 3 |
| `sample-a100-gpu-run` | gpu-host-a100-reference | NVIDIA A100 | `profiler-capture` | passed | 2 |
| `sample-a100-gpu-run` | gpu-host-a100-reference | NVIDIA A100 | `distributed-collectives` | passed | 10 |
| `sample-a100-gpu-run` | gpu-host-a100-reference | NVIDIA A100 | `distributed-training-optimizer` | passed | 7 |
| `sample-a100-gpu-run` | gpu-host-a100-reference | NVIDIA A100 | `full-gpu-regression` | passed | 2 |
| `sample-mi300-gpu-run` | gpu-host-mi300-reference | AMD MI300 | `rocm-hip-port` | passed | 3 |
| `sample-mi300-gpu-run` | gpu-host-mi300-reference | AMD MI300 | `profiler-capture` | passed | 2 |
| `sample-mi300-gpu-run` | gpu-host-mi300-reference | AMD MI300 | `distributed-collectives` | passed | 10 |
| `sample-mi300-gpu-run` | gpu-host-mi300-reference | AMD MI300 | `distributed-training-optimizer` | passed | 7 |
| `sample-mi300-gpu-run` | gpu-host-mi300-reference | AMD MI300 | `full-gpu-regression` | passed | 2 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `cuda-kernel-compile` | passed | 4 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `triton-kernel-sweep` | passed | 3 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `tensor-core-gemm` | passed | 7 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `persistent-kernels` | passed | 7 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `parallel-primitives` | passed | 6 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `torch-custom-extension` | passed | 2 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `model-integration-gpu` | passed | 3 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `vllm-serving-trace` | passed | 3 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `attention-serving-stack` | passed | 6 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `flash-attention-backward` | passed | 7 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `sparse-attention-kernels` | passed | 8 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `fused-training-kernels` | passed | 8 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `speculative-decoding-serving` | passed | 8 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `profiler-capture` | skipped:missing-profiler-tools | 4 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `rocm-hip-port` | skipped:missing-hipcc-or-rocprof | 3 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `distributed-collectives` | skipped:missing-measured-collective-benchmark | 10 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `distributed-training-optimizer` | passed | 7 |
| `colab-advanced-phase` | 3096f7c224ac | Tesla T4 | `full-gpu-regression` | passed | 3 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `cuda-kernel-compile` | passed | 4 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `triton-kernel-sweep` | passed | 3 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `tensor-core-gemm` | passed | 7 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `persistent-kernels` | passed | 7 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `parallel-primitives` | passed | 6 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `torch-custom-extension` | passed | 2 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `model-integration-gpu` | passed | 3 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `vllm-serving-trace` | passed | 3 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `attention-serving-stack` | passed | 6 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `flash-attention-backward` | passed | 7 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `sparse-attention-kernels` | passed | 8 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `fused-training-kernels` | passed | 8 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `speculative-decoding-serving` | passed | 8 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `profiler-capture` | skipped:missing-profiler-tools | 4 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `rocm-hip-port` | skipped:missing-hipcc-or-rocprof | 3 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `distributed-collectives` | skipped:missing-measured-collective-benchmark | 10 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `distributed-training-optimizer` | passed | 7 |
| `colab-full-20260908` | d0f1c6a1b092 | Tesla T4 | `full-gpu-regression` | passed | 3 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `cuda-kernel-compile` | passed | 5 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `eager-kernel-suite-cuda` | passed | 7 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `low-precision-native` | passed | 7 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `trained-digits-quality-cuda` | passed | 9 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `rl-simulation-cuda` | passed | 17 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `rl-policy-quality-cuda` | passed | 15 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `triton-layout-cuda` | passed | 11 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `bank-conflict-cuda` | passed | 4 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `cuda-graphs-native` | passed | 11 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `model-integration-gpu` | passed | 2 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `neural-serving-cuda` | passed | 10 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `trained-neural-quality-cuda` | passed | 15 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `paged-kv-gather-cuda` | passed | 4 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `paged-attention-cuda` | passed | 4 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `serving-tail-load-cuda` | passed | 9 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `triton-kernel-sweep` | partial:matmul-only | 7 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `triton-kernel-families` | passed | 7 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `tensor-core-gemm` | passed | 3 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `profiler-capture` | passed | 10 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `parallel-primitives` | passed | 4 |
| `colab-t4-promoted-20260907` | Google Colab runtime (imported) | Tesla T4 | `distributed-collectives` | partial:world-size-one | 7 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `cuda-kernel-compile` | skipped:missing-nvcc-or-nvidia-gpu | 4 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `triton-kernel-sweep` | skipped:missing-cuda-gpu | 3 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `persistent-kernels` | skipped:missing-cuda-triton-or-ncu | 7 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `parallel-primitives` | skipped:missing-measured-primitive-run | 6 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `torch-custom-extension` | skipped:extension-source-only | 2 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `model-integration-gpu` | skipped:missing-accelerator-runtime | 3 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `vllm-serving-trace` | skipped:missing-vllm-cuda-runtime | 3 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `flash-attention-backward` | skipped:missing-measured-flash-backward-run | 7 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `sparse-attention-kernels` | skipped:missing-measured-sparse-attention-run | 8 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `fused-training-kernels` | skipped:missing-measured-fused-training-run | 8 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `speculative-decoding-serving` | skipped:missing-measured-speculative-decoding-run | 8 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `profiler-capture` | skipped:missing-profiler-tools | 4 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `rocm-hip-port` | skipped:missing-hipcc-or-rocprof | 3 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `distributed-collectives` | skipped:missing-measured-collective-benchmark | 10 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `distributed-training-optimizer` | skipped:missing-measured-training-optimizer-run | 7 |
| `local-cpu-collector-smoke` | MithusLaptop | unavailable | `full-gpu-regression` | skipped:missing-accelerator-regression-run | 3 |
