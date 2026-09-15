#!/usr/bin/env python3
"""Independently validate the retained real-model four-workstream handoff."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate(benchmark: dict, pipeline: dict, summary: dict) -> list[str]:
    errors: list[str] = []
    if benchmark.get("schema_version") != "llm-verification-agent-benchmark-v1":
        errors.append("benchmark schema is not the expected real-model schema")
    provenance = benchmark.get("model_provenance")
    if not isinstance(provenance, dict):
        errors.append("benchmark has no real-model provenance")
    else:
        for key, expected in {
            "schema_version": "real-model-runtime-provenance-v1",
            "provider": "google-colab",
            "accelerator": "cuda",
        }.items():
            if provenance.get(key) != expected:
                errors.append(f"benchmark provenance {key} is invalid")
        if not provenance.get("model_id") or not provenance.get("gpu"):
            errors.append("benchmark provenance lacks model or GPU identity")
        if provenance.get("weights_downloaded_in_runtime") is not True:
            errors.append("benchmark does not prove runtime weight download")
    rows = benchmark.get("model_runs", {}).get("local-batch-command", [])
    if len(rows) != 11:
        errors.append("real-model benchmark does not contain 11 batch cases")
    for row in rows:
        if any(row.get(key) != expected for key, expected in {
            "status": "available", "grounded": True, "diagnosis_match": True,
        }.items()):
            errors.append(f"benchmark case {row.get('design_id')} failed quality gates")
        if row.get("adversarial_review", {}).get("accepted") is not True:
            errors.append(f"benchmark case {row.get('design_id')} failed adversarial review")
    metrics = benchmark.get("metrics", {})
    if metrics.get("model_blocked", {}).get("local-batch-command") != 0:
        errors.append("real-model batch contains blocked cases")

    if pipeline.get("schema_version") != "four-workstream-pipeline-v1":
        errors.append("pipeline schema is invalid")
    if pipeline.get("status") != "passed":
        errors.append("integrated pipeline did not pass")
    if pipeline.get("claim_status") not in {"review_required", "evidence_only"}:
        errors.append("pipeline claim status is not fail-closed")
    for key in ("agent", "repair_agent", "assertion_agent"):
        stage = pipeline.get(key, {})
        if stage.get("status") != "available":
            errors.append(f"pipeline {key} is not available")
    if pipeline.get("repair_agent", {}).get("patch_candidate", {}).get("status") != "review_required":
        errors.append("repair candidate is not review-only")
    for key in ("execution", "scheduling", "svm", "protocol"):
        if pipeline.get(key, {}).get("status") != "passed":
            errors.append(f"pipeline {key} did not pass")

    if summary.get("schema_version") != "aimc-llm-agent-colab-run-v1":
        errors.append("Colab summary schema is invalid")
    if summary.get("status") != "passed":
        errors.append("Colab summary is not passed")
    if not summary.get("model_id"):
        errors.append("Colab summary has no model identity")
    if summary.get("benchmark_artifact") == summary.get("full_pipeline_artifact"):
        errors.append("summary does not distinguish benchmark and pipeline artifacts")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark", type=Path)
    parser.add_argument("pipeline", type=Path)
    parser.add_argument("summary", type=Path)
    args = parser.parse_args()
    try:
        benchmark = json.loads(args.benchmark.read_text(encoding="utf-8"))
        pipeline = json.loads(args.pipeline.read_text(encoding="utf-8"))
        summary = json.loads(args.summary.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        result = {"schema_version": "real-four-workstream-colab-check-v1", "status": "blocked", "errors": [str(error)]}
    else:
        errors = validate(benchmark, pipeline, summary)
        result = {
            "schema_version": "real-four-workstream-colab-check-v1",
            "status": "passed" if not errors else "blocked",
            "benchmark": str(args.benchmark),
            "pipeline": str(args.pipeline),
            "summary": str(args.summary),
            "errors": errors,
        }
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
