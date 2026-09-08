# GPU Host Promotion Runbook

Generated: `2026-09-08T10:36:24.772602+00:00`
Steps: `34`
Ready on this host: `1`
Ready on GPU host: `33`

## Local Capability Snapshot

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
- `torchrun`: `True`

## Steps

### cuda-kernel-compile: Compile CUDA kernel families
Status: `ready-on-gpu-host`
Missing locally: `nvcc, nvidia_smi`
Commands:
- `nvcc -O3 kernel-benchmarks/kernels/cuda/memory.cu -c -o /tmp/gpumode-memory.o`
- `nvcc -O3 kernel-benchmarks/kernels/cuda/reduction.cu -c -o /tmp/gpumode-reduction.o`
- `nvcc -O3 kernel-benchmarks/kernels/cuda/softmax_layernorm.cu -c -o /tmp/gpumode-softmax-layernorm.o`
- `nvcc -O3 kernel-benchmarks/kernels/cuda/matmul_mlp.cu -c -o /tmp/gpumode-matmul-mlp.o`
Expected evidence: `kernel-benchmarks/kernels/cuda/*.cu, kernel-benchmarks/reports/kernel-benchmark-report.json`
Validation: Re-run python3 scripts/verify_kernel_benchmarks.py and confirm torch_device=cuda in the report.

### eager-kernel-suite-cuda: Run the broad eager CUDA kernel suite
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 scripts/run_kernel_benchmarks.py --repeats 7`
Expected evidence: `kernel-benchmarks/reports/kernel-benchmark-report.json`
Validation: Require all 14 cases to pass with raw synchronized CUDA-event samples and explicit device labels; this suite does not attribute work to Triton or custom native kernels.

### triton-kernel-sweep: Run Triton kernels on CUDA
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 kernel-benchmarks/kernels/triton/memory.py`
- `python3 kernel-benchmarks/kernels/triton/reduction.py`
- `python3 kernel-benchmarks/kernels/triton/softmax_layernorm.py`
- `python3 kernel-benchmarks/kernels/triton/matmul_mlp.py`
- `python3 scripts/run_kernel_benchmarks.py`
Expected evidence: `kernel-benchmarks/reports/kernel-benchmark-report.json, autotune-db/autotune-db.json`
Validation: Refresh autotune records and verify selected configs after GPU timings are present.

### triton-kernel-families: Run Triton memory, reduction and normalization families on CUDA
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 kernel-benchmarks/run_triton_families_cuda.py`
Expected evidence: `kernel-benchmarks/reports/triton-families-cuda.json`
Validation: Check contiguous/strided copy, block reduction, softmax and layernorm against CUDA oracles, including non-power-of-two tail columns and synchronized samples.

### tensor-core-gemm: Build and profile CUTLASS/CuTe tensor-core GEMM
Status: `ready-on-gpu-host`
Missing locally: `nvcc, nvidia_smi, ncu`
Commands:
- `python3 scripts/run_tensor_core_gemm.py`
- `python3 scripts/verify_tensor_core_gemm.py`
- `ncu --set full -o tensor-core-gemm python3 <cutlass_gemm_probe.py>`
- `cuobjdump --dump-sass <cutlass_gemm_binary>`
Expected evidence: `tensor-core-gemm/tensor-core-gemm-report.json, tensor-core-gemm/reports/tensor-core-gemm-report.md, site/tensor-core-gemm.html`
Validation: GPU host should provide CUTLASS/CuTe build evidence, MMA instruction evidence, cuBLAS/Triton comparisons, and profiler counters.

### low-precision-native: Measure native CUDA FP16 compute and numerical drift
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 quantization-memory-formats/run_low_precision_cuda.py`
Expected evidence: `quantization-memory-formats/reports/low-precision-cuda.json`
Validation: Compare native FP16 and INT8 activation/weight matmul with an FP32 oracle (including an exact integer accumulator oracle), record memory bytes and synchronized CUDA-event samples, and keep packed INT4 and task-quality evidence separate.

### trained-digits-quality-cuda: Run the held-out trained-digits quality protocol on CUDA
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 quantization-memory-formats/run_digits_cuda.py`
Expected evidence: `quantization-memory-formats/reports/digits-quality-cuda.json`
Validation: Preserve the fixed seeds, split, 150-step Adam protocol and quality thresholds; compare FP32 and packed INT4 held-out accuracy and record CUDA-event inference samples.

### rl-simulation-cuda: Run vectorized reinforcement-learning environment transitions on CUDA
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 rl-gpu-simulation/run_vectorized_simulation.py --device cuda`
Expected evidence: `rl-gpu-simulation/reports/vectorized-simulation.json`
Validation: Compare the vectorized transition and reward path with the scalar oracle, record synchronized CUDA-event samples, and keep the deterministic grid-world scope separate from physics and policy-quality claims.

### rl-policy-quality-cuda: Train and evaluate a deterministic goal-policy on CUDA
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 rl-gpu-simulation/run_policy_quality.py --device cuda`
Expected evidence: `rl-gpu-simulation/reports/policy-quality.json`
Validation: Preserve fixed synthetic seeds and training steps, compare action accuracy and episodic success with the analytic oracle, and keep this supervised grid-world quality result separate from RL optimization and physics claims.

### triton-layout-cuda: Execute blocked and XOR-swizzled layout mappings in Triton
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 layout-algebra/run_triton_layout_cuda.py --device cuda`
Expected evidence: `layout-algebra/reports/triton-layout-cuda.json`
Validation: Compare every emitted device offset against the host layout algebra and record CUDA-event launch samples; this does not establish CuTe lowering, bank-conflict freedom, or occupancy.

### bank-conflict-cuda: Measure shared-memory bank-conflict access patterns
Status: `ready-on-gpu-host`
Missing locally: `nvcc, nvidia_smi`
Commands:
- `python3 layout-algebra/run_bank_conflict_cuda.py`
Expected evidence: `layout-algebra/reports/bank-conflict-cuda.json`
Validation: Compile and execute distinct-bank, 32-way-conflicted, and XOR bank-spread probes; validate output with a relative floating-point tolerance and report raw CUDA-event samples. The timing comparison is workload-specific and is not a general occupancy claim.

### cuda-graphs-native: Capture and replay a fixed-shape CUDA Graph
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 cuda-graphs-latency/run_cuda_graphs_cuda.py`
Expected evidence: `cuda-graphs-latency/reports/cuda-graphs-cuda.json`
Validation: Compare graph replay with eager CUDA using exact output checks and synchronized CUDA-event samples; dynamic shapes and changed addresses must use eager execution or recapture.

### persistent-kernels: Profile persistent Triton/CUDA kernels
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi, ncu`
Commands:
- `python3 scripts/run_persistent_kernels.py`
- `python3 scripts/verify_persistent_kernels.py`
- `python3 kernel-benchmarks/kernels/triton/softmax_layernorm.py`
- `python3 kernel-benchmarks/kernels/triton/matmul_mlp.py`
- `ncu --set full -o persistent-kernels python3 <persistent_kernel_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id persistent-kernels --execute`
Expected evidence: `persistent-kernels/persistent-kernels-report.json, persistent-kernels/reports/persistent-kernels-report.md, site/persistent-kernels.html`
Validation: GPU host should capture occupancy, launch amortization, register pressure, shared memory, L2 reuse, and DRAM-byte counters for persistent versus non-persistent baselines.

### parallel-primitives: Profile GPU parallel primitives
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi, ncu`
Commands:
- `python3 scripts/run_parallel_primitives.py`
- `python3 scripts/verify_parallel_primitives.py`
- `python3 kernel-benchmarks/kernels/triton/reduction.py`
- `nvcc -O3 kernel-benchmarks/kernels/cuda/reduction.cu -c -o /tmp/gpumode-reduction.o`
- `ncu --set full -o parallel-primitives python3 <parallel_primitives_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id parallel-primitives --execute`
Expected evidence: `parallel-primitives/parallel-primitives-report.json, parallel-primitives/reports/parallel-primitives-report.md, site/parallel-primitives.html`
Validation: GPU host should capture DRAM bytes, shared-memory bank conflicts, atomics, synchronization depth, occupancy, and stable-order correctness for primitive kernels.

### torch-custom-extension: Build and validate PyTorch custom extension
Status: `ready-on-gpu-host`
Missing locally: `nvcc, ninja, nvidia_smi`
Commands:
- `python3 scripts/run_custom_ops.py`
- `python3 scripts/verify_custom_ops.py`
Expected evidence: `custom-ops/csrc/fused_bias_gelu_residual.cpp, custom-ops/csrc/fused_bias_gelu_residual_kernel.cu, custom-ops/reports/custom-op-report.json`
Validation: Confirm compiled_extension_status changes from source-only to cuda-ready.

### model-integration-gpu: Run tiny transformer integration on GPU-backed operators
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 scripts/build_autotune_db.py`
- `python3 scripts/run_model_integration.py`
- `python3 scripts/verify_model_integration.py`
Expected evidence: `model-integration/reports/tiny-transformer-report.json, regression-ledger/regression-ledger.json`
Validation: Verify model cases pass and regression ledger captures tokens_per_second from GPU-backed runs.

### neural-serving-cuda: Run real autoregressive KV-cache serving on CUDA
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 model-integration/run_neural_serving_cuda.py`
Expected evidence: `model-integration/reports/neural-serving-cuda.json`
Validation: Compare CUDA-generated text with a separately initialized CPU oracle, retain CUDA-event decode samples, and verify the loopback HTTP response. This is untrained single-GPU application evidence, not vLLM capacity or language quality.

### trained-neural-quality-cuda: Train and evaluate the tiny neural serving model on CUDA
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 model-integration/run_trained_neural_quality_cuda.py --device cuda`
Expected evidence: `model-integration/reports/trained-neural-quality-cuda.json`
Validation: Record fixed-protocol training, held-out next-token accuracy, and cached/full autoregressive parity; keep synthetic quality separate from production language quality, serving capacity, and the untrained serving benchmark.

### trained-serving-e2e-cuda: Serve the trained quality-gated model through the runtime-aware decode selector
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 batch1-decode-vertical-slice/run_serving_bridge.py --trained`
- `python3 batch1-decode-vertical-slice/verify_trained_serving.py --report batch1-decode-vertical-slice/reports/serving-bridge.json`
Expected evidence: `gpu-runs/imports/<run-id>/serving-bridge.json`
Validation: Require held-out synthetic quality, cached/runtime output parity, completed HTTP waves, and parity-gated serving candidate selection; keep this separate from production language quality and capacity claims.

### paged-kv-gather-cuda: Execute native CUDA page-table KV gather against a host oracle
Status: `ready-on-gpu-host`
Missing locally: `nvcc, nvidia_smi`
Commands:
- `python3 gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_paged_kv_cuda.py`
Expected evidence: `model-integration/reports/paged-kv-cuda.json`
Validation: Check non-contiguous page-table gather against exact output, retain CUDA-event samples, and keep CPU/reference or unavailable outcomes separate from native GPU acceptance.

### paged-attention-cuda: Execute native CUDA paged attention against a host oracle
Status: `ready-on-gpu-host`
Missing locally: `nvcc, nvidia_smi`
Commands:
- `python3 gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_paged_attention_cuda.py`
Expected evidence: `model-integration/reports/paged-attention-cuda.json`
Validation: Compare paged softmax attention with a host oracle, retain CUDA-event samples, and keep this bounded correctness kernel distinct from production FlashAttention or paged serving capacity.

### serving-tail-load-cuda: Measure CUDA neural-serving microbatch tail load
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 model-integration/run_serving_tail_load_cuda.py`
Expected evidence: `model-integration/reports/serving-tail-load-cuda.json`
Validation: Require synchronized bounded request waves, exact CPU-oracle output parity, observed vectorized batches, and explicit p95 wall-latency samples; this is single-device loopback evidence, not production capacity or multi-GPU serving.

### trained-serving-tail-cuda: Measure trained neural-serving microbatch tail load
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 model-integration/run_serving_tail_load_cuda.py --mode cuda_graph_microbatch --trained`
- `python3 model-integration/verify_trained_tail_load_cuda.py --report model-integration/reports/serving-tail-load-cuda.json`
Expected evidence: `model-integration/reports/serving-tail-load-cuda.json`
Validation: Require the trained quality profile, synchronized request-wave p95 samples, exact output parity, vectorized batching, and zero scheduler rejection/cancellation; keep synthetic quality separate from production capacity.

### vllm-serving-trace: Replay or import vLLM-style serving traces
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `vllm serve <model> --enable-prefix-caching`
- `python3 scripts/run_serving_traces.py`
- `python3 scripts/verify_serving_traces.py`
Expected evidence: `serving-traces/reports/serving-trace-report.json, site/serving-traces.html`
Validation: Replace deterministic timing constants with server trace measurements using the same schema.

### attention-serving-stack: Profile FlashAttention-to-vLLM serving stack
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi, nsys, ncu`
Commands:
- `python3 scripts/run_attention_serving_stack.py`
- `python3 scripts/verify_attention_serving_stack.py`
- `nsys profile -o flashattention-serving python3 <vllm_trace_replay.py>`
- `ncu --set full -o flashattention-kernel python3 <flash_attention_probe.py>`
Expected evidence: `attention-serving-stack/attention-serving-report.json, attention-serving-stack/reports/attention-serving-report.md, site/attention-serving-stack.html`
Validation: GPU-host run should replace local stack estimates with FlashAttention kernel counters and prefill/decode serving traces.

### flash-attention-backward: Profile FlashAttention backward training kernels
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi, ncu, nsys`
Commands:
- `python3 scripts/run_flash_attention_backward.py`
- `python3 scripts/verify_flash_attention_backward.py`
- `python3 scripts/run_attention_serving_stack.py`
- `ncu --set full -o flash-attention-backward python3 <flash_attention_backward_probe.py>`
- `nsys profile -o flash-attention-training-step python3 <flash_attention_training_step.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id flash-attention-backward --execute`
Expected evidence: `flash-attention-backward/flash-attention-backward-report.json, flash-attention-backward/reports/flash-attention-backward-report.md, site/flash-attention-backward.html`
Validation: GPU host should capture dQ/dK/dV gradient correctness, DRAM bytes, occupancy, register pressure, shared memory, exp recompute cost, and training-step timeline evidence.

### sparse-attention-kernels: Profile sparse and ragged attention kernels
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi, ncu, nsys`
Commands:
- `python3 scripts/run_sparse_attention_kernels.py`
- `python3 scripts/verify_sparse_attention_kernels.py`
- `python3 scripts/run_attention_serving_stack.py`
- `python3 scripts/run_flash_attention_backward.py`
- `ncu --set full -o sparse-attention-kernels python3 <sparse_attention_probe.py>`
- `nsys profile -o sparse-attention-ragged-decode python3 <ragged_decode_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id sparse-attention-kernels --execute`
Expected evidence: `sparse-attention-kernels/sparse-attention-report.json, sparse-attention-kernels/reports/sparse-attention-report.md, site/sparse-attention-kernels.html`
Validation: GPU host should capture metadata build cost, sparse QK/PV DRAM bytes, branch efficiency, warp execution efficiency, load balance, occupancy, metadata cache hit rate, and numerical error.

### fused-training-kernels: Profile fused LLM training kernels
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi, ncu, nsys`
Commands:
- `python3 scripts/run_fused_training_kernels.py`
- `python3 scripts/verify_fused_training_kernels.py`
- `python3 scripts/run_model_integration.py`
- `python3 scripts/run_distributed_training_optimizer.py`
- `ncu --set full -o fused-training-kernels python3 <fused_training_probe.py>`
- `nsys profile -o fused-training-step python3 <training_step_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id fused-training-kernels --execute`
Expected evidence: `fused-training-kernels/fused-training-report.json, fused-training-kernels/reports/fused-training-report.md, site/fused-training-kernels.html`
Validation: GPU host should capture launch count, DRAM bytes, occupancy, register pressure, reduction stability, optimizer-state bandwidth, and max error for fused training kernels.

### speculative-decoding-serving: Profile speculative decoding serving scheduler
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi, nsys, ncu`
Commands:
- `python3 scripts/run_speculative_decoding_serving.py`
- `python3 scripts/verify_speculative_decoding_serving.py`
- `python3 scripts/run_serving_traces.py`
- `python3 scripts/run_serving_engine_comparison.py`
- `nsys profile -o speculative-decoding-serving python3 <speculative_serving_probe.py>`
- `ncu --set full -o speculative-target-verify python3 <target_verify_probe.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id speculative-decoding-serving --execute`
Expected evidence: `speculative-decoding-serving/speculative-decoding-report.json, speculative-decoding-serving/reports/speculative-decoding-report.md, site/speculative-decoding-serving.html`
Validation: GPU host or Colab should capture acceptance rate, target verification latency, wasted draft tokens, rollback count, KV commit telemetry, TTFT, TPOT, throughput, and profiler timelines.

### profiler-capture: Capture Nsight and rocprof evidence
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi, nsys, ncu`
Commands:
- `ncu --set full --target-processes all python3 scripts/run_kernel_benchmarks.py`
- `nsys profile python3 scripts/run_model_integration.py`
- `python3 scripts/run_profiler_evidence.py`
- `python3 scripts/verify_profiler_evidence.py`
Expected evidence: `profiler-evidence/reports/profiler-evidence-report.json, site/profiler-evidence.html`
Validation: Profiler rows should classify memory bandwidth, tensor-core compute, launch overhead, and host/device transfer.

### rocm-hip-port: Compile ROCm/HIP portability path
Status: `ready-on-gpu-host`
Missing locally: `hipcc, rocprof`
Commands:
- `hipcc programming-projects/rocm-hip-port/kernel.hip.cpp -o /tmp/rocm-hip-port`
- `rocprof /tmp/rocm-hip-port`
- `python3 scripts/verify_gpu_programming_projects.py`
Expected evidence: `programming-projects/rocm-hip-port/kernel.hip.cpp, programming-projects/rocm-hip-port/measurements.json`
Validation: ROCm host should move the HIP project from source-only to measured runtime evidence.

### distributed-collectives: Run distributed collective tests
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi`
Commands:
- `python3 scripts/run_distributed_collectives.py`
- `python3 scripts/verify_distributed_collectives.py`
- `torchrun --nproc_per_node=2 scripts/run_distributed_collectives_benchmark.py`
- `python3 scripts/verify_distributed_collectives_benchmark.py`
- `nccl-tests/build/all_reduce_perf -b 8M -e 1G -f 2 -g 1`
- `rocprof <rccl_collective_benchmark>`
- `python3 scripts/gpu_workbench.py "nccl nvshmem all reduce bandwidth" --run-lab --dry-run`
Expected evidence: `distributed-collectives/distributed-collectives-report.json, distributed-collectives/reports/distributed-collectives-report.md, distributed-collectives/reports/collective-benchmark-run.json, site/distributed-collectives.html, programming-projects/distributed-collectives/measurements.json, comprehensive-labs/measurements/comp-lab-07-distributed-collectives.json`
Validation: Capture NCCL/RCCL/NVSHMEM bandwidth, collective algorithm, rank-count, and communication-overlap measurements on a multi-GPU host.

### distributed-training-optimizer: Profile distributed training optimizer stacks
Status: `ready-on-gpu-host`
Missing locally: `nvidia_smi, nsys`
Commands:
- `python3 scripts/run_distributed_training_optimizer.py`
- `python3 scripts/verify_distributed_training_optimizer.py`
- `torchrun --nproc_per_node=8 <fsdp_zero_training_step.py>`
- `nsys profile -o fsdp-zero-step torchrun --nproc_per_node=8 <fsdp_zero_training_step.py>`
Expected evidence: `distributed-training-optimizer/distributed-training-optimizer-report.json, distributed-training-optimizer/reports/distributed-training-optimizer-report.md, site/distributed-training-optimizer.html`
Validation: Measure FSDP/ZeRO step time, memory peak, reduce-scatter/all-gather overlap, and pipeline bubble behavior on a multi-GPU training host.

### full-gpu-regression: Refresh full GPU-host regression ledger
Status: `ready-on-this-host`
Commands:
- `python3 run_all.py`
- `python3 scripts/collect_gpu_run.py --run-id <gpu-host-run-id>`
- `python3 scripts/build_gpu_runs.py`
- `python3 scripts/verify_gpu_runs.py`
- `python3 scripts/build_regression_ledger.py`
- `python3 scripts/verify_regression_ledger.py`
Expected evidence: `regression-ledger/regression-ledger.json, gpu-runs/gpu-run-report.json, analysis/end-to-end-audit.json, runtime-matrix/matrix.json`
Validation: Final GPU-host run should have zero regression failures, a collected GPU-run import, and fewer source-ready fallback profiles.
