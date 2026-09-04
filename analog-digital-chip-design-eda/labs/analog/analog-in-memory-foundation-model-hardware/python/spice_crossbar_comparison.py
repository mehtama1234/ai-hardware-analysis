#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]
SPICE_PATH = LAB_DIR / "spice" / "four_by_four_crossbar.sp"
MEASUREMENTS_DIR = LAB_DIR / "measurements"
CSV_OUT = MEASUREMENTS_DIR / "spice-crossbar-comparison.csv"
MD_OUT = MEASUREMENTS_DIR / "spice-crossbar-comparison.md"


@dataclass(frozen=True)
class Row:
    column: int
    spice_current_a: float
    conductance_sum_a: float
    abs_error_a: float
    relative_error: float


def parse_value(token: str) -> float:
    match = re.fullmatch(r"([0-9.]+)([kmunp]?)", token.strip(), re.IGNORECASE)
    if not match:
        raise ValueError(f"cannot parse SPICE value {token!r}")
    value = float(match.group(1))
    suffix = match.group(2).lower()
    scale = {
        "": 1.0,
        "k": 1e3,
        "m": 1e-3,
        "u": 1e-6,
        "n": 1e-9,
        "p": 1e-12,
    }[suffix]
    return value * scale


def parse_netlist() -> tuple[list[float], list[list[float]]]:
    text = SPICE_PATH.read_text(encoding="utf-8")
    params: dict[str, float] = {}
    for raw in text.splitlines():
        if not raw.startswith(".param"):
            continue
        for name, value in re.findall(r"([a-z][a-z0-9]*)=([0-9.]+[a-z]?)", raw, re.IGNORECASE):
            params[name.lower()] = parse_value(value)

    row_voltages = [0.0] * 4
    for source, node, value in re.findall(r"^V([0-9]+)\s+(row[0-9]+)\s+0\s+DC\s+([0-9.]+)", text, re.MULTILINE):
        row_voltages[int(source) - 1] = float(value)

    resistances = [[0.0 for _ in range(4)] for _ in range(4)]
    for row, col, param in re.findall(r"^R([0-9])([0-9])\s+row[0-9]\s+col[0-9]\s+\{([^}]+)\}", text, re.MULTILINE):
        resistances[int(row) - 1][int(col) - 1] = params[param.lower()]
    return row_voltages, resistances


def run_spice() -> list[float]:
    result = subprocess.run(["ngspice", "-b", str(SPICE_PATH)], cwd=LAB_DIR, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    currents = [0.0] * 4
    for idx, value in re.findall(r"i\(vsense([0-9]+)\)\s+=\s+([-+0-9.eE]+)", result.stdout):
        currents[int(idx) - 1] = float(value)
    if any(current == 0.0 for current in currents):
        raise ValueError("failed to parse all SPICE sense currents")
    return currents


def compare() -> list[Row]:
    voltages, resistances = parse_netlist()
    spice_currents = run_spice()
    rows: list[Row] = []
    for col in range(4):
        expected = sum(voltages[row] / resistances[row][col] for row in range(4))
        actual = spice_currents[col]
        abs_error = abs(actual - expected)
        relative = abs_error / abs(expected) if expected else abs_error
        rows.append(Row(col + 1, actual, expected, abs_error, relative))
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
        "# SPICE Crossbar Comparison",
        "",
        "This report compares the current printed by ngspice for the four-by-four resistive crossbar against the first-principles conductance sum.",
        "",
        "The object is one column current:",
        "",
        "```text",
        "I_column = V_row1 / R_row1_column + V_row2 / R_row2_column + ...",
        "```",
        "",
        "The zero-volt sense source holds the column at virtual ground, so each resistor current is set by row voltage divided by cell resistance.",
        "",
        f"Worst relative difference between ngspice and the direct conductance sum: `{worst:.3e}`.",
        "",
        "## Comparison",
        "",
        "| column | SPICE current A | conductance sum A | abs error A | relative error |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.column} | {row.spice_current_a:.9e} | {row.conductance_sum_a:.9e} | "
            f"{row.abs_error_a:.3e} | {row.relative_error:.3e} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "This is the smallest useful analog in-memory compute claim. A conductance stores a weight as `1/R`. A row voltage carries an activation. A column current is the sum of the branch currents. SPICE is solving the same circuit equations that the direct conductance sum writes down by hand.",
            "",
            "The later Python tile models add programming error, drift, converter quantization, row drop, calibration, and governor decisions. This comparison anchors those models to the base physical operation: weighted current summation at a virtual-ground column.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = compare()
    write_csv(rows)
    write_markdown(rows)
    print("spice_crossbar_comparison")
    print(f"columns,{len(rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
