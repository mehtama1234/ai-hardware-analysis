#!/usr/bin/env python3
"""Verify assessment grading output."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "assessment" / "grading-report.json"
REPORT_MD = ROOT / "assessment" / "reports" / "grading-report.md"
SITE_PAGE = ROOT / "site" / "assessment-grading.html"
REQUIRED_LAYERS = {
    "lesson-labs",
    "comprehensive-labs",
    "kernel-benchmarks",
    "compiler-runtime-inspection",
    "tensor-core-gemm",
    "persistent-kernels",
    "parallel-primitives",
    "custom-ops",
    "autotune-db",
    "model-integration",
    "serving-traces",
    "kv-cache-paged-attention",
    "attention-serving-stack",
    "flash-attention-backward",
    "sparse-attention-kernels",
    "fused-training-kernels",
    "serving-engine-comparison",
    "speculative-decoding-serving",
    "distributed-topology",
    "distributed-collectives",
    "distributed-training-optimizer",
    "moe-routing-all-to-all",
    "hardware-capacity",
    "quantization-memory-formats",
    "numerical-reproducibility",
    "cuda-graphs-latency",
    "multi-tenant-gpu-scheduling",
    "profiler-evidence",
    "gpu-promotion",
    "gpu-promotion-suite",
    "gpu-runs",
    "gpu-import-lint",
    "gpu-provenance",
    "gpu-measurement-queue",
    "gpu-acceptance-logic",
    "gpu-host-preflight",
    "gpu-handoff",
    "regression-ledger",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/grade_assessment.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    results = report.get("results", [])
    practical_layers = {row.get("layer") for row in results if row.get("type") == "practical-task"}
    require(report.get("status") == "passed", "assessment grading did not pass")
    require(report.get("score") == report.get("max_score"), "assessment grading did not earn full score")
    require(report.get("concept_count") >= 10, "too few graded concept checks")
    require(report.get("practical_count") >= 12, "too few graded practical tasks")
    require(REQUIRED_LAYERS.issubset(practical_layers), f"missing graded practical layers: {sorted(REQUIRED_LAYERS - practical_layers)}")
    require(report.get("failed_count") == 0, "assessment grading has failed items")
    require(REPORT_MD.exists(), "assessment grading markdown report missing")
    for row in results:
        require(row.get("status") == "passed", f"{row.get('id')} did not pass")
        require(row.get("earned") == row.get("points"), f"{row.get('id')} did not earn full points")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE assessment grading" in page, "assessment grading site page missing title")
        require("practical-compiler-runtime-inspection" in page, "assessment grading site page missing compiler runtime task")
        require("practical-tensor-core-gemm" in page, "assessment grading site page missing tensor-core GEMM task")
        require("practical-persistent-kernels" in page, "assessment grading site page missing persistent kernels task")
        require("practical-parallel-primitives" in page, "assessment grading site page missing parallel primitives task")
        require("practical-gpu-promotion-suite" in page, "assessment grading site page missing suite task")
        require("practical-kv-cache-paged-attention" in page, "assessment grading site page missing KV-cache task")
        require("practical-attention-serving-stack" in page, "assessment grading site page missing attention serving task")
        require("practical-flash-attention-backward" in page, "assessment grading site page missing FlashAttention backward task")
        require("practical-sparse-attention-kernels" in page, "assessment grading site page missing sparse attention task")
        require("practical-fused-training-kernels" in page, "assessment grading site page missing fused training task")
        require("practical-serving-engine-comparison" in page, "assessment grading site page missing serving engine task")
        require("practical-speculative-decoding-serving" in page, "assessment grading site page missing speculative decoding task")
        require("practical-distributed-topology" in page, "assessment grading site page missing distributed topology task")
        require("practical-distributed-collectives" in page, "assessment grading site page missing distributed collectives task")
        require("practical-distributed-training-optimizer" in page, "assessment grading site page missing distributed training optimizer task")
        require("practical-moe-routing-all-to-all" in page, "assessment grading site page missing MoE task")
        require("practical-hardware-capacity" in page, "assessment grading site page missing hardware capacity task")
        require("practical-quantization-memory-formats" in page, "assessment grading site page missing quantization task")
        require("practical-numerical-reproducibility" in page, "assessment grading site page missing numerical reproducibility task")
        require("practical-cuda-graphs-latency" in page, "assessment grading site page missing CUDA Graphs task")
        require("practical-multi-tenant-gpu-scheduling" in page, "assessment grading site page missing multi-tenant scheduling task")
        require("practical-gpu-host-preflight" in page, "assessment grading site page missing preflight task")
    facts = {
        "score": report["score"],
        "max_score": report["max_score"],
        "concept_count": report["concept_count"],
        "practical_count": report["practical_count"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE assessment grading verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
