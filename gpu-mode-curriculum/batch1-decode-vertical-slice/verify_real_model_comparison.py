#!/usr/bin/env python3
"""Validate captured real-model comparisons without rerunning CUDA workloads."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path


def validate(report: dict) -> list[str]:
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    def same_number(actual, expected):
        return isinstance(actual, (int, float)) and not isinstance(actual, bool) and math.isfinite(actual) and math.isclose(actual, expected, rel_tol=1e-8)

    def timing(samples, median, repeats, label):
        valid = isinstance(samples, list) and len(samples) == repeats and bool(samples) and all(
            isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and x > 0 for x in samples
        )
        require(valid, f"{label}: missing or invalid raw timing samples")
        if not valid:
            return None
        derived = statistics.median(samples)
        require(same_number(median, derived), f"{label}: median disagrees with raw samples")
        return derived

    schema = report.get("schema_version")
    require(schema in ("real-model-sdpa-backend-v0.2", "real-model-device-resident-arrival-load-v0.2"), "unsupported schema: legacy reports do not establish corrected acceptance")
    require(report.get("evidence_kind") == "measured_gpu", "GPU measurement required")
    require(report.get("gpu_execution_accepted") is True, "execution not accepted")
    require(bool(report.get("source_hashes")), "missing source hashes")
    require(bool(report.get("command")), "missing reproduction command")
    require(bool(report.get("runtime")), "missing runtime versions")
    require(bool(report.get("model_profile", {}).get("model_revision")), "missing model revision")
    result = report.get("result", {})
    protocol = report.get("protocol", {})
    repeats = protocol.get("repeats")
    require(isinstance(repeats, int) and not isinstance(repeats, bool) and repeats >= 3, "at least three repeats required")
    require(result.get("output_parity") is True, "candidate output mismatch")
    require(result.get("batch_vs_individual_output_parity") is True, "batching changes individual output")

    if schema == "real-model-sdpa-backend-v0.2":
        require(report.get("attention_backends") == {"eager": "eager", "sdpa": "sdpa"}, "distinct explicit attention backends required")
        tokens = result.get("generated_token_ids", {})
        require(bool(tokens.get("eager")) and tokens.get("eager") == tokens.get("sdpa"), "stored generated tokens disagree or are absent")
        medians = [timing(result.get(f"{name}_wall_time_ms_samples"), result.get(f"{name}_wall_time_ms_median"), repeats, name) for name in ("eager", "sdpa")]
        if all(m is not None for m in medians):
            require(same_number(result.get("sdpa_over_eager_latency_ratio"), medians[1] / medians[0]), "backend latency ratio disagrees with samples")
    elif schema == "real-model-device-resident-arrival-load-v0.2":
        for key in ("direct_output_parity", "persistent_output_parity", "all_correctness_checks_passed"):
            require(result.get(key) is True, f"{key} failed")
        medians = {}
        for name in ("native_sequential", "native_scheduled", "device_resident_scheduled", "device_direct_scheduled", "device_persistent_scheduled"):
            phase = result.get(name, {})
            require(phase.get("repeat_output_parity") is True, f"{name}: outputs changed across repeats")
            medians[name] = timing(phase.get("wall_time_ms_samples"), phase.get("wall_time_ms_median"), repeats, name)
        for label, phase in (("custom", "device_resident_scheduled"), ("direct", "device_direct_scheduled"), ("persistent", "device_persistent_scheduled")):
            if medians[phase] is not None and medians["native_scheduled"] is not None:
                require(same_number(result.get(f"{label}_over_native_scheduled_latency_ratio"), medians[phase] / medians["native_scheduled"]), f"{label}: must compare against equally scheduled native execution")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    errors = validate(json.loads(args.report.read_text()))
    print(json.dumps({"report": str(args.report), "status": "failed" if errors else "passed", "errors": errors}, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
