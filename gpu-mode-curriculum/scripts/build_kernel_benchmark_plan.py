#!/usr/bin/env python3
"""Map GPUMODE lessons to the kernel benchmark families."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "analysis" / "gpumode-curriculum.json"
OUT = ROOT / "kernel-benchmarks"
PLAN_JSON = OUT / "plan.json"
PLAN_MD = OUT / "PLAN.md"


FAMILIES = [
    {
        "id": "memory",
        "title": "Vector memory, coalescing, striding, and bandwidth",
        "signals": ["cuda", "hardware", "memory coalescing"],
        "cuda_source": "kernel-benchmarks/kernels/cuda/memory.cu",
        "triton_source": "kernel-benchmarks/kernels/triton/memory.py",
    },
    {
        "id": "reduction",
        "title": "Block reductions, warp reductions, scans, and aggregation",
        "signals": ["warp execution", "thread/block indexing", "reduction", "scan"],
        "cuda_source": "kernel-benchmarks/kernels/cuda/reduction.cu",
        "triton_source": "kernel-benchmarks/kernels/triton/reduction.py",
    },
    {
        "id": "normalization",
        "title": "Softmax and layernorm row kernels",
        "signals": ["attention", "online softmax", "softmax"],
        "cuda_source": "kernel-benchmarks/kernels/cuda/softmax_layernorm.cu",
        "triton_source": "kernel-benchmarks/kernels/triton/softmax_layernorm.py",
    },
    {
        "id": "matmul",
        "title": "Tiled matmul and tensor-core promotion path",
        "signals": ["cutlass", "tensor cores", "matrix multiplication", "shared memory tiling"],
        "cuda_source": "kernel-benchmarks/kernels/cuda/matmul_mlp.cu",
        "triton_source": "kernel-benchmarks/kernels/triton/matmul_mlp.py",
    },
    {
        "id": "fusion",
        "title": "Fused MLP, activation, and compiler/autotune path",
        "signals": ["kernel fusion", "autotuning", "triton", "pytorch-compiler", "compiler lowering"],
        "cuda_source": "kernel-benchmarks/kernels/cuda/matmul_mlp.cu",
        "triton_source": "kernel-benchmarks/kernels/triton/matmul_mlp.py",
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def score(lesson: dict[str, Any], family: dict[str, Any]) -> int:
    haystack = {
        *(term.lower() for term in lesson.get("topics", [])),
        *(term.lower() for term in lesson.get("concepts", [])),
        *(term.lower() for term in lesson.get("tools", [])),
        *(term.lower() for term in lesson.get("prerequisites", [])),
        *(term.lower() for term in lesson.get("exercise_candidates", [])),
    }
    total = 0
    for signal in family["signals"]:
        signal = signal.lower()
        if signal in haystack:
            total += 10
        elif any(signal in item for item in haystack):
            total += 4
    return total


def build() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    curriculum = load_json(CURRICULUM)
    lessons = curriculum["lessons"]
    rows = []
    for family in FAMILIES:
        mapped = []
        for lesson in lessons:
            lesson_score = score(lesson, family)
            if lesson_score > 0:
                mapped.append(
                    {
                        "index": lesson["index"],
                        "title": lesson["title"],
                        "url": lesson["url"],
                        "score": lesson_score,
                        "topics": lesson.get("topics", []),
                        "concepts": lesson.get("concepts", []),
                    }
                )
        rows.append(family | {"lesson_count": len(mapped), "lessons": sorted(mapped, key=lambda row: (-row["score"], row["index"]))})
    covered = {lesson["index"] for row in rows for lesson in row["lessons"]}
    plan = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lesson_count": len(lessons),
        "covered_lessons": len(covered),
        "uncovered_lessons": [lesson["index"] for lesson in lessons if lesson["index"] not in covered],
        "families": rows,
    }
    write_json(PLAN_JSON, plan)
    PLAN_MD.write_text(markdown(plan), encoding="utf-8")
    return plan


def markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Kernel Benchmark Lesson Map",
        "",
        f"Lessons covered: {plan['covered_lessons']} / {plan['lesson_count']}",
        "",
    ]
    for family in plan["families"]:
        lines.extend(
            [
                f"## {family['title']}",
                "",
                f"- ID: `{family['id']}`",
                f"- CUDA: `{family['cuda_source']}`",
                f"- Triton: `{family['triton_source']}`",
                f"- Lessons mapped: {family['lesson_count']}",
                "",
                "| Lesson | Title | Score |",
                "|---|---|---|",
            ]
        )
        for lesson in family["lessons"][:16]:
            lines.append(f"| {lesson['index']} | {lesson['title']} | {lesson['score']} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    plan = build()
    print(f"wrote {PLAN_JSON.relative_to(ROOT)} and {PLAN_MD.relative_to(ROOT)} ({plan['covered_lessons']}/{plan['lesson_count']} lessons covered)")


if __name__ == "__main__":
    main()
