#!/usr/bin/env python3
"""Verify the local activation-distribution coverage matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REQUIRED_CONTEXTS = {"calibration", "original", "stress", "third_holdout"}
REQUIRED_STATS = {"count", "min_abs", "max_abs", "p50_abs", "p95_abs", "p99_abs", "mean_abs", "per_text"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    report = json.loads((args.package / "activation_coverage_report.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    contexts = report.get("contexts", {})
    if set(contexts) != REQUIRED_CONTEXTS:
        failures.append(f"expected contexts {sorted(REQUIRED_CONTEXTS)}, got {sorted(contexts)}")
    modules = report.get("target_modules", [])
    if len(modules) != 3 or len(set(modules)) != 3:
        failures.append("coverage report must contain exactly three distinct target modules")
    for context, payload in contexts.items():
        distributions = payload.get("distributions", {})
        if set(distributions) != set(modules):
            failures.append(f"{context} does not cover every target module")
        for module in modules:
            stats = distributions.get(module, {})
            if REQUIRED_STATS - set(stats) or stats.get("count", 0) <= 0:
                failures.append(f"{context}/{module} has incomplete or empty statistics")
            if len(stats.get("per_text", [])) != payload.get("text_count"):
                failures.append(f"{context}/{module} per-text coverage count mismatch")
    ratios = report.get("coverage_ratios", {})
    if set(ratios) != set(modules):
        failures.append("coverage ratios do not cover every target module")
    for module in modules:
        if set(ratios.get(module, {})) != REQUIRED_CONTEXTS - {"calibration"}:
            failures.append(f"{module} coverage ratios are incomplete")
    boundary = report.get("claim_boundary", "")
    if any(phrase not in boundary for phrase in ("Local CPU", "no hardware latency", "analog authorization")):
        failures.append("coverage claim boundary is too broad")
    print(json.dumps({
        "status": "passed" if not failures else "failed",
        "failures": failures,
        "finding": "activation distributions are measured across calibration, original, stress, and third-holdout contexts; this does not qualify a transfer profile.",
        "claim_boundary": boundary,
    }, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
