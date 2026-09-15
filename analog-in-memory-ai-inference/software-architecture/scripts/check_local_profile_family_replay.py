#!/usr/bin/env python3
"""Independent fail-closed verifier for local profile-family replay."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED = {
    "nominal_counterfactual",
    "calibrated_counterfactual",
    "pessimistic_error_counterfactual",
    "unsupported_range_counterfactual",
    "timeout_counterfactual",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    family_path = args.package / "profile-family.json"
    replay_path = args.package / "profile-family-replay.jsonl"
    manifest_path = args.package / "manifest.json"
    failures = []
    if not all(path.is_file() for path in (family_path, replay_path, manifest_path)):
        raise SystemExit("PROFILE FAMILY FAILED: required artifact missing")
    family = json.loads(family_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    profiles = family.get("profiles", [])
    ids = {profile.get("id") for profile in profiles}
    vectors = int(family.get("workload_vectors", 0))
    if ids != EXPECTED or len(profiles) != len(EXPECTED):
        failures.append("profile family is incomplete")
    if manifest.get("family", {}).get("sha256") != digest(family_path):
        failures.append("family hash mismatch")
    if manifest.get("replay", {}).get("sha256") != digest(replay_path):
        failures.append("replay hash mismatch")
    rows = [json.loads(line) for line in replay_path.read_text().splitlines() if line]
    if len(rows) != len(EXPECTED) * vectors:
        failures.append("replay record count mismatch")
    by_profile = {profile_id: [] for profile_id in EXPECTED}
    for row in rows:
        if row.get("profile_id") not in by_profile:
            failures.append("unknown profile in replay")
            continue
        by_profile[row["profile_id"]].append(row)
        if row.get("route") != "digital_fallback":
            failures.append("unauthorized non-fallback route")
        if row.get("eligible_for_analog_candidate") is not False:
            failures.append("analog eligibility was promoted")
        if row.get("analog_authorized") is not False:
            failures.append("analog authorization was promoted")
        if row.get("output_preservation") != "digital_reference_exact_by_guarded_fallback":
            failures.append("output preservation boundary missing")
        if not row.get("rejection_reasons"):
            failures.append("fallback reason missing")
    for profile_id, profile_rows in by_profile.items():
        if len(profile_rows) != vectors:
            failures.append(f"profile vector count mismatch: {profile_id}")
        if [row.get("vector_id") for row in profile_rows] != list(range(vectors)):
            failures.append(f"vector ordering mismatch: {profile_id}")
    profile_map = {profile["id"]: profile for profile in profiles}
    for profile_id in ("unsupported_range_counterfactual", "timeout_counterfactual"):
        reasons = {reason for row in by_profile[profile_id] for reason in row["rejection_reasons"]}
        if "open_converter_profile_cases" not in reasons:
            failures.append(f"{profile_id} lacks unsupported-profile reason")
    for profile_id in ("nominal_counterfactual", "calibrated_counterfactual"):
        reasons = {reason for row in by_profile[profile_id] for reason in row["rejection_reasons"]}
        if "timing_profile_not_measured_for_this_vector" not in reasons:
            failures.append(f"{profile_id} lacks timing reason")
    if manifest.get("decision") != "digital_reference_and_deterministic_fallback_only":
        failures.append("unsafe family decision")
    if manifest.get("analog_authorized") is not False:
        failures.append("manifest authorizes analog execution")
    result = {"status": "passed" if not failures else "failed", "profiles": len(EXPECTED),
              "vectors_per_profile": vectors, "failures": failures,
              "claim_boundary": family.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
