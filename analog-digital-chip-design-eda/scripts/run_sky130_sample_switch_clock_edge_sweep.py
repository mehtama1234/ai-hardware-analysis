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
DECK_OUT = SPICE_DIR / "sky130_sample_switch_clock_edge_sweep.sp"
CSV_OUT = MEASUREMENTS / "sky130-sample-switch-clock-edge-sweep.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-clock-edge-sweep.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-clock-edge-sweep.md"
NGSPICE_TIMEOUT_S = 180


@dataclass(frozen=True)
class Config:
    name: str
    edge_ps: float


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


def build_deck(config: Config, input_v: float) -> str:
    edge = f"{config.edge_ps}p"
    return f"""* Sky130 transmission-gate clock-edge sweep.
* This keeps the known-running sample switch and changes only control edge time.

.lib "{PDK_LIB}" tt
.param vin={input_v}
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param csample=0.2p
.param cload=0.05p

VDD vdd 0 {{vdd}}
VSS vss 0 0
VIN in 0 PULSE(0 {{vin}} 0.1n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.2n {edge} {edge} 7n 20n)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.2n {edge} {edge} 7n 20n)

XSWN in ctrl sample vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XSWP in ctrlb sample vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}
CSAMPLE sample 0 {{csample}}
CLOAD sample 0 {{cload}}
RLEAK sample 0 100G

.tran 2p 10n
.measure tran acquired_v FIND v(sample) AT=6.8n
.measure tran held_v FIND v(sample) AT=8.5n
.measure tran input_v FIND v(in) AT=6.8n
.control
run
.endc

.end
"""


def run_case(config: Config, input_v: float) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(config, input_v), encoding="utf-8")
    half_lsb = 1.8 / 4096.0 / 2.0
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {
            "config": config.name,
            "edge_ps": config.edge_ps,
            "input_v": input_v,
            "hold_abs_delta_v": None,
            "total_abs_error_v": None,
            "half_lsb_12b_v": half_lsb,
            "pass_hold_delta_half_lsb_12b": False,
            "pass_total_error_half_lsb_12b": False,
            "ngspice_timed_out": True,
            "ngspice_returncode": None,
        }
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    acquired = read_measure(result.stdout, "acquired_v")
    held = read_measure(result.stdout, "held_v")
    measured_input = read_measure(result.stdout, "input_v")
    hold_delta = abs(held - acquired)
    total_error = abs(measured_input - held)
    return {
        "config": config.name,
        "edge_ps": config.edge_ps,
        "input_v": input_v,
        "measured_input_v": measured_input,
        "acquired_v": acquired,
        "held_v": held,
        "hold_abs_delta_v": hold_delta,
        "total_abs_error_v": total_error,
        "half_lsb_12b_v": half_lsb,
        "pass_hold_delta_half_lsb_12b": hold_delta <= half_lsb,
        "pass_total_error_half_lsb_12b": total_error <= half_lsb,
        "ngspice_timed_out": False,
        "ngspice_returncode": result.returncode,
    }


def summarize(config: Config, rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if row["config"] == config.name]
    measured = [row for row in selected if row["hold_abs_delta_v"] is not None]
    return {
        "config": config.name,
        "edge_ps": config.edge_ps,
        "case_count": len(selected),
        "measured_case_count": len(measured),
        "timed_out_count": sum(1 for row in selected if row["ngspice_timed_out"]),
        "worst_hold_abs_delta_v": max((row["hold_abs_delta_v"] for row in measured), default=None),
        "worst_total_abs_error_v": max((row["total_abs_error_v"] for row in measured), default=None),
        "hold_delta_pass_count": sum(1 for row in selected if row["pass_hold_delta_half_lsb_12b"]),
    }


def fmt(value: float | None) -> str:
    return "timeout" if value is None else f"{value:.9e}"


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    configs = [Config("baseline_20ps_mid_input", 20.0), Config("slower_100ps_mid_input", 100.0)]
    inputs = [0.9]
    rows = [run_case(config, input_v) for config in configs for input_v in inputs]
    summaries = [summarize(config, rows) for config in configs]
    measured_summaries = [item for item in summaries if item["worst_hold_abs_delta_v"] is not None]
    best = min(measured_summaries, key=lambda item: item["worst_hold_abs_delta_v"]) if measured_summaries else None
    return {
        "result_type": "sky130_sample_switch_clock_edge_sweep",
        "status": "sky130_sample_switch_clock_edge_pair_characterized_not_converter_proof",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "device_models": ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"],
        "config_count": len(configs),
        "case_count": len(rows),
        "measured_case_count": sum(1 for row in rows if not row["ngspice_timed_out"]),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
        "rows": rows,
        "summaries": summaries,
        "half_lsb_12b_v": 1.8 / 4096.0 / 2.0,
        "best_config": best["config"] if best else None,
        "best_worst_hold_abs_delta_v": best["worst_hold_abs_delta_v"] if best else None,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "compares 20 ps and 100 ps clock edges on the known-running Sky130 transmission-gate sample-hold fixture at mid input",
            "not_allowed": "does not prove a complete sample-and-hold architecture, comparator behavior, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted({key for row in rows for key in row}))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Sample Switch Clock Edge Sweep",
        "",
        f"- status: `{report['status']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- config count: `{report['config_count']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed out case count: `{report['timed_out_case_count']}`",
        f"- ngspice timeout s: `{report['ngspice_timeout_s']}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- best config: `{report['best_config']}`",
        f"- best worst hold abs delta V: `{fmt(report['best_worst_hold_abs_delta_v'])}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "Clock feedthrough starts when the control voltage moves. A sharper edge moves charge quickly. A slower edge can spread that movement over time, but it also leaves the switch partly on for longer.",
        "",
        "This page records two mid-input edge cases: the original 20 ps edge and a slower 100 ps edge. The earlier nine-case edge sweep was too slow to be a useful bridge step. Keeping a small measured pair is better than keeping a broad sweep that mostly proves timeout behavior.",
        "",
        "## Config Summary",
        "",
        "| config | edge ps | measured cases | timed out cases | worst hold delta V | hold pass count |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in report["summaries"]:
        lines.append(f"| `{item['config']}` | `{item['edge_ps']:.1f}` | `{item['measured_case_count']}` | `{item['timed_out_count']}` | `{fmt(item['worst_hold_abs_delta_v'])}` | `{item['hold_delta_pass_count']}` |")
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_sample_switch_clock_edge_sweep")
    print(f"status,{report['status']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"best_config,{report['best_config']}")
    print(f"best_worst_hold_abs_delta_v,{fmt(report['best_worst_hold_abs_delta_v'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
