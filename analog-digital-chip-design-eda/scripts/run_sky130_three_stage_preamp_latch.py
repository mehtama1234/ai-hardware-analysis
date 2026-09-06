#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from run_sky130_extracted_frontend_two_stage_preamp import make_deck

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
CONFIRM = EVIDENCE / "sky130-capacitive-isolation-both-polarity-confirm.json"
OUT = EVIDENCE / "sky130-three-stage-preamp-latch.json"
MD = EVIDENCE / "sky130-three-stage-preamp-latch.md"
DECK = LAB / "spice" / "sky130_three_stage_preamp_latch.sp"


def m(text: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not values:
        raise ValueError(name)
    return float(values[-1])


def build(diff_mv: float, trim: float) -> str:
    deck = make_deck(diff_mv)
    use_input_sample = os.environ.get("AIMC_THREE_STAGE_INPUT_SAMPLE_ISOLATION") == "1"
    sample_cap_ff = float(os.environ.get("AIMC_THREE_STAGE_SAMPLE_CAP_FF", "100"))
    sample_switch_w = float(os.environ.get("AIMC_THREE_STAGE_SAMPLE_SWITCH_W_UM", "4"))
    load_mode = os.environ.get("AIMC_THREE_STAGE_LOAD_MODE", "resistive")
    load_w = float(os.environ.get("AIMC_THREE_STAGE_LOAD_W_UM", "8"))
    stage3_w = float(os.environ.get("AIMC_THREE_STAGE_W_UM", "1"))
    stage3_tail = float(os.environ.get("AIMC_THREE_STAGE_TAIL_A", "4e-6"))
    stage3_rd = float(os.environ.get("AIMC_THREE_STAGE_RD_OHM", "500000"))
    if load_mode == "pmos_mirror":
        stage3_load = f"XLOAD3REF drive_p drive_p vdd vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXLOAD3MIR drive_n drive_p vdd vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15"
    else:
        stage3_load = f"RDP3 vdd drive_p {stage3_rd:.12g}\nRDN3 vdd drive_n {stage3_rd:.12g}"
    sample_block = "" if not use_input_sample else f"VRESETB3 resetb3 0 PULSE(1.8 0 2.00n 20p 20p 5n 10n)\nXISOP3 drive_p resetb3 sample3_p 0 sky130_fd_pr__nfet_01v8 W={sample_switch_w:.12g} L=0.15\nXISN3 drive_n resetb3 sample3_n 0 sky130_fd_pr__nfet_01v8 W={sample_switch_w:.12g} L=0.15\nCISOP3 sample3_p 0 {sample_cap_ff:.12g}f\nCISN3 sample3_n 0 {sample_cap_ff:.12g}f\n"
    latch_input_p = "sample3_p" if use_input_sample else "latch_in_p"
    latch_input_n = "sample3_n" if use_input_sample else "latch_in_n"
    insertion = f'''* Third resistor-loaded differential stage plus clocked latch.
{stage3_load}
XINP3 drive_p out_p tail3 0 sky130_fd_pr__nfet_01v8 W={stage3_w:.12g} L=0.15
XINN3 drive_n out_n tail3 0 sky130_fd_pr__nfet_01v8 W={stage3_w:.12g} L=0.15
ITAIL3 tail3 0 {stage3_tail:.12g}
VTRIMP3 latch_in_p drive_p DC {-trim / 2:.12g}
VTRIMN3 latch_in_n drive_n DC {trim / 2:.12g}
{sample_block}
VCLB clkb 0 PULSE(1.8 0 2.00n 20p 20p 5n 10n)
XPREPL vdd clk_latch lat_p vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XPRENL vdd clk_latch lat_n vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLPL lat_p lat_n vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLNL lat_p lat_n eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XRPL lat_n lat_p vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XRNL lat_n lat_p eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XINPL lat_p {latch_input_p} tail_l 0 sky130_fd_pr__nfet_01v8 W=1 L=0.15
XINNL lat_n {latch_input_n} tail_l 0 sky130_fd_pr__nfet_01v8 W=1 L=0.15
XTAILL tail_l clk_latch 0 0 sky130_fd_pr__nfet_01v8 W=20 L=0.15
XEVAL eval clk_latch 0 0 sky130_fd_pr__nfet_01v8 W=20 L=0.15
CLATP lat_p 0 5f
CLATN lat_n 0 5f
'''
    deck = deck.replace(".ic v(sense_p)=0.9", insertion + ".ic v(sense_p)=0.9")
    deck = deck.replace(".measure tran out_p_after_v", ".measure tran drive_p_trim_v FIND v(drive_p) AT=2.60n\n.measure tran drive_n_trim_v FIND v(drive_n) AT=2.60n\n.measure tran out_p_after_v")
    deck = deck.replace(".control\nset noaskquit", ".measure tran drive_p_trim_v FIND v(drive_p) AT=2.60n\n.measure tran drive_n_trim_v FIND v(drive_n) AT=2.60n\n.control\nset noaskquit")
    deck = deck.replace(".tran 20p 3n", ".tran 20p 6n")
    deck = deck.replace("AT=2.60n\n.control", "AT=4.60n\n.measure tran lat_p_final_v FIND v(lat_p) AT=4.60n\n.measure tran lat_n_final_v FIND v(lat_n) AT=4.60n\n.measure tran latch_output_diff_v PARAM='lat_n_final_v-lat_p_final_v'\n.control")
    return deck


def run(diff: float, trim: float) -> dict:
    DECK.write_text(build(diff, trim), encoding="utf-8")
    r = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=120)
    row = {"input_diff_mv": diff, "measured": r.returncode == 0, "returncode": r.returncode}
    if r.returncode == 0:
        out = m(r.stdout, "latch_output_diff_v")
        row.update({"latch_output_diff_v": out, "latch_polarity_pass": (out < 0) == (diff > 0) and abs(out) >= 0.9, "drive_diff_v": m(r.stdout, "drive_p_trim_v") - m(r.stdout, "drive_n_trim_v")})
    else:
        row["error_excerpt"] = (r.stdout + r.stderr)[-1200:]
    return row


def main() -> int:
    target = float(json.loads(CONFIRM.read_text())["target_combined_offset_noise_mv"])
    zero = run(0.0, 0.0)
    if not zero["measured"]:
        raise RuntimeError("zero calibration failed")
    # The added measurements are the same-run third-stage output.  Re-run with its measured differential trim.
    DECK.write_text(build(0.0, 0.0), encoding="utf-8")
    raw = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=120)
    trim = m(raw.stdout, "drive_p_trim_v") - m(raw.stdout, "drive_n_trim_v")
    rows = [run(-target, trim), run(target, trim)]
    passing = [r for r in rows if r.get("latch_polarity_pass")]
    report = {"result_type": "sky130_three_stage_preamp_latch", "status": "three_stage_preamp_latch_passed_not_noise_or_sar_proof" if len(passing) == len(rows) else "three_stage_preamp_latch_open", "same_run_zero_stage3_offset_v": trim, "case_count": len(rows), "measured_case_count": sum(r["measured"] for r in rows), "passing_case_count": len(passing), "rows": rows, "accepted_ready_now": False, "claim_boundary": {"allowed": "tests a third resistor-loaded Sky130 differential stage between the extracted frontend and latch", "not_allowed": "does not prove statistical offset, noise, mismatch, DRC/LVS, SAR conversion, or accepted converter evidence"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD.write_text("\n".join(["# Sky130 Three-Stage Preamp Latch", "", f"- status: `{report['status']}`", f"- same-run stage-3 offset V: `{trim}`", f"- passing cases: `{len(passing)}` of `{len(rows)}`", "", "This is a bounded third-stage gain experiment, not converter signoff.", "", "| input diff mV | latch output diff V | polarity pass |", "|---:|---:|---|", *[f"| `{r['input_diff_mv']}` | `{r.get('latch_output_diff_v', 'failed')}` | `{r.get('latch_polarity_pass', False)}` |" for r in rows], "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]), encoding="utf-8")
    print("sky130_three_stage_preamp_latch")
    print(f"status,{report['status']}")
    print(f"passing_case_count,{len(passing)}")
    print(f"json,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
