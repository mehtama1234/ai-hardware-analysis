#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from run_sky130_extracted_frontend_two_stage_preamp import make_deck

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
CONFIRM = EVIDENCE / "sky130-capacitive-isolation-both-polarity-confirm.json"
OUT = EVIDENCE / "sky130-pmos-input-dynamic-latch.json"
MD = EVIDENCE / "sky130-pmos-input-dynamic-latch.md"
DECK = LAB / "spice" / "sky130_pmos_input_dynamic_latch.sp"


def m(text: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not values:
        raise ValueError(name)
    return float(values[-1])


def build(diff_mv: float, trim: float) -> str:
    deck = make_deck(diff_mv)
    add = f'''* PMOS-input dynamic latch: outputs precharge low, then PMOS input pair pulls one side high.
VTRIMP latch_in_p out_p DC {-trim / 2:.12g}
VTRIMN latch_in_n out_n DC {trim / 2:.12g}
VRST rst 0 PULSE(1.8 0 2.00n 20p 20p 5n 10n)
VCLB clkb 0 PULSE(1.8 0 2.00n 20p 20p 5n 10n)
XPREP lat_p rst 0 0 sky130_fd_pr__nfet_01v8 W=6 L=0.15
XPREN lat_n rst 0 0 sky130_fd_pr__nfet_01v8 W=6 L=0.15
XLP vdd lat_n lat_p vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLN lat_p lat_n 0 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XRP vdd lat_p lat_n vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XRN lat_n lat_p 0 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XINP lat_p latch_in_p tailp vdd sky130_fd_pr__pfet_01v8 W=10 L=0.15
XINN lat_n latch_in_n tailp vdd sky130_fd_pr__pfet_01v8 W=10 L=0.15
XTAILP vdd clkb tailp vdd sky130_fd_pr__pfet_01v8 W=20 L=0.15
CLATP lat_p 0 5f
CLATN lat_n 0 5f
'''
    deck = deck.replace(".ic v(sense_p)=0.9", add + ".ic v(sense_p)=0.9")
    deck = deck.replace(".measure tran out_p_after_v", ".measure tran preamp_out_p_for_trim_v FIND v(out_p) AT=2.60n\n.measure tran preamp_out_n_for_trim_v FIND v(out_n) AT=2.60n\n.measure tran out_p_after_v")
    deck = deck.replace(".tran 20p 3n", ".tran 20p 6n")
    deck = deck.replace("AT=2.60n\n.control", "AT=4.60n\n.measure tran lat_p_final_v FIND v(lat_p) AT=4.60n\n.measure tran lat_n_final_v FIND v(lat_n) AT=4.60n\n.measure tran latch_output_diff_v PARAM='lat_n_final_v-lat_p_final_v'\n.control")
    return deck


def run(diff: float, trim: float) -> tuple[dict, str]:
    DECK.write_text(build(diff, trim), encoding="utf-8")
    result = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=120)
    row = {"input_diff_mv": diff, "measured": result.returncode == 0, "returncode": result.returncode}
    if result.returncode == 0:
        row.update({"latch_output_diff_v": m(result.stdout, "latch_output_diff_v"), "preamp_out_diff_v": m(result.stdout, "preamp_out_p_for_trim_v") - m(result.stdout, "preamp_out_n_for_trim_v")})
    else:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
    return row, result.stdout


def main() -> int:
    target = float(json.loads(CONFIRM.read_text())["target_combined_offset_noise_mv"])
    zero, zero_stdout = run(0.0, 0.0)
    if not zero["measured"]:
        raise RuntimeError("zero calibration failed")
    trim = zero["preamp_out_diff_v"]
    rows = [run(-target, trim)[0], run(target, trim)[0]]
    for row in rows:
        if row["measured"]:
            row["expected_sign"] = 1 if row["input_diff_mv"] > 0 else -1
            row["measured_sign"] = 1 if row["latch_output_diff_v"] > 0 else -1 if row["latch_output_diff_v"] < 0 else 0
            row["polarity_pass"] = row["measured_sign"] == row["expected_sign"] and abs(row["latch_output_diff_v"]) >= 0.9
    passing = [r for r in rows if r.get("polarity_pass")]
    report = {"result_type": "sky130_pmos_input_dynamic_latch", "status": "pmos_input_dynamic_latch_passed_not_noise_or_sar_proof" if len(passing) == len(rows) else "pmos_input_dynamic_latch_open", "same_run_preamp_trim_v": trim, "case_count": len(rows), "measured_case_count": sum(r["measured"] for r in rows), "passing_case_count": len(passing), "rows": rows, "accepted_ready_now": False, "claim_boundary": {"allowed": "tests a PMOS-input dynamic latch with low-output precharge driven by the extracted two-stage preamp", "not_allowed": "does not prove noise, statistical offset, mismatch, sampled-node kickback, DRC/LVS, SAR conversion, or accepted converter evidence"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD.write_text("\n".join(["# Sky130 PMOS-Input Dynamic Latch", "", f"- status: `{report['status']}`", f"- same-run preamp trim V: `{trim}`", f"- passing cases: `{len(passing)}` of `{len(rows)}`", "", "This is a different regenerative architecture: outputs precharge low and a PMOS input pair pulls the winning side high during evaluation.", "", "| input diff mV | latch output diff V | polarity pass |", "|---:|---:|---|", *[f"| `{r['input_diff_mv']}` | `{r.get('latch_output_diff_v', 'failed')}` | `{r.get('polarity_pass', False)}` |" for r in rows], "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]), encoding="utf-8")
    print("sky130_pmos_input_dynamic_latch")
    print(f"status,{report['status']}")
    print(f"passing_case_count,{len(passing)}")
    print(f"json,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
