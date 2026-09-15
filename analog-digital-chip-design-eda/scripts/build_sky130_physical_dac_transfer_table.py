#!/usr/bin/env python3
"""Build a measured transfer table from the physical Sky130 DAC sweep."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
DEFAULT_SOURCE = EVIDENCE / "sky130-coupled-dac-comparator-bit-source09.json"
DEFAULT_OUTPUT = EVIDENCE / "sky130-physical-dac-transfer-table.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source_path = args.source.resolve()
    output_path = args.output.resolve()
    source = json.loads(source_path.read_text(encoding="utf-8"))
    rows = sorted(source["rows"], key=lambda row: int(row["code"]))
    expected_codes = list(range(16))
    codes = [int(row["code"]) for row in rows]
    measured = all(row.get("measured") for row in rows)
    complete = codes == expected_codes and len(rows) == 16
    source_v = {round(float(row["dac_source_v"]), 9) for row in rows}
    top_values = [float(row["dac_top_after_v"]) for row in rows]
    increments = [top_values[index + 1] - top_values[index] for index in range(len(top_values) - 1)]
    monotonic = all(increment > 0.0 for increment in increments)
    supply_v = 1.8
    first_over_supply = next((code for code, value in zip(codes, top_values) if value > supply_v), None)
    endpoint_lsb = (top_values[-1] - top_values[0]) / 15.0 if complete else None
    ideal = [top_values[0] + endpoint_lsb * code for code in codes] if endpoint_lsb is not None else []
    max_endpoint_linearity_error = max((abs(actual - target) for actual, target in zip(top_values, ideal)), default=None)
    table = [
        {
            "code": code,
            "dac_top_after_v": value,
            "dac_to_reference_diff_v": float(row["dac_to_reference_diff_v"]),
            "measured_output_sign": int(row["measured_output_sign"]),
            "correct_polarity": bool(row["correct_polarity"]),
        }
        for code, value, row in zip(codes, top_values, rows)
    ]
    if complete and measured and monotonic:
        transfer_status = "physical_dac_transfer_complete_monotonic_in_range" if first_over_supply is None else "physical_dac_transfer_complete_monotonic_range_exceeds_supply"
    else:
        transfer_status = "physical_dac_transfer_incomplete_or_nonmonotonic"
    report: dict[str, Any] = {
        "result_type": "sky130_physical_dac_transfer_table",
        "status": transfer_status,
        "source_report": str(source_path.relative_to(ROOT)) if source_path.is_relative_to(ROOT) else str(source_path),
        "source_sha256": digest(source_path),
        "dac_source_v": sorted(source_v),
        "supply_v": supply_v,
        "code_count": len(rows),
        "codes_complete": complete,
        "all_trials_measured": measured,
        "monotonic": monotonic,
        "first_code_over_supply": first_over_supply,
        "maximum_dac_top_v": max(top_values, default=None),
        "minimum_dac_top_v": min(top_values, default=None),
        "endpoint_lsb_v": endpoint_lsb,
        "maximum_endpoint_linearity_error_v": max_endpoint_linearity_error,
        "increments_v": increments,
        "table": table,
        "repair_contract": "Redesign or calibrate the DAC so every declared code remains within the analog supply range and the SAR threshold contract is bound to this measured transfer, then repeat the 16-code sequence.",
        "claim_boundary": "Complete nominal physical DAC top-plate transfer characterization only; does not prove calibrated SAR accuracy, continuous multi-cycle state retention, PVT, mismatch/noise yield, energy, layout LVS, board behavior, or silicon.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "codes": len(rows), "first_code_over_supply": first_over_supply, "output": str(output_path)}))
    return 0 if report["status"].startswith("physical_dac_transfer_complete") else 1


if __name__ == "__main__":
    raise SystemExit(main())
