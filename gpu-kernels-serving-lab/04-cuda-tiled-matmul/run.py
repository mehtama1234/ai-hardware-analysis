"""Session 04: compile and run CUDA tiled matmul, or emit skip evidence."""

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
SRC = HERE / "tiled_matmul.cu"
BIN = HERE / "tiled_matmul"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(cmd: list[str], timeout: int = 120) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def main() -> None:
    nvcc = shutil.which("nvcc")
    if not nvcc:
        result = {
            "status": "skipped",
            "reason": "nvcc not found on PATH",
            "source": SRC.name,
            "boundary": (
                "The CUDA tiled-matmul source is present, but this machine cannot compile it "
                "until the NVIDIA CUDA toolkit is installed and a CUDA device is exposed."
            ),
        }
    else:
        compile_cmd = [nvcc, "-O3", "-std=c++17", str(SRC), "-o", str(BIN)]
        code, stdout, stderr = run_cmd(compile_cmd)
        if code != 0:
            result = {"status": "compile_failed", "compile_cmd": compile_cmd, "stdout": stdout, "stderr": stderr, "boundary": "nvcc ran but tiled_matmul.cu did not compile."}
        else:
            code, stdout, stderr = run_cmd([str(BIN)])
            try:
                kernel = json.loads(stdout.splitlines()[-1]) if stdout else {}
            except Exception:
                kernel = {"raw_stdout": stdout}
            result = {"status": "ran" if code == 0 else "run_failed", "compile_cmd": compile_cmd, "returncode": code, "stdout": stdout, "stderr": stderr, "kernel": kernel, "boundary": "This compares a readable naive CUDA matmul with a shared-memory tiled kernel. It is a teaching kernel, not cuBLAS."}

    out = {"session": "04-cuda-tiled-matmul", "timestamp": now(), "inventory": collect_inventory("04-cuda-tiled-matmul"), "result": result}
    path = HERE / "out_cuda_tiled_matmul.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, result["status"])


if __name__ == "__main__":
    main()

