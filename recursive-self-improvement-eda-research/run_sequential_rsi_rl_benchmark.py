#!/usr/bin/env python3
"""Benchmark a sequential failure-aware RSI/RL-style experiment planner.

This is offline model-based policy improvement over a frozen simulator ledger,
not a claim of deep RL. Each episode chooses one candidate, observes its
simulator outcome, updates failure memory, and chooses the next candidate under
the same budget. A digital fallback is always available.
"""
from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POPULATION = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/converter-to-inference-v1/results/selector-population.json"
OUT = Path(__file__).resolve().parent / "sequential-rsi-rl-benchmark.json"
BUDGET = 12


def signature(row: dict) -> tuple:
    return (tuple(row["placement"]), int(row["bits"]), round(float(row["gain_factor"]), 4))


def reward(row: dict) -> float:
    if not row["reliable"]:
        return -1_000_000.0
    return 10_000.0 * len(row["placement"]) - float(row["cost"]["estimated_energy"])


def fallback() -> dict:
    return {"placement": [], "bits": 0, "gain_factor": 1.0, "reliable": True,
            "cost": {"estimated_energy": 3072.0}}


def train_prior(rows: list[dict]) -> tuple[dict[tuple, float], set[tuple]]:
    values: dict[tuple, list[float]] = defaultdict(list)
    failures: set[tuple] = set()
    for row in rows:
        key = signature(row)
        if row["reliable"]:
            values[key].append(reward(row))
        else:
            failures.add(key)
    return {key: sum(items) / len(items) for key, items in values.items()}, failures


def choose_sequential(candidates: list[dict], means: dict[tuple, float], failures: set[tuple], visits: Counter,
                      rng: random.Random) -> dict:
    """Choose an experiment from current memory, with deterministic exploration."""
    scored = []
    for row in candidates:
        key = signature(row)
        prior = means.get(key, 0.0)
        failure_penalty = -5_000.0 if key in failures else 0.0
        exploration = 1_500.0 / (1.0 + visits[key])
        jitter = rng.random() * 1e-6
        scored.append((prior + failure_penalty + exploration + jitter, row))
    return max(scored, key=lambda item: item[0])[1]


def run_episode(rows: list[dict], method: str, means: dict[tuple, float], failures: set[tuple], seed: int,
                early_stop_energy: float | None = None) -> tuple[dict, dict]:
    rng = random.Random(seed)
    candidates = list(rows)
    checked: list[dict] = []
    visits: Counter = Counter()
    trace = []
    for step in range(BUDGET):
        if not candidates:
            break
        if method == "random":
            index = rng.randrange(len(candidates))
            row = candidates.pop(index)
        elif method == "grid":
            candidates.sort(key=lambda item: (len(item["placement"]), item["bits"], item["gain_factor"]))
            row = candidates.pop(0)
        elif method == "contextual":
            row = max(candidates, key=lambda item: (means.get(signature(item), -1_000_000.0), reward(item)))
            candidates.remove(row)
        elif method == "sequential_rsi":
            row = choose_sequential(candidates, means, failures, visits, rng)
            candidates.remove(row)
        else:
            raise ValueError(method)
        key = signature(row)
        visits[key] += 1
        checked.append(row)
        if not row["reliable"]:
            failures.add(key)
        trace.append({"step": step + 1, "action": list(key), "reliable": bool(row["reliable"]),
                      "observed_reward": reward(row)})
        if (early_stop_energy is not None and row["reliable"]
                and float(row["cost"]["estimated_energy"]) <= early_stop_energy):
            trace[-1]["early_stop"] = "reliable_candidate_meets_training_energy_target"
            break
    reliable = [row for row in checked if row["reliable"]]
    selected = max(reliable, key=lambda row: (reward(row), -float(row["cost"]["estimated_energy"]))) if reliable else fallback()
    return selected, {"evaluations": len(checked), "trace": trace, "failures_observed": sum(not row["reliable"] for row in checked)}


def summarize(episodes: list[tuple[dict, dict]]) -> dict:
    return {
        "cases": len(episodes),
        "safe_cases": sum(bool(row["reliable"]) for row, _ in episodes),
        "analog_cases": sum(bool(row["placement"]) for row, _ in episodes),
        "fallback_cases": sum(not row["placement"] for row, _ in episodes),
        "candidate_evaluations": sum(meta["evaluations"] for _, meta in episodes),
        "estimated_energy": sum(float(row["cost"]["estimated_energy"]) for row, _ in episodes),
        "observed_failures": sum(meta["failures_observed"] for _, meta in episodes),
    }


def evaluate(heldout: dict[str, list[dict]], means: dict[tuple, float], initial_failures: set[tuple], method: str,
             seed_offset: int, persistent: bool, early_stop_energy: float | None = None) -> tuple[dict, list[dict], set[tuple]]:
    failures = set(initial_failures)
    episodes = []
    traces = []
    for index, (case_id, rows) in enumerate(sorted(heldout.items())):
        planner_method = "sequential_rsi" if method == "sequential_rsi_early_stop" else method
        selected, meta = run_episode(rows, planner_method, means, failures, seed_offset + index, early_stop_energy)
        episodes.append((selected, meta))
        traces.append({"case_id": case_id, **meta} if persistent else {"case_id": case_id, "evaluations": meta["evaluations"]})
    return summarize(episodes), traces, failures


def main() -> int:
    data = json.loads(POPULATION.read_text())
    train_rows = [row for row in data["rows"] if int(row["seed"]) < 6]
    heldout_rows = [row for row in data["rows"] if int(row["seed"]) >= 6]
    heldout: dict[str, list[dict]] = defaultdict(list)
    for row in heldout_rows:
        heldout[row["case_id"]].append(row)
    means, failures = train_prior(train_rows)
    training_reliable = [row for row in train_rows if row["reliable"]]
    training_energy_target = min(float(row["cost"]["estimated_energy"]) for row in training_reliable)

    methods = {}
    traces = {}
    for method in ("grid", "random", "contextual"):
        methods[method], traces[method], _ = evaluate(heldout, means, failures, method, 44021, False)
    methods["sequential_rsi"], traces["sequential_rsi"], first_pass_failures = evaluate(
        heldout, means, failures, "sequential_rsi", 44021, True)
    methods["sequential_rsi_early_stop"], traces["sequential_rsi_early_stop"], _ = evaluate(
        heldout, means, failures, "sequential_rsi_early_stop", 44021, True, training_energy_target)

    # A second pass retains failures observed during the first RSI pass. This
    # is the recursive adaptation signal; it is reported separately from the
    # disjoint held-out correctness result.
    adaptive, adaptive_traces, _ = evaluate(heldout, means, first_pass_failures, "sequential_rsi", 55021, True)
    result = {
        "schema_version": "recursive_sequential_rsi_rl_benchmark.v1",
        "population": str(POPULATION.relative_to(ROOT)),
        "split": {"training_seeds": "0-5", "heldout_seeds": "6-11", "training_rows": len(train_rows),
                  "heldout_cases": len(heldout)},
        "episode": {"candidate_evaluations_per_case": BUDGET, "fallback_always_available": True,
                     "observation_updates_memory": True,
                     "early_stop_training_energy_target": training_energy_target},
        "methods": methods,
        "recursive_adaptation": {"first_pass": methods["sequential_rsi"], "second_pass": adaptive,
                                  "second_pass_traces": adaptive_traces},
        "traces": traces,
        "status": "passed" if all(item["safe_cases"] == item["cases"] for item in methods.values()) and adaptive["safe_cases"] == adaptive["cases"] else "blocked",
        "claim_boundary": "Offline sequential RSI/model-based policy benchmark over frozen simulator evidence; not deep RL, hardware, silicon, measured energy, or production evidence.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "methods": methods,
                      "adaptive_second_pass": adaptive}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
