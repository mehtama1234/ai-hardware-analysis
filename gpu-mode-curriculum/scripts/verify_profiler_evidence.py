#!/usr/bin/env python3
"""Verify profiler evidence fixtures, parser output, and site integration."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROFILER = ROOT / "profiler-evidence"
REPORT = PROFILER / "reports" / "profiler-evidence-report.json"
SITE_PAGE = ROOT / "site" / "profiler-evidence.html"
REQUIRED_FIXTURES = {"nsight_compute_kernels.csv", "nsight_systems_timeline.json", "rocprof_kernels.csv"}
REQUIRED_CLASSES = {"memory-bandwidth", "launch-overhead", "communication"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_profiler_evidence.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    fixtures = {path.name for path in (PROFILER / "fixtures").iterdir() if path.is_file()}
    require(REQUIRED_FIXTURES.issubset(fixtures), f"missing profiler fixtures: {sorted(REQUIRED_FIXTURES - fixtures)}")
    require(report.get("row_count", 0) >= 9, "expected at least nine normalized profiler rows")
    require(report.get("source_count", 0) >= 3, "expected Nsight Compute, Nsight Systems, and rocprof sources")
    require(REQUIRED_CLASSES.issubset(set(report.get("classification_counts", {}))), "missing required profiler classifications")
    require(all(report.get("checks", {}).values()), "profiler report checks did not all pass")
    for row in report.get("rows", []):
        require(row.get("source"), "profiler row missing source")
        require(row.get("name"), "profiler row missing name")
        require(row.get("classification"), "profiler row missing classification")
        require(row.get("remediation"), "profiler row missing remediation")
    require((PROFILER / "README.md").exists(), "missing profiler evidence README")
    require((PROFILER / "reports" / "profiler-evidence-report.md").exists(), "missing profiler evidence Markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE profiler evidence" in page, "profiler site page missing title")
        require("memory-bandwidth" in page, "profiler site page missing classifications")
    facts = {
        "rows": report.get("row_count"),
        "sources": report.get("source_count"),
        "classifications": sorted(report.get("classification_counts", {})),
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE profiler evidence verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
