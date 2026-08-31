# GPU Programming Capstone Portfolio

Generated: `2026-08-31T01:52:32.407157+00:00`

## Summary

- Projects: 8
- Dependency edges: 11
- Contracts passed: 8
- Runtime caveats: 2

## Execution Order

1. `cuda-memory-kernel` - CUDA kernels (memory-bandwidth)
2. `hf-quant-serving` - Hugging Face serving baseline (quantized-numerics)
3. `rocm-hip-port` - ROCm/HIP portability (rocm-hip-portability)
4. `triton-fused-softmax` - Triton kernels (triton-autotune)
5. `nsight-evidence-loop` - Profiler-to-roofline evidence (profiling-roofline)
6. `vllm-kv-scheduler` - vLLM-style serving (serving-scheduler)
7. `jax-scaling-roofline` - JAX scaling and roofline (memory-bandwidth)
8. `distributed-collectives` - Distributed communication (distributed-communication)

## Milestones

### Local baselines and memory model
- `cuda-memory-kernel`: starter=source-only, contract=passed, measurement=`programming-projects/cuda-memory-kernel/measurements.json`
- `hf-quant-serving`: starter=ran, contract=passed, measurement=`programming-projects/hf-quant-serving/measurements.json`
- `jax-scaling-roofline`: starter=ran, contract=passed, measurement=`programming-projects/jax-scaling-roofline/measurements.json`

### Kernel specialization and profiling
- `triton-fused-softmax`: starter=ran, contract=passed, measurement=`programming-projects/triton-fused-softmax/measurements.json`
- `nsight-evidence-loop`: starter=ran, contract=passed, measurement=`programming-projects/nsight-evidence-loop/measurements.json`

### Serving runtime and portability
- `vllm-kv-scheduler`: starter=ran, contract=passed, measurement=`programming-projects/vllm-kv-scheduler/measurements.json`
- `rocm-hip-port`: starter=source-only, contract=passed, measurement=`programming-projects/rocm-hip-port/measurements.json`

### Scale-out communication
- `distributed-collectives`: starter=ran, contract=passed, measurement=`programming-projects/distributed-collectives/measurements.json`

## Runtime Caveats
- `cuda-memory-kernel`: nvcc missing; compile on a CUDA development host
- `rocm-hip-port`: hipcc missing; compile on a ROCm development host

## Capstone Build

The final capstone combines the memory/coalescing baseline, Triton fused-kernel path, profiler evidence loop,
serving/KV scheduler, JAX roofline model, Hugging Face inference baseline, ROCm/HIP portability boundary,
and distributed collective model into one portfolio. A GPU-enabled follow-up run should replace `source-only`
CUDA/HIP artifacts with compiled measurements while preserving the same measurement contracts.
