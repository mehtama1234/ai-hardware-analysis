#!/usr/bin/env python3
"""Verify the bounded multi-module decision package."""

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
    package = args.package
    decision_path = package / "decision_audit.json"
    claim_path = package / "claim_ledger.json"
    manifest_path = package / "manifest.json"
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if decision.get("gate_count") != 8 or decision.get("passed_gate_count") != 6:
        failures.append("multi-module gate counts changed unexpectedly")
    if decision.get("decision") != "multi_module_hybrid_benefit_unproven":
        failures.append("unsafe multi-module decision")
    if decision.get("analog_candidate_authorized") is not False:
        failures.append("analog authorization is not false")
    gates = {row["gate"]: row["passed"] for row in decision.get("gates", [])}
    if gates.get("joint_adc12_task_quality") is not False:
        failures.append("joint ADC12 quality failure was not preserved")
    if gates.get("frozen_multi_module_workload") is not True or gates.get("per_module_shape_and_tensor_replay") is not True:
        failures.append("frozen multi-module replay gates are not passing")
    if gates.get("disjoint_per_module_calibration") is not True:
        failures.append("per-module calibration gate is not passing")
    if gates.get("multi_module_runtime_trace_agreement") is not True:
        failures.append("runtime trace agreement gate is not passing")
    if gates.get("matched_multi_module_cost") is not True:
        failures.append("multi-module cost ledger gate is not passing")
    runtime = manifest.get("multimodule_runtime_trace", {})
    cost = manifest.get("multimodule_cost_trace", {})
    runtime_path = Path(runtime.get("path", ""))
    cost_path = Path(cost.get("path", ""))
    if not runtime_path.is_absolute():
        runtime_path = Path.cwd() / runtime_path
    if not cost_path.is_absolute():
        cost_path = Path.cwd() / cost_path
    if not runtime_path.is_file() or digest(runtime_path) != runtime.get("sha256"):
        failures.append("runtime trace is missing or not bound by hash")
    else:
        runtime_receipt = json.loads(runtime_path.read_text(encoding="utf-8"))
        if runtime_receipt.get("workload_vectors") != 162 or len(runtime_receipt.get("events", [])) != 162:
            failures.append("runtime trace does not contain 162 events")
        if runtime_receipt.get("totals", {}).get("analog_events") != 0:
            failures.append("runtime trace contains analog events despite closed authorization")
    if not cost_path.is_file() or digest(cost_path) != cost.get("sha256"):
        failures.append("cost trace is missing or not bound by hash")
    else:
        cost_rows = [json.loads(line) for line in cost_path.read_text(encoding="utf-8").splitlines() if line]
        if len(cost_rows) != 162 or any(row.get("enforced_route") != "digital_fallback" for row in cost_rows):
            failures.append("cost trace does not cover 162 digital-fallback rows")
    ledger = json.loads(claim_path.read_text(encoding="utf-8"))
    if any(row.get("status") == "authorized" for row in ledger.get("claims", [])):
        failures.append("claim ledger contains an authorization claim")
    claims = {row["claim"]: row for row in ledger.get("claims", [])}
    if claims.get("per_module_calibration_generalization", {}).get("status") != "proven_local_bounded":
        failures.append("calibration claim is not bounded-local proven")
    if claims.get("multi_module_runtime_agreement", {}).get("status") != "proven_local_bounded":
        failures.append("runtime claim is not bounded-local proven")
    result = {
        "status": "passed" if not failures else "failed",
        "failures": failures,
        "claim_boundary": "Local multi-module software evidence only; no physical or analog authorization claim.",
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
