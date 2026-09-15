#!/usr/bin/env python3
"""Build and independently verify the local profile-family replay stage."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOFTWARE = ROOT / "analog-in-memory-ai-inference/software-architecture"
SOURCE_PACKAGE = SOFTWARE / "experiments/gpt2-hybrid-v1/qualification/local-profile-to-workload-qualification"
OUTPUT = SOFTWARE / "experiments/gpt2-hybrid-v1/qualification/local-profile-family-replay"


def run(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=SOFTWARE, text=True,
                               capture_output=True, check=False)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def main() -> int:
    python = sys.executable
    run([python, "scripts/run_local_profile_family_replay.py",
         "--package", str(SOURCE_PACKAGE), "--output", str(OUTPUT)])
    run([python, "scripts/check_local_profile_family_replay.py", str(OUTPUT)])
    print(f"LOCAL PROFILE FAMILY ACCEPTANCE OK: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
