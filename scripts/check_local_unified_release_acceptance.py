#!/usr/bin/env python3
"""Verify the hash-bound local unified release acceptance decision."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_STEPS = {"public_reference_acceptance", "customer_pilot_certification", "model_to_chip_acceptance", "profile_family_acceptance", "final_gate_report", "final_handoff_validation"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path: Path, root: Path) -> list[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read acceptance decision: {exc}"]
    errors: list[str] = []
    stored = payload.get("decision_sha256")
    body = {key: value for key, value in payload.items() if key != "decision_sha256"}
    actual = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if not isinstance(stored, str) or actual != stored:
        errors.append("decision digest is invalid")
    if payload.get("schema_version") != "local-unified-release-acceptance-v1":
        errors.append("unexpected schema version")
    if payload.get("decision") != "local_unified_reference_and_model_to_chip_package_ready_for_signoff":
        errors.append("decision is not local unified release ready")
    if payload.get("hardware_required") is not False:
        errors.append("hardware_required must remain false")
    steps = payload.get("steps") if isinstance(payload.get("steps"), list) else []
    step_map = {step.get("label"): step for step in steps if isinstance(step, dict)}
    if set(step_map) != REQUIRED_STEPS:
        errors.append("acceptance step set is incomplete")
    if any(step.get("returncode") != 0 for step in step_map.values()):
        errors.append("one or more acceptance steps failed")
    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
    if not artifacts:
        errors.append("bound artifact map is missing")
    for name, record in artifacts.items():
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            errors.append(f"invalid artifact record: {name}")
            continue
        relative = Path(record["path"])
        candidate = (root / relative).resolve()
        if relative.is_absolute() or root.resolve() not in candidate.parents:
            errors.append(f"unsafe artifact path: {record['path']}")
        elif not candidate.is_file():
            errors.append(f"missing artifact: {record['path']}")
        elif not isinstance(record.get("sha256"), str) or sha256(candidate) != record["sha256"]:
            errors.append(f"artifact digest mismatch: {record['path']}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decision", type=Path, nargs="?", default=ROOT / ".artifacts/local-unified-release-acceptance.json")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = verify(args.decision, args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"verified local unified release acceptance: {args.decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
