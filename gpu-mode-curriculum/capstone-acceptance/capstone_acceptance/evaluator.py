from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "capstone-acceptance"
REPORT_JSON = OUT / "capstone-acceptance.json"
REPORT_MD = OUT / "reports" / "capstone-acceptance.md"


PATHS = {
    "curriculum": ROOT / "analysis" / "gpumode-curriculum.json",
    "workbench": ROOT / "analysis" / "gpu-systems-workbench.json",
    "project_run": ROOT / "programming-projects" / "project-run-report.json",
    "lesson_labs": ROOT / "lesson-labs" / "run-report.json",
    "comprehensive_labs": ROOT / "comprehensive-labs" / "run-report.json",
    "kernel_benchmarks": ROOT / "kernel-benchmarks" / "reports" / "kernel-benchmark-report.json",
    "compiler_runtime": ROOT / "compiler-runtime-inspection" / "compiler-runtime-report.json",
    "tensor_core_gemm": ROOT / "tensor-core-gemm" / "tensor-core-gemm-report.json",
    "persistent_kernels": ROOT / "persistent-kernels" / "persistent-kernels-report.json",
    "parallel_primitives": ROOT / "parallel-primitives" / "parallel-primitives-report.json",
    "custom_ops": ROOT / "custom-ops" / "reports" / "custom-op-report.json",
    "autotune": ROOT / "autotune-db" / "autotune-db.json",
    "model_integration": ROOT / "model-integration" / "reports" / "tiny-transformer-report.json",
    "serving_traces": ROOT / "serving-traces" / "reports" / "serving-trace-report.json",
    "kv_cache": ROOT / "kv-cache-paged-attention" / "kv-cache-report.json",
    "attention_serving": ROOT / "attention-serving-stack" / "attention-serving-report.json",
    "flash_attention_backward": ROOT / "flash-attention-backward" / "flash-attention-backward-report.json",
    "sparse_attention": ROOT / "sparse-attention-kernels" / "sparse-attention-report.json",
    "fused_training": ROOT / "fused-training-kernels" / "fused-training-report.json",
    "serving_engine_comparison": ROOT / "serving-engine-comparison" / "serving-engine-comparison.json",
    "speculative_decoding": ROOT / "speculative-decoding-serving" / "speculative-decoding-report.json",
    "distributed_topology": ROOT / "distributed-topology" / "distributed-topology-plan.json",
    "distributed_collectives": ROOT / "distributed-collectives" / "distributed-collectives-report.json",
    "distributed_training": ROOT / "distributed-training-optimizer" / "distributed-training-optimizer-report.json",
    "moe_routing": ROOT / "moe-routing-all-to-all" / "moe-routing-report.json",
    "hardware_capacity": ROOT / "hardware-capacity-planning" / "hardware-capacity-plan.json",
    "quantization": ROOT / "quantization-memory-formats" / "quantization-report.json",
    "numerical": ROOT / "numerical-reproducibility" / "numerical-reproducibility-report.json",
    "cuda_graphs": ROOT / "cuda-graphs-latency" / "cuda-graphs-latency-report.json",
    "multi_tenant_scheduling": ROOT / "multi-tenant-gpu-scheduling" / "multi-tenant-scheduling-report.json",
    "regression": ROOT / "regression-ledger" / "regression-ledger.json",
    "gpu_promotion": ROOT / "gpu-promotion" / "gpu-host-promotion-manifest.json",
    "gpu_promotion_suite": ROOT / "gpu-promotion" / "suite-run-report.json",
    "gpu_import_lint": ROOT / "gpu-runs" / "import-lint-report.json",
    "gpu_runs": ROOT / "gpu-runs" / "gpu-run-report.json",
    "gpu_provenance": ROOT / "gpu-provenance" / "gpu-provenance-report.json",
    "gpu_measurement_queue": ROOT / "gpu-measurement-queue" / "gpu-measurement-queue.json",
    "gpu_acceptance_logic": ROOT / "gpu-measurement-queue" / "acceptance-logic-report.json",
    "gpu_host_preflight": ROOT / "gpu-handoff" / "gpu-host-preflight.json",
    "gpu_handoff": ROOT / "gpu-handoff" / "gpu-host-handoff.json",
    "runtime_matrix": ROOT / "runtime-matrix" / "matrix.json",
    "audit": ROOT / "analysis" / "end-to-end-audit.json",
    "assessment": ROOT / "assessment" / "question-bank.json",
    "assessment_grading": ROOT / "assessment" / "grading-report.json",
}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _criterion(criterion_id: str, title: str, points: int, passed: bool, evidence: list[str], facts: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": criterion_id,
        "title": title,
        "points": points,
        "earned": points if passed else 0,
        "status": "passed" if passed else "failed",
        "evidence": evidence,
        "facts": facts,
    }


def _site_pages() -> dict[str, bool]:
    pages = [
        "index.html",
        "workbench.html",
        "lesson-labs.html",
        "kernel-benchmarks.html",
        "compiler-runtime-inspection.html",
        "tensor-core-gemm.html",
        "persistent-kernels.html",
        "parallel-primitives.html",
        "custom-ops.html",
        "autotune-db.html",
        "model-integration.html",
        "serving-traces.html",
        "kv-cache-paged-attention.html",
        "attention-serving-stack.html",
        "flash-attention-backward.html",
        "sparse-attention-kernels.html",
        "fused-training-kernels.html",
        "serving-engine-comparison.html",
        "speculative-decoding-serving.html",
        "distributed-topology.html",
        "distributed-collectives.html",
        "distributed-training-optimizer.html",
        "moe-routing-all-to-all.html",
        "hardware-capacity.html",
        "quantization-memory-formats.html",
        "numerical-reproducibility.html",
        "cuda-graphs-latency.html",
        "multi-tenant-scheduling.html",
        "regression-ledger.html",
        "gpu-promotion.html",
        "gpu-promotion-suite.html",
        "gpu-import-lint.html",
        "gpu-runs.html",
        "gpu-provenance.html",
        "gpu-measurement-queue.html",
        "gpu-acceptance-logic.html",
        "gpu-host-preflight.html",
        "gpu-handoff.html",
        "runtime-matrix.html",
        "profiler-evidence.html",
        "assessment.html",
        "assessment-grading.html",
    ]
    return {page: (ROOT / "site" / page).exists() for page in pages}


def build_acceptance() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    data = {name: load_json(path, {}) for name, path in PATHS.items()}
    curriculum = data["curriculum"]
    workbench = data["workbench"]
    coverage = workbench.get("coverage", {})
    audit = data["audit"]
    site_pages = _site_pages()

    criteria = [
        _criterion(
            "lesson-corpus-coverage",
            "Transcript-backed 118-lesson curriculum and lesson intelligence",
            10,
            curriculum.get("lesson_count") == 118 and curriculum.get("transcript_count", 0) >= 117,
            ["analysis/gpumode-curriculum.json", "analysis/lesson-intelligence.json"],
            {"lessons": curriculum.get("lesson_count", 0), "transcripts": curriculum.get("transcript_count", 0)},
        ),
        _criterion(
            "one-lab-per-lesson",
            "Generated runnable scaffold for every GPUMODE lesson",
            10,
            data["lesson_labs"].get("passed_contracts") == 118,
            ["lesson-labs/run-report.json", "scripts/verify_lesson_labs.py"],
            {"passed_contracts": data["lesson_labs"].get("passed_contracts", 0)},
        ),
        _criterion(
            "comprehensive-programs",
            "Hand-written comprehensive labs combine related lessons into real programs",
            10,
            data["comprehensive_labs"].get("passed") == 8,
            ["comprehensive-labs/run-report.json", "comprehensive-labs/PLAN.md"],
            {"passed": data["comprehensive_labs"].get("passed", 0), "failed": data["comprehensive_labs"].get("failed", 0)},
        ),
        _criterion(
            "project-portfolio",
            "Programming projects, notebooks, and capstone portfolio are runnable and contract-checked",
            10,
            data["project_run"].get("passed_contracts") == 8,
            ["programming-projects/project-run-report.json", "programming-projects/capstone-portfolio.json"],
            {"passed_contracts": data["project_run"].get("passed_contracts", 0)},
        ),
        _criterion(
            "kernel-source-and-benchmarks",
            "CUDA/Triton source families have local correctness/timing reports",
            10,
            data["kernel_benchmarks"].get("passed") == 14 and data["kernel_benchmarks"].get("failed") == 0,
            ["kernel-benchmarks/reports/kernel-benchmark-report.json", "kernel-benchmarks/kernels/cuda", "kernel-benchmarks/kernels/triton"],
            {"passed": data["kernel_benchmarks"].get("passed", 0), "device": data["kernel_benchmarks"].get("accelerator_readiness", {}).get("torch_device", "unknown")},
        ),
        _criterion(
            "compiler-runtime-inspection",
            "Compiler/runtime inspection covers CUDA, Triton, ROCm/HIP, and custom-op source risks",
            10,
            data["compiler_runtime"].get("status") == "inspection-ready"
            and data["compiler_runtime"].get("source_count", 0) >= 10
            and {"cuda", "triton", "custom-op", "hip"}.issubset(set(data["compiler_runtime"].get("groups", []))),
            ["compiler-runtime-inspection/compiler-runtime-report.json", "compiler-runtime-inspection/reports/compiler-runtime-report.md", "scripts/verify_compiler_runtime_inspection.py"],
            {
                "status": data["compiler_runtime"].get("status", "missing"),
                "sources": data["compiler_runtime"].get("source_count", 0),
                "groups": data["compiler_runtime"].get("groups", []),
                "risk_counts": data["compiler_runtime"].get("risk_counts", {}),
            },
        ),
        _criterion(
            "custom-op-model-path",
            "Custom op and model integration connect kernels to transformer-shaped code",
            10,
            data["custom_ops"].get("passed") == 4 and data["model_integration"].get("passed") == 3,
            ["custom-ops/reports/custom-op-report.json", "model-integration/reports/tiny-transformer-report.json"],
            {
                "custom_op_cases": data["custom_ops"].get("passed", 0),
                "model_cases": data["model_integration"].get("passed", 0),
                "uses_custom_op": data["model_integration"].get("uses_custom_op", ""),
            },
        ),
        _criterion(
            "tensor-core-gemm",
            "CUTLASS/CuTe tensor-core GEMM planner covers CTA, warp, MMA, quantized operands, and fused epilogues",
            10,
            data["tensor_core_gemm"].get("status") == "tensor-core-gemm-ready"
            and data["tensor_core_gemm"].get("scenario_count", 0) >= 5
            and data["tensor_core_gemm"].get("tensor_core_eligible_scenarios", 0) >= 5
            and data["tensor_core_gemm"].get("fused_epilogue_scenarios", 0) >= 4
            and data["tensor_core_gemm"].get("gpu_host_promotion", {}).get("required") is True,
            ["tensor-core-gemm/tensor-core-gemm-report.json", "tensor-core-gemm/reports/tensor-core-gemm-report.md", "scripts/verify_tensor_core_gemm.py"],
            {
                "status": data["tensor_core_gemm"].get("status", "missing"),
                "scenarios": data["tensor_core_gemm"].get("scenario_count", 0),
                "tensor_core_eligible": data["tensor_core_gemm"].get("tensor_core_eligible_scenarios", 0),
                "fused_epilogues": data["tensor_core_gemm"].get("fused_epilogue_scenarios", 0),
            },
        ),
        _criterion(
            "persistent-kernels",
            "Persistent-kernel planner covers residency, occupancy, launch amortization, L2 reuse, and producer/consumer tradeoffs",
            10,
            data["persistent_kernels"].get("status") == "persistent-kernels-ready"
            and data["persistent_kernels"].get("scenario_count", 0) >= 6
            and data["persistent_kernels"].get("passed_scenarios", 0) >= 5
            and data["persistent_kernels"].get("family_count", 0) >= 5
            and data["persistent_kernels"].get("gpu_host_promotion", {}).get("required") is True,
            ["persistent-kernels/persistent-kernels-report.json", "persistent-kernels/reports/persistent-kernels-report.md", "scripts/verify_persistent_kernels.py"],
            {
                "status": data["persistent_kernels"].get("status", "missing"),
                "scenarios": data["persistent_kernels"].get("scenario_count", 0),
                "passed": data["persistent_kernels"].get("passed_scenarios", 0),
                "families": data["persistent_kernels"].get("family_count", 0),
                "producer_consumer": data["persistent_kernels"].get("producer_consumer_scenarios", 0),
            },
        ),
        _criterion(
            "parallel-primitives",
            "Parallel-primitives planner covers scan, reduction, compaction, radix sort, histogram, and segmented reduction",
            10,
            data["parallel_primitives"].get("status") == "parallel-primitives-ready"
            and data["parallel_primitives"].get("scenario_count", 0) >= 6
            and data["parallel_primitives"].get("passed_scenarios", 0) >= 5
            and data["parallel_primitives"].get("primitive_count", 0) >= 6
            and data["parallel_primitives"].get("gpu_host_promotion", {}).get("required") is True,
            ["parallel-primitives/parallel-primitives-report.json", "parallel-primitives/reports/parallel-primitives-report.md", "scripts/verify_parallel_primitives.py"],
            {
                "status": data["parallel_primitives"].get("status", "missing"),
                "scenarios": data["parallel_primitives"].get("scenario_count", 0),
                "passed": data["parallel_primitives"].get("passed_scenarios", 0),
                "primitives": data["parallel_primitives"].get("primitive_count", 0),
                "stable_order": data["parallel_primitives"].get("stable_order_scenarios", 0),
            },
        ),
        _criterion(
            "autotune-and-regression",
            "Autotune records and regression ledger preserve performance evidence",
            10,
            data["autotune"].get("record_count") >= 18 and data["regression"].get("failed") == 0 and data["regression"].get("metric_count", 0) >= 95,
            ["autotune-db/autotune-db.json", "regression-ledger/regression-ledger.json"],
            {"autotune_records": data["autotune"].get("record_count", 0), "regression_metrics": data["regression"].get("metric_count", 0)},
        ),
        _criterion(
            "serving-system",
            "Serving traces cover TTFT, TPOT, throughput, prefix cache, and KV pressure",
            10,
            data["serving_traces"].get("passed_traces") == 3,
            ["serving-traces/reports/serving-trace-report.json"],
            {
                "traces": data["serving_traces"].get("trace_count", 0),
                "prefix_blocks_saved": sum(row.get("prefix_cache_blocks_saved", 0) for row in data["serving_traces"].get("comparisons", [])),
            },
        ),
        _criterion(
            "kv-cache-paged-attention",
            "KV-cache allocator layer compares contiguous reservation with PagedAttention block tables",
            10,
            data["kv_cache"].get("status") == "kv-cache-ready"
            and data["kv_cache"].get("scenario_count", 0) >= 5
            and data["kv_cache"].get("passed_scenarios", 0) >= 4
            and data["kv_cache"].get("total_prefix_blocks_reused", 0) > 0
            and data["kv_cache"].get("gpu_host_promotion", {}).get("required") is True,
            ["kv-cache-paged-attention/kv-cache-report.json", "kv-cache-paged-attention/reports/kv-cache-report.md", "scripts/verify_kv_cache_paged_attention.py"],
            {
                "status": data["kv_cache"].get("status", "missing"),
                "scenarios": data["kv_cache"].get("scenario_count", 0),
                "passed": data["kv_cache"].get("passed_scenarios", 0),
                "prefix_blocks_reused": data["kv_cache"].get("total_prefix_blocks_reused", 0),
            },
        ),
        _criterion(
            "attention-serving-stack",
            "FlashAttention-to-vLLM stack connects online softmax tiling with serving scheduler and KV reuse",
            10,
            data["attention_serving"].get("status") == "attention-serving-ready"
            and data["attention_serving"].get("scenario_count", 0) >= 5
            and data["attention_serving"].get("passed_scenarios", 0) >= 4
            and data["attention_serving"].get("total_prefix_blocks_reused", 0) > 0
            and data["attention_serving"].get("gpu_host_promotion", {}).get("required") is True,
            ["attention-serving-stack/attention-serving-report.json", "attention-serving-stack/reports/attention-serving-report.md", "scripts/verify_attention_serving_stack.py"],
            {
                "status": data["attention_serving"].get("status", "missing"),
                "scenarios": data["attention_serving"].get("scenario_count", 0),
                "passed": data["attention_serving"].get("passed_scenarios", 0),
                "prefix_blocks_reused": data["attention_serving"].get("total_prefix_blocks_reused", 0),
            },
        ),
        _criterion(
            "flash-attention-backward",
            "FlashAttention backward layer covers dQ, dK, dV, dSoftmax, recompute, dropout, GQA, and gradient error",
            10,
            data["flash_attention_backward"].get("status") == "flash-attention-backward-ready"
            and data["flash_attention_backward"].get("scenario_count", 0) >= 6
            and data["flash_attention_backward"].get("passed_scenarios", 0) >= 5
            and data["flash_attention_backward"].get("dropout_scenarios", 0) >= 1
            and data["flash_attention_backward"].get("grouped_query_scenarios", 0) >= 1
            and data["flash_attention_backward"].get("gpu_host_promotion", {}).get("required") is True,
            ["flash-attention-backward/flash-attention-backward-report.json", "flash-attention-backward/reports/flash-attention-backward-report.md", "scripts/verify_flash_attention_backward.py"],
            {
                "status": data["flash_attention_backward"].get("status", "missing"),
                "scenarios": data["flash_attention_backward"].get("scenario_count", 0),
                "passed": data["flash_attention_backward"].get("passed_scenarios", 0),
                "dropout": data["flash_attention_backward"].get("dropout_scenarios", 0),
                "grouped_query": data["flash_attention_backward"].get("grouped_query_scenarios", 0),
            },
        ),
        _criterion(
            "sparse-attention-kernels",
            "Sparse attention layer covers block-sparse, sliding-window, ragged decode, neighborhood, top-k, metadata, load-balance, and backward evidence",
            10,
            data["sparse_attention"].get("status") == "sparse-attention-ready"
            and data["sparse_attention"].get("scenario_count", 0) >= 6
            and data["sparse_attention"].get("passed_scenarios", 0) >= 5
            and data["sparse_attention"].get("pattern_count", 0) >= 6
            and data["sparse_attention"].get("ragged_scenarios", 0) >= 1
            and data["sparse_attention"].get("backward_scenarios", 0) >= 4
            and data["sparse_attention"].get("gpu_host_promotion", {}).get("required") is True,
            ["sparse-attention-kernels/sparse-attention-report.json", "sparse-attention-kernels/reports/sparse-attention-report.md", "scripts/verify_sparse_attention_kernels.py"],
            {
                "status": data["sparse_attention"].get("status", "missing"),
                "scenarios": data["sparse_attention"].get("scenario_count", 0),
                "passed": data["sparse_attention"].get("passed_scenarios", 0),
                "patterns": data["sparse_attention"].get("pattern_count", 0),
                "ragged": data["sparse_attention"].get("ragged_scenarios", 0),
                "backward": data["sparse_attention"].get("backward_scenarios", 0),
            },
        ),
        _criterion(
            "fused-training-kernels",
            "Fused training layer covers RMSNorm, SwiGLU, cross-entropy, AdamW, grad clipping, dropout/residual/norm, backward, optimizer-state, and HBM/launch evidence",
            10,
            data["fused_training"].get("status") == "fused-training-ready"
            and data["fused_training"].get("scenario_count", 0) >= 6
            and data["fused_training"].get("passed_scenarios", 0) >= 5
            and data["fused_training"].get("family_count", 0) >= 5
            and data["fused_training"].get("backward_scenarios", 0) >= 4
            and data["fused_training"].get("optimizer_state_scenarios", 0) >= 2
            and data["fused_training"].get("gpu_host_promotion", {}).get("required") is True,
            ["fused-training-kernels/fused-training-report.json", "fused-training-kernels/reports/fused-training-report.md", "scripts/verify_fused_training_kernels.py"],
            {
                "status": data["fused_training"].get("status", "missing"),
                "scenarios": data["fused_training"].get("scenario_count", 0),
                "passed": data["fused_training"].get("passed_scenarios", 0),
                "families": data["fused_training"].get("family_count", 0),
                "backward": data["fused_training"].get("backward_scenarios", 0),
                "optimizer_state": data["fused_training"].get("optimizer_state_scenarios", 0),
            },
        ),
        _criterion(
            "serving-engine-comparison",
            "Production inference engine comparison covers vLLM, TGI, SGLang, TensorRT-LLM, and HF Transformers",
            10,
            data["serving_engine_comparison"].get("status") == "comparison-ready"
            and data["serving_engine_comparison"].get("engine_count", 0) >= 5
            and data["serving_engine_comparison"].get("scenario_count", 0) >= 5,
            ["serving-engine-comparison/serving-engine-comparison.json", "serving-engine-comparison/reports/serving-engine-comparison.md", "scripts/verify_serving_engine_comparison.py"],
            {
                "status": data["serving_engine_comparison"].get("status", "missing"),
                "engines": data["serving_engine_comparison"].get("engine_count", 0),
                "scenarios": data["serving_engine_comparison"].get("scenario_count", 0),
                "engine_wins": data["serving_engine_comparison"].get("engine_wins", {}),
            },
        ),
        _criterion(
            "speculative-decoding-serving",
            "Speculative decoding serving layer covers draft/target verification, rollback, KV commits, and scheduler policy",
            10,
            data["speculative_decoding"].get("status") == "speculative-decoding-ready"
            and data["speculative_decoding"].get("scenario_count", 0) >= 6
            and data["speculative_decoding"].get("passed_scenarios", 0) >= 4
            and data["speculative_decoding"].get("engine_count", 0) >= 4
            and data["speculative_decoding"].get("scheduler_policy_count", 0) >= 2
            and data["speculative_decoding"].get("min_acceptance_rate", 1.0) < 0.50
            and data["speculative_decoding"].get("gpu_host_promotion", {}).get("required") is True,
            ["speculative-decoding-serving/speculative-decoding-report.json", "speculative-decoding-serving/reports/speculative-decoding-report.md", "scripts/verify_speculative_decoding_serving.py"],
            {
                "status": data["speculative_decoding"].get("status", "missing"),
                "scenarios": data["speculative_decoding"].get("scenario_count", 0),
                "passed": data["speculative_decoding"].get("passed_scenarios", 0),
                "engines": data["speculative_decoding"].get("engine_count", 0),
                "policies": data["speculative_decoding"].get("scheduler_policy_count", 0),
                "min_acceptance": data["speculative_decoding"].get("min_acceptance_rate", 0),
            },
        ),
        _criterion(
            "distributed-topology-planning",
            "Multi-GPU topology planning covers tensor, pipeline, and data parallel choices",
            10,
            data["distributed_topology"].get("status") == "topology-plan-ready"
            and data["distributed_topology"].get("topology_count", 0) >= 5
            and data["distributed_topology"].get("workload_count", 0) >= 5
            and data["distributed_topology"].get("candidate_count", 0) > 0,
            ["distributed-topology/distributed-topology-plan.json", "distributed-topology/reports/distributed-topology-plan.md", "scripts/verify_distributed_topology.py"],
            {
                "status": data["distributed_topology"].get("status", "missing"),
                "topologies": data["distributed_topology"].get("topology_count", 0),
                "workloads": data["distributed_topology"].get("workload_count", 0),
                "candidates": data["distributed_topology"].get("candidate_count", 0),
                "rejected": data["distributed_topology"].get("rejected_count", 0),
            },
        ),
        _criterion(
            "distributed-collectives",
            "Distributed collectives layer covers NCCL/RCCL/NVSHMEM algorithms, payloads, overlap, and GPU promotion",
            10,
            data["distributed_collectives"].get("status") == "distributed-collectives-ready"
            and data["distributed_collectives"].get("scenario_count", 0) >= 6
            and data["distributed_collectives"].get("collective_count", 0) >= 5
            and data["distributed_collectives"].get("passed_scenarios", 0) >= 5
            and data["distributed_collectives"].get("gpu_host_promotion", {}).get("required") is True,
            ["distributed-collectives/distributed-collectives-report.json", "distributed-collectives/reports/distributed-collectives-report.md", "scripts/verify_distributed_collectives.py"],
            {
                "status": data["distributed_collectives"].get("status", "missing"),
                "scenarios": data["distributed_collectives"].get("scenario_count", 0),
                "collectives": data["distributed_collectives"].get("collective_count", 0),
                "passed": data["distributed_collectives"].get("passed_scenarios", 0),
                "backends": data["distributed_collectives"].get("backends", []),
            },
        ),
        _criterion(
            "distributed-training-optimizer",
            "Distributed training optimizer layer covers DDP, ZeRO, FSDP, checkpointing, communication overlap, and pipeline bubbles",
            10,
            data["distributed_training"].get("status") == "training-optimizer-ready"
            and data["distributed_training"].get("scenario_count", 0) >= 6
            and data["distributed_training"].get("passed_scenarios", 0) >= 4
            and data["distributed_training"].get("strategy_count", 0) >= 5
            and data["distributed_training"].get("gpu_host_promotion", {}).get("required") is True,
            ["distributed-training-optimizer/distributed-training-optimizer-report.json", "distributed-training-optimizer/reports/distributed-training-optimizer-report.md", "scripts/verify_distributed_training_optimizer.py"],
            {
                "status": data["distributed_training"].get("status", "missing"),
                "scenarios": data["distributed_training"].get("scenario_count", 0),
                "passed": data["distributed_training"].get("passed_scenarios", 0),
                "strategies": data["distributed_training"].get("strategy_count", 0),
                "checkpointed": data["distributed_training"].get("checkpointed_scenarios", 0),
            },
        ),
        _criterion(
            "moe-routing-all-to-all",
            "MoE routing layer covers expert load balance, drops, all-to-all payload, and topology-sensitive promotion",
            10,
            data["moe_routing"].get("status") == "moe-routing-ready"
            and data["moe_routing"].get("scenario_count", 0) >= 5
            and data["moe_routing"].get("passed_scenarios", 0) >= 3
            and data["moe_routing"].get("tuning_required_scenarios", 0) >= 1
            and data["moe_routing"].get("gpu_host_promotion", {}).get("required") is True,
            ["moe-routing-all-to-all/moe-routing-report.json", "moe-routing-all-to-all/reports/moe-routing-report.md", "scripts/verify_moe_routing_all_to_all.py"],
            {
                "status": data["moe_routing"].get("status", "missing"),
                "scenarios": data["moe_routing"].get("scenario_count", 0),
                "passed": data["moe_routing"].get("passed_scenarios", 0),
                "tuning_required": data["moe_routing"].get("tuning_required_scenarios", 0),
            },
        ),
        _criterion(
            "hardware-capacity-planning",
            "Hardware capacity planning maps workloads to GPU classes, memory headroom, bottleneck, power, cost, and validation commands",
            10,
            data["hardware_capacity"].get("status") == "capacity-plan-ready"
            and data["hardware_capacity"].get("profile_count", 0) >= 5
            and data["hardware_capacity"].get("workload_count", 0) >= 5
            and data["hardware_capacity"].get("recommendation_count") == data["hardware_capacity"].get("workload_count"),
            ["hardware-capacity-planning/hardware-capacity-plan.json", "hardware-capacity-planning/reports/hardware-capacity-plan.md", "scripts/verify_hardware_capacity_plan.py"],
            {
                "status": data["hardware_capacity"].get("status", "missing"),
                "profiles": data["hardware_capacity"].get("profile_count", 0),
                "workloads": data["hardware_capacity"].get("workload_count", 0),
                "recommendations": data["hardware_capacity"].get("recommendation_count", 0),
                "rejected": data["hardware_capacity"].get("rejected_count", 0),
            },
        ),
        _criterion(
            "quantization-memory-formats",
            "Quantization memory-format analysis covers compression, drift, dequant tax, serving fit, and GPU promotion",
            10,
            data["quantization"].get("status") == "quantization-ready"
            and data["quantization"].get("format_count", 0) >= 7
            and data["quantization"].get("passed_format_count", 0) >= 4
            and data["quantization"].get("gpu_host_promotion", {}).get("required") is True,
            ["quantization-memory-formats/quantization-report.json", "quantization-memory-formats/reports/quantization-report.md", "scripts/verify_quantization_memory_formats.py"],
            {
                "status": data["quantization"].get("status", "missing"),
                "formats": data["quantization"].get("format_count", 0),
                "passed": data["quantization"].get("passed_format_count", 0),
                "calibration_needed": data["quantization"].get("calibration_needed_count", 0),
            },
        ),
        _criterion(
            "numerical-reproducibility",
            "Numerical reproducibility layer defines tolerance policy across precision and reduction-order modes",
            10,
            data["numerical"].get("status") == "reproducibility-ready"
            and data["numerical"].get("scenario_count", 0) >= 5
            and data["numerical"].get("passed_scenarios", 0) >= 4
            and data["numerical"].get("tolerance_review_scenarios", 0) >= 1
            and data["numerical"].get("gpu_host_promotion", {}).get("required") is True,
            ["numerical-reproducibility/numerical-reproducibility-report.json", "numerical-reproducibility/reports/numerical-reproducibility-report.md", "scripts/verify_numerical_reproducibility.py"],
            {
                "status": data["numerical"].get("status", "missing"),
                "scenarios": data["numerical"].get("scenario_count", 0),
                "passed": data["numerical"].get("passed_scenarios", 0),
                "tolerance_reviews": data["numerical"].get("tolerance_review_scenarios", 0),
            },
        ),
        _criterion(
            "cuda-graphs-latency",
            "CUDA Graphs latency layer models capture eligibility, p95 reduction, and dynamic-shape fallback",
            10,
            data["cuda_graphs"].get("status") == "cuda-graphs-ready"
            and data["cuda_graphs"].get("scenario_count", 0) >= 5
            and data["cuda_graphs"].get("capture_ready_count", 0) >= 3
            and data["cuda_graphs"].get("fallback_required_count", 0) >= 2,
            ["cuda-graphs-latency/cuda-graphs-latency-report.json", "cuda-graphs-latency/reports/cuda-graphs-latency-report.md", "scripts/verify_cuda_graphs_latency.py"],
            {
                "status": data["cuda_graphs"].get("status", "missing"),
                "scenarios": data["cuda_graphs"].get("scenario_count", 0),
                "capture_ready": data["cuda_graphs"].get("capture_ready_count", 0),
                "fallback_required": data["cuda_graphs"].get("fallback_required_count", 0),
            },
        ),
        _criterion(
            "multi-tenant-gpu-scheduling",
            "Multi-tenant GPU scheduling covers MIG/MPS/Kubernetes placement, fairness, isolation, SLO fit, and GPU promotion",
            10,
            data["multi_tenant_scheduling"].get("status") == "scheduling-ready"
            and data["multi_tenant_scheduling"].get("policy_count", 0) >= 4
            and data["multi_tenant_scheduling"].get("tenant_count", 0) >= 5
            and data["multi_tenant_scheduling"].get("accepted_count", 0) >= 4
            and data["multi_tenant_scheduling"].get("gpu_host_promotion", {}).get("required") is True,
            ["multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json", "multi-tenant-gpu-scheduling/reports/multi-tenant-scheduling-report.md", "scripts/verify_multi_tenant_gpu_scheduling.py"],
            {
                "status": data["multi_tenant_scheduling"].get("status", "missing"),
                "policies": data["multi_tenant_scheduling"].get("policy_count", 0),
                "tenants": data["multi_tenant_scheduling"].get("tenant_count", 0),
                "accepted": data["multi_tenant_scheduling"].get("accepted_count", 0),
                "recommended_policy": data["multi_tenant_scheduling"].get("recommended_policy", "missing"),
            },
        ),
        _criterion(
            "gpu-promotion-runtime",
            "GPU-host promotion and runtime gates are explicit about local versus accelerator evidence",
            10,
            data["gpu_promotion"].get("step_count") >= 9 and data["runtime_matrix"].get("profile_count") >= 12,
            ["gpu-promotion/gpu-host-promotion-manifest.json", "runtime-matrix/matrix.json"],
            {
                "promotion_steps": data["gpu_promotion"].get("step_count", 0),
                "ready_on_gpu_host": data["gpu_promotion"].get("ready_on_gpu_host", 0),
                "runtime_profiles": data["runtime_matrix"].get("profile_count", 0),
            },
        ),
        _criterion(
            "gpu-promotion-suite",
            "GPU promotion command suite expands the manifest into a dry-run-safe execution plan",
            10,
            data["gpu_promotion_suite"].get("status") == "dry-run-ready"
            and data["gpu_promotion_suite"].get("command_count", 0) >= 20
            and data["gpu_promotion_suite"].get("step_count", 0) >= 9,
            ["gpu-promotion/suite-run-report.json", "gpu-promotion/reports/suite-run-report.md", "scripts/verify_gpu_promotion_suite.py"],
            {
                "commands": data["gpu_promotion_suite"].get("command_count", 0),
                "steps": data["gpu_promotion_suite"].get("step_count", 0),
                "planned": data["gpu_promotion_suite"].get("planned", 0),
                "skipped": data["gpu_promotion_suite"].get("skipped", 0),
                "status": data["gpu_promotion_suite"].get("status", "missing"),
            },
        ),
        _criterion(
            "gpu-run-imports",
            "GPU-host run import layer captures accelerator validation rows and links them to promotion steps",
            10,
            data["gpu_runs"].get("status") == "import-ready"
            and data["gpu_runs"].get("coverage", {}).get("run_count", 0) >= 2
            and data["gpu_runs"].get("coverage", {}).get("vendor_count", 0) >= 2
            and data["gpu_runs"].get("coverage", {}).get("promotion_step_count", 0) >= 9,
            ["gpu-runs/gpu-run-report.json", "gpu-runs/reports/gpu-run-report.md", "scripts/verify_gpu_runs.py"],
            {
                "runs": data["gpu_runs"].get("coverage", {}).get("run_count", 0),
                "vendors": data["gpu_runs"].get("coverage", {}).get("vendors", []),
                "promotion_steps": data["gpu_runs"].get("coverage", {}).get("promotion_step_count", 0),
                "status": data["gpu_runs"].get("status", "missing"),
            },
        ),
        _criterion(
            "gpu-run-import-lint",
            "GPU run fixture and import files pass schema and provenance linting",
            10,
            data["gpu_import_lint"].get("status") == "lint-clean"
            and data["gpu_import_lint"].get("error_count", 1) == 0
            and data["gpu_import_lint"].get("fixture_count", 0) >= 2
            and data["gpu_import_lint"].get("import_count", 0) >= 1,
            ["gpu-runs/import-lint-report.json", "gpu-runs/reports/import-lint-report.md", "scripts/lint_gpu_run_imports.py"],
            {
                "status": data["gpu_import_lint"].get("status", "missing"),
                "files": data["gpu_import_lint"].get("file_count", 0),
                "errors": data["gpu_import_lint"].get("error_count", 0),
                "warnings": data["gpu_import_lint"].get("warning_count", 0),
            },
        ),
        _criterion(
            "gpu-evidence-provenance",
            "GPU evidence provenance separates sample fixtures from real measured accelerator runs",
            10,
            data["gpu_provenance"].get("status") == "provenance-clear"
            and data["gpu_provenance"].get("sample_run_count", 0) >= 2
            and data["gpu_provenance"].get("host_collected_run_count", 0) >= 1
            and data["gpu_provenance"].get("rows_with_provenance") == data["gpu_provenance"].get("row_count"),
            ["gpu-provenance/gpu-provenance-report.json", "gpu-provenance/reports/gpu-provenance-report.md", "scripts/verify_gpu_provenance.py"],
            {
                "status": data["gpu_provenance"].get("status", "missing"),
                "real_gpu_evidence_status": data["gpu_provenance"].get("real_gpu_evidence_status", "missing"),
                "measured_runs": data["gpu_provenance"].get("measured_run_count", 0),
                "sample_runs": data["gpu_provenance"].get("sample_run_count", 0),
                "host_collected_runs": data["gpu_provenance"].get("host_collected_run_count", 0),
            },
        ),
        _criterion(
            "gpu-measurement-queue",
            "GPU measurement queue defines per-step metrics and acceptance thresholds for real accelerator validation",
            10,
            data["gpu_measurement_queue"].get("status") == "queue-ready"
            and data["gpu_measurement_queue"].get("task_count", 0) >= 9
            and data["gpu_measurement_queue"].get("failed_measured_task_count", 0) == 0
            and all(task.get("has_metric_contract") for task in data["gpu_measurement_queue"].get("tasks", [])),
            ["gpu-measurement-queue/gpu-measurement-queue.json", "gpu-measurement-queue/reports/gpu-measurement-queue.md", "scripts/verify_gpu_measurement_queue.py"],
            {
                "status": data["gpu_measurement_queue"].get("status", "missing"),
                "tasks": data["gpu_measurement_queue"].get("task_count", 0),
                "queued": data["gpu_measurement_queue"].get("queued_task_count", 0),
                "measured": data["gpu_measurement_queue"].get("measured_task_count", 0),
                "accepted": data["gpu_measurement_queue"].get("accepted_task_count", 0),
                "failed_measured": data["gpu_measurement_queue"].get("failed_measured_task_count", 0),
                "real_measured_completion": data["gpu_measurement_queue"].get("real_measured_completion", False),
            },
        ),
        _criterion(
            "gpu-acceptance-logic",
            "GPU measurement acceptance logic accepts good metric rows and rejects bad metric rows",
            10,
            data["gpu_acceptance_logic"].get("status") == "passed"
            and data["gpu_acceptance_logic"].get("accepted_good_cases", 0) >= 9
            and data["gpu_acceptance_logic"].get("rejected_bad_cases", 0) >= 9,
            ["gpu-measurement-queue/acceptance-logic-report.json", "gpu-measurement-queue/reports/acceptance-logic-report.md", "scripts/verify_gpu_acceptance_logic.py"],
            {
                "status": data["gpu_acceptance_logic"].get("status", "missing"),
                "cases": data["gpu_acceptance_logic"].get("case_count", 0),
                "accepted_good": data["gpu_acceptance_logic"].get("accepted_good_cases", 0),
                "rejected_bad": data["gpu_acceptance_logic"].get("rejected_bad_cases", 0),
            },
        ),
        _criterion(
            "gpu-host-preflight",
            "GPU-host preflight classifies accelerator promotion steps before execution",
            10,
            data["gpu_host_preflight"].get("status") == "preflight-complete"
            and data["gpu_host_preflight"].get("step_count", 0) >= 9
            and data["gpu_host_preflight"].get("runnable_step_count", 0) + data["gpu_host_preflight"].get("blocked_step_count", 0) == data["gpu_host_preflight"].get("step_count", -1),
            ["gpu-handoff/gpu-host-preflight.json", "gpu-handoff/reports/gpu-host-preflight.md", "scripts/verify_gpu_host_preflight.py"],
            {
                "status": data["gpu_host_preflight"].get("status", "missing"),
                "accelerator_ready": data["gpu_host_preflight"].get("accelerator_ready", False),
                "steps": data["gpu_host_preflight"].get("step_count", 0),
                "runnable": data["gpu_host_preflight"].get("runnable_step_count", 0),
                "blocked": data["gpu_host_preflight"].get("blocked_step_count", 0),
            },
        ),
        _criterion(
            "gpu-host-handoff",
            "Portable GPU-host handoff bundle packages execution, collection, and validation commands",
            10,
            data["gpu_handoff"].get("status") == "ready"
            and data["gpu_handoff"].get("suite_summary", {}).get("command_count", 0) >= 20
            and len(data["gpu_handoff"].get("bundle_files", [])) >= 8,
            ["gpu-handoff/gpu-host-handoff.json", "gpu-handoff/reports/gpu-host-handoff.md", "gpu-handoff/bin/run-gpu-host-handoff.sh", "scripts/verify_gpu_handoff.py"],
            {
                "status": data["gpu_handoff"].get("status", "missing"),
                "commands": data["gpu_handoff"].get("suite_summary", {}).get("command_count", 0),
                "bundle_files": len(data["gpu_handoff"].get("bundle_files", [])),
                "entrypoint": data["gpu_handoff"].get("entrypoint", ""),
            },
        ),
        _criterion(
            "assessment-readiness",
            "Concept exam and practical task bank cover lessons, official tutorials, and implemented artifact layers",
            10,
            data["assessment"].get("status") == "ready"
            and data["assessment"].get("concept_question_count", 0) >= 10
            and data["assessment"].get("practical_task_count", 0) >= 10
            and data["assessment"].get("total_points", 0) >= 100,
            ["assessment/question-bank.json", "assessment/reports/assessment-report.md", "scripts/verify_assessment.py"],
            {
                "concept_questions": data["assessment"].get("concept_question_count", 0),
                "practical_tasks": data["assessment"].get("practical_task_count", 0),
                "total_points": data["assessment"].get("total_points", 0),
                "tutorial_providers": data["assessment"].get("tutorial_provider_count", 0),
            },
        ),
        _criterion(
            "assessment-grading",
            "Assessment grader scores concept readiness and practical artifact evidence",
            10,
            data["assessment_grading"].get("status") == "passed"
            and data["assessment_grading"].get("score") == data["assessment_grading"].get("max_score")
            and data["assessment_grading"].get("practical_count", 0) >= 12,
            ["assessment/grading-report.json", "assessment/reports/grading-report.md", "scripts/verify_assessment_grading.py"],
            {
                "score": data["assessment_grading"].get("score", 0),
                "max_score": data["assessment_grading"].get("max_score", 0),
                "concept_count": data["assessment_grading"].get("concept_count", 0),
                "practical_count": data["assessment_grading"].get("practical_count", 0),
            },
        ),
        _criterion(
            "site-and-audit",
            "Generated site and end-to-end audit expose every major layer",
            10,
            all(site_pages.values()) and audit.get("overall_status") == "proven-with-runtime-caveats",
            ["site/*.html", "analysis/end-to-end-audit.json"],
            {"site_pages": site_pages, "audit_status": audit.get("overall_status", "missing")},
        ),
    ]
    total = sum(row["points"] for row in criteria)
    earned = sum(row["earned"] for row in criteria)
    acceptance = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "score": earned,
        "max_score": total,
        "percent": round(earned / max(total, 1) * 100, 2),
        "status": "accepted-with-runtime-caveats" if earned == total else "incomplete",
        "criteria_count": len(criteria),
        "passed_criteria": sum(1 for row in criteria if row["status"] == "passed"),
        "failed_criteria": sum(1 for row in criteria if row["status"] == "failed"),
        "coverage_snapshot": {
            "workbench_profiles": coverage.get("profile_count", 0),
            "paper_json": coverage.get("paper_json", 0),
            "tutorial_sources": coverage.get("tutorial_sources", 0),
            "measurement_artifacts": coverage.get("measurement_artifacts", 0),
        },
        "criteria": criteria,
    }
    REPORT_JSON.write_text(json.dumps(acceptance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(acceptance), encoding="utf-8")
    return acceptance


def render_markdown(acceptance: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Capstone Acceptance",
        "",
        f"Generated: `{acceptance['generated_at']}`",
        f"Status: `{acceptance['status']}`",
        f"Score: `{acceptance['score']}/{acceptance['max_score']}` ({acceptance['percent']}%)",
        "",
        "| criterion | status | points | evidence |",
        "|---|---|---:|---|",
    ]
    for row in acceptance["criteria"]:
        lines.append(f"| {row['id']} | {row['status']} | {row['earned']}/{row['points']} | {', '.join(row['evidence'])} |")
    return "\n".join(lines).rstrip() + "\n"
