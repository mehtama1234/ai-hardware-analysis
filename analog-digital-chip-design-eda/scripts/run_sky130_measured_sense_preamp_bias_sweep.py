#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
SPICE_DIR = LAB / "spice"
MEASUREMENTS = LAB / "measurements"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
SOURCE_RAMP = EVIDENCE / "sky130-frontend-sense-to-transistor-ramp-startup.json"
SOURCE_PREAMP = EVIDENCE / "sky130-measured-sense-differential-preamp.json"
DECK_OUT = SPICE_DIR / "sky130_measured_sense_preamp_bias_sweep.sp"
CSV_OUT = MEASUREMENTS / "sky130-measured-sense-preamp-bias-sweep.csv"
OUT_JSON = EVIDENCE / "sky130-measured-sense-preamp-bias-sweep.json"
OUT_MD = EVIDENCE / "sky130-measured-sense-preamp-bias-sweep.md"
NGSPICE_TIMEOUT_S = 120

SETTINGS = [
    {"name": "low_current_wide_load", "rd_ohm": 100_000.0, "itail_a": 5e-6, "win": 2.0},
    {"name": "baseline_softened", "rd_ohm": 100_000.0, "itail_a": 10e-6, "win": 4.0},
    {"name": "known_input_stage_bias", "rd_ohm": 100_000.0, "itail_a": 20e-6, "win": 8.0},
    {"name": "higher_load_low_current", "rd_ohm": 180_000.0, "itail_a": 5e-6, "win": 4.0},
]


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


def build_deck(row: dict[str, Any], setting: dict[str, Any]) -> str:
    sense_diff_v = float(row["sense_diff_v"])
    sense_p = 0.9 + sense_diff_v / 2.0
    sense_n = 0.9 - sense_diff_v / 2.0
    return f"""* Measured-sense preamp bias sweep.
* No extracted frontend. The input is the measured frontend sense voltage.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param rd={setting['rd_ohm']:.12g}
.param itail={setting['itail_a']:.12g}
.param win={setting['win']:.12g}
.param lmin=0.15
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12

VDD vdd 0 {{vdd}}
VINP inp 0 PWL(0 0.9 100p 0.9 700p {sense_p:.12f} 2n {sense_p:.12f})
VINN inn 0 PWL(0 0.9 100p 0.9 700p {sense_n:.12f} 2n {sense_n:.12f})
RDP vdd pre_p {{rd}}
RDN vdd pre_n {{rd}}
XPREP pre_p inp tail 0 sky130_fd_pr__nfet_01v8 W={{win}} L={{lmin}}
XPREN pre_n inn tail 0 sky130_fd_pr__nfet_01v8 W={{win}} L={{lmin}}
ITAIL tail 0 {{itail}}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

.ic v(pre_p)=0.8 v(pre_n)=0.8 v(tail)=0.231
.tran 100p 2n uic
.measure tran pre_p_end_v FIND v(pre_p) AT=2n
.measure tran pre_n_end_v FIND v(pre_n) AT=2n
.measure tran tail_end_v FIND v(tail) AT=2n
.control
set noaskquit
run
.endc
.end
"""


def run_case(row: dict[str, Any], setting: dict[str, Any]) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(row, setting), encoding="utf-8")
    expected_sign = 1 if float(row["input_diff_mv"]) > 0 else -1
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
        return {**setting, "reset_mode": row["reset_mode"], "input_diff_mv": row["input_diff_mv"], "sense_diff_v": row["sense_diff_v"], "ngspice_returncode": None, "ngspice_timed_out": True, "measured": False, "sign_preserved": False, "output_margin_pass": False}
    out: dict[str, Any] = {**setting, "reset_mode": row["reset_mode"], "input_diff_mv": row["input_diff_mv"], "sense_diff_v": row["sense_diff_v"], "ngspice_returncode": result.returncode, "ngspice_timed_out": False, "measured": result.returncode == 0}
    if result.returncode != 0:
        out["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        out["sign_preserved"] = False
        out["output_margin_pass"] = False
        return out
    pre_p = read_measure(result.stdout, "pre_p_end_v")
    pre_n = read_measure(result.stdout, "pre_n_end_v")
    preamp_diff_v = pre_n - pre_p
    measured_sign = 1 if preamp_diff_v > 0 else -1 if preamp_diff_v < 0 else 0
    out.update(
        {
            "pre_p_end_v": pre_p,
            "pre_n_end_v": pre_n,
            "tail_end_v": read_measure(result.stdout, "tail_end_v"),
            "preamp_output_diff_v": preamp_diff_v,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "sign_preserved": measured_sign == expected_sign,
            "output_margin_pass": abs(preamp_diff_v) >= 0.0005,
            "sense_to_preamp_gain_v_per_v": preamp_diff_v / float(row["sense_diff_v"]),
        }
    )
    return out


def summarize_setting(rows: list[dict[str, Any]]) -> dict[str, Any]:
    measured = [row for row in rows if row["measured"]]
    return {
        "name": rows[0]["name"],
        "rd_ohm": rows[0]["rd_ohm"],
        "itail_a": rows[0]["itail_a"],
        "win": rows[0]["win"],
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "sign_pass_count": sum(1 for row in rows if row["sign_preserved"]),
        "output_margin_pass_count": sum(1 for row in rows if row["output_margin_pass"]),
        "minimum_abs_preamp_output_diff_v": min((abs(row["preamp_output_diff_v"]) for row in measured), default=0.0),
        "minimum_sense_to_preamp_gain_v_per_v": min((abs(row["sense_to_preamp_gain_v_per_v"]) for row in measured), default=0.0),
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    ramp = json.loads(SOURCE_RAMP.read_text(encoding="utf-8"))
    prior = json.loads(SOURCE_PREAMP.read_text(encoding="utf-8"))
    source_rows = [row for row in ramp["rows"] if row.get("ramp_startup_measured")]
    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    DECK_OUT.parent.mkdir(parents=True, exist_ok=True)
    for setting in SETTINGS:
        setting_rows = [run_case(row, setting) for row in source_rows]
        rows.extend(setting_rows)
        summaries.append(summarize_setting(setting_rows))
    passing = [
        item for item in summaries
        if item["measured_case_count"] == item["case_count"]
        and item["sign_pass_count"] == item["case_count"]
        and item["output_margin_pass_count"] == item["case_count"]
    ]
    return {
        "result_type": "sky130_measured_sense_preamp_bias_sweep",
        "status": "measured_sense_preamp_bias_sweep_found_passing_setting_not_extracted_frontend" if passing else "measured_sense_preamp_bias_sweep_found_no_passing_setting",
        "source_ramp_startup": rel(SOURCE_RAMP),
        "source_measured_sense_preamp": rel(SOURCE_PREAMP),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "pdk_model_library": str(PDK_LIB),
        "uses_measured_frontend_sense_voltage": True,
        "uses_extracted_frontend_transient": False,
        "uses_sky130_differential_preamp": True,
        "setting_count": len(summaries),
        "case_count": len(rows),
        "measured_case_count": sum(1 for row in rows if row["measured"]),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "passing_setting_count": len(passing),
        "setting_summaries": summaries,
        "rows": rows,
        "prior_preamp_timed_out_case_count": prior["timed_out_case_count"],
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "sweeps standalone Sky130 differential-preamp bias using measured frontend sense voltages",
            "not_allowed": "does not prove extracted frontend loading, latch behavior, SAR conversion, DRC/LVS, post-layout energy, or accepted converter evidence",
        },
    }


def write_csv(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in report["rows"] for key in row})
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Measured Sense Preamp Bias Sweep",
        "",
        f"- status: `{report['status']}`",
        f"- setting count: `{report['setting_count']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- passing setting count: `{report['passing_setting_count']}`",
        f"- uses measured frontend sense voltage: `{report['uses_measured_frontend_sense_voltage']}`",
        f"- uses extracted frontend transient: `{report['uses_extracted_frontend_transient']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "Before a preamp can be blamed for loading the extracted frontend, it must first work when the tiny input voltage is supplied directly. This sweep changes current, load resistance, and transistor width while keeping the input voltage equal to the measured frontend sense voltage.",
        "",
        "A useful setting must do three things at once: run to completion, preserve the sign for both input directions, and create enough output difference for the next decision stage.",
        "",
        "## Setting Summary",
        "",
        "| setting | rd ohm | itail uA | width | measured | sign pass | margin pass | min output mV | min gain V/V |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["setting_summaries"]:
        lines.append(
            f"| `{item['name']}` | `{item['rd_ohm']:.0f}` | `{item['itail_a'] * 1e6:.3f}` | `{item['win']:.3f}` | `{item['measured_case_count']}` | `{item['sign_pass_count']}` | `{item['output_margin_pass_count']}` | `{item['minimum_abs_preamp_output_diff_v'] * 1000.0:.6f}` | `{item['minimum_sense_to_preamp_gain_v_per_v']:.6f}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_measured_sense_preamp_bias_sweep")
    print(f"status,{report['status']}")
    print(f"setting_count,{report['setting_count']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"passing_setting_count,{report['passing_setting_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
