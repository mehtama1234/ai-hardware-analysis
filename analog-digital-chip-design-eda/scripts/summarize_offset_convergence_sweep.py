#!/usr/bin/env python3
"""Summarize numerical convergence experiments for the offset fixture."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
NAMES = ("gear_gmin1e-6", "trap_gmin1e-6", "gear_gmin1e-8", "positive_uic", "positive_step100")
OUT = EVIDENCE / "sky130-two-phase-offset-convergence-sweep.json"


def main() -> int:
    experiments = []
    for name in NAMES:
        path = EVIDENCE / f"{name}.json"
        if not path.exists():
            continue
        report = json.loads(path.read_text(encoding="utf-8"))
        experiments.append({
            "artifact": str(path.relative_to(ROOT)),
            "status": report.get("status"),
            "cases": report.get("case_count"),
            "measured_cases": report.get("measured_case_count"),
            "timeouts": report.get("timed_out_case_count"),
        })
    result = {
        "result_type": "sky130_two_phase_offset_convergence_sweep",
        "status": "all_tested_numerical_configs_timeout_positive_or_zero_case",
        "experiments": experiments,
        "claim_boundary": "Records convergence behavior only; does not establish a circuit performance or converter claim.",
        "next_action": "Reduce or re-bias the latch-free deck and capture a successful operating-point transient before noise analysis.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    print(f"experiments,{len(experiments)}")
    print(f"json,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
