# GPU Host Handoff

Generated: `2026-08-31T01:53:34.885647+00:00`
Status: `ready`
Promotion commands: `88`

## Run On GPU Host

```bash
bash gpu-handoff/bin/run-gpu-host-handoff.sh h100-node-001 --dry-run
bash gpu-handoff/bin/run-gpu-host-handoff.sh h100-node-001 --execute
```

## Bundle Files

- `gpu-promotion/gpu-host-promotion-manifest.json`
- `gpu-handoff/gpu-host-preflight.json`
- `gpu-promotion/suite-run-report.json`
- `compiler-runtime-inspection/compiler-runtime-report.json`
- `tensor-core-gemm/tensor-core-gemm-report.json`
- `persistent-kernels/persistent-kernels-report.json`
- `parallel-primitives/parallel-primitives-report.json`
- `gpu-runs/import-lint-report.json`
- `gpu-runs/gpu-run-report.json`
- `gpu-provenance/gpu-provenance-report.json`
- `serving-engine-comparison/serving-engine-comparison.json`
- `kv-cache-paged-attention/kv-cache-report.json`
- `attention-serving-stack/attention-serving-report.json`
- `flash-attention-backward/flash-attention-backward-report.json`
- `sparse-attention-kernels/sparse-attention-report.json`
- `fused-training-kernels/fused-training-report.json`
- `speculative-decoding-serving/speculative-decoding-report.json`
- `distributed-topology/distributed-topology-plan.json`
- `distributed-collectives/distributed-collectives-report.json`
- `distributed-collectives/reports/collective-benchmark-run.json`
- `distributed-training-optimizer/distributed-training-optimizer-report.json`
- `moe-routing-all-to-all/moe-routing-report.json`
- `hardware-capacity-planning/hardware-capacity-plan.json`
- `quantization-memory-formats/quantization-report.json`
- `numerical-reproducibility/numerical-reproducibility-report.json`
- `cuda-graphs-latency/cuda-graphs-latency-report.json`
- `multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json`
- `gpu-measurement-queue/gpu-measurement-queue.json`
- `gpu-measurement-queue/acceptance-logic-report.json`
- `scripts/run_gpu_promotion_suite.py`
- `scripts/run_gpu_host_preflight.py`
- `scripts/run_compiler_runtime_inspection.py`
- `scripts/verify_compiler_runtime_inspection.py`
- `scripts/run_tensor_core_gemm.py`
- `scripts/verify_tensor_core_gemm.py`
- `scripts/run_persistent_kernels.py`
- `scripts/verify_persistent_kernels.py`
- `scripts/run_parallel_primitives.py`
- `scripts/verify_parallel_primitives.py`
- `scripts/run_serving_engine_comparison.py`
- `scripts/verify_serving_engine_comparison.py`
- `scripts/run_kv_cache_paged_attention.py`
- `scripts/verify_kv_cache_paged_attention.py`
- `scripts/run_attention_serving_stack.py`
- `scripts/verify_attention_serving_stack.py`
- `scripts/run_flash_attention_backward.py`
- `scripts/verify_flash_attention_backward.py`
- `scripts/run_sparse_attention_kernels.py`
- `scripts/verify_sparse_attention_kernels.py`
- `scripts/run_fused_training_kernels.py`
- `scripts/verify_fused_training_kernels.py`
- `scripts/run_speculative_decoding_serving.py`
- `scripts/verify_speculative_decoding_serving.py`
- `scripts/run_distributed_topology.py`
- `scripts/verify_distributed_topology.py`
- `scripts/run_distributed_collectives.py`
- `scripts/verify_distributed_collectives.py`
- `scripts/run_distributed_collectives_benchmark.py`
- `scripts/verify_distributed_collectives_benchmark.py`
- `scripts/run_distributed_training_optimizer.py`
- `scripts/verify_distributed_training_optimizer.py`
- `scripts/run_moe_routing_all_to_all.py`
- `scripts/verify_moe_routing_all_to_all.py`
- `scripts/run_hardware_capacity_plan.py`
- `scripts/verify_hardware_capacity_plan.py`
- `scripts/run_quantization_memory_formats.py`
- `scripts/verify_quantization_memory_formats.py`
- `scripts/run_numerical_reproducibility.py`
- `scripts/verify_numerical_reproducibility.py`
- `scripts/run_cuda_graphs_latency.py`
- `scripts/verify_cuda_graphs_latency.py`
- `scripts/run_multi_tenant_gpu_scheduling.py`
- `scripts/verify_multi_tenant_gpu_scheduling.py`
- `scripts/verify_gpu_host_preflight.py`
- `scripts/collect_gpu_run.py`
- `scripts/lint_gpu_run_imports.py`
- `scripts/build_gpu_runs.py`
- `scripts/build_gpu_provenance.py`
- `scripts/build_gpu_measurement_queue.py`
- `scripts/verify_gpu_runs.py`
- `scripts/verify_gpu_provenance.py`
- `scripts/verify_gpu_measurement_queue.py`
- `scripts/verify_gpu_acceptance_logic.py`
- `scripts/verify_gpu_promotion_suite.py`
- `scripts/verify_capstone_acceptance.py`

## Validation Gates

- `python3 scripts/verify_gpu_promotion_suite.py`
- `python3 scripts/verify_gpu_host_preflight.py`
- `python3 scripts/verify_compiler_runtime_inspection.py`
- `python3 scripts/verify_tensor_core_gemm.py`
- `python3 scripts/verify_persistent_kernels.py`
- `python3 scripts/verify_parallel_primitives.py`
- `python3 scripts/verify_serving_engine_comparison.py`
- `python3 scripts/verify_kv_cache_paged_attention.py`
- `python3 scripts/verify_attention_serving_stack.py`
- `python3 scripts/verify_flash_attention_backward.py`
- `python3 scripts/verify_sparse_attention_kernels.py`
- `python3 scripts/verify_fused_training_kernels.py`
- `python3 scripts/verify_speculative_decoding_serving.py`
- `python3 scripts/verify_distributed_topology.py`
- `python3 scripts/verify_distributed_collectives.py`
- `python3 scripts/verify_distributed_collectives_benchmark.py`
- `python3 scripts/verify_distributed_training_optimizer.py`
- `python3 scripts/verify_moe_routing_all_to_all.py`
- `python3 scripts/verify_hardware_capacity_plan.py`
- `python3 scripts/verify_quantization_memory_formats.py`
- `python3 scripts/verify_numerical_reproducibility.py`
- `python3 scripts/verify_cuda_graphs_latency.py`
- `python3 scripts/verify_multi_tenant_gpu_scheduling.py`
- `python3 scripts/lint_gpu_run_imports.py`
- `python3 scripts/verify_gpu_runs.py`
- `python3 scripts/verify_gpu_provenance.py`
- `python3 scripts/verify_gpu_measurement_queue.py`
- `python3 scripts/verify_gpu_acceptance_logic.py`
- `python3 scripts/verify_runtime_matrix.py`
- `python3 scripts/verify_capstone_acceptance.py`
