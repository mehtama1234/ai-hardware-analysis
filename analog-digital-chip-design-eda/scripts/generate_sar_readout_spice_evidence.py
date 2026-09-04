#!/usr/bin/env python3
"""Generate evidence from the 12-bit SAR readout SPICE testbench."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
RUNNER = LAB / "python" / "sar_readout_12bit_spice.py"
SPICE_DECK = LAB / "spice" / "sar_readout_12bit.sp"
CSV_IN = LAB / "measurements" / "sar-readout-12bit-spice.csv"
MD_IN = LAB / "measurements" / "sar-readout-12bit-spice.md"
HANDOFF = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-spice-handoff-spec.json"
CIRCUIT_SIM = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-simulation-estimate.json"
ROW_DAC = ROOT / "evidence" / "aimc-simulator-adapters" / "row-dac-settling-spice-evidence.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sar-readout-spice-evidence.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sar-readout-spice-evidence.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_rows() -> list[dict[str, object]]:
    if not CSV_IN.exists():
        raise SystemExit(f"missing SAR readout CSV: {CSV_IN}")
    rows: list[dict[str, object]] = []
    with CSV_IN.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            rows.append(
                {
                    "case": raw["case"],
                    "input_v": float(raw["input_v"]),
                    "sampled_v": float(raw["sampled_v"]),
                    "abs_error_v": float(raw["abs_error_v"]),
                    "adc_lsb_v": float(raw["adc_lsb_v"]),
                    "half_lsb_v": float(raw["half_lsb_v"]),
                    "conversion_time_ns": float(raw["conversion_time_ns"]),
                    "comparisons": int(raw["comparisons"]),
                    "pass_half_lsb": raw["pass_half_lsb"] == "True",
                }
            )
    return rows


def main() -> None:
    handoff = load_json(HANDOFF)
    circuit_sim = load_json(CIRCUIT_SIM)
    load_json(ROW_DAC)
    rows = load_rows()
    if not rows:
        raise SystemExit("SAR readout CSV has no rows")

    worst = max(rows, key=lambda row: float(row["abs_error_v"]))
    all_pass = all(bool(row["pass_half_lsb"]) for row in rows)
    circuit_estimate = circuit_sim["estimate"]
    target = circuit_estimate["target_boundary"]

    payload = {
        "result_type": "sar_readout_spice_evidence",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "spice_deck": str(SPICE_DECK.relative_to(ROOT)),
            "runner": str(RUNNER.relative_to(ROOT)),
            "measurement_csv": str(CSV_IN.relative_to(ROOT)),
            "measurement_markdown": str(MD_IN.relative_to(ROOT)),
            "spice_handoff": str(HANDOFF.relative_to(ROOT)),
            "converter_circuit_simulation_estimate": str(CIRCUIT_SIM.relative_to(ROOT)),
            "row_dac_settling_spice": str(ROW_DAC.relative_to(ROOT)),
        },
        "target": {
            "adc_bits": target["adc_bits"],
            "dac_bits": target["dac_bits"],
            "conversion_time_ns": circuit_estimate["latency"]["conversion_time_ns"],
            "output_noise_budget": target["output_noise_budget"],
        },
        "summary": {
            "cases": len(rows),
            "all_cases_pass_half_lsb": all_pass,
            "worst_case": worst["case"],
            "worst_abs_error_v": worst["abs_error_v"],
            "half_lsb_v": worst["half_lsb_v"],
            "comparisons": worst["comparisons"],
            "status": "sar_readout_spice_passes_simple_sample_load",
        },
        "rows": rows,
        "claim_boundary": {
            "allowed": "supports the sampled readout settling part of the 12-bit SAR handoff for this simple source-load model",
            "not_allowed": "does not prove comparator offset, capacitor mismatch, reference settling, switch charge injection, metastability, extracted parasitics, measured silicon, or board energy",
        },
        "handoff_connection": {
            "satisfies_testbench": "S2. 12-bit SAR readout decision",
            "completed_testbenches": [
                "S1. 10-bit row DAC settling",
                "S2. 12-bit SAR readout decision",
            ],
            "remaining_testbenches": [
                test["name"]
                for test in handoff.get("required_testbenches", [])
                if isinstance(test, dict) and test.get("id") not in {"S1", "S2"}
            ],
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# SAR Readout SPICE Evidence",
        "",
        "This file turns the second converter SPICE handoff test into evidence. It checks one narrow readout claim: the sampled voltage can settle within half of one 12-bit ADC step during the 12 ns conversion window used by the behavioral converter estimate.",
        "",
        f"- status: `{payload['summary']['status']}`",
        f"- cases: `{payload['summary']['cases']}`",
        f"- all cases pass half-LSB readout: `{payload['summary']['all_cases_pass_half_lsb']}`",
        f"- worst case: `{payload['summary']['worst_case']}`",
        f"- worst absolute error: `{payload['summary']['worst_abs_error_v']}` V",
        f"- half-LSB limit: `{payload['summary']['half_lsb_v']}` V",
        f"- SAR comparisons: `{payload['summary']['comparisons']}`",
        f"- SPICE deck: `{payload['source_artifacts']['spice_deck']}`",
        f"- measurement CSV: `{payload['source_artifacts']['measurement_csv']}`",
        "",
        "## First-Principles Reading",
        "",
        "A 12-bit ADC claim is a claim about small voltage differences. One full-scale volt divided into 4096 codes gives a step of about `0.000244` V. Half of that step is the safe distance from the nearest neighboring decision boundary.",
        "",
        "The SAR sequence can only make correct bit decisions if the sampled readout node is already inside that half-step window. This SPICE fixture checks that sampled-node part of the claim. It does not yet check comparator offset, reference movement, capacitor mismatch, or switching kickback.",
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

    print("sar_readout_spice_evidence")
    print(f"status,{payload['summary']['status']}")
    print(f"all_pass,{all_pass}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
