#!/usr/bin/env python3
"""Run the selected coupled PMOS-only SAR fixture at required PVT corners."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from run_sky130_coupled_dac_comparator_bit import run_trial


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-coupled-physical-sar-pvt.json"
OUT_MD = EVIDENCE / "sky130-coupled-physical-sar-pvt.md"
SOURCE_V = 0.004
REFERENCE_V = 0.604
CODES = (0, 2, 4, 6, 7)
CORNERS = (
    {"name": "tt_25c_1p80v", "section": "tt", "temperature_c": 25.0, "supply_v": 1.8},
    {"name": "ss_minus20c_1p62v", "section": "ss", "temperature_c": -20.0, "supply_v": 1.62},
    {"name": "ff_85c_1p98v", "section": "ff", "temperature_c": 85.0, "supply_v": 1.98},
    {"name": "sf_25c_1p80v", "section": "sf", "temperature_c": 25.0, "supply_v": 1.8},
    {"name": "fs_25c_1p80v", "section": "fs", "temperature_c": 25.0, "supply_v": 1.8},
)


def run_case(corner: dict[str, Any], code: int) -> dict[str, Any]:
    names = ("AIMC_COUPLED_MODEL_SECTION", "AIMC_COUPLED_TEMPERATURE_C", "AIMC_COUPLED_SUPPLY_V")
    previous = {name: os.environ.get(name) for name in names}
    os.environ.update({
        "AIMC_COUPLED_MODEL_SECTION": corner["section"],
        "AIMC_COUPLED_TEMPERATURE_C": str(corner["temperature_c"]),
        "AIMC_COUPLED_SUPPLY_V": str(corner["supply_v"]),
    })
    try:
        row = run_trial(code, SOURCE_V, REFERENCE_V)
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
    row.update({"corner": corner["name"], "model_section": corner["section"], "temperature_c": corner["temperature_c"], "supply_v": corner["supply_v"]})
    return row


def main() -> int:
    os.environ.setdefault("AIMC_COUPLED_DAC_ACQ", "long")
    os.environ.setdefault("AIMC_COUPLED_BOTTOM_PMOS_ONLY", "1")
    rows = []
    for corner in CORNERS:
        for code in CODES:
            print(f"corner {corner['name']} code {code}", flush=True)
            rows.append(run_case(corner, code))
    measured = [row for row in rows if row.get("measured")]
    by_corner = {corner["name"]: [row for row in measured if row["corner"] == corner["name"]] for corner in CORNERS}
    corner_summaries = {}
    for corner in CORNERS:
        corner_rows = by_corner[corner["name"]]
        values = [row["dac_top_after_v"] for row in corner_rows]
        corner_summaries[corner["name"]] = {
            "measured_count": len(corner_rows),
            "code_count": len(CODES),
            "correct_polarity_count": sum(row.get("correct_polarity", False) for row in corner_rows),
            "top_plate_min_v": min(values) if values else None,
            "top_plate_max_v": max(values) if values else None,
            "minimum_sampled_spacing_v": min(b - a for a, b in zip(values, values[1:])) if len(values) > 1 else None,
        }
    report = {
        "result_type": "sky130_coupled_physical_sar_pvt",
        "status": "same_topology_representative_pvt_characterized_not_full_pvt_sar_proof",
        "topology": "pmos_only_to_vdd",
        "source_v": SOURCE_V,
        "reference_v": REFERENCE_V,
        "codes": list(CODES),
        "corner_count": len(CORNERS),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(row.get("timed_out", False) for row in rows),
        "correct_polarity_count": sum(row.get("correct_polarity", False) for row in measured),
        "corner_summaries": corner_summaries,
        "rows": rows,
        "claim_boundary": {
            "allowed": "same PMOS-only coupled DAC/comparator fixture is characterized at the five required Sky130 model and temperature/supply corners for five representative codes",
            "not_allowed": "does not prove all-code calibration at every corner, mismatch/noise yield, continuous multicycle SAR, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Coupled Physical SAR PVT", "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- representative codes: `{CODES}`",
        f"- measured cases: `{report['measured_case_count']}` of `{report['case_count']}`",
        f"- timed out cases: `{report['timed_out_case_count']}`",
        f"- correct comparator polarities: `{report['correct_polarity_count']}` of `{report['measured_case_count']}`", "",
        "| corner | measured | polarity | top-plate range V | minimum sampled spacing V |", "| --- | ---: | ---: | ---: | ---: |",
    ]
    for corner in CORNERS:
        summary = corner_summaries[corner["name"]]
        value_range = "n/a" if summary["top_plate_min_v"] is None else f"{summary['top_plate_min_v']:.6f}..{summary['top_plate_max_v']:.6f}"
        spacing = "n/a" if summary["minimum_sampled_spacing_v"] is None else f"{summary['minimum_sampled_spacing_v']:.6f}"
        lines.append(f"| `{corner['name']}` | `{summary['measured_count']}/{len(CODES)}` | `{summary['correct_polarity_count']}/{summary['measured_count']}` | `{value_range}` | `{spacing}` |")
    lines += ["", "This is the first PVT artifact tied to the selected coupled PMOS-only topology. It is deliberately bounded to representative codes: the full 16-code calibration and five-code nominal SAR result remain separate artifacts, and mismatch/noise and continuous-SAR gates are still open.", "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{report['measured_case_count']}/{report['case_count']}")
    print(f"correct_polarity,{report['correct_polarity_count']}")
    print(f"json,{OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
