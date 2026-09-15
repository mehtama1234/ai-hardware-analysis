"""Run an AES-128 known-answer test against the native OpenROAD checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REPO = Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts")
REVISION = "be0dca0b1"
SOURCES = [
    Path("flow/designs/src/aes/timescale.v"), Path("flow/designs/src/aes/aes_rcon.v"),
    Path("flow/designs/src/aes/aes_sbox.v"), Path("flow/designs/src/aes/aes_inv_sbox.v"),
    Path("flow/designs/src/aes/aes_key_expand_128.v"), Path("flow/designs/src/aes/aes_cipher_top.v"),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-real/openroad-aes-functional")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if not REPO.is_dir():
        print(json.dumps({"status": "blocked", "reason": "OpenROAD checkout missing"}, sort_keys=True)); return 1
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    if revision != REVISION:
        print(json.dumps({"status": "blocked", "reason": "OpenROAD revision mismatch", "expected": REVISION, "actual": revision}, sort_keys=True)); return 1
    with tempfile.TemporaryDirectory(prefix="openroad-aes-functional-") as directory:
        root = Path(directory)
        copied = []
        for source in SOURCES:
            destination = root / source
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / source, destination)
            copied.append(str(destination))
        testbench = root / "openroad_aes_tb.sv"
        shutil.copy2(ROOT / "benchmarks/repository_scale/openroad_aes_tb.sv", testbench)
        binary = root / "aes.vvp"
        compile_run = subprocess.run(["iverilog", "-g2012", "-I", str(root / "flow/designs/src/aes"), "-o", str(binary), *copied, str(testbench)], cwd=root, capture_output=True, text=True, check=False)
        simulate = subprocess.run(["vvp", str(binary)], cwd=root, capture_output=True, text=True, check=False) if compile_run.returncode == 0 else None
    simulation_text = (simulate.stdout if simulate else "") + (simulate.stderr if simulate else "")
    status = "passed" if compile_run.returncode == 0 and simulate is not None and simulate.returncode == 0 and "PASS aes known-answer" in simulation_text and "FAIL " not in simulation_text else "blocked"
    (args.output / "compile.stdout.log").write_text(compile_run.stdout, encoding="utf-8")
    (args.output / "compile.stderr.log").write_text(compile_run.stderr, encoding="utf-8")
    (args.output / "simulation.log").write_text(simulation_text, encoding="utf-8")
    report = {"schema_version": "openroad-aes-functional-report-v1", "repository": "OpenROAD-flow-scripts", "repository_revision": revision, "status": status, "compile_returncode": compile_run.returncode, "simulation_returncode": simulate.returncode if simulate else None, "claim_boundary": "one AES-128 known-answer vector; not exhaustive cryptographic verification or physical signoff"}
    report["report_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    path = args.output / "openroad-aes-functional-report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "repository_revision": revision, "report": str(path)}, sort_keys=True))
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
