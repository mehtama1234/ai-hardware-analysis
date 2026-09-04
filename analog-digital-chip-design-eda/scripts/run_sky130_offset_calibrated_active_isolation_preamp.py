#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import run_sky130_active_isolation_preamp_candidate as active


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
SOURCE_ACTIVE = EVIDENCE / "sky130-active-isolation-preamp-candidate.json"
DECK_OUT = LAB / "spice" / "sky130_offset_calibrated_active_isolation_preamp.sp"
CSV_OUT = LAB / "measurements" / "sky130-offset-calibrated-active-isolation-preamp.csv"
OUT_JSON = EVIDENCE / "sky130-offset-calibrated-active-isolation-preamp.json"
OUT_MD = EVIDENCE / "sky130-offset-calibrated-active-isolation-preamp.md"

active.DECK_OUT = DECK_OUT


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def source_rows() -> list[dict[str, Any]]:
    frontend = json.loads(active.SOURCE_FRONTEND.read_text(encoding="utf-8"))
    rows = [row for row in frontend["rows"] if row["reset_mode"] == "reset_pulse"]
    if not rows:
        raise SystemExit("missing reset-pulse source rows")
    zero = dict(rows[0])
    zero["input_diff_mv"] = 0.0
    return [zero] + rows


def summarize_setting(rows: list[dict[str, Any]], zero_output: float, output_target: float) -> dict[str, Any]:
    measured_signal = [row for row in rows if row["measured"] and float(row["input_diff_mv"]) != 0.0]
    for row in measured_signal:
        corrected = float(row["preamp_output_diff_v"]) - zero_output
        expected_sign = 1 if float(row["input_diff_mv"]) > 0 else -1
        measured_sign = 1 if corrected > 0 else -1 if corrected < 0 else 0
        row["zero_input_preamp_output_diff_v"] = zero_output
        row["corrected_preamp_output_diff_v"] = corrected
        row["corrected_measured_sign"] = measured_sign
        row["corrected_sign_preserved"] = measured_sign == expected_sign
        row["corrected_output_margin_pass"] = abs(corrected) >= output_target
    return {
        "name": rows[0]["name"],
        "iso_gain": rows[0]["iso_gain"],
        "polarity": rows[0]["polarity"],
        "input_cap_f": rows[0]["input_cap_f"],
        "bias_current_a": rows[0]["bias_current_a"],
        "zero_input_preamp_output_diff_v": zero_output,
        "case_count": len(measured_signal),
        "measured_case_count": len(measured_signal),
        "corrected_sign_pass_count": sum(1 for row in measured_signal if row.get("corrected_sign_preserved")),
        "corrected_margin_pass_count": sum(1 for row in measured_signal if row.get("corrected_output_margin_pass")),
        "minimum_abs_corrected_preamp_output_diff_v": min((abs(row["corrected_preamp_output_diff_v"]) for row in measured_signal), default=0.0),
        "minimum_sample_to_sense_transfer_ratio": min((row["sample_to_sense_transfer_ratio"] for row in measured_signal), default=0.0),
    }


def build_report() -> dict[str, Any]:
    source = json.loads(SOURCE_ACTIVE.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    output_target = float(source["output_margin_target_v"])
    for setting in active.SETTINGS:
        setting_rows = [active.run_case(row, setting, output_target) for row in source_rows()]
        zero_rows = [row for row in setting_rows if row["measured"] and float(row["input_diff_mv"]) == 0.0]
        zero_output = float(zero_rows[0]["preamp_output_diff_v"]) if zero_rows else 0.0
        signal_rows = [row for row in setting_rows if float(row["input_diff_mv"]) != 0.0]
        summaries.append(summarize_setting(signal_rows, zero_output, output_target))
        rows.extend(signal_rows)
    passing = [item for item in summaries if item["corrected_sign_pass_count"] == item["case_count"] and item["corrected_margin_pass_count"] == item["case_count"]]
    best = max(summaries, key=lambda item: (item["corrected_margin_pass_count"], item["corrected_sign_pass_count"], item["minimum_abs_corrected_preamp_output_diff_v"]))
    return {
        "result_type": "sky130_offset_calibrated_active_isolation_preamp",
        "status": "offset_calibrated_active_isolation_macro_passed_not_transistor_layout_or_strict" if passing else "offset_calibrated_active_isolation_macro_failed",
        "source_active_isolation_candidate": rel(SOURCE_ACTIVE),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "output_margin_target_v": output_target,
        "setting_count": len(summaries),
        "case_count": len(rows),
        "measured_case_count": sum(1 for row in rows if row["measured"]),
        "passing_setting_count": len(passing),
        "first_passing_setting": passing[0]["name"] if passing else None,
        "best_setting": best,
        "setting_summaries": summaries,
        "rows": rows,
        "uses_extracted_frontend_netlist": True,
        "uses_ideal_active_isolation_macro": True,
        "uses_offset_calibration": True,
        "uses_sky130_preamp": True,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "tests whether zero-input offset subtraction makes the active-isolation macro handoff preserve both signs with output margin",
            "not_allowed": "does not prove a transistor isolation circuit, drawn layout, offset stability, noise, DRC/LVS, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence",
        },
    }


def write_csv(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in report["rows"] for key in row})
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Offset-Calibrated Active Isolation Preamp",
        "",
        f"- status: `{report['status']}`",
        f"- setting count: `{report['setting_count']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- passing setting count: `{report['passing_setting_count']}`",
        f"- first passing setting: `{report['first_passing_setting']}`",
        f"- best setting: `{report['best_setting']['name']}`",
        f"- best minimum abs corrected preamp output diff V: `{report['best_setting']['minimum_abs_corrected_preamp_output_diff_v']:.9e}`",
        f"- output margin target V: `{report['output_margin_target_v']:.9e}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A differential readout can be wrong even when it has large voltage swing, because a stable offset can move the zero point. The previous active-isolation macro made large outputs, but the raw zero point was shifted enough that one input sign looked like the other.",
        "",
        "This run measures the zero-input output for each setting and subtracts it before judging sign and margin. That does not prove a real calibrated circuit. It tests whether the remaining problem is stable offset rather than missing signal.",
        "",
        "## Setting Summary",
        "",
        "| setting | gain | polarity | zero output mV | measured | corrected sign pass | corrected margin pass | min corrected output mV |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["setting_summaries"]:
        lines.append(
            f"| `{item['name']}` | `{item['iso_gain']:.3f}` | `{item['polarity']:.0f}` | `{item['zero_input_preamp_output_diff_v'] * 1000.0:.6f}` | `{item['measured_case_count']}` | `{item['corrected_sign_pass_count']}` | `{item['corrected_margin_pass_count']}` | `{item['minimum_abs_corrected_preamp_output_diff_v'] * 1000.0:.6f}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_offset_calibrated_active_isolation_preamp")
    print(f"status,{report['status']}")
    print(f"setting_count,{report['setting_count']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"passing_setting_count,{report['passing_setting_count']}")
    print(f"first_passing_setting,{report['first_passing_setting']}")
    print(f"best_setting,{report['best_setting']['name']}")
    print(f"best_minimum_abs_corrected_preamp_output_diff_v,{report['best_setting']['minimum_abs_corrected_preamp_output_diff_v']:.9e}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
