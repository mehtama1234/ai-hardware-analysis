#!/usr/bin/env python3
"""Verify the bounded local multi-module GPT-2 replay receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(path: Path, root: Path) -> Path:
    if path.is_absolute() or path.exists():
        return path
    candidate = root / path
    return candidate if candidate.exists() else path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    package = args.package
    report_path = package / "multimodule_evaluation.json"
    tensor_path = package / "projection_tensors.npz"
    manifest_path = package / "manifest.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = resolve(Path(entry["path"]), Path.cwd())
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest source mismatch: {path}")
    fixture = report["fixture"]
    if fixture["revision"] != "607a30d783dfa663caf39e06633721c8d4cfcd7e":
        failures.append("fixture revision is not pinned")
    modules = fixture.get("target_modules", [])
    if len(modules) != 3 or report["model"]["target_modules"] != modules:
        failures.append("multi-module target list is incomplete or inconsistent")
    if not set(fixture["calibration"]).isdisjoint(fixture["evaluation"]):
        failures.append("calibration and evaluation splits overlap")
    variants = {variant["id"]: variant for variant in report["variants"]}
    if set(variants) != {"ideal_tiled_control", "dac10_weight8_adc12"}:
        failures.append("expected ideal and ADC12 variants are not present")
    ideal = variants.get("ideal_tiled_control", {})
    hybrid = variants.get("dac10_weight8_adc12", {})
    if not ideal.get("exploratory_quality_screen_pass"):
        failures.append("ideal multi-module control failed")
    if hybrid.get("exploratory_quality_screen_pass") is not False:
        failures.append("joint ADC12 quality failure was not preserved")
    if len(hybrid.get("quality", {}).get("rows", [])) != len(fixture["evaluation"]):
        failures.append("joint ADC12 calibrated generation rows are incomplete")
    if hybrid.get("uncalibrated_quality") is None or len(hybrid["uncalibrated_quality"].get("rows", [])) != len(fixture["evaluation"]):
        failures.append("joint ADC12 uncalibrated generation rows are incomplete")
    try:
        with np.load(tensor_path) as arrays:
            expected_keys = {
                name.replace(".", "__") + "__ideal_tiled_control"
                for name in modules
            }
            expected_keys.update({
                name.replace(".", "__") + "__dac10_weight8_adc12__" + state
                for name in modules for state in ("uncalibrated", "calibrated")
            })
            if set(arrays.files) != expected_keys:
                failures.append("tensor artifact keys do not cover every module and variant")
            for key in expected_keys:
                if arrays[key].shape[0] != 162:
                    failures.append(f"tensor row count is not 162: {key}")
    except Exception as exc:
        failures.append(f"tensor artifact unreadable: {exc}")
    if report.get("analog_authorized") is not False or report.get("decision") != "multi_module_hybrid_benefit_unproven":
        failures.append("multi-module replay contains an unsafe decision")
    calibration = report.get("calibration", {})
    if set(calibration) != set(modules) or any(
        row.get("method") != "per-output-channel affine gain and offset correction"
        or row.get("rows", 0) <= 0
        or row.get("channels", 0) <= 0
        or row.get("relative_l2_after", -1) < 0
        for row in calibration.values()
    ):
        failures.append("per-module disjoint calibration records are incomplete")
    if hybrid.get("uncalibrated_quality") is None:
        failures.append("uncalibrated joint quality result is missing")
    result = {
        "status": "passed" if not failures else "failed",
        "failures": failures,
        "scope": "pinned fixture, disjoint split, module coverage, tensor shapes, ideal control, joint ADC12 quality boundary, and authorization guard",
        "claim_boundary": "This verifies local software replay only; it does not prove calibration, runtime latency, hardware energy, silicon yield, or analog authorization.",
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
