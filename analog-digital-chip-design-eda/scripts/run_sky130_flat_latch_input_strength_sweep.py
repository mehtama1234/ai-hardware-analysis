#!/usr/bin/env python3
"""Sweep input-pair strength on the exact flat extracted latch topology."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
EXTRACTED = LAB / "layout-workbench" / "extracted" / "sky130_latch_precharge_flat_extracted.spice"
DECK = LAB / "spice" / "sky130-flat-latch-input-strength-sweep.sp"
OUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-flat-latch-input-strength-sweep.json"
MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-flat-latch-input-strength-sweep.md"


def val(text: str, name: str) -> float:
    found = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not found:
        raise ValueError(name)
    return float(found[-1])


def make_deck(diff: float, ratio: float, feedback_ratio: float) -> str:
    net = EXTRACTED.read_text(encoding="utf-8").replace("sky130_fd_pr__nfet_01v8", "LATCH_NMOS").replace("sky130_fd_pr__pfet_01v8", "PRECHARGE_PMOS").replace("w_12400_300#", "vdd")
    net = re.sub(r"^X(\d+) ", r"M\1 ", net, flags=re.MULTILINE)
    net = re.sub(r"^(M1 .*?)LATCH_NMOS", r"\1INPUT_NMOS", net, flags=re.MULTILINE)
    net = re.sub(r"^(M4 .*?)LATCH_NMOS", r"\1INPUT_NMOS", net, flags=re.MULTILINE)
    net = re.sub(r"^(M0 .*?)LATCH_NMOS", r"\1FEEDBACK_NMOS", net, flags=re.MULTILINE)
    net = re.sub(r"^(M2 .*?)LATCH_NMOS", r"\1FEEDBACK_NMOS", net, flags=re.MULTILINE)
    p, n = 0.9 + diff / 2000.0, 0.9 - diff / 2000.0
    return f'''* Flat extracted latch input-strength design sweep.
.global VSUBS
.model LATCH_NMOS nmos level=1 kp=200u vto=0.55 lambda=0.02
.model INPUT_NMOS nmos level=1 kp={200*ratio:.12g}u vto=0.55 lambda=0.02
.model FEEDBACK_NMOS nmos level=1 kp={200*feedback_ratio:.12g}u vto=0.55 lambda=0.02
.model PRECHARGE_PMOS pmos level=1 kp=100u vto=-0.55 lambda=0.02
{net}
.options method=gear maxord=1 reltol=1e-4 abstol=1e-12 gmin=1e-9
VDD vdd 0 1.8
VSUB VSUBS 0 0
VSP sense_p 0 PULSE(0.9 {p:.12g} 0.50n 20p 20p 20n 40n)
VSN sense_n 0 PULSE(0.9 {n:.12g} 0.50n 20p 20p 20n 40n)
VRESET reset 0 PULSE(0 1.8 1.00n 20p 20p 19n 20n)
XU out_p out_n sense_p sense_n 0 reset vdd sky130_latch_precharge_flat
.ic v(out_p)=1.8 v(out_n)=1.8
.tran 20p 4n uic
.measure tran out_p_final FIND v(out_p) AT=3.00n
.measure tran out_n_final FIND v(out_n) AT=3.00n
.measure tran output_diff_final PARAM='out_p_final-out_n_final'
.control
run
.endc
.end
'''


def main() -> int:
    rows = []
    for ratio in (1.0, 2.0, 4.0, 6.0, 8.0):
      for feedback_ratio in (0.25, 0.5, 0.75, 1.0):
        for diff in (-10.0, -0.5, 0.5, 10.0):
            DECK.write_text(make_deck(diff, ratio, feedback_ratio), encoding="utf-8")
            try:
                p = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=30)
            except subprocess.TimeoutExpired:
                rows.append({"input_strength_ratio": ratio, "feedback_strength_ratio": feedback_ratio, "input_diff_mv": diff, "measured": False, "timed_out": True})
                continue
            row = {"input_strength_ratio": ratio, "feedback_strength_ratio": feedback_ratio, "input_diff_mv": diff, "measured": p.returncode == 0, "timed_out": False, "returncode": p.returncode}
            if p.returncode == 0:
                row["output_diff_final_v"] = val(p.stdout, "output_diff_final")
                row["polarity_pass"] = (row["output_diff_final_v"] < 0) == (diff > 0)
                row["regenerated"] = abs(row["output_diff_final_v"]) >= 0.5
            else:
                row["error_excerpt"] = (p.stdout + p.stderr)[-1000:]
            rows.append(row)
    measured = [r for r in rows if r.get("measured")]
    passing = [r for r in measured if r.get("polarity_pass") and r.get("regenerated")]
    pairs = sorted({(r["input_strength_ratio"], r["feedback_strength_ratio"]) for r in rows})
    summary = {f"input_{inp:g}_feedback_{fb:g}": {"input_strength_ratio": inp, "feedback_strength_ratio": fb, "passing_case_count": sum(1 for row in measured if row["input_strength_ratio"] == inp and row["feedback_strength_ratio"] == fb and row.get("polarity_pass") and row.get("regenerated")), "case_count": sum(1 for row in rows if row["input_strength_ratio"] == inp and row["feedback_strength_ratio"] == fb)} for inp, fb in pairs}
    report = {"result_type": "sky130_flat_latch_input_strength_sweep", "status": "flat_latch_input_strength_sweep_complete_not_physical_width_or_converter_signoff", "case_count": len(rows), "measured_case_count": len(measured), "passing_case_count": len(passing), "strength_summary": summary, "rows": rows, "accepted_post_layout_written": False, "claim_boundary": {"allowed": "uses the exact flat extracted six-device topology and parasitic capacitors to identify whether stronger input devices can overcome the integrated latch polarity bias in a structural model", "not_allowed": "does not prove changed physical widths, Sky130-model behavior, mismatch/noise, LVS, PVT yield, SAR conversion, or converter acceptance"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD.write_text("\n".join(["# Sky130 Flat Latch Input/Feedback Strength Sweep", "", f"- status: `{report['status']}`", f"- measured cases: `{len(measured)}` of `{len(rows)}`", f"- passing cases: `{len(passing)}`", "", "The sweep changes only structural model strengths of the extracted sense and feedback devices. It is a sizing target for the next physical revision, not physical evidence of changed transistor widths.", "", "| input ratio | feedback ratio | passing cases | total cases |", "|---:|---:|---:|---:|"] + [f"| `{data['input_strength_ratio']}` | `{data['feedback_strength_ratio']}` | `{data['passing_case_count']}` | `{data['case_count']}` |" for data in summary.values()] + ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured_case_count,{len(measured)}")
    print(f"passing_case_count,{len(passing)}")
    print(f"json,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
