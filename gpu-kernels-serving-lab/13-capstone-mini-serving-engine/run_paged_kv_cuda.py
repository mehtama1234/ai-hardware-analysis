#!/usr/bin/env python3
"""Compile and execute the native CUDA paged-KV gather proof."""
from __future__ import annotations
import hashlib, json, shutil, subprocess, tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
KERNEL = HERE / "paged_kv_gather.cu"
RUNNER = HERE / "paged_kv_gather_runner.cu"
_ROOT_CANDIDATE = Path(__file__).resolve().parents[2]
CURRICULUM = _ROOT_CANDIDATE if (_ROOT_CANDIDATE / "model-integration").is_dir() else _ROOT_CANDIDATE / "gpu-mode-curriculum"
OUT = CURRICULUM / "model-integration/reports/paged-kv-cuda.json"

def main():
    nvcc = shutil.which("nvcc")
    report = {"experiment": "paged_kv_gather_cuda", "generated_at": datetime.now(timezone.utc).isoformat(),
              "source_sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in (("kernel", KERNEL), ("runner", RUNNER), ("launcher", Path(__file__)))},
              "gpu_execution_accepted": False, "measured": False}
    if not nvcc:
        report.update(status="unavailable", reason="nvcc not found on PATH", scope="native CUDA paged gather source present; no compiler/runtime")
        OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2) + "\n"); print(json.dumps(report, indent=2)); return 2
    with tempfile.TemporaryDirectory(prefix="paged-kv-cuda-") as build:
        binary = Path(build) / "paged_kv_gather"
        compiled = subprocess.run([nvcc, "-O3", "-std=c++17", str(KERNEL), str(RUNNER), "-o", str(binary)], cwd=HERE, capture_output=True, text=True, timeout=180)
        if compiled.returncode != 0:
            report.update(status="compile-failed", stderr_tail=compiled.stderr[-4000:])
        else:
            execution = subprocess.run([str(binary)], cwd=HERE, capture_output=True, text=True, timeout=180)
            report.update(status="passed" if execution.returncode == 0 else "run-failed", measured=execution.returncode == 0, stdout=execution.stdout[-4000:], stderr=execution.stderr[-4000:])
            if execution.returncode == 0:
                try:
                    payload = json.loads(execution.stdout.strip().splitlines()[-1]); report["native"] = payload
                    report["gpu_execution_accepted"] = payload.get("gpu_execution_accepted") is True and payload.get("max_abs_error") == 0
                except (ValueError, IndexError): report["status"] = "invalid-output"
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2))
    return 0 if report["gpu_execution_accepted"] else 1

if __name__ == "__main__": raise SystemExit(main())
