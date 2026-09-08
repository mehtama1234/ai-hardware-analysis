"""Bounded loopback HTTP load experiment with actual neural generation.

Client and server share a process/CPU. This is not isolated production capacity,
streaming TTFT, trained-model quality, GPU performance or open-loop arrival load.
"""
import json
import math
from pathlib import Path
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from statistics import median
import urllib.request

import torch
import server
from neural_generator import NeuralGenerator

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
from common.provenance import source_provenance


def run():
    previous, threads = server.GENERATOR, torch.get_num_threads()
    torch.set_num_threads(1)
    generator = NeuralGenerator()
    server.GENERATOR = generator
    prompts = ["hello gpu", "attention cache", "decode step", "memory traffic"] * 2
    expected = {p: generator.complete(p, 8)["text"] for p in set(prompts)}
    http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    worker = threading.Thread(target=http.serve_forever, daemon=True)
    worker.start()
    endpoint = f"http://127.0.0.1:{http.server_port}/v1/completions"

    def request(prompt):
        body = json.dumps({"prompt": prompt, "max_tokens": 8}).encode()
        req = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
        start = time.perf_counter()
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.load(response)
        elapsed = time.perf_counter() - start
        correct = (result["choices"][0]["text"] == expected[prompt]
                   and result["usage"]["completion_tokens"] == 8
                   and result["backend"] == generator.backend)
        return {"prompt": prompt, "text": result["choices"][0]["text"],
                "seconds": elapsed, "server_compute_ms": result["server_compute_ms"],
                "correct": correct}

    rows = []
    try:
        request(prompts[0])  # HTTP warmup, excluded from samples.
        for concurrency in (1, 2, 4):
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                start = time.perf_counter()
                samples = list(pool.map(request, prompts))
                wall = time.perf_counter() - start
            times = sorted(s["seconds"] for s in samples)
            rows.append({"client_concurrency": concurrency, "requests": len(samples),
                         "samples": samples, "wall_seconds": wall,
                         "median_request_seconds": median(times),
                         "p95_request_seconds_nearest_rank": times[math.ceil(.95 * len(times)) - 1],
                         "completed_output_tokens_per_second": 8 * len(samples) / wall,
                         "correct": all(s["correct"] for s in samples)})
    finally:
        http.shutdown()
        http.server_close()
        worker.join(timeout=10)
        server.GENERATOR = previous
        torch.set_num_threads(threads)
    return {"generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "passed" if all(r["correct"] for r in rows) else "failed",
            "rows": rows, "model_trained": False, "gpu_execution_accepted": False,
            "torch_version": torch.__version__, "intraop_threads_during_run": 1,
            "scope": "same-process loopback CPU, 8 requests per concurrency; closed-loop clients; request latency excludes client executor waiting; p95 has only 8 samples; no streaming TTFT, quality or production capacity claim",
            "provenance": source_provenance(REPO, [Path(__file__)])}


if __name__ == "__main__":
    report = run()
    path = Path(__file__).with_name("out_neural_load.json")
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(report["status"], path)
    raise SystemExit(0 if report["status"] == "passed" else 1)
