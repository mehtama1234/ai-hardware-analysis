#!/usr/bin/env python3
"""Measure a thermometer-coded equal-unit-capacitor Sky130 DAC candidate."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from run_sky130_two_phase_preamp_latch_candidate import Case, build_deck
from run_sky130_switched_capacitor_dac import ROOT


OUT_JSON = Path(os.environ.get("AIMC_THERMOMETER_OUT_JSON", str(ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-thermometer-dac-comparator.json")))
OUT_MD = Path(os.environ.get("AIMC_THERMOMETER_OUT_MD", str(ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-thermometer-dac-comparator.md")))
PROGRESS_JSON = Path(os.environ.get("AIMC_THERMOMETER_PROGRESS_JSON", "")) if os.environ.get("AIMC_THERMOMETER_PROGRESS_JSON") else None
VDD = 1.8
TIMEOUT_S = float(os.environ.get("AIMC_THERMOMETER_TIMEOUT_S", "240"))
_codes = os.environ.get("AIMC_THERMOMETER_CODES", "")
CODES = tuple(int(code.strip()) for code in _codes.split(",") if code.strip()) if _codes else tuple(range(16))


def measure(stdout: str, name: str) -> float:
    matches = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", stdout)
    if not matches:
        raise ValueError(f"missing {name}")
    return float(matches[-1])


def add_dac(source: str, code: int, input_v: float, reference_v: float, differential_source_v: float | None = None) -> str:
    unit_count = int(os.environ.get("AIMC_THERMOMETER_UNIT_COUNT", "16"))
    units_per_code = int(os.environ.get("AIMC_THERMOMETER_UNITS_PER_CODE", "1"))
    split_encoding = os.environ.get("AIMC_THERMOMETER_SPLIT_ENCODING") == "1"
    differential_encoding = os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_ENCODING") == "1"
    unit_cap = float(os.environ.get("AIMC_THERMOMETER_UNIT_CAP_F", "1e-12"))
    differential_dummy_scale = float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_DUMMY_SCALE", "1.0"))
    controls: list[str] = []
    switches: list[str] = []
    redist_ns = float(os.environ.get("AIMC_THERMOMETER_REDIST_NS", "5.0"))
    bottom_scale = float(os.environ.get("AIMC_THERMOMETER_BOTTOM_SCALE", "1.0"))
    top_clamp = os.environ.get("AIMC_THERMOMETER_TOP_CLAMP") == "1"
    top_clamp_off_ns = float(os.environ.get("AIMC_THERMOMETER_TOP_CLAMP_OFF_NS", "3.50"))
    top_clamp_w = float(os.environ.get("AIMC_THERMOMETER_TOP_CLAMP_W", "4.0"))
    top_clamp_l = float(os.environ.get("AIMC_THERMOMETER_TOP_CLAMP_L", "0.15"))
    source_acq_ns = float(os.environ.get("AIMC_THERMOMETER_SOURCE_ACQ_NS", "4.0"))
    source_switch_scale = float(os.environ.get("AIMC_THERMOMETER_SOURCE_SWITCH_SCALE", "1.0"))
    source_switch_boost_v = float(os.environ.get("AIMC_THERMOMETER_SOURCE_SWITCH_BOOST_V", "0.0"))
    if differential_encoding:
        unit_count = 16
        units_per_code = 1
        caps = [f"CDACP{unit} topp dbup{unit} {unit_cap:.12e}" for unit in range(unit_count)]
        caps += [f"CDACN{unit} topn dbun{unit} {unit_cap:.12e}" for unit in range(unit_count)]
        caps += [f"CDACDUMPP topp 0 {unit_cap * differential_dummy_scale:.12e}", f"CDACDUMPN topn 0 {unit_cap * differential_dummy_scale:.12e}"]
        for unit in range(unit_count):
            selected = unit < code
            if selected:
                # Positive plate: precharge low, then switch high.
                controls.append(f"VGN_DACP{unit} gnup{unit} 0 PULSE(1.8 0 {redist_ns:g}n 10p 10p 20p 1u)")
                controls.append(f"VGP_DACP{unit} gpup{unit} 0 PULSE(1.8 0 {redist_ns + 0.02:g}n 10p 10p 200n 1u)")
                switches.append(f"XBNU_DACP{unit} dbup{unit} gnup{unit} 0 0 sky130_fd_pr__nfet_01v8 W={8.0 * bottom_scale:.6g} L=0.15")
                switches.append(f"XBPU_DACP{unit} dbup{unit} gpup{unit} vdd vdd sky130_fd_pr__pfet_01v8 W={16.0 * bottom_scale:.6g} L=0.15")
                # Negative plate: precharge high, then switch low.
                controls.append(f"VGP_DACN{unit} gpun{unit} 0 PULSE(0 1.8 {redist_ns:g}n 10p 10p 20p 1u)")
                controls.append(f"VGN_DACN{unit} gnun{unit} 0 PULSE(0 1.8 {redist_ns + 0.02:g}n 10p 10p 200n 1u)")
                switches.append(f"XBPU_DACN{unit} dbun{unit} gpun{unit} vdd vdd sky130_fd_pr__pfet_01v8 W={16.0 * bottom_scale:.6g} L=0.15")
                switches.append(f"XBNU_DACN{unit} dbun{unit} gnun{unit} 0 0 sky130_fd_pr__nfet_01v8 W={8.0 * bottom_scale:.6g} L=0.15")
            else:
                # Positive plate: precharge high, then switch low.
                controls.append(f"VGP_DACP{unit} gpup{unit} 0 PULSE(0 1.8 {redist_ns:g}n 10p 10p 20p 1u)")
                controls.append(f"VGN_DACP{unit} gnup{unit} 0 PULSE(0 1.8 {redist_ns + 0.02:g}n 10p 10p 200n 1u)")
                switches.append(f"XBPU_DACP{unit} dbup{unit} gpup{unit} vdd vdd sky130_fd_pr__pfet_01v8 W={16.0 * bottom_scale:.6g} L=0.15")
                switches.append(f"XBNU_DACP{unit} dbup{unit} gnup{unit} 0 0 sky130_fd_pr__nfet_01v8 W={8.0 * bottom_scale:.6g} L=0.15")
                # Negative plate: precharge low, then switch high.
                controls.append(f"VGN_DACN{unit} gnun{unit} 0 PULSE(1.8 0 {redist_ns:g}n 10p 10p 20p 1u)")
                controls.append(f"VGP_DACN{unit} gpun{unit} 0 PULSE(1.8 0 {redist_ns + 0.02:g}n 10p 10p 200n 1u)")
                switches.append(f"XBNU_DACN{unit} dbun{unit} gnun{unit} 0 0 sky130_fd_pr__nfet_01v8 W={8.0 * bottom_scale:.6g} L=0.15")
                switches.append(f"XBPU_DACN{unit} dbun{unit} gpun{unit} vdd vdd sky130_fd_pr__pfet_01v8 W={16.0 * bottom_scale:.6g} L=0.15")
    elif split_encoding:
        unit_count = 8
        units_per_code = 0
        caps = [f"CDACU{unit} top dbu{unit} {unit_cap:.12e}" for unit in range(unit_count)]
        caps.append(f"CDACF top dbuf {unit_cap * 0.5:.12e}")
        caps.append(f"CDACDUMMY top 0 {unit_cap:.12e}")
        for unit in range(unit_count):
            selected = unit < code // 2
            if selected:
                controls.append(f"VGP_DACU{unit} gpu{unit} 0 PULSE(1.8 0 {redist_ns:g}n 10p 10p 200n 1u)")
                switches.append(f"XBPU_DACU{unit} dbu{unit} gpu{unit} vdd vdd sky130_fd_pr__pfet_01v8 W={16.0 * bottom_scale:.6g} L=0.15")
            else:
                controls.append(f"VGN_DACU{unit} gnu{unit} 0 1.8")
                switches.append(f"XBNU_DACU{unit} dbu{unit} gnu{unit} 0 0 sky130_fd_pr__nfet_01v8 W={8.0 * bottom_scale:.6g} L=0.15")
        if code % 2:
            controls.append(f"VGP_DACF gpuf 0 PULSE(1.8 0 {redist_ns:g}n 10p 10p 200n 1u)")
            switches.append(f"XBPU_DACF dbuf gpuf vdd vdd sky130_fd_pr__pfet_01v8 W={16.0 * bottom_scale:.6g} L=0.15")
        else:
            controls.append("VGN_DACF gnuf 0 1.8")
            switches.append(f"XBNU_DACF dbuf gnuf 0 0 sky130_fd_pr__nfet_01v8 W={8.0 * bottom_scale:.6g} L=0.15")
    else:
        caps = [f"CDACU{unit} top dbu{unit} {unit_cap:.12e}" for unit in range(unit_count)]
        caps.append(f"CDACDUMMY top 0 {unit_cap:.12e}")
        for unit in range(unit_count):
            selected = unit < code * units_per_code
            if selected:
                controls.append(f"VGP_DACU{unit} gpu{unit} 0 PULSE(1.8 0 {redist_ns:g}n 10p 10p 200n 1u)")
                switches.append(f"XBPU_DACU{unit} dbu{unit} gpu{unit} vdd vdd sky130_fd_pr__pfet_01v8 W={16.0 * bottom_scale:.6g} L=0.15")
            else:
                controls.append(f"VGN_DACU{unit} gnu{unit} 0 1.8")
                switches.append(f"XBNU_DACU{unit} dbu{unit} gnu{unit} 0 0 sky130_fd_pr__nfet_01v8 W={8.0 * bottom_scale:.6g} L=0.15")
    if differential_encoding:
        differential_common_v = float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_COMMON_V", "0.9"))
        differential_input_scale = float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_INPUT_SCALE", "1.0"))
        differential_input_offset = float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_INPUT_OFFSET", str(differential_common_v * (1.0 - differential_input_scale))))
        positive_source_v = differential_input_offset + differential_input_scale * input_v
        negative_source_v = input_v if differential_source_v is None else differential_source_v
        if differential_source_v is not None:
            negative_source_v = differential_common_v
        source_block = f'''VSRC_DACP srcp 0 {positive_source_v:.9f}
VSRC_DACN srcn 0 {negative_source_v:.9f}
XDS_DACP srcp dac_ctrl topp 0 sky130_fd_pr__nfet_01v8 W={32.0 * source_switch_scale:g} L=0.15
XDP_DACP srcp dac_ctrlb topp vdd sky130_fd_pr__pfet_01v8 W={64.0 * source_switch_scale:g} L=0.15
XDS_DACN srcn dac_ctrl topn 0 sky130_fd_pr__nfet_01v8 W={32.0 * source_switch_scale:g} L=0.15
XDP_DACN srcn dac_ctrlb topn vdd sky130_fd_pr__pfet_01v8 W={64.0 * source_switch_scale:g} L=0.15'''
    else:
        source_block = f'''VSRC_DAC srcin 0 {input_v:.9f}
XDS_DAC srcin dac_ctrl top 0 sky130_fd_pr__nfet_01v8 W={32.0 * source_switch_scale:g} L=0.15
XDP_DAC srcin dac_ctrlb top vdd sky130_fd_pr__pfet_01v8 W={64.0 * source_switch_scale:g} L=0.15'''
    block = f'''* Thermometer-coded physical Sky130 capacitor DAC.
VREF inn 0 {reference_v:.9f}
VDAC_CTRL dac_ctrl 0 PULSE(0 {VDD + source_switch_boost_v:g} 0.1n 10p 10p 0.9n 1u)
VDAC_CTRLB dac_ctrlb 0 PULSE({{vdd}} 0 0.1n 10p 10p 0.9n 1u)
{source_block}
{chr(10).join(caps)}
{chr(10).join(switches)}
{chr(10).join(controls)}
'''
    if differential_encoding and os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_DIODE_CLAMP") == "1":
        block += ".model DHEAD D(Is=1e-3 N=0.1 Rs=1)\nDHEAD_LOW 0 topp DHEAD\nDHEAD_HIGH topn vdd DHEAD\n"
    if top_clamp:
        block += f"VTOPCLAMP topclamp 0 PULSE({{vdd}} 0 {top_clamp_off_ns:g}n 20p 20p 0.50n 20n)\nXTOPCLAMP top topclamp 0 0 sky130_fd_pr__nfet_01v8 W={top_clamp_w:g} L={top_clamp_l:g}\n"
    source = source.replace("VINP inp 0 PULSE(0 {vinp} 0.05n 20p 20p 20n 40n)", "")
    source = source.replace("VINN inn 0 PULSE(0 {vinn} 0.05n 20p 20p 20n 40n)", "")
    source = source.replace("VSS vss 0 0\n", f"VSS vss 0 0\n{block}", 1)
    source = source.replace("XSWNP inp ctrl", "XSWNP top ctrl")
    source = source.replace("XSWPP inp ctrlb", "XSWPP top ctrlb")
    if differential_encoding:
        source = source.replace("XSWNP top ctrl", "XSWNP topp ctrl")
        source = source.replace("XSWPP top ctrlb", "XSWPP topp ctrlb")
        source = source.replace("XSWNN inn ctrl", "XSWNN topn ctrl")
        source = source.replace("XSWPN inn ctrlb", "XSWPN topn ctrlb")
    source = source.replace(".param cstore=0.2p", ".param cstore=0.2p")
    source = source.replace("0.9n 1u", f"{source_acq_ns:g}n 20n")
    source = source.replace("VCTRL ctrl 0 PULSE(0 {vdd} 0.10n 20p 20p 0.75n 20n)", "VCTRL ctrl 0 PULSE(0 {vdd} 5.10n 20p 20p 0.50n 20n)")
    source = source.replace("VCTRLB ctrlb 0 PULSE({vdd} 0 0.10n 20p 20p 0.75n 20n)", "VCTRLB ctrlb 0 PULSE({vdd} 0 5.10n 20p 20p 0.50n 20n)")
    source = source.replace("VCLK clk 0 PULSE(0 {vdd} 1.60n 20p 20p 5n 10n)", "VCLK clk 0 PULSE(0 {vdd} 7.70n 20p 20p 5n 10n)")
    source = source.replace("VCLKB clkb 0 PULSE({vdd} 0 1.60n 20p 20p 5n 10n)", "VCLKB clkb 0 PULSE({vdd} 0 7.70n 20p 20p 5n 10n)")
    source = source.replace("IPRE pre_tail_node 0 {pre_tail}", "IPRE pre_tail_node 0 PULSE(0 {pre_tail} 5.70n 20p 20p 5n 10n)")
    source = source.replace(".tran 5p 3n", ".tran 5p 9n")
    source = source.replace("AT=1.45n", "AT=7.55n").replace("AT=2.70n", "AT=8.80n")
    if differential_encoding:
        source = source.replace(".measure tran sampled_p_before_v FIND v(sp) AT=0.90n", ".measure tran dac_top_positive_before_v FIND v(topp) AT=0.90n\n.measure tran dac_top_negative_before_v FIND v(topn) AT=0.90n\n.measure tran dac_top_positive_after_v FIND v(topp) AT=7.55n\n.measure tran dac_top_negative_after_v FIND v(topn) AT=7.55n\n.measure tran comparator_sp_after_v FIND v(sp) AT=7.55n\n.measure tran comparator_sn_after_v FIND v(sn) AT=7.55n")
    else:
        source = source.replace(".measure tran sampled_p_before_v FIND v(sp) AT=0.90n", ".measure tran dac_top_before_v FIND v(top) AT=0.90n\n.measure tran dac_top_after_v FIND v(top) AT=7.55n\n.measure tran comparator_sp_after_v FIND v(sp) AT=7.55n\n.measure tran comparator_sn_after_v FIND v(sn) AT=7.55n")
    source = source.replace("5.10n", f"{redist_ns + 4.10:.2f}n").replace("7.70n", f"{redist_ns + 6.70:.2f}n").replace("5.70n", f"{redist_ns + 4.70:.2f}n")
    source = source.replace("7.55n", f"{redist_ns + 6.45:.2f}n").replace("8.80n", f"{redist_ns + 7.80:.2f}n").replace(".tran 5p 9n", f".tran 5p {redist_ns + 9.0:g}n")
    source = source.replace(f"AT={redist_ns + 6.45:.2f}n", f"AT={redist_ns + 4.00:.2f}n")
    source = source.replace("{vinp}", f"{input_v:.9f}").replace("{vinn}", f"{reference_v:.9f}")
    return source


def run_trial(code: int, input_v: float, reference_v: float, differential_source_v: float | None = None) -> dict[str, Any]:
    source = add_dac(build_deck(Case(f"thermometer_code_{code}", 0.0)), code, input_v, reference_v, differential_source_v)
    with tempfile.TemporaryDirectory(prefix="aimc-thermometer-dac-") as tmp:
        path = Path(tmp) / "thermometer.sp"
        path.write_text(source, encoding="utf-8")
        try:
            result = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {"code": code, "measured": False, "timed_out": True, "input_v": input_v, "reference_v": reference_v}
    row: dict[str, Any] = {"code": code, "measured": result.returncode == 0, "timed_out": False, "input_v": input_v, "reference_v": reference_v}
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        return row
    differential_encoding = os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_ENCODING") == "1"
    if differential_encoding:
        top_positive_before = measure(result.stdout, "dac_top_positive_before_v")
        top_negative_before = measure(result.stdout, "dac_top_negative_before_v")
        top_positive = measure(result.stdout, "dac_top_positive_after_v")
        top_negative = measure(result.stdout, "dac_top_negative_after_v")
        top_before = top_positive_before - top_negative_before
        top = top_positive - top_negative
    else:
        top_before = measure(result.stdout, "dac_top_before_v")
        top = measure(result.stdout, "dac_top_after_v")
    output_diff = measure(result.stdout, "output_n_final_v") - measure(result.stdout, "output_p_final_v")
    input_sign = (1 if top > 0 else -1 if top < 0 else 0) if differential_encoding else (1 if top - reference_v > 0 else -1 if top - reference_v < 0 else 0)
    output_sign = 1 if output_diff > 0 else -1 if output_diff < 0 else 0
    expected_output_sign = -input_sign if input_sign else 0
    row.update({"dac_top_before_v": top_before, "dac_top_after_v": top, "dac_to_reference_diff_v": top if differential_encoding else top - reference_v, "output_diff_v": output_diff, "expected_output_sign": expected_output_sign, "measured_output_sign": output_sign, "correct_polarity": (True if input_sign == 0 else output_sign == expected_output_sign)})
    if differential_encoding:
        row.update({"dac_top_positive_after_v": top_positive, "dac_top_negative_after_v": top_negative, "legal_plate_range": 0.0 <= top_positive <= VDD and 0.0 <= top_negative <= VDD})
    return row


def main() -> int:
    input_v = float(os.environ.get("AIMC_THERMOMETER_INPUT_V", "0.0"))
    unit_count = int(os.environ.get("AIMC_THERMOMETER_UNIT_COUNT", "16"))
    units_per_code = int(os.environ.get("AIMC_THERMOMETER_UNITS_PER_CODE", "1"))
    split_encoding = os.environ.get("AIMC_THERMOMETER_SPLIT_ENCODING") == "1"
    differential_encoding = os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_ENCODING") == "1"
    if split_encoding:
        unit_count = 8
        units_per_code = 0
    rows: list[dict[str, Any]] = []
    reference_v = 0.0 if differential_encoding else 1.0
    for code in CODES:
        row = run_trial(code, input_v, reference_v)
        rows.append(row)
        print(f"code,{code},measured,{row.get('measured', False)},timed_out,{row.get('timed_out', False)}", flush=True)
        if PROGRESS_JSON:
            PROGRESS_JSON.parent.mkdir(parents=True, exist_ok=True)
            PROGRESS_JSON.write_text(json.dumps({"status": "in_progress", "codes": list(CODES), "rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    measured = [row for row in rows if row.get("measured")]
    values = [row["dac_top_after_v"] for row in rows if row.get("measured")]
    spacings = [(values[index + 1] - values[index]) * 1000.0 for index in range(len(values) - 1)] if len(values) == len(CODES) else []
    complete = len(measured) == len(CODES)
    monotonic = complete and all(value > 0 for value in spacings)
    legal = complete and all(row.get("legal_plate_range", 0.0 <= row["dac_top_after_v"] <= VDD) for row in measured)
    half_lsb_mv = VDD / 16.0 * 1000.0 / 2.0
    full_scale_target_v = VDD - (VDD / 16.0)
    full_scale_coverage = complete and bool(values) and max(values) - min(values) >= full_scale_target_v
    spacing_pass = complete and bool(spacings) and monotonic and min(spacings) >= half_lsb_mv and full_scale_coverage
    polarity_pass = complete and all(row.get("correct_polarity", False) for row in measured)
    status = "thermometer_candidate" if spacing_pass and legal and polarity_pass else "thermometer_candidate_rejected"
    topology_name = "complementary differential 16-unit charge-transfer DAC" if differential_encoding else ("8 coarse units plus half-size fine capacitor with split odd/even encoding" if split_encoding else f"{unit_count} equal unit capacitors with {units_per_code} units selected per thermometer code and PMOS-to-VDD/NMOS-to-ground bottom switching")
    report = {"result_type": "sky130_thermometer_dac_comparator", "status": status, "topology": topology_name, "codes": list(CODES), "unit_count": unit_count, "units_per_code": units_per_code, "split_encoding": split_encoding, "differential_encoding": differential_encoding, "unit_cap_f": 1e-12, "differential_dummy_scale": float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_DUMMY_SCALE", "1.0")), "differential_common_v": float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_COMMON_V", "0.9")), "differential_input_scale": float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_INPUT_SCALE", "1.0")), "bottom_switch_scale": float(os.environ.get("AIMC_THERMOMETER_BOTTOM_SCALE", "1.0")), "source_switch_scale": float(os.environ.get("AIMC_THERMOMETER_SOURCE_SWITCH_SCALE", "1.0")), "source_acquisition_ns": float(os.environ.get("AIMC_THERMOMETER_SOURCE_ACQ_NS", "4.0")), "per_code_timeout_s": TIMEOUT_S, "sampled_input_v": input_v, "reference_v": reference_v, "supply_v": VDD, "rows": rows, "adjacent_spacings_mv": spacings, "minimum_spacing_mv": min(spacings) if spacings else None, "required_half_lsb_mv": half_lsb_mv, "full_scale_target_v": full_scale_target_v, "full_scale_coverage": full_scale_coverage, "maximum_dac_top_v": max(values) if values else None, "complete": complete, "monotonic": monotonic, "legal_supply_range": legal, "all_polarities_correct": polarity_pass, "interpretation": "The candidate is accepted only if all requested codes converge with full-scale coverage, monotonic half-LSB spacing, legal node range, and correct comparator polarity. It remains a larger-area converter candidate until SAR, PVT, mismatch, noise, settling, extraction, and energy gates pass.", "claim_boundary": {"allowed": "measures a switched-capacitor DAC coupled to the Sky130 comparator fixture", "not_allowed": "does not prove SAR accuracy, PVT/mismatch/noise yield, extracted layout, area, energy, board behavior, silicon, or model replacement readiness"}}
    lines = ["# Sky130 Thermometer DAC Comparator", "", f"- status: `{status}`", f"- topology: `{report['topology']}`", f"- unit capacitor: `{report['unit_cap_f']:.3e} F`", f"- bottom switch scale: `{report['bottom_switch_scale']}`", f"- source acquisition: `{report['source_acquisition_ns']} ns`", f"- per-code timeout: `{report['per_code_timeout_s']} s`", f"- codes measured: `{len(measured)}/{len(CODES)}`", f"- minimum spacing (mV): `{report['minimum_spacing_mv']}`", f"- required half-LSB (mV): `{half_lsb_mv}`", f"- full-scale target (V): `{report['full_scale_target_v']}`", f"- full-scale coverage: `{report['full_scale_coverage']}`", f"- maximum top plate (V): `{report['maximum_dac_top_v']}`", "", "| code | DAC top (V) | correct polarity |", "| ---: | ---: | --- |"]
    for row in rows:
        lines.append(f"| {row['code']} | {row['dac_top_after_v']:.6f} | {row['correct_polarity']} |" if row.get("measured") else f"| {row['code']} | incomplete | False |")
    lines += ["", "## Result", "", report["interpretation"], "", "## Claim Boundary", "", report["claim_boundary"]["not_allowed"]]
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"status,{status}")
    print(f"measured,{len(measured)}/{len(CODES)}")
    print(f"minimum_spacing_mv,{report['minimum_spacing_mv']}")
    print(f"maximum_dac_top_v,{report['maximum_dac_top_v']}")
    print(f"legal_supply_range,{legal}")
    print(f"all_polarities_correct,{polarity_pass}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
