#!/usr/bin/env python3
"""Bounded admission/queue contract for the teaching neural HTTP backend."""
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
SERVING_DIR = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING_DIR))
import server  # noqa: E402
from admission import AdmissionController  # noqa: E402

OUT = HERE / "reports" / "serving-admission-cpu.json"


class SlowProbeGenerator:
    backend = "admission-probe"
    model_name = "admission-probe"

    def complete(self, prompt, max_tokens):
        time.sleep(0.08)
        return {"text": "ok", "generated_tokens": max_tokens, "prompt_tokens": len(prompt), "backend": self.backend}


def request(endpoint, index):
    body = json.dumps({"prompt": f"request-{index}", "max_tokens": 2}).encode()
    req = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            payload = json.load(response)
            return {"index": index, "status": response.status, "seconds": time.perf_counter() - started, "payload": payload}
    except urllib.error.HTTPError as error:
        payload = json.loads(error.read().decode())
        return {"index": index, "status": error.code, "seconds": time.perf_counter() - started, "payload": payload}


def main():
    previous_generator, previous_admission = server.GENERATOR, server.ADMISSION
    server.GENERATOR = SlowProbeGenerator()
    server.ADMISSION = AdmissionController(capacity=1, queue_limit=2)
    http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    worker = threading.Thread(target=http.serve_forever, daemon=True)
    worker.start()
    endpoint = f"http://127.0.0.1:{http.server_port}/v1/completions"
    try:
        with ThreadPoolExecutor(max_workers=8) as pool:
            rows = list(pool.map(lambda index: request(endpoint, index), range(8)))
    finally:
        http.shutdown(); http.server_close(); worker.join(timeout=5)
        server.GENERATOR, server.ADMISSION = previous_generator, previous_admission
    accepted = [row for row in rows if row["status"] == 200]
    rejected = [row for row in rows if row["status"] == 429]
    checks = {
        "bounded_admission_observed": 1 <= len(accepted) <= 8 and 1 <= len(rejected) <= 7,
        "rejected_when_queue_full": len(rejected) >= 1,
        "accepted_payloads_valid": all(row["payload"].get("choices", [{}])[0].get("text") == "ok" for row in accepted),
        "rejections_identified": all(row["payload"].get("error") == "admission_queue_full" for row in rejected),
        "queue_wait_recorded": any(row["payload"].get("admission_queue_wait_ms", 0) > 0 for row in accepted),
    }
    report = {
        "experiment": "serving_admission_queue_cpu",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if all(checks.values()) else "failed",
        "measured": True,
        "gpu_execution_accepted": False,
        "capacity": 1,
        "queue_limit": 2,
        "request_count": 8,
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "checks": checks,
        "rows": rows,
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__), SERVING_DIR / "server.py", SERVING_DIR / "admission.py")},
        "scope": "same-process CPU loopback server with synthetic 80-ms work; bounded admission semantics, not production capacity or GPU serving",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n"); print(json.dumps({"status": report["status"], "accepted": len(accepted), "rejected": len(rejected)}, indent=2)); return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
