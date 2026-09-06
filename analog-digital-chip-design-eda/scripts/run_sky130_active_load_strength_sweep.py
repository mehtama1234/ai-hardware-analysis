#!/usr/bin/env python3
"""Sweep structural sizing and initial imbalance on the extracted active-load topology."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware"
EXTRACTED = LAB / "layout-workbench/extracted/sky130_latch_precharge_tail_active_load_flat_extracted.spice"
DECK = LAB / "spice/sky130-active-load-strength-sweep.sp"
OUT = ROOT / "evidence/aimc-simulator-adapters/sky130-active-load-strength-sweep.json"


def measure(text: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not values:
        raise ValueError(name)
    return float(values[-1])


def deck(input_kp: float, load_kp: float, tail_kp: float, diff_mv: float, kick_mv: float) -> str:
    net = EXTRACTED.read_text(encoding="utf-8").replace("sky130_fd_pr__nfet_01v8", "LATCH_NMOS").replace("sky130_fd_pr__pfet_01v8", "LOAD_PMOS")
    net = re.sub(r"^X(\d+) ", r"M\1 ", net, flags=re.MULTILINE)
    net = re.sub(r"^(M1 .*?)LATCH_NMOS", r"\1INPUT_NMOS", net, flags=re.MULTILINE)
    net = re.sub(r"^(M5 .*?)LATCH_NMOS", r"\1INPUT_NMOS", net, flags=re.MULTILINE)
    net = re.sub(r"^(M0 .*?)LATCH_NMOS", r"\1FEEDBACK_NMOS", net, flags=re.MULTILINE)
    net = re.sub(r"^(M3 .*?)LATCH_NMOS", r"\1FEEDBACK_NMOS", net, flags=re.MULTILINE)
    net = re.sub(r"^(M6 .*?)LATCH_NMOS", r"\1TAIL_NMOS", net, flags=re.MULTILINE)
    p, n = 0.9 + diff_mv / 2000.0, 0.9 - diff_mv / 2000.0
    return f'''* Extracted active-load strength sweep, structural models only.
.global VSUBS
.model LATCH_NMOS nmos level=1 kp={input_kp:.9g}u vto=0.55 lambda=0.02
.model INPUT_NMOS nmos level=1 kp={input_kp:.9g}u vto=0.55 lambda=0.02
.model FEEDBACK_NMOS nmos level=1 kp={input_kp * 0.5:.9g}u vto=0.55 lambda=0.02
.model TAIL_NMOS nmos level=1 kp={tail_kp:.9g}u vto=0.55 lambda=0.02
.model LOAD_PMOS pmos level=1 kp={load_kp:.9g}u vto=-0.55 lambda=0.02
.options method=gear maxord=1 reltol=1e-4 abstol=1e-12 gmin=1e-9
{net}
VDD vdd 0 1.8
VDD_ACTIVE vdd_active 0 1.8
VSS vss 0 0
VSUB VSUBS 0 0
VSP sense_p 0 PULSE(0.9 {p:.12g} 0.50n 20p 20p 20n 40n)
VSN sense_n 0 PULSE(0.9 {n:.12g} 0.50n 20p 20p 20n 40n)
VRESET reset 0 PULSE(0 1.8 1.00n 20p 20p 19n 20n)
VEVAL eval 0 PULSE(0 1.8 1.10n 20p 20p 8n 20n)
XU out_p out_n sense_p sense_n tail reset vdd vss eval sky130_latch_precharge_tail_active_load_flat
.ic v(out_p)={1.8 + kick_mv / 2000.0:.12g} v(out_n)={1.8 - kick_mv / 2000.0:.12g}
.tran 20p 10n uic
.measure tran out_p_final FIND v(out_p) AT=8.00n
.measure tran out_n_final FIND v(out_n) AT=8.00n
.measure tran output_diff_final PARAM='out_p_final-out_n_final'
.measure tran out_p_eval FIND v(out_p) AT=4.00n
.measure tran out_n_eval FIND v(out_n) AT=4.00n
.measure tran output_diff_eval PARAM='out_p_eval-out_n_eval'
.control
run
.endc
.end
'''


def main() -> int:
    rows = []
    for input_kp in (200.0, 500.0, 1000.0):
        for load_kp in (10.0, 25.0, 50.0, 100.0):
            for tail_kp in (20.0, 50.0, 100.0, 200.0):
                for diff_mv in (-10.0, 10.0):
                    for kick_mv in (-2.0, 2.0):
                        DECK.write_text(deck(input_kp, load_kp, tail_kp, diff_mv, kick_mv), encoding="utf-8")
                        try:
                            proc = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=30)
                        except subprocess.TimeoutExpired:
                            rows.append({"input_kp_u": input_kp, "load_kp_u": load_kp, "tail_kp_u": tail_kp, "input_diff_mv": diff_mv, "initial_kick_mv": kick_mv, "measured": False, "timed_out": True})
                            continue
                        row = {"input_kp_u": input_kp, "load_kp_u": load_kp, "tail_kp_u": tail_kp, "input_diff_mv": diff_mv, "initial_kick_mv": kick_mv, "measured": proc.returncode == 0, "timed_out": False}
                        if proc.returncode == 0:
                            row["output_diff_final_v"] = measure(proc.stdout, "output_diff_final")
                            row["output_diff_eval_v"] = measure(proc.stdout, "output_diff_eval")
                            row["regenerated"] = abs(row["output_diff_eval_v"]) >= 0.5
                            row["polarity_consistent"] = (row["output_diff_eval_v"] < 0) == (diff_mv > 0)
                        rows.append(row)
    measured = [r for r in rows if r.get("measured")]
    passing = [r for r in measured if r.get("regenerated") and r.get("polarity_consistent")]
    report = {"result_type": "sky130_active_load_strength_sweep", "status": "active_load_strength_region_found_not_layout_or_converter_signoff" if passing else "active_load_strength_sweep_no_passing_region", "case_count": len(rows), "measured_case_count": len(measured), "passing_case_count": len(passing), "best_cases": sorted(passing, key=lambda r: abs(r["output_diff_final_v"]), reverse=True)[:10], "rows": rows, "accepted_post_layout_written": False, "claim_boundary": {"allowed": "characterizes sizing and initial-condition sensitivity of the exact extracted integrated topology with bounded structural MOS models", "not_allowed": "does not prove physical Sky130 transient behavior, mismatch, PVT, noise, kickback, LVS, SAR conversion, or converter acceptance"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}"); print(f"measured_case_count,{len(measured)}"); print(f"passing_case_count,{len(passing)}"); print(f"json,{OUT}")
    return 0 if len(measured) == len(rows) and passing else 1


if __name__ == "__main__":
    raise SystemExit(main())
