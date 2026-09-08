"""Fixed-protocol trained digits MLP, held-out INT4 quality/storage/latency."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from common.bench import sample_seconds
from common.packed_linear import converted_copy, tensor_storage_bytes
from common.provenance import source_provenance

# Fixed before observing the held-out results; not selected by the runner.
PROTOCOL = {"split_seed": 142, "model_seed": 141, "training_steps": 150,
            "optimizer": "Adam", "learning_rate": 0.01, "block": 32,
            "minimum_fp32_accuracy": 0.90, "maximum_accuracy_drop": 0.02}


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


def quality_gate(fp32, packed, fp32_bytes, packed_bytes):
    return {"baseline_accuracy": fp32 >= PROTOCOL["minimum_fp32_accuracy"],
            "accuracy_drop": fp32 - packed <= PROTOCOL["maximum_accuracy_drop"],
            "storage_reduced": packed_bytes < fp32_bytes}


def run_case(*, split_seed=142, model_seed=141):
    protocol = dict(PROTOCOL, split_seed=split_seed, model_seed=model_seed)
    import sklearn
    from sklearn.datasets import load_digits
    data, targets = load_digits(return_X_y=True)  # packaged data; no network fetch
    x = torch.tensor(data, dtype=torch.float32) / 16.0
    y = torch.tensor(targets, dtype=torch.long)
    train, test = split_indices(y, protocol["split_seed"])
    assert not set(train.tolist()) & set(test.tolist())
    assert sorted(train.tolist() + test.tolist()) == list(range(len(y)))
    threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(protocol["model_seed"])
            model = torch.nn.Sequential(torch.nn.Linear(64, 64), torch.nn.ReLU(), torch.nn.Linear(64, 10))
        optimizer = torch.optim.Adam(model.parameters(), lr=PROTOCOL["learning_rate"])
        losses = []
        train_x, train_y = x[train], y[train]
        for _ in range(PROTOCOL["training_steps"]):
            optimizer.zero_grad(set_to_none=True)
            loss = torch.nn.functional.cross_entropy(model(train_x), train_y)
            loss.backward()
            optimizer.step()
            losses.append(float(loss.item()))
        model.eval()
        packed = converted_copy(model, PROTOCOL["block"])
        # No held-out features/labels enter training or weight-only packing.
        test_x, test_y = x[test], y[test]
        rows = []
        with torch.no_grad():
            for name, candidate in (("fp32", model), ("packed_int4", packed)):
                logits = candidate(test_x)
                if not bool(torch.isfinite(logits).all()):
                    raise AssertionError("nonfinite evaluation logits")
                predictions = logits.argmax(dim=1)
                rows.append({"name": name, "accuracy": float((predictions == test_y).float().mean()),
                    "correct_count": int((predictions == test_y).sum()),
                    "cross_entropy": float(torch.nn.functional.cross_entropy(logits, test_y)),
                    "predictions": predictions.tolist(), "tensor_storage_bytes": tensor_storage_bytes(candidate),
                    "batch_samples_seconds": sample_seconds(lambda: candidate(test_x), 2, 7)})
        checks = quality_gate(rows[0]["accuracy"], rows[1]["accuracy"], rows[0]["tensor_storage_bytes"], rows[1]["tensor_storage_bytes"])
        state_hash = hashlib.sha256(b"".join(value.detach().contiguous().numpy().tobytes() for value in model.state_dict().values())).hexdigest()
        report = {"timestamp": datetime.now(timezone.utc).isoformat(), "protocol": protocol, "checks": checks,
            "status": "task_gate_passed" if all(checks.values()) else "task_gate_failed", "rows": rows,
            "training_losses": losses, "trained_fp32_state_sha256": state_hash,
            "dataset": {"name": "sklearn bundled digits", "source": "https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html",
                "data_sha256": hashlib.sha256(data.tobytes() + targets.tobytes()).hexdigest(),
                "normalization": "fixed pixel /16; no fitted preprocessing", "train_indices": train.tolist(),
                "test_indices": test.tolist(), "test_labels": test_y.tolist(), "train_count": len(train), "test_count": len(test)},
            "versions": {"torch": torch.__version__, "sklearn": sklearn.__version__},
            "cpu_threads": 1, "warmup": 2, "repeat": 7, "evidence_kind": "measured_cpu",
            "scope": "one fixed split/model seed of a small real digits classification task; not LLM quality or cross-seed confidence; weight-only packed storage with FP32 unpacked compute",
            "gpu_execution_accepted": False,
            "provenance": source_provenance(ROOT.parent, [Path(__file__), ROOT / "common/packed_int4.py",
                ROOT / "common/packed_linear.py", ROOT / "common/bench.py", ROOT / "common/provenance.py"])}
    finally:
        torch.set_num_threads(threads)
    return report


def main():
    report = run_case()
    (HERE / "out_digits_quality.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(report["status"], "train", report["dataset"]["train_count"], "test", report["dataset"]["test_count"])
    for row in report["rows"]:
        print(row["name"], row["accuracy"], row["tensor_storage_bytes"], "bytes")
    return 0 if all(report["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
