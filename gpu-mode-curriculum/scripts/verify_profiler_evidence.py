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
    require(report.get("evidence_kind") == "fixture" and report.get("measured") is False,
            "fixture report must not claim measured execution")
    require(report.get("gpu_execution_accepted") is False, "fixtures cannot accept GPU execution")
    fixtures = {path.name for path in (PROFILER / "fixtures").iterdir() if path.is_file()}
    require(REQUIRED_FIXTURES.issubset(fixtures), f"missing profiler fixtures: {sorted(REQUIRED_FIXTURES - fixtures)}")
    require(report.get("row_count", 0) >= 9, "expected at least nine normalized profiler rows")
    require(report.get("source_count", 0) >= 3, "expected Nsight Compute, Nsight Systems, and rocprof sources")
    require(report.get("source_sha256"), "profiler report must identify parser and fixture sources")
    captures = report.get("native_captures", [])
    require(report.get("native_capture_count") == len(captures) and captures,
            "expected a separately labeled native profiler capture")
    for capture in captures:
        require(capture.get("evidence_kind") == "native-capture" and capture.get("measured") is True,
                "native profiler capture must retain measured evidence class")
        require(capture.get("gpu_execution_accepted") is True, "native profiler capture was not accepted")
        require(capture.get("sass", {}).get("tensor_core_instruction_seen") is True,
                "native capture missing tensor-core SASS evidence")
        require(capture.get("nsight_compute", {}).get("status") == "measured",
                "native capture missing measured Nsight Compute status")
        artifact = ROOT.parent / capture.get("artifact", "")
        require(artifact.is_file(), f"native profiler artifact missing: {capture.get('artifact')}")
    require(REQUIRED_CLASSES.issubset(set(report.get("classification_counts", {}))), "missing required profiler classifications")
    require(all(report.get("checks", {}).values()), "profiler report checks did not all pass")
    for row in report.get("rows", []):
        require(row.get("evidence_kind") == "fixture" and row.get("measured") is False,
                "each normalized row must preserve fixture evidence class")
        require(row.get("source"), "profiler row missing source")
        require(row.get("name"), "profiler row missing name")
        require(row.get("classification"), "profiler row missing classification")
        require(row.get("remediation"), "profiler row missing remediation")
        require(isinstance(row.get("missing_metrics"), list), "profiler row missing explicit missing_metrics list")
        if row.get("missing_metrics"):
            require(row.get("classification") == "insufficient-data",
                    "rows with missing counters must remain insufficient-data")
    require((PROFILER / "README.md").exists(), "missing profiler evidence README")
    require((PROFILER / "reports" / "profiler-evidence-report.md").exists(), "missing profiler evidence Markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE profiler evidence" in page, "profiler site page missing title")
        require("teaching fixtures" in page.lower(), "profiler page must disclose fixture evidence")
        require("native capture" in page.lower(), "profiler page must disclose native capture evidence")
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
