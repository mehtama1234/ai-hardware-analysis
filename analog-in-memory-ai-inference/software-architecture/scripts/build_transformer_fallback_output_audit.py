#!/usr/bin/env python3
"""Join transformer fallback scheduling with retained exact-output evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("runtime_trace", type=Path)
    parser.add_argument("qualification_report", type=Path)
    parser.add_argument("all_code_trace", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runtime = json.loads(args.runtime_trace.read_text(encoding="utf-8"))
    qualification = json.loads(args.qualification_report.read_text(encoding="utf-8"))
    all_code = json.loads(args.all_code_trace.read_text(encoding="utf-8"))
    output_replay = qualification["output_replay"]
    exact_rows = output_replay["digital_fallback_contexts"]
    events = runtime["events"]
    output = {
        "schema_version": "gpt2-transformer-fallback-output-audit-v0.1",
        "result_type": "local_transformer_fallback_output_preservation_audit",
        "sources": {"runtime_trace": {"path": str(args.runtime_trace), "sha256": digest(args.runtime_trace)},
                    "qualification_report": {"path": str(args.qualification_report), "sha256": digest(args.qualification_report)},
                    "all_code_trace": {"path": str(args.all_code_trace), "sha256": digest(args.all_code_trace)},
                    "builder": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}},
        "scheduled_vectors": len(events), "scheduled_vector_ids_contiguous": [event["vector_id"] for event in events] == list(range(len(events))),
        "scheduled_routes_all_fallback": all(event["all_module_routes_fallback"] and event["command"] == "RUN_DIGITAL_FALLBACK" for event in events),
        "all_code_contract_bound": all_code["all_routes_fallback"] and all_code["all_unsupported_codes_explicit"],
        "exact_fallback_context_count": len(exact_rows),
        "exact_fallback_contexts": exact_rows,
        "exact_logits_and_generation_checked": output_replay["fallback_all_contexts_exact"],
        "per_vector_tensor_parity_retained": False,
        "decision": "digital_reference_authoritative_per_vector_parity_receipt_still_open",
        "analog_authorized": False,
        "claim_boundary": "Local fallback audit joins 162 scheduled vectors with four exact held-out context replays; per-vector tensor parity is not retained, and no physical analog execution, measured latency, or energy claim is made.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "transformer_fallback_output_audit.json"
    report_path.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        {"path": str(args.runtime_trace), "sha256": digest(args.runtime_trace)},
        {"path": str(args.qualification_report), "sha256": digest(args.qualification_report)},
        {"path": str(args.all_code_trace), "sha256": digest(args.all_code_trace)},
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "scheduled_vectors": len(events),
                      "exact_contexts": len(exact_rows), "per_vector_tensor_parity_retained": False}, sort_keys=True))


if __name__ == "__main__":
    main()
