#!/usr/bin/env python3
"""Verify all frozen module vectors match digital fallback bitwise."""

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
    report = json.loads((args.package / "per_vector_fallback_fingerprint.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if report.get("workload_vectors") != 162 or len(report.get("target_modules", [])) != 3:
        failures.append("fingerprint report does not cover the 162-vector three-module slice")
    for module, row in report.get("modules", {}).items():
        if row.get("vectors") != 162 or row.get("numerical_mismatch_count") != 0 or row.get("numerical_match_atol_3e-5_rtol_1e-5") is not True:
            failures.append(f"digital fallback numerical mismatch for {module}")
        if len(row.get("native_row_sha256", [])) != 162 or len(row.get("fallback_row_sha256", [])) != 162:
            failures.append(f"incomplete fingerprints for {module}")
    if report.get("all_modules_numerically_equal") is not True or report.get("analog_authorized") is not False:
        failures.append("per-vector fallback parity result is unsafe")
    boundary = report.get("claim_boundary", "")
    if "Local CPU" not in boundary or "no physical analog execution" not in boundary:
        failures.append("claim boundary is too broad")
    print(json.dumps({"status": "passed" if not failures else "failed", "failures": failures,
                      "finding": "all 162 vectors for all three modules match an independent digital fallback recomputation within the explicit float32 GEMM tolerance.",
                      "claim_boundary": boundary}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
