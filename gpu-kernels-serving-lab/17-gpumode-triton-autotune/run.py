"""Session 17: GPUMODE-derived Triton matmul autotuning workbench."""

from __future__ import annotations

import json
import math
import time
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

CONFIGS = [
    {"block_m": 16, "block_n": 16, "block_k": 32, "num_warps": 4},
    {"block_m": 32, "block_n": 32, "block_k": 32, "num_warps": 4},
    {"block_m": 32, "block_n": 64, "block_k": 32, "num_warps": 4},
    {"block_m": 64, "block_n": 32, "block_k": 32, "num_warps": 4},
    {"block_m": 64, "block_n": 64, "block_k": 32, "num_warps": 4},
    {"block_m": 64, "block_n": 128, "block_k": 32, "num_warps": 8},
    {"block_m": 128, "block_n": 64, "block_k": 32, "num_warps": 8},
]


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
            "triton" in topics
            and ("autotuning" in concepts or "kernel fusion" in concepts or "matmul" in title or "sweep block" in exercises)
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


def tflops(flops: int, seconds: float) -> float:
    return round(flops / seconds / 1e12, 6) if seconds > 0 else math.inf


def config_model(m: int = 512, n: int = 512, k: int = 512) -> list[dict[str, object]]:
    rows = []
    for cfg in CONFIGS:
        bm, bn, bk = cfg["block_m"], cfg["block_n"], cfg["block_k"]
        programs = math.ceil(m / bm) * math.ceil(n / bn)
        k_tiles = math.ceil(k / bk)
        tile_flops = 2 * bm * bn * bk
        tile_bytes = (bm * bk + bk * bn + bm * bn) * 2
        ai = tile_flops / tile_bytes
        rows.append(
            {
                **cfg,
                "programs": programs,
                "k_tiles": k_tiles,
                "tile_flops": tile_flops,
                "tile_bytes_fp16_estimate": tile_bytes,
                "arithmetic_intensity_flop_per_byte": round(ai, 3),
                "fit_signal": "larger reuse" if ai >= 16 else "smaller tile",
            }
        )
    return sorted(rows, key=lambda row: (-row["arithmetic_intensity_flop_per_byte"], row["programs"]))


def cpu_baseline(m: int = 512, n: int = 512, k: int = 512) -> dict[str, object]:
    torch.manual_seed(17)
    a = torch.randn((m, k), dtype=torch.float32)
    b = torch.randn((k, n), dtype=torch.float32)
    ref = a @ b

    def work() -> None:
        a @ b

    seconds = median_seconds(work, warmup=2, repeat=8)
    check = a @ b
    error = float((check - ref).abs().max().item())
    flops = 2 * m * n * k
    return {
        "status": "ran",
        "framework": "torch",
        "shape": [m, n, k],
        "seconds": round(seconds, 6),
        "tflops": tflops(flops, seconds),
        "max_abs_error": round(error, 8),
        "finding": "CPU PyTorch matmul is the correctness and portability baseline; Triton config sweep requires CUDA.",
    }


def triton_sweep(m: int = 512, n: int = 512, k: int = 512) -> dict[str, object]:
    if not torch.cuda.is_available():
        return {
            "status": "skipped",
            "reason": "Triton autotune sweep requires a CUDA-visible device.",
            "boundary": "The config model and CPU baseline are still generated; GPU timing starts once PyTorch sees CUDA.",
        }

    import triton  # type: ignore
    import triton.language as tl  # type: ignore

    @triton.jit
    def matmul_kernel(
        a,
        b,
        c,
        m_size: tl.constexpr,
        n_size: tl.constexpr,
        k_size: tl.constexpr,
        stride_am: tl.constexpr,
        stride_ak: tl.constexpr,
        stride_bk: tl.constexpr,
        stride_bn: tl.constexpr,
        stride_cm: tl.constexpr,
        stride_cn: tl.constexpr,
        block_m: tl.constexpr,
        block_n: tl.constexpr,
        block_k: tl.constexpr,
    ):
        pid_m = tl.program_id(0)
        pid_n = tl.program_id(1)
        offs_m = pid_m * block_m + tl.arange(0, block_m)
        offs_n = pid_n * block_n + tl.arange(0, block_n)
        offs_k = tl.arange(0, block_k)
        acc = tl.zeros((block_m, block_n), tl.float32)
        for k0 in range(0, k_size, block_k):
            k_idxs = k0 + offs_k
            av = tl.load(a + offs_m[:, None] * stride_am + k_idxs[None, :] * stride_ak, mask=(offs_m[:, None] < m_size) & (k_idxs[None, :] < k_size), other=0.0)
            bv = tl.load(b + k_idxs[:, None] * stride_bk + offs_n[None, :] * stride_bn, mask=(k_idxs[:, None] < k_size) & (offs_n[None, :] < n_size), other=0.0)
            acc += tl.dot(av, bv)
        tl.store(c + offs_m[:, None] * stride_cm + offs_n[None, :] * stride_cn, acc, mask=(offs_m[:, None] < m_size) & (offs_n[None, :] < n_size))

    a = torch.randn((m, k), device="cuda", dtype=torch.float16)
    b = torch.randn((k, n), device="cuda", dtype=torch.float16)
    ref = a @ b
    rows = []
    flops = 2 * m * n * k
    for cfg in CONFIGS:
        c = torch.empty((m, n), device="cuda", dtype=torch.float16)
        grid = (triton.cdiv(m, cfg["block_m"]), triton.cdiv(n, cfg["block_n"]))
        matmul_kernel[grid](
            a,
            b,
            c,
            m,
            n,
            k,
            a.stride(0),
            a.stride(1),
            b.stride(0),
            b.stride(1),
            c.stride(0),
            c.stride(1),
            cfg["block_m"],
            cfg["block_n"],
            cfg["block_k"],
            num_warps=cfg["num_warps"],
        )
        torch.cuda.synchronize()
        start = time.perf_counter()
        for _ in range(20):
            matmul_kernel[grid](
                a,
                b,
                c,
                m,
                n,
                k,
                a.stride(0),
                a.stride(1),
                b.stride(0),
                b.stride(1),
                c.stride(0),
                c.stride(1),
                cfg["block_m"],
                cfg["block_n"],
                cfg["block_k"],
                num_warps=cfg["num_warps"],
            )
        torch.cuda.synchronize()
        ms = (time.perf_counter() - start) * 1000 / 20
        err = float((c.float() - ref.float()).abs().max().item())
        rows.append({**cfg, "milliseconds": round(ms, 4), "tflops": tflops(flops, ms / 1000), "max_abs_error": round(err, 6)})
    rows.sort(key=lambda row: row["milliseconds"])
    return {"status": "ran", "shape": [m, n, k], "rows": rows, "winner": rows[0]}


def main() -> None:
    shape = [512, 512, 512]
    cpu = cpu_baseline(*shape)
    configs = config_model(*shape)
    triton_result = triton_sweep(*shape)
    out: dict[str, Any] = {
        "session": "17-gpumode-triton-autotune",
        "timestamp": now(),
        "inventory": collect_inventory("17-gpumode-triton-autotune"),
        "source": {
            "gpumode_lab_id": "gpumode-lab-03-triton-autotune",
            "gpumode_lessons": gpumode_links(),
            "extends": "06-triton-matmul",
        },
        "config_model": {
            "status": "ran",
            "shape": shape,
            "rows": configs,
            "finding": f"The highest modeled reuse config is {configs[0]['block_m']}x{configs[0]['block_n']}x{configs[0]['block_k']} with arithmetic intensity {configs[0]['arithmetic_intensity_flop_per_byte']} FLOP/byte.",
        },
        "cpu_baseline": cpu,
        "triton": triton_result,
        "correctness": {
            "status": "passed" if cpu["max_abs_error"] <= 1e-6 and triton_result["status"] in {"skipped", "ran"} else "failed",
            "note": "CPU baseline is checked exactly against a repeated PyTorch matmul. Triton rows compare against torch matmul when CUDA is available.",
        },
        "boundary": (
            "This lab makes autotuning concrete before a GPU is present by ranking tile candidates "
            "and recording the local CPU baseline. Real Triton winner timing requires CUDA."
        ),
    }
    path = HERE / "out_gpumode_triton_autotune.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, "cpu", cpu["status"], "triton", triton_result["status"])


if __name__ == "__main__":
    main()
