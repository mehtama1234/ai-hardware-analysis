#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
SPICE_DIR = LAB / "spice"
MEASUREMENTS = LAB / "measurements"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
SPEC_JSON = EVIDENCE / "sky130-comparator-acceptance-fixture-spec.json"
CONVENTION_JSON = EVIDENCE / "sky130-clocked-latch-output-convention-diagnostic.json"
OUTPUT_STEM = os.environ.get("AIMC_CISO_OUTPUT_STEM", "sky130-corrected-convention-capacitive-isolation-confirm")
DECK_OUT = SPICE_DIR / f"{OUTPUT_STEM.replace('-', '_')}.sp"
CSV_OUT = MEASUREMENTS / f"{OUTPUT_STEM}.csv"
OUT_JSON = EVIDENCE / f"{OUTPUT_STEM}.json"
OUT_MD = EVIDENCE / f"{OUTPUT_STEM}.md"
NGSPICE_TIMEOUT_S = int(os.environ.get("AIMC_CISO_TIMEOUT_S", "160"))
EXPLICIT_GATE_RESET = os.environ.get("AIMC_CISO_EXPLICIT_GATE_RESET") == "1"
TRANSIENT_STEP = os.environ.get("AIMC_CISO_TRANSIENT_STEP", "2p")


@dataclass(frozen=True)
class Case:
    name: str
    coupling_cap_f: float
    diff_mv: float


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def sign(value: float) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def read_measure(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.search(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice measurement {name!r}, found none")
    return values[-1]


def cap_label(value: float) -> str:
    return f"{value * 1e15:g}f"


def build_deck(case: Case) -> str:
    diff_v = case.diff_mv / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    reset_block = """VGEQ geq 0 PULSE(0 {vdd} 0.10n 20p 20p 0.75n 20n)
XEQ gp gn geq 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XRESET_P gp geq vcm 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
XRESET_N gn geq vcm 0 sky130_fd_pr__nfet_01v8 W={wn_in} L={lmin}
""" if EXPLICIT_GATE_RESET else ""
    return f"""* Sky130 corrected-convention capacitive isolation confirm.
* Sample nodes drive latch input gates through tiny capacitors.
* Latch output is interpreted as outp-outn in Python.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param dummy_wn=1.0
.param dummy_wp=2.0
.param csample=0.2p
.param cload=0.05p
.param wn_latch=3.0
.param wp_latch=6.0
.param wn_in=0.5
.param wn_tail=20.0
.param ciso={case.coupling_cap_f:.12e}
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}

VDD vdd 0 {{vdd}}
VSS vss 0 0
VBIAS vcm 0 0.9
VINP inp 0 PULSE(0 {{vinp}} 0.05n 20p 20p 20n 40n)
VINN inn 0 PULSE(0 {{vinn}} 0.05n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.10n 20p 20p 0.75n 20n)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.10n 20p 20p 0.75n 20n)
VCLK clk 0 PULSE(0 {{vdd}} 1.00n 20p 20p 5n 10n)
VCLKB clkb 0 PULSE({{vdd}} 0 1.00n 20p 20p 5n 10n)

XSWNP inp ctrl sp vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XSWPP inp ctrlb sp vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}
XSWNN inn ctrl sn vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XSWPN inn ctrlb sn vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}
XDUMNP sp ctrlb sp vss sky130_fd_pr__nfet_01v8 W={{dummy_wn}} L={{lmin}}
XDUMPP sp ctrl sp vdd sky130_fd_pr__pfet_01v8 W={{dummy_wp}} L={{lmin}}
XDUMNN sn ctrlb sn vss sky130_fd_pr__nfet_01v8 W={{dummy_wn}} L={{lmin}}
XDUMPN sn ctrl sn vdd sky130_fd_pr__pfet_01v8 W={{dummy_wp}} L={{lmin}}
CSP sp 0 {{csample}}
CSN sn 0 {{csample}}
CLP sp 0 {{cload}}
CLN sn 0 {{cload}}
RLEAKP sp 0 100G
RLEAKN sn 0 100G

CISO_P sp gp {{ciso}}
CISO_N sn gn {{ciso}}
RBIASP gp vcm 100G
RBIASN gn vcm 100G
{reset_block}

XPREP vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XPREN vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XINP outp gp tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XINN outn gn tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
COUTP outp 0 5f
COUTN outn 0 5f

.tran {TRANSIENT_STEP} 3n
.measure tran sampled_p_before_v FIND v(sp) AT=0.90n
.measure tran sampled_n_before_v FIND v(sn) AT=0.90n
.measure tran sampled_p_after_v FIND v(sp) AT=2.60n
.measure tran sampled_n_after_v FIND v(sn) AT=2.60n
.measure tran gate_p_after_v FIND v(gp) AT=2.60n
.measure tran gate_n_after_v FIND v(gn) AT=2.60n
.measure tran outp_final_v FIND v(outp) AT=2.60n
.measure tran outn_final_v FIND v(outn) AT=2.60n
.control
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    print(f"case,{case.name}", flush=True)
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    half_lsb = 1.8 / 4096.0 / 2.0
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"case": case.name, "coupling_cap_f": case.coupling_cap_f, "input_diff_mv": case.diff_mv, "measured": False, "ngspice_timed_out": True, "ngspice_returncode": None, "resolved_correct_polarity": False, "kickback_below_half_lsb": False}
    row: dict[str, Any] = {"case": case.name, "coupling_cap_f": case.coupling_cap_f, "coupling_cap_ff": case.coupling_cap_f * 1e15, "input_diff_mv": case.diff_mv, "measured": result.returncode == 0, "ngspice_timed_out": False, "ngspice_returncode": result.returncode}
    if result.returncode != 0:
        row["ngspice_error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        row["resolved_correct_polarity"] = False
        row["kickback_below_half_lsb"] = False
        return row
    sampled_p_before = read_measure(result.stdout, "sampled_p_before_v")
    sampled_n_before = read_measure(result.stdout, "sampled_n_before_v")
    sampled_p_after = read_measure(result.stdout, "sampled_p_after_v")
    sampled_n_after = read_measure(result.stdout, "sampled_n_after_v")
    outp_final = read_measure(result.stdout, "outp_final_v")
    outn_final = read_measure(result.stdout, "outn_final_v")
    sampled_diff_before = sampled_p_before - sampled_n_before
    sampled_diff_after = sampled_p_after - sampled_n_after
    output_diff = outp_final - outn_final
    expected = sign(case.diff_mv)
    kickback = abs(sampled_diff_after - sampled_diff_before)
    row.update(
        {
            "sampled_p_before_v": sampled_p_before,
            "sampled_n_before_v": sampled_n_before,
            "sampled_p_after_v": sampled_p_after,
            "sampled_n_after_v": sampled_n_after,
            "sampled_diff_before_v": sampled_diff_before,
            "sampled_diff_after_v": sampled_diff_after,
            "sampled_diff_kickback_v": kickback,
            "gate_p_after_v": read_measure(result.stdout, "gate_p_after_v"),
            "gate_n_after_v": read_measure(result.stdout, "gate_n_after_v"),
            "outp_final_v": outp_final,
            "outn_final_v": outn_final,
            "output_diff_final_v": output_diff,
            "output_definition": "outp_minus_outn",
            "half_lsb_12b_v": half_lsb,
            "expected_sign": expected,
            "measured_sign": sign(output_diff),
            "resolved_correct_polarity": sign(output_diff) == expected and abs(output_diff) >= 0.9,
            "kickback_below_half_lsb": kickback <= half_lsb,
        }
    )
    return row


def build_report() -> dict[str, Any]:
    convention = json.loads(CONVENTION_JSON.read_text(encoding="utf-8"))
    if convention.get("inferred_clocked_latch_output_contract") != "digital_bit_positive_when_outp_exceeds_outn":
        raise ValueError("missing corrected output convention")
    spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
    target_mv = float(spec["derived_budget"]["target_combined_offset_noise_mv"])
    cases: list[Case] = []
    for cap in [0.1e-15, 0.2e-15]:
        cases.append(Case(f"ciso_{cap_label(cap)}_negative_target", cap, -target_mv))
        cases.append(Case(f"ciso_{cap_label(cap)}_positive_target", cap, target_mv))
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if row["measured"]]
    passing = [row for row in measured if row.get("resolved_correct_polarity") and row.get("kickback_below_half_lsb")]
    return {
        "result_type": "sky130_corrected_convention_capacitive_isolation_confirm",
        "status": "corrected_convention_capacitive_isolation_confirmed_not_noise_or_layout_proof" if len(passing) == len(rows) else "corrected_convention_capacitive_isolation_characterized_not_ready",
        "source_output_convention": rel(CONVENTION_JSON),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "passing_case_count": len(passing),
        "confirmed_coupling_caps_ff": sorted({row["coupling_cap_ff"] for row in passing}),
        "target_combined_offset_noise_mv": target_mv,
        "half_lsb_12b_v": 1.8 / 4096.0 / 2.0,
        "worst_sampled_diff_kickback_v": max((row.get("sampled_diff_kickback_v", 0.0) for row in measured), default=None),
        "minimum_abs_output_diff_v": min((abs(row.get("output_diff_final_v", 0.0)) for row in measured), default=None),
        "output_definition": "outp_minus_outn",
        "uses_capacitive_input_isolation": True,
        "uses_sampled_nodes": True,
        "uses_corrected_latch_output_convention": True,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "explicit_gate_reset": EXPLICIT_GATE_RESET,
        "transient_step": TRANSIENT_STEP,
        "rows": rows,
        "claim_boundary": {
            "allowed": "confirms the tiny-capacitor latch input isolation candidate in both polarities using the corrected outp-minus-outn output convention",
            "not_allowed": "does not prove comparator noise, offset statistics, SAR bit cycling, extracted layout, DRC/LVS, or accepted post-layout converter evidence",
        },
    }


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def write_outputs(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in report["rows"] for key in row})
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Corrected-Convention Capacitive Isolation Confirm",
        "",
        f"- status: `{report['status']}`",
        f"- output definition: `{report['output_definition']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- passing case count: `{report['passing_case_count']}`",
        f"- confirmed coupling caps fF: `{', '.join(f'{cap:g}' for cap in report['confirmed_coupling_caps_ff'])}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- worst sampled differential kickback V: `{fmt(report['worst_sampled_diff_kickback_v'])}`",
        f"- minimum abs output diff V: `{fmt(report['minimum_abs_output_diff_v'])}`",
        f"- uses capacitive input isolation: `{report['uses_capacitive_input_isolation']}`",
        f"- uses sampled nodes: `{report['uses_sampled_nodes']}`",
        f"- uses corrected latch output convention: `{report['uses_corrected_latch_output_convention']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The direct latch gate was too heavy for the sampled node. A tiny coupling capacitor changes the readout job: the sampled node no longer has to directly drive the latch transistor gate. It only has to move a small internal gate node enough for the latch to choose a side.",
        "",
        "This run keeps the sampled nodes connected, keeps the corrected `outp - outn` output convention, and tests the two capacitor values that previously looked useful. The proof target is narrow: both signs must resolve and sampled-node movement must stay below half of one 12-bit LSB.",
        "",
        "## Results",
        "",
        "| cap fF | input diff mV | kickback V | half LSB V | output diff V | resolved | kickback pass |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        if not row.get("measured"):
            lines.append(f"| `{row.get('coupling_cap_ff')}` | `{row['input_diff_mv']}` | failed | failed | failed | `False` | `False` |")
            continue
        lines.append(
            f"| `{row['coupling_cap_ff']:.3f}` | `{row['input_diff_mv']:.6f}` | `{row['sampled_diff_kickback_v']:.9e}` | `{row['half_lsb_12b_v']:.9e}` | `{row['output_diff_final_v']:.9e}` | `{row['resolved_correct_polarity']}` | `{row['kickback_below_half_lsb']}` |"
        )
    lines.extend(["", "## Boundary", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_outputs(report)
    print("sky130_corrected_convention_capacitive_isolation_confirm")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"passing_case_count,{report['passing_case_count']}")
    print(f"worst_sampled_diff_kickback_v,{report['worst_sampled_diff_kickback_v']}")
    print(f"minimum_abs_output_diff_v,{report['minimum_abs_output_diff_v']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
