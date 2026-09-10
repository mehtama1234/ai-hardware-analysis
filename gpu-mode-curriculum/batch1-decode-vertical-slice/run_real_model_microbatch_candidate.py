#!/usr/bin/env python3
"""Measure a real GPT-2 padded microbatch candidate against sequential service."""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "reports" / "real-model-microbatch-candidate.json"
MODEL_ID = "openai-community/gpt2"
PROMPTS = (
    "The system bottleneck is",
    "Memory movement dominates transformer inference when context grows because",
    "attention cache attention cache attention cache attention cache",
    "A hardware decision must account for longer context and concurrency because",
)
MAX_NEW_TOKENS = 8
REPEATS = 5


def timed(fn):
    torch.cuda.synchronize()
    start = time.perf_counter_ns()
    value = fn()
    torch.cuda.synchronize()
    return (time.perf_counter_ns() - start) / 1e6, value


def generate(model, encoded):
    model_kwargs = {}
    if "position_ids" in encoded:
        model_kwargs["position_ids"] = encoded["position_ids"]
    with torch.inference_mode():
        output = model.generate(
            input_ids=encoded["input_ids"],
            attention_mask=encoded["attention_mask"],
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            use_cache=True,
            pad_token_id=model.config.eos_token_id,
            **model_kwargs,
        )
    return output[:, -MAX_NEW_TOKENS:]


def add_position_ids(encoded):
    mask = encoded["attention_mask"]
    encoded["position_ids"] = (mask.long().cumsum(dim=-1) - 1).masked_fill(mask == 0, 0)
    return encoded


def measure(model, tokenizer):
    singles = [add_position_ids(tokenizer([prompt], return_tensors="pt").to("cuda")) for prompt in PROMPTS]
    batch = add_position_ids(tokenizer(list(PROMPTS), return_tensors="pt", padding=True).to("cuda"))
    timed(lambda: [generate(model, item) for item in singles])
    timed(lambda: generate(model, batch))
    sequential_ms = []
    batch_ms = []
    parity = True
    parity_by_request = [False] * len(PROMPTS)
    last_seq_outputs = None
    last_bat_outputs = None
    for _ in range(REPEATS):
        seq_time, seq_outputs = timed(lambda: [generate(model, item) for item in singles])
        bat_time, bat_outputs = timed(lambda: generate(model, batch))
        sequential_ms.append(seq_time)
        batch_ms.append(bat_time)
        last_seq_outputs = seq_outputs
        last_bat_outputs = bat_outputs
        current_parity = [bool(torch.equal(seq.squeeze(0), bat)) for seq, bat in zip(seq_outputs, bat_outputs)]
        parity_by_request = [old and new for old, new in zip(parity_by_request, current_parity)] if any(parity_by_request) else current_parity
        parity = parity and all(current_parity)
    seq_median = statistics.median(sequential_ms)
    batch_median = statistics.median(batch_ms)
    return {
        "request_count": len(PROMPTS),
        "prompt_token_counts": [int(item["attention_mask"].sum().item()) for item in singles],
        "output_parity": parity,
        "output_parity_by_request": parity_by_request,
        "last_sequential_token_ids": [row.detach().cpu().tolist() for row in last_seq_outputs] if last_seq_outputs is not None else [],
        "last_microbatch_token_ids": [row.detach().cpu().tolist() for row in last_bat_outputs] if last_bat_outputs is not None else [],
        "sequential_service": {"wall_time_ms_samples": sequential_ms, "wall_time_ms_median": seq_median, "requests_per_second": len(PROMPTS) / (seq_median / 1000.0)},
        "padded_microbatch_candidate": {"wall_time_ms_samples": batch_ms, "wall_time_ms_median": batch_median, "requests_per_second": len(PROMPTS) / (batch_median / 1000.0)},
        "throughput_speedup": seq_median / max(batch_median, 1e-12),
        "batch_latency_ratio": batch_median / max(seq_median, 1e-12),
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
        "schema_version": "real-model-microbatch-candidate-v0.1",
        "experiment": "real_model_sequential_vs_padded_microbatch",
        "evidence_kind": "measured_gpu",
        "gpu_execution_accepted": True,
        "model_profile": {"model_id": MODEL_ID, "model_revision": getattr(model.config, "_commit_hash", None), "tokenizer_id": MODEL_ID, "trained": True, "parameter_count": sum(parameter.numel() for parameter in model.parameters())},
        "device": "cuda",
        "device_name": torch.cuda.get_device_name(0),
        "runtime": {"torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__},
        "protocol": {"prompts": list(PROMPTS), "max_new_tokens": MAX_NEW_TOKENS, "repeats": REPEATS, "generation": "greedy", "timing": "torch.cuda.synchronize before and after each complete service sample", "candidate_scope": "padded static microbatch; not continuous-arrival scheduler evidence"},
        "result": result,
        "decision": "candidate_accepted_for_recorded_scope" if result["output_parity"] and result["throughput_speedup"] > 1.0 else "candidate_not_proven_better",
        "claim_boundary": {"allowed": "Exact GPT-2 token parity and bounded sequential-versus-padded-microbatch T4 throughput for these requests.", "refused": "Continuous-arrival scheduling, paged-KV eviction, general serving superiority, energy savings, analog benefit, or silicon performance."},
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "output": str(REPORT), "device": report["device_name"], "parity": result["output_parity"], "throughput_speedup": result["throughput_speedup"], "decision": report["decision"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
