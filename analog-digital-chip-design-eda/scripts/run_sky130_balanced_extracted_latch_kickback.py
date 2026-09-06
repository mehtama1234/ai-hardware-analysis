#!/usr/bin/env python3
"""Connect the extracted balanced frontend to the transistor latch.

This is deliberately a bounded physical handoff test.  It is not a SAR proof.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
SPICE = LAB / "spice"
MEASUREMENTS = LAB / "measurements"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
EXTRACTED = Path(os.environ.get("AIMC_HANDOFF_EXTRACTED_FRONTEND", str(LAB / "layout-workbench" / "extracted" / "sky130_balanced_capacitive_isolation_frontend_extracted.spice"))).resolve()
FRONTEND_CELL = os.environ.get("AIMC_HANDOFF_FRONTEND_CELL", "sky130_balanced_capacitive_isolation_frontend")
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
CONFIRM = EVIDENCE / "sky130-capacitive-isolation-both-polarity-confirm.json"
OUTPUT_STEM = os.environ.get("AIMC_HANDOFF_OUTPUT_STEM", "sky130-balanced-extracted-latch-kickback")
OUT_JSON = EVIDENCE / f"{OUTPUT_STEM}.json"
OUT_MD = EVIDENCE / f"{OUTPUT_STEM}.md"
OUT_CSV = MEASUREMENTS / f"{OUTPUT_STEM}.csv"
DECK = SPICE / f"{OUTPUT_STEM}.sp"
LATCH_INPUT_W = float(os.environ.get("AIMC_HANDOFF_LATCH_INPUT_W", "10"))
LATCH_TAIL_W = float(os.environ.get("AIMC_HANDOFF_LATCH_TAIL_W", "20"))
INPUT_DIFF_SCALE = float(os.environ.get("AIMC_HANDOFF_INPUT_DIFF_SCALE", "1"))
SWAP_LATCH_INPUTS = os.environ.get("AIMC_HANDOFF_SWAP_LATCH_INPUTS") == "1"
LATCH_GATE_BIAS_OHM = float(os.environ.get("AIMC_HANDOFF_LATCH_GATE_BIAS_OHM", "1e11"))


def measure(stdout: str, name: str) -> float:
    matches = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", stdout)
    if not matches:
        raise ValueError(f"missing ngspice measurement {name}")
    return float(matches[-1])


def deck(diff_mv: float) -> str:
    diff = diff_mv / 1000.0
    latch_gate_p = "sense_n" if SWAP_LATCH_INPUTS else "sense_p"
    latch_gate_n = "sense_p" if SWAP_LATCH_INPUTS else "sense_n"
    return f'''* Extracted balanced frontend to Sky130 latch handoff.
.lib "{PDK_LIB}" tt
.include "{EXTRACTED}"
.param vdd=1.8
.param lmin=0.15
.param wp_latch=6
.param wn_latch=3
.param wn_in={LATCH_INPUT_W:g}
.param wn_tail={LATCH_TAIL_W:g}
.param vinp={0.9 + diff / 2:.12f}
.param vinn={0.9 - diff / 2:.12f}
VDD vdd 0 {{vdd}}
VSS vss 0 0
VSP sp 0 PULSE(0 {{vinp}} 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 {{vinn}} 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 {{vdd}} 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 {{vdd}} 2.00n 20p 20p 5n 10n)
VCLB clkb 0 PULSE({{vdd}} 0 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 PULSE(0.9 1.8 0.50n 20p 20p 0.50n 2n)
XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn {FRONTEND_CELL}
RBIASP sense_p vcm_reset {LATCH_GATE_BIAS_OHM:.12g}
RBIASN sense_n vcm_reset {LATCH_GATE_BIAS_OHM:.12g}
XPREP vdd clk_latch outp vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XPREN vdd clk_latch outn vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XINP outp {latch_gate_p} tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XINN outn {latch_gate_n} tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XTAIL tail clk_latch 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
XEVAL eval clk_latch 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
CSP sp 0 0.2p
CSN sn 0 0.2p
COUTP outp 0 5f
COUTN outn 0 5f
.tran 2p 6n
.measure tran sense_p_before_v FIND v(sense_p) AT=1.90n
.measure tran sense_n_before_v FIND v(sense_n) AT=1.90n
.measure tran sense_p_after_v FIND v(sense_p) AT=4.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=4.60n
.measure tran sample_p_before_v FIND v(sp) AT=1.90n
.measure tran sample_n_before_v FIND v(sn) AT=1.90n
.measure tran sample_p_after_v FIND v(sp) AT=4.60n
.measure tran sample_n_after_v FIND v(sn) AT=4.60n
.measure tran outp_final_v FIND v(outp) AT=4.60n
.measure tran outn_final_v FIND v(outn) AT=4.60n
.measure tran output_diff_final_v PARAM='outn_final_v-outp_final_v'
.control
run
.endc
.end
'''


def main() -> int:
    target_mv = float(json.loads(CONFIRM.read_text())["target_combined_offset_noise_mv"]) * INPUT_DIFF_SCALE
    rows = []
    for diff_mv in (-target_mv, 0.0, target_mv):
        DECK.write_text(deck(diff_mv), encoding="utf-8")
        try:
            result = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, timeout=120, check=False)
        except subprocess.TimeoutExpired:
            rows.append({"input_diff_mv": diff_mv, "measured": False, "timed_out": True})
            continue
        if result.returncode != 0:
            rows.append({"input_diff_mv": diff_mv, "measured": False, "timed_out": False, "error_excerpt": (result.stdout + result.stderr)[-1200:]})
            continue
        sample_before = measure(result.stdout, "sample_p_before_v") - measure(result.stdout, "sample_n_before_v")
        sample_after = measure(result.stdout, "sample_p_after_v") - measure(result.stdout, "sample_n_after_v")
        output = measure(result.stdout, "output_diff_final_v")
        expected = -1 if diff_mv > 0 else 1 if diff_mv < 0 else 0
        measured_sign = 1 if output > 0 else -1 if output < 0 else 0
        rows.append({
            "input_diff_mv": diff_mv,
            "expected_sign": expected,
            "measured_sign": measured_sign,
            "sense_diff_before_v": measure(result.stdout, "sense_p_before_v") - measure(result.stdout, "sense_n_before_v"),
            "sense_diff_after_v": measure(result.stdout, "sense_p_after_v") - measure(result.stdout, "sense_n_after_v"),
            "sample_diff_before_v": sample_before,
            "sample_diff_after_v": sample_after,
            "sampled_diff_kickback_v": abs(sample_after - sample_before),
            "output_diff_final_v": output,
            "outp_final_v": measure(result.stdout, "outp_final_v"),
            "outn_final_v": measure(result.stdout, "outn_final_v"),
            "measured": True,
            "timed_out": False,
            "resolved_correct_polarity": expected != 0 and measured_sign == expected and abs(output) >= 0.9,
        })
    limit = 1.8 / 4096.0 / 2.0
    signal_rows = [r for r in rows if r.get("input_diff_mv") != 0.0]
    zero_row = next((r for r in rows if r.get("input_diff_mv") == 0.0 and r.get("measured")), None)
    zero_output = zero_row.get("output_diff_final_v") if zero_row else None
    for row in signal_rows:
        row["offset_corrected_output_diff_v"] = row["output_diff_final_v"] - zero_output if zero_output is not None and row.get("measured") and "output_diff_final_v" in row else None
        row["offset_corrected_measured_sign"] = (1 if row["offset_corrected_output_diff_v"] > 0 else -1 if row["offset_corrected_output_diff_v"] < 0 else 0) if row["offset_corrected_output_diff_v"] is not None else 0
        row["offset_corrected_sign"] = row.get("expected_sign") is not None and row["offset_corrected_measured_sign"] == row["expected_sign"]
    passing = [r for r in signal_rows if r.get("measured") and r.get("resolved_correct_polarity") and r.get("sampled_diff_kickback_v", limit + 1) <= limit]
    report = {
        "result_type": "sky130_balanced_extracted_latch_kickback",
        "status": "balanced_extracted_frontend_latch_kickback_passed_not_sar_or_signoff" if len(passing) == len(signal_rows) else "balanced_extracted_frontend_latch_kickback_open",
        "extracted_frontend": str(EXTRACTED.relative_to(ROOT)),
        "frontend_cell": FRONTEND_CELL,
        "generated_deck": str(DECK.relative_to(ROOT)),
        "case_count": len(rows),
        "signal_case_count": len(signal_rows),
        "passing_case_count": len(passing),
        "zero_input_output_diff_v": zero_output,
        "hard_kickback_limit_v": limit,
        "latch_input_width_um": LATCH_INPUT_W,
        "latch_tail_width_um": LATCH_TAIL_W,
        "input_diff_scale": INPUT_DIFF_SCALE,
        "latch_input_swap": SWAP_LATCH_INPUTS,
        "latch_gate_bias_ohm": LATCH_GATE_BIAS_OHM,
        "rows": rows,
        "accepted_ready_now": False,
        "claim_boundary": {
            "allowed": "connects the Magic-extracted balanced frontend to a Sky130 transistor latch and measures both polarity and sampled-node kickback",
            "not_allowed": "does not prove offset, noise, mismatch, DRC/LVS, SAR bit cycling, full converter behavior, or accepted post-layout economics",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_CSV.write_text("\n".join([",".join(sorted(rows[0]))] + [",".join(str(r.get(k, "")) for k in sorted(rows[0])) for r in rows]) + "\n", encoding="utf-8")
    lines = ["# Sky130 Balanced Extracted Frontend Latch Kickback", "", f"- status: `{report['status']}`", f"- passing cases: `{len(passing)}` of `{len(rows)}`", f"- hard kickback limit V: `{limit:.9e}`", "", "This is the first connected extracted-frontend-to-transistor-latch test. It is intentionally bounded and does not constitute converter signoff.", "", "| input diff mV | sense diff after V | sampled kickback V | output diff V | polarity pass |", "|---:|---:|---:|---:|---|"]
    for row in rows:
        lines.append(f"| `{row.get('input_diff_mv')}` | `{row.get('sense_diff_after_v', 'failed')}` | `{row.get('sampled_diff_kickback_v', 'failed')}` | `{row.get('output_diff_final_v', 'failed')}` | `{row.get('resolved_correct_polarity', False)}` |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("sky130_balanced_extracted_latch_kickback")
    print(f"status,{report['status']}")
    print(f"passing_case_count,{len(passing)}")
    print(f"json,{OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
