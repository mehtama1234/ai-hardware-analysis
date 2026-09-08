#!/usr/bin/env python3
"""Measured two-rank CPU/Gloo baseline for collective latency.

This is deliberately a CPU baseline, not a substitute for NCCL/RCCL.  Every
sample starts from fresh rank-specific inputs, validates the complete output,
and records the raw synchronized wall-clock samples.  It exists to make the
performance comparison honest before a multi-GPU host is available.
"""

from __future__ import annotations

import json
import statistics
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "reports" / "cpu-benchmark.json"
OPERATIONS = ("all-reduce", "all-gather", "reduce-scatter", "all-to-all", "broadcast")
SAMPLES = 5


def _worker(rank: int, rendezvous: str, directory: str, samples: int) -> None:
    import torch
    import torch.distributed as dist

    torch.set_num_threads(1)
    dist.init_process_group("gloo", init_method=rendezvous, rank=rank, world_size=2,
                            timeout=timedelta(seconds=30))
    rows = []

    def timed(name, factory, operation, expected, bytes_transferred):
        for _ in range(1):
            value = factory()
            operation(value)
        dist.barrier()
        samples_ms = []
        for _ in range(samples):
            value = factory()
            dist.barrier()
            start = time.perf_counter()
            operation(value)
            dist.barrier()
            samples_ms.append((time.perf_counter() - start) * 1000.0)
            if not torch.isfinite(value if isinstance(value, torch.Tensor) else value[0]).all():
                raise AssertionError(f"{name}: non-finite output")
            if isinstance(value, list):
                actual = torch.cat(value)
            else:
                actual = value
            if not torch.equal(actual, expected):
                raise AssertionError(f"{name}: output mismatch on rank {rank}")
        rows.append({
            "operation": name,
            "status": "passed",
            "bytes_transferred": bytes_transferred,
            "samples_ms": [round(v, 6) for v in samples_ms],
            "median_ms": round(statistics.median(samples_ms), 6),
        })

    base = torch.arange(1024, dtype=torch.float32)
    timed("all-reduce", lambda: base + 100 * rank,
          lambda x: dist.all_reduce(x), base * 2 + 100, base.numel() * 4)
    # all-gather uses a list receive buffer rather than a single output tensor.
    dist.barrier(); samples_ms = []
    expected_gather = torch.cat([base, base + 100])
    for _ in range(samples):
        recv = [torch.empty_like(base) for _ in range(2)]
        dist.barrier(); start = time.perf_counter(); dist.all_gather(recv, base + 100 * rank); dist.barrier()
        samples_ms.append((time.perf_counter() - start) * 1000.0)
        actual = torch.cat(recv)
        if not torch.equal(actual, expected_gather): raise AssertionError("all-gather mismatch")
    rows.append({"operation": "all-gather", "status": "passed", "bytes_transferred": base.numel() * 4 * 2,
                 "samples_ms": [round(v, 6) for v in samples_ms], "median_ms": round(statistics.median(samples_ms), 6)})

    scatter = torch.arange(2048, dtype=torch.float32) + 100 * rank
    expected_scatter = torch.arange(2048, dtype=torch.float32) * 2 + 100
    timed("reduce-scatter", lambda: torch.empty_like(base),
          lambda x: dist.reduce_scatter_tensor(x, scatter), expected_scatter[rank * 1024:(rank + 1) * 1024], base.numel() * 4 * 2)
    exchanged_expected = torch.cat([base[rank * 512:(rank + 1) * 512], base[rank * 512:(rank + 1) * 512] + 100])
    timed("all-to-all", lambda: torch.empty_like(base),
          lambda x: dist.all_to_all_single(x, base + 100 * rank), exchanged_expected, base.numel() * 4)
    timed("broadcast", lambda: base + 100 * rank,
          lambda x: dist.broadcast(x, src=1), base + 100, base.numel() * 4)
    Path(directory, f"rank-{rank}.json").write_text(json.dumps({"rank": rank, "rows": rows}, allow_nan=False) + "\n")
    dist.destroy_process_group()


def main() -> int:
    import torch
    import torch.multiprocessing as mp
    sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
    from common.provenance import source_provenance

    report = {"experiment": "collective-cpu-benchmark", "status": "failed", "measured": False,
              "gpu_execution_accepted": False, "backend": "gloo", "world_size": 2,
              "samples_per_operation": SAMPLES,
              "scope": "two local CPU processes; synchronized Gloo latency baseline with exact output checks; no GPU, overlap, topology or production claim"}
    context = None
    try:
        with tempfile.TemporaryDirectory(prefix="gpu-collective-cpu-bench-") as directory:
            rendezvous = (Path(directory) / "rendezvous").as_uri()
            context = mp.spawn(_worker, args=(rendezvous, directory, SAMPLES), nprocs=2, join=False)
            deadline = time.monotonic() + 90
            while not context.join(timeout=1):
                if time.monotonic() >= deadline: raise TimeoutError("CPU benchmark exceeded 90 seconds")
            ranks = [json.loads(Path(directory, f"rank-{rank}.json").read_text()) for rank in range(2)]
            if [r["rank"] for r in ranks] != [0, 1]: raise ValueError("missing rank report")
            if any([row["operation"] for row in r["rows"]] != list(OPERATIONS) for r in ranks): raise ValueError("operation coverage mismatch")
            rows = [{"operation": op, "rank_median_ms": [r["rows"][i]["median_ms"] for r in ranks],
                     "median_ms": round(statistics.median(r["rows"][i]["median_ms"] for r in ranks), 6),
                     "samples_ms": [r["rows"][i]["samples_ms"] for r in ranks]}
                    for i, op in enumerate(OPERATIONS)]
            report.update({"status": "passed", "measured": True, "rank_reports": ranks, "benchmarks": rows,
                           "generated_at": datetime.now(timezone.utc).isoformat()})
    except Exception as exc:
        report.update({"generated_at": datetime.now(timezone.utc).isoformat(), "error": repr(exc)})
    finally:
        if context is not None:
            for process in context.processes:
                if process.is_alive(): process.terminate()
            for process in context.processes: process.join(timeout=5)
    report["provenance"] = source_provenance(REPO, [Path(__file__)])
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "operations": len(report.get("benchmarks", []))}, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
