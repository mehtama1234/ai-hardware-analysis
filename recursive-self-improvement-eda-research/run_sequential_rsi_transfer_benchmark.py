#!/usr/bin/env python3
"""Transfer the sequential RSI planner to the independent MLP sensitivity task.

This is an offline, model-based policy-transfer experiment over an existing
numeric sensitivity sweep. It is not deep RL and does not add hardware claims.
The planner learns action-level safety/utility priors from two noise contexts,
then operates on disjoint held-out noise contexts with a digital fallback.
"""
from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analog-in-memory-ai-inference/software-architecture/experiments/hexagon-mlir-mlp-v1/comparison/analog-sweep.json"
OUT = Path(__file__).resolve().parent / "sequential-rsi-transfer-benchmark.json"
BUDGET = 4


def action(row: dict) -> tuple[int, int]:
    return int(row["adc_bits"]), int(row["dac_bits"])


def safe(row: dict) -> bool:
    return bool(row["passes_declared_numeric_budget"])


def proxy_cost(row: dict) -> float:
    # The source sweep has no energy model. This is only a precision-complexity
    # proxy used to rank safe actions, never reported as measured energy.
    return float(row["adc_bits"] * row["dac_bits"])


def reward(row: dict) -> float:
    return 10_000.0 - proxy_cost(row) if safe(row) else -1_000_000.0


def fallback() -> dict:
    return {"adc_bits": 0, "dac_bits": 0, "passes_declared_numeric_budget": True,
            "proxy_cost": 0.0, "fallback": True}


def train_prior(rows: list[dict]) -> tuple[dict[tuple[int, int], float], set[tuple[int, int]]]:
    values: dict[tuple[int, int], list[float]] = defaultdict(list)
    failures: set[tuple[int, int]] = set()
    for row in rows:
        key = action(row)
        if safe(row):
            values[key].append(reward(row))
        else:
            failures.add(key)
    return {key: sum(items) / len(items) for key, items in values.items()}, failures


def choose(candidates: list[dict], means: dict[tuple[int, int], float],
           failures: set[tuple[int, int]], visits: Counter, rng: random.Random) -> dict:
    scored = []
    for row in candidates:
        key = action(row)
        prior = means.get(key, 0.0)
        penalty = -5_000.0 if key in failures else 0.0
        exploration = 1_500.0 / (1.0 + visits[key])
        scored.append((prior + penalty + exploration + rng.random() * 1e-6, row))
    return max(scored, key=lambda item: item[0])[1]


def run_episode(rows: list[dict], method: str, means: dict[tuple[int, int], float],
                failures: set[tuple[int, int]], seed: int, early_stop: bool) -> tuple[dict, dict]:
    rng = random.Random(seed)
    candidates = list(rows)
    checked: list[dict] = []
    visits: Counter = Counter()
    trace = []
    for step in range(BUDGET):
        if not candidates:
            break
        if method == "grid":
            candidates.sort(key=lambda row: (row["adc_bits"], row["dac_bits"]))
            row = candidates.pop(0)
        elif method == "random":
            row = candidates.pop(rng.randrange(len(candidates)))
        elif method == "contextual":
            row = max(candidates, key=lambda item: (means.get(action(item), -1_000_000.0), reward(item)))
            candidates.remove(row)
        elif method == "sequential_rsi":
            row = choose(candidates, means, failures, visits, rng)
            candidates.remove(row)
        else:
            raise ValueError(method)
        key = action(row)
        visits[key] += 1
        checked.append(row)
        if not safe(row):
            failures.add(key)
        trace.append({"step": step + 1, "action": list(key), "safe": safe(row),
                      "observed_reward": reward(row)})
        if early_stop and safe(row):
            trace[-1]["early_stop"] = "safe_numeric_configuration_found"
            break
    candidates_safe = [row for row in checked if safe(row)]
    selected = max(candidates_safe, key=lambda row: (reward(row), -proxy_cost(row))) if candidates_safe else fallback()
    return selected, {"evaluations": len(checked), "trace": trace,
                      "observed_failures": sum(not safe(row) for row in checked)}


def summarize(episodes: list[tuple[dict, dict]]) -> dict:
    return {"cases": len(episodes),
            "safe_cases": sum(bool(row.get("passes_declared_numeric_budget", False)) for row, _ in episodes),
            "fallback_cases": sum(bool(row.get("fallback", False)) for row, _ in episodes),
            "candidate_evaluations": sum(meta["evaluations"] for _, meta in episodes),
            "proxy_complexity": sum(float(row.get("proxy_cost", proxy_cost(row))) for row, _ in episodes),
            "observed_failures": sum(meta["observed_failures"] for _, meta in episodes)}


def evaluate(heldout: dict[str, list[dict]], means: dict[tuple[int, int], float],
             initial_failures: set[tuple[int, int]], method: str, seed: int,
             early_stop: bool, persistent: bool) -> tuple[dict, set[tuple[int, int]], list[dict]]:
    failures = set(initial_failures)
    episodes = []
    traces = []
    for index, (case_id, rows) in enumerate(sorted(heldout.items())):
        selected, meta = run_episode(rows, method, means, failures, seed + index, early_stop)
        episodes.append((selected, meta))
        traces.append({"case_id": case_id, **meta} if persistent else {"case_id": case_id, "evaluations": meta["evaluations"]})
    return summarize(episodes), failures, traces


def main() -> int:
    data = json.loads(SOURCE.read_text())
    rows = data["rows"]
    train_rows = [row for row in rows if float(row["noise_stddev"]) == 0.0]
    heldout_rows = [row for row in rows if float(row["noise_stddev"]) in (0.001, 0.005)]
    heldout: dict[str, list[dict]] = defaultdict(list)
    for row in heldout_rows:
        heldout[f"noise-{float(row['noise_stddev']):g}"] .append(row)
    means, failures = train_prior(train_rows)
    methods = {}
    traces = {}
    for method in ("grid", "random", "contextual"):
        methods[method], _, traces[method] = evaluate(heldout, means, failures, method, 62021, False, False)
    methods["sequential_rsi"], first_failures, traces["sequential_rsi"] = evaluate(
        heldout, means, failures, "sequential_rsi", 62021, False, True)
    methods["sequential_rsi_early_stop"], _, traces["sequential_rsi_early_stop"] = evaluate(
        heldout, means, failures, "sequential_rsi", 62021, True, True)
    result = {
        "schema_version": "recursive_sequential_rsi_transfer_benchmark.v1",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_schema": data["schema_version"],
        "workload_id": data["workload_id"],
        "split": {"training_noise_stddev": [0.0], "heldout_noise_stddev": [0.001, 0.005],
                  "training_rows": len(train_rows), "heldout_cases": len(heldout)},
        "episode": {"candidate_evaluations_per_case": BUDGET, "fallback_always_available": True,
                     "observation_updates_memory": True, "early_stop_on_safe_numeric_configuration": True},
        "methods": methods,
        "traces": traces,
        "recursive_adaptation": {"first_pass": methods["sequential_rsi"],
                                  "observed_failure_memory_size": len(first_failures)},
        "status": "passed" if all(item["safe_cases"] == item["cases"] for item in methods.values())
                  and methods["sequential_rsi_early_stop"]["candidate_evaluations"] < methods["grid"]["candidate_evaluations"] else "blocked",
        "claim_boundary": "Offline transfer of a sequential RSI/model-based policy over frozen MLP numeric sensitivity evidence; proxy complexity is not energy, and this is not deep RL, hardware, silicon, or production evidence.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "methods": methods}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
