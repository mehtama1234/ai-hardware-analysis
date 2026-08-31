#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "multi-tenant-gpu-scheduling" / "multi-tenant-scheduling-report.json"
REPORT_MD = ROOT / "multi-tenant-gpu-scheduling" / "reports" / "multi-tenant-scheduling-report.md"
SITE_PAGE = ROOT / "site" / "multi-tenant-scheduling.html"
REQUIRED_SOURCES = {
    "hardware-capacity-planning/hardware-capacity-plan.json",
    "distributed-topology/distributed-topology-plan.json",
    "serving-traces/reports/serving-trace-report.json",
    "cuda-graphs-latency/cuda-graphs-latency-report.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_multi_tenant_gpu_scheduling.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    plans = report.get("plans", [])
    policies = {row.get("id") for row in report.get("policies", [])}
    require(report.get("status") == "scheduling-ready", "multi-tenant scheduling report is not ready")
    require(report.get("policy_count") == len(report.get("policies", [])) >= 4, "policy count mismatch")
    require(report.get("tenant_count") == len(report.get("tenants", [])) >= 5, "tenant count mismatch")
    require(report.get("accepted_count", 0) >= 4, "recommended plan accepts too few tenants")
    require(report.get("placement_count", 0) >= report.get("tenant_count", 0), "placement count too small")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing source reports")
    require("mig-pack" in policies and "mps-fair-share" in policies, "missing MIG or MPS policy")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    for plan in plans:
        require(plan.get("fairness_index", 0) >= 0, f"{plan.get('policy_id')} missing fairness")
        require(plan.get("policy_score", 0) >= 0, f"{plan.get('policy_id')} missing score")
        require(plan.get("placements"), f"{plan.get('policy_id')} missing placements")
        for row in plan["placements"]:
            require(row.get("tenant_id"), "placement missing tenant_id")
            require(row.get("status") in {"accepted", "queued", "rejected"}, f"{row.get('tenant_id')} invalid status")
            require("memory_headroom_gb" in row, f"{row.get('tenant_id')} missing memory headroom")
            require(row.get("isolation"), f"{row.get('tenant_id')} missing isolation")
            require(row.get("slo_status"), f"{row.get('tenant_id')} missing SLO status")
            require(row.get("reason"), f"{row.get('tenant_id')} missing reason")
    require(REPORT_MD.exists(), "missing multi-tenant scheduling markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE multi-tenant scheduling" in page, "multi-tenant scheduling site page missing title")
        require("fairness" in page and "mig-pack" in page and "mps-fair-share" in page, "site page missing scheduling evidence")
    print(
        json.dumps(
            {
                "facts": {
                    "policies": report.get("policy_count"),
                    "tenants": report.get("tenant_count"),
                    "accepted": report.get("accepted_count"),
                    "recommended_policy": report.get("recommended_policy"),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE multi-tenant GPU scheduling verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
