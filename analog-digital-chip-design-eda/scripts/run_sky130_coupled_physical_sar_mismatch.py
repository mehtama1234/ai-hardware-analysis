#!/usr/bin/env python3
"""Run controlled mismatch cases on the selected coupled PMOS-only fixture."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from run_sky130_coupled_dac_comparator_bit import run_trial


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-coupled-physical-sar-mismatch.json"
OUT_MD = EVIDENCE / "sky130-coupled-physical-sar-mismatch.md"
SOURCE_V = 0.004
REFERENCE_V = 0.604
CODES = (0, 2, 4, 6, 7)
CASES = (
    {"name": "matched_nominal", "msb_cap_scale": 1.0, "lsb_cap_scale": 1.0, "bottom_scale": 1.0},
    {"name": "msb_plus_2pct", "msb_cap_scale": 1.02, "lsb_cap_scale": 1.0, "bottom_scale": 1.0},
    {"name": "lsb_minus_2pct", "msb_cap_scale": 1.0, "lsb_cap_scale": 0.98, "bottom_scale": 1.0},
    {"name": "switch_minus_10pct", "msb_cap_scale": 1.0, "lsb_cap_scale": 1.0, "bottom_scale": 0.9},
)
SCALE_ENV = {
    "msb_cap_scale": "AIMC_COUPLED_MSB_CAP_SCALE",
    "lsb_cap_scale": "AIMC_COUPLED_LSB_SCALE",
    "bottom_scale": "AIMC_COUPLED_BOTTOM_SCALE",
}


def run_case(case: dict[str, Any], code: int) -> dict[str, Any]:
    names = tuple(SCALE_ENV.values())
    previous = {name: os.environ.get(name) for name in names}
    os.environ.update({SCALE_ENV[key]: str(case[key]) for key in SCALE_ENV})
    try:
        row = run_trial(code, SOURCE_V, REFERENCE_V)
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
    row.update({"mismatch_case": case["name"], "msb_cap_scale": case["msb_cap_scale"], "lsb_cap_scale": case["lsb_cap_scale"], "bottom_scale": case["bottom_scale"]})
    return row


def main() -> int:
    os.environ.setdefault("AIMC_COUPLED_DAC_ACQ", "long")
    os.environ.setdefault("AIMC_COUPLED_BOTTOM_PMOS_ONLY", "1")
    rows = []
    for case in CASES:
        for code in CODES:
            print(f"case {case['name']} code {code}", flush=True)
            rows.append(run_case(case, code))
    measured = [row for row in rows if row.get("measured")]
    summaries = {}
    for case in CASES:
        case_rows = [row for row in measured if row["mismatch_case"] == case["name"]]
        values = [row["dac_top_after_v"] for row in case_rows]
        summaries[case["name"]] = {
            "measured_count": len(case_rows),
            "code_count": len(CODES),
            "correct_polarity_count": sum(row.get("correct_polarity", False) for row in case_rows),
            "top_plate_min_v": min(values) if values else None,
            "top_plate_max_v": max(values) if values else None,
            "minimum_sampled_spacing_v": min(b - a for a, b in zip(values, values[1:])) if len(values) > 1 else None,
        }
    report = {
        "result_type": "sky130_coupled_physical_sar_mismatch",
        "status": "same_topology_controlled_mismatch_characterized_not_statistical_yield_proof",
        "topology": "pmos_only_to_vdd",
        "source_v": SOURCE_V,
        "reference_v": REFERENCE_V,
        "codes": list(CODES),
        "case_count": len(rows),
        "mismatch_case_count": len(CASES),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(row.get("timed_out", False) for row in rows),
        "correct_polarity_count": sum(row.get("correct_polarity", False) for row in measured),
        "case_summaries": summaries,
        "rows": rows,
        "claim_boundary": {
            "allowed": "characterizes four controlled capacitor and bottom-switch perturbations on the same coupled PMOS-only fixture at five representative codes",
            "not_allowed": "does not prove random mismatch yield, 100-trial acceptance, noise, PVT closure, continuous SAR, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Coupled Physical SAR Mismatch", "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- representative codes: `{CODES}`",
        f"- measured cases: `{report['measured_case_count']}` of `{report['case_count']}`",
        f"- timed out cases: `{report['timed_out_case_count']}`",
        f"- correct comparator polarities: `{report['correct_polarity_count']}` of `{report['measured_case_count']}`", "",
        "| mismatch case | measured | polarity | top-plate range V | minimum sampled spacing V |", "| --- | ---: | ---: | ---: | ---: |",
    ]
    for case in CASES:
        summary = summaries[case["name"]]
        value_range = "n/a" if summary["top_plate_min_v"] is None else f"{summary['top_plate_min_v']:.6f}..{summary['top_plate_max_v']:.6f}"
        spacing = "n/a" if summary["minimum_sampled_spacing_v"] is None else f"{summary['minimum_sampled_spacing_v']:.6f}"
        lines.append(f"| `{case['name']}` | `{summary['measured_count']}/{len(CODES)}` | `{summary['correct_polarity_count']}/{summary['measured_count']}` | `{value_range}` | `{spacing}` |")
    lines += ["", "This controlled sweep tests sensitivity of the selected topology. It is not a substitute for the 100-trial mismatch requirement in the acceptance contract; those trials must eventually run through calibrated SAR decisions, not only one-cycle polarity checks.", "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{report['measured_case_count']}/{report['case_count']}")
    print(f"correct_polarity,{report['correct_polarity_count']}")
    print(f"json,{OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
