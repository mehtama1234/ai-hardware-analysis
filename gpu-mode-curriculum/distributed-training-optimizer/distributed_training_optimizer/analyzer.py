from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "distributed-training-optimizer"
REPORT_JSON = OUT / "distributed-training-optimizer-report.json"
REPORT_MD = OUT / "reports" / "distributed-training-optimizer-report.md"

SOURCE_REPORTS = [
    "distributed-topology/distributed-topology-plan.json",
    "distributed-collectives/distributed-collectives-report.json",
    "distributed-collectives/reports/collective-benchmark-run.json",
    "hardware-capacity-planning/hardware-capacity-plan.json",
    "multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json",
    "numerical-reproducibility/numerical-reproducibility-report.json",
]


@dataclass(frozen=True)
class TrainingScenario:
    scenario_id: str
    strategy: str
    topology: str
    ranks: int
    params_b: float
    microbatch_tokens: int
    layers: int
    model_bytes: float
    grad_bytes: float
    optimizer_bytes: float
    activation_gb: float
    checkpoint_fraction: float
    compute_ms: float
    bubble_fraction: float
    bandwidth_gbps: float
    latency_us: float
    precision: str


SCENARIOS = [
    TrainingScenario("ddp-7b-nvlink-baseline", "ddp", "eight-nvlink", 8, 7, 4096, 32, 2.0, 2.0, 4.0, 18.0, 0.0, 95.0, 0.00, 450.0, 4.0, "bf16"),
    TrainingScenario("zero2-13b-pcie", "zero-2", "dual-pcie-expanded", 4, 13, 4096, 40, 2.0, 2.0, 4.0, 18.0, 0.45, 170.0, 0.00, 64.0, 9.0, "bf16"),
    TrainingScenario("fsdp-70b-ib-checkpoint", "fsdp-full-shard", "sixteen-ib", 16, 70, 8192, 80, 2.0, 2.0, 4.0, 16.0, 0.70, 760.0, 0.00, 200.0, 7.0, "bf16"),
    TrainingScenario("zero3-70b-ib-offload-risk", "zero-3", "sixteen-ib", 16, 70, 4096, 80, 2.0, 2.0, 4.0, 22.0, 0.60, 900.0, 0.04, 200.0, 7.0, "bf16"),
    TrainingScenario("pipeline-tp-70b-ib", "tp-pp-fsdp", "sixteen-ib", 16, 70, 16384, 80, 2.0, 2.0, 4.0, 30.0, 0.65, 960.0, 0.10, 200.0, 7.0, "bf16"),
    TrainingScenario("fp8-fsdp-70b-ib", "fsdp-full-shard", "sixteen-ib", 16, 70, 8192, 80, 1.0, 1.0, 4.0, 28.0, 0.65, 560.0, 0.00, 200.0, 7.0, "fp8-mixed"),
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _traffic(strategy: str, params_b: float, model_bytes: float, grad_bytes: float, ranks: int) -> dict[str, float]:
    param_gb = params_b * model_bytes
    grad_gb = params_b * grad_bytes
    if strategy == "ddp":
        return {"all_reduce_gb": grad_gb, "reduce_scatter_gb": 0.0, "all_gather_gb": 0.0, "param_prefetch_gb": 0.0}
    if strategy == "zero-2":
        return {"all_reduce_gb": 0.0, "reduce_scatter_gb": grad_gb, "all_gather_gb": 0.0, "param_prefetch_gb": 0.0}
    if strategy in {"zero-3", "fsdp-full-shard"}:
        shard = max(ranks, 1)
        return {"all_reduce_gb": 0.0, "reduce_scatter_gb": grad_gb, "all_gather_gb": param_gb * 0.35, "param_prefetch_gb": param_gb / shard}
    return {"all_reduce_gb": 0.0, "reduce_scatter_gb": grad_gb * 0.70, "all_gather_gb": param_gb * 0.30, "param_prefetch_gb": param_gb / max(ranks, 1)}


def _ring_ms(payload_gb: float, ranks: int, bandwidth_gbps: float, latency_us: float, traffic_factor: float) -> float:
    if payload_gb <= 0 or ranks <= 1 or bandwidth_gbps <= 0:
        return 0.0
    steps = ranks - 1
    return traffic_factor * payload_gb * 1_000_000_000 / (bandwidth_gbps * 1_000_000_000) * 1000.0 + steps * latency_us / 1000.0


def _scenario(row: TrainingScenario) -> dict[str, Any]:
    traffic = _traffic(row.strategy, row.params_b, row.model_bytes, row.grad_bytes, row.ranks)
    param_gb = row.params_b * row.model_bytes
    grad_gb = row.params_b * row.grad_bytes
    optimizer_gb = row.params_b * row.optimizer_bytes
    if row.strategy == "ddp":
        persistent_gb = param_gb + grad_gb + optimizer_gb
    elif row.strategy == "zero-2":
        persistent_gb = param_gb + grad_gb / row.ranks + optimizer_gb / row.ranks
    else:
        persistent_gb = param_gb / row.ranks + grad_gb / row.ranks + optimizer_gb / row.ranks + traffic["param_prefetch_gb"]
    activation_gb = row.activation_gb * (1.0 - row.checkpoint_fraction * 0.55)
    memory_gb_per_gpu = persistent_gb + activation_gb
    ar_ms = _ring_ms(traffic["all_reduce_gb"], row.ranks, row.bandwidth_gbps, row.latency_us, 2 * (row.ranks - 1) / row.ranks)
    rs_ms = _ring_ms(traffic["reduce_scatter_gb"], row.ranks, row.bandwidth_gbps, row.latency_us, (row.ranks - 1) / row.ranks)
    ag_ms = _ring_ms(traffic["all_gather_gb"], row.ranks, row.bandwidth_gbps, row.latency_us, (row.ranks - 1) / row.ranks)
    comm_ms = ar_ms + rs_ms + ag_ms
    overlap_fraction = 0.35
    if row.strategy == "zero-2":
        overlap_fraction = 0.45
    elif row.strategy in {"zero-3", "fsdp-full-shard"}:
        overlap_fraction = 0.85
    elif row.strategy == "tp-pp-fsdp":
        overlap_fraction = 0.80
    overlap_budget_ms = row.compute_ms * overlap_fraction
    exposed_comm_ms = max(0.0, comm_ms - overlap_budget_ms)
    bubble_ms = row.compute_ms * row.bubble_fraction
    step_time_ms = row.compute_ms + exposed_comm_ms + bubble_ms
    tokens_per_second = row.microbatch_tokens * row.ranks / max(step_time_ms / 1000.0, 1e-9)
    optimizer_state_savings = 1.0 - persistent_gb / max(param_gb + grad_gb + optimizer_gb, 1e-9)
    fits_80gb = memory_gb_per_gpu <= 76.0
    status = "passed" if fits_80gb and exposed_comm_ms <= row.compute_ms * 0.75 and row.bubble_fraction <= 0.15 else "review"
    return {
        "scenario_id": row.scenario_id,
        "status": status,
        "strategy": row.strategy,
        "topology": row.topology,
        "ranks": row.ranks,
        "params_b": row.params_b,
        "microbatch_tokens": row.microbatch_tokens,
        "precision": row.precision,
        "memory_gb_per_gpu": round(memory_gb_per_gpu, 6),
        "activation_gb_after_checkpoint": round(activation_gb, 6),
        "optimizer_state_savings": round(optimizer_state_savings, 6),
        "all_reduce_ms": round(ar_ms, 6),
        "reduce_scatter_ms": round(rs_ms, 6),
        "all_gather_ms": round(ag_ms, 6),
        "comm_ms": round(comm_ms, 6),
        "exposed_comm_ms": round(exposed_comm_ms, 6),
        "pipeline_bubble_ms": round(bubble_ms, 6),
        "step_time_ms": round(step_time_ms, 6),
        "tokens_per_second": round(tokens_per_second, 6),
        "checkpoint_fraction": row.checkpoint_fraction,
        "fits_80gb": fits_80gb,
        "traffic_gb": {key: round(value, 6) for key, value in traffic.items()},
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "topology_status": reports.get(SOURCE_REPORTS[0], {}).get("status", "missing"),
        "collectives_status": reports.get(SOURCE_REPORTS[1], {}).get("status", "missing"),
        "collectives_benchmark_status": reports.get(SOURCE_REPORTS[2], {}).get("status", "missing"),
        "hardware_capacity_status": reports.get(SOURCE_REPORTS[3], {}).get("status", "missing"),
        "scheduling_status": reports.get(SOURCE_REPORTS[4], {}).get("status", "missing"),
        "numerical_status": reports.get(SOURCE_REPORTS[5], {}).get("status", "missing"),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Distributed Training Optimizer",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "",
        "| scenario | strategy | ranks | memory GB/GPU | exposed comm ms | bubble ms | tokens/s | status |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| {row['scenario_id']} | {row['strategy']} | {row['ranks']} | {row['memory_gb_per_gpu']} | "
            f"{row['exposed_comm_ms']} | {row['pipeline_bubble_ms']} | {row['tokens_per_second']} | {row['status']} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_distributed_training_optimizer_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    scenarios = [_scenario(row) for row in SCENARIOS]
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    strategies = sorted({row["strategy"] for row in scenarios})
    checkpointed = sum(1 for row in scenarios if row["checkpoint_fraction"] > 0)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "training-optimizer-ready" if passed >= 4 and len(strategies) >= 5 and checkpointed >= 3 else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "review_scenarios": len(scenarios) - passed,
        "strategy_count": len(strategies),
        "checkpointed_scenarios": checkpointed,
        "strategies": strategies,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "recommendations": [
            "Teach DDP first as the memory-expensive baseline, then use ZeRO/FSDP to make optimizer-state sharding concrete.",
            "Pair reduce-scatter and all-gather timings with activation checkpointing so learners see the memory/communication exchange.",
            "Treat pipeline parallelism as a bubble-management problem, not only a way to fit model weights.",
            "Require measured torchrun, profiler, and GPU-run import evidence before accepting accelerator performance claims.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["distributed-training-optimizer", "distributed-collectives", "profiler-capture", "full-gpu-regression"],
            "commands": [
                "python3 scripts/run_distributed_training_optimizer.py",
                "python3 scripts/verify_distributed_training_optimizer.py",
                "torchrun --nproc_per_node=8 <fsdp_zero_training_step.py>",
                "nsys profile -o fsdp-zero-step torchrun --nproc_per_node=8 <fsdp_zero_training_step.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id distributed-training-optimizer --execute",
            ],
            "note": "Local report is source-ready; final acceptance needs measured FSDP/ZeRO step time, memory peak, reduce-scatter/all-gather overlap, and profiler traces.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
