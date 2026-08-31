#!/usr/bin/env bash
set -euo pipefail

RUN_ID="${1:-gpu-host-handoff-run}"
MODE="${2:---dry-run}"

if [[ "$MODE" == "--execute" ]]; then
  python3 scripts/run_gpu_host_preflight.py
  python3 scripts/run_gpu_promotion_suite.py --run-id "$RUN_ID" --execute
else
  python3 scripts/run_gpu_host_preflight.py
  python3 scripts/run_gpu_promotion_suite.py --run-id "$RUN_ID"
fi

python3 scripts/collect_gpu_run.py --run-id "$RUN_ID"
python3 scripts/lint_gpu_run_imports.py
python3 scripts/build_gpu_runs.py
python3 scripts/build_gpu_provenance.py
python3 scripts/build_gpu_measurement_queue.py
python3 scripts/verify_gpu_acceptance_logic.py
python3 scripts/verify_gpu_promotion_suite.py
python3 scripts/verify_gpu_runs.py
python3 scripts/verify_gpu_provenance.py
python3 scripts/verify_gpu_measurement_queue.py
python3 scripts/verify_gpu_acceptance_logic.py
python3 scripts/run_compiler_runtime_inspection.py
python3 scripts/verify_compiler_runtime_inspection.py
python3 scripts/run_tensor_core_gemm.py
python3 scripts/verify_tensor_core_gemm.py
python3 scripts/run_persistent_kernels.py
python3 scripts/verify_persistent_kernels.py
python3 scripts/run_parallel_primitives.py
python3 scripts/verify_parallel_primitives.py
python3 scripts/run_serving_engine_comparison.py
python3 scripts/verify_serving_engine_comparison.py
python3 scripts/run_kv_cache_paged_attention.py
python3 scripts/verify_kv_cache_paged_attention.py
python3 scripts/run_attention_serving_stack.py
python3 scripts/verify_attention_serving_stack.py
python3 scripts/run_flash_attention_backward.py
python3 scripts/verify_flash_attention_backward.py
python3 scripts/run_sparse_attention_kernels.py
python3 scripts/verify_sparse_attention_kernels.py
python3 scripts/run_fused_training_kernels.py
python3 scripts/verify_fused_training_kernels.py
python3 scripts/run_speculative_decoding_serving.py
python3 scripts/verify_speculative_decoding_serving.py
python3 scripts/run_distributed_topology.py
python3 scripts/verify_distributed_topology.py
python3 scripts/run_distributed_collectives.py
python3 scripts/verify_distributed_collectives.py
python3 scripts/verify_distributed_collectives_benchmark.py
python3 scripts/run_distributed_training_optimizer.py
python3 scripts/verify_distributed_training_optimizer.py
python3 scripts/run_moe_routing_all_to_all.py
python3 scripts/verify_moe_routing_all_to_all.py
python3 scripts/run_hardware_capacity_plan.py
python3 scripts/verify_hardware_capacity_plan.py
python3 scripts/run_quantization_memory_formats.py
python3 scripts/verify_quantization_memory_formats.py
python3 scripts/run_numerical_reproducibility.py
python3 scripts/verify_numerical_reproducibility.py
python3 scripts/run_cuda_graphs_latency.py
python3 scripts/verify_cuda_graphs_latency.py
python3 scripts/run_multi_tenant_gpu_scheduling.py
python3 scripts/verify_multi_tenant_gpu_scheduling.py
python3 scripts/build_runtime_matrix.py
python3 build_site.py
python3 scripts/build_end_to_end_audit.py
python3 scripts/build_capstone_acceptance.py
python3 scripts/verify_capstone_acceptance.py
