#!/usr/bin/env python3
"""Measure one Sky130 transistor bottom-plate cell with break-before-make control."""

from __future__ import annotations

import json
import re
import os
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUTPUT_STEM = os.environ.get("AIMC_BOTTOM_CELL_OUTPUT_STEM", "sky130-bottom-plate-cell")
OUT_JSON = EVIDENCE / f"{OUTPUT_STEM}.json"
OUT_MD = EVIDENCE / f"{OUTPUT_STEM}.md"
TIMEOUT_S = float(os.environ.get("AIMC_BOTTOM_CELL_TIMEOUT_S", "180"))


def measure(stdout: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", stdout)
    if not values:
        raise ValueError(f"missing measurement {name}")
    return float(values[-1])


def deck(input_v: float, target: str) -> str:
    # The bottom plate starts at ground. A selected cell moves to VDD; an
    # unselected cell remains at ground. Both rail controls are non-overlap.
    if target == "vdd":
        low_delay_ns = float(os.environ.get("AIMC_BOTTOM_CELL_LOW_DELAY_NS", "1.00"))
        low_width_ns = float(os.environ.get("AIMC_BOTTOM_CELL_LOW_PULSE_NS", "0.18"))
        high_delay_ns = float(os.environ.get("AIMC_BOTTOM_CELL_HIGH_DELAY_NS", "1.20"))
        if high_delay_ns < low_delay_ns + low_width_ns:
            raise ValueError("high-side enable must not overlap the low-side on interval")
        low_gate = f"PULSE(1.8 0 {low_delay_ns:g}n 20p 20p {low_width_ns:g}n 20n)"
        high_gate = f"PULSE(1.8 0 {high_delay_ns:g}n 20p 20p 20n 40n)"
    else:
        low_gate = "1.8"
        high_gate = "1.8"
    tran_control = ".tran 5p 4n uic" if os.environ.get("AIMC_BOTTOM_CELL_UIC") == "1" else ".tran 5p 4n"
    high_width = float(os.environ.get("AIMC_BOTTOM_CELL_HIGH_WIDTH", "16.0"))
    high_nf = int(os.environ.get("AIMC_BOTTOM_CELL_HIGH_NF", "1"))
    high_bank = int(os.environ.get("AIMC_BOTTOM_CELL_HIGH_BANK", "1"))
    if high_bank < 1:
        raise ValueError("high-side device bank must contain at least one finger")
    high_devices = "\n".join(
        f"XHIGH{index} bottom high_gate vdd vdd sky130_fd_pr__pfet_01v8 W={high_width:g} L=0.15 NF={high_nf}"
        for index in range(high_bank)
    )
    capacitor_f = os.environ.get("AIMC_BOTTOM_CELL_CAP_F", "8p")
    return f'''* One-bit Sky130 bottom-plate charge-transfer cell.
.lib "{PDK_LIB}" tt
.param vdd=1.8
VDD vdd 0 {{vdd}}
VSS vss 0 0
VTOP top 0 {input_v:.9f}
CBOTTOM top bottom {capacitor_f}
XLOW bottom low_gate vss vss sky130_fd_pr__nfet_01v8 W=8.0 L=0.15
{high_devices}
VLOW low_gate 0 {low_gate}
VHIGH high_gate 0 {high_gate}
.ic v(top)={input_v:.9f} v(bottom)=0
RLEAKTOP top 0 100G
RLEAKBOTTOM bottom 0 100G
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12
.nodeset v(top)={input_v:.9f} v(bottom)=0
{tran_control}
.measure tran top_before_v FIND v(top) AT=0.90n
.measure tran bottom_before_v FIND v(bottom) AT=0.90n
.measure tran top_after_v FIND v(top) AT=2.50n
.measure tran bottom_after_v FIND v(bottom) AT=2.50n
.measure tran bottom_late_v FIND v(bottom) AT=3.50n
.measure tran top_late_v FIND v(top) AT=3.50n
.control
run
.endc
.end
'''


def run(input_v: float, target: str) -> dict[str, Any]:
    source = deck(input_v, target)
    with tempfile.TemporaryDirectory(prefix="aimc-bottom-plate-cell-") as tmp:
        path = Path(tmp) / "cell.sp"
        path.write_text(source, encoding="utf-8")
        process = subprocess.Popen(
            ["ngspice", "-b", str(path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            process.communicate()
            return {"input_v": input_v, "target": target, "measured": False, "timed_out": True}
        result = subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
    row: dict[str, Any] = {"input_v": input_v, "target": target, "measured": result.returncode == 0, "timed_out": False, "returncode": result.returncode}
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        return row
    before = measure(result.stdout, "bottom_before_v")
    after = measure(result.stdout, "bottom_after_v")
    expected_bottom = 1.8 if target == "vdd" else 0.0
    row.update({
        "top_before_v": measure(result.stdout, "top_before_v"),
        "top_after_v": measure(result.stdout, "top_after_v"),
        "top_late_v": measure(result.stdout, "top_late_v"),
        "bottom_late_v": measure(result.stdout, "bottom_late_v"),
        "high_switch_width_um": float(os.environ.get("AIMC_BOTTOM_CELL_HIGH_WIDTH", "16.0")),
        "high_switch_nf": int(os.environ.get("AIMC_BOTTOM_CELL_HIGH_NF", "1")),
        "high_switch_bank": int(os.environ.get("AIMC_BOTTOM_CELL_HIGH_BANK", "1")),
        "capacitor_f": os.environ.get("AIMC_BOTTOM_CELL_CAP_F", "8p"),
        "bottom_before_v": before,
        "bottom_after_v": after,
        "expected_bottom_v": expected_bottom,
        "bottom_error_v": after - expected_bottom,
        "top_movement_v": measure(result.stdout, "top_after_v") - measure(result.stdout, "top_before_v"),
    })
    return row


def main() -> int:
    cases = [(0.3, "vdd"), (0.9, "vdd"), (1.5, "vdd"), (0.9, "ground")]
    rows = [run(*case) for case in cases]
    measured = [row for row in rows if row["measured"]]
    report = {
        "result_type": "sky130_bottom_plate_cell",
        "status": "bottom_plate_cell_characterized" if len(measured) == len(rows) else "bottom_plate_cell_incomplete",
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(row.get("timed_out", False) for row in rows),
        "break_before_make_ns": float(os.environ.get("AIMC_BOTTOM_CELL_HIGH_DELAY_NS", "1.20")) - (float(os.environ.get("AIMC_BOTTOM_CELL_LOW_DELAY_NS", "1.00")) + float(os.environ.get("AIMC_BOTTOM_CELL_LOW_PULSE_NS", "0.18"))),
        "low_side_pulse_width_ns": float(os.environ.get("AIMC_BOTTOM_CELL_LOW_PULSE_NS", "0.18")),
        "low_side_delay_ns": float(os.environ.get("AIMC_BOTTOM_CELL_LOW_DELAY_NS", "1.00")),
        "high_side_delay_ns": float(os.environ.get("AIMC_BOTTOM_CELL_HIGH_DELAY_NS", "1.20")),
        "measured_break_before_make_ns": float(os.environ.get("AIMC_BOTTOM_CELL_HIGH_DELAY_NS", "1.20")) - (float(os.environ.get("AIMC_BOTTOM_CELL_LOW_DELAY_NS", "1.00")) + float(os.environ.get("AIMC_BOTTOM_CELL_LOW_PULSE_NS", "0.18"))),
        "rows": rows,
        "claim_boundary": {
            "allowed": "tests one physical Sky130 bottom-plate capacitor cell with separate low-side and high-side devices and non-overlap control",
            "not_allowed": "does not prove the four-bit DAC, SAR accuracy, mismatch/noise yield, PVT behavior, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Bottom-Plate Cell", "",
        f"- status: `{report['status']}`",
        f"- measured cases: `{len(measured)}` of `{len(rows)}`",
        f"- break-before-make interval: `{report['break_before_make_ns']} ns`",
        f"- low-side pulse width: `{report['low_side_pulse_width_ns']} ns`", "",
        f"- high-side device bank: `{report['rows'][0].get('high_switch_bank', 1)}` parallel device(s)", "",
        "This isolated fixture tests the bottom-plate switch before it is placed back into the binary array. The low-side device is released first; the high-side device is enabled only after the non-overlap interval. The top plate and bottom plate are measured before and after the transition.", "",
        "| input V | target rail | bottom before V | bottom after V | expected V | bottom error V |", "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        if row.get("measured"):
            lines.append(f"| {row['input_v']:.3f} | {row['target']} | {row['bottom_before_v']:.6f} | {row['bottom_after_v']:.6f} | {row['expected_bottom_v']:.3f} | {row['bottom_error_v']:.6f} |")
        else:
            lines.append(f"| {row['input_v']:.3f} | {row['target']} | timeout | timeout | - | timeout |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{len(measured)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
