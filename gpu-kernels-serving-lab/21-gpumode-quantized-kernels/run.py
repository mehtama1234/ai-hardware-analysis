"""Session 21: GPUMODE-derived quantized matmul kernel ladder."""

from __future__ import annotations

import importlib.util
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

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
            "quantization" in topics
            or "quantized numerics" in concepts
            or "int4" in title
            or "fp8" in title
            or "mxfp" in title
            or "quantization error" in exercises
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
    return selected[:14]


def rel_err(x: torch.Tensor, y: torch.Tensor) -> float:
    return float((x - y).norm() / (x.norm() + 1e-12))


def cosine(x: torch.Tensor, y: torch.Tensor) -> float:
    return float(torch.nn.functional.cosine_similarity(x.flatten(), y.flatten(), dim=0))


def quantize_per_tensor(w: torch.Tensor, qmax: int) -> tuple[torch.Tensor, torch.Tensor]:
    scale = w.abs().max() / qmax + 1e-12
    q = (w / scale).round().clamp(-qmax, qmax).to(torch.int8)
    return q, torch.tensor(float(scale), dtype=torch.float32)


def dequant_per_tensor(q: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
    return q.float() * scale


def quantize_groupwise(w: torch.Tensor, qmax: int, group: int) -> tuple[torch.Tensor, torch.Tensor, int]:
    rows, cols = w.shape
    pad = (group - cols % group) % group
    padded = torch.nn.functional.pad(w, (0, pad)) if pad else w
    view = padded.view(rows, -1, group)
    scale = view.abs().amax(dim=-1, keepdim=True) / qmax + 1e-12
    q = (view / scale).round().clamp(-qmax, qmax).to(torch.int8)
    return q, scale.squeeze(-1).float(), pad


def dequant_groupwise(q: torch.Tensor, scale: torch.Tensor, original_cols: int) -> torch.Tensor:
    w = q.float() * scale.unsqueeze(-1)
    return w.view(q.shape[0], -1)[:, :original_cols]


def mxfp4_like(w: torch.Tensor, group: int) -> tuple[torch.Tensor, torch.Tensor, int]:
    codes = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0], dtype=w.dtype)
    rows, cols = w.shape
    pad = (group - cols % group) % group
    padded = torch.nn.functional.pad(w, (0, pad)) if pad else w
    view = padded.view(rows, -1, group)
    scale = torch.pow(2.0, torch.ceil(torch.log2(view.abs().amax(dim=-1, keepdim=True) / 6.0 + 1e-12)))
    scaled = view / scale
    idx = (scaled.abs().unsqueeze(-1) - codes).abs().argmin(dim=-1)
    q = scaled.sign() * codes[idx] * scale
    return q.float(), scale.squeeze(-1).float(), pad


def model_bytes(m: int, k: int, n: int, bits_per_weight: float, scale_count: int = 0) -> dict[str, float]:
    activation = m * k * 2
    weights = k * n * bits_per_weight / 8
    scales = scale_count * 4
    output = m * n * 4
    return {
        "activation_mb": round(activation / 1e6, 4),
        "weight_mb": round(weights / 1e6, 4),
        "scale_mb": round(scales / 1e6, 4),
        "output_mb": round(output / 1e6, 4),
        "total_mb": round((activation + weights + scales + output) / 1e6, 4),
    }


def make_rows() -> dict[str, Any]:
    torch.manual_seed(21)
    m, k, n = 256, 512, 384
    x = torch.randn(m, k, dtype=torch.float32)
    w = torch.randn(k, n, dtype=torch.float32) * 0.02
    reference = x @ w
    flops = 2 * m * k * n

    def timed(name: str, bits: float, scale_count: int, fn: Any) -> dict[str, Any]:
        out = fn()
        seconds = median_seconds(fn, warmup=3, repeat=8)
        bytes_ = model_bytes(m, k, n, bits, scale_count)
        return {
            "scheme": name,
            "status": "ran",
            "seconds": round(seconds, 6),
            "effective_gflops": round(flops / seconds / 1e9, 4),
            "modeled_bytes": bytes_,
            "memory_reduction_vs_fp16_pct": round((1 - bytes_["total_mb"] / fp16_bytes["total_mb"]) * 100, 2),
            "relative_error_pct": round(rel_err(reference, out) * 100, 5),
            "max_abs_error": round(float((reference - out).abs().max()), 7),
            "cosine": round(cosine(reference, out), 7),
        }

    fp16_bytes = model_bytes(m, k, n, 16)
    rows = [
        timed("fp16_dequant_baseline", 16, 0, lambda: x @ w.half().float()),
    ]

    q8, s8 = quantize_per_tensor(w, 127)
    rows.append(timed("int8_per_tensor_dequant_matmul", 8, 1, lambda: x @ dequant_per_tensor(q8, s8)))

    q4, s4, _pad4 = quantize_groupwise(w, 7, 64)
    rows.append(
        timed(
            "int4_group64_dequant_matmul",
            4,
            int(s4.numel()),
            lambda: x @ dequant_groupwise(q4, s4, w.shape[1]),
        )
    )

    mx4, smx4, _padmx = mxfp4_like(w, 64)
    rows.append(
        timed(
            "mxfp4_like_group64_dequant_matmul",
            4,
            int(smx4.numel()),
            lambda: x @ dequant_groupwise(mx4, torch.ones_like(smx4), w.shape[1]),
        )
    )

    return {
        "status": "ran",
        "shape": {"m": m, "k": k, "n": n},
        "estimated_flops": flops,
        "rows": rows,
        "finding": (
            "Weight-only quantization reduces modeled memory traffic, but this CPU proxy also exposes "
            "the dequantization tax that a real GPU kernel must fuse away to turn smaller weights into speed."
        ),
    }


def runtime_paths() -> dict[str, Any]:
    has_triton = importlib.util.find_spec("triton") is not None
    has_cuda = torch.cuda.is_available()
    return {
        "triton": {
            "status": "skipped" if not (has_triton and has_cuda) else "ready",
            "reason": (
                "Triton quantized matmul requires a CUDA-visible device in this lab."
                if not has_cuda
                else "Triton is not installed."
                if not has_triton
                else "CUDA and Triton are available; add a packed int4 kernel sweep next."
            ),
            "next": "Fuse dequantization into a tiled Triton matmul and compare against this CPU proxy.",
        },
        "cuda": {
            "status": "skipped",
            "reason": "No nvcc-backed packed int4 CUDA kernel is built in this session yet.",
            "next": "Implement nibble-packed int4 loads plus per-group scales in CUDA or CUTLASS.",
        },
    }


def main() -> None:
    ladder = make_rows()
    rows = ladder["rows"]
    checks = {
        "all_paths_ran": all(row["status"] == "ran" for row in rows),
        "all_outputs_finite": all(math.isfinite(row["relative_error_pct"]) and math.isfinite(row["cosine"]) for row in rows),
        "quantized_paths_reduce_modeled_memory": all(
            row["memory_reduction_vs_fp16_pct"] > 0 for row in rows if row["scheme"] != "fp16_dequant_baseline"
        ),
        "low_bit_paths_show_measured_drift": max(row["relative_error_pct"] for row in rows) > rows[0]["relative_error_pct"],
    }
    out = {
        "session": "21-gpumode-quantized-kernels",
        "timestamp": now(),
        "inventory": collect_inventory("21-gpumode-quantized-kernels"),
        "source": {
            "gpumode_lab_id": "gpumode-lab-07-quantized-kernels",
            "gpumode_lessons": gpumode_links(),
            "extends": "08-quantized-inference and 17-gpumode-triton-autotune",
        },
        "quantized_matmul": ladder,
        "runtime_paths": runtime_paths(),
        "correctness": {
            "status": "passed" if all(checks.values()) else "failed",
            "checks": checks,
            "max_relative_error_pct": max(row["relative_error_pct"] for row in rows),
            "note": "All quantized paths are compared against fp32 matmul. Relative error is reported as a measured quality signal, not used as a pass/fail proxy for model quality.",
        },
        "boundary": (
            "This session measures weight-only quantized matmul with explicit dequantization on the local runtime. "
            "It does not claim packed GPU int4 Tensor Core throughput until CUDA/Triton kernels are added and run."
        ),
    }
    path = HERE / "out_gpumode_quantized_kernels.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, "schemes", len(rows), "correctness", out["correctness"]["status"])
    for row in rows:
        print(row["scheme"], row["modeled_bytes"]["total_mb"], "MB", row["relative_error_pct"], "% error")


if __name__ == "__main__":
    main()
