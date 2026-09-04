#!/usr/bin/env python3
from __future__ import annotations

import math
import random


def sar_convert(value: float, bits: int, low: float, high: float, comparator_noise: float, rng: random.Random) -> tuple[int, float]:
    code = 0
    for bit in reversed(range(bits)):
        trial = code | (1 << bit)
        trial_value = low + trial * (high - low) / ((1 << bits) - 1)
        observed = value + rng.gauss(0.0, comparator_noise)
        if observed >= trial_value:
            code = trial
    reconstructed = low + code * (high - low) / ((1 << bits) - 1)
    return code, reconstructed


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def main() -> None:
    rng = random.Random(41)
    samples = [rng.uniform(-1.0, 1.0) for _ in range(512)]

    print("sar_adc_sweep")
    print("bits,comparator_noise,rms_error")
    for bits in [3, 4, 5, 6, 7, 8, 10]:
        for noise in [0.0, 0.002, 0.01, 0.03]:
            errors = []
            local_rng = random.Random(1000 + bits * 17 + int(noise * 10000))
            for value in samples:
                _, reconstructed = sar_convert(value, bits, -1.0, 1.0, noise, local_rng)
                errors.append(value - reconstructed)
            print(f"{bits},{noise:.3f},{rms(errors):.6f}")

    print("\nconversion_time_model")
    print("columns,bits,total_comparisons")
    for columns in [64, 128, 256, 512]:
        for bits in [4, 6, 8]:
            print(f"{columns},{bits},{columns * bits}")

    print("\nInterpretation")
    print("More bits reduce quantization error only while comparator noise is below the code step.")
    print("A column-parallel tile pays one comparison per bit per column unless it shares ADCs over time.")


if __name__ == "__main__":
    main()
