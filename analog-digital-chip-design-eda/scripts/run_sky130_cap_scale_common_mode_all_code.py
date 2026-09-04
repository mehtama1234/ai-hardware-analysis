#!/usr/bin/env python3
"""Measure all DAC codes for the scaled-array, low-common-mode candidate."""

from __future__ import annotations

import json
import os
from pathlib import Path

from run_sky130_coupled_dac_comparator_bit import run_trial


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-cap-scale-common-mode-all-code.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-cap-scale-common-mode-all-code.md"
CODES = tuple(range(16))
SUPPLY_V = 1.8


def main() -> int:
    input_v = float(os.environ.get("AIMC_COUPLED_INPUT_V", "0.0"))
    cap_scale = float(os.environ.get("AIMC_COUPLED_CAP_SCALE", "8.0"))
    os.environ.setdefault("AIMC_COUPLED_DAC_ACQ", "long")
    os.environ.setdefault("AIMC_COUPLED_BOTTOM_PMOS_ONLY", "1")
    os.environ["AIMC_COUPLED_CAP_SCALE"] = str(cap_scale)
    rows = [run_trial(code, input_v, 1.0) for code in CODES]
    measured = [row for row in rows if row.get("measured")]
    complete = len(measured) == len(CODES)
    values = [row["dac_top_after_v"] for row in rows]
    spacings = [(values[index + 1] - values[index]) * 1000.0 for index in range(len(values) - 1)] if complete else []
    monotonic = complete and all(value > 0.0 for value in spacings)
    legal_range = complete and all(0.0 <= value <= SUPPLY_V for value in values)
    half_lsb_mv = (SUPPLY_V / 16.0) * 1000.0 / 2.0
    spacing_pass = complete and monotonic and min(spacings) >= half_lsb_mv
    all_polarity = complete and all(row.get("correct_polarity", False) for row in measured)
    status = "all_code_candidate" if spacing_pass and legal_range and all_polarity else "all_code_candidate_rejected"
    report = {
        "result_type": "sky130_cap_scale_common_mode_all_code",
        "status": status,
        "topology": "PMOS-only bottom-plate connection to VDD",
        "full_array_cap_scale": cap_scale,
        "sampled_input_common_mode_v": input_v,
        "reference_v": 1.0,
        "supply_v": SUPPLY_V,
        "codes": list(CODES),
        "rows": rows,
        "adjacent_spacings_mv": spacings,
        "minimum_spacing_mv": min(spacings) if spacings else None,
        "required_half_lsb_mv": half_lsb_mv,
        "maximum_dac_top_v": max(values) if complete else None,
        "monotonic": monotonic,
        "legal_supply_range": legal_range,
        "all_polarities_correct": all_polarity,
        "interpretation": "The scaled-array, zero-common-mode candidate is rejected by the all-code threshold test because the transfer is non-monotonic and leaves the legal supply range. The focused high-code result was not sufficient. SAR sequence, PVT, mismatch, noise, settling, energy, extraction, and model-level converter closure remain open.",
        "claim_boundary": {
            "allowed": "measures all 16 requested upper/lower codes, threshold ordering, comparator polarity, and top-plate supply range in one nominal Sky130 coupled fixture",
            "not_allowed": "does not prove SAR accuracy, PVT/mismatch/noise yield, extracted layout, energy, board behavior, silicon, or model replacement readiness",
        },
    }
    lines = [
        "# Sky130 Capacitor-Scale Common-Mode All-Code Diagnostic",
        "",
        "This is the all-code follow-up to the focused zero-common-mode diagnostic.",
        "",
        f"- topology: `{report['topology']}`",
        f"- full-array capacitor scale: `{cap_scale:.1f}x`",
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
        "",
        "## Claim Boundary",
        "",
        report["claim_boundary"]["not_allowed"],
    ]
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"status,{status}")
    print(f"measured,{len(measured)}/{len(CODES)}")
    print(f"minimum_spacing_mv,{report['minimum_spacing_mv']}")
    print(f"maximum_dac_top_v,{report['maximum_dac_top_v']}")
    print(f"legal_supply_range,{legal_range}")
    print(f"all_polarities_correct,{all_polarity}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
