from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "hardware-capacity-planning"
REPORT_JSON = OUT / "hardware-capacity-plan.json"
REPORT_MD = OUT / "reports" / "hardware-capacity-plan.md"


SOURCE_REPORTS = [
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
    "serving-engine-comparison/serving-engine-comparison.json",
    "distributed-topology/distributed-topology-plan.json",
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _hardware_profiles() -> list[dict[str, Any]]:
    return [
        {
            "id": "local-cpu-fallback",
            "class": "development fallback",
            "accelerators": 0,
            "memory_gb_per_accelerator": 0,
            "interconnect": "host-memory",
            "relative_tensor_score": 0.05,
            "relative_bandwidth_score": 0.08,
            "estimated_power_w": 120,
            "estimated_cost_per_hour": 0.0,
            "best_for": ["schema validation", "unit tests", "CPU proxy timing"],
        },
        {
            "id": "single-24gb-dev-gpu",
            "class": "single developer GPU",
            "accelerators": 1,
            "memory_gb_per_accelerator": 24,
            "interconnect": "single-card",
            "relative_tensor_score": 1.0,
            "relative_bandwidth_score": 1.0,
            "estimated_power_w": 320,
            "estimated_cost_per_hour": 0.6,
            "best_for": ["kernel smoke", "small-model serving", "profiler practice"],
        },
        {
            "id": "datacenter-80gb-training-gpu",
            "class": "single datacenter GPU",
            "accelerators": 1,
            "memory_gb_per_accelerator": 80,
            "interconnect": "single-card",
            "relative_tensor_score": 4.0,
            "relative_bandwidth_score": 3.4,
            "estimated_power_w": 700,
            "estimated_cost_per_hour": 3.4,
            "best_for": ["large single-GPU inference", "fine-tuning smoke", "Nsight profiling"],
        },
        {
            "id": "large-memory-192gb-inference-gpu",
            "class": "large-memory inference GPU",
            "accelerators": 1,
            "memory_gb_per_accelerator": 192,
            "interconnect": "single-card-large-memory",
            "relative_tensor_score": 3.2,
            "relative_bandwidth_score": 3.0,
            "estimated_power_w": 760,
            "estimated_cost_per_hour": 4.2,
            "best_for": ["long context", "large KV cache", "high batch inference"],
        },
        {
            "id": "multi-node-cluster-slice",
            "class": "8 accelerator distributed slice",
            "accelerators": 8,
            "memory_gb_per_accelerator": 80,
            "interconnect": "high-bandwidth-fabric",
            "relative_tensor_score": 24.0,
            "relative_bandwidth_score": 18.0,
            "estimated_power_w": 5600,
            "estimated_cost_per_hour": 24.0,
            "best_for": ["70B training", "tensor parallel serving", "collective profiling"],
        },
        {
            "id": "large-memory-training-slice",
            "class": "8 accelerator large-memory training slice",
            "accelerators": 8,
            "memory_gb_per_accelerator": 192,
            "interconnect": "high-bandwidth-large-memory-fabric",
            "relative_tensor_score": 20.0,
            "relative_bandwidth_score": 16.0,
            "estimated_power_w": 6080,
            "estimated_cost_per_hour": 34.0,
            "best_for": ["long-context fine-tuning", "optimizer-state-heavy training", "large activation checkpoints"],
        },
    ]


def _workloads() -> list[dict[str, Any]]:
    return [
        {
            "id": "kernel-dev-smoke",
            "model_parameters_b": 0,
            "dtype_bytes": 4,
            "batch": 1,
            "context_tokens": 0,
            "output_tokens": 0,
            "activation_gb": 2.0,
            "target": "correctness, launch, memory, reduction, normalization, fusion, and profiler smoke checks",
            "intensity": "mixed",
        },
        {
            "id": "interactive-7b-chat",
            "model_parameters_b": 7,
            "dtype_bytes": 2,
            "batch": 8,
            "context_tokens": 4096,
            "output_tokens": 512,
            "activation_gb": 4.0,
            "target": "interactive vLLM or TGI serving with bounded TTFT",
            "intensity": "memory-bandwidth",
        },
        {
            "id": "long-context-13b-rag",
            "model_parameters_b": 13,
            "dtype_bytes": 2,
            "batch": 8,
            "context_tokens": 32768,
            "output_tokens": 1024,
            "activation_gb": 8.0,
            "target": "long-context retrieval workload with heavy KV cache pressure",
            "intensity": "kv-cache-capacity",
        },
        {
            "id": "batch-70b-inference",
            "model_parameters_b": 70,
            "dtype_bytes": 2,
            "batch": 16,
            "context_tokens": 8192,
            "output_tokens": 1024,
            "activation_gb": 18.0,
            "target": "offline or high-throughput serving with tensor parallelism",
            "intensity": "tensor-core-compute",
        },
        {
            "id": "dense-70b-sft",
            "model_parameters_b": 70,
            "dtype_bytes": 2,
            "batch": 8,
            "context_tokens": 4096,
            "output_tokens": 0,
            "activation_gb": 220.0,
            "target": "supervised fine-tuning step with optimizer state and all-reduce pressure",
            "intensity": "communication",
        },
    ]


def _memory_required_gb(workload: dict[str, Any], profile: dict[str, Any]) -> float:
    model_gb = workload["model_parameters_b"] * workload["dtype_bytes"]
    kv_factor = 0.000018 * max(workload["model_parameters_b"], 1)
    kv_gb = workload["batch"] * (workload["context_tokens"] + workload["output_tokens"]) * kv_factor
    optimizer_gb = model_gb * 6 if workload["id"].endswith("sft") else 0
    total = model_gb + kv_gb + workload["activation_gb"] + optimizer_gb
    accelerators = max(profile["accelerators"], 1)
    return round(total / accelerators, 2)


def _bottleneck(workload: dict[str, Any], profile: dict[str, Any], memory_required: float) -> str:
    if profile["accelerators"] == 0:
        return "accelerator-unavailable"
    if memory_required > profile["memory_gb_per_accelerator"]:
        return "memory-capacity"
    if workload["intensity"] == "communication" or profile["accelerators"] > 1 and workload["model_parameters_b"] >= 70:
        return "communication"
    return workload["intensity"]


def _validation_commands(workload: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    commands = ["python3 scripts/run_gpu_host_preflight.py"]
    if profile["id"] == "local-cpu-fallback":
        return commands + ["python3 scripts/verify_hardware_capacity_plan.py"]
    commands.extend(["nvidia-smi --query-gpu=name,memory.total,power.limit --format=csv", "python3 scripts/run_gpu_promotion_suite.py --run-id capacity-plan --execute"])
    if "serving" in workload["target"] or "vLLM" in workload["target"]:
        commands.append("vllm serve <model> --tensor-parallel-size <tp> --max-model-len <tokens>")
    if workload["id"].endswith("sft"):
        commands.append("torchrun --nproc-per-node=<gpus> <training_script.py>")
    commands.extend(["nsys profile -o capacity-plan python3 <workload.py>", "ncu --set full -o capacity-plan python3 <kernel_or_serving_probe.py>"])
    if "amd" in profile.get("class", "").lower() or "rocm" in profile.get("interconnect", "").lower():
        commands.append("rocprof --stats python3 <workload.py>")
    return commands


def _evaluate(workload: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    required = _memory_required_gb(workload, profile)
    capacity = profile["memory_gb_per_accelerator"] if profile["accelerators"] else 0
    headroom = round(capacity - required, 2)
    bottleneck = _bottleneck(workload, profile, required)
    viable = profile["accelerators"] > 0 and headroom >= 2.0
    throughput_score = round(
        (profile["relative_tensor_score"] * 0.6 + profile["relative_bandwidth_score"] * 0.4)
        / max(required / 80, 0.25),
        3,
    )
    if bottleneck in {"memory-capacity", "accelerator-unavailable"}:
        throughput_score = 0.0
    return {
        "workload_id": workload["id"],
        "profile_id": profile["id"],
        "status": "viable" if viable else "rejected",
        "memory_required_gb": required,
        "memory_headroom_gb": headroom,
        "estimated_power_w": profile["estimated_power_w"],
        "estimated_cost_per_hour": profile["estimated_cost_per_hour"],
        "throughput_score": throughput_score,
        "bottleneck": bottleneck,
        "validation_commands": _validation_commands(workload, profile),
    }


def _recommend(workload: dict[str, Any], evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [row for row in evaluations if row["workload_id"] == workload["id"] and row["status"] == "viable"]
    if not candidates:
        chosen = max([row for row in evaluations if row["workload_id"] == workload["id"]], key=lambda row: row["memory_headroom_gb"])
    else:
        preferred_profiles = {
            "kernel-dev-smoke": ["single-24gb-dev-gpu", "datacenter-80gb-training-gpu"],
            "interactive-7b-chat": ["datacenter-80gb-training-gpu", "single-24gb-dev-gpu"],
            "long-context-13b-rag": ["large-memory-192gb-inference-gpu", "large-memory-training-slice"],
            "batch-70b-inference": ["multi-node-cluster-slice", "large-memory-training-slice"],
            "dense-70b-sft": ["large-memory-training-slice", "multi-node-cluster-slice"],
        }
        ranked = preferred_profiles.get(workload["id"], [])
        chosen = min(
            candidates,
            key=lambda row: (
                ranked.index(row["profile_id"]) if row["profile_id"] in ranked else len(ranked),
                row["estimated_cost_per_hour"],
                -row["throughput_score"],
            ),
        )
    why = (
        f"{chosen['profile_id']} has modeled memory headroom and the preferred hardware class for {workload['target']}."
        if chosen["status"] == "viable"
        else f"{chosen['profile_id']} is the least-bad modeled fallback, but still needs memory or parallelism changes before the workload is viable."
    )
    return {
        "workload_id": workload["id"],
        "recommended_profile": chosen["profile_id"],
        "bottleneck": chosen["bottleneck"],
        "memory_required_gb": chosen["memory_required_gb"],
        "memory_headroom_gb": chosen["memory_headroom_gb"],
        "estimated_power_w": chosen["estimated_power_w"],
        "estimated_cost_per_hour": chosen["estimated_cost_per_hour"],
        "why": why,
        "validation_commands": chosen["validation_commands"],
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    profiler = reports.get(SOURCE_REPORTS[1], {})
    return {
        "kernel_benchmarks": reports.get(SOURCE_REPORTS[0], {}).get("benchmark_count", 0),
        "profiler_rows": profiler.get("row_count", 0),
        "profiler_classifications": sorted(profiler.get("classification_counts", {})),
        "serving_scenarios": reports.get(SOURCE_REPORTS[2], {}).get("scenario_count", 0),
        "distributed_topologies": reports.get(SOURCE_REPORTS[3], {}).get("topology_count", 0),
    }


def render_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Hardware Capacity Plan",
        "",
        f"Generated: `{plan['generated_at']}`",
        f"Status: `{plan['status']}`",
        "",
        "## Recommendations",
        "",
        "| workload | profile | bottleneck | memory GB | headroom GB | power W | cost/hr |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in plan["recommendations"]:
        lines.append(
            f"| {row['workload_id']} | {row['recommended_profile']} | {row['bottleneck']} | "
            f"{row['memory_required_gb']} | {row['memory_headroom_gb']} | {row['estimated_power_w']} | {row['estimated_cost_per_hour']} |"
        )
    lines.extend(["", "## Evidence Commands", ""])
    for row in plan["recommendations"]:
        lines.append(f"### {row['workload_id']}")
        for command in row["validation_commands"]:
            lines.append(f"- `{command}`")
    lines.extend(["", "## Source Reports", ""])
    for source in plan["source_reports"]:
        lines.append(f"- `{source}`")
    return "\n".join(lines).rstrip() + "\n"


def build_hardware_capacity_plan() -> dict[str, Any]:
    profiles = _hardware_profiles()
    workloads = _workloads()
    source_reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    evaluations = [_evaluate(workload, profile) for workload in workloads for profile in profiles]
    recommendations = [_recommend(workload, evaluations) for workload in workloads]
    rejected_count = sum(1 for row in evaluations if row["status"] == "rejected")
    plan = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "capacity-plan-ready",
        "profile_count": len(profiles),
        "workload_count": len(workloads),
        "recommendation_count": len(recommendations),
        "rejected_count": rejected_count,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(source_reports),
        "hardware_profiles": profiles,
        "workloads": workloads,
        "recommendations": recommendations,
        "evaluations": evaluations,
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["preflight", "promotion-suite", "profiler-evidence", "gpu-run-import", "provenance"],
            "note": "Modeled capacity choices must be replaced by measured GPU-host memory, power, throughput, and profiler counters before production claims.",
        },
    }
    _write_json(REPORT_JSON, plan)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(render_markdown(plan), encoding="utf-8")
    return plan
