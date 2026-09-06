#!/usr/bin/env python3
"""Exercise the extracted latch plus active load with bounded MOS models."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware"
CELL = os.environ.get("AIMC_ACTIVE_LOAD_CELL", "sky130_latch_precharge_tail_active_load_flat")
EXTRACTED = LAB / "layout-workbench/extracted" / f"{CELL}_extracted.spice"
DECK = LAB / "spice" / f"{CELL}-extracted-transient.sp"
OUT = ROOT / os.environ.get("AIMC_ACTIVE_LOAD_TRANSIENT_EVIDENCE", "evidence/aimc-simulator-adapters/sky130-latch-precharge-tail-active-load-extracted-transient.json")


def measure(text: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not values:
        raise ValueError(name)
    return float(values[-1])


def make_deck(diff: float, swap_inputs: bool = False, initial_kick_mv: float = 0.0) -> str:
    net = EXTRACTED.read_text(encoding="utf-8")
    net = net.replace("sky130_fd_pr__nfet_01v8", "LATCH_NMOS").replace("sky130_fd_pr__pfet_01v8", "LOAD_PMOS")
    net = re.sub(r"^X(\d+) ", r"M\1 ", net, flags=re.MULTILINE)
    p, n = 0.9 + diff / 2000.0, 0.9 - diff / 2000.0
    if swap_inputs:
        p, n = n, p
    eval_at_ns = float(os.environ.get("AIMC_ACTIVE_LOAD_EVAL_AT_NS", "4.00"))
    return f'''* Extracted latch/precharge/tail/active-load structural transient.
.global VSUBS
.model LATCH_NMOS nmos level=1 kp=200u vto=0.55 lambda=0.02
.model LOAD_PMOS pmos level=1 kp=100u vto=-0.55 lambda=0.02
.options method=gear maxord=1 reltol=1e-4 abstol=1e-12 gmin=1e-9
{net}
VDD vdd 0 1.8
VDD_ACTIVE vdd_active 0 1.8
VSS vss 0 0
VSUB VSUBS 0 0
VSP sense_p 0 PULSE(0.9 {p:.12g} 0.50n 20p 20p 20n 40n)
VSN sense_n 0 PULSE(0.9 {n:.12g} 0.50n 20p 20p 20n 40n)
VRESET reset 0 PULSE(0 1.8 2.00n 20p 20p 18n 20n)
VEVAL eval 0 PULSE(0 1.8 2.10n 20p 20p 7n 20n)
XU out_p out_n sense_p sense_n tail reset vdd vss eval {CELL}
.ic v(out_p)={1.8 + initial_kick_mv / 2000.0:.12g} v(out_n)={1.8 - initial_kick_mv / 2000.0:.12g}
.tran 20p 10n uic
.measure tran out_p_released FIND v(out_p) AT=2.20n
.measure tran out_n_released FIND v(out_n) AT=2.20n
.measure tran out_p_final FIND v(out_p) AT=8.00n
.measure tran out_n_final FIND v(out_n) AT=8.00n
.measure tran out_p_eval FIND v(out_p) AT={eval_at_ns:.12g}n
.measure tran out_n_eval FIND v(out_n) AT={eval_at_ns:.12g}n
.measure tran output_diff_released PARAM='out_p_released-out_n_released'
.measure tran output_diff_final PARAM='out_p_final-out_n_final'
.measure tran output_diff_eval PARAM='out_p_eval-out_n_eval'
.control
run
.endc
.end
'''


def main() -> int:
    rows = []
    for diff in (-500.0, -10.0, 0.0, 10.0, 500.0):
        for swap_inputs in (False, True):
            for initial_kick_mv in (-100.0, 0.0, 100.0):
                DECK.write_text(make_deck(diff, swap_inputs, initial_kick_mv), encoding="utf-8")
                try:
                    proc = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=30)
                except subprocess.TimeoutExpired:
                    rows.append({"input_diff_mv": diff, "swapped_inputs": swap_inputs, "initial_kick_mv": initial_kick_mv, "measured": False, "timed_out": True})
                    continue
                row = {"input_diff_mv": diff, "swapped_inputs": swap_inputs, "initial_kick_mv": initial_kick_mv, "measured": proc.returncode == 0, "timed_out": False, "returncode": proc.returncode}
                if proc.returncode == 0:
                    row["output_diff_released_v"] = measure(proc.stdout, "output_diff_released")
                    row["output_diff_final_v"] = measure(proc.stdout, "output_diff_final")
                    row["output_diff_eval_v"] = measure(proc.stdout, "output_diff_eval")
                    row["regenerated"] = abs(row["output_diff_eval_v"]) >= 0.5
                else:
                    row["error_excerpt"] = (proc.stdout + proc.stderr)[-1000:]
                rows.append(row)
    measured = [r for r in rows if r.get("measured")]
    passing = [r for r in measured if r.get("regenerated")]
    report = {"result_type": "sky130_latch_precharge_tail_active_load_extracted_transient", "status": "active_load_extracted_transient_passed_not_sky130_model_or_converter_signoff" if len(passing) == len(rows) else "active_load_extracted_transient_open", "case_count": len(rows), "measured_case_count": len(measured), "regenerated_case_count": len(passing), "rows": rows, "accepted_post_layout_written": False, "claim_boundary": {"allowed": "tests the DRC-clean extracted nine-device topology with isolated active-load supply using bounded structural MOS models", "not_allowed": "does not prove Sky130-model convergence, polarity yield, noise, mismatch, kickback, PVT, LVS, SAR conversion, or converter acceptance"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}"); print(f"measured_case_count,{len(measured)}"); print(f"regenerated_case_count,{len(passing)}"); print(f"json,{OUT}")
    return 0 if len(measured) == len(rows) and len(passing) == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
