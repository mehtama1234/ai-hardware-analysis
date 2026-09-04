#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
SOURCE = EVIDENCE / "sky130-transistor-active-isolation-preamp.json"
OUT_JSON = EVIDENCE / "sky130-polarity-corrected-transistor-handoff.json"
OUT_MD = EVIDENCE / "sky130-polarity-corrected-transistor-handoff.md"
OUTPUT_TARGET_V = 0.0005


def corrected_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if not row.get("measured") or float(row.get("input_diff_mv", 0.0)) == 0.0:
            continue
        corrected = float(row["corrected_preamp_output_diff_v"])
        polarity_corrected = -corrected
        measured_sign = 1 if polarity_corrected > 0 else -1 if polarity_corrected < 0 else 0
        expected_sign = int(row["expected_sign"])
        out.append(
            {
                "setting": row["name"],
                "input_diff_mv": row["input_diff_mv"],
                "expected_sign": expected_sign,
                "raw_corrected_preamp_output_diff_v": corrected,
                "polarity_corrected_output_diff_v": polarity_corrected,
                "polarity_corrected_measured_sign": measured_sign,
                "polarity_corrected_sign_preserved": measured_sign == expected_sign,
                "polarity_corrected_margin_pass": abs(polarity_corrected) >= OUTPUT_TARGET_V,
                "sample_to_sense_transfer_ratio": row["sample_to_sense_transfer_ratio"],
            }
        )
    return out


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    settings = sorted({row["setting"] for row in rows})
    summaries: list[dict[str, Any]] = []
    for setting in settings:
        group = [row for row in rows if row["setting"] == setting]
        summaries.append(
            {
                "name": setting,
                "case_count": len(group),
                "polarity_corrected_sign_pass_count": sum(1 for row in group if row["polarity_corrected_sign_preserved"]),
                "polarity_corrected_margin_pass_count": sum(1 for row in group if row["polarity_corrected_margin_pass"]),
                "minimum_abs_polarity_corrected_output_diff_v": min((abs(row["polarity_corrected_output_diff_v"]) for row in group), default=0.0),
                "minimum_sample_to_sense_transfer_ratio": min((row["sample_to_sense_transfer_ratio"] for row in group), default=0.0),
            }
        )
    return summaries


def build_report() -> dict[str, Any]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = corrected_rows(source["rows"])
    summaries = summarize(rows)
    passing = [
        item
        for item in summaries
        if item["case_count"] == 2
        and item["polarity_corrected_sign_pass_count"] == item["case_count"]
        and item["polarity_corrected_margin_pass_count"] == item["case_count"]
    ]
    best = max(summaries, key=lambda item: (item["polarity_corrected_margin_pass_count"], item["polarity_corrected_sign_pass_count"], item["minimum_abs_polarity_corrected_output_diff_v"]))
    return {
        "result_type": "sky130_polarity_corrected_transistor_handoff",
        "status": "polarity_corrected_transistor_handoff_passed_schematic_sign_map_not_layout_or_strict" if passing else "polarity_corrected_transistor_handoff_failed",
        "source_transistor_handoff": str(SOURCE.relative_to(ROOT)),
        "source_status": source["status"],
        "output_margin_target_v": OUTPUT_TARGET_V,
        "polarity_contract": "converter_positive_input_is_negative_raw_preamp_output_diff",
        "case_count": len(rows),
        "setting_count": len(summaries),
        "passing_setting_count": len(passing),
        "first_passing_setting": passing[0]["name"] if passing else None,
        "best_setting": best,
        "setting_summaries": summaries,
        "rows": rows,
        "uses_existing_transistor_measurements": True,
        "reruns_ngspice": False,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "shows that the measured transistor isolation/preamp schematic has a deterministic inverted sign that can satisfy both sign and margin checks when the converter polarity contract names the inversion",
            "not_allowed": "does not prove a new circuit, layout, DRC/LVS, offset stability over corners, noise, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence",
        },
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Polarity-Corrected Transistor Handoff",
        "",
        f"- status: `{report['status']}`",
        f"- source transistor status: `{report['source_status']}`",
        f"- polarity contract: `{report['polarity_contract']}`",
        f"- setting count: `{report['setting_count']}`",
        f"- case count: `{report['case_count']}`",
        f"- passing setting count: `{report['passing_setting_count']}`",
        f"- first passing setting: `{report['first_passing_setting']}`",
        f"- best setting: `{report['best_setting']['name']}`",
        f"- best minimum abs polarity-corrected output diff V: `{report['best_setting']['minimum_abs_polarity_corrected_output_diff_v']:.9e}`",
        f"- output margin target V: `{report['output_margin_target_v']:.9e}`",
        f"- reruns ngspice: `{report['reruns_ngspice']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A signed analog value is not only a voltage size. It is a voltage size plus a named direction. If the circuit always turns positive input into negative output and negative input into positive output, the circuit is not random. It is inverted.",
        "",
        "That inversion can be useful only if the next block is told the truth. The converter contract must say which raw preamp side means positive model value. Then both signs are checked after that contract is applied.",
        "",
        "This page does not create a new circuit result. It re-reads the measured transistor isolation/preamp result and asks whether a named polarity contract would make the already measured schematic satisfy sign and margin.",
        "",
        "## Setting Summary",
        "",
        "| setting | cases | sign pass after contract | margin pass after contract | min corrected output mV | min sense ratio |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in report["setting_summaries"]:
        lines.append(
            f"| `{item['name']}` | `{item['case_count']}` | `{item['polarity_corrected_sign_pass_count']}` | `{item['polarity_corrected_margin_pass_count']}` | `{item['minimum_abs_polarity_corrected_output_diff_v'] * 1000.0:.6f}` | `{item['minimum_sample_to_sense_transfer_ratio']:.6f}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            report["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_polarity_corrected_transistor_handoff")
    print(f"status,{report['status']}")
    print(f"setting_count,{report['setting_count']}")
    print(f"case_count,{report['case_count']}")
    print(f"passing_setting_count,{report['passing_setting_count']}")
    print(f"first_passing_setting,{report['first_passing_setting']}")
    print(f"best_setting,{report['best_setting']['name']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
