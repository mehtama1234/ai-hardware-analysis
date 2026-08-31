#!/usr/bin/env python3
"""Build a requirement-to-evidence audit for the GPUMODE workbench goal."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
LAB_ROOT = ROOT.parent / "gpu-kernels-serving-lab"
OUT_JSON = ANALYSIS / "end-to-end-audit.json"
OUT_MD = ANALYSIS / "end-to-end-audit.md"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def status(ok: bool, caveat: str = "") -> str:
    if ok and not caveat:
        return "proven"
    if ok and caveat:
        return "proven-with-runtime-caveat"
    return "missing-or-incomplete"


def evidence_item(requirement: str, ok: bool, evidence: list[str], facts: dict[str, Any], caveat: str = "") -> dict[str, Any]:
    return {
        "requirement": requirement,
        "status": status(ok, caveat),
        "evidence": evidence,
        "facts": facts,
        "caveat": caveat,
    }


def build_audit() -> dict[str, Any]:
    curriculum = read_json(ANALYSIS / "gpumode-curriculum.json")
    graph = read_json(ANALYSIS / "curriculum-graph.json")
    intelligence = read_json(ANALYSIS / "lesson-intelligence.json")
    transcript_index = read_json(ROOT / "raw-material/youtube/transcript-index.json")
    workbench = read_json(ANALYSIS / "gpu-systems-workbench.json")
    tutorial_sources = read_json(ANALYSIS / "tutorial-sources.json")
    exercise_paths = read_json(ANALYSIS / "tutorial-exercise-paths.json")
    corpus_bridges = read_json(ANALYSIS / "lesson-corpus-bridges.json")
    measurements = read_json(ANALYSIS / "latest-measurements-index.json")
    lesson_lab_index = read_json(ROOT / "lesson-labs/index.json") if exists("lesson-labs/index.json") else {"labs": []}
    lesson_lab_run = read_json(ROOT / "lesson-labs/run-report.json") if exists("lesson-labs/run-report.json") else {}
    comprehensive_plan = read_json(ROOT / "comprehensive-labs/plan.json") if exists("comprehensive-labs/plan.json") else {"labs": [], "coverage": {}}
    comprehensive_run = read_json(ROOT / "comprehensive-labs/run-report.json") if exists("comprehensive-labs/run-report.json") else {}
    kernel_plan = read_json(ROOT / "kernel-benchmarks/plan.json") if exists("kernel-benchmarks/plan.json") else {}
    kernel_report = read_json(ROOT / "kernel-benchmarks/reports/kernel-benchmark-report.json") if exists("kernel-benchmarks/reports/kernel-benchmark-report.json") else {}
    compiler_runtime = read_json(ROOT / "compiler-runtime-inspection/compiler-runtime-report.json") if exists("compiler-runtime-inspection/compiler-runtime-report.json") else {}
    tensor_core_gemm = read_json(ROOT / "tensor-core-gemm/tensor-core-gemm-report.json") if exists("tensor-core-gemm/tensor-core-gemm-report.json") else {}
    persistent_kernels = read_json(ROOT / "persistent-kernels/persistent-kernels-report.json") if exists("persistent-kernels/persistent-kernels-report.json") else {}
    parallel_primitives = read_json(ROOT / "parallel-primitives/parallel-primitives-report.json") if exists("parallel-primitives/parallel-primitives-report.json") else {}
    runtime_matrix = read_json(ROOT / "runtime-matrix/matrix.json") if exists("runtime-matrix/matrix.json") else {}
    profiler_report = read_json(ROOT / "profiler-evidence/reports/profiler-evidence-report.json") if exists("profiler-evidence/reports/profiler-evidence-report.json") else {}
    serving_report = read_json(ROOT / "serving-traces/reports/serving-trace-report.json") if exists("serving-traces/reports/serving-trace-report.json") else {}
    kv_cache = read_json(ROOT / "kv-cache-paged-attention/kv-cache-report.json") if exists("kv-cache-paged-attention/kv-cache-report.json") else {}
    attention_serving = read_json(ROOT / "attention-serving-stack/attention-serving-report.json") if exists("attention-serving-stack/attention-serving-report.json") else {}
    flash_attention_backward = read_json(ROOT / "flash-attention-backward/flash-attention-backward-report.json") if exists("flash-attention-backward/flash-attention-backward-report.json") else {}
    sparse_attention = read_json(ROOT / "sparse-attention-kernels/sparse-attention-report.json") if exists("sparse-attention-kernels/sparse-attention-report.json") else {}
    fused_training = read_json(ROOT / "fused-training-kernels/fused-training-report.json") if exists("fused-training-kernels/fused-training-report.json") else {}
    serving_engine_comparison = read_json(ROOT / "serving-engine-comparison/serving-engine-comparison.json") if exists("serving-engine-comparison/serving-engine-comparison.json") else {}
    speculative_decoding = read_json(ROOT / "speculative-decoding-serving/speculative-decoding-report.json") if exists("speculative-decoding-serving/speculative-decoding-report.json") else {}
    distributed_topology = read_json(ROOT / "distributed-topology/distributed-topology-plan.json") if exists("distributed-topology/distributed-topology-plan.json") else {}
    distributed_collectives = read_json(ROOT / "distributed-collectives/distributed-collectives-report.json") if exists("distributed-collectives/distributed-collectives-report.json") else {}
    distributed_training = read_json(ROOT / "distributed-training-optimizer/distributed-training-optimizer-report.json") if exists("distributed-training-optimizer/distributed-training-optimizer-report.json") else {}
    moe_routing = read_json(ROOT / "moe-routing-all-to-all/moe-routing-report.json") if exists("moe-routing-all-to-all/moe-routing-report.json") else {}
    hardware_capacity = read_json(ROOT / "hardware-capacity-planning/hardware-capacity-plan.json") if exists("hardware-capacity-planning/hardware-capacity-plan.json") else {}
    quantization = read_json(ROOT / "quantization-memory-formats/quantization-report.json") if exists("quantization-memory-formats/quantization-report.json") else {}
    numerical = read_json(ROOT / "numerical-reproducibility/numerical-reproducibility-report.json") if exists("numerical-reproducibility/numerical-reproducibility-report.json") else {}
    cuda_graphs = read_json(ROOT / "cuda-graphs-latency/cuda-graphs-latency-report.json") if exists("cuda-graphs-latency/cuda-graphs-latency-report.json") else {}
    multi_tenant_scheduling = read_json(ROOT / "multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json") if exists("multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json") else {}
    custom_op_report = read_json(ROOT / "custom-ops/reports/custom-op-report.json") if exists("custom-ops/reports/custom-op-report.json") else {}
    autotune_db = read_json(ROOT / "autotune-db/autotune-db.json") if exists("autotune-db/autotune-db.json") else {}
    model_report = read_json(ROOT / "model-integration/reports/tiny-transformer-report.json") if exists("model-integration/reports/tiny-transformer-report.json") else {}
    regression_ledger = read_json(ROOT / "regression-ledger/regression-ledger.json") if exists("regression-ledger/regression-ledger.json") else {}
    gpu_promotion = read_json(ROOT / "gpu-promotion/gpu-host-promotion-manifest.json") if exists("gpu-promotion/gpu-host-promotion-manifest.json") else {}
    gpu_promotion_suite = read_json(ROOT / "gpu-promotion/suite-run-report.json") if exists("gpu-promotion/suite-run-report.json") else {}
    gpu_import_lint = read_json(ROOT / "gpu-runs/import-lint-report.json") if exists("gpu-runs/import-lint-report.json") else {}
    gpu_runs = read_json(ROOT / "gpu-runs/gpu-run-report.json") if exists("gpu-runs/gpu-run-report.json") else {}
    gpu_provenance = read_json(ROOT / "gpu-provenance/gpu-provenance-report.json") if exists("gpu-provenance/gpu-provenance-report.json") else {}
    gpu_measurement_queue = read_json(ROOT / "gpu-measurement-queue/gpu-measurement-queue.json") if exists("gpu-measurement-queue/gpu-measurement-queue.json") else {}
    gpu_acceptance_logic = read_json(ROOT / "gpu-measurement-queue/acceptance-logic-report.json") if exists("gpu-measurement-queue/acceptance-logic-report.json") else {}
    gpu_host_preflight = read_json(ROOT / "gpu-handoff/gpu-host-preflight.json") if exists("gpu-handoff/gpu-host-preflight.json") else {}
    gpu_handoff = read_json(ROOT / "gpu-handoff/gpu-host-handoff.json") if exists("gpu-handoff/gpu-host-handoff.json") else {}
    assessment = read_json(ROOT / "assessment/question-bank.json") if exists("assessment/question-bank.json") else {}
    assessment_grading = read_json(ROOT / "assessment/grading-report.json") if exists("assessment/grading-report.json") else {}
    capstone_acceptance = read_json(ROOT / "capstone-acceptance/capstone-acceptance.json") if exists("capstone-acceptance/capstone-acceptance.json") else {}
    coverage = workbench["coverage"]

    lesson_pages = len(list((ROOT / "site").glob("lesson-[0-9][0-9][0-9].html")))
    lesson_lab_pages = len(list((ROOT / "site").glob("lesson-lab-*.html")))
    bridge_pages = len(list((ROOT / "site").glob("bridge-*.html")))
    lab_artifacts = list(LAB_ROOT.glob("**/out_*.json"))
    gpumode_lab_artifacts = [
        path
        for path in lab_artifacts
        if isinstance(read_json(path).get("source"), dict)
        and read_json(path).get("source", {}).get("gpumode_lab_id")
    ]

    caveat = (
        "CUDA/HIP/vLLM/Nsight/NCCL runtime throughput remains environment-gated on this machine; "
        "the artifacts record explicit skip/readiness rows instead of claiming unavailable accelerator measurements."
    )

    items = [
        evidence_item(
            "Ingest and maintain GPUMODE YouTube metadata/transcripts.",
            curriculum["lesson_count"] == len(transcript_index) and curriculum["transcript_count"] > 0,
            ["raw-material/youtube/transcript-index.json", "analysis/gpumode-curriculum.json"],
            {
                "videos": curriculum["lesson_count"],
                "available_transcripts": curriculum["transcript_count"],
                "missing_transcripts": len([row for row in transcript_index if row.get("transcript_status") != "available"]),
            },
        ),
        evidence_item(
            "Extract deterministic lesson intelligence.",
            len(intelligence) == curriculum["lesson_count"] and all(row.get("topics") and row.get("exercise_candidates") for row in intelligence),
            ["analysis/lesson-intelligence.json"],
            {"records": len(intelligence)},
        ),
        evidence_item(
            "Build prerequisite/topic graph and practical topic order.",
            graph["node_count"] >= curriculum["lesson_count"] and graph["edge_count"] >= curriculum["lesson_count"] * 3 and bool(graph.get("practical_topic_order")),
            ["analysis/curriculum-graph.json", "scripts/query_curriculum_graph.py"],
            {
                "nodes": graph["node_count"],
                "edges": graph["edge_count"],
                "top_topics": [row["topic"] for row in graph["practical_topic_order"][:5]],
            },
        ),
        evidence_item(
            "Connect GPUMODE lessons to AI-hardware corpus papers.",
            corpus_bridges["paper_count"] >= 100 and corpus_bridges["link_count"] >= 300,
            ["analysis/lesson-corpus-bridges.json", "scripts/query_corpus_bridge.py"],
            {
                "paper_bridges": corpus_bridges["paper_count"],
                "lesson_bridges": corpus_bridges["lesson_count"],
                "links": corpus_bridges["link_count"],
            },
        ),
        evidence_item(
            "Implement deeper runnable GPU systems labs with correctness checks.",
            coverage["implemented_labs"] >= 12 and measurements["passed_correctness"] >= 12,
            ["gpu-kernels-serving-lab/15-gpumode-coalescing", "gpu-kernels-serving-lab/26-gpumode-distributed-communication", "analysis/latest-measurements-index.json"],
            {
                "implemented_labs": coverage["implemented_labs"],
                "gpumode_lab_artifacts": len(gpumode_lab_artifacts),
                "correctness_passed": measurements["passed_correctness"],
            },
            caveat,
        ),
        evidence_item(
            "Generate measurement-backed lesson, bridge, lab, and workbench pages.",
            lesson_pages == curriculum["lesson_count"] and bridge_pages == coverage["profile_count"] and exists("site/workbench.html"),
            ["site/index.html", "site/workbench.html", "site/lesson-*.html", "site/bridge-*.html"],
            {
                "lesson_pages": lesson_pages,
                "bridge_pages": bridge_pages,
                "measurement_artifacts": measurements["artifact_count"],
            },
        ),
        evidence_item(
            "Identify and implement one generated lab scaffold for every GPUMODE lesson.",
            lesson_lab_index.get("generated_lab_count") == curriculum["lesson_count"]
            and lesson_lab_run.get("passed_contracts") == curriculum["lesson_count"]
            and lesson_lab_pages == curriculum["lesson_count"]
            and exists("site/lesson-labs.html"),
            ["LESSON-LAB-GOAL.md", "lesson-labs/index.json", "lesson-labs/run-report.json", "site/lesson-labs.html", "scripts/verify_lesson_labs.py"],
            {
                "lesson_labs": lesson_lab_index.get("generated_lab_count", 0),
                "lesson_lab_contracts_passed": lesson_lab_run.get("passed_contracts", 0),
                "lesson_lab_pages": lesson_lab_pages,
                "lessons_without_direct_project_before_generation": lesson_lab_index.get("lessons_without_direct_project_before_generation_count", 0),
            },
            "Generated lesson labs are local CPU-proxy implementations with explicit promotion tasks for real CUDA/Triton/HIP/JAX/serving-runtime follow-up on a GPU host.",
        ),
        evidence_item(
            "Plan and implement deliberate comprehensive labs that combine related lessons into real code programs.",
            comprehensive_plan.get("coverage", {}).get("covered_lessons") == curriculum["lesson_count"]
            and len(comprehensive_plan.get("labs", [])) >= 8
            and comprehensive_run.get("passed") == len(comprehensive_plan.get("labs", [])),
            ["comprehensive-labs/PLAN.md", "comprehensive-labs/gpumode_lab_suite", "comprehensive-labs/run-report.json", "scripts/verify_comprehensive_labs.py"],
            {
                "comprehensive_labs": len(comprehensive_plan.get("labs", [])),
                "covered_lessons": comprehensive_plan.get("coverage", {}).get("covered_lessons", 0),
                "passed_comprehensive_labs": comprehensive_run.get("passed", 0),
            },
            "Comprehensive labs run locally as Python implementations/models; GPU-specific promotion remains environment-gated.",
        ),
        evidence_item(
            "Provide a kernel benchmark harness with real CUDA/Triton source families and local correctness/timing reports.",
            kernel_report.get("failed") == 0
            and kernel_report.get("passed", 0) >= 14
            and kernel_plan.get("covered_lessons") == curriculum["lesson_count"]
            and exists("kernel-benchmarks/kernels/cuda/memory.cu")
            and exists("kernel-benchmarks/kernels/triton/matmul_mlp.py")
            and exists("site/kernel-benchmarks.html"),
            ["kernel-benchmarks/PLAN.md", "kernel-benchmarks/README.md", "kernel-benchmarks/kernels/cuda", "kernel-benchmarks/kernels/triton", "kernel-benchmarks/reports/kernel-benchmark-report.json", "site/kernel-benchmarks.html", "scripts/verify_kernel_benchmarks.py"],
            {
                "benchmarks": kernel_report.get("benchmark_count", 0),
                "passed": kernel_report.get("passed", 0),
                "covered_lessons": kernel_plan.get("covered_lessons", 0),
                "torch_device": kernel_report.get("accelerator_readiness", {}).get("torch_device", "unknown"),
                "nvcc": kernel_report.get("accelerator_readiness", {}).get("nvcc", False),
            },
            "CUDA/Triton source files are present; local benchmark execution uses the available PyTorch device and records missing accelerator tooling explicitly.",
        ),
        evidence_item(
            "Inspect compiler/runtime source features and promotion risks across CUDA, Triton, ROCm/HIP, and custom-op code.",
            compiler_runtime.get("status") == "inspection-ready"
            and compiler_runtime.get("source_count", 0) >= 10
            and {"cuda", "triton", "custom-op", "hip"}.issubset(set(compiler_runtime.get("groups", [])))
            and compiler_runtime.get("feature_counts", {}).get("launch_indexing", 0) > 0
            and exists("site/compiler-runtime-inspection.html"),
            ["compiler-runtime-inspection/compiler-runtime-report.json", "compiler-runtime-inspection/reports/compiler-runtime-report.md", "site/compiler-runtime-inspection.html", "scripts/run_compiler_runtime_inspection.py", "scripts/verify_compiler_runtime_inspection.py"],
            {
                "status": compiler_runtime.get("status", "missing"),
                "sources": compiler_runtime.get("source_count", 0),
                "groups": compiler_runtime.get("groups", []),
                "feature_counts": compiler_runtime.get("feature_counts", {}),
                "risk_counts": compiler_runtime.get("risk_counts", {}),
            },
            "Static source inspection is local evidence; PTX, Triton IR, LLVM, and profiler-counter validation remain GPU-host promotion work.",
        ),
        evidence_item(
            "Plan CUTLASS/CuTe tensor-core GEMM kernels with CTA, warp, MMA, pipeline, quantized operand, and fused epilogue constraints.",
            tensor_core_gemm.get("status") == "tensor-core-gemm-ready"
            and tensor_core_gemm.get("scenario_count", 0) >= 5
            and tensor_core_gemm.get("tensor_core_eligible_scenarios", 0) >= 5
            and tensor_core_gemm.get("fused_epilogue_scenarios", 0) >= 4
            and tensor_core_gemm.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/tensor-core-gemm.html"),
            ["tensor-core-gemm/tensor-core-gemm-report.json", "tensor-core-gemm/reports/tensor-core-gemm-report.md", "site/tensor-core-gemm.html", "scripts/run_tensor_core_gemm.py", "scripts/verify_tensor_core_gemm.py"],
            {
                "status": tensor_core_gemm.get("status", "missing"),
                "scenarios": tensor_core_gemm.get("scenario_count", 0),
                "tensor_core_eligible": tensor_core_gemm.get("tensor_core_eligible_scenarios", 0),
                "fused_epilogues": tensor_core_gemm.get("fused_epilogue_scenarios", 0),
                "source_facts": tensor_core_gemm.get("source_facts", {}),
            },
            "Local GEMM evidence is a design planner; final acceptance requires real CUTLASS/CuTe compilation, SASS checks for MMA instructions, and cuBLAS/Triton comparisons.",
        ),
        evidence_item(
            "Plan persistent Triton/CUDA kernels with residency, occupancy, launch amortization, L2 reuse, and producer/consumer constraints.",
            persistent_kernels.get("status") == "persistent-kernels-ready"
            and persistent_kernels.get("scenario_count", 0) >= 6
            and persistent_kernels.get("passed_scenarios", 0) >= 5
            and persistent_kernels.get("family_count", 0) >= 5
            and persistent_kernels.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/persistent-kernels.html"),
            ["persistent-kernels/persistent-kernels-report.json", "persistent-kernels/reports/persistent-kernels-report.md", "site/persistent-kernels.html", "scripts/run_persistent_kernels.py", "scripts/verify_persistent_kernels.py"],
            {
                "status": persistent_kernels.get("status", "missing"),
                "scenarios": persistent_kernels.get("scenario_count", 0),
                "passed": persistent_kernels.get("passed_scenarios", 0),
                "families": persistent_kernels.get("family_count", 0),
                "producer_consumer": persistent_kernels.get("producer_consumer_scenarios", 0),
            },
            "Local persistent-kernel evidence is a design model; final acceptance requires Nsight Compute occupancy, register, shared-memory, L2, DRAM, and launch-duration counters on a GPU host.",
        ),
        evidence_item(
            "Plan parallel primitives for reduction, scan, compaction, radix sort, histogram, and segmented reduction.",
            parallel_primitives.get("status") == "parallel-primitives-ready"
            and parallel_primitives.get("scenario_count", 0) >= 6
            and parallel_primitives.get("passed_scenarios", 0) >= 5
            and parallel_primitives.get("primitive_count", 0) >= 6
            and parallel_primitives.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/parallel-primitives.html"),
            ["parallel-primitives/parallel-primitives-report.json", "parallel-primitives/reports/parallel-primitives-report.md", "site/parallel-primitives.html", "scripts/run_parallel_primitives.py", "scripts/verify_parallel_primitives.py"],
            {
                "status": parallel_primitives.get("status", "missing"),
                "scenarios": parallel_primitives.get("scenario_count", 0),
                "passed": parallel_primitives.get("passed_scenarios", 0),
                "primitives": parallel_primitives.get("primitive_count", 0),
                "stable_order": parallel_primitives.get("stable_order_scenarios", 0),
            },
            "Local primitive evidence is a design model; final acceptance requires measured scan, reduction, histogram, compaction, sort, and segmented-reduction counters on a GPU host.",
        ),
        evidence_item(
            "Define runtime gates for CPU, CUDA, Triton, ROCm/HIP, profiler, and distributed machines.",
            runtime_matrix.get("profile_count", 0) >= 6
            and runtime_matrix.get("ready_profiles", 0) >= 1
            and exists("runtime-matrix/MATRIX.md")
            and exists("site/runtime-matrix.html"),
            ["runtime-matrix/matrix.json", "runtime-matrix/MATRIX.md", "site/runtime-matrix.html", "scripts/verify_runtime_matrix.py"],
            {
                "profiles": runtime_matrix.get("profile_count", 0),
                "ready": runtime_matrix.get("ready_profiles", 0),
                "fallback": runtime_matrix.get("fallback_profiles", 0),
                "blocked": runtime_matrix.get("blocked_profiles", 0),
                "torch_device": runtime_matrix.get("local_capabilities", {}).get("torch_device", "unknown"),
            },
            "Non-CPU profiles may be source-ready local fallback when CUDA, ROCm, profiler, or distributed runtime tools are not installed locally.",
        ),
        evidence_item(
            "Normalize profiler evidence from Nsight Compute, Nsight Systems, and rocprof-shaped exports.",
            profiler_report.get("row_count", 0) >= 9
            and profiler_report.get("source_count", 0) >= 3
            and {"memory-bandwidth", "launch-overhead", "communication"}.issubset(set(profiler_report.get("classification_counts", {})))
            and exists("site/profiler-evidence.html"),
            ["profiler-evidence/fixtures", "profiler-evidence/reports/profiler-evidence-report.json", "profiler-evidence/reports/profiler-evidence-report.md", "site/profiler-evidence.html", "scripts/verify_profiler_evidence.py"],
            {
                "rows": profiler_report.get("row_count", 0),
                "sources": profiler_report.get("source_count", 0),
                "classifications": sorted(profiler_report.get("classification_counts", {})),
            },
            "Fixtures are deterministic local stand-ins; GPU hosts should replace them with real ncu, nsys, or rocprof exports using the same schema.",
        ),
        evidence_item(
            "Replay LLM serving traces with TTFT, TPOT, throughput, prefix-cache, and KV-pressure metrics.",
            serving_report.get("trace_count", 0) >= 3
            and serving_report.get("failed_traces") == 0
            and set(serving_report.get("policy_ids", [])) == {"continuous-batching-prefix-cache", "static-batching"}
            and sum(row.get("prefix_cache_blocks_saved", 0) for row in serving_report.get("comparisons", [])) > 0
            and exists("site/serving-traces.html"),
            ["serving-traces/fixtures", "serving-traces/reports/serving-trace-report.json", "serving-traces/reports/serving-trace-report.md", "site/serving-traces.html", "scripts/verify_serving_traces.py"],
            {
                "traces": serving_report.get("trace_count", 0),
                "passed": serving_report.get("passed_traces", 0),
                "policies": serving_report.get("policy_ids", []),
                "prefix_cache_blocks_saved": sum(row.get("prefix_cache_blocks_saved", 0) for row in serving_report.get("comparisons", [])),
                "speedups": [row.get("throughput_speedup", 0) for row in serving_report.get("comparisons", [])],
            },
            "The replay is a deterministic local serving model; GPU hosts should feed real vLLM/SGLang/TGI traces into the same schema.",
        ),
        evidence_item(
            "Model KV-cache and PagedAttention allocator behavior for fragmentation, prefix reuse, eviction, and admission pressure.",
            kv_cache.get("status") == "kv-cache-ready"
            and kv_cache.get("scenario_count", 0) >= 5
            and kv_cache.get("passed_scenarios", 0) >= 4
            and kv_cache.get("total_prefix_blocks_reused", 0) > 0
            and kv_cache.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/kv-cache-paged-attention.html"),
            ["kv-cache-paged-attention/kv-cache-report.json", "kv-cache-paged-attention/reports/kv-cache-report.md", "site/kv-cache-paged-attention.html", "scripts/run_kv_cache_paged_attention.py", "scripts/verify_kv_cache_paged_attention.py"],
            {
                "status": kv_cache.get("status", "missing"),
                "scenarios": kv_cache.get("scenario_count", 0),
                "passed": kv_cache.get("passed_scenarios", 0),
                "prefix_blocks_reused": kv_cache.get("total_prefix_blocks_reused", 0),
                "source_facts": kv_cache.get("source_facts", {}),
            },
            "Local KV-cache evidence is an allocator model; real acceptance requires vLLM/SGLang block-table telemetry, GPU memory snapshots, and profiler traces.",
        ),
        evidence_item(
            "Connect FlashAttention online-softmax tiling to vLLM-style prefill/decode scheduling, KV reuse, CUDA Graph buckets, and profiler promotion.",
            attention_serving.get("status") == "attention-serving-ready"
            and attention_serving.get("scenario_count", 0) >= 5
            and attention_serving.get("passed_scenarios", 0) >= 4
            and attention_serving.get("total_prefix_blocks_reused", 0) > 0
            and attention_serving.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/attention-serving-stack.html"),
            ["attention-serving-stack/attention-serving-report.json", "attention-serving-stack/reports/attention-serving-report.md", "site/attention-serving-stack.html", "scripts/run_attention_serving_stack.py", "scripts/verify_attention_serving_stack.py"],
            {
                "status": attention_serving.get("status", "missing"),
                "scenarios": attention_serving.get("scenario_count", 0),
                "passed": attention_serving.get("passed_scenarios", 0),
                "prefix_blocks_reused": attention_serving.get("total_prefix_blocks_reused", 0),
                "source_facts": attention_serving.get("source_facts", {}),
            },
            "Local attention-serving evidence models kernel/serving accounting; real acceptance requires CUDA/Triton/ROCm attention kernel timing, nsys/ncu traces, and replayed serving requests.",
        ),
        evidence_item(
            "Model FlashAttention backward training kernels with dQ, dK, dV, dSoftmax, recompute, dropout, GQA, and gradient-error checks.",
            flash_attention_backward.get("status") == "flash-attention-backward-ready"
            and flash_attention_backward.get("scenario_count", 0) >= 6
            and flash_attention_backward.get("passed_scenarios", 0) >= 5
            and flash_attention_backward.get("dropout_scenarios", 0) >= 1
            and flash_attention_backward.get("grouped_query_scenarios", 0) >= 1
            and flash_attention_backward.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/flash-attention-backward.html"),
            ["flash-attention-backward/flash-attention-backward-report.json", "flash-attention-backward/reports/flash-attention-backward-report.md", "site/flash-attention-backward.html", "scripts/run_flash_attention_backward.py", "scripts/verify_flash_attention_backward.py"],
            {
                "status": flash_attention_backward.get("status", "missing"),
                "scenarios": flash_attention_backward.get("scenario_count", 0),
                "passed": flash_attention_backward.get("passed_scenarios", 0),
                "dropout": flash_attention_backward.get("dropout_scenarios", 0),
                "grouped_query": flash_attention_backward.get("grouped_query_scenarios", 0),
                "source_facts": flash_attention_backward.get("source_facts", {}),
            },
            "Local FlashAttention backward evidence is an analytical training-kernel model; real acceptance requires CUDA/Triton backward kernels, gradient comparisons, and ncu/nsys training-step counters on a GPU host.",
        ),
        evidence_item(
            "Model sparse and ragged attention kernels for block-sparse, sliding-window, dilated, neighborhood, top-k, metadata, load-balance, decode, and backward paths.",
            sparse_attention.get("status") == "sparse-attention-ready"
            and sparse_attention.get("scenario_count", 0) >= 6
            and sparse_attention.get("passed_scenarios", 0) >= 5
            and sparse_attention.get("pattern_count", 0) >= 6
            and sparse_attention.get("ragged_scenarios", 0) >= 1
            and sparse_attention.get("backward_scenarios", 0) >= 4
            and sparse_attention.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/sparse-attention-kernels.html"),
            ["sparse-attention-kernels/sparse-attention-report.json", "sparse-attention-kernels/reports/sparse-attention-report.md", "site/sparse-attention-kernels.html", "scripts/run_sparse_attention_kernels.py", "scripts/verify_sparse_attention_kernels.py"],
            {
                "status": sparse_attention.get("status", "missing"),
                "scenarios": sparse_attention.get("scenario_count", 0),
                "passed": sparse_attention.get("passed_scenarios", 0),
                "patterns": sparse_attention.get("pattern_count", 0),
                "ragged": sparse_attention.get("ragged_scenarios", 0),
                "backward": sparse_attention.get("backward_scenarios", 0),
                "source_facts": sparse_attention.get("source_facts", {}),
            },
            "Local sparse attention evidence is an analytical kernel model; real acceptance requires measured block-sparse, ragged-decode, sparse-backward, metadata-build, and load-balance profiler evidence on a GPU host.",
        ),
        evidence_item(
            "Model fused LLM training kernels for RMSNorm/residual backward, SwiGLU MLP fusion, cross-entropy/z-loss, multi-tensor AdamW, grad clipping/unscale, dropout/residual/norm, and checkpoint-safe fusion.",
            fused_training.get("status") == "fused-training-ready"
            and fused_training.get("scenario_count", 0) >= 6
            and fused_training.get("passed_scenarios", 0) >= 5
            and fused_training.get("family_count", 0) >= 5
            and fused_training.get("backward_scenarios", 0) >= 4
            and fused_training.get("optimizer_state_scenarios", 0) >= 2
            and fused_training.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/fused-training-kernels.html"),
            ["fused-training-kernels/fused-training-report.json", "fused-training-kernels/reports/fused-training-report.md", "site/fused-training-kernels.html", "scripts/run_fused_training_kernels.py", "scripts/verify_fused_training_kernels.py"],
            {
                "status": fused_training.get("status", "missing"),
                "scenarios": fused_training.get("scenario_count", 0),
                "passed": fused_training.get("passed_scenarios", 0),
                "families": fused_training.get("family_count", 0),
                "backward": fused_training.get("backward_scenarios", 0),
                "optimizer_state": fused_training.get("optimizer_state_scenarios", 0),
                "source_facts": fused_training.get("source_facts", {}),
            },
            "Local fused training evidence is an analytical kernel model; real acceptance requires measured CUDA/Triton fused norm, MLP, loss, optimizer, grad-scale, and checkpoint-step profiler evidence on a GPU host.",
        ),
        evidence_item(
            "Compare production inference engines across vLLM, Hugging Face TGI, SGLang, TensorRT-LLM, and HF Transformers scenarios.",
            serving_engine_comparison.get("status") == "comparison-ready"
            and serving_engine_comparison.get("engine_count", 0) >= 5
            and serving_engine_comparison.get("scenario_count", 0) >= 5
            and {"vllm", "tgi", "sglang", "tensorrt-llm", "hf-transformers"}.issubset(set(serving_engine_comparison.get("engine_ids", [])))
            and exists("site/serving-engine-comparison.html"),
            ["serving-engine-comparison/serving-engine-comparison.json", "serving-engine-comparison/reports/serving-engine-comparison.md", "site/serving-engine-comparison.html", "scripts/run_serving_engine_comparison.py", "scripts/verify_serving_engine_comparison.py"],
            {
                "status": serving_engine_comparison.get("status", "missing"),
                "engines": serving_engine_comparison.get("engine_count", 0),
                "scenarios": serving_engine_comparison.get("scenario_count", 0),
                "engine_wins": serving_engine_comparison.get("engine_wins", {}),
            },
            "Current engine scores are deterministic local estimates derived from replay traces; production acceptance still requires measured GPU-host serving benchmarks.",
        ),
        evidence_item(
            "Model speculative decoding serving with draft/target verification, acceptance-rate gates, rollback pressure, wasted draft tokens, KV commits, TTFT/TPOT, throughput, and scheduler policy.",
            speculative_decoding.get("status") == "speculative-decoding-ready"
            and speculative_decoding.get("scenario_count", 0) >= 6
            and speculative_decoding.get("passed_scenarios", 0) >= 4
            and speculative_decoding.get("engine_count", 0) >= 4
            and speculative_decoding.get("scheduler_policy_count", 0) >= 2
            and speculative_decoding.get("min_acceptance_rate", 1.0) < 0.50
            and speculative_decoding.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/speculative-decoding-serving.html"),
            ["speculative-decoding-serving/speculative-decoding-report.json", "speculative-decoding-serving/reports/speculative-decoding-report.md", "site/speculative-decoding-serving.html", "scripts/run_speculative_decoding_serving.py", "scripts/verify_speculative_decoding_serving.py"],
            {
                "status": speculative_decoding.get("status", "missing"),
                "scenarios": speculative_decoding.get("scenario_count", 0),
                "passed": speculative_decoding.get("passed_scenarios", 0),
                "review": speculative_decoding.get("review_scenarios", 0),
                "engines": speculative_decoding.get("engine_count", 0),
                "policies": speculative_decoding.get("scheduler_policy_count", 0),
                "min_acceptance": speculative_decoding.get("min_acceptance_rate", 0),
                "source_facts": speculative_decoding.get("source_facts", {}),
            },
            "Local speculative decoding evidence is a deterministic scheduler model; real acceptance requires Colab/GPU-host draft and target model traces, KV commit telemetry, rollback counts, and profiler evidence.",
        ),
        evidence_item(
            "Plan multi-GPU topology and parallelism choices for serving and training workloads.",
            distributed_topology.get("status") == "topology-plan-ready"
            and distributed_topology.get("topology_count", 0) >= 5
            and distributed_topology.get("workload_count", 0) >= 5
            and distributed_topology.get("candidate_count", 0) > 0
            and exists("site/distributed-topology.html"),
            ["distributed-topology/distributed-topology-plan.json", "distributed-topology/reports/distributed-topology-plan.md", "site/distributed-topology.html", "scripts/run_distributed_topology.py", "scripts/verify_distributed_topology.py"],
            {
                "status": distributed_topology.get("status", "missing"),
                "topologies": distributed_topology.get("topology_count", 0),
                "workloads": distributed_topology.get("workload_count", 0),
                "candidates": distributed_topology.get("candidate_count", 0),
                "rejected": distributed_topology.get("rejected_count", 0),
            },
            "Topology and parallelism estimates are source-ready locally; final acceptance requires measured NCCL/RCCL bandwidth on the selected GPU fabric.",
        ),
        evidence_item(
            "Model distributed collective algorithms for all-reduce, reduce-scatter, all-gather, all-to-all, broadcast, overlap, and backend portability.",
            distributed_collectives.get("status") == "distributed-collectives-ready"
            and distributed_collectives.get("scenario_count", 0) >= 6
            and distributed_collectives.get("collective_count", 0) >= 5
            and distributed_collectives.get("passed_scenarios", 0) >= 5
            and exists("site/distributed-collectives.html"),
            ["distributed-collectives/distributed-collectives-report.json", "distributed-collectives/reports/distributed-collectives-report.md", "site/distributed-collectives.html", "scripts/run_distributed_collectives.py", "scripts/verify_distributed_collectives.py"],
            {
                "status": distributed_collectives.get("status", "missing"),
                "scenarios": distributed_collectives.get("scenario_count", 0),
                "collectives": distributed_collectives.get("collective_count", 0),
                "passed": distributed_collectives.get("passed_scenarios", 0),
                "backends": distributed_collectives.get("backends", []),
            },
            "Collective timing is deterministic locally; final acceptance needs measured NCCL/RCCL/NVSHMEM bandwidth and overlap traces on accelerator fabric.",
        ),
        evidence_item(
            "Model distributed training optimizer choices across DDP, ZeRO, FSDP, checkpointing, communication overlap, and pipeline bubbles.",
            distributed_training.get("status") == "training-optimizer-ready"
            and distributed_training.get("scenario_count", 0) >= 6
            and distributed_training.get("passed_scenarios", 0) >= 4
            and distributed_training.get("strategy_count", 0) >= 5
            and exists("site/distributed-training-optimizer.html"),
            ["distributed-training-optimizer/distributed-training-optimizer-report.json", "distributed-training-optimizer/reports/distributed-training-optimizer-report.md", "site/distributed-training-optimizer.html", "scripts/run_distributed_training_optimizer.py", "scripts/verify_distributed_training_optimizer.py"],
            {
                "status": distributed_training.get("status", "missing"),
                "scenarios": distributed_training.get("scenario_count", 0),
                "passed": distributed_training.get("passed_scenarios", 0),
                "strategies": distributed_training.get("strategy_count", 0),
                "checkpointed": distributed_training.get("checkpointed_scenarios", 0),
            },
            "Training optimizer estimates are source-ready locally; final acceptance needs measured FSDP/ZeRO step time, memory peak, and overlap traces.",
        ),
        evidence_item(
            "Model MoE routing and all-to-all behavior for expert load balance, capacity drops, communication payload, and topology-sensitive bottlenecks.",
            moe_routing.get("status") == "moe-routing-ready"
            and moe_routing.get("scenario_count", 0) >= 5
            and moe_routing.get("passed_scenarios", 0) >= 3
            and moe_routing.get("tuning_required_scenarios", 0) >= 1
            and moe_routing.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/moe-routing-all-to-all.html"),
            ["moe-routing-all-to-all/moe-routing-report.json", "moe-routing-all-to-all/reports/moe-routing-report.md", "site/moe-routing-all-to-all.html", "scripts/run_moe_routing_all_to_all.py", "scripts/verify_moe_routing_all_to_all.py"],
            {
                "status": moe_routing.get("status", "missing"),
                "scenarios": moe_routing.get("scenario_count", 0),
                "passed": moe_routing.get("passed_scenarios", 0),
                "tuning_required": moe_routing.get("tuning_required_scenarios", 0),
                "source_facts": moe_routing.get("source_facts", {}),
            },
            "Local MoE evidence is a deterministic routing and communication model; real acceptance requires all-to-all traces, expert-load histograms, and per-expert GPU timings.",
        ),
        evidence_item(
            "Plan hardware capacity, memory headroom, bottleneck class, power, and cost for kernel, serving, and training workloads.",
            hardware_capacity.get("status") == "capacity-plan-ready"
            and hardware_capacity.get("profile_count", 0) >= 5
            and hardware_capacity.get("workload_count", 0) >= 5
            and hardware_capacity.get("recommendation_count") == hardware_capacity.get("workload_count")
            and exists("site/hardware-capacity.html"),
            ["hardware-capacity-planning/hardware-capacity-plan.json", "hardware-capacity-planning/reports/hardware-capacity-plan.md", "site/hardware-capacity.html", "scripts/run_hardware_capacity_plan.py", "scripts/verify_hardware_capacity_plan.py"],
            {
                "status": hardware_capacity.get("status", "missing"),
                "profiles": hardware_capacity.get("profile_count", 0),
                "workloads": hardware_capacity.get("workload_count", 0),
                "recommendations": hardware_capacity.get("recommendation_count", 0),
                "rejected": hardware_capacity.get("rejected_count", 0),
                "source_facts": hardware_capacity.get("source_facts", {}),
            },
            "Capacity, power, cost, and throughput are modeled locally; real production claims require GPU-host telemetry for memory use, power draw, tokens/sec, and profiler counters.",
        ),
        evidence_item(
            "Evaluate quantization and memory-format tradeoffs for compression, accuracy drift, dequantization cost, serving fit, and GPU promotion.",
            quantization.get("status") == "quantization-ready"
            and quantization.get("format_count", 0) >= 7
            and quantization.get("passed_format_count", 0) >= 4
            and quantization.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/quantization-memory-formats.html"),
            ["quantization-memory-formats/quantization-report.json", "quantization-memory-formats/reports/quantization-report.md", "site/quantization-memory-formats.html", "scripts/run_quantization_memory_formats.py", "scripts/verify_quantization_memory_formats.py"],
            {
                "status": quantization.get("status", "missing"),
                "formats": quantization.get("format_count", 0),
                "passed": quantization.get("passed_format_count", 0),
                "calibration_needed": quantization.get("calibration_needed_count", 0),
                "source_facts": quantization.get("source_facts", {}),
            },
            "Local quantization evidence is a CPU simulation; real throughput claims require fused GPU dequantization kernels, low-precision tensor-core paths, and measured serving traces.",
        ),
        evidence_item(
            "Define numerical reproducibility and precision drift tolerance policy across deterministic, fast-math, low-precision, and reduction-order cases.",
            numerical.get("status") == "reproducibility-ready"
            and numerical.get("scenario_count", 0) >= 5
            and numerical.get("passed_scenarios", 0) >= 4
            and numerical.get("tolerance_review_scenarios", 0) >= 1
            and numerical.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/numerical-reproducibility.html"),
            ["numerical-reproducibility/numerical-reproducibility-report.json", "numerical-reproducibility/reports/numerical-reproducibility-report.md", "site/numerical-reproducibility.html", "scripts/run_numerical_reproducibility.py", "scripts/verify_numerical_reproducibility.py"],
            {
                "status": numerical.get("status", "missing"),
                "scenarios": numerical.get("scenario_count", 0),
                "passed": numerical.get("passed_scenarios", 0),
                "tolerance_reviews": numerical.get("tolerance_review_scenarios", 0),
                "source_facts": numerical.get("source_facts", {}),
            },
            "Local reproducibility evidence is CPU-based; real acceptance requires repeated CUDA, Triton, and ROCm runs with deterministic flags and model-level drift checks.",
        ),
        evidence_item(
            "Model CUDA Graph capture eligibility and latency stabilization for launch-overhead-bound serving paths.",
            cuda_graphs.get("status") == "cuda-graphs-ready"
            and cuda_graphs.get("scenario_count", 0) >= 5
            and cuda_graphs.get("capture_ready_count", 0) >= 3
            and cuda_graphs.get("fallback_required_count", 0) >= 2
            and exists("site/cuda-graphs-latency.html"),
            ["cuda-graphs-latency/cuda-graphs-latency-report.json", "cuda-graphs-latency/reports/cuda-graphs-latency-report.md", "site/cuda-graphs-latency.html", "scripts/run_cuda_graphs_latency.py", "scripts/verify_cuda_graphs_latency.py"],
            {
                "status": cuda_graphs.get("status", "missing"),
                "scenarios": cuda_graphs.get("scenario_count", 0),
                "capture_ready": cuda_graphs.get("capture_ready_count", 0),
                "fallback_required": cuda_graphs.get("fallback_required_count", 0),
                "source_facts": cuda_graphs.get("source_facts", {}),
            },
            "Local CUDA Graphs evidence is a deterministic latency model; real acceptance requires CUDA graph capture/replay traces from Nsight Systems and kernel counters from Nsight Compute.",
        ),
        evidence_item(
            "Plan multi-tenant GPU scheduling and isolation for serving/training workloads using MIG/MPS/Kubernetes-style placement, fairness, and SLO evidence.",
            multi_tenant_scheduling.get("status") == "scheduling-ready"
            and multi_tenant_scheduling.get("policy_count", 0) >= 4
            and multi_tenant_scheduling.get("tenant_count", 0) >= 5
            and multi_tenant_scheduling.get("accepted_count", 0) >= 4
            and multi_tenant_scheduling.get("gpu_host_promotion", {}).get("required") is True
            and exists("site/multi-tenant-scheduling.html"),
            ["multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json", "multi-tenant-gpu-scheduling/reports/multi-tenant-scheduling-report.md", "site/multi-tenant-scheduling.html", "scripts/run_multi_tenant_gpu_scheduling.py", "scripts/verify_multi_tenant_gpu_scheduling.py"],
            {
                "status": multi_tenant_scheduling.get("status", "missing"),
                "policies": multi_tenant_scheduling.get("policy_count", 0),
                "tenants": multi_tenant_scheduling.get("tenant_count", 0),
                "accepted": multi_tenant_scheduling.get("accepted_count", 0),
                "recommended_policy": multi_tenant_scheduling.get("recommended_policy", "missing"),
                "source_facts": multi_tenant_scheduling.get("source_facts", {}),
            },
            "Local scheduling evidence is a deterministic placement model; real acceptance requires Kubernetes device-plugin inventory, MIG/MPS telemetry, and measured per-tenant latency/throughput.",
        ),
        evidence_item(
            "Integrate kernel work into a PyTorch custom operator with forward/backward checks and CUDA source promotion.",
            custom_op_report.get("case_count", 0) >= 4
            and custom_op_report.get("failed") == 0
            and custom_op_report.get("operator") == "fused_bias_gelu_residual"
            and exists("custom-ops/csrc/fused_bias_gelu_residual.cpp")
            and exists("custom-ops/csrc/fused_bias_gelu_residual_kernel.cu")
            and exists("site/custom-ops.html"),
            ["custom-ops/custom_ops/fused_bias_gelu_residual.py", "custom-ops/csrc", "custom-ops/reports/custom-op-report.json", "custom-ops/reports/custom-op-report.md", "site/custom-ops.html", "scripts/verify_custom_ops.py"],
            {
                "operator": custom_op_report.get("operator", ""),
                "cases": custom_op_report.get("case_count", 0),
                "passed": custom_op_report.get("passed", 0),
                "compiled_extension_status": custom_op_report.get("accelerator_readiness", {}).get("compiled_extension_status", "unknown"),
                "torch_device": custom_op_report.get("accelerator_readiness", {}).get("torch_device", "unknown"),
            },
            "The compiled CUDA extension path is source-ready on this machine because local accelerator tooling is unavailable; CPU autograd verifies the numerical contract.",
        ),
        evidence_item(
            "Persist autotuning records that select starting configs for kernel families and model-integrated custom ops.",
            autotune_db.get("record_count", 0) >= 18
            and {"memory", "reduction", "normalization", "matmul", "fusion", "custom-op"}.issubset(set(autotune_db.get("families", [])))
            and all(row.get("selected", {}).get("estimated_speedup_vs_measured", 0) >= 1.0 for row in autotune_db.get("records", []))
            and exists("site/autotune-db.html"),
            ["autotune-db/autotune-db.json", "autotune-db/reports/autotune-report.md", "site/autotune-db.html", "scripts/build_autotune_db.py", "scripts/verify_autotune_db.py"],
            {
                "records": autotune_db.get("record_count", 0),
                "families": autotune_db.get("families", []),
                "source_reports": autotune_db.get("source_reports", []),
            },
            "The current selections are benchmark-derived local starting points; GPU hosts should refresh the same schema with measured accelerator sweeps.",
        ),
        evidence_item(
            "Run a model-shaped transformer block that uses custom-op fusion and autotune selections.",
            model_report.get("case_count", 0) >= 3
            and model_report.get("failed") == 0
            and model_report.get("model") == "tiny-causal-transformer-block"
            and model_report.get("uses_custom_op") == "fused_bias_gelu_residual"
            and {"matmul", "normalization", "custom-op"}.issubset(set(model_report.get("selected_tuning_summary", {})))
            and exists("site/model-integration.html"),
            ["model-integration/model_integration/tiny_transformer.py", "model-integration/reports/tiny-transformer-report.json", "model-integration/reports/tiny-transformer-report.md", "site/model-integration.html", "scripts/verify_model_integration.py"],
            {
                "model": model_report.get("model", ""),
                "cases": model_report.get("case_count", 0),
                "passed": model_report.get("passed", 0),
                "uses_custom_op": model_report.get("uses_custom_op", ""),
                "selected_tuning": model_report.get("selected_tuning_summary", {}),
            },
            "The model path runs locally in PyTorch CPU mode; accelerator-backed operator replacement is the GPU-host promotion step.",
        ),
        evidence_item(
            "Track regression metrics across kernel, custom-op, autotune, model, and serving layers.",
            regression_ledger.get("metric_count", 0) >= 70
            and regression_ledger.get("failed") == 0
            and {"kernel", "custom_op", "autotune", "model", "serving"}.issubset(set(regression_ledger.get("source_reports", {})))
            and exists("site/regression-ledger.html"),
            ["regression-ledger/regression-ledger.json", "regression-ledger/reports/regression-ledger.md", "site/regression-ledger.html", "scripts/build_regression_ledger.py", "scripts/verify_regression_ledger.py"],
            {
                "metrics": regression_ledger.get("metric_count", 0),
                "passed": regression_ledger.get("passed", 0),
                "warnings": regression_ledger.get("warnings", 0),
                "failed": regression_ledger.get("failed", 0),
                "source_reports": regression_ledger.get("source_reports", {}),
            },
            "Current thresholds compare against local generated metrics; GPU-host runs should persist their own measured baseline history.",
        ),
        evidence_item(
            "Generate an ordered GPU-host promotion manifest for accelerator-only validation.",
            gpu_promotion.get("step_count", 0) >= 9
            and gpu_promotion.get("ready_on_gpu_host", 0) >= 4
            and {"cuda-kernel-compile", "triton-kernel-sweep", "profiler-capture", "full-gpu-regression"}.issubset({row.get("id") for row in gpu_promotion.get("steps", [])})
            and exists("site/gpu-promotion.html"),
            ["gpu-promotion/gpu-host-promotion-manifest.json", "gpu-promotion/reports/gpu-host-promotion-runbook.md", "site/gpu-promotion.html", "scripts/build_gpu_promotion.py", "scripts/verify_gpu_promotion.py"],
            {
                "steps": gpu_promotion.get("step_count", 0),
                "ready_on_this_host": gpu_promotion.get("ready_on_this_host", 0),
                "ready_on_gpu_host": gpu_promotion.get("ready_on_gpu_host", 0),
                "local_capabilities": gpu_promotion.get("local_capabilities", {}),
            },
            "This host lacks CUDA/ROCm/profiler hardware tools, so accelerator-only steps are intentionally marked ready-on-gpu-host.",
        ),
        evidence_item(
            "Plan the GPU-host promotion commands as a dry-run-safe executable suite.",
            gpu_promotion_suite.get("status") == "dry-run-ready"
            and gpu_promotion_suite.get("command_count", 0) >= 20
            and gpu_promotion_suite.get("step_count", 0) >= 9
            and exists("site/gpu-promotion-suite.html"),
            ["gpu-promotion/suite-run-report.json", "gpu-promotion/reports/suite-run-report.md", "site/gpu-promotion-suite.html", "scripts/run_gpu_promotion_suite.py", "scripts/verify_gpu_promotion_suite.py"],
            {
                "commands": gpu_promotion_suite.get("command_count", 0),
                "steps": gpu_promotion_suite.get("step_count", 0),
                "planned": gpu_promotion_suite.get("planned", 0),
                "skipped": gpu_promotion_suite.get("skipped", 0),
                "status": gpu_promotion_suite.get("status", "missing"),
            },
            "The local suite is a dry-run command plan; use --execute on a GPU host after reviewing placeholder commands.",
        ),
        evidence_item(
            "Import GPU-host run evidence and link it to CUDA, Triton, ROCm/HIP, profiler, serving, distributed, and regression promotion steps.",
            gpu_runs.get("status") == "import-ready"
            and gpu_runs.get("coverage", {}).get("run_count", 0) >= 2
            and gpu_runs.get("coverage", {}).get("vendor_count", 0) >= 2
            and gpu_runs.get("coverage", {}).get("promotion_step_count", 0) >= 9
            and exists("site/gpu-runs.html"),
            ["gpu-runs/fixtures", "gpu-runs/gpu-run-report.json", "gpu-runs/reports/gpu-run-report.md", "site/gpu-runs.html", "scripts/verify_gpu_runs.py"],
            {
                "runs": gpu_runs.get("coverage", {}).get("run_count", 0),
                "vendors": gpu_runs.get("coverage", {}).get("vendors", []),
                "promotion_steps": gpu_runs.get("coverage", {}).get("promotion_step_count", 0),
                "status": gpu_runs.get("status", "missing"),
            },
            "Current fixtures define the import contract; real GPU hosts should replace these rows with measured A100/H100/MI300 evidence.",
        ),
        evidence_item(
            "Lint GPU run fixtures and imports before accepting accelerator evidence.",
            gpu_import_lint.get("status") == "lint-clean"
            and gpu_import_lint.get("error_count", 1) == 0
            and gpu_import_lint.get("fixture_count", 0) >= 2
            and gpu_import_lint.get("import_count", 0) >= 1
            and exists("site/gpu-import-lint.html"),
            ["gpu-runs/import-lint-report.json", "gpu-runs/reports/import-lint-report.md", "site/gpu-import-lint.html", "scripts/lint_gpu_run_imports.py"],
            {
                "status": gpu_import_lint.get("status", "missing"),
                "files": gpu_import_lint.get("file_count", 0),
                "fixtures": gpu_import_lint.get("fixture_count", 0),
                "imports": gpu_import_lint.get("import_count", 0),
                "errors": gpu_import_lint.get("error_count", 0),
                "warnings": gpu_import_lint.get("warning_count", 0),
            },
        ),
        evidence_item(
            "Separate sample fixtures, host-collected smoke runs, and real measured GPU evidence provenance.",
            gpu_provenance.get("status") == "provenance-clear"
            and gpu_provenance.get("sample_run_count", 0) >= 2
            and gpu_provenance.get("host_collected_run_count", 0) >= 1
            and gpu_provenance.get("rows_with_provenance") == gpu_provenance.get("row_count")
            and exists("site/gpu-provenance.html"),
            ["gpu-provenance/gpu-provenance-report.json", "gpu-provenance/reports/gpu-provenance-report.md", "site/gpu-provenance.html", "scripts/verify_gpu_provenance.py"],
            {
                "status": gpu_provenance.get("status", "missing"),
                "real_gpu_evidence_status": gpu_provenance.get("real_gpu_evidence_status", "missing"),
                "measured_runs": gpu_provenance.get("measured_run_count", 0),
                "sample_runs": gpu_provenance.get("sample_run_count", 0),
                "host_collected_runs": gpu_provenance.get("host_collected_run_count", 0),
            },
            "This host has no real measured GPU imports yet; sample fixtures remain schema examples only.",
        ),
        evidence_item(
            "Define per-step GPU measurement contracts with host class, metrics, thresholds, and queued/measured status.",
            gpu_measurement_queue.get("status") == "queue-ready"
            and gpu_measurement_queue.get("task_count", 0) >= 9
            and all(task.get("has_metric_contract") for task in gpu_measurement_queue.get("tasks", []))
            and exists("site/gpu-measurement-queue.html"),
            ["gpu-measurement-queue/gpu-measurement-queue.json", "gpu-measurement-queue/reports/gpu-measurement-queue.md", "site/gpu-measurement-queue.html", "scripts/verify_gpu_measurement_queue.py"],
            {
                "status": gpu_measurement_queue.get("status", "missing"),
                "tasks": gpu_measurement_queue.get("task_count", 0),
                "queued": gpu_measurement_queue.get("queued_task_count", 0),
                "measured": gpu_measurement_queue.get("measured_task_count", 0),
                "accepted": gpu_measurement_queue.get("accepted_task_count", 0),
                "failed_measured": gpu_measurement_queue.get("failed_measured_task_count", 0),
                "real_measured_completion": gpu_measurement_queue.get("real_measured_completion", False),
            },
            "Measurement contracts are ready locally; real measured completion still requires accelerator-host imports.",
        ),
        evidence_item(
            "Regression-test GPU measurement acceptance logic against canonical good and bad metric rows.",
            gpu_acceptance_logic.get("status") == "passed"
            and gpu_acceptance_logic.get("accepted_good_cases", 0) >= 9
            and gpu_acceptance_logic.get("rejected_bad_cases", 0) >= 9
            and exists("site/gpu-acceptance-logic.html"),
            ["gpu-measurement-queue/acceptance-logic-report.json", "gpu-measurement-queue/reports/acceptance-logic-report.md", "site/gpu-acceptance-logic.html", "scripts/verify_gpu_acceptance_logic.py"],
            {
                "status": gpu_acceptance_logic.get("status", "missing"),
                "cases": gpu_acceptance_logic.get("case_count", 0),
                "accepted_good": gpu_acceptance_logic.get("accepted_good_cases", 0),
                "rejected_bad": gpu_acceptance_logic.get("rejected_bad_cases", 0),
            },
        ),
        evidence_item(
            "Run GPU-host preflight before accelerator promotion execution.",
            gpu_host_preflight.get("status") == "preflight-complete"
            and gpu_host_preflight.get("step_count", 0) >= 9
            and gpu_host_preflight.get("runnable_step_count", 0) + gpu_host_preflight.get("blocked_step_count", 0) == gpu_host_preflight.get("step_count", -1)
            and exists("site/gpu-host-preflight.html"),
            ["gpu-handoff/gpu-host-preflight.json", "gpu-handoff/reports/gpu-host-preflight.md", "site/gpu-host-preflight.html", "scripts/run_gpu_host_preflight.py", "scripts/verify_gpu_host_preflight.py"],
            {
                "status": gpu_host_preflight.get("status", "missing"),
                "accelerator_ready": gpu_host_preflight.get("accelerator_ready", False),
                "steps": gpu_host_preflight.get("step_count", 0),
                "runnable": gpu_host_preflight.get("runnable_step_count", 0),
                "blocked": gpu_host_preflight.get("blocked_step_count", 0),
            },
            "This host is CPU-only for accelerator tooling; the preflight report records blocked GPU promotion steps instead of treating them as hidden failures.",
        ),
        evidence_item(
            "Package a portable GPU-host handoff bundle for accelerator execution and evidence collection.",
            gpu_handoff.get("status") == "ready"
            and gpu_handoff.get("suite_summary", {}).get("command_count", 0) >= 20
            and len(gpu_handoff.get("bundle_files", [])) >= 8
            and exists("site/gpu-handoff.html"),
            ["gpu-handoff/gpu-host-handoff.json", "gpu-handoff/reports/gpu-host-handoff.md", "gpu-handoff/bin/run-gpu-host-handoff.sh", "site/gpu-handoff.html", "scripts/verify_gpu_handoff.py"],
            {
                "status": gpu_handoff.get("status", "missing"),
                "commands": gpu_handoff.get("suite_summary", {}).get("command_count", 0),
                "bundle_files": len(gpu_handoff.get("bundle_files", [])),
                "entrypoint": gpu_handoff.get("entrypoint", ""),
            },
            "The handoff is locally validated; execute mode still requires a real GPU host.",
        ),
        evidence_item(
            "Generate a concept exam and practical task bank for the full GPUMODE curriculum stack.",
            assessment.get("status") == "ready"
            and assessment.get("concept_question_count", 0) >= 10
            and assessment.get("practical_task_count", 0) >= 10
            and exists("site/assessment.html"),
            ["assessment/question-bank.json", "assessment/reports/assessment-report.md", "site/assessment.html", "scripts/verify_assessment.py"],
            {
                "concept_questions": assessment.get("concept_question_count", 0),
                "practical_tasks": assessment.get("practical_task_count", 0),
                "total_points": assessment.get("total_points", 0),
                "tutorial_providers": assessment.get("tutorial_provider_count", 0),
            },
            "The bank grades expected reasoning and artifact evidence; hands-on GPU throughput answers still require GPU-host promotion.",
        ),
        evidence_item(
            "Score the assessment bank against current generated artifact evidence.",
            assessment_grading.get("status") == "passed"
            and assessment_grading.get("score") == assessment_grading.get("max_score")
            and assessment_grading.get("practical_count", 0) >= 12
            and exists("site/assessment-grading.html"),
            ["assessment/grading-report.json", "assessment/reports/grading-report.md", "site/assessment-grading.html", "scripts/grade_assessment.py", "scripts/verify_assessment_grading.py"],
            {
                "score": assessment_grading.get("score", 0),
                "max_score": assessment_grading.get("max_score", 0),
                "concept_count": assessment_grading.get("concept_count", 0),
                "practical_count": assessment_grading.get("practical_count", 0),
                "failed_count": assessment_grading.get("failed_count", 0),
            },
            "Concept checks are graded for answer-key/source readiness; practical tasks are graded against current generated artifacts.",
        ),
        evidence_item(
            "Grade the complete curriculum as a portfolio capstone with a scored acceptance rubric.",
            capstone_acceptance.get("criteria_count", 0) >= 10
            and capstone_acceptance.get("max_score", 0) >= 100
            and capstone_acceptance.get("score", -1) <= capstone_acceptance.get("max_score", 0)
            and capstone_acceptance.get("status") in {"accepted-with-runtime-caveats", "incomplete"}
            and exists("site/capstone-acceptance.html"),
            ["capstone-acceptance/capstone-acceptance.json", "capstone-acceptance/reports/capstone-acceptance.md", "site/capstone-acceptance.html", "scripts/build_capstone_acceptance.py", "scripts/verify_capstone_acceptance.py"],
            {
                "score": capstone_acceptance.get("score", 0),
                "max_score": capstone_acceptance.get("max_score", 0),
                "criteria": capstone_acceptance.get("criteria_count", 0),
                "failed_criteria": capstone_acceptance.get("failed_criteria", 0),
                "status": capstone_acceptance.get("status", "missing"),
            },
            "The capstone is accepted with explicit runtime caveats because accelerator hardware validation remains GPU-host gated.",
        ),
        evidence_item(
            "Include external CUDA/Triton/ROCm/HIP/JAX/Hugging Face tutorial sources.",
            len(tutorial_sources) >= 16 and len(exercise_paths) == coverage["profile_count"],
            ["analysis/tutorial-sources.json", "analysis/tutorial-exercise-paths.json"],
            {
                "tutorial_sources": len(tutorial_sources),
                "providers": sorted({row["provider"] for row in tutorial_sources}),
                "exercise_paths": len(exercise_paths),
            },
        ),
        evidence_item(
            "Finish with a queryable workbench recommending bottleneck classes, lessons, papers, labs, and latest measurements.",
            coverage["profile_count"] >= 11 and coverage["latest_measurement_index_rows"] == measurements["artifact_count"],
            ["analysis/gpu-systems-workbench.json", "scripts/query_workbench.py", "scripts/query_measurements.py"],
            {
                "profiles": coverage["profile_count"],
                "latest_measurement_rows": coverage["latest_measurement_index_rows"],
                "paper_json": coverage["paper_json"],
            },
        ),
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": "proven-with-runtime-caveats" if all(item["status"] != "missing-or-incomplete" for item in items) else "incomplete",
        "items": items,
    }


def render_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Workbench End-To-End Audit",
        "",
        f"Generated: {audit['generated_at']}",
        f"Overall status: {audit['overall_status']}",
        "",
    ]
    for item in audit["items"]:
        lines.append(f"## {item['requirement']}")
        lines.append(f"Status: {item['status']}")
        lines.append(f"Evidence: {', '.join(item['evidence'])}")
        facts = ", ".join(f"{key}={value}" for key, value in item["facts"].items())
        lines.append(f"Facts: {facts}")
        if item.get("caveat"):
            lines.append(f"Caveat: {item['caveat']}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    audit = build_audit()
    OUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(audit), encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
