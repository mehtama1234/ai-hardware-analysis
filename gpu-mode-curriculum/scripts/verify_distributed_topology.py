#!/usr/bin/env python3
"""Verify distributed topology planning report and site integration."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "distributed-topology" / "distributed-topology-plan.json"
REPORT_MD = ROOT / "distributed-topology" / "reports" / "distributed-topology-plan.md"
SITE_PAGE = ROOT / "site" / "distributed-topology.html"
REQUIRED_TOPOLOGIES = {"single-gpu", "dual-pcie", "quad-nvlink", "eight-nvlink", "sixteen-ib"}
REQUIRED_WORKLOADS = {"llama-7b-chat", "llama-13b-rag", "llama-70b-batch", "mixtral-8x7b", "dense-70b-sft"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_distributed_topology.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    require(report.get("status") == "topology-plan-ready", "distributed topology plan is not ready")
    require(report.get("topology_count") >= 5, "expected at least five topologies")
    require(report.get("workload_count") >= 5, "expected at least five workloads")
    require(report.get("candidate_count", 0) > report.get("rejected_count", 0) // 2, "too few viable topology candidates")
    require({row.get("id") for row in report.get("topologies", [])} == REQUIRED_TOPOLOGIES, "unexpected topology ids")
    require({row.get("id") for row in report.get("workloads", [])} == REQUIRED_WORKLOADS, "unexpected workload ids")
    require(len(report.get("recommendations", [])) == len(REQUIRED_WORKLOADS), "missing workload recommendations")
    for recommendation in report.get("recommendations", []):
        strategy = recommendation.get("strategy", {})
        require(recommendation.get("status") == "candidate", f"{recommendation.get('workload_id')} did not receive a viable topology")
        require(strategy.get("tensor_parallel", 0) >= 1, f"{recommendation.get('workload_id')} missing TP")
        require(strategy.get("pipeline_parallel", 0) >= 1, f"{recommendation.get('workload_id')} missing PP")
        require(strategy.get("data_parallel", 0) >= 1, f"{recommendation.get('workload_id')} missing DP")
        require(recommendation.get("bottleneck"), f"{recommendation.get('workload_id')} missing bottleneck")
    for plan in report.get("plans", []):
        require(len(plan.get("candidates", [])) == len(REQUIRED_TOPOLOGIES), f"{plan.get('workload', {}).get('id')} missing candidate rows")
        for candidate in plan.get("candidates", []):
            require(candidate.get("validation_commands"), f"{candidate.get('workload_id')} missing validation commands")
            require(candidate.get("memory_gb_per_gpu", -1) >= 0, f"{candidate.get('workload_id')} invalid memory estimate")
            require(candidate.get("estimated_collective_ms", -1) >= 0, f"{candidate.get('workload_id')} invalid collective estimate")
    require(REPORT_MD.exists(), "distributed topology Markdown report missing")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE distributed topology" in page, "distributed topology site page missing title")
        require("tensor" in page and "pipeline" in page and "data" in page, "distributed topology site page missing parallelism terms")
    facts = {
        "status": report["status"],
        "topologies": report["topology_count"],
        "workloads": report["workload_count"],
        "candidates": report["candidate_count"],
        "rejected": report["rejected_count"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE distributed topology verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
