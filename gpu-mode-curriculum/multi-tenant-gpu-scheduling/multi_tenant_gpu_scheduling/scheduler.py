from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "multi-tenant-gpu-scheduling"
REPORT_JSON = OUT / "multi-tenant-scheduling-report.json"
REPORT_MD = OUT / "reports" / "multi-tenant-scheduling-report.md"

SOURCE_REPORTS = [
    "hardware-capacity-planning/hardware-capacity-plan.json",
    "distributed-topology/distributed-topology-plan.json",
    "serving-traces/reports/serving-trace-report.json",
    "cuda-graphs-latency/cuda-graphs-latency-report.json",
]

TENANTS = [
    {"id": "tenant-a-interactive-7b", "kind": "serving", "memory_gb": 18, "sm_fraction": 0.35, "latency_slo_ms": 85, "priority": 4, "isolation_required": True},
    {"id": "tenant-b-batch-embedding", "kind": "batch", "memory_gb": 10, "sm_fraction": 0.20, "latency_slo_ms": 220, "priority": 2, "isolation_required": False},
    {"id": "tenant-c-long-context-rag", "kind": "serving", "memory_gb": 36, "sm_fraction": 0.55, "latency_slo_ms": 160, "priority": 5, "isolation_required": True},
    {"id": "tenant-d-kernel-ci", "kind": "ci", "memory_gb": 6, "sm_fraction": 0.15, "latency_slo_ms": 500, "priority": 1, "isolation_required": False},
    {"id": "tenant-e-70b-training-smoke", "kind": "training", "memory_gb": 72, "sm_fraction": 0.90, "latency_slo_ms": 1000, "priority": 3, "isolation_required": True},
]

POLICIES = [
    {
        "id": "exclusive",
        "label": "Full GPU exclusive tenancy",
        "partitions": [{"id": "gpu0-full", "memory_gb": 80, "sm_fraction": 1.0, "isolation": "exclusive", "max_tenants": 1}],
        "queue": True,
    },
    {
        "id": "mig-pack",
        "label": "MIG-style packed inference slices",
        "partitions": [
            {"id": "gpu0-mig-4g-40gb", "memory_gb": 40, "sm_fraction": 0.50, "isolation": "hardware-slice", "max_tenants": 1},
            {"id": "gpu0-mig-2g-20gb", "memory_gb": 20, "sm_fraction": 0.25, "isolation": "hardware-slice", "max_tenants": 1},
            {"id": "gpu0-mig-1g-10gb-a", "memory_gb": 10, "sm_fraction": 0.125, "isolation": "hardware-slice", "max_tenants": 1},
            {"id": "gpu0-mig-1g-10gb-b", "memory_gb": 10, "sm_fraction": 0.125, "isolation": "hardware-slice", "max_tenants": 1},
        ],
        "queue": True,
    },
    {
        "id": "mps-fair-share",
        "label": "MPS-style shared full GPU fair share",
        "partitions": [{"id": "gpu0-mps-pool", "memory_gb": 80, "sm_fraction": 1.0, "isolation": "process-share", "max_tenants": 4}],
        "queue": True,
    },
    {
        "id": "cluster-queue",
        "label": "Kubernetes device-plugin cluster queue",
        "partitions": [
            {"id": "node-a-gpu0-full", "memory_gb": 80, "sm_fraction": 1.0, "isolation": "exclusive", "max_tenants": 1},
            {"id": "node-b-gpu0-mig-4g-40gb", "memory_gb": 40, "sm_fraction": 0.50, "isolation": "hardware-slice", "max_tenants": 1},
            {"id": "node-b-gpu0-mig-2g-20gb", "memory_gb": 20, "sm_fraction": 0.25, "isolation": "hardware-slice", "max_tenants": 1},
            {"id": "node-c-gpu0-mps-pool", "memory_gb": 80, "sm_fraction": 1.0, "isolation": "process-share", "max_tenants": 3},
        ],
        "queue": True,
    },
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _jains_fairness(shares: list[float]) -> float:
    if not shares:
        return 0.0
    total = sum(shares)
    denom = len(shares) * sum(share * share for share in shares)
    return 0.0 if denom == 0.0 else total * total / denom


def _fits(tenant: dict[str, Any], partition: dict[str, Any], existing: list[dict[str, Any]]) -> bool:
    used_memory = sum(row["memory_gb"] for row in existing)
    used_sm = sum(row["sm_fraction"] for row in existing)
    return (
        len(existing) < partition["max_tenants"]
        and used_memory + tenant["memory_gb"] <= partition["memory_gb"]
        and used_sm + tenant["sm_fraction"] <= partition["sm_fraction"]
    )


def _slo_status(tenant: dict[str, Any], partition: dict[str, Any], shared_count: int, queued: bool) -> str:
    if queued:
        return "queued"
    isolation_penalty = 0.0 if partition["isolation"] in {"exclusive", "hardware-slice"} else 0.25
    share_penalty = max(0.0, tenant["sm_fraction"] / max(partition["sm_fraction"], 1e-9) - 0.8) * 0.35
    contention_penalty = max(0, shared_count - 1) * 0.15
    estimated_ms = tenant["latency_slo_ms"] * (0.72 + isolation_penalty + share_penalty + contention_penalty)
    return "pass" if estimated_ms <= tenant["latency_slo_ms"] else "risk"


def _plan(policy: dict[str, Any]) -> dict[str, Any]:
    assigned: dict[str, list[dict[str, Any]]] = {partition["id"]: [] for partition in policy["partitions"]}
    placements: list[dict[str, Any]] = []
    for tenant in sorted(TENANTS, key=lambda row: (-row["priority"], -row["memory_gb"], row["id"])):
        choice = None
        for partition in sorted(policy["partitions"], key=lambda row: (row["memory_gb"], row["sm_fraction"])):
            if _fits(tenant, partition, assigned[partition["id"]]):
                if tenant["isolation_required"] and partition["isolation"] == "process-share":
                    continue
                choice = partition
                break
        if choice is None:
            placements.append(
                {
                    "tenant_id": tenant["id"],
                    "partition_id": "queue",
                    "status": "queued" if policy["queue"] else "rejected",
                    "memory_headroom_gb": 0,
                    "sm_share": 0.0,
                    "isolation": "none",
                    "slo_status": "queued",
                    "reason": "no partition satisfies memory, SM, and isolation constraints",
                }
            )
            continue
        assigned[choice["id"]].append(tenant)
        used_memory = sum(row["memory_gb"] for row in assigned[choice["id"]])
        used_sm = sum(row["sm_fraction"] for row in assigned[choice["id"]])
        placements.append(
            {
                "tenant_id": tenant["id"],
                "partition_id": choice["id"],
                "status": "accepted",
                "memory_headroom_gb": round(choice["memory_gb"] - used_memory, 3),
                "sm_share": round(tenant["sm_fraction"], 3),
                "isolation": choice["isolation"],
                "slo_status": _slo_status(tenant, choice, len(assigned[choice["id"]]), False),
                "reason": "fits partition with required isolation and capacity",
            }
        )
    accepted = [row for row in placements if row["status"] == "accepted"]
    queued = [row for row in placements if row["status"] != "accepted"]
    fairness = _jains_fairness([row["sm_share"] for row in accepted])
    utilization = sum(row["sm_share"] for row in accepted) / max(sum(row["sm_fraction"] for row in policy["partitions"]), 1e-9)
    slo_pass = sum(1 for row in accepted if row["slo_status"] == "pass")
    isolated = sum(1 for row in accepted if row["isolation"] in {"exclusive", "hardware-slice"})
    score = accepted and (
        len(accepted) * 20.0
        + fairness * 15.0
        + slo_pass * 5.0
        + isolated * 3.0
        - len(queued) * 8.0
        + min(utilization, 1.0) * 10.0
    )
    return {
        "policy_id": policy["id"],
        "label": policy["label"],
        "accepted_count": len(accepted),
        "rejected_count": len(queued),
        "isolated_count": isolated,
        "slo_pass_count": slo_pass,
        "fairness_index": round(fairness, 6),
        "estimated_utilization": round(utilization, 6),
        "policy_score": round(float(score), 6),
        "placements": placements,
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    capacity = reports.get(SOURCE_REPORTS[0], {})
    topology = reports.get(SOURCE_REPORTS[1], {})
    serving = reports.get(SOURCE_REPORTS[2], {})
    graphs = reports.get(SOURCE_REPORTS[3], {})
    return {
        "hardware_profiles": capacity.get("profile_count", 0),
        "capacity_workloads": capacity.get("workload_count", 0),
        "topologies": topology.get("topology_count", 0),
        "serving_traces": serving.get("trace_count", 0),
        "cuda_graph_capture_ready": graphs.get("capture_ready_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Multi-Tenant GPU Scheduling",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        f"Recommended policy: `{report['recommended_policy']}`",
        "",
        "## Policy Results",
        "",
        "| policy | accepted | queued | fairness | utilization | score |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for plan in report["plans"]:
        lines.append(
            f"| {plan['policy_id']} | {plan['accepted_count']} | {plan['rejected_count']} | "
            f"{plan['fairness_index']} | {plan['estimated_utilization']} | {plan['policy_score']} |"
        )
    lines.extend(["", "## Recommended Placements", "", "| tenant | partition | status | isolation | SLO | reason |", "|---|---|---|---|---|---|"])
    best = next(plan for plan in report["plans"] if plan["policy_id"] == report["recommended_policy"])
    for row in best["placements"]:
        lines.append(
            f"| {row['tenant_id']} | {row['partition_id']} | {row['status']} | {row['isolation']} | {row['slo_status']} | {row['reason']} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_multi_tenant_scheduling_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    plans = [_plan(policy) for policy in POLICIES]
    best = max(plans, key=lambda row: row["policy_score"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "scheduling-ready" if best["accepted_count"] >= 4 and best["fairness_index"] >= 0.60 else "needs-work",
        "policy_count": len(POLICIES),
        "tenant_count": len(TENANTS),
        "placement_count": sum(len(plan["placements"]) for plan in plans),
        "accepted_count": best["accepted_count"],
        "rejected_count": best["rejected_count"],
        "recommended_policy": best["policy_id"],
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "policies": POLICIES,
        "tenants": TENANTS,
        "plans": plans,
        "recommendations": [
            "Use hardware-isolated MIG-style slices for latency-sensitive tenants when memory fits.",
            "Route training smoke and oversized long-context jobs through a cluster queue instead of squeezing them into shared MPS.",
            "Allow MPS only for non-isolation-required batch and CI tenants, and cap active tenants per pool.",
            "Promote this local model on a GPU cluster with Kubernetes device-plugin, MIG inventory, MPS control, and per-tenant profiler traces.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["mig-inventory", "mps-daemon", "kubernetes-device-plugin", "tenant-load-test", "per-tenant-profiler-traces"],
            "commands": [
                "kubectl get nodes -o json",
                "kubectl describe node <gpu-node>",
                "nvidia-smi -L",
                "nvidia-smi mig -lgip",
                "nvidia-cuda-mps-control -d",
                "kubectl apply -f <gpu-workload.yaml>",
                "kubectl top pods -A --containers",
                "python3 scripts/run_gpu_promotion_suite.py --run-id multi-tenant-scheduling --execute",
            ],
            "note": "Local model checks placement logic; real acceptance requires device-plugin inventory, MIG/MPS telemetry, and measured per-tenant latency/throughput.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
