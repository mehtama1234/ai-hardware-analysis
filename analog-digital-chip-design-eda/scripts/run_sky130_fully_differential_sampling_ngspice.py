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
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
DECK_OUT = SPICE_DIR / "sky130_fully_differential_sampling.sp"
CSV_OUT = MEASUREMENTS / "sky130-fully-differential-sampling-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-fully-differential-sampling-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-fully-differential-sampling-ngspice.md"
NGSPICE_TIMEOUT_S = 180


@dataclass(frozen=True)
class Case:
    name: str
    diff_v: float


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
    vp = 0.9 + case.diff_v / 2.0
    vn = 0.9 - case.diff_v / 2.0
    return f"""* Sky130 fully differential sampling fixture.
* Two matched transmission gates sample opposite sides of a differential voltage.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param csample=0.2p
.param cload=0.05p
.param vinp={vp}
.param vinn={vn}

VDD vdd 0 {{vdd}}
VSS vss 0 0
VINP inp 0 PULSE(0 {{vinp}} 0.1n 20p 20p 20n 40n)
VINN inn 0 PULSE(0 {{vinn}} 0.1n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.2n 20p 20p 7n 20n)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.2n 20p 20p 7n 20n)

XSWNP inp ctrl sp vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XSWPP inp ctrlb sp vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}
XSWNN inn ctrl sn vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XSWPN inn ctrlb sn vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}

CSP sp 0 {{csample}}
CSN sn 0 {{csample}}
CLP sp 0 {{cload}}
CLN sn 0 {{cload}}
RLEAKP sp 0 100G
RLEAKN sn 0 100G

.tran 2p 10n
.measure tran acquired_p_v FIND v(sp) AT=6.8n
.measure tran acquired_n_v FIND v(sn) AT=6.8n
.measure tran held_p_v FIND v(sp) AT=8.5n
.measure tran held_n_v FIND v(sn) AT=8.5n
.measure tran input_p_v FIND v(inp) AT=6.8n
.measure tran input_n_v FIND v(inn) AT=6.8n
.control
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    half_lsb_12b_v = 1.8 / 4096.0 / 2.0
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {
            "case": case.name,
            "target_diff_v": case.diff_v,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
            "half_lsb_12b_v": half_lsb_12b_v,
            "pass_diff_hold_delta_half_lsb_12b": False,
            "pass_diff_total_error_half_lsb_12b": False,
        }
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    input_p_v = read_measure(result.stdout, "input_p_v")
    input_n_v = read_measure(result.stdout, "input_n_v")
    acquired_p_v = read_measure(result.stdout, "acquired_p_v")
    acquired_n_v = read_measure(result.stdout, "acquired_n_v")
    held_p_v = read_measure(result.stdout, "held_p_v")
    held_n_v = read_measure(result.stdout, "held_n_v")
    input_diff_v = input_p_v - input_n_v
    acquired_diff_v = acquired_p_v - acquired_n_v
    held_diff_v = held_p_v - held_n_v
    p_hold_abs_delta_v = abs(held_p_v - acquired_p_v)
    n_hold_abs_delta_v = abs(held_n_v - acquired_n_v)
    diff_hold_abs_delta_v = abs(held_diff_v - acquired_diff_v)
    diff_total_abs_error_v = abs(input_diff_v - held_diff_v)
    row = {
        "case": case.name,
        "target_diff_v": case.diff_v,
        "input_p_v": input_p_v,
        "input_n_v": input_n_v,
        "acquired_p_v": acquired_p_v,
        "acquired_n_v": acquired_n_v,
        "held_p_v": held_p_v,
        "held_n_v": held_n_v,
        "input_diff_v": input_diff_v,
        "acquired_diff_v": acquired_diff_v,
        "held_diff_v": held_diff_v,
        "p_hold_abs_delta_v": p_hold_abs_delta_v,
        "n_hold_abs_delta_v": n_hold_abs_delta_v,
        "diff_hold_abs_delta_v": diff_hold_abs_delta_v,
        "diff_total_abs_error_v": diff_total_abs_error_v,
        "half_lsb_12b_v": half_lsb_12b_v,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }
    row["pass_diff_hold_delta_half_lsb_12b"] = row["diff_hold_abs_delta_v"] <= half_lsb_12b_v
    row["pass_diff_total_error_half_lsb_12b"] = row["diff_total_abs_error_v"] <= half_lsb_12b_v
    return row


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    rows = [run_case(case) for case in [Case("mid_diff_0p2", 0.2)]]
    measured = [row for row in rows if not row["ngspice_timed_out"]]
    return {
        "result_type": "sky130_fully_differential_sampling_ngspice",
        "status": "sky130_fully_differential_sampling_characterized_not_converter_proof",
        "topology": "matched_transmission_gate_differential_sample_hold_from_baseline",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "device_models": ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"],
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
        "rows": rows,
        "half_lsb_12b_v": 1.8 / 4096.0 / 2.0,
        "worst_single_node_hold_abs_delta_v": max((max(row["p_hold_abs_delta_v"], row["n_hold_abs_delta_v"]) for row in measured), default=None),
        "worst_diff_hold_abs_delta_v": max((row["diff_hold_abs_delta_v"] for row in measured), default=None),
        "worst_diff_total_abs_error_v": max((row["diff_total_abs_error_v"] for row in measured), default=None),
        "diff_hold_pass_count": sum(1 for row in rows if row["pass_diff_hold_delta_half_lsb_12b"]),
        "diff_total_error_pass_count": sum(1 for row in rows if row["pass_diff_total_error_half_lsb_12b"]),
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "characterizes a one-case matched Sky130 transmission-gate fully differential sampling fixture copied from the known-running hold-mode pattern",
            "not_allowed": "does not prove comparator offset, noise, SAR conversion, mismatch across devices, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics",
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
        "# Sky130 Fully Differential Sampling Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- PDK model library: `{report['pdk_model_library']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed out case count: `{report['timed_out_case_count']}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- worst single-node hold abs delta V: `{fmt(report['worst_single_node_hold_abs_delta_v'])}`",
        f"- worst differential hold abs delta V: `{fmt(report['worst_diff_hold_abs_delta_v'])}`",
        f"- worst differential total abs error V: `{fmt(report['worst_diff_total_abs_error_v'])}`",
        f"- differential hold pass count: `{report['diff_hold_pass_count']}` of `{report['case_count']}`",
        f"- differential total error pass count: `{report['diff_total_error_pass_count']}` of `{report['case_count']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A comparator does not care about one stored node by itself. It decides from the difference between two nodes. If clock feedthrough moves both nodes in the same direction, the common movement can disappear from the decision voltage.",
        "",
        "This fixture samples a positive and negative side with matched Sky130 transmission gates and the same clocks. It then measures both the single-node movement and the differential movement. The important number is the differential hold error, because that is what a later comparator would see.",
        "",
        "This is still not a converter. It has no comparator offset, no noise, no SAR loop, no mismatch sweep, and no extracted layout. It is a focused test of whether differential sampling is a better next front-end direction than single-ended holding.",
        "",
        "## Results",
        "",
        "| case | input diff V | acquired diff V | held diff V | p hold delta V | n hold delta V | differential hold delta V | differential total error V |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        if row["ngspice_timed_out"]:
            lines.append(f"| {row['case']} | `{row['target_diff_v']:.9f}` | timeout | timeout | timeout | timeout | timeout | timeout |")
            continue
        lines.append(
            f"| {row['case']} | `{row['input_diff_v']:.9f}` | `{row['acquired_diff_v']:.9f}` | `{row['held_diff_v']:.9f}` | `{row['p_hold_abs_delta_v']:.9e}` | `{row['n_hold_abs_delta_v']:.9e}` | `{row['diff_hold_abs_delta_v']:.9e}` | `{row['diff_total_abs_error_v']:.9e}` |"
        )
    lines.extend(
        [
            "",
            "## Reading The Result",
            "",
            "If the single nodes move but the difference barely moves, differential sampling is doing useful work. It does not make charge injection vanish. It makes the later decision less sensitive to the part of charge injection that is shared by both sides.",
            "",
            "## Refused Claim",
            "",
            report["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_fully_differential_sampling_ngspice")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"worst_single_node_hold_abs_delta_v,{fmt(report['worst_single_node_hold_abs_delta_v'])}")
    print(f"worst_diff_hold_abs_delta_v,{fmt(report['worst_diff_hold_abs_delta_v'])}")
    print(f"worst_diff_total_abs_error_v,{fmt(report['worst_diff_total_abs_error_v'])}")
    print(f"diff_hold_pass_count,{report['diff_hold_pass_count']}")
    print(f"diff_total_error_pass_count,{report['diff_total_error_pass_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
