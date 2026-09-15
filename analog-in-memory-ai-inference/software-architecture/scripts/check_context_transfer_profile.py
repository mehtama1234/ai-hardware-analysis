#!/usr/bin/env python3
"""Verify cross-split context-aware transfer evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    report_path = args.run / "context_transfer_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads((args.run / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    results = report.get("results", {})
    expected = {"global_affine_original", "global_affine_stress",
                "magnitude_context_affine_original", "magnitude_context_affine_stress"}
    if set(results) != expected:
        failures.append("context transfer split matrix is incomplete")
    expected_states = {
        "global_affine_original": False, "global_affine_stress": True,
        "magnitude_context_affine_original": True, "magnitude_context_affine_stress": False,
    }
    for name, expected_pass in expected_states.items():
        if results.get(name, {}).get("quality", {}).get("screen_pass") is not expected_pass:
            failures.append(f"unexpected context transfer result: {name}")
    if report.get("passing_results") != ["global_affine_stress", "magnitude_context_affine_original"]:
        failures.append("context transfer passing set changed unexpectedly")
    if report.get("analog_authorized") is not False:
        failures.append("context transfer authorized analog execution")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "global and magnitude-context affine models each pass only one split; context partitioning alone does not generalize.",
              "claim_boundary": report.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
