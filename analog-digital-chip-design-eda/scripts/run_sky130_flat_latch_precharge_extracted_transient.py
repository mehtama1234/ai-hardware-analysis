#!/usr/bin/env python3
"""Run a structural transient on the flat extracted latch/precharge parent."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
EXTRACTED = LAB / "layout-workbench" / "extracted" / "sky130_latch_precharge_flat_extracted.spice"
DECK = LAB / "spice" / "sky130-flat-latch-precharge-extracted-transient.sp"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-flat-latch-precharge-extracted-transient.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-flat-latch-precharge-extracted-transient.md"


def measure(text: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not values:
        raise ValueError(name)
    return float(values[-1])


def make_deck(diff_mv: float) -> str:
    extracted = EXTRACTED.read_text(encoding="utf-8").replace("sky130_fd_pr__nfet_01v8", "LATCH_NMOS").replace("sky130_fd_pr__pfet_01v8", "PRECHARGE_PMOS").replace("w_12400_300#", "vdd")
    extracted = re.sub(r"^X(\d+) ", r"M\1 ", extracted, flags=re.MULTILINE)
    p = 0.9 + diff_mv / 2000.0
    n = 0.9 - diff_mv / 2000.0
    return f'''* Flat extracted latch plus physical PMOS precharge structural transient.
* Exact extracted topology and parasitic capacitors; bounded level-1 models.
.global VSUBS
.model LATCH_NMOS nmos level=1 kp=200u vto=0.55 lambda=0.02
.model PRECHARGE_PMOS pmos level=1 kp=100u vto=-0.55 lambda=0.02
{extracted}
.options method=gear maxord=1 reltol=1e-4 abstol=1e-12 gmin=1e-9
VDD vdd 0 1.8
VSUB VSUBS 0 0
VSP sense_p 0 PULSE(0.9 {p:.12g} 0.50n 20p 20p 20n 40n)
VSN sense_n 0 PULSE(0.9 {n:.12g} 0.50n 20p 20p 20n 40n)
VRESET reset 0 PULSE(0 1.8 1.00n 20p 20p 19n 20n)
XU out_p out_n sense_p sense_n 0 reset vdd sky130_latch_precharge_flat
.ic v(out_p)=1.8 v(out_n)=1.8
.tran 20p 4n uic
.measure tran out_p_released FIND v(out_p) AT=1.20n
.measure tran out_n_released FIND v(out_n) AT=1.20n
.measure tran out_p_final FIND v(out_p) AT=3.00n
.measure tran out_n_final FIND v(out_n) AT=3.00n
.measure tran output_diff_released PARAM='out_p_released-out_n_released'
.measure tran output_diff_final PARAM='out_p_final-out_n_final'
.control
run
.endc
.end
'''


def main() -> int:
    rows = []
    for diff in (-10.0, -0.5, 0.5, 10.0):
        DECK.write_text(make_deck(diff), encoding="utf-8")
        try:
            proc = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=30)
        except subprocess.TimeoutExpired:
            rows.append({"input_diff_mv": diff, "measured": False, "timed_out": True})
            continue
        row = {"input_diff_mv": diff, "measured": proc.returncode == 0, "timed_out": False, "returncode": proc.returncode}
        if proc.returncode == 0:
            row.update({"output_diff_released_v": measure(proc.stdout, "output_diff_released"), "output_diff_final_v": measure(proc.stdout, "output_diff_final"), "out_p_final_v": measure(proc.stdout, "out_p_final"), "out_n_final_v": measure(proc.stdout, "out_n_final")})
            row["polarity_pass"] = (row["output_diff_final_v"] < 0) == (diff > 0)
            row["regenerated"] = abs(row["output_diff_final_v"]) >= 0.5
        else:
            row["error_excerpt"] = (proc.stdout + proc.stderr)[-1200:]
        rows.append(row)
    measured = [r for r in rows if r.get("measured")]
    passing = [r for r in measured if r.get("polarity_pass") and r.get("regenerated")]
    report = {"result_type": "sky130_flat_latch_precharge_extracted_transient", "status": "flat_extracted_latch_precharge_transient_passed_not_sky130_model_or_converter_signoff" if len(passing) == len(rows) else "flat_extracted_latch_precharge_transient_open", "layout_extracted_netlist": str(EXTRACTED.relative_to(ROOT)), "case_count": len(rows), "measured_case_count": len(measured), "passing_case_count": len(passing), "rows": rows, "accepted_post_layout_written": False, "claim_boundary": {"allowed": "tests the flat extracted latch and physical PMOS precharge topology for post-reset output polarity using bounded structural MOS models", "not_allowed": "does not prove Sky130-model convergence, noise, mismatch, kickback, LVS, PVT yield, SAR conversion, or converter acceptance"}}
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(["# Sky130 Flat Extracted Latch plus Precharge Transient", "", f"- status: `{report['status']}`", f"- measured cases: `{len(measured)}` of `{len(rows)}`", f"- passing cases: `{len(passing)}`", "", "This uses the exact flat Magic-extracted six-device topology and extracted capacitors, with bounded structural MOS models. The physical PMOS reset pair is active during the reset interval and released before evaluation.", "", "| input differential mV | final output differential V | polarity | regenerated |", "|---:|---:|---|---|"] + [f"| `{r['input_diff_mv']}` | `{r.get('output_diff_final_v', 'failed')}` | `{r.get('polarity_pass', False)}` | `{r.get('regenerated', False)}` |" for r in rows] + ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured_case_count,{len(measured)}")
    print(f"passing_case_count,{len(passing)}")
    print(f"json,{OUT_JSON}")
    return 0 if len(measured) == len(rows) and len(passing) == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
