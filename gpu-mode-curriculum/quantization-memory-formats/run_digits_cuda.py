#!/usr/bin/env python3
"""Run the fixed trained-digits quality protocol on CUDA."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LOCAL_LAB = ROOT.parent / "gpu-kernels-serving-lab"
ARCHIVE_LAB = ROOT / "gpu-kernels-serving-lab"
LAB_ROOT = LOCAL_LAB if LOCAL_LAB.is_dir() else ARCHIVE_LAB
LAB = LAB_ROOT / "08-quantized-inference"
COMMON = LAB_ROOT
if not LAB.is_dir():
    raise FileNotFoundError(f"quantized inference lab not found at {LAB}")
sys.path.insert(0, str(LAB))
sys.path.insert(0, str(COMMON))
from common.packed_linear import converted_copy, tensor_storage_bytes  # noqa: E402


OUT = HERE / "reports" / "digits-quality-cuda.json"
PROTOCOL = {"split_seed": 142, "model_seed": 141, "training_steps": 150, "optimizer": "Adam", "learning_rate": 0.01, "block": 32, "minimum_fp32_accuracy": 0.90, "maximum_accuracy_drop": 0.02}
SEED_PAIRS = ((141, 142), (171, 172), (201, 202))


def split_indices(labels, seed=142):
    generator = torch.Generator().manual_seed(seed)
    train, test = [], []
    for label in torch.unique(labels, sorted=True):
        indices = torch.where(labels == label)[0]
        indices = indices[torch.randperm(indices.numel(), generator=generator)]
        boundary = int(0.8 * indices.numel())
        train.extend(indices[:boundary].tolist())
        test.extend(indices[boundary:].tolist())
    return torch.tensor(train), torch.tensor(test)


def event_samples(fn):
    values = []
    for _ in range(7):
        start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        start.record()
        fn()
        end.record()
        end.synchronize()
        values.append(float(start.elapsed_time(end)))
    return values


def run_case(x, y, targets_cpu, data, *, model_seed, split_seed):
    train_cpu, test_cpu = split_indices(targets_cpu, split_seed)
    train, test = train_cpu.to("cuda"), test_cpu.to("cuda")
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(model_seed)
        model = torch.nn.Sequential(torch.nn.Linear(64, 64), torch.nn.ReLU(), torch.nn.Linear(64, 10)).cuda()
    optimizer = torch.optim.Adam(model.parameters(), lr=PROTOCOL["learning_rate"])
    losses = []
    for _ in range(PROTOCOL["training_steps"]):
        optimizer.zero_grad(set_to_none=True)
        loss = torch.nn.functional.cross_entropy(model(x[train]), y[train])
        loss.backward()
        optimizer.step()
        losses.append(float(loss.item()))
    model.eval()
    packed = converted_copy(model, PROTOCOL["block"]).cuda()
    rows = []
    with torch.no_grad():
        for name, candidate in (("fp32", model), ("packed_int4", packed)):
            logits = candidate(x[test])
            predictions = logits.argmax(dim=1)
            rows.append({"name": name, "accuracy": float((predictions == y[test]).float().mean().item()), "correct_count": int((predictions == y[test]).sum().item()), "cross_entropy": float(torch.nn.functional.cross_entropy(logits, y[test]).item()), "tensor_storage_bytes": tensor_storage_bytes(candidate), "samples_ms": event_samples(lambda: candidate(x[test])), "device": str(x.device)})
    checks = {"baseline_accuracy": rows[0]["accuracy"] >= PROTOCOL["minimum_fp32_accuracy"], "accuracy_drop": rows[0]["accuracy"] - rows[1]["accuracy"] <= PROTOCOL["maximum_accuracy_drop"], "storage_reduced": rows[1]["tensor_storage_bytes"] < rows[0]["tensor_storage_bytes"]}
    return {"protocol": dict(PROTOCOL, model_seed=model_seed, split_seed=split_seed), "checks": checks, "status": "task_gate_passed" if all(checks.values()) else "task_gate_failed", "rows": rows, "training_losses": losses, "dataset": {"train_count": len(train_cpu), "test_count": len(test_cpu)}}


def main() -> int:
    report = {"project": "quantization-memory-formats", "experiment": "trained-digits-cuda", "generated_at": datetime.now(timezone.utc).isoformat(), "gpu_execution_accepted": False, "measured": False, "protocol": PROTOCOL, "seed_pairs": SEED_PAIRS}
    if not torch.cuda.is_available():
        report.update({"status": "unavailable:cuda-runtime", "reason": "CUDA is not available"})
    else:
        import sklearn
        from sklearn.datasets import load_digits

        data, targets = load_digits(return_X_y=True)
        x = torch.tensor(data, dtype=torch.float32, device="cuda") / 16.0
        y = torch.tensor(targets, dtype=torch.long, device="cuda")
        targets_cpu = torch.tensor(targets)
        cases = [run_case(x, y, targets_cpu, data, model_seed=model_seed, split_seed=split_seed) for model_seed, split_seed in SEED_PAIRS]
        passed = all(case["status"] == "task_gate_passed" for case in cases)
        report.update({"status": "task_gate_passed" if passed else "task_gate_failed", "gpu_execution_accepted": passed, "measured": True, "device_name": torch.cuda.get_device_name(0), "torch_version": torch.__version__, "sklearn_version": sklearn.__version__, "dataset": {"name": "sklearn bundled digits", "data_sha256": hashlib.sha256(data.tobytes() + targets.tobytes()).hexdigest()}, "cases": cases, "scope": "three predeclared model/split seed pairs on one CUDA device; held-out quality and packed INT4 storage with FP32 unpacked compute; no native INT4 GEMM or LLM-quality claim"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2))
    return 0 if report["gpu_execution_accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
