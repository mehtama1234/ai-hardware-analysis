# GPUMODE GPU Run Imports

Generated: `2026-08-31T02:44:03.406231+00:00`
Status: `import-ready`
Real measured runs: `1`

## Coverage

- `run_count`: `4`
- `host_count`: `4`
- `vendor_count`: `3`
- `vendors`: `['AMD', 'NVIDIA', 'unknown']`
- `measured_run_count`: `1`
- `sample_run_count`: `2`
- `host_collected_run_count`: `1`
- `promotion_step_count`: `18`
- `promotion_steps`: `['attention-serving-stack', 'cuda-kernel-compile', 'distributed-collectives', 'distributed-training-optimizer', 'flash-attention-backward', 'full-gpu-regression', 'fused-training-kernels', 'model-integration-gpu', 'parallel-primitives', 'persistent-kernels', 'profiler-capture', 'rocm-hip-port', 'sparse-attention-kernels', 'speculative-decoding-serving', 'tensor-core-gemm', 'torch-custom-extension', 'triton-kernel-sweep', 'vllm-serving-trace']`
- `passed_steps`: `29`
- `failed_steps`: `0`
- `unknown_steps`: `0`

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
