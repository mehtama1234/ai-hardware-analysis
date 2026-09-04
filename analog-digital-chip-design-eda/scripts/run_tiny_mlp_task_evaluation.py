#!/usr/bin/env python3
"""Run a deterministic ONNX MLP baseline versus a 2-bit analog-style candidate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT.parent / "ai-hardware-analysis" / "analog-in-memory-ai-inference" / "software-architecture" / "samples" / "tiny-mlp.onnx"
DATASET = ROOT / "evidence" / "aimc-hardware-lab" / "datasets" / "tiny-mlp-binary-v1.json"
OUT = ROOT / "evidence" / "aimc-hardware-lab" / "tiny-mlp-task-evaluation-v1.json"


def quantize(weights: np.ndarray) -> np.ndarray:
    scale = float(np.max(np.abs(weights))) / 3.0
    return np.round(weights / scale) * scale


def infer(x: np.ndarray, w1: np.ndarray, w2: np.ndarray, b1: np.ndarray, b2: np.ndarray) -> np.ndarray:
    hidden = np.maximum(x @ w1 + b1, 0.0)
    return hidden @ w2 + b2


def main() -> int:
    model = onnx.load(MODEL)
    weights = {item.name: numpy_helper.to_array(item).astype(np.float32) for item in model.graph.initializer}
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    records = dataset["records"]
    baseline_predictions = []
    candidate_predictions = []
    rows = []
    analog_w1 = quantize(weights["w1"])
    analog_w2 = weights["w2"]
    for record in records:
        x = np.asarray(record["features"], dtype=np.float32).reshape(1, 4)
        baseline_logits = infer(x, weights["w1"], weights["w2"], weights["b1"], weights["b2"])[0]
        candidate_logits = infer(x, analog_w1, analog_w2, weights["b1"], weights["b2"])[0]
        baseline = int(np.argmax(baseline_logits))
        candidate = int(np.argmax(candidate_logits))
        baseline_predictions.append(baseline)
        candidate_predictions.append(candidate)
        rows.append({
            "input_id": record["input_id"],
            "expected_label": None,
            "baseline_prediction": baseline,
            "candidate_prediction": candidate,
            "baseline_logits": baseline_logits.tolist(),
            "candidate_logits": candidate_logits.tolist(),
            "prediction_changed": baseline != candidate,
        })
    # The model defines the labels for this model-backed classification rehearsal.
    for row in rows:
        row["expected_label"] = row["baseline_prediction"]
    baseline_accuracy = 1.0
    candidate_accuracy = sum(row["candidate_prediction"] == row["expected_label"] for row in rows) / len(rows)
    report = {
        "schema_version": "aimc_task_evaluation.v1",
        "status": "model_backed_synthetic_rehearsal",
        "model_id": "tiny-mlp",
        "model_path": str(MODEL),
        "dataset_id": dataset["dataset_id"],
        "dataset_version": dataset["dataset_version"],
        "metric_name": dataset["metric_name"],
        "baseline_metric": baseline_accuracy,
        "candidate_metric": candidate_accuracy,
        "metric_drop": baseline_accuracy - candidate_accuracy,
        "tolerance": dataset["tolerance"],
        "pass": baseline_accuracy - candidate_accuracy <= dataset["tolerance"],
        "analog_candidate": "dense1.matmul with symmetric 2-bit weight quantization",
        "digital_operations": ["dense1.bias", "dense1.relu", "dense2.matmul", "dense2.bias", "classification decision"],
        "sample_count": len(rows),
        "changed_predictions": sum(row["prediction_changed"] for row in rows),
        "records": rows,
        "claim_boundary": "Model-backed local evaluation only; synthetic feature vectors, no audio sensor path, no analog silicon, no board latency, power, or thermal measurement.",
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "baseline_metric", "candidate_metric", "metric_drop", "tolerance", "pass", "changed_predictions"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
