#!/usr/bin/env python3
from __future__ import annotations

import math
import random


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def rel_error(reference: list[float], measured: list[float]) -> float:
    return rms([a - b for a, b in zip(reference, measured)]) / max(1e-12, rms(reference))


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [dot(row, vector) for row in matrix]


def add(a: list[float], b: list[float]) -> list[float]:
    return [x + y for x, y in zip(a, b)]


def tanh_vec(values: list[float]) -> list[float]:
    return [math.tanh(value) for value in values]


def make_matrix(rng: random.Random, dim: int) -> list[list[float]]:
    return [[rng.gauss(0.0, 0.16) for _ in range(dim)] for _ in range(dim)]


def block(x: list[float], matrix: list[list[float]]) -> list[float]:
    update = tanh_vec(matvec(matrix, x))
    return add(x, update)


def noisy_block(
    x: list[float],
    matrix: list[list[float]],
    rng: random.Random,
    random_noise: float,
    stable_bias: list[float],
) -> list[float]:
    clean_update = tanh_vec(matvec(matrix, x))
    noisy_update = [
        value + rng.gauss(0.0, random_noise) + bias
        for value, bias in zip(clean_update, stable_bias)
    ]
    return add(x, noisy_update)


def run_stack(depth: int, random_noise: float, bias_size: float, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    dim = 24
    clean = [rng.gauss(0.0, 0.3) for _ in range(dim)]
    noisy = list(clean)
    bias_direction = [rng.gauss(0.0, 1.0) for _ in range(dim)]
    bias_norm = rms(bias_direction)
    stable_bias = [bias_size * value / bias_norm for value in bias_direction]

    for _ in range(depth):
        matrix = make_matrix(rng, dim)
        clean = block(clean, matrix)
        noisy = noisy_block(noisy, matrix, rng, random_noise, stable_bias)

    diff = [a - b for a, b in zip(noisy, clean)]
    return rel_error(clean, noisy), mean(diff)


def summarize(depth: int, random_noise: float, bias_size: float) -> tuple[float, float]:
    rows = [run_stack(depth, random_noise, bias_size, 2000 + i) for i in range(24)]
    return mean([row[0] for row in rows]), mean([row[1] for row in rows])


def main() -> None:
    print("multilayer_error_drift")
    print("hidden,24")
    print("trials,24")
    print()
    print("case,depth,random_noise,bias_size,relative_state_error,mean_signed_error")
    cases = [
        ("random_only", 0.03, 0.00),
        ("stable_bias_only", 0.00, 0.03),
        ("random_plus_bias", 0.02, 0.02),
    ]
    for case, random_noise, bias_size in cases:
        for depth in [1, 4, 8, 16]:
            error, signed = summarize(depth, random_noise, bias_size)
            print(f"{case},{depth},{random_noise:.2f},{bias_size:.2f},{error:.4f},{signed:.5f}")


if __name__ == "__main__":
    main()
