"""Compile and run the seeded counter testbench for repository-scale tasks."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rtl", type=Path)
    parser.add_argument("testbench", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="seeded-counter-check-") as directory:
        binary = Path(directory) / "counter.vvp"
        compile_run = subprocess.run(
            ["iverilog", "-g2012", "-o", str(binary), str(args.rtl), str(args.testbench)],
            capture_output=True, text=True, check=False,
        )
        if compile_run.returncode != 0:
            sys.stdout.write(compile_run.stdout)
            sys.stderr.write(compile_run.stderr)
            return compile_run.returncode
        simulation = subprocess.run(["vvp", str(binary)], capture_output=True, text=True, check=False)
        sys.stdout.write(simulation.stdout)
        sys.stderr.write(simulation.stderr)
        # Some Icarus/VVP combinations normalize `$finish(1)` to a zero
        # process status. Convert the testbench's explicit verdict into the
        # benchmark contract so fail-to-pass is measured correctly.
        if "FAIL " in simulation.stdout or "FAIL " in simulation.stderr:
            return 1
        return simulation.returncode


if __name__ == "__main__":
    raise SystemExit(main())
