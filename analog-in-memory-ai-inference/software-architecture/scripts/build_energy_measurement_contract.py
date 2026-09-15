#!/usr/bin/env python3
"""Create the evidence contract required before projection energy is claimed."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    coefficients = {
        "DAC_pJ_per_conversion": {"unit": "pJ/conversion", "required_evidence": "matched_dac_supply_trace", "scope": "same Sky130 macro, corner, voltage, and timing used by SAR receipt"},
        "ADC_pJ_per_conversion": {"unit": "pJ/conversion", "required_evidence": "matched_adc_supply_trace", "scope": "same comparator/SAR macro and conversion window"},
        "array_pJ_per_evaluation": {"unit": "pJ/array_evaluation", "required_evidence": "array_mac_supply_trace", "scope": "same active rows, columns, weights, and accumulation mode"},
        "digital_add_pJ": {"unit": "pJ/addition", "required_evidence": "synthesized_or_measured_accumulator_energy", "scope": "same target technology and precision"},
        "boundary_pJ_per_byte": {"unit": "pJ/byte", "required_evidence": "measured_boundary_transfer_energy", "scope": "same movement path and voltage domain"},
        "same_target_digital_projection_pJ": {"unit": "pJ/projection", "required_evidence": "matched_digital_baseline_energy", "scope": "same GPT-2 layer, precision, batch, and target technology"},
    }
    result = {
        "schema_version": "energy-measurement-contract-v0.1",
        "result_type": "matched_projection_energy_measurement_contract",
        "status": "awaiting_matched_measurements",
        "coefficients": coefficients,
        "required_controls": ["source revision", "Sky130 model bundle hash or silicon lot", "process corner", "temperature", "supply voltage", "clock schedule", "active dimensions", "precision", "measurement instrument or SPICE current probes"],
        "ineligible_proxies": [{"artifact": "analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/converter-supply-energy-spice-evidence.json", "reason": "simple-load converter estimate; excludes extracted converter, bias, clock, leakage, comparator, and array energy"}, {"artifact": "analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/gpt2-sar-t4-20260910-r8/evaluation.json", "reason": "CUDA timing and quality evidence; contains no device energy measurement"}],
        "acceptance": {"all_coefficients_present": False, "same_scope_and_revision": False, "projection_cost_model_may_claim_energy": False},
        "claim_boundary": "This contract defines what must be measured. It intentionally makes no analog, hybrid, or energy-efficiency claim until all six coefficients are supplied with matched evidence.",
    }
    body = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["artifact_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "required_coefficients": len(coefficients), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
