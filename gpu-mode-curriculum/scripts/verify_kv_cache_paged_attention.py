#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "kv-cache-paged-attention" / "kv-cache-report.json"
REPORT_MD = ROOT / "kv-cache-paged-attention" / "reports" / "kv-cache-report.md"
SITE_PAGE = ROOT / "site" / "kv-cache-paged-attention.html"
REQUIRED_SOURCES = {
    "serving-traces/reports/serving-trace-report.json",
    "serving-engine-comparison/serving-engine-comparison.json",
    "cuda-graphs-latency/cuda-graphs-latency-report.json",
    "multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_kv_cache_paged_attention.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    require(report.get("status") == "kv-cache-ready", "KV-cache report is not ready")
    require(report.get("scenario_count") == len(report.get("scenarios", [])) >= 5, "scenario count mismatch")
    require(report.get("policy_count", 0) >= 2, "policy coverage too small")
    require(report.get("passed_scenarios", 0) >= 4, "too few passing scenarios")
    require(report.get("total_prefix_blocks_reused", 0) > 0, "prefix reuse was not measured")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing source reports")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    for row in report.get("scenarios", []):
        require(row.get("contiguous") and row.get("paged"), f"{row.get('scenario_id')} missing policy comparison")
        require("waste_ratio" in row["contiguous"] and "waste_ratio" in row["paged"], f"{row.get('scenario_id')} missing waste ratio")
        require(row["paged"].get("rejected_count", 0) <= row["contiguous"].get("rejected_count", 0), f"{row.get('scenario_id')} paged admission regressed")
        require(row.get("capacity_blocks", 0) > 0 and row.get("block_size", 0) > 0, f"{row.get('scenario_id')} invalid block config")
    require(REPORT_MD.exists(), "missing KV-cache markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE KV cache" in page, "KV-cache site page missing title")
        require("PagedAttention" in page and "fragmentation" in page, "KV-cache site page missing allocator evidence")
    print(
        json.dumps(
            {
                "facts": {
                    "scenarios": report.get("scenario_count"),
                    "passed": report.get("passed_scenarios"),
                    "prefix_blocks_reused": report.get("total_prefix_blocks_reused"),
                    "status": report.get("status"),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE KV-cache/PagedAttention verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
