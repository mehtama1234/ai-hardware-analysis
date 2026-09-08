"""Session 23: GPUMODE-derived shared-memory tiled GEMM microscope."""

from __future__ import annotations

import json
import math
import shutil
import statistics
import tempfile
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.bench import sample_seconds
from common.gpu_info import collect_inventory
from common.provenance import source_provenance


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
    if not isinstance(tile, int) or isinstance(tile, bool) or tile < 1:
        raise ValueError("tile must be a positive integer")
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


def comparison(got: torch.Tensor, ref: torch.Tensor) -> dict[str, Any]:
    """Elementwise comparison against an independently accumulated FP64 result."""
    valid = got.shape == ref.shape and bool(torch.isfinite(got).all()) and bool(torch.isfinite(ref).all())
    error = max_abs_error(got.double(), ref) if valid else None
    passed = valid and bool(torch.allclose(got.double(), ref, atol=1e-4, rtol=1e-5))
    return {"passed": passed, "max_abs_error": error, "atol": 1e-4, "rtol": 1e-5,
            "reference": "torch CPU FP64 matmul", "finite_and_shape_match": valid}


def correctness_suite() -> list[dict[str, Any]]:
    generator = torch.Generator().manual_seed(23)
    cases = []
    for name, m, n, k, tile in (("scalar", 1, 1, 1, 8),
                                ("rectangular-tail", 5, 7, 11, 4),
                                ("noncontiguous", 9, 3, 5, 4),
                                ("zeros", 3, 5, 7, 4),
                                ("cancellation", 3, 4, 8, 4)):
        a = torch.randn((m, k), generator=generator)
        b = torch.randn((k, n), generator=generator)
        if name == "noncontiguous":
            a = a.t().contiguous().t()
            b = b.t().contiguous().t()
        elif name == "zeros":
            a.zero_()
        elif name == "cancellation":
            a[:, 1::2] = a[:, ::2]
            b[1::2] = -b[::2]
        ref = a.double() @ b.double()
        for implementation, output in (("naive_cpu_loop", naive_loop(a, b)),
                                       ("tiled_cpu_proxy", tiled_loop(a, b, tile)),
                                       ("torch_matmul_reference", a @ b)):
            cases.append({"case": name, "path": implementation, "shape": [m, n, k],
                          "tile": tile, "evidence_kind": "measured_cpu",
                          "input_strides": [list(a.stride()), list(b.stride())],
                          **comparison(output, ref)})
    return cases


def cpu_proxy(m: int = 32, n: int = 32, k: int = 32, tile: int = 8) -> dict[str, Any]:
    torch.manual_seed(23)
    a = torch.randn((m, k), dtype=torch.float32)
    b = torch.randn((k, n), dtype=torch.float32)
    ref = a.double() @ b.double()
    flops = 2 * m * n * k

    naive_samples = sample_seconds(lambda: naive_loop(a, b), warmup=1, repeat=3)
    tiled_samples = sample_seconds(lambda: tiled_loop(a, b, tile), warmup=1, repeat=5)
    torch_samples = sample_seconds(lambda: a @ b, warmup=2, repeat=10)
    naive_seconds = statistics.median(naive_samples)
    tiled_seconds = statistics.median(tiled_samples)
    torch_seconds = statistics.median(torch_samples)
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
            "max_abs_error": max_abs_error((a @ b).double(), ref),
            "purpose": "Vendor/library-style reference for correctness and scale contrast.",
        },
    ]
    for row, samples, warmup, output in zip(rows, (naive_samples, tiled_samples, torch_samples),
                                            (1, 1, 2), (naive_out, tiled_out, a @ b)):
        row.update({"evidence_kind": "measured_cpu", "samples_seconds": samples,
                    "seconds": statistics.median(samples), "warmup": warmup,
                    "repeat": len(samples), "correctness": comparison(output, ref),
                    "timing_scope": "CPU host wall clock including output allocation and Python dispatch; inputs preallocated",
                    "synchronization": "CPU synchronous operations"})
    model["evidence_kind"] = "analytical"
    speedup = naive_seconds / tiled_seconds if tiled_seconds else math.inf
    return {
        "status": "ran",
        "shape": [m, n, k],
        "tile": tile,
        "seed": 23,
        "torch_version": torch.__version__,
        "cpu_threads": torch.get_num_threads(),
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


def cuda_result(shape: tuple[int, int, int] = (256, 256, 256)) -> dict[str, Any]:
    nvcc = shutil.which("nvcc")
    if not nvcc:
        return {
            "status": "skipped",
            "reason": "nvcc not found on PATH",
            "source": SRC.name,
            "boundary": "CUDA source is present, but compiling/running requires the NVIDIA CUDA toolkit and a visible CUDA device.",
        }
    with tempfile.TemporaryDirectory(prefix="gemm-benchmark-") as build_dir:
        binary = str(Path(build_dir) / "shared_memory_gemm")
        compile_cmd = [nvcc, "-O3", "-std=c++17",
                       *[f"-DGEMM_{axis}={size}" for axis, size in zip("MNK", shape)],
                       str(SRC), "-lcublas", "-o", binary]
        try:
            code, stdout, stderr = run_cmd(compile_cmd)
            if code == 0:
                run_code, run_stdout, run_stderr = run_cmd([binary])
        except subprocess.TimeoutExpired as exc:
            return {"status": "run_failed", "reason": "compile or execution timeout",
                    "command": exc.cmd, "shape": list(shape)}
    if code != 0:
        return {
            "status": "compile_failed",
            "compile_cmd": compile_cmd,
            "stdout": stdout,
            "stderr": stderr,
            "boundary": "nvcc ran but shared_memory_gemm.cu did not compile.",
        }
    code, stdout, stderr = run_code, run_stdout, run_stderr
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
        "requested_shape": list(shape),
        "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
        "boundary": "CUDA path compares naive global-memory GEMM with a shared-memory tiled kernel.",
    }


def cuda_passes(cuda: dict[str, Any]) -> bool:
    if cuda["status"] == "skipped":
        return True  # Execution coverage remains unavailable, not measured.
    if cuda["status"] != "ran":
        return False
    kernel = cuda.get("kernel", {})
    if not isinstance(kernel, dict):
        return False
    if "requested_shape" in cuda and kernel.get("shape") != cuda["requested_shape"]:
        return False
    for key in ("naive_max_abs_error", "tiled_max_abs_error", "cublas_max_abs_error"):
        value = kernel.get(key)
        if not isinstance(value, (float, int)) or isinstance(value, bool) or not math.isfinite(value) or not 0 <= value <= 1e-4:
            return False
    for key in ("naive_ms", "tiled_ms", "cublas_ms"):
        value = kernel.get(key)
        if not isinstance(value, (float, int)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0:
            return False
    for prefix in ("naive", "tiled", "cublas"):
        samples = kernel.get(f"{prefix}_samples_ms")
        if not isinstance(samples, list) or len(samples) != 7:
            return False
        if any(not isinstance(value, (int, float)) or isinstance(value, bool) or
               not math.isfinite(value) or value <= 0 for value in samples):
            return False
        if not math.isclose(statistics.median(samples), kernel[f"{prefix}_ms"], rel_tol=1e-4, abs_tol=1e-5):
            return False
    return True


def main() -> int:
    proxy = cpu_proxy()
    suite = correctness_suite()
    cuda = cuda_result()
    cuda_cases = [cuda]
    if cuda["status"] != "skipped":
        cuda_cases.extend(cuda_result(shape) for shape in ((5, 7, 11), (31, 17, 33)))
    checks = {
        "cpu_proxy_ran": proxy["status"] == "ran",
        "all_cpu_paths_finite": all(math.isfinite(row["seconds"]) and row["seconds"] > 0 for row in proxy["rows"]),
        "naive_correct": proxy["rows"][0]["max_abs_error"] <= 1e-4,
        "tiled_correct": proxy["rows"][1]["max_abs_error"] <= 1e-4,
        "elementwise_reference_checks": all(row["correctness"]["passed"] for row in proxy["rows"]),
        "edge_cases_correct": all(row["passed"] for row in suite),
        "modeled_traffic_reduction": proxy["traffic_model"]["modeled_global_memory_reduction_pct"] > 0,
        "cuda_path_classified": cuda["status"] in {"skipped", "compile_failed", "run_failed", "ran"},
        "cuda_correct_if_executed": all(cuda_passes(case) for case in cuda_cases),
    }
    out = {
        "session": "23-gpumode-shared-memory-gemm",
        "timestamp": now(),
        "provenance": source_provenance(ROOT.parent, [Path(__file__), SRC,
            ROOT / "common/bench.py", ROOT / "common/gpu_info.py", ROOT / "common/provenance.py"]),
        "inventory": collect_inventory("23-gpumode-shared-memory-gemm"),
        "source": {
            "gpumode_lab_id": "gpumode-lab-09-shared-memory-gemm",
            "gpumode_lessons": gpumode_links(),
            "extends": "04-cuda-tiled-matmul, 15-gpumode-coalescing, 17-gpumode-triton-autotune, and 22-gpumode-nsight-roofline",
        },
        "shared_memory_gemm": proxy,
        "cuda": cuda,
        "cuda_cases": cuda_cases,
        "correctness_cases": suite,
        "gpu_execution_accepted": len(cuda_cases) == 3 and all(case["status"] == "ran" and cuda_passes(case) for case in cuda_cases),
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
    path.write_text(json.dumps(out, indent=2, allow_nan=False), encoding="utf-8")
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
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
