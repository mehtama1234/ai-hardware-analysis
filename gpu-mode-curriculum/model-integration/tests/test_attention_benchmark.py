import sys
from pathlib import Path
import unittest
from unittest.mock import patch
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_attention_benchmark import benchmark


class BenchmarkTests(unittest.TestCase):
    def test_no_silent_fallback(self):
        with patch("torch.cuda.is_available", return_value=False):
            report = benchmark("cuda")
        self.assertEqual(report["status"], "unavailable")
        self.assertEqual(report["rows"], [])
        self.assertFalse(report["gpu_execution_accepted"])

    def test_cpu_scope_and_samples(self):
        threads = torch.get_num_threads()
        torch.set_num_threads(1)
        try:
            report = benchmark("cpu", sequence=3, repeat=2)
        finally:
            torch.set_num_threads(threads)
        self.assertFalse(report["gpu_execution_accepted"])
        self.assertEqual(len(report["rows"]), 3)
        for row in report["rows"]:
            self.assertEqual(len(row["samples_seconds"]), 2)
            self.assertEqual(row["memory"]["status"], "unavailable")
            self.assertTrue(row["errors_vs_cpu_fp64"])

    def test_bad_request(self):
        with self.assertRaises(ValueError):
            benchmark("cuda", sequence=0)
