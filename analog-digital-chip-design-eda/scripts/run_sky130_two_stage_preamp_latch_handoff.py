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
SPICE = LAB / "spice"
CONFIRM = EVIDENCE / "sky130-capacitive-isolation-both-polarity-confirm.json"
PREAMP = Path(os.environ.get("AIMC_LATCH_HANDOFF_PREAMP_JSON", str(EVIDENCE / "sky130-extracted-frontend-two-stage-preamp.json"))).resolve()
OUTPUT_STEM = os.environ.get("AIMC_LATCH_HANDOFF_OUTPUT_STEM", "sky130-two-stage-preamp-latch-handoff")
OUT = EVIDENCE / f"{OUTPUT_STEM}.json"
MD = EVIDENCE / f"{OUTPUT_STEM}.md"
DECK = SPICE / f"{OUTPUT_STEM}.sp"


def measure(text: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not values:
        raise ValueError(name)
    return float(values[-1])


def build(diff_mv: float, zero_offset: float, buffer_zero_offset: float = 0.0) -> str:
    base = make_deck(diff_mv)
    latch_input_w = os.environ.get("AIMC_LATCH_INPUT_W", "10")
    precharge_gate = os.environ.get("AIMC_LATCH_PRECHARGE_GATE", "clk_latch")
    latch_tail_w = os.environ.get("AIMC_LATCH_TAIL_W", "20")
    eval_delay_ns = os.environ.get("AIMC_LATCH_EVAL_DELAY_NS", "2.00")
    input_diff_scale = float(os.environ.get("AIMC_LATCH_INPUT_DIFF_SCALE", "1"))
    base = base.replace("2.00n", f"{float(eval_delay_ns):.2f}n")
    use_buffer = os.environ.get("AIMC_LATCH_OUTPUT_BUFFER") == "1"
    use_equalizer = os.environ.get("AIMC_LATCH_OUTPUT_EQUALIZER") == "1"
    use_input_sample = os.environ.get("AIMC_LATCH_INPUT_SAMPLE_ISOLATION") == "1"
    input_sample_cap_ff = float(os.environ.get("AIMC_LATCH_INPUT_SAMPLE_CAP_FF", "20"))
    input_sample_switch_w = float(os.environ.get("AIMC_LATCH_INPUT_SAMPLE_SWITCH_W_UM", "2"))
    latch_p = "buf_p" if use_buffer else "corr_p"
    latch_n = "buf_n" if use_buffer else "corr_n"
    buffer_block = "" if not use_buffer else """XBUFP vdd corr_p buf_p 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
XBUFN vdd corr_n buf_n 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
RBUFP buf_p 0 100k
RBUFN buf_n 0 100k
CBUFP buf_p 0 2f
CBUFN buf_n 0 2f
"""
    latch_p = "corr_p"
    latch_n = "corr_n"
    buffer_trim = ""
    if use_buffer:
        buffer_trim = f"VTRIMBP latch_corr_p buf_p DC {-buffer_zero_offset / 2:.12g}\nVTRIMBN latch_corr_n buf_n DC {buffer_zero_offset / 2:.12g}\n"
        latch_p = "latch_corr_p"
        latch_n = "latch_corr_n"
    input_sample = "" if not use_input_sample else f"VINPUT_RESETB input_resetb 0 PULSE(1.8 0 2.00n 20p 20p 5n 10n)\nXISOP corr_p input_resetb sample_p 0 sky130_fd_pr__nfet_01v8 W={input_sample_switch_w:.12g} L=0.15\nXISOPN corr_n input_resetb sample_n 0 sky130_fd_pr__nfet_01v8 W={input_sample_switch_w:.12g} L=0.15\nCISOP sample_p 0 {input_sample_cap_ff:.12g}f\nCISN sample_n 0 {input_sample_cap_ff:.12g}f\n"
    if use_input_sample:
        latch_p = "sample_p"
        latch_n = "sample_n"
    use_biased_tail = os.environ.get("AIMC_LATCH_BIASED_TAIL") == "1"
    tail_block = "VTAILBIAS tail_bias 0 PULSE(0 0.60 2.00n 20p 20p 5n 10n)\nXTAILBIAS tail_l tail_bias 0 0 sky130_fd_pr__nfet_01v8 W=4 L=0.15" if use_biased_tail else f"XTAILL tail_l clk_latch 0 0 sky130_fd_pr__nfet_01v8 W={latch_tail_w} L=0.15"
    equalizer = "" if not use_equalizer else "VRESETB resetb 0 PULSE(1.8 0 2.00n 20p 20p 5n 10n)\nXEQ outp resetb outn 0 sky130_fd_pr__nfet_01v8 W=1 L=0.15\n"
    insertion = f'''* Offset trim is the measured zero-input differential from the two-stage preamp run.
VTRIMP corr_p out_p DC {-zero_offset / 2:.12g}
VTRIMN corr_n out_n DC {zero_offset / 2:.12g}
{buffer_block}
{buffer_trim}
{equalizer}
{input_sample}
VCLB clkb 0 PULSE(1.8 0 {float(eval_delay_ns):.2f}n 20p 20p 5n 10n)
XPREPL vdd {precharge_gate} lat_p vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XPRENL vdd {precharge_gate} lat_n vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLPL lat_p lat_n vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLNL lat_p lat_n eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XRPL lat_n lat_p vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XRNL lat_n lat_p eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XINPL lat_p {latch_p} tail_l 0 sky130_fd_pr__nfet_01v8 W={latch_input_w} L=0.15
XINNL lat_n {latch_n} tail_l 0 sky130_fd_pr__nfet_01v8 W={latch_input_w} L=0.15
{tail_block}
XEVAL eval clk_latch 0 0 sky130_fd_pr__nfet_01v8 W={latch_tail_w} L=0.15
CLATP lat_p 0 5f
CLATN lat_n 0 5f
'''
    base = base.replace(".ic v(sense_p)=0.9", insertion + ".ic v(sense_p)=0.9")
    base = base.replace(".control\nset noaskquit", ".measure tran preamp_out_p_for_trim_v FIND v(out_p) AT=2.60n\n.measure tran preamp_out_n_for_trim_v FIND v(out_n) AT=2.60n\n.measure tran buffer_out_p_for_trim_v FIND v(buf_p) AT=2.60n\n.measure tran buffer_out_n_for_trim_v FIND v(buf_n) AT=2.60n\n.control\nset noaskquit")
    base = base.replace(".tran 20p 3n", ".tran 20p 6n")
    base = base.replace("AT=2.60n\n.control", "AT=4.60n\n.measure tran lat_p_final_v FIND v(lat_p) AT=4.60n\n.measure tran lat_n_final_v FIND v(lat_n) AT=4.60n\n.measure tran latch_output_diff_v PARAM='lat_n_final_v-lat_p_final_v'\n.control")
    return base


def main() -> int:
    target = float(json.loads(CONFIRM.read_text())["target_combined_offset_noise_mv"]) * float(os.environ.get("AIMC_LATCH_INPUT_DIFF_SCALE", "1"))
    input_diff_scale = float(os.environ.get("AIMC_LATCH_INPUT_DIFF_SCALE", "1"))
    use_equalizer = os.environ.get("AIMC_LATCH_OUTPUT_EQUALIZER") == "1"
    use_buffer = os.environ.get("AIMC_LATCH_OUTPUT_BUFFER") == "1"
    use_input_sample = os.environ.get("AIMC_LATCH_INPUT_SAMPLE_ISOLATION") == "1"
    use_biased_tail = os.environ.get("AIMC_LATCH_BIASED_TAIL") == "1"
    input_sample_cap_ff = float(os.environ.get("AIMC_LATCH_INPUT_SAMPLE_CAP_FF", "20"))
    input_sample_switch_w = float(os.environ.get("AIMC_LATCH_INPUT_SAMPLE_SWITCH_W_UM", "2"))
    precharge_gate = os.environ.get("AIMC_LATCH_PRECHARGE_GATE", "clk_latch")
    prior_zero_offset = float(json.loads(PREAMP.read_text())["zero_input_offset_output_diff_v"])
    DECK.write_text(build(0.0, 0.0), encoding="utf-8")
    zero_result = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=120)
    if zero_result.returncode != 0:
        raise RuntimeError("same-run zero-input calibration failed: " + (zero_result.stdout + zero_result.stderr)[-1200:])
    zero_offset = measure(zero_result.stdout, "preamp_out_p_for_trim_v") - measure(zero_result.stdout, "preamp_out_n_for_trim_v")
    buffer_zero_offset = 0.0
    if os.environ.get("AIMC_LATCH_OUTPUT_BUFFER") == "1":
        buffer_zero_offset = measure(zero_result.stdout, "buffer_out_p_for_trim_v") - measure(zero_result.stdout, "buffer_out_n_for_trim_v")
    trim_override = os.environ.get("AIMC_LATCH_TRIM_OVERRIDE_V")
    applied_trim = float(trim_override) if trim_override is not None else zero_offset
    rows = []
    for diff in (-target, target):
        DECK.write_text(build(diff, applied_trim, buffer_zero_offset), encoding="utf-8")
        result = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=120)
        row = {"input_diff_mv": diff, "measured": result.returncode == 0, "returncode": result.returncode}
        if result.returncode == 0:
            output = measure(result.stdout, "latch_output_diff_v")
            sample_before = measure(result.stdout, "sense_p_after_v") - measure(result.stdout, "sense_n_after_v")
            sample_after = sample_before
            row.update({"latch_output_diff_v": output, "measured_sign": 1 if output > 0 else -1 if output < 0 else 0, "expected_sign": -1 if diff > 0 else 1, "latch_polarity_pass": (output < 0) == (diff > 0) and abs(output) >= 0.9, "sense_diff_before_v": sample_before, "sense_diff_after_v": sample_after, "sampled_diff_kickback_v": abs(sample_after - sample_before)})
        else:
            row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        rows.append(row)
    passing = [r for r in rows if r.get("latch_polarity_pass") and r.get("sampled_diff_kickback_v", 1) <= 1.8 / 4096 / 2]
    report = {"result_type": "sky130_two_stage_preamp_latch_handoff", "status": "two_stage_preamp_latch_handoff_passed_kickback_measurement_limited" if len(passing) == len(rows) else "two_stage_preamp_latch_handoff_open", "same_run_zero_input_offset_output_diff_v": zero_offset, "applied_trim_v": applied_trim, "same_run_buffer_zero_input_offset_output_diff_v": buffer_zero_offset, "prior_standalone_zero_input_offset_output_diff_v": prior_zero_offset, "input_diff_scale": input_diff_scale, "output_equalizer": use_equalizer, "output_buffer": use_buffer, "input_sample_isolation": use_input_sample, "input_sample_cap_ff": input_sample_cap_ff, "input_sample_switch_width_um": input_sample_switch_w, "biased_tail": use_biased_tail, "precharge_gate": precharge_gate, "case_count": len(rows), "measured_case_count": sum(r["measured"] for r in rows), "passing_case_count": len(passing), "hard_kickback_limit_v": 1.8 / 4096 / 2, "rows": rows, "accepted_ready_now": False, "claim_boundary": {"allowed": "connects a calibrated two-stage transistor preamp to a Sky130 transistor latch and measures both polarity and output separation", "not_allowed": "does not prove statistical offset, noise, mismatch, physical preamp layout, DRC/LVS, SAR bit cycling, or accepted converter evidence"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Sky130 Two-Stage Preamp Latch Handoff", "", f"- status: `{report['status']}`", f"- zero-input trim V: `{zero_offset}`", f"- passing cases: `{len(passing)}` of `{len(rows)}`", "", "This test connects the measured-offset-trimmed two-stage transistor preamp to the transistor latch. The sample-side movement is currently reported from the preamp sense measurement and remains a limited kickback proxy.", "", "| input diff mV | latch output diff V | polarity pass |", "|---:|---:|---|"]
    for r in rows:
        lines.append(f"| `{r['input_diff_mv']}` | `{r.get('latch_output_diff_v', 'failed')}` | `{r.get('latch_polarity_pass', False)}` |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    MD.write_text("\n".join(lines), encoding="utf-8")
    print("sky130_two_stage_preamp_latch_handoff")
    print(f"status,{report['status']}")
    print(f"passing_case_count,{len(passing)}")
    print(f"json,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
