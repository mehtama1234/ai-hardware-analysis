#!/usr/bin/env python3
"""Independently verify an agentic hardware release manifest."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    path = args.manifest.resolve()
    errors: list[str] = []
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: cannot read manifest: {error}")
        return 1
    if manifest.get("schema_version") != "agentic-hardware-release-manifest-v1":
        errors.append("unexpected release manifest schema")
    stored_manifest_digest = manifest.get("manifest_sha256")
    manifest_body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    expected_manifest_digest = sha256(json.dumps(manifest_body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if stored_manifest_digest != expected_manifest_digest:
        errors.append("release manifest self-digest does not match")
    closure = manifest.get("closure", {})
    closure_path = Path(closure.get("path", ""))
    if not closure_path.is_absolute():
        closure_path = path.parent / closure_path
    if not closure_path.is_file():
        errors.append("closure summary is missing")
    else:
        if closure.get("sha256") != digest(closure_path):
            errors.append("closure summary digest does not match")
        try:
            summary = json.loads(closure_path.read_text(encoding="utf-8"))
            if closure.get("status") != summary.get("status"):
                errors.append("closure status does not match summary")
            if closure.get("canonical_source_unchanged") is not True:
                errors.append("canonical source is not proven unchanged")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"cannot read closure summary: {error}")
    claims = manifest.get("claims", {})
    expected = {"digital_verification", "physical_layout", "analog_hardware", "measured_hardware"}
    if set(claims) != expected:
        errors.append("claim classes are incomplete")
    statuses = {item.get("status") for item in claims.values() if isinstance(item, dict)}
    if not statuses.issubset({"proven", "review_required", "blocked", "modeled", "unauthorized", "unsupported"}):
        errors.append("claim status is outside the allowed vocabulary")
    if claims.get("analog_hardware", {}).get("status") != "unauthorized":
        errors.append("analog claim is not explicitly unauthorized")
    if manifest.get("analog_authorized") is not False:
        errors.append("analog_authorized must remain false")
    model_execution = manifest.get("model_execution", {})
    if model_execution.get("kind") not in {"real_model", "provider_free_fixture"}:
        errors.append("model execution provenance kind is invalid")
    if model_execution.get("kind") == "real_model":
        provenance = model_execution.get("provenance")
        if not isinstance(provenance, dict) or provenance.get("provider") != "google-colab" or not provenance.get("model_id") or not provenance.get("gpu"):
            errors.append("real-model release provenance is incomplete")
    aimc_boundary = manifest.get("aimc_boundary", {})
    if aimc_boundary.get("status") != "traceable" or aimc_boundary.get("analog_authorized") is not False:
        errors.append("AIMC physical boundary is not traceable or is ambiguously authorized")
    aimc_path = Path(str(aimc_boundary.get("path", "")))
    if not aimc_path.is_absolute():
        aimc_path = Path(__file__).resolve().parents[1] / aimc_path
    if not aimc_path.is_file():
        errors.append("AIMC qualification handoff is missing")
    elif aimc_boundary.get("sha256") != digest(aimc_path):
        errors.append("AIMC qualification handoff digest does not match")
    else:
        try:
            aimc = json.loads(aimc_path.read_text(encoding="utf-8"))
            if aimc.get("status") != "passed" or aimc_boundary.get("qualification_status") != aimc.get("status"):
                errors.append("AIMC qualification handoff is not a passed evidence package")
            if aimc_boundary.get("same_design_run") != aimc.get("relationship", {}).get("same_design_run"):
                errors.append("AIMC boundary relationship metadata does not match")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"cannot read AIMC qualification handoff: {error}")
    if manifest.get("release_decision") not in {"blocked_pending_human_approval", "blocked_human_rejected", "review_required", "blocked", "passed"}:
        errors.append("release decision is invalid")
    approval = closure.get("approval", {})
    if approval.get("fixture_only") is True and manifest.get("release_decision") != "blocked_pending_human_approval":
        errors.append("fixture approval cannot produce a releasable decision")
    signoff = manifest.get("human_signoff")
    if signoff is not None:
        signoff_path = Path(signoff.get("path", ""))
        if not signoff_path.is_file():
            errors.append("human signoff receipt is missing")
        else:
            try:
                receipt = json.loads(signoff_path.read_text(encoding="utf-8"))
                receipt_body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
                expected_receipt = sha256(json.dumps(receipt_body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
                if signoff.get("sha256") != digest(signoff_path) or receipt.get("receipt_sha256") != expected_receipt or signoff.get("status") != receipt.get("status"):
                    errors.append("human signoff receipt integrity does not match")
                if receipt.get("closure_sha256") != closure.get("sha256"):
                    errors.append("human signoff is not bound to closure digest")
                if signoff.get("review_duration_seconds") != receipt.get("review_duration_seconds"):
                    errors.append("human review effort is not bound to signoff receipt")
                if signoff.get("reviewed_manifest_sha256") != receipt.get("manifest_sha256"):
                    errors.append("signoff does not identify the manifest reviewed by the human")
                if signoff.get("review_bindings") != receipt.get("review_bindings"):
                    errors.append("signoff review bindings do not match the receipt")
                expected_bindings = {
                    "primary": {key: (summary.get("approval") or {}).get(key) for key in ("proposal_sha256", "source_sha256", "scope_sha256")},
                    "held_out": {key: (summary.get("held_out", {}).get("approval") or {}).get(key) for key in ("proposal_sha256", "source_sha256", "scope_sha256")},
                }
                if receipt.get("review_bindings") != expected_bindings:
                    errors.append("signoff review bindings are not bound to closure approval records")
            except (OSError, json.JSONDecodeError) as error:
                errors.append(f"cannot read human signoff receipt: {error}")
    metrics = manifest.get("metrics", {})
    required_metrics = {"diagnosis", "repair", "regression", "unsupported_claims", "latency", "human_review_effort"}
    if not isinstance(metrics, dict) or set(metrics) != required_metrics:
        errors.append("release metrics are incomplete")
    elif metrics.get("human_review_effort", {}).get("status") not in {"measured", "not_measured"}:
        errors.append("human review effort metric has an invalid status")
    elif metrics.get("repair", {}).get("success_rate") is None or metrics.get("regression", {}).get("rate") is None:
        errors.append("repair and regression metrics are missing")
    if metrics.get("human_review_effort", {}).get("status") == "measured":
        duration = metrics.get("human_review_effort", {}).get("duration_seconds")
        if not isinstance(duration, (int, float)) or duration < 0:
            errors.append("measured human review effort has an invalid duration")
        if signoff is None:
            errors.append("measured human review effort has no signoff receipt")
    if manifest.get("release_decision") == "passed":
        if not isinstance(signoff, dict) or signoff.get("status") != "approved":
            errors.append("passed release has no approved human signoff")
        if claims.get("digital_verification", {}).get("status") != "proven":
            errors.append("passed release has no proven digital verification")
        if claims.get("physical_layout", {}).get("status") != "proven":
            errors.append("passed release has no proven physical layout")
        if metrics.get("human_review_effort", {}).get("status") != "measured":
            errors.append("passed release has no measured human review effort")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(json.dumps({"status": "passed", "release_decision": manifest["release_decision"], "analog_authorized": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
