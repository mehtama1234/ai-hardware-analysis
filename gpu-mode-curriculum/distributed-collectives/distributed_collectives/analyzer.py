from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "distributed-collectives"
REPORT_JSON = OUT / "distributed-collectives-report.json"
REPORT_MD = OUT / "reports" / "distributed-collectives-report.md"

SOURCE_REPORTS = [
    "distributed-topology/distributed-topology-plan.json",
    "moe-routing-all-to-all/moe-routing-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
    "programming-projects/distributed-collectives/measurements.json",
    "comprehensive-labs/measurements/comp-lab-07-distributed-collectives.json",
]


@dataclass(frozen=True)
class CollectiveScenario:
    scenario_id: str
    collective: str
    algorithm: str
    ranks: int
    payload_mb: float
    bandwidth_gbps: float
    latency_us: float
    compute_ms: float
    overlap_fraction: float
    topology: str
    backend: str


SCENARIOS = [
    CollectiveScenario("dp-grad-all-reduce-nvlink", "all-reduce", "ring", 8, 512.0, 450.0, 4.0, 7.5, 0.55, "eight-nvlink", "nccl"),
    CollectiveScenario("tp-activation-all-gather", "all-gather", "ring", 4, 128.0, 300.0, 5.0, 2.2, 0.35, "quad-nvlink", "nccl"),
    CollectiveScenario("zero-reduce-scatter-pcie", "reduce-scatter", "ring", 4, 768.0, 64.0, 9.0, 12.0, 0.45, "dual-pcie-expanded", "nccl"),
    CollectiveScenario("moe-expert-all-to-all-ib", "all-to-all", "pairwise", 16, 256.0, 200.0, 7.0, 5.5, 0.25, "sixteen-ib", "nccl/nvshmem"),
    CollectiveScenario("small-control-broadcast", "broadcast", "tree", 8, 8.0, 200.0, 4.0, 0.4, 0.10, "eight-nvlink", "nccl"),
    CollectiveScenario("amd-rccl-grad-all-reduce", "all-reduce", "ring", 8, 384.0, 300.0, 5.5, 6.0, 0.50, "eight-xgmi", "rccl"),
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _algorithm_factor(collective: str, algorithm: str, ranks: int) -> tuple[float, int]:
    if ranks <= 1:
        return 0.0, 0
    if collective == "all-reduce" and algorithm == "ring":
        return 2 * (ranks - 1) / ranks, 2 * (ranks - 1)
    if collective == "reduce-scatter" and algorithm == "ring":
        return (ranks - 1) / ranks, ranks - 1
    if collective == "all-gather" and algorithm == "ring":
        return (ranks - 1) / ranks, ranks - 1
    if collective == "all-to-all":
        return (ranks - 1) / ranks, ranks - 1
    if collective == "broadcast" and algorithm == "tree":
        steps = max(1, (ranks - 1).bit_length())
        return 1.0, steps
    return 1.0, ranks - 1


def _scenario(row: CollectiveScenario) -> dict[str, Any]:
    traffic_factor, steps = _algorithm_factor(row.collective, row.algorithm, row.ranks)
    payload_bytes = row.payload_mb * 1_000_000
    transfer_ms = traffic_factor * payload_bytes / (row.bandwidth_gbps * 1_000_000_000) * 1000.0 if row.bandwidth_gbps > 0 else 0.0
    latency_ms = steps * row.latency_us / 1000.0
    exposed_comm_ms = max(0.0, transfer_ms + latency_ms - row.compute_ms * row.overlap_fraction)
    no_overlap_ms = row.compute_ms + transfer_ms + latency_ms
    overlapped_step_ms = row.compute_ms + exposed_comm_ms
    efficiency = payload_bytes / max((transfer_ms + latency_ms) / 1000.0, 1e-9) / (row.bandwidth_gbps * 1_000_000_000)
    overlap_gain = 1.0 - overlapped_step_ms / max(no_overlap_ms, 1e-9)
    passed = efficiency >= 0.45 and exposed_comm_ms <= no_overlap_ms and overlap_gain >= 0.05
    return {
        "scenario_id": row.scenario_id,
        "status": "passed" if passed else "tuning-required",
        "collective": row.collective,
        "algorithm": row.algorithm,
        "ranks": row.ranks,
        "payload_mb": row.payload_mb,
        "topology": row.topology,
        "backend": row.backend,
        "bandwidth_gbps": row.bandwidth_gbps,
        "latency_us": row.latency_us,
        "algorithm_steps": steps,
        "wire_traffic_factor": round(traffic_factor, 6),
        "transfer_ms": round(transfer_ms, 6),
        "latency_ms": round(latency_ms, 6),
        "compute_ms": row.compute_ms,
        "overlap_fraction": row.overlap_fraction,
        "exposed_comm_ms": round(exposed_comm_ms, 6),
        "overlapped_step_ms": round(overlapped_step_ms, 6),
        "bandwidth_efficiency": round(efficiency, 6),
        "overlap_gain": round(overlap_gain, 6),
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "topology_status": reports.get(SOURCE_REPORTS[0], {}).get("status", "missing"),
        "moe_scenarios": reports.get(SOURCE_REPORTS[1], {}).get("scenario_count", 0),
        "profiler_rows": reports.get(SOURCE_REPORTS[2], {}).get("row_count", 0),
        "project_status": reports.get(SOURCE_REPORTS[3], {}).get("status", "missing"),
        "comprehensive_status": reports.get(SOURCE_REPORTS[4], {}).get("status", "missing"),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Distributed Collectives",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "",
        "| scenario | collective | algorithm | ranks | backend | exposed ms | efficiency | overlap gain | status |",
        "|---|---|---|---:|---|---:|---:|---:|---|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| {row['scenario_id']} | {row['collective']} | {row['algorithm']} | {row['ranks']} | "
            f"{row['backend']} | {row['exposed_comm_ms']} | {row['bandwidth_efficiency']} | {row['overlap_gain']} | {row['status']} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_distributed_collectives_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    scenarios = [_scenario(row) for row in SCENARIOS]
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    collectives = sorted({row["collective"] for row in scenarios})
    backends = sorted({row["backend"] for row in scenarios})
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "distributed-collectives-ready" if passed >= 5 and len(collectives) >= 5 else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "collective_count": len(collectives),
        "backend_count": len(backends),
        "collectives": collectives,
        "backends": backends,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "recommendations": [
            "Teach distributed performance through collective algorithm, payload, topology, and exposed communication time together.",
            "Use reduce-scatter plus all-gather as the concrete bridge from data parallelism to ZeRO/FSDP-style sharding.",
            "Require overlap evidence, not only raw bandwidth, because exposed communication controls training and serving latency.",
            "Promote with NCCL/RCCL tests, NVSHMEM where appropriate, torchrun traces, and profiler timelines.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["distributed-collectives", "profiler-capture", "full-gpu-regression"],
            "commands": [
                "python3 scripts/run_gpu_host_preflight.py",
                "python3 scripts/run_distributed_collectives.py",
                "python3 scripts/verify_distributed_collectives.py",
                "torchrun --nproc_per_node=2 <collective_benchmark.py>",
                "nccl-tests/build/all_reduce_perf -b 8M -e 1G -f 2 -g 1",
                "rocprof <rccl_collective_benchmark>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id distributed-collectives --execute",
            ],
            "note": "Local report validates communication contracts; final acceptance needs measured NCCL/RCCL/NVSHMEM bandwidth and overlap traces.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
