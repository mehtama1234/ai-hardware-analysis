#!/usr/bin/env python3
"""Create deterministic audio samples, extracted features, and a matching ONNX model."""
from __future__ import annotations

import json
import math
import wave
from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "aimc-hardware-lab" / "audio-workload-v1"
MODEL = OUT / "wake-nonwake-mlp.onnx"
DATASET = OUT / "wake-nonwake-features-v1.json"


def features(signal: np.ndarray) -> list[float]:
    signs = np.signbit(signal[:-1]) != np.signbit(signal[1:])
    return [
        float(np.sqrt(np.mean(signal * signal))),
        float(np.mean(signs)),
        float(np.max(np.abs(signal))),
        float(np.var(signal)),
    ]


def write_model() -> None:
    # hidden[0] detects an energetic, low-zero-crossing signal; hidden[1] is reserved.
    w1 = np.asarray([[1.0, 0.0], [-0.3, 0.0], [0.0, 0.0], [0.0, 0.0]], dtype=np.float32)
    b1 = np.asarray([-0.05, 0.0], dtype=np.float32)
    w2 = np.asarray([[1.0, 0.0], [0.0, 0.0]], dtype=np.float32)
    b2 = np.asarray([0.0, 0.1], dtype=np.float32)
    graph = helper.make_graph(
        [
            helper.make_node("MatMul", ["input", "w1"], ["hidden_mm"], name="dense1.matmul"),
            helper.make_node("Add", ["hidden_mm", "b1"], ["hidden_add"], name="dense1.bias"),
            helper.make_node("Relu", ["hidden_add"], ["hidden_relu"], name="dense1.relu"),
            helper.make_node("MatMul", ["hidden_relu", "w2"], ["logits_mm"], name="dense2.matmul"),
            helper.make_node("Add", ["logits_mm", "b2"], ["output"], name="dense2.bias"),
        ],
        "WakeNonwakeMLP",
        [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 4])],
        [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 2])],
        initializer=[
            numpy_helper.from_array(w1, "w1"), numpy_helper.from_array(b1, "b1"),
            numpy_helper.from_array(w2, "w2"), numpy_helper.from_array(b2, "b2"),
        ],
    )
    model = helper.make_model(graph, producer_name="analog-digital-chip-design-eda", opset_imports=[helper.make_opsetid("", 13)])
    onnx.checker.check_model(model)
    onnx.save(model, MODEL)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(17)
    records = []
    for index in range(24):
        label = "wake" if index % 2 == 0 else "nonwake"
        sample_count = 1600
        t = np.arange(sample_count, dtype=np.float32) / 16000.0
        if label == "wake":
            signal = 0.55 * np.sin(2 * math.pi * (440 + (index % 3) * 5) * t)
        elif index % 4 == 1:
            signal = np.zeros(sample_count, dtype=np.float32)
        else:
            signal = rng.normal(0.0, 0.18, sample_count).astype(np.float32)
        signal = np.clip(signal, -1.0, 1.0)
        wav_path = OUT / f"sample-{index:03d}-{label}.wav"
        pcm = (signal * 32767).astype("<i2")
        with wave.open(str(wav_path), "wb") as handle:
            handle.setnchannels(1); handle.setsampwidth(2); handle.setframerate(16000); handle.writeframes(pcm.tobytes())
        records.append({"input_id": f"audio-{index:03d}", "wav_path": str(wav_path), "features": features(signal), "expected_label": label})
    write_model()
    DATASET.write_text(json.dumps({"dataset_id": "wake-nonwake-audio-v1", "dataset_version": "v1", "metric_name": "wake_word_f1", "tolerance": 0.05, "sample_rate_hz": 16000, "records": records}, indent=2) + "\n", encoding="utf-8")
    print(f"model,{MODEL}"); print(f"dataset,{DATASET}"); print(f"samples,{len(records)}")


if __name__ == "__main__":
    main()
