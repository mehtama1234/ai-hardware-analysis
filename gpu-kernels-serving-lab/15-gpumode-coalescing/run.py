"""Session 15: GPUMODE-derived memory coalescing microscope."""

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
SRC = HERE / "coalescing.cu"
BIN = HERE / "coalescing"
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
        title = lesson.get("title", "")
        if "memory coalescing" in concepts or "coalesc" in title.lower() or "profile cuda" in title.lower():
            selected.append(
                {
                    "index": lesson["index"],
                    "title": title,
                    "url": lesson["url"],
                    "topics": lesson["topics"],
                    "concepts": lesson.get("concepts", []),
                }
            )
    return selected[:12]


def bandwidth_gbps(bytes_moved: int, seconds: float) -> float:
    return round(bytes_moved / seconds / 1e9, 3) if seconds > 0 else math.inf


def cpu_patterns(n: int = 1_000_000) -> list[dict[str, object]]:
    torch.manual_seed(7)
    a = torch.randn(n, dtype=torch.float32)
    b = torch.randn(n, dtype=torch.float32)
    contiguous_index = torch.arange(n)
    strided_index = (torch.arange(n) * 17) % n
    gathered_index = torch.randperm(n)

    rows = []
    for name, index in [
        ("contiguous", contiguous_index),
        ("strided_mod17", strided_index),
        ("random_gather", gathered_index),
    ]:
        out = torch.empty_like(a)

        def work() -> None:
            torch.index_select(a, 0, index, out=out)
            out.add_(torch.index_select(b, 0, index))

        expected = a[index] + b[index]
        work()
        max_abs_error = float((out - expected).abs().max().item())
        seconds = median_seconds(work, warmup=2, repeat=8)
        bytes_moved = int(n * (4 + 4 + 4) + n * 8)
        rows.append(
            {
                "pattern": name,
                "seconds": round(seconds, 6),
                "elements": n,
                "bytes_moved_estimate": bytes_moved,
                "effective_gbps": bandwidth_gbps(bytes_moved, seconds),
                "max_abs_error": round(max_abs_error, 8),
                "semantic": (
                    "contiguous/coalesced access"
                    if name == "contiguous"
                    else "regular non-contiguous access"
                    if name == "strided_mod17"
                    else "irregular gather access"
                ),
            }
        )
    base = rows[0]["effective_gbps"]
    for row in rows:
        row["relative_to_contiguous"] = round(row["effective_gbps"] / base, 3) if base else None
    return rows


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
    parsed = {}
    try:
        parsed = json.loads(stdout.splitlines()[-1])
    except Exception:
        parsed = {"raw_stdout": stdout}
    return {"status": "ran" if code == 0 else "run_failed", "stdout": stdout, "stderr": stderr, "result": parsed}


def main() -> None:
    cpu_rows = cpu_patterns()
    all_cpu_correct = all(row["max_abs_error"] <= 1e-6 for row in cpu_rows)
    fastest = max(cpu_rows, key=lambda row: row["effective_gbps"])
    slowest = min(cpu_rows, key=lambda row: row["effective_gbps"])
    out = {
        "session": "15-gpumode-coalescing",
        "timestamp": now(),
        "inventory": collect_inventory("15-gpumode-coalescing"),
        "source": {
            "gpumode_lab_id": "gpumode-lab-01-coalescing",
            "gpumode_lessons": gpumode_links(),
            "extends": "03-cuda-vector-reduce",
        },
        "cpu_proxy": {
            "status": "ran",
            "framework": "torch",
            "rows": cpu_rows,
            "finding": (
                f"{fastest['pattern']} measured highest effective bandwidth at {fastest['effective_gbps']} GB/s; "
                f"{slowest['pattern']} measured lowest at {slowest['effective_gbps']} GB/s."
            ),
        },
        "cuda": cuda_result(),
        "correctness": {
            "status": "passed" if all_cpu_correct else "failed",
            "cpu_max_abs_error": max(row["max_abs_error"] for row in cpu_rows),
            "note": "CPU variants are checked against a[index] + b[index]; CUDA source mirrors contiguous, strided, and gathered access patterns.",
        },
        "boundary": (
            "This is a GPUMODE-derived microscope for access patterns. CPU proxy numbers demonstrate "
            "semantic shape on any machine; CUDA measurements become available when nvcc and a GPU are present."
        ),
    }
    path = HERE / "out_gpumode_coalescing.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, "cpu", len(cpu_rows), "cuda", out["cuda"]["status"])


if __name__ == "__main__":
    main()
