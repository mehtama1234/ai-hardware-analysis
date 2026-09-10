#!/usr/bin/env python3
"""Compare native GPT-2 eager attention with the native PyTorch SDPA backend."""

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


REPORT = Path(__file__).resolve().parent / "reports" / "real-model-sdpa-backend.json"
PROMPTS = tuple("context movement " * words + " because" for words in (32, 64, 96, 128))
MAX_NEW_TOKENS = 64
REPEATS = 5
MODEL_REVISION = "607a30d783dfa663caf39e06633721c8d4cfcd7e"


def timed(fn):
    torch.cuda.synchronize()
    start = time.perf_counter_ns()
    value = fn()
    torch.cuda.synchronize()
    return (time.perf_counter_ns() - start) / 1e6, value


def run_model(model, encoded):
    previous = fused_decode.MAX_NEW_TOKENS
    fused_decode.MAX_NEW_TOKENS = MAX_NEW_TOKENS
    try:
        return fused_decode.native_decode(model, encoded)
    finally:
        fused_decode.MAX_NEW_TOKENS = previous


def main() -> int:
    if not torch.cuda.is_available():
        raise SystemExit("CUDA device required; run this entrypoint in Google Colab")
    tokenizer = AutoTokenizer.from_pretrained(fused_decode.MODEL_ID, revision=MODEL_REVISION)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    encoded = tokenizer(list(PROMPTS), return_tensors="pt", padding=True).to("cuda")
    eager = AutoModelForCausalLM.from_pretrained(fused_decode.MODEL_ID, revision=MODEL_REVISION, use_safetensors=True, attn_implementation="eager").to("cuda").eval()
    try:
        sdpa = AutoModelForCausalLM.from_pretrained(
            fused_decode.MODEL_ID, revision=MODEL_REVISION, use_safetensors=True, attn_implementation="sdpa"
        ).to("cuda").eval()
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"native SDPA backend unavailable: {exc}")
    backends = {"eager": eager.config._attn_implementation, "sdpa": sdpa.config._attn_implementation}
    if backends != {"eager": "eager", "sdpa": "sdpa"}:
        raise RuntimeError(f"Attention backend selection mismatch: {backends}")
    timed(lambda: run_model(eager, encoded))
    timed(lambda: run_model(sdpa, encoded))
    eager_times, sdpa_times = [], []
    eager_tokens = run_model(eager, encoded)
    sdpa_tokens = run_model(sdpa, encoded)
    parity = bool(torch.equal(eager_tokens, sdpa_tokens))
    individual_parity = all(
        torch.equal(run_model(eager, tokenizer([prompt], return_tensors="pt").to("cuda"))[0], eager_tokens[index])
        for index, prompt in enumerate(PROMPTS)
    )
    # Alternate order to avoid always assigning warm/clock drift to one backend.
    for repeat in range(REPEATS):
        candidates = [(eager, eager_times), (sdpa, sdpa_times)]
        if repeat % 2:
            candidates.reverse()
        for model, samples in candidates:
            elapsed, tokens = timed(lambda: run_model(model, encoded))
            samples.append(elapsed)
            parity = parity and bool(torch.equal(eager_tokens, tokens))
    accepted = parity and individual_parity
    report = {
        "schema_version": "real-model-sdpa-backend-v0.2",
        "experiment": "real_gpt2_native_eager_vs_sdpa_long_decode",
        "evidence_kind": "measured_gpu",
        "gpu_execution_accepted": accepted,
        "model_profile": {"model_id": fused_decode.MODEL_ID, "model_revision": MODEL_REVISION, "tokenizer_revision": MODEL_REVISION, "trained": True},
        "source_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__), Path(fused_decode.__file__))},
        "command": [sys.executable, *sys.argv],
        "runtime": {"torch": torch.__version__, "transformers": __import__("transformers").__version__},
        "attention_backends": backends,
        "device_name": torch.cuda.get_device_name(0),
        "protocol": {"prompts": list(PROMPTS), "prompt_token_counts": encoded["attention_mask"].sum(-1).tolist(), "padding_side": tokenizer.padding_side, "warmups_per_backend": 1, "order": "alternating", "max_new_tokens": MAX_NEW_TOKENS, "repeats": REPEATS, "timing": "CUDA synchronized around complete generation"},
        "result": {
            "output_parity": parity,
            "batch_vs_individual_output_parity": individual_parity,
            "generated_token_ids": {"eager": eager_tokens.tolist(), "sdpa": sdpa_tokens.tolist()},
            "eager_wall_time_ms_samples": eager_times,
            "sdpa_wall_time_ms_samples": sdpa_times,
            "eager_wall_time_ms_median": statistics.median(eager_times),
            "sdpa_wall_time_ms_median": statistics.median(sdpa_times),
            "sdpa_over_eager_latency_ratio": statistics.median(sdpa_times) / max(statistics.median(eager_times), 1e-12),
        },
        "decision": "native_sdpa_backend_accepted_for_recorded_scope" if accepted and statistics.median(sdpa_times) <= statistics.median(eager_times) else "native_sdpa_backend_not_proven_better",
        "claim_boundary": "Bounded native GPT-2/Tesla-T4 backend comparison; not production serving, silicon performance, or analog benefit.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed" if accepted else "failed", "output": str(REPORT), "device": report["device_name"], **report["result"], "decision": report["decision"]}, indent=2))
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
