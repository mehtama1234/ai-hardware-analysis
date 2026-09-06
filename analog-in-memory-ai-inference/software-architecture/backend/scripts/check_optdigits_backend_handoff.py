#!/usr/bin/env python3
"""Exercise the existing ONNX analysis and placement path for the real task."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from onnx_analyzer import analyze_model
from hardware_placement import build_hardware_placement


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared_run", type=Path)
    args = parser.parse_args()
    run = args.prepared_run.resolve()
    manifest = json.loads((run / "result.json").read_text())
    model = run / "model.onnx"
    if hashlib.sha256(model.read_bytes()).hexdigest() != manifest["model_sha256"]:
        raise ValueError("Prepared model hash mismatch")
    output = run / ("backend-handoff-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    output.mkdir(exist_ok=False)
    analysis = analyze_model(model)
    placement = build_hardware_placement(analysis)
    (output / "analysis.json").write_text(json.dumps(analysis, indent=2) + "\n")
    (output / "placement.json").write_text(json.dumps(placement, indent=2) + "\n")
    rows = placement["placement_rows"]
    checks = {"five_operators": len(rows) == 5,
              "two_matrix_operations": sum(row["operator_kind"] == "MatMul" for row in rows) == 2,
              "unique_operator_ids": len({row["operator_id"] for row in rows}) == len(rows)}
    result = {"checks": checks, "model_sha256": manifest["model_sha256"],
              "physical_execution_authorized": False, "test_evaluated": False,
              "boundary": "Existing backend graph/placement proposal only; heuristic costs are not measurements; contract-specific lowering remains open."}
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    print(output)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
