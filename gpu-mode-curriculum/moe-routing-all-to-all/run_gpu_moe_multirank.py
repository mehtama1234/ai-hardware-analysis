#!/usr/bin/env python3
"""Multi-rank CUDA/NCCL MoE dispatch/compute/return correctness probe.

The single-GPU MoE experiment proves local routing only.  This runner exercises
the actual sharded path with ``all_to_all_single`` and compares every rank's
output and capacity mask with the CPU mathematical oracle.  It records an
explicit unavailable result when the host cannot provide one CUDA device per
rank.
"""

from __future__ import annotations

import json
import os
import socket
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import torch


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "reports" / "gpu-moe-multirank.json"


def _base(rank: int, world: int) -> dict:
    return {
        "project": "moe-routing-all-to-all",
        "experiment": "gpu-moe-multirank",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "host": socket.gethostname(),
        "rank": rank,
        "world_size": world,
        "device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        "torch_version": torch.__version__,
        "backend": "nccl",
        "gpu_execution_accepted": False,
        "measured": False,
    }


def _distributed_linear(tokens, logits, local_weights, *, top_k: int, capacity: int, dist):
    rank, world = dist.get_rank(), dist.get_world_size()
    local_experts, output_width, width = local_weights.shape
    experts = local_experts * world
    selected = torch.argsort(logits, dim=1, descending=True, stable=True)[:, :top_k]
    gates = torch.softmax(logits.gather(1, selected), dim=1)
    assignments = [(selected == expert).nonzero(as_tuple=False) for expert in range(experts)]
    counts = torch.tensor([len(a) for a in assignments], device=tokens.device, dtype=torch.int64)
    all_counts = [torch.empty_like(counts) for _ in range(world)]
    dist.all_gather(all_counts, counts)
    prior = sum(all_counts[:rank], torch.zeros_like(counts))
    kept = [a[: max(0, capacity - int(prior[e].item()))] for e, a in enumerate(assignments)]
    accepted = torch.zeros_like(selected, dtype=torch.bool)
    output = tokens.new_zeros((len(tokens), output_width))
    if capacity == 0:
        return output, accepted

    sends = tokens.new_zeros((world, local_experts, capacity, width))
    for expert, pairs in enumerate(kept):
        if len(pairs):
            owner, local = divmod(expert, local_experts)
            sends[owner, local, : len(pairs)] = tokens[pairs[:, 0]]
            accepted[pairs[:, 0], pairs[:, 1]] = True
    received = torch.empty_like(sends)
    dist.all_to_all_single(received, sends)
    replies = tokens.new_zeros((world, local_experts, capacity, output_width))
    for local in range(local_experts):
        replies[:, local] = received[:, local] @ local_weights[local].T
    returned = torch.empty_like(replies)
    dist.all_to_all_single(returned, replies)
    for expert, pairs in enumerate(kept):
        if len(pairs):
            owner, local = divmod(expert, local_experts)
            ids, slots = pairs.unbind(dim=1)
            output.index_add_(0, ids, returned[owner, local, : len(pairs)] * gates[ids, slots, None])
    return output, accepted


def main() -> int:
    rank = int(os.environ.get("RANK", "0"))
    world = int(os.environ.get("WORLD_SIZE", "1"))
    report = _base(rank, world)
    if not torch.cuda.is_available():
        report.update(status="unavailable:cuda-runtime", reason="CUDA is not available")
    elif world < 2:
        report.update(status="unavailable:world-size", reason="launch with torchrun and at least two ranks")
    elif torch.cuda.device_count() < world:
        report.update(status="unavailable:topology", reason="fewer visible GPUs than ranks")
    else:
        import sys
        import torch.distributed as dist

        sys.path.insert(0, str(REPO / "gpu-mode-curriculum" / "moe-routing-all-to-all"))
        from moe_routing_all_to_all.reference import routed_linear

        dist.init_process_group("nccl", timeout=timedelta(seconds=90))
        torch.cuda.set_device(rank)
        device = torch.device("cuda", rank)
        tokens_per_rank, width, local_experts, output_width, top_k, capacity = 128, 32, 2, 16, 2, 64
        generator = torch.Generator().manual_seed(719)
        global_tokens = torch.randn(tokens_per_rank * world, width, generator=generator, dtype=torch.float32)
        global_logits = torch.randn(tokens_per_rank * world, local_experts * world, generator=generator, dtype=torch.float32)
        global_weights = torch.randn(local_experts * world, output_width, width, generator=generator, dtype=torch.float32)
        expected, route = routed_linear(global_tokens, global_logits, global_weights, top_k=top_k, capacity=capacity)
        start_token, end_token = rank * tokens_per_rank, (rank + 1) * tokens_per_rank
        local_tokens = global_tokens[start_token:end_token].to(device)
        local_logits = global_logits[start_token:end_token].to(device)
        local_weights = global_weights[rank * local_experts : (rank + 1) * local_experts].to(device)
        dist.barrier()
        torch.cuda.synchronize()
        start = time.perf_counter()
        output, accepted = _distributed_linear(local_tokens, local_logits, local_weights, top_k=top_k, capacity=capacity, dist=dist)
        torch.cuda.synchronize()
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        output_error = float((output.cpu() - expected[start_token:end_token]).abs().max())
        route_exact = bool(torch.equal(accepted.cpu(), route["accepted"][start_token:end_token]))
        local = {"rank": rank, "output_error": output_error, "route_exact": route_exact, "elapsed_ms": elapsed_ms}
        gathered: list[dict] = [None] * world
        dist.all_gather_object(gathered, local)
        if rank == 0:
            passed = all(row["route_exact"] and row["output_error"] <= 3e-5 for row in gathered)
            report.update({
                "status": "passed" if passed else "failed",
                "gpu_execution_accepted": passed,
                "measured": True,
                "tokens_per_rank": tokens_per_rank,
                "width": width,
                "local_experts": local_experts,
                "output_width": output_width,
                "top_k": top_k,
                "capacity": capacity,
                "dropped_assignments": route["dropped_assignments"],
                "rank_results": gathered,
                "scope": "multi-rank CUDA/NCCL sharded expert dispatch, local expert GEMMs, return all-to-all, and CPU-oracle comparison",
            })
        dist.barrier()
        dist.destroy_process_group()

    if rank == 0:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"], "world_size": world}, indent=2))
    return 0 if report.get("status") == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
