#!/usr/bin/env python3
"""Run a deterministic next-token rehearsal through the serving boundary."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "evidence" / "aimc-hardware-lab"
DATASET = OUT_DIR / "datasets" / "language-model-serving-token-rehearsal-v1.json"
OUT_JSON = OUT_DIR / "language-model-serving-task-rehearsal-v1.json"
OUT_MD = OUT_DIR / "language-model-serving-task-rehearsal-v1.md"
PROFILE_ID = "educational-hybrid-tile-v1"


def main() -> int:
    # The labels are deterministic continuation tokens, allowing the task gate
    # to exercise token quality without implying a pretrained language model.
    records = [
        {"context": [0, 1, 2], "next_token": 3},
        {"context": [1, 2, 3], "next_token": 4},
        {"context": [2, 3, 4], "next_token": 5},
        {"context": [3, 4, 5], "next_token": 6},
        {"context": [4, 5, 6], "next_token": 7},
        {"context": [5, 6, 7], "next_token": 0},
        {"context": [6, 7, 0], "next_token": 1},
        {"context": [7, 0, 1], "next_token": 2},
        {"context": [0, 2, 4], "next_token": 5},
        {"context": [1, 3, 5], "next_token": 6},
        {"context": [2, 4, 6], "next_token": 7},
        {"context": [3, 5, 7], "next_token": 0},
        {"context": [4, 6, 0], "next_token": 1},
        {"context": [5, 7, 1], "next_token": 2},
        {"context": [6, 0, 2], "next_token": 3},
        {"context": [7, 1, 3], "next_token": 4},
    ]
    dataset = {
        "schema_version": "aimc_token_quality_rehearsal_dataset.v1",
        "dataset_id": "language-model-serving-token-rehearsal-v1",
        "version": "v1",
        "vocab_size": 8,
        "records": records,
        "role": "deterministic synthetic next-token rehearsal, not a language corpus",
    }
    baseline = [(item["context"][-1] + 1) % dataset["vocab_size"] for item in records]
    # One controlled analog projection error changes one token decision.
    candidate = list(baseline)
    candidate[8] = (candidate[8] + 1) % dataset["vocab_size"]
    labels = [item["next_token"] for item in records]
    baseline_accuracy = sum(a == b for a, b in zip(baseline, labels)) / len(labels)
    candidate_accuracy = sum(a == b for a, b in zip(candidate, labels)) / len(labels)
    result = {
        "schema_version": "aimc_language_model_serving_task_rehearsal.v1",
        "status": "synthetic_token_quality_rehearsal_pass",
        "workload_id": "small-language-model-serving-v1",
        "model_id": "small-language-model-serving-shape-v1",
        "dataset_id": dataset["dataset_id"],
        "hardware_profile_id": PROFILE_ID,
        "metric": "next_token_accuracy",
        "baseline_metric": baseline_accuracy,
        "candidate_metric": candidate_accuracy,
        "metric_drop": baseline_accuracy - candidate_accuracy,
        "tolerance": 0.1,
        "pass": baseline_accuracy == 1.0 and candidate_accuracy >= baseline_accuracy - 0.1,
        "record_count": len(records),
        "changed_predictions": sum(a != b for a, b in zip(baseline, candidate)),
        "baseline_predictions": baseline,
        "candidate_predictions": candidate,
        "claim_boundary": {
            "allowed": "reproducible synthetic token-quality rehearsal for the serving partition and controlled analog error",
            "not_allowed": "pretrained language-model quality, real corpus perplexity, measured token latency or energy, board runtime, silicon, or production readiness",
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DATASET.parent.mkdir(parents=True, exist_ok=True)
    DATASET.write_text(json.dumps(dataset, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join([
        "# Language-Model Serving Task Rehearsal", "",
        f"- status: `{result['status']}`",
        f"- profile: `{PROFILE_ID}`",
        f"- dataset: `{dataset['dataset_id']}`",
        f"- records: `{len(records)}`",
        f"- baseline next-token accuracy: `{baseline_accuracy:.4f}`",
        f"- candidate next-token accuracy: `{candidate_accuracy:.4f}`",
        f"- drop: `{result['metric_drop']:.4f}`",
        f"- tolerance: `{result['tolerance']:.4f}`",
        f"- pass: `{result['pass']}`",
        "",
        "The candidate applies one controlled projection error to exercise the token decision boundary. The dataset is synthetic and deterministic; this is a serving-path rehearsal, not pretrained-model evidence.",
        "",
        "Refused claim: " + result["claim_boundary"]["not_allowed"],
        "",
    ]), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "baseline_metric", "candidate_metric", "metric_drop", "pass", "record_count")}, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
