"""Bounded in-process admission controller for the teaching server."""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class AdmissionLease:
    queue_wait_ms: float


class AdmissionController:
    def __init__(self, capacity: int, queue_limit: int):
        if capacity < 1 or queue_limit < 0:
            raise ValueError("capacity must be positive and queue_limit nonnegative")
        self.capacity = capacity
        self.queue_limit = queue_limit
        self._active = 0
        self._queued = 0
        self._condition = threading.Condition()

    def acquire(self, timeout: float = 10.0) -> AdmissionLease | None:
        started = time.perf_counter()
        with self._condition:
            if self._active >= self.capacity:
                if self._queued >= self.queue_limit:
                    return None
                self._queued += 1
                deadline = started + timeout
                while self._active >= self.capacity:
                    remaining = deadline - time.perf_counter()
                    if remaining <= 0:
                        self._queued -= 1
                        return None
                    self._condition.wait(remaining)
                self._queued -= 1
            self._active += 1
            return AdmissionLease((time.perf_counter() - started) * 1000.0)

    def release(self) -> None:
        with self._condition:
            if self._active < 1:
                raise RuntimeError("admission release without acquire")
            self._active -= 1
            self._condition.notify()

    def snapshot(self):
        with self._condition:
            return {"capacity": self.capacity, "active": self._active, "queued": self._queued, "queue_limit": self.queue_limit}
