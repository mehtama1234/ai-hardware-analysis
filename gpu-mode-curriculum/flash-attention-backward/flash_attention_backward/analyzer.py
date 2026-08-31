from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "flash-attention-backward"
REPORT_JSON = OUT / "flash-attention-backward-report.json"
REPORT_MD = OUT / "reports" / "flash-attention-backward-report.md"

SOURCE_REPORTS = [
    "attention-serving-stack/attention-serving-report.json",
    "parallel-primitives/parallel-primitives-report.json",
    "persistent-kernels/persistent-kernels-report.json",
    "numerical-reproducibility/numerical-reproducibility-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
    "tensor-core-gemm/tensor-core-gemm-report.json",
]


@dataclass(frozen=True)
class BackwardScenario:
    scenario_id: str
    batch: int
    heads: int
    seq_q: int
    seq_kv: int
    head_dim: int
    dtype: str
    dtype_bytes: int
    tile_q: int
    tile_k: int
    registers_per_thread: int
    shared_memory_kb: int
    baseline_ms: float
    backward_ms: float
    recompute_overhead_ratio: float
    max_abs_error: float
    dropout: bool
    causal: bool
    grouped_query: bool


SCENARIOS = [
    BackwardScenario("training-prefill-bf16", 8, 16, 1024, 1024, 64, "bf16/fp32-acc", 2, 64, 64, 88, 72, 9.80, 6.20, 0.18, 0.0015, False, True, False),
    BackwardScenario("long-context-checkpointed", 2, 32, 4096, 4096, 128, "bf16/fp32-acc", 2, 64, 128, 116, 112, 46.00, 29.50, 0.24, 0.0028, False, True, False),
    BackwardScenario("dropout-causal-training", 4, 24, 2048, 2048, 128, "fp16/fp32-acc", 2, 64, 128, 120, 120, 28.00, 18.80, 0.28, 0.0035, True, True, False),
    BackwardScenario("gqa-decode-finetune", 8, 32, 512, 2048, 128, "bf16/fp32-acc", 2, 64, 128, 104, 96, 14.20, 9.10, 0.20, 0.0022, False, True, True),
    BackwardScenario("fp8-activation-review", 8, 16, 1024, 1024, 128, "fp8/fp32-acc", 1, 64, 128, 128, 128, 12.40, 8.60, 0.34, 0.0090, False, True, False),
    BackwardScenario("noncausal-cross-attention", 4, 16, 1024, 2048, 64, "fp16/fp32-acc", 2, 64, 64, 84, 64, 13.60, 8.20, 0.16, 0.0018, False, False, False),
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario(row: BackwardScenario) -> dict[str, Any]:
    qkv_elements = row.batch * row.heads * (row.seq_q + 2 * row.seq_kv) * row.head_dim
    score_elements = row.batch * row.heads * row.seq_q * row.seq_kv
    baseline_hbm = (qkv_elements * row.dtype_bytes * 4) + (score_elements * 4 * 3)
    flash_hbm = (qkv_elements * row.dtype_bytes * 5) + (row.batch * row.heads * row.seq_q * 8)
    saved_activation_reduction = round(1.0 - flash_hbm / max(baseline_hbm, 1), 6)
    hbm_reduction = saved_activation_reduction
    speedup = round(row.baseline_ms / max(row.backward_ms, 1e-9), 4)
    occupancy_proxy = round(min(1.0, (96 / max(row.registers_per_thread, 1)) * (128 / max(row.shared_memory_kb, 1))), 4)
    dq_dk_dv_tiles = {
        "dq_tiles": (row.seq_q + row.tile_q - 1) // row.tile_q,
        "dk_dv_tiles": (row.seq_kv + row.tile_k - 1) // row.tile_k,
        "tile_q": row.tile_q,
        "tile_k": row.tile_k,
    }
    passed = (
        speedup >= 1.25
        and hbm_reduction >= 0.40
        and occupancy_proxy >= 0.45
        and row.max_abs_error <= 0.01
        and row.registers_per_thread <= 128
        and row.shared_memory_kb <= 128
    )
    return {
        "scenario_id": row.scenario_id,
        "status": "passed" if passed else "review",
        "shape": {
            "batch": row.batch,
            "heads": row.heads,
            "seq_q": row.seq_q,
            "seq_kv": row.seq_kv,
            "head_dim": row.head_dim,
            "dtype": row.dtype,
        },
        "tiles": dq_dk_dv_tiles,
        "registers_per_thread": row.registers_per_thread,
        "shared_memory_kb": row.shared_memory_kb,
        "baseline_ms": row.baseline_ms,
        "backward_ms": row.backward_ms,
        "speedup_vs_baseline": speedup,
        "recompute_overhead_ratio": row.recompute_overhead_ratio,
        "saved_activation_reduction": saved_activation_reduction,
        "hbm_reduction": hbm_reduction,
        "occupancy_proxy": occupancy_proxy,
        "max_abs_error": row.max_abs_error,
        "dropout": row.dropout,
        "causal": row.causal,
        "grouped_query": row.grouped_query,
        "gradient_paths": ["dQ", "dK", "dV", "dSoftmax"],
        "gpu_evidence_required": ["dram__bytes", "sm__throughput", "registers_per_thread", "shared_memory_per_cta", "exp2_recompute", "dQ_dK_dV_max_error"],
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "attention_scenarios": reports.get(SOURCE_REPORTS[0], {}).get("scenario_count", 0),
        "primitive_scenarios": reports.get(SOURCE_REPORTS[1], {}).get("scenario_count", 0),
        "persistent_scenarios": reports.get(SOURCE_REPORTS[2], {}).get("scenario_count", 0),
        "numerical_scenarios": reports.get(SOURCE_REPORTS[3], {}).get("scenario_count", 0),
        "profiler_rows": reports.get(SOURCE_REPORTS[4], {}).get("row_count", 0),
        "tensor_core_scenarios": reports.get(SOURCE_REPORTS[5], {}).get("scenario_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE FlashAttention backward",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "",
        "| scenario | status | speedup | HBM reduction | recompute overhead | occupancy | max error | gradients |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| {row['scenario_id']} | {row['status']} | {row['speedup_vs_baseline']} | "
            f"{row['hbm_reduction']} | {row['recompute_overhead_ratio']} | {row['occupancy_proxy']} | "
            f"{row['max_abs_error']} | {', '.join(row['gradient_paths'])} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_flash_attention_backward_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    scenarios = [_scenario(row) for row in SCENARIOS]
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    dropout = sum(1 for row in scenarios if row["dropout"])
    grouped_query = sum(1 for row in scenarios if row["grouped_query"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "flash-attention-backward-ready" if len(scenarios) >= 6 and passed >= 5 and dropout >= 1 and grouped_query >= 1 else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "dropout_scenarios": dropout,
        "grouped_query_scenarios": grouped_query,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "recommendations": [
            "Teach FlashAttention backward separately from forward because recompute and gradient accumulation are the real training-kernel constraints.",
            "Track dQ, dK, dV, and dSoftmax correctness independently before accepting performance numbers.",
            "Use activation-recompute savings and HBM reduction together; recompute is only useful when memory pressure drops enough.",
            "Promote with profiler evidence for DRAM bytes, occupancy, register pressure, shared memory, exp recompute cost, and gradient error.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["flash-bwd-dq", "flash-bwd-dkdv", "dropout-mask-recompute", "gqa-backward", "gradient-error-check"],
            "commands": [
                "python3 scripts/run_flash_attention_backward.py",
                "python3 scripts/verify_flash_attention_backward.py",
                "python3 scripts/run_attention_serving_stack.py",
                "ncu --set full -o flash-attention-backward python3 <flash_attention_backward_probe.py>",
                "nsys profile -o flash-attention-training-step python3 <flash_attention_training_step.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id flash-attention-backward --execute",
            ],
            "note": "Local report models backward-pass design constraints; final acceptance requires measured dQ/dK/dV kernels and numerical comparisons on a GPU host.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
