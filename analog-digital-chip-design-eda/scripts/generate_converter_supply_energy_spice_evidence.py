#!/usr/bin/env python3
"""Generate evidence from the converter supply-energy SPICE testbench."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
RUNNER = LAB / "python" / "converter_supply_energy_spice.py"
SPICE_DECK = LAB / "spice" / "converter_supply_energy.sp"
CSV_IN = LAB / "measurements" / "converter-supply-energy-spice.csv"
MD_IN = LAB / "measurements" / "converter-supply-energy-spice.md"
HANDOFF = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-spice-handoff-spec.json"
CIRCUIT_SIM = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-simulation-estimate.json"
ROW_DAC = ROOT / "evidence" / "aimc-simulator-adapters" / "row-dac-settling-spice-evidence.json"
SAR_READOUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sar-readout-spice-evidence.json"
SHARED_LOADING = ROOT / "evidence" / "aimc-simulator-adapters" / "shared-converter-loading-spice-evidence.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-supply-energy-spice-evidence.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-supply-energy-spice-evidence.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_rows() -> list[dict[str, object]]:
    if not CSV_IN.exists():
        raise SystemExit(f"missing converter supply-energy CSV: {CSV_IN}")
    rows: list[dict[str, object]] = []
    with CSV_IN.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            rows.append(
                {
                    "case": raw["case"],
                    "input_v": float(raw["input_v"]),
                    "rail_v": float(raw["rail_v"]),
                    "dac_energy_j": float(raw["dac_energy_j"]),
                    "adc_energy_j": float(raw["adc_energy_j"]),
                    "mux_energy_j": float(raw["mux_energy_j"]),
                    "total_energy_j": float(raw["total_energy_j"]),
                    "conversion_time_ns": float(raw["conversion_time_ns"]),
                    "settling_time_ns": float(raw["settling_time_ns"]),
                    "pass_positive_energy": raw["pass_positive_energy"] == "True",
                }
            )
    return rows


def main() -> None:
    handoff = load_json(HANDOFF)
    circuit_sim = load_json(CIRCUIT_SIM)
    load_json(ROW_DAC)
    load_json(SAR_READOUT)
    load_json(SHARED_LOADING)
    rows = load_rows()
    if not rows:
        raise SystemExit("converter supply-energy CSV has no rows")

    worst = max(rows, key=lambda row: float(row["total_energy_j"]))
    all_pass = all(bool(row["pass_positive_energy"]) for row in rows)
    target = circuit_sim["estimate"]["target_boundary"]

    payload = {
        "result_type": "converter_supply_energy_spice_evidence",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "spice_deck": str(SPICE_DECK.relative_to(ROOT)),
            "runner": str(RUNNER.relative_to(ROOT)),
            "measurement_csv": str(CSV_IN.relative_to(ROOT)),
            "measurement_markdown": str(MD_IN.relative_to(ROOT)),
            "spice_handoff": str(HANDOFF.relative_to(ROOT)),
            "converter_circuit_simulation_estimate": str(CIRCUIT_SIM.relative_to(ROOT)),
            "row_dac_settling_spice": str(ROW_DAC.relative_to(ROOT)),
            "sar_readout_spice": str(SAR_READOUT.relative_to(ROOT)),
            "shared_converter_loading_spice": str(SHARED_LOADING.relative_to(ROOT)),
        },
        "target": {
            "adc_bits": target["adc_bits"],
            "dac_bits": target["dac_bits"],
            "output_noise_budget": target["output_noise_budget"],
            "rail_v": worst["rail_v"],
            "settling_time_ns": worst["settling_time_ns"],
            "conversion_time_ns": worst["conversion_time_ns"],
        },
        "summary": {
            "cases": len(rows),
            "all_cases_have_positive_energy": all_pass,
            "worst_case": worst["case"],
            "worst_total_energy_j": worst["total_energy_j"],
            "worst_dac_energy_j": worst["dac_energy_j"],
            "worst_adc_energy_j": worst["adc_energy_j"],
            "worst_mux_energy_j": worst["mux_energy_j"],
            "status": "converter_supply_energy_spice_complete_simple_load",
        },
        "rows": rows,
        "claim_boundary": {
            "allowed": "supports supply-energy accounting for the simple row-drive, ADC-reference, and shared-mux load model",
            "not_allowed": "does not prove extracted converter energy, bias current, clock power, leakage, comparator short-circuit current, measured board power, post-layout behavior, or measured silicon",
        },
        "handoff_connection": {
            "satisfies_testbench": "S4. energy accounting",
            "completed_testbenches": [
                "S1. 10-bit row DAC settling",
                "S2. 12-bit SAR readout decision",
                "S3. shared converter loading",
                "S4. energy accounting",
            ],
            "remaining_testbenches": [
                test["name"]
                for test in handoff.get("required_testbenches", [])
                if isinstance(test, dict) and test.get("id") not in {"S1", "S2", "S3", "S4"}
            ],
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Supply Energy SPICE Evidence",
        "",
        "This file turns the fourth converter SPICE handoff test into evidence. It checks one narrow energy claim: the simple converter load model now has named rail energy for row drive, ADC-reference charging, and shared-mux charging.",
        "",
        f"- status: `{payload['summary']['status']}`",
        f"- cases: `{payload['summary']['cases']}`",
        f"- all cases have positive integrated energy: `{payload['summary']['all_cases_have_positive_energy']}`",
        f"- worst case: `{payload['summary']['worst_case']}`",
        f"- worst total energy: `{payload['summary']['worst_total_energy_j']}` J",
        f"- worst DAC energy: `{payload['summary']['worst_dac_energy_j']}` J",
        f"- worst ADC energy: `{payload['summary']['worst_adc_energy_j']}` J",
        f"- worst mux energy: `{payload['summary']['worst_mux_energy_j']}` J",
        f"- rail: `{payload['target']['rail_v']}` V",
        f"- SPICE deck: `{payload['source_artifacts']['spice_deck']}`",
        f"- measurement CSV: `{payload['source_artifacts']['measurement_csv']}`",
        "",
        "## First-Principles Reading",
        "",
        "A converter can pass a voltage-error test and still fail as hardware if the signal costs too much energy to create and read. Energy accounting asks how much charge each source moves through the rail during the same timing window used by the accuracy checks.",
        "",
        "This is the missing accounting link after row-DAC settling, SAR readout, and shared loading. The result gives a circuit-derived scale for the clean load model. It still cannot replace break-even by itself, because a real replacement needs post-layout parasitics or measured silicon.",
        "",
        "## Remaining Converter SPICE Work",
        "",
    ]
    if payload["handoff_connection"]["remaining_testbenches"]:
        lines.extend(f"- {name}" for name in payload["handoff_connection"]["remaining_testbenches"])
    else:
        lines.append("- none; all four executable handoff tests now have local SPICE evidence")
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

    print("converter_supply_energy_spice_evidence")
    print(f"status,{payload['summary']['status']}")
    print(f"all_pass,{all_pass}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
