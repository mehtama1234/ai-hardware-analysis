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
DECK_OUT = SPICE_DIR / "sky130_buffered_sample_hold.sp"
CSV_OUT = MEASUREMENTS / "sky130-buffered-sample-hold-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-buffered-sample-hold-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-buffered-sample-hold-ngspice.md"
NGSPICE_TIMEOUT_S = 5


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


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def build_deck(case: Case) -> str:
    return f"""* Sky130 buffered sample-and-hold fixture.
* The sample capacitor drives a MOS gate; the readout load is moved to the source follower output.

.lib "{PDK_LIB}" tt
.param vin={case.input_v}
.param vdd=1.8
.param lmin=0.15
.param sw_wn=2.0
.param sw_wp=4.0
.param buf_wn=8.0
.param bias_wn=1.0
.param csample=0.2p
.param cout=0.05p

VDD vdd 0 {{vdd}}
VSS vss 0 0
VIN in 0 PULSE(0 {{vin}} 0.1n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.2n 20p 20p 7n 20n)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.2n 20p 20p 7n 20n)
VBIAS bias 0 0.55

XSWN in ctrl sample vss sky130_fd_pr__nfet_01v8 W={{sw_wn}} L={{lmin}}
XSWP in ctrlb sample vdd sky130_fd_pr__pfet_01v8 W={{sw_wp}} L={{lmin}}
CSAMPLE sample 0 {{csample}}
RLEAK sample 0 100G

XBUF vdd sample out vss sky130_fd_pr__nfet_01v8 W={{buf_wn}} L={{lmin}}
XBIAS out bias vss vss sky130_fd_pr__nfet_01v8 W={{bias_wn}} L={{lmin}}
COUT out 0 {{cout}}

.tran 10p 12n
.measure tran acquired_sample_v FIND v(sample) AT=6.8n
.measure tran held_sample_v FIND v(sample) AT=8.5n
.measure tran acquired_out_v FIND v(out) AT=6.8n
.measure tran held_out_v FIND v(out) AT=8.5n
.measure tran input_v FIND v(in) AT=6.8n
.measure tran sample_hold_abs_delta_v PARAM='abs(held_sample_v-acquired_sample_v)'
.measure tran output_hold_abs_delta_v PARAM='abs(held_out_v-acquired_out_v)'
.measure tran output_gain_v_per_v PARAM='held_out_v/held_sample_v'
.control
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    half_lsb_12b_v = 1.8 / 4096.0 / 2.0
    try:
        result = subprocess.run(
            ["ngspice", "-b", str(DECK_OUT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=NGSPICE_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return {
            "case": case.name,
            "target_input_v": case.input_v,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
            "half_lsb_12b_v": half_lsb_12b_v,
            "pass_sample_hold_delta_half_lsb_12b": False,
            "pass_output_hold_delta_half_lsb_12b": False,
        }
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    acquired_sample_v = read_measure(result.stdout, "acquired_sample_v")
    held_sample_v = read_measure(result.stdout, "held_sample_v")
    acquired_out_v = read_measure(result.stdout, "acquired_out_v")
    held_out_v = read_measure(result.stdout, "held_out_v")
    input_v = read_measure(result.stdout, "input_v")
    sample_hold = abs(held_sample_v - acquired_sample_v)
    output_hold = abs(held_out_v - acquired_out_v)
    return {
        "case": case.name,
        "target_input_v": case.input_v,
        "measured_input_v": input_v,
        "acquired_sample_v": acquired_sample_v,
        "held_sample_v": held_sample_v,
        "acquired_out_v": acquired_out_v,
        "held_out_v": held_out_v,
        "sample_hold_abs_delta_v": sample_hold,
        "output_hold_abs_delta_v": output_hold,
        "output_gain_v_per_v": read_measure(result.stdout, "output_gain_v_per_v"),
        "half_lsb_12b_v": half_lsb_12b_v,
        "pass_sample_hold_delta_half_lsb_12b": sample_hold <= half_lsb_12b_v,
        "pass_output_hold_delta_half_lsb_12b": output_hold <= half_lsb_12b_v,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    rows = [run_case(case) for case in [Case("low_buffered_hold", 0.3), Case("mid_buffered_hold", 0.9), Case("high_buffered_hold", 1.5)]]
    measured = [row for row in rows if not row["ngspice_timed_out"]]
    return {
        "result_type": "sky130_buffered_sample_hold_ngspice",
        "status": "sky130_buffered_sample_hold_characterized_not_converter_proof",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "device_models": ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"],
        "topology": "nfet_source_follower_readout_buffer_after_sample_capacitor",
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
        "rows": rows,
        "half_lsb_12b_v": 1.8 / 4096.0 / 2.0,
        "worst_sample_hold_abs_delta_v": max((row.get("sample_hold_abs_delta_v", 0) for row in measured), default=None),
        "worst_output_hold_abs_delta_v": max((row.get("output_hold_abs_delta_v", 0) for row in measured), default=None),
        "sample_hold_pass_count": sum(1 for row in rows if row["pass_sample_hold_delta_half_lsb_12b"]),
        "output_hold_pass_count": sum(1 for row in rows if row["pass_output_hold_delta_half_lsb_12b"]),
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "characterizes a Sky130 MOS source-follower readout buffer after the sample capacitor",
            "not_allowed": "does not prove a rail-to-rail buffer, comparator decision, SAR conversion, mismatch, noise, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics",
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
        "# Sky130 Buffered Sample-Hold Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- PDK model library: `{report['pdk_model_library']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed out case count: `{report['timed_out_case_count']}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- worst sample hold abs delta V: `{fmt(report['worst_sample_hold_abs_delta_v'])}`",
        f"- worst output hold abs delta V: `{fmt(report['worst_output_hold_abs_delta_v'])}`",
        f"- sample hold pass count: `{report['sample_hold_pass_count']}` of `{report['case_count']}`",
        f"- output hold pass count: `{report['output_hold_pass_count']}` of `{report['case_count']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A stored voltage should remember charge, not drive the rest of the readout path by itself. If the same tiny node both stores the value and drives load capacitance, any charge pulled by that load becomes voltage error on the memory node.",
        "",
        "This fixture puts a MOS source follower after the sample capacitor. The capacitor drives a gate, so the readout load is moved to a different node. That tests one concrete version of the buffered sample-and-hold idea from the topology decision gate.",
        "",
        "This is still only a first circuit candidate. A source follower has threshold drop, finite gain, bias current, input capacitance, limited swing, and possible convergence trouble. The useful question here is not whether this is a finished ADC front end. The question is whether isolating the stored node produces a measurable hold-mode improvement that deserves a stronger buffer design.",
        "",
        "## Results",
        "",
        "| case | input V | acquired sample V | held sample V | acquired output V | held output V | sample hold delta V | output hold delta V |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        if row["ngspice_timed_out"]:
            lines.append(f"| {row['case']} | `{row['target_input_v']:.9f}` | timeout | timeout | timeout | timeout | timeout | timeout |")
            continue
        lines.append(
            f"| {row['case']} | `{row['measured_input_v']:.9f}` | `{row['acquired_sample_v']:.9f}` | `{row['held_sample_v']:.9f}` | `{row['acquired_out_v']:.9f}` | `{row['held_out_v']:.9f}` | `{row['sample_hold_abs_delta_v']:.9e}` | `{row['output_hold_abs_delta_v']:.9e}` |"
        )
    lines.extend(
        [
            "",
            "## Reading The Result",
            "",
            "If the sample node still moves more than half an LSB, the buffer has not solved the memory problem. If the output node moves less but has poor gain or swing, the next buffer must be redesigned rather than accepted. If the cases time out, the fixture is also not acceptable evidence, because a converter proof has to be rerunnable and numerically stable.",
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
    print("sky130_buffered_sample_hold_ngspice")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"worst_sample_hold_abs_delta_v,{fmt(report['worst_sample_hold_abs_delta_v'])}")
    print(f"worst_output_hold_abs_delta_v,{fmt(report['worst_output_hold_abs_delta_v'])}")
    print(f"sample_hold_pass_count,{report['sample_hold_pass_count']}")
    print(f"output_hold_pass_count,{report['output_hold_pass_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
