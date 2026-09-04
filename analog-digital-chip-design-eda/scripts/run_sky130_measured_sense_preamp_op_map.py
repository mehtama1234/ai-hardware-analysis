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
SOURCE_SWEEP = EVIDENCE / "sky130-measured-sense-preamp-bias-sweep.json"
DECK_OUT = SPICE_DIR / "sky130_measured_sense_preamp_op_map.sp"
CSV_OUT = MEASUREMENTS / "sky130-measured-sense-preamp-op-map.csv"
OUT_JSON = EVIDENCE / "sky130-measured-sense-preamp-op-map.json"
OUT_MD = EVIDENCE / "sky130-measured-sense-preamp-op-map.md"
NGSPICE_TIMEOUT_S = 120

SETTINGS = [
    {"name": "known_input_stage_bias", "rd_ohm": 100_000.0, "itail_a": 20e-6, "win": 8.0},
]


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_node(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.match(rf"\s*{re.escape(name)}\s+([-+0-9.eE]+)\s*$", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice OP node {name!r}, found none")
    return values[-1]


def build_deck(row: dict[str, Any], setting: dict[str, Any]) -> str:
    sense_diff_v = float(row["sense_diff_v"])
    sense_p = 0.9 + sense_diff_v / 2.0
    sense_n = 0.9 - sense_diff_v / 2.0
    return f"""* Measured-sense preamp DC operating-point map.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param rd={setting['rd_ohm']:.12g}
.param itail={setting['itail_a']:.12g}
.param win={setting['win']:.12g}
.param lmin=0.15

VDD vdd 0 {{vdd}}
VINP inp 0 {sense_p:.12f}
VINN inn 0 {sense_n:.12f}
RDP vdd pre_p {{rd}}
RDN vdd pre_n {{rd}}
XPREP pre_p inp tail 0 sky130_fd_pr__nfet_01v8 W={{win}} L={{lmin}}
XPREN pre_n inn tail 0 sky130_fd_pr__nfet_01v8 W={{win}} L={{lmin}}
ITAIL tail 0 {{itail}}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

.op
.control
set noaskquit
op
.endc

.end
"""


def run_case(row: dict[str, Any], setting: dict[str, Any]) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(row, setting), encoding="utf-8")
    expected_sign = 1 if float(row["input_diff_mv"]) > 0 else -1
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {**setting, "reset_mode": row["reset_mode"], "input_diff_mv": row["input_diff_mv"], "sense_diff_v": row["sense_diff_v"], "ngspice_returncode": None, "ngspice_timed_out": True, "op_measured": False, "sign_preserved": False, "output_margin_pass": False, "bias_window_pass": False}
    out: dict[str, Any] = {**setting, "reset_mode": row["reset_mode"], "input_diff_mv": row["input_diff_mv"], "sense_diff_v": row["sense_diff_v"], "ngspice_returncode": result.returncode, "ngspice_timed_out": result.returncode == 124, "op_measured": result.returncode == 0}
    if result.returncode != 0:
        out["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        out.update({"sign_preserved": False, "output_margin_pass": False, "bias_window_pass": False})
        return out
    pre_p = read_node(result.stdout, "pre_p")
    pre_n = read_node(result.stdout, "pre_n")
    tail = read_node(result.stdout, "tail")
    preamp_diff_v = pre_n - pre_p
    measured_sign = 1 if preamp_diff_v > 0 else -1 if preamp_diff_v < 0 else 0
    bias_window_pass = 0.2 <= tail <= 0.8 and 0.2 <= pre_p <= 1.7 and 0.2 <= pre_n <= 1.7
    out.update(
        {
            "pre_p_v": pre_p,
            "pre_n_v": pre_n,
            "tail_v": tail,
            "preamp_output_diff_v": preamp_diff_v,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "sign_preserved": measured_sign == expected_sign,
            "output_margin_pass": abs(preamp_diff_v) >= 0.0005,
            "bias_window_pass": bias_window_pass,
            "sense_to_preamp_gain_v_per_v": preamp_diff_v / float(row["sense_diff_v"]),
        }
    )
    return out


def summarize_setting(rows: list[dict[str, Any]]) -> dict[str, Any]:
    measured = [row for row in rows if row["op_measured"]]
    return {
        "name": rows[0]["name"],
        "rd_ohm": rows[0]["rd_ohm"],
        "itail_a": rows[0]["itail_a"],
        "win": rows[0]["win"],
        "case_count": len(rows),
        "op_measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "sign_pass_count": sum(1 for row in rows if row["sign_preserved"]),
        "output_margin_pass_count": sum(1 for row in rows if row["output_margin_pass"]),
        "bias_window_pass_count": sum(1 for row in rows if row["bias_window_pass"]),
        "minimum_abs_preamp_output_diff_v": min((abs(row["preamp_output_diff_v"]) for row in measured), default=0.0),
        "minimum_gain_v_per_v": min((abs(row["sense_to_preamp_gain_v_per_v"]) for row in measured), default=0.0),
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    ramp = json.loads(SOURCE_RAMP.read_text(encoding="utf-8"))
    sweep = json.loads(SOURCE_SWEEP.read_text(encoding="utf-8"))
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
        if item["op_measured_case_count"] == item["case_count"]
        and item["sign_pass_count"] == item["case_count"]
        and item["output_margin_pass_count"] == item["case_count"]
        and item["bias_window_pass_count"] == item["case_count"]
    ]
    best = max(summaries, key=lambda item: (item["bias_window_pass_count"], item["sign_pass_count"], item["output_margin_pass_count"], item["minimum_abs_preamp_output_diff_v"]))
    return {
        "result_type": "sky130_measured_sense_preamp_op_map",
        "status": "measured_sense_preamp_op_map_found_valid_bias_point_not_transient_or_extracted_frontend" if passing else "measured_sense_preamp_op_map_found_no_valid_bias_point",
        "source_ramp_startup": rel(SOURCE_RAMP),
        "source_transient_bias_sweep": rel(SOURCE_SWEEP),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "pdk_model_library": str(PDK_LIB),
        "uses_measured_frontend_sense_voltage": True,
        "uses_extracted_frontend_transient": False,
        "uses_sky130_differential_preamp": True,
        "uses_dc_operating_point": True,
        "setting_count": len(summaries),
        "case_count": len(rows),
        "op_measured_case_count": sum(1 for row in rows if row["op_measured"]),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "passing_setting_count": len(passing),
        "best_setting": best,
        "setting_summaries": summaries,
        "rows": rows,
        "prior_transient_passing_setting_count": sweep["passing_setting_count"],
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "maps standalone Sky130 differential-preamp DC bias points using measured frontend sense voltages",
            "not_allowed": "does not prove transient startup, extracted frontend loading, latch behavior, SAR conversion, DRC/LVS, post-layout energy, or accepted converter evidence",
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
        "# Sky130 Measured Sense Preamp OP Map",
        "",
        f"- status: `{report['status']}`",
        f"- setting count: `{report['setting_count']}`",
        f"- case count: `{report['case_count']}`",
        f"- OP measured case count: `{report['op_measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- passing setting count: `{report['passing_setting_count']}`",
        f"- uses DC operating point: `{report['uses_dc_operating_point']}`",
        f"- uses measured frontend sense voltage: `{report['uses_measured_frontend_sense_voltage']}`",
        f"- uses extracted frontend transient: `{report['uses_extracted_frontend_transient']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A transient run asks two questions at once: where should the circuit settle, and how does it get there over time? A DC operating-point run asks only the first question. That is the right next test when transient preamp runs time out.",
        "",
        "A useful preamp bias point must leave the tail node and both output nodes away from the rails. It must also give the right output sign for both tiny input directions. Only then is it worth spending time on transient startup.",
        "",
        "## Setting Summary",
        "",
        "| setting | rd ohm | itail uA | width | OP measured | bias pass | sign pass | margin pass | min output mV | min gain V/V |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["setting_summaries"]:
        lines.append(
            f"| `{item['name']}` | `{item['rd_ohm']:.0f}` | `{item['itail_a'] * 1e6:.3f}` | `{item['win']:.3f}` | `{item['op_measured_case_count']}` | `{item['bias_window_pass_count']}` | `{item['sign_pass_count']}` | `{item['output_margin_pass_count']}` | `{item['minimum_abs_preamp_output_diff_v'] * 1000.0:.6f}` | `{item['minimum_gain_v_per_v']:.6f}` |"
        )
    lines.extend(
        [
            "",
            "## Best Observed Bias",
            "",
            f"- setting: `{report['best_setting']['name']}`",
            f"- OP measured cases: `{report['best_setting']['op_measured_case_count']}`",
            f"- bias-window passes: `{report['best_setting']['bias_window_pass_count']}`",
            f"- sign passes: `{report['best_setting']['sign_pass_count']}`",
            f"- margin passes: `{report['best_setting']['output_margin_pass_count']}`",
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
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_measured_sense_preamp_op_map")
    print(f"status,{report['status']}")
    print(f"setting_count,{report['setting_count']}")
    print(f"case_count,{report['case_count']}")
    print(f"op_measured_case_count,{report['op_measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"passing_setting_count,{report['passing_setting_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
