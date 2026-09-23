#!/usr/bin/env python3
"""Measure persistent cross-workload memory retrieval on held-out MLP noise.

Transformer proposal outcomes form the persisted source-task memory. The MLP
noise sweep is split by noise domain; target rows in each held-out fold are
used only to replay the target safety gate, never to select the retrieved
source action. This is an offline simulator-evidence ablation, not deployment.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
SOURCE_MEMORY = HERE / "derived-ledger-transfer.json"
TARGET_SWEEP = ROOT / "analog-in-memory-ai-inference/software-architecture/experiments/hexagon-mlir-mlp-v1/comparison/analog-sweep.json"
SOURCE_POPULATION = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/converter-to-inference-v1/results/selector-population.json"
OUT = HERE / "cross-task-memory-retrieval-ablation.json"
FOLDS = (
    {"name": "heldout_low_noise", "train_noise": [0.005, 0.01], "heldout_noise": [0.0, 0.001]},
    {"name": "heldout_high_noise", "train_noise": [0.0, 0.001], "heldout_noise": [0.005, 0.01]},
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def map_bits(requested: int, supported: list[int]) -> int:
    if not supported:
        raise ValueError("target workload has no supported bit configurations")
    return min(supported, key=lambda value: (abs(value - requested), value))


def choose_source_action(memory: list[dict], mode: str) -> dict:
    """Retrieve a source action using full, mean-return-only, or shuffled memory."""
    if mode not in {"failure_aware", "mean_return_only", "shuffled"}:
        raise ValueError(f"unsupported retrieval mode {mode!r}")
    candidates = [row for row in memory if row.get("safe", 0) > 0]
    if not candidates:
        raise ValueError("source memory has no action with a successful observation")
    ranked = [dict(row) for row in candidates]
    if mode == "shuffled":
        ordered = sorted(ranked, key=lambda row: (
            int(row["action"]["bits"]), float(row["action"]["gain_factor"]),
            tuple(row["action"]["placement"]),
        ))
        metrics = [(row["safe_rate"], row["mean_reward"]) for row in ordered][::-1]
        for row, (safe_rate, mean_reward) in zip(ordered, metrics):
            row["safe_rate"], row["mean_reward"] = safe_rate, mean_reward
        ranked = ordered
    if mode == "failure_aware":
        selected = max(ranked, key=lambda row: (
            float(row["safe_rate"]), float(row["mean_reward"]),
            int(row["action"]["bits"]), float(row["action"]["gain_factor"]),
        ))
    else:
        selected = max(ranked, key=lambda row: (
            float(row["mean_reward"]), int(row["action"]["bits"]),
            float(row["action"]["gain_factor"]),
        ))
    return selected


def choose_local_bits(rows: list[dict], train_noise: list[float]) -> int | None:
    """Choose the cheapest target precision that passed every training noise."""
    supported = sorted({int(row["adc_bits"]) for row in rows})
    for bits in supported:
        by_noise = {
            float(row["noise_stddev"]): row
            for row in rows
            if int(row["adc_bits"]) == bits and int(row["dac_bits"]) == bits
        }
        if all(noise in by_noise and by_noise[noise]["passes_declared_numeric_budget"]
               for noise in train_noise):
            return bits
    return None


def replay_target(rows: list[dict], bits: int | None, noise_levels: list[float]) -> list[dict]:
    decisions = []
    for noise in noise_levels:
        target = next((row for row in rows
                       if float(row["noise_stddev"]) == noise
                       and int(row["adc_bits"]) == bits
                       and int(row["dac_bits"]) == bits), None) if bits is not None else None
        analog_allowed = bool(target and target["passes_declared_numeric_budget"])
        decisions.append({
            "noise_stddev": noise,
            "requested_bits": bits,
            "action": "selective_analog" if analog_allowed else "digital_fallback",
            "target_numeric_pass": bool(target and target["passes_declared_numeric_budget"]),
            "safe": True,  # failed/missing target evidence invokes digital fallback
        })
    return decisions


def summarize(decisions: list[dict]) -> dict:
    return {
        "cases": len(decisions),
        "safe_cases": sum(bool(row["safe"]) for row in decisions),
        "analog_cases": sum(row["action"] == "selective_analog" for row in decisions),
        "fallback_cases": sum(row["action"] == "digital_fallback" for row in decisions),
        "unsafe_analog_cases": sum(
            row["action"] == "selective_analog" and not row["target_numeric_pass"]
            for row in decisions
        ),
    }


def run_seed_heldout_source_ablation(fresh_trials: dict, population: dict) -> dict:
    """Compare failure-aware and conditional-quality retrieval on held-out seeds."""
    rows = fresh_trials["rows"]
    contexts = {row["case_id"]: row for row in population["cases"]}
    case_ids = {row["case_id"] for row in rows}
    if case_ids - contexts.keys():
        raise ValueError("fresh source trials refer to cases missing from the frozen population")
    for row in rows:
        context = contexts[row["case_id"]]
        repeats = row.get("repeats", [])
        repeat_safe = len(repeats) == 3 and all(
            repeat.get("finite") is True and repeat.get("passes") is True
            for repeat in repeats
        )
        expected_reliable = bool(row.get("converter_gate")) and repeat_safe
        if row.get("converter_gate") is not context.get("converter_gate"):
            raise ValueError(f"source trial converter gate disagrees with frozen case {row['case_id']}")
        if row.get("reliable") is not expected_reliable:
            raise ValueError(f"source trial reliability disagrees with its gate/repeats for {row['case_id']}")
    seeds = sorted({int(contexts[case_id]["seed"]) for case_id in case_ids})
    actions = sorted({(
        int(row["proposal"]["bits"]),
        float(row["proposal"]["gain_factor"]),
        tuple(row["proposal"]["placement"]),
    ) for row in rows})
    if len(seeds) < 3 or len(actions) < 2:
        raise ValueError("seed-held-out retrieval needs at least three seeds and two actions")
    case_actions = {
        case_id: [(
            int(row["proposal"]["bits"]),
            float(row["proposal"]["gain_factor"]),
            tuple(row["proposal"]["placement"]),
        ) for row in rows if row["case_id"] == case_id]
        for case_id in case_ids
    }
    if any(sorted(items) != actions for items in case_actions.values()):
        raise ValueError("each source case must contain exactly one observation per proposal action")

    methods = {"failure_aware": [], "conditional_quality_only": []}
    for heldout_seed in seeds:
        training = [row for row in rows if int(contexts[row["case_id"]]["seed"]) != heldout_seed]
        heldout = [row for row in rows if int(contexts[row["case_id"]]["seed"]) == heldout_seed]
        if not training or not heldout:
            raise ValueError(f"seed {heldout_seed} has an empty train or held-out split")
        grouped = {
            action: [row for row in training if (
                int(row["proposal"]["bits"]),
                float(row["proposal"]["gain_factor"]),
                tuple(row["proposal"]["placement"]),
            ) == action]
            for action in actions
        }

        def mean_reward(items: list[dict]) -> float:
            return sum(
                -1_000_000.0 if not row["reliable"] else
                10_000.0 * len(row["proposal"]["placement"]) - float(row["cost"]["estimated_energy"])
                for row in items
            ) / len(items)

        def mean_reliable_error(items: list[dict]) -> float:
            errors = [float(repeat["mean_absolute_error"])
                      for row in items if row["reliable"]
                      for repeat in row["repeats"]]
            return sum(errors) / len(errors) if errors else float("inf")

        failure_action = max(actions, key=lambda action: (
            sum(bool(row["reliable"]) for row in grouped[action]) / len(grouped[action]),
            mean_reward(grouped[action]),
            action[0], action[1], action[2],
        ))
        quality_candidates = [action for action in actions if mean_reliable_error(grouped[action]) < float("inf")]
        quality_action = min(quality_candidates, key=lambda action: (
            mean_reliable_error(grouped[action]), action[0], action[1], action[2],
        )) if quality_candidates else None

        for name, action in (("failure_aware", failure_action),
                             ("conditional_quality_only", quality_action)):
            selected_rows = [] if action is None else [row for row in heldout if (
                int(row["proposal"]["bits"]),
                float(row["proposal"]["gain_factor"]),
                tuple(row["proposal"]["placement"]),
            ) == action]
            if action is not None and len(selected_rows) != len({row["case_id"] for row in heldout}):
                raise ValueError(f"seed {heldout_seed} has incomplete held-out action outcomes")
            methods[name].append({
                "heldout_seed": heldout_seed,
                "training_case_count": len({row["case_id"] for row in training}),
                "heldout_case_count": len({row["case_id"] for row in heldout}),
                "selected_action": None if action is None else {
                    "bits": action[0], "gain_factor": action[1], "placement": list(action[2]),
                },
                "training_failure_rate": None if action is None else 1.0 - (
                    sum(bool(row["reliable"]) for row in grouped[action]) / len(grouped[action])
                ),
                "training_conditional_mean_absolute_error": (
                    None if action is None or mean_reliable_error(grouped[action]) == float("inf")
                    else mean_reliable_error(grouped[action])
                ),
                "heldout_reliable_cases": sum(bool(row["reliable"]) for row in selected_rows),
                "heldout_cases": len(selected_rows),
                "heldout_reliable_by_pvt": {
                    pvt: sum(bool(row["reliable"]) and contexts[row["case_id"]]["pvt_class"] == pvt
                             for row in selected_rows)
                    for pvt in sorted({contexts[row["case_id"]]["pvt_class"] for row in selected_rows})
                },
            })

    totals = {}
    for name, folds in methods.items():
        totals[name] = {
            "folds": len(folds),
            "heldout_cases": sum(row["heldout_cases"] for row in folds),
            "heldout_reliable_cases": sum(row["heldout_reliable_cases"] for row in folds),
            "selected_actions": sorted({json.dumps(row["selected_action"], sort_keys=True) for row in folds}),
            "fold_details": folds,
        }
    return {
        "split": "leave-one-seed-out; all PVT/noise cases for held-out seed excluded from retrieval",
        "source_seed_count": len(seeds),
        "source_case_count": len(case_ids),
        "methods": totals,
        "failure_aware_vs_conditional_quality_heldout_reliable_case_delta": (
            totals["failure_aware"]["heldout_reliable_cases"]
            - totals["conditional_quality_only"]["heldout_reliable_cases"]
        ),
        "claim_boundary": "Descriptive held-out source simulator evidence; small seed count and no statistical promotion claim.",
    }


def run(source_document: dict, target_document: dict, source_population: dict) -> dict:
    updates = source_document["learning_update"]["persistent_memory_updates"]
    source_holdout = run_seed_heldout_source_ablation(
        source_document["derived_ledger"]["fresh_trials"], source_population
    )
    source_action = choose_source_action(updates, "failure_aware")
    performance_only_action = choose_source_action(updates, "mean_return_only")
    shuffled_action = choose_source_action(updates, "shuffled")
    target_rows = target_document["rows"]
    target_bits = sorted({int(row["adc_bits"]) for row in target_rows})
    policies = {
        "task_local_no_cross_task_retrieval": [],
        "cross_task_failure_aware_retrieval": [],
        "cross_task_mean_return_only": [],
        "cross_task_shuffled_memory": [],
    }
    for fold in FOLDS:
        local_bits = choose_local_bits(target_rows, fold["train_noise"])
        recommendations = {
            "task_local_no_cross_task_retrieval": local_bits,
            "cross_task_failure_aware_retrieval": map_bits(int(source_action["action"]["bits"]), target_bits),
            "cross_task_mean_return_only": map_bits(int(performance_only_action["action"]["bits"]), target_bits),
            "cross_task_shuffled_memory": map_bits(int(shuffled_action["action"]["bits"]), target_bits),
        }
        for name, bits in recommendations.items():
            decisions = replay_target(target_rows, bits, fold["heldout_noise"])
            policies[name].append({
                "fold": fold["name"],
                "training_noise": fold["train_noise"],
                "heldout_noise": fold["heldout_noise"],
                "recommended_bits": bits,
                "decisions": decisions,
                "summary": summarize(decisions),
            })

    aggregate = {}
    for name, folds in policies.items():
        decisions = [row for fold in folds for row in fold["decisions"]]
        aggregate[name] = {**summarize(decisions), "folds": folds}

    # Diagnostic ablation: apply the retrieved target precision without the
    # target evidence gate. This is intentionally not a deployable policy.
    ungated = []
    retrieved_bits = map_bits(int(source_action["action"]["bits"]), target_bits)
    for row in target_rows:
        if int(row["adc_bits"]) == retrieved_bits and int(row["dac_bits"]) == retrieved_bits:
            ungated.append({"noise_stddev": row["noise_stddev"],
                            "target_numeric_pass": row["passes_declared_numeric_budget"],
                            "unsafe_analog": not row["passes_declared_numeric_budget"]})

    safe_modes = [name for name in aggregate if name != "cross_task_shuffled_memory"]
    return {
        "schema_version": "recursive_cross_task_memory_retrieval_ablation.v1",
        "recorded_on": "2026-09-22",
        "source_task": source_document["learning_update"]["source_state"]["workload"],
        "target_task": target_document["workload_id"],
        "inputs": {
            "persistent_source_memory": {"path": str(SOURCE_MEMORY.relative_to(ROOT)), "sha256": digest(SOURCE_MEMORY)},
            "target_numeric_sweep": {"path": str(TARGET_SWEEP.relative_to(ROOT)), "sha256": digest(TARGET_SWEEP)},
            "source_context_population": {"path": str(SOURCE_POPULATION.relative_to(ROOT)), "sha256": digest(SOURCE_POPULATION)},
        },
        "retrieval": {
            "source_memory_entries": len(updates),
            "failure_aware_action": source_action["action"],
            "failure_aware_safe_rate": source_action["safe_rate"],
            "failure_aware_failures": source_action["failures"],
            "failure_aware_attempts": source_action["attempts"],
            "performance_only_action": performance_only_action["action"],
            "shuffled_memory_action": shuffled_action["action"],
            "bit_mapping": "nearest target ADC/DAC bit pair; ties choose lower precision",
        },
        "split": {"method": "leave-noise-domain-pair-out", "folds": list(FOLDS),
                  "available_target_sweep_rows": len(target_rows),
                  "heldout_noise_domains": len({float(row["noise_stddev"]) for row in target_rows})},
        "methods": aggregate,
        "source_seed_holdout_ablation": source_holdout,
        "ungated_safety_ablation": {
            "policy": "cross-task retrieved precision without target numeric gate/fallback",
            "rows": ungated,
            "unsafe_analog_cases": sum(row["unsafe_analog"] for row in ungated),
            "claim_boundary": "Diagnostic only; explicitly not an eligible runtime policy.",
        },
        "summary": {
            "failure_aware_safe_cases": aggregate["cross_task_failure_aware_retrieval"]["safe_cases"],
            "failure_aware_analog_cases": aggregate["cross_task_failure_aware_retrieval"]["analog_cases"],
            "local_baseline_analog_cases": aggregate["task_local_no_cross_task_retrieval"]["analog_cases"],
            "mean_return_only_analog_cases": aggregate["cross_task_mean_return_only"]["analog_cases"],
            "shuffled_memory_analog_cases": aggregate["cross_task_shuffled_memory"]["analog_cases"],
            "failure_aware_differs_from_mean_return_only": source_action["action"] != performance_only_action["action"],
            "failure_aware_unsafe_analog_cases": aggregate["cross_task_failure_aware_retrieval"]["unsafe_analog_cases"],
            "ungated_unsafe_analog_cases": sum(row["unsafe_analog"] for row in ungated),
            "all_gated_methods_safe": all(aggregate[name]["safe_cases"] == aggregate[name]["cases"]
                                           for name in safe_modes),
            "cross_task_coverage_gain": (
                aggregate["cross_task_failure_aware_retrieval"]["analog_cases"]
                - aggregate["task_local_no_cross_task_retrieval"]["analog_cases"]
            ),
        },
        "status": "passed" if all(aggregate[name]["safe_cases"] == aggregate[name]["cases"]
                                   for name in aggregate) else "blocked",
        "promotion": {"status": "not_eligible",
                      "reason": "small offline evidence ablation only; no held-out converter improvement, comparable cost evidence, runtime qualification, or hardware evidence"},
        "data_contract_gaps": [
            "the target MLP noise sweep has no explicit PVT corner, converter gate, or comparable relative-cost field; this ablation validates numeric-gated cross-workload transfer only",
        ],
        "claim_boundary": (
            "Offline cross-workload retrieval ablation over persisted transformer simulator memory and a frozen MLP numeric sweep. "
            "MLP numeric pass/fail rows are held-out evidence only; modeled/recorded numeric outcomes are not hardware measurements."
        ),
    }


def main() -> int:
    source = json.loads(SOURCE_MEMORY.read_text())
    target = json.loads(TARGET_SWEEP.read_text())
    population = json.loads(SOURCE_POPULATION.read_text())
    result = run(source, target, population)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "summary": result["summary"],
                      "retrieval": result["retrieval"]}, indent=2, sort_keys=True))
    return 0 if result["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
