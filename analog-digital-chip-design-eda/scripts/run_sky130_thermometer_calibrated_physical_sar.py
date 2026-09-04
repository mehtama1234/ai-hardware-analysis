#!/usr/bin/env python3
"""Calibrate the nominal thermometer DAC and run mapped SAR trials."""

from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from run_sky130_thermometer_dac_comparator import run_trial


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-thermometer-calibrated-physical-sar.json"
OUT_MD = EVIDENCE / "sky130-thermometer-calibrated-physical-sar.md"
BITS = 4
VDD = 1.8
SOURCE_V = float(os.environ.get("AIMC_THERMOMETER_SAR_SOURCE_V", "0.0"))
STEP_V = VDD / (1 << BITS)
CALIBRATION_REFERENCE_V = float(os.environ.get("AIMC_THERMOMETER_SAR_CAL_REFERENCE_V", "1.0"))
INPUT_CODES = tuple(int(value) for value in os.environ.get("AIMC_THERMOMETER_SAR_INPUT_CODES", "0,2,4,6,7").split(",") if value.strip())
DIFFERENTIAL = os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_ENCODING") == "1"
DIFFERENTIAL_COMMON_V = float(os.environ.get("AIMC_THERMOMETER_SAR_DIFFERENTIAL_COMMON_V", "0.9"))


def run_trial_with_retries(code: int, input_v: float, reference_v: float, label: str) -> dict[str, Any]:
    attempts = max(1, int(os.environ.get("AIMC_THERMOMETER_SAR_RETRIES", "2")))
    last_row: dict[str, Any] | None = None
    for attempt in range(1, attempts + 1):
        print(f"{label} code {code} attempt {attempt}/{attempts}", flush=True)
        differential_source_v = DIFFERENTIAL_COMMON_V if DIFFERENTIAL else None
        row = run_trial(code, input_v, reference_v, differential_source_v)
        row["attempt"] = attempt
        last_row = row
        if row.get("measured"):
            return row
    assert last_row is not None
    return last_row


def calibration_metadata() -> dict[str, Any]:
    input_scale = float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_INPUT_SCALE", "1.0"))
    input_offset = float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_INPUT_OFFSET", str(DIFFERENTIAL_COMMON_V * (1.0 - input_scale))))
    return {
        "topology": "complementary_differential_break_before_make_thermometer" if DIFFERENTIAL else "thermometer_equal_unit_capacitor",
        "source_v": SOURCE_V,
        "calibration_reference_v": CALIBRATION_REFERENCE_V,
        "source_acquisition_ns": float(os.environ.get("AIMC_THERMOMETER_SOURCE_ACQ_NS", "4.0")),
        "bottom_switch_scale": float(os.environ.get("AIMC_THERMOMETER_BOTTOM_SCALE", "1.0")),
        "differential_encoding": DIFFERENTIAL,
        "differential_dummy_scale": float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_DUMMY_SCALE", "1.0")),
        "differential_common_v": DIFFERENTIAL_COMMON_V,
        "differential_input_scale": input_scale,
        "differential_input_offset": input_offset,
    }


def read_cache(path: Path) -> dict[int, dict[str, Any]]:
    if not path.exists():
        return {}
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("metadata") != calibration_metadata():
        return {}
    return {int(code): row for code, row in report.get("rows", {}).items() if row.get("measured")}


def write_cache(path: Path, rows: dict[int, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"metadata": calibration_metadata(), "rows": {str(k): rows[k] for k in sorted(rows)}}, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def calibrate() -> list[dict[str, Any]]:
    workers = max(1, int(os.environ.get("AIMC_THERMOMETER_SAR_CAL_WORKERS", "1")))
    cache_name = os.environ.get("AIMC_THERMOMETER_SAR_CAL_CACHE")
    if cache_name and workers == 1:
        path = Path(cache_name)
        rows = read_cache(path)
        for code in range(1 << BITS):
            if code in rows:
                print(f"calibration code {code} cache hit", flush=True)
                continue
            row = run_trial_with_retries(code, DIFFERENTIAL_COMMON_V if DIFFERENTIAL else SOURCE_V, CALIBRATION_REFERENCE_V, "calibration")
            if row.get("measured"):
                rows[code] = row
                write_cache(path, rows)
        return [rows.get(code, {"code": code, "measured": False}) for code in range(1 << BITS)]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda code: run_trial_with_retries(code, DIFFERENTIAL_COMMON_V if DIFFERENTIAL else SOURCE_V, CALIBRATION_REFERENCE_V, "calibration"), range(1 << BITS)))


def mapped_sequence(expected_code: int, code_map: dict[int, int]) -> dict[str, Any]:
    target_v = SOURCE_V + STEP_V * (expected_code + 0.5)
    logical_code = 0
    trace: list[dict[str, Any]] = []
    for decision_number, bit in enumerate(reversed(range(BITS)), start=1):
        logical_trial = logical_code | (1 << bit)
        physical_trial = code_map[logical_trial]
        comparison = run_trial_with_retries(physical_trial, target_v if DIFFERENTIAL else SOURCE_V, DIFFERENTIAL_COMMON_V if DIFFERENTIAL else target_v, f"conversion expected {expected_code} decision {decision_number}")
        measured_value = float(comparison.get("dac_to_reference_diff_v", 0.0))
        accepted = bool(comparison.get("measured")) and (measured_value > 0.0 if DIFFERENTIAL else measured_value < 0.0)
        if accepted:
            logical_code = logical_trial
        trace.append({"decision_number": decision_number, "bit": bit, "logical_trial_code": logical_trial, "physical_trial_code": physical_trial, "accepted": accepted, "comparison": comparison})
        if not comparison.get("measured"):
            break
    return {"expected_code": expected_code, "input_v": target_v, "final_code": logical_code, "comparison_count": len(trace), "correct_code": logical_code == expected_code and len(trace) == BITS, "trace": trace}


def main() -> int:
    calibration_rows = calibrate()
    measured = [row for row in calibration_rows if row.get("measured")]
    missing = sorted(set(range(1 << BITS)) - {int(row["code"]) for row in measured})
    if missing:
        raise SystemExit(f"calibration incomplete; missing codes {missing}")
    thresholds = {int(row["code"]): float(row["dac_top_after_v"]) for row in measured}
    if DIFFERENTIAL:
        low_threshold = min(thresholds.values())
        high_threshold = max(thresholds.values())
        input_scale = float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_INPUT_SCALE", "1.0"))
        input_offset = float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_INPUT_OFFSET", str(DIFFERENTIAL_COMMON_V * (1.0 - input_scale))))
        code_map = {logical: min(thresholds, key=lambda physical: abs(thresholds[physical] - (DIFFERENTIAL_COMMON_V - input_offset - input_scale * STEP_V * logical))) for logical in range(1 << BITS)}
    else:
        code_map = {logical: min(thresholds, key=lambda physical: abs(thresholds[physical] - (SOURCE_V + STEP_V * logical))) for logical in range(1 << BITS)}
    workers = max(1, int(os.environ.get("AIMC_THERMOMETER_SAR_CONVERSION_WORKERS", "1")))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        conversions = list(pool.map(lambda code: mapped_sequence(code, code_map), INPUT_CODES))
    comparisons = [step["comparison"] for conversion in conversions for step in conversion["trace"]]
    correct_conversion_count = sum(bool(row["correct_code"]) for row in conversions)
    sar_status = ("differential_break_before_make_sar_candidate_nominal_only" if correct_conversion_count == len(conversions) else "differential_break_before_make_sar_rejected_source_common_mode") if DIFFERENTIAL else "thermometer_calibrated_sar_characterized_not_continuous_multicycle_proof"
    report = {
        "result_type": "sky130_thermometer_calibrated_physical_sar",
        "status": sar_status,
        "bits": BITS,
        "topology": "complementary_differential_break_before_make_thermometer" if DIFFERENTIAL else "thermometer_equal_unit_capacitor",
        "source_v": SOURCE_V,
        "calibration_reference_v": CALIBRATION_REFERENCE_V,
        "source_acquisition_ns": float(os.environ.get("AIMC_THERMOMETER_SOURCE_ACQ_NS", "4.0")),
        "bottom_switch_scale": float(os.environ.get("AIMC_THERMOMETER_BOTTOM_SCALE", "1.0")),
        "differential_encoding": DIFFERENTIAL,
        "differential_dummy_scale": float(os.environ.get("AIMC_THERMOMETER_DIFFERENTIAL_DUMMY_SCALE", "1.0")),
        "differential_common_v": DIFFERENTIAL_COMMON_V,
        "calibration_case_count": len(calibration_rows),
        "calibration_measured_count": len(measured),
        "calibration_thresholds_v": thresholds,
        "logical_to_physical_code_map": code_map,
        "conversion_count": len(conversions),
        "comparison_count": len(comparisons),
        "measured_comparison_count": sum(bool(row.get("measured")) for row in comparisons),
        "correct_conversion_count": correct_conversion_count,
        "source_common_mode_contract": "differential sampled source requires a legal common-mode and input swing across the full task range",
        "conversions": conversions,
        "claim_boundary": {
            "allowed": "uses the measured nominal thermometer-DAC transfer to drive mapped physical comparator trials",
            "not_allowed": "does not prove PVT, mismatch/noise yield, continuous multi-cycle SPICE SAR state, extracted layout, area, energy, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Sky130 Thermometer Calibrated Physical SAR", "", f"- status: `{report['status']}`", f"- topology: `{report['topology']}`", f"- source acquisition: `{report['source_acquisition_ns']} ns`", f"- calibration codes measured: `{len(measured)}/{len(calibration_rows)}`", f"- physical comparisons: `{report['measured_comparison_count']}/{report['comparison_count']}`", f"- correct conversions: `{report['correct_conversion_count']}/{report['conversion_count']}`", "", "## Calibration", "", "The thermometer DAC is calibrated at the same source common mode and source-acquisition timing used by the physical comparator trials. Logical SAR trial codes are mapped to the closest measured physical thresholds.", "", "| logical code | physical code | threshold (V) |", "| ---: | ---: | ---: |"]
    for logical, physical in sorted(code_map.items()):
        lines.append(f"| {logical} | {physical} | {thresholds[physical]:.9f} |")
    lines += ["", "## Conversions", "", "| expected code | input V | final code | comparisons | correct |", "| ---: | ---: | ---: | ---: | --- |"]
    for row in conversions:
        lines.append(f"| {row['expected_code']} | {row['input_v']:.6f} | {row['final_code']} | {row['comparison_count']} | {row['correct_code']} |")
    lines += ["", "## Claim Boundary", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"calibration,{report['calibration_measured_count']}/{report['calibration_case_count']}")
    print(f"comparisons,{report['measured_comparison_count']}/{report['comparison_count']}")
    print(f"correct_conversions,{report['correct_conversion_count']}/{report['conversion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
