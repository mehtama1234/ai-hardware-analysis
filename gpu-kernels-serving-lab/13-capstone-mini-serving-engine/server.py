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
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            if self.path == "/v1/batch_completions":
                prompts = [str(p) for p in body.get("prompts", [])]
                max_tokens = int(body.get("max_tokens", 16))
                started = time.perf_counter()
                completion = GENERATOR.complete_batch(prompts, max_tokens)
                elapsed_ms = (time.perf_counter() - started) * 1000
                self._json(
                    200,
                    {
                        "id": "gpu-lab-local-batch-completion",
                        "object": "text_completion.batch",
                        "model": "gpu-lab-deterministic-local",
                        "choices": completion["choices"],
                        "usage": {
                            "prompt_count": len(prompts),
                            "completion_tokens": completion["completion_tokens"],
                            "prefix_tokens_reused": completion["prefix_tokens_reused"],
                        },
                        "backend": completion["backend"],
                        "server_compute_ms": round(elapsed_ms, 4),
                    },
                )
                return
            if self.path != "/v1/completions":
                self._json(404, {"error": "not found"})
                return
            prompt = str(body.get("prompt", ""))
            max_tokens = int(body.get("max_tokens", 16))
            started = time.perf_counter()
            completion = GENERATOR.complete(prompt, max_tokens)
            elapsed_ms = (time.perf_counter() - started) * 1000
            self._json(
                200,
                {
                    "id": "gpu-lab-local-completion",
                    "object": "text_completion",
                    "model": "gpu-lab-deterministic-local",
                    "choices": [{"index": 0, "text": completion["text"], "finish_reason": "length"}],
                    "usage": {
                        "prompt_tokens_estimate": len(prompt.split()),
                        "completion_tokens": completion["generated_tokens"],
                        "total_tokens_estimate": len(prompt.split()) + completion["generated_tokens"],
                    },
                    "backend": completion["backend"],
                    "server_compute_ms": round(elapsed_ms, 4),
                },
            )
        except Exception as exc:
            self._json(500, {"error": repr(exc)})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"serving http://{args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
