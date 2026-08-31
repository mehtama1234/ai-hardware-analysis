#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "distributed-training-optimizer" / "distributed-training-optimizer-report.json"
REPORT_MD = ROOT / "distributed-training-optimizer" / "reports" / "distributed-training-optimizer-report.md"
SITE_PAGE = ROOT / "site" / "distributed-training-optimizer.html"
REQUIRED_SOURCES = {
    "distributed-topology/distributed-topology-plan.json",
    "distributed-collectives/distributed-collectives-report.json",
    "distributed-collectives/reports/collective-benchmark-run.json",
    "hardware-capacity-planning/hardware-capacity-plan.json",
    "multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json",
    "numerical-reproducibility/numerical-reproducibility-report.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_distributed_training_optimizer.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    scenarios = report.get("scenarios", [])
    require(report.get("status") == "training-optimizer-ready", "distributed training optimizer report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 6, "scenario count mismatch")
    require(report.get("passed_scenarios", 0) >= 4, "too few passing optimizer scenarios")
    require(report.get("strategy_count", 0) >= 5, "too few optimizer strategies")
    require(report.get("checkpointed_scenarios", 0) >= 3, "checkpointing coverage too small")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing source reports")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    for row in scenarios:
        require(row.get("ranks", 0) >= 2, f"{row.get('scenario_id')} has too few ranks")
        require(row.get("memory_gb_per_gpu", 0) > 0, f"{row.get('scenario_id')} missing memory estimate")
        require(row.get("step_time_ms", 0) > 0, f"{row.get('scenario_id')} missing step time")
        require(row.get("tokens_per_second", 0) > 0, f"{row.get('scenario_id')} missing throughput")
        require(row.get("optimizer_state_savings", -1) >= 0, f"{row.get('scenario_id')} invalid optimizer savings")
        require({"reduce_scatter_gb", "all_gather_gb"}.issubset(set(row.get("traffic_gb", {}))), f"{row.get('scenario_id')} missing communication traffic")
    require(REPORT_MD.exists(), "missing distributed training optimizer markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE distributed training optimizer" in page, "optimizer site page missing title")
        require("fsdp" in page.lower() and "zero" in page.lower() and "pipeline" in page.lower(), "site page missing optimizer evidence")
    print(
        json.dumps(
            {
                "facts": {
                    "scenarios": report.get("scenario_count"),
                    "passed": report.get("passed_scenarios"),
                    "reviews": report.get("review_scenarios"),
                    "strategies": report.get("strategies"),
                    "status": report.get("status"),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE distributed training optimizer verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
