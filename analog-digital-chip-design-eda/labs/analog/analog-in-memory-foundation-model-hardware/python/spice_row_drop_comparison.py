#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from spice_crossbar_comparison import parse_value


LAB_DIR = Path(__file__).resolve().parents[1]
SPICE_PATH = LAB_DIR / "spice" / "row_wire_drop_crossbar.sp"
MEASUREMENTS_DIR = LAB_DIR / "measurements"
CSV_OUT = MEASUREMENTS_DIR / "spice-row-drop-comparison.csv"
MD_OUT = MEASUREMENTS_DIR / "spice-row-drop-comparison.md"


@dataclass(frozen=True)
class Row:
    rseg_ohm: float
    v_in: float
    v_n1: float
    v_n2: float
    v_n3: float
    v_n4: float
    spice_current_a: float
    ideal_no_drop_current_a: float
    distributed_model_current_a: float
    row_drop_current_loss_pct: float
    distributed_model_relative_error: float


def parse_netlist() -> tuple[float, list[float], list[float]]:
    text = SPICE_PATH.read_text(encoding="utf-8")
    params: dict[str, float] = {}
    for raw in text.splitlines():
        if not raw.startswith(".param"):
            continue
        for name, value in re.findall(r"([a-z][a-z0-9]*)=([0-9.]+[a-z]?)", raw, re.IGNORECASE):
            params[name.lower()] = parse_value(value)
    vin_match = re.search(r"^VIN\s+in\s+0\s+DC\s+([0-9.]+)", text, re.MULTILINE)
    if not vin_match:
        raise ValueError("could not parse VIN")
    vin = float(vin_match.group(1))
    rsegs = [params["rseg"], 100.0, 500.0]
    rcells = [params[f"rcell{idx}"] for idx in range(1, 5)]
    return vin, rsegs, rcells


def run_spice() -> list[tuple[float, float, float, float, float, float]]:
    result = subprocess.run(["ngspice", "-b", str(SPICE_PATH)], cwd=LAB_DIR, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    cases: list[tuple[float, float, float, float, float, float]] = []
    current: dict[str, float] = {}
    for raw in result.stdout.splitlines():
        match = re.match(r"(v\(in\)|v\(n[1-4]\)|i\(vsense\))\s+=\s+([-+0-9.eE]+)", raw.strip())
        if not match:
            continue
        current[match.group(1)] = float(match.group(2))
        if "i(vsense)" in current:
            cases.append(
                (
                    current["v(in)"],
                    current["v(n1)"],
                    current["v(n2)"],
                    current["v(n3)"],
                    current["v(n4)"],
                    current["i(vsense)"],
                )
            )
            current = {}
    if len(cases) != 3:
        raise ValueError(f"expected 3 SPICE row-drop cases, found {len(cases)}")
    return cases


def solve_row(vin: float, rseg: float, rcells: list[float]) -> list[float]:
    conductances = [1.0 / value for value in rcells]
    # Nodal equations for the four row taps. The driver node is fixed at vin.
    a = [[0.0 for _ in range(4)] for _ in range(4)]
    b = [0.0 for _ in range(4)]
    for idx in range(4):
        a[idx][idx] += conductances[idx]
        if idx == 0:
            a[idx][idx] += 1.0 / rseg
            b[idx] += vin / rseg
        else:
            a[idx][idx] += 1.0 / rseg
            a[idx][idx - 1] -= 1.0 / rseg
        if idx < 3:
            a[idx][idx] += 1.0 / rseg
            a[idx][idx + 1] -= 1.0 / rseg

    # Gaussian elimination is enough for this fixed 4x4 educational circuit.
    for pivot in range(4):
        scale = a[pivot][pivot]
        for col in range(pivot, 4):
            a[pivot][col] /= scale
        b[pivot] /= scale
        for row in range(4):
            if row == pivot:
                continue
            factor = a[row][pivot]
            for col in range(pivot, 4):
                a[row][col] -= factor * a[pivot][col]
            b[row] -= factor * b[pivot]
    return b


def compare() -> list[Row]:
    vin, rsegs, rcells = parse_netlist()
    spice_cases = run_spice()
    rows: list[Row] = []
    ideal_current = sum(vin / resistance for resistance in rcells)
    for rseg, spice in zip(rsegs, spice_cases):
        taps = solve_row(vin, rseg, rcells)
        model_current = sum(voltage / resistance for voltage, resistance in zip(taps, rcells))
        spice_current = spice[5]
        loss_pct = (ideal_current - spice_current) / ideal_current * 100.0
        rel_error = abs(model_current - spice_current) / abs(spice_current)
        rows.append(
            Row(
                rseg_ohm=rseg,
                v_in=spice[0],
                v_n1=spice[1],
                v_n2=spice[2],
                v_n3=spice[3],
                v_n4=spice[4],
                spice_current_a=spice_current,
                ideal_no_drop_current_a=ideal_current,
                distributed_model_current_a=model_current,
                row_drop_current_loss_pct=loss_pct,
                distributed_model_relative_error=rel_error,
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
    worst_model_error = max(row.distributed_model_relative_error for row in rows)
    worst_loss = max(row.row_drop_current_loss_pct for row in rows)
    lines = [
        "# SPICE Row-Wire-Drop Comparison",
        "",
        "This report compares a row-wire crossbar SPICE run against two hand calculations: the ideal no-drop current and a distributed row-resistance model.",
        "",
        "The ideal model assumes every cell sees the driver voltage:",
        "",
        "```text",
        "I_ideal = V_in / R_cell1 + V_in / R_cell2 + V_in / R_cell3 + V_in / R_cell4",
        "```",
        "",
        "The distributed model solves the row tap voltages first, then sums `V_tap / R_cell` at each tap.",
        "",
        f"Worst current loss versus the ideal no-drop model: `{worst_loss:.2f}%`.",
        f"Worst relative difference between ngspice and the distributed row model: `{worst_model_error:.3e}`.",
        "",
        "## Comparison",
        "",
        "| rseg ohm | v(n1) | v(n2) | v(n3) | v(n4) | SPICE current A | ideal current A | distributed current A | ideal current loss % | model relative error |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.rseg_ohm:.0f} | {row.v_n1:.6f} | {row.v_n2:.6f} | {row.v_n3:.6f} | {row.v_n4:.6f} | "
            f"{row.spice_current_a:.9e} | {row.ideal_no_drop_current_a:.9e} | "
            f"{row.distributed_model_current_a:.9e} | {row.row_drop_current_loss_pct:.2f} | "
            f"{row.distributed_model_relative_error:.3e} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "The ideal crossbar formula treats row voltage as a shared fact. Row-wire resistance makes that false. Current leaves the row at each cell, and that current causes voltage drop along the metal before the next cell is reached. The cells farther from the driver therefore see a smaller activation.",
            "",
            "This is why analog in-memory compute needs a physical error model. The mathematical dot product assumes one activation value per row. The circuit gives different effective activations along the row. The governor later sees the result as residual error, but the cause starts here: charge movement through nonzero wire resistance changes the value being multiplied.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = compare()
    write_csv(rows)
    write_markdown(rows)
    print("spice_row_drop_comparison")
    print(f"cases,{len(rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
