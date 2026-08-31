#!/usr/bin/env python3
"""Verify the GPUMODE assessment bank."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QUESTION_BANK = ROOT / "assessment" / "question-bank.json"
REPORT_MD = ROOT / "assessment" / "reports" / "assessment-report.md"
SITE_PAGE = ROOT / "site" / "assessment.html"
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
    if not QUESTION_BANK.exists():
        subprocess.run([sys.executable, "scripts/build_assessment.py"], cwd=ROOT, check=True)
    assessment = load_json(QUESTION_BANK)
    questions = assessment.get("questions", [])
    practical_tasks = assessment.get("practical_tasks", [])
    layers = {task.get("layer") for task in practical_tasks}
    require(assessment.get("status") == "ready", "assessment is not ready")
    require(assessment.get("concept_question_count") == len(questions) >= 10, "concept question count mismatch")
    require(assessment.get("practical_task_count") == len(practical_tasks) >= 10, "practical task count mismatch")
    require(REQUIRED_LAYERS.issubset(layers), f"missing practical layers: {sorted(REQUIRED_LAYERS - layers)}")
    require(assessment.get("tutorial_provider_count", 0) >= 5, "too few tutorial providers")
    require(assessment.get("total_points", 0) >= 100, "assessment total points too low")
    require(assessment.get("pass_score") == int(assessment["total_points"] * 0.8), "pass score mismatch")
    for question in questions:
        require(question.get("source_lessons"), f"{question.get('id')} missing source lessons")
        require(len(question.get("expected_answer_points", [])) >= 3, f"{question.get('id')} missing answer key")
        require(question.get("related_tutorial_sources"), f"{question.get('id')} missing tutorial sources")
    for task in practical_tasks:
        require(task.get("command", "").startswith("python3 "), f"{task.get('id')} has unexpected command")
        require(task.get("expected_evidence"), f"{task.get('id')} missing evidence")
        require(task.get("grading_checks"), f"{task.get('id')} missing grading checks")
    require(REPORT_MD.exists(), "assessment markdown report missing")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE assessment bank" in page, "assessment site page missing title")
        require("Practical Tasks" in page, "assessment site page missing practical tasks")
    facts = {
        "concept_questions": assessment["concept_question_count"],
        "practical_tasks": assessment["practical_task_count"],
        "total_points": assessment["total_points"],
        "providers": assessment["tutorial_provider_count"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE assessment verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
