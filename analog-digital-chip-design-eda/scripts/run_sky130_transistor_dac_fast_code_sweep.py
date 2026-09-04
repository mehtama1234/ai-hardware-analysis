#!/usr/bin/env python3
"""Characterize every physical DAC code at a comparator-relevant time window."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from run_sky130_transistor_switched_capacitor_dac import CODES, deck, measure
from run_sky130_switched_capacitor_dac import ROOT, VDD, VIN

EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-transistor-dac-fast-code-sweep.json"
OUT_MD = EVIDENCE / "sky130-transistor-dac-fast-code-sweep.md"
TIMEOUT_S = 45
DECISION_NS = 10.0


def timed_deck(code: int) -> str:
    source = deck(code)
    source = source.replace(".tran 10p 80n", ".tran 10p 15n")
    source = source.replace("70.0n", f"{DECISION_NS:.1f}n")
    return source


def run(code: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="aimc-dac-fast-sweep-") as tmp:
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
    value = measure(result.stdout, "top_settled_v")
    expected = VIN + VDD * code / 16.0
    row.update({
        "decision_time_ns": DECISION_NS,
        "top_at_decision_v": value,
        "expected_top_v": expected,
        "error_v": value - expected,
        "error_lsb": (value - expected) / (VDD / 16.0),
        "half_lsb_pass": abs(value - expected) <= VDD / 32.0,
        "bottom_plate_v": [measure(result.stdout, f"b{bit}_settled_v") for bit in range(4)],
    })
    return row


def main() -> int:
    rows = [run(code) for code in CODES]
    measured = [row for row in rows if row["measured"]]
    complete = len(measured) == len(CODES)
    pass_count = sum(row.get("half_lsb_pass", False) for row in measured)
    report = {
        "result_type": "sky130_transistor_dac_fast_code_sweep",
        "status": "fast_code_window_characterized_not_full_accuracy_proof" if complete else "fast_code_window_incomplete",
        "code_count": len(CODES),
        "measured_code_count": len(measured),
        "timed_out_code_count": sum(row.get("timed_out", False) for row in rows),
        "decision_time_ns": DECISION_NS,
        "half_lsb_v": VDD / 32.0,
        "half_lsb_pass_count": pass_count,
        "measured_code_order_monotonic": complete and all(a["top_at_decision_v"] <= b["top_at_decision_v"] for a, b in zip(measured, measured[1:])),
        "rows": rows,
        "claim_boundary": {
            "allowed": "measures all physical Sky130 transistor DAC codes at a defined early decision window",
            "not_allowed": "does not prove long-time settling, calibration, mismatch/noise yield, SAR accuracy, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Transistor DAC Fast Code Sweep", "",
        f"- status: `{report['status']}`",
        f"- decision time: `{DECISION_NS:g} ns`",
        f"- codes measured: `{len(measured)}` of `{len(CODES)}`",
        f"- half-LSB passes: `{pass_count}` of `{len(CODES)}`",
        f"- monotonic at decision time: `{report['measured_code_order_monotonic']}`", "",
        "## Why This Run Exists", "",
        "The long-settle experiment is useful for exposing drift, but it is not the instant at which a SAR comparator necessarily makes its decision. This run measures every physical code at a fixed early window so the code-to-threshold map can be judged at the same time boundary used by the coupled comparator.", "",
        "## Results", "",
        "| code | top plate V | error LSB | half-LSB pass |", "| ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        if row.get("measured"):
            lines.append(f"| {row['code']} | {row['top_at_decision_v']:.6f} | {row['error_lsb']:.3f} | {row['half_lsb_pass']} |")
        else:
            lines.append(f"| {row['code']} | timeout/error | timeout/error | False |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{len(measured)}/{len(CODES)}")
    print(f"half_lsb_pass,{pass_count}/{len(CODES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
