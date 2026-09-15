#!/usr/bin/env python3
"""Check the guarded GPT-2/SAR workload contract and its source provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())
    failures = []
    for name, source in contract.get("sources", {}).items():
        path = Path(source["path"])
        if not path.is_absolute() and not path.exists():
            candidates = [REPO_ROOT / path, REPO_ROOT / "analog-in-memory-ai-inference" / path]
            path = next((candidate for candidate in candidates if candidate.exists()), candidates[0])
        if not path.exists():
            failures.append(f"{name}: missing {path}")
        elif digest(path) != source["sha256"]:
            failures.append(f"{name}: sha256 mismatch")
    schedule = contract.get("per_vector_schedule", {})
    for key in ("macs", "dac_conversions_without_column_tile_broadcast",
                "adc_conversions_after_differential_subtraction", "array_evaluations",
                "digital_partial_sum_additions"):
        if not isinstance(schedule.get(key), int) or schedule[key] <= 0:
            failures.append(f"schedule.{key}: positive integer required")
    binding = contract.get("converter_qualification_binding", {})
    if binding.get("analog_placement_allowed") is not False:
        failures.append("analog placement must remain disabled")
    if contract.get("execution_policy", {}).get("authoritative_path") != "native_digital_fallback":
        failures.append("native digital fallback must remain authoritative")
    if not contract.get("next_experiment", {}).get("validation_split"):
        failures.append("held-out validation split is missing")
    result = {
        "status": "passed" if not failures else "failed",
        "checks": ["source_hashes", "schedule_counts", "placement_guard", "fallback_policy", "held_out_split"],
        "failures": failures,
        "claim_boundary": contract.get("claim_boundary"),
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
