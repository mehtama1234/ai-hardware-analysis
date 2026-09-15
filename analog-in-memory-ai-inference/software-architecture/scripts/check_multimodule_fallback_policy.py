#!/usr/bin/env python3
"""Verify the fail-closed multi-module fallback policy."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    policy_path = args.package / "fallback_policy.json"
    manifest_path = args.package / "manifest.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if policy.get("candidate_policy", {}).get("screen_pass") is not False:
        failures.append("rejected mixed candidate is not recorded as failed")
    enforced = policy.get("enforced_policy", {})
    if enforced.get("route") != "digital_fallback" or enforced.get("analog_authorized") is not False:
        failures.append("enforced route is not fail-closed digital fallback")
    routes = enforced.get("module_routes", {})
    if not routes or any(route != "digital_fallback" for route in routes.values()):
        failures.append("not every module is governed to digital fallback")
    if policy.get("decision") != "reject_partial_analog_policy_and_use_full_digital_fallback":
        failures.append("unexpected fallback policy decision")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "claim_boundary": policy.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
