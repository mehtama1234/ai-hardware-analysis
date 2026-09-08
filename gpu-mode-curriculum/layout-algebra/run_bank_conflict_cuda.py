#!/usr/bin/env python3
"""Compile and run a shared-memory bank-conflict microbenchmark."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
KERNEL = HERE / "bank_conflict_kernel.cu"
RUNNER = HERE / "bank_conflict_runner.cu"
OUT = HERE / "reports/bank-conflict-cuda.json"


def main():
    nvcc = shutil.which("nvcc")
    report = {"experiment": "shared_memory_bank_conflict", "generated_at": datetime.now(timezone.utc).isoformat(),
              "source_sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in (("kernel", KERNEL), ("runner", RUNNER), ("launcher", Path(__file__)))},
              "gpu_execution_accepted": False}
    if not nvcc:
        report.update({"status": "unavailable", "reason": "nvcc not found on PATH", "scope": "CUDA source present; no compiler/runtime"})
        OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2) + "\n"); print(json.dumps(report, indent=2)); return 2
    with tempfile.TemporaryDirectory(prefix="layout-bank-conflict-") as build:
        binary = Path(build) / "bank_conflict"
        command = [nvcc, "-O3", "-std=c++17", str(KERNEL), str(RUNNER), "-o", str(binary)]
        compiled = subprocess.run(command, cwd=HERE, capture_output=True, text=True, timeout=180, check=False)
        if compiled.returncode != 0:
            report.update({"status": "compile-failed", "stderr_tail": compiled.stderr[-4000:]})
            OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2) + "\n"); print(json.dumps(report, indent=2)); return 1
        execution = subprocess.run([str(binary)], cwd=HERE, capture_output=True, text=True, timeout=180, check=False)
    report.update({"status": "passed" if execution.returncode == 0 else "run-failed", "returncode": execution.returncode, "stdout": execution.stdout[-12000:], "stderr": execution.stderr[-4000:]})
    if execution.returncode == 0:
        try:
            payload = json.loads(execution.stdout.strip().splitlines()[-1])
            report["native"] = payload
            report["gpu_execution_accepted"] = payload.get("gpu_execution_accepted") is True and all(case.get("passed") is True and case.get("max_relative_error", 99) <= 0.002 for case in payload.get("cases", []))
        except (ValueError, IndexError):
            report["status"] = "invalid-output"
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n"); print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2)); return 0 if report["gpu_execution_accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
