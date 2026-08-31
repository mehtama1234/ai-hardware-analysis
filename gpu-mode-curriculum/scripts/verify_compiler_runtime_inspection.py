#!/usr/bin/env python3
"""Verify compiler/runtime inspection coverage and site output."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "compiler-runtime-inspection" / "compiler-runtime-report.json"
REPORT_MD = ROOT / "compiler-runtime-inspection" / "reports" / "compiler-runtime-report.md"
SITE_PAGE = ROOT / "site" / "compiler-runtime-inspection.html"
REQUIRED_GROUPS = {"cuda", "triton", "custom-op", "hip"}
REQUIRED_FEATURES = {"global_kernel", "launch_indexing", "bounds_mask", "tensor_core_hint"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_compiler_runtime_inspection.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    require(report.get("status") == "inspection-ready", "compiler runtime inspection is not ready")
    require(report.get("source_count", 0) >= 10, "expected at least ten GPU-facing source files")
    require(REQUIRED_GROUPS.issubset(set(report.get("groups", []))), "missing source groups")
    feature_counts = report.get("feature_counts", {})
    for feature in REQUIRED_FEATURES:
        require(feature_counts.get(feature, 0) > 0, f"missing feature coverage for {feature}")
    require(report.get("promotion_command_count", 0) >= report.get("source_count", 0), "promotion command coverage too low")
    rows = report.get("source_rows", [])
    require(len(rows) == report.get("source_count"), "source row count mismatch")
    for row in rows:
        require((ROOT / row.get("path", "")).exists(), f"{row.get('path')} does not exist")
        require(row.get("lines", 0) > 0, f"{row.get('path')} has no lines")
        require(row.get("features"), f"{row.get('path')} missing features")
        require(row.get("promotion_commands"), f"{row.get('path')} missing promotion commands")
    require(REPORT_MD.exists(), "compiler runtime Markdown report missing")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE compiler runtime inspection" in page, "compiler runtime site page missing title")
        require("CUDA" in page or "cuda" in page, "compiler runtime site page missing CUDA")
        require("Triton" in page or "triton" in page, "compiler runtime site page missing Triton")
    facts = {
        "status": report["status"],
        "sources": report["source_count"],
        "groups": report["groups"],
        "feature_counts": report["feature_counts"],
        "risk_counts": report["risk_counts"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE compiler runtime inspection verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
