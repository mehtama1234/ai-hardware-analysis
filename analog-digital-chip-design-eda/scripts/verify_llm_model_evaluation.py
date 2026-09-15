#!/usr/bin/env python3
"""Verify the acceptance contract for a real-model benchmark artifact."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def verify(path: Path, *, require_real_model: bool = False) -> list[str]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        return [f"cannot parse evaluation: {exc}"]
    errors = []
    stored_evidence_digest = payload.get("evidence_sha256")
    evidence_body = {key: value for key, value in payload.items() if key != "evidence_sha256"}
    expected_evidence_digest = hashlib.sha256(json.dumps(evidence_body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if stored_evidence_digest != expected_evidence_digest:
        errors.append("benchmark evidence self-digest does not match")
    provenance = payload.get("model_provenance")
    if provenance is not None:
        if provenance.get("schema_version") != "real-model-runtime-provenance-v1":
            errors.append("model runtime provenance schema is invalid")
        if not provenance.get("model_id") or provenance.get("provider") != "google-colab":
            errors.append("model runtime provenance is incomplete")
        if provenance.get("accelerator") != "cuda" or not provenance.get("gpu"):
            errors.append("model runtime provenance has no CUDA GPU identity")
        if provenance.get("weights_downloaded_in_runtime") is not True or provenance.get("source_archive_only") is not True:
            errors.append("model runtime provenance does not prove isolated model execution")
    elif require_real_model:
        errors.append("real-model verification requires runtime provenance")
    if payload.get("schema_version") != "llm-verification-agent-benchmark-v1":
        errors.append("unexpected benchmark schema")
    rows = payload.get("model_runs", {}).get("local-batch-command", [])
    if len(rows) != 11:
        errors.append("real-model batch must contain 11 case records")
    for row in rows:
        if row.get("status") != "available":
            errors.append(f"{row.get('design_id')} is not available")
        if row.get("grounded") is not True:
            errors.append(f"{row.get('design_id')} is not grounded")
        if row.get("diagnosis_match") is not True:
            errors.append(f"{row.get('design_id')} does not match diagnosis")
        if row.get("adversarial_review", {}).get("accepted") is not True:
            errors.append(f"{row.get('design_id')} failed adversarial review")
    aimc = payload.get("aimc_mutation_run")
    if aimc is not None:
        if aimc.get("mutation_case", {}).get("status") != "failed_baseline_observed":
            errors.append("AIMC mutation must prove a failed baseline")
        if aimc.get("status") != "available":
            errors.append("AIMC mutation model diagnosis is not available")
        if aimc.get("grounded") is not True:
            errors.append("AIMC mutation model diagnosis is not grounded")
        if aimc.get("diagnosis_match") is not True:
            errors.append("AIMC mutation model diagnosis does not match")
        if aimc.get("adversarial_review", {}).get("accepted") is not True:
            errors.append("AIMC mutation model diagnosis failed adversarial review")
        if payload.get("aimc_root_cause_gate") is True and aimc.get("root_cause_supported") is not True:
            errors.append("AIMC mutation model rationale does not support the RTL root cause")
    if payload.get("aimc_repair_gate") is True:
        repair = payload.get("aimc_mutation_repair_run") or {}
        if repair.get("status") != "available":
            errors.append("AIMC model repair is not available")
        if repair.get("grounded") is not True or repair.get("repair_match") is not True:
            errors.append("AIMC model repair is not grounded or does not match the mutation reversal")
        if repair.get("adversarial_review", {}).get("accepted") is not True:
            errors.append("AIMC model repair failed adversarial review")
    if payload.get("counter_repair_gate") is True:
        repair = payload.get("counter_repair_run") or {}
        if repair.get("status") != "available":
            errors.append("seeded_counter model repair is not available")
        if repair.get("grounded") is not True or repair.get("repair_match") is not True:
            errors.append("seeded_counter model repair is not grounded or does not match the bounded repair")
        if repair.get("adversarial_review", {}).get("accepted") is not True:
            errors.append("seeded_counter model repair failed adversarial review")
    if payload.get("timeout_repair_gate") is True:
        repair = payload.get("timeout_repair_run") or {}
        if repair.get("status") != "available":
            errors.append("seeded_timeout model repair is not available")
        if repair.get("grounded") is not True or repair.get("repair_match") is not True:
            errors.append("seeded_timeout model repair is not grounded or does not match the bounded repair")
        if repair.get("adversarial_review", {}).get("accepted") is not True:
            errors.append("seeded_timeout model repair failed adversarial review")
    if payload.get("register_repair_gate") is True:
        repair = payload.get("register_repair_run") or {}
        if repair.get("status") != "available":
            errors.append("register_peripheral model repair is not available")
        if repair.get("grounded") is not True or repair.get("repair_match") is not True:
            errors.append("register_peripheral model repair is not grounded or does not match the bounded repair")
        if repair.get("adversarial_review", {}).get("accepted") is not True:
            errors.append("register_peripheral model repair failed adversarial review")
    execution = payload.get("reference_execution", {})
    if execution.get("passed_retests") != 11:
        errors.append("reference execution must prove 11 passed retests")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--require-real-model", action="store_true")
    args = parser.parse_args()
    errors = verify(args.artifact, require_real_model=args.require_real_model)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"verified real-model evaluation: {args.artifact}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
