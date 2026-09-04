#!/usr/bin/env python3
"""Analyze deterministic code calibration for the measured transistor DAC."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-switched-capacitor-dac.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-dac-calibration-analysis.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-dac-calibration-analysis.md"


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = [row for row in source["rows"] if row.get("measured")]
    rows.sort(key=lambda row: row["code"])
    full_scale_lsb = 1.8 / 16.0
    points = []
    for row in rows:
        ideal = float(row["expected_top_v"])
        measured = float(row["top_settled_v"])
        points.append({
            "code": row["code"],
            "measured_v": measured,
            "ideal_v": ideal,
            "error_v": measured - ideal,
            "error_lsb": (measured - ideal) / full_scale_lsb,
        })
    monotonic = all(a["measured_v"] <= b["measured_v"] for a, b in zip(points, points[1:]))
    report = {
        "result_type": "sky130_transistor_dac_calibration_analysis",
        "status": "monotonic_lut_candidate_not_calibration_proof" if monotonic else "non_monotonic_lut_rejected",
        "source": str(SOURCE.relative_to(ROOT)),
        "measured_code_count": len(points),
        "declared_code_count": source["code_count"],
        "monotonic": monotonic,
        "ideal_lsb_v": full_scale_lsb,
        "maximum_absolute_error_lsb": max((abs(point["error_lsb"]) for point in points), default=None),
        "points": points,
        "calibration_decision": "deterministic LUT is a possible future correction, but not eligible for acceptance until all codes and PVT/mismatch stability are measured" if monotonic else "do not calibrate; repair the DAC topology first",
        "claim_boundary": {
            "allowed": "quantifies deterministic code error and checks whether the measured code ordering could support a future lookup-table correction",
            "not_allowed": "does not prove calibration repeatability, missing-code behavior, PVT stability, mismatch/noise yield, SAR accuracy, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Transistor DAC Calibration Analysis", "",
        f"- status: `{report['status']}`",
        f"- measured codes: `{report['measured_code_count']}` of `{report['declared_code_count']}`",
        f"- measured ordering monotonic: `{monotonic}`",
        f"- ideal code step V: `{full_scale_lsb:.9e}`",
        f"- maximum absolute error LSB: `{report['maximum_absolute_error_lsb']:.4f}`" if points else "- maximum absolute error LSB: not measured", "",
        "## First-Principles Reading", "",
        "Calibration can remove a repeatable code-to-voltage error. It cannot repair a missing code, a non-monotonic transfer, or an error that changes with supply, temperature, mismatch, noise, or aging. The first question is therefore ordering; the second is repeatability; only then does a lookup table become meaningful.", "",
        f"The measured points are monotonic, so a deterministic lookup table is a possible future correction. The largest measured error is still several LSBs, and only {report['measured_code_count']} of {report['declared_code_count']} codes are present in the source run. No calibration claim is accepted yet.", "",
        "## Refused Claim", "",
        report["claim_boundary"]["not_allowed"], "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured_code_count,{report['measured_code_count']}")
    print(f"maximum_absolute_error_lsb,{report['maximum_absolute_error_lsb']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
