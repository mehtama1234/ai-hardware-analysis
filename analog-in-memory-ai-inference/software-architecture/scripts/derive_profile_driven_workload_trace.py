#!/usr/bin/env python3
"""Derive a claim-safe workload trace from a saved GPT-2 projection run."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--sar-profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variant", default="dac10_weight8_adc12")
    args = parser.parse_args()
    evaluation: dict[str, Any] = json.loads(args.evaluation.read_text())
    contract: dict[str, Any] = json.loads(args.contract.read_text())
    sar: dict[str, Any] = json.loads(args.sar_profile.read_text())
    variant = next((row for row in evaluation.get("variants", []) if row.get("id") == args.variant), None)
    if variant is None:
        raise SystemExit(f"variant not found: {args.variant}")
    per_vector = variant["contract"]["per_vector"]
    phase_rows = []
    for phase in sorted({row.get("phase") for row in variant.get("trace", [])}):
        rows = [row for row in variant["trace"] if row.get("phase") == phase]
        vectors = sum(int(row.get("vectors", 0)) for row in rows)
        phase_rows.append({
            "phase": phase,
            "trace_records": len(rows),
            "vectors": vectors,
            "dac_conversions": vectors * per_vector["dac_conversions_without_column_tile_broadcast"],
            "adc_conversions": vectors * per_vector["adc_conversions_after_differential_subtraction"],
            "array_evaluations": vectors * per_vector["array_evaluations"],
            "digital_partial_sum_additions": vectors * per_vector["digital_partial_sum_additions"],
            "boundary_input_bytes_fp32": vectors * per_vector["boundary_input_bytes_fp32"],
            "boundary_output_bytes_fp32": vectors * per_vector["boundary_output_bytes_fp32"],
            "dac_clipped_values": sum(int(row.get("dac_clipped_values", 0)) for row in rows),
            "adc_clipped_values": sum(int(row.get("adc_clipped_values", 0)) for row in rows),
        })
    totals = {}
    for key in ("vectors", "dac_conversions", "adc_conversions", "array_evaluations",
                "digital_partial_sum_additions", "boundary_input_bytes_fp32",
                "boundary_output_bytes_fp32", "dac_clipped_values", "adc_clipped_values"):
        totals[key] = sum(row[key] for row in phase_rows)
    result = {
        "schema_version": "profile-driven-workload-trace-v0.1",
        "result_type": "derived_gpt2_projection_workload_trace",
        "evidence_kind": "derived_from_saved_real_model_evaluation",
        "sources": {
            "evaluation": {"path": str(args.evaluation), "sha256": digest(args.evaluation)},
            "workload_contract": {"path": str(args.contract), "sha256": digest(args.contract)},
            "sar_profile": {"path": str(args.sar_profile), "sha256": digest(args.sar_profile)},
        },
        "model": evaluation.get("model"),
        "variant": {"id": variant["id"], "quality": variant.get("quality"),
                    "contract": variant.get("contract")},
        "phase_rows": phase_rows,
        "totals": totals,
        "execution_policy": {
            "placement": "digital_fallback_only",
            "fallback_count": totals["vectors"],
            "analog_placement_allowed": contract["converter_qualification_binding"]["analog_placement_allowed"],
            "reason": "circuit profile has open cases and fixed remap holdout promotion is false",
        },
        "energy_latency": {
            "status": "not_identifiable",
            "missing_coefficients": ["DAC_pJ_per_conversion", "ADC_pJ_per_conversion",
                                      "array_pJ_per_evaluation", "digital_add_pJ",
                                      "boundary_pJ_per_byte", "same_target_digital_baseline"],
        },
        "decision": "trace_ready_for_colab_holdout_execution",
        "claim_boundary": "This trace counts operations and movement implied by a saved numerical GPT-2 projection. It is not measured analog hardware execution and does not claim latency, energy, yield, or speedup.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"output": str(args.output), "vectors": totals["vectors"],
                      "dac_conversions": totals["dac_conversions"], "adc_conversions": totals["adc_conversions"],
                      "placement": result["execution_policy"]["placement"]}))


if __name__ == "__main__":
    main()
