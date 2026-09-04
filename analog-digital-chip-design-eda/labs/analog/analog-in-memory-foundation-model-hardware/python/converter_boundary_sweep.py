#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path

from analog_tile_error_evidence import load_spice_row_drop_losses, quantize, row_drop_loss_for_case


LAB_DIR = Path(__file__).resolve().parents[1]
MEASUREMENTS_DIR = LAB_DIR / "measurements"
CSV_OUT = MEASUREMENTS_DIR / "converter-boundary-sweep.csv"
MD_OUT = MEASUREMENTS_DIR / "converter-boundary-sweep.md"


@dataclass(frozen=True)
class Row:
    adc_bits: int
    dac_bits: int
    comparator_noise: float
    settling_fraction: float
    row_drop_case_ohm: float
    spice_row_drop_loss_pct: float
    relative_error: float
    energy_relative: float
    latency_comparisons: int
    useful: int
    interpretation: str


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def rel_error(reference: list[float], measured: list[float]) -> float:
    residual = [actual - ideal for actual, ideal in zip(measured, reference)]
    denom = rms(reference)
    return rms(residual) / denom if denom else rms(residual)


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(weight * value for weight, value in zip(row, vector)) for row in matrix]


def analog_measure(
    matrix: list[list[float]],
    vector: list[float],
    *,
    adc_bits: int,
    dac_bits: int,
    comparator_noise: float,
    settling_fraction: float,
    row_drop_loss: float,
    rng: random.Random,
) -> list[float]:
    rows = max(1, len(vector) - 1)
    q_vector = []
    for value in vector:
        driven = quantize(value, dac_bits, -1.0, 1.0)
        q_vector.append(driven * settling_fraction)

    outputs = []
    for weights in matrix:
        current = 0.0
        for row_idx, (weight, value) in enumerate(zip(weights, q_vector)):
            wire_scale = 1.0 - row_drop_loss * (row_idx / rows)
            current += weight * value * wire_scale
        noisy_current = current + rng.gauss(0.0, comparator_noise)
        outputs.append(quantize(noisy_current, adc_bits, -4.0, 4.0))
    return outputs


def converter_energy(adc_bits: int, dac_bits: int, columns: int, rows: int) -> float:
    adc = columns * (2 ** max(0, adc_bits - 4))
    dac = rows * 0.35 * (2 ** max(0, dac_bits - 4))
    return adc + dac


def classify(error: float, energy: float, best_low_error_energy: float) -> tuple[int, str]:
    if error > 0.12:
        return 0, "too much model-facing error"
    if energy > best_low_error_energy * 2.25:
        return 0, "precision costs more than the error reduction justifies"
    return 1, "reasonable converter boundary"


def sweep() -> list[Row]:
    matrix = [
        [0.80, -0.40, 0.20, 0.10],
        [-0.10, 0.70, 0.30, -0.50],
        [0.20, 0.10, -0.60, 0.90],
        [0.50, -0.20, 0.40, 0.30],
    ]
    vector = [0.25, -0.75, 0.50, 0.10]
    reference = matvec(matrix, vector)
    row_drop_losses = load_spice_row_drop_losses()
    row_drop_case = 100.0
    row_drop_loss = row_drop_loss_for_case(row_drop_losses, row_drop_case)

    raw_rows: list[tuple[int, int, float, float, float, int]] = []
    for dac_bits in [3, 4, 5, 6, 7, 8]:
        for adc_bits in [3, 4, 5, 6, 7, 8]:
            for comparator_noise in [0.0, 0.004, 0.012]:
                for settling_fraction in [1.0, 0.97]:
                    rng = random.Random(5000 + dac_bits * 191 + adc_bits * 31 + int(comparator_noise * 10000) + int(settling_fraction * 100))
                    measured = analog_measure(
                        matrix,
                        vector,
                        adc_bits=adc_bits,
                        dac_bits=dac_bits,
                        comparator_noise=comparator_noise,
                        settling_fraction=settling_fraction,
                        row_drop_loss=row_drop_loss,
                        rng=rng,
                    )
                    error = rel_error(reference, measured)
                    latency = len(matrix) * adc_bits
                    raw_rows.append((adc_bits, dac_bits, comparator_noise, settling_fraction, error, latency))

    base_energy = converter_energy(4, 4, len(matrix), len(vector))
    candidate_energies = [
        converter_energy(adc_bits, dac_bits, len(matrix), len(vector)) / base_energy
        for adc_bits, dac_bits, _noise, _settling, error, _latency in raw_rows
        if error <= 0.12
    ]
    best_low_error_energy = min(candidate_energies) if candidate_energies else 1.0

    rows: list[Row] = []
    for adc_bits, dac_bits, noise, settling, error, latency in raw_rows:
        energy = converter_energy(adc_bits, dac_bits, len(matrix), len(vector)) / base_energy
        useful, interpretation = classify(error, energy, best_low_error_energy)
        rows.append(
            Row(
                adc_bits=adc_bits,
                dac_bits=dac_bits,
                comparator_noise=noise,
                settling_fraction=settling,
                row_drop_case_ohm=row_drop_case,
                spice_row_drop_loss_pct=row_drop_loss * 100.0,
                relative_error=error,
                energy_relative=energy,
                latency_comparisons=latency,
                useful=useful,
                interpretation=interpretation,
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
    useful_rows = [row for row in rows if row.useful]
    best_error = min(rows, key=lambda row: row.relative_error)
    best_useful = min(useful_rows, key=lambda row: row.energy_relative) if useful_rows else best_error
    low_energy = min(rows, key=lambda row: row.energy_relative)
    lines = [
        "# Converter Boundary Sweep",
        "",
        "This sweep asks how many ADC and DAC bits are worth paying for at one analog tile boundary. The object is not converter precision by itself. The object is a measured projection value that must be accurate enough to become model state while cheap enough that analog compute still has a reason to exist.",
        "",
        "The sweep uses the same four-output dot product as the tile evidence model and the `100 ohm` SPICE row-wire-drop case. It varies DAC bits, ADC bits, comparator noise, and row settling. It reports relative output error, a simple relative converter-energy estimate, and the SAR comparison count needed for the four output columns.",
        "",
        "## Summary",
        "",
        f"- cases: {len(rows)}",
        f"- useful boundary cases: {len(useful_rows)}",
        f"- SPICE row-drop current loss used: {rows[0].spice_row_drop_loss_pct:.2f}%",
        f"- lowest-energy case: ADC {low_energy.adc_bits}, DAC {low_energy.dac_bits}, error {low_energy.relative_error:.4f}, energy {low_energy.energy_relative:.2f}x",
        f"- lowest-error case: ADC {best_error.adc_bits}, DAC {best_error.dac_bits}, error {best_error.relative_error:.4f}, energy {best_error.energy_relative:.2f}x",
        f"- lowest-energy useful case: ADC {best_useful.adc_bits}, DAC {best_useful.dac_bits}, error {best_useful.relative_error:.4f}, energy {best_useful.energy_relative:.2f}x",
        "",
        "## Representative Cases",
        "",
        "| ADC | DAC | noise | settling | error | energy x | comparisons | useful | interpretation |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    representative = [
        min(rows, key=lambda row: row.energy_relative),
        min((row for row in rows if row.adc_bits == 4 and row.dac_bits == 4 and row.comparator_noise == 0.0 and row.settling_fraction == 1.0), key=lambda row: row.relative_error),
        min((row for row in rows if row.adc_bits == 6 and row.dac_bits == 6 and row.comparator_noise == 0.004 and row.settling_fraction == 1.0), key=lambda row: row.relative_error),
        min((row for row in rows if row.adc_bits == 8 and row.dac_bits == 8 and row.comparator_noise == 0.004 and row.settling_fraction == 1.0), key=lambda row: row.relative_error),
        min((row for row in rows if row.adc_bits == 8 and row.dac_bits == 8 and row.comparator_noise == 0.012 and row.settling_fraction == 0.97), key=lambda row: row.relative_error),
    ]
    seen: set[tuple[int, int, float, float]] = set()
    for row in representative:
        key = (row.adc_bits, row.dac_bits, row.comparator_noise, row.settling_fraction)
        if key in seen:
            continue
        seen.add(key)
        lines.append(
            f"| {row.adc_bits} | {row.dac_bits} | {row.comparator_noise:.3f} | {row.settling_fraction:.2f} | "
            f"{row.relative_error:.4f} | {row.energy_relative:.2f} | {row.latency_comparisons} | "
            f"{row.useful} | {row.interpretation} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "A DAC error happens before the crossbar sums current. One row voltage is shared by many cells, so one wrong row level pushes many output columns together. An ADC error happens after the current sum. It can collapse distinct column currents into the same code or add comparator-noise decisions near code boundaries.",
            "",
            "More bits reduce quantization step size, but they do not remove row drop, incomplete settling, comparator noise, or conductance drift. Once those effects dominate, extra bits make the code look more exact without making the underlying measurement more correct. That is why the sweep marks a case useful only when error is inside the model-facing budget and converter cost has not grown far beyond the cheapest low-error boundary.",
            "",
            "The concrete design move is to choose converter precision as a tile policy, not as a slogan. The governor should see residual evidence from the actual boundary. The system scheduler should know the energy and latency cost of that boundary. A foundation-model accelerator wins only when the array, converters, correction, calibration, and digital fallback rule all fit the same token budget.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = sweep()
    write_csv(rows)
    write_markdown(rows)
    print("converter_boundary_sweep")
    print(f"cases,{len(rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
