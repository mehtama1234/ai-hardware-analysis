#!/usr/bin/env python3
"""Sweep synthetic projection error and seeds for the tiny causal-LM gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from run_tiny_causal_lm_decode import load_gate, run


ROOT = Path(__file__).resolve().parents[1]


def run_sweep(
    model_path: Path,
    prompt: list[int],
    generated_steps: int,
    error_scales: list[float],
    seeds: list[int],
    target_profile: str,
    calibration_profile: str,
    physical_gate: dict[str, Any] | None = None,
    enforce_physical_gate: bool = False,
) -> dict[str, Any]:
    cases = []
    for error_scale in error_scales:
        for seed in seeds:
            result = run(
                model_path,
                prompt,
                generated_steps,
                error_scale,
                seed,
                target_profile,
                calibration_profile,
                physical_gate,
                enforce_physical_gate,
            )
            cases.append(
                {
                    "error_scale": error_scale,
                    "seed": seed,
                    "passed": result["acceptance"]["passed"],
                    "teacher_forced_next_token_agreement_rate": result["summary"]["teacher_forced_next_token_agreement_rate"],
                    "teacher_forced_max_relative_l2_error": result["summary"]["teacher_forced_max_relative_l2_error"],
                    "free_running_generated_token_agreement_rate": result["summary"]["free_running_generated_token_agreement_rate"],
                    "free_running_exact_sequence_agreement": result["summary"]["free_running_exact_sequence_agreement"],
                    "prefill_reference_relative_l2_error": result["summary"]["prefill_reference_relative_l2_error"],
                    "analog_candidate_count": result["contract"]["analog_candidate_count"],
                }
            )
    total = len(cases)
    return {
        "schema_version": "tiny-causal-lm-reliability-sweep-v0.1",
        "result_type": "synthetic_projection_error_reliability_sweep",
        "provenance": {
            "model": model_path.name,
            "prompt_token_ids": prompt,
            "generated_steps": generated_steps,
            "error_scales": error_scales,
            "seeds": seeds,
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
            "physical_gate_enforced": enforce_physical_gate,
        },
        "cases": cases,
        "summary": {
            "case_count": total,
            "passed_case_count": sum(int(case["passed"]) for case in cases),
            "acceptance_rate": sum(int(case["passed"]) for case in cases) / max(total, 1),
            "mean_teacher_forced_token_agreement_rate": sum(case["teacher_forced_next_token_agreement_rate"] for case in cases) / max(total, 1),
            "minimum_free_running_token_agreement_rate": min(case["free_running_generated_token_agreement_rate"] for case in cases),
            "exact_free_running_sequence_rate": sum(case["free_running_exact_sequence_agreement"] for case in cases) / max(total, 1),
            "worst_teacher_forced_relative_l2_error": max(case["teacher_forced_max_relative_l2_error"] for case in cases),
            "prefill_oracle_passed": all(case["prefill_reference_relative_l2_error"] <= 1e-5 for case in cases),
        },
        "claim_boundary": {
            "allowed": "Seeded software sensitivity distribution for the checked-in tiny causal-LM fixture.",
            "refused": "This is not process/mismatch/PVT silicon data, measured converter calibration, or a production workload distribution.",
            "next_gate": "Replace error_scale with measured per-tile distributions indexed by voltage, temperature, age, and calibration state.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "samples" / "tiny-causal-lm.onnx")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prompt", default="1,2")
    parser.add_argument("--generated-steps", type=int, default=4)
    parser.add_argument("--error-scales", default="0,0.001,0.003,0.005,0.01")
    parser.add_argument("--seeds", default="7,11,19,23")
    parser.add_argument("--target-profile", default="robotics", choices=["wearable", "camera", "robotics"])
    parser.add_argument("--calibration-profile", default="sim-wearable-v0")
    parser.add_argument("--physical-gate", type=Path)
    parser.add_argument("--enforce-physical-gate", action="store_true")
    args = parser.parse_args()
    prompt = [int(item) for item in args.prompt.split(",") if item.strip()]
    scales = [float(item) for item in args.error_scales.split(",") if item.strip()]
    seeds = [int(item) for item in args.seeds.split(",") if item.strip()]
    if not args.model.exists():
        raise SystemExit(f"model not found: {args.model}")
    if any(scale < 0 for scale in scales):
        raise SystemExit("--error-scales cannot contain negative values")
    gate = load_gate(args.physical_gate)
    result = run_sweep(args.model, prompt, args.generated_steps, scales, seeds, args.target_profile, args.calibration_profile, gate, args.enforce_physical_gate)
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "tiny_causal_lm_reliability.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "summary": result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
