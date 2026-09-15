#!/usr/bin/env python3
"""Build a conservative, provenance-linked SAR error/timing profile.

This profile is an integration handoff for model simulation. It is deliberately
not an analog authorization: only corners whose complete five-conversion maps
pass may contribute to the supported set, and failed/open corners remain
visible in the output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_case(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = ("status", "all_conversions_correct", "conversion_coverage_complete",
                "conversions", "reference_profile_v", "transient_step_ps")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"{path}: missing {', '.join(missing)}")
    if not data["conversion_coverage_complete"] or not data["conversions"]:
        raise ValueError(f"{path}: incomplete conversion coverage")
    return data


def summarize(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    rows = data["conversions"]
    errors = []
    margins = []
    for row in rows:
        errors.extend(abs(float(value)) for value in row.get("settling_error_v", []))
        margins.extend(abs(float(value)) for value in row.get("comparator_difference_v", []))
    return {
        "artifact": str(path),
        "sha256": digest(path),
        "status": data["status"],
        "all_conversions_correct": bool(data["all_conversions_correct"]),
        "conversion_count": len(rows),
        "reference_profile_v": data["reference_profile_v"],
        "max_abs_settling_error_v": max(errors) if errors else None,
        "min_abs_comparator_decision_margin_v": min(margins) if margins else None,
        "transient_step_ps": data["transient_step_ps"],
        "conversion_period_ns": 80.0,
    }


def build(inputs: list[Path], output: Path) -> dict[str, Any]:
    if not inputs:
        raise ValueError("at least one circuit artifact is required")
    cases = [load_case(path) for path in inputs]
    summaries = [summarize(path, data) for path, data in zip(inputs, cases)]
    passing = [item for item in summaries if item["all_conversions_correct"]]
    if not passing:
        raise ValueError("no complete passing circuit case is available")
    settling = [item["max_abs_settling_error_v"] for item in passing if item["max_abs_settling_error_v"] is not None]
    margins = [item["min_abs_comparator_decision_margin_v"] for item in passing if item["min_abs_comparator_decision_margin_v"] is not None]
    profile = {
        "schema_version": "circuit-derived-sar-profile-v0.1",
        "result_type": "candidate_circuit_derived_error_timing_profile",
        "candidate": "continuous_sky130_sar_nominal_topology",
        "supported_cases": [item["artifact"] for item in passing],
        "open_cases": [item["artifact"] for item in summaries if not item["all_conversions_correct"]],
        "error_model": {
            "max_abs_settling_error_v": max(settling) if settling else None,
            "min_abs_comparator_decision_margin_v": min(margins) if margins else None,
            "aggregation": "maximum across complete passing cases; no extrapolation to open corners",
        },
        "timing_model": {
            "conversion_period_ns": 80.0,
            "cycles_per_conversion": 4,
            "source_transient_step_ps": sorted({item["transient_step_ps"] for item in summaries}),
        },
        "qualification": {
            "physical_profile_calibrated": False,
            "analog_authorized": False,
            "claim_boundary": "Schematic Sky130 transient-derived integration profile from complete passing representative maps; excludes extracted-layout, foundry mismatch yield, noise, energy, and hardware runtime.",
            "next_gate": "Close FF/FS and fixed-seed mismatch, then validate this profile on held-out circuit cases before model use.",
        },
        "cases": summaries,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    return profile


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("artifacts", type=Path, nargs="+")
    args = parser.parse_args()
    result = build(args.artifacts, args.output)
    print(json.dumps({"output": str(args.output), "supported_cases": len(result["supported_cases"]), "open_cases": len(result["open_cases"])}, sort_keys=True))
