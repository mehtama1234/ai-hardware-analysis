#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
MEASUREMENTS = LAB / "measurements"
CSV_OUT = MEASUREMENTS / "sky130-differential-dummy-candidate-decision-margin.csv"
OUT_JSON = EVIDENCE / "sky130-differential-dummy-candidate-decision-margin.json"
OUT_MD = EVIDENCE / "sky130-differential-dummy-candidate-decision-margin.md"


def load(name: str) -> dict[str, Any]:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def build_report() -> dict[str, Any]:
    input_sweep = load("sky130-differential-dummy-candidate-input-sweep.json")
    mismatch_sweep = load("sky130-differential-dummy-candidate-mismatch-sweep.json")
    half_lsb = input_sweep["half_lsb_12b_v"]
    worst_input = input_sweep["worst_diff_hold_abs_delta_v"]
    worst_mismatch = mismatch_sweep["worst_diff_hold_abs_delta_v"]
    worst_sample_hold = max(worst_input, worst_mismatch)
    remaining_budget = half_lsb - worst_sample_hold
    offsets_mv = [0.02, 0.05, 0.10, 0.15, 0.20]
    rows = []
    for offset_mv in offsets_mv:
        offset_v = offset_mv / 1000.0
        total_error = worst_sample_hold + offset_v
        rows.append(
            {
                "comparator_offset_mv": offset_mv,
                "comparator_offset_v": offset_v,
                "sample_hold_error_v": worst_sample_hold,
                "total_decision_error_v": total_error,
                "half_lsb_12b_v": half_lsb,
                "remaining_margin_v": half_lsb - total_error,
                "passes_half_lsb_12b": total_error <= half_lsb,
            }
        )
    max_passing_offset = max((row["comparator_offset_mv"] for row in rows if row["passes_half_lsb_12b"]), default=None)
    return {
        "result_type": "sky130_differential_dummy_candidate_decision_margin",
        "status": "sky130_differential_dummy_candidate_decision_margin_defined_not_converter_proof",
        "input_sweep_source": "sky130-differential-dummy-candidate-input-sweep",
        "mismatch_sweep_source": "sky130-differential-dummy-candidate-mismatch-sweep",
        "half_lsb_12b_v": half_lsb,
        "worst_input_sweep_diff_hold_v": worst_input,
        "worst_mismatch_sweep_diff_hold_v": worst_mismatch,
        "worst_sample_hold_error_v": worst_sample_hold,
        "remaining_comparator_offset_or_noise_budget_v": remaining_budget,
        "remaining_comparator_offset_or_noise_budget_mv": remaining_budget * 1000.0,
        "tested_offset_rows": rows,
        "max_passing_tested_comparator_offset_mv": max_passing_offset,
        "csv": rel(CSV_OUT),
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "turns the measured sample-hold decision-voltage error into a remaining comparator offset/noise budget",
            "not_allowed": "does not simulate comparator transistors, random noise, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics",
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
        "# Sky130 Differential Dummy Candidate Decision Margin",
        "",
        f"- status: `{report['status']}`",
        f"- input sweep source: `{report['input_sweep_source']}`",
        f"- mismatch sweep source: `{report['mismatch_sweep_source']}`",
        f"- half LSB 12b V: `{fmt(report['half_lsb_12b_v'])}`",
        f"- worst input-sweep differential hold V: `{fmt(report['worst_input_sweep_diff_hold_v'])}`",
        f"- worst mismatch-sweep differential hold V: `{fmt(report['worst_mismatch_sweep_diff_hold_v'])}`",
        f"- worst sample-hold error V: `{fmt(report['worst_sample_hold_error_v'])}`",
        f"- remaining comparator offset or noise budget mV: `{report['remaining_comparator_offset_or_noise_budget_mv']:.4f}`",
        f"- max passing tested comparator offset mV: `{report['max_passing_tested_comparator_offset_mv']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A later comparator does not see the sample-and-hold error separately from its own offset and noise. It sees one decision voltage. If the sample-and-hold already spends part of the half-LSB budget, the comparator must fit inside what remains.",
        "",
        "The measured candidate leaves a finite voltage margin. This page turns that margin into a simple offset and noise budget. It is not a comparator simulation. It is the arithmetic gate that says how accurate the comparator must be before a SAR proof is meaningful.",
        "",
        "## Offset Budget Table",
        "",
        "| comparator offset mV | sample-hold error V | total decision error V | remaining margin V | passes half LSB |",
        "|---:|---:|---:|---:|---|",
    ]
    for row in report["tested_offset_rows"]:
        lines.append(
            f"| `{row['comparator_offset_mv']:.3f}` | `{row['sample_hold_error_v']:.9e}` | `{row['total_decision_error_v']:.9e}` | `{row['remaining_margin_v']:.9e}` | `{row['passes_half_lsb_12b']}` |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "The candidate is useful only if the next comparator can keep its input-referred offset and decision noise inside the remaining margin. If the comparator spends more than that, the sample-and-hold pass no longer matters because the combined decision error crosses the 12-bit line.",
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
    write_csv(report["tested_offset_rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_differential_dummy_candidate_decision_margin")
    print(f"status,{report['status']}")
    print(f"worst_sample_hold_error_v,{report['worst_sample_hold_error_v']:.9e}")
    print(f"remaining_comparator_offset_or_noise_budget_mv,{report['remaining_comparator_offset_or_noise_budget_mv']:.4f}")
    print(f"max_passing_tested_comparator_offset_mv,{report['max_passing_tested_comparator_offset_mv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
