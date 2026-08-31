#!/usr/bin/env python3
"""Starter entry for lesson-048-lecture-66-game-arena."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "lab.py"


def main() -> int:
    proc = subprocess.run([sys.executable, str(SOURCE)], cwd=HERE, capture_output=True, text=True, check=False)
    payload = {}
    if proc.stdout.strip():
        payload = json.loads(proc.stdout)
    payload["source_returncode"] = proc.returncode
    payload["source"] = SOURCE.name
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if proc.returncode == 0 and payload.get("status") == "ran-cpu-proxy" else 1


if __name__ == "__main__":
    raise SystemExit(main())
