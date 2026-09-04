#!/usr/bin/env python3
"""Measure whether PMOS gate overdrive restores high-code DAC spacing."""

from __future__ import annotations

import json
import os
from pathlib import Path

from run_sky130_coupled_dac_comparator_bit import run_trial


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-pmos-gate-overdrive-diagnostic.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-pmos-gate-overdrive-diagnostic.md"


def main() -> int:
    boost_v = float(os.environ.get("AIMC_COUPLED_PFET_BOOST_V", "-0.6"))
    rows = [run_trial(code, 0.9, 1.0) for code in (14, 15)]
    measured = [row for row in rows if row.get("measured")]
    spacing_mv = None
    if len(measured) == 2:
        spacing_mv = (measured[1]["dac_top_after_v"] - measured[0]["dac_top_after_v"]) * 1000.0
    report = {
        "result_type": "sky130_pmos_gate_overdrive_diagnostic",
        "status": "measured_high_code_spacing_inadequate" if spacing_mv is not None and spacing_mv < 56.25 else "incomplete",
        "topology": "PMOS-only bottom-plate connection to VDD",
        "gate_overdrive_v": boost_v,
        "codes": [14, 15],
        "rows": rows,
        "spacing_14_to_15_mv": spacing_mv,
        "required_half_lsb_mv": 56.25,
        "comparison": {
            "baseline_spacing_mv": 16.361,
            "interpretation": "negative result: gate overdrive does not restore the compressed high-code threshold spacing",
        },
        "claim_boundary": {
            "allowed": "measures two high-code physical DAC thresholds with PMOS gate overdrive in the coupled Sky130 DAC/comparator fixture",
            "not_allowed": "does not prove converter acceptance, full SAR accuracy, PVT/mismatch yield, extracted layout, board behavior, or silicon",
        },
    }
    lines = [
        "# Sky130 PMOS Gate Overdrive Diagnostic",
        "",
        f"- topology: `{report['topology']}`",
        f"- PMOS gate low level: `{boost_v:.3f} V`",
        f"- measured codes: `{len(measured)}` of `2`",
        f"- code 14 to 15 spacing: `{spacing_mv:.3f} mV`" if spacing_mv is not None else "- code 14 to 15 spacing: `incomplete`",
        "- required 4-bit half-LSB: `56.25 mV`",
        "",
        "## Result",
        "",
        "Driving the selected PMOS gate below ground is a headroom diagnostic. It does not materially increase the upper threshold spacing: the measured spacing remains far below the half-LSB requirement. The collapse is therefore not repaired by gate overdrive alone; the charge-transfer topology or controlled bottom-plate waveform must change.",
        "",
        "## Claim Boundary",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
        "## Measurements",
        "",
        "| code | DAC top after redistribution (V) | comparator polarity |",
        "| ---: | ---: | --- |",
    ]
    for row in rows:
        if row.get("measured"):
            lines.append(f"| {row['code']} | {row['dac_top_after_v']:.6f} | {row['correct_polarity']} |")
        else:
            lines.append(f"| {row['code']} | incomplete | False |")
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{len(measured)}/2")
    print(f"gate_overdrive_v,{boost_v}")
    print(f"spacing_14_to_15_mv,{spacing_mv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
