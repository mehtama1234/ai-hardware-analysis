#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "moe-routing-all-to-all" / "moe-routing-report.json"
REPORT_MD = ROOT / "moe-routing-all-to-all" / "reports" / "moe-routing-report.md"
SITE_PAGE = ROOT / "site" / "moe-routing-all-to-all.html"
REQUIRED_SOURCES = {
    "distributed-topology/distributed-topology-plan.json",
    "serving-engine-comparison/serving-engine-comparison.json",
    "kv-cache-paged-attention/kv-cache-report.json",
    "multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_moe_routing_all_to_all.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    scenarios = report.get("scenarios", [])
    require(report.get("status") == "moe-routing-ready", "MoE routing report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 5, "scenario count mismatch")
    require(report.get("passed_scenarios", 0) >= 3, "too few passing MoE scenarios")
    require(report.get("tuning_required_scenarios", 0) >= 1, "MoE report lacks tuning-required cases")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing source reports")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    for row in scenarios:
        require(len(row.get("expert_loads", [])) == row.get("expert_count"), f"{row.get('scenario_id')} load histogram mismatch")
        require(row.get("drop_rate", 1) <= 0.45, f"{row.get('scenario_id')} drop rate too high")
        if row.get("status") == "passed":
            require(row.get("drop_rate", 1) <= 0.25, f"{row.get('scenario_id')} passing drop rate too high")
        require(row.get("fairness_index", 0) > 0, f"{row.get('scenario_id')} missing fairness")
        require(row.get("all_to_all_payload_gb", 0) > 0, f"{row.get('scenario_id')} missing payload")
        require(row.get("estimated_all_to_all_ms", 0) >= 0, f"{row.get('scenario_id')} invalid all-to-all estimate")
        require(row.get("bottleneck"), f"{row.get('scenario_id')} missing bottleneck")
    require(REPORT_MD.exists(), "missing MoE markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE MoE routing" in page, "MoE site page missing title")
        require("all-to-all" in page and "drop rate" in page, "MoE site page missing communication evidence")
    print(json.dumps({"facts": {"scenarios": report.get("scenario_count"), "passed": report.get("passed_scenarios"), "tuning_required": report.get("tuning_required_scenarios"), "status": report.get("status")}, "failures": []}, indent=2))
    print("GPUMODE MoE routing/all-to-all verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
