#!/usr/bin/env python3
"""Compile and execute the seeded counter testbench against a supplied RTL copy."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rtl", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    testbench = root / "benchmarks" / "seeded_counter" / "tb.sv"
    with tempfile.TemporaryDirectory(prefix="counter-retest-") as temporary:
        image = Path(temporary) / "counter.vvp"
        compile_run = subprocess.run(
            ["iverilog", "-g2012", "-o", str(image), str(args.rtl), str(testbench)],
            capture_output=True, text=True, check=False,
        )
        if compile_run.returncode:
            print(compile_run.stderr, end="")
            return compile_run.returncode
        simulation = subprocess.run(["vvp", str(image)], capture_output=True, text=True, check=False)
        print(simulation.stdout, end="")
        print(simulation.stderr, end="")
        return simulation.returncode


if __name__ == "__main__":
    raise SystemExit(main())
