#!/usr/bin/env python3
"""Compare uncached and KV-cached decode through the HTTP serving path."""

from __future__ import annotations

import hashlib
import json
import queue
import statistics
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT if (ROOT / "gpu-kernels-serving-lab").exists() else ROOT.parent
SERVING = REPO / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
import server  # noqa: E402
from microbatch import MicroBatchScheduler  # noqa: E402
from neural_generator import NeuralGenerator  # noqa: E402

REPORT = HERE / "reports" / "serving-bridge.json"
WORKLOADS = (
    {"id": "short-context", "prompt": "attention cache", "max_tokens": 12},
    {"id": "long-context", "prompt": "attention cache " * 5, "max_tokens": 24},
    {"id": "long-decode", "prompt": "attention cache", "max_tokens": 96},
)
CONCURRENCIES = (1, 2, 4)
REQUESTS_PER_LEVEL = 8
MODEL_HIDDEN = 128
MODEL_HEADS = 8
GRAPH_POOL_SIZE = 4


class DecodeModeGenerator:
    def __init__(self, mode: str, device: str):
        self.mode = mode
        self.backend = f"neural-{mode}-decode"
        if mode == "cuda_graph":
            self._graph_workers = [NeuralGenerator(device, hidden=MODEL_HIDDEN, heads=MODEL_HEADS) for _ in range(GRAPH_POOL_SIZE)]
            self._graph_slots = queue.Queue()
            for index in range(GRAPH_POOL_SIZE):
                self._graph_slots.put(index)
            self.inner = self._graph_workers[0]
        else:
            self.inner = NeuralGenerator(device, hidden=MODEL_HIDDEN, heads=MODEL_HEADS)
            self._graph_workers = []
            self._graph_slots = None
        self.model_name = self.inner.model_name
        self._graph_bucket_keys = set()
        self._graph_batch_keys = set()

    @property
    def graph_pool_size(self) -> int:
        return len(self._graph_workers)

    def encode(self, prompt: str):
        return self.inner.encode(prompt)

    def prepare(self, workloads) -> None:
        self._graph_bucket_keys = {(workload["prompt"], workload["max_tokens"]) for workload in workloads}
        self._graph_batch_keys = set()
        if self.mode == "cuda_graph_microbatch":
            for workload in workloads:
                # Warm the singleton bucket explicitly so request timings do
                # not include first-use CUDA graph capture.
                self.inner.generate(
                    workload["prompt"], workload["max_tokens"],
                    cached=True, cache_storage="cuda_graph",
                )
                for batch_size in (2, GRAPH_POOL_SIZE):
                    prompts = [workload["prompt"]] * batch_size
                    self.inner.generate_batch_cuda_graph(prompts, workload["max_tokens"])
                    self._graph_batch_keys.add((tuple(prompts), workload["max_tokens"]))
        for worker in self._graph_workers:
            for workload in workloads:
                worker.generate(workload["prompt"], workload["max_tokens"], cached=True, cache_storage="cuda_graph")

    def complete_batch(self, prompts: list[str], max_tokens: int) -> dict:
        if self.mode not in {"microbatch", "cuda_graph_microbatch"}:
            raise RuntimeError("complete_batch is only enabled for microbatch mode")
        graph_batch = self.mode == "cuda_graph_microbatch" and (tuple(prompts), max_tokens) in self._graph_batch_keys
        if graph_batch:
            generated = self.inner.generate_batch_cuda_graph(prompts, max_tokens)
        else:
            generated = self.inner.generate_batch(prompts, max_tokens, cached=True)
        return {
            "choices": [
                {"index": index, "text": "".join(self.inner.model.alphabet[token] for token in tokens), "finish_reason": "length"}
                for index, tokens in enumerate(generated)
            ],
            "completion_tokens": len(prompts) * max_tokens,
            "prefix_tokens_reused": 0,
            "batch_mode": "cuda-graph-vectorized" if graph_batch else "vectorized",
            "backend": self.backend,
        }

    def complete(self, prompt: str, max_tokens: int) -> dict:
        if self.mode == "cuda_graph":
            # Each slot owns static batch-1 addresses and its own graph bucket.
            # The bounded pool permits concurrent requests without racing a
            # single graph's mutable cache/input buffers.
            slot = self._graph_slots.get()
            try:
                worker = self._graph_workers[slot]
                graph_hit = (prompt, max_tokens) in self._graph_bucket_keys
                generated, _ = worker.generate(
                    prompt, max_tokens, cached=True,
                    cache_storage="cuda_graph" if graph_hit else "preallocated",
                )
            finally:
                self._graph_slots.put(slot)
            model = worker.model
            backend = self.backend if graph_hit else f"{self.backend}-fallback"
        else:
            graph_bucket = self.mode == "cuda_graph_microbatch" and (prompt, max_tokens) in self._graph_bucket_keys
            generated, _ = self.inner.generate(
                prompt, max_tokens, cached=self.mode != "uncached",
                cache_storage="cuda_graph" if graph_bucket else ("preallocated" if self.mode in {"preallocated", "microbatch", "cuda_graph_microbatch"} else "dynamic"),
            )
            model = self.inner.model
            backend = self.backend if graph_bucket or self.mode != "cuda_graph_microbatch" else f"{self.backend}-fallback"
        return {
            "text": "".join(model.alphabet[index] for index in generated),
            "generated_tokens": len(generated),
            "prompt_tokens": len(self.inner.encode(prompt)),
            "backend": backend,
        }


def _request(endpoint: str, prompt: str, max_tokens: int) -> dict:
    body = json.dumps({"prompt": prompt, "max_tokens": max_tokens}).encode()
    request = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return {"latency_ms": (time.perf_counter() - started) * 1000.0, "payload": payload}


def _serving_candidate_search(reference: dict, candidates: dict[str, dict]) -> dict:
    """Select the fastest parity-preserving serving backend for one bucket."""
    rows = []
    reference_outputs = reference["output_texts"]
    for candidate_id, candidate in candidates.items():
        output_parity = candidate["output_texts"] == reference_outputs
        rows.append({
            "candidate_id": candidate_id,
            "latency_ms_median": candidate["latency_ms_median"],
            "output_parity": output_parity,
            "accepted": output_parity and candidate["accepted"] == reference["accepted"],
        })
    accepted = [row for row in rows if row["accepted"]]
    selected = min(accepted, key=lambda row: row["latency_ms_median"]) if accepted else None
    return {"candidates": rows, "selected": selected["candidate_id"] if selected else None}


def _run_mode(mode: str, device: str) -> dict:
    previous = server.GENERATOR, server.ADMISSION, server.MICRO_BATCH
    mode_generator = DecodeModeGenerator(mode, device)
    server.GENERATOR = mode_generator
    server.ADMISSION = None
    server.MICRO_BATCH = None
    scheduler = None
    if mode == "microbatch":
        scheduler = MicroBatchScheduler(mode_generator, max_batch=4, window_ms=3.0, max_pending=64)
        server.MICRO_BATCH = scheduler
    if mode == "cuda_graph_microbatch":
        scheduler = MicroBatchScheduler(mode_generator, max_batch=4, window_ms=3.0, max_pending=64)
        server.MICRO_BATCH = scheduler
    http = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    endpoint = f"http://127.0.0.1:{http.server_port}/v1/completions"
    rows = []
    fallback_probe = None
    try:
        server.GENERATOR.prepare(WORKLOADS)
        if mode == "cuda_graph":
            fallback_payload = _request(endpoint, "decode step", 13)["payload"]
            fallback_probe = {
                "backend": fallback_payload.get("backend"),
                "text_nonempty": bool(fallback_payload.get("choices", [{}])[0].get("text")),
                "used_eager_fallback": str(fallback_payload.get("backend", "")).endswith("-fallback"),
            }
        for workload in WORKLOADS:
            prompt = workload["prompt"]
            max_tokens = workload["max_tokens"]
            expected = server.GENERATOR.complete(prompt, max_tokens)["text"]
            for concurrency in CONCURRENCIES:
                prompts = [prompt for _ in range(REQUESTS_PER_LEVEL)]
                started = time.perf_counter()
                with ThreadPoolExecutor(max_workers=concurrency) as pool:
                    results = list(pool.map(lambda item: _request(endpoint, item[0], item[1]), [(p, max_tokens) for p in prompts]))
                wave_ms = (time.perf_counter() - started) * 1000.0
                rows.append({
                    "workload": workload["id"],
                    "prompt_tokens": len(server.GENERATOR.inner.encode(prompt)),
                    "max_tokens": max_tokens,
                    "concurrency": concurrency,
                    "request_count": len(results),
                    "accepted": len(results),
                    "wave_elapsed_ms": wave_ms,
                    "latency_ms_samples": [row["latency_ms"] for row in results],
                    "latency_ms_median": float(statistics.median(row["latency_ms"] for row in results)),
                    "output_texts": [row["payload"]["choices"][0]["text"] for row in results],
                    "output_parity": all(row["payload"]["choices"][0]["text"] == server.GENERATOR.complete(prompts[index], max_tokens)["text"] for index, row in enumerate(results)),
                    "backend_labels": sorted({row["payload"].get("backend") for row in results}),
                    "batch_modes": sorted({row["payload"].get("batch_mode") for row in results}),
                    "expected_probe_nonempty": bool(expected),
                })
    finally:
        http.shutdown()
        http.server_close()
        thread.join(timeout=10)
        if scheduler is not None:
            scheduler.close()
        server.GENERATOR, server.ADMISSION, server.MICRO_BATCH = previous
    return {"mode": mode, "rows": rows, "graph_pool_size": mode_generator.graph_pool_size, "fallback_probe": fallback_probe,
            "scheduler": scheduler.snapshot() if scheduler is not None else None}


def main() -> int:
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        uncached = _run_mode("uncached", device)
        cached = _run_mode("cached", device)
        preallocated = _run_mode("preallocated", device)
        microbatch = _run_mode("microbatch", device)
        cuda_graph_microbatch = _run_mode("cuda_graph_microbatch", device) if device == "cuda" else None
        cuda_graph = _run_mode("cuda_graph", device) if device == "cuda" else None
        checks = {
            "all_requests_completed": all(row["accepted"] == REQUESTS_PER_LEVEL for mode in (uncached, cached, preallocated, microbatch, cuda_graph_microbatch, cuda_graph) if mode is not None for row in mode["rows"]),
            "all_outputs_nonempty": all(row["expected_probe_nonempty"] for mode in (uncached, cached, preallocated, microbatch, cuda_graph_microbatch, cuda_graph) if mode is not None for row in mode["rows"]),
            "all_backend_labels_present": all(row["backend_labels"] for mode in (uncached, cached, preallocated, microbatch, cuda_graph_microbatch, cuda_graph) if mode is not None for row in mode["rows"]),
            "concurrency_levels_present": [row["concurrency"] for row in cached["rows"]] == list(CONCURRENCIES) * len(WORKLOADS),
            "microbatch_vectorized_observed": any("vectorized" in row["batch_modes"] for row in microbatch["rows"]),
        }
        for left, right in zip(uncached["rows"], cached["rows"]):
            left_payloads = left["backend_labels"]
            right_payloads = right["backend_labels"]
            key = f"{left['workload']}_{left['concurrency']}"
            checks[f"backend_pair_{key}"] = bool(left_payloads and right_payloads)
            checks[f"cross_mode_output_parity_{key}"] = left["output_texts"] == right["output_texts"]
        for left, right in zip(uncached["rows"], preallocated["rows"]):
            key = f"{left['workload']}_{left['concurrency']}"
            checks[f"preallocated_backend_pair_{key}"] = bool(left["backend_labels"] and right["backend_labels"])
            checks[f"uncached_preallocated_output_parity_{key}"] = left["output_texts"] == right["output_texts"]
        if cuda_graph is not None:
            for left, right in zip(uncached["rows"], cuda_graph["rows"]):
                key = f"{left['workload']}_{left['concurrency']}"
                checks[f"cuda_graph_backend_pair_{key}"] = bool(left["backend_labels"] and right["backend_labels"])
                checks[f"uncached_cuda_graph_output_parity_{key}"] = left["output_texts"] == right["output_texts"]
            checks["cuda_graph_dynamic_fallback"] = bool(
                cuda_graph.get("fallback_probe", {}).get("used_eager_fallback")
                and cuda_graph.get("fallback_probe", {}).get("text_nonempty")
            )
        for left, right in zip(uncached["rows"], microbatch["rows"]):
            key = f"{left['workload']}_{left['concurrency']}"
            checks[f"microbatch_output_parity_{key}"] = left["output_texts"] == right["output_texts"]
        if cuda_graph_microbatch is not None:
            checks["cuda_graph_microbatch_vectorized_observed"] = any("cuda-graph-vectorized" in row["batch_modes"] for row in cuda_graph_microbatch["rows"])
            for left, right in zip(uncached["rows"], cuda_graph_microbatch["rows"]):
                key = f"{left['workload']}_{left['concurrency']}"
                checks[f"cuda_graph_microbatch_output_parity_{key}"] = left["output_texts"] == right["output_texts"]
        mode_reports = {
            "cached": cached, "preallocated": preallocated, "microbatch": microbatch,
        }
        if cuda_graph is not None:
            mode_reports["cuda_graph"] = cuda_graph
        if cuda_graph_microbatch is not None:
            mode_reports["cuda_graph_microbatch"] = cuda_graph_microbatch
        serving_search = []
        for reference in uncached["rows"]:
            key = (reference["workload"], reference["concurrency"])
            candidates = {
                mode: next(row for row in report["rows"] if (row["workload"], row["concurrency"]) == key)
                for mode, report in mode_reports.items()
            }
            serving_search.append({
                "workload": reference["workload"],
                "concurrency": reference["concurrency"],
                **_serving_candidate_search(reference, candidates),
            })
        checks["serving_search_candidates_accepted"] = all(
            candidate["accepted"] for bucket in serving_search for candidate in bucket["candidates"]
        )
        checks["serving_search_selection_present"] = all(bucket["selected"] for bucket in serving_search)
        report = {
            "experiment": "batch1_decode_serving_bridge",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "passed" if all(checks.values()) else "failed",
            "evidence_kind": "measured_gpu" if device == "cuda" else "measured_cpu",
            "device": device,
            "gpu_execution_accepted": device == "cuda" and all(checks.values()),
            "protocol": {"workloads": list(WORKLOADS), "model_hidden": MODEL_HIDDEN, "model_heads": MODEL_HEADS, "graph_pool_size": GRAPH_POOL_SIZE, "concurrency_levels": list(CONCURRENCIES), "requests_per_level": REQUESTS_PER_LEVEL},
            "uncached": uncached,
            "cached": cached,
            "preallocated": preallocated,
            "microbatch": microbatch,
            "cuda_graph_microbatch": cuda_graph_microbatch,
            "cuda_graph": cuda_graph,
            "serving_candidate_search": serving_search,
            "checks": checks,
            "timing_scope": "loopback HTTP request wall latency including server dispatch and autoregressive generation; excludes client queue wait outside the request",
            "limitations": ["untrained character model", "same-process loopback", "CPU result is not a GPU throughput claim", "no production capacity claim", "microbatching is a separate follow-up comparison"],
            "source_sha256": {str(path.relative_to(REPO)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__).resolve(), SERVING / "server.py", SERVING / "neural_generator.py", SERVING / "microbatch.py")},
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "evidence_kind": report["evidence_kind"], "device": device, "checks": checks}, indent=2))
        return 0 if report["status"] == "passed" else 1
    finally:
        torch.set_num_threads(previous_threads)


if __name__ == "__main__":
    raise SystemExit(main())
