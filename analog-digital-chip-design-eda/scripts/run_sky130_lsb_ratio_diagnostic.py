#!/usr/bin/env python3
"""Test whether changing the physical LSB capacitor restores DAC spacing."""

from __future__ import annotations

import json
import os
from pathlib import Path

from run_sky130_coupled_dac_comparator_bit import run_trial


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-lsb-ratio-diagnostic.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-lsb-ratio-diagnostic.md"


def main() -> int:
    lsb_scale = float(os.environ.get("AIMC_COUPLED_LSB_SCALE", "4.0"))
    os.environ["AIMC_COUPLED_LSB_SCALE"] = str(lsb_scale)
    rows = [run_trial(code, 0.9, 1.0) for code in (12, 13, 14, 15)]
    measured = [row for row in rows if row.get("measured")]
    spacings_mv = []
    if len(measured) == 4:
        spacings_mv = [(measured[idx + 1]["dac_top_after_v"] - measured[idx]["dac_top_after_v"]) * 1000 for idx in range(3)]
    monotonic = bool(spacings_mv) and all(value > 0 for value in spacings_mv)
    report = {
        "result_type": "sky130_lsb_ratio_diagnostic",
        "status": "measured_lsb_ratio_non_monotonic" if len(measured) == 4 and not monotonic else "incomplete",
        "topology": "PMOS-only bottom-plate connection to VDD",
        "lsb_capacitor_scale": lsb_scale,
        "codes": [12, 13, 14, 15],
        "rows": rows,
        "spacing_12_to_13_14_to_15_mv": spacings_mv,
        "monotonic": monotonic,
        "required_high_code_spacing_mv": 56.25,
        "interpretation": "isolated LSB enlargement changes the transfer non-monotonically; the capacitor network must be rebalanced as a complete topology",
        "claim_boundary": {
            "allowed": "measures an LSB capacitor ratio candidate in the coupled Sky130 DAC/comparator fixture",
            "not_allowed": "does not prove converter acceptance, full SAR accuracy, PVT/mismatch yield, extracted layout, board behavior, or silicon",
        },
    }
    lines = [
        "# Sky130 LSB Ratio Diagnostic",
        "",
        "This run changes the LSB capacitor while keeping the PMOS-only switch topology and timing fixed.",
        "",
        f"- LSB capacitor scale: `{lsb_scale:.1f}x`",
        f"- measured codes: `{len(measured)}` of `4`",
        f"- adjacent spacings mV: `{[round(value, 3) for value in spacings_mv]}`",
        f"- monotonic: `{monotonic}`",
        "- required half-LSB: `56.25 mV`",
        "",
        "## Result",
        "",
        report["interpretation"],
        "",
        "| code | DAC top after redistribution (V) | comparator polarity |",
        "| ---: | ---: | --- |",
    ]
    for row in rows:
        if row.get("measured"):
            lines.append(f"| {row['code']} | {row['dac_top_after_v']:.6f} | {row['correct_polarity']} |")
        else:
            lines.append(f"| {row['code']} | incomplete | False |")
    lines += ["", "## Claim Boundary", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{len(measured)}/4")
    print(f"lsb_scale,{lsb_scale}")
    print(f"spacings_mv,{spacings_mv}")
    print(f"monotonic,{monotonic}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
