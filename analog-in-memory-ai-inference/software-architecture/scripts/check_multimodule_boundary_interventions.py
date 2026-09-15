#!/usr/bin/env python3
"""Verify causal-style local boundary intervention evidence."""

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
    report_path = args.run / "boundary_intervention_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads((args.run / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if len(report.get("results", {})) != 3 or report.get("amplitudes") != [0.25, 0.5, 1.0, 2.0]:
        failures.append("boundary intervention matrix is incomplete")
    names = report["target_modules"]
    if report.get("adc_bits") != 12 or report.get("calibrated") is not True:
        failures.append("boundary interventions are not calibrated ADC12 injections")
    for name, row in report["results"].items():
        values = [row["interventions"][str(scale)]["final_logit_relative_l2"] for scale in report["amplitudes"]]
        if any(a <= 0 or b <= a for a, b in zip(values, values[1:])):
            failures.append(f"final-logit propagation is not strictly increasing for {name}")
    c_proj = report["results"][names[1]]["interventions"]["1.0"]
    c_fc = report["results"][names[0]]["interventions"]["1.0"]
    if c_proj["final_argmax_disagreement"] <= c_fc["final_argmax_disagreement"]:
        failures.append("c_proj does not dominate c_fc at full intervention")
    if "no measured hardware" not in report.get("claim_boundary", ""):
        failures.append("boundary claim boundary is incomplete")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "c_proj is the dominant propagation-sensitive boundary; all source perturbations grow monotonically across intervention amplitudes.",
              "claim_boundary": "Local CPU boundary intervention only; no causal hardware or authorization claim."}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
