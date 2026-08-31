"""Start the mini server, send completion requests, and write load-test evidence."""

from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[0]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


PORT = 8765
BASE = f"http://127.0.0.1:{PORT}"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_json(path: str, timeout: float = 2.0) -> dict:
    with urllib.request.urlopen(BASE + path, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post_json(path: str, payload: dict, timeout: float = 5.0) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wait_ready(proc: subprocess.Popen[str]) -> None:
    deadline = time.time() + 10
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited early with {proc.returncode}")
        try:
            health = get_json("/health", timeout=0.5)
            if health.get("status") == "ok":
                return
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(0.1)
    raise TimeoutError("server did not become ready")


def main() -> None:
    proc = subprocess.Popen(
        [sys.executable, "server.py", "--port", str(PORT)],
        cwd=HERE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    single_samples = []
    single_responses = []
    batch_sample = None
    batch_response = None
    try:
        wait_ready(proc)
        prompts = [
            "GPU serving lab shared prefix memory",
            "GPU serving lab shared prefix cache",
            "GPU serving lab shared prefix attention",
            "GPU serving lab shared prefix quantization",
            "GPU serving lab shared prefix scheduler",
        ]
        for prompt in prompts:
            started = time.perf_counter()
            resp = post_json("/v1/completions", {"prompt": prompt, "max_tokens": 16})
            elapsed_ms = (time.perf_counter() - started) * 1000
            single_samples.append(elapsed_ms)
            single_responses.append(resp)
        started = time.perf_counter()
        batch_response = post_json("/v1/batch_completions", {"prompts": prompts, "max_tokens": 16})
        batch_sample = (time.perf_counter() - started) * 1000
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        stdout, stderr = proc.communicate(timeout=1)

    single_tokens = sum(r["usage"]["completion_tokens"] for r in single_responses)
    single_ms = sum(single_samples)
    batch_tokens = batch_response["usage"]["completion_tokens"] if batch_response else 0
    speedup = (single_ms / batch_sample) if batch_sample else None
    out = {
        "session": "13-capstone-load-test",
        "timestamp": now(),
        "inventory": collect_inventory("13-capstone-load-test"),
        "paths": {
            "high_level_single_request": {
                "endpoint": BASE + "/v1/completions",
                "requests": len(single_samples),
                "completion_tokens": single_tokens,
                "latency_ms": {
                    "min": round(min(single_samples), 4),
                    "median": round(statistics.median(single_samples), 4),
                    "max": round(max(single_samples), 4),
                    "total": round(single_ms, 4),
                },
                "tokens_per_sec": round(single_tokens / (single_ms / 1000.0), 3) if single_ms else None,
                "backend": single_responses[0].get("backend") if single_responses else None,
                "sample_text": single_responses[0]["choices"][0]["text"] if single_responses else "",
            },
            "optimized_batched_prefix_cache": {
                "endpoint": BASE + "/v1/batch_completions",
                "requests": 1 if batch_response else 0,
                "logical_prompts": len(prompts),
                "completion_tokens": batch_tokens,
                "latency_ms": {"total": round(batch_sample, 4) if batch_sample else None},
                "tokens_per_sec": round(batch_tokens / (batch_sample / 1000.0), 3) if batch_sample else None,
                "backend": batch_response.get("backend") if batch_response else None,
                "prefix_tokens_reused": batch_response["usage"]["prefix_tokens_reused"] if batch_response else 0,
                "sample_text": batch_response["choices"][0]["text"] if batch_response else "",
            },
        },
        "comparison": {
            "high_level_path": "high_level_single_request",
            "optimized_path": "optimized_batched_prefix_cache",
            "optimized_latency_speedup": round(speedup, 3) if speedup else None,
        },
        "server_stdout": stdout.splitlines()[:5],
        "server_stderr": stderr.splitlines()[:5],
        "boundary": (
            "This is a minimal local endpoint and load-test harness. It proves the capstone "
            "has two measured serving paths: single-request high-level serving and a batched "
            "prefix-cache path. It is not production LLM quality or GPU vLLM throughput."
        ),
    }
    path = HERE / "out_load_test.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    optimized = out["paths"]["optimized_batched_prefix_cache"]
    print("wrote", path.name, optimized["logical_prompts"], "prompts", optimized["tokens_per_sec"], "tokens/sec")


if __name__ == "__main__":
    main()
