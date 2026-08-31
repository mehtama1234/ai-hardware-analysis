#!/usr/bin/env python3
"""Starter harness for JAX scaling and roofline."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "roofline_model.py"


def main() -> int:
    payload = {
        "project": "jax-scaling-roofline",
        "track": "JAX scaling and roofline",
        "query": "jax scaling roofline gpu hbm inference",
        "profile": "memory-bandwidth",
        "source": SOURCE.name,
        "status": "ready",
        "runtime_notes": [],
    }
    if SOURCE.suffix == ".cu":
        if not shutil.which("nvcc"):
            payload["status"] = "source-only"
            payload["runtime_notes"].append("nvcc missing; compile on a CUDA development host")
    elif SOURCE.suffixes[-2:] == [".hip", ".cpp"] or SOURCE.name.endswith(".hip.cpp"):
        if not shutil.which("hipcc"):
            payload["status"] = "source-only"
            payload["runtime_notes"].append("hipcc missing; compile on a ROCm development host")
    elif SOURCE.suffix == ".py":
        proc = subprocess.run([sys.executable, str(SOURCE)], capture_output=True, text=True, check=False)
        payload["source_returncode"] = proc.returncode
        payload["source_stdout"] = proc.stdout.strip()[-1000:]
        payload["source_stderr"] = proc.stderr.strip()[-1000:]
        payload["status"] = "ran" if proc.returncode == 0 else "failed"
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] in {"ready", "ran", "source-only"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
