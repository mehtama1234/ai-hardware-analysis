#!/usr/bin/env python3
"""Run the lesson lab and write measurements.json."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "measurements.json"


def main() -> int:
    proc = subprocess.run([sys.executable, "starter.py"], cwd=HERE, capture_output=True, text=True, check=False)
    payload = {}
    if proc.stdout.strip():
        payload = json.loads(proc.stdout)
    artifact = {
        "lab_id": "lesson-040-lecture-74-scaleml-series-positional-encodings-and-path-attentio",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": payload.get("status", "failed"),
        "correctness": {
            "status": "passed" if proc.returncode == 0 and payload.get("checks") else "failed",
            "checks": {
                "starter_exited_zero": proc.returncode == 0,
                "payload_has_lesson_index": bool(payload.get("lesson_index")),
                "payload_has_checks": bool(payload.get("checks")),
            },
        },
        "runtime_readiness": {
            "status": "cpu-proxy",
            "notes": [
                "Generated lesson lab uses local CPU proxy checks; replace or extend lab.py with CUDA/Triton/HIP kernels on a GPU host."
            ],
        },
        "measurement": {
            "rows": payload.get("checks", []),
            "summary": f"Lesson {payload.get('lesson_index')} local proxy emitted {len(payload.get('checks', []))} checks.",
        },
        "starter": {
            "command": f"{sys.executable} starter.py",
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout.strip()[-2000:],
            "stderr_tail": proc.stderr.strip()[-2000:],
        },
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "correctness": artifact["correctness"]["status"], "path": OUT.name}, indent=2))
    return 0 if artifact["correctness"]["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
