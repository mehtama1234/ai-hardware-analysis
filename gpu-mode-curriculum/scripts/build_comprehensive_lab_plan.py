#!/usr/bin/env python3
"""Build the deliberate one-by-one GPUMODE comprehensive lab plan."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "analysis" / "gpumode-curriculum.json"
OUT = ROOT / "comprehensive-labs"
PLAN_JSON = OUT / "plan.json"
PLAN_MD = OUT / "PLAN.md"


LAB_PLAN = [
    {
        "id": "comp-lab-01-memory-hierarchy",
        "module": "gpumode_lab_suite.memory_hierarchy",
        "title": "Memory hierarchy, coalescing, bank conflicts, occupancy, roofline",
        "primary_signals": ["cuda", "hardware", "memory coalescing", "shared memory tiling", "occupancy"],
        "implementation": "comprehensive-labs/gpumode_lab_suite/memory_hierarchy.py",
        "why": "Most lessons touch CUDA/hardware. This lab makes memory traffic, bank conflicts, occupancy, and roofline constraints measurable before deeper kernels.",
    },
    {
        "id": "comp-lab-02-tiled-attention",
        "module": "gpumode_lab_suite.tiled_attention",
        "title": "Tiled matmul, online softmax, and attention memory behavior",
        "primary_signals": ["attention", "online softmax", "tensor cores", "shared memory tiling"],
        "implementation": "comprehensive-labs/gpumode_lab_suite/tiled_attention.py",
        "why": "Attention lessons need one code path that joins matmul tiling, stable softmax, and IO-aware attention accounting.",
    },
    {
        "id": "comp-lab-03-compiler-autotune",
        "module": "gpumode_lab_suite.compiler_autotune",
        "title": "Compiler lowering, fusion, Triton-style autotuning, schedule search",
        "primary_signals": ["triton", "pytorch-compiler", "autotuning", "kernel fusion", "compiler lowering"],
        "implementation": "comprehensive-labs/gpumode_lab_suite/compiler_autotune.py",
        "why": "Compiler and Triton material should be evaluated through schedule candidates and fusion decisions, not just syntax examples.",
    },
    {
        "id": "comp-lab-04-quantization-formats",
        "module": "gpumode_lab_suite.quantization_formats",
        "title": "Quantized numerics across int8, int4, fp8-like, and nvfp4-like formats",
        "primary_signals": ["quantization", "quantized numerics"],
        "implementation": "comprehensive-labs/gpumode_lab_suite/quantization_formats.py",
        "why": "Quantization lectures need error and format behavior that can be measured before porting into tensor-core kernels.",
    },
    {
        "id": "comp-lab-05-serving-kv-cache",
        "module": "gpumode_lab_suite.serving_kv_cache",
        "title": "Serving scheduler, paged KV cache, prefix sharing, continuous batching",
        "primary_signals": ["serving", "kv cache"],
        "implementation": "comprehensive-labs/gpumode_lab_suite/serving_kv_cache.py",
        "why": "Serving lectures are best combined into an allocator/scheduler lab because latency comes from the interaction of requests, cache blocks, and batching.",
    },
    {
        "id": "comp-lab-06-portability-rocm-hip",
        "module": "gpumode_lab_suite.portability_rocm_hip",
        "title": "CUDA-to-HIP portability scanner and migration plan",
        "primary_signals": ["rocm", "hip", "ROCm/HIP", "compiler lowering"],
        "implementation": "comprehensive-labs/gpumode_lab_suite/portability_rocm_hip.py",
        "why": "Portability needs a code migration/checking pass that records what can be rewritten and what remains manual.",
    },
    {
        "id": "comp-lab-07-distributed-collectives",
        "module": "gpumode_lab_suite.distributed_collectives",
        "title": "Distributed collective algorithm and topology model",
        "primary_signals": ["distributed", "collectives"],
        "implementation": "comprehensive-labs/gpumode_lab_suite/distributed_collectives.py",
        "why": "Collective lessons require algorithm/topology models before moving into NCCL, NVSHMEM, or cluster measurements.",
    },
    {
        "id": "comp-lab-08-profiler-evidence",
        "module": "gpumode_lab_suite.profiler_evidence",
        "title": "Profiler counter triage, roofline evidence, remediation plan",
        "primary_signals": ["profiling", "profiling workflow"],
        "implementation": "comprehensive-labs/gpumode_lab_suite/profiler_evidence.py",
        "why": "Every kernel lab needs a profiler evidence loop that turns counters into bottleneck diagnoses and next code changes.",
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def score_lesson(lesson: dict[str, Any], lab: dict[str, Any]) -> int:
    signals = {value.lower() for value in lab["primary_signals"]}
    topics = {value.lower() for value in lesson.get("topics", [])}
    concepts = {value.lower() for value in lesson.get("concepts", [])}
    tools = {value.lower() for value in lesson.get("tools", [])}
    readiness = {str(lesson.get("lab_readiness", "")).lower()}
    haystack = topics | concepts | tools | readiness
    score = 0
    for signal in signals:
        if signal.lower() in haystack:
            score += 10
        elif any(signal.lower() in item for item in haystack):
            score += 4
    return score


def assign_lessons(lessons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lab_rows = []
    for lab in LAB_PLAN:
        assigned = []
        for lesson in lessons:
            score = score_lesson(lesson, lab)
            if score > 0:
                assigned.append(
                    {
                        "index": lesson["index"],
                        "title": lesson["title"],
                        "url": lesson["url"],
                        "topics": lesson.get("topics", []),
                        "concepts": lesson.get("concepts", []),
                        "score": score,
                    }
                )
        lab_rows.append(lab | {"lesson_count": len(assigned), "lessons": sorted(assigned, key=lambda row: (-row["score"], row["index"]))})
    return lab_rows


def coverage(lessons: list[dict[str, Any]], labs: list[dict[str, Any]]) -> dict[str, Any]:
    covered = {lesson["index"] for lab in labs for lesson in lab["lessons"]}
    return {
        "lesson_count": len(lessons),
        "covered_lessons": len(covered),
        "uncovered_lessons": [lesson["index"] for lesson in lessons if lesson["index"] not in covered],
    }


def build_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Comprehensive Lab Code Plan",
        "",
        "This is the one-by-one implementation plan for the real code layer. The 118 per-lesson labs remain coverage scaffolds; these comprehensive labs are the deliberate programs to build and extend.",
        "",
        f"Lessons covered by comprehensive labs: {plan['coverage']['covered_lessons']} / {plan['coverage']['lesson_count']}",
        "",
    ]
    for idx, lab in enumerate(plan["labs"], start=1):
        lines.extend(
            [
                f"## {idx}. {lab['title']}",
                "",
                f"- ID: `{lab['id']}`",
                f"- Code: `{lab['implementation']}`",
                f"- Module: `{lab['module']}`",
                f"- Lessons mapped: {lab['lesson_count']}",
                f"- Reason: {lab['why']}",
                "- First lesson anchors:",
            ]
        )
        for lesson in lab["lessons"][:8]:
            lines.append(f"  - Lesson {lesson['index']}: {lesson['title']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    curriculum = load_json(CURRICULUM)
    labs = assign_lessons(curriculum["lessons"])
    plan = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plan_type": "hand-written comprehensive lab code plan",
        "coverage": coverage(curriculum["lessons"], labs),
        "labs": labs,
    }
    write_json(PLAN_JSON, plan)
    PLAN_MD.write_text(build_markdown(plan), encoding="utf-8")
    return plan


def main() -> None:
    plan = build()
    print(f"wrote {PLAN_JSON.relative_to(ROOT)} and {PLAN_MD.relative_to(ROOT)} ({plan['coverage']['covered_lessons']}/{plan['coverage']['lesson_count']} lessons covered)")


if __name__ == "__main__":
    main()
