#!/usr/bin/env python3
"""Generate a strict post-layout converter evidence contract."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_SCHEMA = ROOT / "sources" / "evidence" / "converter-circuit-evidence-schema.json"
POST_SCHEMA = ROOT / "sources" / "evidence" / "converter-post-layout-evidence-schema.json"
READINESS = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-readiness.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-evidence-contract.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-evidence-contract.md"
PLACEHOLDER_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "dry-run" / "converter-post-layout-evidence.placeholder.json"


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
        "extraction": "required_extraction_fields",
        "simulation": "required_simulation_fields",
        "energy": "required_energy_fields",
        "latency": "required_latency_fields",
        "noise": "required_noise_fields",
        "area": "required_area_fields",
        "break_even_rerun": "required_break_even_rerun_fields",
        "provenance": "required_provenance_fields",
    }
    for parent, schema_key in nested.items():
        value = payload.get(parent) if isinstance(payload.get(parent), dict) else {}
        for field in schema[schema_key]:
            if field not in value:
                missing.append(f"{parent}.{field}")
    return missing


def main() -> None:
    base_schema = load_json(BASE_SCHEMA)
    post_schema = load_json(POST_SCHEMA)
    readiness = load_json(READINESS)
    placeholder = {
        "result_type": "converter_post_layout_evidence",
        "converter_id": "aihwkit-target-10b-input-12b-output-post-layout-placeholder",
        "measurement_level": "post_layout_simulation",
        "target_boundary": {
            "adc_bits": 12,
            "dac_bits": 10,
            "output_noise_budget": 0.004,
        },
        "extraction": {
            "extracted_netlist": None,
            "parasitic_format": None,
            "includes_row_dac": False,
            "includes_sar_readout": False,
            "includes_shared_mux": False,
            "includes_references": False,
            "includes_sample_path": False,
        },
        "simulation": {
            "simulator": None,
            "command": None,
            "process_corner": None,
            "voltage_v": None,
            "temperature_c": None,
            "model_files": [],
            "run_id": "missing-post-layout-run-id",
        },
        "energy": {
            "adc_energy_per_conversion": None,
            "dac_energy_per_row_drive": None,
            "energy_unit": "joule",
            "method": "missing extracted post-layout run",
            "run_id": "missing-post-layout-run-id",
        },
        "latency": {
            "adc_comparisons": 12,
            "conversion_time_ns": None,
            "settling_time_ns": None,
            "method": "missing extracted post-layout run",
            "run_id": "missing-post-layout-run-id",
        },
        "noise": {
            "output_noise_rms": None,
            "input_referred_noise": None,
            "meets_output_noise_budget": False,
            "method": "missing extracted post-layout run",
            "run_id": "missing-post-layout-run-id",
        },
        "area": {
            "adc_area_um2": None,
            "dac_area_um2": None,
            "replication_or_sharing_rule": "missing extracted layout area",
            "method": "missing extracted post-layout run",
            "run_id": "missing-post-layout-run-id",
        },
        "sharing": {
            "rows_served": 64,
            "columns_served": 4,
            "outputs_per_conversion_cost": 16,
            "converter_instances": 4,
        },
        "break_even_rerun": {
            "rerun_artifact": None,
            "uses_extracted_energy": False,
            "uses_extracted_latency": False,
            "uses_extracted_noise": False,
            "uses_extracted_area": False,
            "uses_same_sharing_rule": True,
            "replacement_decision": "not_ready",
            "run_id": "missing-post-layout-run-id",
        },
        "provenance": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "base_schema": str(BASE_SCHEMA.relative_to(ROOT)),
            "post_layout_schema": str(POST_SCHEMA.relative_to(ROOT)),
            "readiness": str(READINESS.relative_to(ROOT)),
            "source_schema": str(POST_SCHEMA.relative_to(ROOT)),
            "run_id": "missing-post-layout-run-id",
        },
        "claim_boundary": {
            "allowed": "defines the post-layout payload fields needed before converter break-even replacement",
            "not_allowed": "does not claim extracted netlists, post-layout simulation results, measured silicon, DRC/LVS signoff, or board energy exist",
        },
    }
    missing = missing_fields(post_schema, placeholder)
    required_true_flags = [
        placeholder["extraction"]["includes_row_dac"],
        placeholder["extraction"]["includes_sar_readout"],
        placeholder["extraction"]["includes_shared_mux"],
        placeholder["extraction"]["includes_references"],
        placeholder["extraction"]["includes_sample_path"],
        placeholder["break_even_rerun"]["uses_extracted_energy"],
        placeholder["break_even_rerun"]["uses_extracted_latency"],
        placeholder["break_even_rerun"]["uses_extracted_noise"],
        placeholder["break_even_rerun"]["uses_extracted_area"],
    ]
    claim_ready = (
        placeholder["measurement_level"] in set(post_schema["allowed_measurement_levels"])
        and not missing
        and all(required_true_flags)
        and placeholder["noise"]["meets_output_noise_budget"] is True
        and placeholder["break_even_rerun"]["replacement_decision"] != "not_ready"
    )
    payload = {
        "result_type": "converter_post_layout_evidence_contract",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "base_converter_schema": base_schema,
        "post_layout_schema": post_schema,
        "current_placeholder": placeholder,
        "source_artifacts": {
            "readiness": str(READINESS.relative_to(ROOT)),
            "placeholder_payload": str(PLACEHOLDER_JSON.relative_to(ROOT)),
        },
        "validation": {
            "status": "post_layout_contract_defined_placeholder_not_claim_ready",
            "schema_complete": not missing,
            "claim_ready_to_replace_break_even": claim_ready,
            "missing_required_fields": missing,
            "placeholder_refuses_replacement": True,
        },
    }
    PLACEHOLDER_JSON.parent.mkdir(parents=True, exist_ok=True)
    PLACEHOLDER_JSON.write_text(json.dumps(placeholder, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Converter Post-Layout Evidence Contract",
        "",
        "This file defines the exact payload that must exist before converter break-even assumptions can be replaced.",
        "",
        f"- status: `{payload['validation']['status']}`",
        f"- schema complete: `{payload['validation']['schema_complete']}`",
        f"- claim-ready to replace break-even: `{payload['validation']['claim_ready_to_replace_break_even']}`",
        f"- placeholder refuses replacement: `{payload['validation']['placeholder_refuses_replacement']}`",
        f"- post-layout schema: `{POST_SCHEMA.relative_to(ROOT)}`",
        f"- dry-run placeholder payload: `{PLACEHOLDER_JSON.relative_to(ROOT)}`",
        "",
        "## First-Principles Reading",
        "",
        "Post-layout evidence is not just a stronger number. It is a different object. The schematic says what circuit was intended. The extracted netlist says what circuit the geometry actually made after wires and parasitics were added.",
        "",
        "For the converter to replace break-even assumptions, the payload must tie the same target to four things at once: extracted circuit contents, simulation conditions, measured energy and timing, and a break-even rerun that actually uses those extracted values.",
        "",
        "## Required Top-Level Fields",
        "",
    ]
    lines.extend(f"- `{field}`" for field in post_schema["required_top_level_fields"])
    lines.extend(
        [
            "",
            "## Required Extraction Fields",
            "",
        ]
    )
    lines.extend(f"- `{field}`" for field in post_schema["required_extraction_fields"])
    for title, key in [
        ("Required Simulation Fields", "required_simulation_fields"),
        ("Required Energy Fields", "required_energy_fields"),
        ("Required Latency Fields", "required_latency_fields"),
        ("Required Noise Fields", "required_noise_fields"),
        ("Required Area Fields", "required_area_fields"),
    ]:
        lines.extend(["", f"## {title}", ""])
        lines.extend(f"- `{field}`" for field in post_schema[key])
    lines.extend(
        [
            "",
            "## Required Break-Even Rerun Fields",
            "",
        ]
    )
    lines.extend(f"- `{field}`" for field in post_schema["required_break_even_rerun_fields"])
    lines.extend(["", "## Required Provenance Fields", ""])
    lines.extend(f"- `{field}`" for field in post_schema["required_provenance_fields"])
    lines.extend(["", "## Same-Run Rule", "", post_schema["same_run_rule"]])
    lines.extend(
        [
            "",
            "## Refused Claim",
            "",
            placeholder["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("converter_post_layout_evidence_contract")
    print(f"status,{payload['validation']['status']}")
    print(f"claim_ready,{payload['validation']['claim_ready_to_replace_break_even']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"placeholder,{PLACEHOLDER_JSON}")


if __name__ == "__main__":
    main()
