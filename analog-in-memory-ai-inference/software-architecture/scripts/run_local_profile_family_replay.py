#!/usr/bin/env python3
"""Replay a bounded transformer workload against a local profile family.

The profiles are explicitly counterfactual software scenarios. They are not
new SPICE, CUDA, board, or silicon evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from threshold_governor import decide_vector


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path,
        default=Path("experiments/gpt2-hybrid-v1/qualification/local-profile-family-replay"),
    )
    args = parser.parse_args()
    report = load(args.package / "qualification_report.json")
    governor_path = args.package / "threshold_governor_trace.jsonl"
    governor_rows = [json.loads(line) for line in governor_path.read_text().splitlines() if line]
    if not governor_rows:
        raise SystemExit("profile family replay requires a non-empty governor trace")
    vectors = int(report["workload"]["vectors"])
    if len(governor_rows) != vectors:
        raise SystemExit("governor trace does not match workload vector count")

    profiles = [
        {
            "id": "nominal_counterfactual",
            "profile_status": "supported_counterfactual",
            "profile_supported": True,
            "timing_evidence_passed": False,
            "analog_authorized": False,
            "failure_mode": None,
        },
        {
            "id": "calibrated_counterfactual",
            "profile_status": "supported_counterfactual_calibrated",
            "profile_supported": True,
            "timing_evidence_passed": False,
            "analog_authorized": False,
            "failure_mode": None,
        },
        {
            "id": "pessimistic_error_counterfactual",
            "profile_status": "quality_budget_stressed_counterfactual",
            "profile_supported": True,
            "timing_evidence_passed": False,
            "analog_authorized": False,
            "failure_mode": "quality_budget_stressed",
        },
        {
            "id": "unsupported_range_counterfactual",
            "profile_status": "unsupported_range_counterfactual",
            "profile_supported": False,
            "timing_evidence_passed": False,
            "analog_authorized": False,
            "failure_mode": "unsupported_operating_region",
        },
        {
            "id": "timeout_counterfactual",
            "profile_status": "timeout_counterfactual",
            "profile_supported": False,
            "timing_evidence_passed": False,
            "analog_authorized": False,
            "failure_mode": "settling_timeout",
        },
    ]
    args.output.mkdir(parents=True, exist_ok=True)
    family_path = args.output / "profile-family.json"
    family = {
        "schema_version": "local-transformer-profile-family-v0.1",
        "result_type": "counterfactual_profile_family",
        "workload_vectors": vectors,
        "profiles": profiles,
        "source_package": {"path": str(args.package), "report_sha256": digest(args.package / "qualification_report.json"),
                            "governor_sha256": digest(governor_path)},
        "claim_boundary": "Local profile-policy replay only; profiles are counterfactual and do not represent physical measurements.",
    }
    family_path.write_text(json.dumps(family, indent=2) + "\n")

    replay_path = args.output / "profile-family-replay.jsonl"
    with replay_path.open("w", encoding="utf-8") as stream:
        for profile in profiles:
            for source in governor_rows:
                quality = source.get("quality_gate", {})
                decision = decide_vector(
                    relative_l2_error=quality.get("relative_l2_error"),
                    relative_l2_limit=float(quality.get("limit", 0.01)),
                    clipping_passed=source.get("clipping_gate", {}).get("passed") is True,
                    profile_supported=profile["profile_supported"],
                    timing_evidence_passed=profile["timing_evidence_passed"],
                    analog_authorized=profile["analog_authorized"],
                )
                row = {
                    "profile_id": profile["id"],
                    "vector_id": source["vector_id"],
                    "route": decision["enforced_route"],
                    "eligible_for_analog_candidate": decision["eligible_for_analog_candidate"],
                    "rejection_reasons": decision["rejection_reasons"],
                    "failure_mode": profile["failure_mode"],
                    "output_preservation": "digital_reference_exact_by_guarded_fallback",
                    "analog_authorized": False,
                }
                stream.write(json.dumps(row, sort_keys=True) + "\n")

    manifest = {
        "schema_version": "local-profile-family-replay-manifest-v0.1",
        "family": {"path": str(family_path), "sha256": digest(family_path)},
        "replay": {"path": str(replay_path), "sha256": digest(replay_path)},
        "profile_count": len(profiles),
        "vectors_per_profile": vectors,
        "record_count": len(profiles) * vectors,
        "decision": "digital_reference_and_deterministic_fallback_only",
        "analog_authorized": False,
        "claim_boundary": family["claim_boundary"],
    }
    manifest_path = args.output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": "passed", "profiles": len(profiles), "vectors_per_profile": vectors,
                      "output": str(args.output)}))


if __name__ == "__main__":
    main()
