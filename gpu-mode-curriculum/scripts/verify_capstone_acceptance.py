#!/usr/bin/env python3
"""Verify the GPUMODE capstone acceptance report."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "capstone-acceptance" / "capstone-acceptance.json"
SITE_PAGE = ROOT / "site" / "capstone-acceptance.html"
REQUIRED_CRITERIA = {
    "lesson-corpus-coverage",
    "one-lab-per-lesson",
    "comprehensive-programs",
    "project-portfolio",
    "kernel-source-and-benchmarks",
    "compiler-runtime-inspection",
    "tensor-core-gemm",
    "persistent-kernels",
    "parallel-primitives",
    "custom-op-model-path",
    "autotune-and-regression",
    "serving-system",
    "kv-cache-paged-attention",
    "attention-serving-stack",
    "flash-attention-backward",
    "sparse-attention-kernels",
    "fused-training-kernels",
    "serving-engine-comparison",
    "speculative-decoding-serving",
    "distributed-topology-planning",
    "distributed-collectives",
    "distributed-training-optimizer",
    "moe-routing-all-to-all",
    "hardware-capacity-planning",
    "quantization-memory-formats",
    "numerical-reproducibility",
    "cuda-graphs-latency",
    "multi-tenant-gpu-scheduling",
    "gpu-promotion-runtime",
    "gpu-promotion-suite",
    "gpu-run-imports",
    "gpu-run-import-lint",
    "gpu-evidence-provenance",
    "gpu-measurement-queue",
    "gpu-acceptance-logic",
    "gpu-host-preflight",
    "gpu-host-handoff",
    "assessment-readiness",
    "assessment-grading",
    "site-and-audit",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/build_capstone_acceptance.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    criteria = report.get("criteria", [])
    criterion_ids = {row.get("id") for row in criteria}
    require(REQUIRED_CRITERIA.issubset(criterion_ids), f"missing acceptance criteria: {sorted(REQUIRED_CRITERIA - criterion_ids)}")
    require(report.get("criteria_count") == len(criteria), "criteria count mismatch")
    require(report.get("score") == report.get("max_score") and report.get("max_score", 0) >= 100, "capstone acceptance did not earn full score")
    require(report.get("failed_criteria") == 0, "capstone acceptance has failed criteria")
    require(report.get("status") == "accepted-with-runtime-caveats", "unexpected capstone acceptance status")
    for row in criteria:
        require(row.get("status") == "passed", f"{row.get('id')} did not pass")
        require(row.get("earned") == row.get("points"), f"{row.get('id')} did not earn full points")
        require(row.get("evidence"), f"{row.get('id')} missing evidence")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE capstone acceptance" in page, "capstone acceptance site page missing title")
        require("accepted-with-runtime-caveats" in page, "capstone acceptance site page missing status")
    facts = {
        "score": report["score"],
        "max_score": report["max_score"],
        "status": report["status"],
        "criteria": report["criteria_count"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE capstone acceptance verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
