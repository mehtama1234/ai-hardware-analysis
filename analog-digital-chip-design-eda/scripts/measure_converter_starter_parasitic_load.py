#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
EXTRACTED = WORKBENCH / "extracted"
MEASUREMENTS = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-parasitic-load-estimate.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-parasitic-load-estimate.md"
OUT_CSV = MEASUREMENTS / "converter-starter-parasitic-load-estimate.csv"

SUPPLY_V = 1.8
ROW_DRIVER_R_OHM = 1_000.0
ADC_INPUT_R_OHM = 2_000.0
MUX_ON_R_OHM = 250.0


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def parse_cap_farad(value: str) -> float:
    match = re.fullmatch(r"([0-9.]+)([fpnum]?)", value.strip(), flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"unsupported capacitance value {value!r}")
    number = float(match.group(1))
    suffix = match.group(2).lower()
    scale = {
        "": 1.0,
        "f": 1e-15,
        "p": 1e-12,
        "n": 1e-9,
        "u": 1e-6,
        "m": 1e-3,
    }[suffix]
    return number * scale


def parse_caps(path: Path) -> list[dict[str, Any]]:
    caps = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) >= 4 and parts[0].lower().startswith("c"):
            caps.append(
                {
                    "name": parts[0],
                    "node_a": parts[1],
                    "node_b": parts[2],
                    "cap_f": parse_cap_farad(parts[3]),
                }
            )
    return caps


def node_cap(caps: list[dict[str, Any]], node: str) -> float:
    return sum(item["cap_f"] for item in caps if node in {item["node_a"], item["node_b"]})


def pair_cap(caps: list[dict[str, Any]], node_a: str, node_b: str) -> float:
    pair = {node_a, node_b}
    return sum(item["cap_f"] for item in caps if {item["node_a"], item["node_b"]} == pair)


def rc_metrics(cap_f: float, resistance_ohm: float) -> dict[str, float]:
    tau_s = resistance_ohm * cap_f
    return {
        "cap_f": cap_f,
        "energy_j": 0.5 * cap_f * SUPPLY_V * SUPPLY_V,
        "tau_s": tau_s,
        "settle_0p1pct_s": -math.log(0.001) * tau_s,
    }


def build_report() -> dict[str, Any]:
    macro_spice = EXTRACTED / "aimc_converter_macro_layout_smoke.spice"
    row_spice = EXTRACTED / "row_dac_10b_layout_smoke.spice"
    sar_spice = EXTRACTED / "sar_readout_12b_layout_smoke.spice"
    mux_spice = EXTRACTED / "shared_converter_mux_layout_smoke.spice"

    macro_caps = parse_caps(macro_spice)
    row_caps = parse_caps(row_spice)
    sar_caps = parse_caps(sar_spice)
    mux_caps = parse_caps(mux_spice)

    rows = [
        {
            "object": "row_dac_10b.row_drive",
            "source": rel(row_spice),
            "meaning": "extracted row-drive pin capacitance in the starter row-DAC cell",
            **rc_metrics(node_cap(row_caps, "row_drive"), ROW_DRIVER_R_OHM),
        },
        {
            "object": "aimc_converter_macro.row_drive",
            "source": rel(macro_spice),
            "meaning": "extracted row-drive pin capacitance at the starter macro boundary",
            **rc_metrics(node_cap(macro_caps, "row_drive"), ROW_DRIVER_R_OHM),
        },
        {
            "object": "aimc_converter_macro.column_sense",
            "source": rel(macro_spice),
            "meaning": "extracted column-sense pin capacitance at the starter macro boundary",
            **rc_metrics(node_cap(macro_caps, "column_sense"), ADC_INPUT_R_OHM + MUX_ON_R_OHM),
        },
        {
            "object": "aimc_converter_macro.digital_code_out",
            "source": rel(macro_spice),
            "meaning": "extracted digital output pin capacitance at the starter macro boundary",
            **rc_metrics(node_cap(macro_caps, "digital_code_out"), ROW_DRIVER_R_OHM),
        },
        {
            "object": "shared_converter_mux.mux_bus",
            "source": rel(mux_spice),
            "meaning": "extracted mux bus capacitance in the starter shared converter mux",
            **rc_metrics(node_cap(mux_caps, "mux_bus"), MUX_ON_R_OHM + ADC_INPUT_R_OHM),
        },
        {
            "object": "sar_readout_12b.sample_in",
            "source": rel(sar_spice),
            "meaning": "extracted sample input capacitance in the starter SAR readout cell",
            **rc_metrics(node_cap(sar_caps, "sample_in"), ROW_DRIVER_R_OHM),
        },
        {
            "object": "aimc_converter_macro.row_to_column_coupling",
            "source": rel(macro_spice),
            "meaning": "direct extracted parasitic coupling between row drive and column sense",
            **rc_metrics(pair_cap(macro_caps, "row_drive", "column_sense"), ROW_DRIVER_R_OHM),
        },
    ]
    total_pin_energy = sum(item["energy_j"] for item in rows if item["object"] != "aimc_converter_macro.row_to_column_coupling")
    return {
        "result_type": "converter_starter_parasitic_load_estimate",
        "status": "starter_extracted_parasitic_load_estimated_not_converter_proof",
        "supply_v": SUPPLY_V,
        "row_driver_r_ohm": ROW_DRIVER_R_OHM,
        "adc_input_r_ohm": ADC_INPUT_R_OHM,
        "mux_on_r_ohm": MUX_ON_R_OHM,
        "source_netlists": [rel(path) for path in [row_spice, sar_spice, mux_spice, macro_spice]],
        "row_count": len(rows),
        "rows": rows,
        "total_estimated_pin_charge_energy_j": total_pin_energy,
        "max_settle_0p1pct_s": max(item["settle_0p1pct_s"] for item in rows),
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "uses extracted starter-layout capacitances to estimate local pin charging energy and first-order RC settling",
            "not_allowed": "does not simulate transistor converter behavior, comparator offset, DAC linearity, ADC decision error, supply current integration, DRC/LVS signoff, or accepted replacement economics",
        },
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "object",
                "source",
                "cap_f",
                "energy_j",
                "tau_s",
                "settle_0p1pct_s",
                "meaning",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Converter Starter Parasitic Load Estimate",
        "",
        f"- status: `{report['status']}`",
        f"- supply V: `{report['supply_v']}`",
        f"- row driver R ohm: `{report['row_driver_r_ohm']}`",
        f"- ADC input R ohm: `{report['adc_input_r_ohm']}`",
        f"- mux on R ohm: `{report['mux_on_r_ohm']}`",
        f"- row count: `{report['row_count']}`",
        f"- total estimated pin charge energy J: `{report['total_estimated_pin_charge_energy_j']:.6e}`",
        f"- max settle 0.1 percent s: `{report['max_settle_0p1pct_s']:.6e}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{rel(OUT_CSV)}`",
        "",
        "## First Principle",
        "",
        "An extracted capacitance tells us how much charge a node must move when it switches. With voltage fixed, the first-order switching energy is one half times capacitance times voltage squared. With a chosen driver resistance, the first-order settling time is resistance times capacitance.",
        "",
        "This is real information from layout extraction, but it is not the converter result. A converter also needs transistor behavior: settling shape, comparator decision, mismatch, noise, supply current, and the same-run system rerun. Capacitance alone can bound load; it cannot prove conversion quality.",
        "",
        "## Estimated Loads",
        "",
        "| object | capacitance F | energy J | settle 0.1% s | meaning |",
        "|---|---:|---:|---:|---|",
    ]
    for item in report["rows"]:
        lines.append(
            f"| `{item['object']}` | `{item['cap_f']:.6e}` | `{item['energy_j']:.6e}` | `{item['settle_0p1pct_s']:.6e}` | {item['meaning']} |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("converter_starter_parasitic_load_estimate")
    print(f"status,{report['status']}")
    print(f"row_count,{report['row_count']}")
    print(f"total_estimated_pin_charge_energy_j,{report['total_estimated_pin_charge_energy_j']:.6e}")
    print(f"max_settle_0p1pct_s,{report['max_settle_0p1pct_s']:.6e}")
    print(f"candidate_post_layout_written,{report['candidate_post_layout_written']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{OUT_CSV}")
    return 0 if report["status"] == "starter_extracted_parasitic_load_estimated_not_converter_proof" else 1


if __name__ == "__main__":
    raise SystemExit(main())
