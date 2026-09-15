#!/usr/bin/env python3
"""Build a stateful-profile numerical candidate with fail-closed enforcement."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stateful_report", type=Path)
    parser.add_argument("cost_trace", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    stateful_path = args.stateful_report.resolve()
    cost_path = args.cost_trace.resolve()
    report = json.loads(stateful_path.read_text(encoding="utf-8"))
    modules = report["target_modules"]
    cost_rows = [json.loads(line) for line in cost_path.read_text(encoding="utf-8").splitlines() if line]
    candidate = report["results"]["stateful_previous_token_stress"]
    enforced = {"route": "digital_fallback", "module_routes": {name: "digital_fallback" for name in modules},
                "reason": "physical analog authorization gate remains closed", "analog_authorized": False}
    trace = [{"vector_id": row["vector_id"], "candidate_profile": "stateful_previous_token",
              "enforced_route": enforced["route"], "command": "RUN_DIGITAL_FALLBACK",
              "digital_reference_cost_pj": row["digital_reference_cost_pj"],
              "counterfactual_hybrid_cost_pj": row["counterfactual_hybrid_cost_pj"],
              "enforced_route_cost_pj": row["enforced_route_cost_pj"], "analog_authorized": False}
             for row in cost_rows]
    output = {"schema_version": "gpt2-stateful-profile-governor-v0.1",
              "result_type": "local_stateful_transfer_profile_governor",
              "source_stateful_report": {"path": str(stateful_path), "sha256": digest(stateful_path)},
              "source_cost_trace": {"path": str(cost_path), "sha256": digest(cost_path)},
              "target_modules": modules,
              "numerical_candidate": {"profile": candidate["profile"], "route": "full_three_module",
                                       "original_screen_pass": report["results"]["stateful_previous_token_original"]["quality"]["screen_pass"],
                                       "stress_screen_pass": candidate["quality"]["screen_pass"],
                                       "quality": candidate["quality"], "method": "previous provisional output row correction"},
              "enforced_policy": enforced, "route_trace": trace,
              "decision": "stateful_profile_numerically_qualified_but_digital_fallback_enforced",
              "analog_authorized": False,
              "claim_boundary": "Local CPU stateful numerical profile only; no measured hardware latency, energy, silicon yield, or analog authorization."}
    args.output.mkdir(parents=True, exist_ok=False)
    output_path = args.output / "stateful_profile_governor.json"
    output_path.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    trace_path = args.output / "stateful_route_cost_trace.jsonl"
    trace_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in trace), encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(output_path), "sha256": digest(output_path)},
        {"path": str(trace_path), "sha256": digest(trace_path)},
        {"path": str(stateful_path), "sha256": digest(stateful_path)},
        {"path": str(cost_path), "sha256": digest(cost_path)},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output_path), "trace_rows": len(trace), "analog_authorized": False}, sort_keys=True))


if __name__ == "__main__":
    main()
