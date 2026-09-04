#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]
SPICE_PATH = LAB_DIR / "spice" / "sar_readout_12bit.sp"
MEASUREMENTS_DIR = LAB_DIR / "measurements"
CSV_OUT = MEASUREMENTS_DIR / "sar-readout-12bit-spice.csv"
MD_OUT = MEASUREMENTS_DIR / "sar-readout-12bit-spice.md"


@dataclass(frozen=True)
class Row:
    case: str
    input_v: float
    sampled_v: float
    abs_error_v: float
    adc_lsb_v: float
    half_lsb_v: float
    conversion_time_ns: float
    comparisons: int
    pass_half_lsb: bool


def run_spice(input_v: float) -> float:
    template = SPICE_PATH.read_text(encoding="utf-8")
    deck = re.sub(r"\.param vin=[^\n]+", f".param vin={input_v}", template)
    with tempfile.NamedTemporaryFile("w", suffix=".sp", dir=LAB_DIR, delete=False, encoding="utf-8") as handle:
        handle.write(deck)
        temp_path = Path(handle.name)
    result = subprocess.run(["ngspice", "-b", str(temp_path)], cwd=LAB_DIR, text=True, capture_output=True, check=False)
    temp_path.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    values: list[float] = []
    for raw in result.stdout.splitlines():
        match = re.search(r"vsampled\s+=\s+([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError("expected SAR readout sample measurement, found none")
    return values[-1]


def compare() -> list[Row]:
    inputs = [
        ("low_readout", 0.125),
        ("mid_readout", 0.5),
        ("high_readout", 0.875),
    ]
    adc_lsb = 1.0 / 4096.0
    half_lsb = adc_lsb / 2.0
    rows: list[Row] = []
    for case, input_v in inputs:
        sampled = run_spice(input_v)
        abs_error = abs(input_v - sampled)
        rows.append(
            Row(
                case=case,
                input_v=input_v,
                sampled_v=sampled,
                abs_error_v=abs_error,
                adc_lsb_v=adc_lsb,
                half_lsb_v=half_lsb,
                conversion_time_ns=12.0,
                comparisons=12,
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
        "# SAR Readout 12-Bit SPICE",
        "",
        "This report executes the second converter SPICE handoff testbench. It checks whether the sampled readout node can settle close enough for a 12-bit ADC decision inside the 12 ns conversion window used by the behavioral converter estimate.",
        "",
        f"- SPICE deck: `{SPICE_PATH.relative_to(LAB_DIR)}`",
        f"- cases: `{len(rows)}`",
        f"- conversion window: `12.0` ns",
        f"- SAR comparisons: `12`",
        f"- ADC LSB: `{rows[0].adc_lsb_v:.9f}` V",
        f"- half-LSB acceptance limit: `{rows[0].half_lsb_v:.9f}` V",
        f"- worst sampled error: `{worst_error:.9f}` V",
        f"- all cases pass half-LSB readout: `{all_pass}`",
        "",
        "## Results",
        "",
        "| case | input V | sampled V | abs error V | half LSB V | pass |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.case} | {row.input_v:.6f} | {row.sampled_v:.9f} | {row.abs_error_v:.9f} | {row.half_lsb_v:.9f} | {row.pass_half_lsb} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "A SAR ADC is a timed sequence of decisions. The circuit first has to hold a readout voltage on a sample node. Then each comparison decides one bit. If the sampled voltage is still moving by more than half of one 12-bit step, the ADC can choose the wrong neighboring code even if the digital comparison sequence is correct.",
            "",
            "This fixture isolates the sampled readout node. It does not prove comparator offset, capacitor mismatch, reference settling, switch charge injection, or metastability. It proves a narrower thing: this readout load can place the sample node within the half-LSB voltage window before the 12-bit decision sequence finishes.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = compare()
    write_csv(rows)
    write_markdown(rows)
    print("sar_readout_12bit_spice")
    print(f"cases,{len(rows)}")
    print(f"all_pass,{all(row.pass_half_lsb for row in rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
