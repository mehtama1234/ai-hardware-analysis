#!/usr/bin/env python3
"""Run a bounded NCCL collective probe on the visible CUDA device."""
from __future__ import annotations

import hashlib
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

import torch
import torch.distributed as dist

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "reports/nccl-gpu.json"


def main() -> int:
    report = {"project": "distributed-collectives", "generated_at": datetime.now(timezone.utc).isoformat(), "world_size": 1, "backend": "nccl", "gpu_execution_accepted": False, "source_sha256": {"run_nccl_gpu.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    if not torch.cuda.is_available() or not dist.is_nccl_available():
        report.update({"status": "unavailable", "reason": "CUDA or NCCL unavailable"})
    else:
        url = "tcp://127.0.0.1:29591"
        dist.init_process_group("nccl", init_method=url, rank=0, world_size=1)
        try:
            device = torch.device("cuda", 0)
            values = torch.arange(1, (1 << 20) + 1, device=device, dtype=torch.float32)
            expected_sum = values.sum().item()
            samples = []
            for _ in range(7):
                work = values.clone()
                start = torch.cuda.Event(enable_timing=True); stop = torch.cuda.Event(enable_timing=True); start.record()
                dist.all_reduce(work, op=dist.ReduceOp.SUM); stop.record(); stop.synchronize(); samples.append(start.elapsed_time(stop))
                if not torch.equal(work, values): raise AssertionError("world-size-one all_reduce changed tensor")
            gathered = [torch.empty_like(values)]
            dist.all_gather(gathered, values)
            passed = float(gathered[0].sum().item()) == expected_sum and len(samples) == 7 and all(torch.isfinite(torch.tensor(samples)))
            report.update({"status": "passed" if passed else "failed", "gpu_execution_accepted": passed, "device_name": torch.cuda.get_device_name(0), "torch_version": torch.__version__, "torch_nccl": torch.cuda.nccl.version(), "tensor_elements": values.numel(), "all_reduce_sum_error": abs(float(gathered[0].sum().item()) - expected_sum), "all_gather_exact": bool(torch.equal(gathered[0], values)), "median_all_reduce_ms": statistics.median(samples), "samples_ms": samples, "scope": "single-process, world_size=1 NCCL execution on one visible GPU; no multi-GPU communication or scaling claim"})
        finally:
            dist.destroy_process_group()
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n"); print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2)); return 0 if report["gpu_execution_accepted"] else 2


if __name__ == "__main__": raise SystemExit(main())
