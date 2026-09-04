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
DECK_OUT = SPICE_DIR / "sky130_bottom_plate_sampling.sp"
CSV_OUT = MEASUREMENTS / "sky130-bottom-plate-sampling-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-bottom-plate-sampling-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-bottom-plate-sampling-ngspice.md"
NGSPICE_TIMEOUT_S = 20


@dataclass(frozen=True)
class Config:
    name: str
    top_off_ns: float
    bottom_off_ns: float
    sample_at_ns: float
    hold_at_ns: float


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


def build_deck(config: Config, input_v: float) -> str:
    return f"""* Sky130 bottom-plate sampling fixture.
* The stored value is the voltage across CSAMPLE: v(top)-v(bottom).

.lib "{PDK_LIB}" tt
.param vin={input_v}
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param csample=1.0p
.param cload=0.05p

VDD vdd 0 {{vdd}}
VSS vss 0 0
VIN in 0 PULSE(0 {{vin}} 0.1n 20p 20p 20n 40n)
VTOP top_ctrl 0 PULSE(0 {{vdd}} 0.2n 20p 20p {config.top_off_ns}n 20n)
VTOPB top_ctrlb 0 PULSE({{vdd}} 0 0.2n 20p 20p {config.top_off_ns}n 20n)
VBOT bot_ctrl 0 PULSE(0 {{vdd}} 0.2n 20p 20p {config.bottom_off_ns}n 20n)
VBOTB bot_ctrlb 0 PULSE({{vdd}} 0 0.2n 20p 20p {config.bottom_off_ns}n 20n)

XTOPN in top_ctrl top vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XTOPP in top_ctrlb top vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}
XBOTN bottom bot_ctrl vss vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XBOTP bottom bot_ctrlb vss vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}

CSAMPLE top bottom {{csample}}
CLOAD top 0 {{cload}}
RLEAKTOP top 0 100G
RLEAKBOT bottom 0 100G

.tran 2p 10n
.measure tran acquired_top_v FIND v(top) AT={config.sample_at_ns}n
.measure tran acquired_bottom_v FIND v(bottom) AT={config.sample_at_ns}n
.measure tran held_top_v FIND v(top) AT={config.hold_at_ns}n
.measure tran held_bottom_v FIND v(bottom) AT={config.hold_at_ns}n
.measure tran input_v FIND v(in) AT={config.sample_at_ns}n
.measure tran acquired_stored_v PARAM='acquired_top_v-acquired_bottom_v'
.measure tran held_stored_v PARAM='held_top_v-held_bottom_v'
.measure tran hold_abs_delta_v PARAM='abs(held_stored_v-acquired_stored_v)'
.measure tran total_abs_error_v PARAM='abs(input_v-held_stored_v)'
.control
run
.endc

.end
"""


def timeout_row(config: Config, input_v: float) -> dict[str, Any]:
    half_lsb_12b_v = 1.8 / 4096.0 / 2.0
    return {
        "config": config.name,
        "top_off_ns": config.top_off_ns,
        "bottom_off_ns": config.bottom_off_ns,
        "input_v": input_v,
        "acquired_stored_v": None,
        "held_stored_v": None,
        "hold_abs_delta_v": None,
        "total_abs_error_v": None,
        "half_lsb_12b_v": half_lsb_12b_v,
        "pass_hold_delta_half_lsb_12b": False,
        "pass_total_error_half_lsb_12b": False,
        "ngspice_returncode": None,
        "ngspice_timed_out": True,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }


def run_case(config: Config, input_v: float) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(config, input_v), encoding="utf-8")
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
        return timeout_row(config, input_v)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    acquired_stored_v = read_measure(result.stdout, "acquired_stored_v")
    held_stored_v = read_measure(result.stdout, "held_stored_v")
    measured_input_v = read_measure(result.stdout, "input_v")
    half_lsb_12b_v = 1.8 / 4096.0 / 2.0
    return {
        "config": config.name,
        "top_off_ns": config.top_off_ns,
        "bottom_off_ns": config.bottom_off_ns,
        "input_v": input_v,
        "acquired_stored_v": acquired_stored_v,
        "held_stored_v": held_stored_v,
        "hold_abs_delta_v": abs(held_stored_v - acquired_stored_v),
        "total_abs_error_v": abs(measured_input_v - held_stored_v),
        "half_lsb_12b_v": half_lsb_12b_v,
        "pass_hold_delta_half_lsb_12b": abs(held_stored_v - acquired_stored_v) <= half_lsb_12b_v,
        "pass_total_error_half_lsb_12b": abs(measured_input_v - held_stored_v) <= half_lsb_12b_v,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }


def summarize_config(config: Config, rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if row["config"] == config.name]
    measured = [row for row in selected if row["hold_abs_delta_v"] is not None]
    return {
        "config": config.name,
        "top_off_ns": config.top_off_ns,
        "bottom_off_ns": config.bottom_off_ns,
        "case_count": len(selected),
        "measured_case_count": len(measured),
        "timed_out_count": sum(1 for row in selected if row["ngspice_timed_out"]),
        "worst_hold_abs_delta_v": max((row["hold_abs_delta_v"] for row in measured), default=None),
        "worst_total_abs_error_v": max((row["total_abs_error_v"] for row in measured), default=None),
        "hold_delta_pass_count": sum(1 for row in selected if row["pass_hold_delta_half_lsb_12b"]),
        "total_error_pass_count": sum(1 for row in selected if row["pass_total_error_half_lsb_12b"]),
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    configs = [
        Config("same_edge_top_and_bottom_off", 7.0, 7.0, 6.8, 8.5),
        Config("top_opens_before_bottom_200ps", 6.8, 7.0, 6.6, 8.5),
        Config("bottom_opens_before_top_200ps", 7.0, 6.8, 6.6, 8.5),
    ]
    inputs = [0.3, 0.9, 1.5]
    rows = [run_case(config, input_v) for config in configs for input_v in inputs]
    summaries = [summarize_config(config, rows) for config in configs]
    measurable = [item for item in summaries if item["worst_hold_abs_delta_v"] is not None]
    best = min(measurable, key=lambda item: item["worst_hold_abs_delta_v"])
    baseline = summaries[0]
    baseline_worst = baseline["worst_hold_abs_delta_v"]
    improvement = baseline_worst / best["worst_hold_abs_delta_v"] if baseline_worst and best["worst_hold_abs_delta_v"] else 0.0
    return {
        "result_type": "sky130_bottom_plate_sampling_ngspice",
        "status": "sky130_bottom_plate_sampling_characterized_not_converter_proof",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "device_models": ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"],
        "config_count": len(configs),
        "case_count": len(rows),
        "measured_case_count": sum(1 for row in rows if not row["ngspice_timed_out"]),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "half_lsb_12b_v": rows[0]["half_lsb_12b_v"],
        "rows": rows,
        "summaries": summaries,
        "baseline_config": baseline["config"],
        "baseline_worst_hold_abs_delta_v": baseline_worst,
        "best_config": best["config"],
        "best_worst_hold_abs_delta_v": best["worst_hold_abs_delta_v"],
        "best_hold_improvement_x": improvement,
        "best_total_error_pass_count": best["total_error_pass_count"],
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "compares Sky130 MOS bottom-plate clock-order choices for a simple sample-and-hold fixture",
            "not_allowed": "does not prove comparator behavior, SAR conversion, extracted transistor layout, DRC/LVS signoff, converter energy, or accepted replacement economics",
        },
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt_optional(value: float | None) -> str:
    return "timeout" if value is None else f"{value:.9e}"


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Bottom Plate Sampling Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- PDK model library: `{report['pdk_model_library']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- config count: `{report['config_count']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed out case count: `{report['timed_out_case_count']}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- baseline config: `{report['baseline_config']}`",
        f"- baseline worst hold abs delta V: `{fmt_optional(report['baseline_worst_hold_abs_delta_v'])}`",
        f"- best config: `{report['best_config']}`",
        f"- best worst hold abs delta V: `{fmt_optional(report['best_worst_hold_abs_delta_v'])}`",
        f"- best hold improvement x: `{report['best_hold_improvement_x']:.3f}`",
        f"- best total error pass count: `{report['best_total_error_pass_count']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A normal sample switch stores a voltage on one node. When the switch clock turns off, the clock edge can push charge straight into that same node. The stored number moves.",
        "",
        "Bottom-plate sampling stores the voltage across a capacitor. One side of the capacitor sees the input. The other side is held at a known reference during sampling. The clock order matters because the side that is most sensitive should stop seeing the largest clock disturbance before the final switch edge injects charge.",
        "",
        "This fixture measures the stored capacitor voltage, `v(top)-v(bottom)`, after different turn-off orders. It asks a narrow question: does clock ordering reduce held-value movement enough to justify building a stronger converter sample-and-hold around it?",
        "",
        "## Config Summary",
        "",
        "| config | top off ns | bottom off ns | measured cases | timed out cases | worst hold delta V | total error pass count |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["summaries"]:
        lines.append(
            f"| `{item['config']}` | `{item['top_off_ns']:.3f}` | `{item['bottom_off_ns']:.3f}` | `{item['measured_case_count']}` | `{item['timed_out_count']}` | `{fmt_optional(item['worst_hold_abs_delta_v'])}` | `{item['total_error_pass_count']}` |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            f"The best measured clock order is `{report['best_config']}`. If its worst hold movement is still above the half-LSB line, the circuit still needs a stronger sample-and-hold design before it can feed a 12-bit converter claim.",
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
    print("sky130_bottom_plate_sampling_ngspice")
    print(f"status,{report['status']}")
    print(f"config_count,{report['config_count']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"best_config,{report['best_config']}")
    print(f"best_worst_hold_abs_delta_v,{report['best_worst_hold_abs_delta_v']:.9e}")
    print(f"best_hold_improvement_x,{report['best_hold_improvement_x']:.3f}")
    print(f"candidate_post_layout_written,{report['candidate_post_layout_written']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
