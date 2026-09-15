#!/usr/bin/env python3
"""Measure a binary capacitor DAC with Sky130 MOS sampling/redistribution switches."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from run_sky130_switched_capacitor_dac import CUNIT_F, CAPS_F, ROOT, VDD, VIN, measure

EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
DEFAULT_PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
PDK_LIB = Path(os.environ.get("AIMC_SKY130_PDK_LIB", str(DEFAULT_PDK_LIB)))
OUT_JSON = EVIDENCE / "sky130-transistor-switched-capacitor-dac.json"
OUT_MD = EVIDENCE / "sky130-transistor-switched-capacitor-dac.md"
OUTPUT_STEM = os.environ.get("AIMC_TRANSISTOR_DAC_OUTPUT_STEM", "")
CHECKPOINT_DIR = Path(os.environ["AIMC_TRANSISTOR_DAC_CHECKPOINT_DIR"]) if os.environ.get("AIMC_TRANSISTOR_DAC_CHECKPOINT_DIR") else None
if OUTPUT_STEM:
    OUT_JSON = EVIDENCE / f"{OUTPUT_STEM}.json"
    OUT_MD = EVIDENCE / f"{OUTPUT_STEM}.md"
TIMEOUT_S = float(os.environ.get("AIMC_TRANSISTOR_DAC_TIMEOUT_S", "60"))
DECISION_NS = float(os.environ.get("AIMC_TRANSISTOR_DAC_DECISION_NS", "70.0"))
TRAN_NS = float(os.environ.get("AIMC_TRANSISTOR_DAC_TRAN_NS", str(max(80.0, DECISION_NS + 10.0))))
STEP_PS = float(os.environ.get("AIMC_TRANSISTOR_DAC_STEP_PS", "10.0"))
PMOS_BANK = int(os.environ.get("AIMC_TRANSISTOR_DAC_PMOS_BANK", "1"))
if PMOS_BANK < 1:
    raise SystemExit("AIMC_TRANSISTOR_DAC_PMOS_BANK must be at least 1")
NMOS_BANK = int(os.environ.get("AIMC_TRANSISTOR_DAC_NMOS_BANK", "1"))
if NMOS_BANK < 1:
    raise SystemExit("AIMC_TRANSISTOR_DAC_NMOS_BANK must be at least 1")
RAIL_HANDOFF = os.environ.get("AIMC_TRANSISTOR_DAC_RAIL_HANDOFF") == "1"
RAIL_HANDOFF_NS = float(os.environ.get("AIMC_TRANSISTOR_DAC_RAIL_HANDOFF_NS", "3.0"))
RAIL_HANDOFF_RON = float(os.environ.get("AIMC_TRANSISTOR_DAC_RAIL_HANDOFF_RON", "2.0"))
TRANSISTOR_HANDOFF = os.environ.get("AIMC_TRANSISTOR_DAC_TRANSISTOR_HANDOFF") == "1"
TRANSISTOR_HANDOFF_NS = float(os.environ.get("AIMC_TRANSISTOR_DAC_TRANSISTOR_HANDOFF_NS", "3.0"))
TRANSISTOR_HANDOFF_DEAD_NS = float(os.environ.get("AIMC_TRANSISTOR_DAC_TRANSISTOR_HANDOFF_DEAD_NS", "0.25"))
TRANSISTOR_HANDOFF_RISE_NS = float(os.environ.get("AIMC_TRANSISTOR_DAC_TRANSISTOR_HANDOFF_RISE_NS", "0.0"))
if TRANSISTOR_HANDOFF_RISE_NS < 0.0:
    raise SystemExit("AIMC_TRANSISTOR_DAC_TRANSISTOR_HANDOFF_RISE_NS must be non-negative")
if TRANSISTOR_HANDOFF and TRANSISTOR_HANDOFF_RISE_NS > TRANSISTOR_HANDOFF_DEAD_NS:
    raise SystemExit("transistor handoff rise time must fit inside the dead-time interval")
BOTTOM_KEEPER_OHM = float(os.environ.get("AIMC_TRANSISTOR_DAC_BOTTOM_KEEPER_OHM", "0"))
if BOTTOM_KEEPER_OHM < 0.0:
    raise SystemExit("AIMC_TRANSISTOR_DAC_BOTTOM_KEEPER_OHM must be non-negative")
RECLAMP = os.environ.get("AIMC_TRANSISTOR_DAC_RECLAMP") == "1"
RECLAMP_NS = float(os.environ.get("AIMC_TRANSISTOR_DAC_RECLAMP_NS", "4.5"))
if RECLAMP and RECLAMP_NS <= TRANSISTOR_HANDOFF_NS + TRANSISTOR_HANDOFF_DEAD_NS:
    raise SystemExit("reclamp time must follow the transistor handoff dead-time interval")
ISOLATED_HANDOFF = os.environ.get("AIMC_TRANSISTOR_DAC_ISOLATED_HANDOFF") == "1"
ISOLATED_RECONNECT_NS = float(os.environ.get("AIMC_TRANSISTOR_DAC_ISOLATED_RECONNECT_NS", "4.5"))
if ISOLATED_HANDOFF and ISOLATED_RECONNECT_NS <= TRANSISTOR_HANDOFF_NS + TRANSISTOR_HANDOFF_DEAD_NS:
    raise SystemExit("isolated rail reconnect time must follow the handoff dead-time interval")
ACTIVE_HOLD = os.environ.get("AIMC_TRANSISTOR_DAC_ACTIVE_HOLD") == "1"
ACTIVE_HOLD_NS = float(os.environ.get("AIMC_TRANSISTOR_DAC_ACTIVE_HOLD_NS", "4.5"))
ACTIVE_HOLD_WIDTH = float(os.environ.get("AIMC_TRANSISTOR_DAC_ACTIVE_HOLD_WIDTH", "1.0"))
ACTIVE_HOLD_L = float(os.environ.get("AIMC_TRANSISTOR_DAC_ACTIVE_HOLD_L", "0.15"))
if ACTIVE_HOLD and ACTIVE_HOLD_NS <= TRANSISTOR_HANDOFF_NS + TRANSISTOR_HANDOFF_DEAD_NS:
    raise SystemExit("active hold time must follow the transistor handoff dead-time interval")
if ACTIVE_HOLD_WIDTH <= 0.0:
    raise SystemExit("AIMC_TRANSISTOR_DAC_ACTIVE_HOLD_WIDTH must be positive")
if ACTIVE_HOLD_L <= 0.0:
    raise SystemExit("AIMC_TRANSISTOR_DAC_ACTIVE_HOLD_L must be positive")
CODES = tuple(range(16))


def deck(code: int) -> str:
    caps = []
    controls = []
    switches = []
    for bit, cap in enumerate(CAPS_F):
        selected = (code >> (3 - bit)) & 1
        caps.append(f"C{bit} top b{bit} {cap:.12e}")
        caps.append(f"CDUMMY{bit} b{bit} 0 0.01e-12")
        if ISOLATED_HANDOFF:
            rail = f"rail{bit}"
            caps.append(f"CRAIL{bit} {rail} 0 0.01e-12")
            iso_gate = f"PWL(0 1.8 {TRANSISTOR_HANDOFF_NS:g}n 0 {ISOLATED_RECONNECT_NS:g}n 0 {ISOLATED_RECONNECT_NS + 0.01:g}n 1.8 200n 1.8)"
            iso_gate_b = f"PWL(0 0 {TRANSISTOR_HANDOFF_NS:g}n 1.8 {ISOLATED_RECONNECT_NS:g}n 1.8 {ISOLATED_RECONNECT_NS + 0.01:g}n 0 200n 0)"
            controls.extend([f"VISO{bit} isog{bit} 0 {iso_gate}", f"VISOB{bit} isogb{bit} 0 {iso_gate_b}"])
            switches.extend([
                f"XIS_ON{bit} b{bit} isog{bit} {rail} 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15",
                f"XIS_OP{bit} b{bit} isogb{bit} {rail} vdd sky130_fd_pr__pfet_01v8 W=16.0 L=0.15",
            ])
            if selected:
                p_gate = f"PWL(0 1.8 {TRANSISTOR_HANDOFF_NS + TRANSISTOR_HANDOFF_DEAD_NS:g}n 0 200n 0)"
                controls.extend([f"VGP{bit} gp{bit} 0 {p_gate}", f"VGN{bit} gn{bit} 0 0"])
                switches.extend([
                    f"XRAILP{bit} {rail} gp{bit} vdd vdd sky130_fd_pr__pfet_01v8 W=16.0 L=0.15",
                    f"XRAILN{bit} {rail} gn{bit} 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15",
                ])
            else:
                controls.extend([f"VGP{bit} gp{bit} 0 1.8", f"VGN{bit} gn{bit} 0 1.8"])
                switches.append(f"XRAILN{bit} {rail} gn{bit} 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15")
        elif selected:
            # Before the edge the NMOS holds the bottom plate at ground. At
            # the edge it turns off while the PMOS connects the plate to VDD.
            if TRANSISTOR_HANDOFF:
                n_off_ns = TRANSISTOR_HANDOFF_NS + TRANSISTOR_HANDOFF_RISE_NS
                p_on_ns = TRANSISTOR_HANDOFF_NS + TRANSISTOR_HANDOFF_DEAD_NS
                p_final_ns = p_on_ns + TRANSISTOR_HANDOFF_RISE_NS
                n_gate = f"PWL(0 1.8 {TRANSISTOR_HANDOFF_NS:g}n 1.8 {n_off_ns:g}n 0 {p_on_ns:g}n 0 200n 0)"
                p_gate = f"PWL(0 1.8 {p_on_ns:g}n 1.8 {p_final_ns:g}n 0 200n 0)"
            else:
                p_gate = "PULSE(1.8 0 1n 10p 10p 200n 1u)"
                n_gate = "PULSE(1.8 0 1n 10p 10p 200n 1u)"
            controls.extend([
                f"VGP{bit} gp{bit} 0 {p_gate}",
                f"VGN{bit} gn{bit} 0 {n_gate}",
            ])
            switches.extend([
                "\n".join(f"XBP{bit}_{index} b{bit} gp{bit} vdd vdd sky130_fd_pr__pfet_01v8 W=16.0 L=0.15" for index in range(PMOS_BANK)),
                "\n".join(f"XBN{bit}_{index} b{bit} gn{bit} 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15" for index in range(NMOS_BANK)),
            ])
        else:
            controls.append(f"VGP{bit} gp{bit} 0 1.8")
            if RECLAMP:
                n_gate = f"PWL(0 1.8 {TRANSISTOR_HANDOFF_NS:g}n 1.8 {TRANSISTOR_HANDOFF_NS + TRANSISTOR_HANDOFF_DEAD_NS:g}n 0 {RECLAMP_NS:g}n 0 {RECLAMP_NS + 0.01:g}n 1.8 200n 1.8)"
                controls.append(f"VGN{bit} gn{bit} 0 {n_gate}")
            else:
                controls.append(f"VGN{bit} gn{bit} 0 1.8")
            switches.append("\n".join(f"XBN{bit}_{index} b{bit} gn{bit} 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15" for index in range(NMOS_BANK)))
        if RAIL_HANDOFF:
            rail_gate = f"PULSE(0 1.8 {RAIL_HANDOFF_NS:g}n 10p 10p 200n 1u)"
            rail_target = "vdd" if selected else "0"
            controls.append(f"VHND{bit} hnd{bit} 0 {rail_gate}")
            switches.append(f"SHND{bit} b{bit} {rail_target} hnd{bit} 0 SWRAIL")
        if BOTTOM_KEEPER_OHM > 0.0:
            keeper_target = "vdd" if selected else "0"
            switches.append(f"RKEEP{bit} b{bit} {keeper_target} {BOTTOM_KEEPER_OHM:g}")
        if ACTIVE_HOLD:
            hold_gate = f"PWL(0 0 {ACTIVE_HOLD_NS:g}n 0 {ACTIVE_HOLD_NS + 0.01:g}n 1.8 200n 1.8)"
            hold_gate_b = f"PWL(0 1.8 {ACTIVE_HOLD_NS:g}n 1.8 {ACTIVE_HOLD_NS + 0.01:g}n 0 200n 0)"
            if selected:
                controls.append(f"VHOLD{bit} hold{bit} 0 {hold_gate_b}")
                switches.append(f"XHOLD{bit} b{bit} hold{bit} vdd vdd sky130_fd_pr__pfet_01v8 W={ACTIVE_HOLD_WIDTH:g} L={ACTIVE_HOLD_L:g}")
            else:
                controls.append(f"VHOLD{bit} hold{bit} 0 {hold_gate}")
                switches.append(f"XHOLD{bit} b{bit} hold{bit} 0 0 sky130_fd_pr__nfet_01v8 W={ACTIVE_HOLD_WIDTH:g} L={ACTIVE_HOLD_L:g}")
    return f"""* Sky130 transistor-switched binary capacitor DAC.
.lib \"{PDK_LIB}\" tt
.param vdd=1.8
.param vin=0.9
VDD vdd 0 {{vdd}}
VIN vin 0 {{vin}}
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.1n 10p 10p 0.9n 1u)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.1n 10p 10p 0.9n 1u)
VSS vss 0 0
XSN vin ctrl top vss sky130_fd_pr__nfet_01v8 W=2.0 L=0.15
XSP vin ctrlb top vdd sky130_fd_pr__pfet_01v8 W=4.0 L=0.15
{chr(10).join(caps)}
CDUMMY top 0 {CUNIT_F:.12e}
{chr(10).join(switches)}
{chr(10).join(controls)}
{'.model SWRAIL SW(Ron=' + str(RAIL_HANDOFF_RON) + ' Roff=1e12 Vt=0.9 Vh=0.05)' if RAIL_HANDOFF else ''}
.ic v(top)={VIN} v(b0)=0 v(b1)=0 v(b2)=0 v(b3)=0
.tran {STEP_PS:g}p {TRAN_NS:g}n uic
.measure tran top_sampled_v FIND v(top) AT=0.8n
.measure tran top_early_v FIND v(top) AT=3.0n
.measure tran top_settled_v FIND v(top) AT={DECISION_NS:g}n
.measure tran sample_settled_v FIND v(ctrl) AT={DECISION_NS:g}n
.measure tran b0_settled_v FIND v(b0) AT={DECISION_NS:g}n
.measure tran b1_settled_v FIND v(b1) AT={DECISION_NS:g}n
.measure tran b2_settled_v FIND v(b2) AT={DECISION_NS:g}n
.measure tran b3_settled_v FIND v(b3) AT={DECISION_NS:g}n
.control
run
.endc
.end
"""


def run(code: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="aimc-transistor-cdac-") as tmp:
        path = Path(tmp) / "cdac.sp"
        path.write_text(deck(code), encoding="utf-8")
        process = subprocess.Popen(["ngspice", "-b", str(path)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        try:
            stdout, stderr = process.communicate(timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
            return {"code": code, "measured": False, "timed_out": True, "failure_class": "numerical_convergence_timeout", "error_excerpt": (stdout + stderr)[-1200:]}
    result = subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
    row: dict[str, Any] = {"code": code, "measured": result.returncode == 0, "timed_out": False, "returncode": result.returncode}
    if result.returncode != 0:
        row["failure_class"] = "simulator_failure"
        row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        return row
    top_sampled = measure(result.stdout, "top_sampled_v")
    top_settled = measure(result.stdout, "top_settled_v")
    expected = VIN + VDD * code / 16.0
    row.update({
        "top_sampled_v": top_sampled,
        "top_settled_v": top_settled,
        "top_early_v": measure(result.stdout, "top_early_v"),
        "expected_top_v": expected,
        "settling_error_v": abs(top_settled - expected),
        "redistribution_delta_v": top_settled - top_sampled,
        "sample_settled_v": measure(result.stdout, "sample_settled_v"),
        "bottom_plate_v": [measure(result.stdout, f"b{bit}_settled_v") for bit in range(4)],
    })
    return row


def main() -> int:
    # The Sky130 transient decks are numerically heavy; serial execution keeps
    # a timeout attributable to the circuit rather than host contention.
    requested_codes = os.environ.get("AIMC_TRANSISTOR_DAC_CODES", "")
    codes = tuple(int(value.strip()) for value in requested_codes.split(",") if value.strip()) if requested_codes else CODES
    if not codes or any(code not in CODES for code in codes):
        raise SystemExit("AIMC_TRANSISTOR_DAC_CODES must contain values from 0 through 15")
    rows = []
    for code in codes:
        checkpoint_path = CHECKPOINT_DIR / f"code-{code:02d}.json" if CHECKPOINT_DIR is not None else None
        if checkpoint_path is not None and checkpoint_path.is_file():
            try:
                cached = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                cached = {}
            if all(cached.get(key) == value for key, value in (("code", code), ("decision_time_ns", DECISION_NS), ("transient_ns", TRAN_NS), ("transient_step_ps", STEP_PS))) and isinstance(cached.get("row"), dict):
                rows.append(cached["row"])
                continue
        row = run(code)
        rows.append(row)
        if CHECKPOINT_DIR is not None:
            CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
            checkpoint = {
                "result_type": "sky130_transistor_switched_capacitor_dac_code_checkpoint",
                "code": code,
                "decision_time_ns": DECISION_NS,
                "transient_ns": TRAN_NS,
                "transient_step_ps": STEP_PS,
                "row": row,
                "claim_boundary": "Per-code diagnostic checkpoint only; it is not a complete 16-code, PVT, mismatch, comparator, SAR, energy, layout, board, or silicon acceptance receipt.",
            }
            (CHECKPOINT_DIR / f"code-{code:02d}.json").write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    measured = [row for row in rows if row["measured"]]
    half_lsb = VDD / 16.0 / 2.0
    all_bottom_plates_legal = bool(measured) and all(
        all(0.0 <= value <= VDD for value in row["bottom_plate_v"])
        for row in measured
    )
    all_codes_within_half_lsb = len(measured) == len(codes) and all(row["settling_error_v"] <= half_lsb for row in measured)
    all_pass = all_codes_within_half_lsb and all_bottom_plates_legal
    monotonic = bool(measured) and all(a["top_settled_v"] <= b["top_settled_v"] for a, b in zip(measured, measured[1:]))
    report = {
        "result_type": "sky130_transistor_switched_capacitor_dac",
        "status": "transistor_switched_capacitor_dac_passed_boundary" if all_pass else "transistor_switched_capacitor_dac_incomplete_or_half_lsb_or_legal_range_failed",
        "bits": 4,
        "switch_devices": ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"],
        "code_count": len(codes),
        "requested_codes": list(codes),
        "measured_code_count": len(measured),
        "half_lsb_v": half_lsb,
        "decision_time_ns": DECISION_NS,
        "transient_ns": TRAN_NS,
        "transient_step_ps": STEP_PS,
        "pmos_bank": PMOS_BANK,
        "nmos_bank": NMOS_BANK,
        "rail_handoff": RAIL_HANDOFF,
        "rail_handoff_ns": RAIL_HANDOFF_NS,
        "rail_handoff_ron_ohm": RAIL_HANDOFF_RON,
        "transistor_handoff": TRANSISTOR_HANDOFF,
        "transistor_handoff_ns": TRANSISTOR_HANDOFF_NS,
        "transistor_handoff_dead_ns": TRANSISTOR_HANDOFF_DEAD_NS,
        "transistor_handoff_rise_ns": TRANSISTOR_HANDOFF_RISE_NS,
        "bottom_keeper_ohm": BOTTOM_KEEPER_OHM,
        "reclamp": RECLAMP,
        "reclamp_ns": RECLAMP_NS,
        "isolated_handoff": ISOLATED_HANDOFF,
        "isolated_reconnect_ns": ISOLATED_RECONNECT_NS,
        "active_hold": ACTIVE_HOLD,
        "active_hold_ns": ACTIVE_HOLD_NS,
        "active_hold_width_um": ACTIVE_HOLD_WIDTH,
        "active_hold_length_um": ACTIVE_HOLD_L,
        "max_settling_error_v": max((row["settling_error_v"] for row in measured), default=None),
        "all_codes_within_half_lsb": all_codes_within_half_lsb,
        "all_bottom_plates_legal": all_bottom_plates_legal,
        "measured_code_order_monotonic": monotonic,
        "rows": rows,
        "claim_boundary": {
            "allowed": "measures a binary capacitor array driven by Sky130 MOS sampling and bottom-plate switches",
            "not_allowed": "does not prove capacitor mismatch statistics, reference loading across a full SAR, comparator coupling, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Transistor-Switched Capacitor DAC", "",
        f"- status: `{report['status']}`",
        f"- codes measured: `{report['measured_code_count']}` of `{report['code_count']}`",
        f"- half-LSB target V: `{half_lsb:.9e}`",
        f"- maximum settling error V: `{report['max_settling_error_v']:.9e}`" if measured else "- maximum settling error V: not measured",
        f"- all measured codes within half-LSB: `{all_pass}`",
        f"- measured code order monotonic: `{monotonic}`", "",
        "## First-Principles Reading", "",
        "The capacitor array stores charge, but the MOS switches determine how quickly charge arrives and how much error the sampling edge leaves behind. This fixture replaces the ideal switch boundary with Sky130 NMOS/PMOS devices and keeps the code-dependent top-plate measurement unchanged.", "",
        "A pass here would establish a transistor-switched DAC boundary, not a complete SAR. A failure means the switch sizing, timing, common-mode range, or capacitor ratio must be repaired before coupling the DAC to the comparator.", "",
        "## Refused Claim", "",
        report["claim_boundary"]["not_allowed"], "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured_code_count,{report['measured_code_count']}")
    print(f"max_settling_error_v,{report['max_settling_error_v']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
