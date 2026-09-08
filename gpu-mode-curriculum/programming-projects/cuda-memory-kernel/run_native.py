#!/usr/bin/env python3
"""Compile and execute the CUDA memory-coalescing project on a GPU host."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
KERNEL = HERE / "kernel.cu"
RUNNER = HERE / "native_runner.cu"
OUT = HERE / "native-execution.json"


def main() -> int:
    nvcc = shutil.which("nvcc")
    report = {
        "project": "cuda-memory-kernel",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest()
                          for name, path in (("kernel.cu", KERNEL), ("native_runner.cu", RUNNER),
                                              ("run_native.py", Path(__file__)))},
        "gpu_execution_accepted": False,
    }
    if not nvcc:
        report.update({"status": "unavailable", "reason": "nvcc not found on PATH"})
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 2
    with tempfile.TemporaryDirectory(prefix="cuda-memory-kernel-") as build:
        obj = Path(build) / "kernel.o"
        binary = Path(build) / "cuda_memory_kernel"
        compile_kernel = [nvcc, "-O3", "-std=c++17", "-c", "-Dmain=source_only_main", str(KERNEL), "-o", str(obj)]
        compile_runner = [nvcc, "-O3", "-std=c++17", str(RUNNER), str(obj), "-o", str(binary)]
        try:
            first = subprocess.run(compile_kernel, cwd=HERE, capture_output=True, text=True, timeout=120, check=False)
            second = subprocess.run(compile_runner, cwd=HERE, capture_output=True, text=True, timeout=120, check=False) if first.returncode == 0 else None
        except subprocess.TimeoutExpired as exc:
            report.update({"status": "compile-timeout", "command": str(exc.cmd)})
            OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            return 1
        if first.returncode != 0 or second is None or second.returncode != 0:
            failed = second if second is not None and second.returncode != 0 else first
            report.update({"status": "compile-failed", "stdout_tail": failed.stdout[-4000:], "stderr_tail": failed.stderr[-4000:]})
            OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            return 1
        execution = subprocess.run([str(binary)], cwd=HERE, capture_output=True, text=True, timeout=120, check=False)
    report.update({"status": "passed" if execution.returncode == 0 else "run-failed",
                   "returncode": execution.returncode, "stdout": execution.stdout[-12000:],
                   "stderr": execution.stderr[-4000:]})
    if execution.returncode == 0:
        try:
            payload = json.loads(execution.stdout.strip().splitlines()[-1])
            report["native"] = payload
            report["gpu_execution_accepted"] = payload.get("gpu_execution_accepted") is True and all(
                case.get("passed") is True and case.get("max_abs_error") == 0 for case in payload.get("cases", []))
        except (ValueError, IndexError, KeyError):
            report["status"] = "invalid-output"
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2))
    return 0 if report["gpu_execution_accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
