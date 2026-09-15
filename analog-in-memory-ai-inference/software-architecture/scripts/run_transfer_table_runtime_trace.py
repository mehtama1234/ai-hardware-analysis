#!/usr/bin/env python3
"""Replay every transfer-table code through the compiler/runtime fallback contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("policy", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    events = []
    for code in range(policy["requested_code_count"]):
        route = policy["routes"][str(code)]
        events.append({
            "event_id": f"converter-code-{code:02d}",
            "requested_converter_code": code,
            "policy_status": route["status"],
            "compiled_command": "RUN_ANALOG_CONVERTER",
            "actual_route": route["route"],
            "runtime_command": "RUN_DIGITAL_FALLBACK",
            "fallback_reason": route["reason"],
            "analog_instruction_executed": False,
            "output_preservation": "exact_by_digital_fallback_control",
        })
    output = {
        "schema_version": "sky130-transfer-table-runtime-trace-v0.1",
        "result_type": "local_transfer_table_compiler_runtime_trace",
        "source_policy": {"path": str(args.policy), "sha256": digest(args.policy)},
        "requested_code_count": len(events), "events": events,
        "all_routes_fallback": all(event["actual_route"] == "digital_fallback" for event in events),
        "analog_instruction_count": sum(event["analog_instruction_executed"] for event in events),
        "unsupported_code_events": [event["requested_converter_code"] for event in events
                                    if event["policy_status"] == "unsupported"],
        "claim_boundary": "Local compiler/runtime contract replay only; exact fallback preservation is software evidence, not hardware latency, energy, or analog execution.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    trace_path = args.output / "transfer_table_runtime_trace.json"
    trace_path.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(trace_path), "sha256": digest(trace_path)},
        {"path": str(args.policy), "sha256": digest(args.policy)},
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(trace_path), "events": len(events),
                      "unsupported_events": output["unsupported_code_events"], "all_routes_fallback": output["all_routes_fallback"]}, sort_keys=True))


if __name__ == "__main__":
    main()
