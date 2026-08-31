# GPUMODE Runtime Matrix

Generated: `2026-08-31T01:53:46.904920+00:00`

## Local Capabilities

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
- `mpirun`: `False`
- `torchrun`: `True`
- `kubectl`: `True`

## Profiles

| Profile | Status | Purpose | Commands |
|---|---|---|---|
| `cpu-local` | `ready` | Run curriculum, lesson labs, comprehensive labs, and PyTorch CPU benchmark sweeps. | `python3 scripts/run_lesson_labs.py`<br>`python3 scripts/run_comprehensive_labs.py`<br>`python3 scripts/run_kernel_benchmarks.py` |
| `gpu-promotion-suite-dev` | `ready` | Plan or execute the ordered GPU-host promotion commands from the manifest and preserve command-level evidence expectations. | `python3 scripts/run_gpu_promotion_suite.py --run-id local-suite-dry-run`<br>`python3 scripts/verify_gpu_promotion_suite.py` |
| `compiler-runtime-inspection-dev` | `ready` | Inspect CUDA, Triton, ROCm/HIP, and custom-op sources for compiler/runtime features, risks, and GPU-host promotion commands. | `python3 scripts/run_compiler_runtime_inspection.py`<br>`python3 scripts/verify_compiler_runtime_inspection.py` |
| `tensor-core-gemm-dev` | `ready` | Plan CUTLASS/CuTe tensor-core GEMM CTA, warp, MMA, pipeline, epilogue, quantized operand, and profiler promotion choices. | `python3 scripts/run_tensor_core_gemm.py`<br>`python3 scripts/verify_tensor_core_gemm.py` |
| `persistent-kernels-dev` | `ready` | Design and promote persistent Triton/CUDA kernels with occupancy, launch amortization, L2 reuse, register pressure, shared memory, and producer/consumer evidence. | `python3 scripts/run_persistent_kernels.py`<br>`python3 scripts/verify_persistent_kernels.py` |
| `parallel-primitives-dev` | `ready` | Model and promote reduction, scan, compaction, radix sort, histogram, and segmented reduction kernels with memory-traffic and synchronization evidence. | `python3 scripts/run_parallel_primitives.py`<br>`python3 scripts/verify_parallel_primitives.py` |
| `gpu-runs-dev` | `ready` | Import GPU-host validation rows from NVIDIA and AMD-shaped runs and link them to the promotion manifest. | `python3 scripts/build_gpu_runs.py`<br>`python3 scripts/verify_gpu_runs.py` |
| `serving-engine-comparison-dev` | `ready` | Compare vLLM, Hugging Face TGI, SGLang, TensorRT-LLM, and HF Transformers baseline across production inference scenarios. | `python3 scripts/run_serving_engine_comparison.py`<br>`python3 scripts/verify_serving_engine_comparison.py` |
| `speculative-decoding-serving-dev` | `ready` | Model and promote speculative decoding serving with draft/target verification, acceptance rate, rollback pressure, KV commits, TTFT, TPOT, throughput, and scheduler policy. | `python3 scripts/run_speculative_decoding_serving.py`<br>`python3 scripts/verify_speculative_decoding_serving.py` |
| `kv-cache-paged-attention-dev` | `ready` | Compare contiguous KV reservation against PagedAttention-style block tables for fragmentation, prefix reuse, eviction, admission, and GPU-serving promotion. | `python3 scripts/run_kv_cache_paged_attention.py`<br>`python3 scripts/verify_kv_cache_paged_attention.py` |
| `attention-serving-stack-dev` | `ready` | Connect FlashAttention online-softmax tiling to vLLM-style prefill/decode scheduling, KV reuse, CUDA Graph bucket fit, numerical tolerance, and GPU profiling promotion. | `python3 scripts/run_attention_serving_stack.py`<br>`python3 scripts/verify_attention_serving_stack.py` |
| `flash-attention-backward-dev` | `ready` | Model and promote FlashAttention backward dQ, dK, dV, dSoftmax, recompute, dropout, GQA, activation-memory, and gradient-error evidence. | `python3 scripts/run_flash_attention_backward.py`<br>`python3 scripts/verify_flash_attention_backward.py` |
| `sparse-attention-kernels-dev` | `ready` | Model and promote block-sparse, sliding-window, ragged decode, neighborhood, top-k, metadata, load-balance, and sparse backward attention kernels. | `python3 scripts/run_sparse_attention_kernels.py`<br>`python3 scripts/verify_sparse_attention_kernels.py` |
| `fused-training-kernels-dev` | `ready` | Model and promote fused LLM training kernels for RMSNorm, SwiGLU, cross-entropy, AdamW, grad clipping, dropout/residual/norm, backward checks, launch count, and HBM traffic. | `python3 scripts/run_fused_training_kernels.py`<br>`python3 scripts/verify_fused_training_kernels.py` |
| `distributed-topology-dev` | `ready` | Plan tensor, pipeline, and data parallel deployment choices across single-GPU, PCIe, NVLink, and InfiniBand topologies. | `python3 scripts/run_distributed_topology.py`<br>`python3 scripts/verify_distributed_topology.py` |
| `distributed-collectives-dev` | `ready` | Plan NCCL/RCCL/NVSHMEM collective algorithms with rank count, payload, topology bandwidth, latency, communication overlap, and GPU-host promotion evidence. | `python3 scripts/run_distributed_collectives.py`<br>`python3 scripts/verify_distributed_collectives.py`<br>`torchrun --nproc_per_node=2 scripts/run_distributed_collectives_benchmark.py`<br>`python3 scripts/verify_distributed_collectives_benchmark.py` |
| `distributed-training-optimizer-dev` | `ready` | Model DDP, ZeRO, FSDP, tensor/pipeline parallelism, activation checkpointing, optimizer-state sharding, communication exposure, and GPU-host promotion. | `python3 scripts/run_distributed_training_optimizer.py`<br>`python3 scripts/verify_distributed_training_optimizer.py` |
| `moe-routing-all-to-all-dev` | `ready` | Model MoE top-k routing, expert load balance, capacity drops, all-to-all payload, fabric latency, and GPU-host profiler promotion. | `python3 scripts/run_moe_routing_all_to_all.py`<br>`python3 scripts/verify_moe_routing_all_to_all.py` |
| `hardware-capacity-dev` | `ready` | Plan GPU hardware class, memory headroom, bottleneck class, power/cost, and validation commands across kernel, serving, and training workloads. | `python3 scripts/run_hardware_capacity_plan.py`<br>`python3 scripts/verify_hardware_capacity_plan.py` |
| `quantization-memory-dev` | `ready` | Compare BF16, FP8-style, INT8, INT4, and NF4 memory formats for compression, accuracy drift, dequant tax, serving fit, and GPU promotion. | `python3 scripts/run_quantization_memory_formats.py`<br>`python3 scripts/verify_quantization_memory_formats.py` |
| `numerical-reproducibility-dev` | `ready` | Check deterministic seeds, precision-mode tolerance, reduction-order drift, and GPU-host reproducibility promotion across CUDA/Triton/ROCm-style paths. | `python3 scripts/run_numerical_reproducibility.py`<br>`python3 scripts/verify_numerical_reproducibility.py` |
| `cuda-graphs-latency-dev` | `ready` | Model CUDA Graph capture eligibility, warmup, static-shape constraints, p95 latency reduction, and dynamic-shape fallback strategies for serving decode paths. | `python3 scripts/run_cuda_graphs_latency.py`<br>`python3 scripts/verify_cuda_graphs_latency.py` |
| `multi-tenant-scheduling-dev` | `ready` | Plan MIG/MPS/Kubernetes-style GPU sharing, isolation, fairness, SLO fit, and queue fallback across serving, batch, CI, and training tenants. | `python3 scripts/run_multi_tenant_gpu_scheduling.py`<br>`python3 scripts/verify_multi_tenant_gpu_scheduling.py` |
| `gpu-import-lint-dev` | `ready` | Lint GPU run fixtures and imports for schema, provenance, measured flags, and promotion-step evidence. | `python3 scripts/lint_gpu_run_imports.py` |
| `gpu-provenance-dev` | `ready` | Separate sample fixtures, host-collected smoke runs, and real measured accelerator-host evidence. | `python3 scripts/build_gpu_provenance.py`<br>`python3 scripts/verify_gpu_provenance.py` |
| `gpu-measurement-queue-dev` | `ready` | Track per-step GPU-host measurement contracts, metrics, thresholds, and real measured completion. | `python3 scripts/build_gpu_measurement_queue.py`<br>`python3 scripts/verify_gpu_measurement_queue.py` |
| `gpu-acceptance-logic-dev` | `ready` | Regression-test GPU measurement threshold logic with canonical accepted and rejected metric rows. | `python3 scripts/verify_gpu_acceptance_logic.py` |
| `gpu-host-preflight-dev` | `ready` | Snapshot accelerator-host capabilities and classify GPU promotion steps as runnable or blocked before execution. | `python3 scripts/run_gpu_host_preflight.py`<br>`python3 scripts/verify_gpu_host_preflight.py` |
| `gpu-handoff-dev` | `ready` | Generate the portable GPU-host handoff bundle with entrypoint, bundle files, and validation commands. | `python3 scripts/build_gpu_handoff.py`<br>`python3 scripts/verify_gpu_handoff.py` |
| `assessment-grading-dev` | `ready` | Score the generated concept checks and practical tasks against current artifact evidence. | `python3 scripts/grade_assessment.py`<br>`python3 scripts/verify_assessment_grading.py` |
| `assessment-dev` | `ready` | Generate and verify the concept exam and practical task bank across GPUMODE lessons, official tutorials, and implemented artifacts. | `python3 scripts/build_assessment.py`<br>`python3 scripts/verify_assessment.py` |
| `capstone-acceptance-dev` | `ready` | Grade the complete GPU curriculum stack as a portfolio-grade end-to-end systems project. | `python3 scripts/build_capstone_acceptance.py`<br>`python3 scripts/verify_capstone_acceptance.py` |
| `gpu-promotion-dev` | `ready` | Generate the ordered GPU-host promotion manifest for CUDA, Triton, custom op, model, serving, profiler, ROCm/HIP, distributed, and regression runs. | `python3 scripts/build_gpu_promotion.py`<br>`python3 scripts/verify_gpu_promotion.py` |
| `regression-ledger-dev` | `ready` | Collect stable metrics across generated GPU curriculum layers and fail on correctness or performance-regression threshold violations. | `python3 scripts/build_regression_ledger.py`<br>`python3 scripts/verify_regression_ledger.py` |
| `model-integration-dev` | `ready` | Run a tiny transformer block that uses custom-op fusion and autotune selections inside a model-shaped path. | `python3 scripts/run_model_integration.py`<br>`python3 scripts/verify_model_integration.py` |
| `autotune-dev` | `ready` | Persist benchmark-derived tuning records and select starting configs by operator family and shape class. | `python3 scripts/build_autotune_db.py`<br>`python3 scripts/build_autotune_db.py --select-family matmul --select-shape medium-square`<br>`python3 scripts/verify_autotune_db.py` |
| `custom-op-dev` | `ready` | Validate PyTorch custom operator integration with forward/backward correctness, fuzz shapes, and CUDA extension source promotion. | `python3 scripts/run_custom_ops.py`<br>`python3 scripts/verify_custom_ops.py`<br>`python3 -m torch.utils.cpp_extension <custom-op-build>` |
| `serving-dev` | `ready` | Replay LLM serving traces and validate TTFT, TPOT, throughput, prefix-cache reuse, and KV pressure. | `python3 scripts/run_serving_traces.py`<br>`python3 scripts/verify_serving_traces.py`<br>`vllm serve <model> --enable-prefix-caching` |
| `cuda-dev` | `source-ready-local-fallback` | Compile CUDA kernel sources and promote CPU/PyTorch measurements to GPU timings. | `nvcc -O3 kernel-benchmarks/kernels/cuda/memory.cu -c`<br>`nvcc -O3 kernel-benchmarks/kernels/cuda/reduction.cu -c`<br>`nvcc -O3 kernel-benchmarks/kernels/cuda/softmax_layernorm.cu -c`<br>`nvcc -O3 kernel-benchmarks/kernels/cuda/matmul_mlp.cu -c`<br>`python3 scripts/run_kernel_benchmarks.py` |
| `triton-dev` | `source-ready-local-fallback` | Run Triton kernels on a CUDA GPU and compare against PyTorch baselines. | `python3 kernel-benchmarks/kernels/triton/memory.py`<br>`python3 kernel-benchmarks/kernels/triton/reduction.py`<br>`python3 kernel-benchmarks/kernels/triton/softmax_layernorm.py`<br>`python3 kernel-benchmarks/kernels/triton/matmul_mlp.py`<br>`python3 scripts/run_kernel_benchmarks.py` |
| `rocm-hip-dev` | `source-ready-local-fallback` | Compile HIP portability sources and run rocprof-backed measurements. | `hipcc programming-projects/rocm-hip-port/kernel.hip.cpp -o /tmp/rocm-hip-port`<br>`rocprof /tmp/rocm-hip-port` |
| `profiler-dev` | `source-ready-local-fallback` | Collect Nsight Systems/Compute evidence and feed profiler-to-roofline reports. | `ncu --set full --target-processes all <kernel-command>`<br>`nsys profile <serving-command>`<br>`python3 scripts/gpu_workbench_programs.py evidence-report "nsight roofline dram counters"` |
| `distributed-dev` | `ready` | Run multi-process/multi-GPU collective tests and compare against ring/tree models. | `torchrun --nproc_per_node=2 <collective-test>`<br>`python3 scripts/gpu_workbench.py "nccl nvshmem all reduce bandwidth" --run-lab --dry-run` |
