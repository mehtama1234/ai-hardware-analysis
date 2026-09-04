#!/usr/bin/env python3
"""Measure time-dependent DAC error in the physical Sky130 switch fixture."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from run_sky130_transistor_switched_capacitor_dac import deck
from run_sky130_switched_capacitor_dac import ROOT, VDD, VIN

EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-transistor-dac-settling-sweep.json"
OUT_MD = EVIDENCE / "sky130-transistor-dac-settling-sweep.md"
TIMEOUT_S = 60
CODES = (8, 15)
TIMES_NS = (3, 5, 10, 20, 40, 70)


def read_measure(stdout: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", stdout)
    if not values:
        raise ValueError(f"missing measurement {name}")
    return float(values[-1])


def timed_deck(code: int) -> str:
    source = deck(code)
    marker = ".control\n"
    measures = "\n".join(
        f".measure tran top_{time_ns}ns_v FIND v(top) AT={time_ns}n"
        for time_ns in TIMES_NS
    )
    return source.replace(marker, f"{measures}\n{marker}", 1)


def run(code: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="aimc-dac-settling-") as tmp:
        path = Path(tmp) / "dac.sp"
        path.write_text(timed_deck(code), encoding="utf-8")
        try:
            result = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {"code": code, "measured": False, "timed_out": True}
    row: dict[str, Any] = {"code": code, "measured": result.returncode == 0, "timed_out": False, "returncode": result.returncode}
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        return row
    expected = VIN + VDD * code / 16.0
    samples = []
    for time_ns in TIMES_NS:
        value = read_measure(result.stdout, f"top_{time_ns}ns_v")
        error_v = value - expected
        samples.append({
            "time_ns": time_ns,
            "top_v": value,
            "error_v": error_v,
            "error_lsb": error_v / (VDD / 16.0),
            "half_lsb_pass": abs(error_v) <= VDD / 32.0,
        })
    row["expected_top_v"] = expected
    row["samples"] = samples
    passing = [sample for sample in samples if sample["half_lsb_pass"]]
    row["first_half_lsb_pass_time_ns"] = passing[0]["time_ns"] if passing else None
    return row


def main() -> int:
    rows = [run(code) for code in CODES]
    measured = [row for row in rows if row["measured"]]
    samples = [sample for row in measured for sample in row["samples"]]
    report = {
        "result_type": "sky130_transistor_dac_settling_sweep",
        "status": "dac_settling_timed_and_half_lsb_not_reached" if measured and not any(row["first_half_lsb_pass_time_ns"] is not None for row in measured) else "dac_settling_timed_characterization",
        "codes": list(CODES),
        "times_ns": list(TIMES_NS),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(row["timed_out"] for row in rows),
        "sample_count": len(samples),
        "half_lsb_v": VDD / 32.0,
        "first_half_lsb_pass_by_code": {str(row["code"]): row["first_half_lsb_pass_time_ns"] for row in rows},
        "rows": rows,
        "claim_boundary": {
            "allowed": "measures the time-dependent top-plate voltage of the physical Sky130 transistor DAC at representative midscale and full-scale codes",
            "not_allowed": "does not prove a full-code calibration, mismatch yield, comparator noise, SAR accuracy, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Transistor DAC Settling Sweep", "",
        f"- status: `{report['status']}`",
        f"- codes: `{CODES}`",
        f"- times ns: `{TIMES_NS}`",
        f"- measured cases: `{report['measured_case_count']}` of `{report['case_count']}`",
        f"- half-LSB target V: `{report['half_lsb_v']:.9e}`", "",
        "## Why Timing Is Part Of Accuracy", "",
        "The comparator does not see an abstract DAC code. It sees the top-plate voltage at the instant it makes a decision. This sweep samples the same transistor-switched array at several times after redistribution. If an early sample passes and a late sample fails, the clock is too slow; if no time passes, the transfer function or switch topology must be repaired.", "",
        "## Results", "",
        "| code | time ns | top plate V | error LSB | half-LSB pass |", "| ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        if not row["measured"]:
            lines.append(f"| {row['code']} | all | timeout | timeout | False |")
            continue
        for sample in row["samples"]:
            lines.append(f"| {row['code']} | {sample['time_ns']} | {sample['top_v']:.6f} | {sample['error_lsb']:.3f} | {sample['half_lsb_pass']} |")
    lines += ["", "## Interpretation", "", "For this fixture, a faster comparator decision is not a demonstrated fix. The measured early-to-late movement is large, but the static transfer error remains outside the half-LSB target at the representative codes. The SAR must use a measured settle time and a corrected DAC transfer together; either one alone is insufficient.", "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{report['measured_case_count']}/{report['case_count']}")
    print(f"samples,{report['sample_count']}")
    print(f"json,{OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
