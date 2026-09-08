"""Fixed synthetic holdout protocol for a learned top-2 linear-expert MoE."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "reports/trained-task-cpu.json"
PROTOCOL = {"data_seed": 270, "model_seeds": [271, 281, 291],
            "train_count": 512, "test_count": 256, "steps": 200,
            "optimizer": "Adam", "learning_rate": 0.03, "experts": 4, "top_k": 2,
            "max_test_mse": 0.1, "max_test_mse_ratio_to_dense_linear": 0.5}


def main():
    import torch
    from moe_routing_all_to_all.reference import routed_linear
    sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
    from common.provenance import source_provenance
    torch.set_num_threads(1)
    generator = torch.Generator().manual_seed(PROTOCOL["data_seed"])
    inputs = torch.rand(768, 2, generator=generator) * 2 - 1
    targets = torch.where(inputs[:, :1] >= 0, inputs[:, :1] + inputs[:, 1:],
                          -2 * inputs[:, :1] + 0.5 * inputs[:, 1:])
    train_x, test_x = inputs[:512], inputs[512:]
    train_y, test_y = targets[:512], targets[512:]
    # Affine least squares baseline, trained only on the training split.
    train_aug = torch.cat([train_x, torch.ones(512, 1)], dim=1)
    test_aug = torch.cat([test_x, torch.ones(256, 1)], dim=1)
    dense_weights = torch.linalg.lstsq(train_aug.double(), train_y.double()).solution
    dense_predictions = test_aug.double() @ dense_weights
    dense_mse = (dense_predictions - test_y.double()).square().mean().item()
    rows = []
    for seed in PROTOCOL["model_seeds"]:
        rng = torch.Generator().manual_seed(seed)
        router = (torch.randn(2, 4, generator=rng) * 0.2).requires_grad_()
        experts = (torch.randn(4, 1, 2, generator=rng) * 0.2).requires_grad_()
        optimizer = torch.optim.Adam([router, experts], lr=PROTOCOL["learning_rate"])
        losses = []
        for _ in range(PROTOCOL["steps"]):
            optimizer.zero_grad(set_to_none=True)
            predicted, _ = routed_linear(train_x, train_x @ router, experts, top_k=2, capacity=512)
            loss = (predicted - train_y).square().mean()
            if not torch.isfinite(loss):
                raise RuntimeError(f"non-finite training loss for seed {seed}")
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
        with torch.no_grad():
            predictions, route = routed_linear(test_x, test_x @ router, experts, top_k=2, capacity=256)
            mse = (predictions.double() - test_y.double()).square().mean().item()
            ratio = mse / dense_mse
            passed = mse <= PROTOCOL["max_test_mse"] and ratio <= PROTOCOL["max_test_mse_ratio_to_dense_linear"]
            rows.append({"seed": seed, "status": "passed" if passed else "failed",
                         "test_mse": mse, "ratio_to_dense_linear": ratio,
                         "train_losses": losses, "test_predictions": predictions.tolist(),
                         "router_weights": router.tolist(), "expert_weights": experts.tolist(),
                         "offered_loads": route["offered_loads"], "dropped_assignments": route["dropped_assignments"]})
    report = {"status": "passed" if all(row["status"] == "passed" for row in rows) else "failed",
              "evidence_kind": "measured_cpu", "gpu_execution_accepted": False,
              "protocol": PROTOCOL, "rows": rows, "torch_version": torch.__version__,
              "data_sha256": hashlib.sha256(inputs.numpy().tobytes() + targets.numpy().tobytes()).hexdigest(),
              "test_targets": test_y.tolist(), "dense_linear_test_mse": dense_mse,
              "dense_linear_weights": dense_weights.tolist(),
              "parameter_counts": {"moe": 16, "dense_affine": 3},
              "scope": "fixed synthetic piecewise-affine regression, shared held-out split, three initialization seeds; top-2 router and linear experts trained jointly; no balancing loss or capacity drops; affine least-squares comparator is not parameter- or compute-matched; no language quality, expert-specialization, speedup or distributed-training claim",
              "provenance": source_provenance(REPO, [Path(__file__)])}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(report["status"], "dense_mse", dense_mse,
          "moe_mse", [row["test_mse"] for row in rows], OUT)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
