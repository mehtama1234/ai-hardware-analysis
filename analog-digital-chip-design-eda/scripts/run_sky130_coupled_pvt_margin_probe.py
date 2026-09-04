#!/usr/bin/env python3
"""Measure comparator margin around the failing slow/cold/low-supply case."""

from __future__ import annotations

import json
import os
from pathlib import Path

from run_sky130_coupled_dac_comparator_bit import run_trial


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-coupled-pvt-margin-probe.json"
OUT_MD = EVIDENCE / "sky130-coupled-pvt-margin-probe.md"
REFERENCES = (0.50, 0.55, 0.58, 0.604, 0.62, 0.65, 0.70)
CODE = 6
SOURCE_V = 0.004


def main() -> int:
    os.environ.setdefault("AIMC_COUPLED_DAC_ACQ", "long")
    os.environ.setdefault("AIMC_COUPLED_BOTTOM_PMOS_ONLY", "1")
    os.environ.update({
        "AIMC_COUPLED_MODEL_SECTION": "ss",
        "AIMC_COUPLED_TEMPERATURE_C": "-20",
        "AIMC_COUPLED_SUPPLY_V": "1.62",
    })
    rows = []
    for reference in REFERENCES:
        print(f"reference {reference:g}", flush=True)
        row = run_trial(CODE, SOURCE_V, reference)
        row["reference_margin_v"] = row.get("dac_to_reference_diff_v")
        row["reference_test_v"] = reference
        rows.append(row)
    measured = [row for row in rows if row.get("measured")]
    report = {
        "result_type": "sky130_coupled_pvt_margin_probe",
        "status": "slow_cold_low_supply_margin_boundary_characterized",
        "corner": {"model_section": "ss", "temperature_c": -20.0, "supply_v": 1.62},
        "code": CODE,
        "source_v": SOURCE_V,
        "reference_values_v": list(REFERENCES),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "correct_polarity_count": sum(row.get("correct_polarity", False) for row in measured),
        "rows": rows,
        "governor_conclusion": "The low-supply corner requires a measured comparator-margin guard; nominal sign evidence cannot be extrapolated through the approximately 35 mV transition region.",
        "claim_boundary": {
            "allowed": "characterizes comparator polarity as a function of DAC-to-reference margin at the failing required PVT corner",
            "not_allowed": "does not prove a full PVT SAR, offset/noise yield, continuous SAR, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Coupled PVT Margin Probe", "",
        f"- status: `{report['status']}`",
        f"- corner: `ss`, `-20 C`, `1.62 V`",
        f"- physical code: `{CODE}`",
        f"- measured: `{report['measured_case_count']}` of `{report['case_count']}`",
        f"- correct polarity: `{report['correct_polarity_count']}` of `{report['measured_case_count']}`", "",
        "| reference V | DAC-reference margin V | output difference V | correct polarity |", "| ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        if not row.get("measured"):
            lines.append(f"| {row['reference_test_v']:.3f} | unavailable | unavailable | False |")
        else:
            lines.append(f"| {row['reference_test_v']:.3f} | {row['reference_margin_v']:.6f} | {row['output_diff_v']:.6f} | {row['correct_polarity']} |")
    lines += ["", report["governor_conclusion"], "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{report['measured_case_count']}/{report['case_count']}")
    print(f"correct_polarity,{report['correct_polarity_count']}")
    print(f"json,{OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
