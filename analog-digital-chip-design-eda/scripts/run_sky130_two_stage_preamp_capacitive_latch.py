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
PREAMP = EVIDENCE / "sky130-extracted-frontend-two-stage-preamp.json"
OUTPUT_STEM = os.environ.get("AIMC_CAP_LATCH_OUTPUT_STEM", "sky130-two-stage-preamp-capacitive-latch")
OUT = EVIDENCE / f"{OUTPUT_STEM}.json"
MD = EVIDENCE / f"{OUTPUT_STEM}.md"
DECK = LAB / "spice" / f"{OUTPUT_STEM}.sp"


def measure(text: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not values:
        raise ValueError(name)
    return float(values[-1])


def build(diff_mv: float, trim_v: float, coupling_ff: float) -> str:
    deck = make_deck(diff_mv)
    insertion = f'''* Capacitive latch-input isolation; no DC path from latch gates to preamp outputs.
VTRIMP corr_p out_p DC {-trim_v / 2:.12g}
VTRIMN corr_n out_n DC {trim_v / 2:.12g}
VBIAS_LATCH gate_bias 0 0.9
CCP corr_p gate_p {coupling_ff:.12g}f
CCN corr_n gate_n {coupling_ff:.12g}f
RGP gate_p gate_bias 100G
RGN gate_n gate_bias 100G
VCLB clkb 0 PULSE(1.8 0 2.00n 20p 20p 5n 10n)
XPREPL vdd clk_latch lat_p vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XPRENL vdd clk_latch lat_n vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLPL lat_p lat_n vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLNL lat_p lat_n eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XRPL lat_n lat_p vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XRNL lat_n lat_p eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XINPL lat_p gate_p tail_l 0 sky130_fd_pr__nfet_01v8 W=10 L=0.15
XINNL lat_n gate_n tail_l 0 sky130_fd_pr__nfet_01v8 W=10 L=0.15
XTAILL tail_l clk_latch 0 0 sky130_fd_pr__nfet_01v8 W=20 L=0.15
XEVAL eval clk_latch 0 0 sky130_fd_pr__nfet_01v8 W=20 L=0.15
CLATP lat_p 0 5f
CLATN lat_n 0 5f
'''
    deck = deck.replace(".ic v(sense_p)=0.9", insertion + ".ic v(sense_p)=0.9 v(gate_p)=0.9 v(gate_n)=0.9")
    deck = deck.replace(".measure tran out_p_after_v", ".measure tran gate_p_before_v FIND v(gate_p) AT=1.90n\n.measure tran gate_n_before_v FIND v(gate_n) AT=1.90n\n.measure tran gate_p_after_v FIND v(gate_p) AT=4.60n\n.measure tran gate_n_after_v FIND v(gate_n) AT=4.60n\n.measure tran out_p_after_v")
    deck = deck.replace(".tran 20p 3n", ".tran 20p 6n")
    deck = deck.replace("AT=2.60n\n.control", "AT=4.60n\n.measure tran lat_p_final_v FIND v(lat_p) AT=4.60n\n.measure tran lat_n_final_v FIND v(lat_n) AT=4.60n\n.measure tran latch_output_diff_v PARAM='lat_n_final_v-lat_p_final_v'\n.control")
    return deck


def main() -> int:
    target = float(json.loads(CONFIRM.read_text())["target_combined_offset_noise_mv"])
    trim = float(json.loads(PREAMP.read_text())["zero_input_offset_output_diff_v"])
    coupling_ff = float(os.environ.get("AIMC_CAP_LATCH_COUPLING_FF", "0.2"))
    rows = []
    for diff in (-target, target):
        DECK.write_text(build(diff, trim, coupling_ff), encoding="utf-8")
        try:
            result = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=120)
        except subprocess.TimeoutExpired as exc:
            rows.append({"input_diff_mv": diff, "measured": False, "returncode": None, "timed_out": True, "error_excerpt": str(exc)[-1200:]})
            continue
        row = {"input_diff_mv": diff, "measured": result.returncode == 0, "returncode": result.returncode, "timed_out": False}
        if result.returncode == 0:
            output = measure(result.stdout, "latch_output_diff_v")
            gate_before = measure(result.stdout, "gate_p_before_v") - measure(result.stdout, "gate_n_before_v")
            gate_after = measure(result.stdout, "gate_p_after_v") - measure(result.stdout, "gate_n_after_v")
            row.update({"gate_diff_before_v": gate_before, "gate_diff_after_v": gate_after, "latch_output_diff_v": output, "latch_polarity_pass": (output > 0) == (diff > 0) and abs(output) >= 0.9, "gate_kickback_v": abs(gate_after - gate_before)})
        else:
            row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        rows.append(row)
    passing = [r for r in rows if r.get("latch_polarity_pass")]
    report = {"result_type": "sky130_two_stage_preamp_capacitive_latch", "status": "two_stage_preamp_capacitive_latch_passed_not_noise_or_sar_proof" if len(passing) == len(rows) else "two_stage_preamp_capacitive_latch_open", "coupling_cap_ff": coupling_ff, "preamp_trim_v": trim, "case_count": len(rows), "measured_case_count": sum(r["measured"] for r in rows), "passing_case_count": len(passing), "rows": rows, "accepted_ready_now": False, "claim_boundary": {"allowed": "tests capacitive isolation between the two-stage extracted-front-end preamp and the Sky130 latch gates", "not_allowed": "does not prove noise, statistical offset, mismatch, sampled-node kickback, DRC/LVS, SAR conversion, or accepted converter evidence"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Sky130 Two-Stage Preamp Capacitive Latch", "", f"- status: `{report['status']}`", f"- coupling capacitance fF: `{coupling_ff}`", f"- passing cases: `{len(passing)}` of `{len(rows)}`", "", "This test inserts capacitive isolation between the preamp outputs and latch gates so the latch has no DC loading path into the preamp.", "", "| input diff mV | gate differential after V | gate transition V | latch output diff V | polarity pass |", "|---:|---:|---:|---:|---|"]
    for r in rows:
        lines.append(f"| `{r['input_diff_mv']}` | `{r.get('gate_diff_after_v', 'failed')}` | `{r.get('gate_kickback_v', 'failed')}` | `{r.get('latch_output_diff_v', 'failed')}` | `{r.get('latch_polarity_pass', False)}` |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    MD.write_text("\n".join(lines), encoding="utf-8")
    print("sky130_two_stage_preamp_capacitive_latch")
    print(f"status,{report['status']}")
    print(f"passing_case_count,{len(passing)}")
    print(f"json,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
