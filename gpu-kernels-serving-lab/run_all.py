"""Run every currently implemented lab session and rebuild the site."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUNS = [
    "00-orientation",
    "01-hf-baseline",
    "02-roofline",
    "03-cuda-vector-reduce",
    "04-cuda-tiled-matmul",
    "05-cuda-tiny-attention",
    "06-triton-matmul",
    "07-triton-fused-attention",
    "08-quantized-inference",
    "09-vllm-serving",
    "10-kv-cache-memory-manager",
    "11-rocm-hip-port",
    "12-jax-scaling-practicum",
    "15-gpumode-coalescing",
    "16-gpumode-warp-reductions",
    "17-gpumode-triton-autotune",
    "18-gpumode-online-softmax",
    "19-gpumode-torch-compile",
    "20-gpumode-vllm-scheduler",
    "21-gpumode-quantized-kernels",
    "22-gpumode-nsight-roofline",
    "23-gpumode-shared-memory-gemm",
    "24-gpumode-tensor-core-cutlass",
    "25-gpumode-rocm-hip-portability",
    "26-gpumode-distributed-communication",
]
CAPSTONE_EXTRA_RUNS = [("13-capstone-mini-serving-engine", "load_test.py")]
CAPSTONE_REPORT = "13-capstone-mini-serving-engine"
SYNTHESIS_REPORT = "14-final-synthesis"


def run(cmd: list[str], cwd: Path) -> None:
    print("$", " ".join(cmd), "(cwd:", cwd.relative_to(ROOT), ")")
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    for session in RUNS:
        run([sys.executable, "run.py"], ROOT / session)
    for session, script in CAPSTONE_EXTRA_RUNS:
        run([sys.executable, script], ROOT / session)
    run([sys.executable, "run.py"], ROOT / CAPSTONE_REPORT)
    run([sys.executable, "run.py"], ROOT / SYNTHESIS_REPORT)
    for session in [*RUNS, CAPSTONE_REPORT, SYNTHESIS_REPORT]:
        run([sys.executable, "build_page.py"], ROOT / session)
    run([sys.executable, "build_site.py"], ROOT)


if __name__ == "__main__":
    main()
