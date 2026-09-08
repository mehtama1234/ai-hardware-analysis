#!/usr/bin/env python3
"""Bounded multi-rank NCCL collective probe.

This is deliberately separate from the world-size-one smoke.  It is safe to
invoke directly (or under ``torchrun``): missing CUDA, NCCL, or a second
visible device produces an explicit unavailable report rather than a CPU
fallback or a fabricated distributed result.
"""

from __future__ import annotations

import json
import os
import socket
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import torch


HERE = Path(__file__).resolve().parent
OUT = HERE / "reports" / "nccl-multirank.json"


def _base(world_size: int, rank: int) -> dict:
    return {
        "project": "distributed-collectives",
        "experiment": "nccl-multirank",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "host": socket.gethostname(),
        "rank": rank,
        "world_size": world_size,
        "device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        "torch_version": torch.__version__,
        "backend": "nccl",
        "gpu_execution_accepted": False,
        "measured": False,
    }


def main() -> int:
    rank = int(os.environ.get("RANK", "0"))
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    report = _base(world_size, rank)
    if not torch.cuda.is_available():
        report.update({"status": "unavailable:cuda-runtime", "reason": "CUDA is not available"})
    elif world_size < 2:
        report.update({"status": "unavailable:world-size", "reason": "run with torchrun and at least two ranks"})
    elif torch.cuda.device_count() < world_size:
        report.update({"status": "unavailable:topology", "reason": "fewer visible GPUs than ranks"})
    else:
        import torch.distributed as dist

        dist.init_process_group("nccl", timeout=__import__("datetime").timedelta(seconds=60))
        torch.cuda.set_device(rank % torch.cuda.device_count())
        values = torch.arange(1, 1_048_577, device="cuda", dtype=torch.float32) * (rank + 1)
        expected_sum = float(values.detach().cpu().sum()) * world_size * (world_size + 1) / 2 / (rank + 1)
        # all_reduce mutates the input; the expected value is the rank-independent
        # sum of the original rank-scaled vectors.
        expected_sum = float(torch.arange(1, 1_048_577, dtype=torch.float32).sum()) * world_size * (world_size + 1) / 2
        samples_ms: list[float] = []
        errors: list[float] = []
        for _ in range(7):
            dist.barrier()
            torch.cuda.synchronize()
            start = time.perf_counter()
            dist.all_reduce(values)
            torch.cuda.synchronize()
            samples_ms.append((time.perf_counter() - start) * 1000.0)
            errors.append(abs(float(values[0].item()) - expected_sum))
            values.fill_(rank + 1)
        gathered: list[dict] = [None] * world_size
        dist.all_gather_object(gathered, {"rank": rank, "median_ms": statistics.median(samples_ms), "max_error": max(errors)})
        if rank == 0:
            report.update({
                "status": "passed" if all(row["max_error"] == 0 for row in gathered) else "failed",
                "gpu_execution_accepted": all(row["max_error"] == 0 for row in gathered),
                "measured": True,
                "tensor_elements": 1_048_576,
                "expected_reduced_first_value": expected_sum,
                "ranks": gathered,
                "scope": "multi-rank NCCL all-reduce on one process per visible GPU",
            })
        dist.barrier()
        dist.destroy_process_group()

    if rank == 0:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"], "world_size": world_size}, indent=2))
    return 0 if report.get("status") == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
