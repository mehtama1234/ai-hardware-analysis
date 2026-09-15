#!/usr/bin/env python3
"""Join staged error-budget and boundary-intervention receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("error_budget", type=Path)
    parser.add_argument("boundary_interventions", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    budget = json.loads(args.error_budget.read_text(encoding="utf-8"))
    boundary = json.loads(args.boundary_interventions.read_text(encoding="utf-8"))
    modules = budget["target_modules"]
    stages = ("weight_quantization_only", "dac_quantization_only", "adc_quantization_only", "combined_current_profile")
    stage_errors = {stage: {module: budget["configurations"][stage]["module_error"][module]["output_relative_l2"]
                            for module in modules} for stage in stages}
    dominant_by_stage = {stage: max(values, key=values.get) for stage, values in stage_errors.items()}
    boundary_summary = {}
    monotonic_failures = []
    for module in modules:
        row = boundary["results"][module]
        amplitudes = [float(value) for value in boundary["amplitudes"]]
        logits = [row["interventions"][str(value)]["final_logit_relative_l2"] for value in amplitudes]
        boundary_summary[module] = {"calibrated_adc12_output_relative_l2": row["calibrated_adc12_output_relative_l2"],
                                    "amplitudes": amplitudes, "final_logit_relative_l2": logits,
                                    "monotonic": all(left <= right for left, right in zip(logits, logits[1:]))}
        if not boundary_summary[module]["monotonic"]:
            monotonic_failures.append(module)
    output = {
        "schema_version": "gpt2-module-error-decomposition-v0.1",
        "result_type": "local_staged_module_error_decomposition",
        "sources": {"error_budget": {"path": str(args.error_budget), "sha256": digest(args.error_budget)},
                    "boundary_interventions": {"path": str(args.boundary_interventions), "sha256": digest(args.boundary_interventions)},
                    "builder": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}},
        "model_revision": budget["model_revision"], "target_modules": modules,
        "stages": stage_errors, "dominant_module_by_stage": dominant_by_stage,
        "boundary_intervention_summary": boundary_summary,
        "finding": {"dominant_module": dominant_by_stage["combined_current_profile"],
                     "dominant_error_source": max(stages, key=lambda stage: stage_errors[stage][dominant_by_stage["combined_current_profile"]]),
                     "monotonic_boundary_modules": [module for module in modules if module not in monotonic_failures]},
        "decision": "c_proj_boundary_and_adc_resolution_are_the_next_local_targets",
        "analog_authorized": False,
        "claim_boundary": "Local CPU staged error decomposition and perturbation propagation only; no measured hardware latency, energy, silicon yield, or analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "module_error_decomposition_report.json"
    report_path.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        {"path": str(args.error_budget), "sha256": digest(args.error_budget)},
        {"path": str(args.boundary_interventions), "sha256": digest(args.boundary_interventions)},
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "dominant_module": output["finding"]["dominant_module"],
                      "dominant_error_source": output["finding"]["dominant_error_source"]}, sort_keys=True))


if __name__ == "__main__":
    main()
