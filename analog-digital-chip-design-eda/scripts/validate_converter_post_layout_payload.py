#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "sources" / "evidence" / "converter-post-layout-evidence-schema.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    return value is not None


def positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def missing_fields(schema: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for field in schema["required_top_level_fields"]:
        if field not in payload:
            issues.append(f"missing {field}")
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
    for parent, fields_key in nested.items():
        section = payload.get(parent) if isinstance(payload.get(parent), dict) else {}
        for field in schema[fields_key]:
            if field not in section:
                issues.append(f"missing {parent}.{field}")
    return issues


def validate_payload(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    issues = missing_fields(schema, payload)
    if payload.get("result_type") != "converter_post_layout_evidence":
        issues.append("result_type must be converter_post_layout_evidence")
    if payload.get("measurement_level") not in set(schema["allowed_measurement_levels"]):
        issues.append("measurement_level must be post_layout_simulation or measured_silicon")

    target = payload.get("target_boundary") if isinstance(payload.get("target_boundary"), dict) else {}
    if target.get("adc_bits") != 12:
        issues.append("target_boundary.adc_bits must be 12")
    if target.get("dac_bits") != 10:
        issues.append("target_boundary.dac_bits must be 10")
    if not number(target.get("output_noise_budget")) or target.get("output_noise_budget") > 0.004:
        issues.append("target_boundary.output_noise_budget must be numeric and at most 0.004")

    extraction = payload.get("extraction") if isinstance(payload.get("extraction"), dict) else {}
    if not present(extraction.get("extracted_netlist")):
        issues.append("extraction.extracted_netlist must name an extracted netlist")
    if not present(extraction.get("parasitic_format")):
        issues.append("extraction.parasitic_format must be present")
    for field in ["includes_row_dac", "includes_sar_readout", "includes_shared_mux", "includes_references", "includes_sample_path"]:
        if extraction.get(field) is not True:
            issues.append(f"extraction.{field} must be true")

    simulation = payload.get("simulation") if isinstance(payload.get("simulation"), dict) else {}
    for field in ["simulator", "command", "process_corner"]:
        if not present(simulation.get(field)):
            issues.append(f"simulation.{field} must be present")
    if not positive_number(simulation.get("voltage_v")):
        issues.append("simulation.voltage_v must be positive")
    if not number(simulation.get("temperature_c")):
        issues.append("simulation.temperature_c must be numeric")
    if not present(simulation.get("model_files")):
        issues.append("simulation.model_files must list model files")

    energy = payload.get("energy") if isinstance(payload.get("energy"), dict) else {}
    for field in ["adc_energy_per_conversion", "dac_energy_per_row_drive"]:
        if not positive_number(energy.get(field)):
            issues.append(f"energy.{field} must be positive")
    if str(energy.get("energy_unit", "")).lower() not in {"j", "joule", "joules"}:
        issues.append("energy.energy_unit must be joule/J")

    latency = payload.get("latency") if isinstance(payload.get("latency"), dict) else {}
    if latency.get("adc_comparisons") != 12:
        issues.append("latency.adc_comparisons must be 12")
    for field in ["conversion_time_ns", "settling_time_ns"]:
        if not positive_number(latency.get(field)):
            issues.append(f"latency.{field} must be positive")

    noise = payload.get("noise") if isinstance(payload.get("noise"), dict) else {}
    if not number(noise.get("output_noise_rms")):
        issues.append("noise.output_noise_rms must be numeric")
    elif number(target.get("output_noise_budget")) and noise["output_noise_rms"] > target["output_noise_budget"]:
        issues.append("noise.output_noise_rms must be within the output-noise budget")
    if not number(noise.get("input_referred_noise")):
        issues.append("noise.input_referred_noise must be numeric")
    if noise.get("meets_output_noise_budget") is not True:
        issues.append("noise.meets_output_noise_budget must be true")

    area = payload.get("area") if isinstance(payload.get("area"), dict) else {}
    for field in ["adc_area_um2", "dac_area_um2"]:
        if not positive_number(area.get(field)):
            issues.append(f"area.{field} must be positive")

    sharing = payload.get("sharing") if isinstance(payload.get("sharing"), dict) else {}
    expected_sharing = {
        "rows_served": 64,
        "columns_served": 4,
        "outputs_per_conversion_cost": 16,
        "converter_instances": 4,
    }
    for field, expected in expected_sharing.items():
        if sharing.get(field) != expected:
            issues.append(f"sharing.{field} must be {expected}")

    rerun = payload.get("break_even_rerun") if isinstance(payload.get("break_even_rerun"), dict) else {}
    if not present(rerun.get("rerun_artifact")):
        issues.append("break_even_rerun.rerun_artifact must be present")
    for field in ["uses_extracted_energy", "uses_extracted_latency", "uses_extracted_noise", "uses_extracted_area", "uses_same_sharing_rule"]:
        if rerun.get(field) is not True:
            issues.append(f"break_even_rerun.{field} must be true")
    if rerun.get("replacement_decision") in {None, "", "not_ready"}:
        issues.append("break_even_rerun.replacement_decision must make a replacement decision")
    return issues


def resolve_payload_path(payload_path: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    local_candidate = payload_path.parent / candidate
    if local_candidate.exists():
        return local_candidate
    return ROOT / candidate


def validate_referenced_files(payload: dict[str, Any], payload_path: Path) -> list[str]:
    issues: list[str] = []
    extraction = payload.get("extraction") if isinstance(payload.get("extraction"), dict) else {}
    simulation = payload.get("simulation") if isinstance(payload.get("simulation"), dict) else {}
    rerun = payload.get("break_even_rerun") if isinstance(payload.get("break_even_rerun"), dict) else {}

    netlist = resolve_payload_path(payload_path, extraction.get("extracted_netlist"))
    if netlist is None or not netlist.is_file():
        issues.append("extraction.extracted_netlist must point to an existing file")

    model_files = simulation.get("model_files") if isinstance(simulation.get("model_files"), list) else []
    if not model_files:
        issues.append("simulation.model_files must list existing files")
    for index, model_file in enumerate(model_files):
        path = resolve_payload_path(payload_path, model_file)
        if path is None or not path.is_file():
            issues.append(f"simulation.model_files[{index}] must point to an existing file")

    rerun_artifact = resolve_payload_path(payload_path, rerun.get("rerun_artifact"))
    if rerun_artifact is None or not rerun_artifact.is_file():
        issues.append("break_even_rerun.rerun_artifact must point to an existing file")
    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a converter post-layout or measured-silicon payload.")
    parser.add_argument("payload", type=Path)
    parser.add_argument("--expect-reject", action="store_true")
    parser.add_argument("--require-files", action="store_true", help="Require referenced netlist, model files, and rerun artifact to exist.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload_path = args.payload.resolve()
    if not payload_path.exists():
        raise SystemExit(f"payload not found: {payload_path}")
    schema = load_json(SCHEMA)
    payload = load_json(payload_path)
    issues = validate_payload(payload, schema)
    if args.require_files:
        issues.extend(validate_referenced_files(payload, payload_path))
    if args.expect_reject:
        if not issues:
            print("FAIL converter_post_layout_payload_validator: payload accepted under --expect-reject", file=sys.stderr)
            return 1
        print("PASS converter_post_layout_payload_rejected")
        print(f"payload,{payload_path}")
        print(f"issues,{len(issues)}")
        print(f"first_issue,{issues[0]}")
        return 0
    if issues:
        print("FAIL converter_post_layout_payload_validator", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print("PASS converter_post_layout_payload_validator")
    print(f"payload,{payload_path}")
    print("claim_ready_to_replace_break_even,True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
