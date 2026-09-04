#!/usr/bin/env python3
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from analog_tile_error_evidence import main as write_tile_evidence
from converter_boundary_sweep import main as write_converter_sweep
from spice_row_drop_comparison import main as write_row_drop
from spice_signed_crossbar_comparison import main as write_signed_crossbar


LAB_DIR = Path(__file__).resolve().parents[1]
MEASUREMENTS_DIR = LAB_DIR / "measurements"
CSV_OUT = MEASUREMENTS_DIR / "tile-operating-point.csv"
MD_OUT = MEASUREMENTS_DIR / "tile-operating-point.md"
ROW_DROP_CSV = MEASUREMENTS_DIR / "spice-row-drop-comparison.csv"
SIGNED_CSV = MEASUREMENTS_DIR / "spice-signed-crossbar-comparison.csv"
CONVERTER_CSV = MEASUREMENTS_DIR / "converter-boundary-sweep.csv"
EVIDENCE_CSV = MEASUREMENTS_DIR / "analog-tile-error-evidence.csv"


@dataclass(frozen=True)
class OperatingPoint:
    name: str
    adc_bits: int
    dac_bits: int
    row_drop_case_ohm: float
    spice_row_drop_loss_pct: float
    converter_relative_error: float
    converter_energy_relative: float
    latency_comparisons: int
    signed_crossbar_worst_error: float
    evidence_residual_q8: int
    evidence_sensitivity_q8: int
    evidence_drift_age: int
    governor_assumption: str


def rows_from(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        if path == ROW_DROP_CSV:
            write_row_drop()
        elif path == SIGNED_CSV:
            write_signed_crossbar()
        elif path == CONVERTER_CSV:
            write_converter_sweep()
        elif path == EVIDENCE_CSV:
            write_tile_evidence()
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"no rows in {path}")
    return rows


def choose_converter(rows: list[dict[str, str]]) -> dict[str, str]:
    useful = [row for row in rows if row["useful"] == "1"]
    if not useful:
        raise ValueError("converter sweep has no useful operating point")
    return min(
        useful,
        key=lambda row: (
            float(row["energy_relative"]),
            float(row["relative_error"]),
            int(row["adc_bits"]) + int(row["dac_bits"]),
        ),
    )


def build() -> OperatingPoint:
    signed_rows = rows_from(SIGNED_CSV)
    converter = choose_converter(rows_from(CONVERTER_CSV))
    evidence_rows = rows_from(EVIDENCE_CSV)
    evidence_match = [
        row
        for row in evidence_rows
        if row["adc_bits"] == converter["adc_bits"]
        and row["dac_bits"] == converter["dac_bits"]
        and row["row_drop_case_ohm"] == converter["row_drop_case_ohm"]
    ]
    evidence = evidence_match[0] if evidence_match else min(
        evidence_rows,
        key=lambda row: (
            abs(int(row["adc_bits"]) - int(converter["adc_bits"])),
            abs(int(row["dac_bits"]) - int(converter["dac_bits"])),
            abs(float(row["row_drop_case_ohm"]) - float(converter["row_drop_case_ohm"])),
        ),
    )
    worst_signed = max(float(row["relative_error"]) for row in signed_rows)
    residual_q8 = int(evidence["residual_q8"])
    drift_age = int(evidence["drift_age"])
    sensitivity_q8 = int(evidence["sensitivity_q8"])
    if residual_q8 > 46:
        assumption = "digital fallback if this residual appears at runtime"
    elif drift_age > 11:
        assumption = "recalibrate before trusting this tile"
    elif sensitivity_q8 >= 192 and residual_q8 > 24:
        assumption = "digital fallback on sensitive model paths"
    else:
        assumption = "eligible for analog service while cumulative state budget remains available"
    return OperatingPoint(
        name="lowest_energy_useful_converter_boundary",
        adc_bits=int(converter["adc_bits"]),
        dac_bits=int(converter["dac_bits"]),
        row_drop_case_ohm=float(converter["row_drop_case_ohm"]),
        spice_row_drop_loss_pct=float(converter["spice_row_drop_loss_pct"]),
        converter_relative_error=float(converter["relative_error"]),
        converter_energy_relative=float(converter["energy_relative"]),
        latency_comparisons=int(converter["latency_comparisons"]),
        signed_crossbar_worst_error=worst_signed,
        evidence_residual_q8=residual_q8,
        evidence_sensitivity_q8=sensitivity_q8,
        evidence_drift_age=drift_age,
        governor_assumption=assumption,
    )


def write_csv(row: OperatingPoint) -> None:
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(OperatingPoint.__dataclass_fields__.keys()))
        writer.writeheader()
        writer.writerow(row.__dict__)


def write_markdown(row: OperatingPoint) -> None:
    lines = [
        "# AIMC Tile Operating Point",
        "",
        "This file states the measured operating point that the current analog tile and digital governor examples assume. It is generated from the signed-crossbar SPICE proof, row-wire-drop SPICE proof, converter boundary sweep, and analog tile evidence table.",
        "",
        "## Selected Boundary",
        "",
        "| name | ADC | DAC | row case ohm | row loss % | converter error | converter energy x | SAR comparisons | signed-crossbar error | residual q8 | sensitivity q8 | drift age | governor assumption |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        f"| {row.name} | {row.adc_bits} | {row.dac_bits} | {row.row_drop_case_ohm:.0f} | "
        f"{row.spice_row_drop_loss_pct:.2f} | {row.converter_relative_error:.4f} | "
        f"{row.converter_energy_relative:.2f} | {row.latency_comparisons} | "
        f"{row.signed_crossbar_worst_error:.3e} | {row.evidence_residual_q8} | "
        f"{row.evidence_sensitivity_q8} | {row.evidence_drift_age} | {row.governor_assumption} |",
        "",
        "## First-Principles Reading",
        "",
        "An operating point is the smallest honest claim a mixed-signal accelerator can make. It says which physical representation is being used, which converter boundary is being paid for, which wire-loss case is included, and which digital rule will accept or refuse the result.",
        "",
        "The signed-crossbar proof says the weight sign is represented by two nonnegative current paths. The row-drop proof says the activation is not the same voltage at every cell. The converter sweep says how much precision is worth paying for before extra bits become expensive decoration. The tile evidence table turns those physical facts into governor inputs.",
        "",
        "The concrete design move is to keep this operating point visible. If a later design changes ADC bits, DAC bits, row length, calibration schedule, or signed-weight encoding, this file should change before any performance claim is trusted.",
        "",
    ]
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    row = build()
    write_csv(row)
    write_markdown(row)
    print("tile_operating_point")
    print(f"adc_bits,{row.adc_bits}")
    print(f"dac_bits,{row.dac_bits}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
