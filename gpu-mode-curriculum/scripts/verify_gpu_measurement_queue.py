#!/usr/bin/env python3
"""Verify GPU measurement queue contracts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "gpu-measurement-queue" / "gpu-measurement-queue.json"
REPORT_MD = ROOT / "gpu-measurement-queue" / "reports" / "gpu-measurement-queue.md"
SITE_PAGE = ROOT / "site" / "gpu-measurement-queue.html"
REQUIRED_STEPS = {
    "cuda-kernel-compile",
    "triton-kernel-sweep",
    "tensor-core-gemm",
    "persistent-kernels",
    "parallel-primitives",
    "torch-custom-extension",
    "model-integration-gpu",
    "vllm-serving-trace",
    "attention-serving-stack",
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
        subprocess.run([sys.executable, "scripts/build_gpu_measurement_queue.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    tasks = report.get("tasks", [])
    task_ids = {task.get("step_id") for task in tasks}
    require(report.get("status") == "queue-ready", "GPU measurement queue is not ready")
    require(REQUIRED_STEPS.issubset(task_ids), f"missing measurement tasks: {sorted(REQUIRED_STEPS - task_ids)}")
    require(report.get("task_count") == len(tasks) >= 9, "task count mismatch")
    require(report.get("queued_task_count", 0) + report.get("measured_task_count", 0) == len(tasks), "measurement status counts mismatch")
    require(report.get("accepted_task_count", 0) <= report.get("measured_task_count", 0), "accepted count exceeds measured count")
    require(report.get("failed_measured_task_count", 0) <= report.get("measured_task_count", 0), "failed measured count exceeds measured count")
    require(report.get("real_measured_completion") in {True, False}, "real measured completion flag missing")
    for task in tasks:
        require(task.get("has_metric_contract") is True, f"{task.get('step_id')} missing metric contract")
        require(task.get("has_commands") is True, f"{task.get('step_id')} missing commands")
        require(task.get("has_expected_evidence") is True, f"{task.get('step_id')} missing expected evidence")
        require(task.get("acceptance_thresholds"), f"{task.get('step_id')} missing thresholds")
        require(task.get("measurement_status") in {"queued-for-gpu-host", "measured-accepted", "measured-failed"}, f"{task.get('step_id')} invalid status")
        require(task.get("accepted_measured_rows", 0) <= task.get("real_measured_rows", 0), f"{task.get('step_id')} accepted rows exceed real rows")
        require(task.get("failed_measured_rows", 0) <= task.get("real_measured_rows", 0), f"{task.get('step_id')} failed rows exceed real rows")
        for evaluation in task.get("measurement_evaluations", []):
            require(isinstance(evaluation.get("checks"), dict) and evaluation.get("checks"), f"{task.get('step_id')} missing executable checks")
            require(isinstance(evaluation.get("accepted"), bool), f"{task.get('step_id')} missing accepted flag")
    require(REPORT_MD.exists(), "GPU measurement queue markdown report missing")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE GPU measurement queue" in page, "GPU measurement queue site page missing title")
        require("cuda-kernel-compile" in page and "persistent-kernels" in page and "parallel-primitives" in page and "flash-attention-backward" in page and "sparse-attention-kernels" in page and "fused-training-kernels" in page and "speculative-decoding-serving" in page and "full-gpu-regression" in page, "GPU measurement queue site page missing tasks")
    facts = {
        "tasks": report["task_count"],
        "queued": report["queued_task_count"],
        "measured": report["measured_task_count"],
        "accepted": report["accepted_task_count"],
        "failed_measured": report["failed_measured_task_count"],
        "real_complete": report["real_measured_completion"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE GPU measurement queue verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
