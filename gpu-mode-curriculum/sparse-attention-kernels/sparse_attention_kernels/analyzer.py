from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "sparse-attention-kernels"
REPORT_JSON = OUT / "sparse-attention-report.json"
REPORT_MD = OUT / "reports" / "sparse-attention-report.md"

SOURCE_REPORTS = [
    "attention-serving-stack/attention-serving-report.json",
    "flash-attention-backward/flash-attention-backward-report.json",
    "kv-cache-paged-attention/kv-cache-report.json",
    "parallel-primitives/parallel-primitives-report.json",
    "moe-routing-all-to-all/moe-routing-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
]


@dataclass(frozen=True)
class SparseScenario:
    scenario_id: str
    pattern: str
    batch: int
    heads: int
    seq_q: int
    seq_kv: int
    head_dim: int
    density: float
    tile_q: int
    tile_k: int
    metadata_bytes_per_block: int
    baseline_ms: float
    sparse_ms: float
    max_abs_error: float
    requires_ragged: bool
    supports_backward: bool
    supports_decode: bool


SCENARIOS = [
    SparseScenario("block-sparse-prefill", "block-sparse", 4, 16, 4096, 4096, 128, 0.25, 64, 128, 8, 52.0, 19.0, 0.0028, False, True, False),
    SparseScenario("sliding-window-long-context", "sliding-window", 2, 32, 8192, 8192, 128, 0.16, 64, 128, 4, 118.0, 33.5, 0.0032, False, True, False),
    SparseScenario("dilated-global-hybrid", "dilated-global", 2, 24, 8192, 8192, 96, 0.22, 64, 128, 8, 91.0, 31.0, 0.0045, False, True, False),
    SparseScenario("ragged-paged-decode", "ragged-paged", 16, 32, 1, 16384, 128, 0.12, 1, 128, 12, 8.8, 3.1, 0.0025, True, False, True),
    SparseScenario("neighborhood-vision-attention", "neighborhood", 8, 12, 4096, 4096, 64, 0.18, 64, 64, 6, 37.0, 13.8, 0.0038, False, True, False),
    SparseScenario("topk-routing-attention", "topk", 4, 16, 2048, 2048, 128, 0.20, 64, 128, 16, 26.0, 10.7, 0.0065, True, True, False),
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario(row: SparseScenario) -> dict[str, Any]:
    dense_score_elements = row.batch * row.heads * row.seq_q * row.seq_kv
    sparse_score_elements = int(dense_score_elements * row.density)
    blocks_q = (row.seq_q + row.tile_q - 1) // row.tile_q
    blocks_k = (row.seq_kv + row.tile_k - 1) // row.tile_k
    dense_hbm = dense_score_elements * 4 * 2
    sparse_hbm = sparse_score_elements * 4 * 2 + blocks_q * blocks_k * row.metadata_bytes_per_block * row.batch * row.heads
    hbm_reduction = round(1.0 - sparse_hbm / max(dense_hbm, 1), 6)
    metadata_overhead = round((sparse_hbm - sparse_score_elements * 8) / max(sparse_hbm, 1), 6)
    speedup = round(row.baseline_ms / max(row.sparse_ms, 1e-9), 4)
    occupancy_proxy = round(min(1.0, 0.42 + row.density * 1.35 + (0.08 if row.tile_q >= 64 else 0.0)), 4)
    load_balance = round(max(0.0, 1.0 - abs(0.24 - row.density) * 1.4 - (0.08 if row.requires_ragged else 0.0)), 4)
    passed = (
        speedup >= 1.8
        and hbm_reduction >= 0.55
        and row.max_abs_error <= 0.01
        and occupancy_proxy >= 0.50
        and load_balance >= 0.75
    )
    return {
        "scenario_id": row.scenario_id,
        "pattern": row.pattern,
        "status": "passed" if passed else "review",
        "shape": {
            "batch": row.batch,
            "heads": row.heads,
            "seq_q": row.seq_q,
            "seq_kv": row.seq_kv,
            "head_dim": row.head_dim,
        },
        "tiles": {
            "tile_q": row.tile_q,
            "tile_k": row.tile_k,
            "blocks_q": blocks_q,
            "blocks_k": blocks_k,
        },
        "density": row.density,
        "baseline_ms": row.baseline_ms,
        "sparse_ms": row.sparse_ms,
        "speedup_vs_dense": speedup,
        "hbm_reduction": hbm_reduction,
        "metadata_overhead": metadata_overhead,
        "occupancy_proxy": occupancy_proxy,
        "load_balance_proxy": load_balance,
        "max_abs_error": row.max_abs_error,
        "requires_ragged": row.requires_ragged,
        "supports_backward": row.supports_backward,
        "supports_decode": row.supports_decode,
        "kernel_paths": ["metadata-build", "qk-sparse", "online-softmax", "pv-sparse"],
        "gpu_evidence_required": ["dram__bytes", "branch_efficiency", "warp_execution_efficiency", "metadata_l2_hit_rate", "active_blocks_per_sm", "max_abs_error"],
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "attention_scenarios": reports.get(SOURCE_REPORTS[0], {}).get("scenario_count", 0),
        "flash_backward_scenarios": reports.get(SOURCE_REPORTS[1], {}).get("scenario_count", 0),
        "kv_cache_scenarios": reports.get(SOURCE_REPORTS[2], {}).get("scenario_count", 0),
        "primitive_scenarios": reports.get(SOURCE_REPORTS[3], {}).get("scenario_count", 0),
        "moe_scenarios": reports.get(SOURCE_REPORTS[4], {}).get("scenario_count", 0),
        "profiler_rows": reports.get(SOURCE_REPORTS[5], {}).get("row_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE sparse attention kernels",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "",
        "| scenario | pattern | status | density | speedup | HBM reduction | load balance | max error |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| {row['scenario_id']} | {row['pattern']} | {row['status']} | "
            f"{row['density']} | {row['speedup_vs_dense']} | {row['hbm_reduction']} | "
            f"{row['load_balance_proxy']} | {row['max_abs_error']} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_sparse_attention_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    scenarios = [_scenario(row) for row in SCENARIOS]
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    ragged = sum(1 for row in scenarios if row["requires_ragged"])
    backward = sum(1 for row in scenarios if row["supports_backward"])
    decode = sum(1 for row in scenarios if row["supports_decode"])
    patterns = sorted({row["pattern"] for row in scenarios})
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "sparse-attention-ready" if len(scenarios) >= 6 and passed >= 5 and ragged >= 1 and backward >= 4 and decode >= 1 else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "pattern_count": len(patterns),
        "patterns": patterns,
        "ragged_scenarios": ragged,
        "backward_scenarios": backward,
        "decode_scenarios": decode,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "recommendations": [
            "Teach sparse attention as metadata plus online-softmax, not just as fewer QK scores.",
            "Separate block-sparse, sliding-window, ragged decode, and top-k routing because their load-balance failures differ.",
            "Promote with branch efficiency, warp execution efficiency, metadata cache hit rate, DRAM bytes, and numerical error.",
            "Use dense attention and FlashAttention backward reports as baselines before accepting sparse-kernel wins.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["metadata-builder", "sparse-qk", "sparse-online-softmax", "sparse-pv", "ragged-decode", "sparse-backward"],
            "commands": [
                "python3 scripts/run_sparse_attention_kernels.py",
                "python3 scripts/verify_sparse_attention_kernels.py",
                "python3 scripts/run_attention_serving_stack.py",
                "python3 scripts/run_flash_attention_backward.py",
                "ncu --set full -o sparse-attention-kernels python3 <sparse_attention_probe.py>",
                "nsys profile -o sparse-attention-ragged-decode python3 <ragged_decode_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id sparse-attention-kernels --execute",
            ],
            "note": "Local report models sparse-kernel design constraints; final acceptance requires measured sparse attention kernels and profiler evidence on a GPU host.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
