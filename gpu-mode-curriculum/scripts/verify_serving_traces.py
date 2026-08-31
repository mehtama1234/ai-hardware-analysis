#!/usr/bin/env python3
"""Verify serving trace replay fixtures, metrics, and site integration."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "serving-traces" / "reports" / "serving-trace-report.json"
SITE_PAGE = ROOT / "site" / "serving-traces.html"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_serving_traces.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    require(report.get("trace_count", 0) >= 3, "expected at least three serving traces")
    require(set(report.get("policy_ids", [])) == {"continuous-batching-prefix-cache", "static-batching"}, "unexpected policy set")
    require(report.get("failed_traces") == 0, "serving trace checks failed")
    for trace in report.get("traces", []):
        require(trace.get("status") == "passed", f"{trace.get('trace_id')} did not pass")
        require(len(trace.get("policies", [])) == 2, f"{trace.get('trace_id')} missing policy comparison")
        for policy in trace["policies"]:
            summary = policy["summary"]
            require(summary["completed_count"] == summary["request_count"], f"{trace['trace_id']} has incomplete requests")
            require(summary["output_tokens_per_second"] > 0, f"{trace['trace_id']} missing throughput")
            require(summary["p95_ttft_ms"] >= summary["p50_ttft_ms"], f"{trace['trace_id']} TTFT percentile order invalid")
            require(summary["peak_live_kv_blocks"] <= summary["kv_capacity_blocks"], f"{trace['trace_id']} exceeded KV capacity")
    require(any(row["throughput_speedup"] >= 1.0 for row in report.get("comparisons", [])), "continuous batching never improved throughput")
    require(sum(row["prefix_cache_blocks_saved"] for row in report.get("comparisons", [])) > 0, "prefix cache did not save blocks")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE serving trace replay" in page, "serving trace site page missing title")
        require("TTFT" in page and "TPOT" in page, "serving trace site page missing latency metrics")
    facts = {
        "traces": report["trace_count"],
        "policies": report["policy_ids"],
        "speedups": [row["throughput_speedup"] for row in report["comparisons"]],
        "prefix_blocks_saved": sum(row["prefix_cache_blocks_saved"] for row in report["comparisons"]),
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE serving trace verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
