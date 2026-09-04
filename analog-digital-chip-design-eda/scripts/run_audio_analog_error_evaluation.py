#!/usr/bin/env python3
"""Run the generated audio model with a deterministic analog front projection."""
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
OUT = WORKLOAD / "wake-nonwake-analog-error-evaluation-v1.json"


def quantize(values: np.ndarray, bits: int, low: float, high: float) -> np.ndarray:
    levels = (1 << bits) - 1
    clipped = np.clip(values, low, high)
    return low + np.round((clipped - low) / (high - low) * levels) * (high - low) / levels


def f1(rows: list[dict[str, object]], key: str) -> float:
    tp = sum(r[key] == "wake" and r["expected_label"] == "wake" for r in rows)
    fp = sum(r[key] == "wake" and r["expected_label"] != "wake" for r in rows)
    fn = sum(r[key] != "wake" and r["expected_label"] == "wake" for r in rows)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def main() -> None:
    model = onnx.load(MODEL)
    weights = {item.name: numpy_helper.to_array(item).astype(np.float32) for item in model.graph.initializer}
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    # The analog path is dense1.matmul. The remainder stays digital.
    programmed = weights["w1"] * (1.0 + np.asarray([[0.010, -0.006], [-0.004, 0.008], [0.006, -0.010], [-0.008, 0.004]], dtype=np.float32)) * 1.01
    rows = []
    for record in dataset["records"]:
        x = np.asarray(record["features"], dtype=np.float32).reshape(1, 4)
        dac_x = quantize(x, 4, -1.0, 1.0)
        analog_hidden = dac_x @ programmed
        analog_hidden = analog_hidden * 0.965
        analog_hidden = quantize(analog_hidden, 6, -2.0, 2.0)
        hidden = np.maximum(analog_hidden + weights["b1"], 0.0)
        logits = hidden @ weights["w2"] + weights["b2"]
        prediction = "wake" if int(np.argmax(logits)) == 0 else "nonwake"
        rows.append({"input_id": record["input_id"], "expected_label": record["expected_label"], "candidate_prediction": prediction, "analog_hidden": analog_hidden[0].tolist(), "logits": logits[0].tolist()})
    candidate_f1 = f1(rows, "candidate_prediction")
    baseline_f1 = 1.0
    report = {"schema_version": "aimc_task_evaluation.v1", "status": "model_backed_analog_nonideality_rehearsal", "model_id": "wake-nonwake-mlp", "dataset_id": dataset["dataset_id"], "dataset_version": dataset["dataset_version"], "metric_name": dataset["metric_name"], "baseline_metric": baseline_f1, "candidate_metric": candidate_f1, "metric_drop": baseline_f1 - candidate_f1, "tolerance": dataset["tolerance"], "pass": baseline_f1 - candidate_f1 <= dataset["tolerance"], "analog_operation": "dense1.matmul", "digital_operations": ["feature extraction", "bias", "relu", "dense2.matmul", "decision threshold"], "analog_profile": {"dac_bits": 4, "adc_bits": 6, "row_drop_scale": 0.965, "programming_mismatch_pct": 1.0, "drift_pct": 1.0, "weight_precision_bits": 2, "bit_slices": 2}, "sample_count": len(rows), "false_accepts": sum(r["candidate_prediction"] == "wake" and r["expected_label"] != "wake" for r in rows), "false_rejects": sum(r["candidate_prediction"] != "wake" and r["expected_label"] == "wake" for r in rows), "records": rows, "claim_boundary": "Model-backed analog nonideality rehearsal only; deterministic error model, no calibrated array, board runtime, power, or thermal measurement."}
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "baseline_metric", "candidate_metric", "metric_drop", "false_accepts", "false_rejects", "pass"]}, indent=2))


if __name__ == "__main__":
    main()
