#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
SPICE = LAB / "spice"
NETLIST = LAB / "layout-workbench" / "extracted" / "sky130_ultra_sense_capacitive_frontend_extracted.spice"
PDK = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
CONFIRM = EVIDENCE / "sky130-capacitive-isolation-both-polarity-confirm.json"
OUT = EVIDENCE / "sky130-extracted-frontend-two-stage-preamp.json"
MD = EVIDENCE / "sky130-extracted-frontend-two-stage-preamp.md"
DECK = SPICE / "sky130_extracted_frontend_two_stage_preamp.sp"
OUTPUT_STEM = os.environ.get("AIMC_TWO_STAGE_OUTPUT_STEM", "sky130-extracted-frontend-two-stage-preamp")
OUT = EVIDENCE / f"{OUTPUT_STEM}.json"
MD = EVIDENCE / f"{OUTPUT_STEM}.md"
DECK = SPICE / f"{OUTPUT_STEM}.sp"


def m(text: str, name: str) -> float:
    hits = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not hits:
        raise ValueError(name)
    return float(hits[-1])


def make_deck(diff_mv: float) -> str:
    dv = diff_mv / 1000.0
    rd1 = float(os.environ.get("AIMC_TWO_STAGE_RD1_OHM", "500000"))
    rd2 = float(os.environ.get("AIMC_TWO_STAGE_RD2_OHM", "500000"))
    itail1 = float(os.environ.get("AIMC_TWO_STAGE_ITAIL1_A", "4e-6"))
    itail2 = float(os.environ.get("AIMC_TWO_STAGE_ITAIL2_A", "4e-6"))
    w1 = float(os.environ.get("AIMC_TWO_STAGE_W1_UM", "1"))
    w2 = float(os.environ.get("AIMC_TWO_STAGE_W2_UM", "1"))
    model_section = os.environ.get("AIMC_TWO_STAGE_MODEL_SECTION", "tt")
    supply_v = float(os.environ.get("AIMC_TWO_STAGE_SUPPLY_V", "1.8"))
    temperature_c = float(os.environ.get("AIMC_TWO_STAGE_TEMPERATURE_C", "27"))
    load_mode = os.environ.get("AIMC_TWO_STAGE_LOAD_MODE", "resistive")
    if load_mode == "pmos_cascode":
        load_w = float(os.environ.get("AIMC_TWO_STAGE_LOAD_W_UM", "4"))
        load_bias = float(os.environ.get("AIMC_TWO_STAGE_LOAD_BIAS_V", "1.20"))
        cas_bias = float(os.environ.get("AIMC_TWO_STAGE_CAS_BIAS_V", "1.00"))
        stage1_load = f"VLOADBIAS1 load_bias1 0 {load_bias:.12g}\nVCASBIAS1 cas_bias1 0 {cas_bias:.12g}\nXLOAD1P load1_p load_bias1 vdd vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXLOAD1N load1_n load_bias1 vdd vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXCAS1P pre_p cas_bias1 load1_p vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXCAS1N pre_n cas_bias1 load1_n vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15"
        stage2_load = f"VLOADBIAS2 load_bias2 0 {load_bias:.12g}\nVCASBIAS2 cas_bias2 0 {cas_bias:.12g}\nXLOAD2P load2_p load_bias2 vdd vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXLOAD2N load2_n load_bias2 vdd vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXCAS2P out_p cas_bias2 load2_p vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXCAS2N out_n cas_bias2 load2_n vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15"
    elif load_mode == "pmos_diode":
        load_w = float(os.environ.get("AIMC_TWO_STAGE_LOAD_W_UM", "8"))
        stage1_load = f"XLOAD1P vdd pre_p pre_p vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXLOAD1N vdd pre_n pre_n vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15"
        stage2_load = f"XLOAD2P vdd out_p out_p vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXLOAD2N vdd out_n out_n vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15"
    elif load_mode == "pmos_mirror":
        load_w = float(os.environ.get("AIMC_TWO_STAGE_LOAD_W_UM", "2"))
        stage1_load = f"XLOAD1REF pre_p pre_p vdd vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXLOAD1MIR pre_n pre_p vdd vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15"
        stage2_load = f"XLOAD2REF out_p out_p vdd vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXLOAD2MIR out_n out_p vdd vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15"
    elif load_mode == "pmos_bias":
        load_bias = float(os.environ.get("AIMC_TWO_STAGE_LOAD_BIAS_V", "1.20"))
        load_w = float(os.environ.get("AIMC_TWO_STAGE_LOAD_W_UM", "2"))
        stage1_load = f"VLOADBIAS1 load_bias1 0 {load_bias:.12g}\nXLOAD1P vdd load_bias1 pre_p vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXLOAD1N vdd load_bias1 pre_n vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15"
        stage2_load = f"VLOADBIAS2 load_bias2 0 {load_bias:.12g}\nXLOAD2P vdd load_bias2 out_p vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15\nXLOAD2N vdd load_bias2 out_n vdd sky130_fd_pr__pfet_01v8 W={load_w:.12g} L=0.15"
    else:
        stage1_load = "RDP1 vdd pre_p {rd1}".format(rd1=f"{rd1:.12g}") + "\nRDN1 vdd pre_n {rd1}".format(rd1=f"{rd1:.12g}")
        stage2_load = "RDP2 vdd out_p {rd2}".format(rd2=f"{rd2:.12g}") + "\nRDN2 vdd out_n {rd2}".format(rd2=f"{rd2:.12g}")
    return f'''* Two-stage transistor preamp attached to extracted Sky130 frontend.
.global VSUBS
.lib "{PDK}" {model_section}
.include "{NETLIST}"
.param vdd={supply_v:.12g}
.param lmin=0.15
.param rd1={rd1:.12g}
.param rd2={rd2:.12g}
.param itail1={itail1:.12g}
.param itail2={itail2:.12g}
.param w1={w1:.12g}
.param w2={w2:.12g}
.param vinp={0.9 + dv/2:.12f}
.param vinn={0.9 - dv/2:.12f}
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12
.temp {temperature_c:.12g}
VDD vdd 0 {{vdd}}
VSS vss 0 0
VSUB VSUBS 0 0
VSP sp 0 PULSE(0 {{vinp}} 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 {{vinn}} 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 {{vdd}} 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 {{vdd}} 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 PULSE({{vdd/2}} {{vdd}} 0.50n 20p 20p 0.50n 2n)
XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_ultra_sense_capacitive_frontend
RBIASP sense_p 0 100G
RBIASN sense_n 0 100G
{stage1_load}
XINP1 pre_p sense_p tail1 0 sky130_fd_pr__nfet_01v8 W={{w1}} L={{lmin}}
XINN1 pre_n sense_n tail1 0 sky130_fd_pr__nfet_01v8 W={{w1}} L={{lmin}}
ITAIL1 tail1 0 {{itail1}}
{stage2_load}
XINP2 out_p pre_p tail2 0 sky130_fd_pr__nfet_01v8 W={{w2}} L={{lmin}}
XINN2 out_n pre_n tail2 0 sky130_fd_pr__nfet_01v8 W={{w2}} L={{lmin}}
ITAIL2 tail2 0 {{itail2}}
COUTP out_p 0 2f
COUTN out_n 0 2f
.ic v(sense_p)=0.9 v(sense_n)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(out_p)=1.0 v(out_n)=1.0
.tran 20p 3n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran pre_p_after_v FIND v(pre_p) AT=2.60n
.measure tran pre_n_after_v FIND v(pre_n) AT=2.60n
.measure tran out_p_after_v FIND v(out_p) AT=2.60n
.measure tran out_n_after_v FIND v(out_n) AT=2.60n
.control
set noaskquit
run
.endc
.end
'''


def main() -> int:
    target = float(json.loads(CONFIRM.read_text())["target_combined_offset_noise_mv"])
    rows = []
    for diff in (-target, 0.0, target):
        DECK.write_text(make_deck(diff), encoding="utf-8")
        result = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=120)
        row = {"input_diff_mv": diff, "measured": result.returncode == 0, "returncode": result.returncode}
        if result.returncode == 0:
            sense = m(result.stdout, "sense_p_after_v") - m(result.stdout, "sense_n_after_v")
            first = m(result.stdout, "pre_n_after_v") - m(result.stdout, "pre_p_after_v")
            # The established converter contract is positive model value = out_p - out_n.
            final = m(result.stdout, "out_p_after_v") - m(result.stdout, "out_n_after_v")
            row.update({"sense_diff_v": sense, "stage1_diff_v": first, "stage2_output_diff_v": final, "out_p_v": m(result.stdout, "out_p_after_v"), "out_n_v": m(result.stdout, "out_n_after_v")})
        else:
            row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        rows.append(row)
    zero = next((r["stage2_output_diff_v"] for r in rows if r["input_diff_mv"] == 0.0 and r["measured"]), None)
    for row in rows:
        if row["measured"] and row["input_diff_mv"] != 0.0 and zero is not None:
            corrected = row["stage2_output_diff_v"] - zero
            row["offset_corrected_output_diff_v"] = corrected
            row["offset_corrected_sign_pass"] = (corrected > 0) == (row["input_diff_mv"] > 0)
            row["offset_corrected_margin_pass"] = abs(corrected) >= 0.0005
    nonzero = [r for r in rows if r["input_diff_mv"] != 0.0 and r["measured"]]
    report = {
        "result_type": "sky130_extracted_frontend_two_stage_preamp",
        "status": "two_stage_preamp_offset_corrected_margin_passed_not_layout_or_latch_proof" if nonzero and all(r.get("offset_corrected_sign_pass") and r.get("offset_corrected_margin_pass") for r in nonzero) else "two_stage_preamp_characterized_not_accepted",
        "frontend_netlist": str(NETLIST.relative_to(ROOT)),
        "load_mode": os.environ.get("AIMC_TWO_STAGE_LOAD_MODE", "resistive"),
        "load_width_um": float(os.environ.get("AIMC_TWO_STAGE_LOAD_W_UM", "2")),
        "stage1_load_ohm": float(os.environ.get("AIMC_TWO_STAGE_RD1_OHM", "500000")),
        "stage2_load_ohm": float(os.environ.get("AIMC_TWO_STAGE_RD2_OHM", "500000")),
        "stage1_tail_a": float(os.environ.get("AIMC_TWO_STAGE_ITAIL1_A", "4e-6")),
        "stage2_tail_a": float(os.environ.get("AIMC_TWO_STAGE_ITAIL2_A", "4e-6")),
        "stage1_width_um": float(os.environ.get("AIMC_TWO_STAGE_W1_UM", "1")),
        "stage2_width_um": float(os.environ.get("AIMC_TWO_STAGE_W2_UM", "1")),
        "generated_deck": str(DECK.relative_to(ROOT)),
        "case_count": len(rows),
        "measured_case_count": sum(r["measured"] for r in rows),
        "zero_input_offset_output_diff_v": zero,
        "offset_corrected_sign_pass_count": sum(r.get("offset_corrected_sign_pass", False) for r in nonzero),
        "offset_corrected_margin_pass_count": sum(r.get("offset_corrected_margin_pass", False) for r in nonzero),
        "rows": rows,
        "accepted_ready_now": False,
        "claim_boundary": {"allowed": "tests a two-stage Sky130 transistor preamp attached to the extracted frontend with zero-input offset subtraction", "not_allowed": "does not prove calibrated offset statistics, noise, mismatch, latch kickback, DRC/LVS, SAR conversion, or accepted post-layout converter evidence"},
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Sky130 Extracted Frontend Two-Stage Preamp", "", f"- status: `{report['status']}`", f"- zero-input output offset V: `{zero}`", f"- corrected sign pass: `{report['offset_corrected_sign_pass_count']}` of `{len(nonzero)}`", f"- corrected margin pass: `{report['offset_corrected_margin_pass_count']}` of `{len(nonzero)}`", "", "This is a transistor-level two-stage preamp diagnostic. Offset subtraction is a measured diagnostic, not a production calibration proof.", "", "| input diff mV | stage-2 output diff V | corrected output diff V | sign pass | margin pass |", "|---:|---:|---:|---|---|"]
    for r in rows:
        lines.append(f"| `{r['input_diff_mv']}` | `{r.get('stage2_output_diff_v', 'failed')}` | `{r.get('offset_corrected_output_diff_v', '')}` | `{r.get('offset_corrected_sign_pass', '')}` | `{r.get('offset_corrected_margin_pass', '')}` |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    MD.write_text("\n".join(lines), encoding="utf-8")
    print("sky130_extracted_frontend_two_stage_preamp")
    print(f"status,{report['status']}")
    print(f"corrected_margin_pass_count,{report['offset_corrected_margin_pass_count']}")
    print(f"json,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
