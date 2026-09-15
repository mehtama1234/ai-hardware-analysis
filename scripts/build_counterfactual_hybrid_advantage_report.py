#!/usr/bin/env python3
"""Quantify modeled hybrid-vs-digital tradeoffs without claiming measurements."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, default=Path("evidence/local-digital-qualification-v1"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    package = json.loads((args.package / "local_digital_qualification_package.json").read_text())
    sources = package["sources"]
    cost_path = Path(sources["local_multimodule_cost_trace"]["path"])
    runtime_path = Path(sources["local_multimodule_runtime_trace"]["path"])
    error_path = Path(sources["local_module_error_decomposition"]["path"])
    if sha256(cost_path) != sources["local_multimodule_cost_trace"]["sha256"]:
        raise SystemExit("cost trace hash mismatch")
    if sha256(runtime_path) != sources["local_multimodule_runtime_trace"]["sha256"]:
        raise SystemExit("runtime trace hash mismatch")
    if sha256(error_path) != sources["local_module_error_decomposition"]["sha256"]:
        raise SystemExit("error decomposition hash mismatch")
    costs = [json.loads(line) for line in cost_path.read_text().splitlines() if line.strip()]
    runtime = json.loads(runtime_path.read_text())
    error = json.loads(error_path.read_text())
    if len(costs) != 162 or len(runtime["events"]) != 162:
        raise SystemExit("expected 162-vector ledgers")
    totals = {key: sum(float(row[key]) for row in costs) for key in (
        "digital_reference_cost_pj", "counterfactual_hybrid_cost_pj", "enforced_route_cost_pj",
        "digital_reference_cycles", "counterfactual_hybrid_cycles")}
    totals["modeled_cost_reduction_fraction"] = 1.0 - totals["counterfactual_hybrid_cost_pj"] / totals["digital_reference_cost_pj"]
    totals["modeled_cycle_reduction_fraction"] = 1.0 - totals["counterfactual_hybrid_cycles"] / totals["digital_reference_cycles"]
    coefficients = {"analog_array_evaluations": 0, "digital_partial_sum_additions": 0,
                    "converter_conversions": 0, "boundary_bytes": 0}
    for event in runtime["events"]:
        for module in event["modules"]:
            op = module["operation_counts"]
            coefficients["analog_array_evaluations"] += op["array_evaluations"]
            coefficients["digital_partial_sum_additions"] += op["digital_partial_sum_additions"]
            coefficients["converter_conversions"] += op["dac_conversions_without_column_tile_broadcast"] + op["adc_conversions_after_differential_subtraction"]
            coefficients["boundary_bytes"] += op["boundary_input_bytes_fp32"] + op["boundary_output_bytes_fp32"]
    scenarios = []
    for array_pj in (0.3, 0.6, 1.2):
        for converter_pj in (1.0, 2.0, 4.0, 8.0):
            hybrid = (coefficients["analog_array_evaluations"] * array_pj
                      + coefficients["digital_partial_sum_additions"] * 3.0
                      + coefficients["converter_conversions"] * converter_pj
                      + coefficients["boundary_bytes"] * 0.2)
            scenarios.append({"analog_array_pj": array_pj, "converter_pj": converter_pj,
                              "modeled_hybrid_cost_pj": hybrid,
                              "beats_digital_reference": hybrid < totals["digital_reference_cost_pj"]})
    break_even_converter_pj = (totals["digital_reference_cost_pj"]
                               - coefficients["analog_array_evaluations"] * 0.6
                               - coefficients["digital_partial_sum_additions"] * 3.0
                               - coefficients["boundary_bytes"] * 0.2) / coefficients["converter_conversions"]
    output = {
        "schema_version": "counterfactual-hybrid-advantage-report-v0.1",
        "result_type": "local_counterfactual_hybrid_vs_digital_model",
        "decision": "unresolved_counterfactual_only",
        "analog_authorized": False,
        "workload_vectors": 162,
        "target_modules": package["target_modules"],
        "modeled_totals": totals,
        "operation_coefficients": coefficients,
        "break_even": {"converter_pj_at_array_0.6": break_even_converter_pj,
                        "interpretation": "hybrid cost is below the modeled digital reference only under assumptions below this converter cost, with all other coefficients held fixed"},
        "quality_risk": {
            "promotion_gate_open": False,
            "dominant_module": error["finding"]["dominant_module"],
            "dominant_error_source": error["finding"]["dominant_error_source"],
            "combined_profile_relative_l2_by_module": error["stages"]["combined_current_profile"],
            "boundary_logit_relative_l2_at_amplitude_1": {
                module: values["final_logit_relative_l2"][2]
                for module, values in error["boundary_intervention_summary"].items()
            },
            "interpretation": "modeled cost advantage is not actionable unless the converter/error quality gate also passes",
        },
        "sensitivity": scenarios,
        "enforced_route": "digital_fallback",
        "sources": {"digital_package": {"path": str(args.package.resolve() / "local_digital_qualification_package.json"), "sha256": sha256(args.package.resolve() / "local_digital_qualification_package.json")},
                    "cost_trace": {"path": str(cost_path), "sha256": sha256(cost_path)},
                    "runtime_trace": {"path": str(runtime_path), "sha256": sha256(runtime_path)},
                    "error_decomposition": {"path": str(error_path), "sha256": sha256(error_path)}},
        "claim_boundary": "Counterfactual operation-count and coefficient sensitivity model only; pJ/cycle values are assumptions, not measured energy, latency, analog execution, silicon yield, or production evidence.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    path = args.output / "counterfactual_hybrid_advantage_report.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    (args.output / "README.md").write_text("# Counterfactual hybrid advantage\n\nThe report compares modeled hybrid operation costs with the digital reference across explicit coefficient sensitivities. It is not a hardware or energy measurement, and analog authorization remains false.\n")
    print(json.dumps({"output": str(path), "modeled_cost_reduction_fraction": totals["modeled_cost_reduction_fraction"], "analog_authorized": False}, sort_keys=True))


if __name__ == "__main__":
    main()
