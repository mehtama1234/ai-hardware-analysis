#!/usr/bin/env python3
"""Dynamic charge-transfer proof for the measured two-stage preamp outputs.

The preamp is represented by ideal PWL sources whose calibration and target
levels come from a measured Sky130 preamp artifact.  The interface itself is
transistor-model based: series capacitors and gate bias resistors transfer the
target-minus-calibration change into an isolated regenerative latch.
"""
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
PREAMP = Path(os.environ.get("AIMC_DYNAMIC_PREAMP_JSON", str(EVIDENCE / "sky130-extracted-frontend-two-stage-preamp-pmos-cascode4-bias04.json"))).resolve()
STEM = os.environ.get("AIMC_DYNAMIC_OUTPUT_STEM", "sky130-dynamic-offset-cancelled-latch")
DECK = LAB / "spice" / f"{STEM}.sp"
OUT = EVIDENCE / f"{STEM}.json"
MD = EVIDENCE / f"{STEM}.md"


def measure(text: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not values:
        raise ValueError(name)
    return float(values[-1])


def build_deck(zero_p: float, zero_n: float, target_p: float, target_n: float, coupling_ff: float) -> str:
    gate_bias_v = float(os.environ.get("AIMC_DYNAMIC_GATE_BIAS_V", "0.9"))
    return f'''* Dynamic offset cancellation by capacitive charge transfer.
.lib "{Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"}" tt
.param vdd=1.8
.param cal_p={zero_p:.12f}
.param cal_n={zero_n:.12f}
.param target_p={target_p:.12f}
.param target_n={target_n:.12f}
VDD vdd 0 {{vdd}}
* Calibration is held until 2.00 ns; target output arrives before evaluation.
VOP out_p 0 PWL(0 {{cal_p}} 1.90n {{cal_p}} 2.20n {{target_p}} 6n {{target_p}})
VON out_n 0 PWL(0 {{cal_n}} 1.90n {{cal_n}} 2.20n {{target_n}} 6n {{target_n}})
VBIAS gate_bias 0 {gate_bias_v:.12g}
* Crossed polarity preserves the converter contract: latch output is out_n-out_p.
CCP out_p gate_n {coupling_ff:.12g}f
CCN out_n gate_p {coupling_ff:.12g}f
RGP gate_p gate_bias 100G
RGN gate_n gate_bias 100G
VCLK clk 0 PULSE(0 {{vdd}} 2.40n 20p 20p 3n 10n)
VCLKB clkb 0 PULSE({{vdd}} 0 2.40n 20p 20p 3n 10n)
* Dynamic latch; input gates are isolated from the source during regeneration.
XPREP vdd clkb lat_p vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XPREN vdd clkb lat_n vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLP lat_p lat_n vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLN lat_p lat_n eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XRP lat_n lat_p vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XRN lat_n lat_p eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XINP lat_p gate_p tail 0 sky130_fd_pr__nfet_01v8 W=10 L=0.15
XINN lat_n gate_n tail 0 sky130_fd_pr__nfet_01v8 W=10 L=0.15
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W=20 L=0.15
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W=20 L=0.15
CLATP lat_p 0 5f
CLATN lat_n 0 5f
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 chgtol=1e-16 gmin=1e-12
.ic v(gate_p)={gate_bias_v:.12g} v(gate_n)={gate_bias_v:.12g} v(lat_p)=1.8 v(lat_n)=1.8
.tran 2p 6n
.measure tran gate_p_cal_v FIND v(gate_p) AT=1.80n
.measure tran gate_n_cal_v FIND v(gate_n) AT=1.80n
.measure tran gate_p_eval_v FIND v(gate_p) AT=2.35n
.measure tran gate_n_eval_v FIND v(gate_n) AT=2.35n
.measure tran lat_p_final_v FIND v(lat_p) AT=5.60n
.measure tran lat_n_final_v FIND v(lat_n) AT=5.60n
.measure tran latch_output_diff_v PARAM='lat_n_final_v-lat_p_final_v'
.control
set noaskquit
run
.endc
.end
'''


def build_live_deck(diff_mv: float, coupling_ff: float, zero_p: float, zero_n: float, target_p: float, target_n: float) -> str:
    """Attach the dynamic interface to the live extracted frontend.

    The input starts at the common-mode value, steps after the calibration
    interval, and is sampled by the extracted frontend before latch evaluate.
    """
    dv = diff_mv / 1000.0
    supply_v = float(os.environ.get("AIMC_DYNAMIC_SUPPLY_V", os.environ.get("AIMC_TWO_STAGE_SUPPLY_V", "1.8")))
    common_mode_v = supply_v / 2.0
    vinp = common_mode_v + dv / 2.0
    vinn = common_mode_v - dv / 2.0
    input_delay = float(os.environ.get("AIMC_DYNAMIC_INPUT_DELAY_NS", "3.00"))
    sample_delay = float(os.environ.get("AIMC_DYNAMIC_SAMPLE_DELAY_NS", "3.60"))
    latch_delay = float(os.environ.get("AIMC_DYNAMIC_LATCH_DELAY_NS", "5.00"))
    clamp_release = float(os.environ.get("AIMC_DYNAMIC_CLAMP_RELEASE_NS", "2.80"))
    gate_bias_v = float(os.environ.get("AIMC_DYNAMIC_GATE_BIAS_V", str(common_mode_v)))
    use_buffer = os.environ.get("AIMC_DYNAMIC_COMMON_MODE_BUFFER") == "1"
    buffer_w = float(os.environ.get("AIMC_DYNAMIC_BUFFER_W_UM", "1"))
    buffer_rd = float(os.environ.get("AIMC_DYNAMIC_BUFFER_RD_OHM", "500000"))
    use_second_buffer = os.environ.get("AIMC_DYNAMIC_SECOND_BUFFER") == "1"
    second_buffer_w = float(os.environ.get("AIMC_DYNAMIC_SECOND_BUFFER_W_UM", "1"))
    second_buffer_rd = float(os.environ.get("AIMC_DYNAMIC_SECOND_BUFFER_RD_OHM", "500000"))
    use_active_receiver = os.environ.get("AIMC_DYNAMIC_ACTIVE_DIFF_RECEIVER") == "1"
    use_active_receiver_ac_input = os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_AC_INPUT") == "1"
    active_receiver_input_coupling_ff = float(os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_INPUT_COUPLING_FF", "100"))
    use_offset_cancelled_source = os.environ.get("AIMC_DYNAMIC_OFFSET_CANCELLED_SOURCE") == "1"
    active_receiver_w = float(os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_W_UM", "2"))
    active_receiver_rd = float(os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_RD_OHM", "200000"))
    active_receiver_trim_diff_v = float(os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_TRIM_DIFF_V", "0"))
    active_receiver_trim_bias_v = float(os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_TRIM_BIAS_V", "0.7"))
    active_receiver_trim_w = float(os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_TRIM_W_UM", "1"))
    use_receiver_level_shift = os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_LEVEL_SHIFT") == "1"
    receiver_level_shift_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_LEVEL_SHIFT_W_UM", "2"))
    receiver_level_shift_rd = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_LEVEL_SHIFT_RD_OHM", "500000"))
    use_receiver_gain_stage = os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_GAIN_STAGE") == "1"
    receiver_gain_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_W_UM", "2"))
    receiver_gain_rd = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_RD_OHM", "100000"))
    receiver_gain_tail_a = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_TAIL_A", "4e-6"))
    receiver_gain_input_top_ohm = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_INPUT_TOP_OHM", "1000000"))
    receiver_gain_input_bottom_ohm = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_INPUT_BOTTOM_OHM", "1000000"))
    use_receiver_gain_ac_input = os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_AC_INPUT") == "1"
    receiver_gain_input_coupling_ff = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_INPUT_COUPLING_FF", "100"))
    use_receiver_gain_reset = os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_RESET") == "1"
    receiver_gain_trim_diff_v = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_TRIM_DIFF_V", "0"))
    receiver_gain_trim_bias_v = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_TRIM_BIAS_V", "0.7"))
    receiver_gain_trim_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_TRIM_W_UM", "0.5"))
    use_receiver_regen_stage = os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_REGEN_STAGE") == "1"
    receiver_regen_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_W_UM", "2"))
    receiver_regen_tail_a = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_TAIL_A", "2e-6"))
    receiver_regen_reset_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_RESET_W_UM", "4"))
    use_receiver_regen_equalizer = os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_EQUALIZER") == "1"
    receiver_regen_equalizer_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_EQUALIZER_W_UM", "2"))
    use_receiver_regen_input_reset = os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_INPUT_RESET") == "1"
    receiver_regen_input_reset_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_INPUT_RESET_W_UM", "2"))
    use_receiver_regen_ac_input = os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_AC_INPUT") == "1"
    receiver_regen_input_coupling_ff = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_INPUT_COUPLING_FF", "20"))
    receiver_regen_trim_diff_v = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_TRIM_DIFF_V", "0"))
    receiver_regen_trim_bias_v = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_TRIM_BIAS_V", "0.7"))
    receiver_regen_trim_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_TRIM_W_UM", "0.5"))
    crossed = os.environ.get("AIMC_DYNAMIC_CROSSED_POLARITY", "1") == "1"
    use_equalizer = os.environ.get("AIMC_DYNAMIC_OUTPUT_EQUALIZER", "1") == "1"
    latch_input_w = float(os.environ.get("AIMC_DYNAMIC_LATCH_INPUT_W_UM", "10"))
    latch_tail_w = float(os.environ.get("AIMC_DYNAMIC_LATCH_TAIL_W_UM", "20"))
    use_source_isolation = os.environ.get("AIMC_DYNAMIC_SOURCE_ISOLATION") == "1"
    gate_override_diff_mv = os.environ.get("AIMC_DYNAMIC_GATE_OVERRIDE_DIFF_MV")
    gate_bias_r_ohm = float(os.environ.get("AIMC_DYNAMIC_GATE_BIAS_R_OHM", "1e11"))
    use_latch_input_hold = os.environ.get("AIMC_DYNAMIC_LATCH_INPUT_HOLD") == "1"
    latch_hold_cap_ff = float(os.environ.get("AIMC_DYNAMIC_LATCH_HOLD_CAP_FF", "10"))
    latch_hold_switch_w = float(os.environ.get("AIMC_DYNAMIC_LATCH_HOLD_SWITCH_W_UM", "4"))
    latch_hold_bias_r_ohm = float(os.environ.get("AIMC_DYNAMIC_LATCH_HOLD_BIAS_R_OHM", "1e8"))
    hold_release = float(os.environ.get("AIMC_DYNAMIC_LATCH_HOLD_RELEASE_NS", str(max(latch_delay - 0.5, 0.1))))
    deck = make_deck(diff_mv)
    lines = []
    for line in deck.splitlines():
        if line.startswith("VSP sp 0 PULSE("):
            line = f"VSP sp 0 PULSE({common_mode_v:.12g} {vinp:.12f} {input_delay:.3f}n 20p 20p 20n 40n)"
        elif line.startswith("VSN sn 0 PULSE("):
            line = f"VSN sn 0 PULSE({common_mode_v:.12g} {vinn:.12f} {input_delay:.3f}n 20p 20p 20n 40n)"
        elif line.startswith("VCS clk_sample 0 PULSE("):
            line = f"VCS clk_sample 0 PULSE(0 {supply_v:.12g} {sample_delay:.3f}n 20p 20p 5n 10n)"
        elif line.startswith("VCL clk_latch 0 PULSE("):
            line = f"VCL clk_latch 0 PULSE(0 {supply_v:.12g} {latch_delay:.3f}n 20p 20p 5n 10n)"
        elif line == ".tran 20p 3n":
            line = ".tran 20p 12n"
        lines.append(line)
    deck = "\n".join(lines) + "\n"
    corrected_diff = (target_p - target_n) - (zero_p - zero_n)
    corrected_source_block = "" if not use_offset_cancelled_source else f'''* Diagnostic idealization of a zero-input auto-zero stage.
VCALOUTP cal_out_p 0 PWL(0 {common_mode_v:.12g} 2.70n {common_mode_v:.12g} 3.00n {common_mode_v + corrected_diff / 2.0:.12g} 12n {common_mode_v + corrected_diff / 2.0:.12g})
VCALOUTN cal_out_n 0 PWL(0 {common_mode_v:.12g} 2.70n {common_mode_v:.12g} 3.00n {common_mode_v - corrected_diff / 2.0:.12g} 12n {common_mode_v - corrected_diff / 2.0:.12g})
'''
    if use_offset_cancelled_source:
        deck += corrected_source_block
    buffer_block = "" if not use_buffer else f'''RBUF_P vdd buf_p {buffer_rd:.12g}
RBUF_N vdd buf_n {buffer_rd:.12g}
XBUF_P buf_p out_p 0 0 sky130_fd_pr__nfet_01v8 W={buffer_w:.12g} L=0.15
XBUF_N buf_n out_n 0 0 sky130_fd_pr__nfet_01v8 W={buffer_w:.12g} L=0.15
'''
    drive_p = "buf_p" if use_buffer else "out_p"
    drive_n = "buf_n" if use_buffer else "out_n"
    if use_offset_cancelled_source:
        drive_p, drive_n = "cal_out_p", "cal_out_n"
    second_buffer_block = "" if not use_second_buffer else f'''RBUF2_P vdd buf2_p {second_buffer_rd:.12g}
RBUF2_N vdd buf2_n {second_buffer_rd:.12g}
XBUF2_P buf2_p {drive_p} 0 0 sky130_fd_pr__nfet_01v8 W={second_buffer_w:.12g} L=0.15
XBUF2_N buf2_n {drive_n} 0 0 sky130_fd_pr__nfet_01v8 W={second_buffer_w:.12g} L=0.15
'''
    if use_second_buffer:
        drive_p, drive_n = "buf2_p", "buf2_n"
    cap_gate_p = "gate_n" if crossed else "gate_p"
    cap_gate_n = "gate_p" if crossed else "gate_n"
    equalizer = "" if not use_equalizer else f"VRESETB resetb 0 PULSE({supply_v:.12g} 0 {latch_delay:.3f}n 20p 20p 5n 10n)\nXEQ lat_p resetb lat_n 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15\n"
    source_isolation = "" if not use_source_isolation else f"VISO iso_ctrl 0 PULSE({supply_v:.12g} 0 {latch_delay:.3f}n 20p 20p 20n 40n)\nXISOP {drive_p} iso_p iso_ctrl 0 sky130_fd_pr__nfet_01v8 W=4 L=0.15\nXISON {drive_n} iso_n iso_ctrl 0 sky130_fd_pr__nfet_01v8 W=4 L=0.15\n"
    cap_source_p = "iso_p" if use_source_isolation else drive_p
    cap_source_n = "iso_n" if use_source_isolation else drive_n
    receiver_input_block = (f'''CRXINP {cap_source_p} rx_input_p {active_receiver_input_coupling_ff:.12g}f
CRXINN {cap_source_n} rx_input_n {active_receiver_input_coupling_ff:.12g}f
RRXBIASP rx_input_p gate_bias 1000000
RRXBIASN rx_input_n gate_bias 1000000
''' if use_active_receiver_ac_input else "")
    receiver_gate_p = "rx_input_p" if use_active_receiver_ac_input else cap_source_p
    receiver_gate_n = "rx_input_n" if use_active_receiver_ac_input else cap_source_n
    active_receiver = "" if not use_active_receiver else f'''{receiver_input_block}RRXP rx_p 0 {active_receiver_rd:.12g}
RRXN rx_n 0 {active_receiver_rd:.12g}
XRXP rx_p {receiver_gate_p} vdd vdd sky130_fd_pr__pfet_01v8 W={active_receiver_w:.12g} L=0.15
XRXN rx_n {receiver_gate_n} vdd vdd sky130_fd_pr__pfet_01v8 W={active_receiver_w:.12g} L=0.15
VTRIMBP trim_bias_p 0 {active_receiver_trim_bias_v - active_receiver_trim_diff_v / 2.0:.12g}
VTRIMBN trim_bias_n 0 {active_receiver_trim_bias_v + active_receiver_trim_diff_v / 2.0:.12g}
XTRIMP rx_p trim_bias_p 0 0 sky130_fd_pr__nfet_01v8 W={active_receiver_trim_w:.12g} L=0.15
XTRIMN rx_n trim_bias_n 0 0 sky130_fd_pr__nfet_01v8 W={active_receiver_trim_w:.12g} L=0.15
'''
    if use_active_receiver:
        cap_source_p, cap_source_n = "rx_p", "rx_n"
    receiver_level_shift = "" if not use_receiver_level_shift else f'''RLSHIFTP level_p 0 {receiver_level_shift_rd:.12g}
RLSHIFTN level_n 0 {receiver_level_shift_rd:.12g}
XLSHIFTP 0 rx_p level_p vdd sky130_fd_pr__pfet_01v8 W={receiver_level_shift_w:.12g} L=0.15
XLSHIFTN 0 rx_n level_n vdd sky130_fd_pr__pfet_01v8 W={receiver_level_shift_w:.12g} L=0.15
'''
    if use_receiver_level_shift:
        cap_source_p, cap_source_n = "level_p", "level_n"
    receiver_gain_reset = "" if not use_receiver_gain_reset else f'''VGAINRESET gain_reset 0 PULSE({supply_v:.12g} 0 {clamp_release:.3f}n 20p 20p 20n 40n)
XGAINRP gain_p gain_reset gate_bias 0 sky130_fd_pr__nfet_01v8 W=4 L=0.15
XGAINRN gain_n gain_reset gate_bias 0 sky130_fd_pr__nfet_01v8 W=4 L=0.15
'''
    gain_input_block = (f'''CGAININP rx_p gain_in_p {receiver_gain_input_coupling_ff:.12g}f
CGAININN rx_n gain_in_n {receiver_gain_input_coupling_ff:.12g}f
RGAINBIASP gain_in_p gate_bias {receiver_gain_input_bottom_ohm:.12g}
RGAINBIASN gain_in_n gate_bias {receiver_gain_input_bottom_ohm:.12g}
''' if use_receiver_gain_ac_input else f'''RGAININP rx_p gain_in_p {receiver_gain_input_top_ohm:.12g}
RGAININN rx_n gain_in_n {receiver_gain_input_top_ohm:.12g}
RGAINBIASP gain_in_p 0 {receiver_gain_input_bottom_ohm:.12g}
RGAINBIASN gain_in_n 0 {receiver_gain_input_bottom_ohm:.12g}
''')
    receiver_gain_stage = "" if not use_receiver_gain_stage else f'''{gain_input_block}
RGAINP vdd gain_p {receiver_gain_rd:.12g}
RGAINN vdd gain_n {receiver_gain_rd:.12g}
XGAINP gain_p gain_in_p gain_tail 0 sky130_fd_pr__nfet_01v8 W={receiver_gain_w:.12g} L=0.15
XGAINN gain_n gain_in_n gain_tail 0 sky130_fd_pr__nfet_01v8 W={receiver_gain_w:.12g} L=0.15
IGAIN gain_tail 0 {receiver_gain_tail_a:.12g}
'''
    if use_receiver_gain_stage:
        receiver_gain_stage += receiver_gain_reset
        receiver_gain_stage += f'''VGAINTRIMP gain_trim_p 0 {receiver_gain_trim_bias_v - receiver_gain_trim_diff_v / 2.0:.12g}
VGAINTRIMN gain_trim_n 0 {receiver_gain_trim_bias_v + receiver_gain_trim_diff_v / 2.0:.12g}
XGAINTRIMP gain_p gain_trim_p 0 0 sky130_fd_pr__nfet_01v8 W={receiver_gain_trim_w:.12g} L=0.15
XGAINTRIMN gain_n gain_trim_n 0 0 sky130_fd_pr__nfet_01v8 W={receiver_gain_trim_w:.12g} L=0.15
'''
    if use_receiver_gain_stage:
        cap_source_p, cap_source_n = "gain_p", "gain_n"
    regen_input_p = "gain_p" if use_receiver_gain_stage else cap_source_p
    regen_input_n = "gain_n" if use_receiver_gain_stage else cap_source_n
    regen_input_block = (f'''CREGENINP {regen_input_p} regen_in_p {receiver_regen_input_coupling_ff:.12g}f
CREGENINN {regen_input_n} regen_in_n {receiver_regen_input_coupling_ff:.12g}f
RREGENINBIASP regen_in_p gate_bias 1000000
RREGENINBIASN regen_in_n gate_bias 1000000
''' if use_receiver_regen_ac_input else f'''RREGENINP {regen_input_p} regen_in_p 1000000
RREGENINN {regen_input_n} regen_in_n 1000000
RREGENBIASP regen_in_p 0 1000000
RREGENBIASN regen_in_n 0 1000000
''')
    regen_input_reset_block = "" if not use_receiver_regen_input_reset else f'''XREGENRINP regen_in_p regen_reset gate_bias 0 sky130_fd_pr__nfet_01v8 W={receiver_regen_input_reset_w:.12g} L=0.15
XREGENRINN regen_in_n regen_reset gate_bias 0 sky130_fd_pr__nfet_01v8 W={receiver_regen_input_reset_w:.12g} L=0.15
'''
    receiver_regen_stage = "" if not use_receiver_regen_stage else f'''{regen_input_block}
VREGENRESET regen_reset 0 PULSE({supply_v:.12g} 0 {clamp_release:.3f}n 20p 20p 20n 40n)
{regen_input_reset_block}
XREGENRP regen_p regen_reset gate_bias 0 sky130_fd_pr__nfet_01v8 W={receiver_regen_reset_w:.12g} L=0.15
XREGENRN regen_n regen_reset gate_bias 0 sky130_fd_pr__nfet_01v8 W={receiver_regen_reset_w:.12g} L=0.15
{"XREGENEQ regen_p regen_n regen_reset 0 sky130_fd_pr__nfet_01v8 W=" + f"{receiver_regen_equalizer_w:.12g}" + " L=0.15" if use_receiver_regen_equalizer else ""}
XREGENCP regen_p regen_n vdd vdd sky130_fd_pr__pfet_01v8 W={receiver_regen_w:.12g} L=0.15
XREGENCN regen_p regen_n 0 0 sky130_fd_pr__nfet_01v8 W={receiver_regen_w:.12g} L=0.15
XREGENDP regen_n regen_p vdd vdd sky130_fd_pr__pfet_01v8 W={receiver_regen_w:.12g} L=0.15
XREGENDN regen_n regen_p 0 0 sky130_fd_pr__nfet_01v8 W={receiver_regen_w:.12g} L=0.15
XREGENINP regen_p regen_in_p regen_tail 0 sky130_fd_pr__nfet_01v8 W={receiver_regen_w:.12g} L=0.15
XREGENINN regen_n regen_in_n regen_tail 0 sky130_fd_pr__nfet_01v8 W={receiver_regen_w:.12g} L=0.15
IREGEN regen_tail 0 {receiver_regen_tail_a:.12g}
VREGENTRIMP regen_trim_p 0 {receiver_regen_trim_bias_v - receiver_regen_trim_diff_v / 2.0:.12g}
VREGENTRIMN regen_trim_n 0 {receiver_regen_trim_bias_v + receiver_regen_trim_diff_v / 2.0:.12g}
XREGENTRIMP regen_p regen_trim_p 0 0 sky130_fd_pr__nfet_01v8 W={receiver_regen_trim_w:.12g} L=0.15
XREGENTRIMN regen_n regen_trim_n 0 0 sky130_fd_pr__nfet_01v8 W={receiver_regen_trim_w:.12g} L=0.15
'''
    if use_receiver_regen_stage:
        cap_source_p, cap_source_n = "regen_p", "regen_n"
    if gate_override_diff_mv is None:
        transfer_block = f"CCP {cap_source_p} {cap_gate_p} {coupling_ff:.12g}f\nCCN {cap_source_n} {cap_gate_n} {coupling_ff:.12g}f"
    else:
        forced_diff = -float(gate_override_diff_mv) / 1000.0 if diff_mv > 0 else float(gate_override_diff_mv) / 1000.0
        transfer_block = f"VGP gate_p 0 {gate_bias_v + forced_diff / 2.0:.12g}\nVGN gate_n 0 {gate_bias_v - forced_diff / 2.0:.12g}"
    input_hold = ""
    latch_gate_p, latch_gate_n = "gate_p", "gate_n"
    if use_latch_input_hold:
        latch_gate_p, latch_gate_n = "latch_gate_p", "latch_gate_n"
        hold_source_p = cap_source_p if use_active_receiver else "gate_p"
        hold_source_n = cap_source_n if use_active_receiver else "gate_n"
        input_hold = f"VTRACK track_ctrl 0 PULSE({supply_v:.12g} 0 {hold_release:.3f}n 20p 20p 20n 40n)\nXTRACKP {hold_source_p} track_ctrl latch_gate_p 0 sky130_fd_pr__nfet_01v8 W={latch_hold_switch_w:.12g} L=0.15\nXTRACKN {hold_source_n} track_ctrl latch_gate_n 0 sky130_fd_pr__nfet_01v8 W={latch_hold_switch_w:.12g} L=0.15\nCHOLDP latch_gate_p gate_bias {latch_hold_cap_ff:.12g}f\nCHOLDN latch_gate_n gate_bias {latch_hold_cap_ff:.12g}f\nRHOLDP latch_gate_p gate_bias {latch_hold_bias_r_ohm:.12g}\nRHOLDN latch_gate_n gate_bias {latch_hold_bias_r_ohm:.12g}\n"
    insertion = f'''* Live extracted preamp with dynamic offset-transfer interface.
VBIAS gate_bias 0 {gate_bias_v:.12g}
VCAL cal_ctrl 0 PULSE({supply_v:.12g} 0 {clamp_release:.3f}n 20p 20p 20n 40n)
XCALP gate_p cal_ctrl gate_bias 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
XCALN gate_n cal_ctrl gate_bias 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
{buffer_block}{second_buffer_block}{source_isolation}{active_receiver}{receiver_level_shift}{receiver_gain_stage}{receiver_regen_stage}{transfer_block}
{equalizer}
{input_hold}
RGP gate_p gate_bias {gate_bias_r_ohm:.12g}
RGN gate_n gate_bias {gate_bias_r_ohm:.12g}
VCLB clkb 0 PULSE({supply_v:.12g} 0 {latch_delay:.3f}n 20p 20p 5n 10n)
XPREP vdd clk_latch lat_p vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XPREN vdd clk_latch lat_n vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLP lat_p lat_n vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XLN lat_p lat_n eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XRP lat_n lat_p vdd vdd sky130_fd_pr__pfet_01v8 W=6 L=0.15
XRN lat_n lat_p eval 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XINP lat_p {latch_gate_p} tail 0 sky130_fd_pr__nfet_01v8 W={latch_input_w:.12g} L=0.15
XINN lat_n {latch_gate_n} tail 0 sky130_fd_pr__nfet_01v8 W={latch_input_w:.12g} L=0.15
XTAIL tail clk_latch 0 0 sky130_fd_pr__nfet_01v8 W={latch_tail_w:.12g} L=0.15
XEVAL eval clk_latch 0 0 sky130_fd_pr__nfet_01v8 W={latch_tail_w:.12g} L=0.15
CLATP lat_p 0 5f
CLATN lat_n 0 5f
'''
    deck = deck.replace(".ic v(sense_p)=0.9", insertion + f".ic v(sense_p)={common_mode_v:.12g} v(gate_p)={gate_bias_v:.12g} v(gate_n)={gate_bias_v:.12g}")
    # Measure calibration after the clamp releases but before the live input
    # step.  Measuring near latch evaluation would incorrectly label the
    # target response as the zero-input calibration state.
    cal_measure = clamp_release + 0.2
    eval_measure = latch_delay + 0.35
    final_measure = latch_delay + 4.6
    gate_probe_p = "latch_gate_p" if use_latch_input_hold else "gate_p"
    gate_probe_n = "latch_gate_n" if use_latch_input_hold else "gate_n"
    deck = deck.replace(".control\nset noaskquit", f".measure tran live_out_p_v FIND v(out_p) AT={cal_measure:.3f}n\n.measure tran live_out_n_v FIND v(out_n) AT={cal_measure:.3f}n\n.measure tran gate_p_cal_v FIND v({gate_probe_p}) AT={cal_measure:.3f}n\n.measure tran gate_n_cal_v FIND v({gate_probe_n}) AT={cal_measure:.3f}n\n.measure tran gate_p_eval_v FIND v({gate_probe_p}) AT={eval_measure:.3f}n\n.measure tran gate_n_eval_v FIND v({gate_probe_n}) AT={eval_measure:.3f}n\n.measure tran lat_p_final_v FIND v(lat_p) AT={final_measure:.3f}n\n.measure tran lat_n_final_v FIND v(lat_n) AT={final_measure:.3f}n\n.measure tran latch_output_diff_v PARAM='lat_n_final_v-lat_p_final_v'\n.control\nset noaskquit")
    if use_receiver_gain_stage:
        deck = deck.replace(".control\nset noaskquit", f".measure tran gain_p_v FIND v(gain_p) AT={cal_measure:.3f}n\n.measure tran gain_n_v FIND v(gain_n) AT={cal_measure:.3f}n\n.measure tran gain_diff_v PARAM='gain_p_v-gain_n_v'\n.control\nset noaskquit")
    if use_active_receiver:
        deck = deck.replace(".control\nset noaskquit", f".measure tran active_rx_p_v FIND v(rx_p) AT={cal_measure:.3f}n\n.measure tran active_rx_n_v FIND v(rx_n) AT={cal_measure:.3f}n\n.measure tran active_rx_p_eval_v FIND v(rx_p) AT={eval_measure:.3f}n\n.measure tran active_rx_n_eval_v FIND v(rx_n) AT={eval_measure:.3f}n\n.control\nset noaskquit")
    return deck


def main() -> int:
    source = json.loads(PREAMP.read_text(encoding="utf-8"))
    rows = source["rows"]
    zero = next(row for row in rows if float(row["input_diff_mv"]) == 0.0)
    zero_p = float(zero.get("out_p_v", zero.get("outp_2n_v")))
    zero_n = float(zero.get("out_n_v", zero.get("outn_2n_v")))
    coupling_ff = float(os.environ.get("AIMC_DYNAMIC_COUPLING_FF", "100"))
    latch_delay = float(os.environ.get("AIMC_DYNAMIC_LATCH_DELAY_NS", "5.00"))
    live_preamp = os.environ.get("AIMC_DYNAMIC_LIVE_PREAMP") == "1"
    use_offset_cancelled_source = os.environ.get("AIMC_DYNAMIC_OFFSET_CANCELLED_SOURCE") == "1"
    use_buffer = os.environ.get("AIMC_DYNAMIC_COMMON_MODE_BUFFER") == "1"
    buffer_w = float(os.environ.get("AIMC_DYNAMIC_BUFFER_W_UM", "1"))
    buffer_rd = float(os.environ.get("AIMC_DYNAMIC_BUFFER_RD_OHM", "500000"))
    use_second_buffer = os.environ.get("AIMC_DYNAMIC_SECOND_BUFFER") == "1"
    second_buffer_w = float(os.environ.get("AIMC_DYNAMIC_SECOND_BUFFER_W_UM", "1"))
    second_buffer_rd = float(os.environ.get("AIMC_DYNAMIC_SECOND_BUFFER_RD_OHM", "500000"))
    use_active_receiver = os.environ.get("AIMC_DYNAMIC_ACTIVE_DIFF_RECEIVER") == "1"
    use_active_receiver_ac_input = os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_AC_INPUT") == "1"
    active_receiver_input_coupling_ff = float(os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_INPUT_COUPLING_FF", "100"))
    active_receiver_w = float(os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_W_UM", "2"))
    active_receiver_rd = float(os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_RD_OHM", "200000"))
    active_receiver_trim_diff_v = float(os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_TRIM_DIFF_V", "0"))
    active_receiver_trim_bias_v = float(os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_TRIM_BIAS_V", "0.7"))
    active_receiver_trim_w = float(os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_TRIM_W_UM", "1"))
    use_receiver_level_shift = os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_LEVEL_SHIFT") == "1"
    receiver_level_shift_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_LEVEL_SHIFT_W_UM", "2"))
    receiver_level_shift_rd = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_LEVEL_SHIFT_RD_OHM", "500000"))
    use_receiver_gain_stage = os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_GAIN_STAGE") == "1"
    receiver_gain_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_W_UM", "2"))
    receiver_gain_rd = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_RD_OHM", "100000"))
    receiver_gain_tail_a = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_TAIL_A", "4e-6"))
    receiver_gain_input_top_ohm = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_INPUT_TOP_OHM", "1000000"))
    receiver_gain_input_bottom_ohm = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_INPUT_BOTTOM_OHM", "1000000"))
    use_receiver_gain_reset = os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_RESET") == "1"
    receiver_gain_trim_diff_v = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_TRIM_DIFF_V", "0"))
    receiver_gain_trim_bias_v = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_TRIM_BIAS_V", "0.7"))
    receiver_gain_trim_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_GAIN_TRIM_W_UM", "0.5"))
    use_receiver_regen_stage = os.environ.get("AIMC_DYNAMIC_ACTIVE_RECEIVER_REGEN_STAGE") == "1"
    receiver_regen_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_W_UM", "2"))
    receiver_regen_tail_a = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_TAIL_A", "2e-6"))
    receiver_regen_reset_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_RESET_W_UM", "4"))
    use_receiver_regen_equalizer = os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_EQUALIZER") == "1"
    receiver_regen_equalizer_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_EQUALIZER_W_UM", "2"))
    use_receiver_regen_input_reset = os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_INPUT_RESET") == "1"
    receiver_regen_input_reset_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_INPUT_RESET_W_UM", "2"))
    receiver_regen_trim_diff_v = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_TRIM_DIFF_V", "0"))
    receiver_regen_trim_bias_v = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_TRIM_BIAS_V", "0.7"))
    receiver_regen_trim_w = float(os.environ.get("AIMC_DYNAMIC_RECEIVER_REGEN_TRIM_W_UM", "0.5"))
    crossed = os.environ.get("AIMC_DYNAMIC_CROSSED_POLARITY", "1") == "1"
    use_equalizer = os.environ.get("AIMC_DYNAMIC_OUTPUT_EQUALIZER", "1") == "1"
    latch_input_w = float(os.environ.get("AIMC_DYNAMIC_LATCH_INPUT_W_UM", "10"))
    latch_tail_w = float(os.environ.get("AIMC_DYNAMIC_LATCH_TAIL_W_UM", "20"))
    use_source_isolation = os.environ.get("AIMC_DYNAMIC_SOURCE_ISOLATION") == "1"
    gate_override_diff_mv = os.environ.get("AIMC_DYNAMIC_GATE_OVERRIDE_DIFF_MV")
    gate_bias_r_ohm = float(os.environ.get("AIMC_DYNAMIC_GATE_BIAS_R_OHM", "1e11"))
    use_latch_input_hold = os.environ.get("AIMC_DYNAMIC_LATCH_INPUT_HOLD") == "1"
    latch_hold_cap_ff = float(os.environ.get("AIMC_DYNAMIC_LATCH_HOLD_CAP_FF", "10"))
    latch_hold_switch_w = float(os.environ.get("AIMC_DYNAMIC_LATCH_HOLD_SWITCH_W_UM", "4"))
    latch_hold_bias_r_ohm = float(os.environ.get("AIMC_DYNAMIC_LATCH_HOLD_BIAS_R_OHM", "1e8"))
    hold_release = float(os.environ.get("AIMC_DYNAMIC_LATCH_HOLD_RELEASE_NS", str(max(latch_delay - 0.5, 0.1))))
    result_rows = []
    for row in rows:
        if float(row["input_diff_mv"]) == 0.0:
            continue
        target_p = float(row.get("out_p_v", row.get("outp_2n_v")))
        target_n = float(row.get("out_n_v", row.get("outn_2n_v")))
        deck = build_live_deck(float(row["input_diff_mv"]), coupling_ff, zero_p, zero_n, target_p, target_n) if live_preamp else build_deck(zero_p, zero_n, target_p, target_n, coupling_ff)
        DECK.write_text(deck, encoding="utf-8")
        try:
            result = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=120)
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            result = None
            timed_out = True
            item = {"input_diff_mv": float(row["input_diff_mv"]), "measured": False, "returncode": None, "timeout": True, "preamp_zero_diff_v": zero_p - zero_n, "preamp_target_diff_v": target_p - target_n, "error_excerpt": str(exc)[-1200:]}
        if timed_out:
            result_rows.append(item)
            continue
        item = {"input_diff_mv": float(row["input_diff_mv"]), "measured": result.returncode == 0, "returncode": result.returncode, "preamp_zero_diff_v": zero_p - zero_n, "preamp_target_diff_v": target_p - target_n}
        if result.returncode == 0:
            output = measure(result.stdout, "latch_output_diff_v")
            gate_cal = measure(result.stdout, "gate_p_cal_v") - measure(result.stdout, "gate_n_cal_v")
            gate_eval = measure(result.stdout, "gate_p_eval_v") - measure(result.stdout, "gate_n_eval_v")
            gate_p_eval = measure(result.stdout, "gate_p_eval_v")
            gate_n_eval = measure(result.stdout, "gate_n_eval_v")
            item.update({"gate_diff_cal_v": gate_cal, "gate_diff_eval_v": gate_eval, "gate_common_mode_eval_v": (gate_p_eval + gate_n_eval) / 2.0, "gate_p_eval_v": gate_p_eval, "gate_n_eval_v": gate_n_eval, "latch_output_diff_v": output, "measured_sign": 1 if output > 0 else -1 if output < 0 else 0, "expected_sign": -1 if float(row["input_diff_mv"]) > 0 else 1, "polarity_pass": (output < 0) == (float(row["input_diff_mv"]) > 0) and abs(output) >= 0.9})
            if live_preamp:
                item.update({"live_out_p_v": measure(result.stdout, "live_out_p_v"), "live_out_n_v": measure(result.stdout, "live_out_n_v"), "live_output_diff_v": measure(result.stdout, "live_out_p_v") - measure(result.stdout, "live_out_n_v")})
            if use_receiver_gain_stage:
                item.update({"gain_p_v": measure(result.stdout, "gain_p_v"), "gain_n_v": measure(result.stdout, "gain_n_v"), "gain_diff_v": measure(result.stdout, "gain_diff_v")})
            if use_active_receiver:
                item.update({"active_receiver_p_v": measure(result.stdout, "active_rx_p_v"), "active_receiver_n_v": measure(result.stdout, "active_rx_n_v"), "active_receiver_diff_v": measure(result.stdout, "active_rx_p_v") - measure(result.stdout, "active_rx_n_v"), "active_receiver_p_eval_v": measure(result.stdout, "active_rx_p_eval_v"), "active_receiver_n_eval_v": measure(result.stdout, "active_rx_n_eval_v")})
        else:
            item["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        result_rows.append(item)
    passing = sum(1 for row in result_rows if row.get("polarity_pass"))
    claim_allowed = "connects a live extracted Sky130 frontend/preamp deck to a dynamic offset-cancellation latch interface" if live_preamp else "tests clocked capacitive transfer of measured preamp changes into an isolated Sky130 latch"
    report = {"result_type": "sky130_dynamic_offset_cancelled_latch", "status": "dynamic_offset_cancelled_latch_passed_ready_for_coupled_preamp" if passing == len(result_rows) else "dynamic_offset_cancelled_latch_open", "source_preamp": str(PREAMP.relative_to(ROOT)) if PREAMP.is_relative_to(ROOT) else str(PREAMP), "live_extracted_preamp": live_preamp, "ideal_offset_cancelled_source": use_offset_cancelled_source, "common_mode_buffer": use_buffer, "buffer_width_um": buffer_w, "buffer_load_ohm": buffer_rd, "second_buffer": use_second_buffer, "second_buffer_width_um": second_buffer_w, "second_buffer_load_ohm": second_buffer_rd, "active_differential_receiver": use_active_receiver, "active_receiver_ac_input": use_active_receiver_ac_input, "active_receiver_input_coupling_ff": active_receiver_input_coupling_ff, "active_receiver_width_um": active_receiver_w, "active_receiver_load_ohm": active_receiver_rd, "active_receiver_trim_diff_v": active_receiver_trim_diff_v, "active_receiver_trim_bias_v": active_receiver_trim_bias_v, "active_receiver_trim_width_um": active_receiver_trim_w, "receiver_level_shift": use_receiver_level_shift, "receiver_level_shift_width_um": receiver_level_shift_w, "receiver_level_shift_load_ohm": receiver_level_shift_rd, "receiver_gain_stage": use_receiver_gain_stage, "receiver_gain_reset": use_receiver_gain_reset, "receiver_gain_width_um": receiver_gain_w, "receiver_gain_load_ohm": receiver_gain_rd, "receiver_gain_tail_a": receiver_gain_tail_a, "receiver_gain_input_top_ohm": receiver_gain_input_top_ohm, "receiver_gain_input_bottom_ohm": receiver_gain_input_bottom_ohm, "receiver_gain_trim_diff_v": receiver_gain_trim_diff_v, "receiver_gain_trim_bias_v": receiver_gain_trim_bias_v, "receiver_gain_trim_width_um": receiver_gain_trim_w, "receiver_regenerative_stage": use_receiver_regen_stage, "receiver_regenerative_width_um": receiver_regen_w, "receiver_regenerative_tail_a": receiver_regen_tail_a, "receiver_regenerative_reset_width_um": receiver_regen_reset_w, "receiver_regenerative_equalizer": use_receiver_regen_equalizer, "receiver_regenerative_equalizer_width_um": receiver_regen_equalizer_w, "receiver_regenerative_input_reset": use_receiver_regen_input_reset, "receiver_regenerative_input_reset_width_um": receiver_regen_input_reset_w, "receiver_regenerative_trim_diff_v": receiver_regen_trim_diff_v, "receiver_regenerative_trim_bias_v": receiver_regen_trim_bias_v, "receiver_regenerative_trim_width_um": receiver_regen_trim_w, "crossed_polarity": crossed, "output_equalizer": use_equalizer, "source_isolation": use_source_isolation, "latch_input_hold": use_latch_input_hold, "latch_hold_cap_ff": latch_hold_cap_ff, "latch_hold_switch_width_um": latch_hold_switch_w, "latch_hold_bias_resistance_ohm": latch_hold_bias_r_ohm, "latch_hold_release_ns": hold_release, "gate_override_diff_mv": float(gate_override_diff_mv) if gate_override_diff_mv is not None else None, "gate_bias_resistance_ohm": gate_bias_r_ohm, "latch_input_width_um": latch_input_w, "latch_tail_width_um": latch_tail_w, "coupling_cap_ff": coupling_ff, "calibration_zero_diff_v": zero_p - zero_n, "case_count": len(result_rows), "measured_case_count": sum(row["measured"] for row in result_rows), "passing_case_count": passing, "rows": result_rows, "accepted_ready_now": False, "claim_boundary": {"allowed": claim_allowed, "not_allowed": "does not prove offset/noise/mismatch robustness, full converter behavior, layout DRC/LVS, SAR cycling, or accepted converter evidence"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD.write_text("\n".join(["# Sky130 Dynamic Offset-Cancelled Latch", "", f"- status: `{report['status']}`", f"- calibration zero-input differential V: `{report['calibration_zero_diff_v']}`", f"- passing cases: `{passing}` of `{len(result_rows)}`", "", "The source is held at its measured zero-input output during calibration, then steps to the measured target output. Series capacitors transfer the change to an isolated regenerative latch.", "", "This is a dynamic charge-transfer proof; it does not yet connect the transistor preamp directly or prove statistical analog performance.", ""]), encoding="utf-8")
    print("sky130_dynamic_offset_cancelled_latch")
    print(f"status,{report['status']}")
    print(f"passing_case_count,{passing}")
    print(f"json,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
