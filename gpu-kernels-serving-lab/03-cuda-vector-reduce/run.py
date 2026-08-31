"""Session 03: compile and run first CUDA kernels, or emit a skip artifact."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


HERE = Path(__file__).resolve().parent
SRC = HERE / "vector_reduce.cu"
BIN = HERE / "vector_reduce"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(cmd: list[str], timeout: int = 60) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def main() -> None:
    nvcc = shutil.which("nvcc")
    result: dict[str, object]
    if not nvcc:
        result = {
            "status": "skipped",
            "reason": "nvcc not found on PATH",
            "source": str(SRC.name),
            "boundary": (
                "CUDA source exists, but this machine cannot compile it yet. Install the NVIDIA "
                "CUDA toolkit and expose a CUDA GPU to turn this into a measured kernel result."
            ),
        }
    else:
        compile_cmd = [nvcc, "-O3", "-std=c++17", str(SRC), "-o", str(BIN)]
        code, stdout, stderr = run_cmd(compile_cmd, timeout=120)
        if code != 0:
            result = {
                "status": "compile_failed",
                "compile_cmd": compile_cmd,
                "stdout": stdout,
                "stderr": stderr,
                "boundary": "The CUDA compiler ran, but the tutorial kernel did not compile.",
            }
        else:
            code, stdout, stderr = run_cmd([str(BIN)], timeout=120)
            try:
                kernel = json.loads(stdout.splitlines()[-1]) if stdout else {}
            except Exception:
                kernel = {"raw_stdout": stdout}
            result = {
                "status": "ran" if code == 0 else "run_failed",
                "compile_cmd": compile_cmd,
                "returncode": code,
                "stdout": stdout,
                "stderr": stderr,
                "kernel": kernel,
                "boundary": (
                    "This measures two beginner CUDA kernels: coalesced vector add and one-stage "
                    "block reduction. It does not claim library-level performance."
                ),
            }

    out = {
        "session": "03-cuda-vector-reduce",
        "timestamp": now(),
        "inventory": collect_inventory("03-cuda-vector-reduce"),
        "result": result,
    }
    path = HERE / "out_cuda_vector_reduce.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, result["status"])


if __name__ == "__main__":
    main()

