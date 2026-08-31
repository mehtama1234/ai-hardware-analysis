#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "cuda-graphs-latency" / "cuda-graphs-latency-report.json"
REPORT_MD = ROOT / "cuda-graphs-latency" / "reports" / "cuda-graphs-latency-report.md"
SITE_PAGE = ROOT / "site" / "cuda-graphs-latency.html"
REQUIRED_SOURCES = {
    "serving-traces/reports/serving-trace-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
    "serving-engine-comparison/serving-engine-comparison.json",
    "runtime-matrix/matrix.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_cuda_graphs_latency.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    scenarios = report.get("scenarios", [])
    require(report.get("status") == "cuda-graphs-ready", "CUDA Graphs latency report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 5, "scenario count mismatch")
    require(report.get("capture_ready_count", 0) >= 3, "too few capture-ready scenarios")
    require(report.get("fallback_required_count", 0) >= 2, "too few fallback-required scenarios")
    require(report.get("passed_reduction_count", 0) >= 3, "capture scenarios did not reduce p95 latency")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing required source reports")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    for row in scenarios:
        require(row.get("capture_constraints"), f"{row.get('scenario_id')} missing capture constraints")
        require(row.get("fallback_strategy"), f"{row.get('scenario_id')} missing fallback strategy")
        require(row.get("eager_p95_ms", 0) >= 0 and row.get("graph_p95_ms", 0) >= 0, f"{row.get('scenario_id')} has invalid latency")
    require(REPORT_MD.exists(), "missing CUDA Graphs latency markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE CUDA Graphs latency" in page, "CUDA Graphs site page missing title")
        require("capture-ready" in page and "fallback-required" in page, "CUDA Graphs site page missing scenario statuses")
    print(
        json.dumps(
            {
                "facts": {
                    "scenarios": report.get("scenario_count"),
                    "capture_ready": report.get("capture_ready_count"),
                    "fallback_required": report.get("fallback_required_count"),
                    "passed_reductions": report.get("passed_reduction_count"),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE CUDA Graphs latency verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
