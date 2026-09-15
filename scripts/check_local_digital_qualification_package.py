#!/usr/bin/env python3
"""Check the local digital qualification package is complete and fail-closed."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    report = json.loads((args.package / "local_digital_qualification_package.json").read_text())
    failures = []
    if report.get("decision") != "digital_reference_and_deterministic_fallback_only":
        failures.append("decision is not digital fallback only")
    if report.get("analog_authorized") is not False or report.get("workload_vectors") != 162:
        failures.append("package is not fail-closed or does not cover 162 vectors")
    parity = report.get("fallback_parity", {})
    if parity.get("all_modules_numerically_equal") is not True or parity.get("tolerance") != {"atol": 3e-5, "rtol": 1e-5}:
        failures.append("fallback parity gate is incomplete")
    runtime = report.get("runtime", {})
    if (runtime.get("scheduled_vectors") != 162 or runtime.get("analog_instruction_count") != 0
            or runtime.get("all_routes_fallback") is not True):
        failures.append("runtime trace does not prove all-vector fallback")
    for key, source in report.get("sources", {}).items():
        path = Path(source["path"])
        if not path.is_file() or sha256(path) != source.get("sha256"):
            failures.append(f"stale or missing source: {key}")
    boundary = report.get("claim_boundary", "")
    if "no measured analog execution" not in boundary or "production claim" not in boundary:
        failures.append("claim boundary is too broad")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "local digital qualification is complete and analog authorization remains closed."}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
