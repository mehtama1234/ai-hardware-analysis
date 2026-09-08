#!/usr/bin/env python3
"""Execute Triton memory, reduction, softmax and layernorm kernels on CUDA."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

import torch
import triton


HERE = Path(__file__).resolve().parent
OUT = HERE / "reports" / "triton-families-cuda.json"
KERNELS = {
    "memory": HERE / "kernels" / "triton" / "memory.py",
    "reduction": HERE / "kernels" / "triton" / "reduction.py",
    "normalization": HERE / "kernels" / "triton" / "softmax_layernorm.py",
}


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def samples(fn):
    values = []
    for _ in range(7):
        start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        start.record()
        fn()
        end.record()
        end.synchronize()
        values.append(float(start.elapsed_time(end)))
    return values


def main() -> int:
    report = {
        "project": "kernel-benchmarks",
        "experiment": "triton-cuda-families",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gpu_execution_accepted": False,
        "measured": False,
        "source_sha256": {name + ".py": hashlib.sha256(path.read_bytes()).hexdigest() for name, path in KERNELS.items()},
        "rows": [],
    }
    runner_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["source_sha256"]["run_triton_families_cuda.py"] = runner_hash
    if not torch.cuda.is_available():
        report.update({"status": "unavailable:cuda-runtime", "reason": "CUDA is not available"})
    else:
        memory = load(KERNELS["memory"], "triton_memory")
        reduction = load(KERNELS["reduction"], "triton_reduction")
        norm = load(KERNELS["normalization"], "triton_norm")
        rows = []

        for size, stride in ((1_048_576, 1), (65_536, 4), (65_536, 16)):
            x = torch.arange(size * stride, device="cuda", dtype=torch.float32)
            y = torch.empty_like(x)
            block = 256
            grid = (triton.cdiv(size, block),)
            memory.vector_copy_kernel[grid](x, y, n=size * stride, stride=stride, block=block)
            torch.cuda.synchronize()
            values = samples(lambda: memory.vector_copy_kernel[grid](x, y, n=size * stride, stride=stride, block=block))
            error = float((y[::stride] - x[::stride]).abs().max().item())
            rows.append({"family": "memory", "case": f"copy-{size}-stride-{stride}", "max_abs_error": error, "samples_ms": values, "median_ms": statistics.median(values), "grid": list(grid), "block": block})

        n, block = 1_048_576, 256
        x = torch.linspace(-1.0, 1.0, n, device="cuda", dtype=torch.float32)
        partial = torch.empty((triton.cdiv(n, block),), device="cuda", dtype=torch.float32)
        grid = (triton.cdiv(n, block),)
        reduction.block_sum_kernel[grid](x, partial, n=n, block=block)
        torch.cuda.synchronize()
        values = samples(lambda: reduction.block_sum_kernel[grid](x, partial, n=n, block=block))
        error = abs(float(partial.sum().item()) - float(x.sum().item()))
        rows.append({"family": "reduction", "case": f"sum-{n}", "sum_abs_error": error, "samples_ms": values, "median_ms": statistics.median(values), "grid": list(grid), "block": block})

        for rows_count, cols in ((64, 257), (17, 1024)):
            block = triton.next_power_of_2(cols)
            x = torch.randn((rows_count, cols), device="cuda", dtype=torch.float32)
            y = torch.empty_like(x)
            grid = (rows_count,)
            norm.row_softmax_kernel[grid](x, y, cols=cols, block=block)
            torch.cuda.synchronize()
            values = samples(lambda: norm.row_softmax_kernel[grid](x, y, cols=cols, block=block))
            error = float((y - torch.softmax(x, dim=-1)).abs().max().item())
            rows.append({"family": "softmax", "case": f"{rows_count}x{cols}", "max_abs_error": error, "samples_ms": values, "median_ms": statistics.median(values), "grid": list(grid), "block": block})
            y = torch.empty_like(x)
            norm.row_layernorm_kernel[grid](x, y, cols=cols, eps=1e-5, block=block)
            torch.cuda.synchronize()
            values = samples(lambda: norm.row_layernorm_kernel[grid](x, y, cols=cols, eps=1e-5, block=block))
            reference = torch.nn.functional.layer_norm(x, (cols,), eps=1e-5)
            error = float((y - reference).abs().max().item())
            rows.append({"family": "layernorm", "case": f"{rows_count}x{cols}", "max_abs_error": error, "samples_ms": values, "median_ms": statistics.median(values), "grid": list(grid), "block": block})

        passed = all(row.get("max_abs_error", 0.0) <= 3e-4 and len(row["samples_ms"]) == 7 for row in rows if row["family"] != "reduction") and next(row for row in rows if row["family"] == "reduction")["sum_abs_error"] <= 0.02
        report.update({"status": "passed" if passed else "failed", "gpu_execution_accepted": passed, "measured": True, "device_name": torch.cuda.get_device_name(0), "torch_version": torch.__version__, "triton_version": triton.__version__, "rows": rows, "scope": "native Triton memory, block reduction, row softmax and row layernorm kernels versus PyTorch CUDA or exact reduction oracles; seven CUDA-event samples per case"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2))
    return 0 if report["gpu_execution_accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
