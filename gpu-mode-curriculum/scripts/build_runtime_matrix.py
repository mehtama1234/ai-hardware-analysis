#!/usr/bin/env python3
"""Build runtime matrix for CPU, CUDA, ROCm, Triton, compiler/runtime inspection, custom-op, autotune, model, serving, KV-cache/PagedAttention, serving-engine comparison, distributed topology, distributed collectives, distributed training optimizer, MoE routing/all-to-all, hardware capacity, quantization, numerical reproducibility, CUDA Graphs, multi-tenant GPU scheduling, GPU promotion suite, GPU-run import/provenance/measurement queue, GPU handoff, assessment grading, assessment, regression, promotion, capstone, profiler, and distributed gates."""

from __future__ import annotations

import importlib.util
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runtime-matrix"
MATRIX_JSON = OUT / "matrix.json"
MATRIX_MD = OUT / "MATRIX.md"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def local_capabilities() -> dict[str, Any]:
    torch_device = "unavailable"
    try:
        import torch

        torch_device = "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        pass
    return {
        "python": True,
        "torch": module_available("torch"),
        "torch_device": torch_device,
        "triton": module_available("triton"),
        "jax": module_available("jax"),
        "nvcc": bool(shutil.which("nvcc")),
        "hipcc": bool(shutil.which("hipcc")),
        "nvidia_smi": bool(shutil.which("nvidia-smi")),
        "nsys": bool(shutil.which("nsys")),
        "ncu": bool(shutil.which("ncu")),
        "rocprof": bool(shutil.which("rocprof")),
        "mpirun": bool(shutil.which("mpirun")),
        "torchrun": bool(shutil.which("torchrun")),
        "kubectl": bool(shutil.which("kubectl")),
    }


def profile_status(required: list[str], capabilities: dict[str, Any], fallback_ok: bool = False) -> str:
    missing = [name for name in required if not capabilities.get(name)]
    if not missing:
        return "ready"
    return "source-ready-local-fallback" if fallback_ok else "blocked-by-runtime"


def build_profiles(capabilities: dict[str, Any], reports: dict[str, Any]) -> list[dict[str, Any]]:
    kernel_report = reports["kernel_report"]
    compiler_runtime = reports["compiler_runtime"]
    project_report = reports["project_report"]
    lesson_lab_run = reports["lesson_lab_run"]
    comprehensive_run = reports["comprehensive_run"]
    serving_report = reports["serving_report"]
    tensor_core_gemm = reports["tensor_core_gemm"]
    persistent_kernels = reports["persistent_kernels"]
    parallel_primitives = reports["parallel_primitives"]
    kv_cache = reports["kv_cache"]
    attention_serving = reports["attention_serving"]
    flash_attention_backward = reports["flash_attention_backward"]
    sparse_attention = reports["sparse_attention"]
    fused_training = reports["fused_training"]
    serving_engine_comparison = reports["serving_engine_comparison"]
    speculative_decoding = reports["speculative_decoding"]
    distributed_topology = reports["distributed_topology"]
    distributed_collectives = reports["distributed_collectives"]
    distributed_training_optimizer = reports["distributed_training_optimizer"]
    moe_routing = reports["moe_routing"]
    hardware_capacity = reports["hardware_capacity"]
    quantization_report = reports["quantization_report"]
    numerical_reproducibility = reports["numerical_reproducibility"]
    cuda_graphs_latency = reports["cuda_graphs_latency"]
    multi_tenant_scheduling = reports["multi_tenant_scheduling"]
    custom_op_report = reports["custom_op_report"]
    autotune_db = reports["autotune_db"]
    model_report = reports["model_report"]
    regression_ledger = reports["regression_ledger"]
    gpu_promotion = reports["gpu_promotion"]
    gpu_promotion_suite = reports["gpu_promotion_suite"]
    gpu_import_lint = reports["gpu_import_lint"]
    gpu_runs = reports["gpu_runs"]
    gpu_provenance = reports["gpu_provenance"]
    gpu_measurement_queue = reports["gpu_measurement_queue"]
    gpu_acceptance_logic = reports["gpu_acceptance_logic"]
    gpu_host_preflight = reports["gpu_host_preflight"]
    gpu_handoff = reports["gpu_handoff"]
    assessment = reports["assessment"]
    assessment_grading = reports["assessment_grading"]
    capstone_acceptance = reports["capstone_acceptance"]
    return [
        {
            "id": "cpu-local",
            "purpose": "Run curriculum, lesson labs, comprehensive labs, and PyTorch CPU benchmark sweeps.",
            "required_capabilities": ["python", "torch"],
            "status": profile_status(["python", "torch"], capabilities),
            "commands": [
                "python3 scripts/run_lesson_labs.py",
                "python3 scripts/run_comprehensive_labs.py",
                "python3 scripts/run_kernel_benchmarks.py",
            ],
            "evidence": [
                "lesson-labs/run-report.json",
                "comprehensive-labs/run-report.json",
                "kernel-benchmarks/reports/kernel-benchmark-report.json",
            ],
            "local_facts": {
                "lesson_lab_contracts": lesson_lab_run.get("passed_contracts", 0),
                "comprehensive_labs": comprehensive_run.get("passed", 0),
                "kernel_benchmarks": kernel_report.get("passed", 0),
                "custom_op_cases": custom_op_report.get("passed", 0),
                "autotune_records": autotune_db.get("record_count", 0),
                "model_integration_cases": model_report.get("passed", 0),
                "serving_traces": serving_report.get("passed_traces", 0),
                "regression_metrics": regression_ledger.get("metric_count", 0),
                "gpu_promotion_steps": gpu_promotion.get("step_count", 0),
                "gpu_promotion_suite_commands": gpu_promotion_suite.get("command_count", 0),
                "gpu_run_imports": gpu_runs.get("coverage", {}).get("run_count", 0),
                "gpu_handoff_status": gpu_handoff.get("status", "missing"),
                "assessment_questions": assessment.get("concept_question_count", 0),
                "assessment_grading_score": assessment_grading.get("score", 0),
                "capstone_score": capstone_acceptance.get("score", 0),
            },
        },
        {
            "id": "gpu-promotion-suite-dev",
            "purpose": "Plan or execute the ordered GPU-host promotion commands from the manifest and preserve command-level evidence expectations.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvcc", "hipcc", "nvidia_smi", "nsys", "ncu", "rocprof"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_gpu_promotion_suite.py --run-id local-suite-dry-run",
                "python3 scripts/verify_gpu_promotion_suite.py",
            ],
            "evidence": [
                "gpu-promotion/suite-run-report.json",
                "gpu-promotion/reports/suite-run-report.md",
                "site/gpu-promotion-suite.html",
            ],
            "local_facts": {
                "commands": gpu_promotion_suite.get("command_count", 0),
                "steps": gpu_promotion_suite.get("step_count", 0),
                "planned": gpu_promotion_suite.get("planned", 0),
                "skipped": gpu_promotion_suite.get("skipped", 0),
                "status": gpu_promotion_suite.get("status", "missing"),
            },
        },
        {
            "id": "compiler-runtime-inspection-dev",
            "purpose": "Inspect CUDA, Triton, ROCm/HIP, and custom-op sources for compiler/runtime features, risks, and GPU-host promotion commands.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvcc", "nvidia_smi", "triton", "hipcc", "rocprof", "nsys", "ncu"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_compiler_runtime_inspection.py",
                "python3 scripts/verify_compiler_runtime_inspection.py",
            ],
            "evidence": [
                "compiler-runtime-inspection/compiler-runtime-report.json",
                "compiler-runtime-inspection/reports/compiler-runtime-report.md",
                "site/compiler-runtime-inspection.html",
            ],
            "local_facts": {
                "status": compiler_runtime.get("status", "missing"),
                "sources": compiler_runtime.get("source_count", 0),
                "groups": compiler_runtime.get("groups", []),
                "risk_counts": compiler_runtime.get("risk_counts", {}),
            },
        },
        {
            "id": "tensor-core-gemm-dev",
            "purpose": "Plan CUTLASS/CuTe tensor-core GEMM CTA, warp, MMA, pipeline, epilogue, quantized operand, and profiler promotion choices.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvcc", "nvidia_smi", "ncu", "triton"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_tensor_core_gemm.py",
                "python3 scripts/verify_tensor_core_gemm.py",
            ],
            "evidence": [
                "tensor-core-gemm/tensor-core-gemm-report.json",
                "tensor-core-gemm/reports/tensor-core-gemm-report.md",
                "site/tensor-core-gemm.html",
            ],
            "local_facts": {
                "status": tensor_core_gemm.get("status", "missing"),
                "scenarios": tensor_core_gemm.get("scenario_count", 0),
                "passed": tensor_core_gemm.get("passed_scenarios", 0),
                "tensor_core_eligible": tensor_core_gemm.get("tensor_core_eligible_scenarios", 0),
                "fused_epilogues": tensor_core_gemm.get("fused_epilogue_scenarios", 0),
            },
        },
        {
            "id": "persistent-kernels-dev",
            "purpose": "Design and promote persistent Triton/CUDA kernels with occupancy, launch amortization, L2 reuse, register pressure, shared memory, and producer/consumer evidence.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["triton", "nvidia_smi", "ncu", "nsys"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_persistent_kernels.py",
                "python3 scripts/verify_persistent_kernels.py",
            ],
            "evidence": [
                "persistent-kernels/persistent-kernels-report.json",
                "persistent-kernels/reports/persistent-kernels-report.md",
                "site/persistent-kernels.html",
            ],
            "local_facts": {
                "status": persistent_kernels.get("status", "missing"),
                "scenarios": persistent_kernels.get("scenario_count", 0),
                "passed": persistent_kernels.get("passed_scenarios", 0),
                "families": persistent_kernels.get("family_count", 0),
                "producer_consumer": persistent_kernels.get("producer_consumer_scenarios", 0),
            },
        },
        {
            "id": "parallel-primitives-dev",
            "purpose": "Model and promote reduction, scan, compaction, radix sort, histogram, and segmented reduction kernels with memory-traffic and synchronization evidence.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["triton", "nvcc", "nvidia_smi", "ncu", "rocprof"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_parallel_primitives.py",
                "python3 scripts/verify_parallel_primitives.py",
            ],
            "evidence": [
                "parallel-primitives/parallel-primitives-report.json",
                "parallel-primitives/reports/parallel-primitives-report.md",
                "site/parallel-primitives.html",
            ],
            "local_facts": {
                "status": parallel_primitives.get("status", "missing"),
                "scenarios": parallel_primitives.get("scenario_count", 0),
                "passed": parallel_primitives.get("passed_scenarios", 0),
                "primitives": parallel_primitives.get("primitive_count", 0),
                "stable_order": parallel_primitives.get("stable_order_scenarios", 0),
            },
        },
        {
            "id": "gpu-runs-dev",
            "purpose": "Import GPU-host validation rows from NVIDIA and AMD-shaped runs and link them to the promotion manifest.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvidia_smi", "nvcc", "hipcc", "nsys", "ncu", "rocprof"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/build_gpu_runs.py",
                "python3 scripts/verify_gpu_runs.py",
            ],
            "evidence": [
                "gpu-runs/fixtures/*.json",
                "gpu-runs/gpu-run-report.json",
                "gpu-runs/reports/gpu-run-report.md",
                "site/gpu-runs.html",
            ],
            "local_facts": {
                "runs": gpu_runs.get("coverage", {}).get("run_count", 0),
                "vendors": gpu_runs.get("coverage", {}).get("vendors", []),
                "promotion_steps": gpu_runs.get("coverage", {}).get("promotion_step_count", 0),
                "measured_runs": gpu_runs.get("coverage", {}).get("measured_run_count", 0),
                "status": gpu_runs.get("status", "missing"),
            },
        },
        {
            "id": "serving-engine-comparison-dev",
            "purpose": "Compare vLLM, Hugging Face TGI, SGLang, TensorRT-LLM, and HF Transformers baseline across production inference scenarios.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["torch", "triton", "nvidia_smi", "hipcc"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_serving_engine_comparison.py",
                "python3 scripts/verify_serving_engine_comparison.py",
            ],
            "evidence": [
                "serving-engine-comparison/serving-engine-comparison.json",
                "serving-engine-comparison/reports/serving-engine-comparison.md",
                "site/serving-engine-comparison.html",
            ],
            "local_facts": {
                "status": serving_engine_comparison.get("status", "missing"),
                "engines": serving_engine_comparison.get("engine_count", 0),
                "scenarios": serving_engine_comparison.get("scenario_count", 0),
                "engine_wins": serving_engine_comparison.get("engine_wins", {}),
            },
        },
        {
            "id": "speculative-decoding-serving-dev",
            "purpose": "Model and promote speculative decoding serving with draft/target verification, acceptance rate, rollback pressure, KV commits, TTFT, TPOT, throughput, and scheduler policy.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["torch", "transformers", "vllm", "nvidia_smi", "nsys", "ncu"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_speculative_decoding_serving.py",
                "python3 scripts/verify_speculative_decoding_serving.py",
            ],
            "evidence": [
                "speculative-decoding-serving/speculative-decoding-report.json",
                "speculative-decoding-serving/reports/speculative-decoding-report.md",
                "site/speculative-decoding-serving.html",
            ],
            "local_facts": {
                "status": speculative_decoding.get("status", "missing"),
                "scenarios": speculative_decoding.get("scenario_count", 0),
                "passed": speculative_decoding.get("passed_scenarios", 0),
                "review": speculative_decoding.get("review_scenarios", 0),
                "engines": speculative_decoding.get("engine_count", 0),
                "scheduler_policies": speculative_decoding.get("scheduler_policy_count", 0),
                "min_acceptance": speculative_decoding.get("min_acceptance_rate", 0),
            },
        },
        {
            "id": "kv-cache-paged-attention-dev",
            "purpose": "Compare contiguous KV reservation against PagedAttention-style block tables for fragmentation, prefix reuse, eviction, admission, and GPU-serving promotion.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvidia_smi", "nsys", "ncu"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_kv_cache_paged_attention.py",
                "python3 scripts/verify_kv_cache_paged_attention.py",
            ],
            "evidence": [
                "kv-cache-paged-attention/kv-cache-report.json",
                "kv-cache-paged-attention/reports/kv-cache-report.md",
                "site/kv-cache-paged-attention.html",
            ],
            "local_facts": {
                "status": kv_cache.get("status", "missing"),
                "scenarios": kv_cache.get("scenario_count", 0),
                "passed": kv_cache.get("passed_scenarios", 0),
                "prefix_blocks_reused": kv_cache.get("total_prefix_blocks_reused", 0),
            },
        },
        {
            "id": "attention-serving-stack-dev",
            "purpose": "Connect FlashAttention online-softmax tiling to vLLM-style prefill/decode scheduling, KV reuse, CUDA Graph bucket fit, numerical tolerance, and GPU profiling promotion.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvidia_smi", "triton", "nsys", "ncu", "vllm"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_attention_serving_stack.py",
                "python3 scripts/verify_attention_serving_stack.py",
            ],
            "evidence": [
                "attention-serving-stack/attention-serving-report.json",
                "attention-serving-stack/reports/attention-serving-report.md",
                "site/attention-serving-stack.html",
            ],
            "local_facts": {
                "status": attention_serving.get("status", "missing"),
                "scenarios": attention_serving.get("scenario_count", 0),
                "passed": attention_serving.get("passed_scenarios", 0),
                "prefix_blocks_reused": attention_serving.get("total_prefix_blocks_reused", 0),
            },
        },
        {
            "id": "flash-attention-backward-dev",
            "purpose": "Model and promote FlashAttention backward dQ, dK, dV, dSoftmax, recompute, dropout, GQA, activation-memory, and gradient-error evidence.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvidia_smi", "triton", "nsys", "ncu"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_flash_attention_backward.py",
                "python3 scripts/verify_flash_attention_backward.py",
            ],
            "evidence": [
                "flash-attention-backward/flash-attention-backward-report.json",
                "flash-attention-backward/reports/flash-attention-backward-report.md",
                "site/flash-attention-backward.html",
            ],
            "local_facts": {
                "status": flash_attention_backward.get("status", "missing"),
                "scenarios": flash_attention_backward.get("scenario_count", 0),
                "passed": flash_attention_backward.get("passed_scenarios", 0),
                "dropout": flash_attention_backward.get("dropout_scenarios", 0),
                "grouped_query": flash_attention_backward.get("grouped_query_scenarios", 0),
            },
        },
        {
            "id": "sparse-attention-kernels-dev",
            "purpose": "Model and promote block-sparse, sliding-window, ragged decode, neighborhood, top-k, metadata, load-balance, and sparse backward attention kernels.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvidia_smi", "triton", "nsys", "ncu"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_sparse_attention_kernels.py",
                "python3 scripts/verify_sparse_attention_kernels.py",
            ],
            "evidence": [
                "sparse-attention-kernels/sparse-attention-report.json",
                "sparse-attention-kernels/reports/sparse-attention-report.md",
                "site/sparse-attention-kernels.html",
            ],
            "local_facts": {
                "status": sparse_attention.get("status", "missing"),
                "scenarios": sparse_attention.get("scenario_count", 0),
                "passed": sparse_attention.get("passed_scenarios", 0),
                "patterns": sparse_attention.get("pattern_count", 0),
                "ragged": sparse_attention.get("ragged_scenarios", 0),
                "backward": sparse_attention.get("backward_scenarios", 0),
            },
        },
        {
            "id": "fused-training-kernels-dev",
            "purpose": "Model and promote fused LLM training kernels for RMSNorm, SwiGLU, cross-entropy, AdamW, grad clipping, dropout/residual/norm, backward checks, launch count, and HBM traffic.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvidia_smi", "triton", "nsys", "ncu"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_fused_training_kernels.py",
                "python3 scripts/verify_fused_training_kernels.py",
            ],
            "evidence": [
                "fused-training-kernels/fused-training-report.json",
                "fused-training-kernels/reports/fused-training-report.md",
                "site/fused-training-kernels.html",
            ],
            "local_facts": {
                "status": fused_training.get("status", "missing"),
                "scenarios": fused_training.get("scenario_count", 0),
                "passed": fused_training.get("passed_scenarios", 0),
                "families": fused_training.get("family_count", 0),
                "backward": fused_training.get("backward_scenarios", 0),
                "optimizer_state": fused_training.get("optimizer_state_scenarios", 0),
            },
        },
        {
            "id": "distributed-topology-dev",
            "purpose": "Plan tensor, pipeline, and data parallel deployment choices across single-GPU, PCIe, NVLink, and InfiniBand topologies.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["torchrun", "nvidia_smi", "mpirun"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_distributed_topology.py",
                "python3 scripts/verify_distributed_topology.py",
            ],
            "evidence": [
                "distributed-topology/distributed-topology-plan.json",
                "distributed-topology/reports/distributed-topology-plan.md",
                "site/distributed-topology.html",
            ],
            "local_facts": {
                "status": distributed_topology.get("status", "missing"),
                "topologies": distributed_topology.get("topology_count", 0),
                "workloads": distributed_topology.get("workload_count", 0),
                "candidates": distributed_topology.get("candidate_count", 0),
                "rejected": distributed_topology.get("rejected_count", 0),
            },
        },
        {
            "id": "distributed-collectives-dev",
            "purpose": "Plan NCCL/RCCL/NVSHMEM collective algorithms with rank count, payload, topology bandwidth, latency, communication overlap, and GPU-host promotion evidence.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["torchrun", "nvidia_smi", "nccl", "rccl", "nvshmem", "nsys", "rocprof"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_distributed_collectives.py",
                "python3 scripts/verify_distributed_collectives.py",
                "torchrun --nproc_per_node=2 scripts/run_distributed_collectives_benchmark.py",
                "python3 scripts/verify_distributed_collectives_benchmark.py",
            ],
            "evidence": [
                "distributed-collectives/distributed-collectives-report.json",
                "distributed-collectives/reports/distributed-collectives-report.md",
                "distributed-collectives/reports/collective-benchmark-run.json",
                "site/distributed-collectives.html",
            ],
            "local_facts": {
                "status": distributed_collectives.get("status", "missing"),
                "scenarios": distributed_collectives.get("scenario_count", 0),
                "collectives": distributed_collectives.get("collective_count", 0),
                "backends": distributed_collectives.get("backends", []),
                "passed": distributed_collectives.get("passed_scenarios", 0),
            },
        },
        {
            "id": "distributed-training-optimizer-dev",
            "purpose": "Model DDP, ZeRO, FSDP, tensor/pipeline parallelism, activation checkpointing, optimizer-state sharding, communication exposure, and GPU-host promotion.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["torchrun", "nvidia_smi", "nsys", "nccl", "rccl"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_distributed_training_optimizer.py",
                "python3 scripts/verify_distributed_training_optimizer.py",
            ],
            "evidence": [
                "distributed-training-optimizer/distributed-training-optimizer-report.json",
                "distributed-training-optimizer/reports/distributed-training-optimizer-report.md",
                "site/distributed-training-optimizer.html",
            ],
            "local_facts": {
                "status": distributed_training_optimizer.get("status", "missing"),
                "scenarios": distributed_training_optimizer.get("scenario_count", 0),
                "passed": distributed_training_optimizer.get("passed_scenarios", 0),
                "strategies": distributed_training_optimizer.get("strategy_count", 0),
                "checkpointed": distributed_training_optimizer.get("checkpointed_scenarios", 0),
            },
        },
        {
            "id": "moe-routing-all-to-all-dev",
            "purpose": "Model MoE top-k routing, expert load balance, capacity drops, all-to-all payload, fabric latency, and GPU-host profiler promotion.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["torchrun", "nvidia_smi", "nsys", "ncu"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_moe_routing_all_to_all.py",
                "python3 scripts/verify_moe_routing_all_to_all.py",
            ],
            "evidence": [
                "moe-routing-all-to-all/moe-routing-report.json",
                "moe-routing-all-to-all/reports/moe-routing-report.md",
                "site/moe-routing-all-to-all.html",
            ],
            "local_facts": {
                "status": moe_routing.get("status", "missing"),
                "scenarios": moe_routing.get("scenario_count", 0),
                "passed": moe_routing.get("passed_scenarios", 0),
                "tuning_required": moe_routing.get("tuning_required_scenarios", 0),
            },
        },
        {
            "id": "hardware-capacity-dev",
            "purpose": "Plan GPU hardware class, memory headroom, bottleneck class, power/cost, and validation commands across kernel, serving, and training workloads.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvidia_smi", "hipcc", "rocprof", "nsys", "ncu", "torchrun"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_hardware_capacity_plan.py",
                "python3 scripts/verify_hardware_capacity_plan.py",
            ],
            "evidence": [
                "hardware-capacity-planning/hardware-capacity-plan.json",
                "hardware-capacity-planning/reports/hardware-capacity-plan.md",
                "site/hardware-capacity.html",
            ],
            "local_facts": {
                "status": hardware_capacity.get("status", "missing"),
                "profiles": hardware_capacity.get("profile_count", 0),
                "workloads": hardware_capacity.get("workload_count", 0),
                "recommendations": hardware_capacity.get("recommendation_count", 0),
                "rejected": hardware_capacity.get("rejected_count", 0),
            },
        },
        {
            "id": "quantization-memory-dev",
            "purpose": "Compare BF16, FP8-style, INT8, INT4, and NF4 memory formats for compression, accuracy drift, dequant tax, serving fit, and GPU promotion.",
            "required_capabilities": ["python", "torch"],
            "optional_capabilities": ["nvidia_smi", "triton", "nsys", "ncu"],
            "status": profile_status(["python", "torch"], capabilities),
            "commands": [
                "python3 scripts/run_quantization_memory_formats.py",
                "python3 scripts/verify_quantization_memory_formats.py",
            ],
            "evidence": [
                "quantization-memory-formats/quantization-report.json",
                "quantization-memory-formats/reports/quantization-report.md",
                "site/quantization-memory-formats.html",
            ],
            "local_facts": {
                "status": quantization_report.get("status", "missing"),
                "formats": quantization_report.get("format_count", 0),
                "passed": quantization_report.get("passed_format_count", 0),
                "calibration_needed": quantization_report.get("calibration_needed_count", 0),
            },
        },
        {
            "id": "numerical-reproducibility-dev",
            "purpose": "Check deterministic seeds, precision-mode tolerance, reduction-order drift, and GPU-host reproducibility promotion across CUDA/Triton/ROCm-style paths.",
            "required_capabilities": ["python", "torch"],
            "optional_capabilities": ["nvidia_smi", "triton", "hipcc", "nsys", "ncu"],
            "status": profile_status(["python", "torch"], capabilities),
            "commands": [
                "python3 scripts/run_numerical_reproducibility.py",
                "python3 scripts/verify_numerical_reproducibility.py",
            ],
            "evidence": [
                "numerical-reproducibility/numerical-reproducibility-report.json",
                "numerical-reproducibility/reports/numerical-reproducibility-report.md",
                "site/numerical-reproducibility.html",
            ],
            "local_facts": {
                "status": numerical_reproducibility.get("status", "missing"),
                "scenarios": numerical_reproducibility.get("scenario_count", 0),
                "passed": numerical_reproducibility.get("passed_scenarios", 0),
                "tolerance_reviews": numerical_reproducibility.get("tolerance_review_scenarios", 0),
            },
        },
        {
            "id": "cuda-graphs-latency-dev",
            "purpose": "Model CUDA Graph capture eligibility, warmup, static-shape constraints, p95 latency reduction, and dynamic-shape fallback strategies for serving decode paths.",
            "required_capabilities": ["python", "torch"],
            "optional_capabilities": ["nvidia_smi", "nsys", "ncu"],
            "status": profile_status(["python", "torch"], capabilities),
            "commands": [
                "python3 scripts/run_cuda_graphs_latency.py",
                "python3 scripts/verify_cuda_graphs_latency.py",
            ],
            "evidence": [
                "cuda-graphs-latency/cuda-graphs-latency-report.json",
                "cuda-graphs-latency/reports/cuda-graphs-latency-report.md",
                "site/cuda-graphs-latency.html",
            ],
            "local_facts": {
                "status": cuda_graphs_latency.get("status", "missing"),
                "scenarios": cuda_graphs_latency.get("scenario_count", 0),
                "capture_ready": cuda_graphs_latency.get("capture_ready_count", 0),
                "fallback_required": cuda_graphs_latency.get("fallback_required_count", 0),
            },
        },
        {
            "id": "multi-tenant-scheduling-dev",
            "purpose": "Plan MIG/MPS/Kubernetes-style GPU sharing, isolation, fairness, SLO fit, and queue fallback across serving, batch, CI, and training tenants.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvidia_smi", "kubectl"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_multi_tenant_gpu_scheduling.py",
                "python3 scripts/verify_multi_tenant_gpu_scheduling.py",
            ],
            "evidence": [
                "multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json",
                "multi-tenant-gpu-scheduling/reports/multi-tenant-scheduling-report.md",
                "site/multi-tenant-scheduling.html",
            ],
            "local_facts": {
                "status": multi_tenant_scheduling.get("status", "missing"),
                "policies": multi_tenant_scheduling.get("policy_count", 0),
                "tenants": multi_tenant_scheduling.get("tenant_count", 0),
                "accepted": multi_tenant_scheduling.get("accepted_count", 0),
                "recommended_policy": multi_tenant_scheduling.get("recommended_policy", "missing"),
                "fairness": next(
                    (
                        plan.get("fairness_index", 0)
                        for plan in multi_tenant_scheduling.get("plans", [])
                        if plan.get("policy_id") == multi_tenant_scheduling.get("recommended_policy")
                    ),
                    0,
                ),
            },
        },
        {
            "id": "gpu-import-lint-dev",
            "purpose": "Lint GPU run fixtures and imports for schema, provenance, measured flags, and promotion-step evidence.",
            "required_capabilities": ["python"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/lint_gpu_run_imports.py",
            ],
            "evidence": [
                "gpu-runs/import-lint-report.json",
                "gpu-runs/reports/import-lint-report.md",
                "site/gpu-import-lint.html",
            ],
            "local_facts": {
                "status": gpu_import_lint.get("status", "missing"),
                "files": gpu_import_lint.get("file_count", 0),
                "errors": gpu_import_lint.get("error_count", 0),
                "warnings": gpu_import_lint.get("warning_count", 0),
            },
        },
        {
            "id": "gpu-provenance-dev",
            "purpose": "Separate sample fixtures, host-collected smoke runs, and real measured accelerator-host evidence.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvidia_smi", "nvcc", "hipcc", "nsys", "ncu", "rocprof"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/build_gpu_provenance.py",
                "python3 scripts/verify_gpu_provenance.py",
            ],
            "evidence": [
                "gpu-provenance/gpu-provenance-report.json",
                "gpu-provenance/reports/gpu-provenance-report.md",
                "site/gpu-provenance.html",
            ],
            "local_facts": {
                "status": gpu_provenance.get("status", "missing"),
                "real_gpu_evidence_status": gpu_provenance.get("real_gpu_evidence_status", "missing"),
                "measured_runs": gpu_provenance.get("measured_run_count", 0),
                "sample_runs": gpu_provenance.get("sample_run_count", 0),
                "host_collected_runs": gpu_provenance.get("host_collected_run_count", 0),
            },
        },
        {
            "id": "gpu-measurement-queue-dev",
            "purpose": "Track per-step GPU-host measurement contracts, metrics, thresholds, and real measured completion.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvidia_smi", "nvcc", "hipcc", "nsys", "ncu", "rocprof"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/build_gpu_measurement_queue.py",
                "python3 scripts/verify_gpu_measurement_queue.py",
            ],
            "evidence": [
                "gpu-measurement-queue/gpu-measurement-queue.json",
                "gpu-measurement-queue/reports/gpu-measurement-queue.md",
                "site/gpu-measurement-queue.html",
            ],
            "local_facts": {
                "status": gpu_measurement_queue.get("status", "missing"),
                "tasks": gpu_measurement_queue.get("task_count", 0),
                "queued": gpu_measurement_queue.get("queued_task_count", 0),
                "measured": gpu_measurement_queue.get("measured_task_count", 0),
                "accepted": gpu_measurement_queue.get("accepted_task_count", 0),
                "failed_measured": gpu_measurement_queue.get("failed_measured_task_count", 0),
                "real_measured_completion": gpu_measurement_queue.get("real_measured_completion", False),
            },
        },
        {
            "id": "gpu-acceptance-logic-dev",
            "purpose": "Regression-test GPU measurement threshold logic with canonical accepted and rejected metric rows.",
            "required_capabilities": ["python"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/verify_gpu_acceptance_logic.py",
            ],
            "evidence": [
                "gpu-measurement-queue/acceptance-logic-report.json",
                "gpu-measurement-queue/reports/acceptance-logic-report.md",
                "site/gpu-acceptance-logic.html",
            ],
            "local_facts": {
                "status": gpu_acceptance_logic.get("status", "missing"),
                "cases": gpu_acceptance_logic.get("case_count", 0),
                "accepted_good": gpu_acceptance_logic.get("accepted_good_cases", 0),
                "rejected_bad": gpu_acceptance_logic.get("rejected_bad_cases", 0),
            },
        },
        {
            "id": "gpu-host-preflight-dev",
            "purpose": "Snapshot accelerator-host capabilities and classify GPU promotion steps as runnable or blocked before execution.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvcc", "hipcc", "nvidia_smi", "nsys", "ncu", "rocprof"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_gpu_host_preflight.py",
                "python3 scripts/verify_gpu_host_preflight.py",
            ],
            "evidence": [
                "gpu-handoff/gpu-host-preflight.json",
                "gpu-handoff/reports/gpu-host-preflight.md",
                "site/gpu-host-preflight.html",
            ],
            "local_facts": {
                "status": gpu_host_preflight.get("status", "missing"),
                "accelerator_ready": gpu_host_preflight.get("accelerator_ready", False),
                "steps": gpu_host_preflight.get("step_count", 0),
                "runnable": gpu_host_preflight.get("runnable_step_count", 0),
                "blocked": gpu_host_preflight.get("blocked_step_count", 0),
            },
        },
        {
            "id": "gpu-handoff-dev",
            "purpose": "Generate the portable GPU-host handoff bundle with entrypoint, bundle files, and validation commands.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvcc", "hipcc", "nvidia_smi", "nsys", "ncu", "rocprof"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/build_gpu_handoff.py",
                "python3 scripts/verify_gpu_handoff.py",
            ],
            "evidence": [
                "gpu-handoff/gpu-host-handoff.json",
                "gpu-handoff/reports/gpu-host-handoff.md",
                "gpu-handoff/bin/run-gpu-host-handoff.sh",
                "site/gpu-handoff.html",
            ],
            "local_facts": {
                "status": gpu_handoff.get("status", "missing"),
                "commands": gpu_handoff.get("suite_summary", {}).get("command_count", 0),
                "bundle_files": len(gpu_handoff.get("bundle_files", [])),
                "entrypoint": gpu_handoff.get("entrypoint", ""),
            },
        },
        {
            "id": "assessment-grading-dev",
            "purpose": "Score the generated concept checks and practical tasks against current artifact evidence.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["torch", "triton"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/grade_assessment.py",
                "python3 scripts/verify_assessment_grading.py",
            ],
            "evidence": [
                "assessment/grading-report.json",
                "assessment/reports/grading-report.md",
                "site/assessment-grading.html",
            ],
            "local_facts": {
                "score": assessment_grading.get("score", 0),
                "max_score": assessment_grading.get("max_score", 0),
                "concept_count": assessment_grading.get("concept_count", 0),
                "practical_count": assessment_grading.get("practical_count", 0),
                "status": assessment_grading.get("status", "missing"),
            },
        },
        {
            "id": "assessment-dev",
            "purpose": "Generate and verify the concept exam and practical task bank across GPUMODE lessons, official tutorials, and implemented artifacts.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["torch", "triton"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/build_assessment.py",
                "python3 scripts/verify_assessment.py",
            ],
            "evidence": [
                "assessment/question-bank.json",
                "assessment/reports/assessment-report.md",
                "site/assessment.html",
            ],
            "local_facts": {
                "concept_questions": assessment.get("concept_question_count", 0),
                "practical_tasks": assessment.get("practical_task_count", 0),
                "total_points": assessment.get("total_points", 0),
                "status": assessment.get("status", "missing"),
            },
        },
        {
            "id": "capstone-acceptance-dev",
            "purpose": "Grade the complete GPU curriculum stack as a portfolio-grade end-to-end systems project.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["torch", "triton", "nvidia_smi"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/build_capstone_acceptance.py",
                "python3 scripts/verify_capstone_acceptance.py",
            ],
            "evidence": [
                "capstone-acceptance/capstone-acceptance.json",
                "capstone-acceptance/reports/capstone-acceptance.md",
                "site/capstone-acceptance.html",
            ],
            "local_facts": {
                "score": capstone_acceptance.get("score", 0),
                "max_score": capstone_acceptance.get("max_score", 0),
                "status": capstone_acceptance.get("status", "missing"),
                "criteria": capstone_acceptance.get("criteria_count", 0),
            },
        },
        {
            "id": "gpu-promotion-dev",
            "purpose": "Generate the ordered GPU-host promotion manifest for CUDA, Triton, custom op, model, serving, profiler, ROCm/HIP, distributed, and regression runs.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvcc", "hipcc", "nvidia_smi", "nsys", "ncu", "rocprof"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/build_gpu_promotion.py",
                "python3 scripts/verify_gpu_promotion.py",
            ],
            "evidence": [
                "gpu-promotion/gpu-host-promotion-manifest.json",
                "gpu-promotion/reports/gpu-host-promotion-runbook.md",
                "site/gpu-promotion.html",
            ],
            "local_facts": {
                "steps": gpu_promotion.get("step_count", 0),
                "ready_on_this_host": gpu_promotion.get("ready_on_this_host", 0),
                "ready_on_gpu_host": gpu_promotion.get("ready_on_gpu_host", 0),
            },
        },
        {
            "id": "regression-ledger-dev",
            "purpose": "Collect stable metrics across generated GPU curriculum layers and fail on correctness or performance-regression threshold violations.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["torch", "triton", "nvidia_smi"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/build_regression_ledger.py",
                "python3 scripts/verify_regression_ledger.py",
            ],
            "evidence": [
                "regression-ledger/regression-ledger.json",
                "regression-ledger/reports/regression-ledger.md",
                "site/regression-ledger.html",
            ],
            "local_facts": {
                "metrics": regression_ledger.get("metric_count", 0),
                "passed": regression_ledger.get("passed", 0),
                "warnings": regression_ledger.get("warnings", 0),
                "failed": regression_ledger.get("failed", 0),
            },
        },
        {
            "id": "model-integration-dev",
            "purpose": "Run a tiny transformer block that uses custom-op fusion and autotune selections inside a model-shaped path.",
            "required_capabilities": ["python", "torch"],
            "optional_capabilities": ["triton", "nvcc", "nvidia_smi"],
            "status": profile_status(["python", "torch"], capabilities),
            "commands": [
                "python3 scripts/run_model_integration.py",
                "python3 scripts/verify_model_integration.py",
            ],
            "evidence": [
                "model-integration/model_integration/tiny_transformer.py",
                "model-integration/reports/tiny-transformer-report.json",
                "site/model-integration.html",
            ],
            "local_facts": {
                "cases": model_report.get("case_count", 0),
                "passed": model_report.get("passed", 0),
                "model": model_report.get("model", ""),
                "uses_custom_op": model_report.get("uses_custom_op", ""),
            },
        },
        {
            "id": "autotune-dev",
            "purpose": "Persist benchmark-derived tuning records and select starting configs by operator family and shape class.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["torch", "triton", "nvcc", "nvidia_smi"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/build_autotune_db.py",
                "python3 scripts/build_autotune_db.py --select-family matmul --select-shape medium-square",
                "python3 scripts/verify_autotune_db.py",
            ],
            "evidence": [
                "autotune-db/autotune-db.json",
                "autotune-db/reports/autotune-report.md",
                "site/autotune-db.html",
            ],
            "local_facts": {
                "records": autotune_db.get("record_count", 0),
                "families": autotune_db.get("families", []),
                "source_reports": autotune_db.get("source_reports", []),
            },
        },
        {
            "id": "custom-op-dev",
            "purpose": "Validate PyTorch custom operator integration with forward/backward correctness, fuzz shapes, and CUDA extension source promotion.",
            "required_capabilities": ["python", "torch"],
            "optional_capabilities": ["nvcc", "ninja", "nvidia_smi"],
            "status": profile_status(["python", "torch"], capabilities),
            "commands": [
                "python3 scripts/run_custom_ops.py",
                "python3 scripts/verify_custom_ops.py",
                "python3 -m torch.utils.cpp_extension <custom-op-build>",
            ],
            "evidence": [
                "custom-ops/custom_ops/fused_bias_gelu_residual.py",
                "custom-ops/csrc/fused_bias_gelu_residual.cpp",
                "custom-ops/csrc/fused_bias_gelu_residual_kernel.cu",
                "custom-ops/reports/custom-op-report.json",
                "site/custom-ops.html",
            ],
            "local_facts": {
                "case_count": custom_op_report.get("case_count", 0),
                "passed": custom_op_report.get("passed", 0),
                "operator": custom_op_report.get("operator", ""),
                "compiled_extension_status": custom_op_report.get("accelerator_readiness", {}).get("compiled_extension_status", "unknown"),
            },
        },
        {
            "id": "serving-dev",
            "purpose": "Replay LLM serving traces and validate TTFT, TPOT, throughput, prefix-cache reuse, and KV pressure.",
            "required_capabilities": ["python"],
            "optional_capabilities": ["nvidia_smi"],
            "status": profile_status(["python"], capabilities),
            "commands": [
                "python3 scripts/run_serving_traces.py",
                "python3 scripts/verify_serving_traces.py",
                "vllm serve <model> --enable-prefix-caching",
            ],
            "evidence": [
                "serving-traces/fixtures/*.json",
                "serving-traces/reports/serving-trace-report.json",
                "site/serving-traces.html",
            ],
            "local_facts": {
                "trace_count": serving_report.get("trace_count", 0),
                "passed_traces": serving_report.get("passed_traces", 0),
                "policy_ids": serving_report.get("policy_ids", []),
                "prefix_cache_blocks_saved": sum(row.get("prefix_cache_blocks_saved", 0) for row in serving_report.get("comparisons", [])),
            },
        },
        {
            "id": "cuda-dev",
            "purpose": "Compile CUDA kernel sources and promote CPU/PyTorch measurements to GPU timings.",
            "required_capabilities": ["nvcc", "nvidia_smi"],
            "status": profile_status(["nvcc", "nvidia_smi"], capabilities, fallback_ok=True),
            "commands": [
                "nvcc -O3 kernel-benchmarks/kernels/cuda/memory.cu -c",
                "nvcc -O3 kernel-benchmarks/kernels/cuda/reduction.cu -c",
                "nvcc -O3 kernel-benchmarks/kernels/cuda/softmax_layernorm.cu -c",
                "nvcc -O3 kernel-benchmarks/kernels/cuda/matmul_mlp.cu -c",
                "python3 scripts/run_kernel_benchmarks.py",
            ],
            "evidence": [
                "kernel-benchmarks/kernels/cuda/*.cu",
                "kernel-benchmarks/reports/kernel-benchmark-report.json",
            ],
            "local_facts": {
                "cuda_project_status": next((row.get("starter_status") for row in project_report.get("projects", []) if row.get("id") == "cuda-memory-kernel"), "unknown"),
                "nvcc": capabilities["nvcc"],
                "nvidia_smi": capabilities["nvidia_smi"],
            },
        },
        {
            "id": "triton-dev",
            "purpose": "Run Triton kernels on a CUDA GPU and compare against PyTorch baselines.",
            "required_capabilities": ["triton", "nvidia_smi"],
            "status": profile_status(["triton", "nvidia_smi"], capabilities, fallback_ok=True),
            "commands": [
                "python3 kernel-benchmarks/kernels/triton/memory.py",
                "python3 kernel-benchmarks/kernels/triton/reduction.py",
                "python3 kernel-benchmarks/kernels/triton/softmax_layernorm.py",
                "python3 kernel-benchmarks/kernels/triton/matmul_mlp.py",
                "python3 scripts/run_kernel_benchmarks.py",
            ],
            "evidence": [
                "kernel-benchmarks/kernels/triton/*.py",
                "programming-projects/triton-fused-softmax/measurements.json",
            ],
            "local_facts": {
                "triton": capabilities["triton"],
                "nvidia_smi": capabilities["nvidia_smi"],
            },
        },
        {
            "id": "rocm-hip-dev",
            "purpose": "Compile HIP portability sources and run rocprof-backed measurements.",
            "required_capabilities": ["hipcc", "rocprof"],
            "status": profile_status(["hipcc", "rocprof"], capabilities, fallback_ok=True),
            "commands": [
                "hipcc programming-projects/rocm-hip-port/kernel.hip.cpp -o /tmp/rocm-hip-port",
                "rocprof /tmp/rocm-hip-port",
            ],
            "evidence": [
                "programming-projects/rocm-hip-port/kernel.hip.cpp",
                "programming-projects/rocm-hip-port/measurements.json",
            ],
            "local_facts": {
                "rocm_project_status": next((row.get("starter_status") for row in project_report.get("projects", []) if row.get("id") == "rocm-hip-port"), "unknown"),
                "hipcc": capabilities["hipcc"],
                "rocprof": capabilities["rocprof"],
            },
        },
        {
            "id": "profiler-dev",
            "purpose": "Collect Nsight Systems/Compute evidence and feed profiler-to-roofline reports.",
            "required_capabilities": ["nvidia_smi"],
            "optional_capabilities": ["nsys", "ncu"],
            "status": profile_status(["nvidia_smi"], capabilities, fallback_ok=True),
            "commands": [
                "ncu --set full --target-processes all <kernel-command>",
                "nsys profile <serving-command>",
                "python3 scripts/gpu_workbench_programs.py evidence-report \"nsight roofline dram counters\"",
            ],
            "evidence": [
                "program-outputs/profiling-roofline-nsight-roofline-dram-counters-evidence.json",
                "comprehensive-labs/measurements/comp-lab-08-profiler-evidence.json",
                "profiler-evidence/reports/profiler-evidence-report.json",
            ],
            "local_facts": {
                "nsys": capabilities["nsys"],
                "ncu": capabilities["ncu"],
                "profiler_model_available": True,
            },
        },
        {
            "id": "distributed-dev",
            "purpose": "Run multi-process/multi-GPU collective tests and compare against ring/tree models.",
            "required_capabilities": ["torchrun"],
            "optional_capabilities": ["mpirun", "nvidia_smi"],
            "status": profile_status(["torchrun"], capabilities, fallback_ok=True),
            "commands": [
                "torchrun --nproc_per_node=2 <collective-test>",
                "python3 scripts/gpu_workbench.py \"nccl nvshmem all reduce bandwidth\" --run-lab --dry-run",
            ],
            "evidence": [
                "programming-projects/distributed-collectives/measurements.json",
                "comprehensive-labs/measurements/comp-lab-07-distributed-collectives.json",
            ],
            "local_facts": {
                "torchrun": capabilities["torchrun"],
                "mpirun": capabilities["mpirun"],
            },
        },
    ]


def markdown(matrix: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Runtime Matrix",
        "",
        f"Generated: `{matrix['generated_at']}`",
        "",
        "## Local Capabilities",
        "",
    ]
    for key, value in matrix["local_capabilities"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Profiles", "", "| Profile | Status | Purpose | Commands |", "|---|---|---|---|"])
    for profile in matrix["profiles"]:
        commands = "<br>".join(f"`{cmd}`" for cmd in profile["commands"])
        lines.append(f"| `{profile['id']}` | `{profile['status']}` | {profile['purpose']} | {commands} |")
    return "\n".join(lines).rstrip() + "\n"


def build() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    reports = {
        "kernel_report": load_json(ROOT / "kernel-benchmarks/reports/kernel-benchmark-report.json", {}),
        "compiler_runtime": load_json(ROOT / "compiler-runtime-inspection/compiler-runtime-report.json", {}),
        "project_report": load_json(ROOT / "programming-projects/project-run-report.json", {}),
        "lesson_lab_run": load_json(ROOT / "lesson-labs/run-report.json", {}),
        "comprehensive_run": load_json(ROOT / "comprehensive-labs/run-report.json", {}),
        "serving_report": load_json(ROOT / "serving-traces/reports/serving-trace-report.json", {}),
        "tensor_core_gemm": load_json(ROOT / "tensor-core-gemm/tensor-core-gemm-report.json", {}),
        "persistent_kernels": load_json(ROOT / "persistent-kernels/persistent-kernels-report.json", {}),
        "parallel_primitives": load_json(ROOT / "parallel-primitives/parallel-primitives-report.json", {}),
        "kv_cache": load_json(ROOT / "kv-cache-paged-attention/kv-cache-report.json", {}),
        "attention_serving": load_json(ROOT / "attention-serving-stack/attention-serving-report.json", {}),
        "flash_attention_backward": load_json(ROOT / "flash-attention-backward/flash-attention-backward-report.json", {}),
        "sparse_attention": load_json(ROOT / "sparse-attention-kernels/sparse-attention-report.json", {}),
        "fused_training": load_json(ROOT / "fused-training-kernels/fused-training-report.json", {}),
        "serving_engine_comparison": load_json(ROOT / "serving-engine-comparison/serving-engine-comparison.json", {}),
        "speculative_decoding": load_json(ROOT / "speculative-decoding-serving/speculative-decoding-report.json", {}),
        "distributed_topology": load_json(ROOT / "distributed-topology/distributed-topology-plan.json", {}),
        "distributed_collectives": load_json(ROOT / "distributed-collectives/distributed-collectives-report.json", {}),
        "distributed_training_optimizer": load_json(ROOT / "distributed-training-optimizer/distributed-training-optimizer-report.json", {}),
        "moe_routing": load_json(ROOT / "moe-routing-all-to-all/moe-routing-report.json", {}),
        "hardware_capacity": load_json(ROOT / "hardware-capacity-planning/hardware-capacity-plan.json", {}),
        "quantization_report": load_json(ROOT / "quantization-memory-formats/quantization-report.json", {}),
        "numerical_reproducibility": load_json(ROOT / "numerical-reproducibility/numerical-reproducibility-report.json", {}),
        "cuda_graphs_latency": load_json(ROOT / "cuda-graphs-latency/cuda-graphs-latency-report.json", {}),
        "multi_tenant_scheduling": load_json(ROOT / "multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json", {}),
        "custom_op_report": load_json(ROOT / "custom-ops/reports/custom-op-report.json", {}),
        "autotune_db": load_json(ROOT / "autotune-db/autotune-db.json", {}),
        "model_report": load_json(ROOT / "model-integration/reports/tiny-transformer-report.json", {}),
        "regression_ledger": load_json(ROOT / "regression-ledger/regression-ledger.json", {}),
        "gpu_promotion": load_json(ROOT / "gpu-promotion/gpu-host-promotion-manifest.json", {}),
        "gpu_promotion_suite": load_json(ROOT / "gpu-promotion/suite-run-report.json", {}),
        "gpu_import_lint": load_json(ROOT / "gpu-runs/import-lint-report.json", {}),
        "gpu_runs": load_json(ROOT / "gpu-runs/gpu-run-report.json", {}),
        "gpu_provenance": load_json(ROOT / "gpu-provenance/gpu-provenance-report.json", {}),
        "gpu_measurement_queue": load_json(ROOT / "gpu-measurement-queue/gpu-measurement-queue.json", {}),
        "gpu_acceptance_logic": load_json(ROOT / "gpu-measurement-queue/acceptance-logic-report.json", {}),
        "gpu_host_preflight": load_json(ROOT / "gpu-handoff/gpu-host-preflight.json", {}),
        "gpu_handoff": load_json(ROOT / "gpu-handoff/gpu-host-handoff.json", {}),
        "assessment": load_json(ROOT / "assessment/question-bank.json", {}),
        "assessment_grading": load_json(ROOT / "assessment/grading-report.json", {}),
        "capstone_acceptance": load_json(ROOT / "capstone-acceptance/capstone-acceptance.json", {}),
    }
    capabilities = local_capabilities()
    profiles = build_profiles(capabilities, reports)
    matrix = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "local_capabilities": capabilities,
        "profile_count": len(profiles),
        "ready_profiles": sum(1 for row in profiles if row["status"] == "ready"),
        "fallback_profiles": sum(1 for row in profiles if row["status"] == "source-ready-local-fallback"),
        "blocked_profiles": sum(1 for row in profiles if row["status"] == "blocked-by-runtime"),
        "profiles": profiles,
    }
    write_json(MATRIX_JSON, matrix)
    MATRIX_MD.write_text(markdown(matrix), encoding="utf-8")
    return matrix


def main() -> None:
    matrix = build()
    print(
        f"wrote {MATRIX_JSON.relative_to(ROOT)} and {MATRIX_MD.relative_to(ROOT)} "
        f"({matrix['ready_profiles']} ready, {matrix['fallback_profiles']} fallback, {matrix['blocked_profiles']} blocked)"
    )


if __name__ == "__main__":
    main()
