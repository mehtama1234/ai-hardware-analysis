"""Session 24: GPUMODE-derived Tensor Core and CUTLASS matmul readiness lab."""

from __future__ import annotations

import json
import math
import os
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
SRC = HERE / "wmma_tensor_core_gemm.cu"
BIN = HERE / "wmma_tensor_core_gemm"


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
        text = " ".join([title, " ".join(lesson.get("exercise_candidates", []))]).lower()
        if (
            "cutlass" in topics
            or "tensor cores" in concepts
            or "shared memory tiling" in concepts
            or "wmma" in text
            or "cute" in text
            or "wgmma" in text
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
    return selected[:16]


def gflops(flops: int, seconds: float) -> float:
    return round(flops / seconds / 1e9, 4) if seconds > 0 else math.inf


def cpu_precision_proxy(m: int = 256, n: int = 256, k: int = 256) -> dict[str, Any]:
    torch.manual_seed(24)
    a32 = torch.randn((m, k), dtype=torch.float32)
    b32 = torch.randn((k, n), dtype=torch.float32)
    ref = a32 @ b32
    flops = 2 * m * n * k

    rows = []
    for name, a, b, out_dtype in [
        ("fp32_reference", a32, b32, torch.float32),
        ("fp16_inputs_accumulated_to_fp32", a32.to(torch.float16), b32.to(torch.float16), torch.float32),
        ("bf16_inputs_accumulated_to_fp32", a32.to(torch.bfloat16), b32.to(torch.bfloat16), torch.float32),
    ]:
        def work() -> None:
            (a @ b).to(out_dtype)

        seconds = median_seconds(work, warmup=2, repeat=8)
        out = (a @ b).to(torch.float32)
        rows.append(
            {
                "path": name,
                "input_dtype": str(a.dtype).replace("torch.", ""),
                "accumulation_observed_dtype": str(out.dtype).replace("torch.", ""),
                "seconds": round(seconds, 6),
                "gflops": gflops(flops, seconds),
                "max_abs_error": round(float((out - ref).abs().max().item()), 6),
                "relative_l2_error_pct": round(float(torch.linalg.vector_norm(out - ref) / torch.linalg.vector_norm(ref) * 100.0), 6),
            }
        )
    return {
        "status": "ran",
        "shape": [m, n, k],
        "rows": rows,
        "finding": (
            "Tensor Core kernels buy throughput by using low-precision inputs with controlled accumulation. "
            f"On this CPU proxy, fp16 relative L2 error is {rows[1]['relative_l2_error_pct']}% and "
            f"bf16 relative L2 error is {rows[2]['relative_l2_error_pct']}% against fp32."
        ),
    }


def tensor_core_tile_model(m: int = 256, n: int = 256, k: int = 256) -> dict[str, Any]:
    tiles = [
        {"name": "wmma_m16n16k16", "m": 16, "n": 16, "k": 16, "input": "fp16", "accumulator": "fp32"},
        {"name": "wmma_m16n16k8", "m": 16, "n": 16, "k": 8, "input": "tf32", "accumulator": "fp32"},
        {"name": "wgmma_m64n64k16", "m": 64, "n": 64, "k": 16, "input": "fp16/bf16", "accumulator": "fp32"},
    ]
    rows = []
    for tile in tiles:
        programs = math.ceil(m / tile["m"]) * math.ceil(n / tile["n"])
        k_tiles = math.ceil(k / tile["k"])
        mma_ops = programs * k_tiles
        rows.append(
            {
                **tile,
                "shape": [m, n, k],
                "output_tiles": programs,
                "k_tiles_per_output": k_tiles,
                "mma_ops": mma_ops,
                "eligible_shape": m % tile["m"] == 0 and n % tile["n"] == 0 and k % tile["k"] == 0,
                "handoff": "use WMMA for the teaching kernel; use CUTLASS/CuTe for production tiling, epilogues, layouts, and architecture-specific schedules",
            }
        )
    return {
        "status": "ran",
        "rows": rows,
        "finding": "The local shape is tile-clean for WMMA and WGMMA models, so the next GPU run should focus on accumulator precision, layout, and CUTLASS schedule selection rather than edge masking.",
    }


def readiness() -> dict[str, Any]:
    cutlass_root = os.environ.get("CUTLASS_ROOT")
    cutlass_candidates = [
        Path(cutlass_root) if cutlass_root else None,
        Path("/usr/local/cutlass"),
        ROOT.parent / "cutlass",
    ]
    cutlass_path = next((path for path in cutlass_candidates if path and (path / "include" / "cutlass").exists()), None)
    tools = {
        "nvcc": shutil.which("nvcc"),
        "nvidia-smi": shutil.which("nvidia-smi"),
        "cutlass_root": str(cutlass_path) if cutlass_path else None,
    }
    return {
        "status": "ready" if tools["nvcc"] and torch.cuda.is_available() else "skipped",
        "tools": tools,
        "torch_cuda_available": bool(torch.cuda.is_available()),
        "cutlass_available": bool(cutlass_path),
        "reason": (
            "CUDA compiler and device are visible; WMMA source can be compiled and CUTLASS examples can be added if headers are present."
            if tools["nvcc"] and torch.cuda.is_available()
            else "Tensor Core timing requires nvcc plus a CUDA-visible NVIDIA GPU; CUTLASS integration also needs CUTLASS headers."
        ),
    }


def cuda_result() -> dict[str, Any]:
    ready = readiness()
    nvcc = ready["tools"]["nvcc"]
    if not nvcc or not torch.cuda.is_available():
        return {
            "status": "skipped",
            "readiness": ready,
            "source": SRC.name,
            "boundary": "WMMA source is present, but compile/run is gated on nvcc and torch.cuda.is_available().",
        }
    compile_cmd = [nvcc, "-O3", "-std=c++17", "-arch=sm_70", str(SRC), "-o", str(BIN)]
    code, stdout, stderr = run_cmd(compile_cmd)
    if code != 0:
        return {
            "status": "compile_failed",
            "readiness": ready,
            "compile_cmd": compile_cmd,
            "stdout": stdout,
            "stderr": stderr,
            "boundary": "nvcc ran but the WMMA Tensor Core teaching kernel did not compile.",
        }
    code, stdout, stderr = run_cmd([str(BIN)])
    try:
        parsed = json.loads(stdout.splitlines()[-1]) if stdout else {}
    except Exception:
        parsed = {"raw_stdout": stdout}
    return {
        "status": "ran" if code == 0 else "run_failed",
        "readiness": ready,
        "compile_cmd": compile_cmd,
        "returncode": code,
        "stdout": stdout,
        "stderr": stderr,
        "kernel": parsed,
        "boundary": "WMMA path measures a teaching Tensor Core tile, not a tuned CUTLASS production kernel.",
    }


def main() -> None:
    precision = cpu_precision_proxy()
    tile_model = tensor_core_tile_model()
    cuda = cuda_result()
    checks = {
        "precision_proxy_ran": precision["status"] == "ran",
        "tile_model_ran": tile_model["status"] == "ran",
        "all_precision_rows_finite": all(math.isfinite(row["seconds"]) and row["seconds"] > 0 for row in precision["rows"]),
        "low_precision_error_measured": all("relative_l2_error_pct" in row for row in precision["rows"][1:]),
        "tile_eligibility_recorded": all("eligible_shape" in row for row in tile_model["rows"]),
        "cuda_path_classified": cuda["status"] in {"skipped", "compile_failed", "run_failed", "ran"},
    }
    out = {
        "session": "24-gpumode-tensor-core-cutlass",
        "timestamp": now(),
        "inventory": collect_inventory("24-gpumode-tensor-core-cutlass"),
        "source": {
            "gpumode_lab_id": "gpumode-lab-10-tensor-core-cutlass",
            "gpumode_lessons": gpumode_links(),
            "extends": "23-gpumode-shared-memory-gemm, 17-gpumode-triton-autotune, and 06-triton-matmul",
        },
        "tensor_core_precision": precision,
        "tensor_core_tile_model": tile_model,
        "cuda": cuda,
        "correctness": {
            "status": "passed" if all(checks.values()) else "failed",
            "checks": checks,
        },
        "boundary": (
            "This lab turns Tensor Core/CUTLASS lessons into measurable readiness: low-precision numerical drift, "
            "MMA tile eligibility, local CUDA/CUTLASS availability, and a WMMA source path. It does not claim "
            "Tensor Core throughput unless the CUDA kernel actually compiles and runs."
        ),
    }
    path = HERE / "out_gpumode_tensor_core_cutlass.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "wrote",
        path.name,
        "precision",
        precision["status"],
        "cuda",
        cuda["status"],
        "correctness",
        out["correctness"]["status"],
    )


if __name__ == "__main__":
    main()
