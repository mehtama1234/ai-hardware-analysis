#!/usr/bin/env python3
"""Verify the fused LLM training kernel report."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "fused-training-kernels" / "fused-training-report.json"
REPORT_MD = ROOT / "fused-training-kernels" / "reports" / "fused-training-report.md"
SITE_PAGE = ROOT / "site" / "fused-training-kernels.html"
REQUIRED_FAMILIES = {"rmsnorm", "swiglu-mlp", "cross-entropy", "optimizer", "fusion"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_fused_training_kernels.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    scenarios = report.get("scenarios", [])
    require(report.get("status") == "fused-training-ready", "fused training report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 6, "scenario count mismatch")
    require(report.get("passed_scenarios", 0) >= 5, "too few passing fused training scenarios")
    require(REQUIRED_FAMILIES.issubset(set(report.get("families", []))), "missing fused training kernel families")
    require(report.get("backward_scenarios", 0) >= 4, "missing backward fused training coverage")
    require(report.get("optimizer_state_scenarios", 0) >= 2, "missing optimizer-state coverage")
    require(report.get("checkpoint_safe_scenarios", 0) >= 3, "missing checkpoint-safe fusion coverage")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion not required")
    require(REPORT_MD.exists(), "missing fused training markdown report")
    for row in scenarios:
        require(row.get("speedup_vs_unfused", 0) >= 1.8, f"{row.get('scenario_id')} weak fusion speedup")
        require(row.get("hbm_reduction", 0) >= 0.45, f"{row.get('scenario_id')} weak HBM reduction")
        require(row.get("launch_reduction", 0) >= 0.45, f"{row.get('scenario_id')} weak launch reduction")
        require(row.get("max_abs_error", 1) <= 0.01, f"{row.get('scenario_id')} too much numerical error")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE fused training kernels" in page, "fused training site page missing title")
        require("rmsnorm-residual-backward" in page and "adamw-multi-tensor" in page and "cross-entropy-zloss" in page, "fused training site page missing scenarios")
    facts = {
        "scenarios": report["scenario_count"],
        "passed": report["passed_scenarios"],
        "families": report["family_count"],
        "backward": report["backward_scenarios"],
        "optimizer_state": report["optimizer_state_scenarios"],
        "checkpoint_safe": report["checkpoint_safe_scenarios"],
        "status": report["status"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE fused training kernel verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
