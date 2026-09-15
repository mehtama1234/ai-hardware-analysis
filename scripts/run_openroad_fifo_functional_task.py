"""Run a functional FIFO task against the native OpenROAD checkout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
REPO = Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts")
REVISION = "be0dca0b1"
SOURCES = [
    Path("flow/designs/src/fifo/fifo.v"),
    Path("flow/designs/src/fifo/fifo1.v"),
    Path("flow/designs/src/fifo/fifomem.v"),
    Path("flow/designs/src/fifo/rptr_empty.v"),
    Path("flow/designs/src/fifo/wptr_full.v"),
    Path("flow/designs/src/fifo/sync_r2w.v"),
    Path("flow/designs/src/fifo/sync_w2r.v"),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-real/openroad-fifo-functional")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if not REPO.is_dir():
        print(json.dumps({"status": "blocked", "reason": "OpenROAD checkout missing"}, sort_keys=True))
        return 1
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    if revision != REVISION:
        print(json.dumps({"status": "blocked", "reason": "OpenROAD revision mismatch", "expected": REVISION, "actual": revision}, sort_keys=True))
        return 1
    with tempfile.TemporaryDirectory(prefix="openroad-fifo-functional-") as directory:
        root = Path(directory)
        copied = []
        for source in SOURCES:
            destination = root / source
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / source, destination)
            copied.append(str(destination))
        testbench = root / "openroad_fifo_tb.sv"
        shutil.copy2(ROOT / "benchmarks/repository_scale/openroad_fifo_tb.sv", testbench)
        binary = root / "fifo.vvp"
        compile_run = subprocess.run(["iverilog", "-g2012", "-o", str(binary), *copied, str(testbench)], cwd=root, capture_output=True, text=True, check=False)
        simulate = subprocess.run(["vvp", str(binary)], cwd=root, capture_output=True, text=True, check=False) if compile_run.returncode == 0 else None
    output = (simulate.stdout if simulate else "") + (simulate.stderr if simulate else "")
    status = "passed" if compile_run.returncode == 0 and simulate is not None and simulate.returncode == 0 and "PASS fifo functional" in output and "FAIL " not in output else "blocked"
    (args.output / "compile.stdout.log").write_text(compile_run.stdout, encoding="utf-8")
    (args.output / "compile.stderr.log").write_text(compile_run.stderr, encoding="utf-8")
    (args.output / "simulation.log").write_text(output, encoding="utf-8")
    report = {"schema_version": "openroad-fifo-functional-report-v1", "repository": "OpenROAD-flow-scripts", "repository_revision": revision, "status": status, "compile_returncode": compile_run.returncode, "simulation_returncode": simulate.returncode if simulate else None, "claim_boundary": "one native OpenROAD FIFO read/write transaction; not CDC stress or full project regression"}
    (args.output / "openroad-fifo-functional-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "repository_revision": revision, "report": str(args.output / "openroad-fifo-functional-report.json")}, sort_keys=True))
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
