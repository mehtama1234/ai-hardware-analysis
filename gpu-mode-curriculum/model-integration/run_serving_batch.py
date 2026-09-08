#!/usr/bin/env python3
"""Contract and timing probe for vectorized versus fallback neural batching."""
from __future__ import annotations

import hashlib
import json
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
from neural_generator import NeuralGenerator  # noqa: E402

OUT = HERE / "reports" / "serving-batch-cpu.json"


def post(endpoint, path, body):
    request = urllib.request.Request(endpoint + path, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.load(response)
    return payload, (time.perf_counter() - started) * 1000.0


def main():
    torch_threads = __import__("torch").get_num_threads()
    __import__("torch").set_num_threads(1)
    previous = server.GENERATOR
    generator = NeuralGenerator()
    server.GENERATOR = generator
    http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    thread = threading.Thread(target=http.serve_forever, daemon=True); thread.start()
    endpoint = f"http://127.0.0.1:{http.server_port}"
    equal_prompts = ["hello", "world", "there"]
    variable_prompts = ["hi", "attention cache"]
    try:
        vector, vector_ms = post(endpoint, "/v1/batch_completions", {"prompts": equal_prompts, "max_tokens": 6})
        fallback, fallback_ms = post(endpoint, "/v1/batch_completions", {"prompts": variable_prompts, "max_tokens": 6})
        expected_equal = [generator.complete(prompt, 6)["text"] for prompt in equal_prompts]
        expected_variable = [generator.complete(prompt, 6)["text"] for prompt in variable_prompts]
    finally:
        http.shutdown(); http.server_close(); thread.join(timeout=10); server.GENERATOR = previous
        __import__("torch").set_num_threads(torch_threads)
    checks = {
        "vectorized_mode_reported": vector.get("batch_mode") == "vectorized",
        "fallback_mode_reported": fallback.get("batch_mode") == "serial-fallback",
        "vectorized_parity": [c.get("text") for c in vector.get("choices", [])] == expected_equal,
        "fallback_parity": [c.get("text") for c in fallback.get("choices", [])] == expected_variable,
        "vectorized_shape": len(vector.get("choices", [])) == len(equal_prompts),
        "fallback_shape": len(fallback.get("choices", [])) == len(variable_prompts),
    }
    report = {
        "experiment": "serving_batch_cpu", "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if all(checks.values()) else "failed", "measured": True,
        "gpu_execution_accepted": False, "checks": checks,
        "vectorized": {"prompt_count": len(equal_prompts), "server_ms": vector.get("server_compute_ms"), "wall_ms": vector_ms, "batch_mode": vector.get("batch_mode")},
        "serial_fallback": {"prompt_count": len(variable_prompts), "server_ms": fallback.get("server_compute_ms"), "wall_ms": fallback_ms, "batch_mode": fallback.get("batch_mode")},
        "scope": "same-process CPU loopback; equal-length vectorized decode versus explicit variable-length serial fallback; no continuous admission-time batching or GPU throughput claim",
        "source_sha256": {str(path.relative_to(ROOT.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (Path(__file__).resolve(), SERVING / "neural_generator.py", SERVING / "server.py")},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "checks": checks}, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
