#!/usr/bin/env python3
"""Compile and execute one generated protocol sequence with a reference DUT."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sequence", type=Path)
    parser.add_argument("dut", type=Path)
    parser.add_argument("testbench", type=Path)
    args = parser.parse_args()
    binary = Path("protocol-fixture.vvp").resolve()
    compile_run = subprocess.run(
        ["iverilog", "-g2012", "-s", "tb", "-o", str(binary),
         str(args.sequence.resolve()), str(args.dut.resolve()), str(args.testbench.resolve())],
        capture_output=True, text=True, check=False,
    )
    sys.stdout.write(compile_run.stdout)
    sys.stderr.write(compile_run.stderr)
    if compile_run.returncode:
        return compile_run.returncode
    execute_run = subprocess.run(["vvp", str(binary)], capture_output=True, text=True, check=False)
    sys.stdout.write(execute_run.stdout)
    sys.stderr.write(execute_run.stderr)
    return execute_run.returncode


if __name__ == "__main__":
    raise SystemExit(main())
