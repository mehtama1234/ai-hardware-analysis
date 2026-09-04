#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-differential-matching-requirement.json"
OUT_MD = EVIDENCE / "sky130-differential-matching-requirement.md"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def fmt(value: float) -> str:
    return f"{value:.9e}"


def main() -> int:
    target = load("sky130-sample-hold-design-target.json")
    control = load("differential-sampling-control-proof-ngspice.json")
    plain_differential = load("sky130-fully-differential-sampling-ngspice.json")
    half_lsb = target["half_lsb_12b_v"]
    best_error = target["best_measured_hold_error_v"]
    reference_error = plain_differential["worst_diff_hold_abs_delta_v"]
    best_common_mv = reference_error * 1000.0
    best_measured_mv = best_error * 1000.0
    max_mismatch_mv = half_lsb * 1000.0
    allowed_mismatch_fraction_of_reference = half_lsb / reference_error
    required_common_rejection_fraction = max(0.0, 1.0 - allowed_mismatch_fraction_of_reference)
    best_margin_x = half_lsb / best_error
    mismatch_case = next(row for row in control["rows"] if row["mismatch_injection_mv"] > 0)
    measured_mismatch_mv = mismatch_case["diff_hold_abs_delta_v"] * 1000.0
    measured_mismatch_over_limit_x = mismatch_case["diff_hold_abs_delta_v"] / half_lsb

    report = {
        "result_type": "sky130_differential_matching_requirement",
        "status": "sky130_differential_matching_requirement_defined_not_converter_proof",
        "half_lsb_12b_v": half_lsb,
        "best_measured_hold_error_v": best_error,
        "best_measured_hold_error_mv": best_measured_mv,
        "reference_uncancelled_differential_error_v": reference_error,
        "reference_uncancelled_differential_error_mv": best_common_mv,
        "max_allowed_differential_mismatch_v": half_lsb,
        "max_allowed_differential_mismatch_mv": max_mismatch_mv,
        "best_measured_margin_x": best_margin_x,
        "allowed_mismatch_fraction_of_reference_error": allowed_mismatch_fraction_of_reference,
        "allowed_mismatch_percent_of_reference_error": 100.0 * allowed_mismatch_fraction_of_reference,
        "required_common_rejection_fraction": required_common_rejection_fraction,
        "required_common_rejection_percent": 100.0 * required_common_rejection_fraction,
        "control_mismatch_case_mismatch_mv": mismatch_case["mismatch_injection_mv"],
        "control_mismatch_case_diff_error_v": mismatch_case["diff_hold_abs_delta_v"],
        "control_mismatch_case_over_limit_x": measured_mismatch_over_limit_x,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "converts the measured hold-error target and differential control proof into a matching requirement for the next sample-hold circuit",
            "not_allowed": "does not prove Sky130 transistor matching, comparator offset, noise, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Sky130 Differential Matching Requirement",
        "",
        f"- status: `{report['status']}`",
        f"- best measured hold error V: `{fmt(best_error)}`",
        f"- best measured margin x: `{best_margin_x:.3f}`",
        f"- reference uncancelled differential error V: `{fmt(reference_error)}`",
        f"- 12-bit half LSB V: `{fmt(half_lsb)}`",
        f"- max allowed differential mismatch mV: `{max_mismatch_mv:.4f}`",
        f"- allowed mismatch percent of reference error: `{100.0 * allowed_mismatch_fraction_of_reference:.2f}`",
        f"- required common rejection percent: `{100.0 * required_common_rejection_fraction:.2f}`",
        f"- control mismatch case over limit x: `{measured_mismatch_over_limit_x:.3f}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "Differential sampling helps only when the unwanted charge is almost the same on both sides. The shared part disappears from the decision voltage. The unmatched part remains.",
        "",
        "The uncancelled differential fixture moves by millivolts. The 12-bit limit is about 0.2197 mV. The new differential dummy case is below that line in one measured mid-input case, which means the next question is no longer only size. It is whether the cancellation survives input range, device mismatch, noise, and layout parasitics.",
        "",
        "Said another way, if the physical circuit produces a disturbance about as large as the uncancelled differential fixture, the two sides must leave less than the half-LSB line in the decision voltage. The passing dummy row has margin in nominal simulation, but mismatch can spend that margin quickly.",
        "",
        "## Numeric Target",
        "",
        "| quantity | value | meaning |",
        "|---|---:|---|",
        f"| uncancelled differential movement | `{best_common_mv:.4f} mV` | size of the disturbance before dummy cancellation |",
        f"| best measured dummy-cancelled movement | `{best_measured_mv:.4f} mV` | current best nominal decision-voltage movement |",
        f"| max allowed remaining mismatch | `{max_mismatch_mv:.4f} mV` | largest differential error allowed by the 12-bit line |",
        f"| best measured margin | `{best_margin_x:.4f}` | half-LSB line divided by the best measured movement |",
        f"| allowed mismatch fraction | `{allowed_mismatch_fraction_of_reference:.4f}` | remaining mismatch divided by uncancelled movement |",
        f"| required common rejection | `{required_common_rejection_fraction:.4f}` | common movement that must disappear from the decision |",
        "",
        "## Design Consequence",
        "",
        "The next transistor fixture should not only report node movement. It must report matched movement. If both held nodes move by millivolts but their difference moves by less than 0.2197 mV, differential sampling is doing the job. If their difference moves more than that, the circuit still fails even if it looks symmetric on paper.",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("sky130_differential_matching_requirement")
    print(f"status,{report['status']}")
    print(f"max_allowed_differential_mismatch_mv,{max_mismatch_mv:.4f}")
    print(f"required_common_rejection_percent,{100.0 * required_common_rejection_fraction:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
