#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]
SPICE_PATH = LAB_DIR / "spice" / "converter_supply_energy.sp"
MEASUREMENTS_DIR = LAB_DIR / "measurements"
CSV_OUT = MEASUREMENTS_DIR / "converter-supply-energy-spice.csv"
MD_OUT = MEASUREMENTS_DIR / "converter-supply-energy-spice.md"


@dataclass(frozen=True)
class Row:
    case: str
    input_v: float
    rail_v: float
    dac_energy_j: float
    adc_energy_j: float
    mux_energy_j: float
    total_energy_j: float
    conversion_time_ns: float
    settling_time_ns: float
    pass_positive_energy: bool


def read_measure(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.search(rf"{name}\s+=\s+([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected measurement {name}, found none")
    return values[-1]


def run_spice(input_v: float) -> tuple[float, float, float]:
    template = SPICE_PATH.read_text(encoding="utf-8")
    deck = re.sub(r"\.param vin=[^\n]+", f".param vin={input_v}", template)
    with tempfile.NamedTemporaryFile("w", suffix=".sp", dir=LAB_DIR, delete=False, encoding="utf-8") as handle:
        handle.write(deck)
        temp_path = Path(handle.name)
    result = subprocess.run(["ngspice", "-b", str(temp_path)], cwd=LAB_DIR, text=True, capture_output=True, check=False)
    temp_path.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    return (
        abs(read_measure(result.stdout, "edac")),
        abs(read_measure(result.stdout, "eadc")),
        abs(read_measure(result.stdout, "emux")),
    )


def compare() -> list[Row]:
    cases = [
        ("low_conversion", 0.125),
        ("mid_conversion", 0.5),
        ("high_conversion", 0.875),
    ]
    rows: list[Row] = []
    for case, input_v in cases:
        dac_energy, adc_energy, mux_energy = run_spice(input_v)
        total = dac_energy + adc_energy + mux_energy
        rows.append(
            Row(
                case=case,
                input_v=input_v,
                rail_v=1.0,
                dac_energy_j=dac_energy,
                adc_energy_j=adc_energy,
                mux_energy_j=mux_energy,
                total_energy_j=total,
                conversion_time_ns=12.0,
                settling_time_ns=4.0,
                pass_positive_energy=total > 0.0 and dac_energy > 0.0 and adc_energy > 0.0,
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
    worst_energy = max(row.total_energy_j for row in rows)
    all_pass = all(row.pass_positive_energy for row in rows)
    lines = [
        "# Converter Supply Energy SPICE",
        "",
        "This report executes the fourth converter SPICE handoff testbench. It integrates supply work for the row-drive, ADC-reference, and shared-mux capacitive loads in the same settling and conversion windows used by the converter target.",
        "",
        f"- SPICE deck: `{SPICE_PATH.relative_to(LAB_DIR)}`",
        f"- cases: `{len(rows)}`",
        f"- rail: `1.0` V",
        f"- settling window: `4.0` ns",
        f"- conversion window: `12.0` ns",
        f"- worst total energy: `{worst_energy:.12e}` J",
        f"- all cases have positive integrated energy: `{all_pass}`",
        "",
        "## Results",
        "",
        "| case | input V | DAC energy J | ADC energy J | mux energy J | total energy J | pass |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.case} | {row.input_v:.6f} | {row.dac_energy_j:.12e} | {row.adc_energy_j:.12e} | {row.mux_energy_j:.12e} | {row.total_energy_j:.12e} | {row.pass_positive_energy} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "Energy is charge moved through a voltage. A converter may be accurate and still be a bad hardware choice if too much charge is moved every time an activation is driven or a column value is read.",
            "",
            "This fixture names the rail and integrates the work done by three simple sources: row drive, ADC reference charging, and shared mux charging. It gives a circuit-derived energy scale for the clean load model. It does not include layout parasitics, bias currents, clock tree power, leakage, comparator short-circuit current, or measured board power.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = compare()
    write_csv(rows)
    write_markdown(rows)
    print("converter_supply_energy_spice")
    print(f"cases,{len(rows)}")
    print(f"all_pass,{all(row.pass_positive_energy for row in rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
