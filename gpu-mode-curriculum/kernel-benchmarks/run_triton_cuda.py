#!/usr/bin/env python3
"""Execute the repository's Triton matmul kernel on CUDA with an oracle."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import torch


HERE = Path(__file__).resolve().parent
OUT = HERE / "reports" / "triton-cuda.json"
KERNEL_PATH = HERE / "kernels" / "triton" / "matmul_mlp.py"
SHAPES = ((128, 128, 128), (31, 17, 33), (257, 65, 49))


def load_kernel():
    spec = importlib.util.spec_from_file_location("gpumode_triton_matmul", KERNEL_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.matmul_kernel


def main() -> int:
    report = {
        "project": "kernel-benchmarks",
        "experiment": "triton-cuda-matmul",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gpu_execution_accepted": False,
        "measured": False,
        "source_sha256": {
            "run_triton_cuda.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "kernels/triton/matmul_mlp.py": hashlib.sha256(KERNEL_PATH.read_bytes()).hexdigest(),
        },
    }
    if not torch.cuda.is_available():
        report.update({"status": "unavailable:cuda-runtime", "reason": "CUDA is not available"})
    else:
        import triton

        kernel = load_kernel()
        rows = []
        for m, n, k in SHAPES:
            torch.manual_seed(421 + m + n + k)
            a = torch.randn((m, k), device="cuda", dtype=torch.float32)
            b = torch.randn((k, n), device="cuda", dtype=torch.float32)
            c = torch.empty((m, n), device="cuda", dtype=torch.float32)
            grid = (triton.cdiv(m, 32), triton.cdiv(n, 32))
            kernel[grid](a, b, c, m=m, n=n, k=k, bm=32, bn=32, bk=32)
            torch.cuda.synchronize()
            reference = a @ b
            max_error = float((c - reference).abs().max().item())
            samples = []
            for _ in range(7):
                start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
                start.record()
                kernel[grid](a, b, c, m=m, n=n, k=k, bm=32, bn=32, bk=32)
                end.record()
                end.synchronize()
                samples.append(float(start.elapsed_time(end)))
            rows.append({
                "shape": [m, n, k],
                "max_abs_error": max_error,
                "samples_ms": samples,
                "median_ms": statistics.median(samples),
                "grid": list(grid),
                "block": [32, 32, 32],
                "torch_version": torch.__version__,
            })
        passed = all(row["max_abs_error"] <= 2e-4 and len(row["samples_ms"]) == 7 for row in rows)
        report.update({
            "status": "passed" if passed else "failed",
            "gpu_execution_accepted": passed,
            "measured": True,
            "device_name": torch.cuda.get_device_name(0),
            "triton_version": triton.__version__,
            "rows": rows,
            "scope": "native Triton JIT kernel versus torch CUDA FP32 oracle; CUDA-event steady-state samples exclude first compilation call",
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2))
    return 0 if report["gpu_execution_accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
