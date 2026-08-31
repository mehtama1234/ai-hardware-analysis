from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "moe-routing-all-to-all"
REPORT_JSON = OUT / "moe-routing-report.json"
REPORT_MD = OUT / "reports" / "moe-routing-report.md"

SOURCE_REPORTS = [
    "distributed-topology/distributed-topology-plan.json",
    "serving-engine-comparison/serving-engine-comparison.json",
    "kv-cache-paged-attention/kv-cache-report.json",
    "multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json",
]


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    token_count: int
    expert_count: int
    top_k: int
    expert_parallel: int
    hidden_size: int
    capacity_factor: float
    skew: float
    fabric_gbps: float
    latency_us: float


SCENARIOS = [
    Scenario("balanced-chat", 2048, 8, 2, 4, 4096, 1.25, 0.05, 300.0, 5.0),
    Scenario("skewed-agent-tools", 4096, 8, 2, 4, 4096, 1.10, 0.55, 300.0, 5.0),
    Scenario("long-context-mixtral", 8192, 8, 2, 8, 4096, 1.35, 0.35, 450.0, 4.0),
    Scenario("cross-node-moe", 16384, 16, 2, 16, 6144, 1.30, 0.30, 200.0, 7.0),
    Scenario("training-microbatch", 32768, 16, 2, 8, 8192, 1.20, 0.20, 450.0, 4.0),
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _jains_fairness(values: list[float]) -> float:
    total = sum(values)
    denom = len(values) * sum(value * value for value in values)
    return 0.0 if denom == 0.0 else total * total / denom


def _route(row: Scenario) -> dict[str, Any]:
    rng = random.Random(row.scenario_id)
    loads = [0 for _ in range(row.expert_count)]
    hot_experts = max(1, row.expert_count // 4)
    for token in range(row.token_count):
        for rank in range(row.top_k):
            if rng.random() < row.skew:
                expert = (token + rank) % hot_experts
            else:
                expert = rng.randrange(row.expert_count)
            loads[expert] += 1
    total_assignments = row.token_count * row.top_k
    ideal = total_assignments / row.expert_count
    capacity = math.ceil(ideal * row.capacity_factor)
    dropped = sum(max(0, load - capacity) for load in loads)
    accepted = total_assignments - dropped
    peak = max(loads)
    p95 = sorted(loads)[int((len(loads) - 1) * 0.95)]
    fairness = _jains_fairness([float(load) for load in loads])
    imbalance = peak / max(ideal, 1.0)
    bytes_per_assignment = row.hidden_size * 2
    payload_gb = accepted * bytes_per_assignment / 1e9
    ranks = max(row.expert_parallel, 1)
    all_to_all_ms = 0.0
    if ranks > 1:
        wire_bytes = payload_gb * 1e9 * (ranks - 1) / ranks
        all_to_all_ms = 2 * (ranks - 1) * row.latency_us / 1000.0 + wire_bytes / (row.fabric_gbps * 1e9) * 1000.0
    status = "passed" if fairness >= 0.70 and dropped / max(total_assignments, 1) <= 0.20 else "needs-capacity-or-router-tuning"
    return {
        "scenario_id": row.scenario_id,
        "status": status,
        "token_count": row.token_count,
        "expert_count": row.expert_count,
        "top_k": row.top_k,
        "expert_parallel": row.expert_parallel,
        "capacity_factor": row.capacity_factor,
        "expert_loads": loads,
        "ideal_load": round(ideal, 3),
        "capacity_per_expert": capacity,
        "accepted_assignments": accepted,
        "dropped_assignments": dropped,
        "drop_rate": round(dropped / max(total_assignments, 1), 6),
        "fairness_index": round(fairness, 6),
        "load_imbalance": round(imbalance, 6),
        "p95_expert_load": p95,
        "all_to_all_payload_gb": round(payload_gb, 6),
        "estimated_all_to_all_ms": round(all_to_all_ms, 6),
        "bottleneck": "router-load-imbalance" if imbalance > 1.8 else "capacity-drops" if dropped else "all-to-all-communication" if all_to_all_ms > 1.0 else "balanced",
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    topology = reports.get(SOURCE_REPORTS[0], {})
    serving = reports.get(SOURCE_REPORTS[1], {})
    kv_cache = reports.get(SOURCE_REPORTS[2], {})
    scheduling = reports.get(SOURCE_REPORTS[3], {})
    return {
        "topology_workloads": topology.get("workload_count", 0),
        "topology_candidates": topology.get("candidate_count", 0),
        "serving_engines": serving.get("engine_count", 0),
        "kv_cache_scenarios": kv_cache.get("scenario_count", 0),
        "scheduling_policies": scheduling.get("policy_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE MoE Routing and All-to-All",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "",
        "| scenario | status | drop rate | fairness | imbalance | payload GB | all-to-all ms | bottleneck |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| {row['scenario_id']} | {row['status']} | {row['drop_rate']} | {row['fairness_index']} | "
            f"{row['load_imbalance']} | {row['all_to_all_payload_gb']} | {row['estimated_all_to_all_ms']} | {row['bottleneck']} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_moe_routing_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    scenarios = [_route(row) for row in SCENARIOS]
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    tuned = sum(1 for row in scenarios if row["status"] != "passed")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "moe-routing-ready" if passed >= 3 and tuned >= 1 else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "tuning_required_scenarios": tuned,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "recommendations": [
            "Track expert load histograms and drop rate before optimizing expert kernels.",
            "Use capacity factor and auxiliary load-balance loss as first knobs for skewed traffic.",
            "Treat all-to-all payload as a topology decision, especially across nodes.",
            "Promote with NCCL/RCCL all-to-all traces and per-expert kernel timings on accelerator hosts.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["moe-router-profile", "expert-load-histogram", "nccl-all-to-all", "moe-serving-trace", "moe-training-microbatch"],
            "commands": [
                "torchrun --nproc_per_node=8 <moe_router_probe.py>",
                "nsys profile -o moe-all-to-all torchrun --nproc_per_node=8 <moe_router_probe.py>",
                "ncu --set full -o moe-expert-kernels python3 <moe_expert_kernel_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id moe-routing-all-to-all --execute",
            ],
            "note": "Local simulation validates routing/accounting; real acceptance requires all-to-all traces, router histograms, and per-expert GPU kernel timings.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
