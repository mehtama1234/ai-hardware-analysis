#!/usr/bin/env python3
"""Rebuild and check derived local qualification evidence in fresh directories."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=None,
                        help="fresh parent directory; defaults to a unique temporary directory")
    args = parser.parse_args()
    parent = args.output_root.resolve() if args.output_root else Path(tempfile.mkdtemp(prefix="local-derived-qualification-"))
    if parent.exists() and any(parent.iterdir()):
        raise SystemExit(f"output root must be empty: {parent}")
    digital = parent / "digital"
    hybrid = parent / "counterfactual-hybrid"
    archive = parent / "archive"
    run([sys.executable, str(ROOT / "scripts/build_local_digital_qualification_package.py"), "--output", str(digital)])
    run([sys.executable, str(ROOT / "scripts/build_counterfactual_hybrid_advantage_report.py"), "--package", str(digital), "--output", str(hybrid)])
    run([sys.executable, str(ROOT / "scripts/check_local_digital_qualification_package.py"), str(digital)])
    run([sys.executable, str(ROOT / "scripts/check_counterfactual_hybrid_advantage_report.py"), str(hybrid)])
    run([sys.executable, str(ROOT / "scripts/build_local_qualification_archive.py"),
         "--package", str(digital), "--advantage", str(hybrid), "--output", str(archive),
         "--profile-family", str(ROOT / "analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification/local-profile-family-replay")])
    run([sys.executable, str(ROOT / "scripts/check_local_qualification_archive.py"), str(archive)])
    print(f"LOCAL DERIVED QUALIFICATION OK: {parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
