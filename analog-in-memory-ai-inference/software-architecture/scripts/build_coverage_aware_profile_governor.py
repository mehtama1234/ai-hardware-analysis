#!/usr/bin/env python3
"""Bind activation coverage to a fail-closed stateful route governor."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stateful_governor", type=Path)
    parser.add_argument("cost_trace", type=Path)
    parser.add_argument("coverage_report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    governor = json.loads(args.stateful_governor.read_text(encoding="utf-8"))
    coverage = json.loads(args.coverage_report.read_text(encoding="utf-8"))
    cost_rows = [json.loads(line) for line in args.cost_trace.read_text(encoding="utf-8").splitlines() if line]
    modules = coverage["target_modules"]
    ratios = coverage["coverage_ratios"]
    out_of_envelope = {
        module: {context: values for context, values in module_ratios.items()
                 if values["context_max_over_calibration_max"] > 1.0
                 or values["context_p99_over_calibration_p99"] > 1.0}
        for module, module_ratios in ratios.items()
    }
    out_of_envelope = {module: contexts for module, contexts in out_of_envelope.items() if contexts}
    enforced = {
        "route": "digital_fallback",
        "module_routes": {module: "digital_fallback" for module in modules},
        "reason": "activation coverage leaves the retained calibration envelope; physical analog authorization is also closed",
        "analog_authorized": False,
    }
    trace = [{
        "vector_id": row["vector_id"],
        "candidate_profile": "stateful_previous_token",
        "coverage_gate": "out_of_envelope_contexts_force_fallback",
        "enforced_route": enforced["route"],
        "command": "RUN_DIGITAL_FALLBACK",
        "digital_reference_cost_pj": row["digital_reference_cost_pj"],
        "counterfactual_hybrid_cost_pj": row["counterfactual_hybrid_cost_pj"],
        "enforced_route_cost_pj": row["enforced_route_cost_pj"],
        "analog_authorized": False,
    } for row in cost_rows]
    if "numerical_candidate" in governor:
        candidate = governor["numerical_candidate"]
    else:
        candidate = {
            "profile": governor["results"]["stateful_previous_token_stress"]["profile"],
            "route": "full_three_module",
            "original_screen_pass": governor["results"]["stateful_previous_token_original"]["quality"]["screen_pass"],
            "stress_screen_pass": governor["results"]["stateful_previous_token_stress"]["quality"]["screen_pass"],
            "third_holdout_screen_pass": governor["results"].get("stateful_previous_token_third_holdout", {}).get("quality", {}).get("screen_pass"),
            "quality": {name: row["quality"] for name, row in governor["results"].items()},
            "method": "previous provisional output row correction",
        }
    output = {
        "schema_version": "gpt2-coverage-aware-profile-governor-v0.1",
        "result_type": "local_activation_coverage_aware_profile_governor",
        "source_stateful_governor": {"path": str(args.stateful_governor), "sha256": digest(args.stateful_governor)},
        "source_cost_trace": {"path": str(args.cost_trace), "sha256": digest(args.cost_trace)},
        "source_activation_coverage": {"path": str(args.coverage_report), "sha256": digest(args.coverage_report)},
        "target_modules": modules,
        "coverage_gate": {"threshold": 1.0, "out_of_envelope": out_of_envelope,
                           "pass": not bool(out_of_envelope)},
        "inherited_numerical_candidate": candidate,
        "enforced_policy": enforced,
        "route_trace": trace,
        "decision": "coverage_out_of_envelope_full_digital_fallback",
        "analog_authorized": False,
        "claim_boundary": "Local CPU activation coverage governance only; no measured hardware latency, energy, silicon yield, or analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    output_path = args.output / "coverage_aware_profile_governor.json"
    output_path.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    trace_path = args.output / "coverage_aware_route_cost_trace.jsonl"
    trace_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in trace), encoding="utf-8")
    manifest = {"files": [
        {"path": str(output_path), "sha256": digest(output_path)},
        {"path": str(trace_path), "sha256": digest(trace_path)},
        {"path": str(args.stateful_governor), "sha256": digest(args.stateful_governor)},
        {"path": str(args.cost_trace), "sha256": digest(args.cost_trace)},
        {"path": str(args.coverage_report), "sha256": digest(args.coverage_report)},
    ]}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output_path), "trace_rows": len(trace),
                      "out_of_envelope_modules": sorted(out_of_envelope), "analog_authorized": False}, sort_keys=True))


if __name__ == "__main__":
    main()
