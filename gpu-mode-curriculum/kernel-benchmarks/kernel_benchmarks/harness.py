from __future__ import annotations

import json
import importlib.util
import shutil
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from . import ops


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "kernel-benchmarks" / "reports"
REPORT_JSON = REPORTS / "kernel-benchmark-report.json"
REPORT_MD = REPORTS / "kernel-benchmark-report.md"


BENCHMARKS: list[dict[str, Any]] = [
    {"id": "vector-copy-contiguous-64k", "family": "memory", "shape_class": "small", "fn": ops.vector_copy, "params": {"size": 65536, "stride": 1}, "required": ["shape", "sum"]},
    {"id": "vector-copy-contiguous-1m", "family": "memory", "shape_class": "medium", "fn": ops.vector_copy, "params": {"size": 1048576, "stride": 1}, "required": ["shape", "sum"]},
    {"id": "vector-copy-strided-64k-s4", "family": "memory", "shape_class": "strided", "fn": ops.vector_copy, "params": {"size": 65536, "stride": 4}, "required": ["shape", "sum"]},
    {"id": "vector-copy-strided-64k-s16", "family": "memory", "shape_class": "strided", "fn": ops.vector_copy, "params": {"size": 65536, "stride": 16}, "required": ["shape", "sum"]},
    {"id": "reduction-sum-max-128k", "family": "reduction", "shape_class": "medium", "fn": ops.reduction, "params": {"size": 131072}, "required": ["sum", "max"]},
    {"id": "reduction-sum-max-1m", "family": "reduction", "shape_class": "large", "fn": ops.reduction, "params": {"size": 1048576}, "required": ["sum", "max"]},
    {"id": "softmax-8x256", "family": "normalization", "shape_class": "narrow", "fn": ops.softmax, "params": {"rows": 8, "cols": 256}, "required": ["row_sums"]},
    {"id": "softmax-4x1024", "family": "normalization", "shape_class": "wide", "fn": ops.softmax, "params": {"rows": 4, "cols": 1024}, "required": ["row_sums"]},
    {"id": "layernorm-8x256", "family": "normalization", "shape_class": "narrow", "fn": ops.layernorm, "params": {"rows": 8, "cols": 256}, "required": ["means"]},
    {"id": "layernorm-4x1024", "family": "normalization", "shape_class": "wide", "fn": ops.layernorm, "params": {"rows": 4, "cols": 1024}, "required": ["means"]},
    {"id": "matmul-64", "family": "matmul", "shape_class": "small-square", "fn": ops.matmul, "params": {"m": 64, "n": 64, "k": 64}, "required": ["shape", "checksum"]},
    {"id": "matmul-128", "family": "matmul", "shape_class": "medium-square", "fn": ops.matmul, "params": {"m": 128, "n": 128, "k": 128}, "required": ["shape", "checksum"]},
    {"id": "fused-mlp-16x128", "family": "fusion", "shape_class": "small-hidden", "fn": ops.fused_mlp, "params": {"batch": 16, "hidden": 128, "intermediate": 256}, "required": ["shape", "checksum"]},
    {"id": "fused-mlp-8x256", "family": "fusion", "shape_class": "medium-hidden", "fn": ops.fused_mlp, "params": {"batch": 8, "hidden": 256, "intermediate": 512}, "required": ["shape", "checksum"]},
]


def accelerator_readiness() -> dict[str, Any]:
    return {
        "torch_available": ops.has_torch(),
        "torch_device": ops.device(),
        "nvcc": bool(shutil.which("nvcc")),
        "hipcc": bool(shutil.which("hipcc")),
        "nvidia_smi": bool(shutil.which("nvidia-smi")),
        "triton_available": importlib.util.find_spec("triton") is not None,
    }


def timed_call(fn: Callable[..., dict[str, Any]], params: dict[str, Any], repeats: int) -> dict[str, Any]:
    durations = []
    result: dict[str, Any] = {}
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn(**params)
        durations.append(time.perf_counter() - start)
    return {
        "result": result,
        "seconds": {
            "min": min(durations),
            "median": statistics.median(durations),
            "max": max(durations),
        },
    }


def validate(row: dict[str, Any], required: list[str]) -> dict[str, bool]:
    result = row.get("result", {})
    checks = {f"has_{field}": field in result for field in required}
    if "row_sums" in result:
        checks["softmax_rows_sum_to_one"] = all(abs(v - 1.0) <= 1e-5 for v in result["row_sums"])
    if "means" in result:
        checks["layernorm_means_near_zero"] = all(abs(v) <= 1e-4 for v in result["means"])
    if "shape" in result:
        checks["shape_positive"] = all(v > 0 for v in result["shape"])
    if "checksum" in result:
        checks["checksum_finite"] = isinstance(result["checksum"], (int, float))
    return checks


def run_all(repeats: int = 3) -> dict[str, Any]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    rows = []
    for bench in BENCHMARKS:
        timing = timed_call(bench["fn"], bench["params"], repeats)
        checks = validate(timing, bench["required"])
        rows.append(
            {
                "id": bench["id"],
                "family": bench["family"],
                "shape_class": bench["shape_class"],
                "params": bench["params"],
                "status": "passed" if all(checks.values()) else "failed",
                "checks": checks,
                **timing,
            }
        )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_count": len(rows),
        "passed": sum(1 for row in rows if row["status"] == "passed"),
        "failed": sum(1 for row in rows if row["status"] != "passed"),
        "accelerator_readiness": accelerator_readiness(),
        "benchmarks": rows,
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(markdown(report), encoding="utf-8")
    return report


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Kernel Benchmark Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        f"Benchmarks: {report['benchmark_count']}",
        f"Passed: {report['passed']}",
        f"Failed: {report['failed']}",
        "",
        "## Runtime Readiness",
        "",
    ]
    for key, value in report["accelerator_readiness"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Results", "", "| Benchmark | Family | Shape | Status | Median seconds | Device |", "|---|---|---|---|---|---|"])
    for row in report["benchmarks"]:
        lines.append(
            f"| {row['id']} | {row['family']} | {row['shape_class']} | {row['status']} | "
            f"{row['seconds']['median']:.8f} | {row['result'].get('device', '')} |"
        )
    return "\n".join(lines).rstrip() + "\n"
