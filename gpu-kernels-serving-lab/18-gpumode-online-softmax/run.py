"""Session 18: GPUMODE-derived FlashAttention-style online softmax lab."""

from __future__ import annotations

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
        concepts = set(lesson.get("concepts", []))
        topics = set(lesson.get("topics", []))
        title = lesson.get("title", "").lower()
        exercises = " ".join(lesson.get("exercise_candidates", [])).lower()
        if (
            "attention" in topics
            and ("online softmax" in concepts or "kv cache" in concepts or "flashattention" in title or "softmax" in exercises)
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


def materialized_attention(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
    scale = 1.0 / math.sqrt(q.shape[-1])
    scores = q @ k.T * scale
    return torch.softmax(scores, dim=-1) @ v


def online_attention(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor, block: int) -> torch.Tensor:
    scale = 1.0 / math.sqrt(q.shape[-1])
    rows, dim = q.shape
    out = torch.zeros((rows, dim), dtype=torch.float32)
    row_max = torch.full((rows,), -torch.inf, dtype=torch.float32)
    row_denom = torch.zeros((rows,), dtype=torch.float32)

    for start in range(0, k.shape[0], block):
        end = min(start + block, k.shape[0])
        scores = q @ k[start:end].T * scale
        block_max = scores.max(dim=1).values
        new_max = torch.maximum(row_max, block_max)
        old_scale = torch.exp(row_max - new_max)
        exp_scores = torch.exp(scores - new_max[:, None])
        new_denom = row_denom * old_scale + exp_scores.sum(dim=1)
        weighted = exp_scores @ v[start:end]
        out = (out * (row_denom * old_scale)[:, None] + weighted) / new_denom[:, None]
        row_max = new_max
        row_denom = new_denom
    return out


def bytes_materialized(seq: int, dim: int) -> int:
    qkv = 3 * seq * dim * 4
    scores = seq * seq * 4
    probs = seq * seq * 4
    out = seq * dim * 4
    return qkv + scores + probs + out


def bytes_online(seq: int, dim: int, block: int) -> int:
    qkv = 3 * seq * dim * 4
    block_scores = seq * block * 4
    row_state = seq * 2 * 4
    out = seq * dim * 4
    return qkv + block_scores + row_state + out


def benchmark_rows() -> dict[str, object]:
    torch.manual_seed(18)
    rows = []
    for seq in [128, 256, 384]:
        dim = 64
        block = 64
        q = torch.randn((seq, dim), dtype=torch.float32)
        k = torch.randn((seq, dim), dtype=torch.float32)
        v = torch.randn((seq, dim), dtype=torch.float32)
        ref = materialized_attention(q, k, v)
        online = online_attention(q, k, v, block)
        error = float((online - ref).abs().max().item())

        mat_seconds = median_seconds(lambda: materialized_attention(q, k, v), warmup=1, repeat=5)
        online_seconds = median_seconds(lambda: online_attention(q, k, v, block), warmup=1, repeat=5)
        mat_bytes = bytes_materialized(seq, dim)
        online_bytes = bytes_online(seq, dim, block)
        rows.append(
            {
                "seq": seq,
                "dim": dim,
                "block": block,
                "materialized_seconds": round(mat_seconds, 6),
                "online_seconds": round(online_seconds, 6),
                "materialized_bytes_estimate": mat_bytes,
                "online_bytes_estimate": online_bytes,
                "estimated_memory_saved_pct": round(100 * (1 - online_bytes / mat_bytes), 2),
                "max_abs_error": round(error, 8),
            }
        )
    return {
        "status": "ran",
        "framework": "torch",
        "rows": rows,
        "correctness": "passed" if all(row["max_abs_error"] <= 1e-5 for row in rows) else "failed",
        "finding": (
            "Online softmax matches materialized attention while avoiding the full SxS probability matrix; "
            "the CPU loop is slower here because it prioritizes algorithm shape over fused-kernel speed."
        ),
    }


def triton_boundary() -> dict[str, object]:
    if not torch.cuda.is_available():
        return {
            "status": "skipped",
            "reason": "Fused Triton attention requires a CUDA-visible device.",
            "extends": "07-triton-fused-attention",
            "boundary": "Session 18 proves online softmax semantics on CPU; Session 07 and a CUDA runtime are needed for GPU fused-kernel timing.",
        }
    return {
        "status": "delegated",
        "extends": "07-triton-fused-attention",
        "boundary": "Use Session 07 for the CUDA-visible fused Triton timing path after this online-softmax derivation.",
    }


def main() -> None:
    rows = benchmark_rows()
    out: dict[str, Any] = {
        "session": "18-gpumode-online-softmax",
        "timestamp": now(),
        "inventory": collect_inventory("18-gpumode-online-softmax"),
        "source": {
            "gpumode_lab_id": "gpumode-lab-04-online-softmax",
            "gpumode_lessons": gpumode_links(),
            "extends": "05-cuda-tiny-attention and 07-triton-fused-attention",
        },
        "online_softmax": rows,
        "triton": triton_boundary(),
        "correctness": {
            "status": rows["correctness"],
            "note": "Online attention output is compared against materialized torch.softmax(QK^T)V for each sequence length.",
        },
        "boundary": (
            "This lab teaches the core FlashAttention-style online softmax recurrence with measured CPU artifacts. "
            "It does not claim fused GPU speed without a CUDA-visible device."
        ),
    }
    path = HERE / "out_gpumode_online_softmax.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, "online", rows["status"], "triton", out["triton"]["status"])


if __name__ == "__main__":
    main()
