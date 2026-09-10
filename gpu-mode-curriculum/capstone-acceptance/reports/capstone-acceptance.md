# GPUMODE Capstone Acceptance

Generated: `2026-09-10T01:25:48.406982+00:00`
Status: `incomplete`
Score: `390/400` (97.5%)

| criterion | status | points | evidence |
|---|---|---:|---|
| lesson-corpus-coverage | passed | 10/10 | analysis/gpumode-curriculum.json, analysis/lesson-intelligence.json |
| one-lab-per-lesson | passed | 10/10 | lesson-labs/run-report.json, scripts/verify_lesson_labs.py |
| comprehensive-programs | passed | 10/10 | comprehensive-labs/run-report.json, comprehensive-labs/PLAN.md |
| project-portfolio | passed | 10/10 | programming-projects/project-run-report.json, programming-projects/capstone-portfolio.json |
| kernel-source-and-benchmarks | passed | 10/10 | kernel-benchmarks/reports/kernel-benchmark-report.json, kernel-benchmarks/kernels/cuda, kernel-benchmarks/kernels/triton |
| compiler-runtime-inspection | passed | 10/10 | compiler-runtime-inspection/compiler-runtime-report.json, compiler-runtime-inspection/reports/compiler-runtime-report.md, scripts/verify_compiler_runtime_inspection.py |
| custom-op-model-path | passed | 10/10 | custom-ops/reports/custom-op-report.json, model-integration/reports/tiny-transformer-report.json |
| tensor-core-gemm | passed | 10/10 | tensor-core-gemm/tensor-core-gemm-report.json, tensor-core-gemm/reports/tensor-core-gemm-report.md, scripts/verify_tensor_core_gemm.py |
| persistent-kernels | passed | 10/10 | persistent-kernels/persistent-kernels-report.json, persistent-kernels/reports/persistent-kernels-report.md, scripts/verify_persistent_kernels.py |
| parallel-primitives | passed | 10/10 | parallel-primitives/parallel-primitives-report.json, parallel-primitives/reports/parallel-primitives-report.md, scripts/verify_parallel_primitives.py |
| autotune-and-regression | passed | 10/10 | autotune-db/autotune-db.json, regression-ledger/regression-ledger.json |
| serving-system | passed | 10/10 | serving-traces/reports/serving-trace-report.json |
| kv-cache-paged-attention | passed | 10/10 | kv-cache-paged-attention/kv-cache-report.json, kv-cache-paged-attention/reports/kv-cache-report.md, scripts/verify_kv_cache_paged_attention.py |
| attention-serving-stack | passed | 10/10 | attention-serving-stack/attention-serving-report.json, attention-serving-stack/reports/attention-serving-report.md, scripts/verify_attention_serving_stack.py |
| flash-attention-backward | passed | 10/10 | flash-attention-backward/flash-attention-backward-report.json, flash-attention-backward/reports/flash-attention-backward-report.md, scripts/verify_flash_attention_backward.py |
| sparse-attention-kernels | passed | 10/10 | sparse-attention-kernels/sparse-attention-report.json, sparse-attention-kernels/reports/sparse-attention-report.md, scripts/verify_sparse_attention_kernels.py |
| fused-training-kernels | passed | 10/10 | fused-training-kernels/fused-training-report.json, fused-training-kernels/reports/fused-training-report.md, scripts/verify_fused_training_kernels.py |
| serving-engine-comparison | passed | 10/10 | serving-engine-comparison/serving-engine-comparison.json, serving-engine-comparison/reports/serving-engine-comparison.md, scripts/verify_serving_engine_comparison.py |
| speculative-decoding-serving | passed | 10/10 | speculative-decoding-serving/speculative-decoding-report.json, speculative-decoding-serving/reports/speculative-decoding-report.md, scripts/verify_speculative_decoding_serving.py |
| distributed-topology-planning | passed | 10/10 | distributed-topology/distributed-topology-plan.json, distributed-topology/reports/distributed-topology-plan.md, scripts/verify_distributed_topology.py |
| distributed-collectives | passed | 10/10 | distributed-collectives/distributed-collectives-report.json, distributed-collectives/reports/distributed-collectives-report.md, scripts/verify_distributed_collectives.py |
| distributed-training-optimizer | passed | 10/10 | distributed-training-optimizer/distributed-training-optimizer-report.json, distributed-training-optimizer/reports/distributed-training-optimizer-report.md, scripts/verify_distributed_training_optimizer.py |
| moe-routing-all-to-all | passed | 10/10 | moe-routing-all-to-all/moe-routing-report.json, moe-routing-all-to-all/reports/moe-routing-report.md, scripts/verify_moe_routing_all_to_all.py |
| hardware-capacity-planning | passed | 10/10 | hardware-capacity-planning/hardware-capacity-plan.json, hardware-capacity-planning/reports/hardware-capacity-plan.md, scripts/verify_hardware_capacity_plan.py |
| quantization-memory-formats | passed | 10/10 | quantization-memory-formats/quantization-report.json, quantization-memory-formats/reports/quantization-report.md, scripts/verify_quantization_memory_formats.py |
| numerical-reproducibility | passed | 10/10 | numerical-reproducibility/numerical-reproducibility-report.json, numerical-reproducibility/reports/numerical-reproducibility-report.md, scripts/verify_numerical_reproducibility.py |
| cuda-graphs-latency | passed | 10/10 | cuda-graphs-latency/cuda-graphs-latency-report.json, cuda-graphs-latency/reports/cuda-graphs-latency-report.md, scripts/verify_cuda_graphs_latency.py |
| multi-tenant-gpu-scheduling | passed | 10/10 | multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json, multi-tenant-gpu-scheduling/reports/multi-tenant-scheduling-report.md, scripts/verify_multi_tenant_gpu_scheduling.py |
| gpu-promotion-runtime | passed | 10/10 | gpu-promotion/gpu-host-promotion-manifest.json, runtime-matrix/matrix.json |
| gpu-promotion-suite | passed | 10/10 | gpu-promotion/suite-run-report.json, gpu-promotion/reports/suite-run-report.md, scripts/verify_gpu_promotion_suite.py |
| gpu-run-imports | passed | 10/10 | gpu-runs/gpu-run-report.json, gpu-runs/reports/gpu-run-report.md, scripts/verify_gpu_runs.py |
| gpu-run-import-lint | passed | 10/10 | gpu-runs/import-lint-report.json, gpu-runs/reports/import-lint-report.md, scripts/lint_gpu_run_imports.py |
| gpu-evidence-provenance | passed | 10/10 | gpu-provenance/gpu-provenance-report.json, gpu-provenance/reports/gpu-provenance-report.md, scripts/verify_gpu_provenance.py |
| gpu-measurement-queue | failed | 0/10 | gpu-measurement-queue/gpu-measurement-queue.json, gpu-measurement-queue/reports/gpu-measurement-queue.md, scripts/verify_gpu_measurement_queue.py |
| gpu-acceptance-logic | passed | 10/10 | gpu-measurement-queue/acceptance-logic-report.json, gpu-measurement-queue/reports/acceptance-logic-report.md, scripts/verify_gpu_acceptance_logic.py |
| gpu-host-preflight | passed | 10/10 | gpu-handoff/gpu-host-preflight.json, gpu-handoff/reports/gpu-host-preflight.md, scripts/verify_gpu_host_preflight.py |
| gpu-host-handoff | passed | 10/10 | gpu-handoff/gpu-host-handoff.json, gpu-handoff/reports/gpu-host-handoff.md, gpu-handoff/bin/run-gpu-host-handoff.sh, scripts/verify_gpu_handoff.py |
| assessment-readiness | passed | 10/10 | assessment/question-bank.json, assessment/reports/assessment-report.md, scripts/verify_assessment.py |
| assessment-grading | passed | 10/10 | assessment/grading-report.json, assessment/reports/grading-report.md, scripts/verify_assessment_grading.py |
| site-and-audit | passed | 10/10 | site/*.html, analysis/end-to-end-audit.json |
