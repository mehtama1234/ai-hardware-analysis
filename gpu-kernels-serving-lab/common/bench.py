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


def sample_seconds(
    fn: Callable[[], None],
    warmup: int = 3,
    repeat: int = 10,
    *,
    synchronize: Callable[[], None] | None = None,
) -> list[float]:
    """Host-wall-clock samples, optionally waiting for device work to finish.

    Callers must supply their device synchronization callback for asynchronous
    work. Allocate inputs and perform correctness checks outside ``fn`` when
    measuring operation latency. These samples include dispatch and completion
    overhead; they are not device-event kernel timings.
    """
    if not isinstance(warmup, int) or isinstance(warmup, bool) or warmup < 0:
        raise ValueError("warmup must be a nonnegative integer")
    if not isinstance(repeat, int) or isinstance(repeat, bool) or repeat < 1:
        raise ValueError("repeat must be a positive integer")
    sync = synchronize if synchronize is not None else lambda: None
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(repeat):
        sync()
        start = time.perf_counter()
        fn()
        sync()
        samples.append(time.perf_counter() - start)
    return samples


def median_seconds(
    fn: Callable[[], None], warmup: int = 3, repeat: int = 10,
    *, synchronize: Callable[[], None] | None = None,
) -> float:
    """Compatibility wrapper; see sample_seconds for timing semantics."""
    return statistics.median(sample_seconds(fn, warmup, repeat, synchronize=synchronize))
