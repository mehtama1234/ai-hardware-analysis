#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "parallel-primitives" / "parallel-primitives-report.json"
REPORT_MD = ROOT / "parallel-primitives" / "reports" / "parallel-primitives-report.md"
SITE_PAGE = ROOT / "site" / "parallel-primitives.html"
REQUIRED_SOURCES = {
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "autotune-db/autotune-db.json",
    "compiler-runtime-inspection/compiler-runtime-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
    "persistent-kernels/persistent-kernels-report.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_parallel_primitives.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    require(report.get("evidence_kind") == "analytical" and report.get("measured") is False,
            "scenario model must not be labeled measured")
    require(report.get("gpu_execution_accepted") is False, "scenario model cannot accept GPU execution")
    scenarios = report.get("scenarios", [])
    require(report.get("status") == "parallel-primitives-ready", "parallel-primitives report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 6, "scenario count mismatch")
    require(report.get("passed_scenarios", 0) >= 5, "too few passing primitive scenarios")
    require(report.get("primitive_count", 0) >= 6, "primitive family coverage is too small")
    require(report.get("stable_order_scenarios", 0) >= 3, "stable-order coverage is too small")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing source reports")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    for row in scenarios:
        require(row.get("evidence_kind") == "analytical" and row.get("measured") is False
                and row.get("numerical_correctness_status") == "not_executed", "scenario evidence boundary missing")
        sid = row.get("scenario_id")
        require(row.get("work_efficiency", 0) > 1.0, f"{sid} lacks work efficiency")
        require(row.get("memory_traffic_mb", 0) > 0, f"{sid} lacks memory traffic")
        require(row.get("bandwidth_proxy_gbps", 0) > 0, f"{sid} lacks bandwidth proxy")
        require(row.get("occupancy_proxy", 0) > 0, f"{sid} lacks occupancy")
        require(row.get("gpu_evidence_required"), f"{sid} lacks profiler evidence requirements")
    require(REPORT_MD.exists(), "missing parallel-primitives markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE parallel primitives" in page, "parallel-primitives site page missing title")
        require("scan" in page and "histogram" in page and "radix" in page, "site page missing primitive evidence")
    print(
        json.dumps(
            {
                "facts": {
                    "scenarios": report.get("scenario_count"),
                    "passed": report.get("passed_scenarios"),
                    "primitives": report.get("primitive_count"),
                    "stable_order": report.get("stable_order_scenarios"),
                    "status": report.get("status"),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE parallel-primitives verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
