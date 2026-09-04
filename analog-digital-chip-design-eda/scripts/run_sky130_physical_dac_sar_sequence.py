#!/usr/bin/env python3
"""Sequence retained-bit SAR decisions using the physical DAC/comparator runner."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from run_sky130_coupled_dac_comparator_bit import run_trial

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-physical-dac-sar-sequence.json"
OUT_MD = EVIDENCE / "sky130-physical-dac-sar-sequence.md"
BITS = 4
DAC_SOURCE_V = 0.9
STEP_V = 1.8 / (1 << BITS)
# These are centers of ideal code regions while keeping the comparator input
# below the 1.8 V supply. They test retained-bit sequencing, not full range.
INPUT_CODES = (0, 2, 4, 6, 7)


def sequence(expected_code: int) -> dict[str, Any]:
    input_v = DAC_SOURCE_V + STEP_V * (expected_code + 0.5)
    code = 0
    trace = []
    for decision_number, bit in enumerate(reversed(range(BITS)), start=1):
        trial_code = code | (1 << bit)
        comparison = run_trial(trial_code, DAC_SOURCE_V, input_v)
        if not comparison.get("measured"):
            trace.append({"decision_number": decision_number, "bit": bit, "trial_code": trial_code, "comparison": comparison, "accepted": False})
            break
        # The comparator receives DAC top on its positive input and the target
        # input on its negative input. Keep the trial bit when DAC < input.
        accepted = comparison["dac_to_reference_diff_v"] < 0.0
        if accepted:
            code = trial_code
        trace.append({"decision_number": decision_number, "bit": bit, "trial_code": trial_code, "accepted": accepted, "comparison": comparison})
    return {
        "expected_code": expected_code,
        "input_v": input_v,
        "final_code": code,
        "comparison_count": len(trace),
        "all_comparisons_measured": len(trace) == BITS and all(row["comparison"].get("measured") for row in trace),
        "correct_code": code == expected_code and len(trace) == BITS,
        "trace": trace,
    }


def main() -> int:
    conversions = [sequence(code) for code in INPUT_CODES]
    comparisons = [row["comparison"] for conversion in conversions for row in conversion["trace"]]
    measured = [row for row in comparisons if row.get("measured")]
    report = {
        "result_type": "sky130_physical_dac_sar_sequence",
        "status": "physical_dac_sar_sequence_characterized_not_continuous_multicycle_proof",
        "bits": BITS,
        "dac_source_v": DAC_SOURCE_V,
        "input_codes": list(INPUT_CODES),
        "conversion_count": len(conversions),
        "comparison_count": len(comparisons),
        "measured_comparison_count": len(measured),
        "correct_conversion_count": sum(row["correct_code"] for row in conversions),
        "conversions": conversions,
        "claim_boundary": {
            "allowed": "sequences retained-bit SAR decisions where every trial uses the physical Sky130 DAC/comparator transient runner",
            "not_allowed": "does not prove one continuous multi-cycle SPICE deck, full input range, PVT accuracy, random mismatch/noise yield, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Physical DAC SAR Sequence", "",
        f"- status: `{report['status']}`",
        f"- conversions: `{report['conversion_count']}`",
        f"- comparator trials: `{report['measured_comparison_count']}` of `{report['comparison_count']}` measured",
        f"- correct conversions: `{report['correct_conversion_count']}` of `{report['conversion_count']}`", "",
        "## What Is Physical", "",
        "This runner performs a real most-significant-bit-first SAR sequence. It proposes a trial code, runs the physical capacitor DAC and transistor comparator together, reads the sign, and retains or clears the trial bit before proposing the next bit. The next decision sees the previous digital code, so this is stronger than replaying one fixed code per row.", "",
        "Each comparison is currently a fresh transient with the same circuit reset. That preserves physical DAC/comparator behavior for every bit but does not yet prove clock-to-clock state retention inside one continuous SPICE deck. The artifact keeps that boundary explicit.", "",
        "## Results", "",
        "| expected code | input V | final code | comparisons | correct |", "| ---: | ---: | ---: | ---: | --- |",
    ]
    for row in conversions:
        lines.append(f"| {row['expected_code']} | {row['input_v']:.6f} | {row['final_code']} | {row['comparison_count']} | {row['correct_code']} |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"comparisons,{report['measured_comparison_count']}/{report['comparison_count']}")
    print(f"correct_conversions,{report['correct_conversion_count']}/{report['conversion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
