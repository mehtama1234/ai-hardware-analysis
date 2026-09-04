#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
MEASUREMENTS = LAB / "measurements"
CSV_OUT = MEASUREMENTS / "sky130-differential-dummy-candidate-offset-noise-stress.csv"
OUT_JSON = EVIDENCE / "sky130-differential-dummy-candidate-offset-noise-stress.json"
OUT_MD = EVIDENCE / "sky130-differential-dummy-candidate-offset-noise-stress.md"


def load(name: str) -> dict[str, Any]:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def build_report() -> dict[str, Any]:
    margin = load("sky130-differential-dummy-candidate-decision-margin.json")
    half_lsb = margin["half_lsb_12b_v"]
    sample_hold_error = margin["worst_sample_hold_error_v"]
    remaining_budget_v = margin["remaining_comparator_offset_or_noise_budget_v"]
    offset_mv_values = [0.00, 0.05, 0.10, 0.15]
    noise_rms_mv_values = [0.00, 0.03, 0.05, 0.08, 0.10]
    rows = []
    for offset_mv in offset_mv_values:
        for noise_mv in noise_rms_mv_values:
            offset_v = offset_mv / 1000.0
            noise_v = noise_mv / 1000.0
            decision_uncertainty_v = math.hypot(offset_v, noise_v)
            total_error_v = sample_hold_error + decision_uncertainty_v
            rows.append(
                {
                    "comparator_offset_mv": offset_mv,
                    "decision_noise_rms_mv": noise_mv,
                    "sample_hold_error_v": sample_hold_error,
                    "decision_uncertainty_v": decision_uncertainty_v,
                    "total_decision_error_v": total_error_v,
                    "half_lsb_12b_v": half_lsb,
                    "remaining_margin_v": half_lsb - total_error_v,
                    "passes_half_lsb_12b": total_error_v <= half_lsb,
                }
            )
    passing = [row for row in rows if row["passes_half_lsb_12b"]]
    failing = [row for row in rows if not row["passes_half_lsb_12b"]]
    return {
        "result_type": "sky130_differential_dummy_candidate_offset_noise_stress",
        "status": "sky130_differential_dummy_candidate_offset_noise_stress_defined_not_comparator_proof",
        "decision_margin_source": "sky130-differential-dummy-candidate-decision-margin",
        "half_lsb_12b_v": half_lsb,
        "sample_hold_error_v": sample_hold_error,
        "remaining_comparator_offset_or_noise_budget_v": remaining_budget_v,
        "remaining_comparator_offset_or_noise_budget_mv": remaining_budget_v * 1000.0,
        "case_count": len(rows),
        "passing_case_count": len(passing),
        "failing_case_count": len(failing),
        "max_passing_decision_uncertainty_mv": max((row["decision_uncertainty_v"] * 1000.0 for row in passing), default=None),
        "min_failing_decision_uncertainty_mv": min((row["decision_uncertainty_v"] * 1000.0 for row in failing), default=None),
        "rows": rows,
        "csv": rel(CSV_OUT),
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "combines measured sample-hold error with assumed comparator offset and decision noise budgets",
            "not_allowed": "does not simulate comparator devices, noise spectra, metastability, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics",
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
        "# Sky130 Differential Dummy Candidate Offset Noise Stress",
        "",
        f"- status: `{report['status']}`",
        f"- decision margin source: `{report['decision_margin_source']}`",
        f"- half LSB 12b V: `{fmt(report['half_lsb_12b_v'])}`",
        f"- sample-hold error V: `{fmt(report['sample_hold_error_v'])}`",
        f"- remaining comparator offset or noise budget mV: `{report['remaining_comparator_offset_or_noise_budget_mv']:.4f}`",
        f"- case count: `{report['case_count']}`",
        f"- passing case count: `{report['passing_case_count']}`",
        f"- failing case count: `{report['failing_case_count']}`",
        f"- max passing decision uncertainty mV: `{report['max_passing_decision_uncertainty_mv']:.4f}`",
        f"- min failing decision uncertainty mV: `{report['min_failing_decision_uncertainty_mv']:.4f}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "The comparator adds uncertainty to the same voltage that the sample-and-hold already moved. Offset is a fixed shift. Decision noise is a random spread. Before a transistor comparator is worth drawing, the combined uncertainty must fit inside the remaining half-LSB budget.",
        "",
        "This table uses a conservative scalar check. It combines offset and RMS noise as one input-referred decision uncertainty, then adds that to the measured worst sample-hold error. It is a budget stress test, not a transistor-level comparator simulation.",
        "",
        "## Stress Table",
        "",
        "| comparator offset mV | decision noise RMS mV | decision uncertainty mV | total decision error V | remaining margin V | passes half LSB |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| `{row['comparator_offset_mv']:.2f}` | `{row['decision_noise_rms_mv']:.2f}` | `{row['decision_uncertainty_v'] * 1000.0:.4f}` | `{row['total_decision_error_v']:.9e}` | `{row['remaining_margin_v']:.9e}` | `{row['passes_half_lsb_12b']}` |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "The next comparator target is not a vague low-noise request. It must keep input-referred offset and decision noise under the measured remaining budget, or the passing sample-and-hold candidate no longer supports a 12-bit decision.",
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
    print("sky130_differential_dummy_candidate_offset_noise_stress")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"passing_case_count,{report['passing_case_count']}")
    print(f"max_passing_decision_uncertainty_mv,{report['max_passing_decision_uncertainty_mv']:.4f}")
    print(f"min_failing_decision_uncertainty_mv,{report['min_failing_decision_uncertainty_mv']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
