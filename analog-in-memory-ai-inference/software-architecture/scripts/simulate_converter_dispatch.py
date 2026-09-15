#!/usr/bin/env python3
"""Simulate guarded converter routing over a derived workload trace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SCENARIOS = {
    "ff": "digital_fallback",
    "fs": "digital_fallback",
    "mismatch_calibrated": "digital_code_correction_candidate",
    "unknown": "digital_fallback",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--dispatch-policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    trace = json.loads(args.trace.read_text())
    policy = json.loads(args.dispatch_policy.read_text())
    vectors = int(trace["totals"]["vectors"])
    if vectors <= 0:
        raise SystemExit("trace must contain positive vector count")
    routes = {row["route"] for row in policy.get("routes", [])}
    rows = []
    for scenario, route in SCENARIOS.items():
        if route not in routes:
            raise SystemExit(f"dispatch policy does not define route {route}")
        candidate = vectors if route == "digital_code_correction_candidate" else 0
        fallback = vectors - candidate
        rows.append({"scenario": scenario, "route": route, "vectors": vectors,
                     "digital_correction_candidate_vectors": candidate,
                     "fallback_vectors": fallback,
                     "analog_vectors": 0,
                     "promotion": "candidate_only" if candidate else "fallback_required"})
    result = {
        "schema_version": "converter-dispatch-simulation-v0.1",
        "result_type": "guarded_workload_dispatch_simulation",
        "sources": {"trace": str(args.trace), "dispatch_policy": str(args.dispatch_policy)},
        "workload_vectors": vectors,
        "scenarios": rows,
        "invariants": {"analog_vectors_always_zero": True,
                       "fallback_for_unknown": True,
                       "fallback_for_fs_collision": True,
                       "mismatch_candidate_is_digital_correction_only": True},
        "decision": "runtime_policy_is_ready_for_colab_workload_replay",
        "claim_boundary": "This is a deterministic software routing simulation over a derived numerical trace. It does not measure analog hardware execution, latency, energy, yield, or speedup.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "vectors": vectors,
                      "scenarios": len(rows), "analog_vectors": 0}))


if __name__ == "__main__":
    main()
