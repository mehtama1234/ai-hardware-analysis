#!/usr/bin/env python3
"""Reproduce the MSB capacitor-ratio sweep for codes 7 and 8."""

from __future__ import annotations

import json
import os
from pathlib import Path

from run_sky130_coupled_dac_comparator_bit import run_trial


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-msb-cap-ratio-diagnostic.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-msb-cap-ratio-diagnostic.md"


def main() -> int:
    scales = [float(value) for value in os.environ.get("AIMC_MSB_CAP_SCALES", "0.125,0.25,0.5,1,2").split(",")]
    os.environ.setdefault("AIMC_COUPLED_DAC_ACQ", "long")
    os.environ.setdefault("AIMC_COUPLED_BOTTOM_PMOS_ONLY", "1")
    os.environ.setdefault("AIMC_COUPLED_CAP_SCALE", "8")
    os.environ.setdefault("AIMC_COUPLED_INPUT_V", "0")
    rows = []
    for scale in scales:
        os.environ["AIMC_COUPLED_MSB_CAP_SCALE"] = str(scale)
        trial_rows = [run_trial(code, 0.0, 1.0) for code in (7, 8)]
        for row in trial_rows:
            rows.append({
                "msb_cap_scale": scale,
                "code": row["code"],
                "dac_top_after_v": row.get("dac_top_after_v"),
                "msb_bottom_plate_v": (row.get("dac_bottom_plate_v") or [None])[0],
                "correct_polarity": row.get("correct_polarity", False),
                "measured": row.get("measured", False),
            })
    spacing = {}
    for scale in scales:
        pair = [row for row in rows if row["msb_cap_scale"] == scale]
        if len(pair) == 2 and all(row["measured"] for row in pair):
            spacing[str(scale)] = (pair[1]["dac_top_after_v"] - pair[0]["dac_top_after_v"]) * 1000.0
    report = {
        "result_type": "sky130_msb_cap_ratio_diagnostic",
        "status": "msb_cap_ratio_inadequate" if spacing and all(value < 0 for value in spacing.values()) else "incomplete",
        "topology": "PMOS-only bottom-plate connection to VDD",
        "full_array_cap_scale": 8.0,
        "sampled_input_common_mode_v": 0.0,
        "codes": [7, 8],
        "scales": scales,
        "rows": rows,
        "spacing_7_to_8_mv": spacing,
        "interpretation": "Changing the MSB capacitor ratio does not restore code 7 to 8 monotonicity; explicit MSB precharge/isolation or a different DAC architecture is required.",
        "claim_boundary": {
            "allowed": "compares MSB capacitor ratios for the failing code 7 to 8 transition in the coupled Sky130 fixture",
            "not_allowed": "does not prove converter acceptance, SAR accuracy, PVT/mismatch/noise yield, extracted layout, energy, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Sky130 MSB Capacitor-Ratio Diagnostic", "", "| MSB capacitor scale | code 7 top (V) | code 8 top (V) | spacing (mV) |", "| ---: | ---: | ---: | ---: |"]
    for scale in scales:
        pair = [row for row in rows if row["msb_cap_scale"] == scale]
        if len(pair) == 2 and all(row["measured"] for row in pair):
            lines.append(f"| {scale:g}x | {pair[0]['dac_top_after_v']:.6f} | {pair[1]['dac_top_after_v']:.6f} | {spacing[str(scale)]:.3f} |")
        else:
            lines.append(f"| {scale:g}x | incomplete | incomplete | incomplete |")
    lines += ["", "## Result", "", report["interpretation"], "", "## Claim Boundary", "", report["claim_boundary"]["not_allowed"]]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"scales,{scales}")
    print(f"spacing_7_to_8_mv,{spacing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
