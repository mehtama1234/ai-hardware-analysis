"""Compile and run the OpenROAD GCD RTL against its disposable testbench."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rtl", type=Path)
    parser.add_argument("testbench", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="openroad-gcd-check-") as directory:
        binary = Path(directory) / "gcd.vvp"
        compile_run = subprocess.run(["iverilog", "-g2012", "-o", str(binary), str(args.rtl), str(args.testbench)], capture_output=True, text=True, check=False)
        if compile_run.returncode:
            sys.stdout.write(compile_run.stdout); sys.stderr.write(compile_run.stderr)
            return compile_run.returncode
        simulation = subprocess.run(["vvp", str(binary)], capture_output=True, text=True, check=False)
        sys.stdout.write(simulation.stdout); sys.stderr.write(simulation.stderr)
        return 1 if "FAIL " in simulation.stdout or "FAIL " in simulation.stderr else simulation.returncode


if __name__ == "__main__":
    raise SystemExit(main())
