#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path

from analog_tile_error_evidence import matvec, q8, quantize, rms


MEASUREMENTS_DIR = Path(__file__).resolve().parents[1] / "measurements"
CSV_OUT = MEASUREMENTS_DIR / "analog-tile-state-trace.csv"
MD_OUT = MEASUREMENTS_DIR / "analog-tile-state-trace.md"


@dataclass
class TileState:
    gain: list[float]
    bias: list[float]
    drift_rate: list[float]
    age: int = 0


@dataclass(frozen=True)
class Row:
    token: int
    event: str
    adc_bits: int
    dac_bits: int
    calibration_age: int
    mean_abs_gain_error: float
    mean_abs_bias: float
    residual_abs: float
    residual_q8: int
    drift_age: int
    sensitivity_q8: int
    cumulative_error_q8: int
    governor_decision: str
    governor_reason: str
    next_cumulative_error_q8: int


def make_tile(columns: int, seed: int) -> TileState:
    rng = random.Random(seed)
    gain = [1.0 + rng.gauss(0.0, 0.018) for _ in range(columns)]
    bias = [rng.gauss(0.0, 0.012) for _ in range(columns)]
    drift_rate = [abs(rng.gauss(0.0018, 0.0005)) for _ in range(columns)]
    drift_rate[-1] *= 2.4
    return TileState(gain=gain, bias=bias, drift_rate=drift_rate)


def analog_measure(matrix: list[list[float]], vector: list[float], tile: TileState, adc_bits: int, dac_bits: int) -> list[float]:
    q_vector = [quantize(value, dac_bits, -1.0, 1.0) for value in vector]
    measured: list[float] = []
    rows = max(1, len(vector) - 1)
    for col, weights in enumerate(matrix):
        current = 0.0
        for row_idx, (weight, value) in enumerate(zip(weights, q_vector)):
            wire_scale = 1.0 - 0.018 * (row_idx / rows)
            drifted_gain = tile.gain[col] + tile.drift_rate[col] * tile.age
            current += (weight * drifted_gain) * (value * wire_scale)
        current += tile.bias[col]
        measured.append(quantize(current, adc_bits, -4.0, 4.0))
    return measured


def calibrate(tile: TileState, seed: int, columns: list[int] | None = None) -> None:
    rng = random.Random(seed)
    chosen = list(range(len(tile.gain))) if columns is None else columns
    for col in chosen:
        tile.gain[col] = 1.0 + rng.gauss(0.0, 0.006)
        tile.bias[col] = rng.gauss(0.0, 0.004)
    tile.age = 0


def govern(residual_q8: int, drift_age: int, sensitivity_q8: int, cumulative_error_q8: int) -> tuple[str, str, int]:
    if residual_q8 > 46:
        return "digital", "residual_too_high", cumulative_error_q8
    if drift_age > 11:
        return "recalibrate", "calibration_too_old", cumulative_error_q8
    if sensitivity_q8 >= 192 and residual_q8 > 24:
        return "digital", "sensitive_path_needs_digital", cumulative_error_q8
    risk_q8 = residual_q8 + (drift_age * 3) + (sensitivity_q8 >> 4)
    next_error = min(255, cumulative_error_q8 + (risk_q8 >> 2))
    if next_error > 96:
        return "recalibrate", "state_error_budget_spent", cumulative_error_q8
    if drift_age >= 9 or next_error >= 80:
        return "analog", "analog_but_recalibrate_soon", next_error
    return "analog", "analog_within_budget", next_error


def simulate(tokens: int = 36) -> list[Row]:
    matrix = [
        [0.80, -0.40, 0.20, 0.10],
        [-0.10, 0.70, 0.30, -0.50],
        [0.20, 0.10, -0.60, 0.90],
        [0.50, -0.20, 0.40, 0.30],
    ]
    vector_pattern = [
        [0.25, -0.75, 0.50, 0.10],
        [0.10, -0.20, 0.80, -0.35],
        [-0.60, 0.45, 0.20, 0.70],
        [0.90, -0.10, -0.30, 0.15],
    ]
    tile = make_tile(columns=len(matrix), seed=9001)
    rows: list[Row] = []
    cumulative = 0
    adc_bits = 6
    dac_bits = 6
    sensitivity_pattern = [90, 140, 210, 150, 120, 230, 160, 100]

    for token in range(tokens):
        event = "serve"
        if token in {0, 14, 25}:
            calibrate(tile, seed=9100 + token)
            event = "full_calibration"
        elif token in {9, 20}:
            worst = max(range(len(tile.gain)), key=lambda col: abs(tile.bias[col]) + abs(tile.gain[col] - 1.0))
            calibrate(tile, seed=9200 + token, columns=[worst])
            event = f"column_{worst}_calibration"

        vector = vector_pattern[token % len(vector_pattern)]
        ideal = matvec(matrix, vector)
        measured = analog_measure(matrix, vector, tile, adc_bits, dac_bits)
        residual = rms([actual - expected for actual, expected in zip(measured, ideal)])
        relative = residual / rms(ideal) if rms(ideal) else residual
        residual_q8 = q8(relative, 128.0)
        sensitivity_q8 = sensitivity_pattern[token % len(sensitivity_pattern)]
        decision, reason, next_cumulative = govern(residual_q8, tile.age, sensitivity_q8, cumulative)
        rows.append(
            Row(
                token=token,
                event=event,
                adc_bits=adc_bits,
                dac_bits=dac_bits,
                calibration_age=tile.age,
                mean_abs_gain_error=sum(abs(value - 1.0) for value in tile.gain) / len(tile.gain),
                mean_abs_bias=sum(abs(value) for value in tile.bias) / len(tile.bias),
                residual_abs=residual,
                residual_q8=residual_q8,
                drift_age=tile.age,
                sensitivity_q8=sensitivity_q8,
                cumulative_error_q8=cumulative,
                governor_decision=decision,
                governor_reason=reason,
                next_cumulative_error_q8=next_cumulative,
            )
        )
        if decision == "analog":
            cumulative = next_cumulative
        elif decision == "recalibrate":
            cumulative = min(cumulative, 24)
        tile.age += 1
    return rows


def write_csv(rows: list[Row]) -> None:
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_markdown(rows: list[Row]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.governor_reason] = counts.get(row.governor_reason, 0) + 1
    lines = [
        "# Analog Tile State Trace",
        "",
        "This trace follows one analog tile over a token stream. The object is not a static dot-product error. The object is tile state: programmed gain, bias, drift age, calibration events, residual error, and the governor decision that follows from them.",
        "",
        "## Reason Counts",
        "",
    ]
    for reason in sorted(counts):
        lines.append(f"- {reason}: {counts[reason]}")
    lines.extend(
        [
            "",
            "## Trace",
            "",
            "| token | event | age | gain error | bias | residual q8 | sensitivity q8 | cumulative | decision | reason | next cumulative |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row.token} | {row.event} | {row.calibration_age} | {row.mean_abs_gain_error:.4f} | "
            f"{row.mean_abs_bias:.4f} | {row.residual_q8} | {row.sensitivity_q8} | "
            f"{row.cumulative_error_q8} | {row.governor_decision} | {row.governor_reason} | "
            f"{row.next_cumulative_error_q8} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "A tile is not healthy or unhealthy forever. It moves. Calibration pulls gain and bias back toward the intended dot-product map. Drift pushes them away as tokens pass. The governor should therefore read tile state as a moving measurement, not as a fixed label.",
            "",
            "The residual is the visible error at the model boundary. The age is a warning that the visible error may grow. The cumulative budget remembers how much accepted analog error has already entered model state. A useful analog accelerator joins all three. It does not ask only whether the crossbar worked once; it asks whether this tile, at this age, with this residual, on this model path, can be trusted for the next token.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = simulate()
    write_csv(rows)
    write_markdown(rows)
    print("analog_tile_state_trace")
    print(f"tokens,{len(rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
