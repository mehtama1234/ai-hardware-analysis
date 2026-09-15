#!/usr/bin/env python3
"""Verify the staged module-error decomposition."""

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
    report = json.loads((args.package / "module_error_decomposition_report.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    modules = report.get("target_modules", [])
    if len(modules) != 3 or report.get("finding", {}).get("dominant_module") != "transformer.h.0.mlp.c_proj":
        failures.append("decomposition does not preserve c_proj as dominant combined-profile module")
    if report.get("finding", {}).get("dominant_error_source") != "combined_current_profile":
        failures.append("decomposition did not retain combined-profile attribution")
    if any(not row.get("monotonic") for row in report.get("boundary_intervention_summary", {}).values()):
        failures.append("boundary propagation is not monotonic")
    if report.get("decision") != "c_proj_boundary_and_adc_resolution_are_the_next_local_targets" or report.get("analog_authorized") is not False:
        failures.append("decomposition decision is unsafe")
    boundary = report.get("claim_boundary", "")
    if "Local CPU" not in boundary or "analog authorization" not in boundary:
        failures.append("claim boundary is too broad")
    print(json.dumps({"status": "passed" if not failures else "failed", "failures": failures,
                      "finding": "c_proj is the dominant combined-profile error boundary; ADC resolution and its downstream propagation are the next targets.",
                      "claim_boundary": boundary}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
