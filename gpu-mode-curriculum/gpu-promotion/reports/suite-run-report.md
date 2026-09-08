# GPU Promotion Suite Run

Generated: `2026-09-08T06:46:07.499881+00:00`
Run ID: `local-suite-dry-run`
Mode: `dry-run`
Status: `dry-run-ready`

| order | step | status | command |
|---:|---|---|---|
| 1 | `cuda-kernel-compile` | planned | `nvcc -O3 kernel-benchmarks/kernels/cuda/memory.cu -c -o /tmp/gpumode-memory.o` |
| 2 | `cuda-kernel-compile` | planned | `nvcc -O3 kernel-benchmarks/kernels/cuda/reduction.cu -c -o /tmp/gpumode-reduction.o` |
| 3 | `cuda-kernel-compile` | planned | `nvcc -O3 kernel-benchmarks/kernels/cuda/softmax_layernorm.cu -c -o /tmp/gpumode-softmax-layernorm.o` |
| 4 | `cuda-kernel-compile` | planned | `nvcc -O3 kernel-benchmarks/kernels/cuda/matmul_mlp.cu -c -o /tmp/gpumode-matmul-mlp.o` |
| 5 | `eager-kernel-suite-cuda` | planned | `python3 scripts/run_kernel_benchmarks.py --repeats 7` |
| 6 | `triton-kernel-sweep` | planned | `python3 kernel-benchmarks/kernels/triton/memory.py` |
| 7 | `triton-kernel-sweep` | planned | `python3 kernel-benchmarks/kernels/triton/reduction.py` |
| 8 | `triton-kernel-sweep` | planned | `python3 kernel-benchmarks/kernels/triton/softmax_layernorm.py` |
| 9 | `triton-kernel-sweep` | planned | `python3 kernel-benchmarks/kernels/triton/matmul_mlp.py` |
| 10 | `triton-kernel-sweep` | planned | `python3 scripts/run_kernel_benchmarks.py` |
| 11 | `triton-kernel-families` | planned | `python3 kernel-benchmarks/run_triton_families_cuda.py` |
| 12 | `tensor-core-gemm` | planned | `python3 scripts/run_tensor_core_gemm.py` |
| 13 | `tensor-core-gemm` | planned | `python3 scripts/verify_tensor_core_gemm.py` |
| 14 | `tensor-core-gemm` | skipped-placeholder | `ncu --set full -o tensor-core-gemm python3 <cutlass_gemm_probe.py>` |
| 15 | `tensor-core-gemm` | skipped-placeholder | `cuobjdump --dump-sass <cutlass_gemm_binary>` |
| 16 | `low-precision-native` | planned | `python3 quantization-memory-formats/run_low_precision_cuda.py` |
| 17 | `trained-digits-quality-cuda` | planned | `python3 quantization-memory-formats/run_digits_cuda.py` |
| 18 | `rl-simulation-cuda` | planned | `python3 rl-gpu-simulation/run_vectorized_simulation.py --device cuda` |
| 19 | `rl-policy-quality-cuda` | planned | `python3 rl-gpu-simulation/run_policy_quality.py --device cuda` |
| 20 | `triton-layout-cuda` | planned | `python3 layout-algebra/run_triton_layout_cuda.py --device cuda` |
| 21 | `bank-conflict-cuda` | planned | `python3 layout-algebra/run_bank_conflict_cuda.py` |
| 22 | `cuda-graphs-native` | planned | `python3 cuda-graphs-latency/run_cuda_graphs_cuda.py` |
| 23 | `persistent-kernels` | planned | `python3 scripts/run_persistent_kernels.py` |
| 24 | `persistent-kernels` | planned | `python3 scripts/verify_persistent_kernels.py` |
| 25 | `persistent-kernels` | planned | `python3 kernel-benchmarks/kernels/triton/softmax_layernorm.py` |
| 26 | `persistent-kernels` | planned | `python3 kernel-benchmarks/kernels/triton/matmul_mlp.py` |
| 27 | `persistent-kernels` | skipped-placeholder | `ncu --set full -o persistent-kernels python3 <persistent_kernel_probe.py>` |
| 28 | `persistent-kernels` | planned | `python3 scripts/run_gpu_promotion_suite.py --run-id persistent-kernels --execute` |
| 29 | `parallel-primitives` | planned | `python3 scripts/run_parallel_primitives.py` |
| 30 | `parallel-primitives` | planned | `python3 scripts/verify_parallel_primitives.py` |
| 31 | `parallel-primitives` | planned | `python3 kernel-benchmarks/kernels/triton/reduction.py` |
| 32 | `parallel-primitives` | planned | `nvcc -O3 kernel-benchmarks/kernels/cuda/reduction.cu -c -o /tmp/gpumode-reduction.o` |
| 33 | `parallel-primitives` | skipped-placeholder | `ncu --set full -o parallel-primitives python3 <parallel_primitives_probe.py>` |
| 34 | `parallel-primitives` | planned | `python3 scripts/run_gpu_promotion_suite.py --run-id parallel-primitives --execute` |
| 35 | `torch-custom-extension` | planned | `python3 scripts/run_custom_ops.py` |
| 36 | `torch-custom-extension` | planned | `python3 scripts/verify_custom_ops.py` |
| 37 | `model-integration-gpu` | planned | `python3 scripts/build_autotune_db.py` |
| 38 | `model-integration-gpu` | planned | `python3 scripts/run_model_integration.py` |
| 39 | `model-integration-gpu` | planned | `python3 scripts/verify_model_integration.py` |
| 40 | `neural-serving-cuda` | planned | `python3 model-integration/run_neural_serving_cuda.py` |
| 41 | `trained-neural-quality-cuda` | planned | `python3 model-integration/run_trained_neural_quality_cuda.py --device cuda` |
| 42 | `paged-kv-gather-cuda` | planned | `python3 gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_paged_kv_cuda.py` |
| 43 | `paged-attention-cuda` | planned | `python3 gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_paged_attention_cuda.py` |
| 44 | `serving-tail-load-cuda` | planned | `python3 model-integration/run_serving_tail_load_cuda.py` |
| 45 | `vllm-serving-trace` | skipped-placeholder | `vllm serve <model> --enable-prefix-caching` |
| 46 | `vllm-serving-trace` | planned | `python3 scripts/run_serving_traces.py` |
| 47 | `vllm-serving-trace` | planned | `python3 scripts/verify_serving_traces.py` |
| 48 | `attention-serving-stack` | planned | `python3 scripts/run_attention_serving_stack.py` |
| 49 | `attention-serving-stack` | planned | `python3 scripts/verify_attention_serving_stack.py` |
| 50 | `attention-serving-stack` | skipped-placeholder | `nsys profile -o flashattention-serving python3 <vllm_trace_replay.py>` |
| 51 | `attention-serving-stack` | skipped-placeholder | `ncu --set full -o flashattention-kernel python3 <flash_attention_probe.py>` |
| 52 | `flash-attention-backward` | planned | `python3 scripts/run_flash_attention_backward.py` |
| 53 | `flash-attention-backward` | planned | `python3 scripts/verify_flash_attention_backward.py` |
| 54 | `flash-attention-backward` | planned | `python3 scripts/run_attention_serving_stack.py` |
| 55 | `flash-attention-backward` | skipped-placeholder | `ncu --set full -o flash-attention-backward python3 <flash_attention_backward_probe.py>` |
| 56 | `flash-attention-backward` | skipped-placeholder | `nsys profile -o flash-attention-training-step python3 <flash_attention_training_step.py>` |
| 57 | `flash-attention-backward` | planned | `python3 scripts/run_gpu_promotion_suite.py --run-id flash-attention-backward --execute` |
| 58 | `sparse-attention-kernels` | planned | `python3 scripts/run_sparse_attention_kernels.py` |
| 59 | `sparse-attention-kernels` | planned | `python3 scripts/verify_sparse_attention_kernels.py` |
| 60 | `sparse-attention-kernels` | planned | `python3 scripts/run_attention_serving_stack.py` |
| 61 | `sparse-attention-kernels` | planned | `python3 scripts/run_flash_attention_backward.py` |
| 62 | `sparse-attention-kernels` | skipped-placeholder | `ncu --set full -o sparse-attention-kernels python3 <sparse_attention_probe.py>` |
| 63 | `sparse-attention-kernels` | skipped-placeholder | `nsys profile -o sparse-attention-ragged-decode python3 <ragged_decode_probe.py>` |
| 64 | `sparse-attention-kernels` | planned | `python3 scripts/run_gpu_promotion_suite.py --run-id sparse-attention-kernels --execute` |
| 65 | `fused-training-kernels` | planned | `python3 scripts/run_fused_training_kernels.py` |
| 66 | `fused-training-kernels` | planned | `python3 scripts/verify_fused_training_kernels.py` |
| 67 | `fused-training-kernels` | planned | `python3 scripts/run_model_integration.py` |
| 68 | `fused-training-kernels` | planned | `python3 scripts/run_distributed_training_optimizer.py` |
| 69 | `fused-training-kernels` | skipped-placeholder | `ncu --set full -o fused-training-kernels python3 <fused_training_probe.py>` |
| 70 | `fused-training-kernels` | skipped-placeholder | `nsys profile -o fused-training-step python3 <training_step_probe.py>` |
| 71 | `fused-training-kernels` | planned | `python3 scripts/run_gpu_promotion_suite.py --run-id fused-training-kernels --execute` |
| 72 | `speculative-decoding-serving` | planned | `python3 scripts/run_speculative_decoding_serving.py` |
| 73 | `speculative-decoding-serving` | planned | `python3 scripts/verify_speculative_decoding_serving.py` |
| 74 | `speculative-decoding-serving` | planned | `python3 scripts/run_serving_traces.py` |
| 75 | `speculative-decoding-serving` | planned | `python3 scripts/run_serving_engine_comparison.py` |
| 76 | `speculative-decoding-serving` | skipped-placeholder | `nsys profile -o speculative-decoding-serving python3 <speculative_serving_probe.py>` |
| 77 | `speculative-decoding-serving` | skipped-placeholder | `ncu --set full -o speculative-target-verify python3 <target_verify_probe.py>` |
| 78 | `speculative-decoding-serving` | planned | `python3 scripts/run_gpu_promotion_suite.py --run-id speculative-decoding-serving --execute` |
| 79 | `profiler-capture` | planned | `ncu --set full --target-processes all python3 scripts/run_kernel_benchmarks.py` |
| 80 | `profiler-capture` | planned | `nsys profile python3 scripts/run_model_integration.py` |
| 81 | `profiler-capture` | planned | `python3 scripts/run_profiler_evidence.py` |
| 82 | `profiler-capture` | planned | `python3 scripts/verify_profiler_evidence.py` |
| 83 | `rocm-hip-port` | planned | `hipcc programming-projects/rocm-hip-port/kernel.hip.cpp -o /tmp/rocm-hip-port` |
| 84 | `rocm-hip-port` | planned | `rocprof /tmp/rocm-hip-port` |
| 85 | `rocm-hip-port` | planned | `python3 scripts/verify_gpu_programming_projects.py` |
| 86 | `distributed-collectives` | planned | `python3 scripts/run_distributed_collectives.py` |
| 87 | `distributed-collectives` | planned | `python3 scripts/verify_distributed_collectives.py` |
| 88 | `distributed-collectives` | planned | `torchrun --nproc_per_node=2 scripts/run_distributed_collectives_benchmark.py` |
| 89 | `distributed-collectives` | planned | `python3 scripts/verify_distributed_collectives_benchmark.py` |
| 90 | `distributed-collectives` | planned | `nccl-tests/build/all_reduce_perf -b 8M -e 1G -f 2 -g 1` |
| 91 | `distributed-collectives` | skipped-placeholder | `rocprof <rccl_collective_benchmark>` |
| 92 | `distributed-collectives` | planned | `python3 scripts/gpu_workbench.py "nccl nvshmem all reduce bandwidth" --run-lab --dry-run` |
| 93 | `distributed-training-optimizer` | planned | `python3 scripts/run_distributed_training_optimizer.py` |
| 94 | `distributed-training-optimizer` | planned | `python3 scripts/verify_distributed_training_optimizer.py` |
| 95 | `distributed-training-optimizer` | skipped-placeholder | `torchrun --nproc_per_node=8 <fsdp_zero_training_step.py>` |
| 96 | `distributed-training-optimizer` | skipped-placeholder | `nsys profile -o fsdp-zero-step torchrun --nproc_per_node=8 <fsdp_zero_training_step.py>` |
| 97 | `full-gpu-regression` | planned | `python3 run_all.py` |
| 98 | `full-gpu-regression` | skipped-placeholder | `python3 scripts/collect_gpu_run.py --run-id <gpu-host-run-id>` |
| 99 | `full-gpu-regression` | planned | `python3 scripts/build_gpu_runs.py` |
| 100 | `full-gpu-regression` | planned | `python3 scripts/verify_gpu_runs.py` |
| 101 | `full-gpu-regression` | planned | `python3 scripts/build_regression_ledger.py` |
| 102 | `full-gpu-regression` | planned | `python3 scripts/verify_regression_ledger.py` |
