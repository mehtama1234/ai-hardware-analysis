#!/usr/bin/env python3
"""Verify a paired Colab attention and CUDA compiled-training handoff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify(directory: Path) -> dict:
    handoff = load(directory / "handoff.json")
    attention = load(directory / "attention-benchmark-cuda.json")
    training = load(directory / "compiled-training-cuda.json")
    require((directory / "attention-started").exists(), "missing remote start marker")
    require((directory / "attention-finished").exists(), "missing remote completion marker")
    require(attention.get("status") == "passed" and attention.get("gpu_execution_accepted") is True,
            "attention GPU report did not pass")
    require(training.get("status") == "passed" and training.get("gpu_execution_accepted") is True,
            "compiled-training GPU report did not pass")
    require(attention.get("device_name") and training.get("device_name") == attention.get("device_name"),
            "reports do not identify the same GPU")
    attention_rows = attention.get("rows", [])
    require({row.get("backend") for row in attention_rows} == {"materialized", "sdpa", "recomputed"},
            "attention backend coverage is incomplete")
    attention_errors = [max(row.get("errors_vs_cpu_fp64", {}).values()) for row in attention_rows]
    require(attention_errors and max(attention_errors) <= 5e-6, "attention FP64 comparison exceeded tolerance")
    case = training.get("case", {})
    steps = case.get("steps", [])
    require(len(steps) == 3 and all(row.get("status") == "passed" for row in steps),
            "compiled training did not validate three optimizer steps")
    output_errors = [row.get("output_max_abs_error", 1.0) for row in steps]
    gradient_errors = [max(row.get("parameter_gradient_errors", {}).values(), default=1.0) for row in steps]
    update_errors = [max(row.get("updated_parameter_errors", {}).values(), default=1.0) for row in steps]
    momentum_errors = [max(row.get("optimizer_momentum_errors", {}).values(), default=1.0) for row in steps]
    require(max(output_errors) <= 5e-6 and max(gradient_errors) <= 5e-6 and
            max(update_errors) <= 5e-6 and max(momentum_errors) <= 5e-6,
            "compiled-training numerical equivalence exceeded tolerance")
    packaged = handoff.get("source_sha256", {})
    observed = {}
    for report in (attention, training):
        observed.update(report.get("provenance", {}).get("source_sha256", {}))
    require(packaged and all(observed.get(path) == digest for path, digest in packaged.items()),
            "combined report provenance does not cover the packaged source set")
    result = {
        "status": "verified",
        "run_id": handoff.get("run_id"),
        "device_name": attention.get("device_name"),
        "attention_backends": sorted(row["backend"] for row in attention_rows),
        "max_attention_error": max(attention_errors),
        "training_steps": len(steps),
        "max_training_output_error": max(output_errors),
        "max_training_gradient_error": max(gradient_errors),
        "max_training_update_error": max(update_errors),
        "max_training_momentum_error": max(momentum_errors),
        "source_hashes_covered": len(packaged),
    }
    (directory / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.directory), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
