#!/usr/bin/env python3
"""Import a circuit-derived SAR profile into a guarded workload package."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_profile(path: Path) -> dict[str, Any]:
    profile = json.loads(path.read_text(encoding="utf-8"))
    if profile.get("schema_version") != "circuit-derived-sar-profile-v0.1":
        raise ValueError("unsupported circuit profile schema")
    if not profile.get("supported_cases"):
        raise ValueError("profile has no passing supported cases")
    qualification = profile.get("qualification", {})
    return {
        "schema_version": "guarded-circuit-profile-import-v0.1",
        "result_type": "guarded_circuit_derived_sar_profile_import",
        "source_profile": str(path),
        "source_profile_sha256": sha256(path),
        "candidate": profile.get("candidate"),
        "supported_cases": profile.get("supported_cases", []),
        "open_cases": profile.get("open_cases", []),
        "error_model": profile.get("error_model", {}),
        "timing_model": profile.get("timing_model", {}),
        "authorization": {
            "physical_profile_calibrated": bool(qualification.get("physical_profile_calibrated", False)),
            "analog_authorized": False,
            "placement_allowed": False,
            "reason": "profile is schematic transient evidence and still has open qualification cases",
        },
        "next_gate": qualification.get("next_gate", "validate on held-out circuit cases"),
        "claim_boundary": qualification.get("claim_boundary"),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = import_profile(args.profile)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"supported_cases": len(result["supported_cases"]), "open_cases": len(result["open_cases"]), "placement_allowed": result["authorization"]["placement_allowed"]}, sort_keys=True))
