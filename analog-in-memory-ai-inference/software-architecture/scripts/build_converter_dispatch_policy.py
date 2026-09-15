#!/usr/bin/env python3
"""Build a guarded runtime dispatch policy from converter qualification receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--global-remap", type=Path, required=True)
    parser.add_argument("--mismatch-remap", type=Path, required=True)
    parser.add_argument("--workload-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    profile: dict[str, Any] = json.loads(args.profile.read_text())
    global_remap: dict[str, Any] = json.loads(args.global_remap.read_text())
    mismatch: dict[str, Any] = json.loads(args.mismatch_remap.read_text())
    workload: dict[str, Any] = json.loads(args.workload_contract.read_text())
    sources = [args.profile, args.global_remap, args.mismatch_remap, args.workload_contract]
    routes = [
        {"case": "nominal_ss_sf_ff_supported_profile", "route": "digital_fallback",
         "reason": "profile metadata is schematic and analog placement is unauthorized"},
        {"case": "fs_corner", "route": "digital_fallback",
         "reason": "global remap rejected: observed code collision"},
        {"case": "fixed_seed_mismatch_campaign", "route": "digital_code_correction_candidate",
         "reason": "per-converter remap passed 4/4 same-campaign holdouts; analog path remains unqualified"},
        {"case": "unknown_or_uncharacterized", "route": "digital_fallback",
         "reason": "fail closed on missing calibration or out-of-domain code"},
    ]
    result = {
        "schema_version": "converter-dispatch-policy-v0.1",
        "result_type": "guarded_converter_runtime_dispatch_policy",
        "sources": [{"path": str(path), "sha256": sha256(path)} for path in sources],
        "workload_binding": {"model": workload.get("model_binding"),
                             "per_vector_schedule": workload.get("per_vector_schedule")},
        "qualification_summary": {
            "supported_profile_cases": len(profile.get("supported_cases", [])),
            "open_profile_cases": len(profile.get("open_cases", [])),
            "global_remap_usable_cases": global_remap.get("calibration_policy", {}).get("usable_case_count", 0),
            "per_converter_mismatch_holdouts": mismatch.get("passed_holdouts", 0),
            "per_converter_mismatch_holdout_total": mismatch.get("total_holdouts", 0),
        },
        "routes": routes,
        "fail_closed_invariants": ["analog_placement_allowed must remain false",
                                    "unknown code causes digital fallback",
                                    "code collision causes digital fallback",
                                    "calibration must be per converter/tile and held out before workload use"],
        "decision": "digital_runtime_authoritative_with_guarded_calibration_candidate",
        "claim_boundary": "This dispatch policy controls software routing from schematic qualification receipts. It does not authorize analog placement or claim circuit yield, hardware acceleration, latency, or energy benefit.",
    }
    if workload.get("converter_qualification_binding", {}).get("analog_placement_allowed") is not False:
        raise SystemExit("workload contract must keep analog placement disabled")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "routes": len(routes),
                      "analog_placement_allowed": False,
                      "mismatch_candidate_holdouts": mismatch.get("passed_holdouts", 0)}))


if __name__ == "__main__":
    main()
