#!/usr/bin/env python3
"""Verify fallback route coverage and preserve the exact-parity evidence limit."""

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
    report = json.loads((args.package / "transformer_fallback_output_audit.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if (report.get("scheduled_vectors") != 162
            or report.get("scheduled_vector_ids_contiguous") is not True
            or report.get("scheduled_routes_all_fallback") is not True
            or report.get("all_code_contract_bound") is not True):
        failures.append("162-vector fallback schedule is incomplete or unsafe")
    if report.get("exact_fallback_context_count") != 4 or report.get("exact_logits_and_generation_checked") is not True:
        failures.append("four-context exact fallback evidence was not preserved")
    if report.get("per_vector_tensor_parity_retained") is not False:
        failures.append("audit incorrectly claims per-vector tensor parity")
    if report.get("decision") != "digital_reference_authoritative_per_vector_parity_receipt_still_open" or report.get("analog_authorized") is not False:
        failures.append("fallback audit decision is unsafe")
    boundary = report.get("claim_boundary", "")
    if "per-vector tensor parity is not retained" not in boundary:
        failures.append("claim boundary hides the per-vector evidence gap")
    print(json.dumps({"status": "passed" if not failures else "failed", "failures": failures,
                      "finding": "162 fallback routes are bound to the converter-code contract; exact output parity is proven for four contexts, while per-vector tensor parity remains explicitly open.",
                      "claim_boundary": boundary}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
