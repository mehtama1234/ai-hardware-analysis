#!/usr/bin/env python3
"""Independently verify the flagship end-to-end qualification receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "local_unified_acceptance",
    "aggregate_milestone_receipt",
    "aggregate_milestone_report",
    "four_causal_agent_receipt",
    "four_causal_agent_package",
    "rtl2gds_bridge",
    "model_to_chip_manifest",
    "real_model_summary",
    "real_model_benchmark",
    "real_model_heldout",
    "real_model_pipeline",
    "real_model_choice_summary",
    "real_model_choice_benchmark",
    "real_model_choice_heldout",
    "real_model_choice_pipeline",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    errors = []
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "errors": [str(exc)]}, sort_keys=True))
        return 1
    body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    if manifest.get("schema_version") != "flagship-end-to-end-release-v1":
        errors.append("unsupported schema")
    if manifest.get("manifest_sha256") != hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest():
        errors.append("manifest digest mismatch")
    records = manifest.get("evidence", [])
    names = {item.get("name") for item in records if isinstance(item, dict)}
    if names != REQUIRED or len(records) != len(REQUIRED):
        errors.append("evidence set is incomplete or duplicated")
    for item in records:
        if not isinstance(item, dict):
            errors.append("malformed evidence record")
            continue
        raw = item.get("path")
        if not isinstance(raw, str) or Path(raw).is_absolute() or any(part in {"", ".", ".."} for part in raw.split("/")):
            errors.append(f"unsafe evidence path: {raw}")
            continue
        path = (ROOT / raw).resolve()
        if ROOT not in path.parents or not path.is_file():
            errors.append(f"missing evidence: {raw}")
        elif digest(path) != item.get("sha256"):
            errors.append(f"evidence digest mismatch: {raw}")
    gates = manifest.get("gates", {})
    for key in ("local_unified_reference", "aggregate_agentic_verification", "four_real_causal_agent_repairs", "local_rtl_to_gds_bridge"):
        if gates.get(key) != "passed":
            errors.append(f"required local gate is not passed: {key}")
    if gates.get("real_model_primary_benchmark") != "passed":
        errors.append("real-model primary benchmark is not recorded as passed")
    if gates.get("real_model_full_pipeline") != "blocked" or gates.get("real_model_heldout_generalization") != "blocked":
        errors.append("real-model pipeline/generalization boundary was not preserved")
    if manifest.get("release_decision") != "blocked_pending_physical_and_measured_gates":
        errors.append("release decision is not fail-closed")
    if manifest.get("analog_authorized") is not False:
        errors.append("analog_authorized must remain false")
    if gates.get("physical_converter") == "passed" or gates.get("measured_hardware") == "passed":
        errors.append("unsupported physical or measured gate was promoted")
    result = {"schema_version": "flagship-end-to-end-release-check-v1", "status": "passed" if not errors else "blocked", "errors": errors, "manifest": str(args.manifest.resolve())}
    result["check_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
