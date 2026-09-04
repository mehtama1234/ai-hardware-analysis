#!/usr/bin/env python3
"""Validate the staged end-to-end AIMC workload portfolio."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "evidence" / "aimc-hardware-lab" / "end-to-end-workload-portfolio.json"
COMPILER_PACKAGE = ROOT / "evidence" / "aimc-hybrid-compiler-runtime" / "hybrid_compiler_runtime_package.json"
HARDWARE_PROFILE = ROOT / "evidence" / "aimc-hardware-lab" / "hardware-profile-educational-hybrid-tile-v1.json"
EXPECTED_PROFILE_ID = "educational-hybrid-tile-v1"


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def main() -> int:
    try:
        data = json.loads(PORTFOLIO.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"cannot read portfolio: {exc}")

    if data.get("schema_version") != "aimc_end_to_end_workload_portfolio.v1":
        return fail("unexpected schema_version")

    shared = data.get("shared_acceptance_contract")
    if not isinstance(shared, dict):
        return fail("shared_acceptance_contract is missing")
    required_modes = {"digital_only", "hybrid_guarded", "hybrid_analog_enabled"}
    if set(shared.get("required_execution_modes", [])) != required_modes:
        return fail("required execution modes are incomplete")
    required_metrics = {
        "task_metric",
        "end_to_end_latency",
        "energy_per_inference",
        "power",
        "thermal_behavior",
        "sram_traffic",
        "converter_crossings",
        "fallback_rate",
    }
    if set(shared.get("required_system_metrics", [])) != required_metrics:
        return fail("required system metrics are incomplete")
    if shared.get("hardware_profile_id") != EXPECTED_PROFILE_ID:
        return fail("portfolio acceptance contract does not name the authoritative hardware profile")
    try:
        profile = json.loads(HARDWARE_PROFILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"cannot read hardware profile: {exc}")
    if profile.get("schema_version") != "aimc_hardware_profile.v1":
        return fail("unexpected hardware profile schema_version")
    if profile.get("profile_id") != EXPECTED_PROFILE_ID:
        return fail("unexpected hardware profile ID")
    tile = profile.get("tile", {})
    converter = profile.get("converter", {})
    memory = profile.get("memory", {})
    calibration = profile.get("calibration", {})
    required_profile_values = [
        tile.get("rows"), tile.get("columns"), tile.get("cell_precision_bits"),
        tile.get("weight_slice_count"), tile.get("accumulation_width_bits"),
        converter.get("dac_bits"), converter.get("adc_bits"),
        memory.get("sram_capacity_bytes"), memory.get("sram_read_bandwidth_bytes_per_cycle"),
        memory.get("sram_write_bandwidth_bytes_per_cycle"), calibration.get("interval_inferences"),
    ]
    if any(not isinstance(value, int) or value <= 0 for value in required_profile_values):
        return fail("hardware profile is missing positive integer contract fields")

    workloads = data.get("workloads")
    if not isinstance(workloads, list) or not workloads:
        return fail("workloads must be a non-empty list")

    required_fields = {
        "stage",
        "workload_id",
        "family",
        "model_id",
        "dataset_id",
        "task_metric",
        "status",
        "evidence",
        "next_proof",
    }
    ids: list[str] = []
    statuses: Counter[str] = Counter()
    for workload in workloads:
        if not isinstance(workload, dict):
            return fail("each workload must be an object")
        missing = required_fields - workload.keys()
        if missing:
            return fail(f"{workload.get('workload_id', '<unknown>')} missing {sorted(missing)}")
        workload_id = workload["workload_id"]
        if not isinstance(workload_id, str) or not workload_id:
            return fail("workload_id must be a non-empty string")
        if workload_id in ids:
            return fail(f"duplicate workload_id {workload_id}")
        ids.append(workload_id)
        if workload["stage"] not in {1, 2, 3, 4}:
            return fail(f"{workload_id} has invalid stage")
        if not isinstance(workload["evidence"], list) or not workload["evidence"]:
            return fail(f"{workload_id} has no evidence references")
        for reference in workload["evidence"]:
            if not isinstance(reference, str) or not reference:
                return fail(f"{workload_id} has an invalid evidence reference")
            if not (ROOT / reference).is_file():
                return fail(f"{workload_id} references missing file {reference}")
        if not isinstance(workload["next_proof"], str) or not workload["next_proof"]:
            return fail(f"{workload_id} has no next proof")
        statuses[workload["status"]] += 1

    if not any(item["stage"] == 1 and item["model_id"] for item in workloads):
        return fail("portfolio has no executable stage-1 model")
    if not any(item["stage"] == 2 and item["model_id"] for item in workloads):
        return fail("portfolio has no transformer stage-2 model")

    try:
        compiler = json.loads(COMPILER_PACKAGE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"cannot read shared compiler package: {exc}")
    compiler_ids = [model.get("portfolio_workload_id") for model in compiler.get("models", [])]
    shared_hardware = compiler.get("shared_hardware", {})
    if shared_hardware.get("profile_id") != EXPECTED_PROFILE_ID:
        return fail("shared compiler package does not name the authoritative hardware profile")
    if shared_hardware.get("profile_source") != str(HARDWARE_PROFILE.relative_to(ROOT)):
        return fail("shared compiler package hardware profile source is incorrect")
    if len(compiler_ids) != len(set(compiler_ids)):
        return fail("shared compiler package has duplicate canonical workload IDs")
    if set(compiler_ids) != set(ids):
        return fail("shared compiler package and portfolio manifest do not cover the same workload IDs")
    if any(not isinstance(value, str) or not value for value in compiler_ids):
        return fail("shared compiler package has a missing canonical workload ID")
    for model in compiler.get("models", []):
        if model.get("hardware_profile_id") != EXPECTED_PROFILE_ID:
            return fail(f"{model.get('portfolio_workload_id', '<unknown>')} has no matching hardware profile")
        source_model = model.get("source_model")
        if isinstance(source_model, str) and source_model.lower().endswith(".onnx"):
            source_path = Path(source_model)
            candidates = [source_path] if source_path.is_absolute() else [ROOT / source_path, ROOT.parent / source_path]
            if not any(candidate.is_file() for candidate in candidates):
                return fail(f"{model.get('portfolio_workload_id', '<unknown>')} references missing ONNX model {source_model}")

    print("PASS")
    print(f"portfolio_id {data['portfolio_id']}")
    print(f"workloads {len(workloads)}")
    print("stages " + ", ".join(f"{stage}:{sum(item['stage'] == stage for item in workloads)}" for stage in (1, 2, 3, 4)))
    print("statuses " + ", ".join(f"{status}:{count}" for status, count in sorted(statuses.items())))
    print(f"manifest {PORTFOLIO}")
    print(f"compiler {COMPILER_PACKAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
