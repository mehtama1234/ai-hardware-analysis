#!/usr/bin/env python3
"""Extended Colab measurement for the real GPT-2 workload.

This is deliberately a measurement handoff, not a simulator.  It adds
context-length scaling, request-tail samples, and a CUDA operator profile to
the existing synchronized prefill/decode characterization.
"""

from __future__ import annotations

import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Event, Thread
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_real_model_serving_characterization import clocked, generate_cached


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "reports" / "real-model-serving-extended-characterization.json"
MODEL_ID = "openai-community/gpt2"
BASE_PROMPT = "The system bottleneck is"
MAX_NEW_TOKENS = 8
CONTEXT_WORD_COUNTS = (8, 32, 128, 256)
TAIL_REPEATS = 20


class PowerSampler:
    """Best-effort synchronized NVML sampler for Colab runtimes."""

    def __init__(self):
        self.samples = []
        self.stop_event = Event()
        self.thread = None
        self.handle = None
        self.reason = None
        try:
            import pynvml
            pynvml.nvmlInit()
            self.nvml = pynvml
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        except Exception as exc:
            self.reason = f"NVML unavailable: {type(exc).__name__}: {exc}"

    def _sample(self):
        while not self.stop_event.is_set():
            try:
                self.samples.append({
                    "time_ns": time.perf_counter_ns(),
                    "power_w": self.nvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0,
                })
            except Exception as exc:
                self.reason = f"NVML sampling failed: {type(exc).__name__}: {exc}"
                return
            self.stop_event.wait(0.01)

    def start(self):
        if self.handle is not None:
            self.thread = Thread(target=self._sample, daemon=True)
            self.thread.start()

    def stop(self) -> dict:
        if self.thread is None:
            return {"status": "not_sampled", "reason": self.reason}
        self.stop_event.set()
        self.thread.join(timeout=2.0)
        if len(self.samples) < 2:
            return {"status": "not_sampled", "reason": self.reason or "fewer than two NVML samples"}
        duration_s = (self.samples[-1]["time_ns"] - self.samples[0]["time_ns"]) / 1e9
        energy_j = sum(
            ((left["power_w"] + right["power_w"]) / 2.0) * ((right["time_ns"] - left["time_ns"]) / 1e9)
            for left, right in zip(self.samples, self.samples[1:])
        )
        return {
            "status": "sampled_nvml_protocol_scope",
            "sample_count": len(self.samples),
            "duration_s": duration_s,
            "average_power_w": energy_j / max(duration_s, 1e-12),
            "peak_power_w": max(sample["power_w"] for sample in self.samples),
            "integrated_energy_j": energy_j,
            "scope": "entire extended characterization process; not an isolated per-token energy claim",
        }


def quantiles(samples: list[float]) -> dict[str, float]:
    ordered = sorted(samples)
    return {
        "count": len(ordered),
        "min_ms": min(ordered),
        "median_ms": statistics.median(ordered),
        "p95_ms": ordered[max(0, int(len(ordered) * 0.95) - 1)],
        "max_ms": max(ordered),
    }


def context_sweep(model, tokenizer) -> list[dict]:
    rows = []
    for words in CONTEXT_WORD_COUNTS:
        prompt = ("context movement " * words).strip() + " because"
        encoded = tokenizer([prompt], return_tensors="pt", padding=True, truncation=True).to("cuda")
        mask = encoded["attention_mask"]
        generate_cached(model, encoded["input_ids"], mask)
        samples = []
        prefill = decode = 0.0
        peak = 0.0
        for _ in range(3):
            torch.cuda.reset_peak_memory_stats()
            _, prefill, decode = generate_cached(model, encoded["input_ids"], mask)
            samples.append(prefill + decode)
            peak = max(peak, torch.cuda.max_memory_allocated() / (1024 ** 2))
        rows.append({
            "requested_context_words": words,
            "prompt_token_count": int(mask.sum().item()),
            "cached_total_ms": quantiles(samples),
            "last_prefill_ms": prefill,
            "last_decode_ms": decode,
            "peak_memory_mb": peak,
        })
    return rows


def tail_measurement(model, tokenizer) -> dict:
    encoded = tokenizer([BASE_PROMPT], return_tensors="pt").to("cuda")
    generate_cached(model, encoded["input_ids"], encoded["attention_mask"])
    samples = []
    for _ in range(TAIL_REPEATS):
        elapsed, _ = clocked(lambda: generate_cached(model, encoded["input_ids"], encoded["attention_mask"]))
        samples.append(elapsed)
    return {
        "request": BASE_PROMPT,
        "concurrency": 1,
        "protocol": "serialized cached requests; CUDA synchronized around every sample",
        "latency": quantiles(samples),
    }


def _generate_cached_on_stream(model, input_ids, attention_mask, stream):
    with torch.cuda.stream(stream), torch.inference_mode():
        out = model(input_ids=input_ids, attention_mask=attention_mask, use_cache=True)
        past = out.past_key_values
        token = out.logits[:, -1, :].argmax(dim=-1, keepdim=True)
        decode_mask = attention_mask
        for _ in range(MAX_NEW_TOKENS - 1):
            decode_mask = torch.cat((decode_mask, torch.ones((1, 1), device="cuda", dtype=decode_mask.dtype)), dim=1)
            out = model(input_ids=token, attention_mask=decode_mask, past_key_values=past, use_cache=True)
            past = out.past_key_values
            token = out.logits[:, -1, :].argmax(dim=-1, keepdim=True)
    stream.synchronize()


def concurrency_measurement(model, tokenizer) -> list[dict]:
    encoded = tokenizer([BASE_PROMPT], return_tensors="pt").to("cuda")
    rows = []
    for concurrency in (2, 4):
        request_samples = []
        for _ in range(3):
            streams = [torch.cuda.Stream() for _ in range(concurrency)]
            started = time.perf_counter_ns()
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                futures = [pool.submit(_generate_cached_on_stream, model, encoded["input_ids"], encoded["attention_mask"], stream) for stream in streams]
                for future in futures:
                    future.result()
            torch.cuda.synchronize()
            elapsed_ms = (time.perf_counter_ns() - started) / 1e6
            request_samples.append(elapsed_ms / concurrency)
        rows.append({
            "concurrency": concurrency,
            "protocol": "independent CUDA streams with synchronized join",
            "per_request_latency": quantiles(request_samples),
            "batch_equivalent": False,
        })
    return rows


def operator_profile(model, tokenizer) -> dict:
    encoded = tokenizer([BASE_PROMPT], return_tensors="pt").to("cuda")
    generate_cached(model, encoded["input_ids"], encoded["attention_mask"])
    activities = [torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA]
    try:
        with torch.profiler.profile(activities=activities, record_shapes=True, profile_memory=True) as profile:
            generate_cached(model, encoded["input_ids"], encoded["attention_mask"])
        rows = []
        for item in profile.key_averages():
            cuda_ms = float(getattr(item, "self_device_time_total", 0.0)) / 1000.0
            if cuda_ms <= 0:
                continue
            rows.append({
                "operator": item.key,
                "self_cuda_ms": cuda_ms,
                "self_cuda_memory_bytes": int(getattr(item, "self_cuda_memory_usage", 0)),
                "calls": int(item.count),
            })
        rows.sort(key=lambda row: row["self_cuda_ms"], reverse=True)
        return {"status": "measured_cuda_profiler", "top_operators": rows[:20]}
    except Exception as exc:  # profiler availability varies across Colab images
        return {"status": "unavailable", "reason": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    if not torch.cuda.is_available():
        raise SystemExit("CUDA device required; run this entrypoint in Google Colab")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, use_safetensors=True).to("cuda").eval()
    power_sampler = PowerSampler()
    power_sampler.start()
    report = {
        "schema_version": "real-model-serving-extended-characterization-v0.1",
        "experiment": "real_model_colab_context_tail_operator_sweep",
        "evidence_kind": "measured_gpu",
        "gpu_execution_accepted": True,
        "model_profile": {
            "model_id": MODEL_ID,
            "model_revision": getattr(model.config, "_commit_hash", None),
            "tokenizer_id": MODEL_ID,
            "trained": True,
            "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        },
        "device": "cuda",
        "device_name": torch.cuda.get_device_name(0),
        "runtime": {"torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__},
        "protocol": {
            "max_new_tokens": MAX_NEW_TOKENS,
            "context_word_counts": list(CONTEXT_WORD_COUNTS),
            "tail_repeats": TAIL_REPEATS,
            "timing": "torch.cuda.synchronize before and after each measured sample",
            "power": {"status": "pending_until_run_completes"},
        },
        "context_sweep": context_sweep(model, tokenizer),
        "tail_latency": tail_measurement(model, tokenizer),
        "concurrency": concurrency_measurement(model, tokenizer),
        "operator_data_movement_profile": operator_profile(model, tokenizer),
        "claim_boundary": {
            "allowed": "Measured GPT-2/Tesla-T4 context scaling, serialized and concurrent tail samples, and CUDA profiler rows for this protocol.",
            "refused": "Synchronized energy, analog benefit, silicon performance, and production capacity.",
        },
    }
    report["protocol"]["power"] = power_sampler.stop()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "output": str(REPORT), "device": report["device_name"], "context_rows": len(report["context_sweep"]), "profiler": report["operator_data_movement_profile"]["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
