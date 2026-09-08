#!/usr/bin/env python3
"""Bounded streaming-token contract for the neural teaching server."""
from __future__ import annotations

import hashlib
import json
import sys
import threading
import time
import urllib.request
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERVING_DIR = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING_DIR))
import server  # noqa: E402
from neural_generator import NeuralGenerator  # noqa: E402

OUT = HERE / "reports" / "serving-streaming-cpu.json"


def main():
    previous = server.GENERATOR
    generator = NeuralGenerator("cpu")
    server.GENERATOR = generator
    http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    worker = threading.Thread(target=http.serve_forever, daemon=True)
    worker.start()
    endpoint = f"http://127.0.0.1:{http.server_port}/v1/stream"
    prompt, max_tokens = "hello gpu", 8
    expected = generator.complete(prompt, max_tokens)["text"]
    rows = []
    try:
        for repeat in range(3):
            body = json.dumps({"prompt": prompt, "max_tokens": max_tokens}).encode()
            request = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
            started = time.perf_counter()
            token_events = []
            done = False
            with urllib.request.urlopen(request, timeout=30) as response:
                for raw in response:
                    line = raw.decode().strip()
                    if not line.startswith("data: "):
                        continue
                    payload = line[6:]
                    if payload == "[DONE]":
                        done = True
                        continue
                    event = json.loads(payload)
                    event["client_elapsed_ms"] = (time.perf_counter() - started) * 1000
                    token_events.append(event)
            token_text = "".join(event["token"] for event in token_events)
            times = [event["client_elapsed_ms"] for event in token_events]
            rows.append({
                "repeat": repeat,
                "status": response.status,
                "token_count": len(token_events),
                "text_matches_direct": token_text == expected,
                "done_marker": done,
                "first_token_ms": times[0] if times else None,
                "inter_token_ms": [right - left for left, right in zip(times, times[1:])],
                "total_ms": times[-1] if times else None,
            })
    finally:
        http.shutdown(); http.server_close(); worker.join(timeout=5); server.GENERATOR = previous
    checks = {
        "all_http_200": all(row["status"] == 200 for row in rows),
        "token_counts": all(row["token_count"] == max_tokens for row in rows),
        "direct_parity": all(row["text_matches_direct"] for row in rows),
        "done_markers": all(row["done_marker"] for row in rows),
        "timing_present": all(row["first_token_ms"] is not None and row["total_ms"] is not None for row in rows),
    }
    report = {
        "experiment": "serving_streaming_cpu",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "passed" if all(checks.values()) else "failed",
        "measured": True,
        "gpu_execution_accepted": False,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "repeats": len(rows),
        "checks": checks,
        "rows": rows,
        "median_first_token_ms": median(row["first_token_ms"] for row in rows),
        "median_total_ms": median(row["total_ms"] for row in rows),
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__), SERVING_DIR / "server.py", SERVING_DIR / "neural_generator.py")},
        "scope": "same-process CPU loopback SSE-style token stream; parity and timing contract, not production streaming capacity or GPU token timing",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n"); print(json.dumps({"status": report["status"], "checks": checks}, indent=2)); return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
