"""Execute two-rank expert dispatch/compute/return against the CPU oracle."""
from datetime import timedelta
import json
from pathlib import Path
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "reports/distributed-reference-cpu.json"


def worker(rank, rendezvous, directory):
    import torch
    import torch.distributed as dist
    from moe_routing_all_to_all.reference import routed_linear
    from moe_routing_all_to_all.distributed import distributed_linear
    torch.set_num_threads(1)
    dist.init_process_group("gloo", init_method=rendezvous, rank=rank, world_size=2,
                            timeout=timedelta(seconds=30))
    rows = []
    rejection_checks = []
    try:
        for invalid_case in ("capacity-mismatch", "rank-one-nan"):
            x = torch.ones(2, 3)
            logits = torch.ones(2, 4)
            weights = torch.ones(2, 2, 3)
            if invalid_case == "rank-one-nan" and rank == 1:
                logits[0, 0] = float("nan")
            capacity = rank + 1 if invalid_case == "capacity-mismatch" else 2
            try:
                distributed_linear(x, logits, weights, top_k=2, capacity=capacity)
            except ValueError as exc:
                rejection_checks.append({"case": invalid_case, "status": "rejected", "reason": str(exc)})
            else:
                raise AssertionError(f"{invalid_case} was accepted")
            dist.barrier()  # Both ranks rejected and the process group is usable.
        for dtype in (torch.float32, torch.float64):
            for case, capacity, counts in (("balanced", 6, (3, 3)), ("skewed", 2, (3, 3)),
                                           ("ties", 1, (3, 3)), ("all-dropped", 0, (3, 3)),
                                           ("uneven", 2, (1, 5)), ("empty-source", 2, (0, 6))):
                rng = torch.Generator().manual_seed(251)
                tokens = torch.randn(6, 3, generator=rng, dtype=dtype)
                logits = torch.randn(6, 4, generator=rng, dtype=dtype)
                weights = torch.randn(4, 2, 3, generator=rng, dtype=dtype)
                if case == "skewed":
                    logits[:, :2] += 20
                elif case == "ties":
                    logits.zero_()
                local_slice = slice(sum(counts[:rank]), sum(counts[:rank + 1]))
                # Production candidate receives only the locally owned weights.
                output, accepted = distributed_linear(tokens[local_slice], logits[local_slice],
                    weights[rank * 2:(rank + 1) * 2].clone(), top_k=2, capacity=capacity)
                expected, route = routed_linear(tokens, logits, weights, top_k=2, capacity=capacity)
                torch.testing.assert_close(output, expected[local_slice], atol=2e-6, rtol=2e-5)
                if not torch.equal(accepted, route["accepted"][local_slice]):
                    raise AssertionError("global capacity acceptance differs")
                rows.append({"case": case, "dtype": str(dtype), "capacity": capacity,
                             "local_token_count": counts[rank], "source_token_counts": list(counts),
                             "status": "passed", "max_abs_error": (output - expected[local_slice]).abs().max().item() if output.numel() else 0.0,
                             "output": output.tolist(), "expected": expected[local_slice].tolist(),
                             "accepted": accepted.tolist()})
        Path(directory, f"rank-{rank}.json").write_text(json.dumps({"rank": rank, "rows": rows,
            "rejection_checks": rejection_checks}, allow_nan=False))
    finally:
        dist.destroy_process_group()


def main():
    import torch
    import torch.multiprocessing as mp
    sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
    from common.provenance import source_provenance
    report = {"status": "failed", "evidence_kind": "measured_cpu", "backend": "gloo",
              "world_size": 2, "torch_version": torch.__version__, "rank_reports": [],
              "gpu_execution_accepted": False,
              "scope": "two local CPU ranks, sharded linear experts, padded forward/return all-to-all and global rank-ordered capacity; inference correctness only, no timing/gradient/GPU acceptance"}
    context = None
    try:
        with tempfile.TemporaryDirectory(prefix="gpu-moe-distributed-") as directory:
            context = mp.spawn(worker, args=((Path(directory) / "rendezvous").as_uri(), directory), nprocs=2, join=False)
            deadline = time.monotonic() + 90
            while not context.join(timeout=1):
                if time.monotonic() >= deadline:
                    raise TimeoutError("two-rank MoE exceeded 90 seconds")
            reports = [json.loads(Path(directory, f"rank-{r}.json").read_text()) for r in range(2)]
            for rank, data in enumerate(reports):
                if [x.get("case") for x in data.get("rejection_checks", [])] != ["capacity-mismatch", "rank-one-nan"] or any(x.get("status") != "rejected" for x in data["rejection_checks"]):
                    raise ValueError("missing collective rejection checks")
                if data.get("rank") != rank or len(data.get("rows", [])) != 12 or any(row.get("status") != "passed" for row in data["rows"]):
                    raise ValueError("incomplete rank evidence")
            report.update(status="passed", rank_reports=reports)
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
    report["provenance"] = source_provenance(REPO, [Path(__file__),
        HERE / "moe_routing_all_to_all/reference.py", HERE / "moe_routing_all_to_all/distributed.py"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(report["status"], OUT)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
