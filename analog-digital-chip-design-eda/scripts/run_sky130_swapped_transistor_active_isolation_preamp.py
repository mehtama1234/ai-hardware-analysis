#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import run_sky130_transistor_active_isolation_preamp as base


ROOT = base.ROOT
LAB = base.LAB
EVIDENCE = base.EVIDENCE

base.DECK_OUT = base.SPICE_DIR / "sky130_swapped_transistor_active_isolation_preamp.sp"
base.CSV_OUT = base.MEASUREMENTS / "sky130-swapped-transistor-active-isolation-preamp.csv"
# The attached extracted frontend can need more than the short diagnostic
# timeout. Keep the same 120 s convergence budget as the base handoff while
# preserving the swapped-output experiment.
base.NGSPICE_TIMEOUT_S = 120
base.SETTINGS = [setting for setting in base.SETTINGS if setting["name"] == "medium_iso_pair_8ua"]
OUT_JSON = EVIDENCE / "sky130-swapped-transistor-active-isolation-preamp.json"
OUT_MD = EVIDENCE / "sky130-swapped-transistor-active-isolation-preamp.md"
ORIGINAL_BUILD_DECK = base.build_deck
ORIGINAL_RUN_CASE = base.run_case


def swapped_deck(row: dict[str, Any], setting: dict[str, Any]) -> str:
    deck = ORIGINAL_BUILD_DECK(row, setting)
    deck = deck.replace("Sky130 transistor active isolation before preamp.", "Sky130 swapped-output transistor active isolation before preamp.")
    deck = deck.replace(
        "XPREP pre_p iso_p pre_tail 0 sky130_fd_pr__nfet_01v8",
        "XPREP pre_p iso_n pre_tail 0 sky130_fd_pr__nfet_01v8",
    )
    deck = deck.replace(
        "XPREN pre_n iso_n pre_tail 0 sky130_fd_pr__nfet_01v8",
        "XPREN pre_n iso_p pre_tail 0 sky130_fd_pr__nfet_01v8",
    )
    return deck


base.build_deck = swapped_deck


def run_case_with_progress(row: dict[str, Any], setting: dict[str, Any]) -> dict[str, Any]:
    print(f"case,{setting['name']},{row['input_diff_mv']}mV", flush=True)
    return ORIGINAL_RUN_CASE(row, setting)


base.run_case = run_case_with_progress


def build_report() -> dict[str, Any]:
    report = base.build_report()
    passing = [item for item in report["setting_summaries"] if item["measured_case_count"] == item["case_count"] and item["corrected_sign_pass_count"] == item["case_count"] and item["corrected_margin_pass_count"] == item["case_count"]]
    report["result_type"] = "sky130_swapped_transistor_active_isolation_preamp"
    report["status"] = "swapped_transistor_active_isolation_preamp_passed_schematic_not_layout_or_strict" if passing else "swapped_transistor_active_isolation_preamp_failed_schematic"
    report["source_failed_transistor_handoff"] = base.rel(EVIDENCE / "sky130-transistor-active-isolation-preamp.json")
    report["generated_deck"] = base.rel(base.DECK_OUT)
    report["csv"] = base.rel(base.CSV_OUT)
    report["passing_setting_count"] = len(passing)
    report["first_passing_setting"] = passing[0]["name"] if passing else None
    report["uses_swapped_isolation_outputs_into_preamp"] = True
    report["accepted_post_layout_written"] = False
    report["strict_payload_ready"] = False
    report["claim_boundary"] = {
        "allowed": "tests whether the transistor isolation pair had enough magnitude but the wrong handoff polarity by swapping its two outputs into the existing preamp",
        "not_allowed": "does not prove layout, DRC/LVS, offset stability over corners, noise, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence",
    }
    return report


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Swapped Transistor Active Isolation Preamp",
        "",
        f"- status: `{report['status']}`",
        f"- setting count: `{report['setting_count']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- passing setting count: `{report['passing_setting_count']}`",
        f"- first passing setting: `{report['first_passing_setting']}`",
        f"- best setting: `{report['best_setting']['name']}`",
        f"- best minimum abs corrected preamp output diff V: `{report['best_setting']['minimum_abs_corrected_preamp_output_diff_v']:.9e}`",
        f"- output margin target V: `{report['output_margin_target_v']:.9e}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The previous transistor isolation pair made enough output swing, but the corrected sign was inverted. That means the circuit did not fail like a weak amplifier. It failed like a handoff whose two sides are reversed.",
        "",
        "This run keeps the extracted frontend, the isolation pair, and the preamp bias the same. The only circuit change is that the two isolation outputs feed the opposite preamp inputs. If this passes, the next work is to turn the polarity-corrected schematic into a layout candidate and measure the effects that schematic SPICE does not include.",
        "",
        "## Setting Summary",
        "",
        "| setting | iso width | iso tail uA | zero output mV | measured | corrected sign pass | corrected margin pass | min corrected output mV | min sense ratio |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["setting_summaries"]:
        lines.append(
            f"| `{item['name']}` | `{item['wiso']:.3f}` | `{item['iso_tail_a'] * 1e6:.3f}` | `{item['zero_input_preamp_output_diff_v'] * 1000.0:.6f}` | `{item['measured_case_count']}` | `{item['corrected_sign_pass_count']}` | `{item['corrected_margin_pass_count']}` | `{item['minimum_abs_corrected_preamp_output_diff_v'] * 1000.0:.6f}` | `{item['minimum_sample_to_sense_transfer_ratio']:.6f}` |"
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
    base.write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_swapped_transistor_active_isolation_preamp")
    print(f"status,{report['status']}")
    print(f"setting_count,{report['setting_count']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
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
