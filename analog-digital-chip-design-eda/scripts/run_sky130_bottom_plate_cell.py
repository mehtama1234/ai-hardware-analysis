#!/usr/bin/env python3
"""Measure one Sky130 transistor bottom-plate cell with break-before-make control."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-bottom-plate-cell.json"
OUT_MD = EVIDENCE / "sky130-bottom-plate-cell.md"
TIMEOUT_S = 30


def measure(stdout: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", stdout)
    if not values:
        raise ValueError(f"missing measurement {name}")
    return float(values[-1])


def deck(input_v: float, target: str) -> str:
    # The bottom plate starts at ground. A selected cell moves to VDD; an
    # unselected cell remains at ground. Both rail controls are non-overlap.
    if target == "vdd":
        low_gate = "PULSE(1.8 0 1.00n 20p 20p 0.18n 20n)"
        high_gate = "PULSE(1.8 0 1.20n 20p 20p 20n 40n)"
    else:
        low_gate = "1.8"
        high_gate = "1.8"
    return f'''* One-bit Sky130 bottom-plate charge-transfer cell.
.lib "{PDK_LIB}" tt
.param vdd=1.8
VDD vdd 0 {{vdd}}
VSS vss 0 0
VTOP top 0 {input_v:.9f}
CBOTTOM top bottom 8p
XLOW bottom low_gate vss vss sky130_fd_pr__nfet_01v8 W=8.0 L=0.15
XHIGH bottom high_gate vdd vdd sky130_fd_pr__pfet_01v8 W=16.0 L=0.15
VLOW low_gate 0 {low_gate}
VHIGH high_gate 0 {high_gate}
.ic v(top)={input_v:.9f} v(bottom)=0
RLEAKTOP top 0 100G
RLEAKBOTTOM bottom 0 100G
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12
.nodeset v(top)={input_v:.9f} v(bottom)=0
.tran 5p 4n
.measure tran top_before_v FIND v(top) AT=0.90n
.measure tran bottom_before_v FIND v(bottom) AT=0.90n
.measure tran top_after_v FIND v(top) AT=2.50n
.measure tran bottom_after_v FIND v(bottom) AT=2.50n
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
        try:
            result = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {"input_v": input_v, "target": target, "measured": False, "timed_out": True}
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
        "break_before_make_ns": 0.18,
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
        f"- break-before-make interval: `{report['break_before_make_ns']} ns`", "",
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
