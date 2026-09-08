#!/usr/bin/env python3
"""Measure a fixed-shape CUDA Graph capture/replay against eager CUDA."""

from __future__ import annotations

import hashlib
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

import torch


HERE = Path(__file__).resolve().parent
OUT = HERE / "reports" / "cuda-graphs-cuda.json"


def event_samples(fn, count=7):
    samples = []
    result = None
    for _ in range(count):
        start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        start.record()
        result = fn()
        end.record()
        end.synchronize()
        samples.append(float(start.elapsed_time(end)))
    return result, samples


def main() -> int:
    report = {
        "project": "cuda-graphs-latency",
        "experiment": "native-cuda-graph-capture",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gpu_execution_accepted": False,
        "measured": False,
        "source_sha256": {"run_cuda_graphs_cuda.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
    }
    if not torch.cuda.is_available():
        report.update({"status": "unavailable:cuda-runtime", "reason": "CUDA is not available"})
    else:
        torch.manual_seed(2207)
        shape = (512, 512)
        a = torch.randn(shape, device="cuda", dtype=torch.float32)
        b = torch.randn(shape, device="cuda", dtype=torch.float32)
        bias = torch.randn(shape[1], device="cuda", dtype=torch.float32)

        def eager():
            return torch.relu(a @ b + bias)

        # Warm up allocators and kernels before capture and steady-state timing.
        for _ in range(5):
            eager()
        torch.cuda.synchronize()
        eager_output, eager_samples = event_samples(eager)
        torch.cuda.synchronize()

        static_a = a.clone()
        static_b = b.clone()
        static_bias = bias.clone()
        static_output = torch.empty_like(eager_output)
        graph = torch.cuda.CUDAGraph()
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        with torch.cuda.graph(graph):
            static_output.copy_(torch.relu(static_a @ static_b + static_bias))
        torch.cuda.synchronize()
        graph_output, graph_samples = event_samples(graph.replay)
        torch.cuda.synchronize()
        max_error = float((static_output - eager_output).abs().max().item())
        report.update({
            "status": "passed" if max_error <= 2e-4 else "failed",
            "gpu_execution_accepted": max_error <= 2e-4,
            "measured": True,
            "device_name": torch.cuda.get_device_name(0),
            "torch_version": torch.__version__,
            "shape": list(shape),
            "max_abs_error": max_error,
            "eager_samples_ms": eager_samples,
            "graph_samples_ms": graph_samples,
            "eager_median_ms": statistics.median(eager_samples),
            "graph_median_ms": statistics.median(graph_samples),
            "speedup_eager_over_graph": statistics.median(eager_samples) / max(statistics.median(graph_samples), 1e-12),
            "peak_allocated_bytes_after_capture": torch.cuda.max_memory_allocated(),
            "capture_constraints": ["fixed tensor shapes", "static input addresses", "no allocator-changing operations inside replay"],
            "fallback_strategy": "recapture or use eager execution when shapes, addresses, or control flow change",
            "scope": "one CUDA device, fixed-shape matmul-plus-ReLU graph; graph replay versus eager CUDA event timings; no multi-stream or production serving claim",
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2))
    return 0 if report["gpu_execution_accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
