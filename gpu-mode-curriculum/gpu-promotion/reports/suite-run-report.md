# GPU Promotion Suite Run

Generated: `2026-08-31T01:53:34.465532+00:00`
Run ID: `local-suite-dry-run`
Mode: `dry-run`
Status: `dry-run-ready`

| order | step | status | command |
|---:|---|---|---|
| 1 | `cuda-kernel-compile` | planned | `nvcc -O3 kernel-benchmarks/kernels/cuda/memory.cu -c -o /tmp/gpumode-memory.o` |
| 2 | `cuda-kernel-compile` | planned | `nvcc -O3 kernel-benchmarks/kernels/cuda/reduction.cu -c -o /tmp/gpumode-reduction.o` |
| 3 | `cuda-kernel-compile` | planned | `nvcc -O3 kernel-benchmarks/kernels/cuda/softmax_layernorm.cu -c -o /tmp/gpumode-softmax-layernorm.o` |
| 4 | `cuda-kernel-compile` | planned | `nvcc -O3 kernel-benchmarks/kernels/cuda/matmul_mlp.cu -c -o /tmp/gpumode-matmul-mlp.o` |
| 5 | `triton-kernel-sweep` | planned | `python3 kernel-benchmarks/kernels/triton/memory.py` |
| 6 | `triton-kernel-sweep` | planned | `python3 kernel-benchmarks/kernels/triton/reduction.py` |
| 7 | `triton-kernel-sweep` | planned | `python3 kernel-benchmarks/kernels/triton/softmax_layernorm.py` |
| 8 | `triton-kernel-sweep` | planned | `python3 kernel-benchmarks/kernels/triton/matmul_mlp.py` |
| 9 | `triton-kernel-sweep` | planned | `python3 scripts/run_kernel_benchmarks.py` |
| 10 | `tensor-core-gemm` | planned | `python3 scripts/run_tensor_core_gemm.py` |
| 11 | `tensor-core-gemm` | planned | `python3 scripts/verify_tensor_core_gemm.py` |
| 12 | `tensor-core-gemm` | skipped-placeholder | `ncu --set full -o tensor-core-gemm python3 <cutlass_gemm_probe.py>` |
| 13 | `tensor-core-gemm` | skipped-placeholder | `cuobjdump --dump-sass <cutlass_gemm_binary>` |
| 14 | `persistent-kernels` | planned | `python3 scripts/run_persistent_kernels.py` |
| 15 | `persistent-kernels` | planned | `python3 scripts/verify_persistent_kernels.py` |
| 16 | `persistent-kernels` | planned | `python3 kernel-benchmarks/kernels/triton/softmax_layernorm.py` |
| 17 | `persistent-kernels` | planned | `python3 kernel-benchmarks/kernels/triton/matmul_mlp.py` |
| 18 | `persistent-kernels` | skipped-placeholder | `ncu --set full -o persistent-kernels python3 <persistent_kernel_probe.py>` |
| 19 | `persistent-kernels` | planned | `python3 scripts/run_gpu_promotion_suite.py --run-id persistent-kernels --execute` |
| 20 | `parallel-primitives` | planned | `python3 scripts/run_parallel_primitives.py` |
| 21 | `parallel-primitives` | planned | `python3 scripts/verify_parallel_primitives.py` |
| 22 | `parallel-primitives` | planned | `python3 kernel-benchmarks/kernels/triton/reduction.py` |
| 23 | `parallel-primitives` | planned | `nvcc -O3 kernel-benchmarks/kernels/cuda/reduction.cu -c -o /tmp/gpumode-reduction.o` |
| 24 | `parallel-primitives` | skipped-placeholder | `ncu --set full -o parallel-primitives python3 <parallel_primitives_probe.py>` |
| 25 | `parallel-primitives` | planned | `python3 scripts/run_gpu_promotion_suite.py --run-id parallel-primitives --execute` |
| 26 | `torch-custom-extension` | planned | `python3 scripts/run_custom_ops.py` |
| 27 | `torch-custom-extension` | planned | `python3 scripts/verify_custom_ops.py` |
| 28 | `model-integration-gpu` | planned | `python3 scripts/build_autotune_db.py` |
| 29 | `model-integration-gpu` | planned | `python3 scripts/run_model_integration.py` |
| 30 | `model-integration-gpu` | planned | `python3 scripts/verify_model_integration.py` |
| 31 | `vllm-serving-trace` | skipped-placeholder | `vllm serve <model> --enable-prefix-caching` |
| 32 | `vllm-serving-trace` | planned | `python3 scripts/run_serving_traces.py` |
| 33 | `vllm-serving-trace` | planned | `python3 scripts/verify_serving_traces.py` |
| 34 | `attention-serving-stack` | planned | `python3 scripts/run_attention_serving_stack.py` |
| 35 | `attention-serving-stack` | planned | `python3 scripts/verify_attention_serving_stack.py` |
| 36 | `attention-serving-stack` | skipped-placeholder | `nsys profile -o flashattention-serving python3 <vllm_trace_replay.py>` |
| 37 | `attention-serving-stack` | skipped-placeholder | `ncu --set full -o flashattention-kernel python3 <flash_attention_probe.py>` |
| 38 | `flash-attention-backward` | planned | `python3 scripts/run_flash_attention_backward.py` |
| 39 | `flash-attention-backward` | planned | `python3 scripts/verify_flash_attention_backward.py` |
| 40 | `flash-attention-backward` | planned | `python3 scripts/run_attention_serving_stack.py` |
| 41 | `flash-attention-backward` | skipped-placeholder | `ncu --set full -o flash-attention-backward python3 <flash_attention_backward_probe.py>` |
| 42 | `flash-attention-backward` | skipped-placeholder | `nsys profile -o flash-attention-training-step python3 <flash_attention_training_step.py>` |
| 43 | `flash-attention-backward` | planned | `python3 scripts/run_gpu_promotion_suite.py --run-id flash-attention-backward --execute` |
| 44 | `sparse-attention-kernels` | planned | `python3 scripts/run_sparse_attention_kernels.py` |
| 45 | `sparse-attention-kernels` | planned | `python3 scripts/verify_sparse_attention_kernels.py` |
| 46 | `sparse-attention-kernels` | planned | `python3 scripts/run_attention_serving_stack.py` |
| 47 | `sparse-attention-kernels` | planned | `python3 scripts/run_flash_attention_backward.py` |
| 48 | `sparse-attention-kernels` | skipped-placeholder | `ncu --set full -o sparse-attention-kernels python3 <sparse_attention_probe.py>` |
| 49 | `sparse-attention-kernels` | skipped-placeholder | `nsys profile -o sparse-attention-ragged-decode python3 <ragged_decode_probe.py>` |
| 50 | `sparse-attention-kernels` | planned | `python3 scripts/run_gpu_promotion_suite.py --run-id sparse-attention-kernels --execute` |
| 51 | `fused-training-kernels` | planned | `python3 scripts/run_fused_training_kernels.py` |
| 52 | `fused-training-kernels` | planned | `python3 scripts/verify_fused_training_kernels.py` |
| 53 | `fused-training-kernels` | planned | `python3 scripts/run_model_integration.py` |
| 54 | `fused-training-kernels` | planned | `python3 scripts/run_distributed_training_optimizer.py` |
| 55 | `fused-training-kernels` | skipped-placeholder | `ncu --set full -o fused-training-kernels python3 <fused_training_probe.py>` |
| 56 | `fused-training-kernels` | skipped-placeholder | `nsys profile -o fused-training-step python3 <training_step_probe.py>` |
| 57 | `fused-training-kernels` | planned | `python3 scripts/run_gpu_promotion_suite.py --run-id fused-training-kernels --execute` |
| 58 | `speculative-decoding-serving` | planned | `python3 scripts/run_speculative_decoding_serving.py` |
| 59 | `speculative-decoding-serving` | planned | `python3 scripts/verify_speculative_decoding_serving.py` |
| 60 | `speculative-decoding-serving` | planned | `python3 scripts/run_serving_traces.py` |
| 61 | `speculative-decoding-serving` | planned | `python3 scripts/run_serving_engine_comparison.py` |
| 62 | `speculative-decoding-serving` | skipped-placeholder | `nsys profile -o speculative-decoding-serving python3 <speculative_serving_probe.py>` |
| 63 | `speculative-decoding-serving` | skipped-placeholder | `ncu --set full -o speculative-target-verify python3 <target_verify_probe.py>` |
| 64 | `speculative-decoding-serving` | planned | `python3 scripts/run_gpu_promotion_suite.py --run-id speculative-decoding-serving --execute` |
| 65 | `profiler-capture` | planned | `ncu --set full --target-processes all python3 scripts/run_kernel_benchmarks.py` |
| 66 | `profiler-capture` | planned | `nsys profile python3 scripts/run_model_integration.py` |
| 67 | `profiler-capture` | planned | `python3 scripts/run_profiler_evidence.py` |
| 68 | `profiler-capture` | planned | `python3 scripts/verify_profiler_evidence.py` |
| 69 | `rocm-hip-port` | planned | `hipcc programming-projects/rocm-hip-port/kernel.hip.cpp -o /tmp/rocm-hip-port` |
| 70 | `rocm-hip-port` | planned | `rocprof /tmp/rocm-hip-port` |
| 71 | `rocm-hip-port` | planned | `python3 scripts/verify_gpu_programming_projects.py` |
| 72 | `distributed-collectives` | planned | `python3 scripts/run_distributed_collectives.py` |
| 73 | `distributed-collectives` | planned | `python3 scripts/verify_distributed_collectives.py` |
| 74 | `distributed-collectives` | planned | `torchrun --nproc_per_node=2 scripts/run_distributed_collectives_benchmark.py` |
| 75 | `distributed-collectives` | planned | `python3 scripts/verify_distributed_collectives_benchmark.py` |
| 76 | `distributed-collectives` | planned | `nccl-tests/build/all_reduce_perf -b 8M -e 1G -f 2 -g 1` |
| 77 | `distributed-collectives` | skipped-placeholder | `rocprof <rccl_collective_benchmark>` |
| 78 | `distributed-collectives` | planned | `python3 scripts/gpu_workbench.py "nccl nvshmem all reduce bandwidth" --run-lab --dry-run` |
| 79 | `distributed-training-optimizer` | planned | `python3 scripts/run_distributed_training_optimizer.py` |
| 80 | `distributed-training-optimizer` | planned | `python3 scripts/verify_distributed_training_optimizer.py` |
| 81 | `distributed-training-optimizer` | skipped-placeholder | `torchrun --nproc_per_node=8 <fsdp_zero_training_step.py>` |
| 82 | `distributed-training-optimizer` | skipped-placeholder | `nsys profile -o fsdp-zero-step torchrun --nproc_per_node=8 <fsdp_zero_training_step.py>` |
| 83 | `full-gpu-regression` | planned | `python3 run_all.py` |
| 84 | `full-gpu-regression` | skipped-placeholder | `python3 scripts/collect_gpu_run.py --run-id <gpu-host-run-id>` |
| 85 | `full-gpu-regression` | planned | `python3 scripts/build_gpu_runs.py` |
| 86 | `full-gpu-regression` | planned | `python3 scripts/verify_gpu_runs.py` |
| 87 | `full-gpu-regression` | planned | `python3 scripts/build_regression_ledger.py` |
| 88 | `full-gpu-regression` | planned | `python3 scripts/verify_regression_ledger.py` |
