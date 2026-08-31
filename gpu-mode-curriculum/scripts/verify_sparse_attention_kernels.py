#!/usr/bin/env python3
"""Verify the sparse attention kernel report."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "sparse-attention-kernels" / "sparse-attention-report.json"
REPORT_MD = ROOT / "sparse-attention-kernels" / "reports" / "sparse-attention-report.md"
SITE_PAGE = ROOT / "site" / "sparse-attention-kernels.html"
REQUIRED_PATTERNS = {"block-sparse", "sliding-window", "dilated-global", "ragged-paged", "neighborhood", "topk"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_sparse_attention_kernels.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    scenarios = report.get("scenarios", [])
    require(report.get("status") == "sparse-attention-ready", "sparse attention report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 6, "scenario count mismatch")
    require(report.get("passed_scenarios", 0) >= 5, "too few passing sparse attention scenarios")
    require(REQUIRED_PATTERNS.issubset(set(report.get("patterns", []))), "missing sparse attention patterns")
    require(report.get("ragged_scenarios", 0) >= 1, "missing ragged sparse attention scenario")
    require(report.get("backward_scenarios", 0) >= 4, "missing backward sparse attention coverage")
    require(report.get("decode_scenarios", 0) >= 1, "missing decode sparse attention coverage")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion not required")
    require(REPORT_MD.exists(), "missing sparse attention markdown report")
    for row in scenarios:
        require(row.get("kernel_paths") == ["metadata-build", "qk-sparse", "online-softmax", "pv-sparse"], f"{row.get('scenario_id')} missing kernel path")
        require(row.get("hbm_reduction", 0) >= 0.55, f"{row.get('scenario_id')} weak HBM reduction")
        require(row.get("max_abs_error", 1) <= 0.01, f"{row.get('scenario_id')} too much numerical error")
        require(row.get("load_balance_proxy", 0) >= 0.75, f"{row.get('scenario_id')} weak load balance")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE sparse attention kernels" in page, "sparse attention site page missing title")
        require("block-sparse-prefill" in page and "ragged-paged-decode" in page and "topk-routing-attention" in page, "sparse attention site page missing scenarios")
    facts = {
        "scenarios": report["scenario_count"],
        "passed": report["passed_scenarios"],
        "patterns": report["pattern_count"],
        "ragged": report["ragged_scenarios"],
        "backward": report["backward_scenarios"],
        "decode": report["decode_scenarios"],
        "status": report["status"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE sparse attention kernel verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
