"""Session 16: GPUMODE-derived warp reductions and scans."""

from __future__ import annotations

import json
import math
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.bench import median_seconds
from common.gpu_info import collect_inventory


HERE = Path(__file__).resolve().parent
SRC = HERE / "reductions.cu"
BIN = HERE / "reductions"
GPUMODE_ROOT = ROOT.parent / "gpu-mode-curriculum"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(cmd: list[str], timeout: int = 120) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def gpumode_links() -> list[dict[str, object]]:
    path = GPUMODE_ROOT / "analysis" / "lesson-intelligence.json"
    if not path.exists():
        return []
    lessons = json.loads(path.read_text(encoding="utf-8"))
    selected = []
    for lesson in lessons:
        concepts = set(lesson.get("concepts", []))
        title = lesson.get("title", "").lower()
        exercises = " ".join(lesson.get("exercise_candidates", [])).lower()
        if (
            "warp execution" in concepts
            or "shared memory tiling" in concepts
            or "reduction" in title
            or "scan" in title
            or "reduction" in exercises
            or "warp-shuffle" in exercises
        ):
            selected.append(
                {
                    "index": lesson["index"],
                    "title": lesson["title"],
                    "url": lesson["url"],
                    "topics": lesson["topics"],
                    "concepts": lesson.get("concepts", []),
                    "prerequisites": lesson.get("prerequisites", []),
                }
            )
    return selected[:12]


def bandwidth_gbps(bytes_moved: int, seconds: float) -> float:
    return round(bytes_moved / seconds / 1e9, 3) if seconds > 0 else math.inf


def cpu_reduction_and_scan(n: int = 1_048_576) -> dict[str, object]:
    torch.manual_seed(11)
    x = torch.randn(n, dtype=torch.float32)
    reference_sum = x.double().sum()
    reference_scan_tail = x.cumsum(0)[-1]

    rows = []

    def torch_sum() -> torch.Tensor:
        return x.sum()

    seconds = median_seconds(torch_sum, warmup=3, repeat=10)
    value = torch_sum()
    rows.append(
        {
            "pattern": "torch_sum",
            "primitive": "reduction",
            "seconds": round(seconds, 6),
            "bytes_moved_estimate": n * 4,
            "effective_gbps": bandwidth_gbps(n * 4, seconds),
            "abs_error": round(float((value.double() - reference_sum).abs().item()), 8),
            "semantic": "library reduction baseline",
        }
    )

    def chunked_sum() -> torch.Tensor:
        return x.view(1024, -1).sum(dim=1).sum()

    seconds = median_seconds(chunked_sum, warmup=3, repeat=10)
    value = chunked_sum()
    rows.append(
        {
            "pattern": "chunked_tree_sum",
            "primitive": "reduction",
            "seconds": round(seconds, 6),
            "bytes_moved_estimate": n * 4,
            "effective_gbps": bandwidth_gbps(n * 4, seconds),
            "abs_error": round(float((value.double() - reference_sum).abs().item()), 8),
            "semantic": "two-level tree reduction proxy for block partials",
        }
    )

    def cumsum_scan() -> torch.Tensor:
        return x.cumsum(0)

    seconds = median_seconds(cumsum_scan, warmup=2, repeat=8)
    scan = cumsum_scan()
    rows.append(
        {
            "pattern": "torch_cumsum",
            "primitive": "inclusive_scan",
            "seconds": round(seconds, 6),
            "bytes_moved_estimate": n * 8,
            "effective_gbps": bandwidth_gbps(n * 8, seconds),
            "abs_error": round(float((scan[-1] - reference_scan_tail).abs().item()), 8),
            "semantic": "parallel prefix-sum API baseline",
        }
    )

    return {
        "status": "ran",
        "framework": "torch",
        "elements": n,
        "rows": rows,
        "correctness": "passed" if all(row["abs_error"] <= 5e-3 for row in rows) else "failed",
        "finding": (
            "Reduction and scan are both bandwidth-sensitive primitives, but scan has stricter ordering "
            "and dependency structure than a plain sum."
        ),
    }


def cuda_result() -> dict[str, object]:
    nvcc = shutil.which("nvcc")
    if not nvcc:
        return {
            "status": "skipped",
            "reason": "nvcc not found on PATH",
            "source": SRC.name,
            "boundary": "CUDA source is present, but this environment cannot compile GPU kernels.",
        }
    code, stdout, stderr = run_cmd([nvcc, "-O3", "-std=c++17", str(SRC), "-o", str(BIN)], timeout=180)
    if code != 0:
        return {"status": "compile_failed", "stdout": stdout, "stderr": stderr, "source": SRC.name}
    code, stdout, stderr = run_cmd([str(BIN)], timeout=180)
    parsed: dict[str, object] = {}
    try:
        parsed = json.loads(stdout.splitlines()[-1])
    except Exception:
        parsed = {"raw_stdout": stdout}
    return {"status": "ran" if code == 0 else "run_failed", "stdout": stdout, "stderr": stderr, "result": parsed}


def main() -> None:
    cpu = cpu_reduction_and_scan()
    out = {
        "session": "16-gpumode-warp-reductions",
        "timestamp": now(),
        "inventory": collect_inventory("16-gpumode-warp-reductions"),
        "source": {
            "gpumode_lab_id": "gpumode-lab-02-warp-reductions",
            "gpumode_lessons": gpumode_links(),
            "extends": "03-cuda-vector-reduce",
        },
        "cpu_proxy": cpu,
        "cuda": cuda_result(),
        "correctness": {
            "status": cpu["correctness"],
            "note": "CPU reductions and scan are checked against high-precision or reference PyTorch results; CUDA source measures shared-memory and warp-shuffle block reductions when nvcc is available.",
        },
        "boundary": (
            "This lab is designed to bridge GPUMODE warp-level execution lessons into measurable code. "
            "The CPU proxy proves semantics everywhere; CUDA timing requires nvcc plus a CUDA-visible GPU."
        ),
    }
    path = HERE / "out_gpumode_warp_reductions.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, "cpu", len(cpu["rows"]), "cuda", out["cuda"]["status"])


if __name__ == "__main__":
    main()
