#!/usr/bin/env python3
"""Verify local multi-module output-to-logit attribution evidence."""

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
    report_path = args.run / "error_attribution_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads((args.run / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    expected = {"c_fc_only", "c_proj_only", "attn_only", "c_proj_digital_mixed", "full_three_module"}
    if set(report.get("scenarios", {})) != expected:
        failures.append("attribution scenario set is incomplete")
    if report.get("adc_bits") != 12 or report.get("calibrated") is not True:
        failures.append("attribution is not the calibrated ADC12 replay")
    scenarios = report["scenarios"]
    c_proj = scenarios["c_proj_only"]["metrics"]
    c_fc = scenarios["c_fc_only"]["metrics"]
    attn = scenarios["attn_only"]["metrics"]
    if c_proj["modules"][report["target_modules"][1]]["output_relative_l2"] <= c_fc["modules"][report["target_modules"][0]]["output_relative_l2"]:
        failures.append("c_proj is not the largest isolated output error")
    if c_proj["final_logit_relative_l2"] <= attn["final_logit_relative_l2"]:
        failures.append("c_proj is not the largest isolated final-logit error")
    mixed = scenarios["c_proj_digital_mixed"]["metrics"]
    full = scenarios["full_three_module"]["metrics"]
    if mixed["final_argmax_disagreement"] <= 0 or full["final_argmax_disagreement"] <= 0:
        failures.append("mixed and full routes did not preserve a nonzero quality disturbance")
    summary = report.get("interaction_summary", {})
    if not 0 < summary.get("full_to_isolated_sum_ratio", 0) < 1:
        failures.append("non-additive interaction ratio is outside the retained finding")
    if "no measured hardware" not in report.get("claim_boundary", ""):
        failures.append("claim boundary does not exclude hardware claims")
    result = {
        "status": "passed" if not failures else "failed",
        "failures": failures,
        "finding": "c_proj dominates isolated output and logit error; the full route shows non-additive cancellation/interaction",
        "claim_boundary": "Local CPU attribution only; no causal hardware, energy, latency, silicon, or authorization claim.",
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
