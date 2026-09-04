#!/usr/bin/env python3
"""Measure full-array capacitor scaling as a charge-transfer diagnostic."""

from __future__ import annotations

import json
import os
from pathlib import Path

from run_sky130_coupled_dac_comparator_bit import run_trial


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-full-array-cap-scale-diagnostic.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-full-array-cap-scale-diagnostic.md"
CODE_LIST = (12, 13, 14, 15)
REQUIRED_SPACING_MV = 56.25
SUPPLY_V = 1.8


def main() -> int:
    cap_scale = float(os.environ.get("AIMC_COUPLED_CAP_SCALE", "8.0"))
    os.environ.setdefault("AIMC_COUPLED_DAC_ACQ", "long")
    os.environ.setdefault("AIMC_COUPLED_BOTTOM_PMOS_ONLY", "1")
    rows = [run_trial(code, 0.9, 1.0) for code in CODE_LIST]
    measured = [row for row in rows if row.get("measured")]
    values = [row["dac_top_after_v"] for row in rows if row.get("measured")]
    spacings = [
        (rows[index + 1]["dac_top_after_v"] - rows[index]["dac_top_after_v"]) * 1000.0
        for index in range(len(rows) - 1)
        if rows[index].get("measured") and rows[index + 1].get("measured")
    ]
    complete = len(measured) == len(CODE_LIST)
    monotonic = complete and all(spacing > 0 for spacing in spacings)
    spacing_pass = complete and monotonic and min(spacings) >= REQUIRED_SPACING_MV
    supply_violation = bool(values) and max(values) > SUPPLY_V
    if not complete:
        status = "incomplete"
    elif spacing_pass and supply_violation:
        status = "measured_spacing_pass_but_supply_violation"
    elif spacing_pass:
        status = "candidate_charge_transfer_topology"
    else:
        status = "measured_cap_scale_inadequate"
    report = {
        "result_type": "sky130_full_array_cap_scale_diagnostic",
        "status": status,
        "topology": "PMOS-only bottom-plate connection to VDD",
        "cap_scale": cap_scale,
        "codes": list(CODE_LIST),
        "rows": rows,
        "adjacent_spacings_mv": spacings,
        "minimum_spacing_mv": min(spacings) if spacings else None,
        "required_half_lsb_mv": REQUIRED_SPACING_MV,
        "maximum_dac_top_v": max(values) if values else None,
        "supply_v": SUPPLY_V,
        "monotonic": monotonic,
        "supply_violation": supply_violation,
        "interpretation": "Full-array scaling restores monotonic upper-code spacing only by driving the DAC top plate above the 1.8 V supply in this fixture; it is a diagnostic, not an acceptable cell.",
        "claim_boundary": {
            "allowed": "compares full-array capacitor scaling for upper DAC codes in the coupled Sky130 DAC/comparator fixture",
            "not_allowed": "does not prove converter acceptance, SAR accuracy, PVT/mismatch/noise yield, extracted layout, board behavior, or silicon",
        },
    }
    lines = [
        "# Sky130 Full-Array Capacitor-Scale Diagnostic",
        "",
        "This diagnostic tests whether scaling the complete binary capacitor array restores the compressed upper thresholds.",
        "",
        f"- topology: `{report['topology']}`",
        f"- full-array capacitor scale: `{cap_scale:.1f}x`",
        f"- measured codes: `{len(measured)}/{len(CODE_LIST)}`",
        f"- required 4-bit half-LSB: `{REQUIRED_SPACING_MV:.2f} mV`",
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
        "The next design must rebalance the charge-transfer network so the required spacing is obtained within the legal supply range.",
        "",
        "## Claim Boundary",
        "",
        report["claim_boundary"]["not_allowed"],
    ]
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"status,{status}")
    print(f"measured,{len(measured)}/{len(CODE_LIST)}")
    print(f"spacings_mv,{spacings}")
    print(f"maximum_dac_top_v,{report['maximum_dac_top_v']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
