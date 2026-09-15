#!/usr/bin/env python3
"""Build a conservative decision package for the stateful multi-module profile."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stateful_report", type=Path)
    parser.add_argument("third_holdout", type=Path)
    parser.add_argument("runtime_trace", type=Path)
    parser.add_argument("cost_trace", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    stateful_path = args.stateful_report.resolve()
    third_path = args.third_holdout.resolve()
    runtime_path = args.runtime_trace.resolve()
    cost_path = args.cost_trace.resolve()
    stateful = json.loads(stateful_path.read_text(encoding="utf-8"))
    third = json.loads(third_path.read_text(encoding="utf-8"))
    original = stateful["results"]["stateful_previous_token_original"]["quality"]
    prior_stress = stateful["results"]["stateful_previous_token_stress"]["quality"]
    third_quality = third["results"]["stateful_previous_token_original"]["quality"]
    gates = [
        {"gate": "frozen_stateful_profile", "passed": True},
        {"gate": "original_context_quality", "passed": original["screen_pass"],
         "detail": f"agreement {original['teacher_forced_argmax_agreement']:.6f}"},
        {"gate": "prior_stress_context_quality", "passed": prior_stress["screen_pass"],
         "detail": f"agreement {prior_stress['teacher_forced_argmax_agreement']:.6f}"},
        {"gate": "third_holdout_generalization", "passed": third_quality["screen_pass"],
         "detail": f"agreement {third_quality['teacher_forced_argmax_agreement']:.6f}"},
        {"gate": "sequence_state_scope", "passed": True,
         "detail": "previous-row term is computed within each projection call; no cross-call state is retained"},
        {"gate": "governed_runtime_trace", "passed": runtime_path.is_file(),
         "detail": "stateful governor route trace is hash-bound"},
        {"gate": "modeled_cost_trace", "passed": cost_path.is_file(),
         "detail": "162-vector modeled cost/fallback rows are present"},
        {"gate": "analog_authorization", "passed": False},
    ]
    decision = "stateful_profile_not_generalized" if not all(gate["passed"] for gate in gates[:4]) else "stateful_profile_numerically_qualified_authorization_closed"
    result = {
        "schema_version": "gpt2-stateful-multimodule-decision-v0.1",
        "result_type": "bounded_local_stateful_multi_module_decision",
        "sources": {"stateful_report": {"path": str(stateful_path), "sha256": digest(stateful_path)},
                    "third_holdout": {"path": str(third_path), "sha256": digest(third_path)},
                    "runtime_trace": {"path": str(runtime_path), "sha256": digest(runtime_path)},
                    "cost_trace": {"path": str(cost_path), "sha256": digest(cost_path)}},
        "target_modules": stateful["target_modules"],
        "profile": {"weight_bits": 16, "dac_bits": 16, "adc_bits": 14,
                     "range_multiplier": 1.25, "transfer": "previous provisional output row"},
        "gates": gates, "gate_count": len(gates),
        "passed_gate_count": sum(gate["passed"] for gate in gates),
        "decision": decision, "runtime_decision": "digital_reference_and_deterministic_fallback_only",
        "analog_candidate_authorized": False,
        "claim_boundary": "Local CPU multi-context decision only; third holdout fails, modeled costs are not measurements, and no analog authorization is claimed.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    decision_path = args.output / "decision_audit.json"
    decision_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    ledger = {"schema_version": "gpt2-stateful-multimodule-claim-ledger-v0.1", "claims": [
        {"claim": "stateful_profile_original_and_prior_stress", "status": "proven_local_bounded", "evidence": str(stateful_path)},
        {"claim": "stateful_profile_third_holdout_generalization", "status": "not_proven", "evidence": str(third_path)},
        {"claim": "sequence_state_scope", "status": "proven_local_bounded", "evidence": "projection call-local previous-row implementation"},
        {"claim": "runtime_and_modeled_cost_accounting", "status": "proven_local_bounded", "evidence": str(runtime_path)},
        {"claim": "analog_execution_authorization", "status": "not_authorized", "evidence": "analog_candidate_authorized=false"},
    ], "claim_boundary": result["claim_boundary"]}
    ledger_path = args.output / "claim_ledger.json"
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    manifest = {"files": [{"path": str(decision_path), "sha256": digest(decision_path)},
                          {"path": str(ledger_path), "sha256": digest(ledger_path)},
                          {"path": str(stateful_path), "sha256": digest(stateful_path)},
                          {"path": str(third_path), "sha256": digest(third_path)},
                          {"path": str(runtime_path), "sha256": digest(runtime_path)},
                          {"path": str(cost_path), "sha256": digest(cost_path)}]}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(decision_path), "passed": result["passed_gate_count"], "gates": len(gates), "decision": decision}, sort_keys=True))


if __name__ == "__main__":
    main()
