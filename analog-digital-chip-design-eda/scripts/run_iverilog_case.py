#!/usr/bin/env python3
"""Compile and execute one RTL/testbench case, retaining its waveform and logs."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rtl", type=Path)
    parser.add_argument("testbench", type=Path)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    args.run_root.mkdir(parents=True, exist_ok=True)
    image = args.run_root / "design.vvp"
    compile_run = subprocess.run(["iverilog", "-g2012", "-o", str(image), str(args.rtl), str(args.testbench)], capture_output=True, text=True, check=False)
    (args.run_root / "compile.stdout.log").write_text(compile_run.stdout, encoding="utf-8")
    (args.run_root / "compile.stderr.log").write_text(compile_run.stderr, encoding="utf-8")
    if compile_run.returncode:
        return compile_run.returncode
    simulation = subprocess.run(["vvp", str(image)], cwd=args.run_root, capture_output=True, text=True, check=False)
    (args.run_root / "stdout.log").write_text(simulation.stdout, encoding="utf-8")
    (args.run_root / "stderr.log").write_text(simulation.stderr, encoding="utf-8")
    print(simulation.stdout, end="")
    print(simulation.stderr, end="")
    return simulation.returncode


if __name__ == "__main__":
    raise SystemExit(main())
