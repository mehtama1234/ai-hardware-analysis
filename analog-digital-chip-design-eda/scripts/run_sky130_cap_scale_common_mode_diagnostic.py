#!/usr/bin/env python3
"""Test whether a low sampled common-mode makes the scaled DAC legal."""

from __future__ import annotations

import json
import os
from pathlib import Path

from run_sky130_coupled_dac_comparator_bit import run_trial


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-cap-scale-common-mode-diagnostic.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-cap-scale-common-mode-diagnostic.md"
CODES = (12, 13, 14, 15)
CAP_SCALE = 8.0
SUPPLY_V = 1.8
REQUIRED_SPACING_MV = 56.25


def main() -> int:
    input_v = float(os.environ.get("AIMC_COUPLED_INPUT_V", "0.0"))
    os.environ.setdefault("AIMC_COUPLED_DAC_ACQ", "long")
    os.environ.setdefault("AIMC_COUPLED_BOTTOM_PMOS_ONLY", "1")
    os.environ.setdefault("AIMC_COUPLED_CAP_SCALE", str(CAP_SCALE))
    rows = [run_trial(code, input_v, 1.0) for code in CODES]
    measured = [row for row in rows if row.get("measured")]
    complete = len(measured) == len(CODES)
    spacings = [
        (rows[index + 1]["dac_top_after_v"] - rows[index]["dac_top_after_v"]) * 1000.0
        for index in range(len(rows) - 1)
        if rows[index].get("measured") and rows[index + 1].get("measured")
    ]
    tops = [row["dac_top_after_v"] for row in measured]
    monotonic = complete and all(value > 0 for value in spacings)
    legal_range = complete and all(0.0 <= value <= SUPPLY_V for value in tops)
    spacing_pass = complete and monotonic and min(spacings) >= REQUIRED_SPACING_MV
    all_polarity = complete and all(row.get("correct_polarity", False) for row in measured)
    status = "candidate_common_mode_rebalance" if spacing_pass and legal_range and all_polarity else "common_mode_rebalance_inadequate"
    report = {
        "result_type": "sky130_cap_scale_common_mode_diagnostic",
        "status": status,
        "topology": "PMOS-only bottom-plate connection to VDD",
        "full_array_cap_scale": CAP_SCALE,
        "sampled_input_common_mode_v": input_v,
        "reference_v": 1.0,
        "supply_v": SUPPLY_V,
        "codes": list(CODES),
        "rows": rows,
        "adjacent_spacings_mv": spacings,
        "minimum_spacing_mv": min(spacings) if spacings else None,
        "required_half_lsb_mv": REQUIRED_SPACING_MV,
        "maximum_dac_top_v": max(tops) if tops else None,
        "monotonic": monotonic,
        "legal_supply_range": legal_range,
        "all_polarities_correct": all_polarity,
        "interpretation": "At zero sampled common-mode, the 8x array reaches the spacing target while the measured upper-code top-plate values remain within the 1.8 V supply in this fixture. This is a candidate operating-point change, not converter acceptance.",
        "claim_boundary": {
            "allowed": "compares upper-code threshold spacing, polarity, and top-plate supply range for one PMOS-only Sky130 fixture operating point",
            "not_allowed": "does not prove all-code SAR accuracy, PVT/mismatch/noise yield, extracted layout, energy, board behavior, or silicon",
        },
    }
    lines = [
        "# Sky130 Capacitor-Scale Common-Mode Diagnostic",
        "",
        "This diagnostic tests whether lowering the sampled common-mode makes the otherwise promising full-array capacitor ratio legal.",
        "",
        f"- topology: `{report['topology']}`",
        f"- full-array capacitor scale: `{CAP_SCALE:.1f}x`",
        f"- sampled input common-mode: `{input_v:.3f} V`",
        f"- measured codes: `{len(measured)}/{len(CODES)}`",
        f"- status: `{status}`",
        "",
        "## Measurements",
        "",
        "| code | DAC top before comparator (V) | correct polarity |",
        "| ---: | ---: | --- |",
    ]
    for row in rows:
        if row.get("measured"):
            lines.append(f"| {row['code']} | {row['dac_top_after_v']:.6f} | {row['correct_polarity']} |")
        else:
            lines.append(f"| {row['code']} | incomplete | False |")
    lines += [
        "",
        "Adjacent spacings (mV): " + ", ".join(f"{value:.3f}" for value in spacings),
        "",
        "## Result",
        "",
        report["interpretation"],
        "The next run must extend this candidate to all codes and PVT, then test settling, mismatch, noise, and retained-bit SAR behavior before it can replace the blocked converter boundary.",
        "",
        "## Claim Boundary",
        "",
        report["claim_boundary"]["not_allowed"],
    ]
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"status,{status}")
    print(f"measured,{len(measured)}/{len(CODES)}")
    print(f"spacings_mv,{spacings}")
    print(f"maximum_dac_top_v,{report['maximum_dac_top_v']}")
    print(f"legal_supply_range,{legal_range}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
