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
DECK_OUT = SPICE_DIR / "sky130_differential_dummy_cancellation.sp"
CSV_OUT = MEASUREMENTS / "sky130-differential-dummy-cancellation-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-cancellation-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-cancellation-ngspice.md"
BASELINE_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-fully-differential-sampling-ngspice.json"
NGSPICE_TIMEOUT_S = 180


@dataclass(frozen=True)
class Config:
    name: str
    dummy_scale: float


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


def dummy_block(config: Config) -> str:
    if config.dummy_scale <= 0:
        return ""
    return """
XDUMNP sp ctrlb sp vss sky130_fd_pr__nfet_01v8 W={dummy_wn} L={lmin}
XDUMPP sp ctrl sp vdd sky130_fd_pr__pfet_01v8 W={dummy_wp} L={lmin}
XDUMNN sn ctrlb sn vss sky130_fd_pr__nfet_01v8 W={dummy_wn} L={lmin}
XDUMPN sn ctrl sn vdd sky130_fd_pr__pfet_01v8 W={dummy_wp} L={lmin}
"""


def build_deck(config: Config) -> str:
    dummy_wn = 2.0 * config.dummy_scale
    dummy_wp = 4.0 * config.dummy_scale
    return f"""* Sky130 fully differential dummy-cancellation sampling fixture.
* Matched dummy devices add opposite-edge charge on both differential hold nodes.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param dummy_wn={dummy_wn}
.param dummy_wp={dummy_wp}
.param csample=0.2p
.param cload=0.05p
.param vinp=1.0
.param vinn=0.8

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
{dummy_block(config)}
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


def run_case(config: Config) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(config), encoding="utf-8")
    half_lsb_12b_v = 1.8 / 4096.0 / 2.0
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {
            "config": config.name,
            "dummy_scale": config.dummy_scale,
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
    diff_hold_abs_delta_v = abs(held_diff_v - acquired_diff_v)
    diff_total_abs_error_v = abs(input_diff_v - held_diff_v)
    row = {
        "config": config.name,
        "dummy_scale": config.dummy_scale,
        "input_p_v": input_p_v,
        "input_n_v": input_n_v,
        "acquired_p_v": acquired_p_v,
        "acquired_n_v": acquired_n_v,
        "held_p_v": held_p_v,
        "held_n_v": held_n_v,
        "input_diff_v": input_diff_v,
        "acquired_diff_v": acquired_diff_v,
        "held_diff_v": held_diff_v,
        "p_hold_abs_delta_v": abs(held_p_v - acquired_p_v),
        "n_hold_abs_delta_v": abs(held_n_v - acquired_n_v),
        "diff_hold_abs_delta_v": diff_hold_abs_delta_v,
        "diff_total_abs_error_v": diff_total_abs_error_v,
        "half_lsb_12b_v": half_lsb_12b_v,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }
    row["pass_diff_hold_delta_half_lsb_12b"] = diff_hold_abs_delta_v <= half_lsb_12b_v
    row["pass_diff_total_error_half_lsb_12b"] = diff_total_abs_error_v <= half_lsb_12b_v
    return row


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    baseline = json.loads(BASELINE_JSON.read_text(encoding="utf-8")) if BASELINE_JSON.exists() else {}
    configs = [Config("no_dummy", 0.0), Config("dummy_0p25x", 0.25), Config("dummy_0p50x", 0.50)]
    rows = [run_case(config) for config in configs]
    measured = [row for row in rows if not row["ngspice_timed_out"]]
    best = min(measured, key=lambda row: row["diff_hold_abs_delta_v"]) if measured else None
    baseline_error = baseline.get("worst_diff_hold_abs_delta_v")
    best_error = best["diff_hold_abs_delta_v"] if best else None
    return {
        "result_type": "sky130_differential_dummy_cancellation_ngspice",
        "status": "sky130_differential_dummy_cancellation_characterized_not_converter_proof",
        "topology": "matched_transmission_gate_differential_sample_hold_with_opposite_clock_dummy_devices",
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
        "baseline_differential_error_v": baseline_error,
        "best_config": best["config"] if best else None,
        "best_diff_hold_abs_delta_v": best_error,
        "best_diff_total_abs_error_v": best["diff_total_abs_error_v"] if best else None,
        "best_improvement_vs_baseline_x": baseline_error / best_error if baseline_error and best_error else 0.0,
        "diff_hold_pass_count": sum(1 for row in rows if row["pass_diff_hold_delta_half_lsb_12b"]),
        "diff_total_error_pass_count": sum(1 for row in rows if row["pass_diff_total_error_half_lsb_12b"]),
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "compares a few matched dummy-device sizes on the measured Sky130 differential sample-hold fixture",
            "not_allowed": "does not prove comparator offset, noise, SAR conversion, mismatch, extracted layout, DRC/LVS signoff, or accepted replacement economics",
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
        "# Sky130 Differential Dummy Cancellation Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- PDK model library: `{report['pdk_model_library']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed out case count: `{report['timed_out_case_count']}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- baseline differential error V: `{fmt(report['baseline_differential_error_v'])}`",
        f"- best config: `{report['best_config']}`",
        f"- best differential hold abs delta V: `{fmt(report['best_diff_hold_abs_delta_v'])}`",
        f"- best differential total abs error V: `{fmt(report['best_diff_total_abs_error_v'])}`",
        f"- best improvement vs baseline x: `{report['best_improvement_vs_baseline_x']:.3f}`",
        f"- differential hold pass count: `{report['diff_hold_pass_count']}` of `{report['case_count']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A differential comparator sees the distance between two stored voltages. Dummy devices can only help if they make the unwanted clock charge more equal on the two sides or reduce the difference created by switch turn-off.",
        "",
        "The dummy device is not a second signal path. It is a controlled error source. It deliberately injects charge on the opposite clock edge so part of the real switch error is cancelled. If the dummy is too small, it does little. If it is too large, it creates a new error.",
        "",
        "This run keeps the measured Sky130 differential transmission-gate fixture fixed and changes only the dummy-device scale. That makes the result a direct circuit question: does simple matched dummy cancellation reduce the decision-voltage movement enough to matter?",
        "",
        "## Results",
        "",
        "| config | dummy scale | acquired diff V | held diff V | differential hold delta V | differential total error V | passes half LSB |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        if row["ngspice_timed_out"]:
            lines.append(f"| `{row['config']}` | `{row['dummy_scale']:.2f}` | timeout | timeout | timeout | timeout | `False` |")
            continue
        lines.append(
            f"| `{row['config']}` | `{row['dummy_scale']:.2f}` | `{row['acquired_diff_v']:.9f}` | `{row['held_diff_v']:.9f}` | `{row['diff_hold_abs_delta_v']:.9e}` | `{row['diff_total_abs_error_v']:.9e}` | `{row['pass_diff_hold_delta_half_lsb_12b']}` |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "If the best dummy row is still above the half-LSB line, then simple dummy sizing is not the converter answer. The next step must change the sampling event itself: timing, bottom-plate order, capacitance, switch topology, or comparator tolerance.",
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
    print("sky130_differential_dummy_cancellation_ngspice")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"best_config,{report['best_config']}")
    print(f"best_diff_hold_abs_delta_v,{fmt(report['best_diff_hold_abs_delta_v'])}")
    print(f"best_improvement_vs_baseline_x,{report['best_improvement_vs_baseline_x']:.3f}")
    print(f"diff_hold_pass_count,{report['diff_hold_pass_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
