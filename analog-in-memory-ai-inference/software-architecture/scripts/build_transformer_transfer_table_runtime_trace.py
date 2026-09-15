#!/usr/bin/env python3
"""Bind all-code converter fallback invariants to the 162-vector transformer trace."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workload_trace", type=Path)
    parser.add_argument("transfer_policy", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    workload = json.loads(args.workload_trace.read_text(encoding="utf-8"))
    policy = json.loads(args.transfer_policy.read_text(encoding="utf-8"))
    unsupported = policy["unsupported_codes"]
    events = []
    for event in workload["events"]:
        events.append({
            "vector_id": event["vector_id"],
            "converter_code_contract": "all_codes_0_through_15",
            "unsupported_codes": unsupported,
            "modules": event["modules"],
            "compiled_command": event["command"],
            "actual_route": "digital_fallback" if event["all_module_routes_fallback"] else "rejected",
            "analog_authorized": False,
            "output_preservation": "digital_control_required_for_joint_quality_failure",
        })
    output = {
        "schema_version": "gpt2-transformer-transfer-table-runtime-trace-v0.1",
        "result_type": "local_transformer_all_code_converter_fallback_trace",
        "sources": {"workload_trace": {"path": str(args.workload_trace), "sha256": digest(args.workload_trace)},
                    "transfer_policy": {"path": str(args.transfer_policy), "sha256": digest(args.transfer_policy)},
                    "builder": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}},
        "workload_vectors": workload["workload_vectors"], "target_modules": workload["target_modules"],
        "events": events, "all_routes_fallback": all(event["actual_route"] == "digital_fallback" for event in events),
        "all_unsupported_codes_explicit": all(event["unsupported_codes"] == unsupported for event in events),
        "analog_instruction_count": 0,
        "output_preservation_contract": "digital fallback must preserve the native model output exactly",
        "claim_boundary": "Local transformer compiler/runtime contract join only; this does not claim physical analog execution, measured latency, energy, or silicon behavior.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "transformer_transfer_table_runtime_trace.json"
    report_path.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        {"path": str(args.workload_trace), "sha256": digest(args.workload_trace)},
        {"path": str(args.transfer_policy), "sha256": digest(args.transfer_policy)},
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "events": len(events),
                      "all_routes_fallback": output["all_routes_fallback"]}, sort_keys=True))


if __name__ == "__main__":
    main()
