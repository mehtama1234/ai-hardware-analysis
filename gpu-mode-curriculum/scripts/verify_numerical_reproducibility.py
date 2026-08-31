#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "numerical-reproducibility" / "numerical-reproducibility-report.json"
REPORT_MD = ROOT / "numerical-reproducibility" / "reports" / "numerical-reproducibility-report.md"
SITE_PAGE = ROOT / "site" / "numerical-reproducibility.html"
REQUIRED_SOURCES = {
    "quantization-memory-formats/quantization-report.json",
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "model-integration/reports/tiny-transformer-report.json",
    "moe-routing-all-to-all/moe-routing-report.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_numerical_reproducibility.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    scenarios = report.get("scenarios", [])
    modes = {row.get("mode") for row in scenarios}
    require(report.get("status") == "reproducibility-ready", "numerical reproducibility report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 5, "scenario count mismatch")
    require(report.get("passed_scenarios", 0) >= 4, "too few passing reproducibility scenarios")
    require(report.get("tolerance_review_scenarios", 0) >= 1, "missing tolerance-review scenario")
    require({"fp32-deterministic", "fp32-reversed-reduction", "tf32-like", "bf16-like", "fp8-like"}.issubset(modes), "missing precision modes")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing source reports")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    reduction = report.get("reduction_order", {})
    require(reduction.get("status") == "passed", "reduction order check did not pass")
    require(reduction.get("max_order_delta", 1) <= reduction.get("tolerance", 0), "reduction order delta exceeds tolerance")
    for row in scenarios:
        require(row.get("repeat_count", 0) >= 5, f"{row.get('mode')} repeat count too small")
        require(row.get("repeat_max_abs_drift", 1) <= row.get("tolerance", 0), f"{row.get('mode')} repeat drift exceeds tolerance")
        require(row.get("cosine_similarity", 0) > 0.95, f"{row.get('mode')} cosine too low")
        require(row.get("determinism_policy") in {"bitwise-repeatable", "tolerance-bounded"}, f"{row.get('mode')} invalid policy")
    require(REPORT_MD.exists(), "missing numerical reproducibility markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE numerical reproducibility" in page, "numerical reproducibility site page missing title")
        require("tolerance" in page and "reduction order" in page, "site page missing reproducibility evidence")
    print(json.dumps({"facts": {"scenarios": report.get("scenario_count"), "passed": report.get("passed_scenarios"), "reviews": report.get("tolerance_review_scenarios"), "status": report.get("status")}, "failures": []}, indent=2))
    print("GPUMODE numerical reproducibility verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
