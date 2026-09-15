#!/usr/bin/env python3
"""Capture host conditions before interpreting slow ngspice evidence."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "aimc-simulator-adapters" / "simulation-host-preflight.json"


def main() -> int:
    load = [float(value) for value in Path("/proc/loadavg").read_text().split()[:3]]
    cpu_count = os.cpu_count() or 1
    simulators = subprocess.run(["ps", "-eo", "cmd"], capture_output=True, text=True, check=False).stdout.splitlines()
    active = [line.strip() for line in simulators if any(token in line for token in ("ngspice", "vvp", "iverilog", "pytest"))]
    report = {
        "result_type": "simulation_host_preflight",
        "status": "host_contended" if load[0] > cpu_count else "host_available",
        "load_average_1m_5m_15m": load,
        "cpu_count": cpu_count,
        "load_ratio_1m": load[0] / cpu_count,
        "active_simulation_or_test_processes": len(active),
        "process_excerpt": active[:20],
        "claim_boundary": "Host scheduling diagnostic only; does not qualify or disqualify any circuit result.",
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"], f"load_ratio_1m={report['load_ratio_1m']:.2f}", f"active={len(active)}")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
