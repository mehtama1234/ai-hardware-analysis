#!/usr/bin/env python3
"""Measure an isolated Sky130 bottom-plate transfer/hold cell."""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDK = Path(os.environ.get("AIMC_SKY130_PDK_LIB", str(Path.home() / "eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice")))
OUT = Path(os.environ.get("AIMC_ISOLATED_CELL_OUTPUT", str(ROOT / "evidence/aimc-simulator-adapters/sky130-isolated-bottom-plate-cell.json")))
TIMEOUT_S = float(os.environ.get("AIMC_ISOLATED_CELL_TIMEOUT_S", "60"))


def value(text: str, name: str) -> float:
    found = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not found:
        raise ValueError(f"missing measurement {name}")
    return float(found[-1])


def build_deck(input_v: float = 0.9) -> str:
    low_fall = float(os.environ.get("AIMC_ISOLATED_CELL_LOW_FALL_NS", "0.05"))
    pre_rise = float(os.environ.get("AIMC_ISOLATED_CELL_PRECHARGE_RISE_NS", "0.05"))
    low_end = 1.18 + low_fall
    pre_start = float(os.environ.get("AIMC_ISOLATED_CELL_PRECHARGE_NS", "1.25"))
    pre_end = pre_start + pre_rise
    connect = float(os.environ.get("AIMC_ISOLATED_CELL_CONNECT_NS", "1.80"))
    connect_end = connect + 0.05
    measure = float(os.environ.get("AIMC_ISOLATED_CELL_MEASURE_NS", "2.50"))
    tran_ns = float(os.environ.get("AIMC_ISOLATED_CELL_TRAN_NS", "4.0"))
    late_ns = float(os.environ.get("AIMC_ISOLATED_CELL_LATE_NS", "3.50"))
    rail_cap = os.environ.get("AIMC_ISOLATED_CELL_RAIL_CAP_F", "0.10p")
    if connect < pre_end:
        raise ValueError("isolated-cell transfer must follow precharge completion")
    return f'''* Isolated bottom-plate transfer/hold cell.
.lib "{PDK}" tt
.param vdd=1.8
VDD vdd 0 {{vdd}}
VTOP top 0 {input_v:.9f}
CBOTTOM top bottom 8p
CRAIL rail 0 {rail_cap}
* Stored plate is held at ground until the low-side switch releases.
XLOW bottom low_gate 0 0 sky130_fd_pr__nfet_01v8 W=8 L=0.15
* Intermediate rail is precharged separately, then isolated from VDD.
RPRELIMIT vdd precharge_supply 100
XPRE rail pre_gate precharge_supply precharge_supply sky130_fd_pr__pfet_01v8 W=64 L=0.15
* A single isolated PMOS transfer device connects the charged rail to storage.
XTRANSFER bottom transfer_gate rail vdd sky130_fd_pr__pfet_01v8 W=64 L=0.15
VLOW low_gate 0 PWL(0 1.8 1.00n 1.8 1.18n 1.8 {low_end:g}n 0 {tran_ns:g}n 0)
VPRE pre_gate 0 PWL(0 1.8 {pre_start:g}n 1.8 {pre_end:g}n 0 {tran_ns:g}n 0)
VTRANSFER transfer_gate 0 PWL(0 1.8 {connect:g}n 1.8 {connect_end:g}n 0 {tran_ns:g}n 0)
RLEAKTOP top 0 100G
RLEAKBOTTOM bottom 0 100G
RLEAKRAIL rail 0 100G
.ic v(top)={input_v:.9f} v(bottom)=0 v(rail)=0
.nodeset v(top)={input_v:.9f} v(bottom)=0 v(rail)=0
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12
.tran 50p {tran_ns:g}n
.measure tran bottom_before_v FIND v(bottom) AT=0.90n
.measure tran rail_precharged_v FIND v(rail) AT=1.75n
.measure tran rail_after_v FIND v(rail) AT={measure:g}n
.measure tran bottom_after_v FIND v(bottom) AT={measure:g}n
.measure tran bottom_late_v FIND v(bottom) AT={late_ns:g}n
.measure tran top_before_v FIND v(top) AT=0.90n
.measure tran top_after_v FIND v(top) AT={measure:g}n
.control
run
.endc
.end
'''


def main() -> int:
    source = build_deck()
    rail_cap = os.environ.get("AIMC_ISOLATED_CELL_RAIL_CAP_F", "0.10p")
    with tempfile.TemporaryDirectory(prefix="aimc-isolated-bottom-cell-") as tmp:
        deck = Path(tmp) / "cell.sp"
        deck.write_text(source, encoding="utf-8")
        proc = subprocess.Popen(["ngspice", "-b", str(deck)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        try:
            stdout, stderr = proc.communicate(timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
            report = {"result_type": "sky130_isolated_bottom_plate_cell", "status": "isolated_bottom_plate_cell_numerical_convergence_timeout", "measured": False, "timeout_s": TIMEOUT_S, "control": {"transient_step_ps": 50.0, "transient_ns": float(os.environ.get("AIMC_ISOLATED_CELL_TRAN_NS", "4.0")), "decision_time_ns": float(os.environ.get("AIMC_ISOLATED_CELL_MEASURE_NS", "2.50")), "late_measure_ns": float(os.environ.get("AIMC_ISOLATED_CELL_LATE_NS", "3.50")), "transfer_device": "isolated_pmos", "precharge_series_ohm": 100.0}, "claim_boundary": "One isolated transfer/hold cell only; no four-bit DAC, SAR, PVT, mismatch, energy, layout, board, or silicon claim."}
            OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(f"status,{report['status']}")
            return 2
    if proc.returncode:
        report = {"result_type": "sky130_isolated_bottom_plate_cell", "status": "isolated_bottom_plate_cell_simulator_failure", "measured": False, "returncode": proc.returncode, "error_excerpt": (stdout + stderr)[-1200:]}
        OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"status,{report['status']}")
        return 2
    report = {
        "result_type": "sky130_isolated_bottom_plate_cell",
        "status": "isolated_bottom_plate_cell_measured_not_accepted",
        "measured": True,
        "input_v": 0.9,
        "decision_time_ns": float(os.environ.get("AIMC_ISOLATED_CELL_MEASURE_NS", "2.50")),
        "bottom_before_v": value(stdout, "bottom_before_v"),
        "rail_precharged_v": value(stdout, "rail_precharged_v"),
        "rail_after_v": value(stdout, "rail_after_v"),
        "bottom_after_v": value(stdout, "bottom_after_v"),
        "bottom_late_v": value(stdout, "bottom_late_v"),
        "top_before_v": value(stdout, "top_before_v"),
        "top_after_v": value(stdout, "top_after_v"),
        "bottom_error_v": value(stdout, "bottom_after_v") - 1.8,
        "control": {"transient_step_ps": 50.0, "transient_ns": float(os.environ.get("AIMC_ISOLATED_CELL_TRAN_NS", "4.0")), "transfer_device": "isolated_pmos", "precharge_series_ohm": 100.0, "rail_cap_f": rail_cap, "low_fall_ns": float(os.environ.get("AIMC_ISOLATED_CELL_LOW_FALL_NS", "0.05")), "precharge_rise_ns": float(os.environ.get("AIMC_ISOLATED_CELL_PRECHARGE_RISE_NS", "0.05")), "precharge_ns": float(os.environ.get("AIMC_ISOLATED_CELL_PRECHARGE_NS", "1.25")), "connect_ns": float(os.environ.get("AIMC_ISOLATED_CELL_CONNECT_NS", "1.80")), "late_measure_ns": float(os.environ.get("AIMC_ISOLATED_CELL_LATE_NS", "3.50"))},
        "claim_boundary": "One isolated transfer/hold cell only; no four-bit DAC, SAR, PVT, mismatch, energy, layout, board, or silicon claim.",
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"bottom_after_v,{report['bottom_after_v']}")
    print(f"rail_precharged_v,{report['rail_precharged_v']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
