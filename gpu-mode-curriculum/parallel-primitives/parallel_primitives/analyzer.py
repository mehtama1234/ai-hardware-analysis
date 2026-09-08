from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "parallel-primitives"
REPORT_JSON = OUT / "parallel-primitives-report.json"
REPORT_MD = OUT / "reports" / "parallel-primitives-report.md"

SOURCE_REPORTS = [
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "autotune-db/autotune-db.json",
    "compiler-runtime-inspection/compiler-runtime-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
    "persistent-kernels/persistent-kernels-report.json",
]


@dataclass(frozen=True)
class PrimitiveScenario:
    scenario_id: str
    primitive: str
    algorithm: str
    elements: int
    dtype: str
    bytes_per_element: int
    passes: int
    block_threads: int
    items_per_thread: int
    shared_memory_kb: int
    registers_per_thread: int
    atomics_per_element: float
    baseline_ms: float
    optimized_ms: float
    correctness: str
    stable_order_required: bool


SCENARIOS = [
    PrimitiveScenario("warp-block-reduction-bf16", "reduction", "warp-shuffle-block-tree", 16_777_216, "bf16/fp32-acc", 2, 2, 256, 4, 16, 40, 0.0, 1.90, 1.10, "relative-error<=1e-3", False),
    PrimitiveScenario("exclusive-prefix-scan-int32", "scan", "blelloch-hillis-steele-hybrid", 8_388_608, "int32", 4, 3, 256, 4, 32, 52, 0.0, 2.80, 1.70, "exact", True),
    PrimitiveScenario("predicate-stream-compaction", "compaction", "scan-scatter", 16_777_216, "int32+mask", 5, 3, 256, 4, 40, 56, 0.0, 3.60, 2.20, "stable-filter", True),
    PrimitiveScenario("radix-sort-pass-32bit-keys", "sort", "histogram-scan-scatter-radix8", 4_194_304, "uint32", 4, 4, 256, 4, 48, 72, 0.0, 5.80, 3.80, "sorted-and-stable", True),
    PrimitiveScenario("shared-histogram-token-bins", "histogram", "block-private-shared-atomics", 33_554_432, "uint16", 2, 2, 256, 8, 64, 64, 0.125, 4.40, 2.70, "bin-counts-exact", False),
    PrimitiveScenario("segmented-reduce-ragged-batches", "segmented-reduction", "head-flag-scan-reduce", 2_097_152, "fp32", 4, 3, 128, 8, 24, 68, 0.0, 2.20, 1.55, "relative-error<=1e-5", False),
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario(row: PrimitiveScenario) -> dict[str, Any]:
    total_bytes = row.elements * row.bytes_per_element * row.passes
    memory_traffic_mb = round(total_bytes / 1_000_000, 4)
    bandwidth_proxy_gbps = round(total_bytes / max(row.optimized_ms, 1e-9) / 1_000_000, 4)
    work_efficiency = round(row.baseline_ms / max(row.optimized_ms, 1e-9), 4)
    occupancy_proxy = round(min(1.0, (row.block_threads / 256) * (96 / max(row.registers_per_thread, 1)) * (96 / max(row.shared_memory_kb, 1))), 4)
    atomic_pressure = round(row.atomics_per_element * row.elements / 1_000_000, 4)
    passed = work_efficiency >= 1.20 and occupancy_proxy >= 0.35 and row.shared_memory_kb <= 96 and row.registers_per_thread <= 96
    return {
        "scenario_id": row.scenario_id,
        "evidence_kind": "analytical",
        "measured": False,
        "numerical_correctness_status": "not_executed",
        "primitive": row.primitive,
        "algorithm": row.algorithm,
        "elements": row.elements,
        "dtype": row.dtype,
        "passes": row.passes,
        "block_threads": row.block_threads,
        "items_per_thread": row.items_per_thread,
        "shared_memory_kb": row.shared_memory_kb,
        "registers_per_thread": row.registers_per_thread,
        "atomics_per_element": row.atomics_per_element,
        "baseline_ms": row.baseline_ms,
        "optimized_ms": row.optimized_ms,
        "work_efficiency": work_efficiency,
        "memory_traffic_mb": memory_traffic_mb,
        "bandwidth_proxy_gbps": bandwidth_proxy_gbps,
        "occupancy_proxy": occupancy_proxy,
        "atomic_pressure_millions": atomic_pressure,
        "correctness": row.correctness,
        "stable_order_required": row.stable_order_required,
        "status": "passed" if passed else "review",
        "gpu_evidence_required": ["dram__bytes", "sm__throughput", "l1tex__data_bank_conflicts", "shared_load_transactions", "atomic_transactions", "launch__duration"],
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "kernel_benchmarks": reports.get(SOURCE_REPORTS[0], {}).get("benchmark_count", 0),
        "autotune_records": reports.get(SOURCE_REPORTS[1], {}).get("record_count", 0),
        "compiler_sources": reports.get(SOURCE_REPORTS[2], {}).get("source_count", 0),
        "profiler_rows": reports.get(SOURCE_REPORTS[3], {}).get("row_count", 0),
        "persistent_scenarios": reports.get(SOURCE_REPORTS[4], {}).get("scenario_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE parallel primitives",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "Evidence: analytical scenarios; timings are supplied constants, not device measurements. Passing status checks model assumptions, not numerical correctness.",
        "",
        "| scenario | primitive | algorithm | efficiency | bandwidth proxy GB/s | occupancy | status |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| {row['scenario_id']} | {row['primitive']} | {row['algorithm']} | "
            f"{row['work_efficiency']} | {row['bandwidth_proxy_gbps']} | {row['occupancy_proxy']} | {row['status']} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_parallel_primitives_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    scenarios = [_scenario(row) for row in SCENARIOS]
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    primitives = sorted({row["primitive"] for row in scenarios})
    stable = sum(1 for row in scenarios if row["stable_order_required"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_kind": "analytical",
        "measured": False,
        "gpu_execution_accepted": False,
        "status": "parallel-primitives-ready" if len(scenarios) >= 6 and passed >= 5 and len(primitives) >= 6 else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "primitive_count": len(primitives),
        "primitives": primitives,
        "stable_order_scenarios": stable,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "recommendations": [
            "Teach scan, histogram, compaction, and radix sort as composable building blocks, not isolated tricks.",
            "Track memory traffic and synchronization depth beside correctness because most primitive regressions are bandwidth or barrier problems.",
            "Require stable-order checks for compaction and radix sort before using the primitive in token routing or data preprocessing.",
            "Promote with Nsight Compute or rocprof counters for DRAM bytes, shared-memory bank conflicts, atomics, and launch duration.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["block-reduction", "prefix-scan", "stream-compaction", "radix-sort", "histogram", "segmented-reduce"],
            "commands": [
                "python3 scripts/run_parallel_primitives.py",
                "python3 scripts/verify_parallel_primitives.py",
                "python3 kernel-benchmarks/kernels/triton/reduction.py",
                "python3 kernel-benchmarks/kernels/cuda/reduction.cu",
                "ncu --set full -o parallel-primitives python3 <parallel_primitives_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id parallel-primitives --execute",
            ],
            "note": "Local report models primitive design constraints; final acceptance requires measured CUDA/Triton/HIP primitive runs and profiler counters on a GPU host.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
