#!/usr/bin/env python3
from __future__ import annotations

import math
import random


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(w * x for w, x in zip(row, vector)) for row in matrix]


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def rel_error(reference: list[float], measured: list[float]) -> float:
    residual = [a - b for a, b in zip(reference, measured)]
    denom = rms(reference)
    return rms(residual) / denom if denom else rms(residual)


def topk_residual(reference: list[float], measured: list[float], k: int) -> list[float]:
    residual = [a - b for a, b in zip(reference, measured)]
    order = sorted(range(len(residual)), key=lambda idx: abs(residual[idx]), reverse=True)
    corrected = measured[:]
    for idx in order[:k]:
        corrected[idx] += residual[idx]
    return corrected


def noisy_analog(matrix: list[list[float]], vector: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    result = []
    for row in matrix:
        value = 0.0
        for weight, activation in zip(row, vector):
            programmed = weight * (1.0 + rng.gauss(0.0, 0.04))
            value += programmed * activation
        value = value * (1.0 + rng.gauss(0.0, 0.03)) + rng.gauss(0.0, 0.025)
        result.append(value)
    return result


def main() -> None:
    rng = random.Random(19)
    width = 16
    matrix = [[rng.uniform(-0.8, 0.8) for _ in range(width)] for _ in range(width)]
    vectors = [[rng.uniform(-1.0, 1.0) for _ in range(width)] for _ in range(24)]

    print("Digital residual correction")
    print("topk_corrected_outputs,mean_relative_error")
    for k in [0, 1, 2, 4, 8, 16]:
        errors = []
        for sample_idx, vector in enumerate(vectors):
            reference = matvec(matrix, vector)
            measured = noisy_analog(matrix, vector, seed=100 + sample_idx)
            corrected = topk_residual(reference, measured, k)
            errors.append(rel_error(reference, corrected))
        print(f"{k},{sum(errors) / len(errors):.5f}")

    print("\nInterpretation")
    print("The residual path spends digital work only on the largest output errors.")
    print("It is useful when most analog outputs are close and a small tail dominates damage.")


if __name__ == "__main__":
    main()
