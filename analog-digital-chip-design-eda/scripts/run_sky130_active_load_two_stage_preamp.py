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
OUTPUT_STEM = os.environ.get("AIMC_ACTIVE_LOAD_OUTPUT_STEM", "sky130-active-load-two-stage-preamp")
OUT = EVIDENCE / f"{OUTPUT_STEM}.json"
MD = EVIDENCE / f"{OUTPUT_STEM}.md"
DECK = LAB / "spice" / f"{OUTPUT_STEM}.sp"


def measure(text: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not values:
        raise ValueError(name)
    return float(values[-1])


def build(diff_mv: float, bias_v: float) -> str:
    deck = make_deck(diff_mv)
    deck = deck.replace("RDP2 vdd out_p {rd2}\nRDN2 vdd out_n {rd2}", f"VBIAS_LOAD bias_load 0 {bias_v:.6f}\nXLOADP out_p bias_load vdd vdd sky130_fd_pr__pfet_01v8 W=4 L=0.15\nXLOADN out_n bias_load vdd vdd sky130_fd_pr__nfet_01v8 W=4 L=0.15")
    # Use a matched PMOS load on both differential outputs; correct the accidental
    # NMOS polarity in the second load below by replacing it with PMOS.
    deck = deck.replace("XLOADN out_n bias_load vdd vdd sky130_fd_pr__nfet_01v8", "XLOADN out_n bias_load vdd vdd sky130_fd_pr__pfet_01v8")
    deck = deck.replace(".tran 20p 3n", ".tran 20p 3n")
    deck = deck.replace(".measure tran out_n_after_v", ".measure tran out_n_after_v")
    return deck


def main() -> int:
    target = float(json.loads(CONFIRM.read_text())["target_combined_offset_noise_mv"])
    bias_v = float(os.environ.get("AIMC_ACTIVE_LOAD_BIAS_V", "0.9"))
    rows = []
    for diff in (-target, 0.0, target):
        DECK.write_text(build(diff, bias_v), encoding="utf-8")
        result = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=120)
        row = {"input_diff_mv": diff, "measured": result.returncode == 0, "returncode": result.returncode}
        if result.returncode == 0:
            output = measure(result.stdout, "out_p_after_v") - measure(result.stdout, "out_n_after_v")
            row.update({"output_diff_v": output, "out_p_v": measure(result.stdout, "out_p_after_v"), "out_n_v": measure(result.stdout, "out_n_after_v")})
        else:
            row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        rows.append(row)
    zero = next((r["output_diff_v"] for r in rows if r["input_diff_mv"] == 0 and r["measured"]), None)
    target_rows = []
    for row in rows:
        if row["input_diff_mv"] != 0 and row["measured"] and zero is not None:
            corrected = row["output_diff_v"] - zero
            row["offset_corrected_output_diff_v"] = corrected
            row["offset_corrected_sign_pass"] = (corrected > 0) == (row["input_diff_mv"] > 0)
            row["offset_corrected_margin_pass"] = abs(corrected) >= 0.0005
            target_rows.append(row)
    report = {"result_type": "sky130_active_load_two_stage_preamp", "status": "active_load_two_stage_preamp_calibrated_margin_passed_not_latch_or_layout_proof" if target_rows and all(r["offset_corrected_sign_pass"] and r["offset_corrected_margin_pass"] for r in target_rows) else "active_load_two_stage_preamp_characterized_not_accepted", "load_bias_v": bias_v, "zero_input_offset_output_diff_v": zero, "case_count": len(rows), "measured_case_count": sum(r["measured"] for r in rows), "offset_corrected_sign_pass_count": sum(r.get("offset_corrected_sign_pass", False) for r in target_rows), "offset_corrected_margin_pass_count": sum(r.get("offset_corrected_margin_pass", False) for r in target_rows), "rows": rows, "accepted_ready_now": False, "claim_boundary": {"allowed": "tests a matched active-load two-stage Sky130 transistor preamp on the extracted frontend", "not_allowed": "does not prove latch behavior, statistical offset, noise, mismatch, DRC/LVS, SAR conversion, or accepted converter evidence"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Sky130 Active-Load Two-Stage Preamp", "", f"- status: `{report['status']}`", f"- load bias V: `{bias_v}`", f"- zero-input offset output V: `{zero}`", f"- corrected margin pass: `{report['offset_corrected_margin_pass_count']}` of `{len(target_rows)}`", "", "This is a matched active-load transistor preamp diagnostic. The offset subtraction is a measured calibration probe, not a statistical offset proof.", "", "| input diff mV | raw output diff V | corrected output diff V | sign pass | margin pass |", "|---:|---:|---:|---|---|"]
    for r in rows:
        lines.append(f"| `{r['input_diff_mv']}` | `{r.get('output_diff_v', 'failed')}` | `{r.get('offset_corrected_output_diff_v', '')}` | `{r.get('offset_corrected_sign_pass', '')}` | `{r.get('offset_corrected_margin_pass', '')}` |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    MD.write_text("\n".join(lines), encoding="utf-8")
    print("sky130_active_load_two_stage_preamp")
    print(f"status,{report['status']}")
    print(f"corrected_margin_pass_count,{report['offset_corrected_margin_pass_count']}")
    print(f"json,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
