#!/usr/bin/env python3
from __future__ import annotations

import math
import random


def quantize(value: float, bits: int, low: float, high: float) -> float:
    levels = (1 << bits) - 1
    clipped = min(max(value, low), high)
    code = round((clipped - low) / (high - low) * levels)
    return low + code * (high - low) / levels


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(w * x for w, x in zip(row, vector)) for row in matrix]


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def rel_error(reference: list[float], measured: list[float]) -> float:
    residual = [a - b for a, b in zip(reference, measured)]
    denom = rms(reference)
    return rms(residual) / denom if denom else rms(residual)


def drive_rows(
    vector: list[float],
    *,
    bits: int,
    gain_error: float,
    offset_error: float,
    settling_fraction: float,
    rng: random.Random,
) -> list[float]:
    driven = []
    for value in vector:
        quantized = quantize(value, bits, -1.0, 1.0)
        gain = 1.0 + rng.gauss(0.0, gain_error)
        offset = rng.gauss(0.0, offset_error)
        settled = settling_fraction * quantized
        driven.append(gain * settled + offset)
    return driven


def main() -> None:
    matrix = [
        [0.8, -0.4, 0.2, 0.1],
        [-0.1, 0.7, 0.3, -0.5],
        [0.2, 0.1, -0.6, 0.9],
        [0.5, -0.2, 0.4, 0.3],
    ]
    vector = [0.25, -0.75, 0.50, 0.10]
    reference = matvec(matrix, vector)

    print("dac_row_driver_sweep")
    print("bits,gain_error,offset_error,settling_fraction,relative_error")
    for bits in [3, 4, 5, 6, 8]:
        for settling in [1.0, 0.98, 0.95, 0.90]:
            rng = random.Random(200 + bits * 13 + int(settling * 100))
            driven = drive_rows(
                vector,
                bits=bits,
                gain_error=0.01,
                offset_error=0.005,
                settling_fraction=settling,
                rng=rng,
            )
            measured = matvec(matrix, driven)
            print(f"{bits},0.010,0.005,{settling:.2f},{rel_error(reference, measured):.5f}")

    print("\nrow_error_correlation")
    print("row,row_voltage_error,output_error_contribution")
    rng = random.Random(77)
    driven = drive_rows(
        vector,
        bits=6,
        gain_error=0.02,
        offset_error=0.01,
        settling_fraction=0.97,
        rng=rng,
    )
    for row_idx, (ideal, actual) in enumerate(zip(vector, driven)):
        row_error = actual - ideal
        contribution = [matrix[out_idx][row_idx] * row_error for out_idx in range(len(matrix))]
        print(f"{row_idx},{row_error:.6f}," + ",".join(f"{value:.6f}" for value in contribution))

    print("\nInterpretation")
    print("DAC error enters before current summation, so one bad row voltage affects many output columns.")
    print("Settling error behaves like input scaling and cannot be fixed by simply adding more ADC bits.")


if __name__ == "__main__":
    main()
