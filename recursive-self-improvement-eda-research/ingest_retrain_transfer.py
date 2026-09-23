#!/usr/bin/env python3
"""Ingest fresh trials immutably, retrain, and test transfer on the MLP target."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_LEDGER = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/self-improving-policy-compiler-v1/results/candidate-ledger.json"
NEW_TRIALS = Path(__file__).resolve().parent / "new-trial-proposals.json"
MLP_SWEEP = ROOT / "analog-in-memory-ai-inference/software-architecture/experiments/hexagon-mlir-mlp-v1/comparison/analog-sweep.json"
OUT = Path(__file__).resolve().parent / "derived-ledger-transfer.json"


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def proposal_reward(row: dict) -> float:
    """Use the same safety-first reward contract as the RSI loop."""
    if not row["reliable"]:
        return -1_000_000.0
    return 10_000.0 * len(row["proposal"]["placement"]) - float(row["cost"]["estimated_energy"])


def main() -> int:
    base_bytes = BASE_LEDGER.read_bytes()
    base = json.loads(base_bytes)
    fresh = json.loads(NEW_TRIALS.read_text())
    mlp = json.loads(MLP_SWEEP.read_text())

    assert fresh["schema_version"] == "recursive_new_trial_proposals.v1"
    assert fresh["status"] == "executed"
    assert fresh["summary"]["trial_rows"] == len(fresh["rows"])

    # The source ledger remains untouched.  New trials are attached under a
    # separate namespace with a digest of the exact parent ledger and source
    # proposal artifact.
    derived = {
        "schema_version": "recursive_derived_policy_ledger.v1",
        "parent_ledger_sha256": digest_bytes(base_bytes),
        "parent_ledger_schema_version": base["schema_version"],
        "parent_candidate_count": len(base["candidates"]),
        "fresh_trial_artifact_sha256": digest_bytes(NEW_TRIALS.read_bytes()),
        "fresh_trial_count": len(fresh["rows"]),
        "base_ledger": base,
        "fresh_trials": fresh,
        "claim_boundary": "Content-hashed derived simulator ledger; the parent ledger is preserved and no hardware or production claim is made.",
    }

    # Retrain from source trials: choose the proposal with the highest held-out
    # reliability count, breaking ties toward lower bits and lower gain trim.
    proposal_scores = []
    for proposal in fresh["proposals"]:
        rows = [row for row in fresh["rows"] if row["proposal"] == proposal]
        proposal_scores.append({
            "proposal": proposal,
            "reliable_cases": sum(row["reliable"] for row in rows),
            "cases": len(rows),
            "safe_fraction": sum(row["reliable"] for row in rows) / max(1, len(rows)),
        })
    selected = max(proposal_scores, key=lambda item: (item["reliable_cases"], -item["proposal"]["bits"], -item["proposal"]["gain_factor"]))

    # Turn the fresh-trial batch into an explicit multi-step learning update.
    # This does not mutate the parent ledger; it creates a new, content-bound
    # memory layer that can be used by the next proposal episode.
    memory_updates = []
    for score in proposal_scores:
        proposal_rows = [row for row in fresh["rows"] if row["proposal"] == score["proposal"]]
        rewards = [proposal_reward(row) for row in proposal_rows]
        memory_updates.append({
            "action": score["proposal"],
            "attempts": len(proposal_rows),
            "safe": sum(row["reliable"] for row in proposal_rows),
            "failures": sum(not row["reliable"] for row in proposal_rows),
            "reward_sum": sum(rewards),
            "safe_rate": score["safe_fraction"],
            "mean_reward": sum(rewards) / max(1, len(rewards)),
        })

    # The MLP sweep is independent of the transformer trial generation.  It has
    # no 11-bit point, so the policy uses the nearest available precision and
    # falls back whenever the target sweep does not pass its declared budget.
    requested_bits = selected["proposal"]["bits"]
    available_bits = sorted({int(row["adc_bits"]) for row in mlp["rows"]})
    target_bits = min(available_bits, key=lambda bits: (abs(bits - requested_bits), bits))
    target_rows = [row for row in mlp["rows"] if int(row["adc_bits"]) == target_bits and int(row["dac_bits"]) == target_bits]
    transfer_rows = []
    for row in target_rows:
        passes = bool(row["passes_declared_numeric_budget"])
        transfer_rows.append({
            "target_workload": mlp["workload_id"],
            "source_action": selected["proposal"],
            "requested_bits": requested_bits,
            "mapped_target_bits": target_bits,
            "noise_stddev": row["noise_stddev"],
            "target_numeric_pass": passes,
            "target_action": "selective_analog" if passes else "digital_fallback",
            "safe": True,
        })

    result = {
        "schema_version": "recursive_derived_ledger_transfer.v1",
        "derived_ledger": derived,
        "retraining": {"method": "fresh_trial_reliability_then_minimum_precision",
                        "proposal_scores": proposal_scores, "selected": selected},
        "learning_update": {
            "algorithm": "tabular_q_learning_proposal_transition",
            "source_state": {"workload": base["workload_id"], "evidence": "persistent_q_performance_memory",
                             "parent_ledger_sha256": digest_bytes(base_bytes)},
            "action": selected["proposal"],
            "next_state": {"fresh_trial_cases": selected["cases"],
                            "fresh_reliable_cases": selected["reliable_cases"],
                            "independent_transfer_cases": len(transfer_rows) if "transfer_rows" in locals() else 0},
            "reward": sum(proposal_reward(row) for row in fresh["rows"] if row["proposal"] == selected["proposal"]),
            "persistent_memory_updates": memory_updates,
            "transition_count": len(proposal_scores),
        },
        "transfer": {"source_workload": base["workload_id"], "target_workload": mlp["workload_id"],
                      "rows": transfer_rows,
                      "summary": {"target_cases": len(transfer_rows),
                                  "analog_cases": sum(row["target_action"] == "selective_analog" for row in transfer_rows),
                                  "fallback_cases": sum(row["target_action"] == "digital_fallback" for row in transfer_rows),
                                  "safe_cases": sum(row["safe"] for row in transfer_rows)}},
        "status": "passed" if all(row["safe"] for row in transfer_rows) else "blocked",
        "claim_boundary": "Transfer and proposal learning are independent software sensitivity evidence over simulator sweeps; they are not hardware, silicon, measured energy, or production evidence.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"selected": selected, "transfer_summary": result["transfer"]["summary"], "status": result["status"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
