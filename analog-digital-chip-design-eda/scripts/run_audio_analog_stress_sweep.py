#!/usr/bin/env python3
"""Sweep analog error conditions and record task quality plus governor decisions."""
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
OUT = WORKLOAD / "wake-nonwake-analog-stress-sweep-v1.json"
PY_DIR = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "python"
import sys
sys.path.insert(0, str(PY_DIR))
from error_budget_governor_trace import govern  # noqa: E402


def quantize(values: np.ndarray, bits: int, low: float, high: float) -> np.ndarray:
    levels = (1 << bits) - 1
    clipped = np.clip(values, low, high)
    return low + np.round((clipped - low) / (high - low) * levels) * (high - low) / levels


def f1(rows: list[dict[str, object]]) -> float:
    tp = sum(r["prediction"] == "wake" and r["expected"] == "wake" for r in rows)
    fp = sum(r["prediction"] == "wake" and r["expected"] != "wake" for r in rows)
    fn = sum(r["prediction"] != "wake" and r["expected"] == "wake" for r in rows)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def run_case(name: str, weights: dict[str, np.ndarray], records: list[dict[str, object]], profile: dict[str, float]) -> dict[str, object]:
    programmed = weights["w1"] * (1.0 + profile["mismatch"] * np.asarray([[1.0, -0.6], [-0.4, 0.8], [0.6, -1.0], [-0.8, 0.4]], dtype=np.float32)) * (1.0 + profile["drift"])
    rows = []
    for record in records:
        x = np.asarray(record["features"], dtype=np.float32).reshape(1, 4)
        analog_hidden = quantize(x, int(profile["dac_bits"]), -1.0, 1.0) @ programmed
        analog_hidden = analog_hidden * profile["row_scale"]
        analog_hidden = quantize(analog_hidden, int(profile["adc_bits"]), -2.0, 2.0)
        hidden = np.maximum(analog_hidden + weights["b1"], 0.0)
        logits = hidden @ weights["w2"] + weights["b2"]
        rows.append({"expected": record["expected_label"], "prediction": "wake" if int(np.argmax(logits)) == 0 else "nonwake"})
    score = f1(rows)
    drop = 1.0 - score
    residual_q8 = max(0, min(255, round(drop * 255)))
    decision, action, reason, next_error = govern(1, 1, residual_q8, int(profile["drift_age"]), 224 if drop > 0 else 96, 0)
    return {"case": name, "profile": profile, "f1": score, "metric_drop": drop, "false_accepts": sum(r["prediction"] == "wake" and r["expected"] != "wake" for r in rows), "false_rejects": sum(r["prediction"] != "wake" and r["expected"] == "wake" for r in rows), "residual_q8": residual_q8, "governor_decision": decision, "governor_action": action, "governor_reason": reason, "next_cumulative_error_q8": next_error}


def main() -> None:
    model = onnx.load(MODEL)
    weights = {item.name: numpy_helper.to_array(item).astype(np.float32) for item in model.graph.initializer}
    records = json.loads(DATASET.read_text(encoding="utf-8"))["records"]
    profiles = [
        ("nominal", {"dac_bits": 4, "adc_bits": 6, "row_scale": 0.965, "mismatch": 0.01, "drift": 0.01, "drift_age": 1}),
        ("low_adc", {"dac_bits": 4, "adc_bits": 3, "row_scale": 0.965, "mismatch": 0.01, "drift": 0.01, "drift_age": 1}),
        ("high_row_drop", {"dac_bits": 4, "adc_bits": 6, "row_scale": 0.78, "mismatch": 0.01, "drift": 0.01, "drift_age": 1}),
        ("stale_drift", {"dac_bits": 4, "adc_bits": 6, "row_scale": 0.965, "mismatch": 0.03, "drift": 0.08, "drift_age": 12}),
        ("severe_combined", {"dac_bits": 3, "adc_bits": 3, "row_scale": 0.60, "mismatch": 0.08, "drift": 0.12, "drift_age": 12}),
    ]
    cases = [run_case(name, weights, records, profile) for name, profile in profiles]
    report = {"schema_version": "aimc_analog_stress_sweep.v1", "status": "model_backed_analog_stress_sweep", "model_id": "wake-nonwake-mlp", "dataset_id": "wake-nonwake-audio-v1", "cases": cases, "claim_boundary": "Stress sensitivity of a deterministic model-backed error model; not calibrated silicon, field audio, board runtime, power, or thermal evidence."}
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for case in cases:
        print(f"{case['case']}: f1={case['f1']:.4f} drop={case['metric_drop']:.4f} false_accepts={case['false_accepts']} false_rejects={case['false_rejects']} governor={case['governor_reason']}")


if __name__ == "__main__":
    main()
