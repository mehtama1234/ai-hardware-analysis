#!/usr/bin/env python3
"""Run structural LVS on one extracted one-device preamp cell."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--netlist", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--cell", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    device_lines = [
        line for line in args.netlist.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().lower().startswith("c")
    ]
    devices = out / "devices.spice"
    devices.write_text("\n".join(device_lines) + "\n", encoding="utf-8")
    log = out / "netgen.log"
    command = [
        "/home/mehtama1/eda-tools/netgen-1.5/bin/netgen", "-batch", "lvs",
        f"{devices} {args.cell}", f"{args.reference.resolve()} {args.cell}",
        "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/netgen/sky130A_setup.tcl",
        str(log),
    ]
    proc = subprocess.run(command, cwd=out, capture_output=True, text=True, timeout=90)
    log_text = log.read_text(encoding="utf-8") if log.is_file() else proc.stdout + proc.stderr
    passed = proc.returncode == 0 and "Final result: Circuits match uniquely." in log_text
    result = {
        "status": "passed" if passed else "failed",
        "matched_uniquely": passed,
        "cell": args.cell,
        "extracted_netlist": str(args.netlist.resolve()),
        "command": command,
        "claim_boundary": "One extracted transistor cell only; this does not qualify parent routing or converter behavior.",
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
