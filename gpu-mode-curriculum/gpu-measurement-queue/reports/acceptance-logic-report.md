# GPUMODE GPU Acceptance Logic

Generated: `2026-09-07T19:21:48.852811+00:00`
Status: `passed`
Accepted good cases: `18/18`
Rejected bad cases: `18/18`

| step | good accepted | bad rejected | checks |
|---|---:|---:|---|
| `attention-serving-stack` | `True` | `True` | cuda_available == true, attention_scenarios >= 5, hbm_reduction > 0, prefix_blocks_reused > 0, profiler_rows >= 1 |
| `cuda-kernel-compile` | `True` | `True` | nvcc == true, nvidia_smi == true, torch_device == cuda, passed_benchmarks >= 14 |
| `distributed-collectives` | `True` | `True` | torchrun == true, accelerator_ready == true, collective_scenarios >= 6, bandwidth_efficiency >= 0.45, overlap_gain > 0, nccl_or_rccl == true |
| `distributed-training-optimizer` | `True` | `True` | torchrun == true, accelerator_ready == true, training_optimizer_scenarios >= 6, passed_scenarios >= 4, max_memory_gb_per_gpu <= 80, step_time_ms > 0, optimizer_state_savings > 0 |
| `flash-attention-backward` | `True` | `True` | cuda_available == true, flash_backward_scenarios >= 6, gradient_paths >= 4, max_abs_error <= 0.02, hbm_reduction >= 0.40, recompute_overhead_ratio >= 0, occupancy_proxy >= 0.45 |
| `full-gpu-regression` | `True` | `True` | accelerator_ready == true, metric_count >= 79, failed_metrics == 0 |
| `fused-training-kernels` | `True` | `True` | cuda_available == true, fused_training_scenarios >= 6, family_count >= 5, backward_scenarios >= 4, optimizer_state_scenarios >= 2, max_abs_error <= 0.02, hbm_reduction >= 0.45, launch_reduction >= 0.45 |
| `model-integration-gpu` | `True` | `True` | accelerator_ready == true, passed_cases >= 3, uses_custom_op == fused_bias_gelu_residual |
| `parallel-primitives` | `True` | `True` | accelerator_ready == true, primitive_scenarios >= 6, work_efficiency >= 1.20, bandwidth_proxy_gbps > 0, occupancy_proxy >= 0.35, stable_order_scenarios >= 3 |
| `persistent-kernels` | `True` | `True` | triton == true, nvidia_smi == true, ncu == true, persistent_scenarios >= 6, speedup_vs_baseline >= 1.15, occupancy_proxy >= 0.30, hbm_reduction >= 0.15 |
| `profiler-capture` | `True` | `True` | ncu/nsys or rocprof available, profiler_rows >= 9 |
| `rocm-hip-port` | `True` | `True` | hipcc == true, rocprof == true, starter_status == ran |
| `sparse-attention-kernels` | `True` | `True` | cuda_available == true, sparse_attention_scenarios >= 6, pattern_count >= 6, ragged_scenarios >= 1, backward_scenarios >= 4, max_abs_error <= 0.02, hbm_reduction >= 0.55, load_balance_proxy >= 0.75 |
| `speculative-decoding-serving` | `True` | `True` | cuda_available == true, speculative_scenarios >= 6, passed_scenarios >= 4, engine_count >= 4, scheduler_policy_count >= 2, min_acceptance_rate < 0.50, max_speedup_vs_baseline >= 2.0, max_wasted_draft_ratio > 0.35 |
| `tensor-core-gemm` | `True` | `True` | nvcc == true, nvidia_smi == true, ncu == true, tensor_core_scenarios >= 5, mma_instruction_seen == true |
| `torch-custom-extension` | `True` | `True` | compiled_extension_status == cuda-ready, passed_cases >= 4 |
| `triton-kernel-sweep` | `True` | `True` | cuda_available == true, triton_cases >= 4, passed_benchmarks >= 14 |
| `vllm-serving-trace` | `True` | `True` | cuda_available == true, passed_traces >= 3, prefix_cache_blocks_saved > 0 |
