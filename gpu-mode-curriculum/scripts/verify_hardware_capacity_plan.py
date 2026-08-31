#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "hardware-capacity-planning" / "hardware-capacity-plan.json"
REPORT_MD = ROOT / "hardware-capacity-planning" / "reports" / "hardware-capacity-plan.md"
SITE_PAGE = ROOT / "site" / "hardware-capacity.html"
REQUIRED_SOURCES = {
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
    "serving-engine-comparison/serving-engine-comparison.json",
    "distributed-topology/distributed-topology-plan.json",
}
REQUIRED_EVALUATION_FIELDS = {
    "status",
    "memory_required_gb",
    "memory_headroom_gb",
    "estimated_power_w",
    "estimated_cost_per_hour",
    "bottleneck",
    "validation_commands",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_hardware_capacity_plan.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    recommendations = report.get("recommendations", [])
    evaluations = report.get("evaluations", [])
    require(report.get("status") == "capacity-plan-ready", "hardware capacity plan is not ready")
    require(report.get("profile_count", 0) >= 5, "hardware capacity plan lacks hardware profiles")
    require(report.get("workload_count", 0) >= 5, "hardware capacity plan lacks workloads")
    require(report.get("recommendation_count") == report.get("workload_count"), "recommendation count must match workload count")
    require(len(recommendations) == report.get("recommendation_count"), "recommendation list count mismatch")
    require(any(row.get("recommended_profile") != "local-cpu-fallback" for row in recommendations), "all recommendations fell back to CPU")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing required source reports")
    require(REPORT_MD.exists(), "missing hardware capacity markdown report")
    require(evaluations, "missing hardware capacity evaluations")
    for row in evaluations:
        require(REQUIRED_EVALUATION_FIELDS.issubset(row), f"evaluation missing fields: {row}")
        require(row.get("validation_commands"), f"evaluation missing validation commands: {row}")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE hardware capacity" in page, "hardware capacity site page missing title")
        require("memory headroom" in page, "hardware capacity site page missing memory headroom")
    print(
        json.dumps(
            {
                "facts": {
                    "profiles": report.get("profile_count"),
                    "workloads": report.get("workload_count"),
                    "recommendations": report.get("recommendation_count"),
                    "rejected": report.get("rejected_count"),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE hardware capacity plan verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
