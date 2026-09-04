#!/usr/bin/env python3
from __future__ import annotations

import math
import random


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * pct)))
    return ordered[index]


class Tile:
    def __init__(self, columns: int, seed: int) -> None:
        rng = random.Random(seed)
        self.columns = columns
        self.age = [0 for _ in range(columns)]
        self.bias = [rng.gauss(0.0, 0.008) for _ in range(columns)]
        self.drift_rate = [abs(rng.gauss(0.000012, 0.000008)) for _ in range(columns)]
        for index in [5, 17, 42, 53]:
            self.drift_rate[index] *= 5.0

    def step(self, tokens: int) -> None:
        self.age = [age + tokens for age in self.age]

    def true_errors(self) -> list[float]:
        return [abs(bias + drift * age) for bias, drift, age in zip(self.bias, self.drift_rate, self.age)]

    def health_scores(self, rng: random.Random, probe_noise: float) -> list[float]:
        return [error + rng.gauss(0.0, probe_noise) for error in self.true_errors()]

    def recalibrate(self, columns: list[int], rng: random.Random, fit_noise: float) -> None:
        for column in columns:
            self.age[column] = 0
            self.bias[column] = rng.gauss(0.0, fit_noise)


def run_policy(policy: str, seed: int) -> dict[str, float]:
    rng = random.Random(seed)
    tile = Tile(columns=64, seed=seed + 1)
    total_tokens = 8192
    probe_interval = 512
    samples_per_column = 32
    fit_noise = 0.08 / math.sqrt(samples_per_column)
    probe_noise = 0.006
    selected_columns = 8
    calibration_work = 0

    for token in range(0, total_tokens, probe_interval):
        tile.step(probe_interval)
        if policy == "none":
            continue
        if policy == "full_fixed":
            chosen = list(range(tile.columns))
        elif policy == "selective":
            scores = tile.health_scores(rng, probe_noise)
            chosen = sorted(range(tile.columns), key=lambda idx: scores[idx], reverse=True)[:selected_columns]
        elif policy == "selective_plus_sweep":
            if token and token % 2048 == 0:
                chosen = list(range(tile.columns))
            else:
                scores = tile.health_scores(rng, probe_noise)
                chosen = sorted(range(tile.columns), key=lambda idx: scores[idx], reverse=True)[:selected_columns]
        else:
            raise ValueError(f"unknown policy {policy!r}")
        tile.recalibrate(chosen, rng, fit_noise)
        calibration_work += len(chosen) * samples_per_column

    errors = tile.true_errors()
    bad_threshold = 0.075
    return {
        "calibration_work": calibration_work,
        "mean_error": mean(errors),
        "p95_error": percentile(errors, 0.95),
        "worst_error": max(errors),
        "bad_columns": sum(1 for error in errors if error > bad_threshold),
    }


def main() -> None:
    print("tile_health_monitor")
    print("columns,64")
    print("total_tokens,8192")
    print("probe_interval,512")
    print("samples_per_column,32")
    print()
    print("policy,calibration_work,mean_error,p95_error,worst_error,bad_columns")
    for policy in ["none", "full_fixed", "selective", "selective_plus_sweep"]:
        rows = [run_policy(policy, 3000 + trial) for trial in range(40)]
        print(
            f"{policy},"
            f"{mean([row['calibration_work'] for row in rows]):.1f},"
            f"{mean([row['mean_error'] for row in rows]):.5f},"
            f"{mean([row['p95_error'] for row in rows]):.5f},"
            f"{mean([row['worst_error'] for row in rows]):.5f},"
            f"{mean([row['bad_columns'] for row in rows]):.2f}"
        )


if __name__ == "__main__":
    main()
