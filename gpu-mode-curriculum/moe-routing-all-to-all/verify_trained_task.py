"""Independent saved-array checks for the fixed trained MoE task report."""
import hashlib
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def column(values, count):
    if not isinstance(values, list) or len(values) != count or any(
        not isinstance(row, list) or len(row) != 1 or not finite(row[0]) for row in values
    ):
        raise ValueError("expected finite scalar column with declared count")
    return [row[0] for row in values]


def validate(report):
    from run_trained_task import PROTOCOL
    if report.get("protocol") != PROTOCOL:
        raise ValueError("protocol differs from the predeclared experiment")
    if report.get("status") != "passed" or report.get("gpu_execution_accepted") is not False:
        raise ValueError("invalid report acceptance or hardware claim")
    targets = column(report.get("test_targets"), PROTOCOL["test_count"])
    baseline = report.get("dense_linear_test_mse")
    if not finite(baseline) or baseline <= 0:
        raise ValueError("invalid baseline MSE")
    rows = report.get("rows", [])
    if [row.get("seed") for row in rows] != PROTOCOL["model_seeds"]:
        raise ValueError("missing, repeated or reordered seed result")
    for row in rows:
        predictions = column(row.get("test_predictions"), len(targets))
        mse = math.fsum((prediction - target) ** 2 for prediction, target in zip(predictions, targets)) / len(targets)
        ratio = mse / baseline
        for name, actual in (("test_mse", mse), ("ratio_to_dense_linear", ratio)):
            stored = row.get(name)
            if not finite(stored) or not math.isclose(stored, actual, rel_tol=1e-10, abs_tol=1e-12):
                raise ValueError(f"stored {name} disagrees with predictions")
        losses = row.get("train_losses", [])
        if len(losses) != PROTOCOL["steps"] or any(not finite(loss) or loss < 0 for loss in losses):
            raise ValueError("invalid training trace")
        if row.get("status") != "passed" or mse > PROTOCOL["max_test_mse"] or ratio > PROTOCOL["max_test_mse_ratio_to_dense_linear"]:
            raise ValueError("quality gates failed")
        loads = row.get("offered_loads", [])
        if len(loads) != PROTOCOL["experts"] or any(type(load) is not int or load < 0 for load in loads) or sum(loads) != len(targets) * PROTOCOL["top_k"]:
            raise ValueError("invalid assignment counts")
        if type(row.get("dropped_assignments")) is not int or row["dropped_assignments"] != 0:
            raise ValueError("unexpected capacity drops")


def replay(report):
    """Check actual saved weights and independently refit the training baseline."""
    import torch
    from moe_routing_all_to_all.reference import routed_linear
    torch.set_num_threads(1)
    generator = torch.Generator().manual_seed(report["protocol"]["data_seed"])
    inputs = torch.rand(768, 2, generator=generator) * 2 - 1
    targets = torch.where(inputs[:, :1] >= 0, inputs[:, :1] + inputs[:, 1:],
                          -2 * inputs[:, :1] + 0.5 * inputs[:, 1:])
    identity = hashlib.sha256(inputs.numpy().tobytes() + targets.numpy().tobytes()).hexdigest()
    if identity != report.get("data_sha256"):
        raise ValueError("regenerated data identity differs")
    torch.testing.assert_close(torch.tensor(report["test_targets"]), targets[512:], atol=0, rtol=0)
    augmented = torch.cat([inputs.double(), torch.ones(768, 1, dtype=torch.float64)], dim=1)
    fitted = torch.linalg.lstsq(augmented[:512], targets[:512].double()).solution
    stored = torch.tensor(report["dense_linear_weights"], dtype=torch.float64)
    torch.testing.assert_close(stored, fitted, atol=1e-10, rtol=1e-10)
    baseline_mse = (augmented[512:] @ fitted - targets[512:].double()).square().mean().item()
    if not math.isclose(baseline_mse, report["dense_linear_test_mse"], rel_tol=1e-10, abs_tol=1e-12):
        raise ValueError("baseline MSE disagrees with independent fit")
    with torch.no_grad():
        for row in report["rows"]:
            router = torch.tensor(row["router_weights"], dtype=torch.float32)
            experts = torch.tensor(row["expert_weights"], dtype=torch.float32)
            predicted, route = routed_linear(inputs[512:], inputs[512:] @ router, experts,
                                             top_k=2, capacity=256)
            torch.testing.assert_close(predicted, torch.tensor(row["test_predictions"]), atol=2e-6, rtol=2e-5)
            if route["offered_loads"] != row["offered_loads"]:
                raise ValueError("saved expert loads disagree with weight replay")


if __name__ == "__main__":
    sys.path.insert(0, str(HERE.parents[1] / "gpu-mode-curriculum/scripts"))
    from run_advanced_evidence_regression import check_source_hashes
    report = json.loads((HERE / "reports/trained-task-cpu.json").read_text())
    validate(report)
    errors = check_source_hashes(report)
    if errors:
        raise ValueError(errors)
    replay(report)
    print("trained report arrays, protocol, quality gates, source hashes, saved weights and independent baseline fit verified")
