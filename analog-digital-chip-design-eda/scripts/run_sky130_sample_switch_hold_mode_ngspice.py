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
DECK_OUT = SPICE_DIR / "sky130_sample_switch_hold_mode.sp"
CSV_OUT = MEASUREMENTS / "sky130-sample-switch-hold-mode-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-hold-mode-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-hold-mode-ngspice.md"


@dataclass(frozen=True)
class Case:
    name: str
    input_v: float


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
    return f"""* Sky130 sample-switch hold-mode fixture for the AIMC converter handoff.
* This measures held-node movement after the sampling switch turns off.

.lib "{PDK_LIB}" tt
.param vin={case.input_v}
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param csample=0.2p
.param cload=0.05p

VDD vdd 0 {{vdd}}
VSS vss 0 0
VIN in 0 PULSE(0 {{vin}} 0.1n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.2n 20p 20p 7n 20n)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.2n 20p 20p 7n 20n)

XSWN in ctrl sample vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XSWP in ctrlb sample vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}
CSAMPLE sample 0 {{csample}}
CLOAD sample 0 {{cload}}
RLEAK sample 0 100G

.tran 2p 10n
.measure tran acquired_v FIND v(sample) AT=6.8n
.measure tran held_v FIND v(sample) AT=8.5n
.measure tran input_v FIND v(in) AT=6.8n
.measure tran hold_delta_v PARAM='held_v-acquired_v'
.measure tran hold_abs_delta_v PARAM='abs(held_v-acquired_v)'
.measure tran total_abs_error_v PARAM='abs(input_v-held_v)'
.control
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    half_lsb_12b_v = 1.8 / 4096.0 / 2.0
    acquired_v = read_measure(result.stdout, "acquired_v")
    held_v = read_measure(result.stdout, "held_v")
    input_v = read_measure(result.stdout, "input_v")
    return {
        "case": case.name,
        "target_input_v": case.input_v,
        "measured_input_v": input_v,
        "acquired_v": acquired_v,
        "held_v": held_v,
        "hold_delta_v": held_v - acquired_v,
        "hold_abs_delta_v": abs(held_v - acquired_v),
        "total_abs_error_v": abs(input_v - held_v),
        "half_lsb_12b_v": half_lsb_12b_v,
        "pass_hold_delta_half_lsb_12b": abs(held_v - acquired_v) <= half_lsb_12b_v,
        "pass_total_error_half_lsb_12b": abs(input_v - held_v) <= half_lsb_12b_v,
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    rows = [run_case(case) for case in [Case("low_hold", 0.3), Case("mid_hold", 0.9), Case("high_hold", 1.5)]]
    return {
        "result_type": "sky130_sample_switch_hold_mode_ngspice",
        "status": "sky130_sample_switch_hold_mode_characterized_not_converter_proof",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "device_models": ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"],
        "case_count": len(rows),
        "rows": rows,
        "worst_hold_abs_delta_v": max(row["hold_abs_delta_v"] for row in rows),
        "worst_total_abs_error_v": max(row["total_abs_error_v"] for row in rows),
        "half_lsb_12b_v": rows[0]["half_lsb_12b_v"],
        "hold_delta_pass_count": sum(1 for row in rows if row["pass_hold_delta_half_lsb_12b"]),
        "total_error_pass_count": sum(1 for row in rows if row["pass_total_error_half_lsb_12b"]),
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "characterizes held-node movement after a Sky130 MOS transmission-gate sample switch turns off",
            "not_allowed": "does not prove an ADC decision, comparator behavior, bottom-plate sampling fix, mismatch, noise, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Sample Switch Hold Mode Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- PDK model library: `{report['pdk_model_library']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- device models: `{', '.join(report['device_models'])}`",
        f"- case count: `{report['case_count']}`",
        f"- worst hold abs delta V: `{report['worst_hold_abs_delta_v']:.9e}`",
        f"- worst total abs error V: `{report['worst_total_abs_error_v']:.9e}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- hold delta pass count: `{report['hold_delta_pass_count']}` of `{report['case_count']}`",
        f"- total error pass count: `{report['total_error_pass_count']}` of `{report['case_count']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A sampled voltage is stored charge. Once the switch turns off, the sample node should stop following the input. But the switch gate still has capacitance to the sample node, and the channel charge has to go somewhere. That can push the held voltage up or down.",
        "",
        "This fixture separates two questions. The earlier sample-switch run measured whether the sample node can follow the input while the switch is on. This run measures what happens after turn-off. If the held value moves too much, the next design work is not more software glue. It is circuit work: clock feedthrough reduction, charge cancellation, bottom-plate sampling, or a stronger sampling topology.",
        "",
        "## Results",
        "",
        "| case | input V | acquired V | held V | hold delta V | total error V | pass hold delta | pass total error |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['case']} | `{row['measured_input_v']:.9f}` | `{row['acquired_v']:.9f}` | `{row['held_v']:.9f}` | `{row['hold_delta_v']:.9e}` | `{row['total_abs_error_v']:.9e}` | `{row['pass_hold_delta_half_lsb_12b']}` | `{row['pass_total_error_half_lsb_12b']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_sample_switch_hold_mode_ngspice")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"worst_hold_abs_delta_v,{report['worst_hold_abs_delta_v']:.9e}")
    print(f"worst_total_abs_error_v,{report['worst_total_abs_error_v']:.9e}")
    print(f"hold_delta_pass_count,{report['hold_delta_pass_count']}")
    print(f"total_error_pass_count,{report['total_error_pass_count']}")
    print(f"candidate_post_layout_written,{report['candidate_post_layout_written']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
