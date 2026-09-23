#!/usr/bin/env python3
"""Generate and execute new policy actions outside the frozen search grid.

This is the first proposal/action bridge: the policy proposes nearby actions
around the best training configuration, then the simulator evaluates those
actions on held-out contexts.  Results are written separately from the frozen
ledger so they cannot silently become training data or promotion evidence.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUAL = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification"
POPULATION = QUAL / "converter-to-inference-v1/results/selector-population.json"
RUNNER = QUAL / "transformer-hybrid-qualification-v1/run_qualification.py"
RSI_LOOP = Path(__file__).resolve().parent / "end-to-end-rsi-policy-loop.json"
DERIVED_LEDGER = Path(__file__).resolve().parent / "derived-ledger-transfer.json"
OUT = Path(__file__).resolve().parent / "new-trial-proposals.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("transformer_qualification", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    runner = load_runner()
    population = json.loads(POPULATION.read_text())
    rsi_loop = json.loads(RSI_LOOP.read_text())
    assert rsi_loop["schema_version"] == "recursive_end_to_end_rsi_policy_loop.v1"
    assert rsi_loop["status"] == "passed"
    prior_memory = []
    prior_digest = None
    if DERIVED_LEDGER.is_file():
        previous = json.loads(DERIVED_LEDGER.read_text())
        prior_memory = previous.get("learning_update", {}).get("persistent_memory_updates", [])
        prior_digest = __import__("hashlib").sha256(DERIVED_LEDGER.read_bytes()).hexdigest()
    tensors = dict(__import__("numpy").load(
        QUAL.parent / "experiments/hexagon-mlir-transformer-block-v1/fixture/tensors.npz"
    ))
    reference = tensors["reference_output"]

    # Proposal selection is driven by the end-to-end RSI memory, not by a
    # second hand-written search heuristic.  Restricting to safe actions keeps
    # the proposal bridge fail-closed; the new trials remain separate evidence.
    memory = [item for item in rsi_loop["memory"]["persistent_performance_memory"]
              if item["safe_rate"] == 1.0 and item["action"]["placement"]]
    # Keep prior proposal outcomes in the decision context. Current safe
    # actions dominate failed mutations, but the prior memory remains visible
    # and auditable for future generations rather than being discarded.
    memory_context = rsi_loop["memory"]["persistent_performance_memory"] + prior_memory
    best_memory = max(memory, key=lambda item: (item["mean_reward"], -item["action"]["precision"]))
    best = best_memory["action"]
    # These actions are deliberately outside the existing grid (bits 8/10/12,
    # gains .99/1.0/1.01), forcing the policy to request fresh simulator work.
    proposals = [
        {"placement": list(best["placement"]), "bits": bits, "gain_factor": gain}
        for bits, gain in itertools.product((9, 11), (0.995, 1.005))
    ]

    rows = []
    heldout_cases = [case for case in population["cases"] if int(case["seed"]) >= 6]
    for case_index, case in enumerate(heldout_cases):
        if int(case["seed"]) < 6:
            continue
        for proposal_index, proposal in enumerate(proposals):
            repeats = []
            for repeat in range(3):
                output, _ = runner.execute(
                    tensors,
                    proposal["bits"],
                    float(case["injected_relative_noise"]),
                    1.0,
                    runner.SEED + case_index * 100 + proposal_index * 10 + repeat,
                    analog_ops=proposal["placement"],
                    calibration={"per_operator_gain": {op: proposal["gain_factor"] for op in proposal["placement"]}},
                )
                repeats.append(runner.check(output, reference))
            reliable = bool(case["converter_gate"]) and all(item["passes"] for item in repeats)
            rows.append({
                "case_id": case["case_id"],
                "proposal": proposal,
                "repeats": repeats,
                "converter_gate": bool(case["converter_gate"]),
                "reliable": reliable,
                "cost": runner.modeled_cost(proposal["bits"], float(case["injected_relative_noise"]), repeats[0], len(proposal["placement"])),
            })

    result = {
        "schema_version": "recursive_new_trial_proposals.v1",
        "source_population": str(POPULATION.relative_to(ROOT)),
        "source_rsi_loop": str(RSI_LOOP.relative_to(ROOT)),
        "prior_derived_memory": str(DERIVED_LEDGER.relative_to(ROOT)) if prior_digest else None,
        "prior_derived_memory_sha256": prior_digest,
        "memory_context_entries": len(memory_context),
        "proposal_rule": "tabular_q_performance_memory_mutation_outside_frozen_grid",
        "source_action": best,
        "source_action_mean_reward": best_memory["mean_reward"],
        "proposals": proposals,
        "rows": rows,
        "summary": {
            "proposal_count": len(proposals),
            "heldout_cases": len({row["case_id"] for row in rows}),
            "trial_rows": len(rows),
            "reliable_rows": sum(row["reliable"] for row in rows),
            "proposals_with_any_reliable_heldout_case": sum(
                any(row["reliable"] for row in rows if row["proposal"] == proposal)
                for proposal in proposals
            ),
        },
        "status": "executed",
        "claim_boundary": "Fresh simulator trials generated from a learned-search proposal; separate from the frozen ledger and not hardware, silicon, or production evidence.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
