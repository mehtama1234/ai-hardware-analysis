#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "quantization-memory-formats" / "quantization-report.json"
REPORT_MD = ROOT / "quantization-memory-formats" / "reports" / "quantization-report.md"
SITE_PAGE = ROOT / "site" / "quantization-memory-formats.html"
REQUIRED_FORMATS = {"fp32-reference", "bf16-activation", "fp8-e4m3-sim", "int8-per-tensor", "int8-per-channel", "int4-symmetric", "nf4-weight-only"}
REQUIRED_SOURCES = {
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "model-integration/reports/tiny-transformer-report.json",
    "serving-engine-comparison/serving-engine-comparison.json",
    "hardware-capacity-planning/hardware-capacity-plan.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_quantization_memory_formats.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    formats = report.get("formats", [])
    format_ids = {row.get("format_id") for row in formats}
    require(report.get("status") == "quantization-ready", "quantization report is not ready")
    require(REQUIRED_FORMATS.issubset(format_ids), f"missing formats: {sorted(REQUIRED_FORMATS - format_ids)}")
    require(report.get("format_count") == len(formats) >= 7, "format count mismatch")
    require(report.get("passed_format_count", 0) >= 4, "too few quantization formats passed accuracy gates")
    require(any(row.get("compression_vs_fp32", 0) >= 4 for row in formats), "missing 4x compression candidate")
    require(any(row.get("format_id") == "int8-per-channel" and row.get("status") == "passed" for row in formats), "int8 per-channel did not pass")
    require(len(report.get("recommendations", [])) >= 4, "missing quantization recommendations")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing required source reports")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    require(REPORT_MD.exists(), "missing quantization markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE quantization" in page, "quantization site page missing title")
        require("dequant tax" in page, "quantization site page missing dequant tax")
    print(
        json.dumps(
            {
                "facts": {
                    "formats": report.get("format_count"),
                    "passed": report.get("passed_format_count"),
                    "calibration_needed": report.get("calibration_needed_count"),
                    "recommendations": len(report.get("recommendations", [])),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE quantization memory-format verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
