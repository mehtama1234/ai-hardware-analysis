#!/usr/bin/env python3
"""Compute a guarded projection cost model from workload counts and coefficients."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = ("DAC_pJ_per_conversion", "ADC_pJ_per_conversion", "array_pJ_per_evaluation",
            "digital_add_pJ", "boundary_pJ_per_byte", "same_target_digital_projection_pJ")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--coefficients", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    trace = json.loads(args.trace.read_text())
    totals = trace["totals"]
    coefficients = json.loads(args.coefficients.read_text()) if args.coefficients else {}
    missing = [key for key in REQUIRED if key not in coefficients]
    cost = None
    if not missing:
        if any(float(coefficients[key]) < 0 for key in REQUIRED):
            raise SystemExit("cost coefficients must be nonnegative")
        cost = {
            "DAC_pJ": totals["dac_conversions"] * float(coefficients["DAC_pJ_per_conversion"]),
            "ADC_pJ": totals["adc_conversions"] * float(coefficients["ADC_pJ_per_conversion"]),
            "array_pJ": totals["array_evaluations"] * float(coefficients["array_pJ_per_evaluation"]),
            "digital_add_pJ": totals["digital_partial_sum_additions"] * float(coefficients["digital_add_pJ"]),
            "boundary_pJ": (totals["boundary_input_bytes_fp32"] + totals["boundary_output_bytes_fp32"]) * float(coefficients["boundary_pJ_per_byte"]),
        }
        cost["projection_total_pJ"] = sum(cost.values())
        cost["digital_baseline_pJ"] = float(coefficients["same_target_digital_projection_pJ"])
        cost["break_even"] = cost["projection_total_pJ"] < cost["digital_baseline_pJ"]
    result = {
        "schema_version": "projection-cost-model-v0.1",
        "result_type": "guarded_projection_energy_cost_model",
        "source_trace": str(args.trace),
        "workload_totals": totals,
        "coefficients": coefficients,
        "missing_coefficients": missing,
        "status": "computed" if cost is not None else "missing_matched_cost_coefficients",
        "cost": cost,
        "required_measurements": REQUIRED,
        "claim_boundary": "Parameterized operation-cost accounting only. Without matched coefficients this artifact makes no energy claim; with coefficients it remains scoped to the stated GPT-2 projection boundary.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "status": result["status"], "missing": len(missing)}))


if __name__ == "__main__":
    main()
