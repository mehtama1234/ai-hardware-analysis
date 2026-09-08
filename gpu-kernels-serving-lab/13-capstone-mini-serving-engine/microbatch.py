"""Small, explicit continuous-arrival microbatch scheduler for the lab.

The scheduler is intentionally independent of the HTTP server: callers submit
requests as they arrive, a worker waits for a bounded window, groups compatible
equal-length prompts, and resolves one future per request. It is a teaching
reference, not a production queue or paged-KV engine.
"""
from __future__ import annotations

from concurrent.futures import Future
from dataclasses import dataclass
import queue
import threading
import time


@dataclass
class _Request:
    prompt: str
    max_tokens: int
    future: Future
    submitted_at: float


class MicroBatchScheduler:
    def __init__(self, generator, *, max_batch: int = 4, window_ms: float = 5.0, max_pending: int = 64):
        if max_batch < 1 or window_ms < 0 or max_pending < 1:
            raise ValueError("max_batch/max_pending must be positive and window_ms nonnegative")
        self.generator = generator
        self.max_batch = max_batch
        self.window_seconds = window_ms / 1000.0
        self.max_pending = max_pending
        self._queue: queue.Queue[_Request | None] = queue.Queue(maxsize=max_pending)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name="microbatch-worker", daemon=True)
        self._lock = threading.Lock()
        self._batches: list[dict] = []
        self._rejected = 0
        self._cancelled = 0
        self._thread.start()

    def submit(self, prompt: str, max_tokens: int) -> Future:
        future: Future = Future()
        try:
            self._queue.put_nowait(_Request(prompt, max_tokens, future, time.perf_counter()))
        except queue.Full:
            with self._lock:
                self._rejected += 1
            raise
        return future

    def snapshot(self) -> dict:
        with self._lock:
            return {"batch_count": len(self._batches), "batches": [dict(row) for row in self._batches],
                    "rejected_count": self._rejected, "cancelled_count": self._cancelled,
                    "max_pending": self.max_pending}

    def close(self) -> None:
        if not self._stop.is_set():
            self._stop.set(); self._queue.put(None); self._thread.join(timeout=10)
        if self._thread.is_alive():
            raise RuntimeError("microbatch worker did not stop")

    def _run(self) -> None:
        while not self._stop.is_set():
            first = self._queue.get()
            if first is None:
                return
            requests = [first]
            deadline = time.perf_counter() + self.window_seconds
            while len(requests) < self.max_batch:
                remaining = deadline - time.perf_counter()
                if remaining <= 0:
                    break
                try:
                    next_request = self._queue.get(timeout=remaining)
                except queue.Empty:
                    break
                if next_request is None:
                    self._stop.set(); break
                requests.append(next_request)
            active = [request for request in requests if not request.future.cancelled()]
            with self._lock:
                self._cancelled += len(requests) - len(active)
            if not active:
                continue
            requests = active
            # Equal-length groups can share the model's real batched KV cache.
            groups: dict[tuple[int, int], list[_Request]] = {}
            for request in requests:
                key = (len(self.generator.encode(request.prompt)), request.max_tokens)
                groups.setdefault(key, []).append(request)
            for group in groups.values():
                try:
                    if len(group) > 1:
                        result = self.generator.complete_batch([r.prompt for r in group], group[0].max_tokens)
                        mode = result.get("batch_mode", "unknown")
                        choices = result["choices"]
                    else:
                        result = self.generator.complete(group[0].prompt, group[0].max_tokens)
                        mode = "single"
                        choices = [{"text": result["text"]}]
                    with self._lock:
                        self._batches.append({"size": len(group), "mode": mode,
                                              "prompt_length": len(group[0].prompt),
                                              "queue_wait_ms": round((time.perf_counter() - min(r.submitted_at for r in group)) * 1000, 4)})
                    for request, choice in zip(group, choices):
                        request.future.set_result({"text": choice["text"], "batch_mode": mode})
                except Exception as exc:
                    for request in group:
                        request.future.set_exception(exc)
