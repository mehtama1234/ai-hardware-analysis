#!/usr/bin/env python3
"""Sweep comparator sample capacitance without changing the canonical run."""

from __future__ import annotations

import json
import os
from pathlib import Path

from run_sky130_coupled_dac_comparator_bit import run_trial

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-coupled-sample-cap-sweep.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-coupled-sample-cap-sweep.md"
VALUES = ("0.2p", "0.02p", "0.002p")
CODES = (14, 15)


def main() -> int:
    rows = []
    for value in VALUES:
        os.environ["AIMC_COUPLED_CSTORE"] = value
        for code in CODES:
            result = run_trial(code, 0.9, 1.0)
            rows.append({"cstore": value, "code": code, **result})
    report = {
        "result_type": "sky130_coupled_sample_cap_sweep",
        "status": "coupled_sample_capacitance_sweep_characterized_not_final_sizing",
        "values": list(VALUES),
        "codes": list(CODES),
        "rows": rows,
        "claim_boundary": {
            "allowed": "compares controlled comparator sample-capacitance values while retaining the physical DAC, switches, late timing, and transistor comparator",
            "not_allowed": "does not prove optimal sizing, full SAR accuracy, mismatch/noise yield, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Coupled Comparator Sample-Capacitance Sweep", "",
        "This sweep varies only the comparator sample capacitance while keeping the physical DAC, transistor switches, and late sampling schedule fixed. It tests whether DAC loading and decision resolution trade against each other.", "",
        "| sample capacitance | code | DAC top V | DAC-reference diff V | preamp diff V | measured |", "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        if row.get("measured"):
            lines.append(f"| {row['cstore']} | {row['code']} | {row['dac_top_after_v']:.6f} | {row['dac_to_reference_diff_v']:.6f} | {row['preamp_diff_before_latch_v']:.6f} | True |")
        else:
            lines.append(f"| {row['cstore']} | {row['code']} | timeout/error | timeout/error | timeout/error | False |")
    lines += ["", "## Interpretation", "", "The result is not monotonic with capacitance. A smaller sample capacitor reduces direct charge sharing but also changes the transient settling and the amount of charge available to the comparator input storage. The value must therefore be selected with a full timing, code, PVT, mismatch, and noise sweep rather than by one full-scale number.", "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"rows,{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
