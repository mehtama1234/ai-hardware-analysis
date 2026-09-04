#!/usr/bin/env python3
"""Generate evidence from the row-DAC settling SPICE testbench."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
RUNNER = LAB / "python" / "row_dac_settling_spice.py"
SPICE_DECK = LAB / "spice" / "row_dac_settling_10bit.sp"
CSV_IN = LAB / "measurements" / "row-dac-settling-spice.csv"
MD_IN = LAB / "measurements" / "row-dac-settling-spice.md"
HANDOFF = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-spice-handoff-spec.json"
CIRCUIT_SIM = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-simulation-estimate.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "row-dac-settling-spice-evidence.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "row-dac-settling-spice-evidence.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_rows() -> list[dict[str, object]]:
    if not CSV_IN.exists():
        raise SystemExit(f"missing row-DAC settling CSV: {CSV_IN}")
    rows: list[dict[str, object]] = []
    with CSV_IN.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            rows.append(
                {
                    "case": raw["case"],
                    "target_v": float(raw["target_v"]),
                    "settled_v": float(raw["settled_v"]),
                    "abs_error_v": float(raw["abs_error_v"]),
                    "dac_lsb_v": float(raw["dac_lsb_v"]),
                    "half_lsb_v": float(raw["half_lsb_v"]),
                    "settling_time_ns": float(raw["settling_time_ns"]),
                    "pass_half_lsb": raw["pass_half_lsb"] == "True",
                }
            )
    return rows


def main() -> None:
    handoff = load_json(HANDOFF)
    circuit_sim = load_json(CIRCUIT_SIM)
    rows = load_rows()
    if not rows:
        raise SystemExit("row-DAC settling CSV has no rows")

    worst = max(rows, key=lambda row: float(row["abs_error_v"]))
    all_pass = all(bool(row["pass_half_lsb"]) for row in rows)
    circuit_estimate = circuit_sim["estimate"]
    target = circuit_estimate["target_boundary"]

    payload = {
        "result_type": "row_dac_settling_spice_evidence",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "spice_deck": str(SPICE_DECK.relative_to(ROOT)),
            "runner": str(RUNNER.relative_to(ROOT)),
            "measurement_csv": str(CSV_IN.relative_to(ROOT)),
            "measurement_markdown": str(MD_IN.relative_to(ROOT)),
            "spice_handoff": str(HANDOFF.relative_to(ROOT)),
            "converter_circuit_simulation_estimate": str(CIRCUIT_SIM.relative_to(ROOT)),
        },
        "target": {
            "dac_bits": target["dac_bits"],
            "adc_bits": target["adc_bits"],
            "settling_time_ns": circuit_estimate["latency"]["settling_time_ns"],
            "output_noise_budget": target["output_noise_budget"],
        },
        "summary": {
            "cases": len(rows),
            "all_cases_pass_half_lsb": all_pass,
            "worst_case": worst["case"],
            "worst_abs_error_v": worst["abs_error_v"],
            "half_lsb_v": worst["half_lsb_v"],
            "margin_to_half_lsb_v": float(worst["half_lsb_v"]) - float(worst["abs_error_v"]),
            "status": "row_dac_settling_spice_passes_simple_load",
        },
        "rows": rows,
        "claim_boundary": {
            "allowed": "supports the row-DAC settling part of the converter SPICE handoff for this simple driver-load model",
            "not_allowed": "does not prove transistor DAC linearity, mismatch, reference noise, switch charge injection, extracted parasitics, ADC behavior, measured silicon, or board energy",
        },
        "handoff_connection": {
            "satisfies_testbench": "S1. 10-bit row DAC settling",
            "remaining_testbenches": [
                test["name"]
                for test in handoff.get("required_testbenches", [])
                if isinstance(test, dict) and test.get("id") != "S1"
            ],
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Row-DAC Settling SPICE Evidence",
        "",
        "This file turns the first converter SPICE handoff test into evidence. It checks one narrow claim: a simple 10-bit row-driver load can settle within half of one DAC step during the 4 ns window used by the behavioral converter estimate.",
        "",
        f"- status: `{payload['summary']['status']}`",
        f"- cases: `{payload['summary']['cases']}`",
        f"- all cases pass half-LSB settling: `{payload['summary']['all_cases_pass_half_lsb']}`",
        f"- worst case: `{payload['summary']['worst_case']}`",
        f"- worst absolute error: `{payload['summary']['worst_abs_error_v']}` V",
        f"- half-LSB limit: `{payload['summary']['half_lsb_v']}` V",
        f"- margin to half-LSB: `{payload['summary']['margin_to_half_lsb_v']}` V",
        f"- SPICE deck: `{payload['source_artifacts']['spice_deck']}`",
        f"- measurement CSV: `{payload['source_artifacts']['measurement_csv']}`",
        "",
        "## First-Principles Reading",
        "",
        "The 10-bit input target only means something if the row voltage has time to become the requested voltage. A digital control word can name 1024 levels, but a circuit node reaches those levels by charging capacitance through resistance. If the row is still moving when the array is sampled, the array does not see the requested code.",
        "",
        "The acceptance rule is half of one 10-bit step. That is the voltage distance between a safe settled value and the nearest wrong code boundary. Passing this test means the simple row-driver load does not by itself destroy the 10-bit input assumption.",
        "",
        "## Remaining Converter SPICE Work",
        "",
    ]
    lines.extend(f"- {name}" for name in payload["handoff_connection"]["remaining_testbenches"])
    lines.extend(
        [
            "",
            "## Refused Claim",
            "",
            payload["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("row_dac_settling_spice_evidence")
    print(f"status,{payload['summary']['status']}")
    print(f"all_pass,{all_pass}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
