"""CPU-only tests for explicit timing boundaries; no accelerator claims."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.bench import median_seconds, sample_seconds


class TimingTests(unittest.TestCase):
    def test_synchronization_and_raw_samples(self):
        events = []

        def clock():
            events.append("clock")
            return next(ticks)

        ticks = iter([1.0, 1.5, 2.0, 2.75])
        with patch("common.bench.time.perf_counter", side_effect=clock):
            samples = sample_seconds(lambda: events.append("work"), 1, 2,
                                     synchronize=lambda: events.append("sync"))
        self.assertEqual(samples, [0.5, 0.75])
        self.assertEqual(events, ["work"] +
                         ["sync", "clock", "work", "sync", "clock"] * 2)

    def test_median_compatibility(self):
        with patch("common.bench.time.perf_counter", side_effect=[0, 2, 3, 7]):
            self.assertEqual(median_seconds(lambda: None, 0, 2), 3)

    def test_bad_counts(self):
        for kwargs in ({"warmup": -1}, {"repeat": 0}, {"repeat": 1.5},
                       {"warmup": True}, {"repeat": False}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                sample_seconds(lambda: None, **kwargs)

    def test_work_failure_propagates(self):
        with self.assertRaisesRegex(RuntimeError, "kernel failed"):
            sample_seconds(lambda: (_ for _ in ()).throw(RuntimeError("kernel failed")), 0, 1)


if __name__ == "__main__":
    unittest.main()
