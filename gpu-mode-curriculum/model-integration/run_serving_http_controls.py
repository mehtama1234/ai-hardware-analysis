#!/usr/bin/env python3
"""HTTP-level opt-in microbatch and bounded queue contract."""
from __future__ import annotations

import hashlib
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
import server  # noqa: E402
from microbatch import MicroBatchScheduler  # noqa: E402

OUT = HERE / "reports" / "serving-http-controls-cpu.json"


class SlowGenerator:
    backend = "http-control-probe"
    model_name = "http-control-probe"

    def encode(self, prompt): return list(prompt)
    def complete(self, prompt, max_tokens):
        time.sleep(0.05); return {"text": f"{prompt}:ok", "generated_tokens": max_tokens, "prompt_tokens": len(prompt), "backend": self.backend}
    def complete_batch(self, prompts, max_tokens):
        time.sleep(0.05); return {"choices": [{"text": f"{p}:ok"} for p in prompts], "batch_mode": "vectorized", "backend": self.backend}


def request(endpoint, index):
    body = json.dumps({"prompt": f"request-{index}", "max_tokens": 2}).encode()
    req = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode())


def main():
    previous = server.GENERATOR, server.ADMISSION, server.MICRO_BATCH
    server.GENERATOR = SlowGenerator(); server.ADMISSION = None
    server.MICRO_BATCH = MicroBatchScheduler(server.GENERATOR, max_batch=2, window_ms=3.0, max_pending=3)
    http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler); thread = threading.Thread(target=http.serve_forever, daemon=True); thread.start()
    endpoint = f"http://127.0.0.1:{http.server_port}/v1/completions"
    try:
        with ThreadPoolExecutor(max_workers=8) as pool:
            rows = list(pool.map(lambda i: request(endpoint, i), range(8)))
    finally:
        http.shutdown(); http.server_close(); thread.join(timeout=10)
        scheduler_snapshot = server.MICRO_BATCH.snapshot(); server.MICRO_BATCH.close(); server.GENERATOR, server.ADMISSION, server.MICRO_BATCH = previous
    accepted = [payload for status, payload in rows if status == 200]; rejected = [payload for status, payload in rows if status == 429]
    checks = {
        "accepted_outputs_valid": all(payload.get("choices", [{}])[0].get("text", "").endswith(":ok") for payload in accepted),
        "vectorized_mode_observed": any(payload.get("batch_mode") == "vectorized" for payload in accepted),
        "queue_rejection_observed": len(rejected) >= 1,
        "rejection_identity": all(payload.get("error") == "microbatch_queue_full" for payload in rejected),
        "scheduler_capacity_preserved": scheduler_snapshot.get("max_pending") == 3,
    }
    report = {"experiment": "serving_http_controls_cpu", "generated_at": datetime.now(timezone.utc).isoformat(),
              "status": "passed" if all(checks.values()) else "failed", "measured": True, "gpu_execution_accepted": False,
              "request_count": len(rows), "accepted_count": len(accepted), "rejected_count": len(rejected), "checks": checks,
              "scheduler": scheduler_snapshot, "scope": "same-process loopback HTTP with opt-in bounded microbatch scheduler and synthetic slow backend; no production tail or GPU claim",
              "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__).resolve(), SERVING / "server.py", SERVING / "microbatch.py")}}
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "accepted": len(accepted), "rejected": len(rejected), "checks": checks}, indent=2)); return 0 if report["status"] == "passed" else 1


if __name__ == "__main__": raise SystemExit(main())
