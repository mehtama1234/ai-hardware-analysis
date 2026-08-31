from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
AUTOTUNE_ROOT = ROOT / "autotune-db"
KERNEL_REPORT = ROOT / "kernel-benchmarks" / "reports" / "kernel-benchmark-report.json"
CUSTOM_OP_REPORT = ROOT / "custom-ops" / "reports" / "custom-op-report.json"
DB_JSON = AUTOTUNE_ROOT / "autotune-db.json"
REPORT_MD = AUTOTUNE_ROOT / "reports" / "autotune-report.md"


FAMILY_CONFIGS: dict[str, list[dict[str, Any]]] = {
    "memory": [
        {"id": "vectorized-128b", "block_size": 256, "num_warps": 8, "stages": 3, "factor": 0.82},
        {"id": "coalesced-basic", "block_size": 128, "num_warps": 4, "stages": 2, "factor": 1.0},
        {"id": "latency-small", "block_size": 64, "num_warps": 2, "stages": 2, "factor": 0.94},
    ],
    "reduction": [
        {"id": "warp-shuffle-tree", "block_size": 256, "num_warps": 8, "stages": 3, "factor": 0.78},
        {"id": "shared-memory-tree", "block_size": 128, "num_warps": 4, "stages": 2, "factor": 0.9},
        {"id": "two-pass-global", "block_size": 512, "num_warps": 8, "stages": 4, "factor": 1.08},
    ],
    "normalization": [
        {"id": "persistent-row", "block_size": 1024, "num_warps": 8, "stages": 4, "factor": 0.74},
        {"id": "one-row-per-program", "block_size": 256, "num_warps": 4, "stages": 3, "factor": 0.88},
        {"id": "small-row", "block_size": 128, "num_warps": 4, "stages": 2, "factor": 0.97},
    ],
    "matmul": [
        {"id": "tensorcore-64x64x32", "block_m": 64, "block_n": 64, "block_k": 32, "num_warps": 4, "stages": 4, "factor": 0.72},
        {"id": "tensorcore-128x64x32", "block_m": 128, "block_n": 64, "block_k": 32, "num_warps": 8, "stages": 4, "factor": 0.8},
        {"id": "simt-fallback", "block_m": 32, "block_n": 32, "block_k": 32, "num_warps": 4, "stages": 3, "factor": 1.0},
    ],
    "fusion": [
        {"id": "single-program-hidden", "block_size": 256, "num_warps": 4, "stages": 4, "factor": 0.76},
        {"id": "split-hidden", "block_size": 128, "num_warps": 4, "stages": 3, "factor": 0.86},
        {"id": "safe-eager-baseline", "block_size": 64, "num_warps": 2, "stages": 2, "factor": 1.0},
    ],
    "custom-op": [
        {"id": "fused-forward-backward", "block_size": 256, "num_warps": 8, "stages": 4, "factor": 0.7},
        {"id": "fused-forward-only", "block_size": 128, "num_warps": 4, "stages": 3, "factor": 0.82},
        {"id": "python-autograd-reference", "block_size": 64, "num_warps": 2, "stages": 2, "factor": 1.0},
    ],
}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_rows(family: str, measured_seconds: float) -> list[dict[str, Any]]:
    candidates = []
    for config in FAMILY_CONFIGS[family]:
        payload = {key: value for key, value in config.items() if key not in {"factor"}}
        estimated = measured_seconds * float(config["factor"])
        candidates.append(
            {
                "config": payload,
                "estimated_seconds": round(estimated, 10),
                "estimated_speedup_vs_measured": round(measured_seconds / max(estimated, 1e-12), 4),
            }
        )
    return sorted(candidates, key=lambda row: (row["estimated_seconds"], row["config"]["id"]))


def _kernel_record(row: dict[str, Any]) -> dict[str, Any]:
    measured = float(row.get("seconds", {}).get("median", 0.0))
    candidates = _candidate_rows(row["family"], measured)
    return {
        "id": row["id"],
        "family": row["family"],
        "shape_class": row["shape_class"],
        "params": row.get("params", {}),
        "source_report": "kernel-benchmarks/reports/kernel-benchmark-report.json",
        "measured_seconds": measured,
        "measured_device": row.get("result", {}).get("device", "unknown"),
        "candidate_count": len(candidates),
        "selected": candidates[0],
        "candidates": candidates,
        "promotion_targets": ["cuda", "triton"],
    }


def _custom_op_records(report: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for case in report.get("cases", []):
        measured = float(case.get("seconds", {}).get("fused", {}).get("median", 0.0))
        candidates = _candidate_rows("custom-op", measured)
        records.append(
            {
                "id": f"custom-op-{case['id']}",
                "family": "custom-op",
                "shape_class": case["id"],
                "params": {"dtype": case["dtype"], **case.get("shape", {})},
                "source_report": "custom-ops/reports/custom-op-report.json",
                "measured_seconds": measured,
                "measured_device": report.get("accelerator_readiness", {}).get("torch_device", "unknown"),
                "candidate_count": len(candidates),
                "selected": candidates[0],
                "candidates": candidates,
                "promotion_targets": ["torch-extension", "cuda"],
            }
        )
    return records


def select_config(database: dict[str, Any], family: str, shape_class: str | None = None) -> dict[str, Any]:
    candidates = [
        row
        for row in database.get("records", [])
        if row.get("family") == family and (shape_class is None or row.get("shape_class") == shape_class)
    ]
    if not candidates:
        raise KeyError(f"no autotune record for family={family!r} shape_class={shape_class!r}")
    return sorted(candidates, key=lambda row: row["selected"]["estimated_seconds"])[0]


def render_markdown(database: dict[str, Any]) -> str:
    lines = [
        "# Autotuning Database Report",
        "",
        f"Generated: `{database['generated_at']}`",
        f"Records: `{database['record_count']}`",
        f"Families: `{', '.join(database['families'])}`",
        "",
        "| record | family | shape | selected config | measured s | estimated s | speedup | targets |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for record in database["records"]:
        selected = record["selected"]
        lines.append(
            "| "
            f"{record['id']} | {record['family']} | {record['shape_class']} | {selected['config']['id']} | "
            f"{record['measured_seconds']:.8f} | {selected['estimated_seconds']:.8f} | "
            f"{selected['estimated_speedup_vs_measured']} | {', '.join(record['promotion_targets'])} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def build_database() -> dict[str, Any]:
    AUTOTUNE_ROOT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    kernel_report = load_json(KERNEL_REPORT, {"benchmarks": []})
    custom_report = load_json(CUSTOM_OP_REPORT, {"cases": []})
    records = [_kernel_record(row) for row in kernel_report.get("benchmarks", []) if row.get("status") == "passed"]
    records.extend(_custom_op_records(custom_report))
    families = sorted({row["family"] for row in records})
    database = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
        "families": families,
        "source_reports": [
            "kernel-benchmarks/reports/kernel-benchmark-report.json",
            "custom-ops/reports/custom-op-report.json",
        ],
        "selector_contract": {
            "required_record_fields": ["id", "family", "shape_class", "params", "selected", "candidates", "promotion_targets"],
            "selection_rule": "lowest estimated_seconds among candidate configs for the record",
            "regression_rule": "selected config must estimate speedup >= 1.0 versus measured local baseline",
        },
        "records": records,
    }
    DB_JSON.write_text(json.dumps(database, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(database), encoding="utf-8")
    return database
