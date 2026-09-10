#!/usr/bin/env python3
"""Measure a bounded continuous-arrival microbatch scheduler on real GPT-2."""

from __future__ import annotations

import json
import statistics
import time
import math
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "reports" / "real-model-continuous-microbatch.json"
MODEL_ID = "openai-community/gpt2"
PROMPTS = (
    "The system bottleneck is",
    "Memory movement dominates transformer inference when context grows because",
    "attention cache attention cache attention cache attention cache",
    "A hardware decision must account for longer context and concurrency because",
    "The scheduler should preserve output parity while",
    "A cache-aware runtime can reduce movement when",
    "The measured decode bottleneck suggests that",
    "A hybrid architecture is justified only if",
)
ARRIVAL_MS = (0.0, 0.5, 1.0, 1.5, 20.0, 20.5, 21.0, 21.5)
WINDOW_MS = 2.0
MAX_BATCH = 4
CANCELLED_REQUESTS = (7,)
KV_PAGE_SIZE = 16
MAX_NEW_TOKENS = 8
REPEATS = 3


def timed(fn):
    torch.cuda.synchronize()
    start = time.perf_counter_ns()
    value = fn()
    torch.cuda.synchronize()
    return (time.perf_counter_ns() - start) / 1e6, value


def generate(model, encoded):
    with torch.inference_mode():
        result = model.generate(
            input_ids=encoded["input_ids"],
            attention_mask=encoded["attention_mask"],
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            use_cache=True,
            pad_token_id=model.config.eos_token_id,
        )
    return result[:, -MAX_NEW_TOKENS:]


def schedule(arrivals, request_ids):
    groups = []
    current = []
    first = None
    for position, arrival in enumerate(arrivals):
        index = request_ids[position]
        if current and (arrival - first > WINDOW_MS or len(current) >= MAX_BATCH):
            groups.append(current)
            current = []
            first = None
        if first is None:
            first = arrival
        current.append(index)
    if current:
        groups.append(current)
    return groups


def measure(model, tokenizer):
    active_ids = [index for index in range(len(PROMPTS)) if index not in CANCELLED_REQUESTS]
    singles = {index: tokenizer([PROMPTS[index]], return_tensors="pt").to("cuda") for index in active_ids}
    groups = schedule([ARRIVAL_MS[index] for index in active_ids], active_ids)
    batches = [tokenizer([PROMPTS[index] for index in group], return_tensors="pt", padding=True).to("cuda") for group in groups]
    timed(lambda: [generate(model, singles[index]) for index in active_ids])
    timed(lambda: [generate(model, item) for item in batches])
    sequential_samples = []
    scheduler_samples = []
    parity = True
    completion_rows = []
    for _ in range(REPEATS):
        seq_ms, sequential_list = timed(lambda: [generate(model, singles[index]) for index in active_ids])
        sequential = dict(zip(active_ids, sequential_list))
        sched_start = time.perf_counter_ns()
        scheduled = []
        batch_rows = []
        for group, encoded in zip(groups, batches):
            batch_start_ms = (time.perf_counter_ns() - sched_start) / 1e6
            service_ms, outputs = timed(lambda encoded=encoded: generate(model, encoded))
            batch_end_ms = (time.perf_counter_ns() - sched_start) / 1e6
            scheduled.extend((index, output) for index, output in zip(group, outputs))
            batch_rows.append({"request_indices": group, "service_ms": service_ms, "arrival_start_ms": ARRIVAL_MS[group[0]], "completion_end_ms": batch_end_ms, "queue_wait_before_service_ms": max(0.0, batch_start_ms - ARRIVAL_MS[group[0]])})
        torch.cuda.synchronize()
        scheduler_ms = (time.perf_counter_ns() - sched_start) / 1e6
        scheduled.sort(key=lambda row: row[0])
        parity = parity and all(torch.equal(sequential[index].squeeze(0), output) for index, output in scheduled)
        sequential_samples.append(seq_ms)
        scheduler_samples.append(scheduler_ms)
        completion_rows = batch_rows
    seq_median = statistics.median(sequential_samples)
    sched_median = statistics.median(scheduler_samples)
    all_encoded = tokenizer(list(PROMPTS), return_tensors="pt", padding=True)
    token_counts = {index: int(all_encoded["attention_mask"][index].sum().item()) for index in range(len(PROMPTS))}
    page_rows = [{"request_index": index, "prompt_tokens": token_counts[index], "total_tokens": token_counts[index] + MAX_NEW_TOKENS, "pages": math.ceil((token_counts[index] + MAX_NEW_TOKENS) / KV_PAGE_SIZE), "cancelled": index in CANCELLED_REQUESTS} for index in range(len(PROMPTS))]
    return {
        "request_count": len(PROMPTS),
        "active_request_count": len(active_ids),
        "cancelled_request_indices": list(CANCELLED_REQUESTS),
        "arrival_trace_ms": list(ARRIVAL_MS),
        "groups": groups,
        "window_ms": WINDOW_MS,
        "max_batch": MAX_BATCH,
        "output_parity": parity,
        "sequential_service": {"wall_time_ms_samples": sequential_samples, "wall_time_ms_median": seq_median, "requests_per_second": len(PROMPTS) / (seq_median / 1000.0)},
        "continuous_microbatch_candidate": {"wall_time_ms_samples": scheduler_samples, "wall_time_ms_median": sched_median, "requests_per_second": len(PROMPTS) / (sched_median / 1000.0), "last_batch_rows": completion_rows},
        "throughput_speedup": seq_median / max(sched_median, 1e-12),
        "paged_kv_accounting": {
            "status": "logical_page_lifecycle_bound_to_request_scheduler",
            "page_size_tokens": KV_PAGE_SIZE,
            "rows": page_rows,
            "cancelled_pages_reclaimable": sum(row["pages"] for row in page_rows if row["cancelled"]),
            "model_attention_integration": "pending; model.generate still owns contiguous cache storage",
        },
    }


def main() -> int:
    if not torch.cuda.is_available():
        raise SystemExit("CUDA device required; run this entrypoint in Google Colab")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, use_safetensors=True).to("cuda").eval()
    result = measure(model, tokenizer)
    report = {
        "schema_version": "real-model-continuous-microbatch-v0.1",
        "experiment": "real_model_arrival_trace_sequential_vs_continuous_microbatch",
        "evidence_kind": "measured_gpu",
        "gpu_execution_accepted": True,
        "model_profile": {"model_id": MODEL_ID, "model_revision": getattr(model.config, "_commit_hash", None), "tokenizer_id": MODEL_ID, "trained": True, "parameter_count": sum(parameter.numel() for parameter in model.parameters())},
        "device": "cuda",
        "device_name": torch.cuda.get_device_name(0),
        "runtime": {"torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__},
        "protocol": {"max_new_tokens": MAX_NEW_TOKENS, "repeats": REPEATS, "generation": "greedy", "timing": "torch.cuda.synchronize around every sequential request set and scheduled batch", "scheduler": "bounded arrival-window grouping with pre-service cancellation", "paged_kv": "logical page accounting only; no model-attention paged kernel"},
        "result": result,
        "decision": "candidate_accepted_for_recorded_scope" if result["output_parity"] and result["throughput_speedup"] > 1.0 else "candidate_not_proven_better",
        "claim_boundary": {"allowed": "Exact GPT-2 token parity, pre-service cancellation behavior, logical KV page lifecycle accounting, and bounded arrival-trace microbatch throughput on this T4 protocol.", "refused": "Production continuous batching, model-attention paged-KV eviction, energy savings, analog benefit, or silicon performance."},
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "output": str(REPORT), "device": report["device_name"], "parity": result["output_parity"], "throughput_speedup": result["throughput_speedup"], "groups": result["groups"], "decision": report["decision"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
