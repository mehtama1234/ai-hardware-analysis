"""Replay frozen trained MoE weights through two-rank sharded inference."""
import hashlib
import json
from datetime import timedelta
from pathlib import Path
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TRAINED = HERE / "reports/trained-task-cpu.json"
OUT = HERE / "reports/trained-distributed-cpu.json"


def worker(rank, rendezvous, directory):
    import torch
    import torch.distributed as dist
    from moe_routing_all_to_all.distributed import distributed_linear
    torch.set_num_threads(1)
    saved = json.loads(TRAINED.read_text())
    generator = torch.Generator().manual_seed(saved["protocol"]["data_seed"])
    inputs = torch.rand(768, 2, generator=generator) * 2 - 1
    targets = torch.where(inputs[:, :1] >= 0, inputs[:, :1] + inputs[:, 1:],
                          -2 * inputs[:, :1] + 0.5 * inputs[:, 1:])
    identity = hashlib.sha256(inputs.numpy().tobytes() + targets.numpy().tobytes()).hexdigest()
    if identity != saved["data_sha256"]:
        raise ValueError("trained fixture data identity differs")
    test_x, test_y = inputs[512:], targets[512:]
    local_slice = slice(rank * 128, (rank + 1) * 128)
    rows = []
    dist.init_process_group("gloo", init_method=rendezvous, rank=rank, world_size=2,
                            timeout=timedelta(seconds=30))
    try:
        for model in saved["rows"]:
            router = torch.tensor(model["router_weights"], dtype=torch.float32)
            # Construct only this rank's expert weight tensors.
            owned = torch.tensor(model["expert_weights"][rank * 2:(rank + 1) * 2], dtype=torch.float32)
            local_x = test_x[local_slice]
            prediction, accepted = distributed_linear(local_x, local_x @ router, owned,
                                                      top_k=2, capacity=256)
            expected = torch.tensor(model["test_predictions"], dtype=torch.float32)[local_slice]
            torch.testing.assert_close(prediction, expected, atol=2e-6, rtol=2e-5)
            if not accepted.all():
                raise AssertionError("unexpected inference capacity drop")
            rows.append({"seed": model["seed"], "status": "passed", "count": len(local_x),
                         "predictions": prediction.tolist(),
                         "squared_error_sum": (prediction.double() - test_y[local_slice].double()).square().sum().item(),
                         "max_abs_prediction_difference": (prediction - expected).abs().max().item()})
        Path(directory, f"rank-{rank}.json").write_text(json.dumps({"rank": rank, "rows": rows}, allow_nan=False))
    finally:
        dist.destroy_process_group()


def main():
    import torch
    import torch.multiprocessing as mp
    sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
    sys.path.insert(0, str(REPO / "gpu-mode-curriculum/scripts"))
    from common.provenance import source_provenance
    from run_advanced_evidence_regression import check_source_hashes
    report = {"status": "failed", "evidence_kind": "measured_cpu", "rank_reports": [],
              "gpu_execution_accepted": False, "torch_version": torch.__version__,
              "scope": "frozen three-seed trained MoE replay on two CPU/Gloo ranks, 256 previously declared holdout inputs; no retraining, new quality dataset, distributed gradients or performance claim"}
    context = None
    try:
        saved = json.loads(TRAINED.read_text())
        if saved.get("status") != "passed" or check_source_hashes(saved):
            raise ValueError("trained evidence failed or stale; regenerate explicitly")
        initial = hashlib.sha256(TRAINED.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory(prefix="gpu-moe-trained-replay-") as directory:
            context = mp.spawn(worker, args=((Path(directory) / "rendezvous").as_uri(), directory), nprocs=2, join=False)
            deadline = time.monotonic() + 90
            while not context.join(timeout=1):
                if time.monotonic() >= deadline:
                    raise TimeoutError("trained distributed replay exceeded 90 seconds")
            ranks = [json.loads(Path(directory, f"rank-{rank}.json").read_text()) for rank in range(2)]
            for rank, data in enumerate(ranks):
                if data.get("rank") != rank or [row.get("seed") for row in data.get("rows", [])] != [271, 281, 291]:
                    raise ValueError("incomplete rank/seed evidence")
                if any(row.get("status") != "passed" or row.get("count") != 128 for row in data["rows"]):
                    raise ValueError("failed rank output")
            if hashlib.sha256(TRAINED.read_bytes()).hexdigest() != initial:
                raise ValueError("trained artifact changed during replay")
            report.update(status="passed", rank_reports=ranks, trained_artifact_sha256=initial,
                          test_mse_by_seed=[sum(rank["rows"][i]["squared_error_sum"] for rank in ranks) / 256
                                            for i in range(3)])
    except Exception as exc:
        report["error"] = str(exc)
    finally:
        if context is not None:
            for process in context.processes:
                if process.is_alive():
                    process.terminate()
            for process in context.processes:
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=5)
    report["provenance"] = source_provenance(REPO, [Path(__file__), TRAINED,
        HERE / "run_trained_task.py", HERE / "moe_routing_all_to_all/distributed.py",
        HERE / "moe_routing_all_to_all/reference.py"])
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(report["status"], OUT)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
