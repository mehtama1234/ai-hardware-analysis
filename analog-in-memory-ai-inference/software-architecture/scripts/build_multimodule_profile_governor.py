#!/usr/bin/env python3
"""Build a fail-closed profile-aware governor from local route evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sensitivity_report", type=Path)
    parser.add_argument("attribution_report", type=Path)
    parser.add_argument("cost_trace", type=Path)
    parser.add_argument("stress_report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sensitivity_path = args.sensitivity_report.resolve()
    attribution_path = args.attribution_report.resolve()
    cost_path = args.cost_trace.resolve()
    stress_path = args.stress_report.resolve()
    sensitivity = json.loads(sensitivity_path.read_text(encoding="utf-8"))
    attribution = json.loads(attribution_path.read_text(encoding="utf-8"))
    cost_rows = [json.loads(line) for line in cost_path.read_text(encoding="utf-8").splitlines() if line]
    stress = json.loads(stress_path.read_text(encoding="utf-8"))
    threshold = {"minimum_teacher_forced_argmax_agreement": 0.99,
                 "maximum_nll_increase_nats": 0.05,
                 "maximum_module_output_relative_l2": 0.03,
                 "maximum_final_logit_relative_l2": 0.002}
    attribution_scenarios = attribution["scenarios"]
    candidates = []
    for row in sensitivity["results"]:
        candidate = {
            "analog_modules": row["selected_modules"],
            "digital_modules": [name for name in sensitivity["target_modules"] if name not in row["selected_modules"]],
            "adc_bits": row["adc_bits"],
            "activation_bound_multiplier": row["activation_bound_multiplier"],
            "calibrated": row["calibrated"],
            "teacher_forced_argmax_agreement": row["quality"]["teacher_forced_argmax_agreement"],
            "nll_increase_nats": row["quality"]["nll_increase_nats"],
            "generation_exact_match_count": row["quality"]["generation_exact_match_count"],
            "screen_pass": row["screen_pass"],
        }
        matching = next((value for value in attribution_scenarios.values()
                         if value["analog_modules"] == row["selected_modules"]), None)
        stress_matching = next((value for value in stress["results"].values()
                                if value["analog_modules"] == row["selected_modules"]), None)
        if matching is None:
            candidate["propagation_guard_pass"] = False
            candidate["propagation_guard_reason"] = "no matching boundary attribution receipt"
        else:
            output_error = max(matching["metrics"]["modules"][name]["output_relative_l2"]
                               for name in row["selected_modules"])
            logit_error = matching["metrics"]["final_logit_relative_l2"]
            candidate["propagation_guard_pass"] = (output_error <= threshold["maximum_module_output_relative_l2"]
                                                    and logit_error <= threshold["maximum_final_logit_relative_l2"])
            candidate["propagation_guard_metrics"] = {"maximum_module_output_relative_l2": output_error,
                                                        "final_logit_relative_l2": logit_error}
            candidate["propagation_guard_reason"] = "within boundary limits" if candidate["propagation_guard_pass"] else "boundary propagation limit exceeded"
        candidate["stress_screen_pass"] = bool(stress_matching and stress_matching["screen_pass"])
        candidate["governance_pass"] = (candidate["screen_pass"] and candidate["propagation_guard_pass"]
                                         and candidate["stress_screen_pass"])
        if not candidate["stress_screen_pass"]:
            candidate["governance_rejection_reason"] = "disjoint stress screen failed or has no matching receipt"
        candidates.append(candidate)
    passing = [row for row in candidates if row["governance_pass"] and len(row["analog_modules"]) > 0]
    # Maximize analog coverage, then prefer the lower-NLL route.
    selected = max(passing, key=lambda row: (len(row["analog_modules"]),
                                               -row["nll_increase_nats"]), default=None)
    if selected is None:
        selected = {
            "analog_modules": [], "digital_modules": sensitivity["target_modules"],
            "adc_bits": None, "activation_bound_multiplier": None, "calibrated": False,
            "teacher_forced_argmax_agreement": None, "nll_increase_nats": None,
            "generation_exact_match_count": None, "screen_pass": False,
        }
    attribution_modules = attribution["scenarios"]["full_three_module"]["metrics"]["modules"]
    enforced = {
        "route": "digital_fallback",
        "module_routes": {name: "digital_fallback" for name in sensitivity["target_modules"]},
        "reason": "analog authorization gate is closed even when a numerical candidate passes",
        "analog_authorized": False,
    }
    events = []
    for vector_id in range(len(sensitivity["evaluation_split"])):
        events.append({
            "evaluation_id": vector_id,
            "candidate_count": len(candidates),
            "recommended_analog_modules": selected["analog_modules"],
            "recommended_digital_modules": selected["digital_modules"],
            "enforced_route": enforced["route"],
            "command": "RUN_DIGITAL_FALLBACK",
            "analog_authorized": False,
            "fallback_reason": enforced["reason"],
        })
    route_cost_rows = []
    for row in cost_rows:
        route_cost_rows.append({
            "vector_id": row["vector_id"],
            "recommended_analog_modules": selected["analog_modules"],
            "enforced_route": enforced["route"],
            "digital_reference_cost_pj": row["digital_reference_cost_pj"],
            "counterfactual_hybrid_cost_pj": row["counterfactual_hybrid_cost_pj"],
            "enforced_route_cost_pj": row["enforced_route_cost_pj"],
            "analog_authorized": False,
            "claim_boundary": "Per-vector modeled operation-count costs; coefficients are not measured energy.",
        })
    report = {
        "schema_version": "gpt2-multimodule-profile-governor-v0.1",
        "result_type": "local_profile_aware_multi_module_governor",
        "sources": {"sensitivity": {"path": str(sensitivity_path), "sha256": digest(sensitivity_path)},
                    "attribution": {"path": str(attribution_path), "sha256": digest(attribution_path)},
                    "cost_trace": {"path": str(cost_path), "sha256": digest(cost_path)},
                    "stress": {"path": str(stress_path), "sha256": digest(stress_path)}},
        "target_modules": sensitivity["target_modules"], "quality_threshold": threshold,
        "candidate_routes": candidates,
        "recommended_policy": selected,
        "enforced_policy": enforced,
        "diagnostic_context": {
            "full_route_module_output_errors": {name: row["output_relative_l2"] for name, row in attribution_modules.items()},
            "full_route_final_logit_relative_l2": attribution["scenarios"]["full_three_module"]["metrics"]["final_logit_relative_l2"],
            "interaction_ratio": attribution["interaction_summary"]["full_to_isolated_sum_ratio"],
        },
        "trace": events,
        "decision": "full_digital_fallback",
        "analog_authorized": False,
        "claim_boundary": "Local CPU governor decision only; route quality is fixture-scoped and no hardware latency, energy, silicon, or analog authorization is claimed.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "profile_governor_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    route_cost_path = args.output / "route_cost_trace.jsonl"
    route_cost_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in route_cost_rows), encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        {"path": str(sensitivity_path), "sha256": digest(sensitivity_path)},
        {"path": str(attribution_path), "sha256": digest(attribution_path)},
        {"path": str(cost_path), "sha256": digest(cost_path)},
        {"path": str(stress_path), "sha256": digest(stress_path)},
        {"path": str(route_cost_path), "sha256": digest(route_cost_path)},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "candidate_routes": len(candidates),
                      "decision": report["decision"], "analog_authorized": False}, sort_keys=True))


if __name__ == "__main__":
    main()
