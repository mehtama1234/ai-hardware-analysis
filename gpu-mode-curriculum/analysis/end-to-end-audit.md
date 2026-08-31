# GPUMODE Workbench End-To-End Audit

Generated: 2026-08-31T01:53:41.030014+00:00
Overall status: proven-with-runtime-caveats

## Ingest and maintain GPUMODE YouTube metadata/transcripts.
Status: proven
Evidence: raw-material/youtube/transcript-index.json, analysis/gpumode-curriculum.json
Facts: videos=118, available_transcripts=117, missing_transcripts=1

## Extract deterministic lesson intelligence.
Status: proven
Evidence: analysis/lesson-intelligence.json
Facts: records=118

## Build prerequisite/topic graph and practical topic order.
Status: proven
Evidence: analysis/curriculum-graph.json, scripts/query_curriculum_graph.py
Facts: nodes=174, edges=3718, top_topics=['cuda', 'hardware', 'cutlass', 'profiling', 'attention']

## Connect GPUMODE lessons to AI-hardware corpus papers.
Status: proven
Evidence: analysis/lesson-corpus-bridges.json, scripts/query_corpus_bridge.py
Facts: paper_bridges=1244, lesson_bridges=103, links=7451

## Implement deeper runnable GPU systems labs with correctness checks.
Status: proven-with-runtime-caveat
Evidence: gpu-kernels-serving-lab/15-gpumode-coalescing, gpu-kernels-serving-lab/26-gpumode-distributed-communication, analysis/latest-measurements-index.json
Facts: implemented_labs=12, gpumode_lab_artifacts=12, correctness_passed=12
Caveat: CUDA/HIP/vLLM/Nsight/NCCL runtime throughput remains environment-gated on this machine; the artifacts record explicit skip/readiness rows instead of claiming unavailable accelerator measurements.

## Generate measurement-backed lesson, bridge, lab, and workbench pages.
Status: proven
Evidence: site/index.html, site/workbench.html, site/lesson-*.html, site/bridge-*.html
Facts: lesson_pages=118, bridge_pages=11, measurement_artifacts=28

## Identify and implement one generated lab scaffold for every GPUMODE lesson.
Status: proven-with-runtime-caveat
Evidence: LESSON-LAB-GOAL.md, lesson-labs/index.json, lesson-labs/run-report.json, site/lesson-labs.html, scripts/verify_lesson_labs.py
Facts: lesson_labs=118, lesson_lab_contracts_passed=118, lesson_lab_pages=118, lessons_without_direct_project_before_generation=87
Caveat: Generated lesson labs are local CPU-proxy implementations with explicit promotion tasks for real CUDA/Triton/HIP/JAX/serving-runtime follow-up on a GPU host.

## Plan and implement deliberate comprehensive labs that combine related lessons into real code programs.
Status: proven-with-runtime-caveat
Evidence: comprehensive-labs/PLAN.md, comprehensive-labs/gpumode_lab_suite, comprehensive-labs/run-report.json, scripts/verify_comprehensive_labs.py
Facts: comprehensive_labs=8, covered_lessons=118, passed_comprehensive_labs=8
Caveat: Comprehensive labs run locally as Python implementations/models; GPU-specific promotion remains environment-gated.

## Provide a kernel benchmark harness with real CUDA/Triton source families and local correctness/timing reports.
Status: proven-with-runtime-caveat
Evidence: kernel-benchmarks/PLAN.md, kernel-benchmarks/README.md, kernel-benchmarks/kernels/cuda, kernel-benchmarks/kernels/triton, kernel-benchmarks/reports/kernel-benchmark-report.json, site/kernel-benchmarks.html, scripts/verify_kernel_benchmarks.py
Facts: benchmarks=14, passed=14, covered_lessons=118, torch_device=cpu, nvcc=False
Caveat: CUDA/Triton source files are present; local benchmark execution uses the available PyTorch device and records missing accelerator tooling explicitly.

## Inspect compiler/runtime source features and promotion risks across CUDA, Triton, ROCm/HIP, and custom-op code.
Status: proven-with-runtime-caveat
Evidence: compiler-runtime-inspection/compiler-runtime-report.json, compiler-runtime-inspection/reports/compiler-runtime-report.md, site/compiler-runtime-inspection.html, scripts/run_compiler_runtime_inspection.py, scripts/verify_compiler_runtime_inspection.py
Facts: status=inspection-ready, sources=13, groups=['cuda', 'custom-op', 'hip', 'triton'], feature_counts={'global_kernel': 10, 'shared_memory': 4, 'barrier': 4, 'vectorized_load': 4, 'tensor_core_hint': 5, 'launch_indexing': 10, 'bounds_mask': 10, 'atomic': 0}, risk_counts={'tensor_core_without_shape_contract': 2}
Caveat: Static source inspection is local evidence; PTX, Triton IR, LLVM, and profiler-counter validation remain GPU-host promotion work.

## Plan CUTLASS/CuTe tensor-core GEMM kernels with CTA, warp, MMA, pipeline, quantized operand, and fused epilogue constraints.
Status: proven-with-runtime-caveat
Evidence: tensor-core-gemm/tensor-core-gemm-report.json, tensor-core-gemm/reports/tensor-core-gemm-report.md, site/tensor-core-gemm.html, scripts/run_tensor_core_gemm.py, scripts/verify_tensor_core_gemm.py
Facts: status=tensor-core-gemm-ready, scenarios=5, tensor_core_eligible=5, fused_epilogues=5, source_facts={'kernel_benchmarks': 14, 'compiler_sources': 13, 'autotune_records': 18, 'quantization_formats': 7, 'numerical_scenarios': 5}
Caveat: Local GEMM evidence is a design planner; final acceptance requires real CUTLASS/CuTe compilation, SASS checks for MMA instructions, and cuBLAS/Triton comparisons.

## Plan persistent Triton/CUDA kernels with residency, occupancy, launch amortization, L2 reuse, and producer/consumer constraints.
Status: proven-with-runtime-caveat
Evidence: persistent-kernels/persistent-kernels-report.json, persistent-kernels/reports/persistent-kernels-report.md, site/persistent-kernels.html, scripts/run_persistent_kernels.py, scripts/verify_persistent_kernels.py
Facts: status=persistent-kernels-ready, scenarios=6, passed=5, families=5, producer_consumer=4
Caveat: Local persistent-kernel evidence is a design model; final acceptance requires Nsight Compute occupancy, register, shared-memory, L2, DRAM, and launch-duration counters on a GPU host.

## Plan parallel primitives for reduction, scan, compaction, radix sort, histogram, and segmented reduction.
Status: proven-with-runtime-caveat
Evidence: parallel-primitives/parallel-primitives-report.json, parallel-primitives/reports/parallel-primitives-report.md, site/parallel-primitives.html, scripts/run_parallel_primitives.py, scripts/verify_parallel_primitives.py
Facts: status=parallel-primitives-ready, scenarios=6, passed=6, primitives=6, stable_order=3
Caveat: Local primitive evidence is a design model; final acceptance requires measured scan, reduction, histogram, compaction, sort, and segmented-reduction counters on a GPU host.

## Define runtime gates for CPU, CUDA, Triton, ROCm/HIP, profiler, and distributed machines.
Status: proven-with-runtime-caveat
Evidence: runtime-matrix/matrix.json, runtime-matrix/MATRIX.md, site/runtime-matrix.html, scripts/verify_runtime_matrix.py
Facts: profiles=43, ready=39, fallback=4, blocked=0, torch_device=cpu
Caveat: Non-CPU profiles may be source-ready local fallback when CUDA, ROCm, profiler, or distributed runtime tools are not installed locally.

## Normalize profiler evidence from Nsight Compute, Nsight Systems, and rocprof-shaped exports.
Status: proven-with-runtime-caveat
Evidence: profiler-evidence/fixtures, profiler-evidence/reports/profiler-evidence-report.json, profiler-evidence/reports/profiler-evidence-report.md, site/profiler-evidence.html, scripts/verify_profiler_evidence.py
Facts: rows=9, sources=3, classifications=['cache-locality', 'communication', 'compute-occupancy', 'host-device-transfer', 'launch-overhead', 'memory-bandwidth', 'mixed', 'tensor-core-compute']
Caveat: Fixtures are deterministic local stand-ins; GPU hosts should replace them with real ncu, nsys, or rocprof exports using the same schema.

## Replay LLM serving traces with TTFT, TPOT, throughput, prefix-cache, and KV-pressure metrics.
Status: proven-with-runtime-caveat
Evidence: serving-traces/fixtures, serving-traces/reports/serving-trace-report.json, serving-traces/reports/serving-trace-report.md, site/serving-traces.html, scripts/verify_serving_traces.py
Facts: traces=3, passed=3, policies=['continuous-batching-prefix-cache', 'static-batching'], prefix_cache_blocks_saved=642, speedups=[2.9881, 2.0144, 1.0092]
Caveat: The replay is a deterministic local serving model; GPU hosts should feed real vLLM/SGLang/TGI traces into the same schema.

## Model KV-cache and PagedAttention allocator behavior for fragmentation, prefix reuse, eviction, and admission pressure.
Status: proven-with-runtime-caveat
Evidence: kv-cache-paged-attention/kv-cache-report.json, kv-cache-paged-attention/reports/kv-cache-report.md, site/kv-cache-paged-attention.html, scripts/run_kv_cache_paged_attention.py, scripts/verify_kv_cache_paged_attention.py
Facts: status=kv-cache-ready, scenarios=5, passed=5, prefix_blocks_reused=648, source_facts={'serving_traces': 3, 'serving_prefix_blocks_saved': 642, 'serving_engines': 5, 'cuda_graph_capture_ready': 3, 'scheduling_tenants': 5}
Caveat: Local KV-cache evidence is an allocator model; real acceptance requires vLLM/SGLang block-table telemetry, GPU memory snapshots, and profiler traces.

## Connect FlashAttention online-softmax tiling to vLLM-style prefill/decode scheduling, KV reuse, CUDA Graph buckets, and profiler promotion.
Status: proven-with-runtime-caveat
Evidence: attention-serving-stack/attention-serving-report.json, attention-serving-stack/reports/attention-serving-report.md, site/attention-serving-stack.html, scripts/run_attention_serving_stack.py, scripts/verify_attention_serving_stack.py
Facts: status=attention-serving-ready, scenarios=5, passed=5, prefix_blocks_reused=28512, source_facts={'kernel_benchmarks': 14, 'kv_cache_scenarios': 5, 'serving_traces': 3, 'serving_engines': 5, 'numerical_scenarios': 5, 'cuda_graph_capture_ready': 3}
Caveat: Local attention-serving evidence models kernel/serving accounting; real acceptance requires CUDA/Triton/ROCm attention kernel timing, nsys/ncu traces, and replayed serving requests.

## Model FlashAttention backward training kernels with dQ, dK, dV, dSoftmax, recompute, dropout, GQA, and gradient-error checks.
Status: proven-with-runtime-caveat
Evidence: flash-attention-backward/flash-attention-backward-report.json, flash-attention-backward/reports/flash-attention-backward-report.md, site/flash-attention-backward.html, scripts/run_flash_attention_backward.py, scripts/verify_flash_attention_backward.py
Facts: status=flash-attention-backward-ready, scenarios=6, passed=6, dropout=1, grouped_query=1, source_facts={'attention_scenarios': 5, 'primitive_scenarios': 6, 'persistent_scenarios': 6, 'numerical_scenarios': 5, 'profiler_rows': 9, 'tensor_core_scenarios': 5}
Caveat: Local FlashAttention backward evidence is an analytical training-kernel model; real acceptance requires CUDA/Triton backward kernels, gradient comparisons, and ncu/nsys training-step counters on a GPU host.

## Model sparse and ragged attention kernels for block-sparse, sliding-window, dilated, neighborhood, top-k, metadata, load-balance, decode, and backward paths.
Status: proven-with-runtime-caveat
Evidence: sparse-attention-kernels/sparse-attention-report.json, sparse-attention-kernels/reports/sparse-attention-report.md, site/sparse-attention-kernels.html, scripts/run_sparse_attention_kernels.py, scripts/verify_sparse_attention_kernels.py
Facts: status=sparse-attention-ready, scenarios=6, passed=6, patterns=6, ragged=2, backward=5, source_facts={'attention_scenarios': 5, 'flash_backward_scenarios': 6, 'kv_cache_scenarios': 5, 'primitive_scenarios': 6, 'moe_scenarios': 5, 'profiler_rows': 9}
Caveat: Local sparse attention evidence is an analytical kernel model; real acceptance requires measured block-sparse, ragged-decode, sparse-backward, metadata-build, and load-balance profiler evidence on a GPU host.

## Model fused LLM training kernels for RMSNorm/residual backward, SwiGLU MLP fusion, cross-entropy/z-loss, multi-tensor AdamW, grad clipping/unscale, dropout/residual/norm, and checkpoint-safe fusion.
Status: proven-with-runtime-caveat
Evidence: fused-training-kernels/fused-training-report.json, fused-training-kernels/reports/fused-training-report.md, site/fused-training-kernels.html, scripts/run_fused_training_kernels.py, scripts/verify_fused_training_kernels.py
Facts: status=fused-training-ready, scenarios=6, passed=6, families=5, backward=4, optimizer_state=2, source_facts={'custom_op_cases': 4, 'model_cases': 3, 'flash_backward_scenarios': 6, 'training_optimizer_scenarios': 6, 'quantization_formats': 7, 'profiler_rows': 9}
Caveat: Local fused training evidence is an analytical kernel model; real acceptance requires measured CUDA/Triton fused norm, MLP, loss, optimizer, grad-scale, and checkpoint-step profiler evidence on a GPU host.

## Compare production inference engines across vLLM, Hugging Face TGI, SGLang, TensorRT-LLM, and HF Transformers scenarios.
Status: proven-with-runtime-caveat
Evidence: serving-engine-comparison/serving-engine-comparison.json, serving-engine-comparison/reports/serving-engine-comparison.md, site/serving-engine-comparison.html, scripts/run_serving_engine_comparison.py, scripts/verify_serving_engine_comparison.py
Facts: status=comparison-ready, engines=5, scenarios=5, engine_wins={'tensorrt-llm': 2, 'vllm': 3}
Caveat: Current engine scores are deterministic local estimates derived from replay traces; production acceptance still requires measured GPU-host serving benchmarks.

## Model speculative decoding serving with draft/target verification, acceptance-rate gates, rollback pressure, wasted draft tokens, KV commits, TTFT/TPOT, throughput, and scheduler policy.
Status: proven-with-runtime-caveat
Evidence: speculative-decoding-serving/speculative-decoding-report.json, speculative-decoding-serving/reports/speculative-decoding-report.md, site/speculative-decoding-serving.html, scripts/run_speculative_decoding_serving.py, scripts/verify_speculative_decoding_serving.py
Facts: status=speculative-decoding-ready, scenarios=6, passed=4, review=2, engines=5, policies=2, min_acceptance=0.43, source_facts={'serving_traces': 3, 'kv_cache_scenarios': 5, 'attention_serving_scenarios': 5, 'serving_engines': 5, 'cuda_graph_capture_ready': 3, 'profiler_rows': 9}
Caveat: Local speculative decoding evidence is a deterministic scheduler model; real acceptance requires Colab/GPU-host draft and target model traces, KV commit telemetry, rollback counts, and profiler evidence.

## Plan multi-GPU topology and parallelism choices for serving and training workloads.
Status: proven-with-runtime-caveat
Evidence: distributed-topology/distributed-topology-plan.json, distributed-topology/reports/distributed-topology-plan.md, site/distributed-topology.html, scripts/run_distributed_topology.py, scripts/verify_distributed_topology.py
Facts: status=topology-plan-ready, topologies=5, workloads=5, candidates=17, rejected=8
Caveat: Topology and parallelism estimates are source-ready locally; final acceptance requires measured NCCL/RCCL bandwidth on the selected GPU fabric.

## Model distributed collective algorithms for all-reduce, reduce-scatter, all-gather, all-to-all, broadcast, overlap, and backend portability.
Status: proven-with-runtime-caveat
Evidence: distributed-collectives/distributed-collectives-report.json, distributed-collectives/reports/distributed-collectives-report.md, site/distributed-collectives.html, scripts/run_distributed_collectives.py, scripts/verify_distributed_collectives.py
Facts: status=distributed-collectives-ready, scenarios=6, collectives=5, passed=6, backends=['nccl', 'nccl/nvshmem', 'rccl']
Caveat: Collective timing is deterministic locally; final acceptance needs measured NCCL/RCCL/NVSHMEM bandwidth and overlap traces on accelerator fabric.

## Model distributed training optimizer choices across DDP, ZeRO, FSDP, checkpointing, communication overlap, and pipeline bubbles.
Status: proven-with-runtime-caveat
Evidence: distributed-training-optimizer/distributed-training-optimizer-report.json, distributed-training-optimizer/reports/distributed-training-optimizer-report.md, site/distributed-training-optimizer.html, scripts/run_distributed_training_optimizer.py, scripts/verify_distributed_training_optimizer.py
Facts: status=training-optimizer-ready, scenarios=6, passed=5, strategies=5, checkpointed=5
Caveat: Training optimizer estimates are source-ready locally; final acceptance needs measured FSDP/ZeRO step time, memory peak, and overlap traces.

## Model MoE routing and all-to-all behavior for expert load balance, capacity drops, communication payload, and topology-sensitive bottlenecks.
Status: proven-with-runtime-caveat
Evidence: moe-routing-all-to-all/moe-routing-report.json, moe-routing-all-to-all/reports/moe-routing-report.md, site/moe-routing-all-to-all.html, scripts/run_moe_routing_all_to_all.py, scripts/verify_moe_routing_all_to_all.py
Facts: status=moe-routing-ready, scenarios=5, passed=4, tuning_required=1, source_facts={'topology_workloads': 5, 'topology_candidates': 17, 'serving_engines': 5, 'kv_cache_scenarios': 5, 'scheduling_policies': 4}
Caveat: Local MoE evidence is a deterministic routing and communication model; real acceptance requires all-to-all traces, expert-load histograms, and per-expert GPU timings.

## Plan hardware capacity, memory headroom, bottleneck class, power, and cost for kernel, serving, and training workloads.
Status: proven-with-runtime-caveat
Evidence: hardware-capacity-planning/hardware-capacity-plan.json, hardware-capacity-planning/reports/hardware-capacity-plan.md, site/hardware-capacity.html, scripts/run_hardware_capacity_plan.py, scripts/verify_hardware_capacity_plan.py
Facts: status=capacity-plan-ready, profiles=6, workloads=5, recommendations=5, rejected=15, source_facts={'kernel_benchmarks': 14, 'profiler_rows': 9, 'profiler_classifications': ['cache-locality', 'communication', 'compute-occupancy', 'host-device-transfer', 'launch-overhead', 'memory-bandwidth', 'mixed', 'tensor-core-compute'], 'serving_scenarios': 5, 'distributed_topologies': 5}
Caveat: Capacity, power, cost, and throughput are modeled locally; real production claims require GPU-host telemetry for memory use, power draw, tokens/sec, and profiler counters.

## Evaluate quantization and memory-format tradeoffs for compression, accuracy drift, dequantization cost, serving fit, and GPU promotion.
Status: proven-with-runtime-caveat
Evidence: quantization-memory-formats/quantization-report.json, quantization-memory-formats/reports/quantization-report.md, site/quantization-memory-formats.html, scripts/run_quantization_memory_formats.py, scripts/verify_quantization_memory_formats.py
Facts: status=quantization-ready, formats=7, passed=4, calibration_needed=3, source_facts={'kernel_benchmarks': 14, 'model_cases': 3, 'serving_engines': 5, 'hardware_profiles': 6}
Caveat: Local quantization evidence is a CPU simulation; real throughput claims require fused GPU dequantization kernels, low-precision tensor-core paths, and measured serving traces.

## Define numerical reproducibility and precision drift tolerance policy across deterministic, fast-math, low-precision, and reduction-order cases.
Status: proven-with-runtime-caveat
Evidence: numerical-reproducibility/numerical-reproducibility-report.json, numerical-reproducibility/reports/numerical-reproducibility-report.md, site/numerical-reproducibility.html, scripts/run_numerical_reproducibility.py, scripts/verify_numerical_reproducibility.py
Facts: status=reproducibility-ready, scenarios=5, passed=4, tolerance_reviews=1, source_facts={'quantization_formats': 7, 'kernel_benchmarks': 14, 'model_cases': 3, 'moe_scenarios': 5}
Caveat: Local reproducibility evidence is CPU-based; real acceptance requires repeated CUDA, Triton, and ROCm runs with deterministic flags and model-level drift checks.

## Model CUDA Graph capture eligibility and latency stabilization for launch-overhead-bound serving paths.
Status: proven-with-runtime-caveat
Evidence: cuda-graphs-latency/cuda-graphs-latency-report.json, cuda-graphs-latency/reports/cuda-graphs-latency-report.md, site/cuda-graphs-latency.html, scripts/run_cuda_graphs_latency.py, scripts/verify_cuda_graphs_latency.py
Facts: status=cuda-graphs-ready, scenarios=5, capture_ready=3, fallback_required=2, source_facts={'serving_traces': 3, 'profiler_launch_overhead_rows': 1, 'serving_engines': 5, 'torch_device': 'cpu'}
Caveat: Local CUDA Graphs evidence is a deterministic latency model; real acceptance requires CUDA graph capture/replay traces from Nsight Systems and kernel counters from Nsight Compute.

## Plan multi-tenant GPU scheduling and isolation for serving/training workloads using MIG/MPS/Kubernetes-style placement, fairness, and SLO evidence.
Status: proven-with-runtime-caveat
Evidence: multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json, multi-tenant-gpu-scheduling/reports/multi-tenant-scheduling-report.md, site/multi-tenant-scheduling.html, scripts/run_multi_tenant_gpu_scheduling.py, scripts/verify_multi_tenant_gpu_scheduling.py
Facts: status=scheduling-ready, policies=4, tenants=5, accepted=4, recommended_policy=cluster-queue, source_facts={'hardware_profiles': 6, 'capacity_workloads': 5, 'topologies': 5, 'serving_traces': 3, 'cuda_graph_capture_ready': 3}
Caveat: Local scheduling evidence is a deterministic placement model; real acceptance requires Kubernetes device-plugin inventory, MIG/MPS telemetry, and measured per-tenant latency/throughput.

## Integrate kernel work into a PyTorch custom operator with forward/backward checks and CUDA source promotion.
Status: proven-with-runtime-caveat
Evidence: custom-ops/custom_ops/fused_bias_gelu_residual.py, custom-ops/csrc, custom-ops/reports/custom-op-report.json, custom-ops/reports/custom-op-report.md, site/custom-ops.html, scripts/verify_custom_ops.py
Facts: operator=fused_bias_gelu_residual, cases=4, passed=4, compiled_extension_status=source-only, torch_device=cpu
Caveat: The compiled CUDA extension path is source-ready on this machine because local accelerator tooling is unavailable; CPU autograd verifies the numerical contract.

## Persist autotuning records that select starting configs for kernel families and model-integrated custom ops.
Status: proven-with-runtime-caveat
Evidence: autotune-db/autotune-db.json, autotune-db/reports/autotune-report.md, site/autotune-db.html, scripts/build_autotune_db.py, scripts/verify_autotune_db.py
Facts: records=18, families=['custom-op', 'fusion', 'matmul', 'memory', 'normalization', 'reduction'], source_reports=['kernel-benchmarks/reports/kernel-benchmark-report.json', 'custom-ops/reports/custom-op-report.json']
Caveat: The current selections are benchmark-derived local starting points; GPU hosts should refresh the same schema with measured accelerator sweeps.

## Run a model-shaped transformer block that uses custom-op fusion and autotune selections.
Status: proven-with-runtime-caveat
Evidence: model-integration/model_integration/tiny_transformer.py, model-integration/reports/tiny-transformer-report.json, model-integration/reports/tiny-transformer-report.md, site/model-integration.html, scripts/verify_model_integration.py
Facts: model=tiny-causal-transformer-block, cases=3, passed=3, uses_custom_op=fused_bias_gelu_residual, selected_tuning={'matmul': {'record_id': 'matmul-128', 'shape_class': 'medium-square', 'config_id': 'tensorcore-64x64x32', 'estimated_speedup_vs_measured': 1.3889}, 'normalization': {'record_id': 'softmax-4x1024', 'shape_class': 'wide', 'config_id': 'persistent-row', 'estimated_speedup_vs_measured': 1.3514}, 'custom-op': {'record_id': 'custom-op-decoder-hidden', 'shape_class': 'decoder-hidden', 'config_id': 'fused-forward-backward', 'estimated_speedup_vs_measured': 1.4286}}
Caveat: The model path runs locally in PyTorch CPU mode; accelerator-backed operator replacement is the GPU-host promotion step.

## Track regression metrics across kernel, custom-op, autotune, model, and serving layers.
Status: proven-with-runtime-caveat
Evidence: regression-ledger/regression-ledger.json, regression-ledger/reports/regression-ledger.md, site/regression-ledger.html, scripts/build_regression_ledger.py, scripts/verify_regression_ledger.py
Facts: metrics=746, passed=742, warnings=4, failed=0, source_reports={'kernel': 'kernel-benchmarks/reports/kernel-benchmark-report.json', 'custom_op': 'custom-ops/reports/custom-op-report.json', 'tensor_core_gemm': 'tensor-core-gemm/tensor-core-gemm-report.json', 'persistent_kernels': 'persistent-kernels/persistent-kernels-report.json', 'parallel_primitives': 'parallel-primitives/parallel-primitives-report.json', 'autotune': 'autotune-db/autotune-db.json', 'model': 'model-integration/reports/tiny-transformer-report.json', 'serving': 'serving-traces/reports/serving-trace-report.json', 'kv_cache': 'kv-cache-paged-attention/kv-cache-report.json', 'attention_serving': 'attention-serving-stack/attention-serving-report.json', 'flash_attention_backward': 'flash-attention-backward/flash-attention-backward-report.json', 'sparse_attention': 'sparse-attention-kernels/sparse-attention-report.json', 'fused_training': 'fused-training-kernels/fused-training-report.json', 'speculative_decoding': 'speculative-decoding-serving/speculative-decoding-report.json', 'quantization': 'quantization-memory-formats/quantization-report.json', 'numerical': 'numerical-reproducibility/numerical-reproducibility-report.json', 'cuda_graphs': 'cuda-graphs-latency/cuda-graphs-latency-report.json', 'distributed_collectives': 'distributed-collectives/distributed-collectives-report.json', 'distributed_training': 'distributed-training-optimizer/distributed-training-optimizer-report.json', 'moe_routing': 'moe-routing-all-to-all/moe-routing-report.json', 'multi_tenant': 'multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json'}
Caveat: Current thresholds compare against local generated metrics; GPU-host runs should persist their own measured baseline history.

## Generate an ordered GPU-host promotion manifest for accelerator-only validation.
Status: proven-with-runtime-caveat
Evidence: gpu-promotion/gpu-host-promotion-manifest.json, gpu-promotion/reports/gpu-host-promotion-runbook.md, site/gpu-promotion.html, scripts/build_gpu_promotion.py, scripts/verify_gpu_promotion.py
Facts: steps=18, ready_on_this_host=1, ready_on_gpu_host=17, local_capabilities={'python': True, 'torch': True, 'torch_device': 'cpu', 'triton': True, 'jax': True, 'nvcc': False, 'hipcc': False, 'nvidia_smi': False, 'nsys': False, 'ncu': False, 'rocprof': False, 'torchrun': True}
Caveat: This host lacks CUDA/ROCm/profiler hardware tools, so accelerator-only steps are intentionally marked ready-on-gpu-host.

## Plan the GPU-host promotion commands as a dry-run-safe executable suite.
Status: proven-with-runtime-caveat
Evidence: gpu-promotion/suite-run-report.json, gpu-promotion/reports/suite-run-report.md, site/gpu-promotion-suite.html, scripts/run_gpu_promotion_suite.py, scripts/verify_gpu_promotion_suite.py
Facts: commands=88, steps=18, planned=69, skipped=19, status=dry-run-ready
Caveat: The local suite is a dry-run command plan; use --execute on a GPU host after reviewing placeholder commands.

## Import GPU-host run evidence and link it to CUDA, Triton, ROCm/HIP, profiler, serving, distributed, and regression promotion steps.
Status: proven-with-runtime-caveat
Evidence: gpu-runs/fixtures, gpu-runs/gpu-run-report.json, gpu-runs/reports/gpu-run-report.md, site/gpu-runs.html, scripts/verify_gpu_runs.py
Facts: runs=3, vendors=['AMD', 'NVIDIA', 'unknown'], promotion_steps=16, status=import-ready
Caveat: Current fixtures define the import contract; real GPU hosts should replace these rows with measured A100/H100/MI300 evidence.

## Lint GPU run fixtures and imports before accepting accelerator evidence.
Status: proven
Evidence: gpu-runs/import-lint-report.json, gpu-runs/reports/import-lint-report.md, site/gpu-import-lint.html, scripts/lint_gpu_run_imports.py
Facts: status=lint-clean, files=3, fixtures=2, imports=1, errors=0, warnings=0

## Separate sample fixtures, host-collected smoke runs, and real measured GPU evidence provenance.
Status: proven-with-runtime-caveat
Evidence: gpu-provenance/gpu-provenance-report.json, gpu-provenance/reports/gpu-provenance-report.md, site/gpu-provenance.html, scripts/verify_gpu_provenance.py
Facts: status=provenance-clear, real_gpu_evidence_status=not-present-on-this-host, measured_runs=0, sample_runs=2, host_collected_runs=1
Caveat: This host has no real measured GPU imports yet; sample fixtures remain schema examples only.

## Define per-step GPU measurement contracts with host class, metrics, thresholds, and queued/measured status.
Status: proven-with-runtime-caveat
Evidence: gpu-measurement-queue/gpu-measurement-queue.json, gpu-measurement-queue/reports/gpu-measurement-queue.md, site/gpu-measurement-queue.html, scripts/verify_gpu_measurement_queue.py
Facts: status=queue-ready, tasks=18, queued=18, measured=0, accepted=0, failed_measured=0, real_measured_completion=False
Caveat: Measurement contracts are ready locally; real measured completion still requires accelerator-host imports.

## Regression-test GPU measurement acceptance logic against canonical good and bad metric rows.
Status: proven
Evidence: gpu-measurement-queue/acceptance-logic-report.json, gpu-measurement-queue/reports/acceptance-logic-report.md, site/gpu-acceptance-logic.html, scripts/verify_gpu_acceptance_logic.py
Facts: status=passed, cases=18, accepted_good=18, rejected_bad=18

## Run GPU-host preflight before accelerator promotion execution.
Status: proven-with-runtime-caveat
Evidence: gpu-handoff/gpu-host-preflight.json, gpu-handoff/reports/gpu-host-preflight.md, site/gpu-host-preflight.html, scripts/run_gpu_host_preflight.py, scripts/verify_gpu_host_preflight.py
Facts: status=preflight-complete, accelerator_ready=False, steps=18, runnable=1, blocked=17
Caveat: This host is CPU-only for accelerator tooling; the preflight report records blocked GPU promotion steps instead of treating them as hidden failures.

## Package a portable GPU-host handoff bundle for accelerator execution and evidence collection.
Status: proven-with-runtime-caveat
Evidence: gpu-handoff/gpu-host-handoff.json, gpu-handoff/reports/gpu-host-handoff.md, gpu-handoff/bin/run-gpu-host-handoff.sh, site/gpu-handoff.html, scripts/verify_gpu_handoff.py
Facts: status=ready, commands=88, bundle_files=85, entrypoint=gpu-handoff/bin/run-gpu-host-handoff.sh
Caveat: The handoff is locally validated; execute mode still requires a real GPU host.

## Generate a concept exam and practical task bank for the full GPUMODE curriculum stack.
Status: proven-with-runtime-caveat
Evidence: assessment/question-bank.json, assessment/reports/assessment-report.md, site/assessment.html, scripts/verify_assessment.py
Facts: concept_questions=10, practical_tasks=38, total_points=240, tutorial_providers=5
Caveat: The bank grades expected reasoning and artifact evidence; hands-on GPU throughput answers still require GPU-host promotion.

## Score the assessment bank against current generated artifact evidence.
Status: proven-with-runtime-caveat
Evidence: assessment/grading-report.json, assessment/reports/grading-report.md, site/assessment-grading.html, scripts/grade_assessment.py, scripts/verify_assessment_grading.py
Facts: score=240, max_score=240, concept_count=10, practical_count=38, failed_count=0
Caveat: Concept checks are graded for answer-key/source readiness; practical tasks are graded against current generated artifacts.

## Grade the complete curriculum as a portfolio capstone with a scored acceptance rubric.
Status: proven-with-runtime-caveat
Evidence: capstone-acceptance/capstone-acceptance.json, capstone-acceptance/reports/capstone-acceptance.md, site/capstone-acceptance.html, scripts/build_capstone_acceptance.py, scripts/verify_capstone_acceptance.py
Facts: score=400, max_score=400, criteria=40, failed_criteria=0, status=accepted-with-runtime-caveats
Caveat: The capstone is accepted with explicit runtime caveats because accelerator hardware validation remains GPU-host gated.

## Include external CUDA/Triton/ROCm/HIP/JAX/Hugging Face tutorial sources.
Status: proven
Evidence: analysis/tutorial-sources.json, analysis/tutorial-exercise-paths.json
Facts: tutorial_sources=18, providers=['AMD ROCm', 'Hugging Face', 'JAX Scaling Book', 'NVIDIA', 'Triton'], exercise_paths=11

## Finish with a queryable workbench recommending bottleneck classes, lessons, papers, labs, and latest measurements.
Status: proven
Evidence: analysis/gpu-systems-workbench.json, scripts/query_workbench.py, scripts/query_measurements.py
Facts: profiles=11, latest_measurement_rows=28, paper_json=2412
