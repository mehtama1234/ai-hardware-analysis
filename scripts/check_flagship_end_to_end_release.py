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
    "historical_breadth_evidence",
    "semantic_debugging_breadth",
    "proof_carrying_closure_bundle",
    "four_causal_agent_receipt",
    "four_causal_agent_package",
    "rtl2gds_bridge",
    "structured_register_rtl2gds_handoff",
    "physical_evidence_archive",
    "model_to_chip_manifest",
    "model_to_chip_archive_receipt",
    "real_model_summary",
    "real_model_benchmark",
    "real_model_heldout",
    "real_model_pipeline",
    "real_model_choice_summary",
    "real_model_choice_benchmark",
    "real_model_choice_heldout",
    "real_model_choice_pipeline",
    "real_model_evidence_check",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_structured_register_handoff(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        handoff = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"structured register handoff is unreadable: {exc}"]
    if handoff.get("schema_version") != "register-peripheral-model-repair-rtl2gds-handoff-v1":
        errors.append("structured register handoff schema is unsupported")
    if handoff.get("status") != "passed" or handoff.get("design") != "register_peripheral":
        errors.append("structured register handoff is not a passed register package")
    model = handoff.get("model", {})
    if model.get("repair_match") is not True or model.get("grounded") is not True:
        errors.append("structured register model evidence is not grounded and repair-matching")
    retest = handoff.get("repair_retest", {})
    if retest.get("status") != "passed" or retest.get("model_generated") is not True or retest.get("original_unchanged") is not True:
        errors.append("structured register repair retest is incomplete")
    formal = handoff.get("formal", {})
    runs = formal.get("property_runs", [])
    if formal.get("status") != "passed" or formal.get("proof") != "proven" or formal.get("property_count", 0) < 3 or not all(item.get("passed") is True for item in runs):
        errors.append("structured register formal evidence is incomplete")
    physical = handoff.get("physical", {})
    if (physical.get("flow_status") != "flow completed" or physical.get("source_match") is not True
            or physical.get("lvs_errors") != 0 or physical.get("gds_present") is not True
            or physical.get("xor_report") is not True):
        errors.append("structured register physical evidence is incomplete")
    boundary = handoff.get("claim_boundary", "")
    if "not commercial" not in boundary.lower() or "silicon" not in boundary.lower():
        errors.append("structured register claim boundary is missing local-only limits")
    return errors


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
        elif item.get("name") == "structured_register_rtl2gds_handoff":
            errors.extend(validate_structured_register_handoff(path))
    gates = manifest.get("gates", {})
    for key in ("local_unified_reference", "aggregate_agentic_verification", "historical_breadth", "proof_carrying_closure", "four_real_causal_agent_repairs", "local_rtl_to_gds_bridge", "structured_register_spec_to_gds", "portable_physical_evidence", "model_to_chip_portable_archive", "real_model_evidence_boundary"):
        if gates.get(key) != "passed":
            errors.append(f"required local gate is not passed: {key}")
    if gates.get("real_model_primary_benchmark") != "passed":
        errors.append("real-model primary benchmark is not recorded as passed")
    if gates.get("semantic_debugging_breadth") != "blocked_pending_heldout_localization":
        errors.append("semantic-debugging held-out boundary was not preserved")
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
