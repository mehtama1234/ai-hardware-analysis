#!/usr/bin/env python3
"""Derive a guarded digital code-remap contract from measured SAR receipts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("conversions", [])
    if not rows:
        raise ValueError(f"{path}: no measured conversions")
    return data


def derive(path: Path) -> dict[str, Any]:
    data = read(path)
    pairs = [(int(row["expected_code"]), int(row["final_code"])) for row in data["conversions"]]
    observed = [actual for _, actual in pairs]
    expected = [target for target, _ in pairs]
    unique_observed = len(set(observed)) == len(observed)
    monotonic = all(a <= b for a, b in zip(observed, observed[1:]))
    remap = {str(actual): target for target, actual in pairs} if unique_observed else None
    return {
        "source_artifact": str(path),
        "source_sha256": digest(path),
        "status": data.get("status"),
        "expected_codes": expected,
        "observed_codes": observed,
        "observed_code_unique": unique_observed,
        "observed_code_monotonic": monotonic,
        "one_to_one_remap": remap,
        "remap_possible_for_observed_set": unique_observed and set(observed) >= set(expected),
    }


def build(paths: list[Path], output: Path) -> dict[str, Any]:
    cases = [derive(path) for path in paths]
    usable = [case for case in cases if case["one_to_one_remap"] is not None and case["remap_possible_for_observed_set"]]
    result = {
        "schema_version": "sar-code-remap-contract-v0.1",
        "result_type": "guarded_sar_code_remap_contract",
        "cases": cases,
        "calibration_policy": {
            "required": True,
            "per_tile_or_per_converter": True,
            "fit_split": "calibration conversions only",
            "validation_split": "held-out conversions before workload use",
            "usable_case_count": len(usable),
        },
        "authorization": {
            "analog_placement_allowed": False,
            "hardware_claim_allowed": False,
            "reason": "a digital remap can correct labels only when observed codes are one-to-one and cover the target set; this does not repair analog error or establish yield",
        },
        "next_gate": "Run the proposed remap on held-out references and then on the fixed-seed mismatch population; reject any collision, non-monotonic map, or out-of-set code.",
        "claim_boundary": "Digital calibration contract derived from measured schematic SAR maps; no claim of physical yield, noise tolerance, layout qualification, or hardware acceleration.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("artifacts", type=Path, nargs="+")
    args = parser.parse_args()
    result = build(args.artifacts, args.output)
    print(json.dumps({"cases": len(result["cases"]), "usable_cases": result["calibration_policy"]["usable_case_count"], "analog_placement_allowed": result["authorization"]["analog_placement_allowed"]}, sort_keys=True))
