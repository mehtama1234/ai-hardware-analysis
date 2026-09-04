#!/usr/bin/env python3
"""Measure a binary capacitor DAC with Sky130 MOS sampling/redistribution switches."""

from __future__ import annotations

import json
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from run_sky130_switched_capacitor_dac import CUNIT_F, CAPS_F, ROOT, VDD, VIN, measure

EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
OUT_JSON = EVIDENCE / "sky130-transistor-switched-capacitor-dac.json"
OUT_MD = EVIDENCE / "sky130-transistor-switched-capacitor-dac.md"
TIMEOUT_S = 60
CODES = tuple(range(16))


def deck(code: int) -> str:
    caps = []
    controls = []
    switches = []
    for bit, cap in enumerate(CAPS_F):
        selected = (code >> (3 - bit)) & 1
        caps.append(f"C{bit} top b{bit} {cap:.12e}")
        caps.append(f"CDUMMY{bit} b{bit} 0 0.01e-12")
        if selected:
            # Before the edge the NMOS holds the bottom plate at ground. At
            # the edge it turns off while the PMOS connects the plate to VDD.
            controls.extend([
                f"VGP{bit} gp{bit} 0 PULSE(1.8 0 1n 10p 10p 200n 1u)",
                f"VGN{bit} gn{bit} 0 PULSE(1.8 0 1n 10p 10p 200n 1u)",
            ])
            switches.extend([
                f"XBP{bit} b{bit} gp{bit} vdd vdd sky130_fd_pr__pfet_01v8 W=16.0 L=0.15",
                f"XBN{bit} b{bit} gn{bit} 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15",
            ])
        else:
            controls.extend([f"VGP{bit} gp{bit} 0 1.8", f"VGN{bit} gn{bit} 0 1.8"])
            switches.append(f"XBN{bit} b{bit} gn{bit} 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15")
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
{chr(10).join(switches)}
{chr(10).join(controls)}
.ic v(top)={VIN} v(b0)=0 v(b1)=0 v(b2)=0 v(b3)=0
.tran 10p 80n uic
.measure tran top_sampled_v FIND v(top) AT=0.8n
.measure tran top_early_v FIND v(top) AT=3.0n
.measure tran top_settled_v FIND v(top) AT=70.0n
.measure tran sample_settled_v FIND v(ctrl) AT=70.0n
.measure tran b0_settled_v FIND v(b0) AT=70.0n
.measure tran b1_settled_v FIND v(b1) AT=70.0n
.measure tran b2_settled_v FIND v(b2) AT=70.0n
.measure tran b3_settled_v FIND v(b3) AT=70.0n
.control
run
.endc
.end
"""


def run(code: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="aimc-transistor-cdac-") as tmp:
        path = Path(tmp) / "cdac.sp"
        path.write_text(deck(code), encoding="utf-8")
        try:
            result = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {"code": code, "measured": False, "timed_out": True}
    row: dict[str, Any] = {"code": code, "measured": result.returncode == 0, "timed_out": False, "returncode": result.returncode}
    if result.returncode != 0:
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
    with ThreadPoolExecutor(max_workers=1) as pool:
        rows = list(pool.map(run, CODES))
    measured = [row for row in rows if row["measured"]]
    half_lsb = VDD / 16.0 / 2.0
    all_pass = len(measured) == len(CODES) and all(row["settling_error_v"] <= half_lsb for row in measured)
    monotonic = bool(measured) and all(a["top_settled_v"] <= b["top_settled_v"] for a, b in zip(measured, measured[1:]))
    report = {
        "result_type": "sky130_transistor_switched_capacitor_dac",
        "status": "transistor_switched_capacitor_dac_passed_boundary" if all_pass else "transistor_switched_capacitor_dac_measured_but_half_lsb_failed",
        "bits": 4,
        "switch_devices": ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"],
        "code_count": len(CODES),
        "measured_code_count": len(measured),
        "half_lsb_v": half_lsb,
        "max_settling_error_v": max((row["settling_error_v"] for row in measured), default=None),
        "all_codes_within_half_lsb": all_pass,
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
