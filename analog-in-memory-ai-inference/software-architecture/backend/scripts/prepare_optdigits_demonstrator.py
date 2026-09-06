#!/usr/bin/env python3
"""Acquire a real task and train its preregistered baseline without scoring test data."""
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import urllib.request

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper
from onnx.reference import ReferenceEvaluator

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/optdigits-v1"


def main():
    contract_bytes = (EXPERIMENT / "contract.json").read_bytes()
    contract = json.loads(contract_bytes)
    output = EXPERIMENT / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    (output / "contract.json").write_bytes(contract_bytes)
    dataset = contract["dataset"]
    hashes = {}
    locked = json.loads((EXPERIMENT / "dataset-lock.json").read_text())
    for name in (dataset["train_file"], dataset["test_file"]):
        with urllib.request.urlopen(dataset["download_base"] + name, timeout=30) as response:
            data = response.read(2_000_000)
        (output / name).write_bytes(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
        if hashes[name] != locked[name]:
            raise ValueError(f"Dataset content changed: {name}")
    # Only official training data is parsed or scored here. Test bytes are
    # archived and hashed to bind the future evaluation population.
    raw = np.loadtxt(io.BytesIO((output / dataset["train_file"]).read_bytes()), delimiter=",")
    if raw.shape != (dataset["train_rows"], 65) or not np.isfinite(raw).all():
        raise ValueError("Unexpected official training data shape or values")
    if not np.equal(raw, np.floor(raw)).all() or raw[:, :64].min() < 0 or raw[:, :64].max() > 16 or raw[:, 64].min() < 0 or raw[:, 64].max() > 9:
        raise ValueError("Training feature/label range changed")
    x, y = raw[:, :64] / 16, raw[:, 64].astype(int)
    rng = np.random.default_rng(dataset["split_seed"])
    train, calibration = [], []
    for label in range(10):
        ids = rng.permutation(np.flatnonzero(y == label))
        count = len(ids) // 5
        calibration.extend(ids[:count].tolist())
        train.extend(ids[count:].tolist())
    if set(train) & set(calibration) or len(train) + len(calibration) != len(raw):
        raise ValueError("Invalid train/calibration split")
    (output / "split.json").write_text(json.dumps({"train": train, "calibration": calibration}) + "\n")
    rng = np.random.default_rng(contract["model"]["initialization_seed"])
    weights = [rng.normal(0, np.sqrt(2 / 64), (64, 32)), np.zeros(32), rng.normal(0, np.sqrt(2 / 32), (32, 10)), np.zeros(10)]
    m, v = [np.zeros_like(w) for w in weights], [np.zeros_like(w) for w in weights]
    settings = contract["model"]["training"]
    step = 0
    for epoch in range(settings["epochs"]):
        ids = rng.permutation(train)
        for start in range(0, len(ids), settings["batch_size"]):
            batch = ids[start:start + settings["batch_size"]]
            a = x[batch] @ weights[0] + weights[1]
            h = np.maximum(a, 0)
            z = h @ weights[2] + weights[3]
            p = np.exp(z - z.max(axis=1, keepdims=True))
            p /= p.sum(axis=1, keepdims=True)
            p[np.arange(len(batch)), y[batch]] -= 1
            p /= len(batch)
            da = (p @ weights[2].T) * (a > 0)
            grads = [x[batch].T @ da, da.sum(axis=0), h.T @ p, p.sum(axis=0)]
            step += 1
            for i, grad in enumerate(grads):
                m[i] = settings["beta1"] * m[i] + (1 - settings["beta1"]) * grad
                v[i] = settings["beta2"] * v[i] + (1 - settings["beta2"]) * grad * grad
                weights[i] -= settings["learning_rate"] * (m[i] / (1 - settings["beta1"] ** step)) / (np.sqrt(v[i] / (1 - settings["beta2"] ** step)) + settings["epsilon"])
    weights = [w.astype(np.float32) for w in weights]
    names = ["w1", "b1", "w2", "b2"]
    nodes = [helper.make_node("MatMul", ["input", "w1"], ["mm1"], name="input_projection"), helper.make_node("Add", ["mm1", "b1"], ["a1"]), helper.make_node("Relu", ["a1"], ["h1"]), helper.make_node("MatMul", ["h1", "w2"], ["mm2"], name="output_projection"), helper.make_node("Add", ["mm2", "b2"], ["logits"])]
    graph = helper.make_graph(nodes, contract["workload_id"], [helper.make_tensor_value_info("input", TensorProto.FLOAT, [None, 64])], [helper.make_tensor_value_info("logits", TensorProto.FLOAT, [None, 10])], [numpy_helper.from_array(w, name) for name, w in zip(names, weights)])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)], ir_version=8)
    onnx.checker.check_model(model)
    onnx.save(model, output / "model.onnx")
    cx = x[calibration].astype(np.float32)
    expected = np.maximum(cx @ weights[0] + weights[1], 0) @ weights[2] + weights[3]
    actual = ReferenceEvaluator(model).run(None, {"input": cx})[0]
    np.testing.assert_allclose(actual, expected, rtol=1e-5, atol=1e-5)
    result = {"status": "real_task_baseline_prepared_test_unscored", "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(), "dataset_sha256": hashes, "model_sha256": hashlib.sha256((output / "model.onnx").read_bytes()).hexdigest(), "train_rows": len(train), "calibration_rows": len(calibration), "calibration_accuracy": float(np.mean(actual.argmax(axis=1) == y[calibration])), "test_evaluated": False, "onnx_numpy_max_difference": float(np.max(np.abs(actual - expected))), "numpy_version": np.__version__, "onnx_version": onnx.__version__, "accepted_hardware": False}
    result["training_script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["split_sha256"] = hashlib.sha256((output / "split.json").read_bytes()).hexdigest()
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    print(output)


if __name__ == "__main__":
    main()
