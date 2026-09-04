#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
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
PREAMP_JSON = EVIDENCE / "sky130-known-good-shape-preamp-transient-latch-debug.json"
DECK_OUT = SPICE_DIR / "sky130_latch_alone_from_preamp_voltage_debug.sp"
CSV_OUT = MEASUREMENTS / "sky130-latch-alone-from-preamp-voltage-debug.csv"
OUT_JSON = EVIDENCE / "sky130-latch-alone-from-preamp-voltage-debug.json"
OUT_MD = EVIDENCE / "sky130-latch-alone-from-preamp-voltage-debug.md"
NGSPICE_TIMEOUT_S = 80


@dataclass(frozen=True)
class Case:
    name: str
    input_diff_mv: float
    pre_p_v: float
    pre_n_v: float


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_measure(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.search(rf"{re.escape(name)}\s+=\s+([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice measurement {name!r}, found none")
    return values[-1]


def build_deck(case: Case) -> str:
    return f"""* Sky130 latch-alone from measured preamp voltages.
* The preamp is replaced by ideal DC sources at the measured 2ns preamp outputs.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn_latch=3.0
.param wp_latch=6.0
.param wn_in=0.5
.param wn_tail=20.0
.param vinp={case.pre_p_v:.12f}
.param vinn={case.pre_n_v:.12f}
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12

VDD vdd 0 {{vdd}}
VINP inp 0 {{vinp}}
VINN inn 0 {{vinn}}
VCLK clk 0 PULSE(0 {{vdd}} 0.20n 20p 20p 5n 10n)
VCLKB clkb 0 PULSE({{vdd}} 0 0.20n 20p 20p 5n 10n)

XPREP vdd clkb outp vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XPREN vdd clkb outn vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLP outp outn vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XLN outp outn eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XRP outn outp vdd vdd sky130_fd_pr__pfet_01v8 W={{wp_latch}} L={{lmin}}
XRN outn outp eval 0 sky130_fd_pr__nfet_01v8 W={{wn_latch}} L={{lmin}}
XINP outp inp tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XINN outn inn tail 0 sky130_fd_pr__nfet_01v8 W={{wn_in}} L={{lmin}}
XTAIL tail clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
XEVAL eval clk 0 0 sky130_fd_pr__nfet_01v8 W={{wn_tail}} L={{lmin}}
COUTP outp 0 5f
COUTN outn 0 5f

.ic v(outp)=1.8 v(outn)=1.8
.tran 2p 2n uic
.measure tran outp_final_v FIND v(outp) AT=1.80n
.measure tran outn_final_v FIND v(outn) AT=1.80n
.measure tran output_diff_final_v PARAM='outn_final_v-outp_final_v'
.control
set noaskquit
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    print(f"case,{case.name}", flush=True)
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    expected_sign = 1 if case.input_diff_mv > 0 else -1
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"case": case.name, "input_diff_mv": case.input_diff_mv, "measured": False, "ngspice_timed_out": True, "ngspice_returncode": None, "resolved_correct_polarity": False}
    row: dict[str, Any] = {"case": case.name, "input_diff_mv": case.input_diff_mv, "measured": result.returncode == 0, "ngspice_timed_out": False, "ngspice_returncode": result.returncode, "pre_p_v": case.pre_p_v, "pre_n_v": case.pre_n_v}
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        row["resolved_correct_polarity"] = False
        return row
    output_diff = read_measure(result.stdout, "output_diff_final_v")
    measured_sign = 1 if output_diff > 0 else -1 if output_diff < 0 else 0
    row.update(
        {
            "outp_final_v": read_measure(result.stdout, "outp_final_v"),
            "outn_final_v": read_measure(result.stdout, "outn_final_v"),
            "output_diff_final_v": output_diff,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "resolved_correct_polarity": measured_sign == expected_sign and abs(output_diff) >= 0.9,
        }
    )
    return row


def build_cases(preamp: dict[str, Any]) -> list[Case]:
    cases: list[Case] = []
    for row in preamp["rows"]:
        cases.append(Case(str(row["case"]), float(row["input_diff_mv"]), float(row["outp_2n_v"]), float(row["outn_2n_v"])))
    return cases


def build_report() -> dict[str, Any]:
    preamp = json.loads(PREAMP_JSON.read_text(encoding="utf-8"))
    rows = [run_case(case) for case in build_cases(preamp)]
    measured = [row for row in rows if row["measured"]]
    resolved = sum(1 for row in rows if row.get("resolved_correct_polarity"))
    passed = len(measured) == len(rows) and resolved == len(rows)
    return {
        "result_type": "sky130_latch_alone_from_preamp_voltage_debug",
        "status": "latch_alone_from_preamp_voltage_passed_ready_for_clock_timing" if passed else "latch_alone_from_preamp_voltage_failed",
        "source_preamp_transient": rel(PREAMP_JSON),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "resolved_correct_polarity_count": resolved,
        "minimum_abs_latch_output_diff_v": min((abs(row["output_diff_final_v"]) for row in measured), default=0.0),
        "uses_ideal_sources_from_measured_preamp_voltages": True,
        "uses_sampled_nodes": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "rows": rows,
        "claim_boundary": {
            "allowed": "checks whether the clocked latch resolves when driven by ideal sources equal to the measured preamp transient outputs",
            "not_allowed": "does not prove sampled-node kickback, coupled preamp/latch loading, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence",
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
        "# Sky130 Latch-Alone From Preamp Voltage Debug",
        "",
        f"- status: `{report['status']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- resolved correct polarity count: `{report['resolved_correct_polarity_count']}`",
        f"- minimum abs latch output diff V: `{report['minimum_abs_latch_output_diff_v']:.9e}`",
        f"- uses ideal sources from measured preamp voltages: `{report['uses_ideal_sources_from_measured_preamp_voltages']}`",
        f"- uses sampled nodes: `{report['uses_sampled_nodes']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The preamp now settles by itself. The next smaller question is whether the latch can decide when the preamp is replaced by ideal voltage sources at those measured output values.",
        "",
        "This removes sampled-node kickback and preamp loading. If this passes, the latch core can read the preamp voltage in principle. The next question becomes clock timing and then coupled kickback.",
        "",
        "## Results",
        "",
        "| case | measured | pre_p V | pre_n V | output diff V | resolved |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| `{row['case']}` | `{row['measured']}` | `{fmt(row.get('pre_p_v'))}` | `{fmt(row.get('pre_n_v'))}` | `{fmt(row.get('output_diff_final_v'))}` | `{row.get('resolved_correct_polarity')}` |"
        )
    lines.extend(["", "## Boundary", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_outputs(report)
    print("sky130_latch_alone_from_preamp_voltage_debug")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"resolved_correct_polarity_count,{report['resolved_correct_polarity_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
