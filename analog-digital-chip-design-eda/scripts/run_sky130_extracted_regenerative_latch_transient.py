#!/usr/bin/env python3
"""Run bounded polarity/regeneration tests on the extracted latch starter."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
EXTRACTED = LAB / "layout-workbench" / "extracted" / "sky130_regenerative_latch_starter_extracted.spice"
MODEL = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
DECK = LAB / "spice" / "sky130-extracted-regenerative-latch-starter-transient.sp"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-regenerative-latch-starter-transient.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-regenerative-latch-starter-transient.md"


def measure(text: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not values:
        raise ValueError(name)
    return float(values[-1])


def deck(diff_mv: float, initial_bias_mv: float) -> str:
    p = 0.9 + diff_mv / 2000.0
    n = 0.9 - diff_mv / 2000.0
    extracted = EXTRACTED.read_text(encoding="utf-8").replace("sky130_fd_pr__nfet_01v8", "LATCH_NMOS")
    extracted = re.sub(r"^X(\d+) ", r"M\1 ", extracted, flags=re.MULTILINE)
    initial_p = 0.9 + initial_bias_mv / 2000.0
    initial_n = 0.9 - initial_bias_mv / 2000.0
    return f'''* Extracted regenerative latch starter structural transient.
* Uses exact Magic-extracted connectivity and parasitic capacitors with a
* bounded level-1 MOS model; this is not a Sky130 model signoff run.
.global VSUBS
.model LATCH_NMOS nmos level=1 kp=200u vto=0.55 lambda=0.02
{extracted}
.options method=gear maxord=1 trtol=7 reltol=1e-4 abstol=1e-12 gmin=1e-9
VDD vdd 0 1.8
VSUB VSUBS 0 0
VSP sense_p 0 PULSE(0.9 {p:.12g} 0.50n 20p 20p 20n 40n)
VSN sense_n 0 PULSE(0.9 {n:.12g} 0.50n 20p 20p 20n 40n)
RLP vdd out_p 20k
RLN vdd out_n 20k
CLP out_p 0 5f
CLN out_n 0 5f
XU out_p out_n sense_p sense_n 0 sky130_regenerative_latch_starter
    .ic v(out_p)={initial_p:.12g} v(out_n)={initial_n:.12g}
.tran 20p 4n uic
.measure tran out_p_initial FIND v(out_p) AT=0.80n
.measure tran out_n_initial FIND v(out_n) AT=0.80n
.measure tran out_p_final FIND v(out_p) AT=3.00n
.measure tran out_n_final FIND v(out_n) AT=3.00n
.measure tran output_diff_final PARAM='out_p_final-out_n_final'
.measure tran output_diff_initial PARAM='out_p_initial-out_n_initial'
.control
run
.endc
.end
'''


def main() -> int:
    rows = []
    cases = [(diff, bias) for diff in (-0.5, 0.5, -10.0, 10.0) for bias in (-10.0, 10.0)]
    for diff, initial_bias in cases:
        DECK.write_text(deck(diff, initial_bias), encoding="utf-8")
        try:
            proc = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True,
                                  capture_output=True, check=False, timeout=120)
        except subprocess.TimeoutExpired:
            rows.append({"input_diff_mv": diff, "initial_output_bias_mv": initial_bias, "measured": False, "timed_out": True})
            continue
        row = {"input_diff_mv": diff, "initial_output_bias_mv": initial_bias, "measured": proc.returncode == 0, "timed_out": False,
               "returncode": proc.returncode}
        if proc.returncode == 0:
            row.update({"output_diff_initial_v": measure(proc.stdout, "output_diff_initial"),
                        "output_diff_final_v": measure(proc.stdout, "output_diff_final"),
                        "out_p_final_v": measure(proc.stdout, "out_p_final"),
                        "out_n_final_v": measure(proc.stdout, "out_n_final")})
            row["resolved_polarity_pass"] = (row["output_diff_final_v"] < 0) == (diff > 0)
            row["regenerated"] = abs(row["output_diff_final_v"]) >= 0.5
        else:
            row["error_excerpt"] = (proc.stdout + proc.stderr)[-1200:]
        rows.append(row)
    measured = [r for r in rows if r.get("measured")]
    passing = [r for r in measured if r.get("resolved_polarity_pass") and r.get("regenerated")]
    report = {
        "result_type": "sky130_extracted_regenerative_latch_starter_bistability_diagnostic",
        "status": "extracted_regenerative_latch_bistability_passed_not_noise_or_converter_signoff" if len(passing) == len(rows) else "extracted_regenerative_latch_bistability_open",
        "layout_extracted_netlist": str(EXTRACTED.relative_to(ROOT)),
        "transistor_model": "bounded level-1 structural model substituted for Sky130 model because the direct PDK-model run did not converge within the bounded timeout",
        "generated_deck": str(DECK.relative_to(ROOT)), "case_count": len(rows),
        "measured_case_count": len(measured), "passing_case_count": len(passing),
        "rows": rows, "accepted_post_layout_written": False,
        "claim_boundary": {"allowed": "tests polarity, regeneration, and startup-state dependence using the exact extracted connectivity and parasitic capacitors with a bounded structural MOS model",
                           "not_allowed": "does not prove noise, mismatch, kickback budget, LVS against a schematic, PVT yield, SAR conversion, or accepted converter evidence"},
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(["# Sky130 Extracted Regenerative Latch Starter Transient", "",
        f"- status: `{report['status']}`", f"- measured cases: `{len(measured)}` of `{len(rows)}`",
        f"- passing cases: `{len(passing)}`", "", "This is a bounded extracted-netlist transient test with resistive loads. It sweeps both input polarity and initial output bias to distinguish regenerative bistability from one-sided startup. It is not comparator or converter signoff.", "", "| input differential mV | initial output bias mV | final output differential V | polarity | regenerated |", "|---:|---:|---:|---|---|"] +
        [f"| `{r['input_diff_mv']}` | `{r['initial_output_bias_mv']}` | `{r.get('output_diff_final_v', 'failed')}` | `{r.get('resolved_polarity_pass', False)}` | `{r.get('regenerated', False)}` |" for r in rows] + ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured_case_count,{len(measured)}")
    print(f"passing_case_count,{len(passing)}")
    print(f"json,{OUT_JSON}")
    return 0 if len(measured) == len(rows) and len(passing) == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
