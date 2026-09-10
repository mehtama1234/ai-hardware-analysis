#!/usr/bin/env python3
"""Run the accepted arrival trace through device-resident GPT-2 paged decode."""

from __future__ import annotations

import hashlib
import json
import sys
import statistics
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import run_real_model_fused_paged_decode as fused_decode
from run_real_model_continuous_microbatch import ARRIVAL_MS, CANCELLED_REQUESTS, MAX_BATCH, PROMPTS, WINDOW_MS, schedule

REPORT = Path(__file__).resolve().parent / "reports" / "real-model-device-resident-arrival-load.json"
REPEATS = 5


def timed(fn):
    torch.cuda.synchronize()
    start = time.perf_counter_ns()
    value = fn()
    torch.cuda.synchronize()
    return (time.perf_counter_ns() - start) / 1e6, value


def phase(model, singles, batches, groups, fused: bool, repeats: int = REPEATS):
    torch.cuda.reset_peak_memory_stats()
    sampler = fused_decode.PowerSampler()
    sampler.start()
    samples = []
    parity_rows = []
    stable = True
    for _ in range(repeats):
        if fused:
            elapsed, outputs = timed(lambda: [fused_decode.native_decode(model, item) for item in batches])
            flat = [(index, output) for group, output_batch in zip(groups, outputs) for index, output in zip(group, output_batch)]
            parity_rows.append(flat)
        else:
            elapsed, outputs = timed(lambda: [fused_decode.native_decode(model, singles[index]) for index in singles])
            parity_rows.append(list(zip(singles, outputs)))
        if len(parity_rows) > 1:
            stable = stable and all(a == b and torch.equal(x, y) for (a, x), (b, y) in zip(parity_rows[0], parity_rows[-1]))
        samples.append(elapsed)
    return {
        "wall_time_ms_samples": samples,
        "wall_time_ms_median": statistics.median(samples),
        "peak_memory_allocated_mb": torch.cuda.max_memory_allocated() / (1024 * 1024),
        "power": sampler.stop(),
        "outputs": parity_rows[-1],
        "repeat_output_parity": stable,
    }


def main() -> int:
    if not torch.cuda.is_available():
        raise SystemExit("CUDA device required; run this entrypoint in Google Colab")
    long_decode = "--long" in __import__("sys").argv
    fused_decode.MAX_NEW_TOKENS = 64 if long_decode else 8
    repeats = 3 if long_decode else REPEATS
    stress = "--stress" in __import__("sys").argv
    prompts = PROMPTS
    arrivals = ARRIVAL_MS
    cancelled = CANCELLED_REQUESTS
    if stress:
        prompts = tuple("context movement " * words + " because" for words in (32, 64, 96, 128, 192, 256, 320, 448))
        arrivals = (0.0, 0.5, 1.0, 1.5, 20.0, 20.5, 21.0, 21.5)
        cancelled = (7,)
    tokenizer = AutoTokenizer.from_pretrained(fused_decode.MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(fused_decode.MODEL_ID, use_safetensors=True).to("cuda").eval()
    module = fused_decode.build_extension()
    active_ids = [index for index in range(len(prompts)) if index not in cancelled]
    singles = {index: tokenizer([prompts[index]], return_tensors="pt").to("cuda") for index in active_ids}
    groups = schedule([arrivals[index] for index in active_ids], active_ids)
    batches = [tokenizer([prompts[index] for index in group], return_tensors="pt", padding=True).to("cuda") for group in groups]
    native_phase = phase(model, singles, batches, groups, False, repeats)
    native_outputs = dict(native_phase["outputs"])
    native_scheduled_phase = phase(model, singles, batches, groups, True, repeats)
    native_scheduled_outputs = dict(native_scheduled_phase["outputs"])
    batching_parity = all(torch.equal(native_outputs[index], native_scheduled_outputs[index]) for index in active_ids)
    fused_decode.install_direct_attention(model, module)
    direct_phase = phase(model, singles, batches, groups, True, repeats)
    direct_outputs = dict(direct_phase["outputs"])
    direct_parity = all(native_scheduled_outputs[index].equal(direct_outputs[index]) for index in active_ids)
    fused_decode.install_persistent_fused_attention(model, module)
    persistent_phase = phase(model, singles, batches, groups, True, repeats)
    persistent_outputs = dict(persistent_phase["outputs"])
    persistent_parity = all(native_scheduled_outputs[index].equal(persistent_outputs[index]) for index in active_ids)
    fused_decode.install_fused_attention(model, module)
    fused_phase = phase(model, singles, batches, groups, True, repeats)
    fused_outputs = dict((index, output) for index, output in fused_phase["outputs"])
    parity = all(torch.equal(native_scheduled_outputs[index], fused_outputs[index]) for index in active_ids)
    native_ms = native_phase["wall_time_ms_median"]
    fused_ms = fused_phase["wall_time_ms_median"]
    persistent_ms = persistent_phase["wall_time_ms_median"]
    accepted = all((parity, direct_parity, persistent_parity, batching_parity)) and all(p["repeat_output_parity"] for p in (native_phase, native_scheduled_phase, direct_phase, persistent_phase, fused_phase))
    scheduled_ms = native_scheduled_phase["wall_time_ms_median"]
    result = {
        "request_count": len(prompts), "active_request_count": len(active_ids),
        "cancelled_request_indices": list(cancelled), "arrival_trace_ms": list(arrivals),
        "groups": groups, "window_ms": WINDOW_MS, "max_batch": MAX_BATCH,
        "output_parity": parity,
        "batch_vs_individual_output_parity": batching_parity,
        "all_correctness_checks_passed": accepted,
        "custom_over_native_scheduled_latency_ratio": fused_ms / scheduled_ms,
        "persistent_over_native_scheduled_latency_ratio": persistent_ms / scheduled_ms,
        "direct_over_native_scheduled_latency_ratio": direct_phase["wall_time_ms_median"] / scheduled_ms,
        "direct_output_parity": direct_parity,
        "persistent_output_parity": persistent_parity,
        "native_sequential": {k: v for k, v in native_phase.items() if k != "outputs"},
        "native_scheduled": {k: v for k, v in native_scheduled_phase.items() if k != "outputs"},
        "device_resident_scheduled": {k: v for k, v in fused_phase.items() if k != "outputs"},
        "device_direct_scheduled": {k: v for k, v in direct_phase.items() if k != "outputs"},
        "device_persistent_scheduled": {k: v for k, v in persistent_phase.items() if k != "outputs"},
        "throughput_speedup": native_ms / max(fused_ms, 1e-12),
        "persistent_throughput_speedup": native_ms / max(persistent_ms, 1e-12),
        "claim_boundary": "Full GPT-2 arrival-trace parity and bounded scheduled-vs-sequential timing/memory/power at this T4 protocol; not production continuous batching.",
    }
    report = {
        "schema_version": "real-model-device-resident-arrival-load-v0.2",
        "experiment": "real_gpt2_device_resident_paged_decode_arrival_trace",
        "evidence_kind": "measured_gpu", "gpu_execution_accepted": accepted,
        "model_profile": {"model_id": fused_decode.MODEL_ID, "model_revision": getattr(model.config, "_commit_hash", None), "trained": True, "parameter_count": sum(p.numel() for p in model.parameters())},
        "source_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__), Path(fused_decode.__file__), Path(__file__).with_name("run_real_model_continuous_microbatch.py"))},
        "command": [sys.executable, *sys.argv],
        "device": "cuda", "device_name": torch.cuda.get_device_name(0),
        "runtime": {"torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__},
        "protocol": {"max_new_tokens": fused_decode.MAX_NEW_TOKENS, "repeats": repeats, "long_decode_profile": long_decode, "stress_profile": stress, "scheduler": "accepted bounded arrival-window grouping with pre-service cancellation", "decode": "device-resident K/V page packing plus CUDA paged attention across all 12 GPT-2 layers", "kernel_variant": "one CUDA launch per GPT-2 attention layer over batch*heads with reusable page workspace and output buffer", "page_allocator": "reused PyTorch CUDA K/V page workspace and output buffer per batch and token length across GPT-2 layers; no Python page-table or repack path", "diagnostic_control": "direct CUDA K/V attention with identical reduction and no page packing", "persistent_variant": "per-layer page cache initialized from the first decode context and append-only for subsequent one-token calls", "timing": "CUDA synchronized around complete generation", "memory": "torch.cuda.max_memory_allocated per phase"},
        "result": result,
        "decision": "device_resident_arrival_load_parity_passed" if accepted else "device_resident_arrival_load_parity_failed",
        "claim_boundary": {"allowed": "Exact GPT-2 token parity, cancellation trace, scheduled-vs-sequential timing, CUDA peak memory, and phase-scoped NVML samples for this T4 protocol.", "refused": "General serving superiority, isolated per-token energy, production eviction/scalability, analog benefit, or silicon performance."},
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed" if accepted else "failed", "output": str(REPORT), "device": report["device_name"], "parity": parity, "throughput_speedup": result["throughput_speedup"], "groups": groups}, indent=2))
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
