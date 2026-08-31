#!/usr/bin/env python3
"""Verify kernel benchmark harness artifacts and source coverage."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "kernel-benchmarks"
REPORT = BENCH / "reports" / "kernel-benchmark-report.json"
PLAN = BENCH / "plan.json"
SITE_PAGE = ROOT / "site" / "kernel-benchmarks.html"
REQUIRED_FAMILIES = {"memory", "reduction", "normalization", "matmul", "fusion"}
REQUIRED_CUDA = {"memory.cu", "reduction.cu", "softmax_layernorm.cu", "matmul_mlp.cu"}
REQUIRED_TRITON = {"memory.py", "reduction.py", "softmax_layernorm.py", "matmul_mlp.py"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_kernel_benchmarks.py"], cwd=ROOT, check=True)
    if not PLAN.exists():
        subprocess.run([sys.executable, "scripts/build_kernel_benchmark_plan.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    plan = load_json(PLAN)
    require(report["benchmark_count"] >= 14, "expected at least fourteen kernel benchmark shape cases")
    require(report["failed"] == 0, "kernel benchmark report has failures")
    require(report["passed"] == report["benchmark_count"], "not every kernel benchmark passed")
    require(REQUIRED_FAMILIES.issubset({row["family"] for row in report["benchmarks"]}), "missing benchmark families")
    require(plan.get("lesson_count") == 118, "kernel benchmark plan should analyze 118 lessons")
    require(plan.get("covered_lessons") == 118, "kernel benchmark plan should cover every lesson")
    require(not plan.get("uncovered_lessons"), "kernel benchmark plan has uncovered lessons")
    require(len(plan.get("families", [])) >= len(REQUIRED_FAMILIES), "kernel benchmark plan missing families")
    for row in report["benchmarks"]:
        require(row["checks"] and all(row["checks"].values()), f"{row['id']} has failed checks")
        require(row["seconds"]["median"] >= 0, f"{row['id']} missing median time")
        require(row.get("shape_class"), f"{row['id']} missing shape class")
    cuda_files = {path.name for path in (BENCH / "kernels" / "cuda").glob("*.cu")}
    triton_files = {path.name for path in (BENCH / "kernels" / "triton").glob("*.py")}
    require(REQUIRED_CUDA.issubset(cuda_files), f"missing CUDA source files: {sorted(REQUIRED_CUDA - cuda_files)}")
    require(REQUIRED_TRITON.issubset(triton_files), f"missing Triton source files: {sorted(REQUIRED_TRITON - triton_files)}")
    require((BENCH / "README.md").exists(), "missing kernel benchmark README")
    require((BENCH / "PLAN.md").exists(), "missing kernel benchmark lesson map")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE kernel benchmarks" in page, "kernel benchmark site page missing title")
        require("Benchmark Sweeps" in page, "kernel benchmark site page missing sweeps")
        require("118" in page, "kernel benchmark site page missing lesson coverage")
    facts = {
        "benchmarks": report["benchmark_count"],
        "passed": report["passed"],
        "families": sorted({row["family"] for row in report["benchmarks"]}),
        "shape_classes": sorted({row["shape_class"] for row in report["benchmarks"]}),
        "covered_lessons": plan.get("covered_lessons"),
        "torch_device": report["accelerator_readiness"].get("torch_device"),
        "nvcc": report["accelerator_readiness"].get("nvcc"),
        "cuda_sources": len(cuda_files),
        "triton_sources": len(triton_files),
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE kernel benchmark verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
