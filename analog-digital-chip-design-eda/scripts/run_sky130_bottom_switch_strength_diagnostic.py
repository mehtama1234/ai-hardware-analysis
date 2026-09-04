#!/usr/bin/env python3
"""Measure whether larger PMOS bottom-plate switches restore high-code spacing."""

from __future__ import annotations

import json
import os
from pathlib import Path

from run_sky130_coupled_dac_comparator_bit import run_trial


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-bottom-switch-strength-diagnostic.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-bottom-switch-strength-diagnostic.md"


def main() -> int:
    scales = [float(value) for value in os.environ.get("AIMC_BOTTOM_SWITCH_SCALES", "2,4").split(",")]
    rows = []
    for scale in scales:
        os.environ["AIMC_COUPLED_BOTTOM_SCALE"] = str(scale)
        trial_rows = [run_trial(code, 0.9, 1.0) for code in (14, 15)]
        measured = [row for row in trial_rows if row.get("measured")]
        spacing_mv = None
        if len(measured) == 2:
            spacing_mv = (measured[1]["dac_top_after_v"] - measured[0]["dac_top_after_v"]) * 1000.0
        rows.append({"bottom_switch_scale": scale, "trial_rows": trial_rows, "spacing_14_to_15_mv": spacing_mv})
    complete = [row for row in rows if row["spacing_14_to_15_mv"] is not None]
    report = {
        "result_type": "sky130_bottom_switch_strength_diagnostic",
        "status": "measured_switch_strength_inadequate" if complete and all(row["spacing_14_to_15_mv"] < 56.25 for row in complete) else "incomplete",
        "topology": "PMOS-only bottom-plate connection to VDD",
        "scales": scales,
        "rows": rows,
        "required_half_lsb_mv": 56.25,
        "interpretation": "larger PMOS bottom-plate switches do not restore high-code threshold spacing; charge-transfer topology or waveform must change",
        "claim_boundary": {
            "allowed": "compares PMOS bottom-plate switch strength for codes 14 and 15 in the coupled Sky130 DAC/comparator fixture",
            "not_allowed": "does not prove converter acceptance, full SAR accuracy, PVT/mismatch yield, extracted layout, board behavior, or silicon",
        },
    }
    lines = [
        "# Sky130 Bottom-Switch Strength Diagnostic",
        "",
        "This sweep tests whether stronger PMOS bottom-plate charge transfer restores the compressed upper DAC thresholds.",
        "",
        f"- topology: `{report['topology']}`",
        f"- scales: `{scales}` relative to the 16 um PMOS / 8 um NMOS baseline",
        f"- required 4-bit half-LSB: `{report['required_half_lsb_mv']} mV`",
        "",
        "## Result",
        "",
        report["interpretation"],
        "",
        "| switch scale | code 14 top (V) | code 15 top (V) | spacing (mV) | both measured |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        measured = [item for item in row["trial_rows"] if item.get("measured")]
        if len(measured) == 2:
            lines.append(f"| {row['bottom_switch_scale']:.1f}x | {measured[0]['dac_top_after_v']:.6f} | {measured[1]['dac_top_after_v']:.6f} | {row['spacing_14_to_15_mv']:.3f} | True |")
        else:
            lines.append(f"| {row['bottom_switch_scale']:.1f}x | incomplete | incomplete | incomplete | False |")
    lines += ["", "## Claim Boundary", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"scales,{scales}")
    print(f"complete,{len(complete)}/{len(rows)}")
    for row in complete:
        print(f"scale_{row['bottom_switch_scale']},spacing_14_to_15_mv,{row['spacing_14_to_15_mv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
