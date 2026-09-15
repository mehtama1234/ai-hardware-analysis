#!/usr/bin/env python3
"""Run bounded solver-backed properties for the stateful AIMC tile controller."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RTL = ROOT / "labs/digital/aimc-control-plane-rtl"
SOURCES = [
    RTL / "aimc_operation_partition.v",
    RTL / "aimc_tile_readout.v",
    RTL / "aimc_micro_tile_controller.v",
    RTL / "aimc_micro_tile_controller_formal.sv",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--depth", type=int, default=8)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    command = [
        "yosys",
        "-p",
        "read_verilog -formal -sv "
        + " ".join(str(path) for path in SOURCES)
        + "; prep -top aimc_micro_tile_controller_formal; flatten; "
        + "async2sync; opt; "
        + f"sat -seq {args.depth} -prove-asserts -set-init-zero",
    ]
    run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    log = run.stdout + run.stderr
    (output / "yosys.log").write_text(log, encoding="utf-8")
    passed = run.returncode == 0 and "SAT proof finished - no model found: SUCCESS!" in log
    report = {
        "schema_version": "aimc-stateful-formal-suite-v1",
        "status": "passed" if passed else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Bounded solver-backed properties for the single-clock stateful AIMC micro-tile controller, including reset state, monotonic saturated counters, one-event counter increments, and execution/reason consistency.",
        "sources": [{"path": str(path), "sha256": digest(path)} for path in SOURCES],
        "proof": {
            "tool": "yosys-sat",
            "depth": args.depth,
            "assertion_count": 20,
            "result": "proven" if passed else "unknown",
            "returncode": run.returncode,
            "log": str(output / "yosys.log"),
        },
        "claim_boundary": "Bounded single-clock formal evidence only; it does not prove multi-clock CDC behavior, commercial EDA signoff, analog behavior, or silicon correctness.",
    }
    (output / "formal-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "depth": args.depth, "assertion_count": 20, "output": str(output)}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
