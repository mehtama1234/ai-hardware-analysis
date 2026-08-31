# GPUMODE GPU Host Preflight

Generated: `2026-08-31T01:53:33.754433+00:00`
Status: `preflight-complete`
Accelerator ready: `False`
Runnable steps: `1/18`

## Capabilities

- `python`: `True`
- `torch`: `True`
- `torch_device`: `cpu`
- `triton`: `True`
- `jax`: `True`
- `nvcc`: `False`
- `hipcc`: `False`
- `nvidia_smi`: `False`
- `nsys`: `False`
- `ncu`: `False`
- `rocprof`: `False`
- `torchrun`: `True`

## Step Readiness

| step | runnable | missing | first command |
|---|---:|---|---|
| `cuda-kernel-compile` | `False` | nvcc, nvidia_smi | `nvcc -O3 kernel-benchmarks/kernels/cuda/memory.cu -c -o /tmp/gpumode-memory.o` |
| `triton-kernel-sweep` | `False` | nvidia_smi | `python3 kernel-benchmarks/kernels/triton/memory.py` |
| `tensor-core-gemm` | `False` | nvcc, nvidia_smi, ncu | `python3 scripts/run_tensor_core_gemm.py` |
| `persistent-kernels` | `False` | nvidia_smi, ncu | `python3 scripts/run_persistent_kernels.py` |
| `parallel-primitives` | `False` | nvidia_smi, ncu | `python3 scripts/run_parallel_primitives.py` |
| `torch-custom-extension` | `False` | nvcc, ninja, nvidia_smi | `python3 scripts/run_custom_ops.py` |
| `model-integration-gpu` | `False` | nvidia_smi | `python3 scripts/build_autotune_db.py` |
| `vllm-serving-trace` | `False` | nvidia_smi | `vllm serve <model> --enable-prefix-caching` |
| `attention-serving-stack` | `False` | nvidia_smi, nsys, ncu | `python3 scripts/run_attention_serving_stack.py` |
| `flash-attention-backward` | `False` | nvidia_smi, ncu, nsys | `python3 scripts/run_flash_attention_backward.py` |
| `sparse-attention-kernels` | `False` | nvidia_smi, ncu, nsys | `python3 scripts/run_sparse_attention_kernels.py` |
| `fused-training-kernels` | `False` | nvidia_smi, ncu, nsys | `python3 scripts/run_fused_training_kernels.py` |
| `speculative-decoding-serving` | `False` | nvidia_smi, nsys, ncu | `python3 scripts/run_speculative_decoding_serving.py` |
| `profiler-capture` | `False` | nvidia_smi, nsys, ncu | `ncu --set full --target-processes all python3 scripts/run_kernel_benchmarks.py` |
| `rocm-hip-port` | `False` | hipcc, rocprof | `hipcc programming-projects/rocm-hip-port/kernel.hip.cpp -o /tmp/rocm-hip-port` |
| `distributed-collectives` | `False` | nvidia_smi | `python3 scripts/run_distributed_collectives.py` |
| `distributed-training-optimizer` | `False` | nvidia_smi, nsys | `python3 scripts/run_distributed_training_optimizer.py` |
| `full-gpu-regression` | `True` | none | `python3 run_all.py` |
