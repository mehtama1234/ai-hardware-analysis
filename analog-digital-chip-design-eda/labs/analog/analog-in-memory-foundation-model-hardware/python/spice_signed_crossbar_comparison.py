#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from spice_crossbar_comparison import parse_value


LAB_DIR = Path(__file__).resolve().parents[1]
SPICE_PATH = LAB_DIR / "spice" / "differential_signed_crossbar.sp"
MEASUREMENTS_DIR = LAB_DIR / "measurements"
CSV_OUT = MEASUREMENTS_DIR / "spice-signed-crossbar-comparison.csv"
MD_OUT = MEASUREMENTS_DIR / "spice-signed-crossbar-comparison.md"


@dataclass(frozen=True)
class Row:
    column: int
    positive_current_a: float
    negative_current_a: float
    spice_signed_current_a: float
    expected_signed_current_a: float
    signed_dot_value: float
    abs_error_a: float
    relative_error: float


def parse_netlist() -> tuple[float, list[float], list[list[float]]]:
    text = SPICE_PATH.read_text(encoding="utf-8")
    gscale_match = re.search(r"\.param\s+gscale=([0-9.]+[a-z]?)", text, re.IGNORECASE)
    if not gscale_match:
        raise ValueError("could not parse gscale")
    gscale = parse_value(gscale_match.group(1))

    row_voltages = [0.0] * 4
    for idx, value in re.findall(r"^V([0-9]+)\s+row[0-9]+\s+0\s+DC\s+([0-9.]+)", text, re.MULTILINE):
        row_voltages[int(idx) - 1] = float(value)

    weights = [[0.0 for _ in range(2)] for _ in range(4)]
    for row, col, branch, value in re.findall(
        r"^R([0-9])([0-9])([PN])\s+row[0-9]\s+col[0-9][pn]\s+\{1/\(([0-9.]+)\*gscale\)\}",
        text,
        re.MULTILINE,
    ):
        sign = 1.0 if branch == "P" else -1.0
        weights[int(row) - 1][int(col) - 1] = sign * float(value)
    return gscale, row_voltages, weights


def run_spice() -> dict[str, float]:
    result = subprocess.run(["ngspice", "-b", str(SPICE_PATH)], cwd=LAB_DIR, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    values: dict[str, float] = {}
    for name, value in re.findall(r"(i\(vs[12][pn]\)|col[12]_signed)\s+=\s+([-+0-9.eE]+)", result.stdout, re.IGNORECASE):
        values[name.lower()] = float(value)
    expected_names = {"i(vs1p)", "i(vs1n)", "col1_signed", "i(vs2p)", "i(vs2n)", "col2_signed"}
    missing = expected_names - set(values)
    if missing:
        raise ValueError(f"missing SPICE measurements: {', '.join(sorted(missing))}")
    return values


def compare() -> list[Row]:
    gscale, row_voltages, weights = parse_netlist()
    spice = run_spice()
    rows: list[Row] = []
    for col in range(2):
        signed_dot = sum(row_voltages[row] * weights[row][col] for row in range(4))
        expected = signed_dot * gscale
        actual = spice[f"col{col + 1}_signed"]
        abs_error = abs(actual - expected)
        relative = abs_error / abs(expected) if expected else abs_error
        rows.append(
            Row(
                column=col + 1,
                positive_current_a=spice[f"i(vs{col + 1}p)"],
                negative_current_a=spice[f"i(vs{col + 1}n)"],
                spice_signed_current_a=actual,
                expected_signed_current_a=expected,
                signed_dot_value=signed_dot,
                abs_error_a=abs_error,
                relative_error=relative,
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
    worst = max(row.relative_error for row in rows)
    lines = [
        "# SPICE Signed Crossbar Comparison",
        "",
        "This report checks the differential signed-weight crossbar. A passive conductance cannot be negative, so a signed weight is represented by two nonnegative paths. The positive path carries the positive part of the weight. The negative path carries the magnitude of the negative part. The signed result is the positive column current minus the negative column current.",
        "",
        "The object is a signed dot product made from physical currents:",
        "",
        "```text",
        "I_signed = I_positive - I_negative",
        "I_expected = gscale * sum(row_voltage_i * signed_weight_i)",
        "```",
        "",
        f"Worst relative difference between ngspice and the signed dot-product equation: `{worst:.3e}`.",
        "",
        "## Comparison",
        "",
        "| column | positive current A | negative current A | SPICE signed A | expected signed A | signed dot | abs error A | relative error |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.column} | {row.positive_current_a:.9e} | {row.negative_current_a:.9e} | "
            f"{row.spice_signed_current_a:.9e} | {row.expected_signed_current_a:.9e} | "
            f"{row.signed_dot_value:.6f} | {row.abs_error_a:.3e} | {row.relative_error:.3e} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "The unsigned crossbar proves current summation. The signed crossbar adds one more physical boundary: sign is not stored as negative conductance. It is stored as a difference between two ordinary conductance networks. That means a foundation-model weight is not only mapped into a cell value. It is mapped into a representation rule.",
            "",
            "This matters because subtraction is not free. The two paths can have different mismatch, drift, wire drop, and readout error. A signed analog projection is correct only if the positive and negative currents are both measured well enough and the subtraction keeps the difference within the model's error budget.",
            "",
            "The concrete design move is to expose the signed split before claiming transformer acceleration. A useful analog tile report should say how signed weights are encoded, how positive and negative currents are sensed, where subtraction happens, and how mismatch between the two halves enters the governor evidence.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = compare()
    write_csv(rows)
    write_markdown(rows)
    print("spice_signed_crossbar_comparison")
    print(f"columns,{len(rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
