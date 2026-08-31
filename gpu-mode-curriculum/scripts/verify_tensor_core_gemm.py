#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "tensor-core-gemm" / "tensor-core-gemm-report.json"
REPORT_MD = ROOT / "tensor-core-gemm" / "reports" / "tensor-core-gemm-report.md"
SITE_PAGE = ROOT / "site" / "tensor-core-gemm.html"
REQUIRED_SOURCES = {
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "compiler-runtime-inspection/compiler-runtime-report.json",
    "autotune-db/autotune-db.json",
    "quantization-memory-formats/quantization-report.json",
    "numerical-reproducibility/numerical-reproducibility-report.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_tensor_core_gemm.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    scenarios = report.get("scenarios", [])
    require(report.get("status") == "tensor-core-gemm-ready", "tensor-core GEMM report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 5, "scenario count mismatch")
    require(report.get("passed_scenarios", 0) >= 4, "too few passing GEMM scenarios")
    require(report.get("tensor_core_eligible_scenarios", 0) >= 5, "tensor-core coverage is too small")
    require(report.get("fused_epilogue_scenarios", 0) >= 4, "fused epilogue coverage is too small")
    require(REQUIRED_SOURCES.issubset(set(report.get("source_reports", []))), "missing source reports")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion must be required")
    for row in scenarios:
        require(row.get("tensor_core_eligible") is True, f"{row.get('scenario_id')} is not tensor-core eligible")
        require(row.get("shared_memory_bytes", 10**9) <= 164 * 1024, f"{row.get('scenario_id')} exceeds shared memory budget")
        require(row.get("register_pressure_proxy", 999) <= 288, f"{row.get('scenario_id')} register pressure too high")
        require(row.get("arithmetic_intensity", 0) > 0, f"{row.get('scenario_id')} missing arithmetic intensity")
    require(REPORT_MD.exists(), "missing tensor-core GEMM markdown report")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE CUTLASS" in page, "tensor-core GEMM site page missing title")
        require("MMA" in page and "epilogue" in page and "shared memory" in page, "site page missing GEMM evidence")
    print(
        json.dumps(
            {
                "facts": {
                    "scenarios": report.get("scenario_count"),
                    "passed": report.get("passed_scenarios"),
                    "tensor_core_eligible": report.get("tensor_core_eligible_scenarios"),
                    "fused_epilogues": report.get("fused_epilogue_scenarios"),
                    "status": report.get("status"),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE CUTLASS/CuTe tensor-core GEMM verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
