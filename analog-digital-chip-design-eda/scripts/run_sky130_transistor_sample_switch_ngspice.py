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
DECK_OUT = SPICE_DIR / "sky130_transistor_sample_switch.sp"
CSV_OUT = MEASUREMENTS / "sky130-transistor-sample-switch-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-sample-switch-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-sample-switch-ngspice.md"


@dataclass(frozen=True)
class Case:
    name: str
    input_v: float
    sample_time_ns: float


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
    return f"""* Sky130 MOS transmission-gate sample path for the AIMC converter handoff.
* This is a transistor-level switch fixture, not a complete ADC or DAC.

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

.tran 2p 8n
.measure tran sampled_v FIND v(sample) AT={case.sample_time_ns}n
.measure tran input_v FIND v(in) AT={case.sample_time_ns}n
.measure tran sample_error PARAM='abs(input_v-sampled_v)'
.measure tran switch_mid_v FIND v(sample) AT=0.5n
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
    sampled_v = read_measure(result.stdout, "sampled_v")
    measured_input_v = read_measure(result.stdout, "input_v")
    sample_error_v = abs(measured_input_v - sampled_v)
    half_lsb_12b_v = 1.8 / 4096.0 / 2.0
    return {
        "case": case.name,
        "target_input_v": case.input_v,
        "measured_input_v": measured_input_v,
        "sampled_v": sampled_v,
        "sample_error_v": sample_error_v,
        "half_lsb_12b_v": half_lsb_12b_v,
        "sample_time_ns": case.sample_time_ns,
        "switch_mid_v": read_measure(result.stdout, "switch_mid_v"),
        "pass_half_lsb_12b": sample_error_v <= half_lsb_12b_v,
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    cases = [
        Case("low_sample", 0.3, 6.8),
        Case("mid_sample", 0.9, 6.8),
        Case("high_sample", 1.5, 6.8),
    ]
    rows = [run_case(case) for case in cases]
    return {
        "result_type": "sky130_transistor_sample_switch_ngspice",
        "status": "sky130_transistor_sample_switch_passed_not_converter_proof" if all(row["pass_half_lsb_12b"] for row in rows) else "sky130_transistor_sample_switch_failed",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "device_models": ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"],
        "case_count": len(rows),
        "rows": rows,
        "worst_sample_error_v": max(row["sample_error_v"] for row in rows),
        "half_lsb_12b_v": rows[0]["half_lsb_12b_v"],
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "runs ngspice with Sky130 MOS models on a transmission-gate sample path and checks sampled-node error while the switch is still on",
            "not_allowed": "does not prove hold-mode feedthrough, DAC ladder behavior, SAR capacitor array behavior, comparator decision, mismatch, noise, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics",
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
        "# Sky130 Transistor Sample Switch Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- PDK model library: `{report['pdk_model_library']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- device models: `{', '.join(report['device_models'])}`",
        f"- case count: `{report['case_count']}`",
        f"- worst sample error V: `{report['worst_sample_error_v']:.9e}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A sample switch is a controlled path for charge. When the gate turns on, the input node and sample capacitor are connected through real transistor channel behavior. The sampled value is correct only if enough charge moves before the switch turns off.",
        "",
        "This fixture asks that question directly. It drives low, middle, and high input voltages through a Sky130 transmission gate into a sample capacitor. Then it checks whether the sample node is within half of one 12-bit output step while the switch is still on. That is one small part of an ADC boundary: the voltage must arrive before the digital decision can mean anything.",
        "",
        "This is not a full converter. It has no hold-mode feedthrough test, no capacitor DAC, no comparator, no SAR loop, no reference ladder, no mismatch run, and no extracted transistor layout. It proves only that this starter MOS sample path can be simulated with the installed Sky130 models and can settle under this fixture.",
        "",
        "## Results",
        "",
        "| case | input V | sampled V | error V | half LSB 12b V | pass |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['case']} | `{row['measured_input_v']:.9f}` | `{row['sampled_v']:.9f}` | `{row['sample_error_v']:.9e}` | `{row['half_lsb_12b_v']:.9e}` | `{row['pass_half_lsb_12b']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_transistor_sample_switch_ngspice")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"worst_sample_error_v,{report['worst_sample_error_v']:.9e}")
    print(f"half_lsb_12b_v,{report['half_lsb_12b_v']:.9e}")
    print(f"candidate_post_layout_written,{report['candidate_post_layout_written']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0 if report["status"] == "sky130_transistor_sample_switch_passed_not_converter_proof" else 1


if __name__ == "__main__":
    raise SystemExit(main())
