#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "distributed-collectives" / "distributed-collectives-report.json"
REPORT_MD = ROOT / "distributed-collectives" / "reports" / "distributed-collectives-report.md"
SITE_PAGE = ROOT / "site" / "distributed-collectives.html"
BENCHMARK_REPORT = ROOT / "distributed-collectives" / "reports" / "collective-benchmark-run.json"
BENCHMARK_RUNNER = ROOT / "scripts" / "run_distributed_collectives_benchmark.py"
BENCHMARK_VERIFIER = ROOT / "scripts" / "verify_distributed_collectives_benchmark.py"
REQUIRED_SOURCES = {
    "distributed-topology/distributed-topology-plan.json",
    "moe-routing-all-to-all/moe-routing-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
    "programming-projects/distributed-collectives/measurements.json",
    "comprehensive-labs/measurements/comp-lab-07-distributed-collectives.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_distributed_collectives.py"], cwd=ROOT, check=True)
    if not BENCHMARK_REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_distributed_collectives_benchmark.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    scenarios = report.get("scenarios", [])
    require(report.get("status") == "distributed-collectives-ready", "distributed collectives report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 6, "scenario count mismatch")
    require(report.get("passed_scenarios", 0) >= 5, "too few passing collective scenarios")
    require(report.get("collective_count", 0) >= 5, "collective coverage too small")
    require({"nccl", "rccl"}.issubset({backend.split("/")[0] for backend in report.get("backends", [])}), "missing NCCL/RCCL backend coverage")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing source reports")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    require(BENCHMARK_RUNNER.exists(), "distributed collectives benchmark runner missing")
    require(BENCHMARK_VERIFIER.exists(), "distributed collectives benchmark verifier missing")
    require(BENCHMARK_REPORT.exists(), "distributed collectives benchmark report missing")
    for row in scenarios:
        require(row.get("ranks", 0) >= 2, f"{row.get('scenario_id')} has too few ranks")
        require(row.get("algorithm_steps", 0) > 0, f"{row.get('scenario_id')} missing algorithm steps")
        require(row.get("bandwidth_efficiency", 0) > 0, f"{row.get('scenario_id')} missing bandwidth efficiency")
        require(row.get("overlapped_step_ms", -1) >= row.get("compute_ms", 0), f"{row.get('scenario_id')} invalid overlap timing")
        require(row.get("overlap_gain", 0) >= 0, f"{row.get('scenario_id')} invalid overlap gain")
    require(REPORT_MD.exists(), "missing distributed collectives markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE distributed collectives" in page, "distributed collectives site page missing title")
        require("all-reduce" in page and "reduce-scatter" in page and "all-gather" in page, "site page missing collective evidence")
        require("collective-benchmark" in page or "run_distributed_collectives_benchmark.py" in page, "site page missing benchmark evidence")
    print(
        json.dumps(
            {
                "facts": {
                    "scenarios": report.get("scenario_count"),
                    "passed": report.get("passed_scenarios"),
                    "collectives": report.get("collective_count"),
                    "backends": report.get("backends"),
                    "status": report.get("status"),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE distributed collectives verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
