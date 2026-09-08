#!/usr/bin/env python3
"""Measure native CUDA FP16 GEMM against an FP32 oracle.

This is intentionally narrower than a quantized-model quality study: it proves
native half-precision activation/weight compute, memory reduction, and numeric
error on declared shapes. Packed INT4 and task-quality claims remain separate.
"""

from __future__ import annotations

import hashlib
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

import torch


HERE = Path(__file__).resolve().parent
OUT = HERE / "reports" / "low-precision-cuda.json"
SHAPES = ((256, 256, 256), (31, 17, 33), (513, 65, 49))
INT8_SHAPES = ((256, 256, 256), (64, 48, 32), (128, 96, 64))


def main() -> int:
    report = {
        "project": "quantization-memory-formats",
        "experiment": "native-fp16-cuda",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gpu_execution_accepted": False,
        "measured": False,
        "source_sha256": {"run_low_precision_cuda.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
    }
    if not torch.cuda.is_available():
        report.update({"status": "unavailable:cuda-runtime", "reason": "CUDA is not available"})
    else:
        rows = []
        for m, n, k in SHAPES:
            torch.manual_seed(991 + m + n + k)
            a32 = torch.randn((m, k), device="cuda", dtype=torch.float32)
            b32 = torch.randn((k, n), device="cuda", dtype=torch.float32)
            reference = a32 @ b32
            a16, b16 = a32.half(), b32.half()
            # Warm up allocation and kernel selection outside steady-state samples.
            _ = a16 @ b16
            torch.cuda.synchronize()
            samples = []
            output = None
            for _ in range(7):
                start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
                start.record()
                output = a16 @ b16
                end.record()
                end.synchronize()
                samples.append(float(start.elapsed_time(end)))
            output32 = output.float()
            abs_error = float((output32 - reference).abs().max().item())
            relative_error = float(((output32 - reference).abs() / reference.abs().clamp_min(1e-5)).max().item())
            rows.append({
                "shape": [m, n, k],
                "dtype": "float16",
                "reference_dtype": "float32",
                "max_abs_error": abs_error,
                "max_relative_error": relative_error,
                "samples_ms": samples,
                "median_ms": statistics.median(samples),
                "fp32_input_bytes": (a32.numel() + b32.numel()) * 4,
                "fp16_input_bytes": (a16.numel() + b16.numel()) * 2,
                "input_memory_reduction": 1.0 - ((a16.numel() + b16.numel()) * 2) / ((a32.numel() + b32.numel()) * 4),
            })
        int8_rows = []
        for m, n, k in INT8_SHAPES:
            torch.manual_seed(1193 + m + n + k)
            a32 = torch.randn((m, k), device="cuda", dtype=torch.float32)
            b32 = torch.randn((k, n), device="cuda", dtype=torch.float32)
            reference = a32 @ b32
            scale_a = float(a32.abs().max().item()) / 127.0 or 1.0
            scale_b = float(b32.abs().max().item()) / 127.0 or 1.0
            a8 = (a32 / scale_a).round().clamp(-128, 127).to(torch.int8)
            b8 = (b32 / scale_b).round().clamp(-128, 127).to(torch.int8)
            _ = torch._int_mm(a8, b8)
            torch.cuda.synchronize()
            samples = []
            output = None
            for _ in range(7):
                start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
                start.record()
                output = torch._int_mm(a8, b8)
                end.record()
                end.synchronize()
                samples.append(float(start.elapsed_time(end)))
            dequantized = output.float() * (scale_a * scale_b)
            integer_oracle = a8.cpu().to(torch.int32) @ b8.cpu().to(torch.int32)
            integer_max_error = int((output.cpu() - integer_oracle).abs().max().item())
            int8_rows.append({
                "shape": [m, n, k],
                "dtype": "int8",
                "accumulator_dtype": "int32",
                "dequant_scale": scale_a * scale_b,
                "integer_oracle_max_error": integer_max_error,
                "max_abs_error": float((dequantized - reference).abs().max().item()),
                "max_relative_error": float(((dequantized - reference).abs() / reference.abs().clamp_min(1e-5)).max().item()),
                "samples_ms": samples,
                "median_ms": statistics.median(samples),
                "fp32_input_bytes": (a32.numel() + b32.numel()) * 4,
                "int8_input_bytes": (a8.numel() + b8.numel()),
                "input_memory_reduction": 1.0 - (a8.numel() + b8.numel()) / ((a32.numel() + b32.numel()) * 4),
            })
        passed = all(row["max_abs_error"] <= 0.2 and len(row["samples_ms"]) == 7 for row in rows)
        int8_passed = all(row["integer_oracle_max_error"] == 0 and row["max_abs_error"] <= 1.0 and len(row["samples_ms"]) == 7 for row in int8_rows)
        report.update({
            "status": "passed" if passed and int8_passed else "failed",
            "gpu_execution_accepted": passed and int8_passed,
            "measured": True,
            "device_name": torch.cuda.get_device_name(0),
            "torch_version": torch.__version__,
            "rows": rows,
            "int8_rows": int8_rows,
            "scope": "native CUDA FP16 and torch._int_mm INT8 activation/weight matmul versus FP32 oracle; CUDA-event steady-state samples; no packed INT4, model-quality, or training claim",
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2))
    return 0 if report["gpu_execution_accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
