#!/usr/bin/env python3
"""Create the converter circuit evidence contract and current placeholder."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "sources" / "evidence" / "converter-circuit-evidence-schema.json"
BREAK_EVEN = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-break-even.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-evidence-contract.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-evidence-contract.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def missing_fields(schema: dict, payload: dict) -> list[str]:
    missing: list[str] = []
    for field in schema["required_top_level_fields"]:
        if field not in payload:
            missing.append(field)
    nested = {
        "target_boundary": "required_target_boundary_fields",
        "energy": "required_energy_fields",
        "latency": "required_latency_fields",
        "noise": "required_noise_fields",
        "area": "required_area_fields",
        "sharing": "required_sharing_fields",
    }
    for parent, schema_key in nested.items():
        value = payload.get(parent) if isinstance(payload.get(parent), dict) else {}
        for field in schema[schema_key]:
            if field not in value:
                missing.append(f"{parent}.{field}")
    return missing


def main() -> None:
    schema = load_json(SCHEMA)
    break_even = load_json(BREAK_EVEN)
    target = break_even["target_boundary"]
    placeholder = {
        "result_type": "converter_circuit_evidence",
        "converter_id": "aihwkit-target-10b-input-12b-output-placeholder",
        "measurement_level": "local_estimate",
        "target_boundary": {
            "adc_bits": target["adc_bits"],
            "dac_bits": target["dac_bits"],
            "output_noise_budget": target["highest_all_pass_out_noise"],
        },
        "energy": {
            "adc_energy_per_conversion": None,
            "dac_energy_per_row_drive": None,
            "energy_unit": "missing",
            "method": "not measured",
        },
        "latency": {
            "adc_comparisons": target["latency_comparisons"],
            "conversion_time_ns": None,
            "settling_time_ns": None,
            "method": "not measured",
        },
        "noise": {
            "output_noise_rms": None,
            "input_referred_noise": None,
            "meets_output_noise_budget": False,
            "method": "not measured",
        },
        "area": {
            "adc_area_um2": None,
            "dac_area_um2": None,
            "replication_or_sharing_rule": "missing",
            "method": "not measured",
        },
        "sharing": {
            "rows_served": None,
            "columns_served": None,
            "outputs_per_conversion_cost": None,
            "converter_instances": None,
        },
        "provenance": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "schema": str(SCHEMA.relative_to(ROOT)),
            "source_artifact": str(BREAK_EVEN.relative_to(ROOT)),
        },
        "claim_boundary": {
            "allowed": "defines the converter evidence fields that must replace the local break-even assumptions",
            "not_allowed": "does not prove converter energy, converter latency, converter area, silicon noise, or board power",
        },
    }
    missing = missing_fields(schema, placeholder)
    claim_ready = (
        placeholder["measurement_level"] in {"post_layout_simulation", "measured_silicon"}
        and placeholder["noise"]["meets_output_noise_budget"] is True
        and not missing
    )
    payload = {
        "result_type": "converter_circuit_evidence_contract",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "schema": schema,
        "current_placeholder": placeholder,
        "validation": {
            "missing_required_fields": missing,
            "schema_complete": not missing,
            "claim_ready_to_replace_break_even": claim_ready,
            "status": "contract_defined_placeholder_not_claim_ready",
        },
        "required_next_evidence": [
            "transistor-level or post-layout ADC energy for 12-bit output conversion",
            "DAC row-driver energy for 10-bit input drive",
            "settling and conversion time for the same converter setting",
            "output noise RMS below 0.004 in the same scale used by the replay",
            "area and converter-sharing rule for the tile",
            "rerun of the break-even table with measured or post-layout numbers",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Converter Circuit Evidence Contract",
        "",
        "This page defines what must replace the local converter break-even assumptions.",
        "",
        f"- schema: `{SCHEMA.relative_to(ROOT)}`",
        f"- current status: `{payload['validation']['status']}`",
        f"- target ADC bits: `{placeholder['target_boundary']['adc_bits']}`",
        f"- target DAC bits: `{placeholder['target_boundary']['dac_bits']}`",
        f"- output noise budget: `{placeholder['target_boundary']['output_noise_budget']}`",
        f"- claim-ready to replace break-even: `{payload['validation']['claim_ready_to_replace_break_even']}`",
        "",
        "## First-Principles Reading",
        "",
        "The break-even page says the converter target can become useful only if real converter cost is low enough and shared across enough useful outputs. This contract says what real means.",
        "",
        "A converter proof has to measure five separate things. Energy says how much electrical work is spent per conversion. Latency says how long the signal must settle and how long the ADC decision takes. Noise says whether the converter output stays inside the 0.004 budget. Area says how much silicon is spent and whether converters are copied or shared. Sharing says how many rows, columns, and outputs pay for one converter cost.",
        "",
        "Without those fields, a converter number is only a planning estimate. With those fields, the system can rerun the break-even table using circuit or measured evidence instead of assumptions.",
        "",
        "## Required Fields",
        "",
    ]
    for field in schema["required_top_level_fields"]:
        lines.append(f"- `{field}`")
    lines.extend(
        [
            "",
            "## Measurement Levels",
            "",
        ]
    )
    for level in schema["allowed_measurement_levels"]:
        lines.append(f"- `{level}`")
    lines.extend(
        [
            "",
            "## Current Placeholder",
            "",
            "The current placeholder is intentionally not claim-ready. It carries the target bit and noise boundary forward, but leaves energy, latency, area, and sharing as missing measured facts.",
            "",
            "## Required Next Evidence",
            "",
            *[f"- {item}" for item in payload["required_next_evidence"]],
            "",
            "## Refused Claim",
            "",
            placeholder["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("converter_circuit_evidence_contract")
    print(f"status,{payload['validation']['status']}")
    print(f"claim_ready,{payload['validation']['claim_ready_to_replace_break_even']}")
    print(f"schema_complete,{payload['validation']['schema_complete']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
