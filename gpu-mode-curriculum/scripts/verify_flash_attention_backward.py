#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "flash-attention-backward" / "flash-attention-backward-report.json"
REPORT_MD = ROOT / "flash-attention-backward" / "reports" / "flash-attention-backward-report.md"
SITE_PAGE = ROOT / "site" / "flash-attention-backward.html"
REQUIRED_SOURCES = {
    "attention-serving-stack/attention-serving-report.json",
    "parallel-primitives/parallel-primitives-report.json",
    "persistent-kernels/persistent-kernels-report.json",
    "numerical-reproducibility/numerical-reproducibility-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
    "tensor-core-gemm/tensor-core-gemm-report.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_flash_attention_backward.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    scenarios = report.get("scenarios", [])
    require(report.get("status") == "flash-attention-backward-ready", "FlashAttention backward report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 6, "scenario count mismatch")
    require(report.get("passed_scenarios", 0) >= 5, "too few passing backward scenarios")
    require(report.get("dropout_scenarios", 0) >= 1, "dropout backward coverage is missing")
    require(report.get("grouped_query_scenarios", 0) >= 1, "GQA backward coverage is missing")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing source reports")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    for row in scenarios:
        sid = row.get("scenario_id")
        require({"dQ", "dK", "dV", "dSoftmax"}.issubset(set(row.get("gradient_paths", []))), f"{sid} missing gradient paths")
        require(row.get("speedup_vs_baseline", 0) > 1.0, f"{sid} lacks speedup")
        require(row.get("hbm_reduction", 0) > 0, f"{sid} lacks HBM reduction")
        require(row.get("occupancy_proxy", 0) > 0, f"{sid} lacks occupancy")
        require(row.get("max_abs_error", 1) <= 0.02, f"{sid} error too high")
        require(row.get("gpu_evidence_required"), f"{sid} lacks profiler evidence requirements")
    require(REPORT_MD.exists(), "missing FlashAttention backward markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE FlashAttention backward" in page, "FlashAttention backward site page missing title")
        require("dQ" in page and "dK" in page and "dV" in page and "recompute" in page, "site page missing backward evidence")
    print(
        json.dumps(
            {
                "facts": {
                    "scenarios": report.get("scenario_count"),
                    "passed": report.get("passed_scenarios"),
                    "dropout": report.get("dropout_scenarios"),
                    "grouped_query": report.get("grouped_query_scenarios"),
                    "status": report.get("status"),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE FlashAttention backward verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
