#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class TrialResult:
    margin: float
    top_flipped: bool
    l1_probability_movement: float
    output_relative_error: float


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def norm(a: list[float]) -> float:
    return math.sqrt(sum(x * x for x in a))


def softmax(scores: list[float]) -> list[float]:
    peak = max(scores)
    exps = [math.exp(score - peak) for score in scores]
    total = sum(exps)
    return [value / total for value in exps]


def weighted_sum(weights: list[float], values: list[list[float]]) -> list[float]:
    width = len(values[0])
    out = [0.0] * width
    for weight, vector in zip(weights, values):
        for i, value in enumerate(vector):
            out[i] += weight * value
    return out


def make_attention_case(rng: random.Random, context: int, dim: int, target_margin: float) -> tuple[list[float], list[float], list[list[float]]]:
    query = [rng.gauss(0.0, 1.0) for _ in range(dim)]
    query_norm = norm(query)
    unit_query = [x / query_norm for x in query]

    keys: list[list[float]] = []
    keys.append([2.0 * x for x in unit_query])
    keys.append([(2.0 - target_margin * math.sqrt(dim)) * x for x in unit_query])
    for _ in range(context - 2):
        keys.append([rng.gauss(0.0, 0.1) for _ in range(dim)])

    values: list[list[float]] = []
    values.append([1.0 if i == 0 else 0.0 for i in range(dim)])
    values.append([-1.0 if i == 0 else 0.0 for i in range(dim)])
    for _ in range(context - 2):
        values.append([rng.gauss(0.0, 0.3) for _ in range(dim)])
    clean_scores = [dot(query, key) / math.sqrt(dim) for key in keys]
    return query, clean_scores, values


def run_trial(rng: random.Random, clean_scores: list[float], clean_weights: list[float], clean_output: list[float], values: list[list[float]], margin: float, noise_std: float) -> TrialResult:
    noisy_scores = [score + rng.gauss(0.0, noise_std) for score in clean_scores]

    noisy_weights = softmax(noisy_scores)
    noisy_output = weighted_sum(noisy_weights, values)

    top_flipped = clean_scores.index(max(clean_scores)) != noisy_scores.index(max(noisy_scores))
    probability_movement = sum(abs(a - b) for a, b in zip(clean_weights, noisy_weights))
    output_error = norm([a - b for a, b in zip(clean_output, noisy_output)]) / max(1e-12, norm(clean_output))
    return TrialResult(margin, top_flipped, probability_movement, output_error)


def summarize(results: list[TrialResult]) -> tuple[float, float, float, float]:
    n = len(results)
    flip_rate = sum(1 for result in results if result.top_flipped) / n
    mean_prob = sum(result.l1_probability_movement for result in results) / n
    mean_out = sum(result.output_relative_error for result in results) / n
    mean_margin = sum(result.margin for result in results) / n
    return mean_margin, flip_rate, mean_prob, mean_out


def main() -> None:
    rng = random.Random(7)
    context = 128
    dim = 64
    trials = 160
    print("attention_score_noise")
    print(f"context,{context}")
    print(f"head_dim,{dim}")
    print(f"trials,{trials}")
    print()
    print("target_margin,noise_std,mean_margin,top_flip_rate,mean_l1_probability_movement,mean_output_relative_error")
    for target_margin in [0.02, 0.05, 0.10, 0.25, 0.50]:
        _, clean_scores, values = make_attention_case(rng, context, dim, target_margin)
        clean_weights = softmax(clean_scores)
        clean_output = weighted_sum(clean_weights, values)
        ranked = sorted(clean_scores, reverse=True)
        margin = ranked[0] - ranked[1]
        for noise_std in [0.01, 0.03, 0.05, 0.10]:
            results = [run_trial(rng, clean_scores, clean_weights, clean_output, values, margin, noise_std) for _ in range(trials)]
            mean_margin, flip_rate, mean_prob, mean_out = summarize(results)
            print(f"{target_margin:.2f},{noise_std:.2f},{mean_margin:.4f},{flip_rate:.4f},{mean_prob:.4f},{mean_out:.4f}")


if __name__ == "__main__":
    main()
