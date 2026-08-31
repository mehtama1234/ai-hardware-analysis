#!/usr/bin/env python3
"""Verify the GPU promotion suite dry-run report."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "gpu-promotion" / "suite-run-report.json"
REPORT_MD = ROOT / "gpu-promotion" / "reports" / "suite-run-report.md"
RUNNER = ROOT / "scripts" / "run_gpu_promotion_suite.py"
REQUIRED_STEPS = {
    "cuda-kernel-compile",
    "triton-kernel-sweep",
    "persistent-kernels",
    "parallel-primitives",
    "torch-custom-extension",
    "model-integration-gpu",
    "vllm-serving-trace",
    "flash-attention-backward",
    "sparse-attention-kernels",
    "fused-training-kernels",
    "speculative-decoding-serving",
    "profiler-capture",
    "rocm-hip-port",
    "distributed-collectives",
    "full-gpu-regression",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_gpu_promotion_suite.py", "--run-id", "local-suite-dry-run"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    commands = report.get("commands", [])
    step_ids = {row.get("step_id") for row in commands}
    require(RUNNER.exists(), "GPU promotion suite runner missing")
    require(REPORT_MD.exists(), "GPU promotion suite markdown report missing")
    require(report.get("status") == "dry-run-ready", "suite report should be dry-run-ready locally")
    require(report.get("mode") == "dry-run", "suite report should be dry-run mode")
    require(report.get("command_count") == len(commands), "suite command count mismatch")
    require(report.get("command_count", 0) >= 20, "suite plan has too few commands")
    require(REQUIRED_STEPS.issubset(step_ids), f"missing suite steps: {sorted(REQUIRED_STEPS - step_ids)}")
    require(report.get("failed") == 0, "dry-run suite should not have failures")
    require(report.get("planned", 0) > 0, "dry-run suite should have planned commands")
    require(report.get("skipped", 0) > 0, "dry-run suite should skip placeholder commands")
    for row in commands:
        require(row.get("command"), f"{row.get('step_id')} missing command")
        require(row.get("expected_evidence"), f"{row.get('step_id')} missing expected evidence")
        require(row.get("validation"), f"{row.get('step_id')} missing validation")
    facts = {
        "commands": report["command_count"],
        "steps": report["step_count"],
        "planned": report["planned"],
        "skipped": report["skipped"],
        "status": report["status"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE GPU promotion suite verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
