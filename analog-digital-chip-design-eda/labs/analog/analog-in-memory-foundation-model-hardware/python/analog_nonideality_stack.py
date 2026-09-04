#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path


MEASUREMENTS_DIR = Path(__file__).resolve().parents[1] / "measurements"
ROW_DROP_CSV = MEASUREMENTS_DIR / "spice-row-drop-comparison.csv"
TILE_OPERATING_POINT_CSV = MEASUREMENTS_DIR / "tile-operating-point.csv"
CSV_OUT = MEASUREMENTS_DIR / "analog-nonideality-stack.csv"
MD_OUT = MEASUREMENTS_DIR / "analog-nonideality-stack.md"


WEIGHTS = [
    [0.80, -0.40, 0.20, 0.10],
    [-0.10, 0.70, 0.30, -0.50],
    [0.20, 0.10, -0.60, 0.90],
    [0.50, -0.20, 0.40, 0.30],
]
ACTIVATION = [0.25, -0.75, 0.50, 0.10]


@dataclass(frozen=True)
class Stage:
    stage: str
    vector: list[float]
    residual_abs: float
    residual_relative: float
    residual_q8: int
    first_principle: str


def quantize(value: float, bits: int, low: float, high: float) -> float:
    levels = (1 << bits) - 1
    clipped = min(max(value, low), high)
    code = round((clipped - low) / (high - low) * levels)
    return low + code * (high - low) / levels


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(weight * value for weight, value in zip(row, vector)) for row in matrix]


def q8(value: float, scale: float = 128.0) -> int:
    return max(0, min(255, round(value * scale)))


def load_row_loss(row_case_ohm: float) -> float:
    with ROW_DROP_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if float(row["rseg_ohm"]) == row_case_ohm:
                return float(row["row_drop_current_loss_pct"]) / 100.0
    raise ValueError(f"missing row-drop case {row_case_ohm} ohm")


def load_operating_point() -> dict[str, float]:
    with TILE_OPERATING_POINT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        raise ValueError(f"expected one tile operating point row, found {len(rows)}")
    row = rows[0]
    return {
        "adc_bits": float(row["adc_bits"]),
        "dac_bits": float(row["dac_bits"]),
        "row_drop_case_ohm": float(row["row_drop_case_ohm"]),
        "converter_energy_relative": float(row["converter_energy_relative"]),
        "latency_comparisons": float(row["latency_comparisons"]),
    }


def stage_row(stage: str, vector: list[float], ideal: list[float], ideal_norm: float, principle: str) -> Stage:
    residual = rms([value - ref for value, ref in zip(vector, ideal)])
    relative = residual / ideal_norm if ideal_norm else residual
    return Stage(stage, vector, residual, relative, q8(relative), principle)


def differential_signed(matrix: list[list[float]], vector: list[float]) -> list[float]:
    outputs: list[float] = []
    for row in matrix:
        positive_current = sum(max(weight, 0.0) * value for weight, value in zip(row, vector))
        negative_current = sum(max(-weight, 0.0) * value for weight, value in zip(row, vector))
        outputs.append(positive_current - negative_current)
    return outputs


def row_drop(matrix: list[list[float]], vector: list[float], loss: float) -> list[float]:
    far = max(1, len(vector) - 1)
    scaled_vector = [value * (1.0 - loss * (idx / far)) for idx, value in enumerate(vector)]
    return differential_signed(matrix, scaled_vector)


def deterministic_programmed(matrix: list[list[float]], drift: float) -> list[list[float]]:
    programmed: list[list[float]] = []
    for out_idx, row in enumerate(matrix):
        programmed_row = []
        for in_idx, weight in enumerate(row):
            mismatch = 1.0 + 0.006 * ((out_idx + 1) - (in_idx + 1))
            programmed_row.append(weight * mismatch * (1.0 + drift))
        programmed.append(programmed_row)
    return programmed


def simulate() -> tuple[list[Stage], dict[str, float]]:
    operating_point = load_operating_point()
    adc_bits = int(operating_point["adc_bits"])
    dac_bits = int(operating_point["dac_bits"])
    row_case = operating_point["row_drop_case_ohm"]
    row_loss = load_row_loss(row_case)
    ideal = matvec(WEIGHTS, ACTIVATION)
    ideal_norm = rms(ideal)

    stages = [
        stage_row(
            "ideal_digital_dot",
            ideal,
            ideal,
            ideal_norm,
            "A model projection starts as a dot product: each output is a sum of weight times activation.",
        )
    ]

    signed = differential_signed(WEIGHTS, ACTIVATION)
    stages.append(
        stage_row(
            "differential_signed_conductance",
            signed,
            ideal,
            ideal_norm,
            "A passive cell cannot store a negative conductance, so sign is represented by two nonnegative paths and a subtraction.",
        )
    )

    dropped = row_drop(WEIGHTS, ACTIVATION, row_loss)
    stages.append(
        stage_row(
            "spice_row_drop_applied",
            dropped,
            ideal,
            ideal_norm,
            "A row activation is not one voltage everywhere; farther cells see less voltage after current has left through earlier cells.",
        )
    )

    q_activation = [quantize(value, dac_bits, -1.0, 1.0) for value in ACTIVATION]
    dac_and_drop = row_drop(WEIGHTS, q_activation, row_loss)
    stages.append(
        stage_row(
            "dac_quantized_rows",
            dac_and_drop,
            ideal,
            ideal_norm,
            "The DAC damages the input before multiplication, so one rounded activation perturbs every output column that uses it.",
        )
    )

    programmed = deterministic_programmed(WEIGHTS, drift=0.010)
    analog_current = row_drop(programmed, q_activation, row_loss)
    stages.append(
        stage_row(
            "programmed_and_drifted_cells",
            analog_current,
            ideal,
            ideal_norm,
            "The stored conductance is a measured physical state, not the exact trained weight; mismatch and drift move the dot product.",
        )
    )

    adc_output = [quantize(value, adc_bits, -4.0, 4.0) for value in analog_current]
    stages.append(
        stage_row(
            "adc_quantized_column_readout",
            adc_output,
            ideal,
            ideal_norm,
            "The ADC turns current into a code; nearby currents can become the same code and small analog differences can disappear.",
        )
    )

    final = stages[-1]
    metadata = {
        "adc_bits": float(adc_bits),
        "dac_bits": float(dac_bits),
        "row_drop_case_ohm": row_case,
        "spice_row_drop_loss_pct": row_loss * 100.0,
        "converter_energy_relative": operating_point["converter_energy_relative"],
        "latency_comparisons": operating_point["latency_comparisons"],
        "final_residual_q8": float(final.residual_q8),
        "final_relative_residual": final.residual_relative,
    }
    return stages, metadata


def write_csv(stages: list[Stage], metadata: dict[str, float]) -> None:
    fields = [
        "stage",
        "out0",
        "out1",
        "out2",
        "out3",
        "residual_abs",
        "residual_relative",
        "residual_q8",
        "adc_bits",
        "dac_bits",
        "row_drop_case_ohm",
        "spice_row_drop_loss_pct",
        "converter_energy_relative",
        "latency_comparisons",
        "first_principle",
    ]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for stage in stages:
            row = {
                "stage": stage.stage,
                "out0": stage.vector[0],
                "out1": stage.vector[1],
                "out2": stage.vector[2],
                "out3": stage.vector[3],
                "residual_abs": stage.residual_abs,
                "residual_relative": stage.residual_relative,
                "residual_q8": stage.residual_q8,
                "adc_bits": int(metadata["adc_bits"]),
                "dac_bits": int(metadata["dac_bits"]),
                "row_drop_case_ohm": metadata["row_drop_case_ohm"],
                "spice_row_drop_loss_pct": metadata["spice_row_drop_loss_pct"],
                "converter_energy_relative": metadata["converter_energy_relative"],
                "latency_comparisons": int(metadata["latency_comparisons"]),
                "first_principle": stage.first_principle,
            }
            writer.writerow(row)


def write_markdown(stages: list[Stage], metadata: dict[str, float]) -> None:
    final = stages[-1]
    lines = [
        "# Analog Nonideality Stack",
        "",
        "This report follows one small foundation-model projection through the analog tile boundary. The point is not to show that analog compute is accurate in general. The point is to show where the number changes before the digital governor is allowed to trust it.",
        "",
        "The operating point is loaded from `tile-operating-point.csv`: ADC 6, DAC 4, the 100 ohm SPICE row-drop case, and a converter energy cost of 3.22x. The row-drop loss is loaded from the SPICE row-wire measurement instead of being invented inside this script.",
        "",
        "## Stage Table",
        "",
        "| stage | out0 | out1 | out2 | out3 | residual | relative | q8 | first principle |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for stage in stages:
        lines.append(
            f"| {stage.stage} | {stage.vector[0]:.5f} | {stage.vector[1]:.5f} | "
            f"{stage.vector[2]:.5f} | {stage.vector[3]:.5f} | {stage.residual_abs:.5f} | "
            f"{stage.residual_relative:.5f} | {stage.residual_q8} | {stage.first_principle} |"
        )
    lines.extend(
        [
            "",
            "## Governor Input",
            "",
            "```text",
            f"adc_bits: {int(metadata['adc_bits'])}",
            f"dac_bits: {int(metadata['dac_bits'])}",
            f"row_drop_case_ohm: {metadata['row_drop_case_ohm']:.0f}",
            f"spice_row_drop_loss_pct: {metadata['spice_row_drop_loss_pct']:.2f}",
            f"converter_energy_relative: {metadata['converter_energy_relative']:.2f}",
            f"latency_comparisons: {int(metadata['latency_comparisons'])}",
            f"final_relative_residual: {final.residual_relative:.5f}",
            f"final_residual_q8: {final.residual_q8}",
            "```",
            "",
            "## First-Principles Reading",
            "",
            "The ideal dot product is the mathematical object the model was trained to use. The analog tile does not directly produce that object. It produces a current made from conductances, voltages, wires, device state, and a readout circuit.",
            "",
            "The signed-conductance stage has almost no residual because it is still only a representation change. It says that negative weights require two physical paths and a subtraction. That matters because later mismatch can hit the positive and negative paths differently.",
            "",
            "The row-drop stage is the first physical loss. The same input activation is no longer the same voltage at every cell. Cells near the driver and cells farther down the row are multiplying by different voltages, so the dot product is bent before any ADC decision is made.",
            "",
            "The DAC stage changes the input before the array. This is different from output rounding. If an activation is rounded before multiplication, all weights connected to that activation inherit the same input error.",
            "",
            "The programmed-and-drifted stage changes the stored weight. A trained parameter is a number in software; a cell conductance is a physical state that was programmed, measured, and then allowed to age. This is why calibration is not a footnote. It is the act of remeasuring what the weights have become.",
            "",
            "The ADC stage is the trust boundary. Current becomes a code, and the code becomes model state only if the residual is still inside budget. The governor should not ask whether the crossbar multiplied. It should ask whether this measured value is allowed to enter the next transformer layer.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    stages, metadata = simulate()
    write_csv(stages, metadata)
    write_markdown(stages, metadata)
    print("analog_nonideality_stack")
    print(f"stages,{len(stages)}")
    print(f"final_residual_q8,{stages[-1].residual_q8}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
