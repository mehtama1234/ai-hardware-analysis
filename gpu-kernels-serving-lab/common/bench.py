"""Benchmark helper primitives for later sessions."""

from __future__ import annotations

import statistics
import time
from contextlib import contextmanager
from typing import Callable, Iterable


@contextmanager
def timer() -> Iterable[Callable[[], float]]:
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start


def median_seconds(fn: Callable[[], None], warmup: int = 3, repeat: int = 10) -> float:
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)

