# GPU Programming Project Run Report

Generated: `2026-08-31T01:52:32.251467+00:00`

Projects: 8
Passed contracts: 8
Failed contracts: 0

| Project | Track | Profile | Starter | Contract |
|---|---|---|---|---|
| cuda-memory-kernel | CUDA kernels | memory-bandwidth | source-only | passed |
| triton-fused-softmax | Triton kernels | triton-autotune | ran | passed |
| rocm-hip-port | ROCm/HIP portability | rocm-hip-portability | source-only | passed |
| vllm-kv-scheduler | vLLM-style serving | serving-scheduler | ran | passed |
| jax-scaling-roofline | JAX scaling and roofline | memory-bandwidth | ran | passed |
| hf-quant-serving | Hugging Face serving baseline | quantized-numerics | ran | passed |
| nsight-evidence-loop | Profiler-to-roofline evidence | profiling-roofline | ran | passed |
| distributed-collectives | Distributed communication | distributed-communication | ran | passed |

## Runtime Caveats
- cuda-memory-kernel: nvcc missing; compile on a CUDA development host
- rocm-hip-port: hipcc missing; compile on a ROCm development host
