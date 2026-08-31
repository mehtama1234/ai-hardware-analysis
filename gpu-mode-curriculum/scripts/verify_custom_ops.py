#!/usr/bin/env python3
"""Verify the PyTorch custom-op lab reports and source files."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CUSTOM = ROOT / "custom-ops"
REPORT = CUSTOM / "reports" / "custom-op-report.json"
SITE_PAGE = ROOT / "site" / "custom-ops.html"
REQUIRED_SOURCES = {
    "custom_ops/fused_bias_gelu_residual.py",
    "custom_ops/bench.py",
    "csrc/fused_bias_gelu_residual.cpp",
    "csrc/fused_bias_gelu_residual_kernel.cu",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_custom_ops.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    require(report.get("operator") == "fused_bias_gelu_residual", "unexpected custom operator")
    require(report.get("case_count", 0) >= 4, "expected at least four custom-op shape cases")
    require(report.get("failed") == 0, "custom-op report has failures")
    require(report.get("passed") == report.get("case_count"), "not all custom-op cases passed")
    for rel in REQUIRED_SOURCES:
        require((CUSTOM / rel).exists(), f"missing custom-op source {rel}")
    for case in report.get("cases", []):
        require(case.get("status") == "passed", f"{case.get('id')} did not pass")
        require(all(case.get("checks", {}).values()), f"{case.get('id')} has failed checks")
        require(case.get("shape", {}).get("elements", 0) > 0, f"{case.get('id')} missing element count")
        require(case.get("seconds", {}).get("fused", {}).get("median", 0) >= 0, f"{case.get('id')} missing timing")
    readiness = report.get("accelerator_readiness", {})
    require(readiness.get("torch_device") in {"cpu", "cuda"}, "unexpected torch device")
    require(readiness.get("compiled_extension_status") in {"source-only", "cuda-ready"}, "unexpected extension readiness")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE PyTorch custom op" in page, "custom-op site page missing title")
        require("fused_bias_gelu_residual" in page, "custom-op site page missing operator")
    facts = {
        "cases": report["case_count"],
        "passed": report["passed"],
        "operator": report["operator"],
        "compiled_extension_status": readiness.get("compiled_extension_status"),
        "torch_device": readiness.get("torch_device"),
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE custom-op verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
