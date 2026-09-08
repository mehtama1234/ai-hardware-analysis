# GPUMODE GPU Measurement Queue

Generated: `2026-09-08T10:16:40.666200+00:00`
Status: `queue-ready`
Real measured completion: `False`
Measured tasks: `32/32`

| step | host class | status | accepted rows | commands | required metrics | thresholds |
|---|---|---|---:|---:|---|---|
| `cuda-kernel-compile` | nvidia-cuda | `measured-accepted` | 2/3 | 4 | nvcc, nvidia_smi, torch_device, passed_benchmarks | nvcc == true; nvidia_smi == true; torch_device == cuda; passed_benchmarks >= 14 |
| `eager-kernel-suite-cuda` | nvidia-cuda | `measured-accepted` | 1/1 | 1 | benchmark_count, passed, failed, accelerator_readiness | failed == 0; passed == benchmark_count; benchmark_count >= 14; accelerator_readiness.torch_device == cuda; accelerator_readiness.nvidia_smi == true |
| `triton-kernel-sweep` | nvidia-cuda | `measured-accepted` | 2/3 | 5 | cuda_available, triton_cases, passed_benchmarks | cuda_available == true; triton_cases >= 4; passed_benchmarks >= 14 |
| `triton-kernel-families` | accelerator-claim-scoped | `measured-accepted` | 1/1 | 1 | status | status in {passed, task_gate_passed} |
| `tensor-core-gemm` | nvidia-cuda-profiler | `measured-accepted` | 2/3 | 4 | nvcc, nvidia_smi, ncu, tensor_core_scenarios, mma_instruction_seen | nvcc == true; nvidia_smi == true; ncu == true; tensor_core_scenarios >= 5; mma_instruction_seen == true |
| `low-precision-native` | accelerator-claim-scoped | `measured-accepted` | 1/1 | 1 | status | status in {passed, task_gate_passed} |
| `trained-digits-quality-cuda` | accelerator-claim-scoped | `measured-accepted` | 1/1 | 1 | status | status in {passed, task_gate_passed} |
| `rl-simulation-cuda` | accelerator-claim-scoped | `measured-accepted` | 1/1 | 1 | status | status in {passed, task_gate_passed} |
| `rl-policy-quality-cuda` | accelerator-claim-scoped | `measured-accepted` | 1/1 | 1 | status | status in {passed, task_gate_passed} |
| `triton-layout-cuda` | accelerator-claim-scoped | `measured-accepted` | 1/1 | 1 | status | status in {passed, task_gate_passed} |
| `bank-conflict-cuda` | accelerator-claim-scoped | `measured-accepted` | 1/1 | 1 | status | status in {passed, task_gate_passed} |
| `cuda-graphs-native` | accelerator-claim-scoped | `measured-accepted` | 1/1 | 1 | status | status in {passed, task_gate_passed} |
| `persistent-kernels` | nvidia-cuda-profiler | `measured-accepted` | 2/2 | 6 | triton, nvidia_smi, ncu, persistent_scenarios, speedup_vs_baseline, occupancy_proxy, hbm_reduction | triton == true; nvidia_smi == true; ncu == true; persistent_scenarios >= 6; speedup_vs_baseline >= 1.15; occupancy_proxy >= 0.30; hbm_reduction >= 0.15 |
| `parallel-primitives` | nvidia-or-amd-profiler | `measured-accepted` | 2/3 | 6 | accelerator_ready, primitive_scenarios, work_efficiency, bandwidth_proxy_gbps, occupancy_proxy, stable_order_scenarios | accelerator_ready == true; primitive_scenarios >= 6; work_efficiency >= 1.20; bandwidth_proxy_gbps > 0; occupancy_proxy >= 0.35; stable_order_scenarios >= 3 |
| `torch-custom-extension` | nvidia-cuda | `measured-accepted` | 2/2 | 2 | compiled_extension_status, passed_cases | compiled_extension_status == cuda-ready; passed_cases >= 4 |
| `model-integration-gpu` | accelerator-torch | `measured-accepted` | 2/3 | 3 | accelerator_ready, passed_cases, uses_custom_op | accelerator_ready == true; passed_cases >= 3; uses_custom_op == fused_bias_gelu_residual |
| `neural-serving-cuda` | accelerator-claim-scoped | `measured-accepted` | 1/1 | 1 | status | status in {passed, task_gate_passed} |
| `trained-neural-quality-cuda` | accelerator-claim-scoped | `measured-accepted` | 1/1 | 1 | status | status in {passed, task_gate_passed} |
| `paged-kv-gather-cuda` | accelerator-claim-scoped | `measured-accepted` | 1/1 | 1 | status | status in {passed, task_gate_passed} |
| `paged-attention-cuda` | accelerator-claim-scoped | `measured-accepted` | 1/1 | 1 | status | status in {passed, task_gate_passed} |
| `serving-tail-load-cuda` | nvidia-cuda-serving | `measured-accepted` | 1/1 | 1 | status, gpu_execution_accepted, concurrency_levels, requests_per_level, rows | status == passed; gpu_execution_accepted == true; concurrency_levels == [1, 2, 4, 8]; requests_per_level >= 12; all rows have p95 and parity; vectorized batching observed above concurrency 1 |
| `vllm-serving-trace` | nvidia-cuda-serving | `measured-accepted` | 2/2 | 3 | cuda_available, passed_traces, prefix_cache_blocks_saved | cuda_available == true; passed_traces >= 3; prefix_cache_blocks_saved > 0 |
| `attention-serving-stack` | nvidia-cuda-serving-profiler | `measured-accepted` | 2/2 | 4 | cuda_available, attention_scenarios, hbm_reduction, prefix_blocks_reused, profiler_rows | cuda_available == true; attention_scenarios >= 5; hbm_reduction > 0; prefix_blocks_reused > 0; profiler_rows >= 1 |
| `flash-attention-backward` | nvidia-cuda-training-profiler | `measured-accepted` | 2/2 | 6 | cuda_available, flash_backward_scenarios, gradient_paths, max_abs_error, hbm_reduction, recompute_overhead_ratio, occupancy_proxy | cuda_available == true; flash_backward_scenarios >= 6; gradient_paths >= 4; max_abs_error <= 0.02; hbm_reduction >= 0.40; recompute_overhead_ratio >= 0; occupancy_proxy >= 0.45 |
| `sparse-attention-kernels` | nvidia-cuda-sparse-profiler | `measured-accepted` | 2/2 | 7 | cuda_available, sparse_attention_scenarios, pattern_count, ragged_scenarios, backward_scenarios, max_abs_error, hbm_reduction, load_balance_proxy | cuda_available == true; sparse_attention_scenarios >= 6; pattern_count >= 6; ragged_scenarios >= 1; backward_scenarios >= 4; max_abs_error <= 0.02; hbm_reduction >= 0.55; load_balance_proxy >= 0.75 |
| `fused-training-kernels` | nvidia-cuda-training-profiler | `measured-accepted` | 2/2 | 7 | cuda_available, fused_training_scenarios, family_count, backward_scenarios, optimizer_state_scenarios, max_abs_error, hbm_reduction, launch_reduction | cuda_available == true; fused_training_scenarios >= 6; family_count >= 5; backward_scenarios >= 4; optimizer_state_scenarios >= 2; max_abs_error <= 0.02; hbm_reduction >= 0.45; launch_reduction >= 0.45 |
| `speculative-decoding-serving` | nvidia-cuda-serving-profiler | `measured-accepted` | 2/2 | 7 | cuda_available, speculative_scenarios, passed_scenarios, engine_count, scheduler_policy_count, min_acceptance_rate, max_speedup_vs_baseline, max_wasted_draft_ratio | cuda_available == true; speculative_scenarios >= 6; passed_scenarios >= 4; engine_count >= 4; scheduler_policy_count >= 2; min_acceptance_rate < 0.50; max_speedup_vs_baseline >= 2.0; max_wasted_draft_ratio > 0.35 |
| `profiler-capture` | nvidia-or-amd-profiler | `measured-accepted` | 1/3 | 4 | ncu, nsys, rocprof, profiler_rows | ncu/nsys or rocprof available; profiler_rows >= 9 |
| `rocm-hip-port` | amd-rocm | `measured-failed` | 0/2 | 3 | hipcc, rocprof, starter_status | hipcc == true; rocprof == true; starter_status == ran |
| `distributed-collectives` | multi-gpu | `measured-failed` | 0/3 | 7 | torchrun, accelerator_ready, collective_scenarios, bandwidth_efficiency, overlap_gain, nccl_or_rccl | torchrun == true; accelerator_ready == true; collective_scenarios >= 6; bandwidth_efficiency >= 0.45; overlap_gain > 0; nccl_or_rccl == true |
| `distributed-training-optimizer` | multi-gpu-training | `measured-accepted` | 2/2 | 4 | torchrun, accelerator_ready, training_optimizer_scenarios, passed_scenarios, max_memory_gb_per_gpu, step_time_ms, optimizer_state_savings | torchrun == true; accelerator_ready == true; training_optimizer_scenarios >= 6; passed_scenarios >= 4; max_memory_gb_per_gpu <= 80; step_time_ms > 0; optimizer_state_savings > 0 |
| `full-gpu-regression` | final-gpu-regression | `measured-accepted` | 2/2 | 6 | accelerator_ready, metric_count, failed_metrics | accelerator_ready == true; metric_count >= 79; failed_metrics == 0 |
