# GPUMODE Assessment Bank

Generated: `2026-08-31T01:53:34.956871+00:00`
Status: `ready`
Concept questions: `10`
Practical tasks: `38`
Total points: `240`
Pass score: `192`

## Concept Checks

| id | topic | difficulty | points | lessons | tutorial sources |
|---|---|---|---:|---:|---|
| `concept-01-cuda` | cuda | advanced | 5 | 4 | NVIDIA, NVIDIA, AMD ROCm |
| `concept-02-hardware` | hardware | advanced | 5 | 4 | NVIDIA, NVIDIA, Triton |
| `concept-03-cutlass` | cutlass | advanced | 5 | 4 | NVIDIA, NVIDIA, JAX Scaling Book |
| `concept-04-profiling` | profiling | advanced | 5 | 4 | NVIDIA, JAX Scaling Book, JAX Scaling Book |
| `concept-05-attention` | attention | advanced | 5 | 4 | Triton, Triton, JAX Scaling Book |
| `concept-06-serving` | serving | advanced | 5 | 4 | JAX Scaling Book, Hugging Face, Hugging Face |
| `concept-07-distributed` | distributed | intermediate | 5 | 4 | AMD ROCm, JAX Scaling Book, JAX Scaling Book |
| `concept-08-quantization` | quantization | intermediate | 5 | 4 | Hugging Face |
| `concept-09-triton` | triton | intermediate | 5 | 4 | Triton, Triton |
| `concept-10-pytorch-compiler` | pytorch-compiler | intermediate | 5 | 4 | JAX Scaling Book |

## Practical Tasks

| id | layer | command | points |
|---|---|---|---:|
| `practical-one-lab-per-lesson` | lesson-labs | `python3 scripts/verify_lesson_labs.py` | 5 |
| `practical-comprehensive-lab-suite` | comprehensive-labs | `python3 scripts/run_comprehensive_labs.py` | 5 |
| `practical-memory-reduction-normalization` | kernel-benchmarks | `python3 scripts/run_kernel_benchmarks.py` | 5 |
| `practical-compiler-runtime-inspection` | compiler-runtime-inspection | `python3 scripts/verify_compiler_runtime_inspection.py` | 5 |
| `practical-tensor-core-gemm` | tensor-core-gemm | `python3 scripts/verify_tensor_core_gemm.py` | 5 |
| `practical-persistent-kernels` | persistent-kernels | `python3 scripts/verify_persistent_kernels.py` | 5 |
| `practical-parallel-primitives` | parallel-primitives | `python3 scripts/verify_parallel_primitives.py` | 5 |
| `practical-custom-op-autograd` | custom-ops | `python3 scripts/run_custom_ops.py` | 5 |
| `practical-autotune-selector` | autotune-db | `python3 scripts/build_autotune_db.py --select-family matmul --select-shape medium-square` | 5 |
| `practical-model-integration` | model-integration | `python3 scripts/run_model_integration.py` | 5 |
| `practical-serving-replay` | serving-traces | `python3 scripts/run_serving_traces.py` | 5 |
| `practical-kv-cache-paged-attention` | kv-cache-paged-attention | `python3 scripts/verify_kv_cache_paged_attention.py` | 5 |
| `practical-attention-serving-stack` | attention-serving-stack | `python3 scripts/verify_attention_serving_stack.py` | 5 |
| `practical-flash-attention-backward` | flash-attention-backward | `python3 scripts/verify_flash_attention_backward.py` | 5 |
| `practical-sparse-attention-kernels` | sparse-attention-kernels | `python3 scripts/verify_sparse_attention_kernels.py` | 5 |
| `practical-fused-training-kernels` | fused-training-kernels | `python3 scripts/verify_fused_training_kernels.py` | 5 |
| `practical-serving-engine-comparison` | serving-engine-comparison | `python3 scripts/verify_serving_engine_comparison.py` | 5 |
| `practical-speculative-decoding-serving` | speculative-decoding-serving | `python3 scripts/verify_speculative_decoding_serving.py` | 5 |
| `practical-distributed-topology` | distributed-topology | `python3 scripts/verify_distributed_topology.py` | 5 |
| `practical-distributed-collectives` | distributed-collectives | `python3 scripts/verify_distributed_collectives.py` | 5 |
| `practical-distributed-training-optimizer` | distributed-training-optimizer | `python3 scripts/verify_distributed_training_optimizer.py` | 5 |
| `practical-moe-routing-all-to-all` | moe-routing-all-to-all | `python3 scripts/verify_moe_routing_all_to_all.py` | 5 |
| `practical-hardware-capacity` | hardware-capacity | `python3 scripts/verify_hardware_capacity_plan.py` | 5 |
| `practical-quantization-memory-formats` | quantization-memory-formats | `python3 scripts/verify_quantization_memory_formats.py` | 5 |
| `practical-numerical-reproducibility` | numerical-reproducibility | `python3 scripts/verify_numerical_reproducibility.py` | 5 |
| `practical-cuda-graphs-latency` | cuda-graphs-latency | `python3 scripts/verify_cuda_graphs_latency.py` | 5 |
| `practical-multi-tenant-gpu-scheduling` | multi-tenant-gpu-scheduling | `python3 scripts/verify_multi_tenant_gpu_scheduling.py` | 5 |
| `practical-profiler-evidence` | profiler-evidence | `python3 scripts/run_profiler_evidence.py` | 5 |
| `practical-gpu-promotion` | gpu-promotion | `python3 scripts/build_gpu_promotion.py` | 5 |
| `practical-gpu-promotion-suite` | gpu-promotion-suite | `python3 scripts/verify_gpu_promotion_suite.py` | 5 |
| `practical-gpu-run-import` | gpu-runs | `python3 scripts/verify_gpu_runs.py` | 5 |
| `practical-gpu-import-lint` | gpu-import-lint | `python3 scripts/lint_gpu_run_imports.py` | 5 |
| `practical-gpu-evidence-provenance` | gpu-provenance | `python3 scripts/verify_gpu_provenance.py` | 5 |
| `practical-gpu-measurement-queue` | gpu-measurement-queue | `python3 scripts/verify_gpu_measurement_queue.py` | 5 |
| `practical-gpu-acceptance-logic` | gpu-acceptance-logic | `python3 scripts/verify_gpu_acceptance_logic.py` | 5 |
| `practical-gpu-host-preflight` | gpu-host-preflight | `python3 scripts/verify_gpu_host_preflight.py` | 5 |
| `practical-gpu-host-handoff` | gpu-handoff | `python3 scripts/verify_gpu_handoff.py` | 5 |
| `practical-regression-acceptance` | regression-ledger | `python3 scripts/build_regression_ledger.py` | 5 |
