#!/usr/bin/env python3
"""Run one manifestable end-to-end RSI policy loop over the typed AIMC ledger.

The loop is deliberately conservative: correctness and fallback safety are hard
gates; modeled cost is only optimized after a candidate is verified. The
learner is an explicit tabular Q-learning policy over contextual states, not a
deep-RL or hardware claim.
"""
from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "recursive-self-improvement-eda-research/expanded-candidate-ledger.json"
RUNTIME = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/final-package-v1/results/runtime-package.json"
SCHEDULE = ROOT / "recursive-self-improvement-eda-research/fused-schedule-action-qualification.json"
OUT = Path(__file__).resolve().parent / "end-to-end-rsi-policy-loop.json"
BUDGET = 12
FUSED_SCHEDULE = "fused_stack_hoisted_transformer_block"
FALLBACK_SCHEDULE = "staged_boundary_pipeline"
RISK_LOWER_BOUND_THRESHOLD = 0.25


def key(row: dict) -> tuple:
    return (tuple(row["placement"]), int(row["precision"]), round(float(row["calibration"]["gain_factor"]), 4),
            row.get("schedule", FUSED_SCHEDULE))


def reliable(row: dict) -> bool:
    return bool(row["verification"]["reliable"] and row["converter_gate"])


def wilson_lower_bound(successes: int, attempts: int, z: float = 1.96) -> float:
    """Conservative lower confidence bound for repeated simulator checks."""
    if attempts <= 0:
        return 0.0
    rate = successes / attempts
    denominator = 1.0 + z * z / attempts
    center = rate + z * z / (2.0 * attempts)
    margin = z * (rate * (1.0 - rate) / attempts + z * z / (4.0 * attempts * attempts)) ** 0.5
    return (center - margin) / denominator


def risk_gate(row: dict) -> tuple[bool, float]:
    repeats = row["verification"].get("repeats", [])
    successes = sum(bool(item.get("passes")) for item in repeats)
    lower = wilson_lower_bound(successes, len(repeats))
    return bool(reliable(row) and lower >= RISK_LOWER_BOUND_THRESHOLD), lower


def reward(row: dict) -> float:
    if not reliable(row):
        return -1_000_000.0
    return 10_000.0 * len(row["placement"]) - float(row["cost"]["estimated_energy"])


def fallback() -> dict:
    return {"action": "digital_fallback", "placement": [], "precision": 0,
            "calibration": {"gain_factor": 1.0}, "schedule": FALLBACK_SCHEDULE, "reliable": True,
            "cost": {"estimated_energy": 3072.0}}


def state(corner: dict, budget_left: int, failures: set[tuple]) -> dict:
    return {"workload_context": corner["model_section"], "seed": corner["seed"],
            "temperature_c": corner["temperature_c"], "converter_passed": corner["passed"],
            "budget_left": budget_left, "failure_memory_size": len(failures)}


def state_key(corner: dict) -> tuple:
    """Generalize across repeat seeds while retaining workload/PVT context."""
    return (corner["model_section"], float(corner["temperature_c"]), bool(corner["passed"]))


def learn_q(rows: list[dict]) -> tuple[dict[tuple, float], set[tuple], dict]:
    """Fit terminal tabular Q values on the training ledger.

    Each simulator outcome is a terminal transition in this bounded experiment:
    unsafe actions receive a large negative reward and safe actions receive the
    declared capability-minus-cost reward. Repeated rows are processed in
    stable order, making the resulting table reproducible and auditable.
    """
    q_values: dict[tuple, float] = {}
    failures: set[tuple] = set()
    alpha = 0.5
    gamma = 0.0
    updates = 0
    for row in rows:
        q_key = (state_key(row["corner"]), key(row))
        old = q_values.get(q_key, 0.0)
        q_values[q_key] = old + alpha * (reward(row) + gamma * 0.0 - old)
        updates += 1
        if reliable(row):
            continue
        else:
            failures.add(key(row))
    return q_values, failures, {"algorithm": "tabular_q_learning", "alpha": alpha,
                                "gamma": gamma, "epsilon_train": 0.0,
                                "epsilon_eval": 0.0, "terminal_transition": True,
                                "updates": updates, "state_count": len({k[0] for k in q_values}),
                                "state_action_count": len(q_values)}


def memory_snapshot(rows: list[dict], decisions: list[dict]) -> list[dict]:
    """Persist an auditable action-level performance/failure memory."""
    stats = {}
    for row in rows:
        k = key(row)
        entry = stats.setdefault(k, {"attempts": 0, "safe": 0, "failures": 0, "reward_sum": 0.0})
        entry["attempts"] += 1
        if reliable(row):
            entry["safe"] += 1
        else:
            entry["failures"] += 1
        entry["reward_sum"] += reward(row)
    for decision in decisions:
        for observation in decision["episode"]["trace"]:
            action = observation["action"]
            k = (tuple(action["placement"]), int(action["precision"]), round(float(action["gain_factor"]), 4),
                 action.get("schedule", FUSED_SCHEDULE))
            entry = stats.setdefault(k, {"attempts": 0, "safe": 0, "failures": 0, "reward_sum": 0.0})
            entry["attempts"] += 1
            if observation["observation"]["reliable"]:
                entry["safe"] += 1
            else:
                entry["failures"] += 1
            entry["reward_sum"] += float(observation["reward"])
    memory = []
    for k, entry in sorted(stats.items(), key=lambda item: str(item[0])):
        memory.append({"action": {"placement": list(k[0]), "precision": k[1], "gain_factor": k[2], "schedule": k[3]},
                       **entry, "safe_rate": entry["safe"] / entry["attempts"] if entry["attempts"] else 0.0,
                       "mean_reward": entry["reward_sum"] / entry["attempts"] if entry["attempts"] else 0.0})
    return memory


def run_episode(corner: dict, rows: list[dict], q_values: dict[tuple, float],
                failures: set[tuple], seed: int) -> tuple[dict, dict, set[tuple]]:
    rng = random.Random(seed)
    # Repeated ledger rows represent repeated checks of the same action. The
    # planner should not spend its episode budget rediscovering that action;
    # each unique action is an experiment choice in this environment.
    unique_rows = {}
    for row in rows:
        unique_rows.setdefault(key(row), row)
    remaining = list(unique_rows.values())
    visited: Counter = Counter()
    trace = []
    for step in range(BUDGET):
        if not remaining:
            break
        scored = []
        for row in remaining:
            k = key(row)
            prior = q_values.get((state_key(corner), k), 0.0)
            penalty = -5_000.0 if k in failures else 0.0
            explore = 1_500.0 / (1 + visited[k])
            # Deterministic tie-breaks prefer more capable actions, while the
            # learned prior still dominates when evidence exists.
            tie_break = (len(row["placement"]), int(row["precision"]), -float(row["cost"]["estimated_energy"]))
            scored.append(((prior + penalty + explore + rng.random() * 1e-6, tie_break), row))
        row = max(scored, key=lambda item: item[0])[1]
        remaining.remove(row)
        k = key(row)
        visited[k] += 1
        if not reliable(row):
            failures.add(k)
        risk_passed, confidence_lower = risk_gate(row)
        trace.append({"state": state(corner, BUDGET - step, failures),
                      "action": {"placement": list(k[0]), "precision": k[1], "gain_factor": k[2], "schedule": k[3]},
                      "observation": {"reliable": reliable(row), "risk_gate": risk_passed,
                                       "confidence_lower_bound": confidence_lower,
                                       "converter_gate": bool(row["converter_gate"]),
                                       "estimated_energy": row["cost"]["estimated_energy"]},
                      "reward": reward(row)})
        higher_capability_remaining = any(
            len(candidate["placement"]) > len(row["placement"])
            or (len(candidate["placement"]) == len(row["placement"])
                and int(candidate["precision"]) > int(row["precision"]))
            for candidate in remaining
        )
        if reliable(row) and not higher_capability_remaining:
            break
    safe_observations = [item for item in trace if item["observation"]["risk_gate"]]
    selected = max(safe_observations, key=lambda item: (item["reward"], -item["observation"]["estimated_energy"])) if safe_observations else None
    if selected is None:
        decision = fallback()
    else:
        decision = {"action": "selective_analog", "placement": selected["action"]["placement"],
                    "precision": selected["action"]["precision"],
                    "calibration": {"gain_factor": selected["action"]["gain_factor"]},
                    "schedule": selected["action"]["schedule"],
                    "reliable": True, "cost": {"estimated_energy": selected["observation"]["estimated_energy"]}}
    return decision, {"ledger_evidence_lookups": len(trace), "trace": trace,
                      "fallback": decision["action"] == "digital_fallback"}, failures


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ledger = json.loads(LEDGER.read_text())
    schedule = json.loads(SCHEDULE.read_text())
    if schedule.get("promotion", {}).get("status") != "approved_for_simulator_schedule_search":
        raise RuntimeError("qualified fused schedule is not admitted to search")
    rows = ledger["candidates"]
    by_corner: dict[str, list[dict]] = defaultdict(list)
    corners = {}
    for row in rows:
        encoded = json.dumps(row["corner"], sort_keys=True)
        by_corner[encoded].append(row)
        corners[encoded] = row["corner"]
    train_keys = {encoded for encoded, corner in corners.items() if int(corner["seed"]) % 2 == 0}
    heldout_keys = sorted(set(corners) - train_keys)
    train_rows = [row for encoded, items in by_corner.items() if encoded in train_keys for row in items]
    q_values, failures, learning = learn_q(train_rows)
    decisions = []
    for index, encoded in enumerate(heldout_keys):
        decision, episode, failures = run_episode(corners[encoded], by_corner[encoded], q_values, failures, 73001 + index)
        decisions.append({"corner": corners[encoded], "decision": decision, "episode": episode})
    safe = all(item["decision"]["reliable"] for item in decisions)
    analog = [item for item in decisions if item["decision"]["action"] == "selective_analog"]
    exhaustive_evaluations = sum(len({key(row) for row in by_corner[encoded]}) for encoded in heldout_keys)
    observed_evidence_lookups = sum(item["episode"]["ledger_evidence_lookups"] for item in decisions)
    runtime_hash = digest(RUNTIME) if RUNTIME.is_file() else None
    result = {
        "schema_version": "recursive_end_to_end_rsi_policy_loop.v1",
        "inputs": {"candidate_ledger": str(LEDGER.relative_to(ROOT)), "candidate_ledger_sha256": digest(LEDGER),
                   "runtime_package": str(RUNTIME.relative_to(ROOT)), "runtime_package_sha256": runtime_hash,
                   "schedule_qualification": str(SCHEDULE.relative_to(ROOT)), "schedule_qualification_sha256": digest(SCHEDULE)},
        "environment": {"state_fields": ["workload_context", "seed", "temperature_c", "converter_passed", "budget_left", "failure_memory_size"],
                         "action_fields": ["placement", "precision", "gain_factor", "schedule"],
                         "observation_fields": ["reliable", "risk_gate", "confidence_lower_bound", "converter_gate", "estimated_energy"],
                         "reward": "-1000000 unsafe; 10000*placement_size-estimated_energy reliable",
                         "episode_budget": BUDGET, "fallback_action": "digital_fallback", "schedule_fallback": FALLBACK_SCHEDULE,
                         "risk_lower_bound_threshold": RISK_LOWER_BOUND_THRESHOLD},
        "split": {"training_corner_count": len(train_keys), "heldout_corner_count": len(heldout_keys),
                  "training_seeds": sorted(corners[k]["seed"] for k in train_keys),
                  "heldout_seeds": sorted(corners[k]["seed"] for k in heldout_keys)},
        "learning": learning,
        "memory": {"learned_q_value_count": len(q_values), "failure_memory_count": len(failures),
                   "persistent_performance_memory": memory_snapshot(train_rows, decisions)},
        "decisions": decisions,
        "summary": {"heldout_cases": len(decisions), "safe_cases": sum(item["decision"]["reliable"] for item in decisions),
                     "analog_cases": len(analog), "fallback_cases": len(decisions) - len(analog),
                     "ledger_evidence_lookups": observed_evidence_lookups,
                     "exhaustive_unique_ledger_evidence_lookups": exhaustive_evaluations,
                     "ledger_evidence_lookup_reduction": exhaustive_evaluations - observed_evidence_lookups,
                     "ledger_evidence_lookup_reduction_fraction": (exhaustive_evaluations - observed_evidence_lookups) / exhaustive_evaluations if exhaustive_evaluations else 0.0},
        "experiment_execution": {
            "mode": "offline_precomputed_ledger_replay",
            "simulator_calls": 0,
            "baseline_simulator_calls": 0,
            "simulator_call_reduction": None,
            "claim": "Counts are lookups into previously executed candidate evidence; this loop launches no simulator experiments.",
        },
        "promotion": {"status": "rejected", "reason": "learned loop is not promoted until it demonstrates a reproducible held-out improvement over the bound runtime policy while preserving fallback safety", "rollback_action": "digital_fallback"},
        "status": "passed" if safe else "blocked",
        "claim_boundary": "End-to-end offline tabular-Q RSI loop over typed simulator evidence; modeled cost only, not deep RL, hardware, measured energy, silicon, or production evidence."
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "summary": result["summary"], "promotion": result["promotion"]}, indent=2, sort_keys=True))
    return 0 if safe else 1


if __name__ == "__main__":
    raise SystemExit(main())
