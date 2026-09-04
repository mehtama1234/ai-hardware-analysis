#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path


MEASUREMENTS_DIR = Path(__file__).resolve().parents[1] / "measurements"
CSV_OUT = MEASUREMENTS_DIR / "analog-tile-error-evidence.csv"
MD_OUT = MEASUREMENTS_DIR / "analog-tile-error-evidence.md"
ROW_DROP_CSV = MEASUREMENTS_DIR / "spice-row-drop-comparison.csv"


@dataclass(frozen=True)
class Scenario:
    name: str
    adc_bits: int
    dac_bits: int
    program_sigma: float
    drift: float
    row_drop_case_ohm: float
    sensitivity: float
    calibration_age: int


@dataclass(frozen=True)
class Row:
    scenario: str
    adc_bits: int
    dac_bits: int
    program_sigma_pct: float
    drift_pct: float
    row_drop_case_ohm: float
    spice_row_drop_loss_pct: float
    far_row_voltage_scale: float
    calibration_age: int
    ideal_rms: float
    analog_rms: float
    residual_abs: float
    residual_q8: int
    drift_age: int
    sensitivity_q8: int
    analog_candidate: int
    governor_input_meaning: str


def quantize(value: float, bits: int, low: float, high: float) -> float:
    levels = (1 << bits) - 1
    clipped = min(max(value, low), high)
    code = round((clipped - low) / (high - low) * levels)
    return low + code * (high - low) / levels


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(weight * value for weight, value in zip(row, vector)) for row in matrix]


def load_spice_row_drop_losses() -> dict[float, float]:
    if not ROW_DROP_CSV.exists():
        from spice_row_drop_comparison import main as write_row_drop_measurements

        write_row_drop_measurements()
    with ROW_DROP_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"no row-drop measurements found in {ROW_DROP_CSV}")
    return {
        float(row["rseg_ohm"]): float(row["row_drop_current_loss_pct"]) / 100.0
        for row in rows
    }


def row_drop_loss_for_case(losses: dict[float, float], rseg_ohm: float) -> float:
    try:
        return losses[rseg_ohm]
    except KeyError as exc:
        available = ", ".join(str(key) for key in sorted(losses))
        raise ValueError(f"row-drop case {rseg_ohm} ohm missing from SPICE measurements; available: {available}") from exc


def analog_matvec(
    matrix: list[list[float]],
    vector: list[float],
    scenario: Scenario,
    row_drop_loss: float,
    seed: int,
) -> list[float]:
    rng = random.Random(seed)
    q_vector = [quantize(value, scenario.dac_bits, -1.0, 1.0) for value in vector]
    outputs: list[float] = []
    rows = max(1, len(vector) - 1)
    for out_col, weights in enumerate(matrix):
        current = 0.0
        for row_idx, (weight, value) in enumerate(zip(weights, q_vector)):
            wire_scale = 1.0 - row_drop_loss * (row_idx / rows)
            programmed = weight * (1.0 + rng.gauss(0.0, scenario.program_sigma))
            drifted = programmed * (1.0 + scenario.drift)
            current += drifted * (value * wire_scale)
        # Small deterministic column offset stands in for local ADC/reference mismatch.
        current += (out_col - 1.5) * scenario.program_sigma * 0.08
        outputs.append(quantize(current, scenario.adc_bits, -4.0, 4.0))
    return outputs


def q8(value: float, scale: float) -> int:
    return max(0, min(255, round(value * scale)))


def classify(residual_q8: int, drift_age: int, sensitivity_q8: int) -> tuple[int, str]:
    if residual_q8 > 46:
        return 1, "governor should refuse because residual is above the hard stop"
    if drift_age > 11:
        return 1, "governor should recalibrate because calibration age is above the hard stop"
    if sensitivity_q8 >= 192 and residual_q8 > 24:
        return 1, "governor should refuse because this sensitive path amplifies residual error"
    return 1, "governor should admit this tile evidence"


def simulate() -> list[Row]:
    matrix = [
        [0.80, -0.40, 0.20, 0.10],
        [-0.10, 0.70, 0.30, -0.50],
        [0.20, 0.10, -0.60, 0.90],
        [0.50, -0.20, 0.40, 0.30],
    ]
    vector = [0.25, -0.75, 0.50, 0.10]
    ideal = matvec(matrix, vector)
    ideal_norm = rms(ideal)
    row_drop_losses = load_spice_row_drop_losses()
    scenarios = [
        Scenario("fresh_tile_low_sensitivity", 7, 7, 0.010, 0.000, 25.0, 0.35, 1),
        Scenario("fresh_tile_high_sensitivity", 7, 7, 0.010, 0.000, 25.0, 0.82, 1),
        Scenario("six_bit_normal_tile", 6, 6, 0.020, 0.010, 100.0, 0.55, 4),
        Scenario("wire_drop_stressed_tile", 6, 6, 0.020, 0.010, 500.0, 0.55, 5),
        Scenario("drifted_tile", 6, 6, 0.020, 0.060, 100.0, 0.55, 10),
        Scenario("stale_calibration_tile", 6, 6, 0.020, 0.025, 100.0, 0.55, 13),
        Scenario("programming_error_tile", 6, 6, 0.070, 0.020, 100.0, 0.55, 6),
        Scenario("low_precision_tile", 4, 4, 0.020, 0.010, 100.0, 0.55, 4),
    ]
    rows: list[Row] = []
    for idx, scenario in enumerate(scenarios):
        row_drop_loss = row_drop_loss_for_case(row_drop_losses, scenario.row_drop_case_ohm)
        analog = analog_matvec(matrix, vector, scenario, row_drop_loss, seed=101 + idx)
        residual = rms([a - b for a, b in zip(analog, ideal)])
        relative_residual = residual / ideal_norm if ideal_norm else residual
        residual_q8 = q8(relative_residual, 128.0)
        sensitivity_q8 = q8(scenario.sensitivity, 255.0)
        analog_candidate, meaning = classify(residual_q8, scenario.calibration_age, sensitivity_q8)
        rows.append(
            Row(
                scenario=scenario.name,
                adc_bits=scenario.adc_bits,
                dac_bits=scenario.dac_bits,
                program_sigma_pct=scenario.program_sigma * 100.0,
                drift_pct=scenario.drift * 100.0,
                row_drop_case_ohm=scenario.row_drop_case_ohm,
                spice_row_drop_loss_pct=row_drop_loss * 100.0,
                far_row_voltage_scale=1.0 - row_drop_loss,
                calibration_age=scenario.calibration_age,
                ideal_rms=ideal_norm,
                analog_rms=rms(analog),
                residual_abs=residual,
                residual_q8=residual_q8,
                drift_age=scenario.calibration_age,
                sensitivity_q8=sensitivity_q8,
                analog_candidate=analog_candidate,
                governor_input_meaning=meaning,
            )
        )
    return rows


def write_csv(rows: list[Row]) -> None:
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_markdown(rows: list[Row]) -> None:
    accepted = sum(row.analog_candidate for row in rows)
    lines = [
        "# Analog Tile Error Evidence",
        "",
        "This measurement turns an analog tile into the evidence packet consumed by the digital governor. The object is a dot product. The useful question is whether the measured dot product is still safe enough to become transformer state.",
        "",
        "The model includes conductance programming error, drift, DAC quantization, ADC quantization, SPICE-measured row-voltage drop, calibration age, and path sensitivity. Those are not separate stories. They meet at the governor inputs:",
        "",
        "```text",
        "residual_q8: how much analog output error remains",
        "drift_age: how long the tile has run since calibration",
        "sensitivity_q8: how much this model path amplifies numeric error",
        "analog_candidate: whether the tile should even be offered to the scheduler/governor",
        "```",
        "",
        "## Summary",
        "",
        f"- scenarios: {len(rows)}",
        f"- offered as analog candidates: {accepted}",
        f"- not offered as analog candidates: {len(rows) - accepted}",
        "",
        "## Evidence Table",
        "",
        "| scenario | ADC | DAC | program sigma % | drift % | row case ohm | SPICE current loss % | far-row scale | age | residual q8 | sensitivity q8 | candidate | meaning |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.scenario} | {row.adc_bits} | {row.dac_bits} | "
            f"{row.program_sigma_pct:.2f} | {row.drift_pct:.2f} | {row.row_drop_case_ohm:.0f} | "
            f"{row.spice_row_drop_loss_pct:.2f} | {row.far_row_voltage_scale:.3f} | "
            f"{row.calibration_age} | {row.residual_q8} | {row.sensitivity_q8} | "
            f"{row.analog_candidate} | {row.governor_input_meaning} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "An analog array does not produce a model value. It produces a physical measurement. The measurement becomes useful only after the digital side asks how far it may be from the ideal dot product, how old the calibration is, and how dangerous that error is for the current model path.",
            "",
            "Residual is the local miss: the difference between the ideal dot product and the measured tile output after converter and array effects. Row-drop now enters from the SPICE row-wire experiment: the script takes the measured current loss for a stated segment resistance and uses it to reduce the effective activation seen by farther cells. Drift age is the time dimension of the miss: even if the last measurement was good, the stored conductance may have moved. Sensitivity is the model dimension: the same numeric error can be harmless in one projection and dangerous near a selection boundary.",
            "",
            "The governor exists because these three facts must be joined. A fresh low-sensitivity tile can be admitted. A stale tile should recalibrate even if its current residual is moderate. A high-sensitivity path can require digital fallback at residual levels that would be acceptable elsewhere. This is the concrete analog-to-digital bridge: physics becomes residual, residual becomes a budget entry, and the budget decides whether analog compute is allowed for this token.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = simulate()
    write_csv(rows)
    write_markdown(rows)
    print("analog_tile_error_evidence")
    print(f"scenarios,{len(rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
