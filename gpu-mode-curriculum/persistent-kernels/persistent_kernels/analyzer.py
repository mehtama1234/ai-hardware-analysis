from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "persistent-kernels"
REPORT_JSON = OUT / "persistent-kernels-report.json"
REPORT_MD = OUT / "reports" / "persistent-kernels-report.md"

SOURCE_REPORTS = [
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "autotune-db/autotune-db.json",
    "tensor-core-gemm/tensor-core-gemm-report.json",
    "compiler-runtime-inspection/compiler-runtime-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
    "attention-serving-stack/attention-serving-report.json",
]


@dataclass(frozen=True)
class PersistentScenario:
    scenario_id: str
    kernel_family: str
    strategy: str
    problem_size: str
    dtype: str
    sm_count: int
    cta_tile: str
    warps: int
    stages: int
    registers_per_thread: int
    shared_memory_kb: int
    hbm_bytes_mb: int
    l2_reuse_factor: float
    launch_us: float
    baseline_ms: float
    persistent_compute_ms: float
    occupancy_target: float
    producer_consumer: bool


SCENARIOS = [
    PersistentScenario("persistent-row-softmax-long-context", "softmax", "persistent-row", "batch=128 tokens=8192", "bf16/fp32-acc", 108, "1xrow", 4, 3, 48, 32, 512, 1.35, 12.0, 1.80, 1.10, 0.55, False),
    PersistentScenario("persistent-matmul-square", "matmul", "persistent-cta", "m=n=k=4096", "bf16", 108, "128x128x64", 8, 4, 96, 96, 768, 1.50, 14.0, 5.50, 3.90, 0.40, True),
    PersistentScenario("grouped-gemm-moe-experts", "grouped-gemm", "persistent-grouped", "64 experts, variable tokens", "fp16/bf16", 108, "64x128x64", 4, 4, 88, 80, 640, 1.80, 35.0, 4.80, 2.90, 0.45, True),
    PersistentScenario("persistent-layernorm-batch", "normalization", "persistent-vector", "batch=4096 hidden=4096", "fp32-acc", 80, "1x4096", 4, 2, 52, 24, 384, 1.25, 10.0, 1.20, 0.88, 0.60, False),
    PersistentScenario("persistent-attention-prefill", "attention", "persistent-block", "heads=32 seq=8192 d=128", "bf16", 108, "128x64", 8, 5, 112, 128, 1024, 1.65, 16.0, 8.00, 5.60, 0.35, True),
    PersistentScenario("persistent-overregistered-gemm-review", "matmul", "persistent-cta", "m=n=k=8192", "bf16", 108, "256x128x64", 8, 5, 164, 160, 1536, 1.60, 14.0, 15.00, 12.50, 0.22, True),
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _resident_ctas_per_sm(row: PersistentScenario) -> int:
    smem_limit_kb = 228
    register_file = 65536
    threads = row.warps * 32
    reg_limited = max(1, register_file // max(row.registers_per_thread * threads, 1))
    smem_limited = max(1, smem_limit_kb // max(row.shared_memory_kb, 1))
    return int(min(reg_limited, smem_limited, 8))


def _scenario(row: PersistentScenario) -> dict[str, Any]:
    resident = _resident_ctas_per_sm(row)
    occupancy_proxy = round(min(1.0, resident * row.warps / 16), 4)
    hbm_reduction = round(min(0.80, 1.0 - 1.0 / max(row.l2_reuse_factor, 1.0)), 4)
    speedup = round(row.baseline_ms / max(row.persistent_compute_ms, 1e-9), 4)
    launch_savings_ms = round((row.launch_us / 1000.0) * (8 if row.producer_consumer else 4), 4)
    persistent_fit = occupancy_proxy >= 0.30 and row.registers_per_thread <= 128 and row.shared_memory_kb <= 128
    passed = persistent_fit and speedup >= 1.15 and hbm_reduction >= 0.15
    return {
        "scenario_id": row.scenario_id,
        "evidence_kind": "analytical",
        "measured": False,
        "numerical_correctness_status": "not_executed",
        "kernel_family": row.kernel_family,
        "strategy": row.strategy,
        "problem_size": row.problem_size,
        "dtype": row.dtype,
        "sm_count": row.sm_count,
        "cta_tile": row.cta_tile,
        "warps": row.warps,
        "stages": row.stages,
        "registers_per_thread": row.registers_per_thread,
        "shared_memory_kb": row.shared_memory_kb,
        "hbm_bytes_mb": row.hbm_bytes_mb,
        "l2_reuse_factor": row.l2_reuse_factor,
        "baseline_ms": row.baseline_ms,
        "persistent_compute_ms": row.persistent_compute_ms,
        "launch_savings_ms": launch_savings_ms,
        "speedup_vs_baseline": speedup,
        "hbm_reduction": hbm_reduction,
        "resident_ctas_per_sm": resident,
        "occupancy_proxy": occupancy_proxy,
        "occupancy_target": row.occupancy_target,
        "producer_consumer": row.producer_consumer,
        "persistent_fit": persistent_fit,
        "status": "passed" if passed else "review",
        "gpu_evidence_required": ["sm__warps_active.avg.pct_of_peak_sustained_active", "launch__duration", "dram__bytes", "lts__t_sectors", "registers_per_thread", "shared_memory_per_cta"],
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "kernel_benchmarks": reports.get(SOURCE_REPORTS[0], {}).get("benchmark_count", 0),
        "autotune_records": reports.get(SOURCE_REPORTS[1], {}).get("record_count", 0),
        "tensor_core_scenarios": reports.get(SOURCE_REPORTS[2], {}).get("scenario_count", 0),
        "compiler_sources": reports.get(SOURCE_REPORTS[3], {}).get("source_count", 0),
        "profiler_kernels": reports.get(SOURCE_REPORTS[4], {}).get("kernel_count", 0),
        "attention_scenarios": reports.get(SOURCE_REPORTS[5], {}).get("scenario_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE persistent kernels",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "Evidence: analytical scenarios; timings are supplied constants, not device measurements. Passing status checks model assumptions, not numerical correctness.",
        "",
        "| scenario | family | strategy | occupancy | speedup | HBM reduction | resident CTA/SM | status |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| {row['scenario_id']} | {row['kernel_family']} | {row['strategy']} | "
            f"{row['occupancy_proxy']} | {row['speedup_vs_baseline']} | {row['hbm_reduction']} | "
            f"{row['resident_ctas_per_sm']} | {row['status']} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_persistent_kernel_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    scenarios = [_scenario(row) for row in SCENARIOS]
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    families = sorted({row["kernel_family"] for row in scenarios})
    producer_consumer = sum(1 for row in scenarios if row["producer_consumer"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_kind": "analytical",
        "measured": False,
        "gpu_execution_accepted": False,
        "status": "persistent-kernels-ready" if len(scenarios) >= 6 and passed >= 5 and len(families) >= 5 else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "family_count": len(families),
        "families": families,
        "producer_consumer_scenarios": producer_consumer,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "recommendations": [
            "Use persistent kernels only when residency and reuse offset occupancy loss.",
            "Treat register pressure and shared memory as hard launch-shape constraints, not late profiler trivia.",
            "Promote each scenario with Nsight Compute occupancy, launch duration, DRAM, L2, register, and shared-memory evidence.",
            "Keep a non-persistent baseline beside every persistent variant so regressions are visible.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["triton-persistent-softmax", "persistent-matmul", "grouped-gemm-moe", "ncu-occupancy", "launch-amortization"],
            "commands": [
                "python3 scripts/run_persistent_kernels.py",
                "python3 scripts/verify_persistent_kernels.py",
                "python3 kernel-benchmarks/kernels/triton/softmax_layernorm.py",
                "python3 kernel-benchmarks/kernels/triton/matmul_mlp.py",
                "ncu --set full -o persistent-kernels python3 <persistent_kernel_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id persistent-kernels --execute",
            ],
            "note": "Local report models persistent-kernel design constraints; final acceptance requires real CUDA/Triton profiler counters on a GPU host.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
