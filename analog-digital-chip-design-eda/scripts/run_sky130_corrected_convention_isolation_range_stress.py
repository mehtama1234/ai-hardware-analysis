#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_sky130_corrected_convention_capacitive_isolation_confirm as base  # noqa: E402


EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
CONFIRM_JSON = EVIDENCE / "sky130-corrected-convention-capacitive-isolation-confirm.json"
OUT_JSON = EVIDENCE / "sky130-corrected-convention-isolation-range-stress.json"
OUT_MD = EVIDENCE / "sky130-corrected-convention-isolation-range-stress.md"
CSV_OUT = LAB / "measurements" / "sky130-corrected-convention-isolation-range-stress.csv"
base.DECK_OUT = base.SPICE_DIR / "sky130_corrected_convention_isolation_range_stress.sp"
base.CSV_OUT = CSV_OUT


def write_outputs(report: dict[str, Any]) -> None:
    base.CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    import csv

    keys = sorted({key for row in report["rows"] for key in row})
    with base.CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Corrected-Convention Isolation Range Stress",
        "",
        f"- status: `{report['status']}`",
        f"- output definition: `{report['output_definition']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- passing case count: `{report['passing_case_count']}`",
        f"- tested coupling caps fF: `{', '.join(f'{cap:g}' for cap in report['tested_coupling_caps_ff'])}`",
        f"- tested input diff mV: `{', '.join(f'{value:.6f}' for value in report['tested_abs_input_diff_mv'])}`",
        f"- worst sampled differential kickback V: `{base.fmt(report['worst_sampled_diff_kickback_v'])}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- minimum abs output diff V: `{base.fmt(report['minimum_abs_output_diff_v'])}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A comparator candidate that only works at one tiny input is fragile. The next question is whether the same isolated latch input still resolves when the sampled difference is moved above the target edge.",
        "",
        "This run keeps the same tiny capacitive isolation and corrected `outp - outn` convention. It sweeps both signs at one, two, and five times the target-edge differential. The gate is still narrow: no noise, no layout, no SAR loop. It only asks whether nominal schematic behavior stays stable over a small useful range.",
        "",
        "## Results",
        "",
        "| cap fF | input diff mV | kickback V | output diff V | resolved | kickback pass |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        if not row.get("measured"):
            lines.append(f"| `{row.get('coupling_cap_ff')}` | `{row['input_diff_mv']}` | failed | failed | `False` | `False` |")
            continue
        lines.append(
            f"| `{row['coupling_cap_ff']:.3f}` | `{row['input_diff_mv']:.6f}` | `{row['sampled_diff_kickback_v']:.9e}` | `{row['output_diff_final_v']:.9e}` | `{row['resolved_correct_polarity']}` | `{row['kickback_below_half_lsb']}` |"
        )
    lines.extend(["", "## Boundary", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def build_report() -> dict[str, Any]:
    confirm = json.loads(CONFIRM_JSON.read_text(encoding="utf-8"))
    target_mv = float(confirm["target_combined_offset_noise_mv"])
    caps = [cap * 1e-15 for cap in [0.1, 0.2]]
    multipliers = [1.0, 2.0, 5.0]
    cases: list[base.Case] = []
    for cap in caps:
        for mult in multipliers:
            diff_mv = target_mv * mult
            cases.append(base.Case(f"ciso_{base.cap_label(cap)}_negative_{mult:g}x_target", cap, -diff_mv))
            cases.append(base.Case(f"ciso_{base.cap_label(cap)}_positive_{mult:g}x_target", cap, diff_mv))
    rows = [base.run_case(case) for case in cases]
    measured = [row for row in rows if row["measured"]]
    passing = [row for row in measured if row.get("resolved_correct_polarity") and row.get("kickback_below_half_lsb")]
    return {
        "result_type": "sky130_corrected_convention_isolation_range_stress",
        "status": "corrected_convention_isolation_range_stress_passed_not_noise_or_layout_proof" if len(passing) == len(rows) else "corrected_convention_isolation_range_stress_characterized_not_ready",
        "source_confirm": str(CONFIRM_JSON.relative_to(ROOT)),
        "generated_deck": str(base.DECK_OUT.relative_to(ROOT)),
        "csv": str(CSV_OUT.relative_to(ROOT)),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "passing_case_count": len(passing),
        "tested_coupling_caps_ff": [0.1, 0.2],
        "tested_abs_input_diff_mv": [target_mv * mult for mult in multipliers],
        "half_lsb_12b_v": 1.8 / 4096.0 / 2.0,
        "worst_sampled_diff_kickback_v": max((row.get("sampled_diff_kickback_v", 0.0) for row in measured), default=None),
        "minimum_abs_output_diff_v": min((abs(row.get("output_diff_final_v", 0.0)) for row in measured), default=None),
        "output_definition": "outp_minus_outn",
        "uses_capacitive_input_isolation": True,
        "uses_sampled_nodes": True,
        "uses_corrected_latch_output_convention": True,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "rows": rows,
        "claim_boundary": {
            "allowed": "stress-tests the confirmed tiny-capacitor isolated latch input over both signs and three input magnitudes in schematic ngspice",
            "not_allowed": "does not prove comparator noise, offset statistics, clock timing margin, SAR bit cycling, extracted layout, DRC/LVS, or accepted post-layout converter evidence",
        },
    }


def main() -> int:
    report = build_report()
    write_outputs(report)
    print("sky130_corrected_convention_isolation_range_stress")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"passing_case_count,{report['passing_case_count']}")
    print(f"worst_sampled_diff_kickback_v,{report['worst_sampled_diff_kickback_v']}")
    print(f"minimum_abs_output_diff_v,{report['minimum_abs_output_diff_v']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
