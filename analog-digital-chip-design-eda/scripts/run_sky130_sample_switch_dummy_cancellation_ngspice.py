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
DECK_OUT = SPICE_DIR / "sky130_sample_switch_dummy_cancellation.sp"
CSV_OUT = MEASUREMENTS / "sky130-sample-switch-dummy-cancellation-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-dummy-cancellation-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-dummy-cancellation-ngspice.md"
NGSPICE_TIMEOUT_S = 20


@dataclass(frozen=True)
class Config:
    name: str
    switch_wn: float
    switch_wp: float
    dummy_wn: float
    dummy_wp: float
    csample_p: float
    cload_p: float


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


def dummy_devices(config: Config) -> str:
    if config.dummy_wn == 0 and config.dummy_wp == 0:
        return ""
    lines: list[str] = []
    if config.dummy_wn > 0:
        lines.append("XDUMN sample ctrlb sample vss sky130_fd_pr__nfet_01v8 W={dummy_wn} L={lmin}")
    if config.dummy_wp > 0:
        lines.append("XDUMP sample ctrl sample vdd sky130_fd_pr__pfet_01v8 W={dummy_wp} L={lmin}")
    return "\n".join(lines)


def build_deck(config: Config, input_v: float) -> str:
    dummy_block = dummy_devices(config)
    return f"""* Sky130 sample-switch dummy cancellation fixture.
* Dummy devices are shorted at the sample node and clocked on the opposite edge.

.lib "{PDK_LIB}" tt
.param vin={input_v}
.param vdd=1.8
.param lmin=0.15
.param switch_wn={config.switch_wn}
.param switch_wp={config.switch_wp}
.param dummy_wn={config.dummy_wn}
.param dummy_wp={config.dummy_wp}
.param csample={config.csample_p}p
.param cload={config.cload_p}p

VDD vdd 0 {{vdd}}
VSS vss 0 0
VIN in 0 PULSE(0 {{vin}} 0.1n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.2n 20p 20p 7n 20n)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.2n 20p 20p 7n 20n)

XSWN in ctrl sample vss sky130_fd_pr__nfet_01v8 W={{switch_wn}} L={{lmin}}
XSWP in ctrlb sample vdd sky130_fd_pr__pfet_01v8 W={{switch_wp}} L={{lmin}}
{dummy_block}
CSAMPLE sample 0 {{csample}}
CLOAD sample 0 {{cload}}
RLEAK sample 0 100G

.tran 2p 10n
.measure tran acquired_v FIND v(sample) AT=6.8n
.measure tran held_v FIND v(sample) AT=8.5n
.measure tran input_v FIND v(in) AT=6.8n
.measure tran hold_abs_delta_v PARAM='abs(held_v-acquired_v)'
.measure tran total_abs_error_v PARAM='abs(input_v-held_v)'
.control
run
.endc

.end
"""


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
        half_lsb_12b_v = 1.8 / 4096.0 / 2.0
        return {
            "config": config.name,
            "switch_wn_um": config.switch_wn,
            "switch_wp_um": config.switch_wp,
            "dummy_wn_um": config.dummy_wn,
            "dummy_wp_um": config.dummy_wp,
            "csample_p": config.csample_p,
            "cload_p": config.cload_p,
            "input_v": input_v,
            "acquired_v": None,
            "held_v": None,
            "hold_abs_delta_v": None,
            "total_abs_error_v": None,
            "half_lsb_12b_v": half_lsb_12b_v,
            "pass_hold_delta_half_lsb_12b": False,
            "pass_total_error_half_lsb_12b": False,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
        }
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    acquired_v = read_measure(result.stdout, "acquired_v")
    held_v = read_measure(result.stdout, "held_v")
    measured_input_v = read_measure(result.stdout, "input_v")
    half_lsb_12b_v = 1.8 / 4096.0 / 2.0
    return {
        "config": config.name,
        "switch_wn_um": config.switch_wn,
        "switch_wp_um": config.switch_wp,
        "dummy_wn_um": config.dummy_wn,
        "dummy_wp_um": config.dummy_wp,
        "csample_p": config.csample_p,
        "cload_p": config.cload_p,
        "input_v": input_v,
        "acquired_v": acquired_v,
        "held_v": held_v,
        "hold_abs_delta_v": abs(held_v - acquired_v),
        "total_abs_error_v": abs(measured_input_v - held_v),
        "half_lsb_12b_v": half_lsb_12b_v,
        "pass_hold_delta_half_lsb_12b": abs(held_v - acquired_v) <= half_lsb_12b_v,
        "pass_total_error_half_lsb_12b": abs(measured_input_v - held_v) <= half_lsb_12b_v,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }


def summarize_config(config: Config, rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if row["config"] == config.name]
    measured = [row for row in selected if row["hold_abs_delta_v"] is not None]
    worst_hold = max((row["hold_abs_delta_v"] for row in measured), default=None)
    worst_total = max((row["total_abs_error_v"] for row in measured), default=None)
    return {
        "config": config.name,
        "switch_wn_um": config.switch_wn,
        "switch_wp_um": config.switch_wp,
        "dummy_wn_um": config.dummy_wn,
        "dummy_wp_um": config.dummy_wp,
        "csample_p": config.csample_p,
        "cload_p": config.cload_p,
        "worst_hold_abs_delta_v": worst_hold,
        "worst_total_abs_error_v": worst_total,
        "hold_delta_pass_count": sum(1 for row in selected if row["pass_hold_delta_half_lsb_12b"]),
        "total_error_pass_count": sum(1 for row in selected if row["pass_total_error_half_lsb_12b"]),
        "timed_out_count": sum(1 for row in selected if row["ngspice_timed_out"]),
        "measured_case_count": len(measured),
        "case_count": len(selected),
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    configs = [
        Config("no_dummy_best_prior_1p0p_2x4", 2.0, 4.0, 0.0, 0.0, 1.0, 0.05),
        Config("dummy_0p25x_1p0p_2x4", 2.0, 4.0, 0.5, 1.0, 1.0, 0.05),
        Config("dummy_0p50x_1p0p_2x4", 2.0, 4.0, 1.0, 2.0, 1.0, 0.05),
    ]
    inputs = [0.3, 0.9, 1.5]
    rows = [run_case(config, input_v) for config in configs for input_v in inputs]
    summaries = [summarize_config(config, rows) for config in configs]
    baseline = summaries[0]
    measurable = [item for item in summaries if item["worst_hold_abs_delta_v"] is not None]
    best = min(measurable, key=lambda item: item["worst_hold_abs_delta_v"])
    improvement = baseline["worst_hold_abs_delta_v"] / best["worst_hold_abs_delta_v"] if best["worst_hold_abs_delta_v"] else float("inf")
    return {
        "result_type": "sky130_sample_switch_dummy_cancellation_ngspice",
        "status": "sky130_dummy_cancellation_sweep_complete_not_converter_proof",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "device_models": ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"],
        "config_count": len(configs),
        "case_count": len(rows),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "measured_case_count": sum(1 for row in rows if not row["ngspice_timed_out"]),
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
        "half_lsb_12b_v": rows[0]["half_lsb_12b_v"],
        "rows": rows,
        "summaries": summaries,
        "baseline_config": baseline["config"],
        "baseline_worst_hold_abs_delta_v": baseline["worst_hold_abs_delta_v"],
        "best_config": best["config"],
        "best_worst_hold_abs_delta_v": best["worst_hold_abs_delta_v"],
        "best_hold_improvement_x": improvement,
        "best_total_error_pass_count": best["total_error_pass_count"],
        "any_total_error_pass": any(row["pass_total_error_half_lsb_12b"] for row in rows),
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "compares opposite-clock dummy-device charge cancellation choices for a Sky130 MOS sample switch hold fixture",
            "not_allowed": "does not prove a complete sample-and-hold architecture, comparator behavior, SAR conversion, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics",
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
        "# Sky130 Sample Switch Dummy Cancellation Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- PDK model library: `{report['pdk_model_library']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- config count: `{report['config_count']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed out case count: `{report['timed_out_case_count']}`",
        f"- ngspice timeout s: `{report['ngspice_timeout_s']}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- baseline config: `{report['baseline_config']}`",
        f"- baseline worst hold abs delta V: `{report['baseline_worst_hold_abs_delta_v']:.9e}`",
        f"- best config: `{report['best_config']}`",
        f"- best worst hold abs delta V: `{report['best_worst_hold_abs_delta_v']:.9e}`",
        f"- best hold improvement x: `{report['best_hold_improvement_x']:.3f}`",
        f"- best total error pass count: `{report['best_total_error_pass_count']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "When the switch turns off, the gate voltage moves quickly. Some of that movement couples through the MOS device capacitances into the stored node. The stored node is just charge on a capacitor, so a small injected charge becomes a voltage error.",
        "",
        "A dummy device tries to inject charge with the opposite sign. It is not connected as a real signal switch. Its job is to let the clock edge push back on the stored node. This only works if the sign, size, and timing are close enough. Too little dummy charge does not cancel enough. Too much dummy charge pushes the error the other way.",
        "",
        "This run tests that idea directly with Sky130 MOS models. It uses the best capacitor setting from the previous sweep as the baseline, then adds several dummy-device sizes. The result tells us whether simple cancellation is enough or whether the design must move to a stronger sampling topology.",
        "",
        "## Config Summary",
        "",
        "| config | dummy Wn um | dummy Wp um | Csample pF | measured cases | timed out cases | worst hold delta V | total error pass count |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["summaries"]:
        worst = "timeout" if item["worst_hold_abs_delta_v"] is None else f"{item['worst_hold_abs_delta_v']:.9e}"
        lines.append(
            f"| `{item['config']}` | `{item['dummy_wn_um']:.3f}` | `{item['dummy_wp_um']:.3f}` | `{item['csample_p']:.3f}` | `{item['measured_case_count']}` | `{item['timed_out_count']}` | `{worst}` | `{item['total_error_pass_count']}` |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            f"The best setting in this sweep is `{report['best_config']}`. It changes worst hold movement by `{report['best_hold_improvement_x']:.3f}` times compared with the no-dummy baseline. The important question is not whether the table looks better; it is whether the held value reaches the 12-bit half-LSB line.",
            "",
            "If the best row still misses that line, or if the dummy cases are not numerically well behaved enough to finish, simple dummy cancellation is not enough for this converter target. The next circuit move should be bottom-plate sampling or another timing method that disconnects the sensitive node before the largest clock-edge charge arrives.",
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
    print("sky130_sample_switch_dummy_cancellation_ngspice")
    print(f"status,{report['status']}")
    print(f"config_count,{report['config_count']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"best_config,{report['best_config']}")
    print(f"best_worst_hold_abs_delta_v,{report['best_worst_hold_abs_delta_v']:.9e}")
    print(f"best_hold_improvement_x,{report['best_hold_improvement_x']:.3f}")
    print(f"any_total_error_pass,{report['any_total_error_pass']}")
    print(f"candidate_post_layout_written,{report['candidate_post_layout_written']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
