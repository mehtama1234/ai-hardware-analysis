#!/usr/bin/env python3
"""Measure a binary capacitor-DAC charge-redistribution boundary in ngspice."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-switched-capacitor-dac.json"
OUT_MD = EVIDENCE / "sky130-switched-capacitor-dac.md"
VDD = 1.8
VIN = 0.9
CAPS_F = (8e-12, 4e-12, 2e-12, 1e-12)
CUNIT_F = 1e-12
CODES = (0, 1, 7, 8, 13, 15)


def measure(stdout: str, name: str) -> float:
    matches = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", stdout)
    if not matches:
        raise ValueError(f"missing {name}")
    return float(matches[-1])


def deck(code: int) -> str:
    bit_lines = []
    controls = []
    for bit, cap in enumerate(CAPS_F):
        selected = (code >> (3 - bit)) & 1
        bit_lines.append(f"C{bit} top b{bit} {cap:.12e}")
        controls.append(f"VBP{bit} bp{bit} 0 {'PULSE(0 {VDD} 1n 10p 10p 10n 20n)' if selected else '0'}")
        controls.append(f"VBN{bit} bn{bit} 0 {'PULSE({VDD} 0 1n 10p 10p 10n 20n)' if selected else '1.8'}")
        bit_lines.append(f"S{bit}P b{bit} vdd bp{bit} 0 MYMOD")
        bit_lines.append(f"S{bit}N b{bit} 0 bn{bit} 0 MYMOD")
    return f"""* Sky130 AIMC binary switched-capacitor DAC boundary.
* The array is physical capacitive charge redistribution; switch models are ideal.
.param vdd={VDD}
.param vin={VIN}
VDD vdd 0 {{vdd}}
VIN vin 0 {{vin}}
VSAMPLE sample 0 PULSE(0 {{vdd}} 0.1n 10p 10p 0.9n 20n)
.model MYMOD SW(Ron=10 Roff=1e12 Vt=0.5 Vh=0.05)
SAMPLE vin top sample 0 MYMOD
{chr(10).join(bit_lines)}
{chr(10).join(controls)}
CDUMMY top 0 {CUNIT_F:.12e}
.ic v(top)={VIN} v(b0)=0 v(b1)=0 v(b2)=0 v(b3)=0
.tran 2p 4n uic
.measure tran top_sampled_v FIND v(top) AT=0.8n
.measure tran top_early_redistributed_v FIND v(top) AT=1.1n
.measure tran top_mid_redistributed_v FIND v(top) AT=1.5n
.measure tran top_settled_v FIND v(top) AT=3.0n
.measure tran sample_settled_v FIND v(sample) AT=3.0n
.measure tran b0_settled_v FIND v(b0) AT=3.0n
.measure tran b1_settled_v FIND v(b1) AT=3.0n
.measure tran b2_settled_v FIND v(b2) AT=3.0n
.measure tran b3_settled_v FIND v(b3) AT=3.0n
.control
run
.endc
.end
"""


def run(code: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="aimc-cdac-") as tmp:
        path = Path(tmp) / "cdac.sp"
        path.write_text(deck(code), encoding="utf-8")
        result = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=30)
    row: dict[str, Any] = {"code": code, "measured": result.returncode == 0, "returncode": result.returncode}
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1000:]
        return row
    top_sampled = measure(result.stdout, "top_sampled_v")
    top_settled = measure(result.stdout, "top_settled_v")
    expected = VIN + VDD * code / 16.0
    row.update({
        "top_sampled_v": top_sampled,
        "top_settled_v": top_settled,
        "sample_settled_v": measure(result.stdout, "sample_settled_v"),
        "top_early_redistributed_v": measure(result.stdout, "top_early_redistributed_v"),
        "top_mid_redistributed_v": measure(result.stdout, "top_mid_redistributed_v"),
        "expected_top_v": expected,
        "settling_error_v": abs(top_settled - expected),
        "redistribution_delta_v": top_settled - top_sampled,
        "bottom_plate_v": [measure(result.stdout, f"b{bit}_settled_v") for bit in range(4)],
    })
    return row


def main() -> int:
    rows = [run(code) for code in CODES]
    measured = [row for row in rows if row["measured"]]
    half_lsb = VDD / 16.0 / 2.0
    report = {
        "result_type": "sky130_switched_capacitor_dac",
        "status": "switched_capacitor_dac_passed_ideal_boundary_only" if measured and all(row["settling_error_v"] <= half_lsb for row in measured) else "switched_capacitor_dac_measured_but_half_lsb_failed",
        "bits": 4,
        "capacitor_values_f": list(CAPS_F) + [CUNIT_F],
        "code_count": len(CODES),
        "measured_code_count": len(measured),
        "half_lsb_v": half_lsb,
        "max_settling_error_v": max((row["settling_error_v"] for row in measured), default=None),
        "all_codes_within_half_lsb": bool(measured) and all(row["settling_error_v"] <= half_lsb for row in measured),
        "rows": rows,
        "claim_boundary": {
            "allowed": "measures charge redistribution and code-dependent top-plate settling for a binary capacitor array",
            "not_allowed": "does not prove transistor switch resistance, capacitor mismatch, DAC reference loading, comparator coupling, SAR conversion, extracted layout, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Switched-Capacitor DAC", "",
        f"- status: `{report['status']}`",
        f"- bits: `{report['bits']}`",
        f"- codes measured: `{report['measured_code_count']}` of `{report['code_count']}`",
        f"- half-LSB target V: `{half_lsb:.9e}`",
        f"- maximum settling error V: `{report['max_settling_error_v']:.9e}`" if measured else "- maximum settling error V: not measured",
        f"- all measured codes within half-LSB: `{report['all_codes_within_half_lsb']}`", "",
        "## First-Principles Reading", "",
        "A capacitor DAC does not create a voltage by instruction. During sampling, charge is placed on the top plate. During redistribution, the bottom plates move between reference and ground, and the top plate moves by charge conservation. The code is useful only if that movement settles close enough to the intended threshold before the comparator fires.", "",
        "This first boundary uses ideal switch models so the capacitor charge law can be isolated. The next circuit must replace those switches with the selected Sky130 transmission-gate or MOS implementation and measure resistance, charge injection, reference loading, and mismatch.", "",
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
