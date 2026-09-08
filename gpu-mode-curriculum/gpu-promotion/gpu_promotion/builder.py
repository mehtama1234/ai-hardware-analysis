from __future__ import annotations

import importlib.util
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "gpu-promotion"
MANIFEST_JSON = OUT / "gpu-host-promotion-manifest.json"
RUNBOOK_MD = OUT / "reports" / "gpu-host-promotion-runbook.md"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _torch_device() -> str:
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "unavailable"


def capabilities() -> dict[str, Any]:
    return {
        "python": True,
        "torch": importlib.util.find_spec("torch") is not None,
        "torch_device": _torch_device(),
        "triton": importlib.util.find_spec("triton") is not None,
        "jax": importlib.util.find_spec("jax") is not None,
        "nvcc": bool(shutil.which("nvcc")),
        "hipcc": bool(shutil.which("hipcc")),
        "nvidia_smi": bool(shutil.which("nvidia-smi")),
        "nsys": bool(shutil.which("nsys")),
        "ncu": bool(shutil.which("ncu")),
        "rocprof": bool(shutil.which("rocprof")),
        "torchrun": bool(shutil.which("torchrun")),
    }


def _step(
    step_id: str,
    title: str,
    required: list[str],
    commands: list[str],
    expected_evidence: list[str],
    validation: str,
    caps: dict[str, Any],
) -> dict[str, Any]:
    missing = [name for name in required if not caps.get(name)]
    return {
        "id": step_id,
        "title": title,
        "required_capabilities": required,
        "missing_capabilities": missing,
        "status": "ready-on-this-host" if not missing else "ready-on-gpu-host",
        "commands": commands,
        "expected_evidence": expected_evidence,
        "validation": validation,
    }


def promotion_steps(caps: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _step(
            "cuda-kernel-compile",
            "Compile CUDA kernel families",
            ["nvcc", "nvidia_smi"],
            [
                "nvcc -O3 kernel-benchmarks/kernels/cuda/memory.cu -c -o /tmp/gpumode-memory.o",
                "nvcc -O3 kernel-benchmarks/kernels/cuda/reduction.cu -c -o /tmp/gpumode-reduction.o",
                "nvcc -O3 kernel-benchmarks/kernels/cuda/softmax_layernorm.cu -c -o /tmp/gpumode-softmax-layernorm.o",
                "nvcc -O3 kernel-benchmarks/kernels/cuda/matmul_mlp.cu -c -o /tmp/gpumode-matmul-mlp.o",
            ],
            ["kernel-benchmarks/kernels/cuda/*.cu", "kernel-benchmarks/reports/kernel-benchmark-report.json"],
            "Re-run python3 scripts/verify_kernel_benchmarks.py and confirm torch_device=cuda in the report.",
            caps,
        ),
        _step(
            "eager-kernel-suite-cuda",
            "Run the broad eager CUDA kernel suite",
            ["torch", "nvidia_smi"],
            [
                "python3 scripts/run_kernel_benchmarks.py --repeats 7",
            ],
            ["kernel-benchmarks/reports/kernel-benchmark-report.json"],
            "Require all 14 cases to pass with raw synchronized CUDA-event samples and explicit device labels; this suite does not attribute work to Triton or custom native kernels.",
            caps,
        ),
        _step(
            "triton-kernel-sweep",
            "Run Triton kernels on CUDA",
            ["triton", "nvidia_smi"],
            [
                "python3 kernel-benchmarks/kernels/triton/memory.py",
                "python3 kernel-benchmarks/kernels/triton/reduction.py",
                "python3 kernel-benchmarks/kernels/triton/softmax_layernorm.py",
                "python3 kernel-benchmarks/kernels/triton/matmul_mlp.py",
                "python3 scripts/run_kernel_benchmarks.py",
            ],
            ["kernel-benchmarks/reports/kernel-benchmark-report.json", "autotune-db/autotune-db.json"],
            "Refresh autotune records and verify selected configs after GPU timings are present.",
            caps,
        ),
        _step(
            "triton-kernel-families",
            "Run Triton memory, reduction and normalization families on CUDA",
            ["triton", "nvidia_smi"],
            [
                "python3 kernel-benchmarks/run_triton_families_cuda.py",
            ],
            ["kernel-benchmarks/reports/triton-families-cuda.json"],
            "Check contiguous/strided copy, block reduction, softmax and layernorm against CUDA oracles, including non-power-of-two tail columns and synchronized samples.",
            caps,
        ),
        _step(
            "tensor-core-gemm",
            "Build and profile CUTLASS/CuTe tensor-core GEMM",
            ["nvcc", "nvidia_smi", "ncu"],
            [
                "python3 scripts/run_tensor_core_gemm.py",
                "python3 scripts/verify_tensor_core_gemm.py",
                "ncu --set full -o tensor-core-gemm python3 <cutlass_gemm_probe.py>",
                "cuobjdump --dump-sass <cutlass_gemm_binary>",
            ],
            ["tensor-core-gemm/tensor-core-gemm-report.json", "tensor-core-gemm/reports/tensor-core-gemm-report.md", "site/tensor-core-gemm.html"],
            "GPU host should provide CUTLASS/CuTe build evidence, MMA instruction evidence, cuBLAS/Triton comparisons, and profiler counters.",
            caps,
        ),
        _step(
            "low-precision-native",
            "Measure native CUDA FP16 compute and numerical drift",
            ["torch", "nvidia_smi"],
            [
                "python3 quantization-memory-formats/run_low_precision_cuda.py",
            ],
            ["quantization-memory-formats/reports/low-precision-cuda.json"],
            "Compare native FP16 and INT8 activation/weight matmul with an FP32 oracle (including an exact integer accumulator oracle), record memory bytes and synchronized CUDA-event samples, and keep packed INT4 and task-quality evidence separate.",
            caps,
        ),
        _step(
            "trained-digits-quality-cuda",
            "Run the held-out trained-digits quality protocol on CUDA",
            ["torch", "nvidia_smi"],
            [
                "python3 quantization-memory-formats/run_digits_cuda.py",
            ],
            ["quantization-memory-formats/reports/digits-quality-cuda.json"],
            "Preserve the fixed seeds, split, 150-step Adam protocol and quality thresholds; compare FP32 and packed INT4 held-out accuracy and record CUDA-event inference samples.",
            caps,
        ),
        _step(
            "rl-simulation-cuda",
            "Run vectorized reinforcement-learning environment transitions on CUDA",
            ["torch", "nvidia_smi"],
            [
                "python3 rl-gpu-simulation/run_vectorized_simulation.py --device cuda",
            ],
            ["rl-gpu-simulation/reports/vectorized-simulation.json"],
            "Compare the vectorized transition and reward path with the scalar oracle, record synchronized CUDA-event samples, and keep the deterministic grid-world scope separate from physics and policy-quality claims.",
            caps,
        ),
        _step(
            "rl-policy-quality-cuda",
            "Train and evaluate a deterministic goal-policy on CUDA",
            ["torch", "nvidia_smi"],
            [
                "python3 rl-gpu-simulation/run_policy_quality.py --device cuda",
            ],
            ["rl-gpu-simulation/reports/policy-quality.json"],
            "Preserve fixed synthetic seeds and training steps, compare action accuracy and episodic success with the analytic oracle, and keep this supervised grid-world quality result separate from RL optimization and physics claims.",
            caps,
        ),
        _step(
            "triton-layout-cuda",
            "Execute blocked and XOR-swizzled layout mappings in Triton",
            ["torch", "triton", "nvidia_smi"],
            [
                "python3 layout-algebra/run_triton_layout_cuda.py --device cuda",
            ],
            ["layout-algebra/reports/triton-layout-cuda.json"],
            "Compare every emitted device offset against the host layout algebra and record CUDA-event launch samples; this does not establish CuTe lowering, bank-conflict freedom, or occupancy.",
            caps,
        ),
        _step(
            "bank-conflict-cuda",
            "Measure shared-memory bank-conflict access patterns",
            ["nvcc", "nvidia_smi"],
            [
                "python3 layout-algebra/run_bank_conflict_cuda.py",
            ],
            ["layout-algebra/reports/bank-conflict-cuda.json"],
            "Compile and execute distinct-bank, 32-way-conflicted, and XOR bank-spread probes; validate output with a relative floating-point tolerance and report raw CUDA-event samples. The timing comparison is workload-specific and is not a general occupancy claim.",
            caps,
        ),
        _step(
            "cuda-graphs-native",
            "Capture and replay a fixed-shape CUDA Graph",
            ["torch", "nvidia_smi"],
            [
                "python3 cuda-graphs-latency/run_cuda_graphs_cuda.py",
            ],
            ["cuda-graphs-latency/reports/cuda-graphs-cuda.json"],
            "Compare graph replay with eager CUDA using exact output checks and synchronized CUDA-event samples; dynamic shapes and changed addresses must use eager execution or recapture.",
            caps,
        ),
        _step(
            "persistent-kernels",
            "Profile persistent Triton/CUDA kernels",
            ["triton", "nvidia_smi", "ncu"],
            [
                "python3 scripts/run_persistent_kernels.py",
                "python3 scripts/verify_persistent_kernels.py",
                "python3 kernel-benchmarks/kernels/triton/softmax_layernorm.py",
                "python3 kernel-benchmarks/kernels/triton/matmul_mlp.py",
                "ncu --set full -o persistent-kernels python3 <persistent_kernel_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id persistent-kernels --execute",
            ],
            ["persistent-kernels/persistent-kernels-report.json", "persistent-kernels/reports/persistent-kernels-report.md", "site/persistent-kernels.html"],
            "GPU host should capture occupancy, launch amortization, register pressure, shared memory, L2 reuse, and DRAM-byte counters for persistent versus non-persistent baselines.",
            caps,
        ),
        _step(
            "parallel-primitives",
            "Profile GPU parallel primitives",
            ["nvidia_smi", "ncu"],
            [
                "python3 scripts/run_parallel_primitives.py",
                "python3 scripts/verify_parallel_primitives.py",
                "python3 kernel-benchmarks/kernels/triton/reduction.py",
                "nvcc -O3 kernel-benchmarks/kernels/cuda/reduction.cu -c -o /tmp/gpumode-reduction.o",
                "ncu --set full -o parallel-primitives python3 <parallel_primitives_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id parallel-primitives --execute",
            ],
            ["parallel-primitives/parallel-primitives-report.json", "parallel-primitives/reports/parallel-primitives-report.md", "site/parallel-primitives.html"],
            "GPU host should capture DRAM bytes, shared-memory bank conflicts, atomics, synchronization depth, occupancy, and stable-order correctness for primitive kernels.",
            caps,
        ),
        _step(
            "torch-custom-extension",
            "Build and validate PyTorch custom extension",
            ["torch", "nvcc", "ninja", "nvidia_smi"],
            [
                "python3 scripts/run_custom_ops.py",
                "python3 scripts/verify_custom_ops.py",
            ],
            ["custom-ops/csrc/fused_bias_gelu_residual.cpp", "custom-ops/csrc/fused_bias_gelu_residual_kernel.cu", "custom-ops/reports/custom-op-report.json"],
            "Confirm compiled_extension_status changes from source-only to cuda-ready.",
            caps,
        ),
        _step(
            "model-integration-gpu",
            "Run tiny transformer integration on GPU-backed operators",
            ["torch", "nvidia_smi"],
            [
                "python3 scripts/build_autotune_db.py",
                "python3 scripts/run_model_integration.py",
                "python3 scripts/verify_model_integration.py",
            ],
            ["model-integration/reports/tiny-transformer-report.json", "regression-ledger/regression-ledger.json"],
            "Verify model cases pass and regression ledger captures tokens_per_second from GPU-backed runs.",
            caps,
        ),
        _step(
            "neural-serving-cuda",
            "Run real autoregressive KV-cache serving on CUDA",
            ["torch", "nvidia_smi"],
            [
                "python3 model-integration/run_neural_serving_cuda.py",
            ],
            ["model-integration/reports/neural-serving-cuda.json"],
            "Compare CUDA-generated text with a separately initialized CPU oracle, retain CUDA-event decode samples, and verify the loopback HTTP response. This is untrained single-GPU application evidence, not vLLM capacity or language quality.",
            caps,
        ),
        _step(
            "trained-neural-quality-cuda",
            "Train and evaluate the tiny neural serving model on CUDA",
            ["torch", "nvidia_smi"],
            [
                "python3 model-integration/run_trained_neural_quality_cuda.py --device cuda",
            ],
            ["model-integration/reports/trained-neural-quality-cuda.json"],
            "Record fixed-protocol training, held-out next-token accuracy, and cached/full autoregressive parity; keep synthetic quality separate from production language quality, serving capacity, and the untrained serving benchmark.",
            caps,
        ),
        _step(
            "paged-kv-gather-cuda",
            "Execute native CUDA page-table KV gather against a host oracle",
            ["nvcc", "nvidia_smi"],
            [
                "python3 gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_paged_kv_cuda.py",
            ],
            ["model-integration/reports/paged-kv-cuda.json"],
            "Check non-contiguous page-table gather against exact output, retain CUDA-event samples, and keep CPU/reference or unavailable outcomes separate from native GPU acceptance.",
            caps,
        ),
        _step(
            "paged-attention-cuda",
            "Execute native CUDA paged attention against a host oracle",
            ["nvcc", "nvidia_smi"],
            [
                "python3 gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_paged_attention_cuda.py",
            ],
            ["model-integration/reports/paged-attention-cuda.json"],
            "Compare paged softmax attention with a host oracle, retain CUDA-event samples, and keep this bounded correctness kernel distinct from production FlashAttention or paged serving capacity.",
            caps,
        ),
        _step(
            "serving-tail-load-cuda",
            "Measure CUDA neural-serving microbatch tail load",
            ["torch", "nvidia_smi"],
            [
                "python3 model-integration/run_serving_tail_load_cuda.py",
            ],
            ["model-integration/reports/serving-tail-load-cuda.json"],
            "Require synchronized bounded request waves, exact CPU-oracle output parity, observed vectorized batches, and explicit p95 wall-latency samples; this is single-device loopback evidence, not production capacity or multi-GPU serving.",
            caps,
        ),
        _step(
            "vllm-serving-trace",
            "Replay or import vLLM-style serving traces",
            ["nvidia_smi"],
            [
                "vllm serve <model> --enable-prefix-caching",
                "python3 scripts/run_serving_traces.py",
                "python3 scripts/verify_serving_traces.py",
            ],
            ["serving-traces/reports/serving-trace-report.json", "site/serving-traces.html"],
            "Replace deterministic timing constants with server trace measurements using the same schema.",
            caps,
        ),
        _step(
            "attention-serving-stack",
            "Profile FlashAttention-to-vLLM serving stack",
            ["nvidia_smi", "nsys", "ncu"],
            [
                "python3 scripts/run_attention_serving_stack.py",
                "python3 scripts/verify_attention_serving_stack.py",
                "nsys profile -o flashattention-serving python3 <vllm_trace_replay.py>",
                "ncu --set full -o flashattention-kernel python3 <flash_attention_probe.py>",
            ],
            ["attention-serving-stack/attention-serving-report.json", "attention-serving-stack/reports/attention-serving-report.md", "site/attention-serving-stack.html"],
            "GPU-host run should replace local stack estimates with FlashAttention kernel counters and prefill/decode serving traces.",
            caps,
        ),
        _step(
            "flash-attention-backward",
            "Profile FlashAttention backward training kernels",
            ["nvidia_smi", "ncu", "nsys"],
            [
                "python3 scripts/run_flash_attention_backward.py",
                "python3 scripts/verify_flash_attention_backward.py",
                "python3 scripts/run_attention_serving_stack.py",
                "ncu --set full -o flash-attention-backward python3 <flash_attention_backward_probe.py>",
                "nsys profile -o flash-attention-training-step python3 <flash_attention_training_step.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id flash-attention-backward --execute",
            ],
            [
                "flash-attention-backward/flash-attention-backward-report.json",
                "flash-attention-backward/reports/flash-attention-backward-report.md",
                "site/flash-attention-backward.html",
            ],
            "GPU host should capture dQ/dK/dV gradient correctness, DRAM bytes, occupancy, register pressure, shared memory, exp recompute cost, and training-step timeline evidence.",
            caps,
        ),
        _step(
            "sparse-attention-kernels",
            "Profile sparse and ragged attention kernels",
            ["nvidia_smi", "ncu", "nsys"],
            [
                "python3 scripts/run_sparse_attention_kernels.py",
                "python3 scripts/verify_sparse_attention_kernels.py",
                "python3 scripts/run_attention_serving_stack.py",
                "python3 scripts/run_flash_attention_backward.py",
                "ncu --set full -o sparse-attention-kernels python3 <sparse_attention_probe.py>",
                "nsys profile -o sparse-attention-ragged-decode python3 <ragged_decode_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id sparse-attention-kernels --execute",
            ],
            [
                "sparse-attention-kernels/sparse-attention-report.json",
                "sparse-attention-kernels/reports/sparse-attention-report.md",
                "site/sparse-attention-kernels.html",
            ],
            "GPU host should capture metadata build cost, sparse QK/PV DRAM bytes, branch efficiency, warp execution efficiency, load balance, occupancy, metadata cache hit rate, and numerical error.",
            caps,
        ),
        _step(
            "fused-training-kernels",
            "Profile fused LLM training kernels",
            ["nvidia_smi", "ncu", "nsys"],
            [
                "python3 scripts/run_fused_training_kernels.py",
                "python3 scripts/verify_fused_training_kernels.py",
                "python3 scripts/run_model_integration.py",
                "python3 scripts/run_distributed_training_optimizer.py",
                "ncu --set full -o fused-training-kernels python3 <fused_training_probe.py>",
                "nsys profile -o fused-training-step python3 <training_step_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id fused-training-kernels --execute",
            ],
            [
                "fused-training-kernels/fused-training-report.json",
                "fused-training-kernels/reports/fused-training-report.md",
                "site/fused-training-kernels.html",
            ],
            "GPU host should capture launch count, DRAM bytes, occupancy, register pressure, reduction stability, optimizer-state bandwidth, and max error for fused training kernels.",
            caps,
        ),
        _step(
            "speculative-decoding-serving",
            "Profile speculative decoding serving scheduler",
            ["nvidia_smi", "nsys", "ncu"],
            [
                "python3 scripts/run_speculative_decoding_serving.py",
                "python3 scripts/verify_speculative_decoding_serving.py",
                "python3 scripts/run_serving_traces.py",
                "python3 scripts/run_serving_engine_comparison.py",
                "nsys profile -o speculative-decoding-serving python3 <speculative_serving_probe.py>",
                "ncu --set full -o speculative-target-verify python3 <target_verify_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id speculative-decoding-serving --execute",
            ],
            [
                "speculative-decoding-serving/speculative-decoding-report.json",
                "speculative-decoding-serving/reports/speculative-decoding-report.md",
                "site/speculative-decoding-serving.html",
            ],
            "GPU host or Colab should capture acceptance rate, target verification latency, wasted draft tokens, rollback count, KV commit telemetry, TTFT, TPOT, throughput, and profiler timelines.",
            caps,
        ),
        _step(
            "profiler-capture",
            "Capture Nsight and rocprof evidence",
            ["nvidia_smi", "nsys", "ncu"],
            [
                "ncu --set full --target-processes all python3 scripts/run_kernel_benchmarks.py",
                "nsys profile python3 scripts/run_model_integration.py",
                "python3 scripts/run_profiler_evidence.py",
                "python3 scripts/verify_profiler_evidence.py",
            ],
            ["profiler-evidence/reports/profiler-evidence-report.json", "site/profiler-evidence.html"],
            "Profiler rows should classify memory bandwidth, tensor-core compute, launch overhead, and host/device transfer.",
            caps,
        ),
        _step(
            "rocm-hip-port",
            "Compile ROCm/HIP portability path",
            ["hipcc", "rocprof"],
            [
                "hipcc programming-projects/rocm-hip-port/kernel.hip.cpp -o /tmp/rocm-hip-port",
                "rocprof /tmp/rocm-hip-port",
                "python3 scripts/verify_gpu_programming_projects.py",
            ],
            ["programming-projects/rocm-hip-port/kernel.hip.cpp", "programming-projects/rocm-hip-port/measurements.json"],
            "ROCm host should move the HIP project from source-only to measured runtime evidence.",
            caps,
        ),
        _step(
            "distributed-collectives",
            "Run distributed collective tests",
            ["torchrun", "nvidia_smi"],
            [
                "python3 scripts/run_distributed_collectives.py",
                "python3 scripts/verify_distributed_collectives.py",
                "torchrun --nproc_per_node=2 scripts/run_distributed_collectives_benchmark.py",
                "python3 scripts/verify_distributed_collectives_benchmark.py",
                "nccl-tests/build/all_reduce_perf -b 8M -e 1G -f 2 -g 1",
                "rocprof <rccl_collective_benchmark>",
                "python3 scripts/gpu_workbench.py \"nccl nvshmem all reduce bandwidth\" --run-lab --dry-run",
            ],
            [
                "distributed-collectives/distributed-collectives-report.json",
                "distributed-collectives/reports/distributed-collectives-report.md",
                "distributed-collectives/reports/collective-benchmark-run.json",
                "site/distributed-collectives.html",
                "programming-projects/distributed-collectives/measurements.json",
                "comprehensive-labs/measurements/comp-lab-07-distributed-collectives.json",
            ],
            "Capture NCCL/RCCL/NVSHMEM bandwidth, collective algorithm, rank-count, and communication-overlap measurements on a multi-GPU host.",
            caps,
        ),
        _step(
            "distributed-training-optimizer",
            "Profile distributed training optimizer stacks",
            ["torchrun", "nvidia_smi", "nsys"],
            [
                "python3 scripts/run_distributed_training_optimizer.py",
                "python3 scripts/verify_distributed_training_optimizer.py",
                "torchrun --nproc_per_node=8 <fsdp_zero_training_step.py>",
                "nsys profile -o fsdp-zero-step torchrun --nproc_per_node=8 <fsdp_zero_training_step.py>",
            ],
            [
                "distributed-training-optimizer/distributed-training-optimizer-report.json",
                "distributed-training-optimizer/reports/distributed-training-optimizer-report.md",
                "site/distributed-training-optimizer.html",
            ],
            "Measure FSDP/ZeRO step time, memory peak, reduce-scatter/all-gather overlap, and pipeline bubble behavior on a multi-GPU training host.",
            caps,
        ),
        _step(
            "full-gpu-regression",
            "Refresh full GPU-host regression ledger",
            ["python", "torch"],
            [
                "python3 run_all.py",
                "python3 scripts/collect_gpu_run.py --run-id <gpu-host-run-id>",
                "python3 scripts/build_gpu_runs.py",
                "python3 scripts/verify_gpu_runs.py",
                "python3 scripts/build_regression_ledger.py",
                "python3 scripts/verify_regression_ledger.py",
            ],
            ["regression-ledger/regression-ledger.json", "gpu-runs/gpu-run-report.json", "analysis/end-to-end-audit.json", "runtime-matrix/matrix.json"],
            "Final GPU-host run should have zero regression failures, a collected GPU-run import, and fewer source-ready fallback profiles.",
            caps,
        ),
    ]


def render_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# GPU Host Promotion Runbook",
        "",
        f"Generated: `{manifest['generated_at']}`",
        f"Steps: `{manifest['step_count']}`",
        f"Ready on this host: `{manifest['ready_on_this_host']}`",
        f"Ready on GPU host: `{manifest['ready_on_gpu_host']}`",
        "",
        "## Local Capability Snapshot",
        "",
    ]
    for key, value in manifest["local_capabilities"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Steps", ""])
    for step in manifest["steps"]:
        lines.append(f"### {step['id']}: {step['title']}")
        lines.append(f"Status: `{step['status']}`")
        if step["missing_capabilities"]:
            lines.append(f"Missing locally: `{', '.join(step['missing_capabilities'])}`")
        lines.append("Commands:")
        for command in step["commands"]:
            lines.append(f"- `{command}`")
        lines.append(f"Expected evidence: `{', '.join(step['expected_evidence'])}`")
        lines.append(f"Validation: {step['validation']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_manifest() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    RUNBOOK_MD.parent.mkdir(parents=True, exist_ok=True)
    caps = capabilities()
    steps = promotion_steps(caps)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "step_count": len(steps),
        "ready_on_this_host": sum(1 for step in steps if step["status"] == "ready-on-this-host"),
        "ready_on_gpu_host": sum(1 for step in steps if step["status"] == "ready-on-gpu-host"),
        "local_capabilities": caps,
        "input_reports": {
            "runtime_matrix": "runtime-matrix/matrix.json",
            "kernel_benchmarks": "kernel-benchmarks/reports/kernel-benchmark-report.json",
            "custom_ops": "custom-ops/reports/custom-op-report.json",
            "autotune_db": "autotune-db/autotune-db.json",
            "model_integration": "model-integration/reports/tiny-transformer-report.json",
            "serving_traces": "serving-traces/reports/serving-trace-report.json",
            "persistent_kernels": "persistent-kernels/persistent-kernels-report.json",
            "parallel_primitives": "parallel-primitives/parallel-primitives-report.json",
            "flash_attention_backward": "flash-attention-backward/flash-attention-backward-report.json",
            "sparse_attention": "sparse-attention-kernels/sparse-attention-report.json",
            "fused_training": "fused-training-kernels/fused-training-report.json",
            "speculative_decoding": "speculative-decoding-serving/speculative-decoding-report.json",
            "regression_ledger": "regression-ledger/regression-ledger.json",
        },
        "steps": steps,
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    RUNBOOK_MD.write_text(render_markdown(manifest), encoding="utf-8")
    return manifest
