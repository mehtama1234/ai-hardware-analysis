#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]
SPICE_PATH = LAB_DIR / "spice" / "shared_converter_loading.sp"
MEASUREMENTS_DIR = LAB_DIR / "measurements"
CSV_OUT = MEASUREMENTS_DIR / "shared-converter-loading-spice.csv"
MD_OUT = MEASUREMENTS_DIR / "shared-converter-loading-spice.md"


@dataclass(frozen=True)
class Row:
    case: str
    input_v: float
    active_loads: int
    sampled_v: float
    abs_error_v: float
    adc_lsb_v: float
    half_lsb_v: float
    conversion_time_ns: float
    pass_half_lsb: bool


def run_spice(input_v: float, active_loads: int) -> float:
    template = SPICE_PATH.read_text(encoding="utf-8")
    deck = re.sub(r"\.param vin=[^\n]+", f".param vin={input_v}", template)
    deck = re.sub(r"\.param active_loads=[^\n]+", f".param active_loads={active_loads}", deck)
    with tempfile.NamedTemporaryFile("w", suffix=".sp", dir=LAB_DIR, delete=False, encoding="utf-8") as handle:
        handle.write(deck)
        temp_path = Path(handle.name)
    result = subprocess.run(["ngspice", "-b", str(temp_path)], cwd=LAB_DIR, text=True, capture_output=True, check=False)
    temp_path.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    values: list[float] = []
    for raw in result.stdout.splitlines():
        match = re.search(r"vshared\s+=\s+([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError("expected shared converter loading measurement, found none")
    return values[-1]


def compare() -> list[Row]:
    cases = [
        ("single_load_mid", 0.5, 1),
        ("shared_16_mid", 0.5, 16),
        ("shared_16_high", 0.875, 16),
        ("shared_32_mid_stress", 0.5, 32),
    ]
    adc_lsb = 1.0 / 4096.0
    half_lsb = adc_lsb / 2.0
    rows: list[Row] = []
    for case, input_v, active_loads in cases:
        sampled = run_spice(input_v, active_loads)
        abs_error = abs(input_v - sampled)
        rows.append(
            Row(
                case=case,
                input_v=input_v,
                active_loads=active_loads,
                sampled_v=sampled,
                abs_error_v=abs_error,
                adc_lsb_v=adc_lsb,
                half_lsb_v=half_lsb,
                conversion_time_ns=12.0,
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
        "# Shared Converter Loading SPICE",
        "",
        "This report executes the third converter SPICE handoff testbench. It checks whether a shared readout path can still settle inside the 12-bit half-LSB window when extra mux and sample capacitance are attached to the converter input.",
        "",
        f"- SPICE deck: `{SPICE_PATH.relative_to(LAB_DIR)}`",
        f"- cases: `{len(rows)}`",
        f"- conversion window: `12.0` ns",
        f"- ADC LSB: `{rows[0].adc_lsb_v:.9f}` V",
        f"- half-LSB acceptance limit: `{rows[0].half_lsb_v:.9f}` V",
        f"- worst sampled error: `{worst_error:.9f}` V",
        f"- all cases pass half-LSB shared loading: `{all_pass}`",
        "",
        "## Results",
        "",
        "| case | input V | active loads | sampled V | abs error V | half LSB V | pass |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.case} | {row.input_v:.6f} | {row.active_loads} | {row.sampled_v:.9f} | {row.abs_error_v:.9f} | {row.half_lsb_v:.9f} | {row.pass_half_lsb} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "Sharing a converter saves area and energy only if the shared path does not move the signal too much before the ADC decision. The extra mux and sample load behave like extra capacitance. Extra capacitance does not change the final voltage, but it slows the movement toward that voltage.",
            "",
            "The physical question is therefore small and testable: after the same 12 ns readout window, is the sampled node still within half of one 12-bit code step? If not, converter sharing has made the numerical readout too late even if the digital schedule looks efficient.",
            "",
            "This fixture checks that loading term only. It does not prove switch charge injection, comparator offset, capacitor mismatch, routing parasitics, extracted layout, or measured converter energy.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = compare()
    write_csv(rows)
    write_markdown(rows)
    print("shared_converter_loading_spice")
    print(f"cases,{len(rows)}")
    print(f"all_pass,{all(row.pass_half_lsb for row in rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
