#!/usr/bin/env python3
"""Compile and execute the native fused-MLP CUDA probe."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "native_mlp_runner.cu"
OUT = HERE / "reports/native-mlp-execution.json"


def main() -> int:
    nvcc = shutil.which("nvcc")
    report = {"project": "kernel-benchmarks-native-fused-mlp", "generated_at": datetime.now(timezone.utc).isoformat(), "source_sha256": {"native_mlp_runner.cu": hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "run_native_mlp.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}, "gpu_execution_accepted": False}
    if not nvcc:
        report.update({"status": "unavailable", "reason": "nvcc not found on PATH"}); OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2) + "\n"); return 2
    with tempfile.TemporaryDirectory(prefix="native-mlp-") as build:
        binary = Path(build) / "native_mlp_runner"; compiled = subprocess.run([nvcc, "-O3", "-std=c++17", str(SOURCE), "-o", str(binary)], cwd=HERE, capture_output=True, text=True, timeout=180, check=False)
        if compiled.returncode:
            report.update({"status": "compile-failed", "stderr_tail": compiled.stderr[-6000:], "stdout_tail": compiled.stdout[-2000:]}); OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2) + "\n"); return 1
        execution = subprocess.run([str(binary)], cwd=HERE, capture_output=True, text=True, timeout=180, check=False)
    report.update({"status": "passed" if execution.returncode == 0 else "run-failed", "returncode": execution.returncode, "stdout": execution.stdout[-12000:], "stderr": execution.stderr[-4000:]})
    if execution.returncode == 0:
        try:
            payload = json.loads(execution.stdout.strip().splitlines()[-1]); report["native"] = payload; report["gpu_execution_accepted"] = payload.get("gpu_execution_accepted") is True and len(payload.get("samples_ms", [])) == 7
        except (ValueError, IndexError): report["status"] = "invalid-output"
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n"); print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2)); return 0 if report["gpu_execution_accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
