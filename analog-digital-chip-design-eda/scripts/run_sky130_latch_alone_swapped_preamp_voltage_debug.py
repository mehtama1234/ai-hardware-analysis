#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import run_sky130_latch_alone_from_preamp_voltage_debug as base


ROOT = base.ROOT
EVIDENCE = base.EVIDENCE
base.DECK_OUT = base.SPICE_DIR / "sky130_latch_alone_swapped_preamp_voltage_debug.sp"
base.CSV_OUT = base.MEASUREMENTS / "sky130-latch-alone-swapped-preamp-voltage-debug.csv"
OUT_JSON = EVIDENCE / "sky130-latch-alone-swapped-preamp-voltage-debug.json"
OUT_MD = EVIDENCE / "sky130-latch-alone-swapped-preamp-voltage-debug.md"
ORIGINAL_BUILD_DECK = base.build_deck


def swapped_deck(case: base.Case) -> str:
    swapped = base.Case(case.name, case.input_diff_mv, case.pre_n_v, case.pre_p_v)
    deck = ORIGINAL_BUILD_DECK(swapped)
    return deck.replace("Sky130 latch-alone from measured preamp voltages.", "Sky130 latch-alone from swapped measured preamp voltages.")


base.build_deck = swapped_deck


def build_report() -> dict[str, Any]:
    report = base.build_report()
    resolved = sum(1 for row in report["rows"] if row.get("resolved_correct_polarity"))
    passed = report["measured_case_count"] == report["case_count"] and resolved == report["case_count"]
    report["result_type"] = "sky130_latch_alone_swapped_preamp_voltage_debug"
    report["status"] = "latch_alone_swapped_preamp_voltage_passed_ready_for_clock_timing" if passed else "latch_alone_swapped_preamp_voltage_failed"
    report["source_failed_latch_alone"] = base.rel(EVIDENCE / "sky130-latch-alone-from-preamp-voltage-debug.json")
    report["generated_deck"] = base.rel(base.DECK_OUT)
    report["csv"] = base.rel(base.CSV_OUT)
    report["uses_swapped_preamp_voltage_mapping"] = True
    report["resolved_correct_polarity_count"] = resolved
    report["claim_boundary"] = {
        "allowed": "checks whether swapping the measured preamp voltages into the latch input fixes the latch-alone polarity inversion",
        "not_allowed": "does not prove sampled-node kickback, coupled preamp/latch loading, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence",
    }
    return report


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Latch-Alone Swapped Preamp Voltage Debug",
        "",
        f"- status: `{report['status']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- resolved correct polarity count: `{report['resolved_correct_polarity_count']}`",
        f"- minimum abs latch output diff V: `{report['minimum_abs_latch_output_diff_v']:.9e}`",
        f"- uses swapped preamp voltage mapping: `{report['uses_swapped_preamp_voltage_mapping']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The prior latch-alone run did not look weak. It resolved hard, but with the opposite sign. That is a polarity-map failure, not a gain failure.",
        "",
        "This run swaps the two measured preamp voltages before they drive the latch inputs. If both signs now resolve, the next clock-timing work should preserve this mapping explicitly.",
        "",
        "## Results",
        "",
        "| case | measured | pre_p V | pre_n V | output diff V | resolved |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| `{row['case']}` | `{row['measured']}` | `{base.fmt(row.get('pre_p_v'))}` | `{base.fmt(row.get('pre_n_v'))}` | `{base.fmt(row.get('output_diff_final_v'))}` | `{row.get('resolved_correct_polarity')}` |"
        )
    lines.extend(["", "## Boundary", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    base.CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in report["rows"] for key in row})
    with base.CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        import csv

        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_latch_alone_swapped_preamp_voltage_debug")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"resolved_correct_polarity_count,{report['resolved_correct_polarity_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
