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


def quantize(value: float, bits: int, low: float, high: float) -> float:
    levels = (1 << bits) - 1
    clipped = min(max(value, low), high)
    code = round((clipped - low) / (high - low) * levels)
    return low + code * (high - low) / levels


class AnalogTile:
    def __init__(
        self,
        matrix: list[list[float]],
        *,
        conductance_noise: float,
        column_gain_noise: float,
        column_offset_noise: float,
        seed: int,
    ) -> None:
        rng = random.Random(seed)
        self.matrix = [
            [w * (1.0 + rng.gauss(0.0, conductance_noise)) for w in row]
            for row in matrix
        ]
        self.gain = [1.0 + rng.gauss(0.0, column_gain_noise) for _ in matrix]
        self.offset = [rng.gauss(0.0, column_offset_noise) for _ in matrix]

    def read(self, vector: list[float], *, adc_bits: int, dac_bits: int) -> list[float]:
        q_vector = [quantize(v, dac_bits, -1.0, 1.0) for v in vector]
        raw = matvec(self.matrix, q_vector)
        sensed = [self.gain[i] * value + self.offset[i] for i, value in enumerate(raw)]
        return [quantize(value, adc_bits, -4.0, 4.0) for value in sensed]


def fit_gain_bias(reference_samples: list[list[float]], measured_samples: list[list[float]]) -> tuple[list[float], list[float]]:
    columns = len(reference_samples[0])
    gains: list[float] = []
    biases: list[float] = []
    for j in range(columns):
        xs = [measured[j] for measured in measured_samples]
        ys = [reference[j] for reference in reference_samples]
        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)
        var_x = sum((x - mean_x) ** 2 for x in xs)
        cov_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        gain = cov_xy / var_x if var_x else 1.0
        bias = mean_y - gain * mean_x
        gains.append(gain)
        biases.append(bias)
    return gains, biases


def apply_gain_bias(values: list[float], gains: list[float], biases: list[float]) -> list[float]:
    return [g * value + b for value, g, b in zip(values, gains, biases)]


def random_vector(rng: random.Random, size: int) -> list[float]:
    return [rng.uniform(-1.0, 1.0) for _ in range(size)]


def energy_estimate(
    *,
    rows: int,
    cols: int,
    adc_bits: int,
    dac_bits: int,
    tiles: int,
    tokens: int,
) -> dict[str, float]:
    # Relative units, not joules. The point is the scaling, not a process claim.
    array_mac = rows * cols * tiles * tokens * 0.05
    dac = rows * tiles * tokens * (2 ** dac_bits) * 0.002
    adc = cols * tiles * tokens * (2 ** adc_bits) * 0.006
    digital_accum = cols * tiles * tokens * math.log2(max(2, rows)) * 0.03
    memory = (rows + cols) * tiles * tokens * 0.12
    return {
        "array_mac": array_mac,
        "dac": dac,
        "adc": adc,
        "digital_accum": digital_accum,
        "memory": memory,
        "total": array_mac + dac + adc + digital_accum + memory,
    }


def main() -> None:
    matrix = [
        [0.8, -0.4, 0.2, 0.1],
        [-0.1, 0.7, 0.3, -0.5],
        [0.2, 0.1, -0.6, 0.9],
        [0.5, -0.2, 0.4, 0.3],
    ]
    rng = random.Random(5)
    tile = AnalogTile(
        matrix,
        conductance_noise=0.03,
        column_gain_noise=0.08,
        column_offset_noise=0.04,
        seed=31,
    )

    calibration_inputs = [random_vector(rng, 4) for _ in range(48)]
    reference_samples = [matvec(matrix, vector) for vector in calibration_inputs]
    measured_samples = [tile.read(vector, adc_bits=7, dac_bits=7) for vector in calibration_inputs]
    gains, biases = fit_gain_bias(reference_samples, measured_samples)

    test_inputs = [random_vector(rng, 4) for _ in range(32)]
    before_errors = []
    after_errors = []
    for vector in test_inputs:
        reference = matvec(matrix, vector)
        measured = tile.read(vector, adc_bits=7, dac_bits=7)
        corrected = apply_gain_bias(measured, gains, biases)
        before_errors.append(rel_error(reference, measured))
        after_errors.append(rel_error(reference, corrected))

    print("Calibration experiment")
    print(f"mean_relative_error_before,{sum(before_errors) / len(before_errors):.5f}")
    print(f"mean_relative_error_after,{sum(after_errors) / len(after_errors):.5f}")
    print("per_output_gain," + ",".join(f"{value:.5f}" for value in gains))
    print("per_output_bias," + ",".join(f"{value:.5f}" for value in biases))

    print("\nADC/DAC relative energy model")
    print("adc_bits,dac_bits,array_mac,dac,adc,digital_accum,memory,total")
    for bits in [4, 5, 6, 7, 8]:
        energy = energy_estimate(rows=128, cols=128, adc_bits=bits, dac_bits=bits, tiles=16, tokens=256)
        print(
            f"{bits},{bits},"
            f"{energy['array_mac']:.1f},{energy['dac']:.1f},{energy['adc']:.1f},"
            f"{energy['digital_accum']:.1f},{energy['memory']:.1f},{energy['total']:.1f}"
        )

    print("\nTransformer partition sketch")
    print("operation,analog_candidate,reason")
    rows = [
        ("qkv_projection", "yes", "dense reused linear map"),
        ("attention_scores", "partial", "matrix product but sequence-dependent data movement"),
        ("softmax", "no", "normalization and exponentials need controlled digital range"),
        ("mlp_up_down", "yes", "large dense projections with high reuse"),
        ("kv_cache", "no", "addressing and memory traffic problem"),
        ("residual_add", "digital", "cheap exact accumulation and correction point"),
    ]
    for name, candidate, reason in rows:
        print(f"{name},{candidate},{reason}")


if __name__ == "__main__":
    main()
