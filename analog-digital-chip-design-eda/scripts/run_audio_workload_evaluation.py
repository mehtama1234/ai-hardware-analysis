#!/usr/bin/env python3
"""Evaluate the generated audio-feature workload with exact and analog-style weights."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import onnx
from onnx import numpy_helper

ROOT = Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "evidence" / "aimc-hardware-lab" / "audio-workload-v1"
MODEL = WORKLOAD / "wake-nonwake-mlp.onnx"
DATASET = WORKLOAD / "wake-nonwake-features-v1.json"
OUT = WORKLOAD / "wake-nonwake-task-evaluation-v1.json"


def quantize(weights: np.ndarray) -> np.ndarray:
    scale = float(np.max(np.abs(weights))) / 3.0
    return np.round(weights / scale) * scale


def infer(x: np.ndarray, w1: np.ndarray, w2: np.ndarray, b1: np.ndarray, b2: np.ndarray) -> np.ndarray:
    return np.maximum(x @ w1 + b1, 0.0) @ w2 + b2


def main() -> None:
    model = onnx.load(MODEL)
    weights = {item.name: numpy_helper.to_array(item).astype(np.float32) for item in model.graph.initializer}
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    rows = []
    for record in dataset["records"]:
        x = np.asarray(record["features"], dtype=np.float32).reshape(1, 4)
        baseline_logits = infer(x, weights["w1"], weights["w2"], weights["b1"], weights["b2"])[0]
        candidate_logits = infer(x, quantize(weights["w1"]), weights["w2"], weights["b1"], weights["b2"])[0]
        baseline = "wake" if int(np.argmax(baseline_logits)) == 0 else "nonwake"
        candidate = "wake" if int(np.argmax(candidate_logits)) == 0 else "nonwake"
        rows.append({"input_id": record["input_id"], "wav_path": record["wav_path"], "expected_label": record["expected_label"], "baseline_prediction": baseline, "candidate_prediction": candidate, "prediction_changed": baseline != candidate, "baseline_logits": baseline_logits.tolist(), "candidate_logits": candidate_logits.tolist()})
    def f1(label: str, key: str) -> float:
        tp = sum(r[key] == label and r["expected_label"] == label for r in rows)
        fp = sum(r[key] == label and r["expected_label"] != label for r in rows)
        fn = sum(r[key] != label and r["expected_label"] == label for r in rows)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        return 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    baseline_f1 = f1("wake", "baseline_prediction")
    candidate_f1 = f1("wake", "candidate_prediction")
    report = {"schema_version": "aimc_task_evaluation.v1", "status": "generated_audio_feature_rehearsal", "model_id": "wake-nonwake-mlp", "model_path": str(MODEL), "dataset_id": dataset["dataset_id"], "dataset_version": dataset["dataset_version"], "metric_name": dataset["metric_name"], "baseline_metric": baseline_f1, "candidate_metric": candidate_f1, "metric_drop": baseline_f1 - candidate_f1, "tolerance": dataset["tolerance"], "pass": baseline_f1 - candidate_f1 <= dataset["tolerance"], "sample_count": len(rows), "false_accepts": sum(r["candidate_prediction"] == "wake" and r["expected_label"] != "wake" for r in rows), "false_rejects": sum(r["candidate_prediction"] != "wake" and r["expected_label"] == "wake" for r in rows), "changed_predictions": sum(r["prediction_changed"] for r in rows), "analog_candidate": "dense1.matmul with symmetric 2-bit weight quantization", "digital_operations": ["feature extraction", "bias", "relu", "dense2.matmul", "decision threshold"], "records": rows, "claim_boundary": "Generated WAV and feature rehearsal only; no field audio, analog silicon, board runtime, power, or thermal measurement."}
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "baseline_metric", "candidate_metric", "metric_drop", "false_accepts", "false_rejects", "pass"]}, indent=2))


if __name__ == "__main__":
    main()
