#!/usr/bin/env python3
from __future__ import annotations

import math
import random


def quantize(value: float, bits: int, low: float, high: float) -> float:
    if bits <= 0:
        raise ValueError("bits must be positive")
    if high <= low:
        raise ValueError("high must be greater than low")
    levels = (1 << bits) - 1
    clipped = min(max(value, low), high)
    code = round((clipped - low) / (high - low) * levels)
    return low + code * (high - low) / levels


def dot(row: list[float], vector: list[float]) -> float:
    return sum(weight * value for weight, value in zip(row, vector))


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [dot(row, vector) for row in matrix]


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def analog_matvec(
    matrix: list[list[float]],
    vector: list[float],
    *,
    adc_bits: int,
    dac_bits: int,
    conductance_noise: float,
    drift: float,
    seed: int,
) -> list[float]:
    rng = random.Random(seed)
    q_vector = [quantize(value, dac_bits, -1.0, 1.0) for value in vector]
    outputs: list[float] = []
    for row in matrix:
        current = 0.0
        for weight, value in zip(row, q_vector):
            programmed_weight = weight * (1.0 + rng.gauss(0.0, conductance_noise))
            drifted_weight = programmed_weight * (1.0 + drift)
            current += drifted_weight * value
        outputs.append(quantize(current, adc_bits, -4.0, 4.0))
    return outputs


def rel_error(reference: list[float], measured: list[float]) -> float:
    residual = [a - b for a, b in zip(reference, measured)]
    denom = rms(reference)
    if denom == 0:
        return rms(residual)
    return rms(residual) / denom


def gelu_like(values: list[float]) -> list[float]:
    return [0.5 * x * (1.0 + math.tanh(0.79788456 * (x + 0.044715 * x * x * x))) for x in values]


def transformer_mlp(
    x: list[float],
    up: list[list[float]],
    down: list[list[float]],
    analog: bool,
    adc_bits: int = 6,
    dac_bits: int = 6,
) -> list[float]:
    if analog:
        hidden = analog_matvec(
            up,
            x,
            adc_bits=adc_bits,
            dac_bits=dac_bits,
            conductance_noise=0.02,
            drift=0.01,
            seed=17,
        )
    else:
        hidden = matvec(up, x)
    activated = gelu_like(hidden)
    if analog:
        return analog_matvec(
            down,
            activated,
            adc_bits=adc_bits,
            dac_bits=dac_bits,
            conductance_noise=0.02,
            drift=0.01,
            seed=23,
        )
    return matvec(down, activated)


def print_row(label: str, values: list[float]) -> None:
    joined = ", ".join(f"{value: .5f}" for value in values)
    print(f"{label}: [{joined}]")


def main() -> None:
    matrix = [
        [0.8, -0.4, 0.2, 0.1],
        [-0.1, 0.7, 0.3, -0.5],
        [0.2, 0.1, -0.6, 0.9],
        [0.5, -0.2, 0.4, 0.3],
    ]
    vector = [0.25, -0.75, 0.50, 0.10]

    ideal = matvec(matrix, vector)
    analog = analog_matvec(
        matrix,
        vector,
        adc_bits=6,
        dac_bits=6,
        conductance_noise=0.02,
        drift=0.01,
        seed=7,
    )
    print("Analog matrix-vector multiply")
    print_row("ideal", ideal)
    print_row("analog", analog)
    print(f"relative_rms_error: {rel_error(ideal, analog):.5f}")

    print("\nADC bit sweep with fixed 6-bit DAC")
    print("adc_bits,relative_rms_error")
    for bits in [3, 4, 5, 6, 7, 8]:
        measured = analog_matvec(
            matrix,
            vector,
            adc_bits=bits,
            dac_bits=6,
            conductance_noise=0.02,
            drift=0.01,
            seed=11,
        )
        print(f"{bits},{rel_error(ideal, measured):.5f}")

    print("\nDrift sweep with 6-bit ADC/DAC")
    print("drift,relative_rms_error")
    for drift in [0.0, 0.01, 0.03, 0.05, 0.10]:
        measured = analog_matvec(
            matrix,
            vector,
            adc_bits=6,
            dac_bits=6,
            conductance_noise=0.02,
            drift=drift,
            seed=13,
        )
        print(f"{drift:.2f},{rel_error(ideal, measured):.5f}")

    up = [
        [0.7, -0.2, 0.1, 0.4],
        [-0.3, 0.8, 0.5, -0.1],
        [0.2, 0.6, -0.4, 0.3],
        [0.1, -0.5, 0.9, 0.2],
        [0.4, 0.2, -0.1, 0.7],
        [-0.6, 0.1, 0.3, 0.5],
    ]
    down = [
        [0.4, -0.2, 0.5, 0.1, -0.3, 0.2],
        [-0.1, 0.6, 0.2, -0.4, 0.1, 0.3],
        [0.5, 0.1, -0.2, 0.7, 0.2, -0.5],
        [0.2, -0.3, 0.4, 0.1, 0.6, -0.1],
    ]
    digital_mlp = transformer_mlp(vector, up, down, analog=False)
    analog_mlp = transformer_mlp(vector, up, down, analog=True)
    print("\nTiny transformer MLP projection")
    print_row("digital", digital_mlp)
    print_row("analog", analog_mlp)
    print(f"relative_rms_error: {rel_error(digital_mlp, analog_mlp):.5f}")


if __name__ == "__main__":
    main()
