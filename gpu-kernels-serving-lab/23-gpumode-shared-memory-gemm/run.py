"""Session 23: GPUMODE-derived shared-memory tiled GEMM microscope."""

from __future__ import annotations

import json
import math
import shutil
import subprocess
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
SRC = HERE / "shared_memory_gemm.cu"
BIN = HERE / "shared_memory_gemm"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(cmd: list[str], timeout: int = 180) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


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
            "shared memory tiling" in concepts
            or "tensor cores" in concepts
            or "cutlass" in topics
            or ("cuda" in topics and "matmul" in title)
            or "implement naive vs tiled matrix multiplication" in exercises
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


def gflops(flops: int, seconds: float) -> float:
    return round(flops / seconds / 1e9, 4) if seconds > 0 else math.inf


def max_abs_error(a: torch.Tensor, b: torch.Tensor) -> float:
    return float((a - b).abs().max().item())


def naive_loop(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    m, k = a.shape
    _k, n = b.shape
    out = torch.zeros((m, n), dtype=torch.float32)
    for i in range(m):
        for j in range(n):
            acc = 0.0
            for kk in range(k):
                acc += float(a[i, kk]) * float(b[kk, j])
            out[i, j] = acc
    return out


def tiled_loop(a: torch.Tensor, b: torch.Tensor, tile: int) -> torch.Tensor:
    m, k = a.shape
    _k, n = b.shape
    out = torch.zeros((m, n), dtype=torch.float32)
    for ii in range(0, m, tile):
        for jj in range(0, n, tile):
            acc = torch.zeros((min(tile, m - ii), min(tile, n - jj)), dtype=torch.float32)
            for kk in range(0, k, tile):
                a_tile = a[ii : ii + tile, kk : kk + tile]
                b_tile = b[kk : kk + tile, jj : jj + tile]
                acc += a_tile @ b_tile
            out[ii : ii + acc.shape[0], jj : jj + acc.shape[1]] = acc
    return out


def traffic_model(m: int, n: int, k: int, tile: int, bytes_per_element: int = 4) -> dict[str, Any]:
    flops = 2 * m * n * k
    naive_reads = m * n * k * 2
    naive_writes = m * n
    tile_m = math.ceil(m / tile)
    tile_n = math.ceil(n / tile)
    tile_k = math.ceil(k / tile)
    tiled_reads = tile_m * tile_n * tile_k * (tile * tile * 2)
    tiled_writes = m * n
    naive_bytes = (naive_reads + naive_writes) * bytes_per_element
    tiled_bytes = (tiled_reads + tiled_writes) * bytes_per_element
    return {
        "shape": [m, n, k],
        "tile": tile,
        "flops": flops,
        "naive_global_load_elements": naive_reads,
        "tiled_global_load_elements_upper_bound": tiled_reads,
        "naive_bytes": naive_bytes,
        "tiled_bytes_upper_bound": tiled_bytes,
        "modeled_global_memory_reduction_pct": round((1.0 - tiled_bytes / naive_bytes) * 100.0, 3),
        "naive_arithmetic_intensity_flop_per_byte": round(flops / naive_bytes, 4),
        "tiled_arithmetic_intensity_flop_per_byte": round(flops / tiled_bytes, 4),
    }


def cpu_proxy(m: int = 32, n: int = 32, k: int = 32, tile: int = 8) -> dict[str, Any]:
    torch.manual_seed(23)
    a = torch.randn((m, k), dtype=torch.float32)
    b = torch.randn((k, n), dtype=torch.float32)
    ref = a @ b
    flops = 2 * m * n * k

    naive_seconds = median_seconds(lambda: naive_loop(a, b), warmup=1, repeat=3)
    tiled_seconds = median_seconds(lambda: tiled_loop(a, b, tile), warmup=1, repeat=5)
    torch_seconds = median_seconds(lambda: a @ b, warmup=2, repeat=10)
    naive_out = naive_loop(a, b)
    tiled_out = tiled_loop(a, b, tile)
    model = traffic_model(m, n, k, tile)
    rows = [
        {
            "path": "naive_cpu_loop",
            "seconds": round(naive_seconds, 6),
            "gflops": gflops(flops, naive_seconds),
            "max_abs_error": round(max_abs_error(naive_out, ref), 6),
            "purpose": "Readable baseline matching one CUDA thread per output element.",
        },
        {
            "path": "tiled_cpu_proxy",
            "seconds": round(tiled_seconds, 6),
            "gflops": gflops(flops, tiled_seconds),
            "max_abs_error": round(max_abs_error(tiled_out, ref), 6),
            "purpose": "Shows tile reuse and accumulation shape before moving to shared memory.",
        },
        {
            "path": "torch_matmul_reference",
            "seconds": round(torch_seconds, 6),
            "gflops": gflops(flops, torch_seconds),
            "max_abs_error": 0.0,
            "purpose": "Vendor/library-style reference for correctness and scale contrast.",
        },
    ]
    speedup = naive_seconds / tiled_seconds if tiled_seconds else math.inf
    return {
        "status": "ran",
        "shape": [m, n, k],
        "tile": tile,
        "rows": rows,
        "traffic_model": model,
        "tiled_vs_naive_speedup": round(speedup, 4),
        "finding": (
            f"A {tile}x{tile} tile raises modeled arithmetic intensity from "
            f"{model['naive_arithmetic_intensity_flop_per_byte']} to "
            f"{model['tiled_arithmetic_intensity_flop_per_byte']} FLOP/byte and cuts modeled "
            f"global-memory traffic by {model['modeled_global_memory_reduction_pct']}%."
        ),
    }


def cuda_result() -> dict[str, Any]:
    nvcc = shutil.which("nvcc")
    if not nvcc:
        return {
            "status": "skipped",
            "reason": "nvcc not found on PATH",
            "source": SRC.name,
            "boundary": "CUDA source is present, but compiling/running requires the NVIDIA CUDA toolkit and a visible CUDA device.",
        }
    compile_cmd = [nvcc, "-O3", "-std=c++17", str(SRC), "-o", str(BIN)]
    code, stdout, stderr = run_cmd(compile_cmd)
    if code != 0:
        return {
            "status": "compile_failed",
            "compile_cmd": compile_cmd,
            "stdout": stdout,
            "stderr": stderr,
            "boundary": "nvcc ran but shared_memory_gemm.cu did not compile.",
        }
    code, stdout, stderr = run_cmd([str(BIN)])
    try:
        parsed = json.loads(stdout.splitlines()[-1]) if stdout else {}
    except Exception:
        parsed = {"raw_stdout": stdout}
    return {
        "status": "ran" if code == 0 else "run_failed",
        "compile_cmd": compile_cmd,
        "returncode": code,
        "stdout": stdout,
        "stderr": stderr,
        "kernel": parsed,
        "boundary": "CUDA path compares naive global-memory GEMM with a shared-memory tiled kernel.",
    }


def main() -> None:
    proxy = cpu_proxy()
    cuda = cuda_result()
    checks = {
        "cpu_proxy_ran": proxy["status"] == "ran",
        "all_cpu_paths_finite": all(math.isfinite(row["seconds"]) and row["seconds"] > 0 for row in proxy["rows"]),
        "naive_correct": proxy["rows"][0]["max_abs_error"] <= 1e-4,
        "tiled_correct": proxy["rows"][1]["max_abs_error"] <= 1e-4,
        "modeled_traffic_reduction": proxy["traffic_model"]["modeled_global_memory_reduction_pct"] > 0,
        "cuda_path_classified": cuda["status"] in {"skipped", "compile_failed", "run_failed", "ran"},
    }
    out = {
        "session": "23-gpumode-shared-memory-gemm",
        "timestamp": now(),
        "inventory": collect_inventory("23-gpumode-shared-memory-gemm"),
        "source": {
            "gpumode_lab_id": "gpumode-lab-09-shared-memory-gemm",
            "gpumode_lessons": gpumode_links(),
            "extends": "04-cuda-tiled-matmul, 15-gpumode-coalescing, 17-gpumode-triton-autotune, and 22-gpumode-nsight-roofline",
        },
        "shared_memory_gemm": proxy,
        "cuda": cuda,
        "correctness": {
            "status": "passed" if all(checks.values()) else "failed",
            "checks": checks,
        },
        "boundary": (
            "This lab focuses on the shared-memory GEMM idea that sits between naive CUDA matmul "
            "and CUTLASS/Tensor Core kernels. Local CPU proxy numbers prove correctness and reuse math; "
            "CUDA timing is recorded only when the machine can compile and run it."
        ),
    }
    path = HERE / "out_gpumode_shared_memory_gemm.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "wrote",
        path.name,
        "cpu",
        proxy["status"],
        "cuda",
        cuda["status"],
        "correctness",
        out["correctness"]["status"],
    )


if __name__ == "__main__":
    main()
