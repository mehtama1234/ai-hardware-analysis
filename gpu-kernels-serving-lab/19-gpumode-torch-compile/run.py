"""Session 19: GPUMODE-derived torch.compile fusion and graph-break lab."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any, Callable

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.bench import median_seconds
from common.gpu_info import collect_inventory


HERE = Path(__file__).resolve().parent
GPUMODE_ROOT = ROOT.parent / "gpu-mode-curriculum"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def gpumode_links() -> list[dict[str, object]]:
    path = GPUMODE_ROOT / "analysis" / "lesson-intelligence.json"
    if not path.exists():
        return []
    lessons = json.loads(path.read_text(encoding="utf-8"))
    selected = []
    for lesson in lessons:
        topics = set(lesson.get("topics", []))
        concepts = set(lesson.get("concepts", []))
        title = lesson.get("title", "").lower()
        exercises = " ".join(lesson.get("exercise_candidates", [])).lower()
        if (
            "pytorch-compiler" in topics
            or "compiler lowering" in concepts
            or "kernel fusion" in concepts
            or "torch.compile" in title
            or "graph" in title
            or "fusion" in exercises
        ):
            selected.append(
                {
                    "index": lesson["index"],
                    "title": lesson["title"],
                    "url": lesson["url"],
                    "topics": lesson["topics"],
                    "concepts": lesson.get("concepts", []),
                    "exercise_candidates": lesson.get("exercise_candidates", []),
                }
            )
    return selected[:12]


def fused_candidate(x: torch.Tensor, w1: torch.Tensor, b1: torch.Tensor, w2: torch.Tensor, b2: torch.Tensor) -> torch.Tensor:
    y = torch.nn.functional.gelu(x @ w1 + b1)
    z = torch.nn.functional.layer_norm(y, (y.shape[-1],))
    return z @ w2 + b2


def graph_break_candidate(x: torch.Tensor, w1: torch.Tensor, b1: torch.Tensor, w2: torch.Tensor, b2: torch.Tensor) -> torch.Tensor:
    y = torch.nn.functional.gelu(x @ w1 + b1)
    if float(y[0, 0]) > 1e9:
        y = y + 1.0
    z = torch.nn.functional.layer_norm(y, (y.shape[-1],))
    return z @ w2 + b2


def tflops(flops: int, seconds: float) -> float:
    return round(flops / seconds / 1e12, 6) if seconds > 0 else math.inf


def benchmark_fn(fn: Callable[..., torch.Tensor], args: tuple[torch.Tensor, ...], repeat: int = 10) -> tuple[float, torch.Tensor]:
    result = fn(*args)
    seconds = median_seconds(lambda: fn(*args), warmup=2, repeat=repeat)
    return seconds, result


def dynamo_explain(fn: Callable[..., torch.Tensor], args: tuple[torch.Tensor, ...]) -> dict[str, object]:
    try:
        import torch._dynamo as dynamo  # type: ignore

        explanation = dynamo.explain(fn)(*args)
        graph_count = getattr(explanation, "graph_count", None)
        graph_break_count = getattr(explanation, "graph_break_count", None)
        break_reasons = [str(reason) for reason in getattr(explanation, "break_reasons", [])]
        op_count = getattr(explanation, "op_count", None)
        return {
            "status": "ran",
            "graph_count": graph_count,
            "graph_break_count": graph_break_count,
            "op_count": op_count,
            "break_reasons": break_reasons[:8],
        }
    except Exception as exc:
        return {"status": "failed", "reason": repr(exc)}


def compile_and_measure(name: str, fn: Callable[..., torch.Tensor], args: tuple[torch.Tensor, ...], reference: torch.Tensor) -> dict[str, object]:
    if not hasattr(torch, "compile"):
        return {"name": name, "status": "skipped", "reason": "torch.compile is not available in this PyTorch build."}
    try:
        compiled = torch.compile(fn, backend="inductor", mode="default")
        compiled(*args)
        seconds, output = benchmark_fn(compiled, args, repeat=8)
        max_abs_error = float((output - reference).abs().max().item())
        return {
            "name": name,
            "status": "ran",
            "backend": "inductor",
            "seconds": round(seconds, 6),
            "max_abs_error": round(max_abs_error, 8),
        }
    except Exception as exc:
        return {"name": name, "status": "failed", "backend": "inductor", "reason": repr(exc)}


def run_experiment() -> dict[str, object]:
    torch.manual_seed(19)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    batch, hidden = 256, 256
    x = torch.randn((batch, hidden), dtype=torch.float32, device=device)
    w1 = torch.randn((hidden, hidden), dtype=torch.float32, device=device)
    b1 = torch.randn((hidden,), dtype=torch.float32, device=device)
    w2 = torch.randn((hidden, hidden), dtype=torch.float32, device=device)
    b2 = torch.randn((hidden,), dtype=torch.float32, device=device)
    args = (x, w1, b1, w2, b2)
    flops = 4 * batch * hidden * hidden

    eager_seconds, eager_output = benchmark_fn(fused_candidate, args)
    compiled_fused = compile_and_measure("compiled_fused_candidate", fused_candidate, args, eager_output)

    eager_break_seconds, eager_break_output = benchmark_fn(graph_break_candidate, args)
    compiled_break = compile_and_measure("compiled_graph_break_candidate", graph_break_candidate, args, eager_break_output)

    rows = [
        {
            "name": "eager_fused_candidate",
            "status": "ran",
            "seconds": round(eager_seconds, 6),
            "tflops": tflops(flops, eager_seconds),
            "max_abs_error": 0.0,
        },
        {**compiled_fused, "tflops": tflops(flops, compiled_fused["seconds"]) if compiled_fused.get("status") == "ran" else None},
        {
            "name": "eager_graph_break_candidate",
            "status": "ran",
            "seconds": round(eager_break_seconds, 6),
            "tflops": tflops(flops, eager_break_seconds),
            "max_abs_error": 0.0,
        },
        {**compiled_break, "tflops": tflops(flops, compiled_break["seconds"]) if compiled_break.get("status") == "ran" else None},
    ]
    successful_compiled = [row for row in rows if row["name"].startswith("compiled") and row["status"] == "ran"]
    return {
        "status": "ran",
        "device": device,
        "shape": {"batch": batch, "hidden": hidden},
        "estimated_matmul_flops_per_call": flops,
        "rows": rows,
        "graph_analysis": {
            "fused_candidate": dynamo_explain(fused_candidate, args),
            "graph_break_candidate": dynamo_explain(graph_break_candidate, args),
        },
        "finding": (
            "torch.compile is useful when it can keep tensor programs inside captured graphs; "
            "data-dependent Python control flow is a visible graph-break risk."
        ),
        "compiled_paths_ran": len(successful_compiled),
    }


def main() -> None:
    experiment = run_experiment()
    failures = [row for row in experiment["rows"] if row["name"].startswith("compiled") and row["status"] == "failed"]
    out: dict[str, Any] = {
        "session": "19-gpumode-torch-compile",
        "timestamp": now(),
        "inventory": collect_inventory("19-gpumode-torch-compile"),
        "source": {
            "gpumode_lab_id": "gpumode-lab-05-torch-compile",
            "gpumode_lessons": gpumode_links(),
            "extends": "01-hf-baseline and 06-triton-matmul",
        },
        "torch_compile": experiment,
        "correctness": {
            "status": "passed"
            if all(row.get("max_abs_error", 0.0) <= 1e-4 for row in experiment["rows"] if row["status"] == "ran")
            else "failed",
            "compile_failures": failures,
            "note": "Compiled outputs are compared against eager outputs when compilation succeeds; failed compiled paths are recorded explicitly.",
        },
        "boundary": (
            "This lab measures PyTorch compiler capture and graph-break behavior on the local runtime. "
            "It does not prove GPU kernel fusion speedups when CUDA is not visible."
        ),
    }
    path = HERE / "out_gpumode_torch_compile.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, "compile_paths", experiment["compiled_paths_ran"], "correctness", out["correctness"]["status"])


if __name__ == "__main__":
    main()
