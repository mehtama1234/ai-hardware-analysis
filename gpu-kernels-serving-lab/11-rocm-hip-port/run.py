"""Session 11: HIP portability compile/run status."""

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
SRC = HERE / "vector_add.hip.cpp"
BIN = HERE / "vector_add_hip"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(cmd: list[str], timeout: int = 120) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def main() -> None:
    hipcc = shutil.which("hipcc")
    if not hipcc:
        result = {
            "status": "skipped",
            "reason": "hipcc not found on PATH",
            "source": SRC.name,
            "boundary": (
                "HIP source exists, but ROCm compilation cannot run on this machine yet."
            ),
        }
    else:
        cmd = [hipcc, "-O3", str(SRC), "-o", str(BIN)]
        code, stdout, stderr = run_cmd(cmd)
        if code != 0:
            result = {"status": "compile_failed", "compile_cmd": cmd, "stdout": stdout, "stderr": stderr, "boundary": "HIP compiler ran but source did not compile."}
        else:
            code, stdout, stderr = run_cmd([str(BIN)])
            try:
                parsed = json.loads(stdout.splitlines()[-1])
            except Exception:
                parsed = {"raw_stdout": stdout}
            result = {"status": "ran" if code == 0 else "run_failed", "compile_cmd": cmd, "returncode": code, "stdout": stdout, "stderr": stderr, "kernel": parsed, "boundary": "This proves the basic HIP port shape, not tuned AMD performance."}

    out = {"session": "11-rocm-hip-port", "timestamp": now(), "inventory": collect_inventory("11-rocm-hip-port"), "result": result}
    path = HERE / "out_rocm_hip_port.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, result["status"])


if __name__ == "__main__":
    main()

