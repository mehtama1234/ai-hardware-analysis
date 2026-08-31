#!/usr/bin/env python3
"""Verify GPU evidence provenance is explicit and not overstated."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "gpu-provenance" / "gpu-provenance-report.json"
REPORT_MD = ROOT / "gpu-provenance" / "reports" / "gpu-provenance-report.md"
GPU_RUNS = ROOT / "gpu-runs" / "gpu-run-report.json"
SITE_PAGE = ROOT / "site" / "gpu-provenance.html"
ALLOWED_KINDS = {"sample-fixture", "host-collected", "real-measured"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/build_gpu_provenance.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    require(report.get("status") == "provenance-clear", "GPU provenance report is not clear")
    require(GPU_RUNS.exists(), "source GPU run report missing")
    require(report.get("run_count", 0) >= 3, "expected sample and host-collected runs")
    require(report.get("row_count", 0) >= 20, "expected promotion-row provenance coverage")
    require(report.get("rows_with_provenance") == report.get("row_count"), "not every row has provenance")
    require(report.get("sample_run_count", 0) >= 2, "sample GPU fixtures are not identified")
    require(report.get("host_collected_run_count", 0) >= 1, "host-collected run is not identified")
    require(report.get("measured_run_count", -1) >= 0, "measured run count is invalid")
    require(report.get("real_gpu_evidence_status") in {"present", "not-present-on-this-host"}, "invalid real GPU evidence status")
    for row in report.get("runs", []):
        require(row.get("provenance_kind") in ALLOWED_KINDS, f"{row.get('run_id')} has invalid provenance")
        require(isinstance(row.get("measured"), bool), f"{row.get('run_id')} has non-boolean measured flag")
        if row.get("provenance_kind") == "sample-fixture":
            require(row.get("measured") is False, f"{row.get('run_id')} sample fixture cannot be measured")
    require(REPORT_MD.exists(), "GPU provenance markdown report missing")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE GPU evidence provenance" in page, "GPU provenance site page missing title")
        require("not-present-on-this-host" in page or "present" in page, "GPU provenance site page missing evidence status")
    facts = {
        "runs": report["run_count"],
        "rows": report["row_count"],
        "measured_runs": report["measured_run_count"],
        "status": report["real_gpu_evidence_status"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE GPU provenance verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
