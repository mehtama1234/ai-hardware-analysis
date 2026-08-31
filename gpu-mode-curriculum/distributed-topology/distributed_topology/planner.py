from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "distributed-topology"
REPORT_JSON = OUT / "distributed-topology-plan.json"
REPORT_MD = OUT / "reports" / "distributed-topology-plan.md"
COLLECTIVE_REPORT = ROOT / "comprehensive-labs" / "measurements" / "comp-lab-07-distributed-collectives.json"
SERVING_ENGINE_REPORT = ROOT / "serving-engine-comparison" / "serving-engine-comparison.json"


TOPOLOGIES = [
    {"id": "single-gpu", "gpus": 1, "hbm_gb_per_gpu": 80, "intra_gbps": 0, "inter_gbps": 0, "latency_us": 0.0, "fabric": "none"},
    {"id": "dual-pcie", "gpus": 2, "hbm_gb_per_gpu": 48, "intra_gbps": 64, "inter_gbps": 64, "latency_us": 9.0, "fabric": "pcie"},
    {"id": "quad-nvlink", "gpus": 4, "hbm_gb_per_gpu": 80, "intra_gbps": 300, "inter_gbps": 64, "latency_us": 5.0, "fabric": "nvlink"},
    {"id": "eight-nvlink", "gpus": 8, "hbm_gb_per_gpu": 80, "intra_gbps": 450, "inter_gbps": 200, "latency_us": 4.0, "fabric": "nvlink"},
    {"id": "sixteen-ib", "gpus": 16, "hbm_gb_per_gpu": 80, "intra_gbps": 450, "inter_gbps": 200, "latency_us": 7.0, "fabric": "infiniband"},
]


WORKLOADS = [
    {"id": "llama-7b-chat", "params_b": 7, "active_params_b": 7, "context": 4096, "target_qps": 12, "mode": "serving"},
    {"id": "llama-13b-rag", "params_b": 13, "active_params_b": 13, "context": 16384, "target_qps": 8, "mode": "serving"},
    {"id": "llama-70b-batch", "params_b": 70, "active_params_b": 70, "context": 8192, "target_qps": 20, "mode": "serving"},
    {"id": "mixtral-8x7b", "params_b": 47, "active_params_b": 13, "context": 8192, "target_qps": 16, "mode": "serving"},
    {"id": "dense-70b-sft", "params_b": 70, "active_params_b": 70, "context": 4096, "microbatch_tokens": 8192, "mode": "training"},
]


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def model_memory_gb(params_b: float, bytes_per_param: float, optimizer: bool = False) -> float:
    base = params_b * 1e9 * bytes_per_param / 1e9
    return base * (4.0 if optimizer else 1.0)


def kv_cache_gb(active_params_b: float, context: int, replicas: int) -> float:
    hidden_proxy = math.sqrt(active_params_b * 1e9) / 32
    return hidden_proxy * context * 2 * 2 * max(replicas, 1) / 1e9


def all_reduce_ms(payload_gb: float, ranks: int, bandwidth_gbps: float, latency_us: float) -> float:
    if ranks <= 1 or bandwidth_gbps <= 0:
        return 0.0
    bytes_per_rank = payload_gb * 1e9
    link_bytes = 2 * bytes_per_rank * (ranks - 1) / ranks
    steps = 2 * (ranks - 1)
    return round(steps * latency_us / 1000.0 + link_bytes / (bandwidth_gbps * 1e9) * 1000.0, 4)


def choose_strategy(workload: dict[str, Any], topology: dict[str, Any]) -> dict[str, Any]:
    gpus = topology["gpus"]
    is_training = workload["mode"] == "training"
    weight_bytes = 2.0
    required_model_gb = model_memory_gb(workload["params_b"], weight_bytes, optimizer=is_training)
    if gpus == 1:
        tensor_parallel = 1
        pipeline_parallel = 1
    elif workload["params_b"] >= 65:
        tensor_parallel = min(gpus, 8)
        pipeline_parallel = max(1, gpus // tensor_parallel)
    elif workload["params_b"] >= 13 and topology["fabric"] in {"nvlink", "infiniband"}:
        tensor_parallel = min(gpus, 4)
        pipeline_parallel = max(1, gpus // tensor_parallel)
    else:
        tensor_parallel = 1
        pipeline_parallel = 1
    data_parallel = max(1, gpus // max(tensor_parallel * pipeline_parallel, 1))
    model_per_gpu = required_model_gb / max(tensor_parallel * pipeline_parallel, 1)
    kv_per_gpu = 0.0 if is_training else kv_cache_gb(workload["active_params_b"], workload["context"], data_parallel) / max(tensor_parallel, 1)
    activation_gb = 10.0 if is_training else 2.0
    total_per_gpu = round(model_per_gpu + kv_per_gpu + activation_gb, 4)
    fits_memory = total_per_gpu <= topology["hbm_gb_per_gpu"] * 0.9
    comm_payload_gb = workload["active_params_b"] * 2.0 / max(tensor_parallel, 1) if tensor_parallel > 1 else 0.25 * data_parallel
    bandwidth = topology["intra_gbps"] if tensor_parallel > 1 else topology["inter_gbps"]
    comm_ms = all_reduce_ms(comm_payload_gb, max(tensor_parallel, data_parallel), bandwidth, topology["latency_us"])
    bottleneck = "memory-capacity" if not fits_memory else "cross-node-communication" if topology["fabric"] == "infiniband" and comm_ms > 100 else "intra-node-collective" if comm_ms > 30 else "compute-or-scheduler"
    status = "candidate" if fits_memory else "rejected-memory"
    if is_training and data_parallel == 1 and gpus < 8:
        status = "rejected-scale"
        bottleneck = "insufficient-data-parallel-scale"
    return {
        "workload_id": workload["id"],
        "topology_id": topology["id"],
        "status": status,
        "strategy": {
            "tensor_parallel": tensor_parallel,
            "pipeline_parallel": pipeline_parallel,
            "data_parallel": data_parallel,
        },
        "memory_gb_per_gpu": total_per_gpu,
        "hbm_limit_gb": topology["hbm_gb_per_gpu"],
        "estimated_collective_ms": comm_ms,
        "bottleneck": bottleneck,
        "validation_commands": validation_commands(workload, topology),
    }


def validation_commands(workload: dict[str, Any], topology: dict[str, Any]) -> list[str]:
    commands = ["python3 scripts/verify_distributed_topology.py"]
    if topology["gpus"] > 1:
        commands.append(f"torchrun --nproc_per_node={min(topology['gpus'], 8)} <tp-or-collective-benchmark>")
    if workload["mode"] == "serving":
        commands.append("python3 scripts/verify_serving_engine_comparison.py")
    else:
        commands.append("python3 scripts/verify_runtime_matrix.py")
    return commands


def build_distributed_topology_plan() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    collective_report = load_json(COLLECTIVE_REPORT, {})
    serving_engine_report = load_json(SERVING_ENGINE_REPORT, {})
    plans = []
    recommendations = []
    for workload in WORKLOADS:
        candidates = [choose_strategy(workload, topology) for topology in TOPOLOGIES]
        ranked = sorted(
            candidates,
            key=lambda row: (
                row["status"] != "candidate",
                row["estimated_collective_ms"],
                row["memory_gb_per_gpu"],
                TOPOLOGIES[[topology["id"] for topology in TOPOLOGIES].index(row["topology_id"])]["gpus"],
            ),
        )
        plans.append({"workload": workload, "candidates": ranked})
        winner = ranked[0]
        recommendations.append(
            {
                "workload_id": workload["id"],
                "recommended_topology": winner["topology_id"],
                "strategy": winner["strategy"],
                "bottleneck": winner["bottleneck"],
                "estimated_collective_ms": winner["estimated_collective_ms"],
                "status": winner["status"],
            }
        )
    rejected = [candidate for plan in plans for candidate in plan["candidates"] if candidate["status"] != "candidate"]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "topology-plan-ready" if len(plans) == len(WORKLOADS) and any(row["status"] == "candidate" for row in recommendations) else "incomplete",
        "topology_count": len(TOPOLOGIES),
        "workload_count": len(WORKLOADS),
        "candidate_count": sum(1 for plan in plans for row in plan["candidates"] if row["status"] == "candidate"),
        "rejected_count": len(rejected),
        "source_reports": {
            "collective_model": str(COLLECTIVE_REPORT.relative_to(ROOT)),
            "serving_engine_comparison": str(SERVING_ENGINE_REPORT.relative_to(ROOT)),
        },
        "source_facts": {
            "collective_checks": len(collective_report.get("checks", [])),
            "serving_engine_status": serving_engine_report.get("status", "missing"),
        },
        "topologies": TOPOLOGIES,
        "workloads": WORKLOADS,
        "recommendations": recommendations,
        "plans": plans,
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["distributed-collectives", "vllm-serving-trace", "profiler-capture", "full-gpu-regression"],
            "note": "This planner is source-ready locally; final acceptance requires measured NCCL/RCCL bandwidth and serving/training throughput on the selected topology.",
        },
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Distributed Topology Plan",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        f"Topologies: `{report['topology_count']}`",
        f"Workloads: `{report['workload_count']}`",
        "",
        "## Recommendations",
        "",
        "| workload | topology | TP | PP | DP | bottleneck | collective ms | status |",
        "|---|---|---:|---:|---:|---|---:|---|",
    ]
    for row in report["recommendations"]:
        strategy = row["strategy"]
        lines.append(
            f"| {row['workload_id']} | {row['recommended_topology']} | {strategy['tensor_parallel']} | "
            f"{strategy['pipeline_parallel']} | {strategy['data_parallel']} | {row['bottleneck']} | "
            f"{row['estimated_collective_ms']} | {row['status']} |"
        )
    lines.extend(["", "## Candidate Plans", "", "| workload | topology | status | memory GB/GPU | collective ms | bottleneck |", "|---|---|---|---:|---:|---|"])
    for plan in report["plans"]:
        for candidate in plan["candidates"]:
            lines.append(
                f"| {plan['workload']['id']} | {candidate['topology_id']} | {candidate['status']} | "
                f"{candidate['memory_gb_per_gpu']} | {candidate['estimated_collective_ms']} | {candidate['bottleneck']} |"
            )
    lines.extend(["", "## GPU Host Promotion", "", report["gpu_host_promotion"]["note"]])
    return "\n".join(lines).rstrip() + "\n"
