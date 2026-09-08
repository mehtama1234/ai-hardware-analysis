# GPUMODE GPU Host Preflight

Generated: `2026-09-08T01:42:34.499647+00:00`
Status: `preflight-complete`
Accelerator ready: `False`
Runnable steps: `1/32`

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
| `eager-kernel-suite-cuda` | `False` | nvidia_smi | `python3 scripts/run_kernel_benchmarks.py --repeats 7` |
| `triton-kernel-sweep` | `False` | nvidia_smi | `python3 kernel-benchmarks/kernels/triton/memory.py` |
| `triton-kernel-families` | `False` | nvidia_smi | `python3 kernel-benchmarks/run_triton_families_cuda.py` |
| `tensor-core-gemm` | `False` | nvcc, nvidia_smi, ncu | `python3 scripts/run_tensor_core_gemm.py` |
| `low-precision-native` | `False` | nvidia_smi | `python3 quantization-memory-formats/run_low_precision_cuda.py` |
| `trained-digits-quality-cuda` | `False` | nvidia_smi | `python3 quantization-memory-formats/run_digits_cuda.py` |
| `rl-simulation-cuda` | `False` | nvidia_smi | `python3 rl-gpu-simulation/run_vectorized_simulation.py --device cuda` |
| `rl-policy-quality-cuda` | `False` | nvidia_smi | `python3 rl-gpu-simulation/run_policy_quality.py --device cuda` |
| `triton-layout-cuda` | `False` | nvidia_smi | `python3 layout-algebra/run_triton_layout_cuda.py --device cuda` |
| `bank-conflict-cuda` | `False` | nvcc, nvidia_smi | `python3 layout-algebra/run_bank_conflict_cuda.py` |
| `cuda-graphs-native` | `False` | nvidia_smi | `python3 cuda-graphs-latency/run_cuda_graphs_cuda.py` |
| `persistent-kernels` | `False` | nvidia_smi, ncu | `python3 scripts/run_persistent_kernels.py` |
| `parallel-primitives` | `False` | nvidia_smi, ncu | `python3 scripts/run_parallel_primitives.py` |
| `torch-custom-extension` | `False` | nvcc, ninja, nvidia_smi | `python3 scripts/run_custom_ops.py` |
| `model-integration-gpu` | `False` | nvidia_smi | `python3 scripts/build_autotune_db.py` |
| `neural-serving-cuda` | `False` | nvidia_smi | `python3 model-integration/run_neural_serving_cuda.py` |
| `trained-neural-quality-cuda` | `False` | nvidia_smi | `python3 model-integration/run_trained_neural_quality_cuda.py --device cuda` |
| `paged-kv-gather-cuda` | `False` | nvcc, nvidia_smi | `python3 gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_paged_kv_cuda.py` |
| `paged-attention-cuda` | `False` | nvcc, nvidia_smi | `python3 gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_paged_attention_cuda.py` |
| `serving-tail-load-cuda` | `False` | nvidia_smi | `python3 model-integration/run_serving_tail_load_cuda.py` |
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
