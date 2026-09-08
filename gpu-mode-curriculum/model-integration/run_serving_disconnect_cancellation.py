#!/usr/bin/env python3
"""Verify that a disconnected HTTP client cancels queued serving work."""
from __future__ import annotations

import hashlib
import json
import socket
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
import server  # noqa: E402
from microbatch import MicroBatchScheduler  # noqa: E402

OUT = HERE / "reports" / "serving-disconnect-cancellation-cpu.json"


class SlowGenerator:
    backend = "disconnect-probe"
    model_name = "disconnect-probe"

    def __init__(self):
        self.started = threading.Event()
        self.second_started = threading.Event()
        self.cancel_observed = threading.Event()
        self.calls = 0

    def encode(self, prompt):
        return list(prompt)

    def complete(self, prompt, max_tokens, *, cancel_event=None):
        self.calls += 1
        if self.calls == 1:
            self.started.set()
        else:
            self.second_started.set()
        for _ in range(300):
            if cancel_event is not None and cancel_event.is_set():
                self.cancel_observed.set()
                raise RuntimeError("backend observed cancellation")
            time.sleep(0.001)
        return {"text": f"{prompt}:ok", "generated_tokens": max_tokens, "backend": self.backend}

    def complete_batch(self, prompts, max_tokens):
        self.started.set()
        time.sleep(0.15)
        return {"choices": [{"text": f"{prompt}:ok"} for prompt in prompts],
                "batch_mode": "vectorized", "backend": self.backend}


def first_request(endpoint: str, result: dict) -> None:
    body = json.dumps({"prompt": "blocking", "max_tokens": 2}).encode()
    request = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=10) as response:
        result.update(json.load(response))


def main() -> int:
    previous = server.GENERATOR, server.ADMISSION, server.MICRO_BATCH
    generator = SlowGenerator()
    scheduler = MicroBatchScheduler(generator, max_batch=1, window_ms=0.0, max_pending=4)
    server.GENERATOR, server.ADMISSION, server.MICRO_BATCH = generator, None, scheduler
    http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    endpoint = f"http://127.0.0.1:{http.server_port}/v1/completions"
    first_result: dict = {}
    first_thread = threading.Thread(target=first_request, args=(endpoint, first_result), daemon=True)
    first_thread.start()
    try:
        started = generator.started.wait(timeout=5)
        # The first request occupies the worker.  The second request is sent
        # over a raw socket, allowed to enter execution, then disconnected.
        request_body = json.dumps({"prompt": "abandoned", "max_tokens": 2}).encode()
        raw = socket.create_connection(("127.0.0.1", http.server_port), timeout=2)
        raw.sendall((f"POST /v1/completions HTTP/1.1\r\nHost: localhost\r\n"
                     f"Content-Type: application/json\r\nContent-Length: {len(request_body)}\r\n"
                     f"Connection: close\r\n\r\n").encode() + request_body)
        if not generator.second_started.wait(timeout=10):
            raise RuntimeError("second request did not start")
        raw.close()
        deadline = time.perf_counter() + 2
        while time.perf_counter() < deadline and scheduler.snapshot()["cancelled_count"] < 1:
            time.sleep(0.005)
        first_thread.join(timeout=5)
        snapshot = scheduler.snapshot()
        checks = {
            "first_request_started": started,
            "first_request_completed": first_result.get("choices", [{}])[0].get("text") == "blocking:ok",
            "second_request_started": generator.second_started.is_set(),
            "backend_observed_cancellation": generator.cancel_observed.is_set(),
            "disconnect_cancellation_recorded": snapshot["inflight_cancelled_count"] >= 1,
            "abandoned_request_not_completed": not any(row.get("prompt_length") == len("abandoned") for row in snapshot["batches"]),
        }
        report = {
            "experiment": "serving_disconnect_cancellation_cpu",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "passed" if all(checks.values()) else "failed",
            "measured": True,
            "gpu_execution_accepted": False,
            "checks": checks,
            "scheduler": snapshot,
            "scope": "same-process loopback HTTP with a real disconnected socket and cooperative backend; in-flight cancellation is measured for this backend, not forced interruption of arbitrary accelerator kernels or a production capacity claim",
            "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in (Path(__file__).resolve(), SERVING / "server.py", SERVING / "microbatch.py")},
        }
    finally:
        http.shutdown(); http.server_close(); thread.join(timeout=10)
        scheduler.close()
        server.GENERATOR, server.ADMISSION, server.MICRO_BATCH = previous
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "checks": report["checks"]}, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
