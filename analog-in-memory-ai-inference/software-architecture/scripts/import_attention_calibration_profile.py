#!/usr/bin/env python3
"""Import and validate the sibling EDA repo's calibrated attention profile."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import onnx

from build_transformer_execution_contract import build_contract


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = ROOT / "samples" / "attention-block.onnx"
DEFAULT_PROFILE = (
    ROOT.parent.parent
    / "analog-digital-chip-design-eda"
    / "evidence"
    / "aimc-simulator-adapters"
    / "crosssim-calibrated-attention-block-analog-error-simulation.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def import_profile(model_path: Path, profile_path: Path, residual_limit: float = 0.01) -> dict[str, Any]:
    model = onnx.load(model_path)
    initializers = {item.name: list(item.dims) for item in model.graph.initializer}
    contract = build_contract(model_path, "robotics", "imported-crosssim-calibration", "decode")
    expected = {
        row["operator_id"]: row
        for row in contract["operator_inventory"]["operators"]
        if row.get("placement") == "analog"
    }
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    provenance = profile.get("provenance", {})
    artifacts = [str(item) for item in provenance.get("artifacts", [])]
    source_model_match = any(item.endswith(model_path.name) for item in artifacts)
    results = profile.get("error_model", {}).get("per_candidate_results", [])
    rows = []
    errors = []
    for result in results:
        candidate_id = result.get("candidate_id")
        weight_name = result.get("weight_name")
        shape = result.get("weight_shape_in_out")
        residual = float(result.get("simulator_residual_relative", float("inf")))
        shape_matches = initializers.get(weight_name) == shape
        candidate_matches = candidate_id in expected
        if not candidate_matches:
            errors.append(f"unexpected candidate: {candidate_id}")
        if not shape_matches:
            errors.append(f"weight shape mismatch: {candidate_id} -> {weight_name}")
        rows.append(
            {
                "operator_id": candidate_id,
                "weight_name": weight_name,
                "weight_shape": shape,
                "model_candidate_match": candidate_matches,
                "model_weight_shape_match": shape_matches,
                "simulator_residual_relative": residual,
                "residual_within_limit": residual <= residual_limit,
            }
        )
    expected_ids = sorted(expected)
    imported_ids = sorted(row.get("candidate_id") for row in results)
    if expected_ids != imported_ids:
        errors.append(f"candidate set mismatch: expected {expected_ids}, imported {imported_ids}")
    if not source_model_match:
        errors.append("profile provenance does not name the checked-in attention fixture")
    if not profile.get("accuracy_impact", {}).get("pass", False):
        errors.append("profile accuracy_impact.pass is false")
    if any(not row["residual_within_limit"] for row in rows):
        errors.append("one or more calibrated candidate residuals exceed the import limit")
    passed = not errors
    return {
        "schema_version": "attention-calibration-import-v0.1",
        "result_type": "guarded_external_calibration_profile_import",
        "provenance": {
            "source_profile": str(profile_path),
            "source_profile_sha256": sha256(profile_path),
            "source_model": str(model_path),
            "source_model_sha256": sha256(model_path),
            "measurement_level": provenance.get("measurement_level"),
            "tool": provenance.get("tool"),
            "tool_version": provenance.get("tool_version"),
        },
        "scope": {
            "calibration_profile": profile.get("calibration_profile"),
            "candidate_count": len(rows),
            "candidate_rows": rows,
            "voltage_range": profile.get("voltage_range"),
            "temperature_range": profile.get("temperature_range"),
            "calibration_cases": profile.get("error_model", {}).get("array_assumptions", {}).get("calibration_summary", {}).get("calibration_cases"),
        },
        "acceptance": {
            "residual_limit": residual_limit,
            "source_model_match": source_model_match,
            "candidate_set_match": expected_ids == imported_ids,
            "passed": passed,
            "errors": errors,
        },
        "claim_boundary": {
            "allowed": "The imported profile is calibrated external-simulator evidence for static projections in the named attention fixture.",
            "refused": "It does not authorize analog placement on a different model, prove calibrated silicon, prove board runtime/power, or cover drift/PVT beyond its declared scope.",
            "next_gate": "Use this profile only when model identity and candidate shapes match; add measured per-tile calibration before physical claims.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--residual-limit", type=float, default=0.01)
    args = parser.parse_args()
    if not args.model.exists():
        raise SystemExit(f"model not found: {args.model}")
    if not args.profile.exists():
        raise SystemExit(f"calibration profile not found: {args.profile}")
    result = import_profile(args.model, args.profile, args.residual_limit)
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "attention_calibration_import.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "passed": result["acceptance"]["passed"], "errors": result["acceptance"]["errors"]}, indent=2))
    if not result["acceptance"]["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
