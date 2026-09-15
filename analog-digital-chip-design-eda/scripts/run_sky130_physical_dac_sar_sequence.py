#!/usr/bin/env python3
"""Sequence retained-bit SAR decisions using the physical DAC/comparator runner."""

from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
from typing import Any

# The physical DAC/comparator fixture requires the long acquisition schedule
# for bottom-plate redistribution to settle before comparator sampling. Keep
# an explicit environment override for diagnostic short-schedule experiments.
os.environ.setdefault("AIMC_COUPLED_DAC_ACQ", "long")

from run_sky130_coupled_dac_comparator_bit import run_trial

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUTPUT_STEM = os.environ.get("AIMC_PHYSICAL_SAR_OUTPUT_STEM", "sky130-physical-dac-sar-sequence")
OUT_JSON = EVIDENCE / f"{OUTPUT_STEM}.json"
OUT_MD = EVIDENCE / f"{OUTPUT_STEM}.md"
BITS = 4
DAC_SOURCE_V = 0.9
INPUT_SPAN_V = float(os.environ.get("AIMC_PHYSICAL_SAR_INPUT_SPAN_V", "1.8"))
STEP_V = INPUT_SPAN_V / (1 << BITS)
# These are centers of ideal code regions while keeping the comparator input
# below the 1.8 V supply. They test retained-bit sequencing, not full range.
INPUT_CODES = (0, 2, 4, 6, 7)
CALIBRATION_TABLE_PATH = Path(os.environ["AIMC_PHYSICAL_SAR_CALIBRATION_TABLE"]).resolve() if os.environ.get("AIMC_PHYSICAL_SAR_CALIBRATION_TABLE") else None


def calibrated_targets() -> list[float] | None:
    if CALIBRATION_TABLE_PATH is None:
        return None
    report = json.loads(CALIBRATION_TABLE_PATH.read_text(encoding="utf-8"))
    values = [float(row["dac_top_after_v"]) for row in report["table"]]
    if len(values) != 16 or any(b <= a for a, b in zip(values, values[1:])):
        raise ValueError("calibration table must contain a complete monotonic 16-code transfer")
    return [values[0] - (values[1] - values[0]) / 2.0] + [(a + b) / 2.0 for a, b in zip(values, values[1:])] + [values[-1] + (values[-1] - values[-2]) / 2.0]


def requested_input_codes() -> tuple[int, ...]:
    """Allow a bounded smoke subset while preserving the default sweep."""
    raw = os.environ.get("AIMC_PHYSICAL_SAR_INPUT_CODES", "")
    if not raw.strip():
        return INPUT_CODES
    values = tuple(int(token.strip()) for token in raw.split(",") if token.strip())
    if not values or any(value < 0 or value >= (1 << BITS) for value in values):
        raise ValueError("AIMC_PHYSICAL_SAR_INPUT_CODES must contain codes in [0, 15]")
    return values


def sequence(expected_code: int) -> dict[str, Any]:
    targets = calibrated_targets()
    input_v = targets[expected_code] if targets is not None else DAC_SOURCE_V + STEP_V * (expected_code + 0.5)
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
    input_codes = requested_input_codes()
    targets = calibrated_targets()
    workers = max(1, int(os.environ.get("AIMC_PHYSICAL_SAR_WORKERS", "1")))
    # Input-code conversions are independent; each sequence itself remains
    # strictly MSB-first and serial. map() preserves deterministic code order.
    with ThreadPoolExecutor(max_workers=min(workers, len(input_codes))) as pool:
        conversions = list(pool.map(sequence, input_codes))
    comparisons = [row["comparison"] for conversion in conversions for row in conversion["trace"]]
    measured = [row for row in comparisons if row.get("measured")]
    timeouts = sum(row.get("timed_out", False) for row in comparisons)
    full_code_campaign = tuple(input_codes) == tuple(range(1 << BITS))
    status = (
        "physical_dac_sar_full_code_campaign_timeout"
        if timeouts and not measured and full_code_campaign
        else "physical_dac_sar_timeout_smoke"
        if timeouts and not measured
        else "physical_dac_sar_full_code_campaign_characterized_not_continuous_multicycle_proof"
        if full_code_campaign
        else "physical_dac_sar_sequence_characterized_not_continuous_multicycle_proof"
    )
    report = {
        "result_type": "sky130_physical_dac_sar_sequence",
        "status": status,
        "dac_acquisition_schedule": os.environ.get("AIMC_COUPLED_DAC_ACQ", "long"),
        "worker_count": workers,
        "bits": BITS,
        "dac_source_v": DAC_SOURCE_V,
        "input_span_v": INPUT_SPAN_V,
        "input_target_mode": "measured_transfer_midpoints" if targets is not None else "linear_span",
        "calibration_table": str(CALIBRATION_TABLE_PATH) if CALIBRATION_TABLE_PATH else None,
        "calibration_table_sha256": hashlib.sha256(CALIBRATION_TABLE_PATH.read_bytes()).hexdigest() if CALIBRATION_TABLE_PATH else None,
        "input_codes": list(input_codes),
        "full_code_campaign": full_code_campaign,
        "conversion_count": len(conversions),
        "comparison_count": len(comparisons),
        "measured_comparison_count": len(measured),
        "timeout_count": timeouts,
        "correct_conversion_count": sum(row["correct_code"] for row in conversions),
        "failing_input_codes": [row["expected_code"] for row in conversions if not row["correct_code"]],
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
