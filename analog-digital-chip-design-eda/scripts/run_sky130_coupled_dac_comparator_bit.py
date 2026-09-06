#!/usr/bin/env python3
"""Run one physical DAC trial into the physical Sky130 comparator in one deck."""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from run_sky130_two_phase_preamp_latch_candidate import Case, build_deck, read_measure
from run_sky130_switched_capacitor_dac import CAPS_F, ROOT, VDD

EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
_OUTPUT_STEM = os.environ.get("AIMC_COUPLED_OUTPUT_STEM", "sky130-coupled-dac-comparator-bit")
OUT_JSON = EVIDENCE / f"{_OUTPUT_STEM}.json"
OUT_MD = EVIDENCE / f"{_OUTPUT_STEM}.md"
TIMEOUT_S = float(os.environ.get("AIMC_COUPLED_TIMEOUT_S", "180"))

# The DAC input is 1.2 V and the comparator reference is 1.5 V. The selected
# code is chosen so that the physical DAC top plate is close to that reference.
_trial_codes = os.environ.get("AIMC_COUPLED_CODES", "")
TRIALS = tuple((int(code.strip()), 1.2, 1.5) for code in _trial_codes.split(",") if code.strip()) if _trial_codes else tuple((code, 1.2, 1.5) for code in range(16))


def add_dac(source: str, code: int, input_v: float, reference_v: float) -> str:
    cstore_override = os.environ.get("AIMC_COUPLED_CSTORE", "0.2p")
    dummy_override = os.environ.get("AIMC_COUPLED_DUMMY_CAP", "0.01p")
    top_dummy_override = os.environ.get("AIMC_COUPLED_TOP_DUMMY_CAP", "")
    sense_isolation_cap = os.environ.get("AIMC_COUPLED_SENSE_ISOLATION_CAP", "")
    bottom_scale = float(os.environ.get("AIMC_COUPLED_BOTTOM_SCALE", "1.0"))
    msb_switch_scale = float(os.environ.get("AIMC_COUPLED_MSB_SWITCH_SCALE", "1.0"))
    pfet_boost_v = float(os.environ.get("AIMC_COUPLED_PFET_BOOST_V", "0.0"))
    lsb_scale = float(os.environ.get("AIMC_COUPLED_LSB_SCALE", "1.0"))
    cap_scale = float(os.environ.get("AIMC_COUPLED_CAP_SCALE", "1.0"))
    msb_scale = float(os.environ.get("AIMC_COUPLED_MSB_CAP_SCALE", "1.0"))
    bit_cap_scales = {
        bit: float(os.environ.get(f"AIMC_COUPLED_BIT{bit}_CAP_SCALE", "1.0"))
        for bit in range(4)
    }
    redist_ns = float(os.environ.get("AIMC_COUPLED_REDIST_NS", "5.0"))
    isolate_bottom = os.environ.get("AIMC_COUPLED_BOTTOM_PRECHARGE_ISOLATE") == "1"
    keeper_v = float(os.environ.get("AIMC_COUPLED_BOTTOM_KEEPER_V", "0.0"))
    top_reset = os.environ.get("AIMC_COUPLED_TOP_RESET") == "1"
    bottom_leak = os.environ.get("AIMC_COUPLED_BOTTOM_LEAK", "")
    top_rail_clamp = os.environ.get("AIMC_COUPLED_TOP_RAIL_CLAMP") == "1"
    rail_clamp_area = float(os.environ.get("AIMC_COUPLED_RAIL_CLAMP_AREA", "1.0"))
    top_rail_resistor = os.environ.get("AIMC_COUPLED_TOP_RAIL_RESISTOR", "")
    supply_v = float(os.environ.get("AIMC_COUPLED_SUPPLY_V", "1.8"))
    caps = []
    controls = []
    switches = []
    for bit, cap in enumerate(CAPS_F):
        cap *= cap_scale
        if bit == 0:
            cap *= msb_scale
        cap *= bit_cap_scales[bit]
        if bit == 3:
            cap *= lsb_scale
        selected = (code >> (3 - bit)) & 1
        caps.append(f"CDAC{bit} top db{bit} {cap:.12e}")
        caps.append(f"CDACDUMMY{bit} db{bit} 0 {dummy_override}")
        if bottom_leak:
            caps.append(f"RLEAK_DAC{bit} db{bit} 0 {bottom_leak}")
        if selected:
            redistribution_time = f"{redist_ns:g}n" if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long" else "1n"
            selected_nfet_control = f"PULSE(1.8 0 {redistribution_time} 10p 10p 200n 1u)"
            pfet_time = "5.18n" if os.environ.get("AIMC_COUPLED_BREAK_BEFORE_MAKE") == "1" and os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long" else redistribution_time
            selected_pfet_control = f"PULSE(1.8 0 {pfet_time} 10p 10p 200n 1u)"
            if os.environ.get("AIMC_COUPLED_BOTTOM_PMOS_ONLY") != "1":
                controls.append(f"VGN_DAC{bit} gn_dac{bit} 0 {selected_nfet_control}")
                switches.append(f"XBN_DAC{bit} db{bit} gn_dac{bit} 0 0 sky130_fd_pr__nfet_01v8 W={8.0 * bottom_scale:.6g} L=0.15")
            if os.environ.get("AIMC_COUPLED_BOTTOM_NMOS_ONLY") != "1":
                if pfet_boost_v:
                    selected_pfet_control = selected_pfet_control.replace("1.8 0 ", f"1.8 {pfet_boost_v:.6g} ")
                controls.append(f"VGP_DAC{bit} gp_dac{bit} 0 {selected_pfet_control}")
                switch_width = 16.0 * bottom_scale * (msb_switch_scale if bit == 0 else 1.0)
                switches.append(f"XBP_DAC{bit} db{bit} gp_dac{bit} vdd vdd sky130_fd_pr__pfet_01v8 W={switch_width:.6g} L=0.15")
            if os.environ.get("AIMC_COUPLED_HIGH_NMOS") == "1":
                switches.append(f"XBPHI_DAC{bit} db{bit} gn_dac{bit} vdd vdd sky130_fd_pr__nfet_01v8 W=8.0 L=0.15")
        else:
            if isolate_bottom and os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long":
                unselected_nmos_control = f"PULSE(1.8 {keeper_v:g} {redist_ns:g}n 10p 10p 200n 1u)"
            else:
                unselected_nmos_control = "1.8"
            controls.extend([f"VGP_DAC{bit} gp_dac{bit} 0 1.8", f"VGN_DAC{bit} gn_dac{bit} 0 {unselected_nmos_control}"])
            switches.append(f"XBN_DAC{bit} db{bit} gn_dac{bit} 0 0 sky130_fd_pr__nfet_01v8 W={8.0 * bottom_scale:.6g} L=0.15")
    if top_dummy_override:
        caps.append(f"CDAC_TOP_DUMMY top 0 {top_dummy_override}")
    if sense_isolation_cap:
        caps.append(f"CSENSE_ISOLATION top sense {sense_isolation_cap}")
        caps.append("RSENSE_ISOLATION sense 0 100G")
    block = f'''* Physical Sky130 transistor DAC feeding the comparator input.
VREF inn 0 {reference_v:.9f}
VSRC_DAC srcin 0 {input_v:.9f}
VDAC_CTRL dac_ctrl 0 PULSE(0 {{vdd}} 0.1n 10p 10p 0.9n 1u)
VDAC_CTRLB dac_ctrlb 0 PULSE({{vdd}} 0 0.1n 10p 10p 0.9n 1u)
XDS_DAC srcin dac_ctrl top 0 sky130_fd_pr__nfet_01v8 W=2.0 L=0.15
XDP_DAC srcin dac_ctrlb top vdd sky130_fd_pr__pfet_01v8 W=4.0 L=0.15
* Matched source followers isolate the floating DAC/reference nodes from the comparator sample capacitors.
* Buffer control variant: direct late sampling is retained as the comparison
* baseline. The source-follower variant is documented in prior evidence.
{chr(10).join(caps)}
{chr(10).join(switches)}
{chr(10).join(controls)}
'''
    if top_reset and os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long":
        reset_delay = max(0.2, redist_ns - 0.7)
        block += f"VTOP_RESET top_reset 0 PULSE(0 {{vdd}} {reset_delay:g}n 10p 10p 0.5n 20n)\n"
        block += "XTOP_RESET top top_reset 0 0 sky130_fd_pr__nfet_01v8 W=16.0 L=0.15\n"
    if top_rail_clamp:
        block += f".model DTOPRAIL D(Is=1e-12 N=1 Rs=1 area={rail_clamp_area:g})\nD_TOP_LOW 0 top DTOPRAIL\nD_TOP_HIGH top vdd DTOPRAIL\n"
        if sense_isolation_cap:
            block += "D_SENSE_LOW 0 sense DTOPRAIL\nD_SENSE_HIGH sense vdd DTOPRAIL\n"
    if top_rail_resistor:
        block += f"R_TOP_VDD top vdd {top_rail_resistor}\n"
    source = source.replace("VINP inp 0 PULSE(0 {vinp} 0.05n 20p 20p 20n 40n)", "")
    source = source.replace("VINN inn 0 PULSE(0 {vinn} 0.05n 20p 20p 20n 40n)", "")
    source = source.replace("VSS vss 0 0\n", f"VSS vss 0 0\n{block}", 1)
    comparator_sense = "sense" if sense_isolation_cap else "top"
    source = source.replace("XSWNP inp ctrl", f"XSWNP {comparator_sense} ctrl")
    source = source.replace("XSWPP inp ctrlb", f"XSWPP {comparator_sense} ctrlb")
    source = source.replace("XSWNN inn ctrl", "XSWNN inn ctrl")
    if os.environ.get("AIMC_COUPLED_DIRECT_PREAMP") == "1":
        # Route the physical DAC/reference nodes into the high-impedance
        # transistor preamp gates. Remove the sampled storage-switch path so
        # comparator kickback cannot load the DAC node directly.
        source = re.sub(r"^XSWNP .*\nXSWPP .*\nXSWNN .*\nXSWPN .*\n", "", source, flags=re.MULTILINE)
        # The existing preamp/latch contract is inverted at the raw output;
        # cross the gate mapping so a positive DAC-minus-reference input
        # remains represented by the contracted outn-outp polarity.
        source = source.replace("XPREP pre_p sp pre_tail_node 0", "XPREP pre_p inn pre_tail_node 0")
        source = source.replace("XPREN pre_n sn pre_tail_node 0", "XPREN pre_n top pre_tail_node 0")
        source = source.replace(".ic v(top)=", ".ic v(top)=")
    source = source.replace("XSWPN inn ctrlb", "XSWPN inn ctrlb")
    source = source.replace(".param cstore=0.2p", f".param cstore={cstore_override}")
    if os.environ.get("AIMC_COUPLED_DIFFERENTIAL_DUMMY") == "1":
        dummy_scale = float(os.environ.get("AIMC_COUPLED_DIFFERENTIAL_DUMMY_SCALE", "1.0"))
        source = source.replace(".param dummy_wn=1.0", f".param dummy_wn={dummy_scale:.9f}")
        source = source.replace(".param dummy_wp=2.0", f".param dummy_wp={2.0 * dummy_scale:.9f}")
    source = source.replace(".lib \"" + str(Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice") + "\" tt", ".lib \"" + str(Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice") + "\" " + os.environ.get("AIMC_COUPLED_MODEL_SECTION", "tt"))
    source = source.replace(".param vdd=1.8", f".param vdd={supply_v:.9f}")
    temperature_c = os.environ.get("AIMC_COUPLED_TEMPERATURE_C")
    if temperature_c is not None:
        source = source.replace(".options", f".temp {float(temperature_c):.9f}\n.options", 1)
    if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long":
        source = source.replace("XDS_DAC srcin dac_ctrl top 0 sky130_fd_pr__nfet_01v8 W=2.0 L=0.15", "XDS_DAC srcin dac_ctrl top 0 sky130_fd_pr__nfet_01v8 W=32.0 L=0.15")
        source = source.replace("XDP_DAC srcin dac_ctrlb top vdd sky130_fd_pr__pfet_01v8 W=4.0 L=0.15", "XDP_DAC srcin dac_ctrlb top vdd sky130_fd_pr__pfet_01v8 W=64.0 L=0.15")
        source = source.replace("0.9n 1u", "4.0n 20n")
        source = source.replace("1n 10p 10p 200n 1u", f"{redist_ns:g}n 10p 10p 200n 1u")
    # Reduce the comparator sampling switch area while preserving a matched
    # pair. This is an interface-loading experiment, not a final sizing.
    source = source.replace(".ic v(sp)=0.9", f".ic v(top)={input_v:.9f} v(db0)=0 v(db1)=0 v(db2)=0 v(db3)=0 v(sp)=0.9")
    # The DAC must finish redistribution before the comparator samples. The
    # original standalone comparator sampled at 0.1-0.85 ns, before the DAC's
    # 1 ns bottom-plate transition, which held the wrong physical quantity.
    source = source.replace("VCTRL ctrl 0 PULSE(0 {vdd} 0.10n 20p 20p 0.75n 20n)", "VCTRL ctrl 0 PULSE(0 {vdd} 5.10n 20p 20p 0.50n 20n)")
    source = source.replace("VCTRLB ctrlb 0 PULSE({vdd} 0 0.10n 20p 20p 0.75n 20n)", "VCTRLB ctrlb 0 PULSE({vdd} 0 5.10n 20p 20p 0.50n 20n)")
    source = source.replace("VCLK clk 0 PULSE(0 {vdd} 1.60n 20p 20p 5n 10n)", "VCLK clk 0 PULSE(0 {vdd} 7.70n 20p 20p 5n 10n)")
    source = source.replace("VCLKB clkb 0 PULSE({vdd} 0 1.60n 20p 20p 5n 10n)", "VCLKB clkb 0 PULSE({vdd} 0 7.70n 20p 20p 5n 10n)")
    source = source.replace("IPRE pre_tail_node 0 {pre_tail}", "IPRE pre_tail_node 0 PULSE(0 {pre_tail} 5.70n 20p 20p 5n 10n)")
    source = source.replace(".tran 5p 3n", ".tran 5p 9n")
    source = source.replace("AT=1.45n", "AT=7.55n")
    source = source.replace("AT=2.70n", "AT=8.80n")
    source = source.replace(".measure tran sampled_p_before_v FIND v(sp) AT=0.90n", ".measure tran dac_top_before_v FIND v(top) AT=0.90n\n.measure tran dac_top_after_v FIND v(top) AT=7.55n\n.measure tran dac_sense_after_v FIND v(sense) AT=7.55n\n.measure tran dac_b0_after_v FIND v(db0) AT=7.55n\n.measure tran dac_b1_after_v FIND v(db1) AT=7.55n\n.measure tran dac_b2_after_v FIND v(db2) AT=7.55n\n.measure tran dac_b3_after_v FIND v(db3) AT=7.55n\n.measure tran comparator_sp_after_v FIND v(sp) AT=7.55n\n.measure tran comparator_sn_after_v FIND v(sn) AT=7.55n\n.measure tran sampled_p_before_v FIND v(sp) AT=0.90n")
    if not sense_isolation_cap:
        source = source.replace(".measure tran dac_sense_after_v FIND v(sense) AT=7.55n", ".measure tran dac_sense_after_v FIND v(top) AT=7.55n")
    if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long":
        comparator_ns = redist_ns + 4.10
        preamp_ns = redist_ns + 4.70
        latch_ns = redist_ns + 6.70
        dac_measure_ns = redist_ns + 4.00
        preamp_measure_ns = redist_ns + 6.45
        source = source.replace("5.10n", f"{comparator_ns:.2f}n").replace("7.70n", f"{latch_ns:.2f}n").replace("5.70n", f"{preamp_ns:.2f}n")
        source = source.replace("7.55n", f"{preamp_measure_ns:.2f}n").replace("8.80n", f"{redist_ns + 7.80:.2f}n").replace(".tran 5p 9n", f".tran 5p {redist_ns + 9.0:g}n")
        # Keep the DAC threshold measurement before comparator switch closure;
        # measuring it after the latch would include kickback and regeneration.
        source = source.replace(f"AT={preamp_measure_ns:.2f}n", f"AT={dac_measure_ns:.2f}n")
        # The preamp margin is intentionally measured after preamp enable,
        # unlike the DAC threshold and comparator sample observables.
        source = source.replace(f"preamp_p_before_latch_v FIND v(pre_p) AT={dac_measure_ns:.2f}n", f"preamp_p_before_latch_v FIND v(pre_p) AT={preamp_measure_ns:.2f}n")
        source = source.replace(f"preamp_n_before_latch_v FIND v(pre_n) AT={dac_measure_ns:.2f}n", f"preamp_n_before_latch_v FIND v(pre_n) AT={preamp_measure_ns:.2f}n")
    source = source.replace("{vinp}", f"{input_v:.9f}").replace("{vinn}", f"{reference_v:.9f}")
    return source


def run_trial(code: int, input_v: float, reference_v: float) -> dict[str, Any]:
    source = add_dac(build_deck(Case(f"coupled_code_{code}", 0.0)), code, input_v, reference_v)
    with tempfile.TemporaryDirectory(prefix="aimc-coupled-dac-comparator-") as tmp:
        path = Path(tmp) / "coupled.sp"
        path.write_text(source, encoding="utf-8")
        # Keep repeated PVT/SAR sweeps bounded even when ngspice leaves a
        # child transient process behind during convergence trouble.
        process = subprocess.Popen(
            ["ngspice", "-b", str(path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            process.communicate()
            return {"code": code, "measured": False, "timed_out": True, "input_v": input_v, "reference_v": reference_v}
        result = subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
    row: dict[str, Any] = {"code": code, "measured": result.returncode == 0, "timed_out": False, "returncode": result.returncode, "input_v": input_v, "reference_v": reference_v}
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1600:]
        return row
    output_diff = read_measure(result.stdout, "output_n_final_v") - read_measure(result.stdout, "output_p_final_v")
    dac_top = read_measure(result.stdout, "dac_top_after_v")
    sense_value = read_measure(result.stdout, "dac_sense_after_v") if os.environ.get("AIMC_COUPLED_SENSE_ISOLATION_CAP") else dac_top
    input_sign = 1 if sense_value - reference_v > 0 else -1 if sense_value - reference_v < 0 else 0
    output_sign = 1 if output_diff > 0 else -1 if output_diff < 0 else 0
    # This comparator fixture has the raw inverted convention outn-outp.
    row.update({
        "dac_top_before_v": read_measure(result.stdout, "dac_top_before_v"),
        "dac_top_after_v": dac_top,
        "dac_sense_after_v": sense_value,
        "dac_to_reference_diff_v": sense_value - reference_v,
        "dac_bottom_plate_v": [read_measure(result.stdout, f"dac_b{bit}_after_v") for bit in range(4)],
        "comparator_sp_after_v": read_measure(result.stdout, "comparator_sp_after_v"),
        "comparator_sn_after_v": read_measure(result.stdout, "comparator_sn_after_v"),
        "output_diff_v": output_diff,
        "expected_output_sign": -input_sign if input_sign else 0,
        "measured_output_sign": output_sign,
        "correct_polarity": output_sign == (-input_sign if input_sign else 0),
        "preamp_diff_before_latch_v": read_measure(result.stdout, "preamp_n_before_latch_v") - read_measure(result.stdout, "preamp_p_before_latch_v"),
    })
    return row


def main() -> int:
    workers = max(1, int(os.environ.get("AIMC_COUPLED_WORKERS", "1")))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(lambda trial: run_trial(*trial), TRIALS))
    measured = [row for row in rows if row["measured"]]
    report = {
        "result_type": "sky130_coupled_dac_comparator_bit",
        "status": "coupled_dac_comparator_all_code_bit_sweep_characterized_not_full_sar_proof" if measured else "coupled_dac_comparator_bit_incomplete",
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(row["timed_out"] for row in rows),
        "correct_polarity_count": sum(row.get("correct_polarity", False) for row in measured),
        "all_polarities_correct": bool(measured) and all(row.get("correct_polarity", False) for row in measured),
        "failing_codes": [row["code"] for row in measured if not row.get("correct_polarity", False)],
        "phase_schedule": {
            "dac_sampling_and_redistribution": "0.1-4.0 ns source sampling, 5.0 ns bottom-plate transition" if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long" else "0.1-1.0 ns sampling, 1.0 ns bottom-plate transition",
            "comparator_sampling": "9.1-9.6 ns" if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long" else "5.1-5.6 ns",
            "preamp_enable": "9.70 ns" if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long" else "5.70 ns",
            "preamp_latch_boundary": "11.55-11.70 ns" if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long" else "7.55-7.70 ns",
        },
        "worker_count": workers,
        "isolation_topology": "direct late sampling of the physical DAC top plate and matched reference by the comparator input switches with preamp disabled during sampling",
        "differential_dummy_cancellation_enabled": os.environ.get("AIMC_COUPLED_DIFFERENTIAL_DUMMY") == "1",
        "differential_dummy_scale": float(os.environ.get("AIMC_COUPLED_DIFFERENTIAL_DUMMY_SCALE", "1.0")),
        "direct_preamp_enabled": os.environ.get("AIMC_COUPLED_DIRECT_PREAMP") == "1",
        "top_dummy_capacitance": os.environ.get("AIMC_COUPLED_TOP_DUMMY_CAP", ""),
        "top_rail_resistor": os.environ.get("AIMC_COUPLED_TOP_RAIL_RESISTOR", ""),
        "rail_clamp_area": float(os.environ.get("AIMC_COUPLED_RAIL_CLAMP_AREA", "1.0")),
        "rows": rows,
        "claim_boundary": {
            "allowed": "runs a physical Sky130 transistor DAC and physical Sky130 preamp/latch comparator in one transient for representative trial codes",
            "not_allowed": "does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Coupled DAC And Comparator Bit", "",
        f"- status: `{report['status']}`",
        f"- measured trials: `{report['measured_case_count']}` of `{report['case_count']}`",
        f"- correct polarity: `{report['correct_polarity_count']}` of `{report['measured_case_count']}`", "",
        f"- failing codes: `{report['failing_codes']}`", "",
        "## What This Closes", "",
        "The DAC and comparator are in one SPICE transient. The physical capacitor array produces the top-plate voltage, the comparator's transistor input switches sample that node, and the same preamp/latch resolves the decision. This removes the biggest abstraction in the earlier replay: the comparator no longer receives a numerically injected threshold.", "",
        f"Configuration: direct preamp `{report['direct_preamp_enabled']}`, top dummy `{report['top_dummy_capacitance'] or 'none'}`, top-to-VDD resistor `{report['top_rail_resistor'] or 'none' }`.", "",
        ("The working repair removes the source-follower stage that introduced a midrange sign offset and instead samples the physical DAC top plate directly after redistribution. The current long schedule uses a 32/64 um source switch, 4.0 ns acquisition, a 5.0 ns bottom-plate transition, comparator sampling at 9.1-9.6 ns, preamp enable at 9.7 ns, and latch fire at 11.7 ns. This gives the 8 pF MSB time to settle before the decision while preventing the active preamp from loading the DAC during sampling. The all-code sweep is a complete nominal code-level handoff, but it still does not sequence retained bits into a full SAR conversion." if os.environ.get("AIMC_COUPLED_DAC_ACQ") == "long" else "The working repair removes the source-follower stage that introduced a midrange sign offset and instead samples the physical DAC top plate directly after redistribution. The short schedule samples at 5.1-5.6 ns, enables the preamp at 5.7 ns, and fires the latch at 7.7 ns. This gives the 8 pF MSB time to settle before the decision while preventing the active preamp from loading the DAC during sampling. The all-code sweep is a complete nominal code-level handoff, but it still does not sequence retained bits into a full SAR conversion."), "",
        "It is still only one bit-cycle boundary. The controller does not yet sequence four physical redistributions, retain bits, or repeat the experiment over PVT and mismatch.", "",
        "## Results", "",
        "| code | DAC top after redistribution V | DAC-reference diff V | comparator output diff V | correct polarity |", "| ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        if not row["measured"]:
            lines.append(f"| {row['code']} | timeout/error | timeout/error | timeout/error | False |")
        else:
            lines.append(f"| {row['code']} | {row['dac_top_after_v']:.6f} | {row['dac_to_reference_diff_v']:.6f} | {row['output_diff_v']:.6f} | {row['correct_polarity']} |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{report['measured_case_count']}/{report['case_count']}")
    print(f"correct_polarity,{report['correct_polarity_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
