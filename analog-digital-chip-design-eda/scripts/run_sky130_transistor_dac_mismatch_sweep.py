#!/usr/bin/env python3
"""Measure controlled capacitor-ratio mismatch in the Sky130 transistor DAC."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from run_sky130_switched_capacitor_dac import CAPS_F, ROOT, VDD, VIN, measure

EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
OUT_JSON = EVIDENCE / "sky130-transistor-dac-mismatch-sweep.json"
OUT_MD = EVIDENCE / "sky130-transistor-dac-mismatch-sweep.md"
TIMEOUT_S = 60
CODES = (0, 8, 15)


@dataclass(frozen=True)
class Case:
    name: str
    scales: tuple[float, float, float, float]


CASES = (
    Case("matched_nominal", (1.0, 1.0, 1.0, 1.0)),
    Case("msb_plus_2pct", (1.02, 1.0, 1.0, 1.0)),
    Case("lsb_minus_2pct", (1.0, 1.0, 1.0, 0.98)),
    Case("alternating_plus_minus_2pct", (1.02, 0.98, 1.02, 0.98)),
)


def deck(case: Case, code: int) -> str:
    caps = []
    controls = []
    switches = []
    for bit, (cap, scale) in enumerate(zip(CAPS_F, case.scales)):
        selected = (code >> (3 - bit)) & 1
        caps.append(f"C{bit} top b{bit} {cap * scale:.12e}")
        caps.append(f"CDUMMY{bit} b{bit} 0 0.01e-12")
        if selected:
            controls.extend([
                f"VGP{bit} gp{bit} 0 PULSE(1.8 0 1n 10p 10p 200n 1u)",
                f"VGN{bit} gn{bit} 0 PULSE(1.8 0 1n 10p 10p 200n 1u)",
            ])
            switches.extend([
                f"XBP{bit} b{bit} gp{bit} vdd vdd sky130_fd_pr__pfet_01v8 W=16.0 L=0.15",
                f"XBN{bit} b{bit} gn{bit} 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15",
            ])
        else:
            controls.extend([f"VGP{bit} gp{bit} 0 1.8", f"VGN{bit} gn{bit} 0 1.8"])
            switches.append(f"XBN{bit} b{bit} gn{bit} 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15")
    return f'''* Sky130 transistor-switched DAC capacitor mismatch sweep.
.lib "{PDK_LIB}" tt
.param vdd=1.8
.param vin=0.9
VDD vdd 0 {{vdd}}
VIN vin 0 {{vin}}
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.1n 10p 10p 0.9n 1u)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.1n 10p 10p 0.9n 1u)
VSS vss 0 0
XSN vin ctrl top vss sky130_fd_pr__nfet_01v8 W=2.0 L=0.15
XSP vin ctrlb top vdd sky130_fd_pr__pfet_01v8 W=4.0 L=0.15
{chr(10).join(caps)}
{chr(10).join(switches)}
{chr(10).join(controls)}
.ic v(top)={VIN} v(b0)=0 v(b1)=0 v(b2)=0 v(b3)=0
.tran 10p 80n uic
.measure tran top_early_v FIND v(top) AT=3.0n
.measure tran top_settled_v FIND v(top) AT=70.0n
.measure tran b0_settled_v FIND v(b0) AT=70.0n
.measure tran b1_settled_v FIND v(b1) AT=70.0n
.measure tran b2_settled_v FIND v(b2) AT=70.0n
.measure tran b3_settled_v FIND v(b3) AT=70.0n
.control
run
.endc
.end
'''


def run(case: Case, code: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="aimc-dac-mismatch-") as tmp:
        path = Path(tmp) / "dac.sp"
        path.write_text(deck(case, code), encoding="utf-8")
        try:
            result = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {"case": case.name, "code": code, "measured": False, "timed_out": True, "scales": list(case.scales)}
    row: dict[str, Any] = {"case": case.name, "code": code, "measured": result.returncode == 0, "timed_out": False, "scales": list(case.scales), "returncode": result.returncode}
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        return row
    settled = measure(result.stdout, "top_settled_v")
    expected = VIN + VDD * code / 16.0
    row.update({
        "top_early_v": measure(result.stdout, "top_early_v"),
        "top_settled_v": settled,
        "expected_top_v": expected,
        "early_to_late_delta_v": abs(settled - measure(result.stdout, "top_early_v")),
        "error_v": settled - expected,
        "error_lsb": (settled - expected) / (VDD / 16.0),
        "half_lsb_pass": abs(settled - expected) <= VDD / 32.0,
        "bottom_plate_v": [measure(result.stdout, f"b{bit}_settled_v") for bit in range(4)],
    })
    return row


def main() -> int:
    rows = [run(case, code) for case in CASES for code in CODES]
    measured = [row for row in rows if row["measured"]]
    by_case = {
        case.name: [row for row in measured if row["case"] == case.name]
        for case in CASES
    }
    monotonic_cases = sum(
        bool(case_rows) and all(a["top_settled_v"] <= b["top_settled_v"] for a, b in zip(case_rows, case_rows[1:]))
        for case_rows in by_case.values()
    )
    report = {
        "result_type": "sky130_transistor_dac_mismatch_sweep",
        "status": "dac_mismatch_characterized_not_yield_or_sar_proof",
        "pdk_model_library": str(PDK_LIB),
        "case_count": len(CASES),
        "code_count_per_case": len(CODES),
        "total_case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(row["timed_out"] for row in rows),
        "half_lsb_v": VDD / 32.0,
        "half_lsb_pass_count": sum(row.get("half_lsb_pass", False) for row in measured),
        "monotonic_case_count": monotonic_cases,
        "rows": rows,
        "claim_boundary": {
            "allowed": "measures controlled capacitor-ratio perturbations in the physical Sky130 transistor DAC at low, middle, and high codes, including early-to-late settling",
            "not_allowed": "does not prove random mismatch yield, calibration validity, comparator noise, SAR accuracy, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Transistor DAC Mismatch Sweep", "",
        f"- status: `{report['status']}`",
        f"- cases: `{report['case_count']}` with codes `{CODES}`",
        f"- measured: `{report['measured_case_count']}` of `{report['total_case_count']}`",
        f"- timed out: `{report['timed_out_case_count']}`",
        f"- half-LSB passes: `{report['half_lsb_pass_count']}` of `{report['total_case_count']}`",
        f"- monotonic cases: `{report['monotonic_case_count']}` of `{report['case_count']}`", "",
        "## What This Tests", "",
        "The nominal DAC already has transfer error. This run changes one or more capacitor values by a controlled two percent and repeats low, middle, and high codes. It keeps the transistor switches, clocks, and 70 ns read point the same, so the result exposes how sensitive the threshold is to capacitor-ratio error.", "",
        "The early-to-late number is also retained. A large change means the comparator timing is part of the error; a stable but wrong value points more toward charge ratio or switch conduction than insufficient wait time.", "",
        "## Results", "",
        "| case | code | settled error LSB | early-to-late V | half-LSB pass |", "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        if not row["measured"]:
            lines.append(f"| {row['case']} | {row['code']} | timeout | timeout | False |")
        else:
            lines.append(f"| {row['case']} | {row['code']} | {row['error_lsb']:.3f} | {row['early_to_late_delta_v']:.6f} | {row['half_lsb_pass']} |")
    lines += ["", "## Interpretation", "", "This is a controlled sensitivity result, not a statistical yield result. To turn it into a calibration decision, the next run must draw mismatch across every capacitor and switch, repeat every code, and run the resulting thresholds through the closed-loop SAR. A nominal code table cannot represent that distribution.", "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{report['measured_case_count']}/{report['total_case_count']}")
    print(f"half_lsb_pass,{report['half_lsb_pass_count']}/{report['total_case_count']}")
    print(f"monotonic,{report['monotonic_case_count']}/{report['case_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
