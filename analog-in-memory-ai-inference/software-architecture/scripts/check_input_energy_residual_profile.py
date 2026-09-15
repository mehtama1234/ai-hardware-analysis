#!/usr/bin/env python3
"""Verify the input-energy residual profile's negative boundary."""

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
    report = json.loads((args.package / "context_transfer_report.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    results = report.get("results", {})
    for dataset in ("original", "stress", "third_holdout"):
        row = results.get(f"input_energy_residual_affine_{dataset}", {})
        if row.get("quality", {}).get("screen_pass") is not False:
            failures.append(f"input-energy residual unexpectedly passed {dataset}")
    if report.get("analog_authorized") is not False:
        failures.append("input-energy residual report authorized analog execution")
    boundary = report.get("claim_boundary", "")
    if "Local CPU" not in boundary or "analog authorization" not in boundary:
        failures.append("claim boundary is too broad")
    print(json.dumps({"status": "passed" if not failures else "failed", "failures": failures,
                      "finding": "incoming activation-energy residual correction does not generalize across the retained three-split workload.",
                      "claim_boundary": boundary}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
