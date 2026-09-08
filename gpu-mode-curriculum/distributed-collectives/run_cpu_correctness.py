"""Bounded, two-rank Gloo output validation; no GPU or performance acceptance."""
from datetime import timedelta
import json
from pathlib import Path
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OPERATIONS = ("all-reduce", "all-gather", "reduce-scatter", "all-to-all", "broadcast")
OUT = HERE / "reports/cpu-correctness.json"


def worker(rank, rendezvous, output_directory):
    import torch
    import torch.distributed as dist

    torch.set_num_threads(1)
    dist.init_process_group("gloo", init_method=rendezvous, rank=rank, world_size=2,
                            timeout=timedelta(seconds=30))
    rows = []
    try:
        def check(name, actual, expected):
            if not torch.isfinite(actual).all() or not torch.equal(actual, expected):
                raise AssertionError(f"rank {rank}: {name} output mismatch")
            rows.append({"operation": name, "status": "passed",
                         "actual": actual.tolist(), "expected": expected.tolist()})

        # Fresh inputs per operation; small integer values are exact in FP32.
        base = torch.arange(8, dtype=torch.float32)
        reduced = base + 100 * rank
        dist.all_reduce(reduced)
        check("all-reduce", reduced, base * 2 + 100)

        gathered = [torch.full_like(base, float("nan")) for _ in range(2)]
        dist.all_gather(gathered, base + 100 * rank)
        check("all-gather", torch.cat(gathered), torch.cat([base, base + 100]))

        scatter_base = torch.arange(16, dtype=torch.float32)
        scattered = torch.full_like(base, float("nan"))
        dist.reduce_scatter_tensor(scattered, scatter_base + 100 * rank)
        check("reduce-scatter", scattered, (scatter_base * 2 + 100)[rank * 8:(rank + 1) * 8])

        exchanged = torch.full_like(base, float("nan"))
        dist.all_to_all_single(exchanged, base + 100 * rank)
        chunk = base[rank * 4:(rank + 1) * 4]
        check("all-to-all", exchanged, torch.cat([chunk, chunk + 100]))

        broadcast = base + 100 * rank
        dist.broadcast(broadcast, src=1)
        check("broadcast", broadcast, base + 100)
        Path(output_directory, f"rank-{rank}.json").write_text(json.dumps(
            {"rank": rank, "rows": rows}, allow_nan=False) + "\n")
    finally:
        dist.destroy_process_group()


def validate_rank_reports(reports):
    if len(reports) != 2 or any(type(r.get("rank")) is not int for r in reports) or [r.get("rank") for r in reports] != [0, 1]:
        raise ValueError("expected exactly ranks zero and one")
    for report in reports:
        rank = report["rank"]
        # Independently derive the fixture's oracle with Python integers rather
        # than trusting a child report's assertion or its expected-array field.
        oracle = {
            "all-reduce": [2 * i + 100 for i in range(8)],
            "all-gather": [i + 100 * source for source in range(2) for i in range(8)],
            "reduce-scatter": [2 * i + 100 for i in range(rank * 8, (rank + 1) * 8)],
            "all-to-all": [i + 100 * source for source in range(2) for i in range(rank * 4, (rank + 1) * 4)],
            "broadcast": [i + 100 for i in range(8)],
        }
        rows = report.get("rows", [])
        if [row.get("operation") for row in rows] != list(OPERATIONS):
            raise ValueError("missing or duplicate collective output")
        for row in rows:
            if row.get("status") != "passed" or row.get("actual") != row.get("expected"):
                raise ValueError("collective output did not pass its oracle")
            values = row.get("actual")
            import math
            if not isinstance(values, list) or len(values) != (16 if row["operation"] == "all-gather" else 8):
                raise ValueError("unexpected output shape")
            if any(type(value) not in (int, float) or not math.isfinite(value) for value in values):
                raise ValueError("non-finite or non-numeric output")
            if values != oracle[row["operation"]]:
                raise ValueError("output disagrees with independent rank oracle")


def main():
    import torch
    import torch.multiprocessing as mp
    sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
    from common.provenance import source_provenance

    report = {"status": "failed", "evidence_kind": "measured_cpu", "backend": "gloo",
              "world_size": 2, "torch_version": torch.__version__, "rank_reports": [],
              "gpu_execution_accepted": False,
              "scope": "two local CPU processes, five exact FP32 collective output checks per rank; no timing, overlap, GPU or multi-host performance claim"}
    context = None
    try:
        with tempfile.TemporaryDirectory(prefix="gpu-collective-correctness-") as temporary:
            rendezvous = (Path(temporary) / "rendezvous").as_uri()
            context = mp.spawn(worker, args=(rendezvous, temporary), nprocs=2, join=False)
            deadline = time.monotonic() + 90
            while not context.join(timeout=1):
                if time.monotonic() >= deadline:
                    raise TimeoutError("two-rank correctness exceeded 90 seconds")
            reports = [json.loads(Path(temporary, f"rank-{rank}.json").read_text()) for rank in range(2)]
            validate_rank_reports(reports)
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
    report["provenance"] = source_provenance(REPO, [Path(__file__)])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(report["status"], OUT)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
