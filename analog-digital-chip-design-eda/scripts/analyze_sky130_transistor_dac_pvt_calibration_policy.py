#!/usr/bin/env python3
"""Turn representative transistor-DAC measurements into an explicit policy."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-dac-pvt-codes.json"
OUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-dac-pvt-calibration-policy.json"
REPORT = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-dac-pvt-calibration-policy.md"


def main() -> int:
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = source["rows"]
    corners = sorted({row["corner"] for row in rows})
    policies = []
    for corner in corners:
        measured = [row for row in rows if row["corner"] == corner and row.get("measured")]
        by_code = {int(row["code"]): row for row in measured}
        missing = [code for code in (0, 8, 15) if code not in by_code]
        endpoint_calibration = None
        corrected_mid_error_lsb = None
        reasons = []
        if missing:
            reasons.append("required_calibration_code_missing")
        else:
            low = by_code[0]["top_settled_v"]
            high = by_code[15]["top_settled_v"]
            ideal_low = by_code[0]["expected_top_v"]
            ideal_high = by_code[15]["expected_top_v"]
            corrected_mid = ideal_low + (by_code[8]["top_settled_v"] - low) * (ideal_high - ideal_low) / (high - low)
            corrected_mid_error_lsb = (corrected_mid - by_code[8]["expected_top_v"]) / by_code[8]["half_lsb_v"]
            endpoint_calibration = {
                "code_0_measured_v": low,
                "code_15_measured_v": high,
                "code_0_gain_offset_reference_v": ideal_low,
                "code_15_gain_offset_reference_v": ideal_high,
                "code_8_corrected_v": corrected_mid,
            }
            if abs(corrected_mid_error_lsb) > 0.5:
                reasons.append("endpoint_calibration_does_not_fix_midscale")
        if not all(row.get("measured") and row.get("half_lsb_pass") for row in measured):
            reasons.append("measured_code_outside_half_lsb")
        if len(measured) < source["code_count_per_corner"]:
            reasons.append("corner_timeout_or_incomplete")
        accepted = not reasons
        policies.append({
            "corner": corner,
            "measured_code_count": len(measured),
            "required_codes": [0, 8, 15],
            "missing_required_codes": missing,
            "endpoint_calibration": endpoint_calibration,
            "corrected_midscale_error_lsb": corrected_mid_error_lsb,
            "calibration_valid_for_analog_sar": accepted,
            "decision": "analog_service" if accepted else "digital_fallback",
            "reasons": reasons,
        })
    analog_count = sum(row["calibration_valid_for_analog_sar"] for row in policies)
    result = {
        "result_type": "sky130_transistor_dac_pvt_calibration_policy",
        "status": "pvt_calibration_rejected_digital_fallback_required" if analog_count == 0 else "pvt_calibration_partially_accepted",
        "source_artifact": str(INPUT.relative_to(ROOT)),
        "corner_count": len(policies),
        "analog_service_count": analog_count,
        "digital_fallback_count": len(policies) - analog_count,
        "policies": policies,
        "claim_boundary": {
            "allowed": "proves that measured DAC evidence is converted into a conservative per-corner analog-or-digital decision",
            "not_allowed": "does not prove a valid calibration table, mismatch yield, noise, SAR accuracy, extracted layout, board behavior, or silicon",
        },
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Transistor DAC PVT Calibration Policy",
        "",
        "This is the controller-facing answer to a practical question: can measured DAC codes be corrected well enough to let the analog SAR use them at a given operating point?",
        "",
        "## Rule",
        "",
        "A corner may request analog SAR service only when codes 0, 8, and 15 are measured, every measured code is within half an LSB, and an endpoint gain/offset correction leaves code 8 within half an LSB. Otherwise the controller must use digital fallback or keep the analog path in bring-up mode.",
        "",
        "## Results",
        "",
        "| corner | measured | endpoint-corrected code 8 error | decision | reason |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for row in policies:
        error = "missing" if row["corrected_midscale_error_lsb"] is None else f"{row['corrected_midscale_error_lsb']:.3f} LSB"
        lines.append(f"| {row['corner']} | {row['measured_code_count']} | {error} | {row['decision']} | {', '.join(row['reasons'])} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "The nominal and slow corners have enough measurements to test endpoint correction, but the midscale residual remains several half-LSBs. This means the DAC is not behaving like a simple shifted and scaled ideal DAC; the switch resistance, charge injection, capacitor ratios, settling, and operating point interact. A two-point calibration would hide the internal shape error rather than remove it.",
        "",
        "The fast/hot/high-supply corner also has a timeout at code 0. A timeout is a functional failure for a converter policy, even if other codes complete. The current safe policy is therefore digital fallback for all representative corners.",
        "",
        "## Next Measurement",
        "",
        "Measure all 16 codes repeatedly at every corner, then add capacitor mismatch, switch mismatch, comparator noise, reference loading, and SAR closed-loop conversions. Only a calibration model that passes those distributions should be allowed to replace this fallback decision.",
        "",
        "This policy is evidence about the boundary and its control response. It is not silicon, board, or tapeout evidence.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{result['status']}")
    print(f"corners,{len(policies)}")
    print(f"analog_service,{analog_count}")
    print(f"digital_fallback,{len(policies) - analog_count}")
    print(f"json,{OUT}")
    print(f"markdown,{REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
