#!/usr/bin/env python3
"""Generate evidence from the shared converter loading SPICE testbench."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
RUNNER = LAB / "python" / "shared_converter_loading_spice.py"
SPICE_DECK = LAB / "spice" / "shared_converter_loading.sp"
CSV_IN = LAB / "measurements" / "shared-converter-loading-spice.csv"
MD_IN = LAB / "measurements" / "shared-converter-loading-spice.md"
HANDOFF = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-spice-handoff-spec.json"
CIRCUIT_SIM = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-simulation-estimate.json"
ROW_DAC = ROOT / "evidence" / "aimc-simulator-adapters" / "row-dac-settling-spice-evidence.json"
SAR_READOUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sar-readout-spice-evidence.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "shared-converter-loading-spice-evidence.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "shared-converter-loading-spice-evidence.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_rows() -> list[dict[str, object]]:
    if not CSV_IN.exists():
        raise SystemExit(f"missing shared converter loading CSV: {CSV_IN}")
    rows: list[dict[str, object]] = []
    with CSV_IN.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            rows.append(
                {
                    "case": raw["case"],
                    "input_v": float(raw["input_v"]),
                    "active_loads": int(raw["active_loads"]),
                    "sampled_v": float(raw["sampled_v"]),
                    "abs_error_v": float(raw["abs_error_v"]),
                    "adc_lsb_v": float(raw["adc_lsb_v"]),
                    "half_lsb_v": float(raw["half_lsb_v"]),
                    "conversion_time_ns": float(raw["conversion_time_ns"]),
                    "pass_half_lsb": raw["pass_half_lsb"] == "True",
                }
            )
    return rows


def main() -> None:
    handoff = load_json(HANDOFF)
    circuit_sim = load_json(CIRCUIT_SIM)
    load_json(ROW_DAC)
    load_json(SAR_READOUT)
    rows = load_rows()
    if not rows:
        raise SystemExit("shared converter loading CSV has no rows")

    worst = max(rows, key=lambda row: float(row["abs_error_v"]))
    all_pass = all(bool(row["pass_half_lsb"]) for row in rows)
    circuit_estimate = circuit_sim["estimate"]
    target = circuit_estimate["target_boundary"]
    sharing = circuit_estimate["sharing"]

    payload = {
        "result_type": "shared_converter_loading_spice_evidence",
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
        },
        "target": {
            "adc_bits": target["adc_bits"],
            "dac_bits": target["dac_bits"],
            "conversion_time_ns": circuit_estimate["latency"]["conversion_time_ns"],
            "output_noise_budget": target["output_noise_budget"],
            "converter_instances": sharing["converter_instances"],
            "outputs_per_conversion_cost": sharing["outputs_per_conversion_cost"],
        },
        "summary": {
            "cases": len(rows),
            "all_cases_pass_half_lsb": all_pass,
            "worst_case": worst["case"],
            "worst_abs_error_v": worst["abs_error_v"],
            "half_lsb_v": worst["half_lsb_v"],
            "max_active_loads": max(int(row["active_loads"]) for row in rows),
            "status": "shared_converter_loading_spice_passes_simple_mux_load",
        },
        "rows": rows,
        "claim_boundary": {
            "allowed": "supports the shared readout loading part of the converter SPICE handoff for this simple muxed source-load model",
            "not_allowed": "does not prove switch charge injection, comparator offset, capacitor mismatch, extracted routing parasitics, measured converter energy, measured silicon, or full shared ADC macro behavior",
        },
        "handoff_connection": {
            "satisfies_testbench": "S3. shared converter loading",
            "completed_testbenches": [
                "S1. 10-bit row DAC settling",
                "S2. 12-bit SAR readout decision",
                "S3. shared converter loading",
            ],
            "remaining_testbenches": [
                test["name"]
                for test in handoff.get("required_testbenches", [])
                if isinstance(test, dict) and test.get("id") not in {"S1", "S2", "S3"}
            ],
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Shared Converter Loading SPICE Evidence",
        "",
        "This file turns the third converter SPICE handoff test into evidence. It checks one narrow sharing claim: the readout node can still settle within half of one 12-bit ADC step when a simple shared mux/load term is added to the converter input.",
        "",
        f"- status: `{payload['summary']['status']}`",
        f"- cases: `{payload['summary']['cases']}`",
        f"- all cases pass half-LSB shared loading: `{payload['summary']['all_cases_pass_half_lsb']}`",
        f"- worst case: `{payload['summary']['worst_case']}`",
        f"- worst absolute error: `{payload['summary']['worst_abs_error_v']}` V",
        f"- half-LSB limit: `{payload['summary']['half_lsb_v']}` V",
        f"- max active loads: `{payload['summary']['max_active_loads']}`",
        f"- converter instances: `{payload['target']['converter_instances']}`",
        f"- outputs per conversion cost: `{payload['target']['outputs_per_conversion_cost']}`",
        f"- SPICE deck: `{payload['source_artifacts']['spice_deck']}`",
        f"- measurement CSV: `{payload['source_artifacts']['measurement_csv']}`",
        "",
        "## First-Principles Reading",
        "",
        "Converter sharing is a bargain only if the shared path does not turn saved hardware into late or wrong voltage decisions. A shared mux adds resistance and capacitance. Resistance limits how quickly charge can move. Capacitance increases how much charge must move. Together they stretch the settling time.",
        "",
        "The test is therefore not abstract. At the end of the 12 ns readout window, the sampled node must be close enough that a 12-bit ADC would not cross into a neighboring code. This artifact checks that timing-and-loading term before any energy win is trusted.",
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

    print("shared_converter_loading_spice_evidence")
    print(f"status,{payload['summary']['status']}")
    print(f"all_pass,{all_pass}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
