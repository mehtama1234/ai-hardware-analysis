#!/usr/bin/env python3
"""Verify dispatch simulation invariants before workload execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("simulation", type=Path)
    args = parser.parse_args()
    data = json.loads(args.simulation.read_text())
    failures = []
    vectors = data.get("workload_vectors", 0)
    rows = data.get("scenarios", [])
    if not isinstance(vectors, int) or vectors <= 0:
        failures.append("workload_vectors must be positive")
    if len(rows) != 4:
        failures.append("exactly four routing scenarios are required")
    for row in rows:
        if row.get("vectors") != vectors:
            failures.append(f"{row.get('scenario')}: vector count mismatch")
        if row.get("analog_vectors") != 0:
            failures.append(f"{row.get('scenario')}: analog vectors must remain zero")
        if row.get("fallback_vectors", 0) + row.get("digital_correction_candidate_vectors", 0) != vectors:
            failures.append(f"{row.get('scenario')}: routing does not conserve vectors")
    by_name = {row.get("scenario"): row for row in rows}
    for scenario in ("ff", "fs", "unknown"):
        if by_name.get(scenario, {}).get("fallback_vectors") != vectors:
            failures.append(f"{scenario}: must fail closed to fallback")
    if by_name.get("mismatch_calibrated", {}).get("digital_correction_candidate_vectors") != vectors:
        failures.append("mismatch_calibrated: expected bounded digital correction candidate")
    result = {"status": "passed" if not failures else "failed",
              "checks": ["scenario_count", "vector_conservation", "zero_analog", "fail_closed_routes"],
              "failures": failures,
              "claim_boundary": data.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
