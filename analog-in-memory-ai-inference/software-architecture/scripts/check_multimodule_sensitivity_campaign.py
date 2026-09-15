#!/usr/bin/env python3
"""Verify the bounded local multi-module sensitivity campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(path: Path) -> Path:
    if path.is_absolute() or path.is_file():
        return path
    local_root = Path(__file__).resolve().parents[1]
    candidate = local_root / path
    return candidate if candidate.is_file() else path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    report_path = args.run / "sensitivity_report.json"
    manifest_path = args.run / "manifest.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = resolve(Path(entry["path"]))
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if report.get("model_revision") != "607a30d783dfa663caf39e06633721c8d4cfcd7e":
        failures.append("campaign is not tied to the pinned GPT-2 revision")
    if set(report.get("calibration_split", [])) & set(report.get("evaluation_split", [])):
        failures.append("campaign calibration and evaluation splits overlap")
    results = report.get("results", [])
    if len(results) != 17:
        failures.append(f"expected 17 sensitivity scenarios, found {len(results)}")
    if report.get("summary", {}).get("passing_screen_scenarios") != 2:
        failures.append("expected exactly two passing local sensitivity scenarios")
    full = [row for row in results if len(row.get("selected_modules", [])) == 3]
    high_precision = [row for row in full if row.get("adc_bits") == 16 and row.get("activation_bound_multiplier") == 1.0]
    if len(high_precision) != 1 or high_precision[0].get("screen_pass") is not False:
        failures.append("full three-module ADC16 scenario did not preserve the negative boundary")
    c_proj = [row for row in results if row.get("selected_modules") == ["transformer.h.0.mlp.c_proj"]]
    if len(c_proj) != 1 or c_proj[0]["quality"]["teacher_forced_argmax_agreement"] >= 0.99:
        failures.append("c_proj isolation did not identify the weak-module boundary")
    mixed_policy = [row for row in results if row.get("selected_modules") == ["transformer.h.0.mlp.c_fc", "transformer.h.0.attn.c_attn"]]
    if len(mixed_policy) != 1:
        failures.append("governed c_proj-digital mixed policy scenario is missing")
    if report.get("claim_boundary", "").find("no measured hardware") < 0:
        failures.append("campaign claim boundary is incomplete")
    result = {
        "status": "passed" if not failures else "failed",
        "failures": failures,
        "finding": "isolated c_fc and c_attn pass ADC12 screening; the full three-module path fails through ADC16, with c_proj the weakest isolated module",
        "claim_boundary": "Local CPU sensitivity evidence only; no analog authorization, measured energy, latency, or silicon claim.",
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
