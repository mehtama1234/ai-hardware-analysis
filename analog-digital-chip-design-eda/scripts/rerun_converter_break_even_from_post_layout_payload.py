#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_converter_post_layout_payload import SCHEMA, load_json, validate_payload, validate_referenced_files


ROOT = Path(__file__).resolve().parents[1]
BASE_BREAK_EVEN = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-break-even.json"


def saved_array_energy_per_output(rows: int, analog_mac_energy_j: float, digital_mac_energy_j: float) -> float:
    return rows * max(0.0, digital_mac_energy_j - analog_mac_energy_j)


def scenario(
    name: str,
    rows: int,
    columns: int,
    converter_energy_j: float,
    analog_mac_energy_j: float,
    digital_mac_energy_j: float,
    amortized_outputs_per_conversion: int,
) -> dict[str, Any]:
    saving_per_output = saved_array_energy_per_output(rows, analog_mac_energy_j, digital_mac_energy_j)
    converter_per_output = converter_energy_j / float(amortized_outputs_per_conversion)
    analog_array_per_output = rows * analog_mac_energy_j
    target_total = converter_per_output + analog_array_per_output
    digital_total = rows * digital_mac_energy_j
    margin = digital_total - target_total
    required_outputs = None if saving_per_output <= 0 else converter_energy_j / saving_per_output
    return {
        "name": name,
        "rows": rows,
        "columns": columns,
        "analog_mac_energy_j": analog_mac_energy_j,
        "digital_mac_energy_j": digital_mac_energy_j,
        "amortized_outputs_per_conversion": amortized_outputs_per_conversion,
        "converter_energy_j": converter_energy_j,
        "converter_energy_per_output_j": converter_per_output,
        "analog_array_energy_per_output_j": analog_array_per_output,
        "digital_energy_per_output_j": digital_total,
        "target_analog_energy_per_output_j": target_total,
        "margin_vs_digital_per_output_j": margin,
        "target_beats_digital": margin > 0,
        "required_outputs_to_pay_converter": required_outputs,
    }


def build_rerun(payload: dict[str, Any], analog_mac_energy_j: float, digital_mac_energy_j: float) -> dict[str, Any]:
    energy = payload["energy"]
    sharing = payload["sharing"]
    latency = payload["latency"]
    noise = payload["noise"]
    area = payload["area"]
    rows = int(sharing["rows_served"])
    columns = int(sharing["columns_served"])
    outputs_per_conversion = int(sharing["outputs_per_conversion_cost"])
    converter_instances = int(sharing["converter_instances"])
    converter_energy_j = float(energy["adc_energy_per_conversion"]) + float(energy["dac_energy_per_row_drive"])
    scenarios = [
        scenario(
            "payload_sharing_rule",
            rows,
            columns,
            converter_energy_j,
            analog_mac_energy_j,
            digital_mac_energy_j,
            outputs_per_conversion,
        ),
        scenario(
            "no_sharing_same_rows",
            rows,
            columns,
            converter_energy_j,
            analog_mac_energy_j,
            digital_mac_energy_j,
            1,
        ),
    ]
    replacement_decision = "replace_converter_break_even_assumption" if scenarios[0]["target_beats_digital"] else "keep_digital_fallback"
    return {
        "result_type": "converter_post_layout_break_even_rerun",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_payload": payload.get("converter_id"),
        "measurement_level": payload.get("measurement_level"),
        "target_boundary": payload.get("target_boundary"),
        "input_terms": {
            "adc_energy_per_conversion_j": energy["adc_energy_per_conversion"],
            "dac_energy_per_row_drive_j": energy["dac_energy_per_row_drive"],
            "combined_converter_energy_j": converter_energy_j,
            "conversion_time_ns": latency["conversion_time_ns"],
            "settling_time_ns": latency["settling_time_ns"],
            "output_noise_rms": noise["output_noise_rms"],
            "adc_area_um2": area["adc_area_um2"],
            "dac_area_um2": area["dac_area_um2"],
            "rows_served": rows,
            "columns_served": columns,
            "converter_instances": converter_instances,
            "outputs_per_conversion_cost": outputs_per_conversion,
            "analog_mac_energy_j": analog_mac_energy_j,
            "digital_mac_energy_j": digital_mac_energy_j,
        },
        "scenarios": scenarios,
        "summary": {
            "passing_scenarios": sum(1 for item in scenarios if item["target_beats_digital"]),
            "default_scenario": "payload_sharing_rule",
            "replacement_decision": replacement_decision,
            "claim_ready_to_replace_break_even": True,
        },
        "claim_boundary": {
            "allowed": "uses a validator-passing post-layout or measured-silicon payload to rerun converter break-even for the same sharing rule",
            "not_allowed": "does not prove full chip performance, board energy, another workload, or production readiness",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rerun converter break-even from a validator-passing post-layout payload.")
    parser.add_argument("payload", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--analog-mac-energy-j", type=float, default=1.0e-15)
    parser.add_argument("--digital-mac-energy-j", type=float, default=1.0e-14)
    parser.add_argument("--expect-reject", action="store_true")
    parser.add_argument("--require-files", action="store_true", help="Require referenced extraction/model/rerun files to exist.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload_path = args.payload.resolve()
    payload = load_json(payload_path)
    schema = load_json(SCHEMA)
    issues = validate_payload(payload, schema)
    if args.require_files:
        issues.extend(validate_referenced_files(payload, payload_path))
    if payload.get("template_only") is True:
        issues.append("template payloads cannot be used for break-even rerun")
    if issues:
        if args.expect_reject:
            print("PASS converter_post_layout_break_even_rerun_rejected")
            print(f"payload,{payload_path}")
            print(f"issues,{len(issues)}")
            print(f"first_issue,{issues[0]}")
            return 0
        print("FAIL converter_post_layout_break_even_rerun", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    if args.expect_reject:
        print("FAIL converter_post_layout_break_even_rerun: payload accepted under --expect-reject", file=sys.stderr)
        return 1
    rerun = build_rerun(payload, args.analog_mac_energy_j, args.digital_mac_energy_j)
    output = args.output.resolve() if args.output else None
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(rerun, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS converter_post_layout_break_even_rerun")
    print(f"payload,{payload_path}")
    print(f"replacement_decision,{rerun['summary']['replacement_decision']}")
    print(f"claim_ready_to_replace_break_even,{rerun['summary']['claim_ready_to_replace_break_even']}")
    if output:
        print(f"json,{output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
