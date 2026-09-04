#!/usr/bin/env python3
"""Generate a local converter estimate that fills the circuit evidence contract."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "sources" / "evidence" / "converter-circuit-evidence-schema.json"
CONTRACT = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-evidence-contract.json"
BREAK_EVEN = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-break-even.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "local-converter-circuit-estimate.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "local-converter-circuit-estimate.md"


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
    contract = load_json(CONTRACT)
    break_even = load_json(BREAK_EVEN)
    target = break_even["target_boundary"]
    # These are local planning numbers. They are intentionally simple and explicit,
    # so a later SPICE/post-layout record can replace them field by field.
    adc_energy = 1024.0
    dac_energy = 22.4
    rows = 64
    columns = 4
    outputs_shared = 16
    payload = {
        "result_type": "converter_circuit_evidence",
        "converter_id": "local-sar12-dac10-planning-estimate",
        "measurement_level": "local_estimate",
        "target_boundary": {
            "adc_bits": target["adc_bits"],
            "dac_bits": target["dac_bits"],
            "output_noise_budget": target["highest_all_pass_out_noise"],
        },
        "energy": {
            "adc_energy_per_conversion": adc_energy,
            "dac_energy_per_row_drive": dac_energy,
            "energy_unit": "relative_to_4x4_converter_baseline",
            "method": "uses the local exponential bit-cost model from the converter break-even artifact",
        },
        "latency": {
            "adc_comparisons": target["latency_comparisons"],
            "conversion_time_ns": 12.0,
            "settling_time_ns": 4.0,
            "method": "one normalized SAR comparison step per output bit plus a local row-drive settling allowance",
        },
        "noise": {
            "output_noise_rms": 0.004,
            "input_referred_noise": 0.0009765625,
            "meets_output_noise_budget": True,
            "method": "set equal to the highest all-pass AIHWKIT target-noise replay budget, not measured circuit noise",
        },
        "area": {
            "adc_area_um2": 12288.0,
            "dac_area_um2": 2560.0,
            "replication_or_sharing_rule": "one shared 12-bit SAR readout path amortized across 16 output uses; 10-bit row drive budgeted per active row group",
            "method": "local linear bit-area placeholder, not layout",
        },
        "sharing": {
            "rows_served": rows,
            "columns_served": columns,
            "outputs_per_conversion_cost": outputs_shared,
            "converter_instances": columns,
        },
        "provenance": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "schema": str(SCHEMA.relative_to(ROOT)),
            "contract": str(CONTRACT.relative_to(ROOT)),
            "source_artifact": str(BREAK_EVEN.relative_to(ROOT)),
        },
        "claim_boundary": {
            "allowed": "fills the converter evidence contract with local planning numbers",
            "not_allowed": "does not replace break-even assumptions, measured converter energy, post-layout area, silicon noise, or board power",
        },
    }
    missing = missing_fields(schema, payload)
    claim_ready = (
        payload["measurement_level"] in {"post_layout_simulation", "measured_silicon"}
        and payload["noise"]["meets_output_noise_budget"] is True
        and not missing
    )
    output = {
        "result_type": "local_converter_circuit_estimate",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "schema": str(SCHEMA.relative_to(ROOT)),
            "contract": str(CONTRACT.relative_to(ROOT)),
            "break_even": str(BREAK_EVEN.relative_to(ROOT)),
        },
        "estimate": payload,
        "validation": {
            "missing_required_fields": missing,
            "schema_complete": not missing,
            "claim_ready_to_replace_break_even": claim_ready,
            "status": "local_estimate_complete_not_claim_ready",
        },
    }
    OUT_JSON.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Local Converter Circuit Estimate",
        "",
        "This file fills the converter evidence contract with local planning numbers. It is useful because every field is explicit. It is not measured evidence.",
        "",
        f"- status: `{output['validation']['status']}`",
        f"- claim-ready to replace break-even: `{claim_ready}`",
        f"- ADC bits: `{payload['target_boundary']['adc_bits']}`",
        f"- DAC bits: `{payload['target_boundary']['dac_bits']}`",
        f"- output noise RMS: `{payload['noise']['output_noise_rms']}`",
        f"- rows served: `{rows}`",
        f"- columns served: `{columns}`",
        f"- outputs sharing converter cost: `{outputs_shared}`",
        "",
        "## First-Principles Reading",
        "",
        "This estimate makes the hidden assumptions visible. The ADC cost is treated as the expensive edge decision. The DAC cost is treated as row-drive work. The latency is split into settling time and comparison time. The area is split into ADC and DAC area. The sharing rule says how many useful outputs pay for one converter cost.",
        "",
        "Because the measurement level is still `local_estimate`, this record cannot upgrade the claim. Its value is that a later circuit simulation can replace the same fields without changing the workflow.",
        "",
        "## Refused Claim",
        "",
        payload["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("local_converter_circuit_estimate")
    print(f"status,{output['validation']['status']}")
    print(f"schema_complete,{output['validation']['schema_complete']}")
    print(f"claim_ready,{claim_ready}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
