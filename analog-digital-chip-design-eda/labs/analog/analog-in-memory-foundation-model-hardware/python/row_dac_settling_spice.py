#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]
SPICE_PATH = LAB_DIR / "spice" / "row_dac_settling_10bit.sp"
MEASUREMENTS_DIR = LAB_DIR / "measurements"
CSV_OUT = MEASUREMENTS_DIR / "row-dac-settling-spice.csv"
MD_OUT = MEASUREMENTS_DIR / "row-dac-settling-spice.md"


@dataclass(frozen=True)
class Row:
    case: str
    target_v: float
    settled_v: float
    abs_error_v: float
    dac_lsb_v: float
    half_lsb_v: float
    settling_time_ns: float
    pass_half_lsb: bool


def run_spice(target_v: float) -> float:
    template = SPICE_PATH.read_text(encoding="utf-8")
    deck = re.sub(r"\.param vtarget=[^\n]+", f".param vtarget={target_v}", template)
    with tempfile.NamedTemporaryFile("w", suffix=".sp", dir=LAB_DIR, delete=False, encoding="utf-8") as handle:
        handle.write(deck)
        temp_path = Path(handle.name)
    result = subprocess.run(["ngspice", "-b", str(temp_path)], cwd=LAB_DIR, text=True, capture_output=True, check=False)
    temp_path.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    values: list[float] = []
    for raw in result.stdout.splitlines():
        match = re.search(r"vsettled\s+=\s+([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError("expected row DAC settling measurement, found none")
    return values[-1]


def compare() -> list[Row]:
    targets = [
        ("low_code", 0.125),
        ("mid_code", 0.5),
        ("high_code", 0.875),
    ]
    dac_lsb = 1.0 / 1024.0
    half_lsb = dac_lsb / 2.0
    rows: list[Row] = []
    for case, target in targets:
        measured = run_spice(target)
        abs_error = abs(target - measured)
        rows.append(
            Row(
                case=case,
                target_v=target,
                settled_v=measured,
                abs_error_v=abs_error,
                dac_lsb_v=dac_lsb,
                half_lsb_v=half_lsb,
                settling_time_ns=4.0,
                pass_half_lsb=abs_error <= half_lsb,
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
    worst_error = max(row.abs_error_v for row in rows)
    all_pass = all(row.pass_half_lsb for row in rows)
    lines = [
        "# Row-DAC Settling SPICE",
        "",
        "This report executes the first converter SPICE handoff testbench. It checks whether a 10-bit row-drive boundary can settle a representative row load inside the 4 ns window used by the behavioral converter estimate.",
        "",
        f"- SPICE deck: `{SPICE_PATH.relative_to(LAB_DIR)}`",
        f"- cases: `{len(rows)}`",
        f"- settling window: `4.0` ns",
        f"- DAC LSB: `{rows[0].dac_lsb_v:.9f}` V",
        f"- half-LSB acceptance limit: `{rows[0].half_lsb_v:.9f}` V",
        f"- worst settled error: `{worst_error:.9f}` V",
        f"- all cases pass half-LSB settling: `{all_pass}`",
        "",
        "## Results",
        "",
        "| case | target V | settled V | abs error V | half LSB V | pass |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.case} | {row.target_v:.6f} | {row.settled_v:.9f} | {row.abs_error_v:.9f} | {row.half_lsb_v:.9f} | {row.pass_half_lsb} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "A DAC code is not useful at the model boundary until the selected row voltage has actually moved close enough to its target. The row driver has resistance, the row has resistance, and the selected row load has capacitance. That makes the row voltage a time-dependent circuit state, not an instant number.",
            "",
            "For a 10-bit row drive, one code step is full scale divided by 1024. The settling rule used here is stricter than one full code step: after 4 ns, the row voltage must be within half of one step. If it is not, the hardware is effectively using fewer than 10 reliable input bits even if the control word has 10 bits.",
            "",
            "This SPICE fixture therefore tests a concrete part of the converter claim. It does not prove a transistor DAC, reference ladder, switch linearity, mismatch, layout parasitics, or silicon noise. It only proves that this simple driver-load model can meet the 4 ns half-LSB settling condition.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = compare()
    write_csv(rows)
    write_markdown(rows)
    print("row_dac_settling_spice")
    print(f"cases,{len(rows)}")
    print(f"all_pass,{all(row.pass_half_lsb for row in rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
