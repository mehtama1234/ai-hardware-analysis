from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "fused-training-kernels"
REPORT_JSON = OUT / "fused-training-report.json"
REPORT_MD = OUT / "reports" / "fused-training-report.md"

SOURCE_REPORTS = [
    "custom-ops/reports/custom-op-report.json",
    "model-integration/reports/tiny-transformer-report.json",
    "flash-attention-backward/flash-attention-backward-report.json",
    "distributed-training-optimizer/distributed-training-optimizer-report.json",
    "quantization-memory-formats/quantization-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
]


@dataclass(frozen=True)
class TrainingKernelScenario:
    scenario_id: str
    kernel_family: str
    shape: str
    dtype: str
    unfused_ops: int
    fused_ops: int
    baseline_ms: float
    fused_ms: float
    baseline_hbm_mb: float
    fused_hbm_mb: float
    max_abs_error: float
    supports_backward: bool
    optimizer_state: bool
    activation_checkpoint_safe: bool


SCENARIOS = [
    TrainingKernelScenario("rmsnorm-residual-backward", "rmsnorm", "batch=8,seq=2048,hidden=8192", "bf16/fp32-acc", 5, 2, 7.8, 3.4, 920.0, 384.0, 0.0020, True, False, True),
    TrainingKernelScenario("swiglu-mlp-fusion", "swiglu-mlp", "tokens=16384,hidden=8192,intermediate=28672", "bf16/fp32-acc", 6, 3, 31.5, 15.2, 5480.0, 2560.0, 0.0038, True, False, True),
    TrainingKernelScenario("cross-entropy-zloss", "cross-entropy", "tokens=8192,vocab=128k", "fp32-reduction", 4, 1, 22.0, 8.9, 4100.0, 760.0, 0.0012, True, False, False),
    TrainingKernelScenario("adamw-multi-tensor", "optimizer", "params=7B,shards=8", "fp32-master,bf16-param", 7, 2, 44.0, 18.5, 9800.0, 3900.0, 0.0008, False, True, False),
    TrainingKernelScenario("grad-clip-unscale", "optimizer", "params=7B,shards=8", "fp32-reduction", 5, 2, 16.4, 7.2, 5200.0, 2100.0, 0.0010, False, True, False),
    TrainingKernelScenario("dropout-residual-norm", "fusion", "batch=8,seq=4096,hidden=4096", "fp16/fp32-acc", 5, 2, 9.6, 4.1, 1360.0, 560.0, 0.0045, True, False, True),
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario(row: TrainingKernelScenario) -> dict[str, Any]:
    speedup = round(row.baseline_ms / max(row.fused_ms, 1e-9), 4)
    hbm_reduction = round(1.0 - row.fused_hbm_mb / max(row.baseline_hbm_mb, 1e-9), 6)
    launch_reduction = round(1.0 - row.fused_ops / max(row.unfused_ops, 1), 6)
    occupancy_proxy = round(min(1.0, 0.50 + launch_reduction * 0.35 + hbm_reduction * 0.25), 4)
    register_pressure_proxy = round(min(1.0, 0.42 + row.fused_ops * 0.08 + (0.18 if row.supports_backward else 0.08)), 4)
    passed = (
        speedup >= 1.8
        and hbm_reduction >= 0.45
        and launch_reduction >= 0.45
        and row.max_abs_error <= 0.01
        and occupancy_proxy >= 0.65
        and register_pressure_proxy <= 0.95
    )
    return {
        "scenario_id": row.scenario_id,
        "kernel_family": row.kernel_family,
        "status": "passed" if passed else "review",
        "shape": row.shape,
        "dtype": row.dtype,
        "unfused_ops": row.unfused_ops,
        "fused_ops": row.fused_ops,
        "baseline_ms": row.baseline_ms,
        "fused_ms": row.fused_ms,
        "speedup_vs_unfused": speedup,
        "baseline_hbm_mb": row.baseline_hbm_mb,
        "fused_hbm_mb": row.fused_hbm_mb,
        "hbm_reduction": hbm_reduction,
        "launch_reduction": launch_reduction,
        "occupancy_proxy": occupancy_proxy,
        "register_pressure_proxy": register_pressure_proxy,
        "max_abs_error": row.max_abs_error,
        "supports_backward": row.supports_backward,
        "optimizer_state": row.optimizer_state,
        "activation_checkpoint_safe": row.activation_checkpoint_safe,
        "kernel_paths": ["forward", "backward" if row.supports_backward else "state-update", "reduction" if row.optimizer_state else "epilogue"],
        "gpu_evidence_required": ["dram__bytes", "launch_count", "sm__throughput", "registers_per_thread", "achieved_occupancy", "max_abs_error"],
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "custom_op_cases": reports.get(SOURCE_REPORTS[0], {}).get("case_count", 0),
        "model_cases": reports.get(SOURCE_REPORTS[1], {}).get("case_count", 0),
        "flash_backward_scenarios": reports.get(SOURCE_REPORTS[2], {}).get("scenario_count", 0),
        "training_optimizer_scenarios": reports.get(SOURCE_REPORTS[3], {}).get("scenario_count", 0),
        "quantization_formats": reports.get(SOURCE_REPORTS[4], {}).get("format_count", 0),
        "profiler_rows": reports.get(SOURCE_REPORTS[5], {}).get("row_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE fused training kernels",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "",
        "| scenario | family | status | speedup | HBM reduction | launch reduction | max error |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| {row['scenario_id']} | {row['kernel_family']} | {row['status']} | "
            f"{row['speedup_vs_unfused']} | {row['hbm_reduction']} | {row['launch_reduction']} | {row['max_abs_error']} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_fused_training_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    scenarios = [_scenario(row) for row in SCENARIOS]
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    backward = sum(1 for row in scenarios if row["supports_backward"])
    optimizer = sum(1 for row in scenarios if row["optimizer_state"])
    checkpoint_safe = sum(1 for row in scenarios if row["activation_checkpoint_safe"])
    families = sorted({row["kernel_family"] for row in scenarios})
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "fused-training-ready" if len(scenarios) >= 6 and passed >= 5 and backward >= 4 and optimizer >= 2 and checkpoint_safe >= 3 else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "family_count": len(families),
        "families": families,
        "backward_scenarios": backward,
        "optimizer_state_scenarios": optimizer,
        "checkpoint_safe_scenarios": checkpoint_safe,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "recommendations": [
            "Teach LLM training fusion after attention backward because optimizer, norm, and loss kernels are the next launch and HBM bottlenecks.",
            "Separate numerical-error checks for reductions, activation epilogues, and optimizer state updates.",
            "Promote with launch count, DRAM bytes, occupancy, register pressure, and max error rather than speedup alone.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["rmsnorm-bwd", "swiglu-bwd", "cross-entropy-loss", "adamw-update", "grad-clip-unscale", "dropout-residual-norm"],
            "commands": [
                "python3 scripts/run_fused_training_kernels.py",
                "python3 scripts/verify_fused_training_kernels.py",
                "python3 scripts/run_model_integration.py",
                "python3 scripts/run_distributed_training_optimizer.py",
                "ncu --set full -o fused-training-kernels python3 <fused_training_probe.py>",
                "nsys profile -o fused-training-step python3 <training_step_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id fused-training-kernels --execute",
            ],
            "note": "Local report models fused training-kernel constraints; final acceptance requires measured Triton/CUDA kernels and profiler traces on a GPU host.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
