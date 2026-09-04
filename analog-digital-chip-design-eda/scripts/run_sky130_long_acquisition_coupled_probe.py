#!/usr/bin/env python3
"""Record a representative coupled DAC probe with a longer source-acquisition phase."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ["AIMC_COUPLED_DAC_ACQ"] = "long"
from run_sky130_coupled_dac_comparator_bit import run_trial  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-long-acquisition-coupled-probe.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-long-acquisition-coupled-probe.md"


def main() -> int:
    rows = [run_trial(code, 1.2, 1.5) for code in (7, 15)]
    measured = [row for row in rows if row.get("measured")]
    report = {
        "result_type": "sky130_long_acquisition_coupled_probe",
        "status": "long_acquisition_coupled_probe_characterized" if len(measured) == len(rows) else "long_acquisition_coupled_probe_incomplete",
        "codes": [7, 15],
        "source_switch_width_um": {"nfet": 32.0, "pfet": 64.0},
        "source_acquisition_end_ns": 4.0,
        "bottom_plate_transition_ns": 5.0,
        "comparator_sampling_ns": "9.1-9.6",
        "preamp_enable_ns": 9.7,
        "latch_ns": 11.7,
        "rows": rows,
        "claim_boundary": {
            "allowed": "measures two representative codes through the longer-acquisition physical DAC, transistor comparator, preamp, and latch path",
            "not_allowed": "does not prove all DAC codes, full SAR accuracy, calibration, mismatch/noise yield, PVT behavior, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Long-Acquisition Coupled Probe", "",
        f"- status: `{report['status']}`",
        "- codes: `7, 15`",
        "- source switch sizing: `32 um NMOS / 64 um PMOS`",
        "- source acquisition ends: `4.0 ns`",
        "- bottom-plate transition: `5.0 ns`",
        "- comparator sampling: `9.1-9.6 ns`",
        "- preamp enabled: `9.7 ns`",
        "- latch: `11.7 ns`", "",
        "This probe carries the larger source switch and longer acquisition phase from the isolated `8 pF` loading test into the coupled physical DAC/comparator transient. It is a timing and interface probe, not a complete converter result.", "",
        "| code | DAC top after V | DAC-reference diff V | preamp diff V | output diff V | correct polarity |", "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        if row.get("measured"):
            lines.append(f"| {row['code']} | {row['dac_top_after_v']:.6f} | {row['dac_to_reference_diff_v']:.6f} | {row['preamp_diff_before_latch_v']:.6f} | {row['output_diff_v']:.6f} | {row['correct_polarity']} |")
        else:
            lines.append(f"| {row['code']} | timeout/error | timeout/error | timeout/error | timeout/error | False |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{len(measured)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
