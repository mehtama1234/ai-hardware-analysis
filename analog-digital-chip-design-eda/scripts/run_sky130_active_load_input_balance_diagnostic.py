#!/usr/bin/env python3
"""Diagnose extracted input-branch imbalance without changing layout geometry."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware"
EXTRACTED = LAB / "layout-workbench/extracted/sky130_latch_precharge_tail_active_load_flat_extracted.spice"
DECK = LAB / "spice/sky130-active-load-input-balance-diagnostic.sp"
OUT = ROOT / "evidence/aimc-simulator-adapters/sky130-active-load-input-balance-diagnostic.json"


def value(text: str, name: str) -> float:
    vals = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not vals:
        raise ValueError(name)
    return float(vals[-1])


def make_deck(p_ratio: float, n_ratio: float, diff_mv: float) -> str:
    net = EXTRACTED.read_text(encoding="utf-8").replace("sky130_fd_pr__nfet_01v8", "LATCH_NMOS").replace("sky130_fd_pr__pfet_01v8", "LOAD_PMOS")
    net = re.sub(r"^X(\d+) ", r"M\1 ", net, flags=re.MULTILINE)
    net = net.replace("M1 out_n sense_n tail VSUBS LATCH_NMOS", "M1 out_n sense_n tail VSUBS SENSE_N_NMOS")
    net = net.replace("M5 out_p sense_p tail VSUBS LATCH_NMOS", "M5 out_p sense_p tail VSUBS SENSE_P_NMOS")
    p, n = 0.9 + diff_mv / 2000.0, 0.9 - diff_mv / 2000.0
    return f'''* Extracted input-branch balance diagnostic; structural models only.
.global VSUBS
.model LATCH_NMOS nmos level=1 kp=200u vto=0.55 lambda=0.02
.model SENSE_P_NMOS nmos level=1 kp={200*p_ratio:.9g}u vto=0.55 lambda=0.02
.model SENSE_N_NMOS nmos level=1 kp={200*n_ratio:.9g}u vto=0.55 lambda=0.02
.model LOAD_PMOS pmos level=1 kp=25u vto=-0.55 lambda=0.02
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
XU out_p out_n sense_p sense_n tail reset vdd vss eval sky130_latch_precharge_tail_active_load_flat
.ic v(out_p)=1.8 v(out_n)=1.8
.tran 20p 10n uic
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
    for p_ratio, n_ratio in ((1.0, 1.0), (2.0, 1.0), (4.0, 1.0), (8.0, 1.0), (1.0, 2.0), (1.0, 4.0), (1.0, 8.0)):
        for diff_mv in (-500.0, 500.0):
            DECK.write_text(make_deck(p_ratio, n_ratio, diff_mv), encoding="utf-8")
            proc = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=30)
            row = {"sense_p_strength_ratio": p_ratio, "sense_n_strength_ratio": n_ratio, "input_diff_mv": diff_mv, "measured": proc.returncode == 0}
            if proc.returncode == 0:
                row["output_diff_eval_v"] = value(proc.stdout, "output_diff_eval")
                row["strong_regeneration"] = abs(row["output_diff_eval_v"]) >= 0.5
            else:
                row["error_excerpt"] = (proc.stdout + proc.stderr)[-600:]
            rows.append(row)
    measured = [r for r in rows if r["measured"]]
    balanced = [r for r in measured if r.get("strong_regeneration")]
    report = {"result_type": "sky130_active_load_input_balance_diagnostic", "status": "input_balance_compensation_region_found_not_layout_or_converter_signoff" if balanced else "input_balance_compensation_not_found", "case_count": len(rows), "measured_case_count": len(measured), "strong_case_count": len(balanced), "rows": rows, "accepted_post_layout_written": False, "claim_boundary": {"allowed": "identifies directional sensitivity to input-branch strength in the exact extracted topology using bounded structural models", "not_allowed": "does not prove a physical layout revision, Sky130-model behavior, mismatch, PVT, noise, LVS, SAR conversion, or converter acceptance"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}"); print(f"measured_case_count,{len(measured)}"); print(f"strong_case_count,{len(balanced)}"); print(f"json,{OUT}")
    return 0 if len(measured) == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
