#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "persistent-kernels" / "persistent-kernels-report.json"
REPORT_MD = ROOT / "persistent-kernels" / "reports" / "persistent-kernels-report.md"
SITE_PAGE = ROOT / "site" / "persistent-kernels.html"
REQUIRED_SOURCES = {
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "autotune-db/autotune-db.json",
    "tensor-core-gemm/tensor-core-gemm-report.json",
    "compiler-runtime-inspection/compiler-runtime-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
    "attention-serving-stack/attention-serving-report.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_persistent_kernels.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    scenarios = report.get("scenarios", [])
    require(report.get("status") == "persistent-kernels-ready", "persistent-kernel report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 6, "scenario count mismatch")
    require(report.get("passed_scenarios", 0) >= 5, "too few passing persistent-kernel scenarios")
    require(report.get("family_count", 0) >= 5, "persistent-kernel family coverage is too small")
    require(report.get("producer_consumer_scenarios", 0) >= 3, "producer/consumer coverage is too small")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing source reports")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    for row in scenarios:
        sid = row.get("scenario_id")
        require(row.get("speedup_vs_baseline", 0) > 1.0, f"{sid} lacks speedup")
        require(row.get("occupancy_proxy", 0) > 0, f"{sid} lacks occupancy")
        require(row.get("resident_ctas_per_sm", 0) >= 1, f"{sid} has no resident CTA")
        require(row.get("hbm_reduction", -1) >= 0, f"{sid} has invalid HBM reduction")
        require(row.get("gpu_evidence_required"), f"{sid} lacks profiler evidence requirements")
    require(REPORT_MD.exists(), "missing persistent-kernels markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE persistent kernels" in page, "persistent-kernels site page missing title")
        require("persistent" in page and "occupancy" in page and "producer" in page, "site page missing persistent-kernel evidence")
    print(
        json.dumps(
            {
                "facts": {
                    "scenarios": report.get("scenario_count"),
                    "passed": report.get("passed_scenarios"),
                    "families": report.get("family_count"),
                    "producer_consumer": report.get("producer_consumer_scenarios"),
                    "status": report.get("status"),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE persistent-kernels verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
