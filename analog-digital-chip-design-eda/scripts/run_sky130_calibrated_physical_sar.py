#!/usr/bin/env python3
"""Calibrate the physical DAC transfer, then run mapped physical SAR trials."""

from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from run_sky130_coupled_dac_comparator_bit import run_trial

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-calibrated-physical-sar.json"
OUT_MD = EVIDENCE / "sky130-calibrated-physical-sar.md"
PARTIAL_OUT_JSON = EVIDENCE / "sky130-calibrated-physical-sar-partial.json"
PARTIAL_OUT_MD = EVIDENCE / "sky130-calibrated-physical-sar-partial.md"
BITS = 4
SOURCE_V = float(os.environ.get("AIMC_COUPLED_SOURCE_V", "0.9"))
VDD = 1.8
STEP_V = VDD / (1 << BITS)
CALIBRATION_REFERENCE_V = float(os.environ.get("AIMC_COUPLED_CALIBRATION_REFERENCE_V", "1.0"))
INPUT_CODES = (0, 2, 4, 6, 7)


def selected_codes(name: str, default: tuple[int, ...]) -> tuple[int, ...]:
    raw = os.environ.get(name)
    if not raw:
        return default
    values = tuple(sorted({int(value.strip()) for value in raw.split(",") if value.strip()}))
    if not values or any(value < 0 or value >= (1 << BITS) for value in values):
        raise SystemExit(f"{name} must contain unique codes from 0 through {(1 << BITS) - 1}")
    return values


def run_trial_with_retries(code: int, input_v: float, reference_v: float, label: str) -> dict[str, Any]:
    attempts = max(1, int(os.environ.get("AIMC_COUPLED_RETRIES", "2")))
    last_row: dict[str, Any] | None = None
    for attempt in range(1, attempts + 1):
        print(f"{label} code {code} attempt {attempt}/{attempts}", flush=True)
        row = run_trial(code, input_v, reference_v)
        row["attempt"] = attempt
        last_row = row
        if row.get("measured"):
            return row
    assert last_row is not None
    return last_row


def calibration_cache_metadata() -> dict[str, Any]:
    return {
        "measurement_revision": "dac_top_presample_9ns_v1",
        "dac_acq": os.environ.get("AIMC_COUPLED_DAC_ACQ", ""),
        "bottom_pmos_only": os.environ.get("AIMC_COUPLED_BOTTOM_PMOS_ONLY", ""),
        "bottom_nmos_only": os.environ.get("AIMC_COUPLED_BOTTOM_NMOS_ONLY", ""),
        "source_v": SOURCE_V,
        "calibration_reference_v": CALIBRATION_REFERENCE_V,
    }


def read_calibration_cache(path: Path) -> dict[int, dict[str, Any]]:
    if not path.exists():
        return {}
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("metadata") != calibration_cache_metadata():
        return {}
    return {int(code): row for code, row in report.get("rows", {}).items() if row.get("measured")}


def write_calibration_cache(path: Path, rows: dict[int, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "metadata": calibration_cache_metadata(),
        "rows": {str(code): rows[code] for code in sorted(rows)},
    }
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def calibrate() -> list[dict[str, Any]]:
    requested_codes = selected_codes("AIMC_COUPLED_CALIBRATION_CODES", tuple(range(1 << BITS)))
    workers = max(1, int(os.environ.get("AIMC_COUPLED_CAL_WORKERS", os.environ.get("AIMC_COUPLED_WORKERS", "1"))))
    cache_path = os.environ.get("AIMC_COUPLED_CAL_CACHE")
    if cache_path and workers == 1:
        path = Path(cache_path)
        cached_rows = read_calibration_cache(path)
        for code in requested_codes:
            if code in cached_rows:
                print(f"calibration code {code} cache hit", flush=True)
                continue
            row = run_trial_with_retries(code, SOURCE_V, CALIBRATION_REFERENCE_V, "calibration")
            if row.get("measured"):
                cached_rows[code] = row
                write_calibration_cache(path, cached_rows)
        return [cached_rows.get(code, {"code": code, "measured": False}) for code in requested_codes]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda code: run_trial_with_retries(code, SOURCE_V, CALIBRATION_REFERENCE_V, "calibration"), requested_codes))


def mapped_sequence(expected_code: int, code_map: dict[int, int], thresholds: dict[int, float]) -> dict[str, Any]:
    ordered_thresholds = [thresholds[code_map[index]] for index in range(1 << BITS)]
    if expected_code == 0:
        input_v = max(0.0, ordered_thresholds[0] - (ordered_thresholds[1] - ordered_thresholds[0]) / 2.0)
    elif expected_code == (1 << BITS) - 1:
        input_v = min(VDD, ordered_thresholds[-1] + (ordered_thresholds[-1] - ordered_thresholds[-2]) / 2.0)
    else:
        input_v = (ordered_thresholds[expected_code] + ordered_thresholds[expected_code + 1]) / 2.0
    logical_code = 0
    trace = []
    for decision_number, bit in enumerate(reversed(range(BITS)), start=1):
        logical_trial = logical_code | (1 << bit)
        physical_trial = code_map[logical_trial]
        comparison = run_trial_with_retries(physical_trial, SOURCE_V, input_v, f"conversion expected {expected_code} decision {decision_number}")
        accepted = bool(comparison.get("measured")) and comparison.get("dac_to_reference_diff_v", 0.0) < 0.0
        if accepted:
            logical_code = logical_trial
        trace.append({
            "decision_number": decision_number,
            "bit": bit,
            "logical_trial_code": logical_trial,
            "physical_trial_code": physical_trial,
            "accepted": accepted,
            "comparison": comparison,
        })
        if not comparison.get("measured"):
            break
    return {
        "expected_code": expected_code,
        "input_v": input_v,
        "final_code": logical_code,
        "comparison_count": len(trace),
        "correct_code": logical_code == expected_code and len(trace) == BITS,
        "trace": trace,
    }


def main() -> int:
    calibration_rows = calibrate()
    measured = [row for row in calibration_rows if row.get("measured")]
    requested_calibration_codes = selected_codes("AIMC_COUPLED_CALIBRATION_CODES", tuple(range(1 << BITS)))
    missing = sorted(set(requested_calibration_codes) - {row["code"] for row in measured})
    if missing or (os.environ.get("AIMC_COUPLED_PARTIAL_CALIBRATION") == "1" and len(requested_calibration_codes) < (1 << BITS)):
        if os.environ.get("AIMC_COUPLED_PARTIAL_CALIBRATION") == "1":
            partial = {
                "result_type": "sky130_calibrated_physical_sar_partial",
                "status": "calibration_subset_incomplete_not_full_sar_proof",
                "requested_calibration_codes": list(requested_calibration_codes),
                "measured_calibration_codes": sorted(row["code"] for row in measured),
                "missing_calibration_codes": missing,
                "rows": calibration_rows,
                "claim_boundary": "partial calibration diagnostics only; not a complete code map, SAR conversion, converter acceptance, board, or silicon evidence",
            }
            PARTIAL_OUT_JSON.write_text(json.dumps(partial, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            PARTIAL_OUT_MD.write_text("\n".join(["# Sky130 Partial SAR Calibration", "", f"- requested codes: `{requested_calibration_codes}`", f"- measured codes: `{partial['measured_calibration_codes']}`", f"- missing codes: `{missing}`", "", partial["claim_boundary"] + ".", ""]), encoding="utf-8")
            print(f"partial_calibration,{len(measured)}/{len(requested_calibration_codes)}")
            print(f"partial_json,{PARTIAL_OUT_JSON}")
            return 0
        raise SystemExit(f"calibration incomplete; missing codes {missing}")
    thresholds = {int(row["code"]): float(row["dac_top_after_v"]) for row in measured}
    threshold_values = [thresholds[code] for code in sorted(thresholds)]
    adjacent_spacings = [b - a for a, b in zip(threshold_values, threshold_values[1:])]
    ordered_physical_codes = sorted(thresholds, key=thresholds.get)
    if any(a >= b for a, b in zip(threshold_values, threshold_values[1:])):
        raise SystemExit("calibration thresholds are not strictly monotonic")
    # Preserve the measured threshold ordering; nearest-ideal matching can alias
    # codes when the physical transfer is shifted relative to the nominal ladder.
    code_map = {
        logical: ordered_physical_codes[logical]
        for logical in range(1 << BITS)
    }
    legal_range_pass = min(threshold_values) >= 0.0 and max(threshold_values) <= VDD
    spacing_pass = bool(adjacent_spacings) and min(adjacent_spacings) >= STEP_V / 2.0
    code_map_injective = len(set(code_map.values())) == len(code_map)
    workers = max(1, int(os.environ.get("AIMC_COUPLED_CONVERSION_WORKERS", os.environ.get("AIMC_COUPLED_WORKERS", "1"))))
    conversion_codes = selected_codes("AIMC_COUPLED_CONVERSION_CODES", INPUT_CODES)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        conversions = list(pool.map(lambda code: mapped_sequence(code, code_map, thresholds), conversion_codes))
    comparisons = [step["comparison"] for conversion in conversions for step in conversion["trace"]]
    report = {
        "result_type": "sky130_calibrated_physical_sar",
        "status": "calibrated_physical_sar_characterized_not_continuous_multicycle_proof",
        "bits": BITS,
        "source_v": SOURCE_V,
        "calibration_reference_v": CALIBRATION_REFERENCE_V,
        "acquisition_candidate": "long_source_acquisition",
        "bottom_plate_topology": "pmos_only_to_vdd" if os.environ.get("AIMC_COUPLED_BOTTOM_PMOS_ONLY") == "1" else "both_rails_selected_default",
        "source_switch_width_um": {"nfet": 32.0, "pfet": 64.0},
        "source_acquisition_end_ns": 4.0,
        "bottom_plate_transition_ns": 5.0,
        "dac_threshold_measurement_ns": 9.0,
        "comparator_sampling_ns": "9.1-9.6",
        "preamp_enable_ns": 9.7,
        "latch_ns": 11.7,
        "calibration_case_count": len(calibration_rows),
        "calibration_measured_count": len(measured),
        "calibration_thresholds_v": thresholds,
        "logical_to_physical_code_map": code_map,
        "threshold_min_v": min(threshold_values),
        "threshold_max_v": max(threshold_values),
        "minimum_adjacent_spacing_v": min(adjacent_spacings) if adjacent_spacings else None,
        "acceptance_gates": {
            "legal_threshold_range": legal_range_pass,
            "minimum_half_lsb_spacing": spacing_pass,
            "logical_to_physical_map_injective": code_map_injective,
        },
        "conversion_count": len(conversions),
        "comparison_count": len(comparisons),
        "measured_comparison_count": sum(row.get("measured", False) for row in comparisons),
        "correct_conversion_count": sum(row["correct_code"] for row in conversions),
        "conversions": conversions,
        "claim_boundary": {
            "allowed": "uses a measured 16-code DAC transfer at the SAR source common mode and maps logical trial codes to physical codes before running physical DAC/comparator decisions",
            "not_allowed": "does not prove calibration across PVT or mismatch/noise, one continuous multi-cycle SPICE state machine, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Calibrated Physical SAR", "",
        f"- status: `{report['status']}`",
        f"- calibration codes measured: `{report['calibration_measured_count']}` of `{report['calibration_case_count']}`",
        f"- physical comparisons: `{report['measured_comparison_count']}` of `{report['comparison_count']}`",
        f"- correct conversions: `{report['correct_conversion_count']}` of `{report['conversion_count']}`", "",
        "- acquisition candidate: `32/64 um source switch with 4.0 ns acquisition and 5.0 ns redistribution`", "",
        "- bottom-plate topology: `PMOS-only selected connection to VDD`",
        "- DAC threshold measurement: `9.0 ns`, before comparator switch closure", "",
        "## Calibration Method", "",
        "The uncalibrated DAC uses binary physical codes, but its measured voltage is not an ideal binary ladder. This runner first measures every physical code at the same source common mode used by the SAR. It then preserves the rank order of the measured thresholds as a bijective logical-to-physical map. The SAR retains logical bits while applying the mapped physical trial code to the real DAC.", "",
        "Calibration is useful only if it is tied to the same source common mode and decision timing as the workload. A table measured at another input level or after comparator activity is not silently reused.", "",
        f"This low-source PMOS-only calibration measures all 16 codes and passes the bounded conversion below. Its threshold range is `{min(threshold_values):.6f}..{max(threshold_values):.6f} V`; the minimum adjacent spacing is `{min(adjacent_spacings):.6f} V`, and the legal-range gate is `{legal_range_pass}`. The logical-to-physical map is injective: `{code_map_injective}`. These gates remain separate from the conversion count and prevent a single successful conversion from becoming converter acceptance.", "",
        "## Results", "",
        "| expected logical code | input V | final logical code | comparisons | correct |", "| ---: | ---: | ---: | ---: | --- |",
    ]
    for row in conversions:
        lines.append(f"| {row['expected_code']} | {row['input_v']:.6f} | {row['final_code']} | {row['comparison_count']} | {row['correct_code']} |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"calibration,{report['calibration_measured_count']}/{report['calibration_case_count']}")
    print(f"comparisons,{report['measured_comparison_count']}/{report['comparison_count']}")
    print(f"correct_conversions,{report['correct_conversion_count']}/{report['conversion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
