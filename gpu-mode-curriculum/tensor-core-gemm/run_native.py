#!/usr/bin/env python3
"""Compile and execute the WMMA tensor-core GEMM promotion probe."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "native_wmma_runner.cu"
OUT = HERE / "native-execution.json"


def main() -> int:
    nvcc = shutil.which("nvcc")
    report = {"project": "tensor-core-gemm", "generated_at": datetime.now(timezone.utc).isoformat(),
              "source_sha256": {"native_wmma_runner.cu": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                                 "run_native.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
              "gpu_execution_accepted": False}
    if not nvcc:
        report.update({"status": "unavailable", "reason": "nvcc not found on PATH"})
        OUT.write_text(json.dumps(report, indent=2) + "\n")
        return 2
    with tempfile.TemporaryDirectory(prefix="wmma-gemm-") as build:
        binary = Path(build) / "native_wmma_runner"
        command = [nvcc, "-O3", "-std=c++17", "-arch=sm_75", str(SOURCE), "-lcublas", "-o", str(binary)]
        try:
            compiled = subprocess.run(command, cwd=HERE, capture_output=True, text=True, timeout=180, check=False)
        except subprocess.TimeoutExpired as exc:
            report.update({"status": "compile-timeout", "command": str(exc.cmd)})
            OUT.write_text(json.dumps(report, indent=2) + "\n")
            return 1
        if compiled.returncode:
            report.update({"status": "compile-failed", "stderr_tail": compiled.stderr[-6000:], "stdout_tail": compiled.stdout[-2000:]})
            OUT.write_text(json.dumps(report, indent=2) + "\n")
            return 1
        execution = subprocess.run([str(binary)], cwd=HERE, capture_output=True, text=True, timeout=180, check=False)
    report.update({"status": "passed" if execution.returncode == 0 else "run-failed", "returncode": execution.returncode,
                   "stdout": execution.stdout[-12000:], "stderr": execution.stderr[-4000:]})
    if execution.returncode == 0:
        try:
            payload = json.loads(execution.stdout.strip().splitlines()[-1]); report["native"] = payload
            report["gpu_execution_accepted"] = payload.get("gpu_execution_accepted") is True and len(payload.get("wmma_samples_ms", [])) == 7 and len(payload.get("cublas_samples_ms", [])) == 7
        except (ValueError, IndexError):
            report["status"] = "invalid-output"
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2))
    return 0 if report["gpu_execution_accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
