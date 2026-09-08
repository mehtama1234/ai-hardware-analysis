#!/usr/bin/env python3
"""Execute the MoE routing/reference contract on CUDA tensors."""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from moe_routing_all_to_all.reference import routed_linear as cpu_reference
sys.path.insert(0, str(ROOT / "gpu-kernels-serving-lab"))
from common.provenance import source_provenance

OUT = HERE / "reports/gpu-reference.json"


def gpu_routed_linear(tokens, logits, weights, top_k: int, capacity: int):
    selected = torch.argsort(logits, dim=1, descending=True, stable=True)[:, :top_k]
    gates = torch.softmax(logits.gather(1, selected), dim=1)
    accepted = torch.zeros((tokens.shape[0], top_k), dtype=torch.bool, device=tokens.device)
    output = tokens.new_zeros((tokens.shape[0], weights.shape[1]))
    loads = []
    for expert in range(weights.shape[0]):
        assignments = (selected == expert).nonzero(as_tuple=False)
        loads.append(int(assignments.shape[0]))
        kept = assignments[:capacity]
        if kept.numel():
            token_ids, slots = kept.unbind(dim=1)
            accepted[token_ids, slots] = True
            computed = tokens[token_ids] @ weights[expert].transpose(0, 1)
            output = output.index_add(0, token_ids, computed * gates[token_ids, slots, None])
    return output, {"expert_indices": selected, "gates": gates, "accepted": accepted,
                    "offered_loads": loads, "dropped_assignments": tokens.shape[0] * top_k - int(accepted.sum())}


def main() -> int:
    report = {"project": "moe-routing-all-to-all", "generated_at": datetime.now(timezone.utc).isoformat(), "gpu_execution_accepted": False}
    if not torch.cuda.is_available():
        report.update({"status": "unavailable", "reason": "CUDA unavailable"})
    else:
        device = torch.device("cuda")
        generator = torch.Generator(device=device).manual_seed(730)
        tokens = torch.randn(256, 32, generator=generator, device=device, requires_grad=True)
        logits = torch.randn(256, 8, generator=generator, device=device, requires_grad=True)
        weights = torch.randn(8, 16, 32, generator=generator, device=device, requires_grad=True)
        cpu_tokens = tokens.detach().cpu().double().requires_grad_(True)
        cpu_logits = logits.detach().cpu().double().requires_grad_(True)
        cpu_weights = weights.detach().cpu().double().requires_grad_(True)
        cpu_out, cpu_route = cpu_reference(cpu_tokens, cpu_logits, cpu_weights, top_k=2, capacity=64)
        gpu_out, gpu_route = gpu_routed_linear(tokens, logits, weights, top_k=2, capacity=64)
        gpu_out.square().mean().backward(); cpu_out.square().mean().backward()
        torch.testing.assert_close(gpu_out.detach().cpu().double(), cpu_out.detach(), atol=3e-5, rtol=3e-5)
        torch.testing.assert_close(tokens.grad.detach().cpu().double(), cpu_tokens.grad.detach(), atol=3e-5, rtol=3e-5)
        torch.testing.assert_close(logits.grad.detach().cpu().double(), cpu_logits.grad.detach(), atol=3e-5, rtol=3e-5)
        torch.testing.assert_close(weights.grad.detach().cpu().double(), cpu_weights.grad.detach(), atol=3e-5, rtol=3e-5)
        if not torch.equal(gpu_route["expert_indices"].cpu(), cpu_route["expert_indices"]): raise AssertionError("GPU route differs")
        if not torch.equal(gpu_route["accepted"].cpu(), cpu_route["accepted"]): raise AssertionError("GPU capacity mask differs")
        samples = []
        for _ in range(7):
            tokens.grad = logits.grad = weights.grad = None
            start = torch.cuda.Event(enable_timing=True); stop = torch.cuda.Event(enable_timing=True); start.record()
            out, _ = gpu_routed_linear(tokens, logits, weights, top_k=2, capacity=64); out.square().mean().backward()
            stop.record(); stop.synchronize(); samples.append(start.elapsed_time(stop))
        report.update({"status": "passed", "gpu_execution_accepted": True, "device_name": torch.cuda.get_device_name(), "torch_version": torch.__version__, "shape": [256, 32, 8, 16], "top_k": 2, "capacity": 64, "offered_loads": gpu_route["offered_loads"], "dropped_assignments": gpu_route["dropped_assignments"], "max_output_error": float((gpu_out.detach().cpu().double() - cpu_out.detach()).abs().max()), "forward_backward_median_ms": statistics.median(samples), "samples_ms": samples})
    report["provenance"] = source_provenance(ROOT, [Path(__file__), HERE / "moe_routing_all_to_all/reference.py", ROOT / "gpu-kernels-serving-lab/common/provenance.py"])
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n"); print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2)); return 0 if report["gpu_execution_accepted"] else 2


if __name__ == "__main__": raise SystemExit(main())
