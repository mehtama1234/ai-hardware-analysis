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
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
OUTPUT_STEM = os.environ.get("AIMC_LATCH_OUTPUT_STEM", "sky130-clocked-comparator-latch-ngspice")
DECK_OUT = SPICE_DIR / f"{OUTPUT_STEM}.sp"
CSV_OUT = MEASUREMENTS / f"{OUTPUT_STEM}.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / f"{OUTPUT_STEM}.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / f"{OUTPUT_STEM}.md"
SPEC_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-acceptance-fixture-spec.json"
NGSPICE_TIMEOUT_S = 120


@dataclass(frozen=True)
class Case:
    name: str
    diff_mv: float


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_measure(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.search(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice measurement {name!r}, found none")
    return values[-1]


def build_deck(case: Case) -> str:
    diff_v = case.diff_mv / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    return f"""* Sky130 clocked comparator latch proxy.
* Cross-coupled inverter latch with an nfet input pair and ideal input voltages.
* This is a schematic-level latch fixture, not extracted layout and not noise proof.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn_latch=3.0
.param wp_latch=6.0
.param wn_in=10.0
.param wn_tail=20.0
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}

VDD vdd 0 {{vdd}}
VINP inp 0 {{vinp}}
VINN inn 0 {{vinn}}
VCLK clk 0 PULSE(0 {{vdd}} 1n 20p 20p 5n 10n)
VCLKB clkb 0 PULSE({{vdd}} 0 1n 20p 20p 5n 10n)

* Precharge both latch nodes high before evaluation.
XPREP vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XPREN vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}

* Cross-coupled inverter latch.
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}

* Differential input pair steers the falling side during evaluation.
XINP outp inp tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XINN outn inn tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}

COUTP outp 0 5f
COUTN outn 0 5f
.ic v(outp)=1.8 v(outn)=1.8 v(tail)=0 v(eval)=0

.tran 2p 3n uic
.measure tran outp_pre_v FIND v(outp) AT=0.8n
.measure tran outn_pre_v FIND v(outn) AT=0.8n
.measure tran outp_final_v FIND v(outp) AT=2.6n
.measure tran outn_final_v FIND v(outn) AT=2.6n
.measure tran output_diff_final_v PARAM='outn_final_v-outp_final_v'
.measure tran input_kick_proxy_v PARAM='abs(vinp-vinn)'
.control
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {
            "case": case.name,
            "input_diff_mv": case.diff_mv,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
            "resolved_correct_polarity": False,
        }
    if result.returncode != 0:
        return {
            "case": case.name,
            "input_diff_mv": case.diff_mv,
            "ngspice_returncode": result.returncode,
            "ngspice_timed_out": False,
            "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
            "ngspice_error_excerpt": (result.stdout + result.stderr)[-1200:],
            "resolved_correct_polarity": False,
        }
    outp_final_v = read_measure(result.stdout, "outp_final_v")
    outn_final_v = read_measure(result.stdout, "outn_final_v")
    output_diff_final_v = read_measure(result.stdout, "output_diff_final_v")
    expected_sign = 1 if case.diff_mv > 0 else -1
    measured_sign = 1 if output_diff_final_v > 0 else -1 if output_diff_final_v < 0 else 0
    logic_separation_v = abs(output_diff_final_v)
    return {
        "case": case.name,
        "input_diff_mv": case.diff_mv,
        "outp_pre_v": read_measure(result.stdout, "outp_pre_v"),
        "outn_pre_v": read_measure(result.stdout, "outn_pre_v"),
        "outp_final_v": outp_final_v,
        "outn_final_v": outn_final_v,
        "output_diff_final_v": output_diff_final_v,
        "logic_separation_v": logic_separation_v,
        "expected_sign": expected_sign,
        "measured_sign": measured_sign,
        "resolved_correct_polarity": expected_sign == measured_sign and logic_separation_v >= 0.9,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
    budget = spec["derived_budget"]
    target_mv = float(os.environ.get("AIMC_LATCH_INPUT_DIFF_MV", budget["target_combined_offset_noise_mv"]))
    hard_budget_mv = float(budget["remaining_comparator_offset_or_noise_budget_mv"])
    cases = [
        Case("negative_target_edge", -target_mv),
        Case("positive_target_edge", target_mv),
    ]
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if not row.get("ngspice_timed_out") and row.get("ngspice_returncode") == 0]
    pass_count = sum(1 for row in rows if row.get("resolved_correct_polarity") is True)
    all_pass = pass_count == len(rows)
    return {
        "result_type": "sky130_clocked_comparator_latch_ngspice",
        "status": "sky130_clocked_comparator_latch_proxy_passed_not_noise_or_layout_proof" if all_pass else "sky130_clocked_comparator_latch_proxy_characterized_not_accepted",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "device_models": ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"],
        "topology": "clocked_cross_coupled_inverter_latch_with_sky130_nfet_input_pair",
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row.get("ngspice_timed_out")),
        "target_combined_offset_noise_mv": target_mv,
        "hard_budget_mv": hard_budget_mv,
        "resolved_correct_polarity_count": pass_count,
        "all_cases_resolve_correct_polarity": all_pass,
        "resolution_threshold_v": 0.9,
        "rows": rows,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "runs a first Sky130 clocked latch proxy at the measured comparator target edge and records whether the latch resolves with the expected polarity",
            "not_allowed": "does not prove comparator noise, input-referred offset statistics, kickback into the sampled nodes, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Clocked Comparator Latch Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- target combined offset/noise mV: `{report['target_combined_offset_noise_mv']:.4f}`",
        f"- hard budget mV: `{report['hard_budget_mv']:.4f}`",
        f"- resolved correct polarity count: `{report['resolved_correct_polarity_count']}` of `{report['case_count']}`",
        f"- resolution threshold V: `{report['resolution_threshold_v']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "The input-stage proxy only showed that a tiny voltage difference can lean a transistor pair in the right direction. A comparator also has to make a timed decision. A clocked latch starts near an undecided state, then positive feedback pushes one side high and the other side low.",
        "",
        "This fixture checks that timed decision in the smallest useful way. It applies the already-derived target-edge input difference, turns on a Sky130 latch, and asks whether the final output polarity matches the input sign with enough voltage separation to be read as a logic decision.",
        "",
        "This is still not the finished ADC comparator. The inputs are ideal voltage sources, so this run does not yet measure kickback into the real sampled nodes. It does not run noise, mismatch statistics, SAR bit cycling, extracted layout, or post-layout economics.",
        "",
        "## Results",
        "",
        "| case | input diff mV | outp final V | outn final V | output diff V | resolved correct polarity |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        if row.get("ngspice_returncode") != 0:
            lines.append(f"| `{row['case']}` | `{row['input_diff_mv']:.6f}` | failed | failed | failed | `False` |")
            continue
        lines.append(
            f"| `{row['case']}` | `{row['input_diff_mv']:.6f}` | `{row['outp_final_v']:.9f}` | `{row['outn_final_v']:.9f}` | `{row['output_diff_final_v']:.9e}` | `{row['resolved_correct_polarity']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_clocked_comparator_latch_ngspice")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"resolved_correct_polarity_count,{report['resolved_correct_polarity_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
