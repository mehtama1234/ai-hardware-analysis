#!/usr/bin/env python3
"""Run a two-cell bottom-plate ownership fixture before rebuilding the DAC."""
from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDK = Path.home() / "eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice"
PDK = Path(os.environ.get("AIMC_SKY130_PDK_LIB", str(DEFAULT_PDK)))
OUT = ROOT / "evidence/aimc-simulator-adapters/sky130-two-bottom-plate-cells.json"


def deck(code: int) -> str:
    # Cell 0 and cell 1 share a top plate but retain independent rail controls.
    # Every high-side pulse begins after its own low-side release interval.
    rows = []
    high_width = float(os.environ.get("AIMC_TWO_CELL_HIGH_WIDTH_UM", "16"))
    high_bank = int(os.environ.get("AIMC_TWO_CELL_HIGH_BANK", "1"))
    if high_bank < 1:
        raise ValueError("AIMC_TWO_CELL_HIGH_BANK must be at least 1")
    high_nmos_assist = os.environ.get("AIMC_TWO_CELL_HIGH_NMOS_ASSIST") == "1"
    keeper_ohm = os.environ.get("AIMC_TWO_CELL_HIGH_KEEPER_OHM", "")
    measure_ns = float(os.environ.get("AIMC_TWO_CELL_MEASURE_NS", "2.5"))
    tran_ns = float(os.environ.get("AIMC_TWO_CELL_TRAN_NS", "4"))
    step_ps = float(os.environ.get("AIMC_TWO_CELL_STEP_PS", "5"))
    if step_ps <= 0:
        raise ValueError("AIMC_TWO_CELL_STEP_PS must be positive")
    end = f"{tran_ns:g}n"
    for bit in range(2):
        high = (code >> bit) & 1
        low_gate = "1.8" if not high else f"PWL(0 1.8 1n 1.8 1.18n 0 {end} 0)"
        high_gate = f"PWL(0 1.8 1.20n 0 {end} 0)" if high else "1.8"
        high_devices = "\n".join(
            f"XHIGH{bit}_{index} bottom{bit} high{bit} vdd vdd sky130_fd_pr__pfet_01v8 W={high_width:g} L=0.15"
            for index in range(high_bank)
        )
        rows += [
            f"XLOW{bit} bottom{bit} low{bit} 0 0 sky130_fd_pr__nfet_01v8 W=8 L=0.15",
            high_devices,
            f"XHIGHN{bit} bottom{bit} highn{bit} vdd 0 sky130_fd_pr__nfet_01v8 W={high_width:g} L=0.15" if high_nmos_assist else "",
            f"VLOW{bit} low{bit} 0 {low_gate}",
            f"VHIGH{bit} high{bit} 0 {high_gate}",
            f"VHIGHN{bit} highn{bit} 0 PWL(0 0 1.20n 1.8 4n 1.8)" if high_nmos_assist and high else "",
            f"RKEEP{bit} bottom{bit} vdd {keeper_ohm}" if keeper_ohm and high else "",
            f".measure tran b{bit}_before_v FIND v(bottom{bit}) AT=0.90n",
            f".measure tran b{bit}_after_v FIND v(bottom{bit}) AT={measure_ns:g}n",
            f".measure tran b{bit}_late_v FIND v(bottom{bit}) AT=3.50n",
        ]
    return f'''* Two independent Sky130 bottom-plate cells with a shared top plate.
.lib "{PDK}" tt
.param vdd=1.8
VDD vdd 0 {{vdd}}
VTOP top 0 0.9
CB0 top bottom0 4p
CB1 top bottom1 4p
RLEAK top 0 100G
RLEAK0 bottom0 0 100G
RLEAK1 bottom1 0 100G
{chr(10).join(rows)}
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12
.tran {step_ps:g}p {end}
.control
run
.endc
.end
'''


def measure(text: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not values:
        raise ValueError(f"missing {name}")
    return float(values[-1])


def run(code: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="aimc-two-cell-") as tmp:
        path = Path(tmp) / "two-cell.sp"
        path.write_text(deck(code), encoding="utf-8")
        process = subprocess.Popen(
            ["ngspice", "-b", str(path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=float(os.environ.get("AIMC_TWO_CELL_TIMEOUT_S", "180")))
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            stdout, stderr = process.communicate()
            return {"code": code, "measured": False, "timed_out": True, "returncode": None, "failure_class": "numerical_convergence_timeout", "error_excerpt": (stdout + stderr)[-1000:]}
        result = subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
    row = {"code": code, "measured": result.returncode == 0, "timed_out": False, "returncode": result.returncode}
    if result.returncode:
        row["failure_class"] = "simulator_failure"
        row["error_excerpt"] = (result.stdout + result.stderr)[-1000:]
        return row
    row["cells"] = []
    for bit in range(2):
        expected = 1.8 if (code >> bit) & 1 else 0.0
        after = measure(result.stdout, f"b{bit}_after_v")
        row["cells"].append({
            "bit": bit,
            "expected_rail_v": expected,
            "before_v": measure(result.stdout, f"b{bit}_before_v"),
            "after_v": after,
            "late_v": measure(result.stdout, f"b{bit}_late_v"),
            "rail_error_v": after - expected,
            "in_legal_range": 0.0 <= after <= 1.8,
            "within_100mV_of_target": abs(after - expected) <= 0.1,
        })
    return row


def main() -> int:
    requested_codes = os.environ.get("AIMC_TWO_CELL_CODES", "0,1,2,3")
    codes = [int(value) for value in requested_codes.split(",") if value.strip()]
    rows = [run(code) for code in codes]
    report = {
        "result_type": "sky130_two_bottom_plate_cells",
        "status": "two_cell_fixture_measured_not_accepted" if all(r["measured"] for r in rows) else "two_cell_fixture_incomplete",
        "case_count": len(rows),
        "measured_case_count": sum(r["measured"] for r in rows),
        "rows": rows,
        "control_contract": {"break_before_make_ns": 0.02, "low_pulse_width_ns": 0.18, "decision_time_ns": float(os.environ.get("AIMC_TWO_CELL_MEASURE_NS", "2.5")), "transient_ns": float(os.environ.get("AIMC_TWO_CELL_TRAN_NS", "4")), "step_ps": float(os.environ.get("AIMC_TWO_CELL_STEP_PS", "5"))},
        "claim_boundary": "Two nominal shared-top-plate cells only; no four-bit DAC, SAR, PVT, mismatch, energy, layout, board, or silicon claim.",
    }
    output = Path(os.environ.get("AIMC_TWO_CELL_OUTPUT", str(OUT)))
    report["high_switch_width_um"] = float(os.environ.get("AIMC_TWO_CELL_HIGH_WIDTH_UM", "16"))
    report["high_switch_bank"] = int(os.environ.get("AIMC_TWO_CELL_HIGH_BANK", "1"))
    report["high_nmos_assist"] = os.environ.get("AIMC_TWO_CELL_HIGH_NMOS_ASSIST") == "1"
    report["high_keeper_ohm"] = os.environ.get("AIMC_TWO_CELL_HIGH_KEEPER_OHM", "")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "measured": report["measured_case_count"]}, sort_keys=True))
    return 0 if report["status"] == "two_cell_fixture_measured_not_accepted" else 2


if __name__ == "__main__":
    raise SystemExit(main())
