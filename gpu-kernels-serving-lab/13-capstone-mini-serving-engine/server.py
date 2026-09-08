"""Minimal local completion server for the capstone session.

The server intentionally uses the Python standard library. It is not a production
serving engine; it gives the lab a concrete endpoint whose latency and throughput
can be measured against the rest of the artifacts.
"""

from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


class TinyGenerator:
    def __init__(self) -> None:
        self.backend = "deterministic-local"
        self.optimized_backend = "batched-prefix-cache-local"
        self.prefix_cache: dict[str, list[str]] = {}

    def complete(self, prompt: str, max_tokens: int) -> dict[str, Any]:
        words = self._tokenize(prompt)
        seed = words[-1].strip(".,:;!?").lower() if words else "token"
        generated = []
        for idx in range(max_tokens):
            generated.append(f"{seed}_{idx}")
        text = " ".join(generated)
        return {
            "text": text,
            "generated_tokens": max_tokens,
            "backend": self.backend,
        }

    def _tokenize(self, text: str) -> list[str]:
        return text.strip().split()

    def _common_prefix(self, prompts: list[str]) -> str:
        if not prompts:
            return ""
        tokenized = [self._tokenize(prompt) for prompt in prompts]
        prefix = []
        for columns in zip(*tokenized):
            if len(set(columns)) != 1:
                break
            prefix.append(columns[0])
        return " ".join(prefix)

    def complete_batch(self, prompts: list[str], max_tokens: int) -> dict[str, Any]:
        prefix = self._common_prefix(prompts)
        cached = self.prefix_cache.get(prefix)
        if cached is None:
            cached = self._tokenize(prefix)
            self.prefix_cache[prefix] = cached
        choices = []
        completion_tokens = 0
        for index, prompt in enumerate(prompts):
            # The cached prefix approximates the prefill work a serving engine can reuse.
            suffix = prompt[len(prefix) :].strip() if prefix else prompt
            words = [*cached, *self._tokenize(suffix)]
            seed = words[-1].strip(".,:;!?").lower() if words else "token"
            generated = [f"{seed}_{idx}" for idx in range(max_tokens)]
            completion_tokens += len(generated)
            choices.append({"index": index, "text": " ".join(generated), "finish_reason": "length"})
        return {
            "choices": choices,
            "completion_tokens": completion_tokens,
            "prefix_tokens_reused": len(cached) * max(0, len(prompts) - 1),
            "backend": self.optimized_backend,
        }


GENERATOR = TinyGenerator()
ADMISSION = None
MICRO_BATCH = None


def validate_request(body, *, batch):
    """Bound teaching requests before either backend performs work."""
    if not isinstance(body, dict):
        raise ValueError("request must be a JSON object")
    count = body.get("max_tokens", 16)
    if type(count) is not int or not 1 <= count <= 128:
        raise ValueError("max_tokens must be an integer from 1 to 128")
    prompts = body.get("prompts") if batch else [body.get("prompt")]
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 16:
        raise ValueError("prompts must be a list of 1 to 16 strings")
    if any(not isinstance(p, str) or not 1 <= len(p) <= 4096 for p in prompts):
        raise ValueError("each prompt must contain 1 to 4096 characters")
    return prompts, count


class Handler(BaseHTTPRequestHandler):
    server_version = "GpuServingLabMini/0.1"

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, _format: str, *_args: Any) -> None:
        return

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok", "backend": GENERATOR.backend})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        lease = None
        try:
            if self.path not in {"/v1/completions", "/v1/batch_completions", "/v1/stream"}:
                self._json(404, {"error": "not found"})
                return
            if self.headers.get("Transfer-Encoding"):
                raise ValueError("transfer encoding is unsupported; use Content-Length")
            length = int(self.headers.get("Content-Length", "0"))
            if not 1 <= length <= 65536:
                raise ValueError("Content-Length must be between 1 and 65536 bytes")
            self.connection.settimeout(10)
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            prompts, max_tokens = validate_request(body, batch=self.path == "/v1/batch_completions")
            if ADMISSION is not None:
                lease = ADMISSION.acquire()
                if lease is None:
                    self._json(429, {"error": "admission_queue_full", "admission": ADMISSION.snapshot()})
                    return
            if self.path == "/v1/stream":
                started = time.perf_counter()
                stream = GENERATOR.stream(prompts[0], max_tokens) if hasattr(GENERATOR, "stream") else (
                    {"index": index, "token": token} for index, token in enumerate(GENERATOR.complete(prompts[0], max_tokens)["text"])
                )
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                for event in stream:
                    payload = json.dumps({**event, "elapsed_ms": round((time.perf_counter() - started) * 1000, 4)})
                    self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                    self.wfile.flush()
                self.wfile.write(b"data: [DONE]\n\n")
                self.wfile.flush()
                return
            if self.path == "/v1/batch_completions":
                started = time.perf_counter()
                completion = GENERATOR.complete_batch(prompts, max_tokens)
                elapsed_ms = (time.perf_counter() - started) * 1000
                self._json(
                    200,
                    {
                        "id": "gpu-lab-local-batch-completion",
                        "object": "text_completion.batch",
                        "model": getattr(GENERATOR, "model_name", "gpu-lab-deterministic-local"),
                        "choices": completion["choices"],
                        "usage": {
                            "prompt_count": len(prompts),
                            "completion_tokens": completion["completion_tokens"],
                            "prefix_tokens_reused": completion["prefix_tokens_reused"],
                        },
                        "batch_mode": completion.get("batch_mode", "unknown"),
                        "backend": completion["backend"],
                        "server_compute_ms": round(elapsed_ms, 4),
                        "admission_queue_wait_ms": round(lease.queue_wait_ms, 4) if lease else 0.0,
                    },
                )
                return
            if self.path != "/v1/completions":
                self._json(404, {"error": "not found"})
                return
            prompt = prompts[0]
            started = time.perf_counter()
            if MICRO_BATCH is not None:
                try:
                    scheduled = MICRO_BATCH.submit(prompt, max_tokens).result(timeout=10)
                except Exception as exc:
                    # queue.Full is deliberately surfaced as bounded HTTP
                    # backpressure; other scheduler errors remain server errors.
                    import queue
                    if isinstance(exc, queue.Full):
                        self._json(429, {"error": "microbatch_queue_full", "scheduler": MICRO_BATCH.snapshot()})
                        return
                    raise
                completion = {"text": scheduled["text"], "generated_tokens": len(scheduled["text"]),
                              "prompt_tokens": len(prompt), "backend": getattr(GENERATOR, "backend", "microbatch"),
                              "batch_mode": scheduled.get("batch_mode", "unknown")}
            else:
                completion = GENERATOR.complete(prompt, max_tokens)
            elapsed_ms = (time.perf_counter() - started) * 1000
            self._json(
                200,
                {
                    "id": "gpu-lab-local-completion",
                    "object": "text_completion",
                    "model": getattr(GENERATOR, "model_name", "gpu-lab-deterministic-local"),
                    "choices": [{"index": 0, "text": completion["text"], "finish_reason": "length"}],
                    "usage": {
                        "prompt_tokens_estimate": completion.get("prompt_tokens", len(prompt.split())),
                        "completion_tokens": completion["generated_tokens"],
                        "total_tokens_estimate": completion.get("prompt_tokens", len(prompt.split())) + completion["generated_tokens"],
                    },
                    "backend": completion["backend"],
                    "batch_mode": completion.get("batch_mode", "direct"),
                    "server_compute_ms": round(elapsed_ms, 4),
                    "admission_queue_wait_ms": round(lease.queue_wait_ms, 4) if lease else 0.0,
                },
            )
        except (ValueError, TypeError) as exc:
            self._json(400, {"error": str(exc)})
        except Exception as exc:
            self._json(500, {"error": repr(exc)})
        finally:
            if lease is not None and ADMISSION is not None:
                ADMISSION.release()


def main() -> None:
    global GENERATOR, MICRO_BATCH
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--backend", choices=("deterministic", "neural"), default="deterministic")
    parser.add_argument("--microbatch", action="store_true", help="enable bounded arrival-window neural microbatching")
    parser.add_argument("--microbatch-max-pending", type=int, default=64)
    args = parser.parse_args()
    if args.backend == "neural":
        import torch
        from neural_generator import NeuralGenerator
        torch.set_num_threads(1)
        GENERATOR = NeuralGenerator()
    if args.microbatch:
        if args.backend != "neural":
            parser.error("--microbatch requires --backend neural")
        from microbatch import MicroBatchScheduler
        MICRO_BATCH = MicroBatchScheduler(GENERATOR, max_pending=args.microbatch_max_pending)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"serving http://{args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
