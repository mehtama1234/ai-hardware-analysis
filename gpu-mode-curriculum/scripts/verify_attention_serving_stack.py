#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "attention-serving-stack" / "attention-serving-report.json"
REPORT_MD = ROOT / "attention-serving-stack" / "reports" / "attention-serving-report.md"
SITE_PAGE = ROOT / "site" / "attention-serving-stack.html"
REQUIRED_SOURCES = {
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "kv-cache-paged-attention/kv-cache-report.json",
    "serving-traces/reports/serving-trace-report.json",
    "serving-engine-comparison/serving-engine-comparison.json",
    "numerical-reproducibility/numerical-reproducibility-report.json",
    "cuda-graphs-latency/cuda-graphs-latency-report.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_attention_serving_stack.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    scenarios = report.get("scenarios", [])
    require(report.get("status") == "attention-serving-ready", "attention serving report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 5, "scenario count mismatch")
    require(report.get("passed_scenarios", 0) >= 4, "too few passing attention scenarios")
    require(report.get("total_prefix_blocks_reused", 0) > 0, "prefix reuse was not connected to serving")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing source reports")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    for row in scenarios:
        require(row.get("hbm_reduction", 0) >= 0.25, f"{row.get('scenario_id')} HBM reduction too small")
        require(row.get("tiles", {}).get("shared_memory_bytes", 10**9) <= 96 * 1024, f"{row.get('scenario_id')} tile exceeds shared memory budget")
        require(row.get("scheduler", {}).get("graph_bucket_fit") is True, f"{row.get('scenario_id')} graph bucket mismatch")
        require(row.get("numerics_contract", {}).get("requires_reference_check") is True, f"{row.get('scenario_id')} lacks numerics contract")
    require(REPORT_MD.exists(), "missing attention serving markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE FlashAttention" in page, "attention serving site page missing title")
        require("online softmax" in page and "prefill" in page and "decode" in page, "site page missing serving evidence")
    print(
        json.dumps(
            {
                "facts": {
                    "scenarios": report.get("scenario_count"),
                    "passed": report.get("passed_scenarios"),
                    "tuning_required": report.get("tuning_required_scenarios"),
                    "prefix_blocks_reused": report.get("total_prefix_blocks_reused"),
                    "status": report.get("status"),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE FlashAttention/vLLM serving stack verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
