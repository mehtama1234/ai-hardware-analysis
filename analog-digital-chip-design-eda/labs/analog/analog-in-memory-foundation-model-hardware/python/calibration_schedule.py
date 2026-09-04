#!/usr/bin/env python3
from __future__ import annotations

import math


def residual_error(tokens_since_calibration: int, drift_per_token: float, fit_noise: float) -> float:
    drift = tokens_since_calibration * drift_per_token
    return math.sqrt(drift * drift + fit_noise * fit_noise)


def schedule_report(total_tokens: int, interval: int, samples: int, drift_per_token: float) -> dict[str, float]:
    fit_noise = 0.18 / math.sqrt(samples)
    errors = []
    calibration_events = 0
    for token in range(total_tokens):
        if token % interval == 0:
            calibration_events += 1
            age = 0
        else:
            age = token % interval
        errors.append(residual_error(age, drift_per_token, fit_noise))

    inference_work = float(total_tokens)
    calibration_work = float(calibration_events * samples)
    return {
        "interval": interval,
        "samples": samples,
        "calibration_events": calibration_events,
        "calibration_overhead": calibration_work / (inference_work + calibration_work),
        "mean_error": sum(errors) / len(errors),
        "worst_error": max(errors),
        "end_interval_error": residual_error(interval - 1, drift_per_token, fit_noise),
    }


def main() -> None:
    total_tokens = 8192
    drift_per_token = 0.000015
    print("calibration_schedule")
    print(f"total_tokens,{total_tokens}")
    print(f"drift_per_token,{drift_per_token:.8f}")
    print("relative units,not process calibrated")
    print()
    print("interval_tokens,samples,calibration_events,calibration_overhead,mean_error,worst_error,end_interval_error")
    for samples in [16, 64, 256]:
        for interval in [128, 512, 2048, 8192]:
            row = schedule_report(total_tokens, interval, samples, drift_per_token)
            print(
                f"{interval},{samples},{row['calibration_events']},"
                f"{row['calibration_overhead']:.4f},"
                f"{row['mean_error']:.5f},"
                f"{row['worst_error']:.5f},"
                f"{row['end_interval_error']:.5f}"
            )


if __name__ == "__main__":
    main()
