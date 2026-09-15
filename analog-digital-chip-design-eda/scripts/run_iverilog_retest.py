#!/usr/bin/env python3
"""Compile and execute an RTL copy against a supplied Icarus testbench."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rtl", type=Path)
    parser.add_argument("testbench", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="iverilog-retest-") as temporary:
        image = Path(temporary) / "design.vvp"
        compile_run = subprocess.run(["iverilog", "-g2012", "-o", str(image), str(args.rtl), str(args.testbench)], capture_output=True, text=True, check=False)
        if compile_run.returncode:
            print(compile_run.stderr, end="")
            return compile_run.returncode
        simulation = subprocess.run(["vvp", str(image)], capture_output=True, text=True, check=False)
        print(simulation.stdout, end="")
        print(simulation.stderr, end="")
        return simulation.returncode


if __name__ == "__main__":
    raise SystemExit(main())
