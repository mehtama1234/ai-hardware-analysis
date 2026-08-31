#!/usr/bin/env python3
"""Verify tiny transformer model integration artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "model-integration" / "reports" / "tiny-transformer-report.json"
SITE_PAGE = ROOT / "site" / "model-integration.html"
REQUIRED_TUNING = {"matmul", "normalization", "custom-op"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_model_integration.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    require(report.get("model") == "tiny-causal-transformer-block", "unexpected model integration target")
    require(report.get("uses_custom_op") == "fused_bias_gelu_residual", "model integration does not use custom op")
    require(report.get("case_count", 0) >= 3, "expected at least three model integration cases")
    require(report.get("failed") == 0, "model integration report has failures")
    require(report.get("passed") == report.get("case_count"), "not all model integration cases passed")
    selected = report.get("selected_tuning_summary", {})
    require(REQUIRED_TUNING.issubset(selected), "missing selected tuning families")
    require(all(not selected[name].get("missing") for name in REQUIRED_TUNING), "missing autotune selections")
    for case in report.get("cases", []):
        require(case.get("status") == "passed", f"{case.get('id')} did not pass")
        require(all(case.get("checks", {}).values()), f"{case.get('id')} has failed checks")
        require(case.get("shape", {}).get("tokens", 0) > 0, f"{case.get('id')} missing token count")
        require(case.get("tokens_per_second", 0) > 0, f"{case.get('id')} missing throughput")
        require(case.get("max_abs_error", 1) <= 2e-5, f"{case.get('id')} output error too high")
        require(case.get("grad_max_abs_error", 1) <= 2e-5, f"{case.get('id')} grad error too high")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE model integration" in page, "model integration site page missing title")
        require("tiny-causal-transformer-block" in page, "model integration site page missing model")
    facts = {
        "cases": report["case_count"],
        "passed": report["passed"],
        "model": report["model"],
        "uses_custom_op": report["uses_custom_op"],
        "selected_tuning": selected,
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE model integration verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
