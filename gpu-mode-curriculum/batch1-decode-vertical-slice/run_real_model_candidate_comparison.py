#!/usr/bin/env python3
"""Compare the real GPT-2 framework path with an explicit KV decode candidate."""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_real_model_serving_characterization import generate_cached


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "reports" / "real-model-candidate-comparison.json"
MODEL_ID = "openai-community/gpt2"
PROMPTS = ("The system bottleneck is", "Memory movement dominates transformer inference when context grows because")
CONTEXT_WORD_COUNTS = (8, 32, 128, 256)
MAX_NEW_TOKENS = 8
REPEATS = 5


def timed(fn):
    torch.cuda.synchronize()
    start = time.perf_counter_ns()
    value = fn()
    torch.cuda.synchronize()
    return (time.perf_counter_ns() - start) / 1e6, value


def framework_generate(model, input_ids, attention_mask, *, cache_implementation=None):
    kwargs = {}
    if cache_implementation is not None:
        kwargs["cache_implementation"] = cache_implementation
    with torch.inference_mode():
        output = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            use_cache=True,
            pad_token_id=model.config.eos_token_id,
            **kwargs,
        )
    return output[:, -MAX_NEW_TOKENS:]


def measure(model, tokenizer, prompt: str) -> dict:
    encoded = tokenizer([prompt], return_tensors="pt").to("cuda")
    # Warm both paths before collecting timings.
    timed(lambda: framework_generate(model, encoded["input_ids"], encoded["attention_mask"]))
    generate_cached(model, encoded["input_ids"], encoded["attention_mask"])
    baseline_samples = []
    candidate_samples = []
    static_samples = []
    parity = True
    static_parity = True
    static_error = None
    for _ in range(REPEATS):
        baseline_ms, baseline_tokens = timed(lambda: framework_generate(model, encoded["input_ids"], encoded["attention_mask"]))
        candidate_ms, candidate_tokens = timed(lambda: generate_cached(model, encoded["input_ids"], encoded["attention_mask"])[0])
        baseline_samples.append(baseline_ms)
        candidate_samples.append(candidate_ms)
        parity = parity and torch.equal(baseline_tokens, candidate_tokens)
        try:
            static_ms, static_tokens = timed(lambda: framework_generate(model, encoded["input_ids"], encoded["attention_mask"], cache_implementation="static"))
            static_samples.append(static_ms)
            static_parity = static_parity and torch.equal(baseline_tokens, static_tokens)
        except Exception as exc:
            static_error = f"{type(exc).__name__}: {exc}"
    return {
        "prompt": prompt,
        "prompt_token_count": int(encoded["attention_mask"].sum().item()),
        "generated_token_count": MAX_NEW_TOKENS,
        "output_parity": parity,
        "framework_generate": {
            "wall_time_ms_samples": baseline_samples,
            "wall_time_ms_median": statistics.median(baseline_samples),
            "wall_time_ms_p95": max(baseline_samples),
        },
        "explicit_kv_decode_candidate": {
            "wall_time_ms_samples": candidate_samples,
            "wall_time_ms_median": statistics.median(candidate_samples),
            "wall_time_ms_p95": max(candidate_samples),
        },
        "candidate_speedup_framework_over_candidate": statistics.median(baseline_samples) / max(statistics.median(candidate_samples), 1e-12),
        "static_cache_candidate": {
            "status": "measured" if static_samples else "unavailable",
            "wall_time_ms_samples": static_samples,
            "wall_time_ms_median": statistics.median(static_samples) if static_samples else None,
            "wall_time_ms_p95": max(static_samples) if static_samples else None,
            "output_parity": static_parity if static_samples else None,
            "error": static_error,
            "speedup_framework_over_static": statistics.median(baseline_samples) / max(statistics.median(static_samples), 1e-12) if static_samples else None,
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
    context_prompts = [("context movement " * words).strip() + " because" for words in CONTEXT_WORD_COUNTS]
    rows = [measure(model, tokenizer, prompt) for prompt in (*PROMPTS, *context_prompts)]
    report = {
        "schema_version": "real-model-candidate-comparison-v0.1",
        "experiment": "real_model_framework_generate_vs_explicit_kv_decode",
        "evidence_kind": "measured_gpu",
        "gpu_execution_accepted": True,
        "model_profile": {"model_id": MODEL_ID, "model_revision": getattr(model.config, "_commit_hash", None), "tokenizer_id": MODEL_ID, "trained": True, "parameter_count": sum(parameter.numel() for parameter in model.parameters())},
        "device": "cuda",
        "device_name": torch.cuda.get_device_name(0),
        "runtime": {"torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__},
        "protocol": {"prompts": list(PROMPTS), "context_word_counts": list(CONTEXT_WORD_COUNTS), "max_new_tokens": MAX_NEW_TOKENS, "repeats": REPEATS, "generation": "greedy", "timing": "torch.cuda.synchronize before and after each sample"},
        "rows": rows,
        "decision": "candidate_accepted_for_recorded_scope" if all(row["output_parity"] for row in rows) and all(row["candidate_speedup_framework_over_candidate"] > 1.0 for row in rows) and (not any(row["static_cache_candidate"]["status"] == "measured" for row in rows) or (all(row["static_cache_candidate"]["output_parity"] for row in rows) and all(row["static_cache_candidate"]["speedup_framework_over_static"] > 1.0 for row in rows))) else "candidate_not_proven_better",
        "static_cache_summary": {
            "measured_rows": sum(row["static_cache_candidate"]["status"] == "measured" for row in rows),
            "parity": all(row["static_cache_candidate"]["output_parity"] for row in rows if row["static_cache_candidate"]["status"] == "measured"),
        },
        "claim_boundary": {"allowed": "Framework-versus-explicit-KV candidate timing and exact generated-token parity for this GPT-2/T4 protocol.", "refused": "General serving superiority, energy savings, analog benefit, silicon performance, or production readiness."},
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "output": str(REPORT), "device": report["device_name"], "rows": len(rows), "parity": all(row["output_parity"] for row in rows), "decision": report["decision"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
